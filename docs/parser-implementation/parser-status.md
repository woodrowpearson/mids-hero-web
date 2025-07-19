# Parser Implementation Status

## Overview

The Mids Hero Web project uses the DataExporter with MidsReborn's DatabaseAPI for all MHD file parsing. This document provides a comprehensive overview of the parser implementation, including visual diagrams and current status.

## Architecture Overview

```mermaid
graph TB
    subgraph "Data Sources"
        MHD[MHD Files<br/>Binary Format]
        MR[MidsReborn<br/>Application]
    end
    
    subgraph "DataExporter Layer"
        DE[DataExporter<br/>C#/.NET]
        MRAPI[MidsReborn<br/>DatabaseAPI]
        JP[JSON<br/>Processor]
    end
    
    subgraph "Output"
        JSON[JSON Files]
    end
    
    subgraph "Backend Layer"
        IMP[Import Scripts<br/>Python]
        DB[(PostgreSQL<br/>Database)]
    end
    
    MHD --> MR
    MR --> MRAPI
    MRAPI --> DE
    DE --> JP
    JP --> JSON
    JSON --> IMP
    IMP --> DB
    
    classDef source fill:#e1f5fe
    classDef exporter fill:#fff3e0
    classDef output fill:#f3e5f5
    classDef backend fill:#e8f5e9
    
    class MHD,MR source
    class DE,MRAPI,JP exporter
    class JSON output
    class IMP,DB backend
```

## Data Flow Process

```mermaid
sequenceDiagram
    participant User
    participant DataExporter
    participant MidsRebornAPI
    participant FileSystem
    participant ImportScripts
    participant Database
    
    User->>DataExporter: Execute export command
    DataExporter->>MidsRebornAPI: Initialize configuration
    DataExporter->>MidsRebornAPI: Load MHD files
    
    loop For each data type
        MidsRebornAPI->>MidsRebornAPI: Parse binary data
        MidsRebornAPI-->>DataExporter: Return parsed objects
        DataExporter->>DataExporter: Convert to JSON
        DataExporter->>FileSystem: Write JSON file
    end
    
    User->>ImportScripts: Execute import command
    ImportScripts->>FileSystem: Read JSON files
    ImportScripts->>ImportScripts: Validate data
    ImportScripts->>Database: Insert records
    ImportScripts-->>User: Report success/errors
```

## Implementation Status by Data Type

| Data Type | Status | MHD File | JSON Output | Records | Implementation Details |
|-----------|--------|----------|-------------|---------|------------------------|
| Archetypes | ✅ Complete | I12.mhd | archetypes.json | 13 | `DatabaseAPI.LoadMainDatabase()` |
| Powersets | ✅ Complete | I12.mhd | powersets.json | 182 | `DatabaseAPI.LoadMainDatabase()` |
| Powers | ✅ Complete | I12.mhd | powers.json | 12,214 | `DatabaseAPI.LoadMainDatabase()` |
| I12 Powers | ✅ Complete | I12.mhd | I12_extracted.txt | 360,659 | Specialized streaming parser |
| Enhancements | ✅ Complete | EnhDB.mhd | enhancements.json | 10,186 | `DatabaseAPI.LoadEnhancementDb()` |
| Enhancement Sets | ✅ Complete | EnhDB.mhd | enhancement_sets.json | 424 | `DatabaseAPI.LoadEnhancementDb()` |
| Recipes | ✅ Complete | Recipe.mhd | recipes.json | 82,299 | `DatabaseAPI.LoadRecipes()` |
| Salvage | ✅ Complete | Salvage.mhd | salvage.json | 222 | `DatabaseAPI.LoadSalvage()` |

## Parser Implementation Details

### DataExporter Components

```mermaid
graph LR
    subgraph "DataExporter Project"
        Program[Program.cs<br/>Entry Point]
        MRE[MidsRebornExporter.cs<br/>Main Logic]
        DL[DirectDataLoader.cs<br/>Direct Loading]
        JAE[JsonArchiveExtractor.cs<br/>Archive Handler]
        MHP[MhdParser.cs<br/>Basic Parser]
        TJP[TextToJsonParser.cs<br/>Text Processing]
    end
    
    Program --> MRE
    Program --> DL
    MRE --> JAE
    Program --> MHP
    Program --> TJP
    
    style Program fill:#ffeb3b
    style MRE fill:#4caf50
    style DL fill:#2196f3
```

### Key Components

1. **MidsRebornExporter.cs**
   - Primary export logic using MidsReborn's DatabaseAPI
   - Handles initialization and data loading sequence
   - Exports to JSON format

2. **DirectDataLoader.cs**
   - Alternative direct loading approach
   - Used for testing and validation

3. **JsonArchiveExtractor.cs**
   - Handles extraction of archived JSON data
   - Processes MidsReborn's native export format

4. **TextToJsonParser.cs**
   - Converts text-based data to structured JSON
   - Handles I12 power data extraction

## Loading Sequence

```mermaid
graph TD
    Start([Start Export])
    Init[Initialize Configuration]
    Server[Load Server Data]
    Attrib[Load Attribute Modifiers]
    Types[Load Type Grades]
    Levels[Load Level Tables]
    Main[Load Main Database<br/>I12.mhd]
    Math[Load Math Tables]
    Effects[Load Effect IDs]
    EnhClass[Load Enhancement Classes]
    EnhDB[Load Enhancement Database]
    Origins[Load Origins]
    Salvage[Load Salvage]
    Recipes[Load Recipes]
    Post[Post-Loading Setup]
    Export[Export to JSON]
    End([Complete])
    
    Start --> Init
    Init --> Server
    Server --> Attrib
    Attrib --> Types
    Types --> Levels
    Levels --> Main
    Main --> Math
    Math --> Effects
    Effects --> EnhClass
    EnhClass --> EnhDB
    EnhDB --> Origins
    Origins --> Salvage
    Salvage --> Recipes
    Recipes --> Post
    Post --> Export
    Export --> End
    
    style Start fill:#4caf50
    style End fill:#4caf50
    style Main fill:#ff9800
    style Export fill:#2196f3
```

## Technical Implementation Notes

### MidsReborn Integration
- Uses official MidsReborn DLLs for parsing
- Requires MidsReborn 3.7.14 or compatible version
- Handles all binary format complexities internally

### Error Handling
- Graceful fallback for missing files
- Detailed error reporting during parsing
- Validation at each loading step

### Performance Considerations
- Streaming parser for large I12 dataset (360K+ records)
- Memory-efficient processing
- Batch operations for database imports

## Future Considerations

1. **Version Compatibility**
   - Monitor MidsReborn updates for API changes
   - Maintain compatibility matrix

2. **Data Validation**
   - Implement checksums for data integrity
   - Version tracking for incremental updates

3. **Performance Optimization**
   - Parallel processing for independent data types
   - Caching for frequently accessed data

## References

- [DataExporter Implementation](../../DataExporter/MidsRebornExporter.cs)
- [Import Scripts](../../backend/app/data_import/)
- [Database Schema](../../backend/app/models.py)