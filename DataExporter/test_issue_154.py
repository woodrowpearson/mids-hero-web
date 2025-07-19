#!/usr/bin/env python3
"""Test to reproduce issue #154 - Enhancement Database Parser Format Issues"""

import struct
import io

def test_enhancement_db_format_issue():
    """Reproduce the issue where enhancement count is read as 1073741825 (0x40000001)"""
    
    # Create a test file that matches the problematic format
    data = io.BytesIO()
    
    # Header
    header = "Mids Reborn Enhancement Database"
    data.write(bytes([len(header)]))
    data.write(header.encode())
    
    # Empty version string (this is the key issue)
    data.write(bytes([0]))  # Version length = 0
    
    # The problematic bytes that are being misread
    data.write(struct.pack("<I", 0x40000000))  # This is likely a version/flag field
    data.write(struct.pack("<I", 5))  # This is the actual enhancement count
    
    # Reset to beginning to read
    data.seek(0)
    
    # Read as the buggy parser would
    header_len = data.read(1)[0]
    header_str = data.read(header_len).decode()
    print(f"Header: '{header_str}'")
    
    version_len = data.read(1)[0]
    print(f"Version length: {version_len} (empty string)")
    
    if version_len > 0:
        version = data.read(version_len).decode()
        print(f"Version: '{version}'")
    
    # Bug: Reading the next 4 bytes as count
    wrong_count_bytes = data.read(4)
    wrong_count = struct.unpack("<I", wrong_count_bytes)[0]
    print(f"Next 4 bytes: {wrong_count_bytes.hex()} (interpreted as {wrong_count})")
    print(f"In hex: 0x{wrong_count:08X}")
    
    # The actual count is in the following bytes
    actual_count_bytes = data.read(4)
    actual_count = struct.unpack("<I", actual_count_bytes)[0]
    print(f"Following bytes: {actual_count_bytes.hex()} (actual count = {actual_count})")
    
    # Show the issue
    print("\n=== ISSUE SUMMARY ===")
    print(f"Buggy parser reads count as: {wrong_count} (0x{wrong_count:08X})")
    print(f"Actual enhancement count is: {actual_count}")
    print("\nThe parser needs to skip the version/flag bytes (0x40000000) after the empty version string")
    
    return wrong_count == 0x40000000 and actual_count == 5

if __name__ == "__main__":
    print("Testing Enhancement Database Parser Format Issue (GitHub #154)\n")
    if test_enhancement_db_format_issue():
        print("\n✓ Successfully reproduced the issue!")
    else:
        print("\n✗ Could not reproduce the issue")