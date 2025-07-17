"""Data classes for MHD file format.

These classes mirror the structure of the MidsReborn C# classes
but are implemented in Python for cross-platform compatibility.
"""

import struct
from typing import BinaryIO, List, Optional

from .binary_reader import MHDBinaryReader
from .enums import ClassType, PowerType, EnhancementType, BuffDebuff


class Archetype:
    """Character archetype data."""
    
    def __init__(self, reader: Optional[MHDBinaryReader] = None):
        """Initialize archetype, optionally from binary data.
        
        Args:
            reader: Optional binary reader to load data from
        """
        # Set defaults
        self.idx: int = 0
        self.display_name: str = "New Archetype"
        self.class_name: str = "NewClass"
        self.class_type: ClassType = ClassType.NONE
        self.hitpoints: int = 5000
        self.hp_cap: float = 5000.0
        self.desc_long: str = ""
        self.desc_short: str = ""
        self.res_cap: float = 90.0
        self.recharge_cap: float = 5.0
        self.damage_cap: float = 4.0
        self.regen_cap: float = 20.0
        self.recovery_cap: float = 5.0
        self.origin: List[str] = [
            "Magic",
            "Mutation", 
            "Natural",
            "Science",
            "Technology"
        ]
        self.primary: List[int] = []
        self.secondary: List[int] = []
        self.ancillary: List[int] = []
        self.perception_cap: float = 1153.0
        self.column: int = 0
        self.primary_group: str = ""
        self.secondary_group: str = ""
        self.epic_group: str = "EPIC"
        self.pool_group: str = "POOL"
        self.playable: bool = True
        self.base_recovery: float = 1.67
        self.base_regen: float = 1.0
        self.base_threat: float = 1.0
        
        # Tracking fields
        self.is_modified: bool = False
        self.is_new: bool = False
        
        # Load from reader if provided
        if reader:
            self._load_from_reader(reader)
    
    def _load_from_reader(self, reader: MHDBinaryReader):
        """Load archetype data from binary reader.
        
        Args:
            reader: Binary reader positioned at start of archetype data
        """
        self.display_name = reader.read_string()
        self.hitpoints = reader.read_int32()
        self.hp_cap = reader.read_single()
        self.desc_long = reader.read_string()
        self.res_cap = reader.read_single()
        
        # Read origins array
        origin_count = reader.read_int32()
        self.origin = []
        for _ in range(origin_count + 1):  # Count is 0-based
            self.origin.append(reader.read_string())
        
        self.class_name = reader.read_string()
        self.class_type = ClassType(reader.read_int32())
        self.column = reader.read_int32()
        self.desc_short = reader.read_string()
        self.primary_group = reader.read_string()
        self.secondary_group = reader.read_string()
        self.playable = reader.read_boolean()
        self.recharge_cap = reader.read_single()
        self.damage_cap = reader.read_single()
        self.recovery_cap = reader.read_single()
        self.regen_cap = reader.read_single()
        self.base_recovery = reader.read_single()
        self.base_regen = reader.read_single()
        self.base_threat = reader.read_single()
        self.perception_cap = reader.read_single()
    
    def store_to(self, stream: BinaryIO):
        """Write archetype data to binary stream.
        
        Args:
            stream: Binary stream to write to
        """
        # Write string with length prefix
        def write_string(s: str):
            bytes_data = s.encode("utf-8")
            write_7bit_encoded_int(len(bytes_data))
            stream.write(bytes_data)
        
        # Write 7-bit encoded integer
        def write_7bit_encoded_int(value: int):
            while value >= 0x80:
                stream.write(bytes([value | 0x80]))
                value >>= 7
            stream.write(bytes([value]))
        
        write_string(self.display_name)
        stream.write(struct.pack("<i", self.hitpoints))
        stream.write(struct.pack("<f", self.hp_cap))
        write_string(self.desc_long)
        stream.write(struct.pack("<f", self.res_cap))
        
        # Write origins array (0-based count)
        stream.write(struct.pack("<i", len(self.origin) - 1))
        for origin in self.origin:
            write_string(origin)
        
        write_string(self.class_name)
        stream.write(struct.pack("<i", self.class_type.value))
        stream.write(struct.pack("<i", self.column))
        write_string(self.desc_short)
        write_string(self.primary_group)
        write_string(self.secondary_group)
        stream.write(bytes([1 if self.playable else 0]))
        stream.write(struct.pack("<f", self.recharge_cap))
        stream.write(struct.pack("<f", self.damage_cap))
        stream.write(struct.pack("<f", self.recovery_cap))
        stream.write(struct.pack("<f", self.regen_cap))
        stream.write(struct.pack("<f", self.base_recovery))
        stream.write(struct.pack("<f", self.base_regen))
        stream.write(struct.pack("<f", self.base_threat))
        stream.write(struct.pack("<f", self.perception_cap))