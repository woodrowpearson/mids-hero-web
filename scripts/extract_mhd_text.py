#!/usr/bin/env python3
"""Simple MHD text extractor for comparing versions."""

import struct
import sys
from pathlib import Path


def read_7bit_encoded_int(data, offset):
    """Read a 7-bit encoded integer from the data."""
    result = 0
    shift = 0
    
    while offset < len(data):
        byte = data[offset]
        offset += 1
        
        result |= (byte & 0x7F) << shift
        
        if (byte & 0x80) == 0:
            break
            
        shift += 7
        
    return result, offset


def extract_strings_from_mhd(file_path, output_path):
    """Extract readable strings from MHD file."""
    
    with open(file_path, 'rb') as f:
        data = f.read()
    
    strings = []
    offset = 0
    
    # Try to extract strings using 7-bit encoding
    while offset < len(data) - 1:
        try:
            # Try to read string length
            str_len, new_offset = read_7bit_encoded_int(data, offset)
            
            # Sanity check
            if str_len > 0 and str_len < 1000 and new_offset + str_len <= len(data):
                # Try to decode as UTF-8
                try:
                    text = data[new_offset:new_offset + str_len].decode('utf-8')
                    if text.isprintable() or '\n' in text:
                        strings.append(text)
                        offset = new_offset + str_len
                        continue
                except:
                    pass
            
            # Also try to find plain text strings
            if data[offset] >= 32 and data[offset] <= 126:
                text = bytearray()
                while offset < len(data) and data[offset] >= 32 and data[offset] <= 126:
                    text.append(data[offset])
                    offset += 1
                
                decoded = text.decode('ascii', errors='ignore')
                if len(decoded) > 4:  # Only keep strings longer than 4 chars
                    strings.append(decoded)
            else:
                offset += 1
                
        except:
            offset += 1
    
    # Write extracted strings to file
    with open(output_path, 'w', encoding='utf-8') as f:
        for s in strings:
            f.write(s + '\n')
    
    print(f"Extracted {len(strings)} strings to {output_path}")
    
    # Look for specific patterns related to Psychokinetic Barrier
    psycho_strings = [s for s in strings if 'Psychokinetic' in s or 'Barrier' in s]
    if psycho_strings:
        print("\nFound strings related to Psychokinetic Barrier:")
        for s in psycho_strings[:10]:  # Show first 10
            print(f"  - {s[:100]}...")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python extract_mhd_text.py <input.mhd> <output.txt>")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])
    
    if not input_file.exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)
    
    extract_strings_from_mhd(input_file, output_file)