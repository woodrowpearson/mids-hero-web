"""Tests for parsing Salvage records and database from MHD files."""

import io
import struct

import pytest

from app.mhd_parser.salvage_parser import (
    SalvageRarity,
    SalvageType,
    parse_salvage,
    parse_salvage_database,
)


class TestSalvageParser:
    """Test cases for parsing Salvage records."""

    def test_parse_minimal_salvage(self):
        """Test parsing a minimal salvage record."""
        data = io.BytesIO()

        # Write salvage fields
        data.write(b'\x11Alchemical Silver')  # InternalName (17 chars)
        data.write(b'\x11Alchemical Silver')  # DisplayName (17 chars)
        data.write(struct.pack('<i', 0))  # Rarity (Common)
        data.write(struct.pack('<i', 0))  # Type (Component)
        data.write(b'\x1DA rare metal used in crafting')  # Description (29 chars)

        data.seek(0)

        salvage = parse_salvage(data)

        assert salvage.internal_name == "Alchemical Silver"
        assert salvage.display_name == "Alchemical Silver"
        assert salvage.rarity == SalvageRarity.COMMON
        assert salvage.salvage_type == SalvageType.COMPONENT
        assert salvage.description == "A rare metal used in crafting"

    def test_parse_salvage_with_all_rarities(self):
        """Test parsing salvage with different rarity levels."""
        test_cases = [
            (0, SalvageRarity.COMMON),
            (1, SalvageRarity.UNCOMMON),
            (2, SalvageRarity.RARE),
            (3, SalvageRarity.VERY_RARE),
        ]

        for rarity_int, expected_rarity in test_cases:
            data = io.BytesIO()

            data.write(b'\x04Test')  # InternalName
            data.write(b'\x04Test')  # DisplayName
            data.write(struct.pack('<i', rarity_int))  # Rarity
            data.write(struct.pack('<i', 0))  # Type
            data.write(b'\x04Desc')  # Description

            data.seek(0)

            salvage = parse_salvage(data)
            assert salvage.rarity == expected_rarity

    def test_parse_salvage_with_different_types(self):
        """Test parsing salvage with different types."""
        test_cases = [
            (0, SalvageType.COMPONENT),
            (1, SalvageType.CATALYST),
            (2, SalvageType.SPECIAL),
        ]

        for type_int, expected_type in test_cases:
            data = io.BytesIO()

            data.write(b'\x04Test')  # InternalName
            data.write(b'\x04Test')  # DisplayName
            data.write(struct.pack('<i', 0))  # Rarity
            data.write(struct.pack('<i', type_int))  # Type
            data.write(b'\x04Desc')  # Description

            data.seek(0)

            salvage = parse_salvage(data)
            assert salvage.salvage_type == expected_type

    def test_parse_rare_salvage(self):
        """Test parsing a rare salvage example."""
        data = io.BytesIO()

        # Rare salvage example
        data.write(b'\x0BHamidon Goo')  # InternalName (11 chars)
        data.write(b'\x0BHamidon Goo')  # DisplayName (11 chars)
        data.write(struct.pack('<i', 3))  # Rarity (Very Rare)
        data.write(struct.pack('<i', 2))  # Type (Special)
        data.write(b'\x27Goo extracted from Hamidon mitochondria')  # Description (39 chars)

        data.seek(0)

        salvage = parse_salvage(data)

        assert salvage.internal_name == "Hamidon Goo"
        assert salvage.display_name == "Hamidon Goo"
        assert salvage.rarity == SalvageRarity.VERY_RARE
        assert salvage.salvage_type == SalvageType.SPECIAL
        assert salvage.description == "Goo extracted from Hamidon mitochondria"


class TestSalvageDatabaseParser:
    """Test cases for parsing complete Salvage database files."""

    def test_parse_minimal_salvage_database(self):
        """Test parsing a minimal salvage database."""
        data = io.BytesIO()

        # Header
        header = "Mids Reborn Salvage Database"
        data.write(bytes([len(header)]))
        data.write(header.encode())

        # Version
        version = "1.0.0.0"
        data.write(bytes([len(version)]))
        data.write(version.encode())

        # Count
        data.write(struct.pack('<i', 0))  # No salvage items

        data.seek(0)

        db = parse_salvage_database(data)

        assert db.header == "Mids Reborn Salvage Database"
        assert db.version == "1.0.0.0"
        assert len(db.salvage_items) == 0

    def test_parse_salvage_database_with_items(self):
        """Test parsing salvage database with multiple items."""
        data = io.BytesIO()

        # Header
        header = "Mids Reborn Salvage Database"
        data.write(bytes([len(header)]))
        data.write(header.encode())

        # Version
        version = "1.0.0.0"
        data.write(bytes([len(version)]))
        data.write(version.encode())

        # Count
        data.write(struct.pack('<i', 3))  # 3 salvage items

        # Salvage 1: Common component
        data.write(b'\x09Boresight')  # InternalName (9 chars)
        data.write(b'\x09Boresight')  # DisplayName (9 chars)
        data.write(struct.pack('<i', 0))  # Rarity (Common)
        data.write(struct.pack('<i', 0))  # Type (Component)
        data.write(b'\x14Simple targeting aid')  # Description (20 chars)

        # Salvage 2: Uncommon catalyst
        data.write(b'\x0ALuck Charm')  # InternalName (10 chars)
        data.write(b'\x0ALuck Charm')  # DisplayName (10 chars)
        data.write(struct.pack('<i', 1))  # Rarity (Uncommon)
        data.write(struct.pack('<i', 1))  # Type (Catalyst)
        data.write(b'\x18Increases fortune chance')  # Description (24 chars)

        # Salvage 3: Rare component
        data.write(b'\x0FTemporal Tracer')  # InternalName (15 chars)
        data.write(b'\x0FTemporal Tracer')  # DisplayName (15 chars)
        data.write(struct.pack('<i', 2))  # Rarity (Rare)
        data.write(struct.pack('<i', 0))  # Type (Component)
        data.write(b'\x19Tracks temporal anomalies')  # Description (25 chars)

        data.seek(0)

        db = parse_salvage_database(data)

        assert len(db.salvage_items) == 3
        assert db.salvage_items[0].display_name == "Boresight"
        assert db.salvage_items[0].rarity == SalvageRarity.COMMON
        assert db.salvage_items[1].display_name == "Luck Charm"
        assert db.salvage_items[1].rarity == SalvageRarity.UNCOMMON
        assert db.salvage_items[2].display_name == "Temporal Tracer"
        assert db.salvage_items[2].rarity == SalvageRarity.RARE

    def test_parse_salvage_database_eof_handling(self):
        """Test handling of EOF during database parsing."""
        data = io.BytesIO()

        # Header only
        header = "Mids Reborn Salvage Database"
        data.write(bytes([len(header)]))
        data.write(header.encode())
        # Missing rest

        data.seek(0)

        with pytest.raises(EOFError):
            parse_salvage_database(data)
