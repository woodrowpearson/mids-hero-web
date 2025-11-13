"""
Test suite for Buff/Debuff Calculator

Tests based on comprehensive test cases from Spec 03, Section 4.
All expected values are exact calculations from the specification.
"""

from decimal import Decimal

import pytest

from app.calculations.core.effect import Effect
from app.calculations.core.effect_types import DamageType, EffectType
from app.calculations.core.enums import Stacking, ToWho
from app.calculations.powers.buff_calculator import (
    BuffDebuffCalculator,
    BuffDebuffEffect,
    BuffDebuffType,
    StackingMode,
    format_buff_display,
)


class TestDefenseBuff:
    """Test Case 1: Defense Buff (Typed Aspect) - from Spec 03"""

    def test_defense_buff_melee(self):
        """
        Power: Super Reflexes > Focused Fighting (Toggle)
        Level: 50
        Archetype: Scrapper (modifier 1.0)

        Input:
            - Base defense: 13.875% (Melee)
            - Enhancement: 95% (3x level 50 Defense IOs, after ED)
            - AT modifier: 1.0
            - Target: Self

        Calculation:
            base = 0.13875 * 1.0 * 1.0 = 0.13875
            enhanced = 0.13875 * (1.0 + 0.95) = 0.13875 * 1.95 = 0.2705625

        Expected: 27.06% Defense(Melee)
        """
        effect = Effect(
            unique_id=1,
            effect_type=EffectType.DEFENSE,
            magnitude=0.13875,
            damage_type=DamageType.NONE,  # Positional defense stored separately
            scale=1.0,
            to_who=ToWho.SELF,
            buffable=True,
            resistible=False,
            stacking=Stacking.YES,
        )

        calculator = BuffDebuffCalculator()
        result = calculator.calculate_magnitude(
            effect=effect,
            enhancement_bonus=Decimal("0.95"),  # 95% from enhancements
            at_modifier=Decimal("1.0"),  # Scrapper
        )

        assert result["base_mag"] == pytest.approx(
            Decimal("0.13875"), abs=Decimal("0.00001")
        )
        assert result["enhanced_mag"] == pytest.approx(
            Decimal("0.2705625"), abs=Decimal("0.0001")
        )
        assert result["final_mag"] == pytest.approx(
            Decimal("0.2705625"), abs=Decimal("0.0001")
        )


class TestResistanceDebuff:
    """Test Case 2: Resistance Debuff (Typed Aspect) - from Spec 03"""

    def test_resistance_debuff_with_target_resistance(self):
        """
        Power: Sonic Resonance > Sonic Siphon (Click)
        Level: 50
        Archetype: Defender (modifier 1.0)

        Input:
            - Base resistance debuff: -30% (All types)
            - Enhancement: 56% (3x level 50 Defense Debuff IOs, after ED)
            - AT modifier: 1.0
            - Target resistance to debuffs: 20%

        Calculation:
            base = -0.30 * 1.0 * 1.0 = -0.30
            enhanced = -0.30 * (1.0 + 0.56) = -0.468
            after_resistance = -0.468 * (1.0 - 0.20) = -0.3744

        Expected: -37.44% Resistance(All)
        """
        effect = Effect(
            unique_id=1,
            effect_type=EffectType.RESISTANCE,
            magnitude=-0.30,
            damage_type=DamageType.SMASHING,  # All types, using one as example
            scale=1.0,
            to_who=ToWho.TARGET,  # Debuff on enemy
            buffable=True,
            resistible=True,
            stacking=Stacking.YES,
            duration=30.0,
        )

        calculator = BuffDebuffCalculator()
        result = calculator.calculate_magnitude(
            effect=effect,
            enhancement_bonus=Decimal("0.56"),
            at_modifier=Decimal("1.0"),
            target_resistance=Decimal("0.20"),  # 20% debuff resistance
        )

        assert result["base_mag"] == pytest.approx(
            Decimal("-0.30"), abs=Decimal("0.001")
        )
        assert result["enhanced_mag"] == pytest.approx(
            Decimal("-0.468"), abs=Decimal("0.001")
        )
        assert result["final_mag"] == pytest.approx(
            Decimal("-0.3744"), abs=Decimal("0.0001")
        )
        assert result["duration"] == Decimal("30.0")


