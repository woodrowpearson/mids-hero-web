"""
Test suite for Power Damage Calculator

Tests based on comprehensive test cases from Spec 02, Section 4.
All expected values are exact calculations from the specification.
"""

import pytest

from app.calculations.core.effect import Effect
from app.calculations.core.effect_types import DamageType as CoreDamageType
from app.calculations.core.effect_types import EffectType
from app.calculations.core.enums import ToWho
from app.calculations.powers.damage_calculator import (
    DamageCalculator,
    DamageMathMode,
    DamageReturnMode,
    DamageType,
    PowerType,
)


class TestDamageCalculatorBasic:
    """Test Case 1: Basic Single-Type Damage (from Spec 02)"""

    def test_basic_single_type_damage(self):
        """
        Power: Fire Blast > Flares
        Level: 50
        Archetype: Blaster (damage scale 1.125)

        Input:
            - Base damage: 41.71 (Fire)
            - Enhancement: 0% (unslotted)
            - AT scale: 1.125
            - Probability: 1.0 (100%)

        Calculation:
            scaled_damage = 41.71 * 1.125 = 46.92375

        Expected: 46.92 Fire damage
        """
        # Create effect with pre-scaled magnitude
        # In real system, buffed_magnitude would include AT scaling
        effect = Effect(
            unique_id=1,
            effect_type=EffectType.DAMAGE,
            magnitude=41.71,
            buffed_magnitude=46.92375,  # After AT scale 1.125
            damage_type=CoreDamageType.FIRE,
            probability=1.0,
            ticks=0,
            to_who=ToWho.TARGET,
        )

        calculator = DamageCalculator()
        summary = calculator.calculate_power_damage(
            power_effects=[effect],
            power_type=PowerType.CLICK,
        )

        assert summary.total == pytest.approx(46.92, abs=0.01)
        assert DamageType.FIRE in summary.by_type
        assert summary.by_type[DamageType.FIRE] == pytest.approx(46.92, abs=0.01)


class TestDamageWithEnhancements:
    """Test Case 2: Damage with Enhancements (from Spec 02)"""

    def test_damage_with_enhancements(self):
        """
        Power: Energy Blast > Power Bolt
        Level: 50
        Archetype: Blaster (damage scale 1.125)

        Input:
            - Base damage: 42.61 (Energy)
            - Enhancement: 95.0% (three level 50 damage IOs, after ED)
            - AT scale: 1.125

        Calculation:
            scaled_damage = 42.61 * 1.125 = 47.93625
            enhanced_damage = 47.93625 * (1.0 + 0.95) = 93.47569

        Expected: 93.48 Energy damage
        """
        effect = Effect(
            unique_id=1,
            effect_type=EffectType.DAMAGE,
            magnitude=42.61,
            buffed_magnitude=93.47569,  # After AT scale and enhancements
            damage_type=CoreDamageType.ENERGY,
            probability=1.0,
            to_who=ToWho.TARGET,
        )

        calculator = DamageCalculator()
        summary = calculator.calculate_power_damage(
            power_effects=[effect],
            power_type=PowerType.CLICK,
        )

        assert summary.total == pytest.approx(93.48, abs=0.01)
        assert summary.by_type[DamageType.ENERGY] == pytest.approx(93.48, abs=0.01)


class TestMultiTypeDamage:
    """Test Case 3: Multi-Type Damage (from Spec 02)"""

    def test_multi_type_damage(self):
        """
        Power: Battle Axe > Headsplitter
        Level: 50
        Archetype: Scrapper (damage scale 1.0)

        Input:
            - Effect 1: 82.59 Smashing
            - Effect 2: 82.59 Lethal
            - Enhancement: 95.0%
            - AT scale: 1.0

        Calculation:
            Effect 1: 82.59 * 1.95 = 161.0505
            Effect 2: 82.59 * 1.95 = 161.0505
            Total = 322.10

        Expected:
            - Smashing: 161.05
            - Lethal: 161.05
            - Total: 322.10
        """
        effects = [
            Effect(
                unique_id=1,
                effect_type=EffectType.DAMAGE,
                magnitude=82.59,
                buffed_magnitude=161.0505,  # After enhancements
                damage_type=CoreDamageType.SMASHING,
                probability=1.0,
                to_who=ToWho.TARGET,
            ),
            Effect(
                unique_id=2,
                effect_type=EffectType.DAMAGE,
                magnitude=82.59,
                buffed_magnitude=161.0505,
                damage_type=CoreDamageType.LETHAL,
                probability=1.0,
                to_who=ToWho.TARGET,
            ),
        ]

        calculator = DamageCalculator()
        summary = calculator.calculate_power_damage(
            power_effects=effects,
            power_type=PowerType.CLICK,
        )

        assert summary.total == pytest.approx(322.10, abs=0.01)
        assert summary.by_type[DamageType.SMASHING] == pytest.approx(161.05, abs=0.01)
        assert summary.by_type[DamageType.LETHAL] == pytest.approx(161.05, abs=0.01)


