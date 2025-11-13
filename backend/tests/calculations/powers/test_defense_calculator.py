"""
Test suite for Power Defense/Resistance Calculator

Tests based on comprehensive test cases from Spec 09, Section 4.
All expected values are exact calculations from the specification.
"""

import pytest

from app.calculations.core.effect import Effect
from app.calculations.core.effect_types import DamageType as CoreDamageType
from app.calculations.core.effect_types import EffectType
from app.calculations.core.enums import ToWho
from app.calculations.powers.defense_calculator import (
    DamageType,
    DefenseCalculator,
    DefenseValues,
    PositionType,
    ResistanceValues,
)


class TestBasicDefenseExtraction:
    """Test Case 1: Basic Typed Defense Extraction"""

    def test_single_typed_defense(self):
        """
        Power: Force Field > Deflection Shield
        Effect: +15% Smashing defense

        Expected: DefenseValues with smashing=0.15
        """
        effect = Effect(
            unique_id=1,
            effect_type=EffectType.DEFENSE,
            magnitude=0.15,
            buffed_magnitude=0.15,
            damage_type=CoreDamageType.SMASHING,
            to_who=ToWho.TARGET,
        )

        calculator = DefenseCalculator()
        defense = calculator.extract_defense_from_power([effect])

        assert defense.smashing == pytest.approx(0.15, abs=0.01)
        assert defense.lethal == pytest.approx(0.0, abs=0.01)
        assert defense.melee == pytest.approx(0.0, abs=0.01)

    def test_multiple_typed_defense(self):
        """
        Power: Ice Armor > Frozen Armor
        Effects:
            - +13.875% Smashing defense
            - +13.875% Lethal defense
            - +13.875% Cold defense

        Expected: DefenseValues with multiple typed defenses
        """
        effects = [
            Effect(
                unique_id=1,
                effect_type=EffectType.DEFENSE,
                magnitude=0.13875,
                buffed_magnitude=0.13875,
                damage_type=CoreDamageType.SMASHING,
                to_who=ToWho.SELF,
            ),
            Effect(
                unique_id=2,
                effect_type=EffectType.DEFENSE,
                magnitude=0.13875,
                buffed_magnitude=0.13875,
                damage_type=CoreDamageType.LETHAL,
                to_who=ToWho.SELF,
            ),
            Effect(
                unique_id=3,
                effect_type=EffectType.DEFENSE,
                magnitude=0.13875,
                buffed_magnitude=0.13875,
                damage_type=CoreDamageType.COLD,
                to_who=ToWho.SELF,
            ),
        ]

        calculator = DefenseCalculator()
        defense = calculator.extract_defense_from_power(effects)

        assert defense.smashing == pytest.approx(0.13875, abs=0.001)
        assert defense.lethal == pytest.approx(0.13875, abs=0.001)
        assert defense.cold == pytest.approx(0.13875, abs=0.001)
        assert defense.fire == pytest.approx(0.0, abs=0.01)


class TestPositionalDefenseExtraction:
    """Test Case 2: Positional Defense Extraction"""

    def test_single_positional_defense(self):
        """
        Power: Super Reflexes > Focused Fighting
        Effect: +13.875% Melee defense

        Expected: DefenseValues with melee=0.13875
        """
        # Note: Positional defense uses a special damage type or attribute
        # For this implementation, we'll use a position attribute
        effect = Effect(
            unique_id=1,
            effect_type=EffectType.DEFENSE,
            magnitude=0.13875,
            buffed_magnitude=0.13875,
            to_who=ToWho.SELF,
        )
        # Add position attribute
        effect.position = PositionType.MELEE

        calculator = DefenseCalculator()
        defense = calculator.extract_defense_from_power([effect])

        assert defense.melee == pytest.approx(0.13875, abs=0.001)
        assert defense.ranged == pytest.approx(0.0, abs=0.01)
        assert defense.smashing == pytest.approx(0.0, abs=0.01)

    def test_multiple_positional_defense(self):
        """
        Power: Super Reflexes > All 3 toggles active
        Effects:
            - +13.875% Melee defense (Focused Fighting)
            - +13.875% Ranged defense (Focused Senses)
            - +13.875% AoE defense (Evasion)

        Expected: DefenseValues with all three positional defenses
        """
        effects = []
        for idx, position in enumerate(
            [PositionType.MELEE, PositionType.RANGED, PositionType.AOE]
        ):
            effect = Effect(
                unique_id=idx + 1,
                effect_type=EffectType.DEFENSE,
                magnitude=0.13875,
                buffed_magnitude=0.13875,
                to_who=ToWho.SELF,
            )
            effect.position = position
            effects.append(effect)

        calculator = DefenseCalculator()
        defense = calculator.extract_defense_from_power(effects)

        assert defense.melee == pytest.approx(0.13875, abs=0.001)
        assert defense.ranged == pytest.approx(0.13875, abs=0.001)
        assert defense.aoe == pytest.approx(0.13875, abs=0.001)


