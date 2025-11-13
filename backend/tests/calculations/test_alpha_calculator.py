"""
Tests for Incarnate Alpha Slot Calculator

Tests Alpha slot level shifts, passive boosts, and purple patch calculations.
Based on test cases from Spec 29 section 4.
"""

from decimal import Decimal

import pytest
from backend.app.calculations.incarnates.alpha_calculator import (
    AlphaSlotCalculator,
    AlphaSlotFactory,
    AlphaTier,
    AlphaType,
    BuildStats,
)


class TestLevelShifts:
    """Test level shift calculations."""

    def test_t1_no_level_shift(self):
        """Test T1 Musculature Boost provides no level shift (Test Case 1 from Spec 29)."""
        alpha = AlphaSlotFactory.create_musculature(AlphaTier.T1_BOOST)

        level_shift = alpha.get_level_shift()
        effective_level = alpha.get_effective_level(50)

        assert level_shift == 0
        assert effective_level == 50

    def test_t3_provides_one_shift(self):
        """Test T3 Alpha provides +1 level shift (Test Case 2 from Spec 29)."""
        alpha = AlphaSlotFactory.create_musculature(AlphaTier.T3_PARTIAL_CORE_REVAMP)

        level_shift = alpha.get_level_shift()
        effective_level = alpha.get_effective_level(50)

        assert level_shift == 1
        assert effective_level == 51

    def test_t4_provides_one_shift(self):
        """Test T4 Alpha provides +1 level shift (Test Case 3 from Spec 29)."""
        alpha = AlphaSlotFactory.create_musculature(AlphaTier.T4_CORE_PARAGON)

        level_shift = alpha.get_level_shift()
        effective_level = alpha.get_effective_level(50)

        assert level_shift == 1
        assert effective_level == 51

    def test_t4_with_lore_provides_two_shifts(self):
        """Test T4 Alpha + T4 Lore provides +2 level shift (Test Case 4 from Spec 29)."""
        alpha = AlphaSlotFactory.create_spiritual(AlphaTier.T4_CORE_PARAGON)

        level_shift = alpha.get_level_shift(has_lore_t4=True)
        effective_level = alpha.get_effective_level(50, has_lore_t4=True)

        assert level_shift == 2
        assert effective_level == 52

    def test_t4_with_lore_and_destiny_provides_three_shifts(self):
        """Test T4 Alpha + T4 Lore + T4 Destiny provides +3 level shift (Test Case 5 from Spec 29)."""
        alpha = AlphaSlotFactory.create_cardiac(AlphaTier.T4_RADIAL_PARAGON)

        level_shift = alpha.get_level_shift(has_lore_t4=True, has_destiny_t4=True)
        effective_level = alpha.get_effective_level(
            50, has_lore_t4=True, has_destiny_t4=True
        )

        assert level_shift == 3
        assert effective_level == 53

    def test_maximum_shift_is_three(self):
        """Test maximum level shift is capped at +3."""
        alpha = AlphaSlotFactory.create_musculature(AlphaTier.T4_CORE_PARAGON)

        # Even if we somehow had more shifts, cap at 3
        level_shift = alpha.get_level_shift(has_lore_t4=True, has_destiny_t4=True)

        assert level_shift <= 3


