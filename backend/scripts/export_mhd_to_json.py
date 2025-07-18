#!/usr/bin/env python3
"""Export MHD files to JSON format for database import."""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.mhd_parser.parser import parse_main_database, parse_enhancement_database
from app.mhd_parser.models import MHDArchetype, MHDPowerset, MHDPower, MHDEnhancement


def export_archetypes(archetypes, output_dir):
    """Export archetypes to JSON."""
    print(f"Exporting {len(archetypes)} archetypes...")
    
    archetype_data = []
    seen_names = set()
    
    for arch in archetypes:
        # Handle duplicate names by appending index
        name = arch.class_name
        if name in seen_names:
            name = f"{name}_{arch.idx}"
        seen_names.add(name)
        
        # Map MHD archetype to database schema
        archetype_data.append({
            'id': arch.idx + 1,  # Convert 0-based to 1-based ID
            'name': name,
            'display_name': arch.display_name,
            'description': arch.desc_long,
            'primary_group': arch.primary_group,
            'secondary_group': arch.secondary_group,
            'hit_points_base': arch.hitpoints,
            'hit_points_max': int(arch.hitpoints * arch.hp_cap) if arch.hp_cap > 0 else arch.hitpoints,
            # Note: inherent_power_id will need to be set later after powers are imported
        })
    
    output_file = output_dir / 'archetypes.json'
    with open(output_file, 'w') as f:
        json.dump(archetype_data, f, indent=2)
    print(f"  Saved to {output_file}")
    
    return archetype_data


def export_powersets(powersets, archetype_map, output_dir):
    """Export powersets to JSON."""
    print(f"Exporting {len(powersets)} powersets...")
    
    powerset_data = []
    powerset_type_map = {
        0: 'primary',
        1: 'secondary',
        2: 'pool',
        3: 'epic',
        4: 'inherent',
        5: 'temporary',
        6: 'pet',
        7: 'incarnate'
    }
    
    for ps in powersets:
        # Skip invalid powersets
        if ps.archetype_id < 0 or ps.archetype_id >= len(archetype_map):
            continue
            
        powerset_data.append({
            'id': ps.nid + 1,  # Convert 0-based to 1-based ID
            'name': ps.set_name or ps.display_name,
            'display_name': ps.display_name,
            'description': ps.description,
            'archetype_id': ps.archetype_id + 1,  # Convert to 1-based
            'powerset_type': powerset_type_map.get(ps.set_type, 'other'),
            'icon_path': ps.image_name if ps.image_name else None,
        })
    
    output_file = output_dir / 'powersets.json'
    with open(output_file, 'w') as f:
        json.dump(powerset_data, f, indent=2)
    print(f"  Saved to {output_file}")
    
    return powerset_data


def export_powers(powers, powersets, output_dir):
    """Export powers to JSON with proper database mapping."""
    print(f"Exporting {len(powers)} powers...")
    
    # Create powerset name to ID map
    powerset_map = {}
    for i, ps in enumerate(powersets):
        powerset_map[ps.set_name] = i + 1  # 1-based IDs
    
    power_data = []
    powers_without_powerset = 0
    
    # Map power type enum to string
    power_type_map = {
        0: 'click',
        1: 'toggle', 
        2: 'auto',
        3: 'passive',
        4: 'inherent'
    }
    
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
            'description': power.desc_long or power.desc_short or "",
            'powerset_id': powerset_id,
            'level_available': power.available,
            'power_type': power_type_map.get(power.power_type, 'click'),
            'accuracy': float(power.accuracy) if power.accuracy else 1.0,
            'endurance_cost': float(power.end_cost) if power.end_cost else 0.0,
            'recharge_time': float(power.recharge_time) if power.recharge_time else 0.0,
            'activation_time': float(power.cast_time) if power.cast_time else 0.0,
            'range_feet': float(power.range) if power.range else 0.0
        }
        
        power_data.append(power_entry)
    
    # Sort by ID for consistency
    power_data.sort(key=lambda x: x['id'])
    
    output_file = output_dir / 'powers.json'
    with open(output_file, 'w') as f:
        json.dump(power_data, f, indent=2)
    print(f"  Saved to {output_file}")
    
    if powers_without_powerset > 0:
        print(f"  Warning: {powers_without_powerset} powers without powerset mapping")
    
    return power_data


