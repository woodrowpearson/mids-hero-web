"""
Test Build Defense & Resistance - Specs 19, 20

Tests based on Batch 2A test cases from Milestone 4 Implementation Plan.
Validates defense aggregation ("highest wins") and resistance aggregation (additive stacking).
"""

import pytest

from app.calculations.build import (
    DEFENSE_SOFT_CAP,
    DefenseType,
    ResistanceType,
    aggregate_defense_bonuses,
    aggregate_resistance_bonuses,
    calculate_damage_reduction,
    calculate_effective_defense,
    create_build_totals,
)
from app.calculations.core import ArchetypeType


class TestDefenseAggregation:
    """Test Suite: Defense Aggregation (Spec 19)"""

    def test_1_smashing_typed_only(self):
        """
        Defense Test 1: Smashing typed only → 30.0%

        From plan line 190.
        Character has only typed smashing defense, no positional.
        """
        bonuses = [{DefenseType.SMASHING: 0.30}]
        result = aggregate_defense_bonuses(bonuses)

        assert result.get_defense(DefenseType.SMASHING) == 0.30
        assert result.get_defense(DefenseType.MELEE) == 0.0

    def test_2_melee_positional_only(self):
        """
        Defense Test 2: Melee positional only → 40.0%

        From plan line 191.
        Character has only positional melee defense, no typed.
        """
        bonuses = [{DefenseType.MELEE: 0.40}]
        result = aggregate_defense_bonuses(bonuses)

        assert result.get_defense(DefenseType.MELEE) == 0.40
        assert result.get_defense(DefenseType.SMASHING) == 0.0

    def test_3_both_sources_highest_wins(self):
        """
        Defense Test 3: Both sources → 40.0% (highest wins!)

        From plan line 192.
        Character has 30% typed smashing and 40% positional melee.
        Against a melee smashing attack, 40% applies (highest wins).
        """
        bonuses = [
            {DefenseType.SMASHING: 0.30},
            {DefenseType.MELEE: 0.40}
        ]
        result = aggregate_defense_bonuses(bonuses)

        typed_val = result.get_defense(DefenseType.SMASHING)
        positional_val = result.get_defense(DefenseType.MELEE)

        assert typed_val == 0.30
        assert positional_val == 0.40

        # Effective defense against melee smashing attack
        effective = calculate_effective_defense(typed_val, positional_val)
        assert effective == 0.40  # Highest wins!

    def test_4_defense_debuff_resistance(self):
        """
        Defense Test 4: Defense debuff resistance (DDR)

        From plan line 193.
        DDR reduces the effectiveness of defense debuffs.
        This test is a placeholder for future DDR implementation.
        """
        # Placeholder - DDR mechanics to be implemented in future batch
        pass

    def test_5_soft_cap_constant(self):
        """
        Defense Test 5: Soft cap is 45%

        Verifies the soft cap constant is correctly defined.
        """
        assert DEFENSE_SOFT_CAP == 0.45

    def test_6_at_soft_cap_check(self):
        """
        Defense Test 6: Check if defense is at soft cap

        Validates is_at_soft_cap() method.
        """
        bonuses = [{DefenseType.MELEE: 0.45}]
        result = aggregate_defense_bonuses(bonuses)

        assert result.is_at_soft_cap(DefenseType.MELEE)
        assert not result.is_at_soft_cap(DefenseType.RANGED)

    def test_7_multiple_typed_defense_sources(self):
        """
        Defense Test 7: Multiple typed defense sources stack additively

        Multiple powers granting the same typed defense should stack.
        """
        bonuses = [
            {DefenseType.SMASHING: 0.15, DefenseType.LETHAL: 0.15},
            {DefenseType.SMASHING: 0.10, DefenseType.LETHAL: 0.10},
            {DefenseType.SMASHING: 0.05, DefenseType.LETHAL: 0.05}
        ]
        result = aggregate_defense_bonuses(bonuses)

        assert result.get_defense(DefenseType.SMASHING) == 0.30
        assert result.get_defense(DefenseType.LETHAL) == 0.30

    def test_8_multiple_positional_defense_sources(self):
        """
        Defense Test 8: Multiple positional defense sources stack additively

        Multiple IO bonuses granting positional defense should stack.
        """
        bonuses = [
            {DefenseType.MELEE: 0.05},
            {DefenseType.MELEE: 0.05},
            {DefenseType.MELEE: 0.05}
        ]
        result = aggregate_defense_bonuses(bonuses)

        assert result.get_defense(DefenseType.MELEE) == pytest.approx(0.15)


