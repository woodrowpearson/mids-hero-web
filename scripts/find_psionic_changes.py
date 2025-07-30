#!/usr/bin/env python3
"""Find all Psionic Armor related changes."""

import re
from pathlib import Path


def find_psionic_armor_entries(file_path):
    """Extract all Psionic Armor related entries."""
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Find all Psionic Armor power entries
    pattern = r'([A-Za-z_]+)\.Psionic_Armor\.([A-Za-z_]+)'
    matches = re.findall(pattern, content)
    
    # Extract context for each match
    entries = {}
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        if 'Psionic_Armor' in line:
            # Get archetype and power name
            match = re.search(pattern, line)
            if match:
                archetype = match.group(1)
                power_name = match.group(2)
                key = f"{archetype}.Psionic_Armor.{power_name}"
                
                # Collect next 15 lines for context
                context_lines = []
                for j in range(i, min(i + 15, len(lines))):
                    if lines[j].strip():
                        context_lines.append(lines[j].strip())
                
                entries[key] = '\n'.join(context_lines)
    
    return entries


def compare_psionic_powers(orig_file, dev_file):
    """Compare Psionic Armor powers between files."""
    
    print("=== Psionic Armor Power Analysis ===\n")
    
    orig_entries = find_psionic_armor_entries(orig_file)
    dev_entries = find_psionic_armor_entries(dev_file)
    
    print(f"Original file: {len(orig_entries)} Psionic Armor powers")
    print(f"Dev file: {len(dev_entries)} Psionic Armor powers\n")
    
    # Find all unique power names
    all_powers = set()
    for key in list(orig_entries.keys()) + list(dev_entries.keys()):
        if 'Psionic_Armor' in key:
            power_name = key.split('.')[-1]
            all_powers.add(power_name)
    
    print("Power Summary by Name:")
    for power in sorted(all_powers):
        print(f"\n{power}:")
        
        # Check each archetype
        for archetype in ['Brute_Defense', 'Scrapper_Defense', 'Tanker_Defense', 
                         'Stalker_Defense', 'Sentinel_Defense']:
            key = f"{archetype}.Psionic_Armor.{power}"
            
            in_orig = key in orig_entries
            in_dev = key in dev_entries
            
            if in_orig and in_dev:
                # Check if description changed
                orig_desc = orig_entries[key]
                dev_desc = dev_entries[key]
                
                if orig_desc != dev_desc:
                    print(f"  {archetype}: MODIFIED")
                    
                    # Look for specific changes
                    if 'debuff' in dev_desc.lower() and 'debuff' not in orig_desc.lower():
                        print(f"    - Added debuff resistance")
                    if 'absorption' in dev_desc.lower() and 'absorption' not in orig_desc.lower():
                        print(f"    - Added absorption")
                else:
                    print(f"  {archetype}: No changes")
            elif in_dev and not in_orig:
                print(f"  {archetype}: NEW in dev version")
            elif in_orig and not in_dev:
                print(f"  {archetype}: REMOVED in dev version")


def main():
    orig_file = Path("data/exported-json-latest/I12_extracted.txt")
    dev_file = Path("data/dev/I12-dev-071925_extracted.txt")
    
    compare_psionic_powers(orig_file, dev_file)


if __name__ == "__main__":
    main()