"""Main parser functions for MHD files."""

from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from .binary_reader import BinaryReader
from .models import MHDDatabase, MHDArchetype, MHDPowerset, MHDPower, MHDEnhancement


def parse_main_database(file_path: str) -> MHDDatabase:
    """Parse the main I12.mhd database file.
    
    Args:
        file_path: Path to the I12.mhd file
        
    Returns:
        MHDDatabase object containing all parsed data
    """
    db = MHDDatabase()
    
    with open(file_path, 'rb') as f:
        reader = BinaryReader(f)
        
        # Read header
        header = reader.read_string()
        if header != "Mids Reborn Powers Database":
            raise ValueError(f"Invalid database header: {header}")
        
        # Read version
        db.version = reader.read_string()
        
        # Read date info
        year = reader.read_int32()
        if year > 0:
            month = reader.read_int32()
            day = reader.read_int32()
            try:
                db.date = datetime(year, month, day)
            except ValueError:
                # Invalid date, use current date
                db.date = datetime.now()
        else:
            # .NET binary date format
            date_binary = reader.read_int64()
            try:
                # Convert from .NET ticks (100-nanosecond intervals since 1/1/0001)
                # to Python datetime
                ticks_per_second = 10000000
                seconds_since_epoch = (date_binary - 621355968000000000) / ticks_per_second
                db.date = datetime.fromtimestamp(seconds_since_epoch)
            except (ValueError, OSError):
                # Invalid timestamp, use current date
                db.date = datetime.now()
        
        db.issue = reader.read_int32()
        db.page_vol = reader.read_int32()
        db.page_vol_text = reader.read_string()
        
        # Read Archetypes
        section_header = reader.read_string()
        if section_header != "BEGIN:ARCHETYPES":
            raise ValueError(f"Expected Archetype section, got: {section_header}")
        
        archetype_count = reader.read_int32() + 1
        db.archetypes = []
        for i in range(archetype_count):
            db.archetypes.append(MHDArchetype.from_reader(reader, i))
        
        # Read Powersets
        section_header = reader.read_string()
        if section_header != "BEGIN:POWERSETS":
            raise ValueError(f"Expected Powerset section, got: {section_header}")
        
        powerset_count = reader.read_int32() + 1
        db.powersets = []
        for i in range(powerset_count):
            db.powersets.append(MHDPowerset.from_reader(reader, i))
        
        # Read Powers
        section_header = reader.read_string()
        if section_header != "BEGIN:POWERS":
            raise ValueError(f"Expected Power section, got: {section_header}")
        
        power_count = reader.read_int32() + 1
        db.powers = []
        print(f"Loading {power_count} powers...")
        
        # Parse all powers
        for i in range(power_count):
            if i % 1000 == 0:
                print(f"  Loaded {i}/{power_count} powers...")
            try:
                db.powers.append(MHDPower.from_reader(reader))
            except Exception as e:
                print(f"Error parsing power {i}: {e}")
                # Continue parsing remaining powers
                if i < 10:  # Only show first few errors
                    import traceback
                    traceback.print_exc()
        
        # Skip Summons/Entities section for now
        
    return db


def parse_enhancement_database(file_path: str) -> MHDDatabase:
    """Parse the EnhDB.mhd enhancement database file.
    
    Args:
        file_path: Path to the EnhDB.mhd file
        
    Returns:
        MHDDatabase object with enhancements populated
    """
    db = MHDDatabase()
    
    with open(file_path, 'rb') as f:
        reader = BinaryReader(f)
        
        # Read header
        header = reader.read_string()
        if "Enhancement" not in header:
            raise ValueError(f"Invalid enhancement database header: {header}")
        
        # Read version (may be empty)
        db.version = reader.read_string()
        
        # Skip version/flag bytes if present
        # The file has 0x40000000 (1073741824) which is not a count
        flag_or_date = reader.read_uint32()
        if flag_or_date == 0x40000000:
            # This is a flag, actual count follows
            enhancement_count = reader.read_uint32()
        else:
            # This might be the count directly (older format)
            enhancement_count = flag_or_date
        
        db.enhancements = []
        
        print(f"Loading {enhancement_count} enhancements...")
        for i in range(enhancement_count):
            if i % 100 == 0:
                print(f"  Loaded {i}/{enhancement_count} enhancements...")
            try:
                db.enhancements.append(MHDEnhancement.from_reader(reader))
            except Exception as e:
                print(f"Error parsing enhancement {i}: {e}")
                import traceback
                traceback.print_exc()
                break
    
    return db


def parse_text_file(file_path: str) -> Dict[str, Any]:
    """Parse text-based MHD files like Origins.mhd or EClasses.mhd.
    
    Args:
        file_path: Path to the text MHD file
        
    Returns:
        Dictionary containing parsed data
    """
    data = {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Simple key-value parser
    current_section = None
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        if line.startswith('[') and line.endswith(']'):
            current_section = line[1:-1]
            data[current_section] = []
        elif '=' in line and current_section:
            key, value = line.split('=', 1)
            data[current_section].append({
                'key': key.strip(),
                'value': value.strip()
            })
        elif current_section:
            # Tab-delimited data
            parts = line.split('\t')
            if len(parts) > 1:
                data[current_section].append(parts)
    
    return data


if __name__ == "__main__":
    # Test parsing
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python parser.py <path_to_mhd_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        if file_path.endswith('I12.mhd'):
            db = parse_main_database(file_path)
            print(f"Parsed database version: {db.version}")
            print(f"Database date: {db.date}")
            print(f"Archetypes: {len(db.archetypes)}")
            print(f"Powersets: {len(db.powersets)}")
            
            # Show first few archetypes
            for arch in db.archetypes[:5]:
                print(f"  - {arch.display_name} ({arch.class_name})")
        
        elif file_path.endswith('EnhDB.mhd'):
            db = parse_enhancement_database(file_path)
            print(f"Parsed enhancement database version: {db.version}")
            print(f"Enhancements: {len(db.enhancements)}")
            
            # Show first few enhancements
            for enh in db.enhancements[:5]:
                print(f"  - {enh.name} ({enh.short_name})")
        
        else:
            # Try as text file
            data = parse_text_file(file_path)
            print(f"Parsed text file with sections: {list(data.keys())}")
            
    except Exception as e:
        print(f"Error parsing file: {e}")
        import traceback
        traceback.print_exc()