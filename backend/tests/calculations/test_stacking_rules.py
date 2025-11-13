"""
Tests for Buff Stacking Rules

Tests all stacking modes, Rule of 5, and effect grouping logic.
Based on test cases from Spec 25 section 4.
"""

import pytest
from backend.app.calculations.build.stacking_rules import (
    BuffStackingCalculator,
    StackingMode,
)
from backend.app.calculations.core.effect import Effect
from backend.app.calculations.core.effect_types import DamageType, EffectType
from backend.app.calculations.core.enums import Stacking, ToWho


class TestStackingModes:
    """Test different stacking modes."""

    def test_additive_stacking_defense_buffs(self):
        """Test additive stacking for defense buffs (Test Case 1 from Spec 25)."""
        calc = BuffStackingCalculator()

        effects = [
            Effect(
                unique_id=1,
                effect_type=EffectType.DEFENSE,
                magnitude=0.075,  # 7.5% from IO set
                buffed_magnitude=0.075,
                damage_type=DamageType.NONE,
                stacking=Stacking.YES,
            ),
            Effect(
                unique_id=2,
                effect_type=EffectType.DEFENSE,
                magnitude=0.05,  # 5% from IO set
                buffed_magnitude=0.05,
                damage_type=DamageType.NONE,
                stacking=Stacking.YES,
            ),
            Effect(
                unique_id=3,
                effect_type=EffectType.DEFENSE,
                magnitude=0.0375,  # 3.75% from IO set
                buffed_magnitude=0.0375,
                damage_type=DamageType.NONE,
                stacking=Stacking.YES,
            ),
        ]

        grouped = calc.group_effects(effects)

        assert len(grouped) == 1
        assert grouped[0].enhanced_magnitude == pytest.approx(0.1625, rel=1e-4)
        assert grouped[0].is_aggregated is True
        assert len(grouped[0].included_effects) == 3
        assert grouped[0].stacking_mode == StackingMode.ADDITIVE

    def test_multiplicative_stacking_damage_buffs(self):
        """Test multiplicative stacking for damage buffs (Test Case 2 from Spec 25)."""
        calc = BuffStackingCalculator()

        effects = [
            Effect(
                unique_id=1,
                effect_type=EffectType.DAMAGE_BUFF,
                magnitude=1.0,  # 100% damage buff (Build Up)
                buffed_magnitude=1.0,
                damage_type=DamageType.NONE,
                stacking=Stacking.YES,
            ),
            Effect(
                unique_id=2,
                effect_type=EffectType.DAMAGE_BUFF,
                magnitude=0.5,  # 50% damage buff (Aim)
                buffed_magnitude=0.5,
                damage_type=DamageType.NONE,
                stacking=Stacking.YES,
            ),
        ]

        grouped = calc.group_effects(effects)

        assert len(grouped) == 1
        # (1+1.0) * (1+0.5) - 1 = 2.0 * 1.5 - 1 = 2.0
        assert grouped[0].enhanced_magnitude == pytest.approx(2.0, rel=1e-4)
        assert grouped[0].is_aggregated is True
        assert grouped[0].stacking_mode == StackingMode.MULTIPLICATIVE

    def test_best_value_only_non_stacking(self):
        """Test best value only for non-stacking effects (Test Case 3 from Spec 25)."""
        calc = BuffStackingCalculator()

        effects = [
            Effect(
                unique_id=1,
                effect_type=EffectType.RECHARGE_TIME,
                magnitude=0.075,  # 7.5% recharge (LotG)
                buffed_magnitude=0.075,
                stacking=Stacking.NO,  # Unique IO
            ),
            Effect(
                unique_id=2,
                effect_type=EffectType.RECHARGE_TIME,
                magnitude=0.075,  # 7.5% recharge (same IO)
                buffed_magnitude=0.075,
                stacking=Stacking.NO,  # Unique IO
            ),
        ]

        grouped = calc.group_effects(effects)

        assert len(grouped) == 1
        # Best value only: MAX(0.075, 0.075) = 0.075
        assert grouped[0].enhanced_magnitude == pytest.approx(0.075, rel=1e-4)
        assert grouped[0].is_aggregated is True
        assert len(grouped[0].included_effects) == 2  # Both tracked
        assert grouped[0].stacking_mode == StackingMode.BEST_VALUE


