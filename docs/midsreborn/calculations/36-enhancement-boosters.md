# Enhancement Boosters

## Overview
- **Purpose**: Track and apply enhancement booster consumables that increase IO enhancement effective levels by +5 per booster
- **Used By**: Enhancement value calculation, slotting system, build tracking, salvage counting
- **Complexity**: Low
- **Priority**: Low
- **Status**: 🟡 Breadth Complete

## MidsReborn Implementation

### Primary Location
- **File**: `Core/I9Slot.cs`
- **Property**: `RelativeLevel` (enum) - Lines 15, 21, 34, 74-86
- **Method**: `GetScheduleMult()` - Lines 67-137 (applies booster multiplier)
- **Method**: `GetRelativeLevelMultiplier()` - Lines 139-154 (converts boosters to multiplier)

### Related Files
- **File**: `BuildImportTools.cs`
  - **Line 199**: Converts booster count to RelativeLevel: `RelativeLevel = (Enums.eEnhRelative)(p.Slots[i].Boosters + 4)`
  - **Line 206**: Same conversion for IO/SetO types
  - **Line 648**: Extracts booster count from level: `e.Boosters = Math.Max(0, e.Level - 50)`
  - **Line 654**: Clamps boosters to max 5: `e.Boosters = Math.Min(e.Boosters, 5)`

- **File**: `clsBuildSalvageSummary.cs`
  - **Method**: `CalcEnhBoosters()` - Lines 124-147 (counts total boosters needed)
  - **Logic**: Maps RelativeLevel (+1 through +5) to booster count (1-5)

- **File**: `Forms/Controls/EnhCheckMode.cs`
  - **Property**: `Boosters` - Lines 29-39 (UI display of booster count)
  - **Property**: `BoostersColor` - Lines 35-38 (color coding for boosters)

- **File**: `Forms/frmRecipeViewer.cs`
  - **Method**: `GetNumBoosters()` - Lines 120-131 (extracts booster count from slot)
  - **Lines 402-432**: Uses booster count in recipe display

### Data Structures

```csharp
// Core/I9Slot.cs
public class I9Slot
{
    public int Enh;                          // Enhancement index
    public Enums.eEnhGrade Grade;            // TO/DO/SO grade
    public int IOLevel;                      // Base IO level (0-52)
    public Enums.eEnhRelative RelativeLevel; // Encodes booster level
    public bool Obtained;                    // Tracking flag

    // RelativeLevel enum values used for boosters:
    // Even = 4     (0 boosters, default)
    // PlusOne = 5  (1 booster, +5 levels)
    // PlusTwo = 6  (2 boosters, +10 levels)
    // PlusThree = 7 (3 boosters, +15 levels)
    // PlusFour = 8  (4 boosters, +20 levels)
    // PlusFive = 9  (5 boosters, +25 levels)
}

// Enums.cs
public enum eEnhRelative
{
    None = 0,
    MinusThree = 1,  // -3 levels (SO/HO)
    MinusTwo = 2,    // -2 levels
    MinusOne = 3,    // -1 level
    Even = 4,        // 0 boosters (base level)
    PlusOne = 5,     // 1 booster (+5 levels)
    PlusTwo = 6,     // 2 boosters (+10 levels)
    PlusThree = 7,   // 3 boosters (+15 levels)
    PlusFour = 8,    // 4 boosters (+20 levels)
    PlusFive = 9     // 5 boosters (+25 levels, max)
}
```

### Booster Count Extraction

```csharp
// clsBuildSalvageSummary.cs - Lines 136-144
var relativeLevel = p.Slots[j].Enhancement.RelativeLevel;
EnhBoosters += relativeLevel switch
{
    Enums.eEnhRelative.PlusOne => 1,
    Enums.eEnhRelative.PlusTwo => 2,
    Enums.eEnhRelative.PlusThree => 3,
    Enums.eEnhRelative.PlusFour => 4,
    Enums.eEnhRelative.PlusFive => 5,
    _ => 0
};
```

### Booster Application

