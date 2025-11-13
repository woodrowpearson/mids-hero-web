"""
Tests for Enhancement Set Bonuses System (Spec 13)

Implements all 4 test cases from the specification with exact expected values.
Tests the Rule of 5 and set bonus activation logic.
"""

import pytest

from app.calculations.enhancements.set_bonuses import (
    BonusItem,
    EnhancementSet,
    PvMode,
    SetBonusCalculator,
    SlottedSet,
    create_bonus_summary,
    track_slotted_sets,
    validate_enhancement_set,
    validate_slotted_set,
)


@pytest.fixture
def sample_set_definitions():
    """Create sample enhancement set definitions for testing."""
    return {
        # Thunderstrike set (popular damage/acc set)
        10: EnhancementSet(
            id=10,
            uid="thunderstrike",
            name="Thunderstrike",
            short_name="Thund",
            set_type="RangedST",
            level_min=30,
            level_max=50,
            enhancement_ids=[100, 101, 102, 103, 104, 105],
            bonuses=[
                BonusItem(
                    slotted_required=2,
                    power_ids=[1000],  # +2% Damage
                    pv_mode=PvMode.ANY,
                    power_names=["+2% Damage (All Types)"],
                ),
                BonusItem(
                    slotted_required=3,
                    power_ids=[1001],  # +9% Accuracy
                    pv_mode=PvMode.ANY,
                    power_names=["+9% Accuracy"],
                ),
                BonusItem(
                    slotted_required=4,
                    power_ids=[1002],  # +2.5% Damage
                    pv_mode=PvMode.ANY,
                    power_names=["+2.5% Damage (All Types)"],
                ),
                BonusItem(
                    slotted_required=5,
                    power_ids=[1003],  # +5% Recharge
                    pv_mode=PvMode.ANY,
                    power_names=["+5% Recharge"],
                ),
                BonusItem(
                    slotted_required=6,
                    power_ids=[1004],  # +1.5% Energy/Neg Def
                    pv_mode=PvMode.ANY,
                    power_names=["+1.5% Energy/Negative Defense"],
                ),
            ],
            special_bonuses=[BonusItem(slotted_required=0, power_ids=[])] * 6,
        ),
        # Set X (for Rule of 5 testing) - grants Ranged Defense
        20: EnhancementSet(
            id=20,
            uid="set_x",
            name="Set X",
            short_name="SetX",
            set_type="RangedST",
            level_min=10,
            level_max=50,
            enhancement_ids=[200, 201],
            bonuses=[
                BonusItem(
                    slotted_required=2,
                    power_ids=[2000],  # +1.5% Ranged Defense
                    pv_mode=PvMode.ANY,
                    power_names=["+1.5% Ranged Defense"],
                ),
            ],
            special_bonuses=[BonusItem(slotted_required=0, power_ids=[])] * 2,
        ),
        # Set Y - also grants Ranged Defense
        21: EnhancementSet(
            id=21,
            uid="set_y",
            name="Set Y",
            short_name="SetY",
            set_type="RangedST",
            level_min=10,
            level_max=50,
            enhancement_ids=[210, 211],
            bonuses=[
                BonusItem(
                    slotted_required=2,
                    power_ids=[2000],  # Same power ID!
                    pv_mode=PvMode.ANY,
                    power_names=["+1.5% Ranged Defense"],
                ),
            ],
            special_bonuses=[BonusItem(slotted_required=0, power_ids=[])] * 2,
        ),
        # PvP set (has PvE and PvP specific bonuses)
        30: EnhancementSet(
            id=30,
            uid="pvp_set",
            name="PvP IO Set",
            short_name="PvP",
            set_type="RangedST",
            level_min=10,
            level_max=50,
            enhancement_ids=[300, 301, 302, 303, 304, 305],
            bonuses=[
                BonusItem(
                    slotted_required=2,
                    power_ids=[3000],  # PvE bonus
                    pv_mode=PvMode.PVE,
                    power_names=["+2% Damage (PvE)"],
                ),
                BonusItem(
                    slotted_required=3,
                    power_ids=[3001],  # PvP bonus
                    pv_mode=PvMode.PVP,
                    power_names=["+5% Damage (PvP)"],
                ),
                BonusItem(
                    slotted_required=4,
                    power_ids=[3002],  # Any mode bonus
                    pv_mode=PvMode.ANY,
                    power_names=["+10 MaxHP"],
                ),
            ],
            special_bonuses=[BonusItem(slotted_required=0, power_ids=[])] * 6,
        ),
        # Pet set with special bonus (6th enhancement has special effect)
        40: EnhancementSet(
            id=40,
            uid="pet_set",
            name="Call of the Sandman",
            short_name="CoS",
            set_type="Pets",
            level_min=10,
            level_max=50,
            enhancement_ids=[400, 401, 402, 403, 404, 405],
            bonuses=[
                BonusItem(
                    slotted_required=2,
                    power_ids=[4000],
                    pv_mode=PvMode.ANY,
                    power_names=["+10% Accuracy"],
                ),
            ],
            special_bonuses=[
                BonusItem(slotted_required=0, power_ids=[]),  # Enh 0: no special
                BonusItem(slotted_required=0, power_ids=[]),  # Enh 1: no special
                BonusItem(slotted_required=0, power_ids=[]),  # Enh 2: no special
                BonusItem(slotted_required=0, power_ids=[]),  # Enh 3: no special
                BonusItem(slotted_required=0, power_ids=[]),  # Enh 4: no special
                BonusItem(
                    slotted_required=0,
                    power_ids=[4001],  # Enh 5: Chance for Heal proc
                    pv_mode=PvMode.ANY,
                    power_names=["Chance for Heal"],
                ),
            ],
        ),
    }


