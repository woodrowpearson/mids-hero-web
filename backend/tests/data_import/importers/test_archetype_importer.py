import pytest
import json
from pathlib import Path
from app.data_import.importers.archetype_importer import ArchetypeImporter
from app.models import Archetype


@pytest.fixture
def sample_archetype_json(tmp_path):
    """Create sample archetype JSON file"""
    archetype_data = {
        "name": "Blaster",
        "display_name": "Blaster",
        "display_help": "Ranged damage specialist",
        "display_short_help": "Deals heavy ranged damage",
        "icon": "blaster.png",
        "class_key": "class_blaster",
        "primary_category": "ranged_damage",
        "secondary_category": "manipulation",
        "default_rank": "level_1",
        "is_villain": False,
        "attrib_base": {"hit_points": 100, "endurance": 100}
    }

    archetype_file = tmp_path / "blaster.json"
    archetype_file.write_text(json.dumps(archetype_data, indent=2))
    return archetype_file


@pytest.fixture
def importer(db_session):
    return ArchetypeImporter(db_session)


@pytest.mark.asyncio
async def test_import_single_archetype(importer, sample_archetype_json, db_session):
    """Test importing a single archetype from JSON"""
    result = await importer.import_from_file(sample_archetype_json)

    assert result['success'] is True
    assert result['imported'] == 1

    # Verify in database
    archetype = db_session.query(Archetype).filter_by(name="Blaster").first()
    assert archetype is not None
    assert archetype.name == "Blaster"
    assert archetype.display_name == "Blaster"
    assert archetype.class_key == "class_blaster"


@pytest.mark.asyncio
async def test_import_duplicate_archetype_skips(importer, sample_archetype_json, db_session):
    """Test that importing duplicate archetype is skipped"""
    # Import once
    await importer.import_from_file(sample_archetype_json)

    # Import again - should skip
    result = await importer.import_from_file(sample_archetype_json)

    assert result['success'] is True
    assert result['skipped'] == 1
    assert db_session.query(Archetype).filter_by(name="Blaster").count() == 1