```csharp
// I9Slot.cs - Lines 130-136
var scheduleMult = GetScheduleMult(enhancement.TypeID, sEffect.Schedule);
var num2 = num1 * GetRelativeLevelMultiplier();

// GetRelativeLevelMultiplier() - Lines 139-154
private float GetRelativeLevelMultiplier()
{
    if (RelativeLevel == Enums.eEnhRelative.None)
        return 0.0f;

    var num2 = (int)(RelativeLevel - 4);  // Convert to offset from Even
    // num2 = 0 for Even, 1 for PlusOne, 2 for PlusTwo, etc.

    // Positive offset: +5% per booster
    // Negative offset: -10% per level below (for SO/HO)
    return num2 >= 0
        ? (float)(num2 * 0.05 + 1.0)      // 1.0, 1.05, 1.10, 1.15, 1.20, 1.25
        : (float)(1.0 + num2 * 0.10);     // 0.9, 0.8, 0.7 for minus levels
}
```

## High-Level Algorithm

```
Enhancement Booster System:

1. Storage Representation:
   Boosters are stored as RelativeLevel enum values:
   - Even (4) = 0 boosters
   - PlusOne (5) = 1 booster
   - PlusTwo (6) = 2 boosters
   - PlusThree (7) = 3 boosters
   - PlusFour (8) = 4 boosters
   - PlusFive (9) = 5 boosters (maximum)

2. Booster Count Extraction:
   boosterCount = switch (RelativeLevel):
     case PlusOne:   return 1
     case PlusTwo:   return 2
     case PlusThree: return 3
     case PlusFour:  return 4
     case PlusFive:  return 5
     default:        return 0

3. Enhancement Value Multiplier Calculation:
   offset = (int)RelativeLevel - 4  # 4 = Even

   IF offset >= 0:
     # Boosters add 5% per booster
     multiplier = 1.0 + (offset × 0.05)
     # Results: 1.0, 1.05, 1.10, 1.15, 1.20, 1.25
   ELSE:
     # Negative levels (SO/HO below player level)
     multiplier = 1.0 + (offset × 0.10)
     # Results: 0.9, 0.8, 0.7

4. Apply to Enhancement Schedule Value:
   baseValue = GetScheduleValue(schedule, IOLevel)
   boostedValue = baseValue × GetRelativeLevelMultiplier()

   IF enhancement.Superior:
     boostedValue *= 1.25  # Superior set bonus

5. Restrictions:
   - Only InventO and SetO types can use boosters
   - Normal/SpecialO types cannot be boosted (use relative level for SO grading)
   - Attuned IOs cannot be boosted (level-scaling already)
   - Maximum 5 boosters per enhancement (RelativeLevel capped at PlusFive)

6. Import/Export:
   When importing from game data:
     IF level > 50 AND type is IO/SetO:
       boosters = Min(level - 50, 5)
       ioLevel = 50
       RelativeLevel = (eEnhRelative)(boosters + 4)

7. Salvage Counting:
   Total boosters needed = SUM(all IO enhancements):
     Map RelativeLevel to booster count (0-5)
```

## Game Mechanics Context

### Enhancement Booster Overview

**Enhancement Boosters** are consumable items in City of Heroes that permanently increase the effective level of Invention Origin (IO) enhancements. They were introduced to allow players to improve the power of their level 50 IOs beyond the normal maximum.

**Key Properties**:
- **Consumable**: Each booster is used once and consumed
- **Permanent**: Boost remains on the enhancement forever
- **Stackable**: Can apply up to 5 boosters to a single IO
- **IO Only**: Only works on Invention Origin and Set IOs
- **Non-Attuned**: Cannot boost attuned/scalable IOs

### How Boosters Work

**Application**:
1. Right-click on an IO enhancement in inventory
2. Select "Boost" option
3. Booster is consumed, enhancement gains +1 boost level
4. Enhancement shows "+1", "+2", "+3", "+4", or "+5" indicator
5. Each boost increases effective level by +5 (level 50 → 50+5 = 53 equivalent)

**Effect on Enhancement Values**:
- **0 boosters** (base level 50): 1.00x multiplier (100% of schedule value)
- **1 booster** (+5 levels): 1.05x multiplier (105% of schedule value)
- **2 boosters** (+10 levels): 1.10x multiplier (110% of schedule value)
- **3 boosters** (+15 levels): 1.15x multiplier (115% of schedule value)
- **4 boosters** (+20 levels): 1.20x multiplier (120% of schedule value)
- **5 boosters** (+25 levels): 1.25x multiplier (125% of schedule value, maximum)

**Example**:
```
Level 50 Damage IO (unboosted):
- Base enhancement value: 42.4% (Schedule A, level 50)

Level 50+5 Damage IO (5 boosters):
- Boosted value: 42.4% × 1.25 = 53.0%
- Effective level: 53 (capped, not actually level 55)
```

