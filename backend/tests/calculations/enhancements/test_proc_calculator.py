"""
Test suite for Proc Chance Calculator

Tests based on comprehensive test cases from Spec 34.
All expected values are exact calculations from the specification.
"""

import pytest

from app.calculations.enhancements.proc_calculator import (
    CharacterProcContext,
    EffectArea,
    PowerProcContext,
    PowerType,
    ProcChanceCalculator,
    ProcEnhancement,
)


class TestAoEModifierCalculation:
    """Test Case 1: AoE Modifier Calculation (Spec 34)"""

    def test_single_target_modifier(self):
        """
        Verify AoE modifier for single target power.

        Setup:
            - Effect Area: Single
            - Radius: 0

        Expected:
            - AoE Modifier: 1.0
        """
        calculator = ProcChanceCalculator()

        power = PowerProcContext(
            power_type=PowerType.CLICK,
            base_recharge_time=4.0,
            current_recharge_time=4.0,
            cast_time=1.0,
            effect_area=EffectArea.SINGLE,
            radius=0.0,
        )

        modifier = calculator.calculate_aoe_modifier(power)
        assert modifier == pytest.approx(1.0, abs=0.01)

    def test_sphere_modifier_small_radius(self):
        """
        Verify AoE modifier for small sphere.

        Setup:
            - Effect Area: Sphere
            - Radius: 10 feet

        Formula:
            modifier = 1 + 10 × 0.15 = 2.5

        Expected:
            - AoE Modifier: 2.5
        """
        calculator = ProcChanceCalculator()

        power = PowerProcContext(
            power_type=PowerType.CLICK,
            base_recharge_time=8.0,
            current_recharge_time=8.0,
            cast_time=1.0,
            effect_area=EffectArea.SPHERE,
            radius=10.0,
        )

        modifier = calculator.calculate_aoe_modifier(power)
        assert modifier == pytest.approx(2.5, abs=0.01)

    def test_sphere_modifier_large_radius(self):
        """
        Verify AoE modifier for large sphere.

        Setup:
            - Effect Area: Sphere
            - Radius: 25 feet

        Formula:
            modifier = 1 + 25 × 0.15 = 4.75

        Expected:
            - AoE Modifier: 4.75
        """
        calculator = ProcChanceCalculator()

        power = PowerProcContext(
            power_type=PowerType.CLICK,
            base_recharge_time=16.0,
            current_recharge_time=16.0,
            cast_time=2.03,
            effect_area=EffectArea.SPHERE,
            radius=25.0,
        )

        modifier = calculator.calculate_aoe_modifier(power)
        assert modifier == pytest.approx(4.75, abs=0.01)

    def test_cone_modifier_narrow_arc(self):
        """
        Verify AoE modifier for narrow cone.

        Setup:
            - Effect Area: Cone
            - Radius: 40 feet
            - Arc: 30 degrees

        Formula:
            modifier = 1 + 40 × 0.15 - 40 × 0.000366669992217794 × (360 - 30)
                     = 1 + 6.0 - 40 × 0.000366669992217794 × 330
                     = 1 + 6.0 - 4.84
                     = 2.16

        Expected:
            - AoE Modifier: ~2.16
        """
        calculator = ProcChanceCalculator()

        power = PowerProcContext(
            power_type=PowerType.CLICK,
            base_recharge_time=12.0,
            current_recharge_time=12.0,
            cast_time=1.67,
            effect_area=EffectArea.CONE,
            radius=40.0,
            arc=30,
        )

        modifier = calculator.calculate_aoe_modifier(power)
        expected = 1 + 40 * 0.15 - 40 * 0.000366669992217794 * (360 - 30)
        assert modifier == pytest.approx(expected, abs=0.01)


