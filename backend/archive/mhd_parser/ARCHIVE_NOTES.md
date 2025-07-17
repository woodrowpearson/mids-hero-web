# MHD Parser Archive Notes

## Overview

This Python implementation of an MHD binary parser was developed as part of Epic 2 Task 2.5. It was ultimately archived in favor of using the existing C# parser from Mids Reborn.

## What Was Built

### Core Components

1. **Binary Reader** (`binary_reader.py`)
   - Custom binary reading utilities
   - Attempted to handle .NET BinaryReader format
   - Discovered Homecoming uses custom encoding

2. **Parser Modules**
   - `archetype_parser.py` - Partially working archetype parsing
   - `powerset_parser.py` - Basic powerset structure parsing  
   - `power_parser.py` - Complex power data parsing (incomplete)
   - `enhancement_parser.py` - Enhancement database parsing (incomplete)

3. **Comprehensive Test Suite**
   - TDD approach with 100% initial coverage
   - Tests revealed format inconsistencies
   - Helped identify custom encoding issues

### Technical Discoveries

1. **Custom String Encoding**
   ```python
   # Expected .NET format:
   # - 7-bit encoded length
   # - UTF-8 string data
   
   # Actual Homecoming format:
   # - Single byte length
   # - Custom encoded string
   ```

2. **File Structure**
   ```
   MHD File:
   ├── Header (custom format)
   ├── Archetype Records
   ├── Powerset Records (with references)
   └── Power Records (complex nested data)
   ```

3. **Binary Format Analysis**
   - Created hex dump analysis tools
   - Identified record boundaries
   - Mapped basic structure

## Why It Was Archived

### Technical Reasons

1. **Format Complexity**
   - Homecoming's custom binary format differs from standard .NET
   - Would require extensive reverse engineering
   - No official documentation available

2. **Maintenance Burden**
   - Parallel implementation to Mids Reborn
   - Format changes would require updates in two places
   - Risk of parsing inconsistencies

3. **Existing Solution**
   - Mids Reborn already has working C# parser
   - Community maintained and tested
   - Handles all edge cases

### Strategic Decision

After implementing ~40% of the parser and discovering the format complexities, we decided to:

1. Use Mids Reborn's parser via C# DataExporter
2. Export to JSON/SQL for import
3. Archive this implementation for reference

## Lessons Learned

1. **Binary Format Reverse Engineering**
   - Start with hex analysis before coding
   - Test assumptions early with real data
   - Consider existing implementations

2. **TDD Benefits**
   - Tests caught encoding issues early
   - Provided clear failure points
   - Documented expected behavior

3. **Build vs Buy (or Reuse)**
   - Evaluated effort vs benefit
   - Chose pragmatic solution
   - Preserved work for reference

## Code Quality

Despite being archived, this code demonstrates:
- Clean architecture with separated concerns
- Comprehensive test coverage
- Good documentation practices
- Proper error handling

## DO NOT USE IN PRODUCTION

This code is archived and should not be used. Use the C# DataExporter approach instead.

See `/docs/mhd-data-import-solution.md` for the current solution.