### Restrictions and Limitations

**Cannot Boost**:
1. **Training/Dual/Single Origin** enhancements (TO/DO/SO)
   - These use relative level for +/- grading instead
   - RelativeLevel represents character level offset

2. **Hamidon/Synthetic Hamidon Origin** (HO/SHO)
   - Special enhancements, not boostable
   - RelativeLevel used for level offset grading

3. **Attuned IOs** (level-scaling)
   - Already scale to character level
   - Enhancement.IsScalable = true
   - Provide full value at any level

4. **Boosted IOs above level 50**
   - Can only boost level 50 IOs in practice
   - Some lower-level IOs can be boosted but rarely done
   - Game mechanics limit boosting to max-level IOs

**Maximum Boost**:
- **5 boosters** maximum per enhancement
- **+25 effective levels** total
- **Level 53 equivalent** for level 50 IOs (50 + 5 boosters × 5 levels = 75, capped to 53)
- Cannot apply more boosters once at +5

### Historical Context

**Introduction** (Issue 24: Resurgence, 2012):
- Added to provide progression path at level 50
- Allowed players to improve builds without new content
- Became major influence/enhancement converter sink

**Homecoming Era**:
- Boosters remain valuable for min-maxing builds
- Often used on expensive purple/ATO sets
- Build guides specify "+5 all IOs" for maximum performance
- Recipe viewer shows booster count in build planning

**Economic Impact**:
- High-end builds require hundreds of boosters
- Boosters purchased with Empyrean Merits or influence
- Significant cost: ~100 merits for 10 boosters
- Added long-term goal for endgame characters

### MidsReborn Tracking

**UI Display**:
- Enhancement checker mode shows total boosters needed
- Recipe viewer displays booster count per enhancement
- Build summary counts total boosters required
- Color coding indicates boosted enhancements

**Build Import**:
- Game export includes booster level in enhancement data
- Format: `Enhancement: internal_name, level, (dummy), boosters`
- Level > 50 converted to boosters: `boosters = level - 50`
- Clamped to 0-5 range on import

**Salvage Summary**:
- Tracks total boosters across entire build
- Only counts IO/SetO type enhancements
- Maps RelativeLevel to booster count (0-5)
- Used for build cost estimation

### Booster vs Relative Level Dual Use

**Critical Design Note**: `RelativeLevel` serves dual purposes in MidsReborn:

**For SO/HO Enhancements**:
- Represents level offset from character level
- MinusThree = enhancement 3 levels below character
- Even = enhancement at character level
- PlusThree = enhancement 3 levels above character
- Affects enhancement strength (±10% per level)

**For IO Enhancements**:
- Represents number of boosters applied
- Even = 0 boosters
- PlusOne = 1 booster (+5% strength)
- PlusTwo = 2 boosters (+10% strength)
- PlusFive = 5 boosters (+25% strength, max)

**Multiplier Calculation Handles Both**:
```csharp
// Positive offset: +5% per booster (IOs)
// Negative offset: -10% per level below (SOs)
var num2 = (int)(RelativeLevel - 4);
return num2 >= 0
    ? (float)(num2 * 0.05 + 1.0)      // IOs: 1.0, 1.05, 1.10, 1.15, 1.20, 1.25
    : (float)(1.0 + num2 * 0.10);     // SOs: 0.9, 0.8, 0.7
```

This dual-use design explains why the booster count calculation uses `RelativeLevel - 4`:
- Offset of 0 (Even) = 0 boosters
- Offset of 1 (PlusOne) = 1 booster
- Offset of 5 (PlusFive) = 5 boosters

### Common Build Patterns

**Budget Build**:
- No boosters (level 50 IOs)
- Acceptable performance
- Save influence for other upgrades

**Mid-Range Build**:
- Boost critical enhancements (defense/recharge)
- Leave less important IOs unboosted
- Partial optimization

**Min-Max Build**:
- +5 boosters on ALL IOs
- Maximum possible performance
- Hundreds of boosters required
- Expensive but optimal

## Python Implementation Guide

### Proposed Architecture

**Module**: `backend/app/calculations/enhancement_boosters.py`

