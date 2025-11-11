# Archetype Modifiers

## Overview

- **Purpose**: Applies AT-specific scaling to power effects - the same power does different amounts of damage/buff/debuff/control for different archetypes
- **Used By**: All power effect calculations (damage, buffs, debuffs, control, healing, etc.)
- **Complexity**: Medium
- **Priority**: **CRITICAL** - Foundation for correct power display
- **Status**: Breadth Complete

**Why This Is Critical**: Without AT modifiers, a Defender would show the same damage numbers as a Scrapper, which is completely wrong. This is the core mechanic that differentiates archetypes beyond just HP/caps.

---

## MidsReborn Implementation

### Primary Location

- **File**: `Core/Modifiers.cs`
- **Class**: `Modifiers` and `ModifierTable`
- **Methods**:
  - `Modifiers.Load()` - Loads modifier tables from JSON/binary (lines 41-120)
  - `ModifierTable.Load()` - Loads individual table from binary (lines 183-196)
  - `ModifierTable.StoreTo()` - Saves table to binary (lines 168-181)

### Application Location

- **File**: `Core/DatabaseAPI.cs`
- **Methods**:
  - `GetModifier(IEffect iEffect)` - Main entry point, determines which table/class/level to use (lines ~600-650)
  - `GetModifier(int iClass, int iTable, int iLevel)` - Core lookup function (lines ~650-680)
  - `MatchModifierIDs()` - Links effect ModifierTable strings to table indices (lines ~1200-1210)

### Data Storage

- **File**: `Core/Base/Data_Classes/Effect.cs`
- **Properties**:
  - `string ModifierTable` - Table name like "Melee_Damage", "Ranged_Buff_Def"
  - `int nModifierTable` - Index into Modifiers.Modifier list
- **Default**: `ModifierTable = "Melee_Ones"` (all 1.0 modifiers)

### Data Files

- **Location**: `Data/Homecoming/AttribMod.json` (also Rebirth, Generic servers)
- **Format**: JSON file with 102 modifier tables
- **Structure**:
  - Each table has ID (name), BaseIndex, and Table (2D array)
  - Table dimensions: [55 levels] × [60 archetypes]
  - Values are floating-point multipliers

---

## Dependencies

### Required Data
- **Archetype.Column** - Which column in the modifier table corresponds to each AT
- **IEffect.ModifierTable** - Which modifier table to use for an effect
- **Character level** - Which row in the table to use (0-54 for levels 1-55)

### Related Classes
- `Archetype` - Contains Column property mapping AT to table column
- `IEffect` / `Effect` - Contains ModifierTable and nModifierTable
- `DatabaseAPI` - Provides lookup functions
- `Power` - May have ForcedClass to override which AT's modifiers are used

---

## Algorithm Pseudocode

### Loading Modifier Tables
```
FUNCTION Load(filepath):
    IF JSON file exists:
        Deserialize JSON to Modifiers object
        RETURN success

    ELSE IF binary file exists:
        Open binary reader
        READ header "Mids' Hero Designer Attribute Modifier Tables"
        READ Revision, RevisionDate, SourceIndex, SourceTables

        FOR each modifier table:
            READ table ID (string)
            READ BaseIndex (int)
            FOR each level (55 rows):
                READ archetype count
                FOR each archetype:
                    READ modifier value (float)

        RETURN success

    RETURN failure
END FUNCTION
```

### Applying Modifiers to Effects
```
FUNCTION GetModifier(effect):
    // Determine which archetype to use
    IF effect has summoned entity:
        iClass = entity's archetype index
    ELSE IF power has ForcedClass:
        iClass = NidFromUidClass(ForcedClass)
    ELSE IF effect.Absorbed_Class_nID >= 0:
        iClass = effect.Absorbed_Class_nID
    ELSE:
        iClass = current character's archetype index

    // Get modifier table index
    iTable = effect.nModifierTable

    // Get character level (zero-based)
    iLevel = character.Level - 1

    // Look up modifier value
    RETURN GetModifier(iClass, iTable, iLevel)
END FUNCTION

FUNCTION GetModifier(iClass, iTable, iLevel):
    // Validation
    IF iClass < 0 OR iTable < 0 OR iLevel < 0:
        RETURN 0

    IF iTable >= modifier table count:
        RETURN 0

    IF iLevel >= table row count:
        RETURN 0

    // Get archetype column from class definition
    iClassColumn = Database.Classes[iClass].Column

    IF iClassColumn < 0:
        RETURN 0

    IF iClassColumn >= table column count:
        RETURN 0

    // Return the modifier value
    RETURN AttribMods.Modifier[iTable].Table[iLevel][iClassColumn]
END FUNCTION
```

