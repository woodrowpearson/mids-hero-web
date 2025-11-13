"""
Unit tests for Calculation API endpoints.

Tests all Phase 5 calculation endpoints with exact values from specs.
"""

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


# ============================================================================
# Power Damage Calculation Tests
# ============================================================================


class TestPowerDamageCalculation:
    """Tests for POST /api/v1/calculations/power/damage endpoint."""

    def test_basic_damage_calculation(self):
        """Test basic damage calculation with single smashing damage effect."""
        request = {
            "effects": [
                {
                    "effect_type": "damage",
                    "magnitude": 62.56,
                    "damage_type": "smashing",
                    "probability": 1.0,
                    "ticks": 1,
                }
            ],
            "power_type": "click",
            "recharge_time": 4.0,
            "cast_time": 1.07,
            "damage_return_mode": "numeric",
        }

        response = client.post("/api/v1/calculations/power/damage", json=request)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == pytest.approx(62.56, rel=1e-2)
        assert "smashing" in data["by_type"]
        assert data["by_type"]["smashing"] == pytest.approx(62.56, rel=1e-2)
        assert data["has_toggle_enhancements"] is False
        assert "Total: 62.56" in data["tooltip"]

    def test_multiple_damage_types(self):
        """Test power with multiple damage types (e.g., Fire/Energy)."""
        request = {
            "effects": [
                {
                    "effect_type": "damage",
                    "magnitude": 42.5,
                    "damage_type": "fire",
                    "probability": 1.0,
                },
                {
                    "effect_type": "damage",
                    "magnitude": 28.3,
                    "damage_type": "energy",
                    "probability": 1.0,
                },
            ],
            "power_type": "click",
            "recharge_time": 8.0,
            "cast_time": 1.5,
            "damage_return_mode": "numeric",
        }

        response = client.post("/api/v1/calculations/power/damage", json=request)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == pytest.approx(70.8, rel=1e-2)
        assert data["by_type"]["fire"] == pytest.approx(42.5, rel=1e-2)
        assert data["by_type"]["energy"] == pytest.approx(28.3, rel=1e-2)

    def test_dot_damage_with_ticks(self):
        """Test DoT effect with multiple ticks."""
        request = {
            "effects": [
                {
                    "effect_type": "damage",
                    "magnitude": 10.0,
                    "damage_type": "fire",
                    "probability": 1.0,
                    "ticks": 5,
                    "duration": 10.0,
                }
            ],
            "power_type": "click",
            "damage_return_mode": "numeric",
        }

        response = client.post("/api/v1/calculations/power/damage", json=request)

        assert response.status_code == 200
        data = response.json()
        # 10.0 magnitude × 5 ticks = 50.0 total damage
        assert data["total"] == pytest.approx(50.0, rel=1e-2)

    def test_probabilistic_damage_average_mode(self):
        """Test damage with probability in AVERAGE mode."""
        request = {
            "effects": [
                {
                    "effect_type": "damage",
                    "magnitude": 100.0,
                    "damage_type": "energy",
                    "probability": 0.5,
                }
            ],
            "power_type": "click",
            "damage_math_mode": "average",
            "damage_return_mode": "numeric",
        }

        response = client.post("/api/v1/calculations/power/damage", json=request)

        assert response.status_code == 200
        data = response.json()
        # 100.0 × 0.5 probability = 50.0 average damage
        assert data["total"] == pytest.approx(50.0, rel=1e-2)

    def test_probabilistic_damage_minimum_mode(self):
        """Test damage with probability in MINIMUM mode (excludes procs)."""
        request = {
            "effects": [
                {
                    "effect_type": "damage",
                    "magnitude": 100.0,
                    "damage_type": "energy",
                    "probability": 0.5,
                }
            ],
            "power_type": "click",
            "damage_math_mode": "minimum",
            "damage_return_mode": "numeric",
        }

        response = client.post("/api/v1/calculations/power/damage", json=request)

        assert response.status_code == 200
        data = response.json()
        # Minimum mode excludes procs (probability < 0.999)
        assert data["total"] == pytest.approx(0.0, rel=1e-2)

    def test_dps_mode(self):
        """Test DPS (Damage Per Second) return mode."""
        request = {
            "effects": [
                {
                    "effect_type": "damage",
                    "magnitude": 100.0,
                    "damage_type": "smashing",
                    "probability": 1.0,
                }
            ],
            "power_type": "click",
            "recharge_time": 4.0,
            "cast_time": 1.0,
            "damage_return_mode": "dps",
        }

        response = client.post("/api/v1/calculations/power/damage", json=request)

        assert response.status_code == 200
        data = response.json()
        # 100.0 damage / (4.0 recharge + 1.0 cast) = 20.0 DPS
        assert data["total"] == pytest.approx(20.0, rel=1e-2)

    def test_dpa_mode(self):
        """Test DPA (Damage Per Activation) return mode."""
        request = {
            "effects": [
                {
                    "effect_type": "damage",
                    "magnitude": 100.0,
                    "damage_type": "smashing",
                    "probability": 1.0,
                }
            ],
            "power_type": "click",
            "cast_time": 2.0,
            "damage_return_mode": "dpa",
        }

        response = client.post("/api/v1/calculations/power/damage", json=request)

        assert response.status_code == 200
        data = response.json()
        # 100.0 damage / 2.0 cast time = 50.0 DPA
        assert data["total"] == pytest.approx(50.0, rel=1e-2)


