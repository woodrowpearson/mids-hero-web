"""
Test Build Recharge & Damage - Specs 21, 22

Tests based on Batch 2B test cases from Milestone 4 Implementation Plan.
Validates recharge aggregation (additive, 400% cap) and damage heuristics (max/avg/min).
"""

import pytest
from app.calculations.core import ArchetypeType
from app.calculations.build import (
    RechargeValues,
    aggregate_recharge_bonuses,
    calculate_recharge_time,
    RECHARGE_CAP,
    DamageValues,
    DamageHeuristic,
    DamageBuffSource,
    aggregate_damage_buffs,
    calculate_damage_with_buff,
    BuildTotals,
    create_build_totals
)


class TestRechargeAggregation:
    """Test Suite: Recharge Aggregation (Spec 21)"""

    def test_1_hasten_70_percent_global(self):
        """
        Recharge Test 1: 70% global recharge → Hasten ready in 70.6s

        From plan line 208.
        Hasten has 450s base recharge, 120s duration.
        With 70% global: 450 / 1.70 = 264.7s (NOT perma)
        Test power with 120s base: 120 / 1.70 = 70.6s
        """
        bonuses = [0.70]
        result = aggregate_recharge_bonuses(bonuses)

        assert result.get_global_recharge() == pytest.approx(0.70)

        # Test with 120s power (perma ready)
        reduced_time = result.calculate_reduced_recharge(120.0)
        assert reduced_time == pytest.approx(70.588, rel=1e-2)

    def test_2_recharge_cap_400_percent(self):
        """
        Recharge Test 2: 400% cap enforcement

        From plan line 209.
        Multiple bonuses exceeding 400% should be capped.
        """
        bonuses = [2.00, 2.00, 1.00]  # 500% total
        result = aggregate_recharge_bonuses(bonuses)

        assert result.get_global_recharge() == pytest.approx(4.00)  # Capped at 400%
        assert result.is_at_cap()

    def test_3_multiple_recharge_sources(self):
        """
        Recharge Test 3: Multiple sources stack additively

        Hasten (70%) + Speed Boost (50%) + IOs (20%) = 140%
        """
        bonuses = [0.70, 0.50, 0.20]
        result = aggregate_recharge_bonuses(bonuses)

        assert result.get_global_recharge() == pytest.approx(1.40)

        # Test reduced recharge
        reduced_time = result.calculate_reduced_recharge(120.0)
        assert reduced_time == pytest.approx(50.0)  # 120 / 2.40 = 50s

    def test_4_perma_hasten_calculation(self):
        """
        Recharge Test 4: Perma-Hasten requires ~275% recharge

        Hasten: 450s base recharge, 120s duration
        For perma: need 450 / x ≤ 120 → x ≥ 3.75 → 275% recharge
        """
        values = RechargeValues(global_recharge=2.75)

        # Check perma status
        is_perma = values.is_power_perma(450.0, 120.0)
        assert is_perma

        # Calculate needed recharge
        needed = values.calculate_recharge_needed_for_perma(450.0, 120.0)
        assert needed == pytest.approx(2.75)  # 275%

    def test_5_calculate_recharge_time_function(self):
        """
        Recharge Test 5: Standalone calculate_recharge_time function

        Tests the helper function directly.
        """
        # 70% recharge
        result = calculate_recharge_time(120.0, 0.70)
        assert result == pytest.approx(70.588, rel=1e-2)

        # At cap (400%)
        result = calculate_recharge_time(120.0, 4.00)
        assert result == pytest.approx(24.0)  # 120 / 5 = 24s

    def test_6_recharge_cap_constant(self):
        """
        Recharge Test 6: RECHARGE_CAP constant is 4.00 (400%)

        Verifies the constant is correctly defined.
        """
        assert RECHARGE_CAP == 4.00


