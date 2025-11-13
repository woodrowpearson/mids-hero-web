"""
Test suite for Power Endurance Calculator

Tests based on comprehensive test cases from Spec 06, Section 4.
All expected values are exact calculations from the specification.
"""

import pytest

from app.calculations.core.effect import Effect
from app.calculations.core.effect_types import EffectType
from app.calculations.powers.endurance_calculator import (
    ArchetypeEnduranceStats,
    EnduranceCalculator,
    PowerType,
    validate_power_endurance_config,
    validate_recovery_config,
    InvalidPowerConfigError,
    InvalidRecoveryConfigError,
)


class TestBasicClickPowerCost:
    """Test Case 1: Basic Click Power Endurance Cost (from Spec 06)"""

    def test_basic_click_power_unslotted(self):
        """
        Power: Footstomp (Super Strength)
        Level: 50
        Power Type: Click

        Input:
            - Base EndCost: 13.0
            - ActivatePeriod: N/A (click power)
            - EnduranceDiscount effects: None (unslotted)
            - Power type: Click

        Expected: 13.0 endurance per activation
        """
        calculator = EnduranceCalculator()
        result = calculator.calculate_power_cost(
            base_end_cost=13.0,
            activate_period=0.0,
            power_type=PowerType.CLICK,
            end_discount_effects=[],
        )

        assert result.base_cost == 13.0
        assert result.modified_cost == pytest.approx(13.0, abs=0.01)
        assert result.cost_per_second == 13.0
        assert result.discount_applied == 0.0
        assert result.is_toggle is False


class TestClickPowerWithEndRdx:
    """Test Case 2: Click Power with EndRdx Slotting (from Spec 06)"""

    def test_click_power_with_endrx(self):
        """
        Power: Footstomp (Super Strength)
        Level: 50
        Power Type: Click

        Input:
            - Base EndCost: 13.0
            - EnduranceDiscount: 56% (3× level 50 EndRdx SOs, after ED)
            - Power type: Click

        Calculation:
            modified_cost = 13.0 * (1.0 - 0.56) = 5.72

        Expected: 5.72 endurance per activation
        """
        # EndRdx effect after ED
        endrx_effect = Effect(
            unique_id=1,
            effect_type=EffectType.ENDURANCE_DISCOUNT,
            magnitude=0.9566,  # Pre-ED (3× 33.33%)
            buffed_magnitude=0.56,  # Post-ED
        )

        calculator = EnduranceCalculator()
        result = calculator.calculate_power_cost(
            base_end_cost=13.0,
            activate_period=0.0,
            power_type=PowerType.CLICK,
            end_discount_effects=[endrx_effect],
        )

        assert result.base_cost == 13.0
        assert result.modified_cost == pytest.approx(5.72, abs=0.01)
        assert result.discount_applied == pytest.approx(0.56, abs=0.01)


class TestTogglePowerBaseCost:
    """Test Case 3: Toggle Power Base Cost (from Spec 06)"""

    def test_toggle_power_unslotted(self):
        """
        Power: Tough (Fighting pool toggle)
        Level: 50
        Power Type: Toggle

        Input:
            - Base EndCost: 0.26
            - ActivatePeriod: 0.5 seconds
            - EnduranceDiscount: None (unslotted)
            - Power type: Toggle

        Calculation:
            cost_per_second = 0.26 / 0.5 = 0.52 end/sec

        Expected: 0.52 end/sec
        """
        calculator = EnduranceCalculator()
        result = calculator.calculate_power_cost(
            base_end_cost=0.26,
            activate_period=0.5,
            power_type=PowerType.TOGGLE,
            end_discount_effects=[],
        )

        assert result.base_cost == 0.26
        assert result.cost_per_second == pytest.approx(0.52, abs=0.01)
        assert result.modified_cost == pytest.approx(0.52, abs=0.01)
        assert result.is_toggle is True


class TestTogglePowerWithEndRdx:
    """Test Case 4: Toggle Power with EndRdx Slotting (from Spec 06)"""

    def test_toggle_power_with_endrx(self):
        """
        Power: Tough (Fighting pool toggle)
        Level: 50
        Power Type: Toggle

        Input:
            - Base EndCost: 0.26
            - ActivatePeriod: 0.5 seconds
            - EnduranceDiscount: 42% (1× level 50 EndRdx IO)
            - Power type: Toggle

        Calculation:
            cost_per_second = 0.26 / 0.5 = 0.52 end/sec
            modified_cost = 0.52 * (1.0 - 0.42) = 0.3016

        Expected: 0.30 end/sec
        """
        endrx_effect = Effect(
            unique_id=1,
            effect_type=EffectType.ENDURANCE_DISCOUNT,
            magnitude=0.42,
            buffed_magnitude=0.42,
        )

        calculator = EnduranceCalculator()
        result = calculator.calculate_power_cost(
            base_end_cost=0.26,
            activate_period=0.5,
            power_type=PowerType.TOGGLE,
            end_discount_effects=[endrx_effect],
        )

        assert result.modified_cost == pytest.approx(0.30, abs=0.01)