# ============================================================================
# Build Defense Calculation Tests
# ============================================================================


class TestBuildDefenseCalculation:
    """Tests for POST /api/v1/calculations/build/defense endpoint."""

    def test_typed_defense_only(self):
        """Test defense from typed sources only."""
        request = {
            "archetype": "Scrapper",
            "defense_bonuses": [
                {"bonuses": {"smashing": 0.30}},
                {"bonuses": {"lethal": 0.25}},
            ],
        }

        response = client.post("/api/v1/calculations/build/defense", json=request)

        assert response.status_code == 200
        data = response.json()
        assert data["typed"]["smashing"] == pytest.approx(0.30, rel=1e-3)
        assert data["typed"]["lethal"] == pytest.approx(0.25, rel=1e-3)

    def test_positional_defense_only(self):
        """Test defense from positional sources only."""
        request = {
            "archetype": "Scrapper",
            "defense_bonuses": [
                {"bonuses": {"melee": 0.40}},
                {"bonuses": {"ranged": 0.20}},
            ],
        }

        response = client.post("/api/v1/calculations/build/defense", json=request)

        assert response.status_code == 200
        data = response.json()
        assert data["positional"]["melee"] == pytest.approx(0.40, rel=1e-3)
        assert data["positional"]["ranged"] == pytest.approx(0.20, rel=1e-3)

    def test_highest_wins_logic(self):
        """Test that highest value wins between typed and positional."""
        request = {
            "archetype": "Scrapper",
            "defense_bonuses": [
                {"bonuses": {"smashing": 0.30}},  # Typed
                {"bonuses": {"melee": 0.40}},  # Positional (higher)
            ],
        }

        response = client.post("/api/v1/calculations/build/defense", json=request)

        assert response.status_code == 200
        data = response.json()
        # Both should be present; highest wins logic is applied at usage time
        assert data["typed"]["smashing"] == pytest.approx(0.30, rel=1e-3)
        assert data["positional"]["melee"] == pytest.approx(0.40, rel=1e-3)


# ============================================================================
# Build Resistance Calculation Tests
# ============================================================================


