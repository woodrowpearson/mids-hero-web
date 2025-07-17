"""Test cases for fixed enhancement database parser."""

import struct
from io import BytesIO
import pytest

from app.mhd_parser.binary_reader import BinaryReader
from app.mhd_parser.models import MHDDatabase, MHDEnhancement


class TestEnhancementParserFix:
    """Test the fixed enhancement database parser."""
    
    def test_enhancement_header_with_empty_version(self):
        """Test parsing header with empty version string."""
        # Create mock EnhDB.mhd data based on our analysis
        data = BytesIO()
        
        # Header string
        header = "Mids Reborn Enhancement Database"
        data.write(struct.pack('B', len(header)))
        data.write(header.encode('utf-8'))
        
        # Empty version string
        data.write(struct.pack('B', 0))
        
        # Version/flag (0x40000000) - not a count!
        data.write(struct.pack('<I', 0x40000000))
        
        # Actual enhancement count
        data.write(struct.pack('<I', 5))
        
        # Mock enhancement data (simplified)
        for i in range(5):
            # Static index
            data.write(struct.pack('<i', i))
            # Name
            name = f"Enhancement_{i}"
            data.write(struct.pack('B', len(name)))
            data.write(name.encode('utf-8'))
            # Short name
            short = f"Enh{i}"
            data.write(struct.pack('B', len(short)))
            data.write(short.encode('utf-8'))
            # Description
            desc = f"Test enhancement {i}"
            data.write(struct.pack('B', len(desc)))
            data.write(desc.encode('utf-8'))
            # Type and subtype
            data.write(struct.pack('<ii', 1, 0))
            
            # Class IDs array (empty for simplicity)
            data.write(struct.pack('<i', -1))  # count = 0
            
            # Remaining fields with defaults
            data.write(struct.pack('B', 0))  # empty image string
            data.write(struct.pack('<i', -1))  # set_id
            data.write(struct.pack('B', 0))  # empty uid_set
            data.write(struct.pack('<f', 1.0))  # effect_chance
            data.write(struct.pack('<ii', 1, 50))  # level_min, level_max
            data.write(struct.pack('?', False))  # unique
            data.write(struct.pack('<i', -1))  # mutex_id
            data.write(struct.pack('<i', 0))  # buff_mode
            
            # Effect array (empty)
            data.write(struct.pack('<i', -1))  # effect count = 0
            
            data.write(struct.pack('B', 0))  # empty uid
            data.write(struct.pack('B', 0))  # empty recipe_name
            data.write(struct.pack('?', False))  # superior
            data.write(struct.pack('?', False))  # is_proc
            data.write(struct.pack('?', False))  # is_scalable
        
        data.seek(0)
        
        # Test the parser
        reader = BinaryReader(data)
        
        # Read header
        header_str = reader.read_string()
        assert header_str == "Mids Reborn Enhancement Database"
        
        # Read version (empty)
        version = reader.read_string()
        assert version == ""
        
        # Skip version/flag bytes
        flag = reader.read_uint32()
        assert flag == 0x40000000
        
        # Read actual count
        count = reader.read_uint32()
        assert count == 5
        
        # Parse enhancements
        enhancements = []
        for i in range(count):
            enh = MHDEnhancement.from_reader(reader)
            enhancements.append(enh)
            assert enh.static_index == i
            assert enh.name == f"Enhancement_{i}"
    
    def test_parse_enhancement_database_fixed(self):
        """Test the fixed parse_enhancement_database function."""
        from app.mhd_parser.parser import parse_enhancement_database
        
        # Create test data
        data = self._create_test_enhancement_db()
        
        # Parse it
        db = parse_enhancement_database(data)
        
        # Verify results
        assert db.version == ""
        assert len(db.enhancements) == 3
        assert db.enhancements[0].name == "Accuracy"
        assert db.enhancements[1].name == "Damage" 
        assert db.enhancements[2].name == "Endurance"
    
    def _create_test_enhancement_db(self):
        """Create a test enhancement database file."""
        data = BytesIO()
        
        # Header
        header = "Mids Reborn Enhancement Database"
        data.write(struct.pack('B', len(header)))
        data.write(header.encode('utf-8'))
        
        # Empty version
        data.write(struct.pack('B', 0))
        
        # Version flag
        data.write(struct.pack('<I', 0x40000000))
        
        # Count
        data.write(struct.pack('<I', 3))
        
        # Three test enhancements
        test_enhancements = [
            ("Accuracy", "Acc", "Increases accuracy", 1, 0),
            ("Damage", "Dmg", "Increases damage", 2, 0),
            ("Endurance", "End", "Reduces endurance cost", 3, 0)
        ]
        
        for i, (name, short, desc, type_id, subtype) in enumerate(test_enhancements):
            # Static index
            data.write(struct.pack('<i', i))
            # Name
            data.write(struct.pack('B', len(name)))
            data.write(name.encode('utf-8'))
            # Short name
            data.write(struct.pack('B', len(short)))
            data.write(short.encode('utf-8'))
            # Description
            data.write(struct.pack('B', len(desc)))
            data.write(desc.encode('utf-8'))
            # Type and subtype
            data.write(struct.pack('<ii', type_id, subtype))
            # Class IDs (empty)
            data.write(struct.pack('<i', -1))
            # Image (empty)
            data.write(struct.pack('B', 0))
            # Set ID
            data.write(struct.pack('<i', -1))
            # UID Set (empty)
            data.write(struct.pack('B', 0))
            # Effect chance
            data.write(struct.pack('<f', 1.0))
            # Level range
            data.write(struct.pack('<ii', 1, 50))
            # Unique
            data.write(struct.pack('?', False))
            # mutex_id
            data.write(struct.pack('<i', -1))
            # buff_mode
            data.write(struct.pack('<i', 0))
            # Effect array (empty)
            data.write(struct.pack('<i', -1))
            # UID (empty)
            data.write(struct.pack('B', 0))
            # Recipe name (empty)
            data.write(struct.pack('B', 0))
            # Superior
            data.write(struct.pack('?', False))
            # is_proc
            data.write(struct.pack('?', False))
            # is_scalable
            data.write(struct.pack('?', False))
        
        data.seek(0)
        return data