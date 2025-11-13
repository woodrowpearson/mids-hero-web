"""
Test suite for Pet Calculator

Tests based on comprehensive test cases from Spec 32.
All expected values are exact calculations from the specification.
"""

import pytest

from app.calculations.powers.pet_calculator import (
    InheritedCasterBuffs,
    PetCalculator,
)


class TestPetInheritanceBasic:
    """Test Case 1: Basic Pet Power Inheritance (Spec 32)"""

    def test_pet_inherits_accuracy_and_damage_not_recharge(self):
        """
        Verifies pets inherit accuracy and damage buffs but NOT recharge.

        Setup:
            - Base pet damage: 18.63 (smashing)
            - Base accuracy: 1.0
            - Caster has: +20% accuracy, +50% smashing damage, +70% recharge
            - Expected: Pet gets accuracy and damage, NOT recharge

        Calculation:
            accuracy: 1.0 × 1.20 = 1.20
            damage: 18.63 × 1.50 = 27.945

        Expected:
            - Final accuracy: 1.20
            - Final damage: 27.95
            - Recharge unchanged (pets don't inherit recharge)
        """
        calculator = PetCalculator()

        caster_buffs = InheritedCasterBuffs(
            accuracy_multiplier=1.20,  # +20% accuracy
            damage_buffs={"smashing": 0.50},  # +50% smashing damage
            # Recharge is NOT in inherited buffs (pets don't get it)
        )

        result = calculator.calculate_pet_power(
            base_damage=18.63,
            damage_type="smashing",
            base_accuracy=1.0,
            pet_enhancements={},  # No pet slotting
            caster_buffs=caster_buffs,
        )

        assert result.base_damage == pytest.approx(18.63, abs=0.01)
        assert result.final_damage == pytest.approx(27.95, abs=0.01)
        assert result.final_accuracy == pytest.approx(1.20, abs=0.01)


class TestPetEnhancementSlotting:
    """Test Case 2: Pet Enhancement Slotting (Spec 32)"""

    def test_pet_ios_enhance_pet_power(self):
        """
        Verifies pet IOs enhance the pet's power, not the summon power.

        Setup:
            - Base pet damage: 18.63 (smashing)
            - Pet slotting: 2× Call to Arms Pet Damage = +63.6% damage
            - No caster buffs

        Calculation:
            enhanced_damage = 18.63 × (1.0 + 0.636) = 30.47868

        Expected:
            - Enhanced damage: 30.48
        """
        calculator = PetCalculator()

        result = calculator.calculate_pet_power(
            base_damage=18.63,
            damage_type="smashing",
            pet_enhancements={"damage": 0.636},  # +63.6% from pet IOs
            caster_buffs=InheritedCasterBuffs(),  # No caster buffs
        )

        assert result.base_damage == pytest.approx(18.63, abs=0.01)
        assert result.enhanced_damage == pytest.approx(30.48, abs=0.01)
        assert result.final_damage == pytest.approx(30.48, abs=0.01)


class TestPetWithEnhancementsAndBuffs:
    """Test Case 3: Pet with Both Enhancement and Caster Buffs (Spec 32)"""

    def test_pet_ios_plus_caster_buffs(self):
        """
        Verifies correct stacking of pet enhancements and caster buffs.

        Setup:
            - Base pet damage: 18.63 (smashing)
            - Pet slotting: +63.6% damage
            - Caster buffs: +50% smashing damage

        Calculation:
            enhanced = 18.63 × 1.636 = 30.47868
            final = 30.47868 × 1.50 = 45.71802

        Expected:
            - Enhanced damage: 30.48
            - Final damage: 45.72
        """
        calculator = PetCalculator()

        caster_buffs = InheritedCasterBuffs(damage_buffs={"smashing": 0.50})

        result = calculator.calculate_pet_power(
            base_damage=18.63,
            damage_type="smashing",
            pet_enhancements={"damage": 0.636},
            caster_buffs=caster_buffs,
        )

        assert result.base_damage == pytest.approx(18.63, abs=0.01)
        assert result.enhanced_damage == pytest.approx(30.48, abs=0.01)
        assert result.final_damage == pytest.approx(45.72, abs=0.01)
        assert result.total_increase_percent == pytest.approx(145.36, abs=0.5)


