"""Tests for Enhancement Diversification (ED) calculations."""

import pytest
from hypothesis import given, strategies as st

from app.calc.ed import apply_ed


class TestEnhancementDiversification:
    """Test ED calculations match game rules."""

    def test_ed_below_first_threshold(self):
        """ED should not reduce values below first threshold."""
        # Schedule A: First threshold is 95%
        assert apply_ed("A", 0.0) == 0.0
        assert apply_ed("A", 0.5) == 0.5
        assert apply_ed("A", 0.94) == 0.94
        assert apply_ed("A", 0.95) == 0.95

    def test_ed_schedule_a_thresholds(self):
        """Test Schedule A ED calculations at key points."""
        # Schedule A: 0-95% = 1.0x, 95-170% = 0.9x, 170-260% = 0.7x, >260% = 0.15x
        
        # At first threshold
        assert apply_ed("A", 0.95) == 0.95
        
        # Between first and second threshold
        # 95% + (100% - 95%) * 0.9 = 0.95 + 0.045 = 0.995
        assert abs(apply_ed("A", 1.0) - 0.995) < 0.001
        
        # At second threshold (170%)
        # 95% + (170% - 95%) * 0.9 = 0.95 + 0.675 = 1.625
        assert abs(apply_ed("A", 1.70) - 1.625) < 0.001
        
        # Between second and third threshold
        # 95% + 75% * 0.9 + (200% - 170%) * 0.7 = 0.95 + 0.675 + 0.21 = 1.835
        assert abs(apply_ed("A", 2.0) - 1.835) < 0.001
        
        # At third threshold (260%)
        # 95% + 75% * 0.9 + 90% * 0.7 = 0.95 + 0.675 + 0.63 = 2.255
        assert abs(apply_ed("A", 2.60) - 2.255) < 0.001
        
        # Beyond third threshold
        # 95% + 75% * 0.9 + 90% * 0.7 + (300% - 260%) * 0.15 = 2.255 + 0.06 = 2.315
        assert abs(apply_ed("A", 3.0) - 2.315) < 0.001

    def test_ed_schedule_b_thresholds(self):
        """Test Schedule B ED calculations at key points."""
        # Schedule B: 0-40% = 1.0x, 40-80% = 0.9x, 80-120% = 0.7x, >120% = 0.15x
        
        assert apply_ed("B", 0.40) == 0.40
        
        # 40% + (50% - 40%) * 0.9 = 0.40 + 0.09 = 0.49
        assert abs(apply_ed("B", 0.50) - 0.49) < 0.001
        
        # At second threshold
        # 40% + 40% * 0.9 = 0.40 + 0.36 = 0.76
        assert abs(apply_ed("B", 0.80) - 0.76) < 0.001
        
        # At third threshold
        # 40% + 40% * 0.9 + 40% * 0.7 = 0.40 + 0.36 + 0.28 = 1.04
        assert abs(apply_ed("B", 1.20) - 1.04) < 0.001

    def test_ed_schedule_c_thresholds(self):
        """Test Schedule C ED calculations at key points."""
        # Schedule C: 0-25% = 1.0x, 25-50% = 0.9x, 50-75% = 0.7x, >75% = 0.15x
        
        assert apply_ed("C", 0.25) == 0.25
        
        # 25% + (30% - 25%) * 0.9 = 0.25 + 0.045 = 0.295
        assert abs(apply_ed("C", 0.30) - 0.295) < 0.001
        
        # At second threshold
        # 25% + 25% * 0.9 = 0.25 + 0.225 = 0.475
        assert abs(apply_ed("C", 0.50) - 0.475) < 0.001
        
        # At third threshold
        # 25% + 25% * 0.9 + 25% * 0.7 = 0.25 + 0.225 + 0.175 = 0.65
        assert abs(apply_ed("C", 0.75) - 0.65) < 0.001

    def test_ed_negative_values(self):
        """ED should handle negative values (debuffs) correctly."""
        # Negative values should be returned as-is (no ED on debuffs)
        assert apply_ed("A", -0.5) == -0.5
        assert apply_ed("B", -1.0) == -1.0
        assert apply_ed("C", -0.25) == -0.25

    def test_ed_invalid_schedule(self):
        """ED should raise error for invalid schedule."""
        with pytest.raises(ValueError, match="Unknown ED schedule"):
            apply_ed("X", 1.0)

    @given(
        value=st.floats(min_value=0.0, max_value=5.0),
        schedule=st.sampled_from(["A", "B", "C"])
    )
    def test_ed_never_increases_value(self, value, schedule):
        """Property: ED should never increase the enhancement value."""
        result = apply_ed(schedule, value)
        assert result <= value

    @given(
        value=st.floats(min_value=0.0, max_value=5.0),
        schedule=st.sampled_from(["A", "B", "C"])
    )
    def test_ed_is_monotonic(self, value, schedule):
        """Property: ED function should be monotonically increasing."""
        epsilon = 0.01
        if value + epsilon <= 5.0:
            result1 = apply_ed(schedule, value)
            result2 = apply_ed(schedule, value + epsilon)
            assert result2 >= result1

    def test_ed_common_enhancement_values(self):
        """Test ED with common enhancement configurations."""
        # 3 SOs (3 * 33.33% = 99.99%)
        three_sos = 0.9999
        assert abs(apply_ed("A", three_sos) - 0.994) < 0.01  # ~99.4% after ED
        
        # 6 SOs (6 * 33.33% = 199.98%)
        six_sos = 1.9998
        assert abs(apply_ed("A", six_sos) - 1.86) < 0.01  # ~186% after ED
        
        # Common IO build (95% enhancement)
        assert apply_ed("A", 0.95) == 0.95  # No reduction at cap