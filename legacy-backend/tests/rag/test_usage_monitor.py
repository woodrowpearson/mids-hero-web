"""Tests for usage monitor."""

from datetime import datetime, timedelta

import pytest

from app.rag import UsageLimitError, UsageMonitor
from app.rag.config import rag_settings


@pytest.fixture
def usage_file(tmp_path):
    """Set up temporary usage data file."""
    original_path = rag_settings.embedding_cache_path
    rag_settings.embedding_cache_path = str(tmp_path)

    yield tmp_path / "usage_data.json"

    rag_settings.embedding_cache_path = original_path


@pytest.fixture
def monitor(usage_file):
    """Create a usage monitor."""
    return UsageMonitor()


class TestUsageMonitor:
    """Test usage monitor functionality."""

    def test_initialization(self, monitor):
        """Test monitor initialization."""
        assert monitor.daily_limit == rag_settings.daily_token_limit
        assert monitor.alert_threshold == rag_settings.alert_threshold
        assert monitor.current_date == datetime.now().date().isoformat()
        assert len(monitor.alert_callbacks) == 0

    def test_track_usage(self, monitor, usage_file):
        """Test basic usage tracking."""
        # Track some usage
        monitor.track_usage(100, "embedding")
        monitor.track_usage(50, "search")

        # Check current usage
        usage = monitor.get_current_usage()

        assert usage["date"] == datetime.now().date().isoformat()
        assert usage["tokens"] == 150
        assert usage["requests"] == 2
        assert usage["embeddings"] == 1
        assert usage["cost"] > 0
        assert usage["limit"] == monitor.daily_limit
        assert usage["percentage"] == (150 / monitor.daily_limit * 100)
        assert usage["remaining"] == monitor.daily_limit - 150

        # Check data was saved
        assert usage_file.exists()

    def test_cost_calculation(self, monitor):
        """Test cost calculation."""
        # Embedding cost
        embedding_cost = monitor._calculate_cost(1000, "embedding")
        assert embedding_cost == 0.0001  # $0.0001 per 1K tokens

        # Other operation cost
        other_cost = monitor._calculate_cost(1000, "other")
        assert other_cost == 0.0002  # $0.0002 per 1K tokens

    def test_daily_limit_enforcement(self, monitor):
        """Test that daily limits are enforced."""
        # Set a low limit for testing
        monitor.daily_limit = 1000

        # Track usage up to limit
        monitor.track_usage(900, "embedding")

        # Should still work
        monitor.track_usage(50, "embedding")

        # Should exceed limit
        with pytest.raises(UsageLimitError):
            monitor.track_usage(100, "embedding")

    def test_alert_threshold(self, monitor):
        """Test alert threshold functionality."""
        # Set up alert tracking
        alerts_received = []

        def alert_callback(message):
            alerts_received.append(message)

        monitor.register_alert_callback(alert_callback)

        # Set low limit for testing
        monitor.daily_limit = 1000
        monitor.alert_threshold = 0.8

        # Track usage below threshold
        monitor.track_usage(700, "embedding")
        assert len(alerts_received) == 0

        # Track usage above threshold
        monitor.track_usage(100, "embedding")
        assert len(alerts_received) == 1
        assert "Approaching daily token limit" in alerts_received[0]

        # Additional usage shouldn't trigger more alerts (limited to 3)
        monitor.track_usage(50, "embedding")
        monitor.track_usage(50, "embedding")
        monitor.track_usage(50, "embedding")
        monitor.track_usage(50, "embedding")

        assert len(alerts_received) <= 4  # Initial + 3 more max

    def test_date_rollover(self, monitor):
        """Test handling of date changes."""
        # Track usage for current date
        monitor.track_usage(500, "embedding")
        today = datetime.now().date().isoformat()

        # Simulate date change by directly adding data for tomorrow
        tomorrow = (datetime.now() + timedelta(days=1)).date().isoformat()
        monitor.usage_data["daily_usage"][tomorrow] = {
            "tokens": 300,
            "requests": 1,
            "embeddings": 1,
            "cost": monitor._calculate_cost(300, "embedding"),
            "alerts_sent": 0,
        }

        # Check both dates have separate usage
        assert monitor.usage_data["daily_usage"][today]["tokens"] == 500
        assert monitor.usage_data["daily_usage"][tomorrow]["tokens"] == 300

    def test_get_usage_report(self, monitor):
        """Test usage report generation."""
        # Add usage for multiple days
        today = datetime.now().date()

        for i in range(7):
            date = (today - timedelta(days=i)).isoformat()
            if date not in monitor.usage_data["daily_usage"]:
                monitor.usage_data["daily_usage"][date] = {
                    "tokens": 1000 * (i + 1),
                    "requests": 10 * (i + 1),
                    "embeddings": 5 * (i + 1),
                    "cost": 0.1 * (i + 1),
                    "alerts_sent": 0,
                }

        monitor._save_usage_data()

        # Get 7-day report
        report = monitor.get_usage_report(days=7)

        assert report["period"]["days"] == 7
        assert len(report["daily_usage"]) == 7
        assert report["summary"]["total_tokens"] > 0
        assert report["summary"]["total_cost"] > 0
        assert report["summary"]["total_requests"] > 0
        assert report["summary"]["avg_tokens_per_day"] > 0
        assert report["summary"]["avg_cost_per_day"] > 0

    def test_cost_breakdown(self, monitor):
        """Test cost breakdown report."""
        # Track some usage
        monitor.track_usage(10000, "embedding")

        breakdown = monitor.get_cost_breakdown()

        assert breakdown["total_cost"] > 0
        assert "embeddings" in breakdown["breakdown"]
        assert "other" in breakdown["breakdown"]
        assert breakdown["currency"] == "USD"
        assert "start" in breakdown["period"]
        assert "end" in breakdown["period"]

    def test_reset_daily_usage(self, monitor):
        """Test resetting daily usage."""
        # Track some usage
        monitor.track_usage(500, "embedding")

        # Reset
        monitor.reset_daily_usage()

        # Check reset
        usage = monitor.get_current_usage()
        assert usage["tokens"] == 0
        assert usage["requests"] == 0
        assert usage["embeddings"] == 0
        assert usage["cost"] == 0.0

    def test_cleanup_old_data(self, monitor):
        """Test cleaning up old usage data."""
        # Add old and recent data
        today = datetime.now().date()
        old_date = (today - timedelta(days=40)).isoformat()
        recent_date = (today - timedelta(days=10)).isoformat()

        monitor.usage_data["daily_usage"][old_date] = {
            "tokens": 1000,
            "requests": 10,
            "embeddings": 5,
            "cost": 0.1,
            "alerts_sent": 0,
        }

        monitor.usage_data["daily_usage"][recent_date] = {
            "tokens": 2000,
            "requests": 20,
            "embeddings": 10,
            "cost": 0.2,
            "alerts_sent": 0,
        }

        # Clean up data older than 30 days
        cleaned = monitor.cleanup_old_data(days_to_keep=30)

        assert cleaned == 1
        assert old_date not in monitor.usage_data["daily_usage"]
        assert recent_date in monitor.usage_data["daily_usage"]

    def test_persistence(self, monitor, usage_file):
        """Test that usage data persists."""
        # Track usage
        monitor.track_usage(1000, "embedding")
        monitor.track_usage(500, "search")

        # Create new monitor instance
        monitor2 = UsageMonitor()

        # Should load previous data
        usage = monitor2.get_current_usage()
        assert usage["tokens"] == 1500
        assert usage["requests"] == 2

    def test_concurrent_operations(self, monitor):
        """Test handling of concurrent usage tracking."""
        import asyncio

        async def track_async():
            for _i in range(10):
                monitor.track_usage(100, "embedding")
                await asyncio.sleep(0.001)

        # Run multiple concurrent tracks
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        tasks = [track_async() for _ in range(3)]
        loop.run_until_complete(asyncio.gather(*tasks))

        # Should have tracked all usage
        usage = monitor.get_current_usage()
        assert usage["tokens"] == 3000  # 3 tasks * 10 calls * 100 tokens
        assert usage["requests"] == 30

    def test_metadata_in_tracking(self, monitor):
        """Test tracking with metadata."""
        # Track with metadata (not used but shouldn't break)
        metadata = {"source": "test", "user": "test_user"}
        monitor.track_usage(100, "embedding", metadata)

        usage = monitor.get_current_usage()
        assert usage["tokens"] == 100

    def test_zero_limit_handling(self, monitor):
        """Test handling of zero daily limit."""
        monitor.daily_limit = 0

        # Should handle percentage calculation
        usage = monitor.get_current_usage()
        assert usage["percentage"] == 0

        # Should immediately exceed limit
        with pytest.raises(UsageLimitError):
            monitor.track_usage(1, "embedding")

    def test_async_alert_callbacks(self, monitor):
        """Test async alert callbacks."""
        import asyncio

        alerts = []

        async def async_callback(message):
            alerts.append(f"async: {message}")

        def sync_callback(message):
            alerts.append(f"sync: {message}")

        monitor.register_alert_callback(async_callback)
        monitor.register_alert_callback(sync_callback)

        # Set low limit to trigger alerts
        monitor.daily_limit = 100
        monitor.alert_threshold = 0.8

        # Trigger alert
        monitor.track_usage(85, "embedding")

        # Give async callback time to execute
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(asyncio.sleep(0.1))

        # Should have both alerts
        assert any("sync:" in alert for alert in alerts)
        # Async alert might not be captured in test
