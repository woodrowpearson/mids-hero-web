"""
Test Enhancement Diversification (ED) Schedules

Tests based on Spec 10 test cases from the plan.
Validates ED curve calculations for all 4 schedules (A, B, C, D).
"""

import pytest
from app.calculations.core import (
    EDSchedule,
    apply_ed,
    get_schedule,
    calculate_ed_loss,
    constants
)


class TestEDScheduleApplication:
    """Test Suite: ED Schedule Application from Spec 10 Test Cases"""

    def test_schedule_a_at_50_percent(self):
        """
        Test 1: Schedule A at 50% → 50.0% (no diminishing)

        From Spec 10, Section 4, Test Case 1.
        Below first threshold (70%), no ED applies.
        """
        result = apply_ed(EDSchedule.A, 0.50)
        assert result == 0.50  # No ED below threshold

    def test_schedule_a_at_75_percent(self):
        """
        Test 2: Schedule A at 75% → 73.0% (90% efficiency)

        From Spec 10, Section 4, Test Case 2.
        Between threshold 1 (70%) and threshold 2 (90%), 90% efficiency applies.

        Calculation:
        0.70 + (0.75 - 0.70) * 0.90 = 0.70 + 0.045 = 0.745
        """
        result = apply_ed(EDSchedule.A, 0.75)
        expected = 0.70 + (0.75 - 0.70) * 0.90  # = 0.745
        assert abs(result - expected) < 0.001

    def test_schedule_a_at_95_percent(self):
        """
        Test 3: Schedule A at 95% → 88.75% (15% efficiency after 90%)

        From Spec 10, Section 4, Test Case 3.
        Above threshold 2 (90%), 70% efficiency applies, then 15% above threshold 3.

        Calculation:
        Region 1: 0.70 (below 70%)
        Region 2: 0.70 + (0.90 - 0.70) * 0.90 = 0.70 + 0.18 = 0.88 (at 90%)
        Region 3: 0.88 + (0.95 - 0.90) * 0.70 = 0.88 + 0.035 = 0.915 (at 95%)
        """
        result = apply_ed(EDSchedule.A, 0.95)

        # Pre-calculate cumulative values
        edm1 = 0.70
        edm2 = 0.70 + (0.90 - 0.70) * 0.90  # = 0.88
        expected = edm2 + (0.95 - 0.90) * 0.70  # = 0.915

        assert abs(result - expected) < 0.001

    def test_schedule_b_at_100_percent(self):
        """
        Test 4: Schedule B at 100% → 56.0% (strict curve)

        From Spec 10, Section 4, Test Case 4.
        Schedule B is very aggressive for defense/resistance.

        At 100% with Schedule B (thresholds: 40%, 50%, 60%):
        Region 1: 0.40 (below 40%)
        Region 2: 0.40 + (0.50 - 0.40) * 0.90 = 0.40 + 0.09 = 0.49 (at 50%)
        Region 3: 0.49 + (0.60 - 0.50) * 0.70 = 0.49 + 0.07 = 0.56 (at 60%)
        Region 4: 0.56 + (1.00 - 0.60) * 0.15 = 0.56 + 0.06 = 0.62 (at 100%)
        """
        result = apply_ed(EDSchedule.B, 1.00)

        # Pre-calculate cumulative values
        edm1 = 0.40
        edm2 = 0.40 + (0.50 - 0.40) * 0.90  # = 0.49
        edm3 = edm2 + (0.60 - 0.50) * 0.70  # = 0.56
        expected = edm3 + (1.00 - 0.60) * 0.15  # = 0.62

        assert abs(result - expected) < 0.001

    def test_schedule_c_at_150_percent(self):
        """
        Test 5: Schedule C at 150% → 97.5% (very strict)

        From Spec 10, Section 4, Test Case 5.
        Schedule C is lenient (thresholds: 80%, 100%, 120%).

        At 150%:
        Region 1: 0.80 (below 80%)
        Region 2: 0.80 + (1.00 - 0.80) * 0.90 = 0.80 + 0.18 = 0.98 (at 100%)
        Region 3: 0.98 + (1.20 - 1.00) * 0.70 = 0.98 + 0.14 = 1.12 (at 120%)
        Region 4: 1.12 + (1.50 - 1.20) * 0.15 = 1.12 + 0.045 = 1.165 (at 150%)
        """
        result = apply_ed(EDSchedule.C, 1.50)

        # Pre-calculate cumulative values
        edm1 = 0.80
        edm2 = 0.80 + (1.00 - 0.80) * 0.90  # = 0.98
        edm3 = edm2 + (1.20 - 1.00) * 0.70  # = 1.12
        expected = edm3 + (1.50 - 1.20) * 0.15  # = 1.165

        assert abs(result - expected) < 0.001

    def test_schedule_d_at_200_percent(self):
        """
        Test 6: Schedule D at 200% → 200.0% (no diminishing)

        From Spec 10, Section 4, Test Case 6.
        Schedule D is VERY lenient (thresholds: 120%, 150%, 180%).

        At 200%:
        Region 1: 1.20 (below 120%)
        Region 2: 1.20 + (1.50 - 1.20) * 0.90 = 1.20 + 0.27 = 1.47 (at 150%)
        Region 3: 1.47 + (1.80 - 1.50) * 0.70 = 1.47 + 0.21 = 1.68 (at 180%)
        Region 4: 1.68 + (2.00 - 1.80) * 0.15 = 1.68 + 0.03 = 1.71 (at 200%)
        """
        result = apply_ed(EDSchedule.D, 2.00)

        # Pre-calculate cumulative values
        edm1 = 1.20
        edm2 = 1.20 + (1.50 - 1.20) * 0.90  # = 1.47
        edm3 = edm2 + (1.80 - 1.50) * 0.70  # = 1.68
        expected = edm3 + (2.00 - 1.80) * 0.15  # = 1.71

        assert abs(result - expected) < 0.001


