# MHD Data Import Solution

## Overview

Based on analysis of the MidsReborn source code, here's the minimal implementation needed to parse MHD files for the Mids Hero Web project.

## MHD File Format

MHD files are binary files with a specific structure:

1. **Header**: String identifier (e.g., "Mids Reborn Powers Database")
2. **Version**: String version number
3. **Metadata**: Date, issue number, etc.
4. **Data Sections**: Each section has:
   - Section header (e.g., "BEGIN:ARCHETYPES")
   - Count of items
   - Binary data for each item

## Key MHD Files

- `I12.mhd` - Main database (Archetypes, Powersets, Powers, Entities)
- `EnhDB.mhd` - Enhancement database
- `Recipe.mhd` - Recipe database
- `Salvage.mhd` - Salvage database
- `EClasses.mhd` - Enhancement classes (text format)
- `Origins.mhd` - Origins (text format)
- `AttribMod.json` - Attribute modifiers (JSON format)
- `TypeGrades.json` - Type grades (JSON format)

## Core Data Structures

### 1. Archetype
```python
class Archetype:
    def __init__(self, reader: BinaryReader):
        self.display_name = reader.read_string()
        self.hitpoints = reader.read_int32()
        self.hp_cap = reader.read_float()
        self.desc_long = reader.read_string()
        self.res_cap = reader.read_float()
        
        origin_count = reader.read_int32()
        self.origins = []
        for i in range(origin_count + 1):
            self.origins.append(reader.read_string())
        
        self.class_name = reader.read_string()
        self.class_type = reader.read_int32()  # Enum value
        self.column = reader.read_int32()
        self.desc_short = reader.read_string()
        self.primary_group = reader.read_string()
        self.secondary_group = reader.read_string()
        self.playable = reader.read_boolean()
        self.recharge_cap = reader.read_float()
        self.damage_cap = reader.read_float()
        self.recovery_cap = reader.read_float()
        self.regen_cap = reader.read_float()
        self.base_recovery = reader.read_float()
        self.base_regen = reader.read_float()
        self.base_threat = reader.read_float()
        self.perception_cap = reader.read_float()
```

### 2. Powerset
```python
class Powerset:
    def __init__(self, reader: BinaryReader):
        self.display_name = reader.read_string()
        self.archetype_id = reader.read_int32()
        self.set_type = reader.read_int32()  # Enum value
        self.image_name = reader.read_string()
        self.full_name = reader.read_string()
        self.set_name = reader.read_string()
        self.description = reader.read_string()
        self.sub_name = reader.read_string()
        self.at_class = reader.read_string()
        self.uid_trunk_set = reader.read_string()
        self.uid_link_secondary = reader.read_string()
        
        mutex_count = reader.read_int32()
        self.uid_mutex_sets = []
        self.nid_mutex_sets = []
        for i in range(mutex_count + 1):
            self.uid_mutex_sets.append(reader.read_string())
            self.nid_mutex_sets.append(reader.read_int32())
```

### 3. Power (simplified)
```python
class Power:
    def __init__(self, reader: BinaryReader):
        self.static_index = reader.read_int32()
        self.full_name = reader.read_string()
        self.group_name = reader.read_string()
        self.set_name = reader.read_string()
        self.power_name = reader.read_string()
        self.display_name = reader.read_string()
        self.available = reader.read_int32()
        # Requirement object read here
        self.modes_required = reader.read_int32()
        self.modes_disallowed = reader.read_int32()
        self.power_type = reader.read_int32()
        self.accuracy = reader.read_float()
        self.attack_types = reader.read_int32()
        # ... many more fields
```

### 4. Enhancement
```python
class Enhancement:
    def __init__(self, reader: BinaryReader):
        self.static_index = reader.read_int32()
        self.name = reader.read_string()
        self.short_name = reader.read_string()
        self.desc = reader.read_string()
        self.type_id = reader.read_int32()
        self.sub_type_id = reader.read_int32()
        
        class_count = reader.read_int32()
        self.class_ids = []
        for i in range(class_count + 1):
            self.class_ids.append(reader.read_int32())
        
        self.image = reader.read_string()
        self.set_id = reader.read_int32()
        self.uid_set = reader.read_string()
        self.effect_chance = reader.read_float()
        self.level_min = reader.read_int32()
        self.level_max = reader.read_int32()
        self.unique = reader.read_boolean()
        # ... more fields
```

## Python Implementation

### BinaryReader Helper Class
```python
import struct
from io import BytesIO

class BinaryReader:
    def __init__(self, stream):
        self.stream = stream
    
    def read_int32(self):
        return struct.unpack('<i', self.stream.read(4))[0]
    
    def read_float(self):
        return struct.unpack('<f', self.stream.read(4))[0]
    
    def read_boolean(self):
        return struct.unpack('?', self.stream.read(1))[0]
    
    def read_string(self):
        # .NET BinaryWriter encodes strings with a 7-bit encoded length prefix
        length = self._read_7bit_encoded_int()
        if length == 0:
            return ""
        return self.stream.read(length).decode('utf-8')
    
    def _read_7bit_encoded_int(self):
        count = 0
        shift = 0
        byte = 0x80
        while (byte & 0x80) != 0:
            byte = ord(self.stream.read(1))
            count |= (byte & 0x7F) << shift
            shift += 7
        return count
```

