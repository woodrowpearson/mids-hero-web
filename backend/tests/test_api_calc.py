"""Integration tests for calculation API endpoint."""

import pytest
from fastapi.testclient import TestClient

from app.schemas.build import BuildPayload
from main import app

client = TestClient(app)


class TestCalculationAPI:
    """Test the /api/calculate endpoint."""

    def test_calculate_basic_build(self):
        """Test basic build calculation."""
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
                    "id": "test_power_1",
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
        assert response.status_code == 200
        
        data = response.json()
        assert data["build_name"] == "Test Blaster"
        assert data["archetype"] == "Blaster"
        assert data["level"] == 50
        assert len(data["per_power_stats"]) == 1
        assert data["per_power_stats"][0]["power_name"] == "Test Power"

    def test_calculate_with_enhancements(self):
        """Test calculation with enhancement slots."""
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
                    "id": "fire_blast",
                    "power_name": "Fire Blast",
                    "powerset": "Fire Blast",
                    "level_taken": 1,
                    "slots": [
                        {
                            "slot_index": 0,
                            "enhancement_id": "damage_so",
                            "enhancement_level": 50,
                            "boosted": False,
                            "catalyzed": False
                        },
                        {
                            "slot_index": 1,
                            "enhancement_id": "damage_so",
                            "enhancement_level": 50,
                            "boosted": False,
                            "catalyzed": False
                        },
                        {
                            "slot_index": 2,
                            "enhancement_id": "damage_so",
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
        assert response.status_code == 200
        
        data = response.json()
        power_stats = data["per_power_stats"][0]
        
        # Check that damage was enhanced
        assert power_stats["enhanced_stats"]["damage"] > power_stats["base_stats"]["damage"]
        # Check ED was applied (3 SOs should give ~95% after ED)
        assert power_stats["enhancement_values"]["damage"] == pytest.approx(95.0, rel=0.1)

    def test_calculate_with_global_buffs(self):
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

    def test_calculate_exceeding_caps(self):
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

    def test_calculate_invalid_archetype(self):
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

    def test_calculate_invalid_level(self):
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

    def test_calculate_duplicate_power_ids(self):
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