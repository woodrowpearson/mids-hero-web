"""
Test suite for Power Accuracy/ToHit Calculator

Tests based on comprehensive test cases from Spec 08, Section 4.
All expected values are exact calculations from the specification.
"""

import pytest

from app.calculations.powers.accuracy_calculator import (
    AccuracyCalculator,
    EntityType,
)


class TestBasicAccuracyCalculation:
    """Test Case 1: Basic Accuracy (No Enhancements, Even Level)"""

    def test_basic_accuracy_even_level(self):
        """
        Power: Energy Blast > Power Bolt (unslotted)
        Level: 50 vs 50 (even level)
        Archetype: Blaster

        Input:
            - Base accuracy: 1.0 (standard)
            - Enhancement: 0.0 (unslotted)
            - Global accuracy buffs: 0.0
            - Global tohit buffs: 0.0
            - ScalingToHit: 0.75 (even level)

        Calculation:
            final_accuracy = 1.0 * (1.0 + 0.0 + 0.0) * (0.75 + 0.0)
                          = 1.0 * 1.0 * 0.75
                          = 0.75 (75%)

        Expected: 75% hit chance vs even-level enemy with no defense
        """
        calculator = AccuracyCalculator(base_tohit=0.75, enemy_level_diff=0)

        result = calculator.calculate_accuracy(
            power_base_accuracy=1.0,
            enhancement_accuracy=0.0,
            global_accuracy_buffs=0.0,
            global_tohit_buffs=0.0,
        )

        assert result.final_accuracy == pytest.approx(0.75, abs=0.01)
        assert result.accuracy_mult == pytest.approx(1.0, abs=0.01)
        assert result.scaling_tohit == pytest.approx(0.75, abs=0.01)
        assert result.hit_chance_vs_even_defense == pytest.approx(0.75, abs=0.01)


class TestAccuracyWithEnhancements:
    """Test Case 2: Accuracy with Enhancements (3 SOs after ED)"""

    def test_three_so_accuracy_even_level(self):
        """
        Power: Energy Blast > Power Bolt (3x level 50 Accuracy SOs)
        Level: 50 vs 50 (even level)

        Input:
            - Base accuracy: 1.0
            - Enhancement: 0.95 (three SOs at 33.3% each = 99.9% → 95% after ED)
            - Global accuracy buffs: 0.0
            - Global tohit buffs: 0.0
            - ScalingToHit: 0.75

        Calculation:
            accuracy_mult = 1.0 * (1.0 + 0.95 + 0.0) = 1.95
            final_accuracy = 1.95 * (0.75 + 0.0) = 1.4625 (146.25%)

        Expected: 146.25% displayed accuracy, 95% hit chance (capped)
        """
        calculator = AccuracyCalculator(base_tohit=0.75, enemy_level_diff=0)

        result = calculator.calculate_accuracy(
            power_base_accuracy=1.0,
            enhancement_accuracy=0.95,  # After ED
            global_accuracy_buffs=0.0,
            global_tohit_buffs=0.0,
        )

        assert result.final_accuracy == pytest.approx(1.4625, abs=0.01)
        assert result.accuracy_mult == pytest.approx(1.95, abs=0.01)
        # Hit chance capped at 95%
        assert result.hit_chance_vs_even_defense == pytest.approx(0.95, abs=0.01)


class TestAccuracyVsPlusLevelEnemies:
    """Test Case 3: Accuracy vs Higher Level Enemies (+4)"""

    def test_accuracy_vs_plus_4_enemies(self):
        """
        Power: Energy Blast > Power Bolt (3x level 50 Accuracy SOs)
        Level: 50 vs 54 (+4 level difference)

        Input:
            - Base accuracy: 1.0
            - Enhancement: 0.95
            - Global accuracy buffs: 0.0
            - Global tohit buffs: 0.0
            - ScalingToHit: 0.39 (+4 enemies)

        Calculation:
            accuracy_mult = 1.0 * (1.0 + 0.95) = 1.95
            final_accuracy = 1.95 * (0.39 + 0.0) = 0.7605 (76.05%)

        Expected: 76.05% displayed accuracy, 76.05% hit chance
        """
        calculator = AccuracyCalculator(base_tohit=0.75, enemy_level_diff=4)

        result = calculator.calculate_accuracy(
            power_base_accuracy=1.0,
            enhancement_accuracy=0.95,
            global_accuracy_buffs=0.0,
            global_tohit_buffs=0.0,
        )

        assert result.scaling_tohit == pytest.approx(0.39, abs=0.01)
        assert result.final_accuracy == pytest.approx(0.7605, abs=0.01)
        assert result.hit_chance_vs_even_defense == pytest.approx(0.7605, abs=0.01)


