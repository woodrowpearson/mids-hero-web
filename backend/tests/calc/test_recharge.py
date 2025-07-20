"""Tests for recharge calculation module."""

import pytest

from app.calc.recharge import (
    calc_activation_time,
    calc_chain_time,
    calc_dps_with_recharge,
    calc_perma_status,
    calc_recharge,
)


class TestRechargeCalculations:
    """Test recharge calculation functions."""

    def test_recharge_basic(self):
        """Test basic recharge calculation."""
        base = 10.0
        enhancement = 0.0
        global_rech = 0.0

        result = calc_recharge(base, enhancement, global_rech)
        assert result == 10.0

    def test_recharge_with_enhancement(self):
        """Test recharge with enhancement."""
        base = 10.0
        enhancement = 0.95  # 95% recharge (at ED cap)
        global_rech = 0.0

        result = calc_recharge(base, enhancement, global_rech)
        assert result == pytest.approx(5.13, rel=0.01)  # 10 / 1.95

    def test_recharge_with_global(self):
        """Test recharge with global bonuses."""
        base = 10.0
        enhancement = 0.95
        global_rech = 0.70  # 70% global (Hasten + sets)

        result = calc_recharge(base, enhancement, global_rech)
        # 10 / (1 + 0.95 + 0.70) = 10 / 2.65
        assert result == pytest.approx(3.77, rel=0.01)

    def test_recharge_cap(self):
        """Test recharge cap at +500%."""
        base = 10.0
        enhancement = 2.0  # 200%
        global_rech = 4.0  # 400%

        # Total would be 600% but capped at 500%
        result = calc_recharge(base, enhancement, global_rech)
        assert result == pytest.approx(1.67, rel=0.01)  # 10 / 6.0

    def test_recharge_minimum(self):
        """Test minimum recharge time."""
        base = 0.1  # Very fast power
        enhancement = 5.0  # Extreme enhancement
        global_rech = 5.0

        result = calc_recharge(base, enhancement, global_rech)
        assert result == 0.5  # Minimum recharge time

    def test_chain_time_seamless(self):
        """Test power chain with seamless rotation."""
        powers = [
            {
                "name": "Power 1",
                "base_recharge": 4.0,
                "recharge_enhancement": 0.95,
                "activation_time": 1.0
            },
            {
                "name": "Power 2",
                "base_recharge": 6.0,
                "recharge_enhancement": 0.95,
                "activation_time": 1.5
            },
            {
                "name": "Power 3",
                "base_recharge": 8.0,
                "recharge_enhancement": 0.95,
                "activation_time": 2.0
            }
        ]

        result = calc_chain_time(powers, global_recharge=0.70)

        # Total animation time
        assert result["total_animation"] == 4.5

        # Check seamless
        assert result["seamless"] is True
        assert result["gap_time"] == 0.0

    def test_chain_time_with_gap(self):
        """Test power chain with gaps."""
        powers = [
            {
                "name": "Slow Power",
                "base_recharge": 20.0,
                "recharge_enhancement": 0.0,
                "activation_time": 2.0
            }
        ]

        result = calc_chain_time(powers)

        assert result["limiting_recharge"] == 20.0
        assert result["gap_time"] == 18.0  # 20 - 2
        assert result["seamless"] is False

    def test_perma_status_permanent(self):
        """Test permanent power status."""
        duration = 120.0  # 2 minute duration
        recharge = 100.0  # Recharges before it expires

        result = calc_perma_status(duration, recharge)

        assert result["is_perma"] is True
        assert result["uptime_percent"] == 100.0
        assert result["overlap_seconds"] == 20.0
        assert result["gap_seconds"] == 0.0

    def test_perma_status_not_permanent(self):
        """Test non-permanent power status."""
        duration = 90.0
        recharge = 120.0  # 30 second gap

        result = calc_perma_status(duration, recharge)

        assert result["is_perma"] is False
        assert result["uptime_percent"] == 75.0  # 90/120
        assert result["overlap_seconds"] == 0.0
        assert result["gap_seconds"] == 30.0

    def test_activation_time_basic(self):
        """Test activation time calculation."""
        base = 1.67  # Common activation time

        result = calc_activation_time(base)
        assert result == 1.67

        # With reduction (rare)
        result = calc_activation_time(base, animation_bonus=0.1)
        assert result == pytest.approx(1.503, rel=0.01)

    def test_activation_time_minimum(self):
        """Test minimum activation time (arcanatime)."""
        base = 0.1  # Very fast

        result = calc_activation_time(base)
        assert result == 0.132  # Minimum arcanatime

    def test_dps_with_recharge(self):
        """Test DPS calculation accounting for recharge."""
        damage = 100.0
        recharge = 8.0
        activation = 2.0

        # DPS = 100 / (8 + 2) = 10
        result = calc_dps_with_recharge(damage, recharge, activation)
        assert result == 10.0
