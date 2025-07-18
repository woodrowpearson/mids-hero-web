# Python MHD Parser Implementation Plan

## Executive Summary

The Python MHD parser is **65% complete** and can be finished with **8-12 hours** of focused work. The core infrastructure works, and most complexity is already handled.

## Current Status

### ✅ Complete (Working)
1. **Binary Reader** - Handles .NET format correctly
2. **Archetypes** - 61 successfully parsed and exported
3. **Powersets** - 3,665 successfully parsed (export limited by constraints)
4. **Database Schema** - All tables and relationships defined

### 🔧 Needs Minor Fix
1. **Powers** - Parser works but export not implemented (1-2 hours)
   - Issue: Loop has `pass` statement instead of `MHDPower.from_reader(reader)`
   - Fix: Simply uncomment/add the line
   
2. **Powerset Constraints** - Only 380/3,665 import (1 hour)
   - Issue: Foreign key constraints during import
   - Fix: Handle orphaned powersets or adjust constraints

### ❌ Needs Implementation
1. **Enhancements** - Non-standard file format (4-6 hours)
   - Issue: EnhDB.mhd doesn't use standard .NET BinaryWriter format
   - Found: 631+ enhancements in file (not just 5)
   - Solution: Custom parser for this specific format

2. **Recipes** - Not implemented (2-3 hours)
   - Need to reverse-engineer format
   - Create parser

3. **Salvage** - Not implemented (2-3 hours)  
   - Need to reverse-engineer format
   - Create parser

## Implementation Steps

### Step 1: Fix Power Export (1-2 hours)
```python
# In parser.py, replace:
try:
    pass
except Exception as e:
    print(f"Error parsing power {i}: {e}")

# With:
try:
    db.powers.append(MHDPower.from_reader(reader))
except Exception as e:
    print(f"Error parsing power {i}: {e}")
```

Then update export_mhd_to_json.py to use the export_powers_complete function.

### Step 2: Fix Enhancement Parser (4-6 hours)
The EnhDB.mhd file has a custom format:
- File size: 453KB
- Contains 631+ enhancements (not 5)
- Uses mixed null-terminated and Pascal strings
- Non-standard structure

Approach:
1. Use enhancement_raw_parser.py as starting point
2. Reverse-engineer the full structure
3. Parse all enhancement fields
4. Handle enhancement sets

### Step 3: Recipe Parser (2-3 hours)
1. Analyze Recipe.mhd format
2. Create MHDRecipe model
3. Implement parser
4. Map to database schema

### Step 4: Salvage Parser (2-3 hours)
1. Analyze Salvage.mhd format
2. Create MHDSalvage model
3. Implement parser
4. Map to database schema

### Step 5: Fix Import Constraints (1 hour)
1. Analyze why only 380 powersets import
2. Either:
   - Add missing archetype references
   - Make archetype_id nullable
   - Handle orphaned powersets separately

## Quick Wins

For immediate progress (2-3 hours total):

1. **Fix power export** - Get 10,942 powers into the database
2. **Fix powerset constraints** - Get all 3,665 powersets importing
3. **Run full import** - Have working archetypes, powersets, and powers

This would give us ~80% of the data needed for a functional application.

## Risk Assessment

### Low Risk
- Power export (code already works)
- Powerset constraints (simple schema adjustment)
- Recipe/Salvage parsers (similar to existing parsers)

### Medium Risk  
- Enhancement parser (non-standard format, but data is readable)

### Mitigations
- Enhancement data less critical for MVP
- Can defer recipes/salvage for later release
- Core functionality works without them

## Recommendation

**Proceed with Python parser:**

1. **Today**: Fix power export and powerset constraints (2-3 hours)
2. **Tomorrow**: Enhancement parser (4-6 hours)
3. **Later**: Recipe and salvage parsers (4-6 hours)

This gives us a working system quickly while maintaining cross-platform compatibility.