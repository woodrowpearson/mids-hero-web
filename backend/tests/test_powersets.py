"""
Tests for powerset API endpoints.
"""

import pytest
from sqlalchemy.orm import Session

from app.models import Power


def test_get_powerset_by_id(client, sample_powerset):
    """Test getting a specific powerset by ID."""
    response = client.get(f"/api/powersets/{sample_powerset.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Fire Blast"
    assert data["display_name"] == "Fire Blast"
    assert "powers" in data
    assert data["powers"] == []  # No powers added yet


def test_get_powerset_with_powers(client, sample_powerset, sample_power):
    """Test getting a powerset with its powers."""
    response = client.get(f"/api/powersets/{sample_powerset.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Fire Blast"
    assert len(data["powers"]) == 1
    assert data["powers"][0]["name"] == "Fire Blast"
    assert data["powers"][0]["level_available"] == 1


def test_get_powerset_without_powers(client, sample_powerset, sample_power):
    """Test getting a powerset without including powers."""
    response = client.get(f"/api/powersets/{sample_powerset.id}?include_powers=false")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Fire Blast"
    assert data["powers"] == []


def test_get_powerset_not_found(client):
    """Test getting a non-existent powerset."""
    response = client.get("/api/powersets/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Powerset not found"


def test_get_powerset_powers(client, sample_powerset, sample_power, db_session):
    """Test getting all powers in a powerset."""
    # Add another power
    power2 = Power(
        name="Fire Ball",
        display_name="Fire Ball",
        description="Hurl a fire ball that explodes",
        powerset_id=sample_powerset.id,
        power_type="click",
        level_available=2,
        requires_tokens=1,
        accuracy_base=1.0,
        damage_base=150.0,
        endurance_cost=8.5,
        recharge_time=16.0,
        activation_time=1.0,
        range_base=80.0,
        effect_area="aoe",
        max_targets=16,
        radius=15.0
    )
    db_session.add(power2)
    db_session.commit()
    
    response = client.get(f"/api/powersets/{sample_powerset.id}/powers")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    
    # Powers should be returned in order
    assert data[0]["name"] == "Fire Blast"
    assert data[0]["level_available"] == 1
    assert data[1]["name"] == "Fire Ball"
    assert data[1]["level_available"] == 2


def test_get_powerset_powers_empty(client, sample_powerset):
    """Test getting powers from a powerset with no powers."""
    response = client.get(f"/api/powersets/{sample_powerset.id}/powers")
    assert response.status_code == 200
    assert response.json() == []


def test_get_powerset_powers_not_found(client):
    """Test getting powers from non-existent powerset."""
    response = client.get("/api/powersets/999/powers")
    assert response.status_code == 404
    assert response.json()["detail"] == "Powerset not found"