class TestGlobalAccuracyBuffs:
    """Test Case 4: Global Accuracy Buffs (Kismet +Accuracy)"""

    def test_kismet_accuracy_buff(self):
        """
        Power: Energy Blast > Power Bolt (3 SOs + Kismet)
        Level: 50 vs 50

        Input:
            - Base accuracy: 1.0
            - Enhancement: 0.95
            - Global accuracy buffs: 0.06 (Kismet +6% accuracy - multiplicative!)
            - Global tohit buffs: 0.0
            - ScalingToHit: 0.75

        Calculation:
            accuracy_mult = 1.0 * (1.0 + 0.95 + 0.06) = 2.01
            final_accuracy = 2.01 * (0.75 + 0.0) = 1.5075 (150.75%)

        Expected: 150.75% displayed accuracy, 95% hit chance (capped)
        """
        calculator = AccuracyCalculator(base_tohit=0.75, enemy_level_diff=0)

        result = calculator.calculate_accuracy(
            power_base_accuracy=1.0,
            enhancement_accuracy=0.95,
            global_accuracy_buffs=0.06,  # Kismet
            global_tohit_buffs=0.0,
        )

        assert result.final_accuracy == pytest.approx(1.5075, abs=0.01)
        assert result.accuracy_mult == pytest.approx(2.01, abs=0.01)
        assert result.hit_chance_vs_even_defense == pytest.approx(0.95, abs=0.01)


class TestGlobalToHitBuffs:
    """Test Case 5: Global ToHit Buffs (Build Up, Tactics)"""

    def test_tohit_buffs_build_up_and_tactics(self):
        """
        Power: Energy Blast > Power Bolt (3 SOs) + Build Up + Tactics
        Level: 50 vs 50

        Input:
            - Base accuracy: 1.0
            - Enhancement: 0.95
            - Global accuracy buffs: 0.0
            - Global tohit buffs: 0.27 (Build Up +20% + Tactics +7%)
            - ScalingToHit: 0.75

        Calculation:
            accuracy_mult = 1.0 * (1.0 + 0.95 + 0.0) = 1.95
            final_accuracy = 1.95 * (0.75 + 0.27) = 1.989 (198.9%)

        Expected: 198.9% displayed accuracy, 95% hit chance (capped)
        """
        calculator = AccuracyCalculator(base_tohit=0.75, enemy_level_diff=0)

        result = calculator.calculate_accuracy(
            power_base_accuracy=1.0,
            enhancement_accuracy=0.95,
            global_accuracy_buffs=0.0,
            global_tohit_buffs=0.27,  # Build Up + Tactics
        )

        assert result.final_accuracy == pytest.approx(1.989, abs=0.01)
        assert result.accuracy_mult == pytest.approx(1.95, abs=0.01)
        assert result.hit_chance_vs_even_defense == pytest.approx(0.95, abs=0.01)


class TestSniperAccuracy:
    """Test Case 6: Sniper Powers (Base Accuracy 1.2)"""

    def test_sniper_power_base_accuracy(self):
        """
        Power: Sniper Blast (1.2 base accuracy, 3 SOs)
        Level: 50 vs 50

        Input:
            - Base accuracy: 1.2 (sniper bonus)
            - Enhancement: 0.95
            - Global accuracy buffs: 0.0
            - Global tohit buffs: 0.0
            - ScalingToHit: 0.75

        Calculation:
            accuracy_mult = 1.2 * (1.0 + 0.95 + 0.0) = 2.34
            final_accuracy = 2.34 * (0.75 + 0.0) = 1.755 (175.5%)

        Expected: 175.5% displayed accuracy, 95% hit chance (capped)
        """
        calculator = AccuracyCalculator(base_tohit=0.75, enemy_level_diff=0)

        result = calculator.calculate_accuracy(
            power_base_accuracy=1.2,  # Sniper
            enhancement_accuracy=0.95,
            global_accuracy_buffs=0.0,
            global_tohit_buffs=0.0,
        )

        assert result.final_accuracy == pytest.approx(1.755, abs=0.01)
        assert result.accuracy_mult == pytest.approx(2.34, abs=0.01)
        assert result.hit_chance_vs_even_defense == pytest.approx(0.95, abs=0.01)