```python
from dataclasses import dataclass
from enum import IntEnum
from typing import Optional

class RelativeLevel(IntEnum):
    """Enhancement relative level - dual use for SO grading and IO boosters"""
    NONE = 0
    MINUS_THREE = 1  # -3 levels (SO/HO only)
    MINUS_TWO = 2    # -2 levels (SO/HO only)
    MINUS_ONE = 3    # -1 level (SO/HO only)
    EVEN = 4         # 0 boosters / at level
    PLUS_ONE = 5     # 1 booster / +1 level
    PLUS_TWO = 6     # 2 boosters / +2 levels
    PLUS_THREE = 7   # 3 boosters / +3 levels
    PLUS_FOUR = 8    # 4 boosters / +4 levels
    PLUS_FIVE = 9    # 5 boosters / +5 levels (max)

class EnhancementType(IntEnum):
    """Enhancement type enumeration"""
    NORMAL = 0       # TO/DO/SO
    INVENTO = 1      # Invention Origin
    SPECIAL_O = 2    # HO/SHO
    SET_O = 3        # Set IO

@dataclass
class EnhancementSlot:
    """Represents a slotted enhancement"""
    enhancement_id: int
    enhancement_type: EnhancementType
    io_level: int = 50
    relative_level: RelativeLevel = RelativeLevel.EVEN
    is_attuned: bool = False
    is_superior: bool = False
    obtained: bool = False

class EnhancementBooster:
    """Handles enhancement booster mechanics"""

    @staticmethod
    def get_booster_count(relative_level: RelativeLevel) -> int:
        """
        Extract booster count from RelativeLevel.

        Args:
            relative_level: RelativeLevel enum value

        Returns:
            Number of boosters (0-5)
        """
        booster_map = {
            RelativeLevel.PLUS_ONE: 1,
            RelativeLevel.PLUS_TWO: 2,
            RelativeLevel.PLUS_THREE: 3,
            RelativeLevel.PLUS_FOUR: 4,
            RelativeLevel.PLUS_FIVE: 5,
        }
        return booster_map.get(relative_level, 0)

    @staticmethod
    def get_relative_level_multiplier(relative_level: RelativeLevel) -> float:
        """
        Calculate enhancement multiplier from RelativeLevel.

        Handles dual use:
        - Positive offset (IOs): +5% per booster
        - Negative offset (SOs): -10% per level below

        Args:
            relative_level: RelativeLevel enum value

        Returns:
            Multiplier (0.7 to 1.25)
        """
        if relative_level == RelativeLevel.NONE:
            return 0.0

        offset = int(relative_level) - 4  # 4 = EVEN

        if offset >= 0:
            # IOs: +5% per booster (0, 1, 2, 3, 4, 5 boosters)
            return 1.0 + (offset * 0.05)  # 1.0, 1.05, 1.10, 1.15, 1.20, 1.25
        else:
            # SOs: -10% per level below character
            return 1.0 + (offset * 0.10)  # 0.9, 0.8, 0.7

    @staticmethod
    def can_boost_enhancement(slot: EnhancementSlot) -> bool:
        """
        Check if an enhancement can be boosted.

        Args:
            slot: Enhancement slot to check

        Returns:
            True if enhancement can receive boosters
        """
        # Only IO and SetO types can be boosted
        if slot.enhancement_type not in (EnhancementType.INVENTO, EnhancementType.SET_O):
            return False

        # Attuned IOs cannot be boosted
        if slot.is_attuned:
            return False

        # Already at max boosters
        if slot.relative_level >= RelativeLevel.PLUS_FIVE:
            return False

        return True

    @staticmethod
    def apply_booster(slot: EnhancementSlot) -> bool:
        """
        Apply one booster to an enhancement.

        Args:
            slot: Enhancement slot to boost (modified in-place)

        Returns:
            True if booster was applied, False if cannot boost
        """
        if not EnhancementBooster.can_boost_enhancement(slot):
            return False

        # Increment relative level (add one booster)
        slot.relative_level = RelativeLevel(int(slot.relative_level) + 1)
        return True

    @staticmethod
    def set_booster_count(slot: EnhancementSlot, count: int) -> bool:
        """
        Set enhancement to specific booster count.

        Args:
            slot: Enhancement slot to modify (modified in-place)
            count: Number of boosters (0-5)

        Returns:
            True if booster count was set, False if invalid
        """
        # Validate booster count
        if count < 0 or count > 5:
            return False

        # Check if enhancement can be boosted
        if count > 0 and slot.enhancement_type not in (EnhancementType.INVENTO, EnhancementType.SET_O):
            return False

        if count > 0 and slot.is_attuned:
            return False

        # Set relative level (EVEN = 4, so add count)
        slot.relative_level = RelativeLevel(4 + count)
        return True

    @staticmethod
    def get_boosted_value(
        base_value: float,
        relative_level: RelativeLevel,
        is_superior: bool = False
    ) -> float:
        """
        Calculate boosted enhancement value.

        Args:
            base_value: Base enhancement value from schedule
            relative_level: RelativeLevel indicating booster count
            is_superior: Whether this is a superior enhancement

        Returns:
            Boosted enhancement value
        """
        # Apply booster multiplier
        multiplier = EnhancementBooster.get_relative_level_multiplier(relative_level)
        boosted = base_value * multiplier

        # Superior sets get additional 25% bonus
        if is_superior:
            boosted *= 1.25

        return boosted

# Helper function for build salvage counting
def count_total_boosters(build_slots: list[EnhancementSlot]) -> int:
    """
    Count total boosters needed across entire build.

    Args:
        build_slots: All enhancement slots in build

    Returns:
        Total booster count
    """
    total = 0
    for slot in build_slots:
        # Only count IO/SetO enhancements
        if slot.enhancement_type in (EnhancementType.INVENTO, EnhancementType.SET_O):
            total += EnhancementBooster.get_booster_count(slot.relative_level)

    return total

# Helper function for build import
def import_booster_from_level(level: int, enh_type: EnhancementType) -> tuple[int, RelativeLevel]:
    """
    Convert game export level to IO level + booster count.

    Game exports level 50+X IOs as level 50+X.
    Convert to level 50 with X boosters.

    Args:
        level: Exported level (may be > 50)
        enh_type: Enhancement type

    Returns:
        Tuple of (io_level, relative_level)
    """
    if enh_type not in (EnhancementType.INVENTO, EnhancementType.SET_O):
        # Not an IO, return level as-is
        return (level, RelativeLevel.EVEN)

    if level <= 50:
        return (level, RelativeLevel.EVEN)

    # Extract boosters from level
    io_level = 50
    booster_count = min(level - 50, 5)  # Max 5 boosters
    relative_level = RelativeLevel(4 + booster_count)

    return (io_level, relative_level)
```