class TestAreaFactorCalculation:
    """Test Case 2: Area Factor Calculation (Spec 34)"""

    def test_area_factor_single_target(self):
        """
        Verify area factor for single target.

        Formula:
            areaFactor = AoEModifier × 0.75 + 0.25
            areaFactor = 1.0 × 0.75 + 0.25 = 1.0

        Expected:
            - Area Factor: 1.0
        """
        calculator = ProcChanceCalculator()

        power = PowerProcContext(
            power_type=PowerType.CLICK,
            base_recharge_time=4.0,
            current_recharge_time=4.0,
            cast_time=1.0,
            effect_area=EffectArea.SINGLE,
        )

        factor = calculator.calculate_area_factor(power)
        assert factor == pytest.approx(1.0, abs=0.01)

    def test_area_factor_small_aoe(self):
        """
        Verify area factor for small AoE.

        Setup:
            - Radius: 10 feet (modifier = 2.5)

        Formula:
            areaFactor = 2.5 × 0.75 + 0.25 = 2.125

        Expected:
            - Area Factor: 2.125
        """
        calculator = ProcChanceCalculator()

        power = PowerProcContext(
            power_type=PowerType.CLICK,
            base_recharge_time=8.0,
            current_recharge_time=8.0,
            cast_time=1.0,
            effect_area=EffectArea.SPHERE,
            radius=10.0,
        )

        factor = calculator.calculate_area_factor(power)
        assert factor == pytest.approx(2.125, abs=0.01)

    def test_area_factor_large_aoe(self):
        """
        Verify area factor for large AoE.

        Setup:
            - Radius: 25 feet (modifier = 4.75)

        Formula:
            areaFactor = 4.75 × 0.75 + 0.25 = 3.8125

        Expected:
            - Area Factor: 3.8125
        """
        calculator = ProcChanceCalculator()

        power = PowerProcContext(
            power_type=PowerType.CLICK,
            base_recharge_time=16.0,
            current_recharge_time=16.0,
            cast_time=2.03,
            effect_area=EffectArea.SPHERE,
            radius=25.0,
        )

        factor = calculator.calculate_area_factor(power)
        assert factor == pytest.approx(3.8125, abs=0.01)


class TestMinProcChanceCap:
    """Test Case 3: Minimum Proc Chance Cap (Spec 34)"""

    def test_min_cap_1_ppm(self):
        """
        Verify minimum cap for 1.0 PPM.

        Formula:
            minChance = 1.0 × 0.015 + 0.05 = 0.065 (6.5%)

        Expected:
            - Min Chance: 6.5%
        """
        calculator = ProcChanceCalculator()

        min_chance = calculator.calculate_min_proc_chance(1.0)
        assert min_chance == pytest.approx(0.065, abs=0.001)

    def test_min_cap_3_5_ppm(self):
        """
        Verify minimum cap for 3.5 PPM.

        Formula:
            minChance = 3.5 × 0.015 + 0.05 = 0.1025 (10.25%)

        Expected:
            - Min Chance: 10.25%
        """
        calculator = ProcChanceCalculator()

        min_chance = calculator.calculate_min_proc_chance(3.5)
        assert min_chance == pytest.approx(0.1025, abs=0.001)

    def test_min_cap_4_5_ppm(self):
        """
        Verify minimum cap for 4.5 PPM.

        Formula:
            minChance = 4.5 × 0.015 + 0.05 = 0.1175 (11.75%)

        Expected:
            - Min Chance: 11.75%
        """
        calculator = ProcChanceCalculator()

        min_chance = calculator.calculate_min_proc_chance(4.5)
        assert min_chance == pytest.approx(0.1175, abs=0.001)