def export_enhancements(enhancements, output_dir):
    """Export enhancements to JSON."""
    print(f"Exporting {len(enhancements)} enhancements...")
    
    enhancement_data = []
    enhancement_sets = {}
    
    # First pass: collect enhancement sets
    for enh in enhancements:
        if hasattr(enh, 'set_name') and enh.set_name:
            if enh.set_name not in enhancement_sets:
                enhancement_sets[enh.set_name] = {
                    'id': len(enhancement_sets) + 1,
                    'name': enh.set_name,
                    'display_name': enh.set_name,
                    'description': f"Enhancement set: {enh.set_name}",
                    'min_level': 10,  # Default values
                    'max_level': 50,
                }
    
    # Export enhancement sets
    sets_file = output_dir / 'enhancement_sets.json'
    with open(sets_file, 'w') as f:
        json.dump(list(enhancement_sets.values()), f, indent=2)
    print(f"  Saved {len(enhancement_sets)} sets to {sets_file}")
    
    # Second pass: export enhancements
    for i, enh in enumerate(enhancements):
        set_id = None
        if hasattr(enh, 'set_name') and enh.set_name and enh.set_name in enhancement_sets:
            set_id = enhancement_sets[enh.set_name]['id']
            
        enhancement_data.append({
            'id': i + 1,
            'name': enh.name,
            'display_name': enh.short_name or enh.name,
            'enhancement_type': 'set_piece' if set_id else 'IO',  # Simplified
            'set_id': set_id,
            'level_min': 1,  # Default values
            'level_max': 50,
            # TODO: Map actual enhancement bonuses when available
        })
    
    output_file = output_dir / 'enhancements.json'
    with open(output_file, 'w') as f:
        json.dump(enhancement_data, f, indent=2)
    print(f"  Saved to {output_file}")
    
    return enhancement_data, enhancement_sets


def main():
    """Main export function."""
    if len(sys.argv) < 3:
        print("Usage: python export_mhd_to_json.py <mhd_data_dir> <output_dir>")
        print("Example: python export_mhd_to_json.py ../data/Homecoming_2025-7-1111 ../data/exported-json")
        sys.exit(1)
    
    mhd_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    
    if not mhd_dir.exists():
        print(f"Error: MHD data directory not found: {mhd_dir}")
        sys.exit(1)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"MHD Data Directory: {mhd_dir}")
    print(f"Output Directory: {output_dir}")
    print()
    
    # Export metadata
    metadata = {
        'export_date': datetime.now().isoformat(),
        'source_directory': str(mhd_dir),
        'files_processed': []
    }
    
    # Parse and export main database
    i12_file = mhd_dir / 'I12.mhd'
    if i12_file.exists():
        print(f"Processing {i12_file.name}...")
        try:
            db = parse_main_database(str(i12_file))
            
            # Create archetype ID map
            archetype_map = {i: arch for i, arch in enumerate(db.archetypes)}
            
            # Export data
            export_archetypes(db.archetypes, output_dir)
            export_powersets(db.powersets, archetype_map, output_dir)
            export_powers(db.powers, db.powersets, output_dir)
            
            metadata['files_processed'].append({
                'file': 'I12.mhd',
                'version': db.version,
                'date': db.date.isoformat() if db.date else None,
                'archetypes': len(db.archetypes),
                'powersets': len(db.powersets),
                'powers': len(db.powers)
            })
        except Exception as e:
            print(f"Error processing I12.mhd: {e}")
            import traceback
            traceback.print_exc()
    
    # Parse and export enhancement database
    enhdb_file = mhd_dir / 'EnhDB.mhd'
    if enhdb_file.exists():
        print(f"\nProcessing {enhdb_file.name}...")
        try:
            enh_db = parse_enhancement_database(str(enhdb_file))
            export_enhancements(enh_db.enhancements, output_dir)
            
            metadata['files_processed'].append({
                'file': 'EnhDB.mhd',
                'version': enh_db.version,
                'enhancements': len(enh_db.enhancements)
            })
        except Exception as e:
            print(f"Error processing EnhDB.mhd: {e}")
            import traceback
            traceback.print_exc()
    
    # Save metadata
    metadata_file = output_dir / 'export_metadata.json'
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"\nExport metadata saved to {metadata_file}")
    
    print("\nExport complete!")


if __name__ == "__main__":
    main()