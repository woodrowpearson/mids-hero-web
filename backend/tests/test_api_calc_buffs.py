"""Integration tests for buff/debuff calculations in the API."""

import pytest
from sqlalchemy.orm import Session

from app import models


class TestBuffDebuffAPI:
    """Test buff and debuff calculations through the API."""

    def test_calculate_with_buff_powers(self, client, db: Session):
        """Test calculation with powers that provide buffs."""
        # Create test archetype
        archetype = models.Archetype(
            id=1,
            name="Tanker",
            display_name="Tanker",
            primary_group="defense",
            secondary_group="melee",
            hit_points_base=1874,
            hit_points_max=3534,
        )
        db.add(archetype)

        # Create a toggle power that provides defense buffs
        toggle_power = models.Power(
            id=1,
            name="invincibility",
            display_name="Invincibility",
            powerset_id=1,
            level_available=8,
            power_type="toggle",
            endurance_cost=0.26,
            recharge_time=10.0,
            activation_time=1.17,
            effects={
                "defense_melee": 0.15,  # 15% melee defense
                "defense_ranged": 0.075,  # 7.5% ranged defense
            }
        )
        db.add(toggle_power)

        # Create an auto power that provides resistance
        auto_power = models.Power(
            id=2,
            name="resist_physical",
            display_name="Resist Physical Damage",
            powerset_id=1,
            level_available=1,
            power_type="auto",
            effects={
                "resistance_smashing": 0.10,  # 10% smashing resistance
                "resistance_lethal": 0.10,    # 10% lethal resistance
            }
        )
        db.add(auto_power)

        db.commit()

        payload = {
            "build": {
                "name": "Buff Test Tanker",
                "archetype": "Tanker",
                "origin": "Natural",
                "level": 50,
                "alignment": "Hero"
            },
            "powers": [
                {
                    "id": 1,
                    "power_name": "Invincibility",
                    "powerset": "Invulnerability",
                    "level_taken": 8,
                    "slots": []
                },
                {
                    "id": 2,
                    "power_name": "Resist Physical Damage",
                    "powerset": "Invulnerability",
                    "level_taken": 1,
                    "slots": []
                }
            ],
            "global_buffs": {
                "damage": 20.0,
                "recharge": 50.0,
                "defense": {
                    "melee": 10.0,
                    "ranged": 5.0,
                    "aoe": 5.0
                },
                "resistance": {
                    "smashing": 5.0,
                    "lethal": 5.0,
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

        # Debug print
        print(f"Aggregate stats: {data['aggregate_stats']}")
        print(f"Damage buffs: {data['aggregate_stats']['damage_buff']}")

        # Check that buffs were aggregated correctly
        # Defense: 10% (global) + 15% (invincibility) = 25% melee
        assert data["aggregate_stats"]["defense"]["melee"] == pytest.approx(25.0, rel=0.1)
        assert data["aggregate_stats"]["defense"]["ranged"] == pytest.approx(12.5, rel=0.1)  # 5% + 7.5%

        # Resistance: 5% (global) + 10% (auto power) = 15%
        assert data["aggregate_stats"]["resistance"]["smashing"] == pytest.approx(15.0, rel=0.1)
        assert data["aggregate_stats"]["resistance"]["lethal"] == pytest.approx(15.0, rel=0.1)

        # Damage buff
        assert data["aggregate_stats"]["damage_buff"]["melee"] == 20.0

    def test_calculate_with_set_bonuses_and_buffs(self, client, db: Session):
        """Test buff aggregation from multiple sources including set bonuses."""
        # Create test data
        archetype = models.Archetype(
            id=1,
            name="Scrapper",
            display_name="Scrapper",
            primary_group="melee",
            secondary_group="defense",
            hit_points_base=1338,
            hit_points_max=2088,
        )
        db.add(archetype)

        # Create enhancement set
        enh_set = models.EnhancementSet(
            id=1,
            name="Crushing Impact",
            display_name="Crushing Impact",
            min_level=20,
            max_level=50,
        )
        db.add(enh_set)

        # Create set bonuses
        set_bonus_1 = models.SetBonus(
            id=1,
            set_id=1,
            pieces_required=2,
            bonus_description="5% Recharge",
            bonus_type="recharge",
            bonus_amount=5.0,
            bonus_details={"recharge": 5.0}
        )
        set_bonus_2 = models.SetBonus(
            id=2,
            set_id=1,
            pieces_required=3,
            bonus_description="7% Accuracy",
            bonus_type="accuracy",
            bonus_amount=7.0,
            bonus_details={"accuracy": 7.0}
        )
        set_bonus_3 = models.SetBonus(
            id=3,
            set_id=1,
            pieces_required=4,
            bonus_description="2.5% Damage",
            bonus_type="damage",
            bonus_amount=2.5,
            bonus_details={"damage": 2.5}
        )
        db.add_all([set_bonus_1, set_bonus_2, set_bonus_3])

        # Create enhancements from the set
        enhancements = []
        for i in range(4):
            enh = models.Enhancement(
                id=i+1,
                name=f"crushing_impact_{i+1}",
                display_name=f"Crushing Impact: {['Acc/Dam', 'Dam/End', 'Dam/Rech', 'Acc/Dam/Rech'][i]}",
                enhancement_type="IO",
                set_id=1,
                damage_bonus=20.0,
                accuracy_bonus=15.0 if i in [0, 3] else 0.0,
                endurance_bonus=15.0 if i == 1 else 0.0,
                recharge_bonus=15.0 if i in [2, 3] else 0.0,
            )
            enhancements.append(enh)
        db.add_all(enhancements)

        # Create power
        power = models.Power(
            id=1,
            name="strike",
            display_name="Strike",
            powerset_id=1,
            level_available=1,
            power_type="attack",
            damage_scale=1.0,
            endurance_cost=5.2,
            recharge_time=3.0,
            activation_time=0.83,
            accuracy=1.0,
        )
        db.add(power)

        db.commit()

        payload = {
            "build": {
                "name": "Set Bonus Test",
                "archetype": "Scrapper",
                "origin": "Magic",
                "level": 50,
                "alignment": "Hero"
            },
            "powers": [
                {
                    "id": 1,
                    "power_name": "Strike",
                    "powerset": "Street Justice",
                    "level_taken": 1,
                    "slots": [
                        {"slot_index": 0, "enhancement_id": 1, "enhancement_level": 50, "boosted": False, "catalyzed": False},
                        {"slot_index": 1, "enhancement_id": 2, "enhancement_level": 50, "boosted": False, "catalyzed": False},
                        {"slot_index": 2, "enhancement_id": 3, "enhancement_level": 50, "boosted": False, "catalyzed": False},
                        {"slot_index": 3, "enhancement_id": 4, "enhancement_level": 50, "boosted": False, "catalyzed": False},
                    ]
                }
            ],
            "global_buffs": {
                "damage": 30.0,
                "recharge": 70.0,
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

        # Check that set bonuses were applied
        assert len(data["aggregate_stats"]["set_bonuses"]) == 3

        # Check buff totals
        # Damage: 30% (global) + 2.5% (set bonus) = 32.5%
        assert data["aggregate_stats"]["damage_buff"]["melee"] == 32.5

        # Verify recharge buffed appropriately (but need to check in utility stats)
        # For now just verify set bonuses are listed
        set_bonus_names = [b["bonus_description"] for b in data["aggregate_stats"]["set_bonuses"]]
        assert "5% Recharge" in set_bonus_names
        assert "7% Accuracy" in set_bonus_names
        assert "2.5% Damage" in set_bonus_names

    def test_calculate_with_debuffs(self, client, db: Session):
        """Test calculation with debuff effects."""
        # Create test archetype
        archetype = models.Archetype(
            id=1,
            name="Controller",
            display_name="Controller",
            primary_group="control",
            secondary_group="support",
            hit_points_base=1017,
            hit_points_max=1606,
        )
        db.add(archetype)

        # Create a power that could be debuffed
        power = models.Power(
            id=1,
            name="hold",
            display_name="Block of Ice",
            powerset_id=1,
            level_available=1,
            power_type="attack",
            damage_scale=0.8,
            endurance_cost=8.528,
            recharge_time=8.0,
            activation_time=1.87,
            accuracy=1.2,
        )
        db.add(power)

        db.commit()

        # Simulate being debuffed
        payload = {
            "build": {
                "name": "Debuffed Controller",
                "archetype": "Controller",
                "origin": "Science",
                "level": 50,
                "alignment": "Hero"
            },
            "powers": [
                {
                    "id": 1,
                    "power_name": "Block of Ice",
                    "powerset": "Ice Control",
                    "level_taken": 1,
                    "slots": []
                }
            ],
            "global_buffs": {
                "damage": -30.0,  # Simulating damage debuff
                "recharge": -50.0,  # Simulating recharge debuff
                "defense": {
                    "melee": -20.0,  # Defense debuff
                    "ranged": -20.0,
                    "aoe": -20.0
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

        # Check that debuffs were applied
        assert data["aggregate_stats"]["damage_buff"]["melee"] == -30.0
        assert data["aggregate_stats"]["defense"]["melee"] == -20.0

        # Check per-power stats show reduced values
        power_stats = data["per_power_stats"][0]
        # Base damage should be reduced by 30%
        assert power_stats["enhanced_stats"]["damage"] < power_stats["base_stats"]["damage"]

