"""Parser for Homecoming MHD file format.

This parser handles the specific format used by Homecoming/Mids Reborn,
which differs from the standard .NET BinaryWriter format.
"""

import io
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, List, Optional

from .archetype_parser import Archetype
from .main_database_parser import MainDatabase
from .powerset_parser import Powerset
from .power_parser import Power


def read_mids_string(stream: BinaryIO) -> str:
    """Read a string in Mids format (length byte followed by string data)."""
    length_byte = stream.read(1)
    if not length_byte:
        raise EOFError("EOF while reading string length")
    
    length = ord(length_byte)
    if length == 0:
        return ""
    
    string_data = stream.read(length)
    if len(string_data) < length:
        raise EOFError(f"String truncated: expected {length} bytes, got {len(string_data)}")
    
    # Try UTF-8 first, fallback to latin-1
    try:
        return string_data.decode('utf-8')
    except UnicodeDecodeError:
        return string_data.decode('latin-1')


def read_int32(stream: BinaryIO) -> int:
    """Read a 32-bit integer."""
    data = stream.read(4)
    if len(data) < 4:
        raise EOFError("EOF while reading int32")
    return struct.unpack('<i', data)[0]


def read_float32(stream: BinaryIO) -> float:
    """Read a 32-bit float."""
    data = stream.read(4)
    if len(data) < 4:
        raise EOFError("EOF while reading float32")
    return struct.unpack('<f', data)[0]


class HomecomingParser:
    """Parser for Homecoming MHD format."""
    
    def __init__(self, stream: BinaryIO):
        self.stream = stream
        self.archetypes: List[Archetype] = []
        self.powersets: List[Powerset] = []
        self.powers: List[Power] = []
    
    def parse(self) -> MainDatabase:
        """Parse the MHD file and return a MainDatabase object."""
        # Read header
        header = read_mids_string(self.stream)
        if "Mids" not in header:
            raise ValueError(f"Invalid header: {header}")
        
        # Read version
        version = read_mids_string(self.stream)
        
        # Skip unknown bytes
        self.stream.read(16)  # Skip bytes we don't understand yet
        
        # Look for section markers
        while True:
            try:
                marker = read_mids_string(self.stream)
                if not marker:
                    continue
                    
                if marker == "BEGIN:ARCHETYPES":
                    self._parse_archetypes()
                elif marker == "BEGIN:POWERSETS":
                    self._parse_powersets()
                elif marker == "BEGIN:POWERS":
                    self._parse_powers()
                elif marker.startswith("END:"):
                    # End of a section
                    continue
                    
            except EOFError:
                break
        
        return MainDatabase(
            header=header,
            version=version,
            date=0,  # Will be parsed later
            issue=0,
            page_vol=0,
            page_vol_text="",
            archetypes=self.archetypes,
            powersets=self.powersets,
            powers=self.powers,
            summons=[]
        )
    
    def _parse_archetypes(self) -> None:
        """Parse the archetypes section."""
        count = read_int32(self.stream)
        
        for _ in range(count):
            # Read archetype data
            display_name = read_mids_string(self.stream)
            hit_points = read_int32(self.stream)
            # Skip unknown bytes for now
            self.stream.read(8)
            
            # Read description
            desc_length = struct.unpack('<H', self.stream.read(2))[0]  # 16-bit length
            desc = self.stream.read(desc_length).decode('utf-8', errors='replace')
            
            # For now, create a minimal archetype
            arch = Archetype(
                display_name=display_name,
                hitpoints=hit_points,
                hp_cap=1606.0,  # Default value
                desc_long=desc,
                res_cap=75.0,
                origins=["Magic", "Mutation", "Natural", "Science", "Technology"],
                class_name=f"Class_{display_name.replace(' ', '_')}",
                class_type=0,
                column=0,
                desc_short=display_name[:4],
                primary_group="",
                secondary_group="",
                playable=True,
                recharge_cap=500.0,
                damage_cap=400.0,
                recovery_cap=200.0,
                regen_cap=175.0,
                threat_cap=500.0,
                resist_cap=95.0,
                damage_resist_cap=300.0,
                base_recovery=1.0,
                base_regen=1.0,
                base_threat=1.0,
                perception_cap=1153.0,
            )
            
            self.archetypes.append(arch)
            
            # Skip rest of archetype data for now
            # This is a simplified parser - full implementation would read all fields


def parse_homecoming_database(file_path: Path) -> MainDatabase:
    """Parse a Homecoming MHD file."""
    with open(file_path, 'rb') as f:
        parser = HomecomingParser(f)
        return parser.parse()