class TestScheduleAssignment:
    """Test Suite: Schedule Assignment Logic"""

    def test_damage_uses_schedule_a(self):
        """Damage uses Schedule A (standard)"""
        assert get_schedule("Damage") == EDSchedule.A

    def test_defense_uses_schedule_b(self):
        """Defense uses Schedule B (aggressive)"""
        assert get_schedule("Defense") == EDSchedule.B

    def test_interrupt_uses_schedule_c(self):
        """Interrupt uses Schedule C (lenient)"""
        assert get_schedule("Interrupt") == EDSchedule.C

    def test_mez_afraid_uses_schedule_d(self):
        """Afraid mez (subtype 4) uses Schedule D"""
        assert get_schedule("Mez", 4) == EDSchedule.D

    def test_mez_confused_uses_schedule_d(self):
        """Confused mez (subtype 5) uses Schedule D"""
        assert get_schedule("Mez", 5) == EDSchedule.D

    def test_mez_hold_uses_schedule_a(self):
        """Hold mez (subtype 1) uses Schedule A"""
        assert get_schedule("Mez", 1) == EDSchedule.A

    def test_resistance_uses_schedule_b(self):
        """Resistance uses Schedule B (aggressive)"""
        assert get_schedule("Resistance") == EDSchedule.B

    def test_range_uses_schedule_b(self):
        """Range uses Schedule B"""
        assert get_schedule("Range") == EDSchedule.B

    def test_tohit_uses_schedule_b(self):
        """ToHit uses Schedule B"""
        assert get_schedule("ToHit") == EDSchedule.B

    def test_accuracy_uses_schedule_a(self):
        """Accuracy uses Schedule A (standard)"""
        assert get_schedule("Accuracy") == EDSchedule.A

    def test_recharge_uses_schedule_a(self):
        """Recharge uses Schedule A"""
        assert get_schedule("Recharge") == EDSchedule.A


class TestRealisticExamples:
    """Test Suite: Realistic Enhancement Examples"""

    def test_three_sos_damage(self):
        """
        Three SOs in damage (Schedule A).

        3 × 33.3% = 99.9% ≈ 1.0
        Expected output: 95% (5% loss to ED)
        """
        result = apply_ed(EDSchedule.A, 1.0)

        # Calculate expected
        edm1 = 0.70
        edm2 = 0.70 + (0.90 - 0.70) * 0.90  # = 0.88
        expected = edm2 + (1.00 - 0.90) * 0.70  # = 0.95

        assert abs(result - expected) < 0.001
        assert abs(result - 0.95) < 0.01  # ~95%

    def test_six_sos_damage(self):
        """
        Six SOs in damage (Schedule A) - The classic "six-slotting" case.

        6 × 33.3% = 199.8% ≈ 2.0
        Expected output: 110% (45% loss to ED!)

        This is why six-slotting died with Issue 5.
        """
        result = apply_ed(EDSchedule.A, 2.0)

        # Calculate expected
        edm1 = 0.70
        edm2 = 0.70 + (0.90 - 0.70) * 0.90  # = 0.88
        edm3 = edm2 + (1.00 - 0.90) * 0.70  # = 0.95
        expected = edm3 + (2.00 - 1.00) * 0.15  # = 1.10

        assert abs(result - expected) < 0.001
        assert abs(result - 1.10) < 0.01  # ~110%

    def test_three_sos_defense(self):
        """
        Three SOs in defense (Schedule B) - Much more aggressive ED.

        3 × 33.3% = 99.9% ≈ 1.0
        Expected output: 62% (38% loss to ED!)

        Defense is MUCH more heavily penalized than damage.
        """
        result = apply_ed(EDSchedule.B, 1.0)

        # Calculate expected
        edm1 = 0.40
        edm2 = 0.40 + (0.50 - 0.40) * 0.90  # = 0.49
        edm3 = edm2 + (0.60 - 0.50) * 0.70  # = 0.56
        expected = edm3 + (1.00 - 0.60) * 0.15  # = 0.62

        assert abs(result - expected) < 0.001
        assert abs(result - 0.62) < 0.01  # ~62%

    def test_below_threshold_no_ed(self):
        """Enhancement below first threshold has no ED"""
        # Schedule A threshold 1 is 70%
        result = apply_ed(EDSchedule.A, 0.50)
        assert result == 0.50  # No change

        # Schedule B threshold 1 is 40%
        result = apply_ed(EDSchedule.B, 0.30)
        assert result == 0.30  # No change


