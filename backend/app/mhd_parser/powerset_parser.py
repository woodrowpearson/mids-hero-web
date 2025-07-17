"""Parser for Powerset records from MHD files."""

from dataclasses import dataclass
from enum import IntEnum
from typing import BinaryIO, List, Tuple

from .binary_reader import BinaryReader


class PowersetType(IntEnum):
    """Powerset type enumeration."""
    PRIMARY = 0
    SECONDARY = 1
    POOL = 2
    EPIC = 3
    INHERENT = 4
    INCARNATE = 5


@dataclass
class Powerset:
    """Represents a Powerset record from MHD data."""
    
    # Basic info
    display_name: str
    archetype_index: int  # -1 for pool powers
    set_type: PowersetType
    image_name: str
    full_name: str
    set_name: str
    description: str
    sub_name: str
    
    # Archetype and UID info
    at_class: str
    uid_trunk_set: str
    uid_link_secondary: str
    
    # Mutex list (mutually exclusive powersets)
    mutex_list: List[Tuple[str, int]]  # List of (name, index) pairs


def parse_powerset(stream: BinaryIO) -> Powerset:
    """Parse a Powerset record from a binary stream.
    
    Args:
        stream: Binary stream positioned at the start of a Powerset record
        
    Returns:
        Parsed Powerset object
        
    Raises:
        EOFError: If stream ends while reading
    """
    reader = BinaryReader(stream)
    
    try:
        # 1. DisplayName (string)
        display_name = reader.read_string()
        
        # 2. nArchetype (Int32) - archetype index
        archetype_index = reader.read_int32()
        
        # 3. SetType (Int32 as enum)
        set_type = PowersetType(reader.read_int32())
        
        # 4. ImageName (string)
        image_name = reader.read_string()
        
        # 5. FullName (string) - with Orphan fallback
        full_name = reader.read_string()
        if not full_name:
            full_name = f"Orphan.{display_name}"
        
        # 6. SetName (string)
        set_name = reader.read_string()
        
        # 7. Description (string)
        description = reader.read_string()
        
        # 8. SubName (string)
        sub_name = reader.read_string()
        
        # 9. ATClass (string)
        at_class = reader.read_string()
        
        # 10. UIDTrunkSet (string)
        uid_trunk_set = reader.read_string()
        
        # 11. UIDLinkSecondary (string)
        uid_link_secondary = reader.read_string()
        
        # 12. numMutex (Int32) + mutex arrays (count+1 pairs of string/Int32)
        num_mutex = reader.read_int32()
        mutex_list = []
        
        # Read mutex pairs
        for i in range(num_mutex):
            mutex_name = reader.read_string()
            mutex_index = reader.read_int32()
            mutex_list.append((mutex_name, mutex_index))
        
        # Read the extra entries (count+1 pattern)
        reader.read_string()  # Extra string
        reader.read_int32()   # Extra int
        
        return Powerset(
            display_name=display_name,
            archetype_index=archetype_index,
            set_type=set_type,
            image_name=image_name,
            full_name=full_name,
            set_name=set_name,
            description=description,
            sub_name=sub_name,
            at_class=at_class,
            uid_trunk_set=uid_trunk_set,
            uid_link_secondary=uid_link_secondary,
            mutex_list=mutex_list
        )
        
    except EOFError as e:
        # Re-raise with more context
        raise EOFError(f"Unexpected EOF while parsing Powerset: {str(e)}")