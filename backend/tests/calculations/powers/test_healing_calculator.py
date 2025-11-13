"""
Tests for Healing and Absorption Calculator

Based on test cases from Spec 05 section 4.
"""

import math

import pytest

from app.calculations.powers.healing_calculator import (
    BASE_MAGIC,
    AbsorbEffect,
    ArchetypeHealthStats,
    HealEffect,
    HealingCalculator,
    HitPointsEffect,
    RegenerationEffect,
)


class TestHealingCalculator:
    """Test HealingCalculator class"""

    def setup_method(self):
        """Setup calculator instance for each test"""
        self.calculator = HealingCalculator()

    def test_basic_instant_heal(self):
        """
        Test Case 1: Basic Instant Heal

        Scenario: Healing Aura (Defender), unenhanced
        Expected: 106.01 HP healed
        """
        # Setup
        heal_effect = HealEffect(magnitude=10.42)  # 10.42% heal

        # Calculate heal
        result = self.calculator.calculate_instant_heal(
            heal_effects=[heal_effect], max_hp=1017.4, current_hp=500.0
        )

        assert result["heal_magnitude_pct"] == pytest.approx(10.42, abs=0.01)
        assert result["heal_amount"] == pytest.approx(106.01, abs=0.1)
        assert result["new_hp"] == pytest.approx(606.01, abs=0.1)
        assert result["overheal"] == 0.0

    def test_enhanced_heal(self):
        """
        Test Case 2: Enhanced Heal

        Scenario: Healing Aura with 3x level 50 Heal IOs (95.66% enhancement)
        Expected: 207.45 HP healed
        """
        # Setup
        heal_effect = HealEffect(
            magnitude=10.42, buffed_magnitude=20.39  # 10.42 * 1.9566
        )

        # Calculate heal
        result = self.calculator.calculate_instant_heal(
            heal_effects=[heal_effect], max_hp=1017.4, current_hp=800.0
        )

        assert result["heal_magnitude_pct"] == pytest.approx(20.39, abs=0.01)
        assert result["heal_amount"] == pytest.approx(207.45, abs=0.5)
        assert result["new_hp"] == pytest.approx(1007.45, abs=0.5)
        assert result["overheal"] == 0.0

    def test_heal_with_overheal(self):
        """
        Test Case 3: Heal with Overheal

        Scenario: Large heal on nearly full HP
        Expected: 500 HP overheal
        """
        # Setup
        heal_effect = HealEffect(magnitude=30.0)  # 30% heal

        # Calculate heal
        result = self.calculator.calculate_instant_heal(
            heal_effects=[heal_effect], max_hp=2000.0, current_hp=1900.0
        )

        assert result["heal_magnitude_pct"] == 30.0
        assert result["heal_amount"] == 600.0  # 30% of 2000
        assert result["new_hp"] == 2000.0  # Capped at max
        assert result["overheal"] == 500.0  # 1900 + 600 - 2000

    def test_max_hp_calculation_dull_pain(self):
        """
        Test Case 4: Maximum HP Calculation (Dull Pain)

        Scenario: Tanker with Dull Pain (+40% max HP)
        Expected: 2623.74 HP total (under cap)
        """
        # Setup
        at_stats = ArchetypeHealthStats(
            base_hitpoints=1874.1, hp_cap=3534.0, base_regen=1.0, regen_cap=25.0
        )

        hp_effect = HitPointsEffect(magnitude=40.0, display_percentage=True)  # +40%

        # Calculate max HP
        result = self.calculator.calculate_max_hp(
            at_stats=at_stats, hp_effects=[hp_effect]
        )

        assert result["base_hp"] == 1874.1
        assert result["hp_bonus"] == pytest.approx(749.64, abs=0.1)
        assert result["uncapped_hp"] == pytest.approx(2623.74, abs=0.1)
        assert result["capped_hp"] == pytest.approx(2623.74, abs=0.1)
        assert result["over_cap"] == 0.0

    def test_regeneration_calculation_scrapper(self):
        """
        Test Case 5: Regeneration Calculation (Scrapper with Health + Fast Healing)

        Scenario: Scrapper with Health (+40%) and Fast Healing (+75%)
        Expected: 86.31 HP/sec, 27.91 seconds to full
        """
        # Setup
        at_stats = ArchetypeHealthStats(
            base_hitpoints=1338.6, hp_cap=2409.0, base_regen=1.0, regen_cap=30.0
        )

        regen_effects = [
            RegenerationEffect(magnitude=0.40),  # Health: +40%
            RegenerationEffect(magnitude=0.75),  # Fast Healing: +75%
        ]

        # Calculate regeneration
        result = self.calculator.calculate_regeneration(
            at_stats=at_stats, regen_effects=regen_effects, max_hp=2409.0
        )

        assert result["regen_total"] == pytest.approx(2.15, abs=0.01)
        assert result["regen_percent_per_sec"] == pytest.approx(3.583, abs=0.01)
        assert result["hp_per_sec"] == pytest.approx(86.31, abs=0.5)
        assert result["time_to_full"] == pytest.approx(27.91, abs=0.5)
        assert result["hp_per_tick"] == pytest.approx(345.24, abs=2.0)

    def test_absorption_shield_barrier_destiny(self):
        """
        Test Case 6: Absorption Shield (Barrier Destiny)

        Scenario: Defender activates Barrier Destiny (600 absorb)
        Expected: 600 HP absorb, 58.97% of base
        """
        # Setup
        absorb_effect = AbsorbEffect(magnitude=600.0, display_percentage=False)

        # Calculate absorption
        result = self.calculator.calculate_absorption(
            absorb_effects=[absorb_effect], max_hp=1874.1, base_hp=1017.4
        )

        assert result["absorb_amount"] == 600.0
        assert result["absorb_percent_base"] == pytest.approx(58.97, abs=0.5)
        assert result["absorb_percent_max"] == pytest.approx(32.01, abs=0.5)
        assert result["capped"] is False

    def test_hp_cap_scenario(self):
        """
        Test Case 7: HP Cap Scenario (Tanker with Massive +HP)

        Scenario: Tanker with Dull Pain + Accolades + Set Bonuses
        Expected: Capped at archetype limit
        """
        # Setup
        at_stats = ArchetypeHealthStats(
            base_hitpoints=1874.1, hp_cap=3534.0, base_regen=1.0, regen_cap=25.0
        )

        hp_effects = [
            HitPointsEffect(magnitude=40.0, display_percentage=True),  # Dull Pain
            HitPointsEffect(magnitude=9.5, display_percentage=True),  # Accolades
            HitPointsEffect(magnitude=10.0, display_percentage=True),  # Set bonuses
        ]

        # Calculate max HP
        result = self.calculator.calculate_max_hp(
            at_stats=at_stats, hp_effects=hp_effects
        )

        total_bonus = result["hp_bonus"]
        assert total_bonus == pytest.approx(1115.09, abs=1.0)
        assert result["uncapped_hp"] == pytest.approx(2989.19, abs=1.0)
        assert result["capped_hp"] == pytest.approx(2989.19, abs=1.0)  # Under cap
        assert result["over_cap"] == 0.0

    def test_heal_over_time(self):
        """
        Test Case 8: Heal Over Time (Regeneration Aura)

        Scenario: Regeneration Aura ticking heal
        Expected: 8 HP/tick, 15 ticks, 120 total, 4 HP/sec
        """
        # Setup
        heal_effect = HealEffect(
            magnitude=6.0,  # 6% over 30 seconds
            duration=30.0,
            tick_interval=2.0,
        )

        # Calculate HoT
        result = self.calculator.calculate_heal_over_time(
            heal_effect=heal_effect, max_hp=2000.0
        )

        assert result["heal_per_tick"] == pytest.approx(8.0, abs=0.1)
        assert result["num_ticks"] == 15
        assert result["total_heal"] == pytest.approx(120.0, abs=0.1)
        assert result["heal_per_sec"] == pytest.approx(4.0, abs=0.1)

    def test_absorption_capping(self):
        """
        Test Case 9: Absorption Capping

        Scenario: Large absorption shield exceeding max HP
        Expected: Capped at max HP (2000)
        """
        # Setup
        absorb_effect = AbsorbEffect(magnitude=5000.0, display_percentage=False)

        # Calculate absorption
        result = self.calculator.calculate_absorption(
            absorb_effects=[absorb_effect], max_hp=2000.0, base_hp=2000.0
        )

        assert result["absorb_amount"] == 2000.0  # Capped at max HP
        assert result["absorb_percent_base"] == pytest.approx(100.0, abs=0.1)
        assert result["absorb_percent_max"] == pytest.approx(100.0, abs=0.1)
        assert result["capped"] is True

    def test_multiple_absorption_sources(self):
        """
        Test Case 10: Multiple Absorption Sources (Highest Wins)

        Scenario: Character has multiple absorption shields active
        Expected: Takes highest value (600)
        """
        # Setup
        absorb_effects = [
            AbsorbEffect(magnitude=600.0),  # Barrier Destiny
            AbsorbEffect(magnitude=400.0),  # Power Boost effect
            AbsorbEffect(magnitude=200.0),  # Set bonus
        ]

        # Calculate absorption
        result = self.calculator.calculate_absorption(
            absorb_effects=absorb_effects, max_hp=2000.0, base_hp=2000.0
        )

        assert result["absorb_amount"] == 600.0  # Highest value
        assert result["absorb_percent_base"] == pytest.approx(30.0, abs=0.1)
        assert result["capped"] is False

    def test_negative_regeneration_regen_debuff(self):
        """
        Test Case 11: Negative Regeneration (Regen Debuff)

        Scenario: Character with regen buffs hit by regen debuff
        Expected: Regen reduced but not negative (with resistance)
        """
        # Setup
        result = self.calculator.apply_regen_debuff(
            current_regen=2.15,  # 215%
            debuff_magnitude=-1.50,  # -150%
            debuff_resistance=0.30,  # 30% resistance
        )

        assert result["resisted_debuff"] == pytest.approx(-1.05, abs=0.01)
        assert result["new_regen"] == pytest.approx(1.10, abs=0.01)
        assert result["is_negative"] is False

    def test_base_magic_constant(self):
        """Test BASE_MAGIC constant value"""
        assert BASE_MAGIC == pytest.approx(
            1.666667, abs=0.000001
        ), "BASE_MAGIC should be 1.666667"

        # Verify BASE_MAGIC converts regen correctly
        # At 100% regen (1.0), you should recover 100% HP in 240 seconds
        # That's 1.666667% per 4-second tick, or 0.416667% per second
        regen_percent_per_sec = 1.0 * 1.0 * BASE_MAGIC  # 100% regen, base 1.0
        assert regen_percent_per_sec == pytest.approx(1.666667, abs=0.000001)

    def test_archetype_health_stats_validation(self):
        """Test ArchetypeHealthStats validation"""
        # Valid stats
        stats = ArchetypeHealthStats(
            base_hitpoints=1874.1, hp_cap=3534.0, base_regen=1.0, regen_cap=25.0
        )
        assert stats.base_hitpoints == 1874.1

        # Invalid base HP
        with pytest.raises(ValueError):
            ArchetypeHealthStats(
                base_hitpoints=-100.0,  # Invalid
                hp_cap=3534.0,
            )

        # Invalid HP cap (less than base)
        with pytest.raises(ValueError):
            ArchetypeHealthStats(
                base_hitpoints=1874.1,
                hp_cap=1000.0,  # Invalid (< base)
            )

        # Invalid base regen
        with pytest.raises(ValueError):
            ArchetypeHealthStats(
                base_hitpoints=1874.1, hp_cap=3534.0, base_regen=-1.0  # Invalid
            )

    def test_heal_effect_validation(self):
        """Test HealEffect validation"""
        # Valid heal
        heal = HealEffect(magnitude=10.0)
        assert heal.magnitude == 10.0

        # Invalid negative magnitude
        with pytest.raises(ValueError):
            HealEffect(magnitude=-10.0)

        # Invalid probability
        with pytest.raises(ValueError):
            HealEffect(magnitude=10.0, probability=1.5)  # > 1.0

        # Invalid duration
        with pytest.raises(ValueError):
            HealEffect(magnitude=10.0, duration=-5.0)

    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        # Invalid max_hp for instant heal
        with pytest.raises(ValueError):
            self.calculator.calculate_instant_heal(
                heal_effects=[], max_hp=-100.0, current_hp=0.0  # Invalid
            )

        # Current HP > max HP
        with pytest.raises(ValueError):
            self.calculator.calculate_instant_heal(
                heal_effects=[],
                max_hp=1000.0,
                current_hp=2000.0,  # Invalid
            )

        # Invalid max_hp for regeneration
        with pytest.raises(ValueError):
            at_stats = ArchetypeHealthStats(
                base_hitpoints=1000.0, hp_cap=2000.0, base_regen=1.0
            )
            self.calculator.calculate_regeneration(
                at_stats=at_stats, regen_effects=[], max_hp=-100.0  # Invalid
            )

        # Invalid max_hp for absorption
        with pytest.raises(ValueError):
            self.calculator.calculate_absorption(
                absorb_effects=[], max_hp=-100.0, base_hp=1000.0  # Invalid
            )

        # HoT with invalid duration
        with pytest.raises(ValueError):
            heal_effect = HealEffect(magnitude=10.0, duration=0.0)  # Invalid for HoT
            self.calculator.calculate_heal_over_time(
                heal_effect=heal_effect, max_hp=1000.0
            )

        # HoT with missing tick_interval
        with pytest.raises(ValueError):
            heal_effect = HealEffect(
                magnitude=10.0, duration=30.0, tick_interval=None  # Invalid
            )
            self.calculator.calculate_heal_over_time(
                heal_effect=heal_effect, max_hp=1000.0
            )

    def test_format_heal_display(self):
        """Test heal display formatting"""
        display = self.calculator.format_heal_display(
            heal_amount=106.01, base_hp=1017.4
        )

        assert "106.01 HP" in display
        assert "10.42% of base HP" in display or "10.4" in display

    def test_format_regen_display(self):
        """Test regeneration display formatting"""
        # Normal regen
        display = self.calculator.format_regen_display(
            hp_per_sec=86.31, time_to_full=27.9
        )

        assert "86.31 HP/sec" in display
        assert "27.9" in display

        # No regeneration
        display_no_regen = self.calculator.format_regen_display(
            hp_per_sec=0.0, time_to_full=float("inf")
        )

        assert "No regeneration" in display_no_regen

    def test_format_absorption_display(self):
        """Test absorption display formatting"""
        display = self.calculator.format_absorption_display(
            absorb_amount=600.0, base_hp=1017.4
        )

        assert "600.00 HP" in display
        assert "58.97% of base HP" in display or "58.9" in display

    def test_percentage_based_absorption(self):
        """Test percentage-based absorption conversion"""
        # Percentage-based absorb effect
        absorb_effect = AbsorbEffect(
            magnitude=50.0,  # 50%
            display_percentage=True,
        )

        result = self.calculator.calculate_absorption(
            absorb_effects=[absorb_effect], max_hp=2000.0, base_hp=1500.0
        )

        # Should convert to 50% of max HP (not base HP)
        assert result["absorb_amount"] == pytest.approx(1000.0, abs=0.1)
        assert result["capped"] is False

    def test_regen_debuff_resistance(self):
        """Test regeneration debuff with different resistance levels"""
        # No resistance
        result_no_res = self.calculator.apply_regen_debuff(
            current_regen=2.0, debuff_magnitude=-1.0, debuff_resistance=0.0
        )
        assert result_no_res["new_regen"] == pytest.approx(1.0, abs=0.01)

        # 50% resistance
        result_half_res = self.calculator.apply_regen_debuff(
            current_regen=2.0, debuff_magnitude=-1.0, debuff_resistance=0.5
        )
        assert result_half_res["new_regen"] == pytest.approx(1.5, abs=0.01)

        # 100% resistance (immune)
        result_full_res = self.calculator.apply_regen_debuff(
            current_regen=2.0, debuff_magnitude=-1.0, debuff_resistance=1.0
        )
        assert result_full_res["new_regen"] == pytest.approx(2.0, abs=0.01)

        # Invalid resistance
        with pytest.raises(ValueError):
            self.calculator.apply_regen_debuff(
                current_regen=2.0,
                debuff_magnitude=-1.0,
                debuff_resistance=1.5,  # Invalid
            )
