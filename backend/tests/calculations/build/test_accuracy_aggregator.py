"""
Tests for Build Accuracy & ToHit Aggregation

Maps to Spec 23 test cases (Section 4).
Verifies accuracy and tohit calculation logic matches MidsReborn.
"""

import pytest
from app.calculations.build.accuracy_aggregator import (
    BuildAccuracyCalculator,
    GlobalAccuracyTotals,
    AccuracySource,
    AccuracyContribution
)


class TestAccuracyAggregator:
    """Test suite for accuracy and tohit aggregation"""

    def setup_method(self):
        """Set up calculator for each test"""
        self.calculator = BuildAccuracyCalculator()

    # Test Case 1: Base Build (No Bonuses)
    def test_base_build_no_bonuses(self):
        """
        Test Case 1 from Spec 23:
        Character with no accuracy or tohit bonuses.

        Expected:
          - Accuracy: 0%
          - ToHit: 0%
        """
        totals = self.calculator.calculate_accuracy_totals(
            set_bonuses=[],
            special_ios=[],
            power_buffs=[],
            incarnate_bonuses=[]
        )

        assert totals.accuracy == 0.0, "Base accuracy should be 0"
        assert totals.tohit == 0.0, "Base tohit should be 0"
        assert totals.accuracy_percentage == 0.0
        assert totals.tohit_percentage == 0.0
        assert len(totals.accuracy_contributions) == 0
        assert len(totals.tohit_contributions) == 0

    # Test Case 2: Set Bonuses Only
    def test_set_bonuses_only(self):
        """
        Test Case 2 from Spec 23:
        Character with 2× Thunderstrike sets (9% acc each) + 1× Decimation (9% acc).

        Expected:
          - Accuracy: 27% (9 + 9 + 9)
          - ToHit: 0%
        """
        set_bonuses = [
            {"name": "Thunderstrike (Set 1)", "type": "accuracy", "magnitude": 0.09},
            {"name": "Thunderstrike (Set 2)", "type": "accuracy", "magnitude": 0.09},
            {"name": "Decimation", "type": "accuracy", "magnitude": 0.09}
        ]

        totals = self.calculator.calculate_accuracy_totals(
            set_bonuses=set_bonuses,
            special_ios=[],
            power_buffs=[],
            incarnate_bonuses=[]
        )

        assert abs(totals.accuracy - 0.27) < 0.001, f"Expected 0.27, got {totals.accuracy}"
        assert totals.tohit == 0.0
        assert abs(totals.accuracy_percentage - 27.0) < 0.01
        assert len(totals.accuracy_contributions) == 3
        assert len(totals.tohit_contributions) == 0

    # Test Case 3: Kismet +ToHit IO (Actually Accuracy!)
    def test_kismet_io_accuracy(self):
        """
        Test Case 3 from Spec 23:
        CRITICAL: Kismet +ToHit IO grants +6% ACCURACY, not tohit!
        This is MidsReborn's documented behavior (despite the IO name).

        Expected:
          - Accuracy: 6% (from Kismet)
          - ToHit: 0%
        """
        special_ios = [
            {"name": "Kismet +ToHit", "type": "accuracy", "magnitude": 0.06}
        ]

        totals = self.calculator.calculate_accuracy_totals(
            set_bonuses=[],
            special_ios=special_ios,
            power_buffs=[],
            incarnate_bonuses=[]
        )

        assert abs(totals.accuracy - 0.06) < 0.001, "Kismet grants accuracy, not tohit"
        assert totals.tohit == 0.0, "Kismet should not grant tohit"
        assert abs(totals.accuracy_percentage - 6.0) < 0.01
        assert len(totals.accuracy_contributions) == 1
        assert totals.accuracy_contributions[0].source_name == "Kismet +ToHit"
        assert totals.accuracy_contributions[0].source_type == AccuracySource.SPECIAL_IO

    # Test Case 4: Tactics Power (ToHit Buff)
    def test_tactics_tohit_buff(self):
        """
        Test Case 4 from Spec 23:
        Tactics power grants +7% tohit (when slotted for tohit).

        Expected:
          - Accuracy: 0%
          - ToHit: 7%
        """
        power_buffs = [
            {"power": "Tactics", "type": "tohit", "magnitude": 0.07}
        ]

        totals = self.calculator.calculate_accuracy_totals(
            set_bonuses=[],
            special_ios=[],
            power_buffs=power_buffs,
            incarnate_bonuses=[]
        )

        assert totals.accuracy == 0.0
        assert abs(totals.tohit - 0.07) < 0.001
        assert abs(totals.tohit_percentage - 7.0) < 0.01
        assert len(totals.tohit_contributions) == 1
        assert totals.tohit_contributions[0].source_name == "Tactics"
        assert totals.tohit_contributions[0].power_name == "Tactics"

    # Test Case 5: Combined Build (Set Bonuses + Kismet + Tactics)
    def test_combined_accuracy_and_tohit(self):
        """
        Test Case 5 from Spec 23:
        Realistic IO'd build with:
        - 2× Thunderstrike sets (9% acc each)
        - 1× Decimation set (9% acc)
        - Kismet +ToHit IO (6% acc)
        - Tactics power (7% tohit)

        Expected:
          - Accuracy: 33% (9 + 9 + 9 + 6)
          - ToHit: 7%
        """
        set_bonuses = [
            {"name": "Thunderstrike (Set 1)", "type": "accuracy", "magnitude": 0.09},
            {"name": "Thunderstrike (Set 2)", "type": "accuracy", "magnitude": 0.09},
            {"name": "Decimation", "type": "accuracy", "magnitude": 0.09}
        ]
        special_ios = [
            {"name": "Kismet +ToHit", "type": "accuracy", "magnitude": 0.06}
        ]
        power_buffs = [
            {"power": "Tactics", "type": "tohit", "magnitude": 0.07}
        ]

        totals = self.calculator.calculate_accuracy_totals(
            set_bonuses=set_bonuses,
            special_ios=special_ios,
            power_buffs=power_buffs,
            incarnate_bonuses=[]
        )

        assert abs(totals.accuracy - 0.33) < 0.001, f"Expected 0.33, got {totals.accuracy}"
        assert abs(totals.tohit - 0.07) < 0.001, f"Expected 0.07, got {totals.tohit}"
        assert abs(totals.accuracy_percentage - 33.0) < 0.01
        assert abs(totals.tohit_percentage - 7.0) < 0.01
        assert len(totals.accuracy_contributions) == 4  # 3 sets + Kismet
        assert len(totals.tohit_contributions) == 1  # Tactics

    # Test Case 6: Incarnate Alpha Accuracy
    def test_incarnate_alpha_accuracy(self):
        """
        Test Case 6 from Spec 23:
        Incarnate Alpha slot provides +5% accuracy.

        Expected:
          - Accuracy: 5%
          - ToHit: 0%
        """
        incarnate_bonuses = [
            {"slot": "Alpha", "type": "accuracy", "magnitude": 0.05}
        ]

        totals = self.calculator.calculate_accuracy_totals(
            set_bonuses=[],
            special_ios=[],
            power_buffs=[],
            incarnate_bonuses=incarnate_bonuses
        )

        assert abs(totals.accuracy - 0.05) < 0.001
        assert totals.tohit == 0.0
        assert abs(totals.accuracy_percentage - 5.0) < 0.01
        assert len(totals.accuracy_contributions) == 1
        assert totals.accuracy_contributions[0].source_type == AccuracySource.INCARNATE

    # Edge Case: Ignore Power Buff Flags
    def test_power_ignore_buffs_flag(self):
        """
        Test that powers can ignore global accuracy/tohit when flagged.
        Some powers (auto-hit, pet summons) ignore these buffs.
        """
        set_bonuses = [
            {"name": "Thunderstrike", "type": "accuracy", "magnitude": 0.09}
        ]
        power_buffs = [
            {"power": "Tactics", "type": "tohit", "magnitude": 0.07}
        ]

        totals = self.calculator.calculate_accuracy_totals(
            set_bonuses=set_bonuses,
            special_ios=[],
            power_buffs=power_buffs,
            incarnate_bonuses=[]
        )

        # Normal power: gets full bonuses
        accuracy_normal = totals.get_accuracy_for_power(power_ignores_buffs=False)
        tohit_normal = totals.get_tohit_for_power(power_ignores_buffs=False)
        assert abs(accuracy_normal - 0.09) < 0.001
        assert abs(tohit_normal - 0.07) < 0.001

        # Auto-hit power: ignores bonuses
        accuracy_ignored = totals.get_accuracy_for_power(power_ignores_buffs=True)
        tohit_ignored = totals.get_tohit_for_power(power_ignores_buffs=True)
        assert accuracy_ignored == 0.0
        assert tohit_ignored == 0.0

    # Edge Case: No Caps on Accuracy/ToHit
    def test_no_caps_on_accuracy_tohit(self):
        """
        Verify that accuracy and tohit have NO caps at aggregation level.
        Unlike defense (45% soft cap) or resistance (75-90% hard cap),
        accuracy/tohit can stack infinitely.

        Final hit chance is capped at 5%-95% per attack, but totals are uncapped.
        """
        # Absurdly high bonuses (would never happen in real gameplay)
        set_bonuses = [
            {"name": "Set 1", "type": "accuracy", "magnitude": 0.50},
            {"name": "Set 2", "type": "accuracy", "magnitude": 0.50},
            {"name": "Set 3", "type": "accuracy", "magnitude": 0.50}
        ]
        power_buffs = [
            {"power": "Buff 1", "type": "tohit", "magnitude": 0.50},
            {"power": "Buff 2", "type": "tohit", "magnitude": 0.50}
        ]

        totals = self.calculator.calculate_accuracy_totals(
            set_bonuses=set_bonuses,
            special_ios=[],
            power_buffs=power_buffs,
            incarnate_bonuses=[]
        )

        # Should aggregate without capping
        assert abs(totals.accuracy - 1.50) < 0.001, "Accuracy should not be capped"
        assert abs(totals.tohit - 1.00) < 0.001, "ToHit should not be capped"
        assert abs(totals.accuracy_percentage - 150.0) < 0.01
        assert abs(totals.tohit_percentage - 100.0) < 0.01

    # Edge Case: Invalid Magnitudes
    def test_invalid_magnitude_validation(self):
        """
        Test that invalid magnitude values raise ValueError.
        Magnitudes should be 0.0-2.0 (0-200%).
        """
        # Negative magnitude
        with pytest.raises(ValueError, match="Invalid magnitude"):
            self.calculator.calculate_accuracy_totals(
                set_bonuses=[{"name": "Bad", "type": "accuracy", "magnitude": -0.1}],
                special_ios=[],
                power_buffs=[],
                incarnate_bonuses=[]
            )

        # Too large magnitude
        with pytest.raises(ValueError, match="Invalid magnitude"):
            self.calculator.calculate_accuracy_totals(
                set_bonuses=[{"name": "Bad", "type": "accuracy", "magnitude": 2.5}],
                special_ios=[],
                power_buffs=[],
                incarnate_bonuses=[]
            )

    # Test Formatting
    def test_format_accuracy_breakdown(self):
        """
        Test that breakdown formatting matches expected output.
        """
        set_bonuses = [
            {"name": "Thunderstrike", "type": "accuracy", "magnitude": 0.09}
        ]
        power_buffs = [
            {"power": "Tactics", "type": "tohit", "magnitude": 0.07}
        ]

        totals = self.calculator.calculate_accuracy_totals(
            set_bonuses=set_bonuses,
            special_ios=[],
            power_buffs=power_buffs,
            incarnate_bonuses=[]
        )

        breakdown = self.calculator.format_accuracy_breakdown(totals)

        # Should contain all key info
        assert "Total Accuracy: 9.00%" in breakdown
        assert "Thunderstrike: +9.00%" in breakdown
        assert "Total ToHit: 7.00%" in breakdown
        assert "Tactics (Tactics): +7.00%" in breakdown  # Power name included in parentheses

    # Test String Representation
    def test_totals_string_representation(self):
        """
        Test __str__ method formats correctly.
        """
        set_bonuses = [
            {"name": "Thunderstrike", "type": "accuracy", "magnitude": 0.09}
        ]
        power_buffs = [
            {"power": "Tactics", "type": "tohit", "magnitude": 0.07}
        ]

        totals = self.calculator.calculate_accuracy_totals(
            set_bonuses=set_bonuses,
            special_ios=[],
            power_buffs=power_buffs,
            incarnate_bonuses=[]
        )

        string_repr = str(totals)
        assert "Accuracy: 9.00%" in string_repr
        assert "ToHit: 7.00%" in string_repr