class TestEffectiveDefense:
    """Test Case 3: Effective Defense (Highest Wins)"""

    def test_typed_vs_positional_typed_higher(self):
        """
        Character has:
            - 35% Ranged defense (positional)
            - 20% Fire defense (typed)

        Enemy: Ranged Fire attack

        Expected: 35% effective defense (Ranged is higher)
        """
        defense = DefenseValues(ranged=0.35, fire=0.20)

        effective = defense.get_effective(
            damage_type=DamageType.FIRE, position=PositionType.RANGED
        )

        assert effective == pytest.approx(0.35, abs=0.01)

    def test_typed_vs_positional_positional_higher(self):
        """
        Character has:
            - 20% Melee defense (positional)
            - 45% Smashing defense (typed)

        Enemy: Melee Smashing attack

        Expected: 45% effective defense (Smashing is higher)
        """
        defense = DefenseValues(melee=0.20, smashing=0.45)

        effective = defense.get_effective(
            damage_type=DamageType.SMASHING, position=PositionType.MELEE
        )

        assert effective == pytest.approx(0.45, abs=0.01)

    def test_equal_typed_and_positional(self):
        """
        Character has:
            - 45% Ranged defense
            - 45% Energy defense

        Enemy: Ranged Energy attack

        Expected: 45% effective defense (both equal)
        """
        defense = DefenseValues(ranged=0.45, energy=0.45)

        effective = defense.get_effective(
            damage_type=DamageType.ENERGY, position=PositionType.RANGED
        )

        assert effective == pytest.approx(0.45, abs=0.01)


class TestResistanceExtraction:
    """Test Case 4: Resistance Extraction"""

    def test_single_typed_resistance(self):
        """
        Power: Invulnerability > Temp Invulnerability
        Effect: +32.5% Smashing resistance

        Expected: ResistanceValues with smashing=0.325
        """
        effect = Effect(
            unique_id=1,
            effect_type=EffectType.RESISTANCE,
            magnitude=0.325,
            buffed_magnitude=0.325,
            damage_type=CoreDamageType.SMASHING,
            to_who=ToWho.SELF,
        )

        calculator = DefenseCalculator()
        resistance = calculator.extract_resistance_from_power([effect])

        assert resistance.smashing == pytest.approx(0.325, abs=0.01)
        assert resistance.lethal == pytest.approx(0.0, abs=0.01)

    def test_multiple_typed_resistance(self):
        """
        Power: Fire Armor > Fire Shield
        Effects:
            - +28.125% Fire resistance
            - +28.125% Lethal resistance

        Expected: ResistanceValues with multiple types
        """
        effects = [
            Effect(
                unique_id=1,
                effect_type=EffectType.RESISTANCE,
                magnitude=0.28125,
                buffed_magnitude=0.28125,
                damage_type=CoreDamageType.FIRE,
                to_who=ToWho.SELF,
            ),
            Effect(
                unique_id=2,
                effect_type=EffectType.RESISTANCE,
                magnitude=0.28125,
                buffed_magnitude=0.28125,
                damage_type=CoreDamageType.LETHAL,
                to_who=ToWho.SELF,
            ),
        ]

        calculator = DefenseCalculator()
        resistance = calculator.extract_resistance_from_power(effects)

        assert resistance.fire == pytest.approx(0.28125, abs=0.001)
        assert resistance.lethal == pytest.approx(0.28125, abs=0.001)