class TestEffectiveRechargeCalculation:
    """Test Case 4: Effective Recharge Calculation (Spec 34)"""

    def test_effective_recharge_no_global(self):
        """
        Verify effective recharge with no global recharge.

        Setup:
            - Base recharge: 8.0s
            - Current recharge: 4.0s (from enhancements)
            - Global recharge: 0.0

        Formula:
            effective = 8.0 / (8.0 / 4.0 - 0.0) = 8.0 / 2.0 = 4.0

        Expected:
            - Effective Recharge: 4.0s
        """
        calculator = ProcChanceCalculator()

        power = PowerProcContext(
            power_type=PowerType.CLICK,
            base_recharge_time=8.0,
            current_recharge_time=4.0,
            cast_time=1.0,
            effect_area=EffectArea.SINGLE,
        )

        character = CharacterProcContext(global_recharge_bonus=0.0)

        effective = calculator.calculate_effective_recharge(power, character)
        assert effective == pytest.approx(4.0, abs=0.01)

    def test_effective_recharge_with_global(self):
        """
        Verify effective recharge removes global bonuses.

        Setup:
            - Base recharge: 8.0s
            - Current recharge: 2.35s (with enhancements + global)
            - Global recharge: +70% (0.7)

        Formula:
            effective = 8.0 / (8.0 / 2.35 - 0.7)
                     = 8.0 / (3.404 - 0.7)
                     = 8.0 / 2.704
                     = 2.958s

        Expected:
            - Effective Recharge: ~2.96s (removes global, keeps enhancement)
        """
        calculator = ProcChanceCalculator()

        power = PowerProcContext(
            power_type=PowerType.CLICK,
            base_recharge_time=8.0,
            current_recharge_time=2.35,
            cast_time=1.0,
            effect_area=EffectArea.SINGLE,
        )

        character = CharacterProcContext(global_recharge_bonus=0.7)

        effective = calculator.calculate_effective_recharge(power, character)
        expected = 8.0 / (8.0 / 2.35 - 0.7)
        assert effective == pytest.approx(expected, abs=0.01)


class TestProcChanceClickPowers:
    """Test Case 5: Proc Chance for Click Powers (Spec 34)"""

    def test_fast_single_target_click(self):
        """
        Verify proc chance for fast single-target attack.

        Setup:
            - PPM: 3.5
            - Base recharge: 4.0s
            - Current recharge: 2.35s (with enhancements)
            - Cast time: 1.0s
            - Effect area: Single
            - Global recharge: +70% (0.7)

        Calculation:
            effective_recharge = 4.0 / (4.0 / 2.35 - 0.7) = 4.0 / 1.0
            = 4.0s (approximately)
            area_factor = 1.0
            chance = 3.5 × (4.0 + 1.0) / (60 × 1.0) = 17.5 / 60 = 0.2917

        Expected:
            - Proc Chance: ~29.17%
        """
        calculator = ProcChanceCalculator()

        proc = ProcEnhancement(name="Test Proc", procs_per_minute=3.5)

        power = PowerProcContext(
            power_type=PowerType.CLICK,
            base_recharge_time=4.0,
            current_recharge_time=2.35,
            cast_time=1.0,
            effect_area=EffectArea.SINGLE,
        )

        character = CharacterProcContext(global_recharge_bonus=0.7)

        chance = calculator.calculate_proc_chance(proc, power, character)

        # Allow some variance due to effective recharge calculation
        assert 0.25 <= chance <= 0.35

    def test_large_aoe_click(self):
        """
        Verify proc chance for large AoE attack.

        Setup:
            - PPM: 3.5
            - Base recharge: 16.0s
            - Current recharge: 8.0s
            - Cast time: 2.03s
            - Effect area: Sphere, radius 25 feet
            - Global recharge: +70%

        Calculation:
            effective_recharge ≈ 9.4s (with global removal)
            aoe_modifier = 4.75
            area_factor = 4.75 × 0.75 + 0.25 = 3.8125
            chance = 3.5 × (9.4 + 2.03) / (60 × 3.8125) ≈ 0.1746

        Expected:
            - Proc Chance: ~17-22% (area penalty reduces chance significantly)
        """
        calculator = ProcChanceCalculator()

        proc = ProcEnhancement(name="AoE Proc", procs_per_minute=3.5)

        power = PowerProcContext(
            power_type=PowerType.CLICK,
            base_recharge_time=16.0,
            current_recharge_time=8.0,
            cast_time=2.03,
            effect_area=EffectArea.SPHERE,
            radius=25.0,
        )

        character = CharacterProcContext(global_recharge_bonus=0.7)

        chance = calculator.calculate_proc_chance(proc, power, character)

        # AoE penalty should significantly reduce chance
        assert 0.15 <= chance <= 0.25


