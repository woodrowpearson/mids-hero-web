"""Tests for parsing complete MHD database files."""

import io
import struct
from datetime import datetime
from dataclasses import dataclass
from typing import List

import pytest

from app.mhd_parser.main_database_parser import (
    parse_main_database, parse_summoned_entity,
    MainDatabase, SummonedEntity, DatabaseSection
)
from app.mhd_parser.archetype_parser import Archetype
from app.mhd_parser.powerset_parser import Powerset
from app.mhd_parser.power_parser import Power


class TestSummonedEntityParser:
    """Test cases for parsing SummonedEntity records."""
    
    def test_parse_minimal_summoned_entity(self):
        """Test parsing a minimal summoned entity."""
        data = io.BytesIO()
        
        # UID
        data.write(b'\x0BPet.FireImp')  # length 11
        
        # DisplayName
        data.write(b'\x08Fire Imp')
        
        # EntityType (Int32)
        data.write(struct.pack('<i', 1))  # Pet
        
        # ClassName
        data.write(b'\x0BPet_FireImp')
        
        # PowersetFullName array
        data.write(struct.pack('<i', 0))  # count
        
        # UpgradePowerFullName array
        data.write(struct.pack('<i', 0))  # count
        
        data.seek(0)
        
        entity = parse_summoned_entity(data)
        
        assert entity.uid == "Pet.FireImp"
        assert entity.display_name == "Fire Imp"
        assert entity.entity_type == 1
        assert entity.class_name == "Pet_FireImp"
        assert entity.powerset_full_names == []
        assert entity.upgrade_power_full_names == []
    
    def test_parse_summoned_entity_with_arrays(self):
        """Test parsing summoned entity with powerset and upgrade arrays."""
        data = io.BytesIO()
        
        # Basic fields
        data.write(b'\x0CPet.Phantasm')  # length 12
        data.write(b'\x08Phantasm')
        data.write(struct.pack('<i', 2))  # Illusion pet
        data.write(b'\x0CPet_Phantasm')  # length 12
        
        # PowersetFullName array
        data.write(struct.pack('<i', 2))  # count
        data.write(b'\x13Illusion.Pet_Attack')  # length 19
        data.write(b'\x14Illusion.Pet_Defense')  # length 20 (0x14 is correct)
        
        # UpgradePowerFullName array
        data.write(struct.pack('<i', 1))  # count
        data.write(b'\x17Illusion.Phantasm_Boost')
        
        data.seek(0)
        
        entity = parse_summoned_entity(data)
        
        assert entity.uid == "Pet.Phantasm"
        assert entity.entity_type == 2
        assert len(entity.powerset_full_names) == 2
        assert entity.powerset_full_names[0] == "Illusion.Pet_Attack"
        assert entity.powerset_full_names[1] == "Illusion.Pet_Defense"
        assert len(entity.upgrade_power_full_names) == 1
        assert entity.upgrade_power_full_names[0] == "Illusion.Phantasm_Boost"