### Main Database Loader
```python
def load_main_database(file_path):
    with open(file_path, 'rb') as f:
        reader = BinaryReader(f)
        
        # Read header
        header = reader.read_string()
        if header != "Mids Reborn Powers Database":
            raise ValueError("Invalid database header")
        
        # Read version
        version = reader.read_string()
        
        # Read date info
        year = reader.read_int32()
        if year > 0:
            month = reader.read_int32()
            day = reader.read_int32()
            date = datetime(year, month, day)
        else:
            date_binary = reader.read_int64()
            # Convert from .NET binary date format
        
        issue = reader.read_int32()
        page_vol = reader.read_int32()
        page_vol_text = reader.read_string()
        
        # Read Archetypes
        if reader.read_string() != "BEGIN:ARCHETYPES":
            raise ValueError("Expected Archetype section")
        
        archetype_count = reader.read_int32() + 1
        archetypes = []
        for i in range(archetype_count):
            archetypes.append(Archetype(reader))
        
        # Read Powersets
        if reader.read_string() != "BEGIN:POWERSETS":
            raise ValueError("Expected Powerset section")
        
        powerset_count = reader.read_int32() + 1
        powersets = []
        for i in range(powerset_count):
            powersets.append(Powerset(reader))
        
        # Read Powers
        if reader.read_string() != "BEGIN:POWERS":
            raise ValueError("Expected Power section")
        
        power_count = reader.read_int32() + 1
        powers = []
        for i in range(power_count):
            powers.append(Power(reader))
        
        # Read Summons/Entities
        if reader.read_string() != "BEGIN:SUMMONS":
            raise ValueError("Expected Summon section")
        
        # ... load entities
        
        return {
            'version': version,
            'date': date,
            'issue': issue,
            'archetypes': archetypes,
            'powersets': powersets,
            'powers': powers
        }
```

## Integration with Epic 2

### 1. Create Python Parser Module
Create `backend/app/mhd_parser/` with:
- `binary_reader.py` - BinaryReader implementation
- `models.py` - Python dataclasses for Archetype, Powerset, Power, etc.
- `parser.py` - Main parsing logic
- `importer.py` - SQLAlchemy import logic

### 2. Import Script
```python
# backend/scripts/import_mhd_data.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.mhd_parser import parse_main_database
from app.db.session import SessionLocal
from app.db.models import Archetype, Powerset, Power

def import_data(mhd_path):
    # Parse MHD file
    data = parse_main_database(mhd_path)
    
    # Import to database
    db = SessionLocal()
    try:
        # Import archetypes
        for arch_data in data['archetypes']:
            arch = Archetype(
                name=arch_data.display_name,
                class_name=arch_data.class_name,
                # ... map fields
            )
            db.add(arch)
        
        # Import powersets
        # Import powers
        
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    import_data("data/Homecoming/I12.mhd")
```

### 3. Next Steps

1. **Implement the parser module** with the structures above
2. **Test with sample MHD files** from the Homecoming data
3. **Map to SQLAlchemy models** already created in Epic 2
4. **Handle relationships** between archetypes, powersets, and powers
5. **Import enhancement data** from EnhDB.mhd
6. **Import recipes and salvage** from their respective files

## Notes

- The MHD format uses .NET's BinaryWriter format with 7-bit encoded string lengths
- All integer counts in the file format use +1 (e.g., count of 10 means 11 items)
- String encoding is UTF-8
- The format is little-endian
- Some files like EClasses.mhd and Origins.mhd are text-based, not binary
- AttribMod.json and TypeGrades.json are already in JSON format

## Implementation Status

### Completed
- ✅ Created `backend/app/mhd_parser/` module
- ✅ Implemented BinaryReader for .NET format
- ✅ Created data models for Archetype, Powerset, Power, Enhancement
- ✅ Basic parser for I12.mhd (Archetypes and Powersets working)
- ✅ Test script successfully reads Homecoming data

### Test Results
Successfully parsed Homecoming_2025.7.1111 data:
- Database Version: 2025.7.1111
- Issue: 28
- Archetypes: 61 (all playable archetypes loaded correctly)
- Powersets: 3665 (all powersets loaded)
- Powers: Not yet implemented (complex structure)

### Next Steps
1. Complete Power parsing (complex due to effects and requirements)
2. Implement Enhancement database parser
3. Create import script to load data into SQLAlchemy models
4. Handle cross-references between archetypes, powersets, and powers
5. Import recipe and salvage data