class TestBaseRecovery:
    """Test Case 5: Base Endurance Recovery (from Spec 06)"""

    def test_base_recovery_no_bonuses(self):
        """
        Character: Scrapper, level 50
        Recovery Bonuses: None

        Input:
            - Archetype BaseRecovery: 1.67
            - Recovery effects: None
            - Max endurance: 100.0 (base)

        Constants:
            - BASE_MAGIC = 1.666667
            - BASE_MAX_ENDURANCE = 100.0

        Calculation:
            recovery_total = 1.0 (100%)
            max_end_multiplier = (100.0 / 100.0) + 1.0 = 2.0
            recovery_numeric = 1.0 * 1.67 * 1.666667 * 2.0 = 5.566667 end/sec

        Expected: 5.57 end/sec
        """
        calculator = EnduranceCalculator()
        result = calculator.calculate_recovery_rate(recovery_effects=[], max_endurance=100.0)

        assert result.recovery_total == pytest.approx(1.0, abs=0.01)
        assert result.recovery_numeric == pytest.approx(5.57, abs=0.01)
        assert result.recovery_percentage == pytest.approx(100.0, abs=0.1)
        assert result.is_capped is False


class TestRecoveryWithStamina:
    """Test Case 6: Endurance Recovery with Stamina (from Spec 06)"""

    def test_recovery_with_stamina(self):
        """
        Character: Scrapper, level 50
        Recovery Bonuses: Stamina (+25%)

        Input:
            - Archetype BaseRecovery: 1.67
            - Stamina: +0.25 (25% recovery)
            - Max endurance: 100.0

        Calculation:
            recovery_total = 1.0 + 0.25 = 1.25 (125%)
            max_end_multiplier = 2.0
            recovery_numeric = 1.25 * 1.67 * 1.666667 * 2.0 = 6.958334 end/sec

        Expected: 6.96 end/sec
        """
        stamina = Effect(
            unique_id=1, effect_type=EffectType.RECOVERY, magnitude=0.25
        )

        calculator = EnduranceCalculator()
        result = calculator.calculate_recovery_rate(
            recovery_effects=[stamina], max_endurance=100.0
        )

        assert result.recovery_total == pytest.approx(1.25, abs=0.01)
        assert result.recovery_numeric == pytest.approx(6.96, abs=0.01)
        assert result.recovery_percentage == pytest.approx(125.0, abs=0.1)


class TestRecoveryWithMultiplePowers:
    """Test Case 7: Recovery with Stamina + Physical Perfection (from Spec 06)"""

    def test_recovery_with_multiple_powers(self):
        """
        Character: Scrapper, level 50
        Recovery Bonuses: Stamina + Physical Perfection

        Input:
            - Stamina: +0.25 (25%)
            - Physical Perfection: +0.10 (10%)
            - Max endurance: 100.0

        Calculation:
            recovery_total = 1.0 + 0.25 + 0.10 = 1.35 (135%)
            recovery_numeric = 1.35 * 1.67 * 1.666667 * 2.0 = 7.530001 end/sec

        Expected: 7.53 end/sec
        """
        stamina = Effect(
            unique_id=1, effect_type=EffectType.RECOVERY, magnitude=0.25
        )
        phys_perf = Effect(
            unique_id=2, effect_type=EffectType.RECOVERY, magnitude=0.10
        )

        calculator = EnduranceCalculator()
        result = calculator.calculate_recovery_rate(
            recovery_effects=[stamina, phys_perf], max_endurance=100.0
        )

        assert result.recovery_total == pytest.approx(1.35, abs=0.01)
        assert result.recovery_numeric == pytest.approx(7.53, abs=0.01)


class TestMaxEndurance:
    """Test Case 8: Max Endurance with Bonuses (from Spec 06)"""

    def test_max_endurance_with_bonuses(self):
        """
        Character: Scrapper, level 50
        Endurance Bonuses: IO set bonuses

        Input:
            - 5× +2.25% max endurance IO bonuses = +11.25 total

        Calculation:
            max_end = 100.0 + 11.25 = 111.25

        Expected: 111.25
        """
        bonuses = [
            Effect(unique_id=i, effect_type=EffectType.ENDURANCE, magnitude=2.25)
            for i in range(1, 6)
        ]

        calculator = EnduranceCalculator()
        max_end = calculator.calculate_max_endurance(bonuses)

        assert max_end == pytest.approx(111.25, abs=0.01)


class TestRecoveryWithIncreasedMaxEnd:
    """Test Case 9: Recovery with Increased Max Endurance (from Spec 06)"""

    def test_recovery_with_increased_max_end(self):
        """
        Character: Scrapper, level 50
        Recovery: Stamina (+25%)
        Max Endurance: 110.0 (+10 from set bonuses)

        Calculation:
            recovery_total = 1.25 (125%)
            max_end_multiplier = (110.0 / 100.0) + 1.0 = 2.1
            recovery_numeric = 1.25 * 1.67 * 1.666667 * 2.1 = 7.306251 end/sec

        Expected: 7.31 end/sec (5% more than with 100 max end)
        """
        stamina = Effect(
            unique_id=1, effect_type=EffectType.RECOVERY, magnitude=0.25
        )

        calculator = EnduranceCalculator()
        result = calculator.calculate_recovery_rate(
            recovery_effects=[stamina], max_endurance=110.0
        )

        assert result.recovery_numeric == pytest.approx(7.31, abs=0.01)