class TestMainDatabaseParser:
    """Test cases for parsing complete MHD database files."""
    
    def test_parse_database_header(self):
        """Test parsing database header and version info."""
        data = io.BytesIO()
        
        # Write header
        header = "Mids Reborn Powers Database"
        data.write(bytes([len(header)]))
        data.write(header.encode())
        
        # Version (use 2.x to trigger Int32 date format)
        version = "2.9.0.0"
        data.write(bytes([len(version)]))
        data.write(version.encode())
        
        # Date (using Int32 format for version < 3.0)
        data.write(struct.pack('<i', 20230615))  # June 15, 2023
        
        # Issue info
        data.write(struct.pack('<i', 27))  # Issue 27
        data.write(struct.pack('<i', 7))   # PageVol
        data.write(b'\x06Page 7')          # PageVolText
        
        # Empty sections for minimal test
        marker = "BEGIN:ARCHETYPES"
        data.write(bytes([len(marker)]))
        data.write(marker.encode())
        data.write(struct.pack('<i', 0))   # count
        
        marker = "BEGIN:POWERSETS"
        data.write(bytes([len(marker)]))
        data.write(marker.encode())
        data.write(struct.pack('<i', 0))   # count
        
        marker = "BEGIN:POWERS"
        data.write(bytes([len(marker)]))
        data.write(marker.encode())
        data.write(struct.pack('<i', 0))   # count
        
        marker = "BEGIN:SUMMONS"
        data.write(bytes([len(marker)]))
        data.write(marker.encode())
        data.write(struct.pack('<i', 0))   # count
        
        data.seek(0)
        
        db = parse_main_database(data)
        
        assert db.header == "Mids Reborn Powers Database"
        assert db.version == "2.9.0.0"
        assert db.date == 20230615
        assert db.issue == 27
        assert db.page_vol == 7
        assert db.page_vol_text == "Page 7"
        assert len(db.archetypes) == 0
        assert len(db.powersets) == 0
        assert len(db.powers) == 0
        assert len(db.summons) == 0
    
    def test_parse_database_with_date_format_detection(self):
        """Test date parsing with version-based format detection."""
        data = io.BytesIO()
        
        # Header
        header = "Mids Reborn Powers Database"
        data.write(bytes([len(header)]))
        data.write(header.encode())
        
        # Version >= 3.0 triggers Int64 date format
        version = "3.0.7.22"
        data.write(bytes([len(version)]))
        data.write(version.encode())
        
        # Date as Int64
        data.write(struct.pack('<q', 638229120000000000))  # .NET ticks
        
        # Rest of header
        data.write(struct.pack('<i', 27))
        data.write(struct.pack('<i', 7))
        data.write(b'\x06Page 7')
        
        # Empty sections
        for section in ['ARCHETYPES', 'POWERSETS', 'POWERS', 'SUMMONS']:
            marker = f'BEGIN:{section}'
            data.write(bytes([len(marker)]))
            data.write(marker.encode())
            data.write(struct.pack('<i', 0))  # count
        
        data.seek(0)
        
        db = parse_main_database(data)
        
        assert db.version == "3.0.7.22"
        # Date should be converted from .NET ticks
        assert isinstance(db.date, datetime)
    
    def test_parse_database_section_markers(self):
        """Test validation of section markers."""
        data = io.BytesIO()
        
        # Valid header
        header = "Mids Reborn Powers Database"
        data.write(bytes([len(header)]))
        data.write(header.encode())
        version = "2.9.0.0"
        data.write(bytes([len(version)]))
        data.write(version.encode())
        data.write(struct.pack('<i', 20230615))
        data.write(struct.pack('<i', 27))
        data.write(struct.pack('<i', 7))
        data.write(b'\x06Page 7')
        
        # Invalid section marker
        marker = "BEGIN:WRONGNAME"
        data.write(bytes([len(marker)]))
        data.write(marker.encode())
        
        data.seek(0)
        
        with pytest.raises(ValueError, match="Invalid section marker"):
            parse_main_database(data)
    
    def test_parse_database_with_entities(self):
        """Test parsing database with actual entity data."""
        data = io.BytesIO()
        
        # Header
        header = "Mids Reborn Powers Database"
        data.write(bytes([len(header)]))
        data.write(header.encode())
        version = "2.9.0.0"
        data.write(bytes([len(version)]))
        data.write(version.encode())
        data.write(struct.pack('<i', 20230615))
        data.write(struct.pack('<i', 27))
        data.write(struct.pack('<i', 7))
        data.write(b'\x06Page 7')
        
        # Archetypes section
        marker = "BEGIN:ARCHETYPES"
        data.write(bytes([len(marker)]))
        data.write(marker.encode())
        data.write(struct.pack('<i', 1))  # count
        
        # Minimal archetype
        data.write(b'\x06Tanker')  # DisplayName
        data.write(struct.pack('<i', 1000))  # Hitpoints
        data.write(struct.pack('<f', 1500.0))  # HPCap
        data.write(b'\x00')  # DescLong empty
        data.write(struct.pack('<f', 90.0))  # ResCap
        data.write(struct.pack('<i', 0))  # numOrigins
        data.write(b'\x00')  # Origin[0]
        data.write(b'\x0CClass_Tanker')  # ClassName
        data.write(struct.pack('<i', 1))  # ClassType
        data.write(struct.pack('<i', 0))  # Column
        data.write(b'\x04Tank')  # DescShort
        data.write(b'\x07Defense')  # PrimaryGroup
        data.write(b'\x05Melee')  # SecondaryGroup
        data.write(b'\x01')  # Playable
        for _ in range(7):  # Caps
            data.write(struct.pack('<f', 100.0))
        for _ in range(3):  # Base stats
            data.write(struct.pack('<f', 1.0))
        data.write(struct.pack('<f', 1000.0))  # PerceptionCap
        
        # Empty other sections
        for section in ['POWERSETS', 'POWERS', 'SUMMONS']:
            marker = f'BEGIN:{section}'
            data.write(bytes([len(marker)]))
            data.write(marker.encode())
            data.write(struct.pack('<i', 0))
        
        data.seek(0)
        
        db = parse_main_database(data)
        
        assert len(db.archetypes) == 1
        assert db.archetypes[0].display_name == "Tanker"
        assert db.archetypes[0].hitpoints == 1000
    
    def test_parse_database_missing_section(self):
        """Test handling of missing sections."""
        data = io.BytesIO()
        
        # Header
        data.write(b'\x1CMids Reborn Powers Database')
        data.write(b'\x082.9.0.0')
        data.write(struct.pack('<i', 20230615))
        data.write(struct.pack('<i', 27))
        data.write(struct.pack('<i', 7))
        data.write(b'\x06Page 7')
        
        # Only archetypes section, missing others
        marker = "BEGIN:ARCHETYPES"
        data.write(bytes([len(marker)]))
        data.write(marker.encode())
        data.write(struct.pack('<i', 0))
        
        # EOF instead of next section
        data.seek(0)
        
        with pytest.raises(EOFError):
            parse_main_database(data)
    
    def test_parse_complete_minimal_database(self):
        """Test parsing a complete minimal database with all sections."""
        data = io.BytesIO()
        
        # Write complete minimal database
        header = "Mids Reborn Powers Database"
        data.write(bytes([len(header)]))
        data.write(header.encode())
        version = "2.9.0.0"
        data.write(bytes([len(version)]))
        data.write(version.encode())
        data.write(struct.pack('<i', 20230615))
        data.write(struct.pack('<i', 27))
        data.write(struct.pack('<i', 7))
        data.write(b'\x06Page 7')
        
        # All sections present but empty
        for section in ['ARCHETYPES', 'POWERSETS', 'POWERS', 'SUMMONS']:
            marker = f'BEGIN:{section}'
            data.write(bytes([len(marker)]))
            data.write(marker.encode())
            data.write(struct.pack('<i', 0))  # count = 0
        
        data.seek(0)
        
        db = parse_main_database(data)
        
        assert db.header == "Mids Reborn Powers Database"
        assert all(len(getattr(db, section.lower())) == 0 
                  for section in ['archetypes', 'powersets', 'powers', 'summons'])