class TestBasicSetBonusActivation:
    """Test basic set bonus activation mechanics."""

    def test_empty_build(self, sample_set_definitions):
        """Test calculator with no slotted sets."""
        calculator = SetBonusCalculator(pv_mode=PvMode.PVE)
        bonuses = calculator.calculate_set_bonuses([], sample_set_definitions)

        assert len(bonuses) == 0

    def test_incomplete_set_no_bonus(self, sample_set_definitions):
        """Test that 1 piece doesn't activate 2-piece bonus."""
        calculator = SetBonusCalculator(pv_mode=PvMode.PVE)

        slotted_sets = [
            SlottedSet(
                power_id=1, set_id=10, slotted_count=1, enhancement_ids=[100]
            )
        ]

        bonuses = calculator.calculate_set_bonuses(
            slotted_sets, sample_set_definitions
        )

        assert len(bonuses) == 0  # No bonuses with only 1 piece

    def test_two_piece_bonus(self, sample_set_definitions):
        """Test 2-piece bonus activation."""
        calculator = SetBonusCalculator(pv_mode=PvMode.PVE)

        slotted_sets = [
            SlottedSet(
                power_id=1, set_id=10, slotted_count=2, enhancement_ids=[100, 101]
            )
        ]

        bonuses = calculator.calculate_set_bonuses(
            slotted_sets, sample_set_definitions
        )

        # Should get 2-piece bonus: +2% Damage (power ID 1000)
        assert len(bonuses) == 1
        assert bonuses[0] == 1000


# ====================
# SPEC TEST CASES
# ====================


class TestCase1_BasicSetActivation:
    """
    Test Case 1: Basic Set Activation

    Setup:
    - Power A: 3x Thunderstrike enhancements

    Expected:
    - 2-piece bonus active: +2% Damage (all types)
    - 3-piece bonus active: +9% Accuracy
    - 4-piece bonus NOT active
    - 5-piece bonus NOT active
    - 6-piece bonus NOT active
    """

    def test_three_piece_thunderstrike(self, sample_set_definitions):
        """Test 3-piece Thunderstrike activates 2 and 3 piece bonuses."""
        calculator = SetBonusCalculator(pv_mode=PvMode.PVE)

        slotted_sets = [
            SlottedSet(
                power_id=1,
                set_id=10,  # Thunderstrike
                slotted_count=3,
                enhancement_ids=[100, 101, 102],
            )
        ]

        bonuses = calculator.calculate_set_bonuses(
            slotted_sets, sample_set_definitions
        )

        # Should activate 2-piece and 3-piece bonuses
        assert len(bonuses) == 2

        # Check which bonuses activated
        assert 1000 in bonuses  # 2-piece: +2% Damage
        assert 1001 in bonuses  # 3-piece: +9% Accuracy

        # 4-piece and above should NOT be active
        assert 1002 not in bonuses  # 4-piece
        assert 1003 not in bonuses  # 5-piece
        assert 1004 not in bonuses  # 6-piece

    def test_six_piece_full_set(self, sample_set_definitions):
        """Test full 6-piece set activates all bonuses."""
        calculator = SetBonusCalculator(pv_mode=PvMode.PVE)

        slotted_sets = [
            SlottedSet(
                power_id=1,
                set_id=10,
                slotted_count=6,
                enhancement_ids=[100, 101, 102, 103, 104, 105],
            )
        ]

        bonuses = calculator.calculate_set_bonuses(
            slotted_sets, sample_set_definitions
        )

        # Should activate all 5 bonus tiers
        assert len(bonuses) == 5

        # Verify all bonuses
        assert 1000 in bonuses  # 2-piece
        assert 1001 in bonuses  # 3-piece
        assert 1002 in bonuses  # 4-piece
        assert 1003 in bonuses  # 5-piece
        assert 1004 in bonuses  # 6-piece