class TestDefenseDebuffResistance:
    """Test Case 5: Defense Debuff Resistance (DDR)"""

    def test_ddr_extraction(self):
        """
        Power: Super Reflexes > Elude
        Effect: +100% Defense Debuff Resistance

        Expected: DebuffResistanceValues with defense=1.0
        """
        effect = Effect(
            unique_id=1,
            effect_type=EffectType.DEFENSE_DEBUFF_RESISTANCE,
            magnitude=1.0,
            buffed_magnitude=1.0,
            to_who=ToWho.SELF,
        )

        calculator = DefenseCalculator()
        ddr = calculator.extract_debuff_resistance_from_power([effect])

        assert ddr.defense == pytest.approx(1.0, abs=0.01)

    def test_ddr_application_50_percent(self):
        """
        Base defense: 45%
        Defense debuff: -20%
        DDR: 50%

        Calculation:
            actual_debuff = 20% * (1 - 0.5) = 10%
            net_defense = 45% - 10% = 35%

        Expected: 35% defense after debuff
        """
        calculator = DefenseCalculator()

        net_defense = calculator.apply_defense_debuff(
            base_defense=0.45, defense_debuff=0.20, ddr=0.50
        )

        assert net_defense == pytest.approx(0.35, abs=0.01)

    def test_ddr_application_100_percent(self):
        """
        Base defense: 45%
        Defense debuff: -20%
        DDR: 100% (immune)

        Calculation:
            actual_debuff = 20% * (1 - 1.0) = 0%
            net_defense = 45% - 0% = 45%

        Expected: 45% defense (debuff negated)
        """
        calculator = DefenseCalculator()

        net_defense = calculator.apply_defense_debuff(
            base_defense=0.45, defense_debuff=0.20, ddr=1.0
        )

        assert net_defense == pytest.approx(0.45, abs=0.01)

    def test_ddr_application_no_ddr(self):
        """
        Base defense: 45%
        Defense debuff: -20%
        DDR: 0%

        Calculation:
            actual_debuff = 20% * (1 - 0.0) = 20%
            net_defense = 45% - 20% = 25%

        Expected: 25% defense
        """
        calculator = DefenseCalculator()

        net_defense = calculator.apply_defense_debuff(
            base_defense=0.45, defense_debuff=0.20, ddr=0.0
        )

        assert net_defense == pytest.approx(0.25, abs=0.01)


class TestResistanceCaps:
    """Test Case 6: Archetype Resistance Caps"""

    def test_tanker_resistance_cap_90_percent(self):
        """
        Archetype: Tanker (90% cap)
        Resistance: 100% (overcapped)

        Expected: 90% (capped)
        """
        calculator = DefenseCalculator(archetype_resistance_cap=0.90)

        capped = calculator.apply_resistance_cap(resistance_value=1.0)

        assert capped == pytest.approx(0.90, abs=0.01)

    def test_scrapper_resistance_cap_75_percent(self):
        """
        Archetype: Scrapper (75% cap)
        Resistance: 85% (overcapped)

        Expected: 75% (capped)
        """
        calculator = DefenseCalculator(archetype_resistance_cap=0.75)

        capped = calculator.apply_resistance_cap(resistance_value=0.85)

        assert capped == pytest.approx(0.75, abs=0.01)

    def test_resistance_under_cap(self):
        """
        Archetype: Tanker (90% cap)
        Resistance: 60% (under cap)

        Expected: 60% (unchanged)
        """
        calculator = DefenseCalculator(archetype_resistance_cap=0.90)

        capped = calculator.apply_resistance_cap(resistance_value=0.60)

        assert capped == pytest.approx(0.60, abs=0.01)

    def test_apply_resistance_cap_to_values(self):
        """
        Test applying cap to all resistance values.

        Archetype: Scrapper (75% cap)
        Resistance values: Mixed (some over, some under cap)

        Expected: All capped at 75%
        """
        calculator = DefenseCalculator(archetype_resistance_cap=0.75)

        resistance = ResistanceValues(
            smashing=0.85,  # Over cap
            lethal=0.60,  # Under cap
            fire=0.75,  # At cap
            cold=0.50,  # Under cap
        )

        capped = calculator.apply_resistance_cap_to_values(resistance)

        assert capped.smashing == pytest.approx(0.75, abs=0.01)  # Capped
        assert capped.lethal == pytest.approx(0.60, abs=0.01)  # Unchanged
        assert capped.fire == pytest.approx(0.75, abs=0.01)  # Unchanged
        assert capped.cold == pytest.approx(0.50, abs=0.01)  # Unchanged