### Effect Magnitude Calculation
```
FUNCTION Calculate_Effect_Magnitude(effect):
    base_magnitude = effect.nMagnitude
    scale = effect.Scale
    modifier = GetModifier(effect)

    RETURN scale * base_magnitude * modifier
END FUNCTION
```

---

## Key Logic Snippets

### Modifier Table Structure (Modifiers.cs, lines 138-197)
```csharp
[JsonObject]
public class ModifierTable
{
    [JsonProperty("Table")]
    public List<List<float>> Table = new List<List<float>>();

    [JsonProperty("BaseIndex")]
    public int BaseIndex;

    [JsonProperty("ID")]
    public string ID = string.Empty;

    public void Load(BinaryReader reader)
    {
        ID = reader.ReadString();
        BaseIndex = reader.ReadInt32();
        for (var index1 = 0; index1 <= Table.Count - 1; ++index1)
        {
            Table.Add(new List<float>());
            for (var index2 = 0; index2 <= Table[index1].Count - 1; ++index2)
            {
                Table[index1].Add(reader.ReadSingle());
            }
        }
    }
}
```

### Modifier Lookup (DatabaseAPI.cs, ~lines 650-680)
```csharp
private static float GetModifier(int iClass, int iTable, int iLevel)
{
    //Warning: calling this method with iTable == 0 can lead to super weird return values.
    if (iClass < 0) return 0;
    if (iTable < 0) return 0;
    if (iLevel < 0) return 0;

    if (iClass > Database.Classes.Length - 1) return 0;

    var iClassColumn = Database.Classes[iClass].Column;
    if (iClassColumn < 0) return 0;
    if (iTable > Database.AttribMods.Modifier.Count - 1) return 0;
    if (iLevel > Database.AttribMods.Modifier[iTable].Table.Count - 1) return 0;
    if (iClassColumn > Database.AttribMods.Modifier[iTable].Table[iLevel].Count - 1) return 0;

    return Database.AttribMods.Modifier[iTable].Table[iLevel][iClassColumn];
}
```

### Effect Using Modifier (Effect.cs, ~line 800)
```csharp
Enums.eAttribType.Magnitude => Scale * nMagnitude * DatabaseAPI.GetModifier(this),
```

---

## Game Mechanics Context

### Why Modifiers Exist

Archetype modifiers are **the core balancing mechanism** in City of Heroes that allows different archetypes to use the same powers but with different effectiveness:

1. **AT Balance**: Scrappers do more melee damage than Tankers, who focus on survival
2. **Role Definition**: Defenders buff/debuff better than Controllers, who control better
3. **Power Sharing**: Same power (like Hasten from Speed pool) works identically for all ATs
4. **Forced Multiplier**: Epic/Patron pools scale with the AT that uses them

### Modifier Categories

There are 102 different modifier tables in Homecoming's data, organized by:

1. **Range**: Melee vs Ranged
2. **Effect Type**: Damage, Heal, Buff, Debuff, Control (Stun, Sleep, Immobilize, etc.)
3. **Specific Attribute**: Defense, ToHit, Damage, MaxHP, Recharge, etc.

**Common Table Names**:
- `Melee_Damage` - Melee attack damage scaling
- `Ranged_Damage` - Ranged attack damage scaling
- `Melee_Buff_Def` - Melee defense buff scaling
- `Melee_Debuff_Def` - Melee defense debuff scaling
- `Ranged_Buff_ToHit` - Ranged ToHit buff scaling
- `Melee_Heal` - Melee healing scaling
- `Melee_Control` - Melee control effect scaling
- `Melee_Ones` / `Ranged_Ones` - No scaling (all 1.0)

### Example Scaling Values (Level 50, First 5 ATs)

From `AttribMod.json`:

**Melee_Damage** (negative values represent damage):
- Column 0: -10.0 (Tanker)
- Column 1: -9.1 (likely Scrapper)
- Column 2: -9.1
- Column 3: -10.25
- Column 4: -9.9