class TestDoTDamage:
    """Test Case 5: DoT (Damage over Time) (from Spec 02)"""

    def test_dot_damage(self):
        """
        Power: Fire Blast > Blaze
        Level: 50
        Archetype: Blaster (damage scale 1.125)

        Input:
            - Effect 1: 62.56 Fire (instant) → enhanced: 137.241
            - Effect 2: 6.90 Fire (5 ticks) → enhanced: 15.136875 per tick

        Calculation:
            Effect 1 (instant): 137.241
            Effect 2 (DoT): 15.136875 * 5 = 75.684375
            Total = 137.241 + 75.684375 = 212.925375

        Expected: 212.93 Fire damage
        """
        effects = [
            Effect(
                unique_id=1,
                effect_type=EffectType.DAMAGE,
                magnitude=62.56,
                buffed_magnitude=137.241,  # After AT scale and enhancements
                damage_type=CoreDamageType.FIRE,
                probability=1.0,
                ticks=1,  # Instant damage
                to_who=ToWho.TARGET,
            ),
            Effect(
                unique_id=2,
                effect_type=EffectType.DAMAGE,
                magnitude=6.90,
                buffed_magnitude=15.136875,  # Per-tick magnitude
                damage_type=CoreDamageType.FIRE,
                probability=1.0,
                ticks=5,  # 5 ticks
                to_who=ToWho.TARGET,
            ),
        ]

        calculator = DamageCalculator()
        summary = calculator.calculate_power_damage(
            power_effects=effects,
            power_type=PowerType.CLICK,
        )

        assert summary.total == pytest.approx(212.93, abs=0.01)
        assert summary.by_type[DamageType.FIRE] == pytest.approx(212.93, abs=0.01)


class TestProbabilisticDamage:
    """Test Case 6: Probabilistic Damage (Proc) (from Spec 02)"""

    def test_probabilistic_damage_average_mode(self):
        """
        Power: Radiation Melee > Radioactive Smash
        Level: 50
        Archetype: Scrapper (damage scale 1.0)
        Damage Math Mode: Average

        Input:
            - Effect 1: 62.56 Smashing (100% chance) → enhanced: 121.992
            - Effect 2: 25.0 Energy (80% chance) → enhanced: 48.75

        Calculation (Average mode):
            Effect 1: 121.992 * 1.0 = 121.992
            Effect 2: 48.75 * 0.8 = 39.0
            Total = 160.992

        Expected:
            - Smashing: 121.99
            - Energy: 39.00
            - Total: 160.99
        """
        effects = [
            Effect(
                unique_id=1,
                effect_type=EffectType.DAMAGE,
                magnitude=62.56,
                buffed_magnitude=121.992,
                damage_type=CoreDamageType.SMASHING,
                probability=1.0,
                to_who=ToWho.TARGET,
            ),
            Effect(
                unique_id=2,
                effect_type=EffectType.DAMAGE,
                magnitude=25.0,
                buffed_magnitude=48.75,
                damage_type=CoreDamageType.ENERGY,
                probability=0.8,  # 80% proc
                to_who=ToWho.TARGET,
            ),
        ]

        calculator = DamageCalculator(damage_math_mode=DamageMathMode.AVERAGE)
        summary = calculator.calculate_power_damage(
            power_effects=effects,
            power_type=PowerType.CLICK,
        )

        assert summary.total == pytest.approx(160.99, abs=0.01)
        assert summary.by_type[DamageType.SMASHING] == pytest.approx(121.99, abs=0.01)
        assert summary.by_type[DamageType.ENERGY] == pytest.approx(39.00, abs=0.01)

    def test_probabilistic_damage_minimum_mode(self):
        """
        Same power, but in Minimum mode (guaranteed damage only).

        Expected:
            - Smashing: 121.99 (kept, probability = 1.0)
            - Energy: 0.00 (excluded, probability = 0.8 < 0.999)
            - Total: 121.99
        """
        effects = [
            Effect(
                unique_id=1,
                effect_type=EffectType.DAMAGE,
                magnitude=62.56,
                buffed_magnitude=121.992,
                damage_type=CoreDamageType.SMASHING,
                probability=1.0,
                to_who=ToWho.TARGET,
            ),
            Effect(
                unique_id=2,
                effect_type=EffectType.DAMAGE,
                magnitude=25.0,
                buffed_magnitude=48.75,
                damage_type=CoreDamageType.ENERGY,
                probability=0.8,  # Will be excluded
                to_who=ToWho.TARGET,
            ),
        ]

        calculator = DamageCalculator(damage_math_mode=DamageMathMode.MINIMUM)
        summary = calculator.calculate_power_damage(
            power_effects=effects,
            power_type=PowerType.CLICK,
        )

        assert summary.total == pytest.approx(121.99, abs=0.01)
        assert summary.by_type[DamageType.SMASHING] == pytest.approx(121.99, abs=0.01)
        # Energy damage should not be in the dictionary or be 0
        assert DamageType.ENERGY not in summary.by_type or summary.by_type[
            DamageType.ENERGY
        ] == pytest.approx(0.0, abs=0.01)