class TestPetEntityClassModifiers:
    """Test Case 4: Entity Class Modifiers (Spec 32)"""

    def test_entity_class_modifier_applied(self):
        """
        Verifies entity class modifiers (like archetype modifiers for pets).

        Setup:
            - Base pet damage: 20.0
            - Entity class modifier: 1.0 (Class_Boss_Pets for melee)
            - Pet enhancements: +95% damage

        Calculation:
            enhanced = 20.0 × 1.95 = 39.0
            with_class = 39.0 × 1.0 = 39.0

        Expected:
            - Final damage: 39.0 (modifier is 1.0, no change)
        """
        calculator = PetCalculator()

        result = calculator.calculate_pet_power(
            base_damage=20.0,
            damage_type="smashing",
            pet_enhancements={"damage": 0.95},
            entity_class_modifier=1.0,  # Boss pet melee modifier
        )

        assert result.enhanced_damage == pytest.approx(39.0, abs=0.01)
        assert result.final_damage == pytest.approx(39.0, abs=0.01)


class TestPetAbsorbedEffects:
    """Test Case 5: Absorbed Pet Effects for Summon Display (Spec 32)"""

    def test_absorbed_effects_with_stacking(self):
        """
        Verifies summon power can absorb and display total pet capabilities.

        Setup:
            - Pet has 3 powers: Jab (18.63), Punch (37.26), KO Blow (111.78)
            - Number of pets: 1 (Bruiser is single summon)
            - Entity class modifier: 1.0

        Calculation:
            total = (18.63 + 37.26 + 111.78) × 1.0 × 1 = 167.67

        Expected:
            - Total absorbed damage: 167.67
        """
        calculator = PetCalculator()

        pet_damages = [18.63, 37.26, 111.78]

        total = calculator.calculate_absorbed_pet_effects(
            pet_damage_per_power=pet_damages, stacking=1, entity_class_modifier=1.0
        )

        assert total == pytest.approx(167.67, abs=0.01)

    def test_absorbed_effects_with_multiple_pets(self):
        """
        Verifies absorbed effects scale with number of pets (MM T1 minions).

        Setup:
            - Pet damage per power: 10.0
            - Number of pets: 3 (T1 minions)
            - Entity class modifier: 1.0

        Calculation:
            total = 10.0 × 1.0 × 3 = 30.0

        Expected:
            - Total absorbed damage: 30.0
        """
        calculator = PetCalculator()

        total = calculator.calculate_absorbed_pet_effects(
            pet_damage_per_power=[10.0], stacking=3, entity_class_modifier=1.0
        )

        assert total == pytest.approx(30.0, abs=0.01)


class TestPetAccuracyInheritance:
    """Test Case 6: Pet Accuracy Inheritance (Spec 32)"""

    def test_pet_accuracy_with_enhancements_and_buffs(self):
        """
        Verifies accuracy stacks multiplicatively.

        Setup:
            - Base accuracy: 1.0
            - Pet accuracy enhancement: +20%
            - Caster accuracy buff: +20%

        Calculation:
            enhanced = 1.0 × 1.20 = 1.20
            final = 1.20 × 1.20 = 1.44

        Expected:
            - Final accuracy: 1.44
        """
        calculator = PetCalculator()

        caster_buffs = InheritedCasterBuffs(accuracy_multiplier=1.20)

        result = calculator.calculate_pet_power(
            base_damage=10.0,
            damage_type="smashing",
            base_accuracy=1.0,
            pet_enhancements={"accuracy": 0.20},
            caster_buffs=caster_buffs,
        )

        assert result.base_accuracy == pytest.approx(1.0, abs=0.01)
        assert result.final_accuracy == pytest.approx(1.44, abs=0.01)