class TestProcChanceTogglePowers:
    """Test Case 6: Proc Chance for Toggle Powers (Spec 34)"""

    def test_damage_aura_toggle(self):
        """
        Verify proc chance for toggle power (damage aura).

        Setup:
            - PPM: 2.0
            - Power type: Toggle
            - Effect area: Sphere, radius 8 feet
            - Cast time: 1.17s (not used for toggles)

        Formula:
            aoe_modifier = 1 + 8 × 0.15 = 2.2
            area_factor = 2.2 × 0.75 + 0.25 = 1.9
            chance = 2.0 × 10 / (60 × 1.9) = 20 / 114 = 0.1754

        Expected:
            - Proc Chance: ~17.54%
        """
        calculator = ProcChanceCalculator()

        proc = ProcEnhancement(name="Toggle Proc", procs_per_minute=2.0)

        power = PowerProcContext(
            power_type=PowerType.TOGGLE,
            base_recharge_time=0.0,  # Toggles have no recharge
            current_recharge_time=0.0,
            cast_time=1.17,
            effect_area=EffectArea.SPHERE,
            radius=8.0,
        )

        character = CharacterProcContext()

        chance = calculator.calculate_proc_chance(proc, power, character)
        expected = 2.0 * 10 / (60 * (2.2 * 0.75 + 0.25))
        assert chance == pytest.approx(expected, abs=0.01)


class TestMaxProcChanceCap:
    """Test Case 7: Maximum Proc Chance Cap (Spec 34)"""

    def test_slow_nuke_hits_max_cap(self):
        """
        Verify maximum 90% cap for slow nuke.

        Setup:
            - PPM: 4.5
            - Base recharge: 145.0s
            - Current recharge: 50.0s
            - Cast time: 3.0s
            - Global recharge: +120%

        Calculation:
            effective_recharge ≈ 60.4s (with global removal)
            area_factor = 1.0 (single target)
            uncapped = 4.5 × (60.4 + 3.0) / 60 = 4.76 (>1.0)
            capped = 0.90

        Expected:
            - Proc Chance: 90% (maximum cap)
        """
        calculator = ProcChanceCalculator()

        proc = ProcEnhancement(name="Nuke Proc", procs_per_minute=4.5)

        power = PowerProcContext(
            power_type=PowerType.CLICK,
            base_recharge_time=145.0,
            current_recharge_time=50.0,
            cast_time=3.0,
            effect_area=EffectArea.SINGLE,
        )

        character = CharacterProcContext(global_recharge_bonus=1.2)

        chance = calculator.calculate_proc_chance(proc, power, character)

        # Should hit the 90% maximum cap
        assert chance == pytest.approx(0.90, abs=0.01)


class TestMinProcChanceCapEnforcement:
    """Test Case 8: Minimum Cap Enforcement (Spec 34)"""

    def test_very_fast_power_hits_min_cap(self):
        """
        Verify minimum cap for very fast power.

        Setup:
            - PPM: 3.5
            - Base recharge: 1.0s
            - Current recharge: 0.5s
            - Cast time: 0.67s
            - Global recharge: +70%

        Calculation:
            effective_recharge ≈ 1.0s
            uncapped = 3.5 × (1.0 + 0.67) / 60 = 0.0971
            min_cap = 3.5 × 0.015 + 0.05 = 0.1025
            final = max(0.0971, 0.1025) = 0.1025

        Expected:
            - Proc Chance: 10.25% (minimum cap enforced)
        """
        calculator = ProcChanceCalculator()

        proc = ProcEnhancement(name="Fast Proc", procs_per_minute=3.5)

        power = PowerProcContext(
            power_type=PowerType.CLICK,
            base_recharge_time=1.0,
            current_recharge_time=0.5,
            cast_time=0.67,
            effect_area=EffectArea.SINGLE,
        )

        character = CharacterProcContext(global_recharge_bonus=0.7)

        chance = calculator.calculate_proc_chance(proc, power, character)

        # Should hit the minimum cap
        min_cap = 3.5 * 0.015 + 0.05
        assert chance == pytest.approx(min_cap, abs=0.001)


