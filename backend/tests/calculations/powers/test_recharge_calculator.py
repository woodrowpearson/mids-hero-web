"""
Test suite for Power Recharge Calculator

Tests based on comprehensive test cases from Spec 07, Section 4.
All expected values are exact calculations from the specification.
"""

import pytest

from app.calculations.powers.recharge_calculator import (
    InvalidRechargeConfigError,
    RechargeCalculator,
    validate_recharge_config,
)


class TestBasicPowerNoEnhancements:
    """Test Case 1: Basic Power - No Enhancements (from Spec 07)"""

    def test_basic_power_no_enhancements(self):
        """
        Power: Foot Stomp (Super Strength)
        Level: 50
        Archetype: Tanker

        Input:
            - Base Recharge: 20.0 seconds
            - Local Enhancements: [] (none)
            - Global Recharge: 0.0 (none)
            - Archetype Cap: 5.0 (400%)

        Calculation:
            local_mult = 1.0 + 0.0 = 1.0
            global_mult = 1.0 + 0.0 = 1.0
            total_mult = 1.0 * 1.0 = 1.0
            actual_recharge = 20.0 / 1.0 = 20.0

        Expected: 20.0 seconds
        """
        calculator = RechargeCalculator()
        result = calculator.calculate_recharge(
            base_recharge=20.0,
            local_bonuses=[],
            global_bonus=0.0,
            archetype_cap=5.0,
        )

        assert result.base_recharge == 20.0
        assert result.local_recharge_bonus_pre_ed == 0.0
        assert result.local_recharge_bonus_after_ed == 0.0
        assert result.local_recharge_multiplier == pytest.approx(1.0, abs=0.01)
        assert result.global_recharge_multiplier == pytest.approx(1.0, abs=0.01)
        assert result.total_multiplier == pytest.approx(1.0, abs=0.01)
        assert result.actual_recharge == pytest.approx(20.0, abs=0.01)
        assert result.is_capped is False


class TestThreeRechargeSOs:
    """Test Case 2: Three Recharge SOs (Tests ED) (from Spec 07)"""

    def test_three_recharge_sos(self):
        """
        Power: Generic 60s recharge power
        Level: 50

        Input:
            - Base Recharge: 60.0 seconds
            - Local Bonuses: [0.385, 0.385, 0.385] (three +38.5% SOs)
            - Global Bonus: 0.0
            - Archetype Cap: 5.0

        Calculation:
            Total Local Bonus: 115.5% (1.155)
            After ED Schedule A (thresholds: 70%, 90%, 100%):
                - Region 1 (0-70%): 70% × 100% = 70.0%
                - Region 2 (70%-90%): 20% × 90% = 18.0%
                - Region 3 (90%-100%): 10% × 70% = 7.0%
                - Region 4 (100%-115.5%): 15.5% × 15% = 2.325%
                - Total: 97.325% (0.97325)
            local_mult = 1.0 + 0.97325 = 1.97325
            actual_recharge = 60.0 / 1.97325 = 30.41

        Expected: ~30.41 seconds
        """
        calculator = RechargeCalculator()
        result = calculator.calculate_recharge(
            base_recharge=60.0,
            local_bonuses=[0.385, 0.385, 0.385],
            global_bonus=0.0,
            archetype_cap=5.0,
        )

        # Verify ED applied correctly
        assert result.local_recharge_bonus_pre_ed == pytest.approx(1.155, abs=0.001)
        # After ED: should be reduced significantly
        assert result.local_recharge_bonus_after_ed == pytest.approx(0.97325, abs=0.01)
        assert result.actual_recharge == pytest.approx(30.41, abs=0.1)


class TestHastenAndSetBonuses:
    """Test Case 3: Hasten + Set Bonuses (from Spec 07)"""

    def test_hasten_plus_set_bonuses(self):
        """
        Power: Hasten itself
        Level: 50

        Input:
            - Base Recharge: 120.0 seconds (Hasten)
            - Local Bonuses: [0.424, 0.424] (two Level 50 Recharge IOs)
            - Global Bonus: 1.00 (+100% from set bonuses, not including Hasten)
            - Archetype Cap: 5.0

        Calculation:
            Total Local Bonus: 84.8% (0.848)
            After ED: 70% + (14.8% × 0.9) = 83.32% (0.8332)
            local_mult = 1.8332
            global_mult = 2.00
            total = 1.8332 × 2.00 = 3.6664
            actual_recharge = 120 / 3.6664 = 32.73

        Expected: ~32.73 seconds
        """
        calculator = RechargeCalculator()
        result = calculator.calculate_recharge(
            base_recharge=120.0,
            local_bonuses=[0.424, 0.424],
            global_bonus=1.00,
            archetype_cap=5.0,
        )

        assert result.local_recharge_bonus_pre_ed == pytest.approx(0.848, abs=0.001)
        assert result.local_recharge_bonus_after_ed == pytest.approx(0.8332, abs=0.01)
        assert result.local_recharge_multiplier == pytest.approx(1.8332, abs=0.01)
        assert result.global_recharge_multiplier == pytest.approx(2.0, abs=0.01)
        assert result.total_multiplier == pytest.approx(3.6664, abs=0.01)
        assert result.actual_recharge == pytest.approx(32.73, abs=0.1)


