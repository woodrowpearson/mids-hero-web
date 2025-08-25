"""Usage monitoring and cost tracking for RAG system."""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from .config import rag_settings
from .exceptions import UsageLimitError

logger = logging.getLogger(__name__)


class UsageMonitor:
    """Monitor and track usage of the RAG system."""

    def __init__(self):
        """Initialize usage monitor."""
        self.daily_limit = rag_settings.daily_token_limit
        self.alert_threshold = rag_settings.alert_threshold

        # Usage data file
        self.usage_file = Path(rag_settings.embedding_cache_path) / "usage_data.json"
        self.usage_data = self._load_usage_data()

        # Current day tracking
        self.current_date = datetime.now().date().isoformat()
        self._ensure_current_date()

        # Alert callbacks
        self.alert_callbacks: list[Any] = []

    def _load_usage_data(self) -> dict[str, Any]:
        """Load usage data from file."""
        if self.usage_file.exists():
            try:
                with open(self.usage_file) as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load usage data: {e}")

        return {
            "daily_usage": {},
            "total_usage": {
                "tokens": 0,
                "requests": 0,
                "cost": 0.0,
                "started_at": datetime.now().isoformat(),
            },
        }

    def _save_usage_data(self) -> None:
        """Save usage data to file."""
        try:
            self.usage_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.usage_file, "w") as f:
                json.dump(self.usage_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save usage data: {e}")

    def _ensure_current_date(self) -> None:
        """Ensure current date exists in usage data."""
        if self.current_date not in self.usage_data["daily_usage"]:
            self.usage_data["daily_usage"][self.current_date] = {
                "tokens": 0,
                "requests": 0,
                "embeddings": 0,
                "cost": 0.0,
                "alerts_sent": 0,
            }

    def track_usage(
        self,
        tokens: int,
        operation: str = "embedding",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Track usage for an operation."""
        # Update date if needed
        new_date = datetime.now().date().isoformat()
        if new_date != self.current_date:
            self.current_date = new_date
            self._ensure_current_date()

        # Calculate cost (Gemini pricing estimate)
        cost = self._calculate_cost(tokens, operation)

        # Update daily usage
        daily = self.usage_data["daily_usage"][self.current_date]
        daily["tokens"] += tokens
        daily["requests"] += 1
        daily["cost"] += cost

        if operation == "embedding":
            daily["embeddings"] += 1

        # Update total usage
        total = self.usage_data["total_usage"]
        total["tokens"] += tokens
        total["requests"] += 1
        total["cost"] += cost

        # Check limits
        if daily["tokens"] > self.daily_limit:
            raise UsageLimitError(
                f"Daily token limit exceeded: {daily['tokens']} > {self.daily_limit}"
            )

        # Check alert threshold
        if daily["tokens"] >= self.daily_limit * self.alert_threshold:
            if daily["alerts_sent"] < 3:  # Limit alerts per day
                self._send_alert(
                    f"Approaching daily token limit: {daily['tokens']} / {self.daily_limit} "
                    f"({daily['tokens'] / self.daily_limit * 100:.1f}%)"
                )
                daily["alerts_sent"] += 1

        # Save data
        self._save_usage_data()

        # Log usage
        logger.debug(
            f"Tracked {tokens} tokens for {operation} "
            f"(daily total: {daily['tokens']}, cost: ${daily['cost']:.4f})"
        )

    def _calculate_cost(self, tokens: int, operation: str) -> float:
        """Calculate estimated cost for tokens."""
        # Gemini pricing (estimated)
        if operation == "embedding":
            # $0.0001 per 1K tokens for embeddings
            return (tokens / 1000) * 0.0001
        else:
            # Default pricing
            return (tokens / 1000) * 0.0002

    def _send_alert(self, message: str) -> None:
        """Send usage alert."""
        logger.warning(f"Usage Alert: {message}")

        # Call registered callbacks
        for callback in self.alert_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(message))
                else:
                    callback(message)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")

    def register_alert_callback(self, callback: Any) -> None:
        """Register a callback for usage alerts."""
        self.alert_callbacks.append(callback)

    def get_current_usage(self) -> dict[str, Any]:
        """Get current day's usage."""
        self._ensure_current_date()
        daily = self.usage_data["daily_usage"][self.current_date]

        return {
            "date": self.current_date,
            "tokens": daily["tokens"],
            "requests": daily["requests"],
            "embeddings": daily["embeddings"],
            "cost": daily["cost"],
            "limit": self.daily_limit,
            "percentage": (
                (daily["tokens"] / self.daily_limit * 100)
                if self.daily_limit > 0
                else 0
            ),
            "remaining": max(0, self.daily_limit - daily["tokens"]),
        }

    def get_usage_report(
        self, days: int = 7, include_hourly: bool = False
    ) -> dict[str, Any]:
        """Get usage report for the specified period."""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days - 1)

        # Collect daily usage
        daily_usage = []
        total_tokens = 0
        total_cost = 0.0
        total_requests = 0

        for i in range(days):
            date = (start_date + timedelta(days=i)).isoformat()
            if date in self.usage_data["daily_usage"]:
                usage = self.usage_data["daily_usage"][date]
                daily_usage.append(
                    {
                        "date": date,
                        "tokens": usage["tokens"],
                        "requests": usage["requests"],
                        "cost": usage["cost"],
                    }
                )
                total_tokens += usage["tokens"]
                total_cost += usage["cost"]
                total_requests += usage["requests"]
            else:
                daily_usage.append(
                    {"date": date, "tokens": 0, "requests": 0, "cost": 0.0}
                )

        report = {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days,
            },
            "daily_usage": daily_usage,
            "summary": {
                "total_tokens": total_tokens,
                "total_cost": total_cost,
                "total_requests": total_requests,
                "avg_tokens_per_day": total_tokens / days,
                "avg_cost_per_day": total_cost / days,
                "avg_tokens_per_request": (
                    total_tokens / total_requests if total_requests > 0 else 0
                ),
            },
            "total_usage": self.usage_data["total_usage"],
        }

        return report

    def get_cost_breakdown(self) -> dict[str, Any]:
        """Get cost breakdown by operation type."""
        # This would need more detailed tracking in production
        total_cost = self.usage_data["total_usage"]["cost"]

        return {
            "total_cost": total_cost,
            "breakdown": {
                "embeddings": total_cost * 0.8,  # Estimate
                "other": total_cost * 0.2,
            },
            "currency": "USD",
            "period": {
                "start": self.usage_data["total_usage"]["started_at"],
                "end": datetime.now().isoformat(),
            },
        }

    def reset_daily_usage(self) -> None:
        """Reset daily usage (for testing)."""
        self.current_date = datetime.now().date().isoformat()
        self.usage_data["daily_usage"][self.current_date] = {
            "tokens": 0,
            "requests": 0,
            "embeddings": 0,
            "cost": 0.0,
            "alerts_sent": 0,
        }
        self._save_usage_data()
        logger.info("Daily usage reset")

    def cleanup_old_data(self, days_to_keep: int = 30) -> int:
        """Clean up old usage data."""
        cutoff_date = (datetime.now().date() - timedelta(days=days_to_keep)).isoformat()

        old_dates = [
            date for date in self.usage_data["daily_usage"] if date < cutoff_date
        ]

        for date in old_dates:
            del self.usage_data["daily_usage"][date]

        if old_dates:
            self._save_usage_data()
            logger.info(f"Cleaned up {len(old_dates)} old usage records")

        return len(old_dates)