class TestAutoHitPowers:
    """Test Case 7: Auto-Hit Powers"""

    def test_auto_hit_self_buff(self):
        """
        Power: Self buff (EntitiesAutoHit = CASTER)

        Input:
            - EntitiesAutoHit: CASTER

        Expected: "Auto" display, 100% hit chance
        """
        calculator = AccuracyCalculator()

        result = calculator.calculate_accuracy(
            power_base_accuracy=1.0,
            enhancement_accuracy=0.0,
            auto_hit_entities=EntityType.CASTER,
        )

        assert result.is_auto_hit is True
        assert result.hit_chance_vs_even_defense == 1.0
        assert str(result) == "Auto"


class TestHitChanceVsDefense:
    """Test Case 8: Hit Chance vs Enemy Defense"""

    def test_hit_chance_vs_45_percent_defense(self):
        """
        Power: Energy Blast > Power Bolt (3 SOs)
        Level: 50 vs 50
        Enemy: 45% defense

        Input:
            - Base accuracy: 1.0
            - Enhancement: 0.95
            - ScalingToHit: 0.75
            - Enemy defense: 0.45

        Calculation:
            final_accuracy = 1.95 * 0.75 = 1.4625
            hit_chance = 1.4625 - 0.45 = 1.0125
            capped = min(0.95, 1.0125) = 0.95 (95%)

        Expected: 95% hit chance (capped)
        """
        calculator = AccuracyCalculator(base_tohit=0.75, enemy_level_diff=0)

        result = calculator.calculate_accuracy(
            power_base_accuracy=1.0,
            enhancement_accuracy=0.95,
        )

        hit_chance = result.hit_chance_vs_defense(enemy_defense=0.45)
        assert hit_chance == pytest.approx(0.95, abs=0.01)

    def test_hit_chance_floor_vs_high_defense(self):
        """
        Test hit chance floor (5%) vs very high defense.

        Enemy: 200% defense (extreme case)

        Expected: 5% hit chance (floored)
        """
        calculator = AccuracyCalculator(base_tohit=0.75, enemy_level_diff=0)

        result = calculator.calculate_accuracy(
            power_base_accuracy=1.0,
            enhancement_accuracy=0.95,
        )

        hit_chance = result.hit_chance_vs_defense(enemy_defense=2.0)
        assert hit_chance == pytest.approx(0.05, abs=0.01)


class TestIgnoreBuffFlags:
    """Test Case 9: Powers that Ignore Buffs"""

    def test_ignore_accuracy_buffs(self):
        """
        Power that ignores accuracy buffs (some inherent powers).

        Input:
            - Global accuracy buffs: 0.06 (Kismet)
            - Ignores accuracy buffs: True

        Expected: Accuracy buffs not applied
        """
        calculator = AccuracyCalculator(base_tohit=0.75, enemy_level_diff=0)

        result = calculator.calculate_accuracy(
            power_base_accuracy=1.0,
            enhancement_accuracy=0.95,
            global_accuracy_buffs=0.06,  # Should be ignored
            ignores_accuracy_buffs=True,
        )

        # Should NOT include Kismet bonus
        assert result.global_accuracy_buff == 0.0
        assert result.accuracy_mult == pytest.approx(1.95, abs=0.01)
        assert result.final_accuracy == pytest.approx(1.4625, abs=0.01)

    def test_ignore_tohit_buffs(self):
        """
        Power that ignores tohit buffs (some auto-powers).

        Input:
            - Global tohit buffs: 0.20 (Build Up)
            - Ignores tohit buffs: True

        Expected: ToHit buffs not applied
        """
        calculator = AccuracyCalculator(base_tohit=0.75, enemy_level_diff=0)

        result = calculator.calculate_accuracy(
            power_base_accuracy=1.0,
            enhancement_accuracy=0.95,
            global_tohit_buffs=0.20,  # Should be ignored
            ignores_tohit_buffs=True,
        )

        # Should NOT include Build Up bonus
        assert result.global_tohit_buff == 0.0
        assert result.final_accuracy == pytest.approx(1.4625, abs=0.01)


