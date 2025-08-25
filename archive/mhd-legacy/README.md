# MHD Legacy Code Archive

## Archive Date: 2025-08-24

## Purpose
This archive contains legacy MHD (Mids Hero Designer) binary parsing code that has been deprecated as part of Epic 2.5.5 cleanup. The project has transitioned to a JSON-based data import pipeline.

## Archive Contents

### 1. `/parser/`
Contains the Python MHD binary parser implementation that was originally located at `/backend/app/mhd_parser/`. This includes:
- Binary reading utilities
- Archetype, power, enhancement, powerset, salvage, and recipe parsers
- I12 database parser
- CLI interface
- Full test suite (27 test files)

**Reason for Archival**: Complex binary format maintenance burden, replaced with JSON import.

### 2. `/dataexporter/`
Contains the C# DataExporter project for converting MHD binary files to JSON.
- **Note**: This is kept for reference but the active version remains in `/DataExporter/` for MHD→JSON conversion

### 3. `/documentation/`
Contains outdated documentation related to MHD binary parsing:
- Parser implementation guides
- Binary format specifications
- Integration documentation

### 4. `/examples/`
Sample MHD files and parsing examples for reference.

## Migration Path

The new data pipeline:
```
MHD Binary Files → C# DataExporter → JSON Files → I12StreamingParser → Database
```

### To Import Data (New Method)

1. **Convert MHD to JSON** (if needed):
   ```bash
   cd DataExporter
   dotnet run -- /path/to/mhd/file.mhd
   ```

2. **Import JSON to Database**:
   ```bash
   python backend/scripts/import_i12_data.py /path/to/json/file.json
   # OR
   just i12-import /path/to/json/file.json
   ```

## Deprecated Commands

The following commands are no longer functional:
- `python -m app.commands.import_mhd` - Returns deprecation notice
- Any direct MHD binary parsing operations

## Related Issues

- Epic 2.5.5: Project Cleanup & JSON Migration Preparation (#256)
- Task 2.5.5.2: Refactor MHD Dependencies (#263)
- Epic 2.6: JSON Data Source Migration (#253)

## Notes

- Most Python MHD parser code was already archived to `/backend/archive/mhd_parser/` on 2025-07-19
- The C# DataExporter remains active for MHD→JSON conversion
- The I12StreamingParser remains active for JSON import
- Database models and schemas are generic and don't require changes

## Contact

For questions about this archive or the migration, refer to the project documentation or Epic 2.5.5 issues.