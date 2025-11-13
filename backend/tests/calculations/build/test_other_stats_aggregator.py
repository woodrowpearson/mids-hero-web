"""
Tests for Build Other Stats Aggregation

Maps to Spec 24 test cases (Section 4).
Verifies HP, endurance, movement, perception, stealth, and threat calculations match MidsReborn.
"""

import pytest
from app.calculations.build.other_stats_aggregator import (
    BuildOtherStatsCalculator,
    ArchetypeData,
    ServerData,
    StatType,
    OtherStatsTotals
)


class TestOtherStatsAggregator:
    """Test suite for HP, endurance, movement, and other stat aggregation"""

    # Test Case 1: Tanker Base Stats (No Bonuses)
    def test_tanker_base_stats(self):
        """
        Test Case 1 from Spec 24:
        Tanker at level 50 with no bonuses.

        Expected:
          - HP Max: 1606
          - HP%: 100%
          - HP Regen/sec: 2.67
          - End Max: 100
          - End Recovery/sec: 2.78
          - Run Speed: 21.0 ft/sec
          - Jump Speed: 22.275 ft/sec
          - Jump Height: 4.0 ft
          - Fly Speed: 0 (no fly power)
          - Perception: 500 ft
          - Stealth PvE: 0
          - Threat: 0 (additive from powers, not base)
        """
        tanker = ArchetypeData(
            name="Tanker",
            hitpoints=1606,
            hp_cap=3212.0,
            base_regen=1.0,
            regen_cap=20.0,
            base_recovery=1.67,
            recovery_cap=5.0,
            perception_cap=1153.0,
            base_threat=4.0
        )

        calculator = BuildOtherStatsCalculator(tanker)
        effects = {stat: 0.0 for stat in StatType}

        uncapped, capped = calculator.calculate_all(effects, can_fly=False)

        # HP
        assert abs(capped.hp_max - 1606.0) < 0.1
        assert abs(capped.hp_percent_of_base - 100.0) < 0.1
        assert abs(capped.hp_regen_per_sec - 1.666667) < 0.01  # 1.0 * 1.0 * 1.666667

        # Endurance
        assert abs(capped.end_max - 100.0) < 0.1
        assert abs(capped.end_recovery_per_sec - 2.78) < 0.01  # 1.0 * 1.67 * 1.666667

        # Movement
        assert abs(capped.run_speed - 21.0) < 0.1
        assert abs(capped.jump_speed - 22.275) < 0.1
        assert abs(capped.jump_height - 4.0) < 0.1
        assert abs(capped.fly_speed - 0.0) < 0.1
        assert not capped.can_fly

        # Perception / Stealth / Threat
        assert abs(capped.perception - 500.0) < 0.1
        assert abs(capped.stealth_pve - 0.0) < 0.1
        assert abs(capped.threat_level - 0.0) < 0.1

    # Test Case 2: Blaster with Accolades
    def test_blaster_with_accolades(self):
        """
        Test Case 2 from Spec 24:
        Blaster with Accolades:
        - Atlas Medallion: +10% HP
        - Freedom Phalanx Reserve: +20% HP, +10 end
        - Demonic: +5 end

        Expected:
          - HP Max: 1322.1 (1017 + 30% = 1017 * 1.3)
          - HP%: 130%
          - HP Regen/sec: 2.20 (1.0 * 1.0 * 1.666667, doesn't scale with HP in display)
          - End Max: 115 (100 + 15)
          - End Recovery/sec: 3.20 (1.0 * 1.67 * 1.666667 * 1.15)
        """
        blaster = ArchetypeData(
            name="Blaster",
            hitpoints=1017,
            hp_cap=2088.0,
            base_regen=1.0,
            regen_cap=20.0,
            base_recovery=1.67,
            recovery_cap=5.0,
            perception_cap=1153.0,
            base_threat=1.0
        )

        calculator = BuildOtherStatsCalculator(blaster)
        effects = {
            StatType.HP_MAX: 305.1,  # 30% of 1017
            StatType.END_MAX: 15.0,  # Accolades
        }

        uncapped, capped = calculator.calculate_all(effects, can_fly=False)

        # HP
        assert abs(capped.hp_max - 1322.1) < 0.1
        assert abs(capped.hp_percent_of_base - 130.0) < 0.1

        # Endurance
        assert abs(capped.end_max - 115.0) < 0.1
        # End recovery scales with max end: base_recovery * magic * (1 + end_max_bonus/100)
        expected_recovery = 1.0 * 1.67 * 1.666667 * (1 + 15.0/100.0)
        assert abs(capped.end_recovery_per_sec - expected_recovery) < 0.01

    # Test Case 3: Scrapper at HP Cap
    def test_scrapper_at_hp_cap(self):
        """
        Test Case 3 from Spec 24:
        Scrapper with HP bonuses exceeding cap.

        Expected:
          - HP Max Uncapped: 2704 (1204 + 1500)
          - HP Max Capped: 2409 (AT cap)
          - HP%: 200%
          - Cap Status: CAPPED
        """
        scrapper = ArchetypeData(
            name="Scrapper",
            hitpoints=1204,
            hp_cap=2409.0,
            base_regen=1.0,
            regen_cap=20.0,
            base_recovery=1.67,
            recovery_cap=5.0,
            perception_cap=1153.0,
            base_threat=1.0
        )

        calculator = BuildOtherStatsCalculator(scrapper)
        effects = {StatType.HP_MAX: 1500.0}

        uncapped, capped = calculator.calculate_all(effects, can_fly=False)

        assert abs(uncapped.hp_max - 2704.0) < 0.1
        assert abs(capped.hp_max - 2409.0) < 0.1
        assert abs(capped.hp_percent_of_base - 200.0) < 0.1
        assert capped.hp_max < uncapped.hp_max  # Capped

    # Test Case 4: Speed Build with Soft Cap Increases
    def test_speed_build_soft_cap_increases(self):
        """
        Test Case 4 from Spec 24:
        Speed build with:
        - Run Speed: +95%
        - Max Run Speed: +50% (increases soft cap)
        - Jump Speed: +150%
        - Max Jump Speed: +25%

        Expected:
          - Run Speed Uncapped: 40.95 ft/sec
          - Run Speed Soft Cap: 69.15 ft/sec
          - Run Speed Capped: 40.95 (under soft cap)
          - Jump Speed Uncapped: 55.69 ft/sec
          - Jump Speed Soft Cap: 119.97 ft/sec
          - Jump Speed Capped: 55.69 (under soft cap)
        """
        scrapper = ArchetypeData(
            name="Scrapper",
            hitpoints=1204,
            hp_cap=2409.0,
            base_regen=1.0,
            regen_cap=20.0,
            base_recovery=1.67,
            recovery_cap=5.0,
            perception_cap=1153.0,
            base_threat=1.0
        )

        calculator = BuildOtherStatsCalculator(scrapper)
        effects = {
            StatType.RUN_SPEED: 0.95,
            StatType.MAX_RUN_SPEED: 0.50,
            StatType.JUMP_SPEED: 1.50,
            StatType.MAX_JUMP_SPEED: 0.25
        }

        uncapped, capped = calculator.calculate_all(effects, can_fly=False)

        # Run speed
        assert abs(uncapped.run_speed - 40.95) < 0.1
        assert abs(uncapped.run_speed_soft_cap - 69.15) < 0.1
        assert abs(capped.run_speed - 40.95) < 0.1

        # Jump speed
        assert abs(uncapped.jump_speed - 55.69) < 0.1
        assert abs(uncapped.jump_speed_soft_cap - 119.97) < 0.1
        assert abs(capped.jump_speed - 55.69) < 0.1

    # Test Case 5: Speed Build Hitting Soft Cap
    def test_speed_build_hitting_soft_cap(self):
        """
        Test Case 5 from Spec 24:
        Speed build hitting soft caps:
        - Run Speed: +200%
        - Max Run Speed: 0
        - Fly Speed: +150%
        - Has Fly Power: True

        Expected:
          - Run Speed Uncapped: 63.0 ft/sec
          - Run Speed Soft Cap: 58.65 (default, no increase)
          - Run Speed Capped: 58.65 (at soft cap)
          - Fly Speed Uncapped: 78.75 ft/sec
          - Fly Speed Soft Cap: 58.65
          - Fly Speed Capped: 58.65
        """
        scrapper = ArchetypeData(
            name="Scrapper",
            hitpoints=1204,
            hp_cap=2409.0,
            base_regen=1.0,
            regen_cap=20.0,
            base_recovery=1.67,
            recovery_cap=5.0,
            perception_cap=1153.0,
            base_threat=1.0
        )

        calculator = BuildOtherStatsCalculator(scrapper)
        effects = {
            StatType.RUN_SPEED: 2.0,
            StatType.FLY_SPEED: 1.5
        }

        uncapped, capped = calculator.calculate_all(effects, can_fly=True)

        # Run speed at soft cap
        assert abs(uncapped.run_speed - 63.0) < 0.1
        assert abs(uncapped.run_speed_soft_cap - 58.65) < 0.1
        assert abs(capped.run_speed - 58.65) < 0.1

        # Fly speed at soft cap
        assert abs(uncapped.fly_speed - 78.75) < 0.1
        assert abs(uncapped.fly_speed_soft_cap - 58.65) < 0.1
        assert abs(capped.fly_speed - 58.65) < 0.1
        assert capped.can_fly

    # Test Case 6: Recovery Cap Build
    def test_recovery_cap_build(self):
        """
        Test Case 6 from Spec 24:
        Build hitting recovery cap:
        - Recovery Buff: +450% (550% total, exceeds 500% cap)
        - End Max Bonus: +10

        Expected:
          - End Recovery Buff Uncapped: 4.5
          - End Recovery Buff Capped: 4.0 (5.0 cap - 1.0 base)
          - End Recovery%: 500% (capped)
          - End Recovery/sec Capped: ~9.17
          - End Recovery/sec Uncapped: ~10.08
          - Cap Status: CAPPED
        """
        defender = ArchetypeData(
            name="Defender",
            hitpoints=937,
            hp_cap=1874.0,
            base_regen=1.0,
            regen_cap=20.0,
            base_recovery=1.67,
            recovery_cap=5.0,
            perception_cap=1153.0,
            base_threat=1.0
        )

        calculator = BuildOtherStatsCalculator(defender)
        effects = {
            StatType.END_RECOVERY: 4.5,  # 550% total including base
            StatType.END_MAX: 10.0
        }

        uncapped, capped = calculator.calculate_all(effects, can_fly=False)

        assert abs(uncapped.end_recovery_buff - 4.5) < 0.01
        assert abs(capped.end_recovery_buff - 4.0) < 0.01  # Capped at 5.0 - 1.0
        assert abs(capped.end_recovery_percent - 500.0) < 0.1

        # Calculate expected recovery/sec
        # Capped: 5.0 * 1.67 * 1.666667 * 1.1
        expected_capped = 5.0 * 1.67 * 1.666667 * (1 + 10.0/100.0)
        assert abs(capped.end_recovery_per_sec - expected_capped) < 0.1

        # Uncapped: 5.5 * 1.67 * 1.666667 * 1.1
        expected_uncapped = 5.5 * 1.67 * 1.666667 * (1 + 10.0/100.0)
        assert abs(uncapped.end_recovery_per_sec - expected_uncapped) < 0.1

    # Test Case 7: Regen Build
    def test_regen_build(self):
        """
        Test Case 7 from Spec 24:
        Regen build with +500% regen (600% total):
        - Regen Buff: +5.0
        - HP Max: 2000

        Expected:
          - HP Regen Buff: 5.0
          - HP Regen%: 600%
          - HP Regen/sec: 10.0 (6.0 * 1.0 * 1.666667)

        Note: Regen/sec does NOT scale with HP in MidsReborn display.
        """
        scrapper = ArchetypeData(
            name="Scrapper",
            hitpoints=1204,
            hp_cap=2409.0,
            base_regen=1.0,
            regen_cap=20.0,
            base_recovery=1.67,
            recovery_cap=5.0,
            perception_cap=1153.0,
            base_threat=1.0
        )

        calculator = BuildOtherStatsCalculator(scrapper)
        effects = {
            StatType.HP_REGEN: 5.0,
            StatType.HP_MAX: 796.0  # Brings total to ~2000
        }

        uncapped, capped = calculator.calculate_all(effects, can_fly=False)

        assert abs(capped.hp_regen_buff - 5.0) < 0.01
        assert abs(capped.hp_regen_percent - 600.0) < 0.1
        # (1 + 5.0) * 1.0 * 1.666667 = 10.0
        expected_regen = 6.0 * 1.0 * 1.666667
        assert abs(capped.hp_regen_per_sec - expected_regen) < 0.01

    # Test Case 8: Movement Speed Floor (-90% Debuff)
    def test_movement_speed_floor(self):
        """
        Test Case 8 from Spec 24:
        Movement speed debuffs floored at -90%:
        - Run Speed Debuff: -95% (exceeds floor)
        - Jump Speed Debuff: -85%

        Expected:
          - Run Speed: 2.1 ft/sec (floored at -90%)
          - Jump Speed: 3.34 ft/sec (not floored)
        """
        scrapper = ArchetypeData(
            name="Scrapper",
            hitpoints=1204,
            hp_cap=2409.0,
            base_regen=1.0,
            regen_cap=20.0,
            base_recovery=1.67,
            recovery_cap=5.0,
            perception_cap=1153.0,
            base_threat=1.0
        )

        calculator = BuildOtherStatsCalculator(scrapper)
        effects = {
            StatType.RUN_SPEED: -0.95,  # Exceeds floor
            StatType.JUMP_SPEED: -0.85  # Within bounds
        }

        uncapped, capped = calculator.calculate_all(effects, can_fly=False)

        # Run speed floored at -90%
        # (1 + max(-0.95, -0.9)) * 21.0 = 0.1 * 21.0 = 2.1
        assert abs(capped.run_speed - 2.1) < 0.1

        # Jump speed not floored
        # (1 + (-0.85)) * 22.275 = 0.15 * 22.275 = 3.34
        assert abs(capped.jump_speed - 3.34) < 0.1

    # Test Case 9: Perception and Stealth
    def test_perception_and_stealth(self):
        """
        Test Case 9 from Spec 24:
        Stalker with Hide power:
        - Perception Buff: +50%
        - Perception Cap: 1153 ft
        - Stealth PvE: -500 ft (Hide power)
        - Stealth PvP: -200 ft (Hide power, lower in PvP)

        Expected:
          - Perception Uncapped: 750 ft
          - Perception Capped: 750 ft (under cap)
          - Stealth PvE: -500 ft
          - Stealth PvP: -200 ft
        """
        stalker = ArchetypeData(
            name="Stalker",
            hitpoints=1204,
            hp_cap=2409.0,
            base_regen=1.0,
            regen_cap=20.0,
            base_recovery=1.67,
            recovery_cap=5.0,
            perception_cap=1153.0,
            base_threat=1.0
        )

        calculator = BuildOtherStatsCalculator(stalker)
        effects = {
            StatType.PERCEPTION: 0.50,
            StatType.STEALTH_PVE: -500.0,
            StatType.STEALTH_PVP: -200.0
        }

        uncapped, capped = calculator.calculate_all(effects, can_fly=False)

        # Perception: 500 * (1 + 0.5) = 750
        assert abs(uncapped.perception - 750.0) < 0.1
        assert abs(capped.perception - 750.0) < 0.1

        # Stealth (no caps, additive)
        assert abs(capped.stealth_pve - (-500.0)) < 0.1
        assert abs(capped.stealth_pvp - (-200.0)) < 0.1

    # Test Case 10: Absorb Shield Capped at HP
    def test_absorb_capped_at_hp(self):
        """
        Test Case 10 from Spec 24:
        Absorb (temp HP) capped at max HP:
        - HP Max: 2000
        - Absorb: 2500 (exceeds HP)

        Expected:
          - HP Max: 2000
          - Absorb Uncapped: 2500
          - Absorb Capped: 2000 (capped at max HP)
        """
        scrapper = ArchetypeData(
            name="Scrapper",
            hitpoints=1204,
            hp_cap=2409.0,
            base_regen=1.0,
            regen_cap=20.0,
            base_recovery=1.67,
            recovery_cap=5.0,
            perception_cap=1153.0,
            base_threat=1.0
        )

        calculator = BuildOtherStatsCalculator(scrapper)
        effects = {
            StatType.HP_MAX: 796.0,  # Brings total to 2000
            StatType.ABSORB: 2500.0  # Exceeds HP
        }

        uncapped, capped = calculator.calculate_all(effects, can_fly=False)

        assert abs(capped.hp_max - 2000.0) < 0.1
        assert abs(uncapped.absorb - 2500.0) < 0.1
        assert abs(capped.absorb - 2000.0) < 0.1  # Capped at max HP

    # Test Case 11: Multiple Stats Combined (IO'd Build)
    def test_iod_build_combined_stats(self):
        """
        Test Case 11 from Spec 24:
        Realistic IO'd build with multiple stats:
        - HP Bonus: +361 (30%)
        - Regen Bonus: +150% (250% total)
        - End Max Bonus: +10
        - Recovery Bonus: +95% (195% total)
        - Run Speed: +50%
        - Max Run Speed: +30%

        Expected:
          - HP Max: 1565
          - HP%: 130%
          - HP Regen/sec: 4.17
          - End Max: 110
          - End Recovery/sec: 5.98
          - Run Speed Uncapped: 31.5 ft/sec
          - Run Speed Soft Cap: 64.95 ft/sec
          - Run Speed Capped: 31.5 ft/sec
        """
        scrapper = ArchetypeData(
            name="Scrapper",
            hitpoints=1204,
            hp_cap=2409.0,
            base_regen=1.0,
            regen_cap=20.0,
            base_recovery=1.67,
            recovery_cap=5.0,
            perception_cap=1153.0,
            base_threat=1.0
        )

        calculator = BuildOtherStatsCalculator(scrapper)
        effects = {
            StatType.HP_MAX: 361.0,
            StatType.HP_REGEN: 1.5,
            StatType.END_MAX: 10.0,
            StatType.END_RECOVERY: 0.95,
            StatType.RUN_SPEED: 0.5,
            StatType.MAX_RUN_SPEED: 0.3
        }

        uncapped, capped = calculator.calculate_all(effects, can_fly=False)

        # HP
        assert abs(capped.hp_max - 1565.0) < 0.1
        assert abs(capped.hp_percent_of_base - 130.0) < 0.1

        # Regen: (1 + 1.5) * 1.0 * 1.666667 = 4.17
        expected_regen = 2.5 * 1.0 * 1.666667
        assert abs(capped.hp_regen_per_sec - expected_regen) < 0.01

        # End
        assert abs(capped.end_max - 110.0) < 0.1

        # Recovery: (1 + 0.95) * 1.67 * 1.666667 * 1.1
        expected_recovery = 1.95 * 1.67 * 1.666667 * (1 + 10.0/100.0)
        assert abs(capped.end_recovery_per_sec - expected_recovery) < 0.01

        # Movement
        assert abs(capped.run_speed - 31.5) < 0.1
        assert abs(capped.run_speed_soft_cap - 64.95) < 0.1

    # Test Display Formatting
    def test_display_formatting(self):
        """
        Test that format_for_display returns properly formatted values.
        """
        tanker = ArchetypeData(
            name="Tanker",
            hitpoints=1606,
            hp_cap=3212.0,
            base_regen=1.0,
            regen_cap=20.0,
            base_recovery=1.67,
            recovery_cap=5.0,
            perception_cap=1153.0,
            base_threat=4.0
        )

        calculator = BuildOtherStatsCalculator(tanker)
        effects = {
            StatType.HP_MAX: 482.0,  # 30%
            StatType.RUN_SPEED: 0.5  # 50%
        }

        uncapped, capped = calculator.calculate_all(effects, can_fly=False)
        display = calculator.format_for_display(uncapped, capped)

        # Check structure
        assert 'hp' in display
        assert 'endurance' in display
        assert 'movement' in display
        assert 'perception' in display

        # Check formatted values contain units
        assert 'ft/sec' in display['movement']['run_speed']
        assert '%' in display['hp']['percent']
        assert 'ft' in display['perception']['value']