class TestLegacyFlatPercentageProcs:
    """Test Case 9: Legacy Flat Percentage Procs (Spec 34)"""

    def test_legacy_flat_proc(self):
        """
        Verify legacy flat % proc (pre-Issue 24).

        Setup:
            - PPM: 0.0 (indicates legacy)
            - Base probability: 0.20 (20%)
            - Power properties: (not used for legacy)

        Expected:
            - Proc Chance: 20% (flat, ignores power properties)
        """
        calculator = ProcChanceCalculator()

        proc = ProcEnhancement(
            name="Legacy Proc", procs_per_minute=0.0, base_probability=0.20
        )

        power = PowerProcContext(
            power_type=PowerType.CLICK,
            base_recharge_time=4.0,
            current_recharge_time=2.0,
            cast_time=1.0,
            effect_area=EffectArea.SINGLE,
        )

        character = CharacterProcContext()

        chance = calculator.calculate_proc_chance(proc, power, character)

        # Should return base probability, ignoring power properties
        assert chance == pytest.approx(0.20, abs=0.001)


class TestProcCalculationDetailed:
    """Test Case 10: Detailed Proc Calculation Result (Spec 34)"""

    def test_detailed_calculation_result(self):
        """
        Verify detailed calculation result includes all breakdown values.

        Setup:
            - PPM: 3.5
            - Fast single-target click

        Expected:
            - Result includes all intermediate values
            - Flags indicate which caps were applied
        """
        calculator = ProcChanceCalculator()

        proc = ProcEnhancement(name="Detail Proc", procs_per_minute=3.5)

        power = PowerProcContext(
            power_type=PowerType.CLICK,
            base_recharge_time=4.0,
            current_recharge_time=2.35,
            cast_time=1.0,
            effect_area=EffectArea.SINGLE,
        )

        character = CharacterProcContext(global_recharge_bonus=0.7)

        result = calculator.calculate_proc_chance_detailed(proc, power, character)

        # Verify structure
        assert hasattr(result, "proc_chance")
        assert hasattr(result, "aoe_modifier")
        assert hasattr(result, "area_factor")
        assert hasattr(result, "effective_recharge")
        assert hasattr(result, "min_cap")
        assert hasattr(result, "calculation_method")

        # Verify values make sense
        assert 0.0 <= result.proc_chance <= 1.0
        assert result.aoe_modifier == pytest.approx(1.0, abs=0.01)
        assert result.area_factor == pytest.approx(1.0, abs=0.01)
        assert result.calculation_method == "ppm_click"