class TestAlphaBoosts:
    """Test Alpha passive boost calculations."""

    def test_musculature_t1_boost(self):
        """Test Musculature T1 provides 20% damage boost."""
        alpha = AlphaSlotFactory.create_musculature(AlphaTier.T1_BOOST)

        # Check effects
        damage_effect = [
            e for e in alpha.effects if str(e.effect_type).endswith("DAMAGE_BUFF")
        ][0]

        assert damage_effect.magnitude == Decimal("0.20")  # 20% before ED

    def test_musculature_t4_core_paragon(self):
        """Test Musculature T4 Core Paragon provides 33% damage boost."""
        alpha = AlphaSlotFactory.create_musculature(AlphaTier.T4_CORE_PARAGON)

        # Check effects
        damage_effect = [
            e for e in alpha.effects if str(e.effect_type).endswith("DAMAGE_BUFF")
        ][0]

        assert damage_effect.magnitude == Decimal("0.33")  # 33% before ED
        assert damage_effect.ignore_ed is False  # Subject to ED!

    def test_musculature_t4_radial_has_endurance_discount(self):
        """Test Musculature T4 Radial Paragon has endurance discount."""
        alpha = AlphaSlotFactory.create_musculature(AlphaTier.T4_RADIAL_PARAGON)

        # Check for endurance discount effect
        end_effects = [
            e
            for e in alpha.effects
            if str(e.effect_type).endswith("ENDURANCE_DISCOUNT")
        ]

        assert len(end_effects) == 1
        assert end_effects[0].magnitude == Decimal("0.33")  # 33%

    def test_spiritual_t4_core_has_recharge(self):
        """Test Spiritual T4 Core Paragon has recharge boost."""
        alpha = AlphaSlotFactory.create_spiritual(AlphaTier.T4_CORE_PARAGON)

        # Check for recharge effect
        recharge_effects = [
            e for e in alpha.effects if str(e.effect_type).endswith("RECHARGE_TIME")
        ]

        assert len(recharge_effects) == 1
        assert recharge_effects[0].magnitude == Decimal("0.33")  # 33%

    def test_t3_and_t4_have_level_shift_effect(self):
        """Test T3 and T4 Alphas include level shift effect."""
        alpha_t3 = AlphaSlotFactory.create_musculature(AlphaTier.T3_PARTIAL_CORE_REVAMP)
        alpha_t4 = AlphaSlotFactory.create_musculature(AlphaTier.T4_CORE_PARAGON)

        # Check for level shift effect
        t3_shift_effects = [
            e for e in alpha_t3.effects if str(e.effect_type).endswith("LEVEL_SHIFT")
        ]
        t4_shift_effects = [
            e for e in alpha_t4.effects if str(e.effect_type).endswith("LEVEL_SHIFT")
        ]

        assert len(t3_shift_effects) == 1
        assert t3_shift_effects[0].magnitude == Decimal("1")
        assert t3_shift_effects[0].ignore_ed is True  # Level shift not subject to ED

        assert len(t4_shift_effects) == 1
        assert t4_shift_effects[0].magnitude == Decimal("1")


class TestApplyAlphaToBuild:
    """Test applying Alpha slot to build statistics."""

    def test_alpha_updates_effective_level(self):
        """Test Alpha updates effective level in build stats."""
        alpha = AlphaSlotFactory.create_musculature(AlphaTier.T4_CORE_PARAGON)
        stats = BuildStats(effective_level=50)

        updated = AlphaSlotCalculator.apply_alpha_to_build(
            alpha_slot=alpha,
            build_stats=stats,
            character_level=50,
            archetype_name="Scrapper",
        )

        assert updated.effective_level == 51  # +1 level shift

    def test_alpha_adds_passive_boosts_to_totals(self):
        """Test Alpha adds passive boosts to build totals."""
        alpha = AlphaSlotFactory.create_musculature(AlphaTier.T1_BOOST)
        stats = BuildStats(effective_level=50)

        # Mock ED curve that returns input unchanged (for testing)
        def mock_ed_curve(value: float) -> float:
            return value

        updated = AlphaSlotCalculator.apply_alpha_to_build(
            alpha_slot=alpha,
            build_stats=stats,
            character_level=50,
            archetype_name="Scrapper",
            ed_curve_func=mock_ed_curve,
        )

        # Check damage buff was added
        assert "DAMAGE_BUFF" in updated.totals
        assert updated.totals["DAMAGE_BUFF"] == Decimal("0.20")  # 20%

    def test_invalid_character_level_raises_error(self):
        """Test invalid character level raises ValueError."""
        alpha = AlphaSlotFactory.create_musculature(AlphaTier.T4_CORE_PARAGON)
        stats = BuildStats(effective_level=50)

        with pytest.raises(ValueError, match="Invalid character level"):
            AlphaSlotCalculator.apply_alpha_to_build(
                alpha_slot=alpha,
                build_stats=stats,
                character_level=51,  # Invalid (max 50)
                archetype_name="Scrapper",
            )


