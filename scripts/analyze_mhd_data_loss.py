#!/usr/bin/env python3
"""Analyze data loss from text extraction vs binary parsing."""

import struct
import json
from pathlib import Path
from collections import defaultdict


def analyze_mhd_structure(file_path):
    """Analyze the binary structure of an MHD file."""
    
    with open(file_path, 'rb') as f:
        data = f.read()
    
    # MHD files use specific data types:
    # - Strings: 7-bit encoded length + UTF-8 data
    # - Integers: 4 bytes little-endian
    # - Floats: 4 bytes IEEE 754
    # - Booleans: 1 byte
    # - Arrays: 4-byte count + elements
    
    analysis = {
        'file_size': len(data),
        'data_types_found': defaultdict(int),
        'numeric_values': [],
        'float_values': [],
        'boolean_values': [],
        'array_counts': [],
        'string_lengths': []
    }
    
    offset = 0
    
    # Skip header
    offset += 35  # "Mids' Hero Designer Database MK II"
    
    # Scan for patterns
    while offset < len(data) - 4:
        try:
            # Check for float pattern (common in power data)
            float_val = struct.unpack('<f', data[offset:offset+4])[0]
            if -1000 < float_val < 1000 and float_val != 0 and not float_val.is_integer():
                analysis['float_values'].append(float_val)
                analysis['data_types_found']['float'] += 1
            
            # Check for integer pattern
            int_val = struct.unpack('<i', data[offset:offset+4])[0]
            if 0 < int_val < 1000000:  # Reasonable range for game data
                if int_val < 256:
                    # Could be array count or level
                    analysis['array_counts'].append(int_val)
                analysis['numeric_values'].append(int_val)
                analysis['data_types_found']['integer'] += 1
            
            # Check for boolean
            if data[offset] in [0, 1] and offset < len(data) - 1 and data[offset+1] > 127:
                analysis['boolean_values'].append(data[offset])
                analysis['data_types_found']['boolean'] += 1
            
            # Check for 7-bit encoded string length
            str_len, new_offset = read_7bit_encoded_int(data, offset)
            if 0 < str_len < 500 and new_offset + str_len <= len(data):
                try:
                    text = data[new_offset:new_offset + str_len].decode('utf-8')
                    if text.isprintable() or '\n' in text:
                        analysis['string_lengths'].append(str_len)
                        analysis['data_types_found']['string'] += 1
                        offset = new_offset + str_len
                        continue
                except:
                    pass
            
            offset += 1
            
        except:
            offset += 1
    
    return analysis


def read_7bit_encoded_int(data, offset):
    """Read a 7-bit encoded integer (used for string lengths)."""
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


