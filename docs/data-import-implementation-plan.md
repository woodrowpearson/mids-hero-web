# Data Import Implementation Plan

## Current Status

We have successfully implemented a basic data import pipeline using a Python MHD parser:
- ✅ Archetypes: 61 imported
- ✅ Powersets: 380 imported (partial due to constraints)
- ❌ Powers: Not imported (parser incomplete)
- ❌ Enhancements: Failed (format issue)
- ❌ Recipes: Not attempted
- ❌ Salvage: Not attempted

## Decision Point

### Option 1: Continue with Python Parser (Current Approach)
**Pros:**
- Already partially working
- Cross-platform compatible
- No Windows dependencies
- We understand the code

**Cons:**
- Complex binary format reverse engineering required
- Incomplete - needs significant work
- May have accuracy issues

### Option 2: Use MidsReborn C# Parser
**Pros:**
- Complete and proven parser
- Handles all edge cases
- Maintained by community

**Cons:**
- Windows-specific (uses WinForms)
- Requires .NET Framework
- Complex integration

### Option 3: Hybrid Approach (Recommended)
Use the working Python parser for what it can do, and create focused parsers for missing pieces:

1. **Keep using Python parser for:**
   - Archetypes ✅
   - Powersets ✅
   
2. **Fix Python parser for:**
   - Enhancements (we identified the issue)
   - Powers (implement remaining fields)
   
3. **Create simple parsers for:**
   - Recipes (likely simpler format)
   - Salvage (likely simpler format)

## Implementation Steps

### Phase 1: Fix Enhancement Parser (1 day)
- [x] Identified issue: 0x40000000 is a flag, not count
- [ ] Update parser to skip flag bytes
- [ ] Test with real EnhDB.mhd
- [ ] Import all enhancements

### Phase 2: Complete Power Parser (2-3 days)
- [ ] Analyze power structure in archived parser
- [ ] Implement effect parsing
- [ ] Handle requirements/prerequisites
- [ ] Test with known powers
- [ ] Import all 10,942 powers

### Phase 3: Implement Recipe Parser (1 day)
- [ ] Analyze Recipe.mhd format
- [ ] Create recipe model
- [ ] Parse salvage requirements
- [ ] Import recipes

### Phase 4: Implement Salvage Parser (1 day)
- [ ] Analyze Salvage.mhd format
- [ ] Create salvage model
- [ ] Import salvage items

### Phase 5: Fix Powerset Constraints (1 day)
- [ ] Analyze why only 380/3665 import
- [ ] Update schema or import logic
- [ ] Import all powersets

## Alternative: Quick Win with Existing Data

If we need data quickly, we could:
1. Use the partially imported data (archetypes + some powersets)
2. Create mock data for powers/enhancements for development
3. Continue parser work in parallel

## Recommendation

Given that:
- Python parser is already 60% working
- We've identified the enhancement issue
- Cross-platform is important
- We need to move forward

**Continue with the Python parser approach**, fixing the identified issues rather than switching to C# which would require significant rework and platform constraints.

## Next Actions

1. Fix enhancement parser (skip 0x40000000 flag)
2. Run full import with fixed parser
3. Assess what's still missing
4. Implement remaining parsers with TDD
5. Complete full data import

This approach gets us to a working state fastest while maintaining cross-platform compatibility.