class TestCase2_RuleOfFive:
    """
    Test Case 2: Rule of 5

    Setup:
    - Power A: 2x Set X (grants +1.5% Ranged Def)
    - Power B: 2x Set X (grants +1.5% Ranged Def)
    - Power C: 2x Set Y (grants +1.5% Ranged Def)
    - Power D: 2x Set Z (grants +1.5% Ranged Def)
    - Power E: 2x Set W (grants +1.5% Ranged Def)
    - Power F: 2x Set V (grants +1.5% Ranged Def)

    Expected:
    - Only 5 instances of "+1.5% Ranged Def" active
    - 6th instance suppressed
    - Final total: +7.5% Ranged Defense (5 × 1.5%)
    """

    def test_rule_of_five_suppression(self, sample_set_definitions):
        """Test Rule of 5 suppresses 6th instance of same bonus."""
        calculator = SetBonusCalculator(pv_mode=PvMode.PVE)

        # Create 6 different sets that all grant the same bonus (power ID 2000)
        # Sets 20-25 all grant +1.5% Ranged Defense
        set_definitions = {**sample_set_definitions}

        # Add more sets that grant the same bonus
        for set_id in [22, 23, 24, 25]:
            set_definitions[set_id] = EnhancementSet(
                id=set_id,
                uid=f"set_{set_id}",
                name=f"Set {chr(ord('X') + set_id - 20)}",
                short_name=f"S{set_id}",
                set_type="RangedST",
                level_min=10,
                level_max=50,
                enhancement_ids=[set_id * 10, set_id * 10 + 1],
                bonuses=[
                    BonusItem(
                        slotted_required=2,
                        power_ids=[2000],  # Same power ID!
                        pv_mode=PvMode.ANY,
                        power_names=["+1.5% Ranged Defense"],
                    ),
                ],
                special_bonuses=[BonusItem(slotted_required=0, power_ids=[])] * 2,
            )

        # Slot 2 pieces from each set in different powers
        slotted_sets = []
        for power_id, set_id in enumerate([20, 21, 22, 23, 24, 25], start=1):
            slotted_sets.append(
                SlottedSet(
                    power_id=power_id,
                    set_id=set_id,
                    slotted_count=2,
                    enhancement_ids=[set_id * 10, set_id * 10 + 1],
                )
            )

        bonuses = calculator.calculate_set_bonuses(slotted_sets, set_definitions)

        # Rule of 5: Only 5 instances should be active
        assert len(bonuses) == 5

        # All should be the same power ID
        assert all(b == 2000 for b in bonuses)

        # Check bonus counts
        counts = calculator.get_bonus_counts()
        assert counts[2000] == 6  # 6 instances attempted
        assert bonuses.count(2000) == 5  # Only 5 active

        # Check suppressed
        suppressed = calculator.get_suppressed_bonuses()
        assert 2000 in suppressed

    def test_rule_of_five_with_mixed_bonuses(self, sample_set_definitions):
        """Test Rule of 5 applied independently to each bonus type."""
        calculator = SetBonusCalculator(pv_mode=PvMode.PVE)

        # Create multiple slotted sets
        # - 3 powers with Thunderstrike (each grants power 1000)
        # - 2 powers with Set X (each grants power 2000)
        slotted_sets = [
            # Three Thunderstrikes
            SlottedSet(
                power_id=1, set_id=10, slotted_count=2, enhancement_ids=[100, 101]
            ),
            SlottedSet(
                power_id=2, set_id=10, slotted_count=2, enhancement_ids=[100, 101]
            ),
            SlottedSet(
                power_id=3, set_id=10, slotted_count=2, enhancement_ids=[100, 101]
            ),
            # Two Set X
            SlottedSet(
                power_id=4, set_id=20, slotted_count=2, enhancement_ids=[200, 201]
            ),
            SlottedSet(
                power_id=5, set_id=20, slotted_count=2, enhancement_ids=[200, 201]
            ),
        ]

        bonuses = calculator.calculate_set_bonuses(
            slotted_sets, sample_set_definitions
        )

        # Should get:
        # - 3 instances of power 1000 (Thunderstrike 2-piece)
        # - 2 instances of power 2000 (Set X 2-piece)
        assert bonuses.count(1000) == 3
        assert bonuses.count(2000) == 2

        counts = calculator.get_bonus_counts()
        assert counts[1000] == 3
        assert counts[2000] == 2