class TestEffectiveHitPoints:
    """Test Case 7: Effective Hit Points (EHP) Calculation"""

    def test_ehp_45_defense_75_resistance(self):
        """
        Base HP: 2000
        Defense: 45%
        Resistance: 75%
        Enemy base tohit: 50%

        Calculation:
            chance_to_hit = max(0.05, 0.50 - 0.45) = 0.05
            damage_multiplier = 1 - 0.75 = 0.25
            EHP = 2000 / 0.25 / 0.05 = 160,000

        Expected: 160,000 EHP
        """
        calculator = DefenseCalculator()

        ehp = calculator.calculate_effective_hp(
            base_hp=2000.0, defense=0.45, resistance=0.75
        )

        assert ehp == pytest.approx(160000.0, abs=100.0)

    def test_ehp_45_defense_no_resistance(self):
        """
        Base HP: 2000
        Defense: 45%
        Resistance: 0%

        Calculation:
            chance_to_hit = max(0.05, 0.50 - 0.45) = 0.05
            damage_multiplier = 1.0
            EHP = 2000 / 1.0 / 0.05 = 40,000

        Expected: 40,000 EHP
        """
        calculator = DefenseCalculator()

        ehp = calculator.calculate_effective_hp(
            base_hp=2000.0, defense=0.45, resistance=0.0
        )

        assert ehp == pytest.approx(40000.0, abs=100.0)

    def test_ehp_no_defense_75_resistance(self):
        """
        Base HP: 2000
        Defense: 0%
        Resistance: 75%

        Calculation:
            chance_to_hit = max(0.05, 0.50 - 0.0) = 0.50
            damage_multiplier = 1 - 0.75 = 0.25
            EHP = 2000 / 0.25 / 0.50 = 16,000

        Expected: 16,000 EHP
        """
        calculator = DefenseCalculator()

        ehp = calculator.calculate_effective_hp(
            base_hp=2000.0, defense=0.0, resistance=0.75
        )

        assert ehp == pytest.approx(16000.0, abs=100.0)

    def test_ehp_no_mitigation(self):
        """
        Base HP: 2000
        Defense: 0%
        Resistance: 0%

        Expected: 4,000 EHP (2000 / 1.0 / 0.50)
        """
        calculator = DefenseCalculator()

        ehp = calculator.calculate_effective_hp(
            base_hp=2000.0, defense=0.0, resistance=0.0
        )

        assert ehp == pytest.approx(4000.0, abs=100.0)


