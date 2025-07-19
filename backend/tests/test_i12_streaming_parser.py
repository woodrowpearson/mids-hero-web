"""Tests for I12 power data streaming JSON parser."""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.data_import.i12_streaming_parser import (
    I12StreamingParser,
    PowerDataProcessor,
    StreamingJsonReader,
)
from app.database import Base
from app.models import Archetype, Power, Powerset


@pytest.fixture
def test_db():
    """Create a test database for streaming parser tests."""
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
def sample_i12_power_data():
    """Sample I12 power data for testing."""
    return {
        "Name": "Fire Blast",
        "InternalName": "Blaster_Ranged.Fire_Blast.Blast",
        "DisplayName": "Fire Blast",
        "Description": "You can hurl a blast of fire at a targeted foe.",
        "PowersetFullName": "Blaster.Fire_Blast",
        "PowersetName": "Fire Blast",
        "ArchetypeName": "Blaster",
        "Level": 1,
        "PowerType": "Click",
        "TargetType": "Enemy",
        "Range": 80.0,
        "Accuracy": 1.0,
        "EnduranceCost": 5.2,
        "RechargeTime": 4.0,
        "ActivationTime": 1.67,
        "MaxTargets": 1,
        "Effects": [
            {
                "EffectType": "Damage",
                "DamageType": "Fire",
                "Scale": 1.0,
                "Duration": 0.0,
                "Chance": 1.0,
                "AttributeModifiers": [
                    {
                        "Attribute": "kDamage",
                        "Aspect": "Cur",
                        "Modifier": "kDamage",
                        "Scale": 1.0,
                        "nMagnitude": -1.0,
                        "nDuration": 0.0,
                    }
                ],
            }
        ],
        "Requirements": {"Level": 1, "PowersRequired": [], "PowersDisallowed": []},
        "EnhancementTypes": [
            "Accuracy",
            "Damage",
            "EnduranceReduction",
            "Range",
            "Recharge",
        ],
    }