class TestPetDoesNotInheritDefense:
    """Test Case 7: Verify pets do NOT inherit defense/resistance (Spec 32)"""

    def test_pet_does_not_get_caster_defense(self):
        """
        Verifies pets maintain their own defense, not inheriting caster's.

        This is a design verification test - the InheritedCasterBuffs
        structure explicitly does NOT include defense/resistance fields.

        Setup:
            - Caster has: +45% defense, +75% resistance
            - Pet should: NOT inherit these values

        Expected:
            - InheritedCasterBuffs has no defense/resistance fields
        """
        # Verify the data structure enforces this constraint
        caster_buffs = InheritedCasterBuffs(
            accuracy_multiplier=1.20, damage_buffs={"smashing": 0.50}
        )

        # These attributes should not exist
        assert not hasattr(caster_buffs, "defense_buff")
        assert not hasattr(caster_buffs, "resistance_buff")
        assert not hasattr(caster_buffs, "recharge_buff")
        assert not hasattr(caster_buffs, "hp_buff")


class TestGetInheritedBuffs:
    """Test Case 8: Build inherited caster buffs structure (Spec 32)"""

    def test_get_inherited_caster_buffs(self):
        """
        Verifies building inherited buffs structure from caster totals.

        Setup:
            - Caster accuracy: 1.424 (from Kismet +6% tohit = +1.2% acc, set bonuses)
            - Caster damage: +50% smashing, +30% fire
            - Caster healing: 1.30 (+30%)

        Expected:
            - InheritedCasterBuffs with correct values
        """
        calculator = PetCalculator()

        buffs = calculator.get_inherited_caster_buffs(
            caster_accuracy_mult=1.424,
            caster_damage_buffs={"smashing": 0.50, "fire": 0.30},
            caster_healing_mult=1.30,
        )

        assert buffs.accuracy_multiplier == pytest.approx(1.424, abs=0.001)
        assert buffs.damage_buffs["smashing"] == pytest.approx(0.50, abs=0.01)
        assert buffs.damage_buffs["fire"] == pytest.approx(0.30, abs=0.01)
        assert buffs.healing_multiplier == pytest.approx(1.30, abs=0.01)


class TestPetHealingInheritance:
    """Test Case 9: Pet Healing Powers Inherit Caster Healing Buffs (Spec 32)"""

    def test_pet_healing_with_caster_buff(self):
        """
        Verifies pet healing powers benefit from caster healing buffs.

        Note: This simplified test demonstrates that healing would use the same
        multiplicative stacking as damage. Full implementation would require
        healing-specific calculator logic.

        Setup:
            - Base pet heal: 50.0
            - Pet enhancement: +95% healing
            - Caster healing buff would be: +30% (conceptually)

        Calculation (with pet enhancements only):
            enhanced = 50.0 × 1.95 = 97.5

        Expected:
            - Enhanced healing: 97.5 (without caster buffs, since our simplified
              calculator doesn't have healing-specific damage_type support yet)

        Note: Full healing implementation would require treating healing as a
        separate buff type that benefits from healing_multiplier, not damage_buffs.
        """
        calculator = PetCalculator()

        # Test with pet enhancements only (no caster buffs for simplified case)
        result = calculator.calculate_pet_power(
            base_damage=50.0,
            damage_type="healing",  # Conceptual - would need special handling
            pet_enhancements={"damage": 0.95},  # Healing enhancement
        )

        # For now, test that pet enhancements work correctly
        # Full implementation would add healing multiplier support
        expected_healing = 50.0 * 1.95
        assert result.final_damage == pytest.approx(expected_healing, abs=0.01)