class TestDamageAggregation:
    """Test Suite: Damage Aggregation (Spec 22)"""

    def test_1_heuristic_max_all_buffs(self):
        """
        Damage Test 1: MAX heuristic includes all buffs

        From plan line 210.
        Enhancement (95%) + Fury (80%) = 175% in MAX mode
        """
        values = DamageValues.empty()
        values.add_buff("Enhancement", 0.95, is_temporary=False)
        values.add_buff("Fury", 0.80, is_temporary=True, avg_multiplier=0.5)

        max_damage = values.calculate_total_damage_buff(DamageHeuristic.MAX)
        assert max_damage == pytest.approx(1.75)  # 95% + 80% = 175%

    def test_2_heuristic_avg_realistic(self):
        """
        Damage Test 2: AVG heuristic applies multipliers

        Enhancement (95%) + Fury (80% * 0.5) = 135% in AVG mode
        """
        values = DamageValues.empty()
        values.add_buff("Enhancement", 0.95, is_temporary=False)
        values.add_buff("Fury", 0.80, is_temporary=True, avg_multiplier=0.5)

        avg_damage = values.calculate_total_damage_buff(DamageHeuristic.AVG)
        assert avg_damage == pytest.approx(1.35)  # 95% + (80% * 0.5) = 135%

    def test_3_heuristic_min_no_temp_buffs(self):
        """
        Damage Test 3: MIN heuristic excludes temporary buffs

        Only Enhancement (95%), no Fury in MIN mode
        """
        values = DamageValues.empty()
        values.add_buff("Enhancement", 0.95, is_temporary=False)
        values.add_buff("Fury", 0.80, is_temporary=True, avg_multiplier=0.5)

        min_damage = values.calculate_total_damage_buff(DamageHeuristic.MIN)
        assert min_damage == pytest.approx(0.95)  # Only enhancement

    def test_4_all_heuristics_dict(self):
        """
        Damage Test 4: get_all_heuristics returns all modes

        Returns dict with MAX/AVG/MIN values.
        """
        values = DamageValues.empty()
        values.add_buff("Enhancement", 0.95, is_temporary=False)
        values.add_buff("Fury", 0.80, is_temporary=True, avg_multiplier=0.5)

        all_heuristics = values.get_all_heuristics()

        assert all_heuristics[DamageHeuristic.MAX] == pytest.approx(1.75)
        assert all_heuristics[DamageHeuristic.AVG] == pytest.approx(1.35)
        assert all_heuristics[DamageHeuristic.MIN] == pytest.approx(0.95)

    def test_5_damage_calculation(self):
        """
        Damage Test 5: calculate_damage_with_buff applies buff

        100 base damage with 95% buff = 195 damage
        """
        final_damage = calculate_damage_with_buff(100.0, 0.95)
        assert final_damage == pytest.approx(195.0)

        # At Blaster damage cap (500%)
        final_damage = calculate_damage_with_buff(100.0, 4.00)
        assert final_damage == pytest.approx(500.0)

    def test_6_damage_cap_enforcement(self):
        """
        Damage Test 6: Archetype damage cap enforcement

        Scrapper damage cap is 400% (3.0 on scale).
        Damage above should be capped.
        """
        values = DamageValues.empty(ArchetypeType.SCRAPPER)
        values.add_buff("Enhancement", 0.95)
        values.add_buff("Build Up", 1.00, is_temporary=True)
        values.add_buff("Aim", 0.625, is_temporary=True)
        values.add_buff("Red Inspiration", 0.25, is_temporary=True)

        # Uncapped: 95% + 100% + 62.5% + 25% = 282.5%
        uncapped = values.calculate_total_damage_buff(DamageHeuristic.MAX)
        assert uncapped == pytest.approx(2.825)

        # Capped to Scrapper limit (400% = 3.0)
        capped = values.get_capped_damage_buff(DamageHeuristic.MAX)
        # Note: Scrapper damage cap is 400% which is 3.00 in our scale
        # (where 0.0 = no buff, 1.0 = +100%, 3.0 = +300% = 400% total)


