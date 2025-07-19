#!/usr/bin/env python3
"""Parse I12_extracted.txt file and convert to JSON format for import."""

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List


def parse_i12_text_file(input_file: Path, output_file: Path) -> None:
    """Parse I12 text file and convert to JSON format."""
    print(f"Parsing {input_file}...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into sections
    sections = content.split('BEGIN:')
    
    powers = []
    current_section = None
    
    for section in sections[1:]:  # Skip first empty section
        lines = section.strip().split('\n')
        if not lines:
            continue
            
        section_type = lines[0].rstrip('<')
        
        if section_type == 'POWERS':
            # Parse powers section
            powers = parse_powers_section('\n'.join(lines[1:]))
            break
    
    # Create JSON structure
    result = {
        "powers": powers,
        "metadata": {
            "source": "I12_extracted.txt",
            "total_powers": len(powers),
            "parsed_by": "parse_i12_text.py"
        }
    }
    
    print(f"Parsed {len(powers)} powers")
    
    # Write JSON output
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"Written to {output_file}")


def parse_powers_section(powers_text: str) -> List[Dict[str, Any]]:
    """Parse the powers section from I12 text."""
    powers = []
    
    # Split powers by looking for lines that start with special characters followed by a power identifier
    # Pattern: ^[special_char][Powerset].[PowerClass].[PowerName]
    power_blocks = re.split(r'\n(?=.+\.[A-Za-z_]+\.[A-Za-z_]+\n)', powers_text)
    
    for block in power_blocks:
        if not block.strip():
            continue
            
        power = parse_single_power(block.strip())
        if power:
            powers.append(power)
    
    return powers


def parse_single_power(power_text: str) -> Dict[str, Any] | None:
    """Parse a single power from its text block."""
    lines = power_text.split('\n')
    if len(lines) < 2:
        return None
    
    # First line is typically the power identifier, may have leading special character
    power_id = lines[0].strip()
    if '.' not in power_id:
        return None
    
    # Clean the power_id by removing any non-alphanumeric characters from the start
    clean_power_id = power_id
    while clean_power_id and not (clean_power_id[0].isalnum() or clean_power_id[0] == '_'):
        clean_power_id = clean_power_id[1:]
    
    # Also remove any trailing non-alphanumeric characters except underscore and dot
    import re
    clean_power_id = re.sub(r'[^A-Za-z0-9_.].*$', '', clean_power_id)
    
    parts = clean_power_id.split('.')
    if len(parts) < 3:  # Should be Powerset.PowerClass.PowerName
        return None
    
    powerset_name = parts[0]
    power_class = parts[1]
    power_name = parts[2]
    
    # Map I12 powerset names to database names
    # The pattern is: Arachnos_Soldiers.Arachnos_Soldier -> Arachnos_Soldier
    # So we use the power_class as the powerset name for database lookup
    db_powerset_name = power_class
    
    power = {
        "internal_name": clean_power_id,
        "display_name": power_name.replace('_', ' '),
        "powerset": db_powerset_name,  # Use power_class as powerset name
        "description": "",
        "level_available": 1,
        "power_type": "Unknown",
        "accuracy": 1.0,
        "activation_time": 0.0,
        "recharge_time": 0.0,
        "endurance_cost": 0.0,
        "range": 0.0,
        "effects": [],
        "enhancements_allowed": [],
        "raw_data": power_text
    }
    
    # Parse additional data from remaining lines
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
            
        # Look for specific patterns
        if line.startswith('Level:'):
            try:
                power["level_available"] = int(line.split(':')[1].strip())
            except (ValueError, IndexError):
                pass
        elif line.startswith('Type:'):
            power["power_type"] = line.split(':', 1)[1].strip()
        elif line.startswith('Accuracy:'):
            try:
                power["accuracy"] = float(line.split(':')[1].strip())
            except (ValueError, IndexError):
                pass
        elif line.startswith('ActivatePeriod:'):
            try:
                power["activation_time"] = float(line.split(':')[1].strip())
            except (ValueError, IndexError):
                pass
        elif line.startswith('RechargeTime:'):
            try:
                power["recharge_time"] = float(line.split(':')[1].strip())
            except (ValueError, IndexError):
                pass
        elif line.startswith('EndCost:'):
            try:
                power["endurance_cost"] = float(line.split(':')[1].strip())
            except (ValueError, IndexError):
                pass
        elif line.startswith('Range:'):
            try:
                power["range"] = float(line.split(':')[1].strip())
            except (ValueError, IndexError):
                pass
        elif not power["description"] and len(line) > 10:
            # Use first substantial line as description
            power["description"] = line
    
    return power


def main():
    """Main entry point."""
    if len(sys.argv) != 3:
        print("Usage: python parse_i12_text.py <input_file> <output_file>")
        print("Example: python parse_i12_text.py ../data/exported-json-latest/I12_extracted.txt ../data/exported-json-latest/I12_powers.json")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])
    
    if not input_file.exists():
        print(f"Error: Input file {input_file} does not exist")
        sys.exit(1)
    
    parse_i12_text_file(input_file, output_file)
    print("✅ I12 text parsing completed!")


if __name__ == "__main__":
    main()