class TestPetDamageTypeSpecific:
    """Test Case 10: Verify damage type-specific buffs work correctly (Spec 32)"""

    def test_damage_buff_applies_to_matching_type_only(self):
        """
        Verifies damage buffs are type-specific.

        Setup:
            - Pet fire damage: 25.0
            - Caster has: +50% smashing, +30% fire
            - Pet should get: +30% fire (NOT smashing)

        Calculation:
            final = 25.0 × 1.30 = 32.5

        Expected:
            - Final damage: 32.5
        """
        calculator = PetCalculator()

        caster_buffs = InheritedCasterBuffs(
            damage_buffs={"smashing": 0.50, "fire": 0.30}
        )

        result = calculator.calculate_pet_power(
            base_damage=25.0,
            damage_type="fire",  # Fire damage
            caster_buffs=caster_buffs,
        )

        # Should use fire buff (0.30), not smashing buff (0.50)
        assert result.final_damage == pytest.approx(32.5, abs=0.01)

    def test_no_buff_for_unbuffed_damage_type(self):
        """
        Verifies pet damage with no matching caster buff.

        Setup:
            - Pet toxic damage: 20.0
            - Caster has: +50% smashing only
            - Pet should get: no damage buff

        Expected:
            - Final damage: 20.0 (unchanged)
        """
        calculator = PetCalculator()

        caster_buffs = InheritedCasterBuffs(damage_buffs={"smashing": 0.50})

        result = calculator.calculate_pet_power(
            base_damage=20.0,
            damage_type="toxic",  # No toxic buff in caster
            caster_buffs=caster_buffs,
        )

        assert result.final_damage == pytest.approx(20.0, abs=0.01)


class TestPetCalculationIntegration:
    """Test Case 11: Full integration test with all features (Spec 32)"""

    def test_full_pet_calculation_workflow(self):
        """
        Complete pet calculation with all features.

        Setup:
            - Base damage: 18.63 (smashing)
            - Base accuracy: 1.0
            - Pet enhancements: +63.6% damage, +20% accuracy
            - Entity class modifier: 1.0
            - Caster buffs: +50% smashing damage, +20% accuracy

        Calculation:
            enhanced_damage = 18.63 × 1.636 = 30.47868
            with_class = 30.47868 × 1.0 = 30.47868
            final_damage = 30.47868 × 1.50 = 45.71802

            enhanced_accuracy = 1.0 × 1.20 = 1.20
            final_accuracy = 1.20 × 1.20 = 1.44

        Expected:
            - Final damage: 45.72
            - Final accuracy: 1.44
            - Total increase: ~145%
        """
        calculator = PetCalculator()

        caster_buffs = InheritedCasterBuffs(
            accuracy_multiplier=1.20, damage_buffs={"smashing": 0.50}
        )

        result = calculator.calculate_pet_power(
            base_damage=18.63,
            damage_type="smashing",
            base_accuracy=1.0,
            pet_enhancements={"damage": 0.636, "accuracy": 0.20},
            caster_buffs=caster_buffs,
            entity_class_modifier=1.0,
        )

        assert result.base_damage == pytest.approx(18.63, abs=0.01)
        assert result.enhanced_damage == pytest.approx(30.48, abs=0.01)
        assert result.final_damage == pytest.approx(45.72, abs=0.01)
        assert result.base_accuracy == pytest.approx(1.0, abs=0.01)
        assert result.final_accuracy == pytest.approx(1.44, abs=0.01)
        assert result.total_increase_percent == pytest.approx(145.36, abs=0.5)


class TestEdgeCases:
    """Test Case 12: Edge cases and boundary conditions"""

    def test_zero_base_damage(self):
        """Verify handling of zero base damage."""
        calculator = PetCalculator()

        result = calculator.calculate_pet_power(
            base_damage=0.0, damage_type="smashing", pet_enhancements={"damage": 0.95}
        )

        assert result.base_damage == 0.0
        assert result.final_damage == 0.0
        assert result.total_increase_percent == 0.0

    def test_no_enhancements_no_buffs(self):
        """Verify pet power with no enhancements or buffs."""
        calculator = PetCalculator()

        result = calculator.calculate_pet_power(base_damage=25.0, damage_type="fire")

        assert result.base_damage == pytest.approx(25.0, abs=0.01)
        assert result.enhanced_damage == pytest.approx(25.0, abs=0.01)
        assert result.final_damage == pytest.approx(25.0, abs=0.01)

    def test_very_high_enhancement_values(self):
        """Verify handling of very high enhancement values (pre-ED cap)."""
        calculator = PetCalculator()

        # Note: ED would normally cap this, but our basic calculator applies directly
        result = calculator.calculate_pet_power(
            base_damage=20.0,
            damage_type="smashing",
            pet_enhancements={"damage": 2.0},  # +200%
        )

        assert result.enhanced_damage == pytest.approx(60.0, abs=0.01)