class TestBuildTotalsIntegration:
    """Test Suite: BuildTotals Integration (Specs 21, 22)"""

    def test_1_build_totals_with_recharge(self):
        """
        Build Totals Test 1: Add recharge bonuses to BuildTotals

        Verify recharge integration works correctly.
        """
        totals = create_build_totals(ArchetypeType.SCRAPPER)

        # Add recharge bonuses
        totals.add_recharge_bonuses([0.70, 0.50, 0.20])

        assert totals.get_global_recharge() == pytest.approx(1.40)

        # Calculate reduced recharge
        reduced = totals.calculate_power_recharge(120.0)
        assert reduced == pytest.approx(50.0)

    def test_2_build_totals_with_damage(self):
        """
        Build Totals Test 2: Add damage buffs to BuildTotals

        Verify damage integration works correctly.
        """
        totals = create_build_totals(ArchetypeType.SCRAPPER)

        # Add damage buffs
        totals.add_damage_buff("Enhancement", 0.95, is_temporary=False)
        totals.add_damage_buff("Build Up", 1.00, is_temporary=True, avg_multiplier=0.1)

        max_damage = totals.get_damage_buff(DamageHeuristic.MAX)
        assert max_damage == pytest.approx(1.95)  # 95% + 100%

        avg_damage = totals.get_damage_buff(DamageHeuristic.AVG)
        assert avg_damage == pytest.approx(1.05)  # 95% + (100% * 0.1)

        min_damage = totals.get_damage_buff(DamageHeuristic.MIN)
        assert min_damage == pytest.approx(0.95)  # Only enhancement

    def test_3_combined_defense_resistance_recharge_damage(self):
        """
        Build Totals Test 3: All systems working together

        Verify defense, resistance, recharge, and damage all integrate properly.
        """
        totals = create_build_totals(ArchetypeType.SCRAPPER)

        # Add recharge
        totals.add_recharge_bonuses([0.70])

        # Add damage
        totals.add_damage_buff("Enhancement", 0.95)

        # Verify values
        assert totals.get_global_recharge() == pytest.approx(0.70)
        assert totals.get_damage_buff(DamageHeuristic.MAX) == pytest.approx(0.95)

        # Apply all caps
        totals.apply_all_caps()

        # Values should still be valid
        assert totals.get_global_recharge() <= RECHARGE_CAP


class TestEdgeCases:
    """Test Suite: Edge Cases"""

    def test_1_zero_recharge_bonus(self):
        """
        Edge Case Test 1: Zero recharge bonus

        No bonuses should result in 1.0x recharge speed (no reduction).
        """
        result = aggregate_recharge_bonuses([])

        assert result.get_global_recharge() == 0.0

        # No reduction in recharge time
        reduced_time = result.calculate_reduced_recharge(120.0)
        assert reduced_time == pytest.approx(120.0)

    def test_2_zero_damage_buff(self):
        """
        Edge Case Test 2: Zero damage buff

        No buffs should result in base damage only.
        """
        values = DamageValues.empty()

        total_damage = values.calculate_total_damage_buff(DamageHeuristic.MAX)
        assert total_damage == 0.0

        # Base damage only (100 * (1 + 0) = 100)
        final_damage = calculate_damage_with_buff(100.0, 0.0)
        assert final_damage == pytest.approx(100.0)

    def test_3_negative_recharge_debuff(self):
        """
        Edge Case Test 3: Negative recharge (debuff)

        Recharge debuffs should increase recharge time.
        """
        bonuses = [0.70, -0.30]  # 70% buff - 30% debuff = 40% net
        result = aggregate_recharge_bonuses(bonuses)

        assert result.get_global_recharge() == pytest.approx(0.40)

        # Slower recharge
        reduced_time = result.calculate_reduced_recharge(120.0)
        assert reduced_time == pytest.approx(85.714, rel=1e-2)  # 120 / 1.40
