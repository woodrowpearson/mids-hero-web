# Attuned IOs

**Status:** 🟡 Breadth Complete
**Priority:** Medium
**Complexity:** Medium (level scaling with no exemplar penalty)

## Overview

**Purpose**: Attuned Invention Origin Enhancements automatically scale their enhancement values to the character's current level (20-50), with NO exemplar penalty. This makes them always active at full strength regardless of level reduction.

**Used By**:
- Enhancement value calculations (I9Slot.cs)
- Build totals (all stats)
- Set bonus activation (some sets are always attuned)
- Exemplar mechanics (attuned IOs bypass exemplar penalties)

**Key Benefit**: Unlike standard IOs which have a fixed level and suffer exemplar penalties, attuned IOs scale dynamically with character level and maintain full effectiveness when exemplared down.

**Complexity**: Medium - requires tracking character level, applying set's level range, and bypassing normal exemplar penalty logic.

## MidsReborn Implementation

### Primary Location

**Files**:
- `Core/DatabaseAPI.cs` - Lines 803-809 (EnhIsNaturallyAttuned)
- `Core/I9Slot.cs` - Lines 14, 90-98, 119, 125 (IOLevel property and scaling)
- `Core/Enhancement.cs` - Lines 56-57, 105-106 (LevelMin/LevelMax properties)
- `Forms/OptionsMenuItems/DbEditor/frmEnhData.cs` - Lines 396-401 (Attuned editing logic)
- `Core/Base/Data_Classes/Character.cs` - Lines 1036, 1041-1042 (Display logic)

