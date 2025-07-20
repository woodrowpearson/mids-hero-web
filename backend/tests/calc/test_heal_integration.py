"""Integration tests for healing calculations in the calculator service."""
import pytest
from sqlalchemy.orm import Session

from app import models


class TestHealingIntegration:
    """Test healing calculations integrated into the calculator."""

    def test_healing_power_calculation(self, client, db: Session):
        """Test that healing powers are calculated correctly."""
        # Create test archetype
        test_archetype = models.Archetype(
            id=1,
            name="Defender",
            display_name="Defender",
            primary_group="support",
            secondary_group="damage",
            hit_points_base=1017,
            hit_points_max=1606,
        )
        db.add(test_archetype)

        # Create test powerset
        test_powerset = models.Powerset(
            id=1,
            name="Empathy",
            display_name="Empathy",
            archetype_id=1,
            powerset_type="primary",
        )
        db.add(test_powerset)

        # Create healing power with heal_scale in effects
        test_power = models.Power(
            id=1,
            name="heal_other",
            display_name="Heal Other",
            powerset_id=1,
            level_available=1,
            power_type="heal",
            damage_scale=0.0,
            endurance_cost=13.0,
            recharge_time=4.0,
            activation_time=2.37,
            accuracy=1.0,
            range_feet=80.0,
            radius_feet=0.0,
            effects={"heal_scale": 0.3}  # 30% heal scale
        )
        db.add(test_power)

        # Create healing enhancement
        test_enhancement = models.Enhancement(
            id=1,
            name="Heal SO",
            display_name="Heal SO",
            enhancement_type="single_origin",
            level_min=1,
            level_max=50,
            other_bonuses={"heal": 33.33}
        )
        db.add(test_enhancement)
        
        db.commit()

        # Build payload with healing enhancements
        payload = {
            "build": {
                "name": "Healer Build",
                "archetype": "Defender",
                "origin": "Science",
                "level": 50,
                "alignment": "Hero"
            },
            "powers": [
                {
                    "id": 1,
                    "power_name": "Heal Other",
                    "powerset": "Empathy",
                    "level_taken": 1,
                    "slots": [
                        {
                            "slot_index": 0,
                            "enhancement_id": 1,
                            "enhancement_level": 50,
                            "boosted": False,
                            "catalyzed": False
                        },
                        {
                            "slot_index": 1,
                            "enhancement_id": 1,
                            "enhancement_level": 50,
                            "boosted": False,
                            "catalyzed": False
                        },
                        {
                            "slot_index": 2,
                            "enhancement_id": 1,
                            "enhancement_level": 50,
                            "boosted": False,
                            "catalyzed": False
                        }
                    ]
                }
            ],
            "global_buffs": {
                "damage": 0.0,
                "recharge": 0.0,
                "healing": 15.0,  # 15% global healing from set bonuses
                "defense": {
                    "melee": 0.0,
                    "ranged": 0.0,
                    "aoe": 0.0
                },
                "resistance": {
                    "smashing": 0.0,
                    "lethal": 0.0,
                    "fire": 0.0,
                    "cold": 0.0,
                    "energy": 0.0,
                    "negative": 0.0,
                    "toxic": 0.0,
                    "psionic": 0.0
                }
            }
        }

        response = client.post("/api/calculate", json=payload)
        assert response.status_code == 200

        data = response.json()
        
        # Find the healing power in results
        heal_power = next(
            (p for p in data["per_power_stats"] if p["power_id"] == 1),
            None
        )
        assert heal_power is not None
        
        # Verify base healing calculation
        # Defender at level 50: 357.95 base * 0.3 scale = 107.385
        assert heal_power["base_stats"]["healing"] == pytest.approx(107.385, 0.01)
        
        # Verify enhanced healing calculation
        # 3x 33.33% = 99.99% enhancement, which is ~95% after ED
        # 107.385 * (1 + 0.95 + 0.15) = 107.385 * 2.10 = 225.509
        assert heal_power["enhanced_stats"]["healing"] == pytest.approx(225.509, 0.5)
        
        # Verify enhancement values after ED
        assert heal_power["enhancement_values"]["healing"] == pytest.approx(95.0, 0.5)

    def test_no_healing_on_damage_power(self, client, db: Session):
        """Test that non-healing powers have zero healing."""
        # Create test archetype
        test_archetype = models.Archetype(
            id=2,
            name="Blaster",
            display_name="Blaster",
            primary_group="damage",
            secondary_group="damage",
            hit_points_base=1204,
            hit_points_max=1606,
        )
        db.add(test_archetype)

        # Create test powerset
        test_powerset = models.Powerset(
            id=2,
            name="Energy Blast",
            display_name="Energy Blast",
            archetype_id=2,
            powerset_type="primary",
        )
        db.add(test_powerset)

        # Create damage power without heal_scale
        test_power = models.Power(
            id=2,
            name="energy_blast",
            display_name="Energy Blast",
            powerset_id=2,
            level_available=1,
            power_type="attack",
            damage_scale=1.0,
            endurance_cost=8.528,
            recharge_time=4.0,
            activation_time=1.67,
            accuracy=1.0,
            range_feet=80.0,
            radius_feet=0.0,
            effects={}  # No heal_scale
        )
        db.add(test_power)
        db.commit()

        payload = {
            "build": {
                "name": "Blaster Build",
                "archetype": "Blaster",
                "origin": "Science",
                "level": 50,
                "alignment": "Hero"
            },
            "powers": [
                {
                    "id": 2,
                    "power_name": "Energy Blast",
                    "powerset": "Energy Blast",
                    "level_taken": 1,
                    "slots": []
                }
            ],
            "global_buffs": {
                "damage": 0.0,
                "recharge": 0.0,
                "healing": 0.0,
                "defense": {
                    "melee": 0.0,
                    "ranged": 0.0,
                    "aoe": 0.0
                },
                "resistance": {
                    "smashing": 0.0,
                    "lethal": 0.0,
                    "fire": 0.0,
                    "cold": 0.0,
                    "energy": 0.0,
                    "negative": 0.0,
                    "toxic": 0.0,
                    "psionic": 0.0
                }
            }
        }

        response = client.post("/api/calculate", json=payload)
        assert response.status_code == 200

        data = response.json()
        power_stats = data["per_power_stats"][0]
        
        # Should have no healing
        assert power_stats["base_stats"]["healing"] == 0.0
        assert power_stats["enhanced_stats"]["healing"] == 0.0

    def test_archetype_heal_modifiers(self, client, db: Session):
        """Test that different archetypes have different heal modifiers."""
        # Create Defender and Tanker archetypes
        defender = models.Archetype(
            id=3,
            name="Defender",
            display_name="Defender",
            primary_group="support",
            secondary_group="damage",
            hit_points_base=1017,
            hit_points_max=1606,
        )
        tanker = models.Archetype(
            id=4,
            name="Tanker",
            display_name="Tanker",
            primary_group="defense",
            secondary_group="damage",
            hit_points_base=1874,
            hit_points_max=3534,
        )
        db.add_all([defender, tanker])

        # Create powersets for both
        defender_powerset = models.Powerset(
            id=3,
            name="Empathy",
            display_name="Empathy",
            archetype_id=3,
            powerset_type="primary",
        )
        tanker_powerset = models.Powerset(
            id=4,
            name="Radiation Armor",
            display_name="Radiation Armor",
            archetype_id=4,
            powerset_type="primary",
        )
        db.add_all([defender_powerset, tanker_powerset])

        # Create healing powers for both
        defender_heal = models.Power(
            id=3,
            name="heal_other_def",
            display_name="Heal Other",
            powerset_id=3,
            level_available=1,
            power_type="heal",
            damage_scale=0.0,
            endurance_cost=13.0,
            recharge_time=4.0,
            activation_time=2.37,
            accuracy=1.0,
            range_feet=80.0,
            radius_feet=0.0,
            effects={"heal_scale": 0.3}
        )
        tanker_heal = models.Power(
            id=4,
            name="radiation_therapy",
            display_name="Radiation Therapy",
            powerset_id=4,
            level_available=20,
            power_type="heal",
            damage_scale=0.0,
            endurance_cost=13.0,
            recharge_time=180.0,
            activation_time=2.1,
            accuracy=1.0,
            range_feet=0.0,
            radius_feet=25.0,
            effects={"heal_scale": 0.3}
        )
        db.add_all([defender_heal, tanker_heal])
        db.commit()

        # Test Defender healing
        defender_payload = {
            "build": {
                "name": "Defender Healer",
                "archetype": "Defender",
                "origin": "Science",
                "level": 50,
                "alignment": "Hero"
            },
            "powers": [
                {
                    "id": 3,
                    "power_name": "Heal Other",
                    "powerset": "Empathy",
                    "level_taken": 1,
                    "slots": []
                }
            ],
            "global_buffs": {
                "damage": 0.0,
                "recharge": 0.0,
                "healing": 0.0,
                "defense": {"melee": 0.0, "ranged": 0.0, "aoe": 0.0},
                "resistance": {
                    "smashing": 0.0, "lethal": 0.0, "fire": 0.0, "cold": 0.0,
                    "energy": 0.0, "negative": 0.0, "toxic": 0.0, "psionic": 0.0
                }
            }
        }

        # Test Tanker healing
        tanker_payload = {
            "build": {
                "name": "Tanker Healer",
                "archetype": "Tanker",
                "origin": "Science",
                "level": 50,
                "alignment": "Hero"
            },
            "powers": [
                {
                    "id": 4,
                    "power_name": "Radiation Therapy",
                    "powerset": "Radiation Armor",
                    "level_taken": 20,
                    "slots": []
                }
            ],
            "global_buffs": {
                "damage": 0.0,
                "recharge": 0.0,
                "healing": 0.0,
                "defense": {"melee": 0.0, "ranged": 0.0, "aoe": 0.0},
                "resistance": {
                    "smashing": 0.0, "lethal": 0.0, "fire": 0.0, "cold": 0.0,
                    "energy": 0.0, "negative": 0.0, "toxic": 0.0, "psionic": 0.0
                }
            }
        }

        # Get responses
        defender_response = client.post("/api/calculate", json=defender_payload)
        tanker_response = client.post("/api/calculate", json=tanker_payload)
        
        assert defender_response.status_code == 200
        assert tanker_response.status_code == 200
        
        defender_data = defender_response.json()
        tanker_data = tanker_response.json()
        
        defender_heal_value = defender_data["per_power_stats"][0]["base_stats"]["healing"]
        tanker_heal_value = tanker_data["per_power_stats"][0]["base_stats"]["healing"]
        
        # Tanker should heal for 60% of Defender
        assert tanker_heal_value == pytest.approx(defender_heal_value * 0.6, 0.01)