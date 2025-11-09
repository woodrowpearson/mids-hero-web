import pytest
import json
from pathlib import Path
from app.data_import.importers.power_importer import PowerImporter
from app.models import Powerset, Power, Archetype


@pytest.fixture
def sample_archetype(db_session):
    """Create sample archetype for testing"""
    archetype = Archetype(
        name="blaster",
        display_name="Blaster",
        primary_category="ranged_damage",
        secondary_category="manipulation"
    )
    db_session.add(archetype)
    db_session.commit()
    return archetype


@pytest.fixture
def sample_powerset_data(tmp_path):
    """Create sample powerset with index.json"""
    powerset_dir = tmp_path / "blaster_ranged" / "fire_blast"
    powerset_dir.mkdir(parents=True)

    powerset_data = {
        "name": "Fire_Blast",
        "display_name": "Fire Blast",
        "display_fullname": "Blaster Ranged.Fire Blast",
        "display_help": "Fire Blast allows you to blast fire at foes",
        "display_short_help": "Fire Blast",
        "icon": "fire_blast_set.png",
        "requires": "",
        "available_level": [0, 0, 1, 5, 7],
        "power_names": [
            "Blaster_Ranged.Fire_Blast.Flares",
            "Blaster_Ranged.Fire_Blast.Fire_Blast"
        ],
        "power_display_names": ["Flares", "Fire Blast"],
        "power_short_helps": ["Ranged DMG", "Ranged DMG"]
    }

    index_file = powerset_dir / "index.json"
    index_file.write_text(json.dumps(powerset_data, indent=2))

    return powerset_dir


@pytest.fixture
def importer(db_session):
    return PowerImporter(db_session)


@pytest.mark.asyncio
async def test_import_powerset(importer, sample_powerset_data, sample_archetype, db_session):
    """Test importing a powerset from directory"""
    result = await importer.import_powerset(sample_powerset_data, sample_archetype.id)

    assert result['success'] is True
    assert result['powersets_imported'] == 1

    # Verify powerset in database
    powerset = db_session.query(Powerset).filter_by(name="Fire_Blast").first()
    assert powerset is not None
    assert powerset.display_name == "Fire Blast"
    assert powerset.archetype_id == sample_archetype.id
    assert powerset.display_fullname == "Blaster Ranged.Fire Blast"


@pytest.mark.asyncio
async def test_import_duplicate_powerset_skips(importer, sample_powerset_data, sample_archetype, db_session):
    """Test that importing duplicate powerset is skipped"""
    # Import once
    await importer.import_powerset(sample_powerset_data, sample_archetype.id)

    # Import again - should skip
    result = await importer.import_powerset(sample_powerset_data, sample_archetype.id)

    assert result['success'] is True
    assert result['skipped'] == 1
    assert db_session.query(Powerset).filter_by(name="Fire_Blast").count() == 1


@pytest.fixture
def sample_power_json(tmp_path):
    """Create sample power JSON file"""
    power_data = {
        "name": "Fire_Blast",
        "display_name": "Fire Blast",
        "display_help": "Hurl a blast of fire at your target",
        "display_short_help": "Ranged DMG(Fire)",
        "type": "Click",
        "available_level": 1,
        "icon": "fire_blast.png",
        "accuracy": 1.0,
        "activation_time": 1.17,
        "recharge_time": 4.0,
        "endurance_cost": 5.2,
        "range": 80,
        "target_type": "Foe",
        "max_boosts": 6,
        "boosts_allowed": ["Enhance Damage", "Enhance Accuracy"],
        "effects": [
            {"type": "damage", "damage_type": "fire", "scale": 1.0}
        ]
    }

    power_file = tmp_path / "fire_blast.json"
    power_file.write_text(json.dumps(power_data, indent=2))
    return power_file


@pytest.fixture
def sample_powerset(db_session, sample_archetype):
    """Create sample powerset for testing"""
    powerset = Powerset(
        name="Fire_Blast",
        display_name="Fire Blast",
        archetype_id=sample_archetype.id,
        powerset_type="primary"
    )
    db_session.add(powerset)
    db_session.commit()
    return powerset


@pytest.mark.asyncio
async def test_import_individual_power(importer, sample_power_json, sample_powerset, db_session):
    """Test importing an individual power"""
    result = await importer.import_power(sample_power_json, sample_powerset.id)

    assert result['success'] is True
    assert result['imported'] == 1

    # Verify power in database
    power = db_session.query(Power).filter_by(name="Fire_Blast").first()
    assert power is not None
    assert power.display_name == "Fire Blast"
    assert power.powerset_id == sample_powerset.id
    assert power.type == "Click"
    assert power.accuracy == 1.0


@pytest.mark.asyncio
async def test_import_duplicate_power_skips(importer, sample_power_json, sample_powerset, db_session):
    """Test that importing duplicate power is skipped"""
    # Import once
    await importer.import_power(sample_power_json, sample_powerset.id)

    # Import again - should skip
    result = await importer.import_power(sample_power_json, sample_powerset.id)

    assert result['success'] is True
    assert result['skipped'] == 1
    assert db_session.query(Power).filter_by(name="Fire_Blast").count() == 1
