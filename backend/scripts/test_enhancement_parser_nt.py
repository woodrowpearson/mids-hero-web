#!/usr/bin/env python3
"""Test the enhanced enhancement parser."""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.mhd_parser.enhancement_parser_nt import parse_enhancement_database_nt


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_enhancement_parser_nt.py <EnhDB.mhd>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        db = parse_enhancement_database_nt(file_path)
        
        print(f"\nParsing complete!")
        print(f"Total enhancements loaded: {len(db.enhancements)}")
        
        if db.enhancements:
            print("\nFirst 5 enhancements:")
            for i, enh in enumerate(db.enhancements[:5]):
                print(f"{i+1}. {enh.name} (ID: {enh.static_index})")
                print(f"   Short: {enh.short_name}")
                print(f"   Type: {enh.type_id}, Subtype: {enh.sub_type_id}")
                print(f"   Image: {enh.image}")
                print(f"   Set ID: {enh.set_id}")
                print()
        
        # Check for enhancement sets
        sets = {}
        for enh in db.enhancements:
            if enh.set_id >= 0:
                sets[enh.set_id] = sets.get(enh.set_id, 0) + 1
        
        print(f"Enhancement sets found: {len(sets)}")
        print(f"Standalone enhancements: {sum(1 for e in db.enhancements if e.set_id < 0)}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()