class TestNetRecoveryPositive:
    """Test Case 10: Net Recovery (Positive) (from Spec 06)"""

    def test_net_recovery_positive(self):
        """
        Character: Scrapper, level 50
        Recovery: Stamina (7.53 end/sec)
        Toggle Usage: 3 toggles (0.63 end/sec total)

        Calculation:
            endurance_usage = 0.30 + 0.26 + 0.07 = 0.63 end/sec
            net_recovery = 7.53 - 0.63 = 6.90 end/sec

        Expected: +6.90 end/sec (positive)
        """
        calculator = EnduranceCalculator()
        result = calculator.calculate_net_recovery(
            recovery_numeric=7.53,
            toggle_costs=[0.30, 0.26, 0.07],
            max_endurance=100.0,
        )

        assert result.endurance_usage == pytest.approx(0.63, abs=0.01)
        assert result.net_recovery == pytest.approx(6.90, abs=0.01)
        assert result.is_positive is True
        assert result.time_to_full == pytest.approx(13.28, abs=0.1)


class TestNetRecoveryNegative:
    """Test Case 11: Net Recovery (Negative) (from Spec 06)"""

    def test_net_recovery_negative(self):
        """
        Character: Scrapper, level 50
        Recovery: Base only (5.57 end/sec, no Stamina)
        Toggle Usage: Many toggles (6.0 end/sec total)

        Calculation:
            net_recovery = 5.57 - 6.0 = -0.43 end/sec
            time_to_zero = 100.0 / 0.43 = 232.56 seconds

        Expected: -0.43 end/sec (draining)
        """
        calculator = EnduranceCalculator()
        result = calculator.calculate_net_recovery(
            recovery_numeric=5.57, toggle_costs=[6.0], max_endurance=100.0
        )

        assert result.net_recovery == pytest.approx(-0.43, abs=0.01)
        assert result.is_positive is False
        assert result.time_to_zero == pytest.approx(232.56, abs=1.0)


class TestRecoveryAtCap:
    """Test Case 12: Recovery at Cap (from Spec 06)"""

    def test_recovery_at_cap(self):
        """
        Character: Scrapper, level 50
        Recovery Bonuses: Extreme recovery build

        Input:
            - Stamina: +0.25
            - Physical Perfection: +0.10
            - Set bonuses: +0.50
            - Other powers: +3.50
            - Total uncapped: +4.35 → 5.35 (535%)
            - RecoveryCap: 5.0 (500%)

        Calculation:
            recovery_total_uncapped = 1.0 + 4.35 = 5.35 (535%)
            recovery_total_capped = min(5.35, 5.0) = 5.0 (500%)
            recovery_numeric = 5.0 * 1.67 * 1.666667 * 2.0 = 27.833335 end/sec

        Expected: 27.83 end/sec (capped at 500%)
        """
        recovery_effects = [
            Effect(unique_id=1, effect_type=EffectType.RECOVERY, magnitude=0.25),
            Effect(unique_id=2, effect_type=EffectType.RECOVERY, magnitude=0.10),
            Effect(unique_id=3, effect_type=EffectType.RECOVERY, magnitude=0.50),
            Effect(unique_id=4, effect_type=EffectType.RECOVERY, magnitude=3.50),
        ]

        calculator = EnduranceCalculator()
        result = calculator.calculate_recovery_rate(
            recovery_effects=recovery_effects, max_endurance=100.0
        )

        assert result.recovery_total == pytest.approx(5.0, abs=0.01)
        assert result.recovery_numeric == pytest.approx(27.83, abs=0.1)
        assert result.is_capped is True
        assert result.uncapped_percentage == pytest.approx(535.0, abs=1.0)


class TestValidation:
    """Test validation functions"""

    def test_invalid_negative_cost(self):
        """Test that negative endurance cost raises error"""
        with pytest.raises(InvalidPowerConfigError, match="cannot be negative"):
            validate_power_endurance_config(-1.0, 0.5, PowerType.CLICK)

    def test_invalid_toggle_period(self):
        """Test that toggle with zero period raises error"""
        with pytest.raises(InvalidPowerConfigError, match="activate_period > 0"):
            validate_power_endurance_config(0.26, 0.0, PowerType.TOGGLE)

    def test_invalid_max_endurance(self):
        """Test that negative max endurance raises error"""
        with pytest.raises(InvalidRecoveryConfigError, match="must be positive"):
            validate_recovery_config(-1.0, [])


class TestFormatting:
    """Test display formatting functions"""

    def test_format_click_cost(self):
        """Test formatting click power cost"""
        calculator = EnduranceCalculator()
        assert calculator.format_endurance_display(13.0, is_toggle=False) == "13.00"

    def test_format_toggle_cost(self):
        """Test formatting toggle power cost"""
        calculator = EnduranceCalculator()
        assert calculator.format_endurance_display(0.52, is_toggle=True) == "0.52/s"