class TestExceedingArchetypeCap:
    """Test Case 4: Exceeding Archetype Cap (from Spec 07)"""

    def test_exceeding_archetype_cap(self):
        """
        Power: 60s power with extreme recharge
        Level: 50

        Input:
            - Base Recharge: 60.0 seconds
            - Local Bonuses: [0.424, 0.424, 0.424] (three Level 50 Recharge IOs)
            - Global Bonus: 2.50 (+250% global recharge)
            - Archetype Cap: 5.0 (400%)

        Calculation:
            Local After ED: ~116% (1.16)
            local_mult = 2.16
            global_mult = 3.50
            Uncapped Total: 2.16 × 3.50 = 7.56
            Exceeds cap: 7.56 > 5.0
            Capped multiplier: 5.00
            actual_recharge = 60 / 5.00 = 12.0

        Expected: 12.0 seconds (capped)
        """
        calculator = RechargeCalculator()
        result = calculator.calculate_recharge(
            base_recharge=60.0,
            local_bonuses=[0.424, 0.424, 0.424],
            global_bonus=2.50,
            archetype_cap=5.0,
        )

        # Verify cap is applied
        assert result.total_multiplier > 5.0  # Uncapped would exceed
        assert result.actual_recharge == pytest.approx(12.0, abs=0.01)
        assert result.is_capped is True


class TestZeroRechargePower:
    """Test Case 5: Zero Recharge Power (Toggle/Auto) (from Spec 07)"""

    def test_zero_recharge_power(self):
        """
        Power: Toggle or Auto power
        Level: 50

        Input:
            - Base Recharge: 0.0 seconds
            - Local Bonuses: [0.424] (enhancement present but irrelevant)
            - Global Bonus: 0.70
            - Archetype Cap: 5.0

        Expected: 0.0 seconds (no recharge time)
        """
        calculator = RechargeCalculator()
        result = calculator.calculate_recharge(
            base_recharge=0.0,
            local_bonuses=[0.424],
            global_bonus=0.70,
            archetype_cap=5.0,
        )

        assert result.base_recharge == 0.0
        assert result.actual_recharge == 0.0
        assert result.is_capped is False


class TestGlobalRechargeCalculation:
    """Test calculating global recharge from multiple sources"""

    def test_global_recharge_with_hasten(self):
        """
        Test global recharge: 5× LotG + 4× set bonuses + Hasten

        Input:
            - Set bonuses: 5× +7.5% LotG + 4× +6.25% sets
            - Hasten: +70%

        Calculation:
            LotG: 5 × 0.075 = 0.375
            Sets: 4 × 0.0625 = 0.25
            Hasten: 0.70
            Total: 0.375 + 0.25 + 0.70 = 1.325

        Expected: 1.325 (132.5% bonus)
        """
        calculator = RechargeCalculator()
        global_bonus = calculator.calculate_global_recharge(
            set_bonuses=[0.075] * 5 + [0.0625] * 4,
            hasten_active=True,
            other_buffs=None,
        )

        assert global_bonus == pytest.approx(1.325, abs=0.001)

    def test_global_recharge_with_incarnate(self):
        """
        Test global recharge with Incarnate ability

        Input:
            - Set bonuses: 5× +7.5% LotG
            - Hasten: +70%
            - Spiritual Alpha T4: +20%

        Calculation:
            Total: 0.375 + 0.70 + 0.20 = 1.275

        Expected: 1.275
        """
        calculator = RechargeCalculator()
        global_bonus = calculator.calculate_global_recharge(
            set_bonuses=[0.075] * 5,
            hasten_active=True,
            other_buffs=[0.20],  # Spiritual Alpha
        )

        assert global_bonus == pytest.approx(1.275, abs=0.001)