class TestPurplePatch:
    """Test purple patch level difference calculations."""

    def test_even_level_no_modifier(self):
        """Test even level combat has no modifier (Test Case 7 from Spec 29)."""
        damage_mod = AlphaSlotCalculator.get_purple_patch_damage_modifier(50, 50)
        tohit_mod = AlphaSlotCalculator.get_purple_patch_tohit_modifier(50, 50)

        assert damage_mod == Decimal("1.0")  # 100% damage
        assert tohit_mod == Decimal("0.0")  # 0% ToHit modifier

    def test_two_levels_above_bonus(self):
        """Test 2 levels above target provides bonus."""
        damage_mod = AlphaSlotCalculator.get_purple_patch_damage_modifier(52, 50)
        tohit_mod = AlphaSlotCalculator.get_purple_patch_tohit_modifier(52, 50)

        assert damage_mod == Decimal("1.10")  # 110% damage (+10%)
        assert tohit_mod == Decimal("0.10")  # +10% ToHit

    def test_two_levels_below_penalty(self):
        """Test 2 levels below target provides penalty."""
        damage_mod = AlphaSlotCalculator.get_purple_patch_damage_modifier(50, 52)
        tohit_mod = AlphaSlotCalculator.get_purple_patch_tohit_modifier(50, 52)

        assert damage_mod == Decimal("0.80")  # 80% damage (-20%)
        assert tohit_mod == Decimal("-0.15")  # -15% ToHit

    def test_level_shift_impact_on_damage(self):
        """Test level shift improves damage vs higher level enemies."""
        # Without shift: Level 50 vs 54
        no_shift_mod = AlphaSlotCalculator.get_purple_patch_damage_modifier(50, 54)

        # With +2 shift: Level 52 vs 54
        with_shift_mod = AlphaSlotCalculator.get_purple_patch_damage_modifier(52, 54)

        assert no_shift_mod == Decimal("0.60")  # 60% damage (-40%)
        assert with_shift_mod == Decimal("0.80")  # 80% damage (-20%)

        # Level shift provides +20% effective damage (0.80/0.60 = 1.333 = 33% more)
        improvement = float(with_shift_mod) / float(no_shift_mod)
        assert improvement == pytest.approx(1.333, rel=0.01)


class TestAlphaTypes:
    """Test different Alpha types and their configurations."""

    def test_all_alpha_types_have_unique_focus(self):
        """Test all 8 Alpha types have unique focus areas."""
        assert len(AlphaType) == 8

        # Verify each has unique value
        values = [t.value for t in AlphaType]
        assert len(values) == len(set(values))  # No duplicates

    def test_all_tiers_available(self):
        """Test all 9 tiers are defined."""
        assert len(AlphaTier) == 9

        # Verify tier levels
        tier_levels = [t.tier_level for t in AlphaTier]
        assert 1 in tier_levels  # T1
        assert 2 in tier_levels  # T2
        assert 3 in tier_levels  # T3
        assert 4 in tier_levels  # T4

    def test_cardiac_has_endurance_and_resistance(self):
        """Test Cardiac Alpha has endurance and resistance boosts."""
        alpha = AlphaSlotFactory.create_cardiac(AlphaTier.T4_CORE_PARAGON)

        effect_types = [str(e.effect_type) for e in alpha.effects]

        # Should have endurance and resistance
        assert any("ENDURANCE" in et for et in effect_types)
        assert any("RESISTANCE" in et for et in effect_types)


class TestBuildStatsCopy:
    """Test BuildStats copy functionality."""

    def test_build_stats_copy_creates_independent_copy(self):
        """Test BuildStats.copy() creates independent copy."""
        stats = BuildStats(effective_level=50, totals={"DEFENSE": Decimal("0.15")})

        copy = stats.copy()

        # Modify copy
        copy.effective_level = 51
        copy.totals["DEFENSE"] = Decimal("0.20")

        # Original unchanged
        assert stats.effective_level == 50
        assert stats.totals["DEFENSE"] == Decimal("0.15")

        # Copy changed
        assert copy.effective_level == 51
        assert copy.totals["DEFENSE"] == Decimal("0.20")
