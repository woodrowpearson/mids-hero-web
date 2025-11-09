"""Integration tests for end-to-end JSON import pipeline"""
import pytest
import json
from pathlib import Path
from app.data_import.importers.archetype_importer import ArchetypeImporter
from app.data_import.importers.enhancement_importer import EnhancementImporter
from app.data_import.importers.power_importer import PowerImporter
from app.models import Archetype, EnhancementSet, Powerset, Power


@pytest.fixture
def sample_data_dir(tmp_path):
    """Create a complete sample data structure"""
    # Create archetypes
    arch_dir = tmp_path / "archetypes"
    arch_dir.mkdir()

    archetype_data = {
        "name": "blaster",
        "display_name": "Blaster",
        "display_help": "Ranged damage specialist",
        "class_key": "class_blaster",
        "primary_category": "ranged_damage",
        "secondary_category": "manipulation",
        "is_villain": False,
        "attrib_base": {"hit_points": 100}
    }
    (arch_dir / "blaster.json").write_text(json.dumps(archetype_data))

    # Create enhancement set
    boost_dir = tmp_path / "boost_sets"
    boost_dir.mkdir()

    boost_data = {
        "name": "Thunderstrike",
        "display_name": "Thunderstrike",
        "group_name": "Ranged Damage",
        "min_level": 30,
        "max_level": 50,
        "bonuses": [{"min": 2, "effects": [{"type": "accuracy", "value": 0.07}]}]
    }
    (boost_dir / "thunderstrike.json").write_text(json.dumps(boost_data))

    # Create powerset
    powers_dir = tmp_path / "powers" / "blaster_ranged" / "fire_blast"
    powers_dir.mkdir(parents=True)

    powerset_data = {
        "name": "Fire_Blast",
        "display_name": "Fire Blast",
        "display_fullname": "Blaster Ranged.Fire Blast",
        "power_names": ["Blaster_Ranged.Fire_Blast.Flares"],
        "available_level": [0]
    }
    (powers_dir / "index.json").write_text(json.dumps(powerset_data))

    # Create power
    power_data = {
        "name": "Flares",
        "display_name": "Flares",
        "type": "Click",
        "available_level": 1,
        "accuracy": 1.0,
        "activation_time": 1.0,
        "endurance_cost": 4.2
    }
    (powers_dir / "flares.json").write_text(json.dumps(power_data))

    return tmp_path


@pytest.mark.asyncio
async def test_end_to_end_import(sample_data_dir, db_session):
    """Test complete import pipeline from JSON to database"""

    # Step 1: Import archetypes
    arch_importer = ArchetypeImporter(db_session)
    arch_result = await arch_importer.import_from_directory(sample_data_dir / "archetypes")

    assert arch_result['success'] is True
    assert arch_result['imported'] == 1

    # Verify archetype in DB
    archetype = db_session.query(Archetype).filter_by(name="blaster").first()
    assert archetype is not None
    assert archetype.display_name == "Blaster"

    # Step 2: Import enhancement sets
    enh_importer = EnhancementImporter(db_session)
    enh_result = await enh_importer.import_from_directory(sample_data_dir / "boost_sets")

    assert enh_result['success'] is True
    assert enh_result['sets_imported'] == 1

    # Verify enhancement set in DB
    boost_set = db_session.query(EnhancementSet).filter_by(name="Thunderstrike").first()
    assert boost_set is not None
    assert boost_set.min_level == 30

    # Step 3: Import powerset with powers
    power_importer = PowerImporter(db_session)
    powerset_dir = sample_data_dir / "powers" / "blaster_ranged" / "fire_blast"
    ps_result = await power_importer.import_powerset_with_powers(powerset_dir, archetype.id)

    assert ps_result['success'] is True
    assert ps_result['powersets_imported'] == 1
    assert ps_result['powers_imported'] == 1

    # Verify powerset in DB
    powerset = db_session.query(Powerset).filter_by(name="Fire_Blast").first()
    assert powerset is not None
    assert powerset.archetype_id == archetype.id
    assert powerset.display_name == "Fire Blast"

    # Verify power in DB
    power = db_session.query(Power).filter_by(name="Flares").first()
    assert power is not None
    assert power.powerset_id == powerset.id
    assert power.type == "Click"
    assert power.accuracy == 1.0

    # Verify relationships
    assert len(archetype.powersets) == 1
    assert archetype.powersets[0].name == "Fire_Blast"
    assert len(powerset.powers) == 1
    assert powerset.powers[0].name == "Flares"


@pytest.mark.asyncio
async def test_reimport_is_idempotent(sample_data_dir, db_session):
    """Test that re-importing the same data is idempotent"""

    # Import once
    arch_importer = ArchetypeImporter(db_session)
    result1 = await arch_importer.import_from_directory(sample_data_dir / "archetypes")
    assert result1['imported'] == 1

    # Import again - should skip
    result2 = await arch_importer.import_from_directory(sample_data_dir / "archetypes")
    assert result2['skipped'] == 1
    assert result2['imported'] == 0

    # Verify only one archetype in DB
    count = db_session.query(Archetype).filter_by(name="blaster").count()
    assert count == 1