@pytest.fixture
def large_json_test_file():
    """Create a large JSON file for streaming tests."""

    def _create_file(num_records: int = 1000) -> Path:
        """Create a test JSON file with specified number of records."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            # Write opening bracket and first record
            f.write("[\n")

            for i in range(num_records):
                power_data = {
                    "Name": f"Test Power {i}",
                    "InternalName": f"Test.Power.{i}",
                    "DisplayName": f"Test Power {i}",
                    "Description": f"Test power description {i}",
                    "PowersetFullName": f"Archetype.Test_Powerset_{i % 10}",
                    "PowersetName": f"Test Powerset {i % 10}",
                    "ArchetypeName": f"Test Archetype {i % 3}",
                    "Level": (i % 50) + 1,
                    "PowerType": "Click",
                    "TargetType": "Enemy",
                    "Range": 80.0,
                    "Accuracy": 1.0,
                    "EnduranceCost": 5.0 + (i % 10),
                    "RechargeTime": 4.0 + (i % 20),
                    "ActivationTime": 1.67,
                    "MaxTargets": 1,
                    "Effects": [],
                    "Requirements": {"Level": (i % 50) + 1},
                    "EnhancementTypes": ["Accuracy", "Damage"],
                }

                if i > 0:
                    f.write(",\n")
                json.dump(power_data, f, indent=2)

            f.write("\n]")
            return Path(f.name)

    return _create_file


class TestStreamingJsonReader:
    """Test the streaming JSON reader component."""

    def test_read_json_chunks_small_file(self, large_json_test_file):
        """Test reading small JSON file in chunks."""
        json_file = large_json_test_file(10)
        reader = StreamingJsonReader(chunk_size=3)

        chunks = list(reader.read_chunks(json_file))

        # Should have 4 chunks: [0,1,2], [3,4,5], [6,7,8], [9]
        assert len(chunks) == 4
        assert len(chunks[0]) == 3
        assert len(chunks[1]) == 3
        assert len(chunks[2]) == 3
        assert len(chunks[3]) == 1

        # Verify first chunk content
        assert chunks[0][0]["Name"] == "Test Power 0"
        assert chunks[0][1]["Name"] == "Test Power 1"
        assert chunks[0][2]["Name"] == "Test Power 2"

        # Cleanup
        json_file.unlink()

    def test_read_json_chunks_progress_callback(self, large_json_test_file):
        """Test progress callback during chunk reading."""
        json_file = large_json_test_file(50)
        reader = StreamingJsonReader(chunk_size=10)

        progress_calls = []

        def progress_callback(processed: int, total: int, percentage: float):
            progress_calls.append((processed, total, percentage))

        chunks = list(
            reader.read_chunks(json_file, progress_callback=progress_callback)
        )

        # Verify chunks
        assert len(chunks) == 5  # 50 records / 10 per chunk

        # Verify progress calls
        assert len(progress_calls) == 5
        assert progress_calls[0] == (10, 50, 20.0)
        assert progress_calls[1] == (20, 50, 40.0)
        assert progress_calls[-1] == (50, 50, 100.0)

        # Cleanup
        json_file.unlink()

    def test_read_empty_file(self):
        """Test handling of empty JSON file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("[]")
            empty_file = Path(f.name)

        reader = StreamingJsonReader()
        chunks = list(reader.read_chunks(empty_file))

        assert len(chunks) == 0

        # Cleanup
        empty_file.unlink()

    def test_read_malformed_json(self):
        """Test handling of malformed JSON file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write('{"invalid": json,}')
            malformed_file = Path(f.name)

        reader = StreamingJsonReader()

        with pytest.raises(json.JSONDecodeError):
            list(reader.read_chunks(malformed_file))

        # Cleanup
        malformed_file.unlink()


class TestPowerDataProcessor:
    """Test the power data processor component."""

    def test_transform_i12_power_data(self, sample_i12_power_data):
        """Test transformation of I12 power data format."""
        processor = PowerDataProcessor()

        # Mock powerset cache
        processor._powerset_cache = {"Fire Blast": 1}

        transformed = processor.transform_data(sample_i12_power_data)

        assert transformed["name"] == "Fire Blast"
        assert transformed["internal_name"] == "Blaster_Ranged.Fire_Blast.Blast"
        assert transformed["display_name"] == "Fire Blast"
        assert transformed["powerset_id"] == 1
        assert transformed["level_available"] == 1
        assert transformed["power_type"] == "attack"
        assert transformed["target_type"] == "enemy"
        assert transformed["accuracy"] == 1.0
        assert transformed["endurance_cost"] == 5.2
        assert transformed["recharge_time"] == 4.0
        assert transformed["activation_time"] == 1.67
        assert transformed["range_feet"] == 80
        assert transformed["max_targets"] == 1
        assert transformed["effects"] == sample_i12_power_data["Effects"]

    def test_determine_power_type_from_i12_data(self):
        """Test power type determination from I12 data."""
        processor = PowerDataProcessor()

        # Test attack power
        attack_data = {
            "PowerType": "Click",
            "TargetType": "Enemy",
            "Effects": [{"EffectType": "Damage"}],
        }
        assert processor._determine_power_type(attack_data) == "attack"

        # Test defense power
        defense_data = {
            "PowerType": "Toggle",
            "TargetType": "Self",
            "Effects": [{"EffectType": "Defense"}],
        }
        assert processor._determine_power_type(defense_data) == "defense"

        # Test control power
        control_data = {
            "PowerType": "Click",
            "TargetType": "Enemy",
            "Effects": [{"EffectType": "Hold"}],
        }
        assert processor._determine_power_type(control_data) == "control"

    def test_validate_required_fields(self):
        """Test validation of required fields."""
        processor = PowerDataProcessor()

        # Valid data
        valid_data = {
            "name": "Test Power",
            "powerset_id": 1,
            "level_available": 1,
            "accuracy": 1.0,
            "endurance_cost": 5.0,
            "recharge_time": 4.0,
            "activation_time": 1.0,
        }
        assert processor.validate_data(valid_data) is True

        # Missing required field
        invalid_data = {"powerset_id": 1}
        assert processor.validate_data(invalid_data) is False

        # Invalid numeric value
        invalid_numeric = {
            "name": "Test Power",
            "powerset_id": 1,
            "level_available": -1,  # Invalid
        }
        assert processor.validate_data(invalid_numeric) is False


class TestI12StreamingParser:
    """Test the complete I12 streaming parser."""

    def setup_method(self):
        """Set up test database with sample data."""
        self.test_archetype = None
        self.test_powerset = None

    def test_memory_usage_during_processing(self, test_db, large_json_test_file):
        """Test memory usage stays within limits during large file processing."""
        session, db_url = test_db

        # Create test archetype and powerset
        archetype = Archetype(name="Test Archetype 0", display_name="Test Archetype 0")
        session.add(archetype)
        session.commit()

        powerset = Powerset(
            name="Test Powerset 0",
            display_name="Test Powerset 0",
            archetype_id=archetype.id,
            powerset_type="primary",
        )
        session.add(powerset)
        session.commit()

        # Create large test file (1000 records)
        json_file = large_json_test_file(1000)

        parser = I12StreamingParser(db_url, batch_size=100, chunk_size=50)

        # Track memory usage (mock for testing)
        with patch("psutil.Process") as mock_process:
            mock_memory_info = Mock()
            mock_memory_info.memory_info.return_value.rss = 500 * 1024 * 1024  # 500MB
            mock_process.return_value = mock_memory_info

            # Should not raise memory exception
            parser.import_data(json_file)

        # Verify data was processed
        assert parser.processed_count > 0

        # Cleanup
        json_file.unlink()

    def test_progress_tracking(self, test_db, large_json_test_file):
        """Test progress tracking during import."""
        session, db_url = test_db

        # Setup test data
        archetype = Archetype(name="Test Archetype 0", display_name="Test Archetype 0")
        session.add(archetype)
        session.commit()

        powerset = Powerset(
            name="Test Powerset 0",
            display_name="Test Powerset 0",
            archetype_id=archetype.id,
            powerset_type="primary",
        )
        session.add(powerset)
        session.commit()

        json_file = large_json_test_file(100)

        parser = I12StreamingParser(db_url, batch_size=25, chunk_size=20)

        progress_updates = []

        def progress_callback(processed: int, total: int, percentage: float):
            progress_updates.append((processed, total, percentage))

        parser.import_data(json_file, progress_callback=progress_callback)

        # Verify progress tracking
        assert len(progress_updates) > 0
        assert progress_updates[-1][0] == 100  # Final processed count
        assert progress_updates[-1][1] == 100  # Total count
        assert progress_updates[-1][2] == 100.0  # Final percentage

        # Cleanup
        json_file.unlink()

    def test_error_handling_and_recovery(self, test_db, large_json_test_file):
        """Test error handling during import with some invalid records."""
        session, db_url = test_db

        # Create mixed valid/invalid test data
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            test_data = [
                # Valid record
                {
                    "Name": "Valid Power",
                    "InternalName": "Valid.Power",
                    "PowersetFullName": "Archetype.Valid_Powerset",
                    "PowersetName": "Valid Powerset",
                    "ArchetypeName": "Valid Archetype",
                    "Level": 1,
                    "PowerType": "Click",
                    "TargetType": "Enemy",
                    "Accuracy": 1.0,
                    "EnduranceCost": 5.0,
                    "RechargeTime": 4.0,
                    "ActivationTime": 1.0,
                },
                # Invalid record (missing required fields)
                {
                    "Name": "Invalid Power"
                    # Missing most required fields
                },
                # Another valid record
                {
                    "Name": "Another Valid Power",
                    "InternalName": "Another.Valid.Power",
                    "PowersetFullName": "Archetype.Valid_Powerset",
                    "PowersetName": "Valid Powerset",
                    "ArchetypeName": "Valid Archetype",
                    "Level": 2,
                    "PowerType": "Click",
                    "TargetType": "Self",
                    "Accuracy": 1.0,
                    "EnduranceCost": 3.0,
                    "RechargeTime": 2.0,
                    "ActivationTime": 1.0,
                },
            ]
            json.dump(test_data, f, indent=2)
            error_test_file = Path(f.name)

        # Setup required database data
        archetype = Archetype(name="Valid Archetype", display_name="Valid Archetype")
        session.add(archetype)
        session.commit()

        powerset = Powerset(
            name="Valid Powerset",
            display_name="Valid Powerset",
            archetype_id=archetype.id,
            powerset_type="primary",
        )
        session.add(powerset)
        session.commit()

        parser = I12StreamingParser(db_url, batch_size=10)

        # Should not raise exception despite invalid records
        parser.import_data(error_test_file)

        # Verify error tracking
        assert parser.error_count > 0  # Should have errors from invalid record
        assert parser.imported_count == 2  # Should have imported 2 valid records
        assert len(parser.errors) > 0  # Should have error details

        # Verify valid records were imported
        powers = session.query(Power).all()
        assert len(powers) == 2
        assert any(p.name == "Valid Power" for p in powers)
        assert any(p.name == "Another Valid Power" for p in powers)

        # Cleanup
        error_test_file.unlink()

    def test_performance_benchmark(self, test_db, large_json_test_file):
        """Test import performance with timing."""
        import time

        session, db_url = test_db

        # Setup test data - create all required archetypes and powersets
        for i in range(3):  # 3 archetypes for i % 3
            archetype = Archetype(
                name=f"Test Archetype {i}", display_name=f"Test Archetype {i}"
            )
            session.add(archetype)
        session.commit()

        # Get the first archetype for creating powersets
        archetype = (
            session.query(Archetype)
            .filter(Archetype.name == "Test Archetype 0")
            .first()
        )

        # Create all required powersets (0-9 for i % 10)
        for i in range(10):
            powerset = Powerset(
                name=f"Test Powerset {i}",
                display_name=f"Test Powerset {i}",
                archetype_id=archetype.id,
                powerset_type="primary",
            )
            session.add(powerset)
        session.commit()

        # Create test file with 1000 records
        json_file = large_json_test_file(1000)

        parser = I12StreamingParser(db_url, batch_size=100, chunk_size=200)

        start_time = time.time()
        parser.import_data(json_file)
        end_time = time.time()

        import_time = end_time - start_time
        records_per_second = (
            parser.imported_count / import_time if import_time > 0 else 0
        )

        # Performance assertions (adjust based on requirements)
        assert import_time < 30.0  # Should complete within 30 seconds
        assert records_per_second > 10  # Should process at least 10 records/sec

        # Verify all records imported successfully
        assert parser.imported_count == 1000
        assert parser.error_count == 0

        # Cleanup
        json_file.unlink()
