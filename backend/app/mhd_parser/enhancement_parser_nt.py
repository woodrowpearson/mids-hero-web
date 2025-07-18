"""Enhancement parser that handles null-terminated strings."""

from typing import List
from dataclasses import dataclass, field
from .binary_reader import BinaryReader
from .models import MHDEnhancement, MHDDatabase


class NTBinaryReader(BinaryReader):
    """Binary reader that can handle null-terminated strings."""
    
    def read_string_nt(self) -> str:
        """Read a null-terminated string."""
        chars = []
        while True:
            char = self.stream.read(1)
            if not char or char == b'\x00':
                break
            chars.append(char)
        
        if not chars:
            return ""
        
        return b''.join(chars).decode('utf-8', errors='replace')
    
    def skip_bytes(self, count: int):
        """Skip a number of bytes."""
        self.stream.read(count)


@dataclass
class MHDEnhancementNT(MHDEnhancement):
    """Enhancement with corrected parsing for Homecoming format."""
    
    @classmethod
    def from_reader(cls, reader: NTBinaryReader) -> 'MHDEnhancementNT':
        """Parse enhancement with null-terminated strings and separators."""
        enh = cls()
        
        # Read static_index (appears to be byte-swapped)
        raw_idx = reader.read_int32()
        # Convert from big-endian if needed (0x08000000 -> 8)
        if raw_idx > 0x1000000:
            enh.static_index = int.from_bytes(raw_idx.to_bytes(4, 'little'), 'big')
        else:
            enh.static_index = raw_idx
        
        # Read name (null-terminated)
        enh.name = reader.read_string_nt()
        
        # Skip separator byte (0x03 seen in debug)
        sep = reader.stream.read(1)
        
        # Read short name (null-terminated)
        enh.short_name = reader.read_string_nt()
        
        # Skip separator
        sep = reader.stream.read(1)
        
        # Read description (null-terminated)
        enh.desc = reader.read_string_nt()
        
        # Read type_id and sub_type_id
        enh.type_id = reader.read_int32()
        enh.sub_type_id = reader.read_int32()
        
        # Read class_ids array
        class_count = reader.read_int32()
        enh.class_ids = []
        for i in range(class_count):
            enh.class_ids.append(reader.read_int32())
        
        # Read image (null-terminated)
        enh.image = reader.read_string_nt()
        
        # Read remaining fields
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
    """Parse EnhDB.mhd with corrected string handling.
    
    Args:
        file_path: Path to the EnhDB.mhd file
        
    Returns:
        MHDDatabase object with enhancements populated
    """
    db = MHDDatabase()
    
    with open(file_path, 'rb') as f:
        reader = NTBinaryReader(f)
        
        # Read header
        header = reader.read_string()
        if "Enhancement" not in header:
            raise ValueError(f"Invalid enhancement database header: {header}")
        
        # Read version (may be empty)
        db.version = reader.read_string()
        
        # Read flag and actual count
        flag_or_date = reader.read_uint32()
        if flag_or_date == 0x40000000:
            # This is a flag, actual count follows
            enhancement_count = reader.read_uint32()
        else:
            # This might be the count directly (older format)
            enhancement_count = flag_or_date
        
        # Debug: what's the actual count?
        print(f"Enhancement count from file: {enhancement_count}")
        
        # Sanity check - if count seems wrong, try reading more
        if enhancement_count < 10:
            print(f"Warning: Enhancement count seems low ({enhancement_count}), checking for actual data...")
        
        db.enhancements = []
        
        print(f"Loading {enhancement_count} enhancements...")
        for i in range(enhancement_count):
            if i % 100 == 0:
                print(f"  Loaded {i}/{enhancement_count} enhancements...")
            try:
                db.enhancements.append(MHDEnhancementNT.from_reader(reader))
                if i < 3:  # Debug first few
                    enh = db.enhancements[-1]
                    print(f"  Enhancement {i}: idx={enh.static_index}, name={enh.name}, short={enh.short_name}")
            except Exception as e:
                print(f"Error parsing enhancement {i}: {e}")
                # Try to continue parsing to see how many we can get
                if i < 10:  # Only show errors for first few
                    import traceback
                    traceback.print_exc()
                # Skip to estimated next record (rough estimate)
                try:
                    reader.skip_bytes(200)
                except:
                    break
    
    print(f"Successfully loaded {len(db.enhancements)} enhancements")
    return db