### Implementation Notes

**Key Considerations**:

1. **RelativeLevel Dual Use**:
   - Same enum serves two purposes (SO grading and IO boosters)
   - Logic must distinguish by enhancement type
   - Multiplier calculation handles both cases
   - EVEN (value 4) is baseline for both uses

2. **Booster Restrictions**:
   - Only IO and SetO types can be boosted
   - Attuned IOs explicitly prohibited
   - Maximum 5 boosters enforced
   - Check `can_boost_enhancement()` before applying

3. **Value Calculation**:
   - Base value from schedule (Spec 10)
   - Apply booster multiplier (+5% per booster)
   - Apply superior bonus (×1.25 if applicable)
   - Order: schedule → booster → superior

4. **Import/Export**:
   - Game exports level 50+5 IO as "level 55"
   - Convert to level 50 with RelativeLevel.PLUS_FIVE
   - Clamp to 0-5 booster range
   - Handle both legacy and modern formats

5. **Salvage Counting**:
   - Sum booster counts across all IO enhancements
   - Ignore SO/HO (they use RelativeLevel for grading)
   - Used for build cost estimation
   - Display in build summary

6. **Database Storage**:
   - Store RelativeLevel as integer (0-9)
   - Efficient single-column storage
   - Compatible with MidsReborn format
   - Easy conversion to/from enum

### Edge Cases to Test

1. **Attuned IO Boost Attempt**:
   ```python
   slot = EnhancementSlot(
       enhancement_id=123,
       enhancement_type=EnhancementType.SET_O,
       is_attuned=True
   )
   assert not EnhancementBooster.can_boost_enhancement(slot)
   assert not EnhancementBooster.apply_booster(slot)
   ```

2. **Maximum Booster Limit**:
   ```python
   slot = EnhancementSlot(
       enhancement_id=456,
       enhancement_type=EnhancementType.INVENTO,
       relative_level=RelativeLevel.PLUS_FIVE
   )
   assert not EnhancementBooster.apply_booster(slot)  # Already at max
   ```