class TestPermaHasten:
    """Test perma-Hasten calculation"""

    def test_perma_hasten_achieved(self):
        """
        Test perma-Hasten with sufficient global recharge

        Input:
            - Global without Hasten: 82.5% (0.825)
            - Local in Hasten: 95% (0.95)

        Calculation:
            local_mult = 1.95
            global_mult = 1.825
            total_mult = 3.559
            actual_recharge = 120 / 3.559 = 33.71
            33.71 <= 116.83 → TRUE (perma achieved)

        Expected: True, 33.71 seconds
        """
        calculator = RechargeCalculator()
        is_perma, recharge = calculator.check_perma_hasten(
            global_recharge_without_hasten=0.825, local_recharge_in_hasten=0.95
        )

        assert is_perma is True
        assert recharge == pytest.approx(33.71, abs=0.1)

    def test_perma_hasten_not_achieved(self):
        """
        Test perma-Hasten with insufficient global recharge

        Input:
            - Global without Hasten: 0% (0.0) - no global recharge
            - Local in Hasten: 0% (0.0) - unslotted Hasten

        Calculation:
            total_mult = 1.0 × 1.0 = 1.0
            actual_recharge = 120 / 1.0 = 120.0
            max_allowed = 120 - 1.17 - 2.0 = 116.83
            120.0 > 116.83 → FALSE (not perma)

        Expected: False, 120.0 seconds
        """
        calculator = RechargeCalculator()
        is_perma, recharge = calculator.check_perma_hasten(
            global_recharge_without_hasten=0.0, local_recharge_in_hasten=0.0
        )

        assert is_perma is False
        assert recharge == pytest.approx(120.0, abs=0.1)


class TestValidation:
    """Test validation functions"""

    def test_invalid_negative_recharge(self):
        """Test that negative base recharge raises error"""
        with pytest.raises(InvalidRechargeConfigError, match="cannot be negative"):
            validate_recharge_config(-1.0, [], 0.0, 5.0)

    def test_invalid_negative_local_bonus(self):
        """Test that negative local bonus raises error"""
        with pytest.raises(
            InvalidRechargeConfigError, match="Local bonus cannot be negative"
        ):
            validate_recharge_config(60.0, [-0.5], 0.0, 5.0)

    def test_invalid_negative_global_bonus(self):
        """Test that negative global bonus raises error"""
        with pytest.raises(
            InvalidRechargeConfigError, match="Global bonus cannot be negative"
        ):
            validate_recharge_config(60.0, [], -0.5, 5.0)

    def test_invalid_zero_cap(self):
        """Test that zero archetype cap raises error"""
        with pytest.raises(InvalidRechargeConfigError, match="must be positive"):
            validate_recharge_config(60.0, [], 0.0, 0.0)


class TestFormatting:
    """Test display formatting functions"""

    def test_format_recharge_time(self):
        """Test formatting recharge time"""
        calculator = RechargeCalculator()
        assert calculator.format_recharge_display(16.15) == "16.15s"
        assert calculator.format_recharge_display(0.0) == "N/A"

    def test_format_global_recharge_display(self):
        """Test formatting global recharge percentage"""
        calculator = RechargeCalculator()
        # Storage: 0.70 → Display: 170.0%
        assert calculator.format_global_recharge_display(0.70) == "170.0%"
        # Storage: 1.525 → Display: 252.5%
        assert calculator.format_global_recharge_display(1.525) == "252.5%"
        # Storage: 0.0 → Display: 100.0% (base, no bonuses)
        assert calculator.format_global_recharge_display(0.0) == "100.0%"


class TestEdgeCases:
    """Test edge cases and special scenarios"""

    def test_very_high_local_bonuses(self):
        """Test with extreme local recharge slotting"""
        calculator = RechargeCalculator()
        # Six Level 50 IOs (wasteful, but test ED correctly handles it)
        result = calculator.calculate_recharge(
            base_recharge=60.0,
            local_bonuses=[0.424] * 6,  # 254.4% total
            global_bonus=0.0,
            archetype_cap=5.0,
        )

        # Should have severe ED penalty
        assert result.local_recharge_bonus_pre_ed == pytest.approx(2.544, abs=0.01)
        # After ED, should be much lower
        assert result.local_recharge_bonus_after_ed < 1.5
        # Still should calculate correctly
        assert result.actual_recharge > 0

    def test_exactly_at_cap(self):
        """Test power exactly at archetype cap"""
        calculator = RechargeCalculator()
        # Arrange for total multiplier to be exactly 5.0
        result = calculator.calculate_recharge(
            base_recharge=60.0,
            local_bonuses=[0.424] * 2,  # ~83.32% after ED
            global_bonus=1.7297,  # Chosen to hit exactly 5.0 multiplier
            archetype_cap=5.0,
        )

        # Should be at or very close to cap
        assert result.actual_recharge == pytest.approx(12.0, abs=0.1)
