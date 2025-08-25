"""
Tests for archetype API endpoints.
"""

from app.models import Archetype, Powerset


def test_get_archetypes_empty(client):
    """Test getting archetypes when database is empty."""
    response = client.get("/api/archetypes")
    assert response.status_code == 200
    assert response.json() == []


def test_get_archetypes_with_data(client, sample_archetype):
    """Test getting archetypes with data."""
    response = client.get("/api/archetypes")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Blaster"
    assert data[0]["display_name"] == "Blaster"
    assert data[0]["primary_group"] == "damage"


def test_get_archetypes_pagination(client, db_session):
    """Test archetype pagination."""
    # Create multiple archetypes
    archetypes = [
        Archetype(
            name=f"Archetype{i}",
            display_name=f"Archetype {i}",
            description=f"Test archetype {i}",
            hit_points_base=1000,
            hit_points_max=1606,
            primary_group="damage",
            secondary_group="support",
        )
        for i in range(5)
    ]
    db_session.add_all(archetypes)
    db_session.commit()

    # Test pagination
    response = client.get("/api/archetypes?skip=2&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Archetype2"
    assert data[1]["name"] == "Archetype3"


def test_get_archetype_by_id(client, sample_archetype):
    """Test getting a specific archetype by ID."""
    response = client.get(f"/api/archetypes/{sample_archetype.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Blaster"
    assert data["id"] == sample_archetype.id


def test_get_archetype_not_found(client):
    """Test getting a non-existent archetype."""
    response = client.get("/api/archetypes/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Archetype not found"


def test_get_archetype_powersets(client, sample_archetype, sample_powerset):
    """Test getting powersets for an archetype."""
    response = client.get(f"/api/archetypes/{sample_archetype.id}/powersets")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Fire Blast"
    assert data[0]["powerset_type"] == "primary"


def test_get_archetype_powersets_filtered(client, sample_archetype, db_session):
    """Test getting powersets filtered by type."""
    # Create primary and secondary powersets
    primary = Powerset(
        name="Fire Blast",
        display_name="Fire Blast",
        description="Primary powerset",
        archetype_id=sample_archetype.id,
        powerset_type="primary",
    )
    secondary = Powerset(
        name="Fire Manipulation",
        display_name="Fire Manipulation",
        description="Secondary powerset",
        archetype_id=sample_archetype.id,
        powerset_type="secondary",
    )
    db_session.add_all([primary, secondary])
    db_session.commit()

    # Test filtering by primary
    response = client.get(
        f"/api/archetypes/{sample_archetype.id}/powersets?powerset_type=primary"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Fire Blast"

    # Test filtering by secondary
    response = client.get(
        f"/api/archetypes/{sample_archetype.id}/powersets?powerset_type=secondary"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Fire Manipulation"


def test_get_archetype_powersets_not_found(client):
    """Test getting powersets for non-existent archetype."""
    response = client.get("/api/archetypes/999/powersets")
    assert response.status_code == 404
    assert response.json()["detail"] == "Archetype not found"