**Melee_Buff_Def**:
- Column 0: 0.07 (Tanker - weaker defense buffs)
- Column 1: 0.09 (Scrapper)
- Column 2: 0.1 (likely Defender - stronger defense buffs)
- Column 3: 0.075
- Column 4: 0.1

**Melee_Debuff_Def**:
- Column 0: -0.07 (Tanker - weaker debuffs)
- Column 1: -0.1 (Scrapper)
- Column 2: -0.125 (likely Defender - stronger debuffs)
- Column 3: -0.075
- Column 4: -0.07

**Pattern**: Higher absolute value = stronger effect for that AT

### Level Scaling

Modifier tables have 55 rows (levels 1-55) to support:
- Normal levels 1-50
- Alpha shift levels 51-53 (Incarnate)
- Additional headroom for future level increases

Values generally scale up as level increases, though the scaling pattern varies by table and AT.

### Special Cases

1. **ForcedClass**: Some powers override which AT's modifiers are used
   - Example: Patron/Epic pools may force specific scaling

2. **Absorbed Effects**: Powers that grant other powers may use different AT scaling
   - `Absorbed_Class_nID` property determines which AT to use

3. **Pet Powers**: Summoned pets use their own AT modifiers, not the player's
   - Pet archetype (Henchman, Pet, etc.) has its own column

4. **Default Tables**:
   - `Melee_Ones` and `Ranged_Ones` contain all 1.0 values
   - Used when no scaling is desired (e.g., cosmetic effects)

---

## Python Implementation Guide

### Proposed Architecture

**Location**: `backend/mhw/calculations/modifiers.py`

**Module Structure**:
```python
class ModifierTable:
    """Single modifier table (e.g., Melee_Damage)"""
    id: str
    base_index: int
    table: list[list[float]]  # [level][archetype_column]

    def get_modifier(self, level: int, archetype_column: int) -> float:
        """Get modifier for specific level and AT"""

class ArchetypeModifiers:
    """Manager for all modifier tables"""
    tables: dict[str, ModifierTable]  # ID -> table
    table_index: dict[str, int]  # ID -> index

    @classmethod
    def load_from_json(cls, filepath: Path) -> 'ArchetypeModifiers':
        """Load from AttribMod.json"""

    def get_modifier(
        self,
        table_id: str,
        level: int,
        archetype_column: int
    ) -> float:
        """Main lookup function"""

    def get_modifier_for_effect(
        self,
        effect: 'Effect',
        character_archetype: 'Archetype',
        character_level: int
    ) -> float:
        """Get modifier for an effect based on character state"""
```

### Integration Points

1. **Database Schema**:
   - Store modifier tables in JSON format in database or load from file
   - Link archetypes to their Column value
   - Effects should store modifier_table_id

2. **Effect Calculation**:
   - Every effect magnitude calculation must call `get_modifier()`
   - Integrate with power calculation engine from spec 01

3. **Archetype System**:
   - Archetype model needs `column` field
   - Character build needs current archetype and level

### Implementation Notes

**Data Loading**:
- Load `AttribMod.json` at application startup or cache in database
- Validate table structure (55 levels, consistent column count)
- Build index for fast lookups by table ID

**Lookup Performance**:
- Simple 2D array lookup: O(1) after validation
- Cache frequently-used modifiers if performance is concern
- Most lookups happen during power calculation, not every frame

**Validation**:
- Bounds checking critical (level, archetype column, table existence)
- Return 0.0 or raise exception for invalid lookups? Decision needed
- Log warnings for missing tables (helps debug data issues)

**Edge Cases**:
1. **Level out of range**: Clamp to 1-55 or return error?
2. **Missing table**: Fall back to "Melee_Ones" / "Ranged_Ones"?
3. **Invalid archetype column**: Return 0.0 or error?
4. **Future level expansion**: Table may not have row 56+ yet

**C# vs Python Differences**:
- C# uses 0-based indexing (level 1 = index 0)
- Python will use same convention for consistency
- C# returns 0 for errors; Python could raise exceptions or return Optional[float]

### Test Cases

**Test 1: Basic Melee Damage Lookup**
```python
# Level 50 Scrapper (column 1) using Melee_Damage
table_id = "Melee_Damage"
level = 50
archetype_column = 1
expected = -9.1  # From actual data

modifier = modifiers.get_modifier(table_id, level, archetype_column)
assert abs(modifier - expected) < 0.001
```

