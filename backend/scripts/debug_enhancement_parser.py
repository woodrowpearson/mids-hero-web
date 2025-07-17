#!/usr/bin/env python3
"""Debug script to inspect enhancement database format."""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.mhd_parser.binary_reader import BinaryReader


def debug_enhancement_db(file_path):
    """Debug the enhancement database format."""
    print(f"Debugging: {file_path}")
    
    with open(file_path, 'rb') as f:
        reader = BinaryReader(f)
        
        # Read header
        header = reader.read_string()
        print(f"Header: {header}")
        
        # Read version
        version = reader.read_string()
        print(f"Version: {version}")
        
        # Read flag/count
        flag_or_count = reader.read_uint32()
        print(f"Flag/Count (hex): 0x{flag_or_count:08x} (decimal: {flag_or_count})")
        
        # If it's the flag, read the actual count
        if flag_or_count == 0x40000000:
            actual_count = reader.read_uint32()
            print(f"Actual count: {actual_count}")
        else:
            actual_count = flag_or_count
            print(f"Using flag as count: {actual_count}")
        
        print(f"\nAttempting to read first enhancement...")
        print(f"Current position: {f.tell()}")
        
        # Show raw bytes from current position
        current_pos = f.tell()
        raw_preview = f.read(100)
        f.seek(current_pos)
        print(f"Next 100 bytes from position {current_pos}:")
        print(f"Hex: {raw_preview.hex()}")
        print(f"ASCII: {raw_preview.decode('utf-8', errors='replace')}")
        
        # Try to read first enhancement fields
        print("\nReading static_index...")
        static_index = reader.read_int32()
        print(f"static_index: {static_index} (hex: 0x{static_index:08x})")
        
        print("\nTrying to read name string...")
        print(f"Position before string: {f.tell()}")
        
        # Read raw bytes to inspect
        f.seek(f.tell())  # Save position
        raw_bytes = f.read(20)
        print(f"Next 20 bytes (hex): {raw_bytes.hex()}")
        print(f"Next 20 bytes (raw): {raw_bytes}")
        
        # Try different interpretations
        f.seek(f.tell() - 20)  # Go back
        
        # Check if static_index has wrong byte order
        f.seek(f.tell() - 24)  # Go back to static_index position
        print(f"\nRe-reading static_index with different byte orders:")
        static_idx_bytes = f.read(4)
        print(f"Raw bytes: {static_idx_bytes.hex()}")
        print(f"Little endian: {int.from_bytes(static_idx_bytes, 'little')}")
        print(f"Big endian: {int.from_bytes(static_idx_bytes, 'big')}")
        
        # Now try to read strings as null-terminated
        print(f"\nTrying to read null-terminated strings:")
        
        # Read name
        name_bytes = bytearray()
        while True:
            b = f.read(1)
            if not b or b == b'\x00':
                break
            name_bytes.extend(b)
        print(f"Name: {name_bytes.decode('utf-8', errors='replace')}")
        
        # Read short name  
        short_name_bytes = bytearray()
        while True:
            b = f.read(1)
            if not b or b == b'\x00':
                break
            short_name_bytes.extend(b)
        print(f"Short name: {short_name_bytes.decode('utf-8', errors='replace')}")
        
        # Read description
        desc_bytes = bytearray()
        while True:
            b = f.read(1)
            if not b or b == b'\x00':
                break
            desc_bytes.extend(b)
        print(f"Description (first 50 chars): {desc_bytes.decode('utf-8', errors='replace')[:50]}...")
        
        print(f"\nCurrent position after 3 strings: {f.tell()}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_enhancement_parser.py <EnhDB.mhd>")
        sys.exit(1)
    
    debug_enhancement_db(sys.argv[1])