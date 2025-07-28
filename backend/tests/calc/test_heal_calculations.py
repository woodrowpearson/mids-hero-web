"""Test heal calculations following TDD approach."""

import pytest

from app.calc.healing import (
    HealOverTimeResult,
    calc_base_heal,
    calc_final_healing,
    calc_heal_over_time,
)
from app.core.enums import Archetype


class TestHealCalculations:
    """Test suite for healing calculations."""

    def test_base_heal_amount(self):
        """Should calculate base heal from heal scale."""
        # Test Defender base heal at level 50
        result = calc_base_heal(
            heal_scale=1.0,
            archetype=Archetype.DEFENDER,
            level=50
        )
        assert result == pytest.approx(357.95, 0.01)

        # Test Controller with same base
        result = calc_base_heal(
            heal_scale=1.0,
            archetype=Archetype.CONTROLLER,
            level=50
        )
        assert result == pytest.approx(357.95, 0.01)

        # Test partial heal scale
        result = calc_base_heal(
            heal_scale=0.3,  # 30% heal scale (Heal Other)
            archetype=Archetype.DEFENDER,
            level=50
        )
        assert result == pytest.approx(107.385, 0.01)

    def test_heal_with_enhancement(self):
        """Should apply heal enhancement with ED."""
        # Test below ED threshold
        enhanced = calc_final_healing(
            base_heal=300.0,
            heal_enhancement=0.95,  # 95% heal enhancement
            global_heal_buff=0.0,
            archetype=Archetype.DEFENDER
        )
        # ED Schedule A: 95% = 95% (no reduction at threshold)
        assert enhanced == pytest.approx(585.0, 0.01)  # 300 * 1.95

        # Test above ED threshold
        enhanced = calc_final_healing(
            base_heal=300.0,
            heal_enhancement=1.20,  # 120% heal enhancement
            global_heal_buff=0.0,
            archetype=Archetype.DEFENDER
        )
        # ED Schedule A: 120% reduces to ~105.6%
        assert enhanced == pytest.approx(616.8, 0.1)  # 300 * 2.056

    def test_heal_with_global_buffs(self):
        """Should apply global heal buffs."""
        enhanced = calc_final_healing(
            base_heal=300.0,
            heal_enhancement=0.50,  # 50% from enhancements
            global_heal_buff=0.15,  # 15% from set bonuses
            archetype=Archetype.CONTROLLER
        )
        # 300 * (1 + 0.50 + 0.15) = 300 * 1.65
        assert enhanced == pytest.approx(495.0, 0.01)

    def test_heal_over_time(self):
        """Should calculate total healing for HoT powers."""
        result = calc_heal_over_time(
            heal_scale=0.5,
            duration=10.0,
            interval=2.0,  # Heals every 2 seconds
            archetype=Archetype.CONTROLLER,
            level=50,
            heal_enhancement=0.0,
            global_heal_buff=0.0
        )

        assert isinstance(result, HealOverTimeResult)
        assert result.ticks == 5  # 10 seconds / 2 second interval
        assert result.heal_per_tick == pytest.approx(178.975, 0.01)
        assert result.total_healing == pytest.approx(894.875, 0.01)
        assert result.duration == 10.0
        assert result.interval == 2.0

    def test_heal_over_time_with_enhancements(self):
        """Should apply enhancements to HoT powers."""
        result = calc_heal_over_time(
            heal_scale=0.5,
            duration=10.0,
            interval=2.0,
            archetype=Archetype.CORRUPTOR,
            level=50,
            heal_enhancement=0.95,  # 95% heal enhancement
            global_heal_buff=0.10   # 10% from set bonuses
        )

        # Base heal per tick: 357.95 * 0.5 = 178.975
        # With ED and buffs: 178.975 * (1 + 0.95 + 0.10) = 366.896
        assert result.heal_per_tick == pytest.approx(366.896, 0.1)
        assert result.total_healing == pytest.approx(1834.48, 0.1)

    def test_archetype_differences(self):
        """Should handle different archetype heal scales."""
        # Tanker has lower heal modifier
        tanker_heal = calc_base_heal(
            heal_scale=1.0,
            archetype=Archetype.TANKER,
            level=50
        )

        # Defender has full heal modifier
        defender_heal = calc_base_heal(
            heal_scale=1.0,
            archetype=Archetype.DEFENDER,
            level=50
        )

        # Tanker should heal for less
        assert tanker_heal < defender_heal
        assert tanker_heal == pytest.approx(214.77, 0.01)  # 60% of defender

    def test_self_only_vs_ally_heal(self):
        """Should handle self-only heal modifiers."""
        # Self heals often have different scales
        # This is typically handled by the power's heal_scale value
        # but we can test the calculation is correct

        # Reconstruction (self-only) typically 25% scale
        self_heal = calc_base_heal(
            heal_scale=0.25,
            archetype=Archetype.SCRAPPER,
            level=50
        )

        # Scrappers have reduced heal scales
        assert self_heal == pytest.approx(53.69, 0.01)  # 25% of 214.77

    def test_edge_cases(self):
        """Should handle edge cases gracefully."""
        # Zero heal scale
        result = calc_final_healing(
            base_heal=0.0,
            heal_enhancement=0.95,
            global_heal_buff=0.10,
            archetype=Archetype.DEFENDER
        )
        assert result == 0.0

        # Negative values should be handled
        result = calc_final_healing(
            base_heal=100.0,
            heal_enhancement=-0.50,  # Debuff?
            global_heal_buff=0.0,
            archetype=Archetype.DEFENDER
        )
        assert result == 50.0  # 100 * (1 - 0.5)

        # Very high enhancement values
        result = calc_final_healing(
            base_heal=100.0,
            heal_enhancement=3.0,  # 300% enhancement
            global_heal_buff=0.0,
            archetype=Archetype.DEFENDER
        )
        # ED should cap this significantly
        # 300% reduces to 231.5% after ED
        assert result == pytest.approx(331.5, 0.1)  # 100 * (1 + 2.315)

    def test_level_scaling(self):
        """Should scale healing with level."""
        # Level 1 heal
        level_1_heal = calc_base_heal(
            heal_scale=1.0,
            archetype=Archetype.DEFENDER,
            level=1
        )

        # Level 50 heal
        level_50_heal = calc_base_heal(
            heal_scale=1.0,
            archetype=Archetype.DEFENDER,
            level=50
        )

        # Higher level should heal more
        assert level_50_heal > level_1_heal
        # Level 50 is approximately 10x level 1
        assert level_50_heal / level_1_heal == pytest.approx(10, rel=0.1)
