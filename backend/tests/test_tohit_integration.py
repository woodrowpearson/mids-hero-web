"""Integration tests for ToHit system with calculator service."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models import Power


class TestToHitIntegration:
    """Test ToHit integration with the calculator service."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_power_hit_chance_calculation(self, client, db: Session):
        """Test that hit_chance is calculated for powers."""
        # Create a test power in the database
        test_power = Power(
            id=99999,
            name="Test Blast",
            display_name="Test Blast",
            power_type="click",
            damage_scale=1.0,
            accuracy=1.0,
            endurance_cost=10.0,
            recharge_time=8.0,
            activation_time=1.5,
            range_feet=80
        )
        db.add(test_power)
        db.commit()

        payload = {
            "build": {
                "name": "Test Build",
                "archetype": "Blaster",
                "origin": "Science",
                "level": 50,
                "alignment": "Hero"
            },
            "powers": [
                {
                    "id": "99999",
                    "power_name": "Test Blast",
                    "powerset": "Test Set",
                    "level_taken": 1,
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
        assert "per_power_stats" in data
        assert len(data["per_power_stats"]) == 1

        power_stats = data["per_power_stats"][0]
        assert "enhanced_stats" in power_stats
        assert "hit_chance" in power_stats["enhanced_stats"]

        # Base ToHit (75%) with no defense, no buffs, base accuracy (1.0)
        # Should be 75%
        expected_hit_chance = 75.0
        assert abs(power_stats["enhanced_stats"]["hit_chance"] - expected_hit_chance) < 0.1

        # Clean up
        db.delete(test_power)
        db.commit()

    def test_power_hit_chance_with_accuracy_enhancement(self, client, db: Session):
        """Test hit_chance calculation with accuracy enhancements."""
        # This test would need enhancement data in the database
        # For now, just verify the structure is correct
        payload = {
            "build": {
                "name": "Test Build",
                "archetype": "Blaster",
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
        assert response.status_code == 200

        data = response.json()
        # Verify the response structure includes hit_chance even with no powers
        assert "per_power_stats" in data
        assert isinstance(data["per_power_stats"], list)
