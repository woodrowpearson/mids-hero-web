# Archive Directory

This directory contains code that was developed but ultimately not used in the final implementation. Following the principle of "archive over delete", we preserve this code for historical reference and potential future use.

## Why Archive Instead of Delete?

1. **Historical Context**: Shows the evolution of our approach
2. **Learning Reference**: Documents what was tried and why it didn't work
3. **Potential Reuse**: Code might be useful for future features or debugging
4. **Transparency**: Demonstrates the development process and decision-making

## Archived Components

### mhd_parser/ - Python MHD Binary Parser

**Status**: Partially implemented, superseded by C# DataExporter approach

**Reason for Archiving**:
- The MHD files use a custom binary format specific to Homecoming
- After extensive reverse engineering, we discovered:
  - Custom string encoding (not standard .NET BinaryReader format)
  - Complex nested structures requiring deep knowledge of the format
  - Maintaining a Python parser would duplicate the work already done in Mids Reborn (C#)
  
**Decision**: Use the existing C# parser from Mids Reborn via a DataExporter tool

**What Was Implemented**:
- Basic binary reader infrastructure
- Archetype parsing (partial)
- Powerset parsing (partial)
- Comprehensive test suite with TDD approach
- Binary format analysis tools

**Lessons Learned**:
- Custom binary formats are challenging to reverse engineer
- Leveraging existing parsers is more maintainable than reimplementing
- Test-driven development helped identify format inconsistencies early

## DO NOT USE THIS CODE

The code in this archive is preserved for reference only. It should not be imported or used in production code. If you need MHD parsing functionality, use the C# DataExporter approach documented in `/docs/mhd-data-import-solution.md`.

## Claude Context Management

This directory is excluded from Claude's context to prevent confusion. The `.claudeignore` file ensures AI assistants don't reference archived code when working on current features.