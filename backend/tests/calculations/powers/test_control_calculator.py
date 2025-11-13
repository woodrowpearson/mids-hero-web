"""
Tests for Control/Mez Calculator

Based on test cases from Spec 04 section 4.
"""

import pytest

from app.calculations.powers.control_calculator import (
    ControlCalculator,
    KnockbackCalculator,
    MezEffect,
    MezProtection,
    MezResistance,
    MezType,
)


class TestControlCalculator:
    """Test ControlCalculator class"""

    def setup_method(self):
        """Setup calculator instance for each test"""
        self.calculator = ControlCalculator()

    def test_controller_hold_vs_minion(self):
        """
        Test Case 1: Controller Hold vs Minion

        Scenario: Level 50 Controller uses Mag 3 Hold on level 50 minion
        Expected: Hold applies, duration 15.6 seconds with enhancements
        """
        # Setup
        hold = MezEffect(
            mez_type=MezType.HELD, magnitude=3.0, duration=8.0, scale=1.0, stacks=True
        )

        minion_protection = MezProtection(held=1.0)
        minion_resistance = MezResistance(held=0.0)

        # Test magnitude check
        applies = self.calculator.applies(
            mez=hold,
            protection=minion_protection,
            at_scale=1.0,  # Controller base scale
            modifier_table_scale=1.0,
            caster_level=50,
            target_level=50,
        )

        assert applies is True, "Mag 3 should overcome Mag 1 protection"

        # Test duration calculation
        duration = self.calculator.calculate_duration(
            mez=hold,
            resistance=minion_resistance,
            at_duration_scale=1.0,
            duration_enhancement=0.95,  # 95% after ED
            caster_level=50,
            target_level=50,
        )

        assert duration == pytest.approx(
            15.6, abs=0.1
        ), f"Expected 15.6s duration, got {duration}"

    def test_blaster_stun_vs_boss_requires_stacking(self):
        """
        Test Case 2: Blaster Stun vs Boss (Requires Stacking)

        Scenario: Level 50 Blaster uses Mag 2 Stun twice on level 50 boss
        Expected: First application fails, second (stacked) succeeds
        """
        # Setup
        stun = MezEffect(
            mez_type=MezType.STUNNED,
            magnitude=2.0,
            duration=10.0,
            scale=1.0,
            stacks=True,
        )

        boss_protection = MezProtection(stunned=3.0)

        # First application - should fail
        applies_first = self.calculator.applies(
            mez=stun,
            protection=boss_protection,
            at_scale=0.8,  # Blasters have reduced mez scale
            modifier_table_scale=1.0,
            caster_level=50,
            target_level=50,
        )

        assert (
            applies_first is False
        ), "Single Mag 1.6 (2.0 * 0.8) should NOT overcome Mag 3 protection"

        # Stack magnitude
        stacked = self.calculator.stack_magnitude(
            mezzes=[stun, stun], at_scale=0.8, modifier_table_scale=1.0
        )

        # Check stacked magnitude
        total_mag = stacked[MezType.STUNNED]
        assert total_mag == pytest.approx(
            3.2, abs=0.01
        ), f"Expected stacked mag 3.2, got {total_mag}"
        assert total_mag > 3.0, "Stacked magnitude should exceed boss protection"

    def test_immobilize_with_mez_resistance(self):
        """
        Test Case 3: Immobilize with Mez Resistance

        Scenario: Controller Immobilize vs target with 50% immobilize resistance
        Expected: Applies, but duration reduced to 5.0 seconds
        """
        # Setup
        immob = MezEffect(
            mez_type=MezType.IMMOBILIZED,
            magnitude=3.0,
            duration=10.0,
            scale=1.0,
            stacks=False,
        )

        target_protection = MezProtection(immobilized=1.0)
        target_resistance = MezResistance(immobilized=0.5)  # 50% resistance

        # Test magnitude check
        applies = self.calculator.applies(
            mez=immob,
            protection=target_protection,
            at_scale=1.0,
            modifier_table_scale=1.0,
            caster_level=50,
            target_level=50,
        )

        assert applies is True, "Mag 3 should overcome Mag 1 protection"

        # Test duration with resistance
        duration = self.calculator.calculate_duration(
            mez=immob,
            resistance=target_resistance,
            at_duration_scale=1.0,
            duration_enhancement=0.0,  # No enhancements
            caster_level=50,
            target_level=50,
        )

        assert duration == pytest.approx(
            5.0, abs=0.1
        ), f"Expected 5.0s (50% reduction), got {duration}"

    def test_purple_patch_hold_vs_plus3_boss(self):
        """
        Test Case 4: Purple Patch - Hold vs +3 Level Boss

        Scenario: Level 50 Controller Hold vs level 53 boss (+3 levels)
        Expected: Fails due to purple patch reducing magnitude below protection
        """
        # Setup
        hold = MezEffect(
            mez_type=MezType.HELD, magnitude=3.0, duration=8.0, scale=1.0, stacks=True
        )

        boss_protection = MezProtection(held=3.0)

        # Test vs +3 boss
        applies = self.calculator.applies(
            mez=hold,
            protection=boss_protection,
            at_scale=1.0,
            modifier_table_scale=1.0,
            caster_level=50,
            target_level=53,  # +3 levels
        )

        assert (
            applies is False
        ), "Purple patch should reduce mag 3.0 * 0.70 = 2.1, which fails vs mag 3.0"

    def test_magnitude_stacking_breakpoint_boss(self):
        """
        Test Case 5: Magnitude Stacking Breakpoint (Boss)

        Scenario: Two controllers stack holds to break boss protection
        Expected: First mag 3.0 fails (tie), stacked mag 6.0 succeeds
        """
        # Setup
        hold = MezEffect(
            mez_type=MezType.HELD, magnitude=3.0, duration=8.0, scale=1.0, stacks=True
        )

        boss_protection = MezProtection(held=3.0)

        # First application - should fail (magnitude must be GREATER THAN)
        applies_first = self.calculator.applies(
            mez=hold,
            protection=boss_protection,
            at_scale=1.0,
            modifier_table_scale=1.0,
            caster_level=50,
            target_level=50,
        )

        assert (
            applies_first is False
        ), "Mag 3.0 should NOT overcome Mag 3.0 (ties don't break through)"

        # Stack two holds
        stacked = self.calculator.stack_magnitude(
            mezzes=[hold, hold], at_scale=1.0, modifier_table_scale=1.0
        )

        total_mag = stacked[MezType.HELD]
        assert total_mag == pytest.approx(
            6.0, abs=0.01
        ), f"Expected stacked mag 6.0, got {total_mag}"

        # Check breakpoint
        breaks_through = self.calculator.check_breakpoint(
            total_magnitude=total_mag, target_rank="boss", mez_type=MezType.HELD
        )

        assert (
            breaks_through is True
        ), "Mag 6.0 should break through boss protection (3.0)"

    def test_knockback_distance_calculation(self):
        """
        Test Case 6: Knockback Distance Calculation

        Scenario: Energy Blast knockback vs target with KB protection
        Expected: Different effects based on protection level
        """
        kb_calc = KnockbackCalculator()

        # Test 1: Full knockback (protection 4.0, magnitude 5.84)
        effect_type, distance = kb_calc.calculate_knockback_distance(
            magnitude=5.84, kb_protection=4.0
        )

        assert effect_type == "knockback", "Should be full knockback"
        assert distance > 0, "Distance should be positive"
        assert distance == pytest.approx(
            18.4, abs=1.0
        ), f"Expected ~18.4 feet, got {distance}"

        # Test 2: Knockdown (protection 5.5, magnitude 5.84)
        effect_type2, distance2 = kb_calc.calculate_knockback_distance(
            magnitude=5.84, kb_protection=5.5
        )

        assert effect_type2 == "knockdown", "Should be knockdown"
        assert distance2 == 0.0, "Knockdown has no distance"

        # Test 3: No effect (protection exceeds magnitude)
        effect_type3, distance3 = kb_calc.calculate_knockback_distance(
            magnitude=5.84, kb_protection=6.0
        )

        assert effect_type3 == "none", "Should be no effect"
        assert distance3 == 0.0, "No knockback distance"

    def test_duration_enhanceable_mezzes(self):
        """Test that only certain mez types are duration-enhanceable"""
        # Duration-enhanceable mezzes
        enhanceable = [
            MezType.CONFUSED,
            MezType.HELD,
            MezType.IMMOBILIZED,
            MezType.PLACATE,
            MezType.SLEEP,
            MezType.STUNNED,
            MezType.TAUNT,
            MezType.TERRORIZED,
            MezType.UNTOUCHABLE,
        ]

        for mez_type in enhanceable:
            effect = MezEffect(mez_type=mez_type, magnitude=1.0)
            assert (
                effect.is_duration_enhanceable() is True
            ), f"{mez_type} should be duration-enhanceable"

        # NOT duration-enhanceable
        not_enhanceable = [
            MezType.KNOCKBACK,
            MezType.KNOCKUP,
            MezType.REPEL,
            MezType.TOGGLE_DROP,
        ]

        for mez_type in not_enhanceable:
            effect = MezEffect(mez_type=mez_type, magnitude=1.0)
            assert (
                effect.is_duration_enhanceable() is False
            ), f"{mez_type} should NOT be duration-enhanceable"

    def test_av_mez_immunity(self):
        """Test that AVs are effectively immune to standard mezzes"""
        hold = MezEffect(
            mez_type=MezType.HELD, magnitude=3.0, duration=8.0, scale=1.0, stacks=True
        )

        # Check vs AV protection
        breaks_through = self.calculator.check_breakpoint(
            total_magnitude=3.0, target_rank="av", mez_type=MezType.HELD
        )

        assert breaks_through is False, "Mag 3 should NOT break AV protection (50.0)"

        # Calculate required magnitude
        required_mag = 51.0  # Just over 50.0
        breaks_through_stacked = self.calculator.check_breakpoint(
            total_magnitude=required_mag, target_rank="av", mez_type=MezType.HELD
        )

        assert (
            breaks_through_stacked is True
        ), f"Mag {required_mag} should break AV protection"

    def test_standard_protection_values(self):
        """Test standard NPC protection values"""
        # Minion: Mag 1
        assert self.calculator.check_breakpoint(
            1.1, "minion", MezType.HELD
        ), "Mag 1.1 should break minion"
        assert not self.calculator.check_breakpoint(
            1.0, "minion", MezType.HELD
        ), "Mag 1.0 should NOT break minion (tie)"

        # Lieutenant: Mag 2
        assert self.calculator.check_breakpoint(
            2.1, "lieutenant", MezType.HELD
        ), "Mag 2.1 should break lieutenant"
        assert not self.calculator.check_breakpoint(
            2.0, "lieutenant", MezType.HELD
        ), "Mag 2.0 should NOT break lieutenant (tie)"

        # Boss: Mag 3
        assert self.calculator.check_breakpoint(
            3.1, "boss", MezType.HELD
        ), "Mag 3.1 should break boss"
        assert not self.calculator.check_breakpoint(
            3.0, "boss", MezType.HELD
        ), "Mag 3.0 should NOT break boss (tie)"

        # Elite Boss: Mag 6
        assert self.calculator.check_breakpoint(
            6.1, "elite_boss", MezType.HELD
        ), "Mag 6.1 should break elite boss"
        assert not self.calculator.check_breakpoint(
            6.0, "elite_boss", MezType.HELD
        ), "Mag 6.0 should NOT break elite boss (tie)"

    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        hold = MezEffect(mez_type=MezType.HELD, magnitude=3.0)
        protection = MezProtection(held=1.0)
        resistance = MezResistance(held=0.0)

        # Test negative AT scale
        with pytest.raises(ValueError):
            self.calculator.applies(
                mez=hold, protection=protection, at_scale=-1.0  # Invalid
            )

        # Test invalid resistance value
        with pytest.raises(ValueError):
            self.calculator.calculate_duration(
                mez=hold,
                resistance=MezResistance(held=1.5),  # Invalid (> 1.0)
                at_duration_scale=1.0,
            )

        # Test negative duration enhancement
        with pytest.raises(ValueError):
            self.calculator.calculate_duration(
                mez=hold,
                resistance=resistance,
                at_duration_scale=1.0,
                duration_enhancement=-0.5,  # Invalid
            )

        # Test unknown target rank
        with pytest.raises(ValueError):
            self.calculator.check_breakpoint(
                total_magnitude=5.0, target_rank="unknown", mez_type=MezType.HELD
            )

    def test_purple_patch_calculations(self):
        """Test purple patch modifier calculations"""
        # Same level: 1.0
        assert (
            self.calculator._calculate_purple_patch(0) == 1.0
        ), "Same level should have 1.0 modifier"

        # +1 level: ~0.90
        assert self.calculator._calculate_purple_patch(1) == pytest.approx(
            0.9, abs=0.01
        )

        # +3 levels: ~0.70
        assert self.calculator._calculate_purple_patch(3) == pytest.approx(
            0.7, abs=0.01
        )

        # +5 levels: 0.5
        assert self.calculator._calculate_purple_patch(5) == pytest.approx(
            0.5, abs=0.01
        )

        # +6 levels: 0.48 (minimum)
        assert (
            self.calculator._calculate_purple_patch(6) == 0.48
        ), "Should hit minimum at +6"

        # -1 level: ~1.10
        assert self.calculator._calculate_purple_patch(-1) == pytest.approx(
            1.1, abs=0.01
        )

        # -3 levels: ~1.30
        assert self.calculator._calculate_purple_patch(-3) == pytest.approx(
            1.3, abs=0.01
        )

        # -5 levels: 1.5 (maximum)
        assert (
            self.calculator._calculate_purple_patch(-5) == 1.5
        ), "Should hit maximum at -5"


class TestKnockbackCalculator:
    """Test KnockbackCalculator class"""

    def setup_method(self):
        """Setup calculator instance for each test"""
        self.calculator = KnockbackCalculator()

    def test_knockback_to_knockdown_conversion(self):
        """Test knockback to knockdown conversion logic"""
        # Test knockdown with partial protection
        is_kd = self.calculator.is_knockdown(kb_magnitude=5.0, kb_protection=4.5)
        assert is_kd is True, "Partial protection should create knockdown"

        # Test full knockback
        is_kd2 = self.calculator.is_knockdown(kb_magnitude=5.0, kb_protection=2.0)
        assert is_kd2 is False, "Low protection should allow full knockback"

        # Test negative protection (knockdown enhancement)
        is_kd3 = self.calculator.is_knockdown(kb_magnitude=5.0, kb_protection=-1.0)
        assert is_kd3 is True, "Negative protection should force knockdown"
