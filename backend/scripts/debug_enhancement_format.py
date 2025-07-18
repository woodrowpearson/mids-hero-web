#!/usr/bin/env python3
"""Deep dive into enhancement database format."""

import struct


def analyze_enhancement_db(file_path):
    """Analyze the enhancement database format in detail."""
    
    with open(file_path, 'rb') as f:
        # Read header
        header_len = struct.unpack('<I', f.read(4))[0]
        header = f.read(header_len).decode('utf-8', errors='replace')
        print(f"Header ({header_len} bytes): {header}")
        
        # Read version
        version_len = struct.unpack('<I', f.read(4))[0]
        if version_len > 0:
            version = f.read(version_len).decode('utf-8')
            print(f"Version ({version_len} bytes): {version}")
        else:
            print("Version: (empty)")
        
        # Read next values
        val1 = struct.unpack('<I', f.read(4))[0]
        print(f"\nValue 1: 0x{val1:08x} ({val1})")
        
        val2 = struct.unpack('<I', f.read(4))[0]
        print(f"Value 2: 0x{val2:08x} ({val2})")
        
        # Current position
        print(f"\nCurrent file position: {f.tell()}")
        
        # Read next 200 bytes and analyze
        print("\nNext 200 bytes:")
        data = f.read(200)
        
        # Show hex dump
        for i in range(0, len(data), 16):
            hex_str = ' '.join(f'{b:02x}' for b in data[i:i+16])
            ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
            print(f"{i:04x}: {hex_str:<48} {ascii_str}")
        
        # Try to find patterns
        print("\n\nLooking for string patterns...")
        
        # Reset to after header
        f.seek(0)
        f.read(4)  # header len
        f.read(header_len)  # header
        f.read(4)  # version len
        if version_len > 0:
            f.read(version_len)
        
        # Skip the two values we read
        f.read(8)
        
        # Try reading as different structures
        print("\nTrying to read first enhancement structure:")
        pos = f.tell()
        
        # Read what looks like static_index
        try:
            static_idx = struct.unpack('<I', f.read(4))[0]
            print(f"Static index?: 0x{static_idx:08x} ({static_idx})")
            
            # Look for strings
            next_bytes = f.read(50)
            print(f"Next 50 bytes: {next_bytes}")
            
            # Find null bytes
            null_positions = [i for i, b in enumerate(next_bytes) if b == 0]
            print(f"Null byte positions: {null_positions}")
            
            # Extract possible strings
            if null_positions:
                str1 = next_bytes[:null_positions[0]].decode('utf-8', errors='replace')
                print(f"Possible string 1: '{str1}'")
                
                if len(null_positions) > 1:
                    start = null_positions[0] + 1
                    end = null_positions[1]
                    if start < end:
                        str2 = next_bytes[start:end].decode('utf-8', errors='replace')
                        print(f"Possible string 2: '{str2}'")
        except Exception as e:
            print(f"Error: {e}")
        
        # Check file size
        f.seek(0, 2)  # End of file
        file_size = f.tell()
        print(f"\n\nTotal file size: {file_size:,} bytes")
        
        # If the count is really 5, and file is large, something's wrong
        if file_size > 1000:
            print("File is large enough to contain many enhancements")
            print("The count of '5' is likely incorrect")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python debug_enhancement_format.py <EnhDB.mhd>")
        sys.exit(1)
    
    analyze_enhancement_db(sys.argv[1])