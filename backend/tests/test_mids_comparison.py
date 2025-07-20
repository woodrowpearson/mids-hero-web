"""Tests comparing our calculations with MidsReborn expected values."""

import pytest
from sqlalchemy.orm import Session

from app import models
from app.calc_schemas.mids_comparison import MidsTotalStatistics, compare_with_mids


class TestMidsRebornComparison:
    """Test our calculations against known MidsReborn outputs."""
    
    def test_basic_blaster_no_enhancements(self, client, db: Session):
        """Test a basic Blaster with no enhancements - simplest comparison case."""
        # Create Blaster archetype
        blaster = models.Archetype(
            id=1,
            name="Blaster",
            display_name="Blaster",
            description="Ranged damage dealer",
            primary_group="damage",
            secondary_group="damage",
            hit_points_base=1204.8,
            hit_points_max=1606.4,
        )
        db.add(blaster)
        
        # Create a simple power for testing
        energy_blast_set = models.Powerset(
            id=101,
            name="Energy Blast",
            display_name="Energy Blast",
            archetype_id=1,
            powerset_type="primary",
        )
        db.add(energy_blast_set)
        
        power_bolt = models.Power(
            id=1001,
            name="energy_blast.power_bolt",
            display_name="Power Bolt",
            powerset_id=101,
            level_available=1,
            power_type="attack",
            target_type="enemy",
            accuracy=1.0,
            damage_scale=1.0,
            endurance_cost=5.2,
            recharge_time=4.0,
            activation_time=1.0,
            range_feet=80,
        )
        db.add(power_bolt)
        
        db.commit()
        
        # Create minimal build payload
        payload = {
            "build": {
                "name": "Basic Blaster Test",
                "archetype": "Blaster",
                "origin": "Science",
                "level": 50,
                "alignment": "Hero"
            },
            "powers": [
                {
                    "id": 1001,
                    "power_name": "Power Bolt",
                    "powerset": "Energy Blast",
                    "level_taken": 1,
                    "slots": []  # No enhancements
                }
            ],
            "global_buffs": {
                "damage": 0.0,
                "recharge": 0.0,
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
        
        # Expected values from MidsReborn for level 50 Blaster
        # These are baseline values with no enhancements or bonuses
        expected_mids_stats = MidsTotalStatistics(
            # Base HP for Blaster at 50
            hp_max=1204.8,
            hp_regen=5.06,  # Base regen ~0.42% per second
            
            # Base endurance
            end_max=100.0,
            end_rec=1.67,  # Base recovery
            
            # Base movement (no travel powers)
            run_speed=14.32,  # Base run speed
            jump_speed=14.32,
            fly_speed=0.0,  # No fly power
            jump_height=8.0,
            
            # No defense/resistance without powers
            defense_melee=0.0,
            defense_ranged=0.0,
            defense_aoe=0.0,
            resistance_smashing=0.0,
            resistance_lethal=0.0,
            resistance_fire=0.0,
            resistance_cold=0.0,
            resistance_energy=0.0,
            resistance_negative=0.0,
            resistance_toxic=0.0,
            resistance_psionic=0.0,
            
            # Base perception
            perception_radius=500.0,
            stealth_radius=0.0,
        )
        
        # Compare results
        comparison = compare_with_mids(data, expected_mids_stats, tolerance_pct=5.0)
        
        # Print comparison for debugging
        if comparison.differences:
            print("\nDifferences found:")
            for stat, diff in comparison.differences.items():
                print(f"  {stat}: ours={diff['ours']:.2f}, mids={diff['mids']:.2f}, "
                      f"diff={diff['diff']:.2f} ({diff['diff_pct']:.1f}%)")
        
        assert comparison.passed, f"Max difference {comparison.max_difference_pct:.1f}% exceeds tolerance"
    
    def test_tanker_with_basic_defenses(self, client, db: Session):
        """Test Tanker with basic defense powers - validates defense calculations."""
        # Create Tanker archetype  
        tanker = models.Archetype(
            id=2,
            name="Tanker",
            display_name="Tanker",
            description="Defensive powerhouse",
            primary_group="defense",
            secondary_group="melee",
            hit_points_base=1874.1,
            hit_points_max=3534.3,
        )
        db.add(tanker)
        
        # Create Invulnerability powerset
        invuln = models.Powerset(
            id=201,
            name="Invulnerability",
            display_name="Invulnerability",
            archetype_id=2,
            powerset_type="primary",
        )
        db.add(invuln)
        
        # Temp Invulnerability (auto power - resistance)
        temp_invuln = models.Power(
            id=2001,
            name="invulnerability.temp_invulnerability",
            display_name="Temp Invulnerability",
            powerset_id=201,
            level_available=1,
            power_type="auto",
            target_type="self",
            effects={
                "resistance_smashing": 0.15,  # 15% S/L resist
                "resistance_lethal": 0.15,
            }
        )
        db.add(temp_invuln)
        
        # Resist Physical Damage (auto power)
        resist_physical = models.Power(
            id=2002,
            name="invulnerability.resist_physical_damage",
            display_name="Resist Physical Damage",
            powerset_id=201,
            level_available=2,
            power_type="auto",
            target_type="self",
            effects={
                "resistance_smashing": 0.075,  # 7.5% S/L resist
                "resistance_lethal": 0.075,
            }
        )
        db.add(resist_physical)
        
        db.commit()
        
        # Build payload with auto powers
        payload = {
            "build": {
                "name": "Tanker Defense Test",
                "archetype": "Tanker",
                "origin": "Magic",
                "level": 50,
                "alignment": "Hero"
            },
            "powers": [
                {
                    "id": 2001,
                    "power_name": "Temp Invulnerability",
                    "powerset": "Invulnerability",
                    "level_taken": 1,
                    "slots": []
                },
                {
                    "id": 2002,
                    "power_name": "Resist Physical Damage", 
                    "powerset": "Invulnerability",
                    "level_taken": 2,
                    "slots": []
                }
            ],
            "global_buffs": {
                "damage": 0.0,
                "recharge": 0.0,
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
        
        # Expected MidsReborn values for Tanker with these powers
        expected_mids_stats = MidsTotalStatistics(
            # Tanker base HP at 50
            hp_max=1874.1,
            hp_regen=7.88,  # Higher regen than Blaster
            
            # Base endurance
            end_max=100.0,
            end_rec=1.67,
            
            # Movement
            run_speed=14.32,
            jump_speed=14.32,
            fly_speed=0.0,
            jump_height=8.0,
            
            # Resistances from powers (should stack to 22.5%)
            resistance_smashing=22.5,  # 15% + 7.5%
            resistance_lethal=22.5,
            resistance_fire=0.0,
            resistance_cold=0.0,
            resistance_energy=0.0,
            resistance_negative=0.0,
            resistance_toxic=0.0,
            resistance_psionic=0.0,
            
            # No defense from these powers
            defense_melee=0.0,
            defense_ranged=0.0,
            defense_aoe=0.0,
            
            perception_radius=500.0,
            stealth_radius=0.0,
        )
        
        comparison = compare_with_mids(data, expected_mids_stats, tolerance_pct=5.0)
        
        if comparison.differences:
            print("\nDifferences found:")
            for stat, diff in comparison.differences.items():
                print(f"  {stat}: ours={diff['ours']:.2f}, mids={diff['mids']:.2f}, "
                      f"diff={diff['diff']:.2f} ({diff['diff_pct']:.1f}%)")
        
        # Note: This test will likely fail initially because we haven't implemented
        # auto powers yet. That's expected and helps us identify what needs work.
        assert comparison.passed, f"Max difference {comparison.max_difference_pct:.1f}% exceeds tolerance"
    
    def test_set_bonus_accuracy(self, client, db: Session):
        """Test that set bonus accuracy matches MidsReborn calculations."""
        # This test would verify that accuracy bonuses from sets like Thunderstrike
        # are calculated the same way MidsReborn does
        
        # TODO: Implement after we have more specific MidsReborn test data
        pass