class TestResistanceAggregation:
    """Test Suite: Resistance Aggregation (Spec 20)"""

    def test_1_power_only_30_percent(self):
        """
        Resistance Test 1: Power only → 30.0%

        From plan line 194.
        Character has a single power granting 30% S/L resistance.
        """
        bonuses = [{
            ResistanceType.SMASHING: 0.30,
            ResistanceType.LETHAL: 0.30
        }]
        result = aggregate_resistance_bonuses(bonuses)

        assert result.get_resistance(ResistanceType.SMASHING) == 0.30
        assert result.get_resistance(ResistanceType.LETHAL) == 0.30

    def test_2_multiple_sources_75_percent(self):
        """
        Resistance Test 2: Multiple sources → 75.0% (additive)

        From plan line 195.
        Character has multiple powers granting S/L resistance.
        30% + 20% + 25% = 75% (additive stacking).
        """
        bonuses = [
            {ResistanceType.SMASHING: 0.30, ResistanceType.LETHAL: 0.30},
            {ResistanceType.SMASHING: 0.20, ResistanceType.LETHAL: 0.20},
            {ResistanceType.SMASHING: 0.25, ResistanceType.LETHAL: 0.25}
        ]
        result = aggregate_resistance_bonuses(bonuses)

        assert result.get_resistance(ResistanceType.SMASHING) == 0.75
        assert result.get_resistance(ResistanceType.LETHAL) == 0.75

    def test_3_damage_reduction_calculation(self):
        """
        Resistance Test 3: Damage reduction from resistance

        75% resistance = take 25% damage
        90% resistance = take 10% damage
        """
        # 75% resistance
        assert calculate_damage_reduction(0.75) == pytest.approx(0.25)

        # 90% resistance
        assert calculate_damage_reduction(0.90) == pytest.approx(0.10)

    def test_4_cap_enforcement_scrapper(self):
        """
        Resistance Test 4: Cap enforcement for Scrapper (75% cap)

        Scrapper resistance caps at 75%.
        100% resistance should be capped to 75%.
        """
        bonuses = [{
            ResistanceType.SMASHING: 1.00  # 100% uncapped
        }]
        result = aggregate_resistance_bonuses(bonuses, ArchetypeType.SCRAPPER)

        assert result.get_resistance(ResistanceType.SMASHING) == 0.75  # Capped


class TestBuildTotals:
    """Test Suite: BuildTotals Integration"""

    def test_1_build_totals_creation(self):
        """
        Build Totals Test 1: Create BuildTotals for Scrapper
        """
        totals = create_build_totals(ArchetypeType.SCRAPPER)

        assert totals.archetype == ArchetypeType.SCRAPPER
        assert totals.defense.get_defense(DefenseType.MELEE) == 0.0
        assert totals.resistance.get_resistance(ResistanceType.SMASHING) == 0.0

    def test_2_add_defense_bonuses(self):
        """
        Build Totals Test 2: Add defense bonuses to build
        """
        totals = create_build_totals(ArchetypeType.SCRAPPER)

        defense_bonuses = [
            {DefenseType.SMASHING: 0.15, DefenseType.LETHAL: 0.15},
            {DefenseType.MELEE: 0.20}
        ]
        totals.add_defense_bonuses(defense_bonuses)

        assert totals.defense.get_defense(DefenseType.SMASHING) == 0.15
        assert totals.defense.get_defense(DefenseType.MELEE) == 0.20

    def test_3_add_resistance_bonuses(self):
        """
        Build Totals Test 3: Add resistance bonuses to build
        """
        totals = create_build_totals(ArchetypeType.SCRAPPER)

        resistance_bonuses = [
            {ResistanceType.SMASHING: 0.30, ResistanceType.LETHAL: 0.30},
            {ResistanceType.SMASHING: 0.20, ResistanceType.LETHAL: 0.20}
        ]
        totals.add_resistance_bonuses(resistance_bonuses)

        assert totals.resistance.get_resistance(ResistanceType.SMASHING) == 0.50
        assert totals.resistance.get_resistance(ResistanceType.LETHAL) == 0.50

    def test_4_effective_defense_against_attack(self):
        """
        Build Totals Test 4: Calculate effective defense against specific attack

        Character has 30% typed smashing and 40% positional melee.
        Against melee smashing attack, 40% applies (highest wins).
        """
        totals = create_build_totals(ArchetypeType.SCRAPPER)

        defense_bonuses = [
            {DefenseType.SMASHING: 0.30},
            {DefenseType.MELEE: 0.40}
        ]
        totals.add_defense_bonuses(defense_bonuses)

        effective = totals.calculate_effective_defense_against(
            DefenseType.SMASHING,
            DefenseType.MELEE
        )

        assert effective == 0.40  # Highest wins


class TestEdgeCases:
    """Test Suite: Edge Cases"""

    def test_1_negative_resistance_debuff(self):
        """
        Edge Case Test 1: Negative resistance (debuff)

        Character with -20% resistance takes MORE damage.
        """
        bonuses = [{ResistanceType.SMASHING: -0.20}]
        result = aggregate_resistance_bonuses(bonuses)

        assert result.get_resistance(ResistanceType.SMASHING) == -0.20

        # Damage reduction with negative resistance
        damage_mult = calculate_damage_reduction(-0.20)
        assert damage_mult == 1.20  # Take 120% damage

    def test_2_empty_bonuses(self):
        """
        Edge Case Test 2: Empty bonus lists

        No bonuses should result in zero defense/resistance.
        """
        defense_result = aggregate_defense_bonuses([])
        resistance_result = aggregate_resistance_bonuses([])

        assert defense_result.get_defense(DefenseType.MELEE) == 0.0
        assert resistance_result.get_resistance(ResistanceType.SMASHING) == 0.0

    def test_3_mixed_damage_types(self):
        """
        Edge Case Test 3: Different resistance values for different types

        Character can have different resistance for each damage type.
        """
        bonuses = [
            {ResistanceType.SMASHING: 0.75, ResistanceType.LETHAL: 0.75},
            {ResistanceType.FIRE: 0.30, ResistanceType.COLD: 0.30},
            {ResistanceType.ENERGY: 0.20}
        ]
        result = aggregate_resistance_bonuses(bonuses)

        assert result.get_resistance(ResistanceType.SMASHING) == 0.75
        assert result.get_resistance(ResistanceType.FIRE) == 0.30
        assert result.get_resistance(ResistanceType.ENERGY) == 0.20
        assert result.get_resistance(ResistanceType.PSIONIC) == 0.0