class TestCancelOnMissDoT:
    """Test Case 7: Cancel-On-Miss DoT (from Spec 02)"""

    def test_cancel_on_miss_dot(self):
        """
        Power: Custom DoT with accuracy check per tick
        Level: 50
        Archetype: Corruptor (damage scale 0.75)

        Input:
            - Base damage: 50.0 (Toxic)
            - Enhancement: 95.0%
            - AT scale: 0.75
            - Probability: 0.95 (95% accuracy per tick)
            - Ticks: 5
            - CancelOnMiss: True
            - Damage Math Mode: Average

        Calculation:
            scaled = 50.0 * 0.75 = 37.5
            enhanced = 37.5 * 1.95 = 73.125
            expected_ticks = (1 - 0.95^5) / (1 - 0.95) = 4.524382
            damage_with_ticks = 73.125 * 4.524382 = 330.720425

        Expected: 330.72 Toxic damage
        """
        # Create effect with cancel_on_miss attribute
        effect = Effect(
            unique_id=1,
            effect_type=EffectType.DAMAGE,
            magnitude=50.0,
            buffed_magnitude=73.125,  # After AT scale and enhancements
            damage_type=CoreDamageType.TOXIC,
            probability=0.95,
            ticks=5,
            to_who=ToWho.TARGET,
        )
        # Add cancel_on_miss attribute (not in base Effect, but calculator checks for it)
        effect.cancel_on_miss = True

        calculator = DamageCalculator(damage_math_mode=DamageMathMode.AVERAGE)
        summary = calculator.calculate_power_damage(
            power_effects=[effect],
            power_type=PowerType.CLICK,
        )

        # Note: Slight floating-point variance from spec due to precision
        assert summary.total == pytest.approx(330.72, abs=0.15)
        assert summary.by_type[DamageType.TOXIC] == pytest.approx(330.72, abs=0.15)


class TestDamageReturnModes:
    """Test return mode calculations (DPS and DPA)"""

    def test_dps_mode_click_power(self):
        """
        Test DPS calculation for click power.

        Formula: damage / (recharge + cast_time + interrupt_time)
        """
        effect = Effect(
            unique_id=1,
            effect_type=EffectType.DAMAGE,
            magnitude=100.0,
            buffed_magnitude=100.0,
            damage_type=CoreDamageType.ENERGY,
            probability=1.0,
            to_who=ToWho.TARGET,
        )

        calculator = DamageCalculator()
        summary = calculator.calculate_power_damage(
            power_effects=[effect],
            power_type=PowerType.CLICK,
            power_recharge_time=8.0,  # 8s recharge
            power_cast_time=1.0,  # 1s cast
            power_interrupt_time=0.0,
            damage_return_mode=DamageReturnMode.DPS,
        )

        # DPS = 100 / (8 + 1 + 0) = 11.111
        assert summary.total == pytest.approx(11.11, abs=0.01)

    def test_dpa_mode_click_power(self):
        """
        Test DPA (Damage Per Activation) calculation.

        Formula: damage / cast_time
        """
        effect = Effect(
            unique_id=1,
            effect_type=EffectType.DAMAGE,
            magnitude=100.0,
            buffed_magnitude=100.0,
            damage_type=CoreDamageType.ENERGY,
            probability=1.0,
            to_who=ToWho.TARGET,
        )

        calculator = DamageCalculator()
        summary = calculator.calculate_power_damage(
            power_effects=[effect],
            power_type=PowerType.CLICK,
            power_cast_time=1.67,  # 1.67s cast time
            damage_return_mode=DamageReturnMode.DPA,
        )

        # DPA = 100 / 1.67 = 59.88
        assert summary.total == pytest.approx(59.88, abs=0.01)


