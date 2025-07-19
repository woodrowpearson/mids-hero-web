"""Tests for data import functionality."""

import json
import tempfile
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.data_import import (
    ArchetypeImporter,
    EnhancementImporter,
    RecipeImporter,
    SalvageImporter,
)
from app.database import Base
from app.models import Archetype, Salvage


@pytest.fixture
def test_db():
    """Create a test database."""
    # Use a file-based SQLite database for testing to share across connections
    db_path = tempfile.mktemp(suffix=".db")
    db_url = f"sqlite:///{db_path}"

    engine = create_engine(db_url)
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    yield session, db_url

    session.close()
    engine.dispose()
    # Clean up the database file
    import os

    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def temp_json_file():
    """Create temporary JSON file for testing."""

    def _create_file(data):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            return Path(f.name)

    return _create_file


class TestArchetypeImporter:
    """Test archetype importer."""

    def test_import_archetypes(self, test_db, temp_json_file):
        """Test importing archetype data."""
        session, db_url = test_db

        # Create test data
        test_data = {
            "archetypes": [
                {"name": "Blaster", "origins": ["Magic", "Science", "Technology"]},
                {"name": "Controller", "origins": ["Magic", "Science", "Technology"]},
            ]
        }

        json_file = temp_json_file(test_data)

        # Import data
        importer = ArchetypeImporter(db_url)
        importer.import_data(json_file)

        # Verify import - check from importer directly to avoid detached session issues
        assert importer.imported_count == 2
        assert len(importer.errors) == 0

        # Check database
        archetypes = session.query(Archetype).all()
        assert len(archetypes) == 2
        assert archetypes[0].name == "Blaster"
        assert archetypes[1].name == "Controller"

        # Cleanup
        json_file.unlink()

    def test_archetype_transform(self):
        """Test archetype data transformation."""
        importer = ArchetypeImporter("sqlite:///:memory:")

        raw_data = {"name": "Scrapper", "origins": ["Natural", "Magic"]}

        transformed = importer.transform_data(raw_data)

        assert transformed["name"] == "Scrapper"
        assert transformed["primary_group"] == "damage"
        assert transformed["secondary_group"] == "defense"
        assert transformed["hit_points_base"] == 1339
        assert transformed["hit_points_max"] == 2088


class TestSalvageImporter:
    """Test salvage importer."""

    def test_import_salvage(self, test_db, temp_json_file):
        """Test importing salvage data."""
        session, db_url = test_db

        # Create test data
        test_data = {
            "salvage": [
                "S_InanimateCarbonRod",
                "Inanimate Carbon Rod",
                "S_HumanBloodSample",
                "Human Blood Sample",
            ]
        }

        json_file = temp_json_file(test_data)

        # Import data
        importer = SalvageImporter(db_url)
        importer.import_data(json_file)

        # Verify import - check from importer directly to avoid detached session issues
        assert importer.imported_count == 2
        assert len(importer.errors) == 0

        # Check database
        salvage_items = session.query(Salvage).all()
        assert len(salvage_items) == 2
        assert salvage_items[0].internal_name == "InanimateCarbonRod"
        assert salvage_items[0].display_name == "Inanimate Carbon Rod"

        # Cleanup
        json_file.unlink()

    def test_salvage_type_determination(self):
        """Test salvage type determination."""
        importer = SalvageImporter("sqlite:///:memory:")

        # Test common salvage
        assert (
            importer._determine_salvage_type("Simple Chemical", "S_SimpleChemical")
            == "common"
        )

        # Test uncommon salvage
        assert (
            importer._determine_salvage_type("Complex Chemical", "S_ComplexChemical")
            == "uncommon"
        )

        # Test rare salvage
        assert (
            importer._determine_salvage_type("Synthetic Enzyme", "S_SyntheticEnzyme")
            == "rare"
        )


class TestEnhancementImporter:
    """Test enhancement importer."""

    def test_enhancement_type_determination(self):
        """Test enhancement type determination."""
        importer = EnhancementImporter("sqlite:///:memory:")

        assert importer._determine_enhancement_type("Invention: Damage") == "IO"
        assert (
            importer._determine_enhancement_type("Devastation: Accuracy/Damage")
            == "set_piece"
        )
        assert importer._determine_enhancement_type("Hamidon Enhancement") == "HamiO"

    def test_parse_bonus_values(self):
        """Test parsing bonus values from description."""
        importer = EnhancementImporter("sqlite:///:memory:")

        bonuses = importer._parse_bonus_values(
            "Increases accuracy by 26.5% and damage by 26.5%"
        )
        assert bonuses.get("accuracy") == 26.5
        assert bonuses.get("damage") == 26.5

        bonuses = importer._parse_bonus_values("Endurance reduction 33%")
        assert bonuses.get("endurance") == 33.0


class TestRecipeImporter:
    """Test recipe importer."""

    def test_recipe_type_determination(self):
        """Test recipe type determination."""
        importer = RecipeImporter("sqlite:///:memory:")

        assert importer._determine_recipe_type("Common IO Recipe", None) == "common"
        assert importer._determine_recipe_type("Rare Recipe", None) == "rare"
        assert importer._determine_recipe_type("Purple Recipe", None) == "very_rare"
        assert (
            importer._determine_recipe_type("Recipe", "Devastation: Damage")
            == "very_rare"
        )

    def test_parse_crafting_cost(self):
        """Test crafting cost calculation."""
        importer = RecipeImporter("sqlite:///:memory:")

        recipe_data = {"recipe_type": "common", "level_min": 20}
        normal, premium = importer._parse_crafting_cost(recipe_data)

        assert normal == 10000  # 5000 * (20/10)
        assert premium == 50000  # 25000 * (20/10)
