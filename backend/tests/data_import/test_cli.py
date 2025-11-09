import pytest
from pathlib import Path
from app.data_import.cli import import_archetypes, import_enhancements


@pytest.mark.asyncio
async def test_cli_import_archetypes(db_session, tmp_path):
    """Test CLI archetype import function"""
    # Create test directory with JSON
    archetype_dir = tmp_path / "archetypes"
    archetype_dir.mkdir()

    result = await import_archetypes(str(archetype_dir), db_session)
    assert 'total_imported' in result
    assert result['total_imported'] == 0  # Empty directory


@pytest.mark.asyncio
async def test_cli_import_enhancements(db_session, tmp_path):
    """Test CLI enhancement import function"""
    # Create test directory
    enhancement_dir = tmp_path / "boost_sets"
    enhancement_dir.mkdir()

    result = await import_enhancements(str(enhancement_dir), db_session)
    assert 'total_sets' in result
    assert result['total_sets'] == 0  # Empty directory