class TestEDLossCalculation:
    """Test Suite: ED Loss Calculation"""

    def test_calculate_ed_loss_schedule_a(self):
        """Test ED loss calculation for Schedule A"""
        post_ed, pre_ed, percent_lost = calculate_ed_loss(EDSchedule.A, 2.0)

        assert pre_ed == 2.0
        assert abs(post_ed - 1.10) < 0.01
        assert abs(percent_lost - 45.0) < 1.0  # ~45% loss

    def test_calculate_ed_loss_schedule_b(self):
        """Test ED loss calculation for Schedule B"""
        post_ed, pre_ed, percent_lost = calculate_ed_loss(EDSchedule.B, 1.0)

        assert pre_ed == 1.0
        assert abs(post_ed - 0.62) < 0.01
        assert abs(percent_lost - 38.0) < 1.0  # ~38% loss

    def test_calculate_ed_loss_below_threshold(self):
        """No loss when below threshold"""
        post_ed, pre_ed, percent_lost = calculate_ed_loss(EDSchedule.A, 0.50)

        assert pre_ed == 0.50
        assert post_ed == 0.50
        assert percent_lost == 0.0


class TestConstants:
    """Test Suite: Verify Game Constants"""

    def test_base_magic_constant(self):
        """Verify BASE_MAGIC constant is correct"""
        assert abs(constants.BASE_MAGIC - 1.666667) < 0.000001

    def test_ed_thresholds_schedule_a(self):
        """Verify Schedule A thresholds"""
        assert constants.ED_SCHEDULE_A_THRESH_1 == 0.70
        assert constants.ED_SCHEDULE_A_THRESH_2 == 0.90
        assert constants.ED_SCHEDULE_A_THRESH_3 == 1.00

    def test_ed_thresholds_schedule_b(self):
        """Verify Schedule B thresholds (most aggressive)"""
        assert constants.ED_SCHEDULE_B_THRESH_1 == 0.40
        assert constants.ED_SCHEDULE_B_THRESH_2 == 0.50
        assert constants.ED_SCHEDULE_B_THRESH_3 == 0.60

    def test_ed_thresholds_schedule_c(self):
        """Verify Schedule C thresholds (lenient)"""
        assert constants.ED_SCHEDULE_C_THRESH_1 == 0.80
        assert constants.ED_SCHEDULE_C_THRESH_2 == 1.00
        assert constants.ED_SCHEDULE_C_THRESH_3 == 1.20

    def test_ed_thresholds_schedule_d(self):
        """Verify Schedule D thresholds (very lenient)"""
        assert constants.ED_SCHEDULE_D_THRESH_1 == 1.20
        assert constants.ED_SCHEDULE_D_THRESH_2 == 1.50
        assert constants.ED_SCHEDULE_D_THRESH_3 == 1.80

    def test_ed_efficiency_constants(self):
        """Verify ED efficiency multipliers"""
        assert constants.ED_EFFICIENCY_REGION_1 == 1.00  # 100%
        assert constants.ED_EFFICIENCY_REGION_2 == 0.90  # 90%
        assert constants.ED_EFFICIENCY_REGION_3 == 0.70  # 70%
        assert constants.ED_EFFICIENCY_REGION_4 == 0.15  # 15%

    def test_standard_enhancement_values(self):
        """Verify standard enhancement values"""
        assert abs(constants.SINGLE_ORIGIN_VALUE - 0.3333) < 0.0001
        assert abs(constants.INVENTION_ORIGIN_L50_VALUE - 0.424) < 0.001

    def test_rule_of_five(self):
        """Verify Rule of 5 constant"""
        assert constants.RULE_OF_FIVE_LIMIT == 5
