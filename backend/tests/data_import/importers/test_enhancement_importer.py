import json

import pytest

from app.data_import.importers.enhancement_importer import EnhancementImporter
from app.models import EnhancementSet


@pytest.fixture
def sample_boost_set_json(tmp_path):
    """Create sample enhancement set JSON"""
    boost_set_data = {
        "name": "Crushing Impact",
        "display_name": "Crushing Impact",
        "group_name": "Stuns",
        "min_level": 15,
        "max_level": 50,
        "bonuses": [
            {
                "min": 2,
                "max": 2,
                "effects": [{"type": "accuracy", "value": 0.07}]
            },
            {
                "min": 3,
                "max": 3,
                "effects": [{"type": "recharge", "value": 0.05}]
            }
        ],
        "boost_lists": [
            ["Crushing_Impact.Crushing_Impact.Acc_Dmg"],
            ["Crushing_Impact.Crushing_Impact.Dmg_EndRdx"]
        ]
    }

    boost_set_file = tmp_path / "crushing_impact.json"
    boost_set_file.write_text(json.dumps(boost_set_data, indent=2))
    return boost_set_file


@pytest.fixture
def importer(db_session):
    return EnhancementImporter(db_session)


@pytest.mark.asyncio
async def test_import_enhancement_set(importer, sample_boost_set_json, db_session):
    """Test importing an enhancement set"""
    result = await importer.import_from_file(sample_boost_set_json)

    assert result['success'] is True
    assert result['sets_imported'] == 1

    # Verify set in database
    boost_set = db_session.query(EnhancementSet).filter_by(
        name="Crushing Impact"
    ).first()
    assert boost_set is not None
    assert boost_set.display_name == "Crushing Impact"
    assert boost_set.min_level == 15
    assert boost_set.group_name == "Stuns"


@pytest.mark.asyncio
async def test_import_duplicate_set_skips(importer, sample_boost_set_json, db_session):
    """Test that importing duplicate enhancement set is skipped"""
    # Import once
    await importer.import_from_file(sample_boost_set_json)

    # Import again - should skip
    result = await importer.import_from_file(sample_boost_set_json)

    assert result['success'] is True
    assert result['skipped'] == 1
    assert db_session.query(EnhancementSet).filter_by(name="Crushing Impact").count() == 1