class TestPurplePatchScaling:
    """Test Case 10: Purple Patch Level Scaling"""

    def test_all_level_differences(self):
        """Test ScalingToHit for all level differences."""
        test_cases = [
            (-4, 0.95),  # Gray con (very easy)
            (-3, 0.90),
            (-2, 0.85),
            (-1, 0.80),
            (0, 0.75),  # Even level
            (1, 0.65),  # Orange con
            (2, 0.56),  # Red con
            (3, 0.48),  # Purple con
            (4, 0.39),  # Purple +1
            (5, 0.30),  # Purple +2
            (6, 0.20),  # Purple +3
            (7, 0.08),  # Purple +4 (nearly impossible)
        ]

        for level_diff, expected_scaling in test_cases:
            calculator = AccuracyCalculator(
                base_tohit=0.75, enemy_level_diff=level_diff
            )

            result = calculator.calculate_accuracy(
                power_base_accuracy=1.0, enhancement_accuracy=0.0
            )

            assert result.scaling_tohit == pytest.approx(expected_scaling, abs=0.01), (
                f"Level diff {level_diff:+d}: expected {expected_scaling}, "
                f"got {result.scaling_tohit}"
            )


class TestAccuracyResultFormatting:
    """Test AccuracyResult display formatting"""

    def test_str_formatting_percentage(self):
        """Test __str__ method for normal accuracy."""
        calculator = AccuracyCalculator(base_tohit=0.75, enemy_level_diff=0)

        result = calculator.calculate_accuracy(
            power_base_accuracy=1.0,
            enhancement_accuracy=0.95,
        )

        # Should format as percentage
        assert "146" in str(result) or "1.46" in str(result)

    def test_str_formatting_auto_hit(self):
        """Test __str__ method for auto-hit powers."""
        calculator = AccuracyCalculator()

        result = calculator.calculate_accuracy(
            power_base_accuracy=1.0,
            enhancement_accuracy=0.0,
            auto_hit_entities=EntityType.CASTER,
        )

        assert str(result) == "Auto"


class TestEdgeCases:
    """Test edge cases and special scenarios"""

    def test_zero_base_accuracy(self):
        """Some powers may have 0 base accuracy (always miss)."""
        calculator = AccuracyCalculator(base_tohit=0.75, enemy_level_diff=0)

        result = calculator.calculate_accuracy(
            power_base_accuracy=0.0,
            enhancement_accuracy=0.95,
        )

        assert result.final_accuracy == 0.0
        assert result.hit_chance_vs_even_defense == pytest.approx(0.05, abs=0.01)

    def test_extreme_accuracy_buffs(self):
        """Test with extreme accuracy buffs (Alpha Incarnate + all bonuses)."""
        calculator = AccuracyCalculator(base_tohit=0.75, enemy_level_diff=0)

        result = calculator.calculate_accuracy(
            power_base_accuracy=1.0,
            enhancement_accuracy=0.95,
            global_accuracy_buffs=0.33,  # Alpha T4 Musculature
            global_tohit_buffs=0.27,  # Build Up + Tactics
        )

        # accuracy_mult = 1.0 * (1.0 + 0.95 + 0.33) = 2.28
        # final_accuracy = 2.28 * (0.75 + 0.27) = 2.3256
        assert result.final_accuracy == pytest.approx(2.3256, abs=0.01)
        # Capped at 95%
        assert result.hit_chance_vs_even_defense == pytest.approx(0.95, abs=0.01)

    def test_negative_tohit_scenario(self):
        """Test scenario where net tohit goes negative (extreme defense debuffs)."""
        calculator = AccuracyCalculator(base_tohit=0.75, enemy_level_diff=0)

        result = calculator.calculate_accuracy(
            power_base_accuracy=1.0,
            enhancement_accuracy=0.0,
            global_tohit_buffs=-0.80,  # Extreme tohit debuff
        )

        # final_accuracy = 1.0 * (0.75 - 0.80) = -0.05
        # But hit chance floored at 5%
        assert result.hit_chance_vs_even_defense == pytest.approx(0.05, abs=0.01)