class TestRuleOfFive:
    """Test Rule of 5 for set bonuses."""

    def test_rule_of_five_suppression(self):
        """Test Rule of 5 suppresses 6th+ instances (Test Case 4 from Spec 25)."""
        calc = BuffStackingCalculator(rule_of_5_enabled=True)

        # Create 6 instances of the same set bonus
        effects = []
        for i in range(6):
            effect = Effect(
                unique_id=i + 1,
                effect_type=EffectType.RECHARGE_TIME,
                magnitude=0.05,  # 5% recharge bonus
                buffed_magnitude=0.05,
                stacking=Stacking.YES,
            )
            # Add source tracking attributes
            effect.source_type = "set_bonus"
            effect.source_power_id = 12345  # Same set bonus power ID
            effects.append(effect)

        grouped = calc.group_effects(effects)

        assert len(grouped) == 1
        # Only first 5 should be included: 0.05 * 5 = 0.25
        assert grouped[0].enhanced_magnitude == pytest.approx(0.25, rel=1e-4)
        assert len(grouped[0].included_effects) == 5  # 6th suppressed

    def test_rule_of_five_different_bonuses(self):
        """Test Rule of 5 applies per set bonus power ID (Test Case 9 from Spec 25)."""
        calc = BuffStackingCalculator(rule_of_5_enabled=True)

        effects = []

        # Set Bonus A: 6 instances of +5% recharge (power ID 100)
        for i in range(6):
            effect = Effect(
                unique_id=i + 1,
                effect_type=EffectType.RECHARGE_TIME,
                magnitude=0.05,
                buffed_magnitude=0.05,
                stacking=Stacking.YES,
            )
            effect.source_type = "set_bonus"
            effect.source_power_id = 100
            effects.append(effect)

        # Set Bonus B: 3 instances of +3% defense (power ID 200)
        for i in range(3):
            effect = Effect(
                unique_id=100 + i,
                effect_type=EffectType.DEFENSE,
                magnitude=0.03,
                buffed_magnitude=0.03,
                damage_type=DamageType.NONE,
                stacking=Stacking.YES,
            )
            effect.source_type = "set_bonus"
            effect.source_power_id = 200
            effects.append(effect)

        grouped = calc.group_effects(effects)

        # Find recharge group
        recharge_group = [
            g for g in grouped if g.identifier.effect_type == EffectType.RECHARGE_TIME
        ][0]
        # Find defense group
        defense_group = [
            g for g in grouped if g.identifier.effect_type == EffectType.DEFENSE
        ][0]

        # Recharge: 5 instances included (6th suppressed)
        assert recharge_group.enhanced_magnitude == pytest.approx(0.25, rel=1e-4)
        assert len(recharge_group.included_effects) == 5

        # Defense: All 3 instances included (< 6)
        assert defense_group.enhanced_magnitude == pytest.approx(0.09, rel=1e-4)
        assert len(defense_group.included_effects) == 3


class TestEffectGrouping:
    """Test effect grouping by FxIdentifier."""

    def test_different_damage_types_separate_groups(self):
        """Test different damage types create separate groups (Test Case 5 from Spec 25)."""
        calc = BuffStackingCalculator()

        effects = [
            Effect(
                unique_id=1,
                effect_type=EffectType.RESISTANCE,
                magnitude=0.10,  # 10% S resist
                buffed_magnitude=0.10,
                damage_type=DamageType.SMASHING,
                stacking=Stacking.YES,
            ),
            Effect(
                unique_id=2,
                effect_type=EffectType.RESISTANCE,
                magnitude=0.10,  # 10% L resist
                buffed_magnitude=0.10,
                damage_type=DamageType.LETHAL,
                stacking=Stacking.YES,
            ),
            Effect(
                unique_id=3,
                effect_type=EffectType.RESISTANCE,
                magnitude=0.05,  # 5% S resist (different source)
                buffed_magnitude=0.05,
                damage_type=DamageType.SMASHING,
                stacking=Stacking.YES,
            ),
        ]

        grouped = calc.group_effects(effects)

        # Should have 2 groups: Smashing and Lethal
        assert len(grouped) == 2

        # Find Smashing group
        smashing_group = [
            g for g in grouped if g.identifier.damage_type == DamageType.SMASHING.value
        ][0]

        # Find Lethal group
        lethal_group = [
            g for g in grouped if g.identifier.damage_type == DamageType.LETHAL.value
        ][0]

        # Smashing: 0.10 + 0.05 = 0.15
        assert smashing_group.enhanced_magnitude == pytest.approx(0.15, rel=1e-4)
        assert len(smashing_group.included_effects) == 2

        # Lethal: 0.10 (only one effect)
        assert lethal_group.enhanced_magnitude == pytest.approx(0.10, rel=1e-4)
        assert len(lethal_group.included_effects) == 1

    def test_different_targets_separate_groups(self):
        """Test different targets create separate groups (Test Case 7 from Spec 25)."""
        calc = BuffStackingCalculator()

        effects = [
            Effect(
                unique_id=1,
                effect_type=EffectType.DEFENSE,
                magnitude=0.10,  # 10% defense to self
                buffed_magnitude=0.10,
                damage_type=DamageType.NONE,
                to_who=ToWho.SELF,
                stacking=Stacking.YES,
            ),
            Effect(
                unique_id=2,
                effect_type=EffectType.DEFENSE,
                magnitude=0.05,  # 5% defense to team
                buffed_magnitude=0.05,
                damage_type=DamageType.NONE,
                to_who=ToWho.TEAM,
                stacking=Stacking.YES,
            ),
        ]

        grouped = calc.group_effects(effects)

        # Should have 2 groups: Self and Team
        assert len(grouped) == 2

        # Find Self group
        self_group = [g for g in grouped if g.identifier.target == ToWho.SELF][0]

        # Find Team group
        team_group = [g for g in grouped if g.identifier.target == ToWho.TEAM][0]

        # Self: 0.10
        assert self_group.enhanced_magnitude == pytest.approx(0.10, rel=1e-4)

        # Team: 0.05
        assert team_group.enhanced_magnitude == pytest.approx(0.05, rel=1e-4)


