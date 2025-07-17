"""Special parser for EnhDB.mhd which uses a different string format."""

from typing import List
from dataclasses import dataclass, field
from .binary_reader import BinaryReader
from .models import MHDEnhancement, MHDDatabase


class EnhancementBinaryReader(BinaryReader):
    """Binary reader that handles null-terminated strings for enhancements."""
    
    def read_string_nt(self) -> str:
        """Read a null-terminated string."""
        bytes_list = []
        while True:
            byte = self.stream.read(1)
            if not byte or byte == b'\x00':
                break
            bytes_list.append(byte)
        
        if not bytes_list:
            return ""
        
        return b''.join(bytes_list).decode('utf-8', errors='replace')


@dataclass
class MHDEnhancementNT(MHDEnhancement):
    """Enhancement with null-terminated string reading."""
    
    @classmethod
    def from_reader(cls, reader: EnhancementBinaryReader) -> 'MHDEnhancementNT':
        """Create an Enhancement from a BinaryReader with null-terminated strings."""
        enh = cls()
        
        # Read basic fields
        enh.static_index = reader.read_int32()
        enh.name = reader.read_string_nt()
        enh.short_name = reader.read_string_nt()
        enh.desc = reader.read_string_nt()
        enh.type_id = reader.read_int32()
        enh.sub_type_id = reader.read_int32()
        
        # Read class IDs array
        class_count = reader.read_int32()
        enh.class_ids = []
        for i in range(class_count):
            enh.class_ids.append(reader.read_int32())
        
        # Read remaining fields
        enh.image = reader.read_string_nt()
        enh.set_id = reader.read_int32()
        enh.uid_set = reader.read_string_nt()
        enh.effect_chance = reader.read_float()
        enh.level_min = reader.read_int32()
        enh.level_max = reader.read_int32()
        enh.unique = reader.read_bool()
        enh.uid = reader.read_string_nt()
        enh.recipe_name = reader.read_string_nt()
        enh.superior = reader.read_bool()
        
        return enh


def parse_enhancement_database_nt(file_path: str) -> MHDDatabase:
    """Parse the EnhDB.mhd enhancement database file with null-terminated strings.
    
    Args:
        file_path: Path to the EnhDB.mhd file
        
    Returns:
        MHDDatabase object with enhancements populated
    """
    db = MHDDatabase()
    
    with open(file_path, 'rb') as f:
        reader = EnhancementBinaryReader(f)
        
        # Read header
        header = reader.read_string()
        if "Enhancement" not in header:
            raise ValueError(f"Invalid enhancement database header: {header}")
        
        # Read version (may be empty)
        db.version = reader.read_string()
        
        # Skip version/flag bytes if present
        # The file has 0x40000000 (1073741824) which is not a count
        flag_or_date = reader.read_uint32()
        if flag_or_date == 0x40000000:
            # This is a flag, actual count follows
            enhancement_count = reader.read_uint32()
        else:
            # This might be the count directly (older format)
            enhancement_count = flag_or_date
        
        db.enhancements = []
        
        print(f"Loading {enhancement_count} enhancements...")
        for i in range(enhancement_count):
            if i % 100 == 0:
                print(f"  Loaded {i}/{enhancement_count} enhancements...")
            try:
                db.enhancements.append(MHDEnhancementNT.from_reader(reader))
            except Exception as e:
                print(f"Error parsing enhancement {i}: {e}")
                import traceback
                traceback.print_exc()
                break
    
    return db