class TestDamageBuff:
    """Test Case 3: Damage Buff (Global) - from Spec 03"""

    def test_damage_buff_single_stack(self):
        """
        Power: Kinetics > Fulcrum Shift (Click) - single target hit
        Level: 50
        Archetype: Controller (modifier 0.80)

        Input:
            - Base damage buff: 50% per target
            - Enhancement: 0% (not typically enhanced)
            - AT modifier: 0.80

        Calculation:
            base = 0.50 * 1.0 * 0.80 = 0.40
            enhanced = 0.40 (no enhancement)

        Expected: 40% damage buff
        """
        effect = Effect(
            unique_id=1,
            effect_type=EffectType.DAMAGE_BUFF,
            magnitude=0.50,
            scale=1.0,
            to_who=ToWho.SELF,
            buffable=True,
            resistible=False,
            stacking=Stacking.YES,
            duration=45.0,
        )

        calculator = BuffDebuffCalculator()
        result = calculator.calculate_magnitude(
            effect=effect,
            enhancement_bonus=Decimal("0.0"),
            at_modifier=Decimal("0.80"),  # Controller
        )

        assert result["final_mag"] == pytest.approx(
            Decimal("0.40"), abs=Decimal("0.001")
        )

    def test_damage_buff_multiplicative_stacking(self):
        """
        Test multiplicative stacking for damage buffs.

        Three stacks of 40% each should multiply:
        (1 + 0.40) * (1 + 0.40) * (1 + 0.40) - 1 = 1.744 = 174.4%
        """
        # Create three identical buff effects
        effects = []
        for i in range(3):
            effect = Effect(
                unique_id=i + 1,
                effect_type=EffectType.DAMAGE_BUFF,
                magnitude=0.40,
                to_who=ToWho.SELF,
                buffable=False,
                stacking=Stacking.YES,
            )
            buff_effect = BuffDebuffEffect(
                effect=effect,
                buff_debuff_type=BuffDebuffType.DAMAGE_BUFF,
                final_magnitude=Decimal("0.40"),
            )
            effects.append(buff_effect)

        calculator = BuffDebuffCalculator()
        total = calculator.apply_stacking(effects, StackingMode.MULTIPLICATIVE)

        # Expected: (1.4 * 1.4 * 1.4) - 1 = 2.744 - 1 = 1.744
        assert total == pytest.approx(Decimal("1.744"), abs=Decimal("0.001"))


class TestRechargeBuff:
    """Test Case 4: Recharge Buff - from Spec 03"""

    def test_recharge_buff_hasten(self):
        """
        Power: Speed > Hasten (Click)
        Level: 50
        Archetype: Any (modifier 1.0)

        Input:
            - Base recharge: 70%
            - Enhancement: 95% (3x level 50 Recharge IOs)
            - AT modifier: 1.0

        Calculation:
            base = 0.70 * 1.0 * 1.0 = 0.70
            enhanced = 0.70 * (1.0 + 0.95) = 1.365

        Expected: +136.5% recharge (57.7% faster recharge time)
        """
        effect = Effect(
            unique_id=1,
            effect_type=EffectType.RECHARGE_TIME,
            magnitude=0.70,
            scale=1.0,
            to_who=ToWho.SELF,
            buffable=True,
            resistible=False,
            stacking=Stacking.YES,
            duration=120.0,
        )

        calculator = BuffDebuffCalculator()
        result = calculator.calculate_magnitude(
            effect=effect,
            enhancement_bonus=Decimal("0.95"),
            at_modifier=Decimal("1.0"),
        )

        assert result["enhanced_mag"] == pytest.approx(
            Decimal("1.365"), abs=Decimal("0.001")
        )

        # Recharge time multiplier calculation
        recharge_multiplier = 1.0 / (1.0 + float(result["enhanced_mag"]))
        assert recharge_multiplier == pytest.approx(0.423, abs=0.001)


class TestMovementSpeedBuff:
    """Test Case 5: Movement Speed Buff - from Spec 03"""

    def test_movement_speed_not_buffable(self):
        """
        Power: Speed > Super Speed (Toggle)
        Level: 50

        Input:
            - Base speed: 216.7%
            - Enhancement: N/A (buffable = False)
            - AT modifier: 1.0

        Calculation:
            base = 2.167 * 1.0 * 1.0 = 2.167
            enhanced = 2.167 (not buffable)

        Expected: +216.7% running speed (3.167x normal speed)
        """
        effect = Effect(
            unique_id=1,
            effect_type=EffectType.SPEED_RUNNING,
            magnitude=2.167,
            scale=1.0,
            to_who=ToWho.SELF,
            buffable=False,  # Speed powers not enhanced
            resistible=False,
            stacking=Stacking.YES,
        )

        calculator = BuffDebuffCalculator()
        result = calculator.calculate_magnitude(
            effect=effect,
            enhancement_bonus=Decimal("0.95"),  # Should be ignored
            at_modifier=Decimal("1.0"),
        )

        # Enhancement should not apply
        assert result["base_mag"] == pytest.approx(
            Decimal("2.167"), abs=Decimal("0.001")
        )
        assert result["enhanced_mag"] == pytest.approx(
            Decimal("2.167"), abs=Decimal("0.001")
        )  # Same as base


