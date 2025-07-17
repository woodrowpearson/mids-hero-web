"""Tests for Archetype data class."""

import io
import struct

import pytest

from app.mhd_parser.binary_reader import MHDBinaryReader
from app.mhd_parser.data_classes import Archetype
from app.mhd_parser.enums import ClassType


class TestArchetype:
    """Test Archetype data class."""
    
    def test_archetype_defaults(self):
        """Test default archetype values."""
        arch = Archetype()
        
        assert arch.display_name == "New Archetype"
        assert arch.class_name == "NewClass"
        assert arch.class_type == ClassType.NONE
        assert arch.hitpoints == 5000
        assert arch.hp_cap == 5000.0
        assert arch.playable is True
        assert arch.base_regen == 1.0
        assert arch.base_recovery == 1.67
        assert arch.base_threat == 1.0
        assert len(arch.origin) == 5
        assert "Magic" in arch.origin
    
    def test_archetype_from_binary(self):
        """Test reading archetype from binary data."""
        buffer = io.BytesIO()
        
        # Write test data in the expected format
        # Display name
        buffer.write(bytes([7]))  # Length
        buffer.write(b"Blaster")
        
        # Hitpoints
        buffer.write(struct.pack("<i", 1204))
        
        # HP Cap
        buffer.write(struct.pack("<f", 1606.4))
        
        # Desc Long
        buffer.write(bytes([18]))  # Length
        buffer.write(b"Ranged damage role")
        
        # Resistance Cap
        buffer.write(struct.pack("<f", 75.0))
        
        # Origins count and array
        buffer.write(struct.pack("<i", 4))  # 5 origins (0-based count)
        for origin in ["Magic", "Mutation", "Natural", "Science", "Technology"]:
            buffer.write(bytes([len(origin)]))
            buffer.write(origin.encode())
        
        # Class name
        buffer.write(bytes([7]))
        buffer.write(b"Blaster")
        
        # Class type
        buffer.write(struct.pack("<i", ClassType.BLASTER.value))
        
        # Column
        buffer.write(struct.pack("<i", 0))
        
        # Desc Short
        buffer.write(bytes([13]))  # Fixed length
        buffer.write(b"Ranged Damage")
        
        # Primary Group
        buffer.write(bytes([14]))  # Length for "Blaster_Ranged"
        buffer.write(b"Blaster_Ranged")
        
        # Secondary Group
        buffer.write(bytes([15]))  # Length for "Blaster_Support"
        buffer.write(b"Blaster_Support")
        
        # Playable
        buffer.write(bytes([1]))  # True
        
        # Caps
        buffer.write(struct.pack("<f", 5.0))    # Recharge cap
        buffer.write(struct.pack("<f", 4.0))    # Damage cap
        buffer.write(struct.pack("<f", 5.0))    # Recovery cap
        buffer.write(struct.pack("<f", 20.0))   # Regen cap
        
        # Base values
        buffer.write(struct.pack("<f", 1.67))   # Base recovery
        buffer.write(struct.pack("<f", 1.0))    # Base regen
        buffer.write(struct.pack("<f", 1.0))    # Base threat
        
        # Perception cap
        buffer.write(struct.pack("<f", 1153.0))
        
        buffer.seek(0)
        reader = MHDBinaryReader(buffer)
        arch = Archetype(reader)
        
        assert arch.display_name == "Blaster"
        assert arch.hitpoints == 1204
        assert arch.hp_cap == pytest.approx(1606.4, rel=1e-3)
        assert arch.desc_long == "Ranged damage role"
        assert arch.res_cap == 75.0
        assert len(arch.origin) == 5
        assert arch.class_name == "Blaster"
        assert arch.class_type == ClassType.BLASTER
        assert arch.column == 0
        assert arch.desc_short == "Ranged Damage"
        assert arch.primary_group == "Blaster_Ranged"
        assert arch.secondary_group == "Blaster_Support"
        assert arch.playable is True
        assert arch.recharge_cap == 5.0
        assert arch.damage_cap == 4.0
        assert arch.recovery_cap == 5.0
        assert arch.regen_cap == 20.0
        assert arch.base_recovery == pytest.approx(1.67, rel=1e-3)
        assert arch.base_regen == 1.0
        assert arch.base_threat == 1.0
        assert arch.perception_cap == 1153.0
    
    def test_archetype_store_to_binary(self):
        """Test writing archetype to binary format."""
        arch = Archetype()
        arch.display_name = "Tanker"
        arch.class_name = "Tanker"
        arch.class_type = ClassType.TANKER
        arch.hitpoints = 1874
        arch.hp_cap = 3534.0
        arch.desc_long = "Melee tank role"
        arch.res_cap = 90.0
        arch.playable = True
        
        buffer = io.BytesIO()
        arch.store_to(buffer)
        
        # Read it back
        buffer.seek(0)
        reader = MHDBinaryReader(buffer)
        arch2 = Archetype(reader)
        
        assert arch2.display_name == arch.display_name
        assert arch2.class_name == arch.class_name
        assert arch2.class_type == arch.class_type
        assert arch2.hitpoints == arch.hitpoints
        assert arch2.hp_cap == arch.hp_cap
        assert arch2.res_cap == arch.res_cap
        assert arch2.playable == arch.playable