**Key Methods**:
- `DatabaseAPI.EnhIsNaturallyAttuned(int enhIdx)` - Identifies naturally attuned enhancements
- `DatabaseAPI.EnhIsATO(int enhIdx)` - Checks if enhancement is Archetype Origin
- `DatabaseAPI.EnhIsWinterEventE(int enhIdx)` - Checks for Winter Event sets
- `DatabaseAPI.EnhIsMovieE(int enhIdx)` - Checks for Movie sets (Overwhelming Force, Cupid's Crush)
- `I9Slot.GetScheduleMult()` - Uses IOLevel to look up enhancement value

### Dependencies

**Data Structures**:
- `Enhancement.LevelMin` (int) - Minimum level for the enhancement (set's min level)
- `Enhancement.LevelMax` (int) - Maximum level for the enhancement (usually 0 for attuned)
- `I9Slot.IOLevel` (int) - Current effective level for IO calculations
- `Database.MultIO` (float[][]) - Enhancement value lookup table by level

**Related Classes**:
- `EnhancementSet` - Contains set metadata (DisplayName for detection)
- `Character` - Provides current character level
- `Build` - Aggregates attuned IO effects

### Algorithm Pseudocode

```
function EnhIsNaturallyAttuned(enhancementIndex):
    // Three categories are always attuned
    if EnhIsATO(enhancementIndex):           // Archetype Origin enhancements
        return true
    if EnhIsWinterEventE(enhancementIndex):  // Winter Event sets (5 sets)
        return true
    if EnhIsMovieE(enhancementIndex):        // Movie sets (Overwhelming Force, Cupid's Crush)
        return true
    return false

function EnhIsATO(enhancementIndex):
    enhancement = Database.Enhancements[enhancementIndex]
    if enhancement has no set (nIDSet == -1):
        return false

    enhancementSet = Database.EnhancementSets[enhancement.nIDSet]
    setTypeName = GetSetTypeByIndex(enhancementSet.SetType).Name

    return setTypeName contains "Archetype"

function EnhIsWinterEventE(enhancementIndex):
    enhancement = Database.Enhancements[enhancementIndex]
    if enhancement has no set:
        return false

    enhancementSet = Database.EnhancementSets[enhancement.nIDSet]
    setName = enhancementSet.DisplayName

    // Five Winter Event sets are naturally attuned
    return setName in ["Avalanche", "Blistering Cold", "Entomb",
                       "Frozen Blast", "Winter's Bite"]

function EnhIsMovieE(enhancementIndex):
    enhancement = Database.Enhancements[enhancementIndex]
    if enhancement has no set:
        return false

    enhancementSet = Database.EnhancementSets[enhancement.nIDSet]
    setName = enhancementSet.DisplayName

    // Two movie sets are naturally attuned
    return setName in ["Overwhelming Force", "Cupid's Crush"]

function CalculateAttunedIOLevel(enhancement, characterLevel):
    // Attuned IOs scale to character level within set's range

    if enhancement.LevelMin == 0 and enhancement.LevelMax == 0:
        // Special case: attuned sets often have min=0, max=0
        // This means they use their set's level range
        enhancementSet = Database.EnhancementSets[enhancement.nIDSet]
        minLevel = enhancementSet.MinLevel  // Usually 10-25
        maxLevel = 50  // Attuned IOs cap at 50
    else:
        minLevel = enhancement.LevelMin
        maxLevel = enhancement.LevelMax

    // Clamp character level to valid range
    effectiveLevel = max(minLevel, min(characterLevel, maxLevel))

    // Convert to 0-based index for MultIO lookup
    ioLevel = effectiveLevel - 1

    return ioLevel

function GetEnhancementValue(slot, attribute, schedule):
    // Standard IO calculation - attuned IOs use same logic
    // but IOLevel is dynamically calculated from character level

    if slot.IOLevel < 0:
        slot.IOLevel = 0
    if slot.IOLevel >= Database.MultIO.Length:
        slot.IOLevel = Database.MultIO.Length - 1

    // Look up base value from schedule table
    baseValue = Database.MultIO[slot.IOLevel][schedule]

    // Apply relative level multiplier (for non-attuned IOs)
    // Attuned IOs don't use relative level (always "Even")
    value = baseValue * GetRelativeLevelMultiplier(slot.RelativeLevel)

    // Apply Superior multiplier if applicable
    if slot.Enh.Superior:
        value *= 1.25

    return value

function CheckExemplarPenalty(slot, characterLevel, powerLevel):
    // Attuned IOs bypass exemplar penalties entirely

    enhancement = Database.Enhancements[slot.Enh]

    if EnhIsNaturallyAttuned(slot.Enh):
        // NO PENALTY - this is the key benefit
        // Attuned IO scales to current character level (even if exemplared)
        return NO_PENALTY
    else:
        // Standard IOs suffer penalties when exemplared
        // If character level < power level + 3, enhancement may not work
        if characterLevel < powerLevel + 3:
            return APPLY_PENALTY
        return NO_PENALTY
```

### Key Logic Snippets

**EnhIsNaturallyAttuned Detection** (DatabaseAPI.cs:803-809):
```csharp
public static bool EnhIsNaturallyAttuned(int enhIdx)
{
    if (enhIdx == -1) return false;
    if (enhIdx >= Database.Enhancements.Length) return false;

    return EnhIsATO(enhIdx) || EnhIsWinterEventE(enhIdx) || EnhIsMovieE(enhIdx);
}
```

**Winter Event Set Detection** (DatabaseAPI.cs:722-737):
```csharp
public static bool EnhIsWinterEventE(int enhIdx)
{
    if (enhIdx == -1) return false;
    if (enhIdx >= Database.Enhancements.Length) return false;

    var enhData = Database.Enhancements[enhIdx];
    if (enhData.nIDSet == -1) return false;

    var enhSetData = Database.EnhancementSets[enhData.nIDSet];

    return enhSetData.DisplayName.IndexOf("Avalanche", StringComparison.OrdinalIgnoreCase) > -1 ||
           enhSetData.DisplayName.IndexOf("Blistering Cold", StringComparison.OrdinalIgnoreCase) > -1 ||
           enhSetData.DisplayName.IndexOf("Entomb", StringComparison.OrdinalIgnoreCase) > -1 ||
           enhSetData.DisplayName.IndexOf("Frozen Blast", StringComparison.OrdinalIgnoreCase) > -1 ||
           enhSetData.DisplayName.IndexOf("Winter's Bite", StringComparison.OrdinalIgnoreCase) > -1;
}
```

**IOLevel Scaling** (I9Slot.cs:90-98, 119):
```csharp
// IOLevel clamping for MultIO lookup
if (IOLevel <= 0)
{
    IOLevel = 0;
}

if (IOLevel > DatabaseAPI.Database.MultIO.Length - 1)
{
    IOLevel = DatabaseAPI.Database.MultIO.Length - 1;
}

// ...

case Enums.eType.InventO:
    num1 = DatabaseAPI.Database.MultIO[IOLevel][(int)iSched];
    break;
```

**Display Logic for Attuned IOs** (Character.cs:1036, 1041-1042):
```csharp
case Enums.eType.InventO:
    popupData1.Sections[index1].Add($"Invention Level: {iSlot.IOLevel + 1}{iSlot.GetRelativeString(false)} - {iSlot.GetEnhancementString()}", PopUp.Colors.Invention);
    break;
// ...
case Enums.eType.SetO when !DatabaseAPI.EnhIsNaturallyAttuned(iSlot.Enh):
    // Only show level for NON-attuned set IOs
    popupData1.Sections[index1].Add($"Invention Level: {iSlot.IOLevel + 1}{iSlot.GetRelativeString(false)}", PopUp.Colors.Invention);
    break;
```

**Attuned LevelMin/LevelMax Handling** (frmEnhData.cs:396-401):
```csharp
if (txtInternal.Text.Contains("Attuned"))
{
    // Attuned enhancements have special level handling
    myEnh.LevelMin = 0;
    myEnh.LevelMax = 0;
    udMinLevel.Minimum = 1;
    udMinLevel.Maximum = 53;
}
```

## Game Mechanics Context

### Why Attuned IOs Exist

**Problem**: Standard Invention Origin Enhancements have a fixed level (crafted at level 25, 30, 35, etc.). When a character exemplars down to a lower level (e.g., to play with friends or run lower-level content), IOs more than 3 levels above the character become inactive, losing set bonuses and enhancement values.

**Solution**: Attuned IOs dynamically scale to the character's current level within the set's level range. They provide full enhancement values and set bonuses regardless of exemplar level, making them ideal for characters who frequently play at different levels.

### Historical Context

**Introduction**: Attuned enhancements were introduced with the Paragon Market (City of Heroes Freedom, Issue 21, September 2011) as a premium feature.

**Initial Implementation**:
- Archetype Origin (ATO) enhancements were always attuned
- Winter Event sets were always attuned
- Other IO sets could be converted to attuned versions using "Attuned" conversion recipes

**Homecoming Changes**:
- Attuned conversion became more accessible
- Additional special sets (Movie sets) added as naturally attuned
- Catalyst system introduced for Superior versions (but attuned can't be catalyzed)

### The Three Categories of Attuned IOs

1. **Archetype Origin (ATO) Sets** - Always Attuned
   - Exclusive to specific archetypes
   - Always drop/craft as attuned
   - Can be catalyzed to Superior (still attuned)
   - Examples: Brute's Fury, Blaster's Wrath, Controller's Absolute Amazement

2. **Winter Event Sets** - Always Attuned
   - Five sets available only during Winter Event
   - Always attuned by default
   - Can be catalyzed to Superior
   - Sets: Avalanche, Blistering Cold, Entomb, Frozen Blast, Winter's Bite

3. **Movie/Special Sets** - Always Attuned
   - Overwhelming Force (Knockback to Knockdown unique)
   - Cupid's Crush (Valentine's Day event set)

4. **Converted Attuned IOs** - Optional Attuning
   - Most IO sets can be converted to attuned versions
   - Requires "Attuned" prefix in UID (e.g., "Attuned_Thunderstrike_A")
   - Cannot be boosted with Enhancement Boosters (mutually exclusive)

### Key Benefits

1. **No Exemplar Penalty**: Full effectiveness at any level
2. **Leveling Convenience**: Automatically improves as character levels
3. **Set Bonus Retention**: Set bonuses remain active when exemplared
4. **Quality of Life**: No need to re-slot when changing level ranges

### Trade-offs

**Advantages**:
- Always active regardless of level
- Scale up automatically while leveling
- Perfect for characters who exemplar frequently

**Disadvantages**:
- CANNOT be boosted with Enhancement Boosters (+1 to +5)
- May be weaker than a fixed-level +5 boosted IO at maximum level
- Generally more expensive on the auction house

### Known Quirks

1. **Level Range**: Attuned IOs use the set's minimum level (usually 10-25) as their floor, scaling up to character level (max 50)

2. **Superior Attuned**: Superior ATOs and Winter sets are both Superior AND Attuned, getting 1.25x multiplier + level scaling + no exemplar penalty

3. **Database Representation**: Attuned enhancements often have `LevelMin=0` and `LevelMax=0` in the database, indicating they use the set's level range instead

4. **UID Prefix**: Attuned versions of standard sets use "Attuned_" prefix in their UID (e.g., "Attuned_Crushing_Impact_A" vs "Crushing_Impact_A")

5. **Cannot Be Boosted**: Attuned and Boosted are mutually exclusive. You must choose one or the other.

6. **Display Difference**: Non-attuned IOs show "Invention Level: XX" in tooltips. Attuned IOs omit this because level is dynamic.

## Python Implementation Notes

### Proposed Architecture

**Location**: `backend/app/calculations/enhancements/attuned.py`

**Related Modules**:
- `enhancements/base.py` - Base Enhancement class
- `enhancements/io_scaling.py` - MultIO lookup tables
- `enhancements/schedules.py` - Schedule system (ED curves)
- `character/level.py` - Character level tracking
- `character/exemplar.py` - Exemplar mechanics (attuned bypass)

### Data Classes

```python
from dataclasses import dataclass
from enum import Enum

class AttunedType(Enum):
    """Categories of naturally attuned enhancements"""
    NONE = 0
    ATO = 1              # Archetype Origin
    WINTER_EVENT = 2     # Winter Event sets
    MOVIE = 3            # Overwhelming Force, Cupid's Crush
    CONVERTED = 4        # Standard IO converted to attuned

@dataclass
class AttunedEnhancement:
    """Represents an attuned IO with level scaling"""

    enhancement_id: int
    set_id: int
    attuned_type: AttunedType
    base_min_level: int  # Set's minimum level (usually 10-25)
    base_max_level: int  # Always 50 for attuned
    is_superior: bool    # Can be both superior AND attuned

    def calculate_effective_level(self, character_level: int) -> int:
        """
        Calculate effective IO level based on character level.

        Args:
            character_level: Current character level (1-50)

        Returns:
            Effective IO level clamped to set's range (0-based index)
        """
        # Clamp to set's valid range
        clamped_level = max(self.base_min_level,
                           min(character_level, self.base_max_level))

        # Convert to 0-based index for MultIO lookup
        return clamped_level - 1

    def calculate_scaled_value(
        self,
        character_level: int,
        schedule: int,
        mult_io_table: list[list[float]]
    ) -> float:
        """
        Calculate enhancement value at current character level.

        Args:
            character_level: Current character level
            schedule: ED schedule (0-4)
            mult_io_table: MultIO lookup table [level][schedule]

        Returns:
            Enhancement value (0.0 to ~1.0)
        """
        io_level = self.calculate_effective_level(character_level)

        # Bounds check
        if io_level < 0:
            io_level = 0
        if io_level >= len(mult_io_table):
            io_level = len(mult_io_table) - 1

        # Base value from MultIO table
        base_value = mult_io_table[io_level][schedule]

        # Apply Superior multiplier if applicable
        if self.is_superior:
            base_value *= 1.25

        return base_value

    def bypasses_exemplar_penalty(self) -> bool:
        """
        Attuned IOs ALWAYS bypass exemplar penalties.

        This is the key benefit of attuned enhancements.
        """
        return True

@dataclass
class AttunedDetector:
    """Detects if an enhancement is naturally attuned"""

    # Class constants for naturally attuned sets
    WINTER_EVENT_SETS = {
        "Avalanche",
        "Blistering Cold",
        "Entomb",
        "Frozen Blast",
        "Winter's Bite"
    }

    MOVIE_SETS = {
        "Overwhelming Force",
        "Cupid's Crush"
    }

    @staticmethod
    def is_ato(enhancement_set_type_name: str) -> bool:
        """Check if enhancement is Archetype Origin"""
        return "Archetype" in enhancement_set_type_name

    @staticmethod
    def is_winter_event(enhancement_set_name: str) -> bool:
        """Check if enhancement is from Winter Event"""
        return enhancement_set_name in AttunedDetector.WINTER_EVENT_SETS

    @staticmethod
    def is_movie(enhancement_set_name: str) -> bool:
        """Check if enhancement is from Movie sets"""
        return enhancement_set_name in AttunedDetector.MOVIE_SETS

    @staticmethod
    def is_converted_attuned(enhancement_uid: str) -> bool:
        """Check if enhancement has Attuned_ prefix"""
        return enhancement_uid.startswith("Attuned_")

    @classmethod
    def detect_attuned_type(
        cls,
        enhancement_uid: str,
        enhancement_set_name: str,
        enhancement_set_type_name: str
    ) -> AttunedType:
        """
        Detect what type of attuned enhancement this is.

        Returns AttunedType.NONE if not attuned.
        """
        if cls.is_ato(enhancement_set_type_name):
            return AttunedType.ATO

        if cls.is_winter_event(enhancement_set_name):
            return AttunedType.WINTER_EVENT

        if cls.is_movie(enhancement_set_name):
            return AttunedType.MOVIE

        if cls.is_converted_attuned(enhancement_uid):
            return AttunedType.CONVERTED

        return AttunedType.NONE

    @classmethod
    def is_naturally_attuned(
        cls,
        enhancement_uid: str,
        enhancement_set_name: str,
        enhancement_set_type_name: str
    ) -> bool:
        """
        Check if enhancement is naturally attuned.

        Equivalent to MidsReborn's EnhIsNaturallyAttuned().
        """
        attuned_type = cls.detect_attuned_type(
            enhancement_uid,
            enhancement_set_name,
            enhancement_set_type_name
        )

        return attuned_type != AttunedType.NONE
```

### Key Functions

```python
def calculate_attuned_io_value(
    enhancement: AttunedEnhancement,
    character_level: int,
    schedule_id: int,
    attribute_value: float,
    mult_io_table: list[list[float]]
) -> float:
    """
    Calculate attuned IO's contribution to an attribute.

    Args:
        enhancement: Attuned enhancement data
        character_level: Current character level (1-50)
        schedule_id: ED schedule (0-4) for the attribute
        attribute_value: Existing attribute value before this enhancement
        mult_io_table: MultIO lookup table

    Returns:
        Enhanced value after applying attuned IO

    Example:
        # Level 35 character with Attuned ATO (min 10, max 50)
        # +33.33% damage enhancement on Schedule A
        enhanced = calculate_attuned_io_value(
            ato_damage_piece,
            character_level=35,
            schedule_id=SCHEDULE_A,
            attribute_value=0.0,
            mult_io_table=MULT_IO_TABLE
        )
        # Returns ~0.333 (level 35 IO value)

        # Same character exemplared to level 20
        enhanced = calculate_attuned_io_value(
            ato_damage_piece,
            character_level=20,  # Exemplared down
            schedule_id=SCHEDULE_A,
            attribute_value=0.0,
            mult_io_table=MULT_IO_TABLE
        )
        # Returns ~0.256 (level 20 IO value)
        # Standard IO would be INACTIVE at this point!
    """
    base_value = enhancement.calculate_scaled_value(
        character_level,
        schedule_id,
        mult_io_table
    )

    return attribute_value + base_value
```

### Implementation Notes

**C# vs Python Differences**:
1. **String Detection**: C# uses `IndexOf()` for case-insensitive matching. Python should use `str.lower() in set()` for performance.
2. **0-based vs 1-based**: C# IOLevel is 0-based index. Character level is 1-based. Keep this distinction clear.
3. **Array Bounds**: C# clamps IOLevel explicitly. Python should validate array access or use `min(index, len(table)-1)`.

**Edge Cases to Test**:
1. **Level 1 Character**: Attuned IO should use set's minimum level
2. **Level 50 Character**: Attuned IO should cap at 50
3. **Exemplar to Level 1**: Attuned IO should still work (at set's min level)
4. **Superior Attuned**: Should get both 1.25x multiplier AND level scaling
5. **LevelMin=0, LevelMax=0**: Should use set's level range instead

**Performance Considerations**:
- Cache attuned detection results (doesn't change during session)
- Pre-compute effective levels for common character levels
- Use set lookups for Winter/Movie set detection (O(1) vs string contains)

**Validation Strategy**:
1. Extract MultIO table from MidsReborn database
2. Test attuned calculations at levels 1, 10, 20, 30, 40, 50
3. Compare with MidsReborn's display values for same enhancement
4. Verify exemplar bypass (attuned should work, standard should not)
5. Test Superior attuned (1.25x multiplier applies)

### Test Cases

```python
# Test Case 1: ATO at various levels
# Enhancement: Brute's Fury: Accuracy/Damage (ATO, min level 10)
# Expected: Scales from level 10 to 50
assert calculate_io_level(ato_acc_dam, char_level=1) == 9   # Clamped to min (10-1=9)
assert calculate_io_level(ato_acc_dam, char_level=25) == 24  # Normal scaling
assert calculate_io_level(ato_acc_dam, char_level=50) == 49  # Max level

# Test Case 2: Winter Event IO
# Enhancement: Avalanche: Damage/Endurance (min level 10)
assert is_naturally_attuned("Avalanche") == True
assert calculate_io_level(avalanche_dam_end, char_level=15) == 14

# Test Case 3: Exemplar scenario
# Standard IO vs Attuned IO at level 20 (character exemplared from 50)
# Standard level 35 IO: INACTIVE (35 > 20+3)
# Attuned ATO: ACTIVE at level 20 value
assert bypasses_exemplar_penalty(standard_io) == False
assert bypasses_exemplar_penalty(attuned_ato) == True

# Test Case 4: Superior Attuned
# Superior ATO should get 1.25x multiplier
superior_ato = AttunedEnhancement(
    attuned_type=AttunedType.ATO,
    is_superior=True,
    base_min_level=10,
    base_max_level=50
)
value = calculate_scaled_value(superior_ato, char_level=50, schedule=SCHEDULE_A)
# Should be ~0.416 (0.333 * 1.25) at level 50

# Test Case 5: Converted Attuned vs Standard
# "Attuned_Crushing_Impact_A" vs "Crushing_Impact_A"
assert is_converted_attuned("Attuned_Crushing_Impact_A") == True
assert is_converted_attuned("Crushing_Impact_A") == False
```

## References

- **Related Specs**:
  - Spec 10: Enhancement Schedules (ED curves applied to attuned values)
  - Spec 11: Enhancement Slotting (how attuned IOs slot into powers)
  - Spec 13: Enhancement Set Bonuses (attuned sets maintain bonuses when exemplared)
  - Spec 36: Enhancement Boosters (mutually exclusive with attuned)
  - Spec 42: Exemplar Mechanics (attuned IOs bypass penalties)

- **MidsReborn Files**:
  - `Core/DatabaseAPI.cs` - Attuned detection logic
  - `Core/I9Slot.cs` - IO level scaling calculations
  - `Core/Enhancement.cs` - Enhancement data model

- **Game Mechanics**:
  - City of Heroes Wiki: "Invention Origin Enhancements"
  - Homecoming Wiki: "Attuned Enhancements"
  - Paragon Wiki: "Enhancement Diversification"

---

**Document Status**: ✅ Breadth Complete - High-level overview, algorithm, game context, Python design documented
**Next Step**: Add to index, mark Spec 37 complete, commit changes
