"""
Test suite for ToHit and Accuracy calculations.

Tests the complete ToHit system including base calculations,
buffs/debuffs, defense integration, and hit chance limits.
"""

from app.calc.tohit import ToHitCalculator


class TestToHitCalculations:
    """Test cases for ToHit and Accuracy system."""

    def test_base_tohit_chance(self):
        """Base ToHit should be 75% for even-con enemies."""
        # Arrange
        calculator = ToHitCalculator()

        # Act
        chance = calculator.calculate_base_tohit(
            attacker_level=50,
            target_level=50
        )

        # Assert
        assert chance == 0.75

    def test_base_tohit_level_difference(self):
        """ToHit should adjust by 5% per level difference."""
        # Arrange
        calculator = ToHitCalculator()

        # Test higher level attacker
        chance_plus5 = calculator.calculate_base_tohit(50, 45)  # +5 levels
        assert chance_plus5 == 1.0  # 75% + (5 * 5%) = 100%

        # Test lower level attacker
        chance_minus5 = calculator.calculate_base_tohit(45, 50)  # -5 levels
        assert chance_minus5 == 0.5  # 75% - (5 * 5%) = 50%

    def test_base_tohit_pvp(self):
        """PvP should use 50% base ToHit regardless of level."""
        # Arrange
        calculator = ToHitCalculator()

        # Act - same level
        chance_even = calculator.calculate_base_tohit(50, 50, is_pvp=True)
        # Act - different levels
        chance_diff = calculator.calculate_base_tohit(50, 45, is_pvp=True)

        # Assert - both should be 50%
        assert chance_even == 0.5
        assert chance_diff == 0.5

    def test_tohit_with_buffs_and_defense(self):
        """Should apply ToHit buffs and subtract defense."""
        # Arrange
        calculator = ToHitCalculator()
        combat_data = {
            'base_tohit': 0.75,
            'tohit_buffs': 0.15,  # +15% from Tactics
            'target_defense': 0.45,  # Soft-capped defense
            'accuracy': 1.0
        }

        # Act
        final_chance = calculator.calculate_hit_chance(combat_data)

        # Assert
        # 75% + 15% - 45% = 45% * 1.0 accuracy = 45%
        assert final_chance == 0.45

    def test_tohit_floor_and_ceiling(self):
        """Hit chance should respect 5% floor and 95% ceiling."""
        # Arrange
        calculator = ToHitCalculator()

        # Test floor
        low_chance = calculator.calculate_hit_chance({
            'base_tohit': 0.75,
            'tohit_buffs': 0.0,
            'target_defense': 0.95,  # Very high defense
            'accuracy': 1.0
        })
        assert low_chance == 0.05  # 5% floor

        # Test ceiling
        high_chance = calculator.calculate_hit_chance({
            'base_tohit': 0.75,
            'tohit_buffs': 0.50,  # High buffs
            'target_defense': 0.0,
            'accuracy': 2.0  # High accuracy
        })
        assert high_chance == 0.95  # 95% ceiling

    def test_accuracy_multiplier(self):
        """Accuracy should multiply after ToHit calculation."""
        # Arrange
        calculator = ToHitCalculator()
        combat_data = {
            'base_tohit': 0.50,
            'tohit_buffs': 0.0,
            'target_defense': 0.0,
            'accuracy': 1.5  # +50% accuracy enhancement
        }

        # Act
        chance = calculator.calculate_hit_chance(combat_data)

        # Assert
        assert chance == 0.75  # 50% * 1.5 = 75%

    def test_negative_tohit_buffs(self):
        """Should handle ToHit debuffs (negative buffs)."""
        # Arrange
        calculator = ToHitCalculator()
        combat_data = {
            'base_tohit': 0.75,
            'tohit_buffs': -0.20,  # -20% ToHit debuff
            'target_defense': 0.0,
            'accuracy': 1.0
        }

        # Act
        chance = calculator.calculate_hit_chance(combat_data)

        # Assert
        assert chance == 0.55  # 75% - 20% = 55%

    def test_combined_buffs_defense_accuracy(self):
        """Test complex scenario with all factors."""
        # Arrange
        calculator = ToHitCalculator()
        combat_data = {
            'base_tohit': 0.75,      # Even con
            'tohit_buffs': 0.30,     # +30% from multiple sources
            'target_defense': 0.25,   # 25% defense
            'accuracy': 1.4          # 40% accuracy enhancement
        }

        # Act
        chance = calculator.calculate_hit_chance(combat_data)

        # Assert
        # (75% + 30% - 25%) * 1.4 = 80% * 1.4 = 112% -> clamped to 95%
        assert chance == 0.95

    def test_calculate_power_hit_chance(self):
        """Test the complete power hit chance calculation."""
        # Arrange
        calculator = ToHitCalculator()

        # Act
        hit_chance = calculator.calculate_power_hit_chance(
            power_accuracy=1.0,          # Standard power
            tohit_buffs=0.15,           # 15% ToHit buff
            target_defense=0.30,        # 30% defense
            accuracy_enhancements=0.40,  # 40% accuracy enhancement (post-ED)
            global_accuracy_bonus=0.10,  # 10% global accuracy
            attacker_level=50,
            target_level=50
        )

        # Assert
        # Base: 75%, +15% buff, -30% def = 60%
        # Accuracy: 1.0 * (1 + 0.4 + 0.1) = 1.5
        # Final: 60% * 1.5 = 90%
        assert abs(hit_chance - 0.90) < 0.0001  # Allow for floating point precision

    def test_defense_cascade_tohit(self):
        """Test defense cascade selection."""
        # Arrange
        calculator = ToHitCalculator()
        defense_values = {
            'smashing': 0.20,
            'lethal': 0.15,
            'melee': 0.30,
            'ranged': 0.25,
            'aoe': 0.10
        }

        # Test typed vs positional - should use higher
        melee_smashing = calculator.get_defense_cascade_tohit(
            defense_values, 'smashing_melee'
        )
        assert melee_smashing == 0.30  # Melee (30%) > Smashing (20%)

        ranged_lethal = calculator.get_defense_cascade_tohit(
            defense_values, 'lethal_ranged'
        )
        assert ranged_lethal == 0.25  # Ranged (25%) > Lethal (15%)

    def test_streak_breaker_rules(self):
        """Test streak breaker activation thresholds."""
        # Arrange
        calculator = ToHitCalculator()

        # Test various hit chance thresholds
        assert calculator.calculate_streak_breaker(1, 0.90) is True   # 90%+ after 1 miss
        assert calculator.calculate_streak_breaker(0, 0.90) is False  # Not yet

        assert calculator.calculate_streak_breaker(2, 0.85) is True   # 80-89% after 2
        assert calculator.calculate_streak_breaker(1, 0.85) is False

        assert calculator.calculate_streak_breaker(3, 0.70) is True   # 60-79% after 3
        assert calculator.calculate_streak_breaker(2, 0.70) is False

        assert calculator.calculate_streak_breaker(4, 0.40) is True   # 30-59% after 4
        assert calculator.calculate_streak_breaker(6, 0.25) is True   # 20-29% after 6
        assert calculator.calculate_streak_breaker(8, 0.15) is True   # 10-19% after 8
        assert calculator.calculate_streak_breaker(100, 0.05) is True  # <10% after 100

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Arrange
        calculator = ToHitCalculator()

        # Test with extreme values
        extreme_chance = calculator.calculate_hit_chance({
            'base_tohit': 2.0,      # Way over 100%
            'tohit_buffs': 1.0,     # +100% buff
            'target_defense': -0.5,  # Negative defense (debuff)
            'accuracy': 3.0         # 300% accuracy
        })
        assert extreme_chance == 0.95  # Still capped at 95%

        # Test with all zeros
        zero_chance = calculator.calculate_hit_chance({
            'base_tohit': 0.0,
            'tohit_buffs': 0.0,
            'target_defense': 0.0,
            'accuracy': 0.0
        })
        assert zero_chance == 0.05  # Floor at 5%

    def test_pvp_calculations(self):
        """Test PvP-specific calculations."""
        # Arrange
        calculator = ToHitCalculator()

        # Act
        pvp_chance = calculator.calculate_power_hit_chance(
            power_accuracy=1.0,
            tohit_buffs=0.20,
            target_defense=0.30,
            accuracy_enhancements=0.50,
            global_accuracy_bonus=0.0,
            attacker_level=50,
            target_level=50,
            is_pvp=True
        )

        # Assert
        # Base PvP: 50%, +20% buff, -30% def = 40%
        # Accuracy: 1.0 * (1 + 0.5) = 1.5
        # Final: 40% * 1.5 = 60%
        assert pvp_chance == 0.60