class TestCase3_PvEVsPvP:
    """
    Test Case 3: PvE vs PvP Mode

    Setup:
    - Power A: Full PvP IO set (6 pieces)
    - Mode: PvE

    Expected:
    - PvE-specific bonuses active
    - PvP-specific bonuses suppressed
    - "Any" mode bonuses active
    """

    def test_pve_mode_bonuses(self, sample_set_definitions):
        """Test PvE mode activates correct bonuses."""
        calculator = SetBonusCalculator(pv_mode=PvMode.PVE)

        slotted_sets = [
            SlottedSet(
                power_id=1,
                set_id=30,  # PvP set
                slotted_count=6,
                enhancement_ids=[300, 301, 302, 303, 304, 305],
            )
        ]

        bonuses = calculator.calculate_set_bonuses(
            slotted_sets, sample_set_definitions
        )

        # Should activate:
        # - 2-piece PvE bonus (power 3000)
        # - 4-piece Any mode bonus (power 3002)
        # Should NOT activate:
        # - 3-piece PvP bonus (power 3001)

        assert 3000 in bonuses  # PvE bonus
        assert 3002 in bonuses  # Any mode bonus
        assert 3001 not in bonuses  # PvP bonus (suppressed)

        assert len(bonuses) == 2

    def test_pvp_mode_bonuses(self, sample_set_definitions):
        """Test PvP mode activates correct bonuses."""
        calculator = SetBonusCalculator(pv_mode=PvMode.PVP)

        slotted_sets = [
            SlottedSet(
                power_id=1,
                set_id=30,
                slotted_count=6,
                enhancement_ids=[300, 301, 302, 303, 304, 305],
            )
        ]

        bonuses = calculator.calculate_set_bonuses(
            slotted_sets, sample_set_definitions
        )

        # Should activate:
        # - 3-piece PvP bonus (power 3001)
        # - 4-piece Any mode bonus (power 3002)
        # Should NOT activate:
        # - 2-piece PvE bonus (power 3000)

        assert 3001 in bonuses  # PvP bonus
        assert 3002 in bonuses  # Any mode bonus
        assert 3000 not in bonuses  # PvE bonus (suppressed)

        assert len(bonuses) == 2


class TestCase4_SpecialEnhancementBonus:
    """
    Test Case 4: Special Enhancement Bonus

    Setup:
    - Power A (Pet): 6x Call of the Sandman (Pet Damage set)
    - Enhancement 6: "Chance for Heal" proc

    Expected:
    - Regular set bonuses (2-piece) active
    - Special bonus from 6th enhancement (heal proc) active
    """

    def test_special_enhancement_bonus(self, sample_set_definitions):
        """Test special per-enhancement bonuses activate."""
        calculator = SetBonusCalculator(pv_mode=PvMode.PVE)

        slotted_sets = [
            SlottedSet(
                power_id=1,
                set_id=40,  # Pet set with special bonus
                slotted_count=6,
                enhancement_ids=[400, 401, 402, 403, 404, 405],
            )
        ]

        bonuses = calculator.calculate_set_bonuses(
            slotted_sets, sample_set_definitions
        )

        # Should activate:
        # - 2-piece bonus: +10% Accuracy (power 4000)
        # - Special bonus from 6th enh: Chance for Heal (power 4001)

        assert 4000 in bonuses  # Regular 2-piece
        assert 4001 in bonuses  # Special bonus from enh 405

        assert len(bonuses) == 2

    def test_special_bonus_only_if_specific_enh_slotted(
        self, sample_set_definitions
    ):
        """Test special bonus only activates with specific enhancement."""
        calculator = SetBonusCalculator(pv_mode=PvMode.PVE)

        # Slot only first 5 enhancements (not the 6th with special bonus)
        slotted_sets = [
            SlottedSet(
                power_id=1,
                set_id=40,
                slotted_count=5,
                enhancement_ids=[400, 401, 402, 403, 404],  # No 405!
            )
        ]

        bonuses = calculator.calculate_set_bonuses(
            slotted_sets, sample_set_definitions
        )

        # Should only get regular bonus, not special
        assert 4000 in bonuses  # Regular 2-piece
        assert 4001 not in bonuses  # Special NOT active

        assert len(bonuses) == 1