class TestBuildResistanceCalculation:
    """Tests for POST /api/v1/calculations/build/resistance endpoint."""

    def test_single_resistance_source(self):
        """Test resistance from single source."""
        request = {
            "archetype": "Tanker",
            "resistance_bonuses": [
                {"bonuses": {"smashing": 0.30, "lethal": 0.30}},
            ],
        }

        response = client.post("/api/v1/calculations/build/resistance", json=request)

        assert response.status_code == 200
        data = response.json()
        assert data["values"]["smashing"] == pytest.approx(0.30, rel=1e-3)
        assert data["values"]["lethal"] == pytest.approx(0.30, rel=1e-3)

    def test_additive_stacking(self):
        """Test that resistances stack additively."""
        request = {
            "archetype": "Tanker",
            "resistance_bonuses": [
                {"bonuses": {"fire": 0.30}},
                {"bonuses": {"fire": 0.25}},
                {"bonuses": {"fire": 0.20}},
            ],
        }

        response = client.post("/api/v1/calculations/build/resistance", json=request)

        assert response.status_code == 200
        data = response.json()
        # 0.30 + 0.25 + 0.20 = 0.75 (75%)
        assert data["values"]["fire"] == pytest.approx(0.75, rel=1e-3)

    def test_archetype_cap_enforcement(self):
        """Test that archetype caps are enforced (Tanker: 90% = 0.90)."""
        request = {
            "archetype": "Tanker",
            "resistance_bonuses": [
                {"bonuses": {"smashing": 0.50}},
                {"bonuses": {"smashing": 0.50}},  # Would exceed 90% cap
            ],
        }

        response = client.post("/api/v1/calculations/build/resistance", json=request)

        assert response.status_code == 200
        data = response.json()
        # Should be capped at Tanker's 90% cap
        assert data["values"]["smashing"] <= 0.90


# ============================================================================
# Build Totals Tests
# ============================================================================


class TestBuildTotals:
    """Tests for POST /api/v1/calculations/build/totals endpoint."""

    def test_combined_defense_and_resistance(self):
        """Test calculating both defense and resistance in one call."""
        request = {
            "archetype": "Scrapper",
            "defense_bonuses": [
                {"bonuses": {"melee": 0.30}},
            ],
            "resistance_bonuses": [
                {"bonuses": {"smashing": 0.20, "lethal": 0.15}},
            ],
        }

        response = client.post("/api/v1/calculations/build/totals", json=request)

        assert response.status_code == 200
        data = response.json()

        # Check defense
        assert data["defense"]["positional"]["melee"] == pytest.approx(0.30, rel=1e-3)

        # Check resistance
        assert data["resistance"]["values"]["smashing"] == pytest.approx(0.20, rel=1e-3)
        assert data["resistance"]["values"]["lethal"] == pytest.approx(0.15, rel=1e-3)


# ============================================================================
# Game Constants Tests
# ============================================================================


class TestGameConstants:
    """Tests for GET /api/v1/calculations/constants endpoint."""

    def test_get_constants(self):
        """Test retrieving all game constants."""
        response = client.get("/api/v1/calculations/constants")

        assert response.status_code == 200
        data = response.json()

        # Verify BASE_MAGIC
        assert data["base_magic"] == pytest.approx(1.666667, rel=1e-5)

        # Verify ED Schedule A thresholds
        assert data["ed_schedule_a_thresholds"] == [0.70, 0.90, 1.00]

        # Verify ED efficiencies
        assert data["ed_efficiencies"] == [1.00, 0.90, 0.70, 0.15]

        # Verify game tick
        assert data["game_tick_seconds"] == 4.0

        # Verify Rule of 5
        assert data["rule_of_five_limit"] == 5

        # Verify enhancement values
        assert data["training_origin_value"] == pytest.approx(0.0833, rel=1e-3)
        assert data["dual_origin_value"] == pytest.approx(0.1667, rel=1e-3)
        assert data["single_origin_value"] == pytest.approx(0.3333, rel=1e-3)
        assert data["invention_origin_l50_value"] == pytest.approx(0.424, rel=1e-3)


# ============================================================================
# Proc Calculation Tests
# ============================================================================