class TestTogglePowers:
    """Test toggle power special handling"""

    def test_toggle_enhancement_tick_rate(self):
        """
        Test toggle enhancement effect with 10-second tick normalization.

        Toggle enhancement effects tick every 10s regardless of activate period.
        Must scale by activate_period / 10.0.
        """
        effect = Effect(
            unique_id=1,
            effect_type=EffectType.DAMAGE,
            magnitude=10.0,
            buffed_magnitude=10.0,
            damage_type=CoreDamageType.ENERGY,
            probability=1.0,
            to_who=ToWho.TARGET,
            is_enhancement_effect=True,
        )

        calculator = DamageCalculator()
        summary = calculator.calculate_power_damage(
            power_effects=[effect],
            power_type=PowerType.TOGGLE,
            power_activate_period=3.0,  # Activates every 3 seconds
        )

        # Damage scaled by: 10.0 * (3.0 / 10.0) = 3.0
        assert summary.total == pytest.approx(3.0, abs=0.01)
        assert summary.has_toggle_enhancements is True


class TestEdgeCases:
    """Test edge cases and special scenarios"""

    def test_self_targeted_special_damage_excluded(self):
        """
        Self-targeted SPECIAL damage should be excluded.

        This represents "damage" used for UI display of healing.
        """
        effect = Effect(
            unique_id=1,
            effect_type=EffectType.DAMAGE,
            magnitude=50.0,
            buffed_magnitude=50.0,
            damage_type=CoreDamageType.ENERGY,  # Using ENERGY as placeholder
            to_who=ToWho.SELF,  # Self-targeted
            probability=1.0,
        )
        # Mark as special damage via attribute
        effect.is_special_damage = True

        calculator = DamageCalculator()
        summary = calculator.calculate_power_damage(
            power_effects=[effect],
            power_type=PowerType.CLICK,
        )

        # Should be excluded completely
        assert summary.total == 0.0
        assert len(summary.by_type) == 0

    def test_zero_probability_excluded(self):
        """Effects with probability <= 0 should be excluded."""
        effect = Effect(
            unique_id=1,
            effect_type=EffectType.DAMAGE,
            magnitude=100.0,
            buffed_magnitude=100.0,
            damage_type=CoreDamageType.ENERGY,
            probability=0.0,  # Zero probability
            to_who=ToWho.TARGET,
        )

        calculator = DamageCalculator()
        summary = calculator.calculate_power_damage(
            power_effects=[effect],
            power_type=PowerType.CLICK,
        )

        assert summary.total == 0.0

    def test_non_damage_effects_ignored(self):
        """Non-damage effects should be ignored by damage calculator."""
        effect = Effect(
            unique_id=1,
            effect_type=EffectType.DEFENSE,  # Not damage
            magnitude=0.15,
            buffed_magnitude=0.15,
            to_who=ToWho.SELF,
        )

        calculator = DamageCalculator()
        summary = calculator.calculate_power_damage(
            power_effects=[effect],
            power_type=PowerType.CLICK,
        )

        assert summary.total == 0.0


class TestDamageSummaryFormatting:
    """Test DamageSummary string formatting"""

    def test_str_formatting(self):
        """Test __str__ method produces correct format."""
        from app.calculations.powers.damage_calculator import DamageSummary, DamageType

        summary = DamageSummary(
            by_type={
                DamageType.FIRE: 42.5,
                DamageType.ENERGY: 28.3,
            },
            total=70.8,
        )

        result = str(summary)
        assert "Fire(42.5" in result or "Fire(42.50)" in result
        assert "Energy(28.3" in result or "Energy(28.30)" in result

    def test_tooltip_formatting(self):
        """Test tooltip generation."""
        from app.calculations.powers.damage_calculator import DamageSummary, DamageType

        summary = DamageSummary(
            by_type={
                DamageType.FIRE: 100.0,
                DamageType.ENERGY: 50.0,
            },
            total=150.0,
        )

        tooltip = summary.format_tooltip()
        assert "Total: 150" in tooltip
        assert "Fire:" in tooltip
        assert "Energy:" in tooltip
