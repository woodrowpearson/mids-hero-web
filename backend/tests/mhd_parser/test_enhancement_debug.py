"""Debug script to analyze EnhDB.mhd format."""

import struct
from pathlib import Path

def analyze_enhdb_header(file_path):
    """Analyze the header of EnhDB.mhd file."""
    with open(file_path, 'rb') as f:
        # Read first 100 bytes as hex
        data = f.read(100)
        print("First 100 bytes (hex):")
        print(' '.join(f'{b:02x}' for b in data))
        print()
        
        # Reset to beginning
        f.seek(0)
        
        # Try to read as .NET BinaryReader format
        # First byte should be string length
        str_len = struct.unpack('B', f.read(1))[0]
        print(f"String length byte: {str_len}")
        
        # Read string
        header_str = f.read(str_len).decode('utf-8', errors='replace')
        print(f"Header string: '{header_str}'")
        
        # Next should be version string
        version_len = struct.unpack('B', f.read(1))[0]
        print(f"Version length byte: {version_len}")
        
        if version_len > 0 and version_len < 100:
            version_str = f.read(version_len).decode('utf-8', errors='replace')
            print(f"Version string: '{version_str}'")
        
        # Next should be enhancement count
        print(f"\nNext 4 bytes (potential count):")
        count_bytes = f.read(4)
        print(f"Hex: {' '.join(f'{b:02x}' for b in count_bytes)}")
        
        # Try different interpretations
        count_le = struct.unpack('<i', count_bytes)[0]  # Little-endian int32
        count_be = struct.unpack('>i', count_bytes)[0]  # Big-endian int32
        count_ule = struct.unpack('<I', count_bytes)[0]  # Little-endian uint32
        
        print(f"As little-endian int32: {count_le}")
        print(f"As big-endian int32: {count_be}")
        print(f"As little-endian uint32: {count_ule}")
        
        # Check if it's the problematic value
        if count_le == 1073741824:
            print("\nThis is 0x40000000 (2^30) - likely a flag or version number, not a count!")
        
        # Read next few integers to understand pattern
        print(f"\nNext 20 bytes:")
        next_bytes = f.read(20)
        print(f"Hex: {' '.join(f'{b:02x}' for b in next_bytes)}")
        
        # Try to interpret as int32 values
        for i in range(0, len(next_bytes)-3, 4):
            val = struct.unpack('<i', next_bytes[i:i+4])[0]
            print(f"  Bytes {i}-{i+3} as int32: {val}")


def check_archive_parser():
    """Check if there's a parser in the archive that handles this correctly."""
    archive_parser = Path("/Users/w/code/mids-hero-web/backend/archive/mhd_parser/enhancement_database_parser.py")
    if archive_parser.exists():
        print("\nFound archived enhancement parser - checking implementation...")
        with open(archive_parser, 'r') as f:
            content = f.read()
            if "parse_enhancement_database" in content:
                print("Archive has enhancement database parser - might have correct format!")
                # Look for count reading logic
                for line in content.split('\n'):
                    if 'count' in line.lower() and ('read' in line or 'struct' in line):
                        print(f"  {line.strip()}")


if __name__ == "__main__":
    enhdb_path = "/Users/w/code/mids-hero-web/data/Homecoming_2025-7-1111/EnhDB.mhd"
    
    print(f"Analyzing: {enhdb_path}")
    print("=" * 60)
    
    analyze_enhdb_header(enhdb_path)
    print("\n" + "=" * 60)
    check_archive_parser()