"""
Tests for power API endpoints.
"""

from app.models import Power, PowerPrerequisite


def test_get_power_by_id(client, sample_power):
    """Test getting a specific power by ID."""
    response = client.get(f"/api/powers/{sample_power.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Fire Blast"
    assert data["display_name"] == "Fire Blast"
    assert data["level_available"] == 1
    assert data["damage_scale"] == "1.00"  # Decimal fields are serialized as strings
    assert "prerequisites" in data
    assert data["prerequisites"] == []


def test_get_power_with_prerequisites(
    client, sample_power, sample_powerset, db_session
):
    """Test getting a power with prerequisites."""
    # Create another power that requires the first
    power2 = Power(
        name="Blaze",
        display_name="Blaze",
        description="Close-range fire attack",
        powerset_id=sample_powerset.id,
        power_type="attack",
        target_type="enemy",
        level_available=18,
        accuracy=1.0,
        damage_scale=2.0,
        endurance_cost=10.2,
        recharge_time=10.0,
        activation_time=1.0,
        range_feet=20,
        max_targets=1,
    )
    db_session.add(power2)
    db_session.commit()
    db_session.refresh(power2)

    # Add prerequisite
    prereq = PowerPrerequisite(
        power_id=power2.id, required_power_id=sample_power.id, prerequisite_type="power"
    )
    db_session.add(prereq)
    db_session.commit()

    response = client.get(f"/api/powers/{power2.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Blaze"
    assert len(data["prerequisites"]) == 1
    assert data["prerequisites"][0]["required_power_id"] == sample_power.id
    assert data["prerequisites"][0]["prerequisite_type"] == "power"


def test_get_power_without_prerequisites(client, sample_power):
    """Test getting a power without including prerequisites."""
    response = client.get(f"/api/powers/{sample_power.id}?include_prerequisites=false")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Fire Blast"
    assert data["prerequisites"] == []


def test_get_power_not_found(client):
    """Test getting a non-existent power."""
    response = client.get("/api/powers/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Power not found"


def test_search_powers_by_name(client, sample_power, sample_powerset, db_session):
    """Test searching powers by name."""
    # Add more powers
    powers = [
        Power(
            name="Fire Ball",
            display_name="Fire Ball",
            description="AoE fire attack",
            powerset_id=sample_powerset.id,
            power_type="attack",
            target_type="enemy",
            level_available=2,
        ),
        Power(
            name="Ice Blast",
            display_name="Ice Blast",
            description="Ice attack",
            powerset_id=sample_powerset.id,
            power_type="attack",
            target_type="enemy",
            level_available=1,
        ),
    ]
    db_session.add_all(powers)
    db_session.commit()

    # Search for "fire"
    response = client.get("/api/powers?name=fire")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    names = [p["name"] for p in data]
    assert "Fire Blast" in names
    assert "Fire Ball" in names
    assert "Ice Blast" not in names


def test_search_powers_by_type(client, sample_power, sample_powerset, db_session):
    """Test filtering powers by type."""
    # Add a toggle power
    toggle = Power(
        name="Fire Shield",
        display_name="Fire Shield",
        description="Toggle defense",
        powerset_id=sample_powerset.id,
        power_type="toggle",
        target_type="self",
        level_available=4,
    )
    db_session.add(toggle)
    db_session.commit()

    # Filter by attack powers
    response = client.get("/api/powers?power_type=attack")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2  # Fire Blast and Fire Ball
    names = [p["name"] for p in data]
    assert "Fire Blast" in names
    assert "Fire Ball" in names

    # Filter by toggle powers
    response = client.get("/api/powers?power_type=toggle")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Fire Shield"


def test_search_powers_by_level(client, sample_powerset, db_session):
    """Test filtering powers by level range."""
    # Create powers at different levels
    powers = [
        Power(
            name=f"Power Level {level}",
            display_name=f"Power Level {level}",
            description=f"Power available at level {level}",
            powerset_id=sample_powerset.id,
            power_type="attack",
            target_type="enemy",
            level_available=level,
        )
        for level in [1, 10, 20, 30, 40]
    ]
    db_session.add_all(powers)
    db_session.commit()

    # Filter by min level
    response = client.get("/api/powers?min_level=20")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all(p["level_available"] >= 20 for p in data)

    # Filter by max level
    response = client.get("/api/powers?max_level=20")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all(p["level_available"] <= 20 for p in data)

    # Filter by level range
    response = client.get("/api/powers?min_level=10&max_level=30")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all(10 <= p["level_available"] <= 30 for p in data)


def test_search_powers_pagination(client, sample_powerset, db_session):
    """Test power search pagination."""
    # Create multiple powers
    powers = [
        Power(
            name=f"Power {i}",
            display_name=f"Power {i}",
            description=f"Test power {i}",
            powerset_id=sample_powerset.id,
            power_type="attack",
            target_type="enemy",
            level_available=1,
        )
        for i in range(5)
    ]
    db_session.add_all(powers)
    db_session.commit()

    # Test pagination
    response = client.get("/api/powers?skip=2&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_search_powers_empty(client):
    """Test searching powers when database is empty."""
    response = client.get("/api/powers")
    assert response.status_code == 200
    assert response.json() == []