class TestStackingScenarios:
    """Test Case 6: Stacking Scenarios - from Spec 03"""

    def test_additive_stacking(self):
        """
        Test additive stacking for defense buffs.

        Three defense buffs: 15%, 20%, 25%
        Should sum to: 60%
        """
        effects = []
        magnitudes = [Decimal("0.15"), Decimal("0.20"), Decimal("0.25")]

        for i, mag in enumerate(magnitudes):
            effect = Effect(
                unique_id=i + 1,
                effect_type=EffectType.DEFENSE,
                magnitude=float(mag),
                to_who=ToWho.SELF,
                stacking=Stacking.YES,
            )
            buff_effect = BuffDebuffEffect(
                effect=effect,
                buff_debuff_type=BuffDebuffType.DEFENSE,
                final_magnitude=mag,
            )
            effects.append(buff_effect)

        calculator = BuffDebuffCalculator()
        total = calculator.apply_stacking(effects, StackingMode.ADDITIVE)

        assert total == pytest.approx(Decimal("0.60"), abs=Decimal("0.001"))

    def test_best_value_stacking(self):
        """
        Test best-value stacking (Stacking = NO).

        Three buffs: 15%, 20%, 25%
        Should take maximum: 25%
        """
        effects = []
        magnitudes = [Decimal("0.15"), Decimal("0.20"), Decimal("0.25")]

        for i, mag in enumerate(magnitudes):
            effect = Effect(
                unique_id=i + 1,
                effect_type=EffectType.DEFENSE,
                magnitude=float(mag),
                to_who=ToWho.SELF,
                stacking=Stacking.NO,  # Does not stack
            )
            buff_effect = BuffDebuffEffect(
                effect=effect,
                buff_debuff_type=BuffDebuffType.DEFENSE,
                final_magnitude=mag,
            )
            effects.append(buff_effect)

        calculator = BuffDebuffCalculator()
        total = calculator.apply_stacking(effects, StackingMode.BEST_VALUE)

        assert total == pytest.approx(Decimal("0.25"), abs=Decimal("0.001"))


class TestBuffDebuffClassification:
    """Test buff vs debuff classification"""

    def test_is_buff_self_targeted(self):
        """Self-targeted effects are buffs."""
        effect = Effect(
            unique_id=1,
            effect_type=EffectType.DEFENSE,
            magnitude=0.15,
            to_who=ToWho.SELF,
        )
        buff_effect = BuffDebuffEffect(
            effect=effect, buff_debuff_type=BuffDebuffType.DEFENSE
        )

        assert buff_effect.is_buff() is True
        assert buff_effect.is_debuff() is False

    def test_is_debuff_target_enemy(self):
        """Enemy-targeted effects are debuffs."""
        effect = Effect(
            unique_id=1,
            effect_type=EffectType.DEFENSE,
            magnitude=-0.15,
            to_who=ToWho.TARGET,
        )
        buff_effect = BuffDebuffEffect(
            effect=effect, buff_debuff_type=BuffDebuffType.DEFENSE
        )

        assert buff_effect.is_buff() is False
        assert buff_effect.is_debuff() is True


class TestGroupingAndAggregation:
    """Test effect grouping and aggregation"""

    def test_grouping_by_type_and_aspect(self):
        """Effects should group by (type, damage_type, mez_type, to_who, pv_mode)."""
        # Create two defense buffs with same grouping
        effects = []
        for i in range(2):
            effect = Effect(
                unique_id=i + 1,
                effect_type=EffectType.DEFENSE,
                magnitude=0.15,
                damage_type=DamageType.SMASHING,
                to_who=ToWho.SELF,
            )
            buff_effect = BuffDebuffEffect(
                effect=effect,
                buff_debuff_type=BuffDebuffType.DEFENSE,
                final_magnitude=Decimal("0.15"),
            )
            effects.append(buff_effect)

        calculator = BuffDebuffCalculator()
        groups = calculator.group_effects(effects)

        # Should be one group
        assert len(groups) == 1

        # Group should have 2 effects
        key = list(groups.keys())[0]
        assert len(groups[key]) == 2

    def test_aggregation_with_stacking(self):
        """Test full aggregation pipeline."""
        # Create defense buffs
        effects = []
        for i in range(3):
            effect = Effect(
                unique_id=i + 1,
                effect_type=EffectType.DEFENSE,
                magnitude=0.10,
                damage_type=DamageType.SMASHING,
                to_who=ToWho.SELF,
                stacking=Stacking.YES,
            )
            buff_effect = BuffDebuffEffect(
                effect=effect,
                buff_debuff_type=BuffDebuffType.DEFENSE,
                final_magnitude=Decimal("0.10"),
            )
            effects.append(buff_effect)

        calculator = BuffDebuffCalculator()
        aggregated = calculator.aggregate_effects(effects)

        # Should have one key with total of 0.30
        assert len(aggregated) == 1
        total = list(aggregated.values())[0]
        assert total == pytest.approx(Decimal("0.30"), abs=Decimal("0.001"))