3. **SO Enhancement Grading**:
   ```python
   # SO at -3 levels below character
   slot = EnhancementSlot(
       enhancement_id=789,
       enhancement_type=EnhancementType.NORMAL,
       relative_level=RelativeLevel.MINUS_THREE
   )
   multiplier = EnhancementBooster.get_relative_level_multiplier(slot.relative_level)
   assert multiplier == 0.7  # 1.0 + (-3 × 0.10)
   ```

4. **Import Level 53 IO**:
   ```python
   io_level, rel_level = import_booster_from_level(53, EnhancementType.INVENTO)
   assert io_level == 50
   assert rel_level == RelativeLevel.PLUS_THREE  # 3 boosters
   ```

5. **Superior + Boosted IO**:
   ```python
   base_value = 42.4  # Level 50 damage IO
   boosted = EnhancementBooster.get_boosted_value(
       base_value,
       RelativeLevel.PLUS_FIVE,  # 5 boosters
       is_superior=True
   )
   # Expected: 42.4 × 1.25 (booster) × 1.25 (superior) = 66.25
   assert abs(boosted - 66.25) < 0.01
   ```

### Test Cases

**Test Case 1: Basic Booster Application**:
```python
Input:
  Level 50 Damage IO (unboosted)
  Base value: 42.4% (Schedule A, level 50)

Apply 5 boosters:
  relative_level = PLUS_FIVE
  multiplier = 1.25

Expected:
  boosted_value = 42.4 × 1.25 = 53.0%
```

**Test Case 2: Build Booster Count**:
```python
Input:
  Build with 50 IOs:
  - 30 unboosted (RelativeLevel.EVEN)
  - 10 with +3 boosters (RelativeLevel.PLUS_THREE)
  - 10 with +5 boosters (RelativeLevel.PLUS_FIVE)

Expected:
  total_boosters = (30 × 0) + (10 × 3) + (10 × 5)
                 = 0 + 30 + 50
                 = 80 boosters
```

**Test Case 3: Cannot Boost Attuned**:
```python
Input:
  Attuned Set IO (is_attuned=True)

Attempt to boost:
  can_boost_enhancement() = False

Expected:
  Booster not applied
  RelativeLevel remains EVEN
```

**Test Case 4: Import from Game Data**:
```python
Input:
  Game export: "Crafted_Damage_A.Crafted_Damage_A.53"
  Type: InventO

Parse:
  import_booster_from_level(53, EnhancementType.INVENTO)

Expected:
  io_level = 50
  relative_level = PLUS_THREE (3 boosters)
```

### Validation Strategy

1. **Compare Multipliers to MidsReborn**:
   - Test all RelativeLevel values (0-9)
   - Verify multipliers match GetRelativeLevelMultiplier()
   - Check both positive (boosters) and negative (SO grading)

2. **Test Import/Export**:
   - Import MidsReborn build with boosted IOs
   - Verify booster counts extracted correctly
   - Re-export and compare to original

3. **Validate Build Counting**:
   - Load reference build with known booster counts
   - Count total boosters in Python
   - Compare to MidsReborn salvage summary

4. **Test Enhancement Values**:
   - Calculate boosted values for common IOs
   - Compare to MidsReborn display values
   - Verify superior bonus stacking

## References

- Related Specs:
  - **Spec 10**: Enhancement Schedules (base values boosters multiply)
  - **Spec 11**: Enhancement Slotting (booster application context)
  - **Spec 13**: Enhancement Set Bonuses (boosters don't affect set bonuses)
  - **Spec 14**: Special IOs (attuned restriction)
  - **Spec 37**: Enhancement Catalysts (similar consumable mechanic)

- MidsReborn Files:
  - `Core/I9Slot.cs` - RelativeLevel property and multiplier calculation
  - `BuildImportTools.cs` - Booster import/export conversion
  - `clsBuildSalvageSummary.cs` - Booster counting for salvage display
  - `Forms/Controls/EnhCheckMode.cs` - UI booster display
  - `Forms/frmRecipeViewer.cs` - Recipe view booster tracking

- Game Mechanics:
  - City of Heroes Wiki: Enhancement Boosters
  - Homecoming Wiki: Enhancement Boosters
  - Paragon Wiki: Invention Origin Enhancements

---

**Document Status**: ✅ Breadth Complete - High-level structure documented
**Next Steps**: Await Milestone 3 for depth detail (comprehensive testing, edge case handling, UI integration)
