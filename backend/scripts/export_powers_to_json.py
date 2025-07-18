#!/usr/bin/env python3
"""Export powers from MHD to JSON with proper formatting."""

import json
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.mhd_parser.parser import parse_main_database


def map_power_type(power_type_id: int) -> str:
    """Map power type enum to string."""
    power_type_map = {
        0: 'click',
        1: 'toggle',
        2: 'auto',
        3: 'passive',
        4: 'inherent'
    }
    return power_type_map.get(power_type_id, 'click')


def export_powers_complete(powers, powersets, output_dir):
    """Export powers to JSON with proper database mapping."""
    print(f"Exporting {len(powers)} powers...")
    
    # Create powerset name to ID map
    powerset_map = {}
    for i, ps in enumerate(powersets):
        powerset_map[ps.set_name] = i + 1  # 1-based IDs
    
    power_data = []
    powers_without_powerset = 0
    
    for power in powers:
        # Find powerset_id from power's set_name
        powerset_id = None
        if power.set_name:
            powerset_id = powerset_map.get(power.set_name)
            if not powerset_id:
                powers_without_powerset += 1
        
        # Map power data to database schema
        power_entry = {
            'id': power.static_index + 1,  # 1-based ID
            'name': power.power_name or power.full_name,
            'display_name': power.display_name or power.power_name,
            'description': power.desc_long or power.desc_short,
            'powerset_id': powerset_id,
            'level_available': power.available,
            'power_type': map_power_type(power.power_type),
            'accuracy': float(power.accuracy) if power.accuracy else 1.0,
            'endurance_cost': float(power.end_cost) if power.end_cost else 0.0,
            'recharge_time': float(power.recharge_time) if power.recharge_time else 0.0,
            'activation_time': float(power.cast_time) if power.cast_time else 0.0,
            'range_feet': float(power.range) if power.range else 0.0,
            # Additional fields that might be useful
            'group_name': power.group_name,
            'full_name': power.full_name
        }
        
        power_data.append(power_entry)
    
    # Sort by ID for consistency
    power_data.sort(key=lambda x: x['id'])
    
    # Save to file
    output_file = output_dir / 'powers_complete.json'
    with open(output_file, 'w') as f:
        json.dump(power_data, f, indent=2)
    
    print(f"Saved {len(power_data)} powers to {output_file}")
    print(f"Powers without powerset mapping: {powers_without_powerset}")
    
    # Also create a summary
    summary = {
        'total_powers': len(power_data),
        'powers_with_powerset': len([p for p in power_data if p['powerset_id']]),
        'powers_without_powerset': powers_without_powerset,
        'power_types': {}
    }
    
    # Count by type
    for power in power_data:
        ptype = power['power_type']
        summary['power_types'][ptype] = summary['power_types'].get(ptype, 0) + 1
    
    summary_file = output_dir / 'powers_summary.json'
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nPower type distribution:")
    for ptype, count in summary['power_types'].items():
        print(f"  {ptype}: {count}")
    
    return power_data


def main():
    """Main function."""
    if len(sys.argv) < 3:
        print("Usage: python export_powers_to_json.py <I12.mhd> <output_dir>")
        sys.exit(1)
    
    mhd_file = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    
    if not mhd_file.exists():
        print(f"Error: MHD file not found: {mhd_file}")
        sys.exit(1)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Loading {mhd_file}...")
    
    try:
        db = parse_main_database(str(mhd_file))
        
        print(f"Loaded {len(db.powers)} powers and {len(db.powersets)} powersets")
        
        # Export powers with proper mapping
        export_powers_complete(db.powers, db.powersets, output_dir)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()