class TestBuffedEffectCalculation:
    """Test complete buffed effect calculation"""

    def test_calculate_buffed_effect_complete(self):
        """Test full calculation pipeline from effect to BuffDebuffEffect."""
        effect = Effect(
            unique_id=1,
            effect_type=EffectType.DEFENSE,
            magnitude=0.13875,
            scale=1.0,
            to_who=ToWho.SELF,
            buffable=True,
            stacking=Stacking.YES,
        )

        calculator = BuffDebuffCalculator()
        buff_effect = calculator.calculate_buffed_effect(
            effect=effect,
            enhancement_bonus=Decimal("0.95"),
            at_modifier=Decimal("1.0"),
        )

        assert buff_effect.buff_debuff_type == BuffDebuffType.DEFENSE
        assert buff_effect.base_magnitude == pytest.approx(
            Decimal("0.13875"), abs=Decimal("0.00001")
        )
        assert buff_effect.enhanced_magnitude == pytest.approx(
            Decimal("0.2705625"), abs=Decimal("0.0001")
        )
        assert buff_effect.final_magnitude == pytest.approx(
            Decimal("0.2705625"), abs=Decimal("0.0001")
        )


class TestFormatting:
    """Test buff display formatting"""

    def test_format_defense_with_aspect(self):
        """Test formatting with damage type aspect."""
        result = format_buff_display(
            BuffDebuffType.DEFENSE, Decimal("0.2706"), damage_type="Melee"
        )
        assert "Defense(Melee)" in result
        assert "27.06%" in result

    def test_format_recharge(self):
        """Test formatting without aspect."""
        result = format_buff_display(BuffDebuffType.RECHARGE_TIME, Decimal("0.70"))
        assert "Recharge Time" in result
        assert "+70.00%" in result

    def test_format_debuff_negative(self):
        """Test formatting negative values."""
        result = format_buff_display(BuffDebuffType.DEFENSE, Decimal("-0.15"))
        assert "-15.00%" in result


class TestErrorHandling:
    """Test error handling"""

    def test_negative_enhancement_bonus_raises(self):
        """Enhancement bonus cannot be negative."""
        effect = Effect(
            unique_id=1,
            effect_type=EffectType.DEFENSE,
            magnitude=0.15,
            to_who=ToWho.SELF,
        )

        calculator = BuffDebuffCalculator()
        with pytest.raises(ValueError, match="Enhancement bonus cannot be negative"):
            calculator.calculate_magnitude(
                effect=effect,
                enhancement_bonus=Decimal("-0.10"),
                at_modifier=Decimal("1.0"),
            )

    def test_invalid_at_modifier_raises(self):
        """AT modifier must be positive."""
        effect = Effect(
            unique_id=1,
            effect_type=EffectType.DEFENSE,
            magnitude=0.15,
            to_who=ToWho.SELF,
        )

        calculator = BuffDebuffCalculator()
        with pytest.raises(ValueError, match="AT modifier must be positive"):
            calculator.calculate_magnitude(
                effect=effect,
                enhancement_bonus=Decimal("0.95"),
                at_modifier=Decimal("0.0"),
            )

    def test_invalid_target_resistance_raises(self):
        """Target resistance must be 0-1."""
        effect = Effect(
            unique_id=1,
            effect_type=EffectType.DEFENSE,
            magnitude=0.15,
            to_who=ToWho.TARGET,
        )

        calculator = BuffDebuffCalculator()
        with pytest.raises(ValueError, match="Target resistance must be 0-1"):
            calculator.calculate_magnitude(
                effect=effect,
                enhancement_bonus=Decimal("0.0"),
                at_modifier=Decimal("1.0"),
                target_resistance=Decimal("1.5"),  # Invalid
            )