class TestProcCalculation:
    """Tests for POST /api/v1/calculations/enhancements/procs endpoint."""

    def test_basic_proc_calculation(self):
        """Test basic proc chance calculation."""
        request = {
            "ppm": 3.5,
            "recharge_time": 8.0,
            "cast_time": 1.67,
            "area_factor": 1.0,
        }

        response = client.post("/api/v1/calculations/enhancements/procs", json=request)

        assert response.status_code == 200
        data = response.json()

        # PPM × (recharge + cast) / (60 × area)
        # 3.5 × (8.0 + 1.67) / (60 × 1.0) = 3.5 × 9.67 / 60 = 0.5645
        expected_chance = 3.5 * (8.0 + 1.67) / (60.0 * 1.0)
        assert data["chance"] == pytest.approx(expected_chance, rel=1e-3)
        assert data["chance_percent"] == pytest.approx(expected_chance * 100, rel=1e-2)
        assert data["capped"] is False

    def test_proc_cap_at_90_percent(self):
        """Test that proc chance is capped at 90%."""
        request = {
            "ppm": 10.0,  # Very high PPM
            "recharge_time": 120.0,  # Long recharge
            "cast_time": 2.0,
            "area_factor": 1.0,
        }

        response = client.post("/api/v1/calculations/enhancements/procs", json=request)

        assert response.status_code == 200
        data = response.json()

        # Should be capped at 90%
        if data["chance"] >= 0.90:
            assert data["capped"] is True
            assert data["chance"] <= 0.90

    def test_aoe_area_factor(self):
        """Test proc calculation with AoE area factor."""
        request = {
            "ppm": 3.5,
            "recharge_time": 8.0,
            "cast_time": 1.67,
            "area_factor": 4.0,  # AoE modifier
        }

        response = client.post("/api/v1/calculations/enhancements/procs", json=request)

        assert response.status_code == 200
        data = response.json()

        # With area_factor = 4, chance should be 1/4 of single-target
        expected_chance = 3.5 * (8.0 + 1.67) / (60.0 * 4.0)
        assert data["chance"] == pytest.approx(expected_chance, rel=1e-3)


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestErrorHandling:
    """Tests for error handling in calculation endpoints."""

    def test_invalid_archetype(self):
        """Test error handling for invalid archetype."""
        request = {
            "archetype": "InvalidArchetype",  # Not a valid AT
            "defense_bonuses": [],
        }

        response = client.post("/api/v1/calculations/build/defense", json=request)

        # Should return 422 for validation error
        assert response.status_code == 422

    def test_negative_damage(self):
        """Test handling of negative damage values."""
        request = {
            "effects": [
                {
                    "effect_type": "damage",
                    "magnitude": -50.0,  # Negative damage
                    "damage_type": "smashing",
                }
            ],
            "power_type": "click",
        }

        response = client.post("/api/v1/calculations/power/damage", json=request)

        # Should accept but calculate correctly (healing displayed as negative damage)
        assert response.status_code == 200

    def test_invalid_probability(self):
        """Test validation of probability range (0.0 to 1.0)."""
        request = {
            "effects": [
                {
                    "effect_type": "damage",
                    "magnitude": 50.0,
                    "damage_type": "smashing",
                    "probability": 1.5,  # Invalid: > 1.0
                }
            ],
            "power_type": "click",
        }

        response = client.post("/api/v1/calculations/power/damage", json=request)

        # Should return 422 for validation error
        assert response.status_code == 422


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Integration tests combining multiple calculation types."""

    def test_complete_scrapper_build(self):
        """Test a complete Scrapper build with defense, resistance, and damage."""
        # Build totals request
        build_request = {
            "archetype": "Scrapper",
            "defense_bonuses": [
                {"bonuses": {"melee": 0.30}},
                {"bonuses": {"smashing": 0.15, "lethal": 0.15}},
            ],
            "resistance_bonuses": [
                {"bonuses": {"smashing": 0.20, "lethal": 0.20}},
                {"bonuses": {"fire": 0.10, "cold": 0.10}},
            ],
        }

        build_response = client.post(
            "/api/v1/calculations/build/totals", json=build_request
        )
        assert build_response.status_code == 200

        # Power damage request
        power_request = {
            "effects": [
                {
                    "effect_type": "damage",
                    "magnitude": 82.6,
                    "damage_type": "smashing",
                    "probability": 1.0,
                }
            ],
            "power_type": "click",
            "recharge_time": 8.0,
            "cast_time": 1.5,
            "damage_return_mode": "dps",
        }

        power_response = client.post(
            "/api/v1/calculations/power/damage", json=power_request
        )
        assert power_response.status_code == 200

        # Both should succeed
        build_data = build_response.json()
        power_data = power_response.json()

        assert build_data["defense"]["positional"]["melee"] == pytest.approx(
            0.30, rel=1e-3
        )
        assert power_data["total"] > 0
