#!/usr/bin/env python3
"""Comprehensive comparison of MHD file changes."""

import re
from pathlib import Path
from collections import defaultdict
from difflib import SequenceMatcher


def extract_power_entries(file_path):
    """Extract all power entries with their descriptions."""
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Split into lines for processing
    lines = content.split('\n')
    
    powers = {}
    current_power = None
    current_lines = []
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Look for power identifiers (e.g., Brute_Defense.PowerSet.PowerName)
        if re.match(r'^[A-Za-z_]+\.[A-Za-z_]+\.[A-Za-z_]+$', line):
            # Save previous power if exists
            if current_power and current_lines:
                # Find description in the collected lines
                desc_lines = []
                for l in current_lines:
                    if any(keyword in l.lower() for keyword in ['you ', 'this ', 'your ', 'when ', 'while ', 'grants ', 'provides ']):
                        desc_lines.append(l)
                
                if desc_lines:
                    powers[current_power] = ' '.join(desc_lines)
            
            # Start new power
            current_power = line
            current_lines = [line]
        elif current_power and line:
            current_lines.append(line)
            # Stop collecting after ~20 lines to avoid mixing powers
            if len(current_lines) > 20:
                # Save and reset
                desc_lines = []
                for l in current_lines:
                    if any(keyword in l.lower() for keyword in ['you ', 'this ', 'your ', 'when ', 'while ', 'grants ', 'provides ']):
                        desc_lines.append(l)
                
                if desc_lines:
                    powers[current_power] = ' '.join(desc_lines)
                
                current_power = None
                current_lines = []
    
    return powers


def find_significant_changes(orig_powers, dev_powers):
    """Find powers with significant description changes."""
    
    changes = {
        'modified': [],
        'added': [],
        'removed': []
    }
    
    # Check for modified and removed powers
    for power, orig_desc in orig_powers.items():
        if power in dev_powers:
            dev_desc = dev_powers[power]
            # Use sequence matcher to find similarity
            similarity = SequenceMatcher(None, orig_desc, dev_desc).ratio()
            
            # If descriptions are different enough (less than 90% similar)
            if similarity < 0.9 and orig_desc != dev_desc:
                changes['modified'].append({
                    'power': power,
                    'original': orig_desc,
                    'new': dev_desc,
                    'similarity': similarity
                })
        else:
            changes['removed'].append({
                'power': power,
                'description': orig_desc
            })
    
    # Check for added powers
    for power, dev_desc in dev_powers.items():
        if power not in orig_powers:
            changes['added'].append({
                'power': power,
                'description': dev_desc
            })
    
    return changes


def analyze_changes_by_category(changes):
    """Group changes by powerset/archetype."""
    
    categories = defaultdict(list)
    
    for change in changes['modified']:
        parts = change['power'].split('.')
        if len(parts) >= 2:
            category = f"{parts[0]}.{parts[1]}"
            categories[category].append(change)
    
    return categories


def main():
    """Main comparison function."""
    
    orig_file = Path("data/exported-json-latest/I12_extracted.txt")
    dev_file = Path("data/dev/I12-dev-071925_extracted.txt")
    
    print("=== Comprehensive MHD File Change Analysis ===\n")
    print("Extracting power data from files...")
    
    orig_powers = extract_power_entries(orig_file)
    dev_powers = extract_power_entries(dev_file)
    
    print(f"Original file: {len(orig_powers)} powers found")
    print(f"Dev file: {len(dev_powers)} powers found\n")
    
    changes = find_significant_changes(orig_powers, dev_powers)
    
    print(f"Summary of Changes:")
    print(f"- Modified: {len(changes['modified'])} powers")
    print(f"- Added: {len(changes['added'])} powers")
    print(f"- Removed: {len(changes['removed'])} powers")
    
    if changes['modified']:
        print("\n=== MODIFIED POWERS ===")
        
        # Group by category
        categories = analyze_changes_by_category(changes)
        
        # Sort by most changes
        sorted_categories = sorted(categories.items(), key=lambda x: len(x[1]), reverse=True)
        
        for category, category_changes in sorted_categories[:10]:  # Show top 10 categories
            print(f"\n{category} ({len(category_changes)} changes):")
            
            for change in category_changes[:3]:  # Show first 3 changes per category
                print(f"\n  Power: {change['power']}")
                print(f"  Similarity: {change['similarity']:.1%}")
                
                # Show key differences
                orig_words = set(change['original'].split())
                new_words = set(change['new'].split())
                
                added_words = new_words - orig_words
                removed_words = orig_words - new_words
                
                if added_words:
                    print(f"  Added: {' '.join(list(added_words)[:10])}")
                if removed_words:
                    print(f"  Removed: {' '.join(list(removed_words)[:10])}")
    
    # Look for patterns in changes
    print("\n=== CHANGE PATTERNS ===")
    
    # Count common added phrases
    added_phrases = defaultdict(int)
    for change in changes['modified']:
        if 'debuff' in change['new'] and 'debuff' not in change['original']:
            added_phrases['debuff resistance'] += 1
        if 'absorption' in change['new'] and 'absorption' not in change['original']:
            added_phrases['absorption'] += 1
        if 'moderate' in change['new'] and 'moderate' not in change['original']:
            added_phrases['moderate'] += 1
    
    if added_phrases:
        print("\nCommonly added terms:")
        for phrase, count in sorted(added_phrases.items(), key=lambda x: x[1], reverse=True):
            print(f"  - '{phrase}': {count} occurrences")
    
    # Save detailed report
    with open("data/dev/mhd_changes_detailed_report.txt", "w") as f:
        f.write("=== DETAILED MHD CHANGES REPORT ===\n\n")
        
        f.write(f"Total changes: {len(changes['modified'])} modified, ")
        f.write(f"{len(changes['added'])} added, {len(changes['removed'])} removed\n\n")
        
        f.write("=== ALL MODIFIED POWERS ===\n")
        for change in sorted(changes['modified'], key=lambda x: x['similarity']):
            f.write(f"\nPower: {change['power']}\n")
            f.write(f"Similarity: {change['similarity']:.1%}\n")
            f.write(f"Original: {change['original']}\n")
            f.write(f"New: {change['new']}\n")
            f.write("-" * 80 + "\n")
    
    print(f"\nDetailed report saved to: data/dev/mhd_changes_detailed_report.txt")


if __name__ == "__main__":
    main()