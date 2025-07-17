"""Test MHD parser functionality."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.mhd_parser import parse_main_database


def test_parse_i12():
    """Test parsing the I12.mhd file."""
    # Path to the Homecoming data
    data_path = Path("/Users/w/code/Homecoming_2025.7.1111/I12.mhd")
    
    if not data_path.exists():
        print(f"Data file not found: {data_path}")
        return
    
    print(f"Testing parser with: {data_path}")
    
    try:
        db = parse_main_database(str(data_path))
        
        print(f"\nDatabase Info:")
        print(f"  Version: {db.version}")
        print(f"  Date: {db.date}")
        print(f"  Issue: {db.issue}")
        print(f"  Page Vol: {db.page_vol} ({db.page_vol_text})")
        
        print(f"\nData Counts:")
        print(f"  Archetypes: {len(db.archetypes)}")
        print(f"  Powersets: {len(db.powersets)}")
        print(f"  Powers: {len(db.powers)}")
        
        print(f"\nSample Archetypes:")
        for arch in db.archetypes[:10]:
            print(f"  - {arch.display_name} ({arch.class_name})")
            print(f"    HP: {arch.hitpoints}, HP Cap: {arch.hp_cap}")
            print(f"    Primary: {arch.primary_group}, Secondary: {arch.secondary_group}")
            print(f"    Playable: {arch.playable}")
            print()
        
        print(f"\nSample Powersets:")
        for ps in db.powersets[:10]:
            print(f"  - {ps.display_name} ({ps.full_name})")
            print(f"    Type: {ps.set_type}, AT: {ps.at_class}")
            print()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_parse_i12()