#!/usr/bin/env python3
"""Compare Psychokinetic Barrier entries between two extracted files."""

import sys
import re
from pathlib import Path


def extract_power_blocks(file_path, power_name):
    """Extract blocks of text related to a specific power."""
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    blocks = []
    current_block = []
    in_block = False
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Start of a power block
        if power_name in line and ('Defense' in line or '_Armor' in line):
            in_block = True
            current_block = [line]
            # Look back a few lines for context
            for j in range(max(0, i-5), i):
                current_block.insert(0, lines[j].strip())
        elif in_block:
            current_block.append(line)
            # End block after description or significant gap
            if len(current_block) > 15 or (line == '' and len(current_block) > 5):
                blocks.append('\n'.join(current_block))
                current_block = []
                in_block = False
    
    return blocks


def compare_files(orig_file, dev_file):
    """Compare Psychokinetic Barrier between files."""
    
    print("=== Psychokinetic Barrier Comparison ===\n")
    
    # Extract blocks for each archetype
    archetypes = ['Brute', 'Scrapper', 'Sentinel', 'Tanker', 'Stalker']
    
    for archetype in archetypes:
        print(f"\n--- {archetype} ---")
        
        # Find blocks containing both archetype and power
        orig_blocks = extract_power_blocks(orig_file, 'Psychokinetic_Barrier')
        dev_blocks = extract_power_blocks(dev_file, 'Psychokinetic_Barrier')
        
        # Filter by archetype
        orig_arch_blocks = [b for b in orig_blocks if archetype in b]
        dev_arch_blocks = [b for b in dev_blocks if archetype in b]
        
        if orig_arch_blocks or dev_arch_blocks:
            # Find description differences
            orig_desc = None
            dev_desc = None
            
            for block in orig_arch_blocks:
                lines = block.split('\n')
                for line in lines:
                    if 'crystalized psionic energy' in line:
                        # Get full description
                        idx = lines.index(line)
                        desc_lines = []
                        for j in range(idx, min(idx + 3, len(lines))):
                            if lines[j]:
                                desc_lines.append(lines[j])
                        orig_desc = ' '.join(desc_lines)
                        break
            
            for block in dev_arch_blocks:
                lines = block.split('\n')
                for line in lines:
                    if 'crystalized psionic energy' in line:
                        # Get full description
                        idx = lines.index(line)
                        desc_lines = []
                        for j in range(idx, min(idx + 3, len(lines))):
                            if lines[j]:
                                desc_lines.append(lines[j])
                        dev_desc = ' '.join(desc_lines)
                        break
            
            if orig_desc and dev_desc:
                if orig_desc != dev_desc:
                    print(f"\nOriginal description:")
                    print(f"  {orig_desc}")
                    print(f"\nNew description:")
                    print(f"  {dev_desc}")
                    print(f"\nCHANGE DETECTED!")
                else:
                    print("  No changes in description")
            elif dev_desc and not orig_desc:
                print(f"\nNEW ENTRY:")
                print(f"  {dev_desc}")
            elif orig_desc and not dev_desc:
                print(f"\nREMOVED ENTRY")


if __name__ == "__main__":
    orig_file = Path("data/exported-json-latest/I12_extracted.txt")
    dev_file = Path("data/dev/I12-dev-071925_extracted.txt")
    
    if not orig_file.exists():
        print(f"Error: {orig_file} not found")
        sys.exit(1)
    
    if not dev_file.exists():
        print(f"Error: {dev_file} not found")
        sys.exit(1)
    
    compare_files(orig_file, dev_file)