class TestCombinedDefenseAndResistance:
    """Test Case 8: Combined Defense and Resistance Extraction"""

    def test_power_with_both_defense_and_resistance(self):
        """
        Power: Invulnerability > Invincibility (near max targets)
        Effects:
            - +13.875% Melee defense
            - +13.875% Smashing defense
            - +13.875% Lethal defense
            - +7.5% Smashing resistance
            - +7.5% Lethal resistance

        Expected: Both defense and resistance values extracted
        """
        effects = [
            # Defenses
            Effect(
                unique_id=1,
                effect_type=EffectType.DEFENSE,
                magnitude=0.13875,
                buffed_magnitude=0.13875,
                damage_type=CoreDamageType.SMASHING,
                to_who=ToWho.SELF,
            ),
            Effect(
                unique_id=2,
                effect_type=EffectType.DEFENSE,
                magnitude=0.13875,
                buffed_magnitude=0.13875,
                damage_type=CoreDamageType.LETHAL,
                to_who=ToWho.SELF,
            ),
            # Resistances
            Effect(
                unique_id=4,
                effect_type=EffectType.RESISTANCE,
                magnitude=0.075,
                buffed_magnitude=0.075,
                damage_type=CoreDamageType.SMASHING,
                to_who=ToWho.SELF,
            ),
            Effect(
                unique_id=5,
                effect_type=EffectType.RESISTANCE,
                magnitude=0.075,
                buffed_magnitude=0.075,
                damage_type=CoreDamageType.LETHAL,
                to_who=ToWho.SELF,
            ),
        ]
        # Add positional defense
        melee_def = Effect(
            unique_id=3,
            effect_type=EffectType.DEFENSE,
            magnitude=0.13875,
            buffed_magnitude=0.13875,
            to_who=ToWho.SELF,
        )
        melee_def.position = PositionType.MELEE
        effects.insert(2, melee_def)

        calculator = DefenseCalculator()
        defense = calculator.extract_defense_from_power(effects)
        resistance = calculator.extract_resistance_from_power(effects)

        # Defense checks
        assert defense.smashing == pytest.approx(0.13875, abs=0.001)
        assert defense.lethal == pytest.approx(0.13875, abs=0.001)
        assert defense.melee == pytest.approx(0.13875, abs=0.001)

        # Resistance checks
        assert resistance.smashing == pytest.approx(0.075, abs=0.001)
        assert resistance.lethal == pytest.approx(0.075, abs=0.001)


class TestEdgeCases:
    """Test edge cases and special scenarios"""

    def test_zero_probability_effects_excluded(self):
        """Effects with probability <= 0 should be excluded."""
        effect = Effect(
            unique_id=1,
            effect_type=EffectType.DEFENSE,
            magnitude=0.15,
            buffed_magnitude=0.15,
            damage_type=CoreDamageType.SMASHING,
            probability=0.0,  # Should be excluded
            to_who=ToWho.SELF,
        )

        calculator = DefenseCalculator()
        defense = calculator.extract_defense_from_power([effect])

        # Should be excluded
        assert defense.smashing == pytest.approx(0.0, abs=0.01)

    def test_non_defense_resistance_effects_ignored(self):
        """Non-defense/resistance effects should be ignored."""
        effect = Effect(
            unique_id=1,
            effect_type=EffectType.DAMAGE,  # Not defense/resistance
            magnitude=50.0,
            buffed_magnitude=50.0,
            to_who=ToWho.TARGET,
        )

        calculator = DefenseCalculator()
        defense = calculator.extract_defense_from_power([effect])
        resistance = calculator.extract_resistance_from_power([effect])

        # Should have no defense/resistance
        assert defense.smashing == pytest.approx(0.0, abs=0.01)
        assert resistance.smashing == pytest.approx(0.0, abs=0.01)

    def test_extreme_ddr_over_100_percent(self):
        """DDR can exceed 100% (debuffs become buffs - rare)."""
        calculator = DefenseCalculator()

        net_defense = calculator.apply_defense_debuff(
            base_defense=0.45, defense_debuff=0.20, ddr=1.50  # 150% DDR
        )

        # actual_debuff = 0.20 * (1 - 1.50) = -0.10 (becomes buff)
        # net_defense = 0.45 - (-0.10) = 0.55
        assert net_defense == pytest.approx(0.55, abs=0.01)

    def test_resistance_cap_at_100_percent(self):
        """Resistance values at exactly 100% should cap correctly."""
        calculator = DefenseCalculator(archetype_resistance_cap=0.90)

        capped = calculator.apply_resistance_cap(resistance_value=1.0)

        assert capped == pytest.approx(0.90, abs=0.01)

    def test_ehp_with_damage_immunity(self):
        """100% resistance = infinite EHP."""
        calculator = DefenseCalculator()

        ehp = calculator.calculate_effective_hp(
            base_hp=2000.0, defense=0.0, resistance=1.0
        )

        assert ehp == float("inf")
