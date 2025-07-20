"""Integration tests for calculation API endpoint."""

import pytest
from sqlalchemy.orm import Session

from app import models


class TestCalculationAPI:
    """Test the /api/calculate endpoint."""

    def test_calculate_basic_build(self, client, db: Session):
        """Test basic build calculation."""
        # Create test power in database
        test_archetype = models.Archetype(
            id=1,
            name="Blaster",
            display_name="Blaster",
            primary_group="damage",
            secondary_group="damage",
            hit_points_base=1204,
            hit_points_max=1606,
        )
        db.add(test_archetype)
        
        test_powerset = models.Powerset(
            id=1,
            name="Fire Blast",
            display_name="Fire Blast",
            archetype_id=1,
            powerset_type="primary",
        )
        db.add(test_powerset)
        
        test_power = models.Power(
            id=1,
            name="test_power_1",
            display_name="Test Power",
            powerset_id=1,
            level_available=1,
            power_type="attack",
            damage_scale=1.0,
            endurance_cost=8.528,
            recharge_time=8.0,
            activation_time=1.67,
            accuracy=1.0,
            range_feet=80,
        )
        db.add(test_power)
        db.commit()
        
        payload = {
            "build": {
                "name": "Test Blaster",
                "archetype": "Blaster",
                "origin": "Science",
                "level": 50,
                "alignment": "Hero"
            },
            "powers": [
                {
                    "id": 1,
                    "power_name": "Test Power",
                    "powerset": "Test Set",
                    "level_taken": 1,
                    "slots": []
                }
            ],
            "global_buffs": {
                "damage": 0.0,
                "recharge": 0.0,
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
        if response.status_code != 200:
            print(f"Error response: {response.json()}")
        assert response.status_code == 200

        data = response.json()
        assert data["build_name"] == "Test Blaster"
        assert data["archetype"] == "Blaster"
        assert data["level"] == 50
        assert len(data["per_power_stats"]) == 1
        assert data["per_power_stats"][0]["power_name"] == "Test Power"

    def test_calculate_with_enhancements(self, client, db: Session):
        """Test calculation with enhancement slots."""
        # Create test data in database
        test_archetype = models.Archetype(
            id=1,
            name="Blaster",
            display_name="Blaster",
            primary_group="damage",
            secondary_group="damage",
            hit_points_base=1204,
            hit_points_max=1606,
        )
        db.add(test_archetype)
        
        test_powerset = models.Powerset(
            id=1,
            name="Fire Blast",
            display_name="Fire Blast",
            archetype_id=1,
            powerset_type="primary",
        )
        db.add(test_powerset)
        
        test_power = models.Power(
            id=2,
            name="fire_blast",
            display_name="Fire Blast",
            powerset_id=1,
            level_available=1,
            power_type="attack",
            damage_scale=1.0,
            endurance_cost=8.528,
            recharge_time=8.0,
            activation_time=1.67,
            accuracy=1.0,
            range_feet=80,
        )
        db.add(test_power)
        
        # Create damage SO enhancement
        damage_so = models.Enhancement(
            id=1,
            name="damage_so",
            display_name="Damage SO",
            enhancement_type="SO",
            damage_bonus=33.33,  # Base 33.33% for SOs
            level_min=1,
            level_max=50,
        )
        db.add(damage_so)
        db.commit()
        
        payload = {
            "build": {
                "name": "Enhanced Blaster",
                "archetype": "Blaster",
                "origin": "Technology",
                "level": 50,
                "alignment": "Hero"
            },
            "powers": [
                {
                    "id": 2,
                    "power_name": "Fire Blast",
                    "powerset": "Fire Blast",
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
                "defense": {"melee": 0.0, "ranged": 0.0, "aoe": 0.0},
                "resistance": {
                    "smashing": 0.0, "lethal": 0.0, "fire": 0.0,
                    "cold": 0.0, "energy": 0.0, "negative": 0.0,
                    "toxic": 0.0, "psionic": 0.0
                }
            }
        }

        response = client.post("/api/calculate", json=payload)
        if response.status_code != 200:
            print(f"Error response: {response.json()}")
        assert response.status_code == 200

        data = response.json()
        power_stats = data["per_power_stats"][0]

        # Check that damage was enhanced
        assert power_stats["enhanced_stats"]["damage"] > power_stats["base_stats"]["damage"]
        # Check ED was applied (3 SOs should give ~95% after ED)
        print(f"Enhancement values: {power_stats['enhancement_values']}")
        print(f"Base damage: {power_stats['base_stats']['damage']}")
        print(f"Enhanced damage: {power_stats['enhanced_stats']['damage']}")
        assert power_stats["enhancement_values"]["damage"] == pytest.approx(95.0, rel=0.1)

    def test_calculate_with_global_buffs(self, client, db: Session):
        """Test calculation with global buffs."""
        payload = {
            "build": {
                "name": "Buffed Tanker",
                "archetype": "Tanker",
                "origin": "Natural",
                "level": 50,
                "alignment": "Hero"
            },
            "powers": [],
            "global_buffs": {
                "damage": 25.0,
                "recharge": 70.0,
                "defense": {
                    "melee": 45.0,  # At soft cap
                    "ranged": 30.0,
                    "aoe": 20.0
                },
                "resistance": {
                    "smashing": 90.0,  # At Tanker cap
                    "lethal": 90.0,
                    "fire": 50.0,
                    "cold": 30.0,
                    "energy": 30.0,
                    "negative": 20.0,
                    "toxic": 0.0,
                    "psionic": 10.0
                }
            }
        }

        response = client.post("/api/calculate", json=payload)
        assert response.status_code == 200

        data = response.json()

        # Check defense values
        assert data["aggregate_stats"]["defense"]["melee"] == 45.0
        assert data["aggregate_stats"]["defense"]["ranged"] == 30.0

        # Check resistance values (should be capped at 90% for Tanker)
        assert data["aggregate_stats"]["resistance"]["smashing"] == 90.0
        assert data["aggregate_stats"]["resistance"]["lethal"] == 90.0

    def test_calculate_exceeding_caps(self, client, db: Session):
        """Test that caps are enforced and warnings generated."""
        payload = {
            "build": {
                "name": "Over-capped Blaster",
                "archetype": "Blaster",
                "origin": "Magic",
                "level": 50,
                "alignment": "Hero"
            },
            "powers": [],
            "global_buffs": {
                "damage": 0.0,
                "recharge": 0.0,
                "defense": {
                    "melee": 100.0,  # Over hard cap
                    "ranged": 100.0,
                    "aoe": 100.0
                },
                "resistance": {
                    "smashing": 95.0,  # Over Blaster cap of 75%
                    "lethal": 95.0,
                    "fire": 95.0,
                    "cold": 95.0,
                    "energy": 95.0,
                    "negative": 95.0,
                    "toxic": 95.0,
                    "psionic": 95.0
                }
            }
        }

        response = client.post("/api/calculate", json=payload)
        assert response.status_code == 200

        data = response.json()

        # Check that warnings were generated
        assert len(data["validation_warnings"]) > 0

        # Check that values were capped
        assert data["aggregate_stats"]["defense"]["melee"] == 95.0  # Hard cap
        assert data["aggregate_stats"]["resistance"]["smashing"] == 75.0  # Blaster cap

    def test_calculate_invalid_archetype(self, client, db: Session):
        """Test error handling for invalid archetype."""
        payload = {
            "build": {
                "name": "Invalid Build",
                "archetype": "InvalidArchetype",
                "origin": "Science",
                "level": 50,
                "alignment": "Hero"
            },
            "powers": [],
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
        assert response.status_code == 400
        assert "Unknown archetype" in response.json()["detail"]

    def test_calculate_invalid_level(self, client, db: Session):
        """Test validation for invalid character level."""
        payload = {
            "build": {
                "name": "Invalid Level",
                "archetype": "Scrapper",
                "origin": "Mutation",
                "level": 100,  # Invalid - max is 50
                "alignment": "Hero"
            },
            "powers": [],
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
        assert response.status_code == 422  # Validation error

    def test_calculate_duplicate_power_ids(self, client, db: Session):
        """Test validation for duplicate power IDs."""
        payload = {
            "build": {
                "name": "Duplicate Powers",
                "archetype": "Controller",
                "origin": "Science",
                "level": 50,
                "alignment": "Hero"
            },
            "powers": [
                {
                    "id": "power_1",
                    "power_name": "Power 1",
                    "powerset": "Set 1",
                    "level_taken": 1,
                    "slots": []
                },
                {
                    "id": "power_1",  # Duplicate ID
                    "power_name": "Power 2",
                    "powerset": "Set 2",
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
        assert response.status_code == 422  # Validation error