class TestMixedScenarios:
    """Test complex scenarios with multiple stacking rules."""

    def test_three_damage_buffs_multiplicative(self):
        """Test multiplicative stacking with 3 damage buffs (Test Case 8 from Spec 25)."""
        calc = BuffStackingCalculator()

        effects = [
            Effect(
                unique_id=1,
                effect_type=EffectType.DAMAGE_BUFF,
                magnitude=0.80,  # 80% (Fury)
                buffed_magnitude=0.80,
                damage_type=DamageType.NONE,
                stacking=Stacking.YES,
            ),
            Effect(
                unique_id=2,
                effect_type=EffectType.DAMAGE_BUFF,
                magnitude=0.50,  # 50% (Aim)
                buffed_magnitude=0.50,
                damage_type=DamageType.NONE,
                stacking=Stacking.YES,
            ),
            Effect(
                unique_id=3,
                effect_type=EffectType.DAMAGE_BUFF,
                magnitude=0.25,  # 25% (set bonus)
                buffed_magnitude=0.25,
                damage_type=DamageType.NONE,
                stacking=Stacking.YES,
            ),
        ]

        grouped = calc.group_effects(effects)

        assert len(grouped) == 1
        # (1+0.80) * (1+0.50) * (1+0.25) - 1
        # = 1.8 * 1.5 * 1.25 - 1
        # = 3.375 - 1 = 2.375
        assert grouped[0].enhanced_magnitude == pytest.approx(2.375, rel=1e-4)

    def test_single_effect_no_aggregation(self):
        """Test single effect returns non-aggregated group."""
        calc = BuffStackingCalculator()

        effects = [
            Effect(
                unique_id=1,
                effect_type=EffectType.DEFENSE,
                magnitude=0.10,
                buffed_magnitude=0.10,
                damage_type=DamageType.NONE,
                stacking=Stacking.YES,
            ),
        ]

        grouped = calc.group_effects(effects)

        assert len(grouped) == 1
        assert grouped[0].enhanced_magnitude == pytest.approx(0.10, rel=1e-4)
        assert grouped[0].is_aggregated is False  # Single effect
        assert len(grouped[0].included_effects) == 1

    def test_empty_effects_list(self):
        """Test empty effects list returns empty result."""
        calc = BuffStackingCalculator()

        grouped = calc.group_effects([])

        assert len(grouped) == 0


class TestStatTotal:
    """Test get_stat_total helper method."""

    def test_get_stat_total_defense(self):
        """Test getting total for specific stat."""
        calc = BuffStackingCalculator()

        effects = [
            Effect(
                unique_id=1,
                effect_type=EffectType.DEFENSE,
                magnitude=0.10,
                buffed_magnitude=0.10,
                damage_type=DamageType.NONE,
                stacking=Stacking.YES,
            ),
            Effect(
                unique_id=2,
                effect_type=EffectType.DEFENSE,
                magnitude=0.05,
                buffed_magnitude=0.05,
                damage_type=DamageType.NONE,
                stacking=Stacking.YES,
            ),
            Effect(
                unique_id=3,
                effect_type=EffectType.RESISTANCE,
                magnitude=0.15,
                buffed_magnitude=0.15,
                damage_type=DamageType.NONE,
                stacking=Stacking.YES,
            ),
        ]

        grouped = calc.group_effects(effects)

        defense_total = calc.get_stat_total(grouped, EffectType.DEFENSE)
        resistance_total = calc.get_stat_total(grouped, EffectType.RESISTANCE)

        assert defense_total == pytest.approx(0.15, rel=1e-4)
        assert resistance_total == pytest.approx(0.15, rel=1e-4)
