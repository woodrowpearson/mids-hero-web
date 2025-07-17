"""Debug test to understand archetype binary format."""

import io
import struct

from app.mhd_parser.binary_reader import MHDBinaryReader


def test_debug_binary_position():
    """Debug test to check exact binary positions."""
    buffer = io.BytesIO()
    
    # Track positions
    positions = {}
    
    # Display name
    positions['display_name_start'] = buffer.tell()
    buffer.write(bytes([7]))  # Length
    buffer.write(b"Blaster")
    
    # Hitpoints
    positions['hitpoints'] = buffer.tell()
    buffer.write(struct.pack("<i", 1204))
    
    # HP Cap
    positions['hp_cap'] = buffer.tell()
    buffer.write(struct.pack("<f", 1606.4))
    
    # Desc Long
    positions['desc_long'] = buffer.tell()
    buffer.write(bytes([18]))  # Length
    buffer.write(b"Ranged damage role")
    
    # Resistance Cap
    positions['res_cap'] = buffer.tell()
    buffer.write(struct.pack("<f", 75.0))
    
    # Origins count and array
    positions['origins'] = buffer.tell()
    buffer.write(struct.pack("<i", 4))  # 5 origins (0-based count)
    for origin in ["Magic", "Mutation", "Natural", "Science", "Technology"]:
        buffer.write(bytes([len(origin)]))
        buffer.write(origin.encode())
    
    # Class name
    positions['class_name'] = buffer.tell()
    buffer.write(bytes([7]))
    buffer.write(b"Blaster")
    
    # Class type
    positions['class_type'] = buffer.tell()
    buffer.write(struct.pack("<i", 1))
    
    # Column
    positions['column'] = buffer.tell()
    buffer.write(struct.pack("<i", 0))
    
    # Desc Short
    positions['desc_short'] = buffer.tell()
    buffer.write(bytes([14]))
    buffer.write(b"Ranged Damage")
    
    # Primary Group
    positions['primary_group'] = buffer.tell()
    buffer.write(bytes([14]))  # Length for "Blaster_Ranged"
    buffer.write(b"Blaster_Ranged")
    
    positions['after_primary'] = buffer.tell()
    
    print("Positions:")
    for name, pos in positions.items():
        print(f"  {name}: {pos}")
    
    print(f"\nTotal bytes written: {buffer.tell()}")
    
    # Now let's check what's at position 116
    buffer.seek(116)
    next_bytes = buffer.read(10)
    print(f"\nBytes at position 116: {next_bytes}")
    print(f"As integers: {[b for b in next_bytes]}")
    print(f"As ASCII: {repr(next_bytes)}")
    
    # Let's read up to position 116 manually
    buffer.seek(0)
    reader = MHDBinaryReader(buffer)
    
    # Read each field and track position
    display_name = reader.read_string()
    print(f"\nAfter display_name: {buffer.tell()}")
    
    hitpoints = reader.read_int32()
    print(f"After hitpoints: {buffer.tell()}")
    
    hp_cap = reader.read_single()
    print(f"After hp_cap: {buffer.tell()}")
    
    desc_long = reader.read_string()
    print(f"After desc_long: {buffer.tell()}")
    
    res_cap = reader.read_single()
    print(f"After res_cap: {buffer.tell()}")
    
    origin_count = reader.read_int32()
    print(f"After origin_count: {buffer.tell()}")
    
    for i in range(origin_count + 1):
        origin = reader.read_string()
        print(f"After origin {i}: {buffer.tell()}")
    
    class_name = reader.read_string()
    print(f"After class_name: {buffer.tell()}")
    
    class_type = reader.read_int32()
    print(f"After class_type: {buffer.tell()}")
    
    column = reader.read_int32()
    print(f"After column: {buffer.tell()}")
    
    desc_short = reader.read_string()
    print(f"After desc_short: {buffer.tell()}")
    
    print(f"\nCurrent position: {buffer.tell()}")
    print(f"Next byte: {buffer.read(1)}")


if __name__ == "__main__":
    test_debug_binary_position()