# MHD Text Extraction Data Loss Assessment

## Executive Summary

The Mac compatibility text extraction approach introduces **SEVERE data loss** - approximately **95% of numeric data** is lost. This is not just "possible loss of accurate characters" but rather **complete loss of critical game mechanics data**.

## Critical Data Loss Statistics

From analyzing `I12-dev-071925.mhd` (28.5 MB):

### Binary Content Found:
- **7,717,214 float values** (power attributes, modifiers)
- **3,818,644 integer values** (IDs, levels, counts)
- **1,477,023 boolean flags** (availability, features)
- **378,218 strings** (names, descriptions)

### Text Extraction Preserved:
- **385,233 strings** ✓ (good coverage)
- **5,584 numeric values** ❌ (0.07% of total)
- **2 float values** ❌ (0.00003% of floats)
- **0 structured arrays** ❌

## What Is Actually Lost

### 1. **Power Mechanics (CRITICAL)**
All numeric attributes default to placeholder values:
```json
{
  "accuracy": 1.0,        // Default, not actual
  "activation_time": 0.0, // Lost
  "recharge_time": 0.0,   // Lost
  "endurance_cost": 0.0,  // Lost
  "range": 0.0,           // Lost
  "damage_scale": ???     // Completely missing
}
```

### 2. **Power Effects (CRITICAL)**
Complex effect structures are completely lost:
- Damage values and types
- Buff/debuff magnitudes
- Duration values
- Status effect chances
- Conditional triggers

### 3. **Enhancement Values (CRITICAL)**
- Base enhancement bonuses
- Set bonus thresholds
- Enhancement categories
- Stacking rules

### 4. **Data Relationships (CRITICAL)**
- Power → Effect mappings
- Enhancement → Power compatibility
- Archetype → Powerset availability
- Level progression data

### 5. **Game Balance Data (CRITICAL)**
- Damage scales by archetype
- Modifier tables
- Level-based scaling
- PvP vs PvE values

## Real-World Impact

### Example: Psychokinetic Barrier
**Text extraction shows**: "grants a moderate amount of absorption"
**Missing from binary**:
- Actual absorption value (e.g., 187.5 HP)
- Duration (e.g., 20 seconds)
- Recharge time (e.g., 120 seconds)
- Endurance cost (e.g., 13.5)
- Debuff resistance values (e.g., 40% to each type)

### This means:
1. **Build planners cannot calculate**:
   - Actual damage output
   - Survivability metrics
   - Endurance management
   - Recharge optimization

2. **Players cannot determine**:
   - Whether a power is worth taking
   - How to slot enhancements
   - Power rotation timing
   - Comparative build effectiveness

## Why This Happened

The text extraction approach:
1. Reads strings sequentially from binary
2. Ignores binary structure markers
3. Cannot distinguish data types
4. Loses all numeric encoding
5. Destroys array/object relationships

## Severity Assessment

| Data Type | Loss % | Impact | Recovery Possible? |
|-----------|--------|--------|-------------------|
| Strings | ~0% | Low | ✓ Yes |
| Integers | 99.9% | Critical | ❌ No |
| Floats | 99.99% | Critical | ❌ No |
| Booleans | 100% | High | ❌ No |
| Arrays | 100% | Critical | ❌ No |
| Relationships | 100% | Critical | ❌ No |

## Conclusion

**The Mac compatibility text extraction is NOT suitable for production use.**

While it preserves power names and descriptions (useful for searching), it completely fails to capture the actual game mechanics data. This makes it impossible to:
- Perform accurate build calculations
- Compare power effectiveness
- Plan character builds
- Validate game balance changes

## Recommendation

**IMMEDIATE ACTION REQUIRED**: 
1. Do not rely on text-extracted data for any gameplay calculations
2. Implement proper binary MHD parsing using the MidsReborn library
3. If Mac compatibility is required, use the MidsReborn library in a cross-platform .NET Core application
4. Text extraction should only be used for search indexing, never for game data

The current approach is equivalent to extracting only the table of contents from a technical manual while discarding all the actual specifications.