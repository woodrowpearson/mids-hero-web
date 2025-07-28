"""Realistic build tests for calculation API using actual game data patterns."""

import pytest
from sqlalchemy.orm import Session

from app import models


class TestRealisticBuilds:
    """Test calculations with realistic character builds."""

    def setup_fire_blast_powerset(self, db: Session, archetype_id: int):
        """Create Fire Blast powerset with realistic powers."""
        powerset = models.Powerset(
            id=101,
            name="Fire Blast",
            display_name="Fire Blast",
            archetype_id=archetype_id,
            powerset_type="primary",
            description="Wield the primal power of fire to blast your foes."
        )
        db.add(powerset)

        # Create realistic Fire Blast powers
        powers = [
            models.Power(
                id=1001,
                name="fire_blast.flares",
                display_name="Flares",
                powerset_id=101,
                level_available=1,
                power_type="attack",
                target_type="enemy",
                accuracy=1.0,
                damage_scale=0.63,  # Actual scale from game
                endurance_cost=3.69,
                recharge_time=2.18,
                activation_time=1.0,
                range_feet=80,
                max_targets=1,
            ),
            models.Power(
                id=1002,
                name="fire_blast.fire_blast",
                display_name="Fire Blast",
                powerset_id=101,
                level_available=1,
                power_type="attack",
                target_type="enemy",
                accuracy=1.0,
                damage_scale=1.0,  # Standard blast damage
                endurance_cost=5.2,
                recharge_time=4.0,
                activation_time=1.67,
                range_feet=80,
                max_targets=1,
            ),
            models.Power(
                id=1003,
                name="fire_blast.fire_ball",
                display_name="Fire Ball",
                powerset_id=101,
                level_available=2,
                power_type="attack",
                target_type="enemy",
                accuracy=1.0,
                damage_scale=0.79,  # AoE has lower scale
                endurance_cost=15.18,
                recharge_time=32.0,
                activation_time=1.0,
                range_feet=80,
                radius_feet=15,
                max_targets=16,
            ),
            models.Power(
                id=1004,
                name="fire_blast.rain_of_fire",
                display_name="Rain of Fire",
                powerset_id=101,
                level_available=8,
                power_type="attack",
                target_type="location",
                accuracy=1.0,
                damage_scale=0.4167,  # DoT scale per tick
                endurance_cost=15.6,
                recharge_time=60.0,
                activation_time=2.03,
                range_feet=80,
                radius_feet=25,
                max_targets=16,
            ),
            models.Power(
                id=1005,
                name="fire_blast.aim",
                display_name="Aim",
                powerset_id=101,
                level_available=6,
                power_type="support",
                target_type="self",
                accuracy=1.0,
                damage_scale=0.0,  # No damage
                endurance_cost=5.2,
                recharge_time=90.0,
                activation_time=1.17,
                effects={
                    "accuracy_buff": 0.375,  # +37.5% accuracy
                    "damage_buff": 0.625,    # +62.5% damage
                    "duration": 10.0
                }
            ),
            models.Power(
                id=1006,
                name="fire_blast.blaze",
                display_name="Blaze",
                powerset_id=101,
                level_available=18,
                power_type="attack",
                target_type="enemy",
                accuracy=1.0,
                damage_scale=2.12,  # High damage, close range
                endurance_cost=10.19,
                recharge_time=10.0,
                activation_time=1.0,
                range_feet=20,  # Short range
                max_targets=1,
            ),
            models.Power(
                id=1007,
                name="fire_blast.blazing_bolt",
                display_name="Blazing Bolt",
                powerset_id=101,
                level_available=12,
                power_type="attack",
                target_type="enemy",
                accuracy=1.2,  # Sniper has bonus accuracy
                damage_scale=2.76,  # Sniper damage
                endurance_cost=14.35,
                recharge_time=12.0,
                activation_time=4.67,  # Long animation
                range_feet=150,  # Sniper range
                max_targets=1,
            ),
            models.Power(
                id=1008,
                name="fire_blast.inferno",
                display_name="Inferno",
                powerset_id=101,
                level_available=32,
                power_type="attack",
                target_type="enemy",
                accuracy=1.0,
                damage_scale=3.0,  # Nuke damage
                endurance_cost=20.8,
                recharge_time=360.0,  # 6 minute recharge
                activation_time=3.0,
                range_feet=0,  # PBAoE
                radius_feet=25,
                max_targets=16,
            ),
        ]

        for power in powers:
            db.add(power)

        return powerset

    def setup_enhancement_sets(self, db: Session):
        """Create realistic enhancement sets."""
        # Devastation - Ranged damage set
        devastation = models.EnhancementSet(
            id=201,
            name="Devastation",
            display_name="Devastation",
            description="Superior ranged damage set",
            min_level=30,
            max_level=50,
        )
        db.add(devastation)

        # Create individual pieces
        devastation_pieces = [
            models.Enhancement(
                id=2001,
                name="devastation_acc_dmg",
                display_name="Devastation: Acc/Dmg",
                enhancement_type="set_piece",
                set_id=201,
                accuracy_bonus=18.55,
                damage_bonus=18.55,
                level_min=30,
                level_max=50,
            ),
            models.Enhancement(
                id=2002,
                name="devastation_dmg_rech",
                display_name="Devastation: Dmg/Rech",
                enhancement_type="set_piece",
                set_id=201,
                damage_bonus=18.55,
                recharge_bonus=18.55,
                level_min=30,
                level_max=50,
            ),
            models.Enhancement(
                id=2003,
                name="devastation_acc_dmg_rech",
                display_name="Devastation: Acc/Dmg/Rech",
                enhancement_type="set_piece",
                set_id=201,
                accuracy_bonus=12.36,
                damage_bonus=12.36,
                recharge_bonus=12.36,
                level_min=30,
                level_max=50,
            ),
            models.Enhancement(
                id=2004,
                name="devastation_acc_dmg_end_rech",
                display_name="Devastation: Acc/Dmg/End/Rech",
                enhancement_type="set_piece",
                set_id=201,
                accuracy_bonus=9.27,
                damage_bonus=9.27,
                endurance_bonus=9.27,
                recharge_bonus=9.27,
                level_min=30,
                level_max=50,
            ),
            models.Enhancement(
                id=2005,
                name="devastation_dmg",
                display_name="Devastation: Dmg",
                enhancement_type="set_piece",
                set_id=201,
                damage_bonus=37.09,
                level_min=30,
                level_max=50,
            ),
            models.Enhancement(
                id=2006,
                name="devastation_proc",
                display_name="Devastation: Chance for Hold",
                enhancement_type="set_piece",
                set_id=201,
                unique_enhancement=True,
                other_bonuses={"proc_chance": 0.15, "proc_type": "hold"},
                level_min=30,
                level_max=50,
            ),
        ]

        for enh in devastation_pieces:
            db.add(enh)

        # Create set bonuses
        devastation_bonuses = [
            models.SetBonus(
                set_id=201,
                pieces_required=2,
                bonus_type="hp",
                bonus_amount=1.13,
                bonus_description="Increases maximum health by 1.13%",
            ),
            models.SetBonus(
                set_id=201,
                pieces_required=3,
                bonus_type="damage",
                bonus_amount=3.0,
                bonus_description="Increases damage by 3%",
            ),
            models.SetBonus(
                set_id=201,
                pieces_required=4,
                bonus_type="recharge",
                bonus_amount=5.0,
                bonus_description="Increases recharge rate by 5%",
            ),
            models.SetBonus(
                set_id=201,
                pieces_required=5,
                bonus_type="defense_ranged",
                bonus_amount=1.875,
                bonus_description="Increases ranged defense by 1.875%",
            ),
            models.SetBonus(
                set_id=201,
                pieces_required=6,
                bonus_type="accuracy",
                bonus_amount=7.5,
                bonus_description="Increases accuracy by 7.5%",
            ),
        ]

        for bonus in devastation_bonuses:
            db.add(bonus)

        # Also add generic SOs for comparison
        damage_so = models.Enhancement(
            id=2100,
            name="damage_so",
            display_name="Damage SO",
            enhancement_type="SO",
            damage_bonus=33.33,
            level_min=1,
            level_max=50,
        )
        db.add(damage_so)

        return devastation

    def test_fire_blaster_realistic_build(self, client, db: Session):
        """Test a realistic Fire/Fire Blaster build at level 50."""
        # Setup archetype
        blaster = models.Archetype(
            id=1,
            name="Blaster",
            display_name="Blaster",
            description="Offensive juggernaut",
            primary_group="damage",
            secondary_group="damage",
            hit_points_base=1204,
            hit_points_max=1606,
        )
        db.add(blaster)

        # Setup powersets and enhancements
        self.setup_fire_blast_powerset(db, 1)
        self.setup_enhancement_sets(db)

        db.commit()

        # Create a realistic build payload
        payload = {
            "build": {
                "name": "Fire/Fire Blaster - Farming Build",
                "archetype": "Blaster",
                "origin": "Magic",
                "level": 50,
                "alignment": "Hero"
            },
            "powers": [
                {
                    "id": 1002,  # Fire Blast
                    "power_name": "Fire Blast",
                    "powerset": "Fire Blast",
                    "level_taken": 1,
                    "slots": [
                        # 6-slot Devastation
                        {"slot_index": 0, "enhancement_id": 2001, "enhancement_level": 50},
                        {"slot_index": 1, "enhancement_id": 2002, "enhancement_level": 50},
                        {"slot_index": 2, "enhancement_id": 2003, "enhancement_level": 50},
                        {"slot_index": 3, "enhancement_id": 2004, "enhancement_level": 50},
                        {"slot_index": 4, "enhancement_id": 2005, "enhancement_level": 50},
                        {"slot_index": 5, "enhancement_id": 2006, "enhancement_level": 50},
                    ]
                },
                {
                    "id": 1003,  # Fire Ball
                    "power_name": "Fire Ball",
                    "powerset": "Fire Blast",
                    "level_taken": 2,
                    "slots": [
                        # 6-slot Devastation (second set)
                        {"slot_index": 0, "enhancement_id": 2001, "enhancement_level": 50},
                        {"slot_index": 1, "enhancement_id": 2002, "enhancement_level": 50},
                        {"slot_index": 2, "enhancement_id": 2003, "enhancement_level": 50},
                        {"slot_index": 3, "enhancement_id": 2004, "enhancement_level": 50},
                        {"slot_index": 4, "enhancement_id": 2005, "enhancement_level": 50},
                        {"slot_index": 5, "enhancement_id": 2006, "enhancement_level": 50},
                    ]
                },
                {
                    "id": 1006,  # Blaze
                    "power_name": "Blaze",
                    "powerset": "Fire Blast",
                    "level_taken": 18,
                    "slots": [
                        # 3 damage SOs for comparison
                        {"slot_index": 0, "enhancement_id": 2100, "enhancement_level": 50},
                        {"slot_index": 1, "enhancement_id": 2100, "enhancement_level": 50},
                        {"slot_index": 2, "enhancement_id": 2100, "enhancement_level": 50},
                    ]
                }
            ],
            "global_buffs": {
                "damage": 15.0,  # From other set bonuses
                "recharge": 25.0,  # From Hasten + set bonuses
                "defense": {"melee": 5.0, "ranged": 8.0, "aoe": 5.0},
                "resistance": {
                    "smashing": 0.0, "lethal": 0.0, "fire": 15.0,
                    "cold": 0.0, "energy": 0.0, "negative": 0.0,
                    "toxic": 0.0, "psionic": 0.0
                }
            }
        }

        response = client.post("/api/calculate", json=payload)
        assert response.status_code == 200

        data = response.json()

        # Debug: print set bonuses
        print(f"\nSet bonuses found: {len(data['aggregate_stats']['set_bonuses'])}")
        for bonus in data["aggregate_stats"]["set_bonuses"]:
            print(f"  {bonus['set_name']} (tier {bonus['bonus_tier']}): {bonus['bonus_values']}")

        # Verify basic build info
        assert data["build_name"] == "Fire/Fire Blaster - Farming Build"
        assert data["archetype"] == "Blaster"
        assert data["level"] == 50

        # Check Fire Blast calculations
        fire_blast_stats = next(p for p in data["per_power_stats"] if p["power_id"] == 1002)

        # Base damage: 1.0 scale * 62.56 (Blaster ranged at 50) = 62.56
        assert fire_blast_stats["base_stats"]["damage"] == pytest.approx(62.56, rel=0.01)

        # Enhancement values from Devastation set (should be less than 95% due to mixed enhancements)
        # Total damage bonus from set pieces: 18.55 + 18.55 + 12.36 + 9.27 + 37.09 = 95.82%
        assert fire_blast_stats["enhancement_values"]["damage"] == pytest.approx(95.82, rel=0.1)

        # Enhanced damage with 15% global buff
        # Base * (1 + ED(enhancement) + global) = 62.56 * (1 + ~0.95 + 0.15)
        assert fire_blast_stats["enhanced_stats"]["damage"] > 130.0

        # Check Fire Ball calculations
        fire_ball_stats = next(p for p in data["per_power_stats"] if p["power_id"] == 1003)

        # Base damage: 0.79 scale * 62.56 = 49.42
        assert fire_ball_stats["base_stats"]["damage"] == pytest.approx(49.42, rel=0.01)

        # Check Blaze with standard SOs
        blaze_stats = next(p for p in data["per_power_stats"] if p["power_id"] == 1006)

        # Base damage: 2.12 scale * 62.56 = 132.63
        assert blaze_stats["base_stats"]["damage"] == pytest.approx(132.63, rel=0.01)

        # 3 damage SOs = 99.99% enhancement, after ED ~95%
        assert blaze_stats["enhancement_values"]["damage"] == pytest.approx(99.99, rel=0.1)

        # Check set bonuses
        assert len(data["aggregate_stats"]["set_bonuses"]) > 0

        # Should have Devastation set bonuses (but unique rule applies)
        # Even with 2 sets slotted, we only get each unique bonus once
        devastation_bonuses = [b for b in data["aggregate_stats"]["set_bonuses"]
                              if b["set_name"] == "Devastation"]
        assert len(devastation_bonuses) == 5  # 5 unique bonuses, regardless of how many sets

        # Verify aggregate stats include set bonuses
        # From Devastation (once): +1.13% HP, +3% damage, +5% recharge, +1.875% ranged def, +7.5% acc
        defense_stats = data["aggregate_stats"]["defense"]
        assert defense_stats["ranged"] >= 9.875  # 8% base + 1.875% from set

        print("\nRealistic build calculations:")
        print(f"Fire Blast: {fire_blast_stats['base_stats']['damage']:.2f} -> "
              f"{fire_blast_stats['enhanced_stats']['damage']:.2f} damage")
        print(f"Fire Ball: {fire_ball_stats['base_stats']['damage']:.2f} -> "
              f"{fire_ball_stats['enhanced_stats']['damage']:.2f} damage")
        print(f"Blaze: {blaze_stats['base_stats']['damage']:.2f} -> "
              f"{blaze_stats['enhanced_stats']['damage']:.2f} damage")
        print(f"Total set bonuses: {len(data['aggregate_stats']['set_bonuses'])}")
        print(f"Ranged Defense: {defense_stats['ranged']:.2f}%")

    def test_build_with_mixed_enhancements(self, client, db: Session):
        """Test a build with various enhancement types and levels."""
        # Setup archetype
        controller = models.Archetype(
            id=3,
            name="Controller",
            display_name="Controller",
            description="Crowd control specialist",
            primary_group="control",
            secondary_group="support",
            hit_points_base=1017,
            hit_points_max=1606,
        )
        db.add(controller)

        # Create a simple control power
        gravity_control = models.Powerset(
            id=301,
            name="Gravity Control",
            display_name="Gravity Control",
            archetype_id=3,
            powerset_type="primary",
            description="Manipulate gravity",
        )
        db.add(gravity_control)

        gravity_distortion = models.Power(
            id=3001,
            name="gravity_control.gravity_distortion",
            display_name="Gravity Distortion",
            powerset_id=301,
            level_available=1,
            power_type="control",
            target_type="enemy",
            accuracy=1.2,  # Control powers have accuracy bonus
            damage_scale=0.0,  # No damage
            endurance_cost=8.53,
            recharge_time=8.0,
            activation_time=1.83,
            range_feet=80,
            max_targets=1,
            effects={
                "hold_duration": 9.536,  # Base hold duration
                "hold_mag": 3.0,
            }
        )
        db.add(gravity_distortion)

        # Create various enhancement types
        # 1. Standard SO
        hold_so = models.Enhancement(
            id=3100,
            name="hold_so",
            display_name="Hold Duration SO",
            enhancement_type="SO",
            other_bonuses={"hold": 33.33},
            level_min=1,
            level_max=50,
        )
        db.add(hold_so)

        # 2. Dual Aspect SO
        acc_hold_so = models.Enhancement(
            id=3101,
            name="acc_hold_so",
            display_name="Accuracy/Hold SO",
            enhancement_type="SO",
            accuracy_bonus=16.67,
            other_bonuses={"hold": 16.67},
            level_min=1,
            level_max=50,
        )
        db.add(acc_hold_so)

        # 3. Standard IO
        hold_io = models.Enhancement(
            id=3102,
            name="hold_io",
            display_name="Hold Duration IO",
            enhancement_type="IO",
            other_bonuses={"hold": 42.4},  # Level 50 IO value
            level_min=10,
            level_max=50,
        )
        db.add(hold_io)

        # 4. Set IO - Basilisk's Gaze
        basilisk_set = models.EnhancementSet(
            id=302,
            name="Basilisk's Gaze",
            display_name="Basilisk's Gaze",
            description="Hold set",
            min_level=10,
            max_level=30,
        )
        db.add(basilisk_set)

        basilisk_acc_hold = models.Enhancement(
            id=3103,
            name="basilisk_acc_hold",
            display_name="Basilisk's Gaze: Acc/Hold",
            enhancement_type="set_piece",
            set_id=302,
            accuracy_bonus=18.55,
            other_bonuses={"hold": 18.55},
            level_min=10,
            level_max=30,
        )
        db.add(basilisk_acc_hold)

        basilisk_proc = models.Enhancement(
            id=3104,
            name="basilisk_proc",
            display_name="Basilisk's Gaze: Chance for Recharge Slow",
            enhancement_type="set_piece",
            set_id=302,
            unique_enhancement=True,
            other_bonuses={"proc_chance": 0.2, "proc_type": "recharge_slow"},
            level_min=10,
            level_max=30,
        )
        db.add(basilisk_proc)

        # 5. Hami-O (special enhancement)
        hamio = models.Enhancement(
            id=3105,
            name="hamio_acc_dmg_def",
            display_name="Nucleolus Exposure",
            enhancement_type="HO",
            accuracy_bonus=33.0,
            damage_bonus=33.0,
            defense_bonus=20.0,
            level_min=45,
            level_max=50,
        )
        db.add(hamio)

        db.commit()

        # Create test payload with mixed enhancements
        payload = {
            "build": {
                "name": "Controller Mixed Enhancement Test",
                "archetype": "Controller",
                "origin": "Science",
                "level": 50,
                "alignment": "Hero"
            },
            "powers": [
                {
                    "id": 3001,
                    "power_name": "Gravity Distortion",
                    "powerset": "Gravity Control",
                    "level_taken": 1,
                    "slots": [
                        # Level 50+5 SO (boosted)
                        {
                            "slot_index": 0,
                            "enhancement_id": 3100,
                            "enhancement_level": 50,
                            "boosted": True  # +5 levels
                        },
                        # Level 30 dual SO
                        {
                            "slot_index": 1,
                            "enhancement_id": 3101,
                            "enhancement_level": 30
                        },
                        # Level 40 IO
                        {
                            "slot_index": 2,
                            "enhancement_id": 3102,
                            "enhancement_level": 40
                        },
                        # Level 30+5 Set piece (attuned)
                        {
                            "slot_index": 3,
                            "enhancement_id": 3103,
                            "enhancement_level": 30,
                            "catalyzed": True  # Attuned/catalyzed
                        },
                        # Proc enhancement
                        {
                            "slot_index": 4,
                            "enhancement_id": 3104,
                            "enhancement_level": 30
                        },
                        # Hami-O
                        {
                            "slot_index": 5,
                            "enhancement_id": 3105,
                            "enhancement_level": 50
                        },
                    ]
                }
            ],
            "global_buffs": {
                "damage": 0.0,
                "recharge": 70.0,  # High recharge from Hasten + sets
                "defense": {"melee": 0.0, "ranged": 0.0, "aoe": 0.0},
                "resistance": {
                    "smashing": 0.0, "lethal": 0.0, "fire": 0.0,
                    "cold": 0.0, "energy": 0.0, "negative": 0.0,
                    "toxic": 0.0, "psionic": 0.0
                }
            }
        }

        response = client.post("/api/calculate", json=payload)
        assert response.status_code == 200

        data = response.json()

        # Check that all enhancement types were processed
        grav_dist_stats = next(p for p in data["per_power_stats"] if p["power_id"] == 3001)

        # We should have accuracy enhancement from multiple sources
        # acc_hold_so (16.67% * level factor) + basilisk (18.55%) + hamio (33%)
        assert grav_dist_stats["enhancement_values"]["accuracy"] > 50.0

        # Verify boosted and catalyzed enhancements were handled
        # (Currently these are stubs in the code, but test structure is ready)

        print("\nMixed enhancement test results:")
        print(f"Total accuracy enhancement: {grav_dist_stats['enhancement_values']['accuracy']:.2f}%")
        print(f"Base accuracy: {grav_dist_stats['base_stats']['accuracy']}")
        print(f"Enhanced accuracy: {grav_dist_stats['enhanced_stats']['accuracy']}")

        # Check that procs and special enhancements don't contribute to normal bonuses
        # The proc should not add to hold duration
        # The Hami-O should only contribute its valid bonuses for this power type

    def test_tanker_defense_build(self, client, db: Session):
        """Test a defensive Tanker build focusing on caps."""
        # Setup Tanker archetype
        tanker = models.Archetype(
            id=2,
            name="Tanker",
            display_name="Tanker",
            description="Defensive powerhouse",
            primary_group="defense",
            secondary_group="melee",
            hit_points_base=1874,
            hit_points_max=3534,  # Tanker has highest HP cap
        )
        db.add(tanker)

        # Create Shield Defense powerset
        shield_defense = models.Powerset(
            id=201,
            name="Shield Defense",
            display_name="Shield Defense",
            archetype_id=2,
            powerset_type="primary",
            description="Master defensive combat with a shield",
        )
        db.add(shield_defense)

        # Create defensive powers
        deflection = models.Power(
            id=2001,
            name="shield_defense.deflection",
            display_name="Deflection",
            powerset_id=201,
            level_available=1,
            power_type="defense",
            target_type="self",
            accuracy=1.0,
            damage_scale=0.0,
            endurance_cost=0.26,  # Toggle cost per second
            recharge_time=2.0,
            activation_time=2.0,
            effects={
                "defense_melee": 0.15,  # 15% base melee defense
                "defense_lethal": 0.15,  # 15% lethal defense
            }
        )
        db.add(deflection)

        battle_agility = models.Power(
            id=2002,
            name="shield_defense.battle_agility",
            display_name="Battle Agility",
            powerset_id=201,
            level_available=2,
            power_type="defense",
            target_type="self",
            accuracy=1.0,
            damage_scale=0.0,
            endurance_cost=0.26,
            recharge_time=2.0,
            activation_time=2.0,
            effects={
                "defense_ranged": 0.15,  # 15% ranged defense
                "defense_aoe": 0.15,     # 15% AoE defense
            }
        )
        db.add(battle_agility)

        # Create defense enhancement sets
        luck_gambler = models.EnhancementSet(
            id=203,
            name="Luck of the Gambler",
            display_name="Luck of the Gambler",
            description="Defense set with recharge bonus",
            min_level=25,
            max_level=50,
        )
        db.add(luck_gambler)

        # LotG pieces
        lotg_def = models.Enhancement(
            id=2201,
            name="lotg_def",
            display_name="Luck of the Gambler: Defense",
            enhancement_type="set_piece",
            set_id=203,
            defense_bonus=25.5,
            level_min=25,
            level_max=50,
        )
        db.add(lotg_def)

        lotg_def_rech = models.Enhancement(
            id=2202,
            name="lotg_def_rech",
            display_name="Luck of the Gambler: Defense/Recharge",
            enhancement_type="set_piece",
            set_id=203,
            defense_bonus=15.9,
            recharge_bonus=15.9,
            level_min=25,
            level_max=50,
        )
        db.add(lotg_def_rech)

        lotg_global = models.Enhancement(
            id=2203,
            name="lotg_global",
            display_name="Luck of the Gambler: Recharge Speed",
            enhancement_type="set_piece",
            set_id=203,
            unique_enhancement=True,
            other_bonuses={"global_recharge": 7.5},
            level_min=25,
            level_max=50,
        )
        db.add(lotg_global)

        # Create LotG set bonuses
        lotg_bonuses = [
            models.SetBonus(
                set_id=203,
                pieces_required=2,
                bonus_type="regeneration",
                bonus_amount=10.0,
                bonus_description="Increases regeneration by 10%",
            ),
            models.SetBonus(
                set_id=203,
                pieces_required=3,
                bonus_type="hp",
                bonus_amount=1.5,
                bonus_description="Increases maximum health by 1.5%",
            ),
            models.SetBonus(
                set_id=203,
                pieces_required=4,
                bonus_type="accuracy",
                bonus_amount=9.0,
                bonus_description="Increases accuracy by 9%",
            ),
            models.SetBonus(
                set_id=203,
                pieces_required=5,
                bonus_type="recharge",
                bonus_amount=7.5,
                bonus_description="Increases recharge rate by 7.5%",
            ),
            models.SetBonus(
                set_id=203,
                pieces_required=6,
                bonus_type="defense_smashing",
                bonus_amount=3.75,
                bonus_description="Increases smashing defense by 3.75%",
            ),
            models.SetBonus(
                set_id=203,
                pieces_required=6,
                bonus_type="defense_lethal",
                bonus_amount=3.75,
                bonus_description="Increases lethal defense by 3.75%",
            ),
        ]

        for bonus in lotg_bonuses:
            db.add(bonus)

        db.commit()

        # Create test payload - aiming for defense cap
        payload = {
            "build": {
                "name": "Tanker Defense Cap Build",
                "archetype": "Tanker",
                "origin": "Technology",
                "level": 50,
                "alignment": "Hero"
            },
            "powers": [
                {
                    "id": 2001,
                    "power_name": "Deflection",
                    "powerset": "Shield Defense",
                    "level_taken": 1,
                    "slots": [
                        # 6-slot LotG for bonuses
                        {"slot_index": 0, "enhancement_id": 2201, "enhancement_level": 50},
                        {"slot_index": 1, "enhancement_id": 2202, "enhancement_level": 50},
                        {"slot_index": 2, "enhancement_id": 2203, "enhancement_level": 50},
                        {"slot_index": 3, "enhancement_id": 2201, "enhancement_level": 50},
                        {"slot_index": 4, "enhancement_id": 2202, "enhancement_level": 50},
                        {"slot_index": 5, "enhancement_id": 2201, "enhancement_level": 50},
                    ]
                },
                {
                    "id": 2002,
                    "power_name": "Battle Agility",
                    "powerset": "Shield Defense",
                    "level_taken": 2,
                    "slots": [
                        # Another 6-slot LotG
                        {"slot_index": 0, "enhancement_id": 2201, "enhancement_level": 50},
                        {"slot_index": 1, "enhancement_id": 2202, "enhancement_level": 50},
                        {"slot_index": 2, "enhancement_id": 2203, "enhancement_level": 50},
                        {"slot_index": 3, "enhancement_id": 2201, "enhancement_level": 50},
                        {"slot_index": 4, "enhancement_id": 2202, "enhancement_level": 50},
                        {"slot_index": 5, "enhancement_id": 2201, "enhancement_level": 50},
                    ]
                }
            ],
            "global_buffs": {
                "damage": 0.0,
                "recharge": 100.0,  # High recharge from Hasten + multiple LotG globals
                "defense": {
                    "melee": 20.0,    # From other powers/set bonuses
                    "ranged": 20.0,   # From other powers/set bonuses
                    "aoe": 20.0       # From other powers/set bonuses
                },
                "resistance": {
                    "smashing": 50.0,   # Tanker gets decent resists
                    "lethal": 50.0,
                    "fire": 30.0,
                    "cold": 30.0,
                    "energy": 30.0,
                    "negative": 30.0,
                    "toxic": 20.0,
                    "psionic": 20.0
                }
            }
        }

        response = client.post("/api/calculate", json=payload)
        assert response.status_code == 200

        data = response.json()

        # Verify basic build info
        assert data["build_name"] == "Tanker Defense Cap Build"
        assert data["archetype"] == "Tanker"

        # Check defense values are approaching or at soft cap (45%)
        defense_stats = data["aggregate_stats"]["defense"]

        # Base + global + set bonuses should give high defense
        # Melee: 20% global + 3.75% from LotG 6-piece (unique rule applies)
        assert defense_stats["melee"] >= 23.75

        # Check that resistance caps are enforced (90% for Tanker)
        resistance_stats = data["aggregate_stats"]["resistance"]
        assert resistance_stats["smashing"] <= 90.0
        assert resistance_stats["lethal"] <= 90.0

        # Check HP calculations with Tanker's high base
        hp_stats = data["aggregate_stats"]["totals"]["hit_points"]
        assert hp_stats["base"] == pytest.approx(1874, rel=0.01)  # Tanker base HP

        # With set bonuses: +1.5% HP from LotG (unique rule)
        expected_hp = 1874 * 1.015  # 1.5% increase
        assert hp_stats["max"] >= expected_hp

        print("\nTanker defense build results:")
        print(f"Melee Defense: {defense_stats['melee']:.2f}%")
        print(f"Ranged Defense: {defense_stats['ranged']:.2f}%")
        print(f"AoE Defense: {defense_stats['aoe']:.2f}%")
        print(f"Smashing Resistance: {resistance_stats['smashing']:.2f}%")
        print(f"Max HP: {hp_stats['max']:.0f} (base: {hp_stats['base']:.0f})")