class TestHelperFunctions:
    """Test helper functions for set bonus tracking."""

    def test_track_slotted_sets(self):
        """Test tracking sets from build data."""
        build_powers = [
            {
                "id": 1,
                "slots": [
                    {"enhancement": {"id": 100, "type": "SetO", "set_id": 10}},
                    {"enhancement": {"id": 101, "type": "SetO", "set_id": 10}},
                    {"enhancement": {"id": 200, "type": "SetO", "set_id": 20}},
                ],
            },
            {
                "id": 2,
                "slots": [
                    {"enhancement": {"id": 102, "type": "SetO", "set_id": 10}},
                    {"enhancement": {"id": 500, "type": "InventO"}},  # Regular IO
                ],
            },
        ]

        slotted_sets = track_slotted_sets(build_powers)

        # Should find 3 SlottedSet entries:
        # - Power 1: 2x set 10, 1x set 20
        # - Power 2: 1x set 10
        assert len(slotted_sets) == 3

        # Check Set 10 in Power 1
        set_10_p1 = [s for s in slotted_sets if s.power_id == 1 and s.set_id == 10][
            0
        ]
        assert set_10_p1.slotted_count == 2
        assert 100 in set_10_p1.enhancement_ids
        assert 101 in set_10_p1.enhancement_ids

    def test_create_bonus_summary(self):
        """Test bonus summary creation."""
        active_bonuses = [1000, 1000, 1000, 2000, 2000]
        bonus_counts = {1000: 3, 2000: 2}
        power_names = {1000: "+2% Damage", 2000: "+1.5% Defense"}

        summary = create_bonus_summary(active_bonuses, bonus_counts, power_names)

        assert summary["total_bonuses"] == 5
        assert summary["unique_bonuses"] == 2
        assert len(summary["bonuses"]) == 2
        assert summary["rule_of_5_active"] is False

        # Check first bonus (should be 1000 with count 3)
        bonus_1000 = [b for b in summary["bonuses"] if b["power_id"] == 1000][0]
        assert bonus_1000["count"] == 3
        assert bonus_1000["suppressed"] is False

    def test_create_bonus_summary_with_suppression(self):
        """Test summary with Rule of 5 suppression."""
        # 6 instances of same bonus
        active_bonuses = [1000] * 5  # Only 5 active
        bonus_counts = {1000: 6}  # 6 attempted
        power_names = {1000: "+2% Damage"}

        summary = create_bonus_summary(active_bonuses, bonus_counts, power_names)

        assert summary["total_bonuses"] == 5  # Only 5 active
        assert summary["rule_of_5_active"] is True
        assert summary["suppressed_bonuses"] == 1

        bonus = summary["bonuses"][0]
        assert bonus["count"] == 6
        assert bonus["effective_count"] == 5
        assert bonus["suppressed"] is True
        assert bonus["suppressed_count"] == 1


class TestValidation:
    """Test validation functions."""

    def test_validate_enhancement_set(self, sample_set_definitions):
        """Test set validation."""
        valid_set = sample_set_definitions[10]
        errors = validate_enhancement_set(valid_set)
        assert len(errors) == 0

    def test_validate_invalid_levels(self):
        """Test set with invalid levels."""
        invalid_set = EnhancementSet(
            id=1,
            uid="test",
            name="Test",
            short_name="T",
            set_type="Melee",
            level_min=60,  # Invalid!
            level_max=70,  # Invalid!
            enhancement_ids=[1, 2],
            bonuses=[],
        )

        errors = validate_enhancement_set(invalid_set)
        assert len(errors) > 0

    def test_validate_slotted_set(self):
        """Test slotted set validation."""
        valid = SlottedSet(
            power_id=1, set_id=10, slotted_count=3, enhancement_ids=[100, 101, 102]
        )

        errors = validate_slotted_set(valid)
        assert len(errors) == 0

    def test_validate_slotted_set_mismatch(self):
        """Test slotted set with count/IDs mismatch."""
        invalid = SlottedSet(
            power_id=1, set_id=10, slotted_count=3, enhancement_ids=[100, 101]  # Only 2!
        )

        errors = validate_slotted_set(invalid)
        assert len(errors) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
