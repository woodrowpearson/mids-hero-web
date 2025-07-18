"""Raw enhancement parser that reads the file structure directly."""

import struct
from typing import List, Tuple
from dataclasses import dataclass, field
from .models import MHDEnhancement, MHDDatabase


def read_cstring(data: bytes, offset: int) -> Tuple[str, int]:
    """Read a null-terminated string from bytes."""
    end = data.find(b'\x00', offset)
    if end == -1:
        return "", len(data)
    
    string = data[offset:end].decode('utf-8', errors='replace')
    return string, end + 1


def read_pascal_string(data: bytes, offset: int) -> Tuple[str, int]:
    """Read a Pascal-style string (1-byte length prefix)."""
    if offset >= len(data):
        return "", offset
    
    length = data[offset]
    offset += 1
    
    if offset + length > len(data):
        return "", len(data)
    
    string = data[offset:offset + length].decode('utf-8', errors='replace')
    return string, offset + length


def analyze_enhancement_structure(file_path: str):
    """Analyze the enhancement file to understand its structure."""
    with open(file_path, 'rb') as f:
        data = f.read()
    
    print(f"File size: {len(data):,} bytes")
    
    # The file appears to start with "Mids Reborn Enhancement Database"
    # Let's find this string
    header_start = data.find(b'Mids Reborn Enhancement Database')
    if header_start == -1:
        print("Header not found!")
        return
    
    print(f"Header found at offset: {header_start}")
    
    # Skip the header string
    offset = header_start + len(b'Mids Reborn Enhancement Database') + 1
    
    # Look for enhancement data patterns
    # From the debug output, we see strings like "Accuracy", "Acc", etc.
    
    # Find all occurrences of "Accuracy" to understand the pattern
    accuracy_positions = []
    pos = 0
    while True:
        pos = data.find(b'Accuracy', pos)
        if pos == -1:
            break
        accuracy_positions.append(pos)
        pos += 1
    
    print(f"\nFound 'Accuracy' at {len(accuracy_positions)} positions: {accuracy_positions[:10]}...")
    
    # Let's examine the structure around the first few enhancements
    enhancements = []
    
    # Try to parse from after the header
    offset = 38  # Skip to where data seems to start based on debug output
    
    # The debug showed: 00000008 41636375726163790341636322...
    # This is: 0x08000000 (8 in little-endian), then "Accuracy", 0x03, "Acc"
    
    count = 0
    while offset < len(data) and count < 10:  # Parse first 10 for analysis
        try:
            # Read what might be an index
            if offset + 4 > len(data):
                break
            
            idx = struct.unpack_from('<I', data, offset)[0]
            offset += 4
            
            # Read name (null-terminated)
            name, offset = read_cstring(data, offset)
            if not name:
                # Try Pascal string
                name, offset = read_pascal_string(data, offset - 4)
                if not name:
                    break
            
            # Read short name (might be after a separator byte)
            if offset < len(data) and data[offset] < 32:  # Control character
                offset += 1  # Skip separator
            
            short_name, offset = read_pascal_string(data, offset)
            
            print(f"\nEnh{count}: idx={idx}, name='{name}', short='{short_name}'")
            print(f"  Next 20 bytes: {data[offset:offset+20].hex()}")
            
            enhancements.append({
                'index': idx,
                'name': name,
                'short_name': short_name,
                'offset': offset
            })
            
            count += 1
            
            # Skip to next enhancement (rough estimate)
            offset += 200  # Adjust based on actual structure
            
        except Exception as e:
            print(f"Error at offset {offset}: {e}")
            break
    
    return enhancements


def parse_enhancement_database_raw(file_path: str) -> MHDDatabase:
    """Parse EnhDB.mhd using direct byte reading.
    
    This parser is based on analyzing the actual file structure
    rather than assuming .NET BinaryWriter format.
    """
    db = MHDDatabase()
    
    with open(file_path, 'rb') as f:
        data = f.read()
    
    print(f"Loading enhancements from {len(data):,} byte file...")
    
    # Based on analysis, the file has a different structure
    # Skip to where enhancement data starts (after header)
    offset = 38  # Determined from hex analysis
    
    db.enhancements = []
    
    # The actual count seems to be much higher than 5
    # Let's parse until we run out of data or hit an error
    
    enhancement_count = 0
    errors = 0
    max_errors = 10
    
    while offset < len(data) - 100 and errors < max_errors:  # Leave buffer at end
        try:
            enh = MHDEnhancement()
            
            # Read index (4 bytes)
            enh.static_index = struct.unpack_from('<I', data, offset)[0]
            offset += 4
            
            # Handle odd indices (like 0x08000000)
            if enh.static_index > 100000:
                # Might be byte-swapped or contain flags
                enh.static_index = enh.static_index & 0xFF
            
            # Read name (null-terminated)
            name_end = data.find(b'\x00', offset)
            if name_end == -1 or name_end - offset > 100:
                raise ValueError("Invalid name length")
            
            enh.name = data[offset:name_end].decode('utf-8', errors='replace')
            offset = name_end + 1
            
            # Skip separator if present
            if offset < len(data) and data[offset] < 32:
                offset += 1
            
            # Read short name (Pascal string with 1-byte length)
            if offset >= len(data):
                raise ValueError("Unexpected end of data")
            
            short_len = data[offset]
            offset += 1
            
            if offset + short_len > len(data):
                raise ValueError("Short name extends past end of file")
            
            enh.short_name = data[offset:offset + short_len].decode('utf-8', errors='replace')
            offset += short_len
            
            # Skip more data for now (would need to reverse engineer full structure)
            # Just advance to approximate next record
            offset += 150  # Rough estimate
            
            db.enhancements.append(enh)
            enhancement_count += 1
            
            if enhancement_count % 50 == 0:
                print(f"  Loaded {enhancement_count} enhancements...")
            
            # Reset error count on success
            errors = 0
            
        except Exception as e:
            errors += 1
            if enhancement_count < 10 or errors < 3:
                print(f"Error parsing enhancement {enhancement_count} at offset {offset}: {e}")
            
            # Try to recover by searching for next valid enhancement
            # Look for pattern of 4-byte int followed by ASCII text
            found = False
            for search_offset in range(offset + 1, min(offset + 500, len(data) - 10)):
                try:
                    # Check if this looks like an enhancement start
                    test_idx = struct.unpack_from('<I', data, search_offset)[0]
                    if 0 <= test_idx < 10000:  # Reasonable index range
                        # Check if followed by readable text
                        if 32 <= data[search_offset + 4] < 127:  # ASCII
                            offset = search_offset
                            found = True
                            break
                except:
                    continue
            
            if not found:
                break
    
    print(f"\nSuccessfully parsed {len(db.enhancements)} enhancements")
    
    # Set version info
    db.version = "Homecoming"
    
    return db


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        # Run analysis
        analyze_enhancement_structure(sys.argv[1])
    else:
        print("Usage: python enhancement_raw_parser.py <EnhDB.mhd>")