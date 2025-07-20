"""Tests for endurance calculation module."""

import pytest

from app.calc.endurance import (
    calc_end_cost,
    calc_endurance_per_second,
    calc_endurance_recovery,
    calc_net_endurance,
    calc_toggle_endurance,
    can_sustain_toggles,
)


class TestEnduranceCalculations:
    """Test endurance calculation functions."""

    def test_end_cost_basic(self):
        """Test basic endurance cost calculation."""
        base = 10.0
        reduction = 0.0
        
        result = calc_end_cost(base, reduction)
        assert result == 10.0

    def test_end_cost_with_reduction(self):
        """Test endurance cost with reduction."""
        base = 10.0
        reduction = 0.50  # 50% reduction
        
        result = calc_end_cost(base, reduction)
        assert result == pytest.approx(6.67, rel=0.01)  # 10 / 1.5

    def test_end_cost_with_ed(self):
        """Test endurance cost with ED applied."""
        base = 10.0
        reduction = 0.95  # 95% reduction (at ED threshold)
        
        result = calc_end_cost(base, reduction)
        assert result == pytest.approx(5.13, rel=0.01)  # 10 / 1.95

    def test_end_cost_minimum_floor(self):
        """Test minimum endurance cost floor (10% of base)."""
        base = 10.0
        reduction = 5.0  # 500% reduction (impossible but tests floor)
        
        result = calc_end_cost(base, reduction)
        assert result == 1.0  # 10% of base

    def test_endurance_per_second(self):
        """Test EPS calculation."""
        cost = 10.0
        recharge = 8.0
        activation = 2.0
        
        # Total cycle = 8 + 2 = 10 seconds
        # EPS = 10 / 10 = 1.0
        result = calc_endurance_per_second(cost, recharge, activation)
        assert result == 1.0

    def test_toggle_endurance(self):
        """Test toggle power endurance cost."""
        base = 0.26  # Common toggle cost
        reduction = 0.50  # 50% reduction
        
        # Cost per tick after reduction
        result = calc_toggle_endurance(base, reduction)
        # Default tick rate is 0.5 seconds
        # 0.26 / 1.5 = 0.173 per tick
        # 0.173 / 0.5 = 0.346 per second
        assert result == pytest.approx(0.346, rel=0.01)

    def test_endurance_recovery(self):
        """Test endurance recovery calculation."""
        # Base recovery
        result = calc_endurance_recovery()
        assert result == 1.67  # Base 1.67 end/sec
        
        # With recovery bonus
        result = calc_endurance_recovery(recovery_bonus=1.0)  # +100% recovery
        assert result == 3.34  # Doubled
        
        # With increased max endurance
        result = calc_endurance_recovery(
            recovery_bonus=0.5,  # +50%
            max_endurance=110.0  # Accolade bonus
        )
        assert result == pytest.approx(2.755, rel=0.01)

    def test_net_endurance(self):
        """Test net endurance gain/loss."""
        recovery = 1.67
        toggles = [0.26, 0.26, 0.52]  # 3 toggles
        active_eps = 0.5  # Average from active powers
        
        result = calc_net_endurance(recovery, toggles, active_eps)
        # 1.67 - (0.26 + 0.26 + 0.52 + 0.5) = 0.13
        assert result == pytest.approx(0.13, rel=0.01)

    def test_can_sustain_toggles(self):
        """Test toggle sustainability check."""
        recovery = 1.67
        
        # Can sustain
        toggles = [0.26, 0.26, 0.26]  # 0.78 total
        assert can_sustain_toggles(recovery, toggles) is True
        
        # Cannot sustain with safety margin
        toggles = [0.52, 0.52, 0.52]  # 1.56 total
        assert can_sustain_toggles(recovery, toggles) is False
        
        # Edge case - exactly at limit with margin
        toggles = [0.52, 0.52, 0.35]  # 1.39 total
        # With 20% margin needs 1.668 recovery
        assert can_sustain_toggles(recovery, toggles) is True