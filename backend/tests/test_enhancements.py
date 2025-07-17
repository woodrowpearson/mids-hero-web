"""
Tests for enhancement API endpoints.
"""


from app.models import Enhancement, EnhancementSet, SetBonus


def test_get_enhancements_empty(client):
    """Test getting enhancements when database is empty."""
    response = client.get("/api/enhancements")
    assert response.status_code == 200
    assert response.json() == []


def test_get_enhancements_with_data(client, sample_enhancement):
    """Test getting enhancements with data."""
    response = client.get("/api/enhancements")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Devastation: Accuracy/Damage"
    assert data[0]["enhancement_type"] == "set_piece"
    assert data[0]["level_min"] == 30


def test_get_enhancements_pagination(client, sample_enhancement_set, db_session):
    """Test enhancement pagination."""
    # Create multiple enhancements
    enhancements = [
        Enhancement(
            name=f"Enhancement {i}",
            short_name=f"Enh {i}",
            description=f"Test enhancement {i}",
            enhancement_type="IO",
            level_min=1,
            level_max=50,
            effect_type="damage",
            effect_value=0.25
        )
        for i in range(5)
    ]
    db_session.add_all(enhancements)
    db_session.commit()

    # Test pagination
    response = client.get("/api/enhancements?skip=2&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Enhancement 2"
    assert data[1]["name"] == "Enhancement 3"


def test_get_enhancements_filtered_by_type(client, sample_enhancement, db_session):
    """Test filtering enhancements by type."""
    # Add different types of enhancements
    io_enh = Enhancement(
        name="Damage IO",
        short_name="Dam IO",
        description="Generic damage enhancement",
        enhancement_type="IO",
        level_min=10,
        level_max=50,
        effect_type="damage",
        effect_value=0.425
    )
    so_enh = Enhancement(
        name="Damage SO",
        short_name="Dam SO",
        description="Single origin damage enhancement",
        enhancement_type="SO",
        level_min=22,
        level_max=50,
        effect_type="damage",
        effect_value=0.333
    )
    db_session.add_all([io_enh, so_enh])
    db_session.commit()

    # Filter by IO
    response = client.get("/api/enhancements?enhancement_type=IO")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Damage IO"

    # Filter by SO
    response = client.get("/api/enhancements?enhancement_type=SO")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Damage SO"

    # Filter by set_piece
    response = client.get("/api/enhancements?enhancement_type=set_piece")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Devastation: Accuracy/Damage"


def test_get_enhancement_by_id(client, sample_enhancement):
    """Test getting a specific enhancement by ID."""
    response = client.get(f"/api/enhancements/{sample_enhancement.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Devastation: Accuracy/Damage"
    assert data["id"] == sample_enhancement.id
    assert data["set_id"] == sample_enhancement.set_id


def test_get_enhancement_not_found(client):
    """Test getting a non-existent enhancement."""
    response = client.get("/api/enhancements/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Enhancement not found"


def test_get_enhancement_sets_empty(client):
    """Test getting enhancement sets when database is empty."""
    response = client.get("/api/enhancement-sets")
    assert response.status_code == 200
    assert response.json() == []


def test_get_enhancement_sets_with_data(client, sample_enhancement_set):
    """Test getting enhancement sets with data."""
    response = client.get("/api/enhancement-sets")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Devastation"
    assert data[0]["min_level"] == 30
    assert data[0]["max_level"] == 50


def test_get_enhancement_sets_pagination(client, db_session):
    """Test enhancement set pagination."""
    # Create multiple sets
    sets = [
        EnhancementSet(
            name=f"Set {i}",
            display_name=f"Enhancement Set {i}",
            description=f"Test set {i}",
            min_level=10,
            max_level=50
        )
        for i in range(5)
    ]
    db_session.add_all(sets)
    db_session.commit()

    # Test pagination
    response = client.get("/api/enhancement-sets?skip=1&limit=3")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["name"] == "Set 1"
    assert data[2]["name"] == "Set 3"


def test_get_enhancement_set_by_id(client, sample_enhancement_set):
    """Test getting a specific enhancement set by ID."""
    response = client.get(f"/api/enhancement-sets/{sample_enhancement_set.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Devastation"
    assert "enhancements" in data
    assert "set_bonuses" in data
    assert data["enhancements"] == []
    assert data["set_bonuses"] == []


def test_get_enhancement_set_with_enhancements(client, sample_enhancement_set, sample_enhancement):
    """Test getting an enhancement set with its enhancements."""
    response = client.get(f"/api/enhancement-sets/{sample_enhancement_set.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Devastation"
    assert len(data["enhancements"]) == 1
    assert data["enhancements"][0]["name"] == "Devastation: Accuracy/Damage"


def test_get_enhancement_set_with_bonuses(client, sample_enhancement_set, db_session):
    """Test getting an enhancement set with set bonuses."""
    # Add set bonuses
    bonuses = [
        SetBonus(
            set_id=sample_enhancement_set.id,
            pieces_required=2,
            bonus_type="recovery",
            bonus_value=0.025,
            description="2.5% Recovery"
        ),
        SetBonus(
            set_id=sample_enhancement_set.id,
            pieces_required=3,
            bonus_type="damage",
            bonus_amount=0.03,
            bonus_description="3% Damage"
        ),
        SetBonus(
            set_id=sample_enhancement_set.id,
            pieces_required=4,
            bonus_type="recharge",
            bonus_amount=0.05,
            bonus_description="5% Recharge"
        )
    ]
    db_session.add_all(bonuses)
    db_session.commit()

    response = client.get(f"/api/enhancement-sets/{sample_enhancement_set.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["set_bonuses"]) == 3

    # Bonuses should be ordered by pieces required
    assert data["set_bonuses"][0]["pieces_required"] == 2
    assert data["set_bonuses"][0]["bonus_type"] == "recovery"
    assert data["set_bonuses"][1]["pieces_required"] == 3
    assert data["set_bonuses"][2]["pieces_required"] == 4


def test_get_enhancement_set_without_related_data(client, sample_enhancement_set, sample_enhancement, db_session):
    """Test getting an enhancement set without related data."""
    # Add bonus
    bonus = SetBonus(
        set_id=sample_enhancement_set.id,
        pieces_required=2,
        bonus_type="recovery",
        bonus_amount=0.025,
        bonus_description="2.5% Recovery"
    )
    db_session.add(bonus)
    db_session.commit()

    response = client.get(
        f"/api/enhancement-sets/{sample_enhancement_set.id}?include_enhancements=false&include_bonuses=false"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["enhancements"] == []
    assert data["set_bonuses"] == []


def test_get_enhancement_set_not_found(client):
    """Test getting a non-existent enhancement set."""
    response = client.get("/api/enhancement-sets/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Enhancement set not found"
