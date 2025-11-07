import pytest
from pathlib import Path
from app.data_import.json_importer import JSONDataImporter


@pytest.fixture
def importer():
    return JSONDataImporter()


def test_json_importer_initialization(importer):
    """Test that JSONDataImporter initializes"""
    assert importer is not None
    assert hasattr(importer, 'import_archetypes')


@pytest.mark.asyncio
async def test_import_archetypes_from_manifest(importer, tmp_path):
    """Test importing archetypes from JSON manifest"""
    # Create test manifest
    manifest = tmp_path / "manifest.json"
    manifest.write_text('{"archetypes": []}')

    result = await importer.import_archetypes(manifest)
    assert result['success'] is True
