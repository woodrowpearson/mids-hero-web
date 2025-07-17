"""Tests for parsing complete Enhancement database files."""

import io
import struct
from datetime import datetime
from dataclasses import dataclass
from typing import List

import pytest

from app.mhd_parser.enhancement_database_parser import (
    parse_enhancement_database, EnhancementDatabase
)
from app.mhd_parser.enhancement_parser import Enhancement, EnhancementSet


class TestEnhancementDatabaseParser:
    """Test cases for parsing complete Enhancement database files."""
    
    def test_parse_minimal_enhancement_database(self):
        """Test parsing a minimal enhancement database."""
        data = io.BytesIO()
        
        # Header
        header = "Mids Reborn Enhancement Database"
        data.write(bytes([len(header)]))
        data.write(header.encode())
        
        # Version
        version = "1.0.0.0"
        data.write(bytes([len(version)]))
        data.write(version.encode())
        
        # Date (Int32 format for old version)
        data.write(struct.pack('<i', 20231215))
        
        # Counts
        data.write(struct.pack('<i', 0))  # Enhancement count
        data.write(struct.pack('<i', 0))  # EnhancementSet count
        
        data.seek(0)
        
        db = parse_enhancement_database(data)
        
        assert db.header == "Mids Reborn Enhancement Database"
        assert db.version == "1.0.0.0"
        assert db.date == 20231215
        assert len(db.enhancements) == 0
        assert len(db.enhancement_sets) == 0
    
    def test_parse_database_with_enhancements(self):
        """Test parsing database with actual enhancement data."""
        data = io.BytesIO()
        
        # Header
        header = "Mids Reborn Enhancement Database"
        data.write(bytes([len(header)]))
        data.write(header.encode())
        
        # Version
        version = "1.0.0.0"
        data.write(bytes([len(version)]))
        data.write(version.encode())
        
        # Date
        data.write(struct.pack('<i', 20231215))
        
        # Enhancement count
        data.write(struct.pack('<i', 2))  # 2 enhancements
        
        # Enhancement 1: Simple IO
        data.write(struct.pack('<i', 1))  # StaticIndex
        data.write(b'\x0BAccuracy IO')  # Name
        data.write(b'\x06Acc IO')  # ShortName
        data.write(b'\x12Increases accuracy')  # Desc (length 18)
        data.write(struct.pack('<i', 1))  # TypeID
        data.write(struct.pack('<i', 0))  # SubTypeID
        data.write(struct.pack('<i', 0))  # ClassID count
        data.write(struct.pack('<i', -1))  # ClassID terminator
        data.write(b'\x07acc.png')  # Image
        data.write(struct.pack('<i', 0))  # nIDSet
        data.write(b'\x00')  # UIDSet empty
        data.write(struct.pack('<f', 100.0))  # EffectChance
        data.write(struct.pack('<i', 10))  # LevelMin
        data.write(struct.pack('<i', 50))  # LevelMax
        data.write(struct.pack('<?', False))  # Unique
        data.write(struct.pack('<i', 0))  # MutExID
        data.write(struct.pack('<i', 0))  # BuffMode
        # Effects
        data.write(struct.pack('<i', 1))  # Effect count
        data.write(struct.pack('<i', 1))  # Mode
        data.write(struct.pack('<i', 0))  # BuffMode
        data.write(struct.pack('<i', 1))  # Enhance.ID
        data.write(struct.pack('<i', 0))  # Enhance.SubID
        data.write(struct.pack('<i', 0))  # Schedule
        data.write(struct.pack('<f', 0.3333))  # Multiplier
        data.write(struct.pack('<?', False))  # No FX
        # Final fields
        data.write(b'\x06IO.Acc')  # UID
        data.write(b'\x00')  # RecipeName
        data.write(struct.pack('<?', False))  # Superior
        data.write(struct.pack('<?', False))  # IsProc
        data.write(struct.pack('<?', True))  # IsScalable
        
        # Enhancement 2: Damage IO
        data.write(struct.pack('<i', 2))  # StaticIndex
        data.write(b'\x09Damage IO')  # Name
        data.write(b'\x06Dam IO')  # ShortName
        data.write(b'\x10Increases damage')  # Desc (length 16)
        data.write(struct.pack('<i', 1))  # TypeID
        data.write(struct.pack('<i', 0))  # SubTypeID
        data.write(struct.pack('<i', 0))  # ClassID count
        data.write(struct.pack('<i', -1))  # ClassID terminator
        data.write(b'\x07dam.png')  # Image
        data.write(struct.pack('<i', 0))  # nIDSet
        data.write(b'\x00')  # UIDSet empty
        data.write(struct.pack('<f', 100.0))  # EffectChance
        data.write(struct.pack('<i', 10))  # LevelMin
        data.write(struct.pack('<i', 50))  # LevelMax
        data.write(struct.pack('<?', False))  # Unique
        data.write(struct.pack('<i', 0))  # MutExID
        data.write(struct.pack('<i', 0))  # BuffMode
        # Effects
        data.write(struct.pack('<i', 1))  # Effect count
        data.write(struct.pack('<i', 1))  # Mode
        data.write(struct.pack('<i', 0))  # BuffMode
        data.write(struct.pack('<i', 2))  # Enhance.ID (Damage)
        data.write(struct.pack('<i', 0))  # Enhance.SubID
        data.write(struct.pack('<i', 0))  # Schedule
        data.write(struct.pack('<f', 0.3333))  # Multiplier
        data.write(struct.pack('<?', False))  # No FX
        # Final fields
        data.write(b'\x06IO.Dam')  # UID
        data.write(b'\x00')  # RecipeName
        data.write(struct.pack('<?', False))  # Superior
        data.write(struct.pack('<?', False))  # IsProc
        data.write(struct.pack('<?', True))  # IsScalable
        
        # EnhancementSet count
        data.write(struct.pack('<i', 0))  # No sets
        
        data.seek(0)
        
        db = parse_enhancement_database(data)
        
        assert len(db.enhancements) == 2
        assert db.enhancements[0].name == "Accuracy IO"
        assert db.enhancements[0].static_index == 1
        assert db.enhancements[1].name == "Damage IO"
        assert db.enhancements[1].static_index == 2
    
    def test_parse_database_with_enhancement_sets(self):
        """Test parsing database with enhancement sets."""
        data = io.BytesIO()
        
        # Header
        header = "Mids Reborn Enhancement Database"
        data.write(bytes([len(header)]))
        data.write(header.encode())
        
        # Version
        version = "1.0.0.0"
        data.write(bytes([len(version)]))
        data.write(version.encode())
        
        # Date
        data.write(struct.pack('<i', 20231215))
        
        # Enhancement count (0 for this test)
        data.write(struct.pack('<i', 0))
        
        # EnhancementSet count
        data.write(struct.pack('<i', 1))  # 1 set
        
        # EnhancementSet 1
        data.write(struct.pack('<i', 1))  # DisplayIndex
        data.write(b'\x0DThunderstrike')  # DisplayName
        data.write(b'\x07Thunder')  # ShortName
        data.write(b'\x0CMelee damage')  # Desc
        data.write(struct.pack('<i', 1))  # SetType
        # Enhancement indices
        data.write(struct.pack('<i', 3))  # 3 pieces
        data.write(struct.pack('<i', 100))
        data.write(struct.pack('<i', 101))
        data.write(struct.pack('<i', 102))
        # Bonuses
        data.write(struct.pack('<i', 2))  # 2 bonuses
        data.write(struct.pack('<i', 1000))  # Bonus 1
        data.write(struct.pack('<i', 1001))  # Bonus 2
        # BonusMin
        data.write(struct.pack('<i', 2))  # count
        data.write(struct.pack('<i', 2))  # 2 pieces
        data.write(struct.pack('<i', 3))  # 3 pieces
        # BonusMax
        data.write(struct.pack('<i', 0))  # count
        # SpecialBonus
        data.write(struct.pack('<i', 0))  # count
        # Final fields
        data.write(b'\x0ASet.Thunder')  # UIDSet
        data.write(struct.pack('<i', 10))  # LevelMin
        data.write(struct.pack('<i', 50))  # LevelMax
        
        data.seek(0)
        
        db = parse_enhancement_database(data)
        
        assert len(db.enhancement_sets) == 1
        assert db.enhancement_sets[0].display_name == "Thunderstrike"
        assert len(db.enhancement_sets[0].enhancement_indices) == 3
        assert len(db.enhancement_sets[0].bonuses) == 2
        assert db.enhancement_sets[0].bonus_min == [2, 3]
    
    def test_parse_database_version_3_date_format(self):
        """Test parsing database with version 3.x date format."""
        data = io.BytesIO()
        
        # Header
        header = "Mids Reborn Enhancement Database"
        data.write(bytes([len(header)]))
        data.write(header.encode())
        
        # Version >= 3.0 triggers Int64 date
        version = "3.0.0.0"
        data.write(bytes([len(version)]))
        data.write(version.encode())
        
        # Date as Int64 (.NET ticks)
        data.write(struct.pack('<q', 638229120000000000))
        
        # Counts
        data.write(struct.pack('<i', 0))  # Enhancement count
        data.write(struct.pack('<i', 0))  # EnhancementSet count
        
        data.seek(0)
        
        db = parse_enhancement_database(data)
        
        assert db.version == "3.0.0.0"
        assert isinstance(db.date, datetime)
    
    def test_parse_database_eof_handling(self):
        """Test handling of EOF during parsing."""
        data = io.BytesIO()
        
        # Header only
        header = "Mids Reborn Enhancement Database"
        data.write(bytes([len(header)]))
        data.write(header.encode())
        
        # Missing rest of data
        data.seek(0)
        
        with pytest.raises(EOFError):
            parse_enhancement_database(data)