**Test 2: Buff Scaling Difference**
```python
# Level 50 - Tanker vs Defender defense buff
table_id = "Melee_Buff_Def"
level = 50

tanker_mod = modifiers.get_modifier(table_id, level, 0)  # 0.07
defender_mod = modifiers.get_modifier(table_id, level, 2)  # 0.1

assert defender_mod > tanker_mod  # Defenders buff better
```

**Test 3: Level Scaling**
```python
# Same AT, different levels
table_id = "Melee_Damage"
archetype_column = 1  # Scrapper

level_1_mod = modifiers.get_modifier(table_id, 1, archetype_column)
level_50_mod = modifiers.get_modifier(table_id, 50, archetype_column)

# Level 50 should have higher magnitude (more negative = more damage)
assert abs(level_50_mod) > abs(level_1_mod)
```

**Test 4: Ones Table (No Scaling)**
```python
# Melee_Ones should return 1.0 for all ATs and levels
table_id = "Melee_Ones"

for level in [1, 25, 50]:
    for archetype in range(10):  # Test first 10 ATs
        mod = modifiers.get_modifier(table_id, level, archetype)
        assert abs(mod - 1.0) < 0.001
```

**Test 5: Invalid Inputs**
```python
# Test bounds checking
invalid_cases = [
    ("Melee_Damage", -1, 0),    # Negative level
    ("Melee_Damage", 0, -1),    # Negative column
    ("Melee_Damage", 100, 0),   # Level too high
    ("Melee_Damage", 50, 999),  # Column too high
    ("NonExistent", 50, 0),     # Invalid table
]

for table_id, level, column in invalid_cases:
    result = modifiers.get_modifier(table_id, level, column)
    assert result == 0.0 or result is None  # Define error behavior
```

**Test 6: Effect Magnitude Calculation**
```python
# Full effect calculation with modifier
effect_data = {
    "magnitude": 10.0,
    "scale": 1.0,
    "modifier_table": "Melee_Damage"
}

# Scrapper at level 50
modifier = -9.1
expected_damage = 1.0 * 10.0 * (-9.1) = -91.0  # Negative = damage

damage = calculate_effect_magnitude(effect_data, modifier)
assert abs(damage - expected_damage) < 0.01
```

### Validation Strategy

1. **Data Integrity**:
   - Load `AttribMod.json` and verify structure
   - Confirm 102 tables exist (Homecoming)
   - Verify each table has 55 rows
   - Verify consistent column count (should match archetype count)

2. **Known Power Comparison**:
   - Pick well-known power (e.g., "Brawl", "Health")
   - Calculate damage/effect for multiple ATs
   - Compare to MidsReborn's displayed values
   - Account for any other modifiers (Scale, base magnitude)

3. **AT Scaling Relationships**:
   - Verify Scrapper > Tanker for melee damage
   - Verify Defender > Scrapper for buffs/debuffs
   - Verify Controller > Defender for control duration
   - These relationships should hold across powers

4. **Cross-Reference with Game Data**:
   - If possible, get actual in-game combat logs
   - Verify calculated damage matches game output
   - Account for other factors (resistances, defenses, random rolls)

---

## References

### Related Calculation Specs
- **Spec 01**: Power Effects Core - Uses modifiers for all effect calculations
- **Spec 02**: Power Damage - Primary use case for damage modifiers
- **Spec 03**: Power Buffs/Debuffs - Uses buff/debuff modifiers
- **Spec 04**: Power Control Effects - Uses control modifiers
- **Spec 05**: Power Healing - Uses heal modifiers
- **Spec 17**: Archetype Caps - Complementary to modifiers (caps vs scaling)

### MidsReborn Code References
- `Core/Modifiers.cs` - Complete implementation
- `Core/DatabaseAPI.cs` - `GetModifier()` methods
- `Core/Base/Data_Classes/Effect.cs` - ModifierTable property
- `Data/Homecoming/AttribMod.json` - 102 modifier tables with actual values

### External Resources
- City of Heroes Wiki - Archetype AT modifiers
- Homecoming Forums - AT balance discussions
- Paragon Wiki (archive) - Historical modifier information

---

**Document Status**: ✅ Breadth Complete - Ready for implementation
**Implementation Priority**: **CRITICAL** - Required for correct power calculations
**Next Steps**:
1. Implement `ArchetypeModifiers` class in Python
2. Load and validate `AttribMod.json` data
3. Integration with Effect calculation system
4. Test against known power values from MidsReborn
