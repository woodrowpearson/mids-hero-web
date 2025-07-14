# Epic 2: Data Model & Database Integration

## Current Status: 🚧 BLOCKED

**Blocker**: Need City of Heroes game data files (.mhd format) from Homecoming team.

## Overview

This epic focuses on importing City of Heroes game data into our PostgreSQL database. This is the critical foundation that all other features depend on.

## Prerequisites

- [x] Database models defined (Epic 1)
- [x] PostgreSQL running in Docker
- [ ] **City of Heroes data files** (.mhd format)
- [ ] Understanding of .mhd file format

## Tasks Breakdown

### Task 2.1: Design Database Schema ✅
- [x] Identify all data entities
- [x] Create SQLAlchemy models
- [ ] Run initial migrations

### Task 2.2: Data Import Utilities 🚧
- [ ] Investigate .mhd file format
- [ ] Create binary parser or C# export tool
- [ ] Write Python import scripts
- [ ] Validate imported data

### Task 2.3: Validation ⏳
- [ ] Cross-check entity counts
- [ ] Verify known build scenarios

### Task 2.4: Automation ⏳
- [ ] Create reusable import pipeline
- [ ] Document the process

## Technical Implementation

### File Structure
```
backend/app/data_import/
├── __init__.py
├── parser.py          # .mhd file parser
├── importer.py        # Database import logic
├── validator.py       # Data validation
└── schemas/           # Import data schemas
    ├── archetype.py
    ├── powerset.py
    ├── power.py
    └── enhancement.py
```

### Import Pipeline Design

```python
# Conceptual flow
class DataImportPipeline:
    def __init__(self, mhd_file_path: str):
        self.parser = MHDParser(mhd_file_path)
        self.validator = DataValidator()
        self.importer = DatabaseImporter()
    
    def run(self):
        # 1. Parse .mhd file
        raw_data = self.parser.parse()
        
        # 2. Validate data structure
        validated_data = self.validator.validate(raw_data)
        
        # 3. Import to database
        import_result = self.importer.import_data(validated_data)
        
        # 4. Generate report
        return ImportReport(import_result)
```

### Database Migration

```python
# First migration after data import
def upgrade():
    # Create initial schema
    op.create_table('archetypes', ...)
    op.create_table('powersets', ...)
    op.create_table('powers', ...)
    op.create_table('enhancements', ...)
    
    # Add indexes for performance
    op.create_index('idx_archetype_name', 'archetypes', ['name'])
    op.create_index('idx_power_level', 'powers', ['level_available'])
```

## Data Sources

### Option 1: Homecoming Data Files
- Contact: Homecoming development team
- Format: Binary .mhd files
- Version: 2025.7.1111 (latest)

### Option 2: Community Export
- Alternative: JSON/CSV export from existing tools
- Pros: Easier to parse
- Cons: May be incomplete or outdated

### Option 3: Manual Entry
- Last resort: Enter critical data manually
- Focus: Core archetypes and powers only
- Timeline: Would delay project significantly

## Validation Checklist

After import, verify:

1. **Archetype Count**
   - [ ] 14 primary archetypes present
   - [ ] Correct primary/secondary group assignments

2. **Powerset Integrity**
   - [ ] All archetypes have appropriate powersets
   - [ ] Pool powers available to all
   - [ ] Epic/Patron pools properly restricted

3. **Power Details**
   - [ ] Correct level availability
   - [ ] Accurate base statistics
   - [ ] Proper enhancement categories

4. **Enhancement Sets**
   - [ ] All named sets imported
   - [ ] Set bonuses match game values
   - [ ] Unique enhancements flagged

5. **Data Relationships**
   - [ ] Foreign keys properly linked
   - [ ] No orphaned records
   - [ ] Prerequisite chains intact

## Known Challenges

1. **Binary Format**: .mhd files are proprietary binary format
   - Solution: Reverse engineer or use Mids Reborn code
   
2. **Data Volume**: Thousands of powers and enhancements
   - Solution: Batch processing, progress tracking
   
3. **Version Changes**: Game updates modify data
   - Solution: Version tracking, incremental updates

4. **Accuracy Requirements**: Community expects 100% accuracy
   - Solution: Extensive validation, community testing

## Success Criteria

- [ ] All game data imported successfully
- [ ] Zero data integrity errors
- [ ] Import process documented
- [ ] Automated pipeline for updates
- [ ] Performance benchmarks met (<5 min import)

## Next Steps

1. **Immediate**: Contact Homecoming team for data files
2. **While Waiting**: 
   - Complete database migrations
   - Set up import framework
   - Create validation tests
3. **After Data Obtained**:
   - Parse and import data
   - Run validation suite
   - Begin Epic 3 (API development)

## Resources

- [Homecoming Forums](https://forums.homecomingservers.com/)
- [Mids Reborn Source](https://github.com/Crytilis/mids-reborn-hero-designer)
- [City of Heroes Wiki](https://hcwiki.cityofheroes.dev/)

## Command Reference

```bash
# Run migrations
just db-migrate

# Create import migration
just db-migration-create "import game data"

# Run import (when ready)
cd backend && uv run python -m app.data_import.importer

# Validate import
cd backend && uv run python -m app.data_import.validator
```