class TestEdgeCases:
    """Test Case 11: Edge Cases and Boundary Conditions"""

    def test_zero_recharge_power(self):
        """Verify handling of zero recharge time."""
        calculator = ProcChanceCalculator()

        proc = ProcEnhancement(name="Zero Recharge", procs_per_minute=3.5)

        power = PowerProcContext(
            power_type=PowerType.CLICK,
            base_recharge_time=0.0,
            current_recharge_time=0.0,
            cast_time=1.0,
            effect_area=EffectArea.SINGLE,
        )

        character = CharacterProcContext()

        # Should not crash, returns minimum cap
        chance = calculator.calculate_proc_chance(proc, power, character)
        min_cap = 3.5 * 0.015 + 0.05
        assert chance == pytest.approx(min_cap, abs=0.001)

    def test_extremely_large_radius(self):
        """Verify handling of extremely large AoE radius."""
        calculator = ProcChanceCalculator()

        proc = ProcEnhancement(name="Huge AoE", procs_per_minute=3.5)

        power = PowerProcContext(
            power_type=PowerType.CLICK,
            base_recharge_time=16.0,
            current_recharge_time=16.0,
            cast_time=2.0,
            effect_area=EffectArea.SPHERE,
            radius=100.0,  # Extremely large
        )

        character = CharacterProcContext()

        chance = calculator.calculate_proc_chance(proc, power, character)

        # Should still return valid probability
        assert 0.0 <= chance <= 1.0
        # Should hit minimum cap due to massive area penalty
        min_cap = 3.5 * 0.015 + 0.05
        assert chance == pytest.approx(min_cap, abs=0.001)

    def test_high_global_recharge(self):
        """Verify handling of very high global recharge."""
        calculator = ProcChanceCalculator()

        proc = ProcEnhancement(name="High Recharge", procs_per_minute=3.5)

        power = PowerProcContext(
            power_type=PowerType.CLICK,
            base_recharge_time=8.0,
            current_recharge_time=1.5,
            cast_time=1.0,
            effect_area=EffectArea.SINGLE,
        )

        character = CharacterProcContext(global_recharge_bonus=2.0)  # +200%

        # Should handle high global recharge gracefully
        chance = calculator.calculate_proc_chance(proc, power, character)
        assert 0.0 <= chance <= 1.0


class TestRealWorldScenarios:
    """Test Case 12: Real-world build scenarios"""

    def test_apocalypse_proc_in_blaster_attack(self):
        """
        Real scenario: Apocalypse proc in Blaster single-target attack.

        Setup:
            - Apocalypse: Chance for Negative (3.5 PPM)
            - Power: Energy Bolt (4s recharge, 1s cast)
            - Slotted: 95% recharge reduction
            - Character: +70% global recharge (Hasten)

        Expected:
            - Reasonable proc chance (20-35%)
        """
        calculator = ProcChanceCalculator()

        proc = ProcEnhancement(
            name="Apocalypse: Chance for Negative", procs_per_minute=3.5
        )

        power = PowerProcContext(
            power_type=PowerType.CLICK,
            base_recharge_time=4.0,
            current_recharge_time=4.0 / 1.95,  # With 95% enhancement
            cast_time=1.0,
            effect_area=EffectArea.SINGLE,
        )

        character = CharacterProcContext(global_recharge_bonus=0.7)

        chance = calculator.calculate_proc_chance(proc, power, character)

        assert 0.20 <= chance <= 0.35

    def test_force_feedback_in_aoe_knockdown(self):
        """
        Real scenario: Force Feedback proc in AoE knockdown power.

        Setup:
            - Force Feedback: +Recharge (2.0 PPM)
            - Power: Foot Stomp (20s recharge, 2.1s cast, 15ft radius)
            - Slotted: 95% recharge
            - Character: +70% global recharge

        Calculation:
            - AoE modifier = 1 + 15 × 0.15 = 3.25
            - Area factor = 3.25 × 0.75 + 0.25 = 2.6875
            - Effective recharge ≈ 20.0 / (20.0 / 10.26 - 0.7) ≈ 16.0s
            - Chance = 2.0 × (16.0 + 2.1) / (60 × 2.6875) ≈ 0.224

        Expected:
            - Proc chance with AoE penalty: ~22-24%
        """
        calculator = ProcChanceCalculator()

        proc = ProcEnhancement(name="Force Feedback: +Recharge", procs_per_minute=2.0)

        power = PowerProcContext(
            power_type=PowerType.CLICK,
            base_recharge_time=20.0,
            current_recharge_time=20.0 / 1.95,
            cast_time=2.1,
            effect_area=EffectArea.SPHERE,
            radius=15.0,
        )

        character = CharacterProcContext(global_recharge_bonus=0.7)

        chance = calculator.calculate_proc_chance(proc, power, character)

        # AoE penalty reduces chance, but power is slow enough to stay reasonable
        assert 0.20 <= chance <= 0.25