def compare_with_extracted_text(mhd_file, text_file):
    """Compare binary content with extracted text."""
    
    # Analyze binary
    binary_analysis = analyze_mhd_structure(mhd_file)
    
    # Count text content
    with open(text_file, 'r', encoding='utf-8', errors='ignore') as f:
        text_lines = f.readlines()
    
    text_analysis = {
        'total_lines': len(text_lines),
        'numeric_lines': 0,
        'float_lines': 0,
        'power_entries': 0,
        'enhancement_entries': 0
    }
    
    # Analyze text patterns
    for line in text_lines:
        line = line.strip()
        
        # Count numeric data
        try:
            if '.' in line:
                float(line)
                text_analysis['float_lines'] += 1
            else:
                int(line)
                text_analysis['numeric_lines'] += 1
        except:
            pass
        
        # Count game entities
        if '.Power.' in line or '_Power.' in line:
            text_analysis['power_entries'] += 1
        elif 'Enhancement' in line or 'enhancement' in line:
            text_analysis['enhancement_entries'] += 1
    
    # Calculate potential data loss
    print("=== MHD Data Loss Analysis ===\n")
    
    print(f"Binary File Analysis ({mhd_file.name}):")
    print(f"  File size: {binary_analysis['file_size']:,} bytes")
    print(f"  Floats found: {len(binary_analysis['float_values']):,}")
    print(f"  Integers found: {len(binary_analysis['numeric_values']):,}")
    print(f"  Booleans found: {len(binary_analysis['boolean_values']):,}")
    print(f"  Strings found: {binary_analysis['data_types_found']['string']:,}")
    
    if binary_analysis['float_values']:
        print(f"  Sample floats: {binary_analysis['float_values'][:5]}")
    
    print(f"\nText Extraction Analysis ({text_file.name}):")
    print(f"  Total lines: {text_analysis['total_lines']:,}")
    print(f"  Numeric lines: {text_analysis['numeric_lines']:,}")
    print(f"  Float lines: {text_analysis['float_lines']:,}")
    print(f"  Power entries: {text_analysis['power_entries']:,}")
    
    print("\n=== Data Loss Assessment ===")
    
    # Critical data types that are lost
    losses = []
    
    # 1. Numeric precision
    if len(binary_analysis['float_values']) > text_analysis['float_lines']:
        losses.append(f"CRITICAL: Missing {len(binary_analysis['float_values']) - text_analysis['float_lines']:,} float values")
        losses.append("  - Power attributes (damage, accuracy, recharge times)")
        losses.append("  - Enhancement values (bonuses, modifiers)")
    
    # 2. Boolean flags
    if binary_analysis['boolean_values']:
        losses.append(f"MODERATE: Lost {len(binary_analysis['boolean_values']):,} boolean flags")
        losses.append("  - Power availability flags")
        losses.append("  - Feature toggles")
    
    # 3. Array structures
    if binary_analysis['array_counts']:
        losses.append("CRITICAL: Lost array/list structures")
        losses.append("  - Power effect lists")
        losses.append("  - Enhancement set memberships")
        losses.append("  - Allowed archetype lists")
    
    # 4. Data relationships
    losses.append("CRITICAL: Lost data relationships")
    losses.append("  - Parent-child relationships (powerset → powers)")
    losses.append("  - Cross-references (enhancement → power)")
    losses.append("  - Index-based references")
    
    # 5. Metadata
    losses.append("MODERATE: Lost metadata")
    losses.append("  - Version information")
    losses.append("  - Data type markers")
    losses.append("  - Null vs empty string distinction")
    
    for loss in losses:
        print(f"  {loss}")
    
    return binary_analysis, text_analysis


def main():
    """Run the analysis."""
    
    # Analyze original I12
    orig_text = Path("data/exported-json-latest/I12_extracted.txt")
    
    # Analyze dev version
    dev_mhd = Path("external/dev/I12-dev-071925.mhd")
    dev_text = Path("data/dev/I12-dev-071925_extracted.txt")
    
    if dev_mhd.exists() and dev_text.exists():
        print("Analyzing I12-dev-071925.mhd...\n")
        compare_with_extracted_text(dev_mhd, dev_text)
    
    # Check a sample of the JSON to see what's preserved
    print("\n=== JSON Structure Check ===")
    
    json_file = Path("data/exported-json-latest/I12_powers.json")
    if json_file.exists():
        with open(json_file, 'r') as f:
            powers = json.load(f)
        
        if powers and 'powers' in powers:
            sample_power = powers['powers'][0]
            print(f"\nSample power structure:")
            for key, value in sample_power.items():
                print(f"  {key}: {type(value).__name__} = {str(value)[:50]}...")
            
            # Check for numeric data
            numeric_fields = ['accuracy', 'activation_time', 'recharge_time', 
                            'endurance_cost', 'range', 'level_available']
            
            preserved = [f for f in numeric_fields if f in sample_power and isinstance(sample_power[f], (int, float))]
            missing = [f for f in numeric_fields if f not in sample_power or sample_power[f] == 0]
            
            print(f"\nNumeric fields preserved: {preserved}")
            print(f"Numeric fields missing/zero: {missing}")


if __name__ == "__main__":
    main()