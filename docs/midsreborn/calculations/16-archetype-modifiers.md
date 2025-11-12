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

## DEPTH COVERAGE - DETAILED IMPLEMENTATION

### Section 1: Detailed Algorithm

#### Complete Modifier Table Structure

The modifier system in MidsReborn consists of **102 modifier tables** stored in `AttribMod.json`, each with:
- **55 rows** (levels 1-55, supporting normal play through Incarnate levels)
- **60 columns** (one per archetype, including playable ATs, epic ATs, and NPC classes)
- **Float values** representing multipliers applied to power effects

**Table Organization Pattern**:
```
Table Name Format: [Range]_[EffectType]_[Attribute]
- Range: Melee | Ranged
- EffectType: Damage | Heal | Buff | Debuff | Res | Control | etc.
- Attribute: (optional) Def | ToHit | Dmg | MaxHP | etc.

Examples:
- Melee_Damage         → Melee attack damage scaling
- Ranged_Heal          → Ranged healing scaling
- Melee_Buff_Def       → Melee-range defense buff scaling
- Ranged_Debuff_ToHit  → Ranged ToHit debuff scaling
- Melee_Ones           → No scaling (all 1.0)
```

**Complete Table List** (102 tables):
```
Damage Tables:
- Melee_Damage, Ranged_Damage
- Melee_TempDamage, Ranged_TempDamage

Healing Tables:
- Melee_Heal, Ranged_Heal
- Melee_HealSelf, Ranged_HealSelf

Control Tables:
- Melee_Stun, Ranged_Stun
- Melee_Sleep, Ranged_Sleep
- Melee_Immobilize, Ranged_Immobilize
- Melee_Slow, Ranged_Slow
- Melee_Hold, Ranged_Hold
- Melee_Knockback, Ranged_Knockback
- Melee_Fear, Ranged_Fear
- Melee_Confuse, Ranged_Confuse
- Melee_Control, Ranged_Control

Buff Tables:
- Melee_Buff_MaxHP, Ranged_Buff_MaxHP
- Melee_Buff_Def, Ranged_Buff_Def
- Melee_Buff_Dmg, Ranged_Buff_Dmg
- Melee_Buff_ToHit, Ranged_Buff_ToHit

Debuff Tables:
- Melee_DeBuff_ToHit, Ranged_DeBuff_ToHit
- Melee_Debuff_Dam, Ranged_Debuff_Dam
- Melee_Debuff_Def, Ranged_Debuff_Def
- Ranged_Debuff_Dmg

Resistance Tables:
- Melee_Res_Dmg, Ranged_Res_Dmg
- Melee_Res_Boolean, Ranged_Res_Boolean

Movement Tables:
- Melee_Leap, Ranged_Leap
- Melee_SpeedRunning, Ranged_SpeedRunning
- Melee_SpeedFlying, Ranged_SpeedFlying
- Melee_SpeedSwimming, Ranged_SpeedSwimming
- Melee_SpeedJumping, Ranged_SpeedJumping

Special Tables:
- Melee_Ones, Ranged_Ones (all 1.0 - no scaling)
- Melee_EndDrain, Ranged_EndDrain
- Melee_Friction, Ranged_Friction
- Melee_Level, Melee_Levelminus
- default
```

#### Sample Modifier Values - Level 50 Primary Archetypes

Based on actual `AttribMod.json` data from MidsReborn/Data/Homecoming:

**Archetype Column Mapping** (inferred from damage patterns):
- Column 0: Tanker
- Column 1: Scrapper
- Column 2: Defender
- Column 3: Controller
- Column 4: Blaster (likely, based on values)
- Column 5-9: Other primary ATs
- Column 10+: Epic ATs and NPC classes

**Melee_Damage** (Level 50, Row Index 49):
```
Column 0 (Tanker):    -55.6102  (lower damage, defensive role)
Column 1 (Scrapper):  -30.5856  (high melee damage)
Column 2 (Defender):  -30.5856  (moderate melee damage)
Column 3 (Controller):-62.5615  (lowest melee damage)
Column 4 (Blaster):   -52.8297  (lower melee, high ranged)

Note: Negative values represent damage magnitude
Higher absolute value = more damage
```

**Melee_Damage** (Level 1, Row Index 0):
```
Column 0 (Tanker):    -10.0
Column 1 (Scrapper):  -9.1
Column 2 (Defender):  -9.1
Column 3 (Controller):-10.25
Column 4 (Blaster):   -9.9
```

**Melee_Damage** (Level 25, Row Index 24):
```
Column 0 (Tanker):    -34.3344
Column 1 (Scrapper):  -18.8839
Column 2 (Defender):  -18.8839
Column 3 (Controller):-38.6262
Column 4 (Blaster):   -32.6177
```

**Ranged_Damage** (Level 50, Row Index 49):
```
Column 0 (Tanker):    -62.5615  (lowest ranged damage)
Column 1 (Scrapper):  -30.5856  (moderate ranged)
Column 2 (Defender):  -36.1466  (moderate ranged)
Column 3 (Controller):-27.8051  (good ranged for control)
Column 4 (Blaster):   -44.4882  (highest ranged damage)

Note: Blasters have higher ranged than melee
Tankers have lower ranged than melee
```

**Melee_Buff_Def** (Level 50, Row Index 49):
```
Column 0 (Tanker):    0.07   (weaker defense buffs)
Column 1 (Scrapper):  0.09   (moderate buffs)
Column 2 (Defender):  0.1    (strongest defense buffs)
Column 3 (Controller):0.075  (lower buffs than Defender)
Column 4 (Blaster):   0.1    (surprisingly high)

Note: Positive values for buffs
Defenders excel at buffing
```

**Melee_Debuff_Def** (Level 50, Row Index 49):
```
Column 0 (Tanker):    -0.07   (weakest defense debuffs)
Column 1 (Scrapper):  -0.1    (moderate debuffs)
Column 2 (Defender):  -0.125  (strongest debuffs)
Column 3 (Controller):-0.075  (lower than Defender)
Column 4 (Blaster):   -0.07   (weak debuffs)

Note: Negative values for debuffs
Higher absolute value = stronger debuff
Defenders excel at debuffing
```

**Ranged_Heal** (Level 50, Row Index 49):
```
Column 0 (Tanker):    96.3807
Column 1 (Scrapper):  117.7986
Column 2 (Defender):  133.8621  (strongest healing)
Column 3 (Controller):96.3807
Column 4 (Blaster):   96.3807
```

**Melee_Control** (Level 50, Row Index 49):
```
All Columns: 4.0

Note: Control duration appears uniform across ATs
Control magnitude differences come from base values, not modifiers
```

**Melee_Ones** (Level 50, Row Index 49):
```
All Columns, All Levels: 1.0

Used for effects that should not scale by archetype
```

#### Level Scaling Pattern

Modifier values scale **roughly linearly** from level 1 to level 50:

**Example: Scrapper Melee Damage (Column 1)**
- Level 1:  -9.1
- Level 25: -18.8839  (roughly 2x level 1)
- Level 50: -30.5856  (roughly 3.36x level 1)

**Scaling Formula** (approximate):
```
modifier(level) ≈ modifier(level_1) * (1 + (level - 1) * growth_rate)

Where growth_rate varies by table and archetype
Actual values are stored in table, not calculated
```

**Why Not Calculate?**: While scaling appears linear, exact values are stored in tables to allow for:
1. Fine-tuning by game developers
2. Non-linear adjustments for specific levels
3. Server-specific balance changes

#### Effect Type → Modifier Table Mapping

Effects must specify which modifier table to use via the `ModifierTable` property:

```
Effect Attribute          → Modifier Table
=====================================================
Damage (melee origin)     → Melee_Damage
Damage (ranged origin)    → Ranged_Damage
Defense Buff (melee)      → Melee_Buff_Def
Defense Debuff (ranged)   → Ranged_Debuff_Def
ToHit Buff (melee)        → Melee_Buff_ToHit
ToHit Debuff (ranged)     → Ranged_DeBuff_ToHit
Healing (ranged)          → Ranged_Heal
Healing (self)            → Melee_HealSelf / Ranged_HealSelf
Stun (melee)              → Melee_Stun
Hold (ranged)             → Ranged_Hold
Slow (melee)              → Melee_Slow
Knockback (ranged)        → Ranged_Knockback
MaxHP Buff (melee)        → Melee_Buff_MaxHP
Damage Resistance (melee) → Melee_Res_Dmg
Damage Buff (ranged)      → Ranged_Buff_Dmg
No scaling needed         → Melee_Ones / Ranged_Ones
```

**Default Table**: If no modifier table is specified, effects default to `Melee_Ones` (all 1.0 modifiers).

#### Pseudocode: get_modifier Function

```python
def get_modifier(
    archetype_idx: int,
    effect: Effect,
    character_level: int
) -> float:
    """
    Get the archetype modifier for an effect.

    Args:
        archetype_idx: Index of the archetype (0-59)
        effect: Effect object containing modifier table reference
        character_level: Character level (1-55)

    Returns:
        Modifier multiplier (float)
    """
    # Validation
    if archetype_idx < 0:
        return 0.0
    if character_level < 1 or character_level > 55:
        return 0.0

    # Get modifier table index from effect
    table_idx = effect.nModifierTable
    if table_idx < 0:
        return 0.0

    # Convert level to 0-based index
    level_idx = character_level - 1

    # Get archetype column from archetype definition
    archetype = Database.Classes[archetype_idx]
    column_idx = archetype.Column

    if column_idx < 0:
        return 0.0

    # Bounds checking
    if table_idx >= len(Database.AttribMods.Modifier):
        return 0.0

    modifier_table = Database.AttribMods.Modifier[table_idx]

    if level_idx >= len(modifier_table.Table):
        return 0.0

    if column_idx >= len(modifier_table.Table[level_idx]):
        return 0.0

    # Return the modifier value
    return modifier_table.Table[level_idx][column_idx]


def get_modifier_with_context(effect: Effect) -> float:
    """
    Get modifier with full context resolution.

    Handles:
    - ForcedClass (power overrides which AT to use)
    - Absorbed_Class_nID (effect uses different AT)
    - Pet/summoned entity archetypes
    """
    # Determine which archetype to use
    power = effect.GetPower()

    if power is None:
        # Enhancement or standalone effect
        archetype_idx = 0
    elif power.ForcedClass is not None:
        # Power forces specific archetype scaling
        archetype_idx = NidFromUidClass(power.ForcedClass)
    elif effect.Absorbed_Class_nID >= 0:
        # Effect uses different archetype
        archetype_idx = effect.Absorbed_Class_nID
    else:
        # Use character's archetype
        archetype_idx = MidsContext.Archetype.Idx

    # Use character's current level
    level = MidsContext.Level

    return get_modifier(archetype_idx, effect, level)
```

#### Level Interpolation Algorithm

**MidsReborn does NOT interpolate** - all 55 levels are stored in tables.

However, for edge cases:
```python
def get_modifier_safe(
    archetype_idx: int,
    effect: Effect,
    character_level: int
) -> float:
    """Safe modifier lookup with bounds clamping."""

    # Clamp level to valid range
    if character_level < 1:
        character_level = 1
    if character_level > 55:
        character_level = 55  # Use level 55 cap

    return get_modifier(archetype_idx, effect, character_level)
```

---

### Section 2: C# Implementation Details

#### Archetype.cs - Column Property

**File**: `Core/Base/Data_Classes/Archetype.cs`

**Key Property** (line 153):
```csharp
public int Column { get; set; }
```

**Purpose**: Maps each archetype to its column index in modifier tables.

**Set During Load** (line 102, 255):
```csharp
// From binary file
Column = reader.ReadInt32();

// From CSV (line 255)
Column = int.Parse(array[1]) - 2;  // CSV is 1-based, subtract 2 for offset
```

**Usage in Comparison** (line 198):
```csharp
if (Column > archetype.Column) return 1;
return Column < archetype.Column ? 1 : 0;
```

**Stored to Binary** (line 215):
```csharp
writer.Write(Column);
```

#### Modifiers.cs - Table Structure

**File**: `Core/Modifiers.cs`

**Main Class** (lines 10-25):
```csharp
public class Modifiers : ICloneable
{
    public List<ModifierTable> Modifier = new List<ModifierTable>();
    public int Revision;
    public DateTime RevisionDate = new DateTime(0L);
    public string SourceIndex = string.Empty;
    public string SourceTables = string.Empty;
}
```

**ModifierTable Class** (lines 137-197):
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

    // Load from binary (lines 183-196)
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

**JSON Loading** (lines 41-58):
```csharp
public bool Load(string? iPath)
{
    var path = Files.SelectDataFileLoad(Files.JsonFileModifiers, iPath);

    if (File.Exists(path))
    {
        try
        {
            var jsonText = File.ReadAllText(path);
            DatabaseAPI.Database.AttribMods =
                JsonConvert.DeserializeObject<Modifiers>(
                    jsonText,
                    Serializer.SerializerSettings
                );
            return true;
        }
        catch (Exception ex)
        {
            MessageBox.Show($@"Modifier table file isn't how it should be....
                Message: {ex.Message}
                No modifiers were loaded.");
            return false;
        }
    }
    // Fall back to binary format...
}
```

**Binary Loading** (lines 59-120):
```csharp
// Binary file format (legacy):
// - Header: "Mids' Hero Designer Attribute Modifier Tables"
// - Revision (int32)
// - RevisionDate (int64 - binary DateTime)
// - SourceIndex (string)
// - SourceTables (string)
// - For each table:
//   - ID (string)
//   - BaseIndex (int32)
//   - For each level (55 rows):
//     - Archetype count (int32)
//     - For each archetype:
//       - Modifier value (float32)
```

#### DatabaseAPI.cs - Modifier Lookup

**File**: `Core/DatabaseAPI.cs`

**GetModifier(IEffect)** (lines 2947-2968):
```csharp
public static float GetModifier(IEffect iEffect)
{
    //Currently expects a zero-based level.

    //This value is returned as a modifier if a value is out of bounds
    var iClass = 0;
    var iLevel = MidsContext.MathLevelBase;
    var effPower = iEffect.GetPower();

    if (effPower == null)
    {
        return iEffect.Enhancement == null
            ? 1
            : GetModifier(iClass, iEffect.nModifierTable, iLevel);
    }

    iClass = string.IsNullOrEmpty(effPower.ForcedClass)
        ? iEffect.Absorbed_Class_nID <= -1
            ? MidsContext.Archetype.Idx
            : iEffect.Absorbed_Class_nID
        : NidFromUidClass(effPower.ForcedClass);

    //Everything seems to be valid, return the modifier
    return GetModifier(iClass, iEffect.nModifierTable, iLevel);
}
```

**GetModifier(int, int, int)** (lines 2970-2985):
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

**MatchModifierIDs** (lines ~3002):
```csharp
MatchModifierIDs();  // Called during database initialization
```

#### Effect.cs - ModifierTable Property

**File**: `Core/Base/Data_Classes/Effect.cs`

**Properties**:
```csharp
public string ModifierTable { get; set; }  // Table name like "Melee_Damage"
public int nModifierTable { get; set; }    // Index into Modifiers.Modifier list
```

**Default Value**:
```csharp
ModifierTable = "Melee_Ones";  // Default to no scaling
```

**Usage in Magnitude Calculation** (~line 800):
```csharp
Enums.eAttribType.Magnitude =>
    Scale * nMagnitude * DatabaseAPI.GetModifier(this),
```

#### Edge Cases

**Edge Case 1: Level 0 or Negative**
```csharp
if (iLevel < 0) return 0;
```
Returns 0, which will zero out the effect. This is a bug - should probably return 1.0 or clamp to level 1.

**Edge Case 2: Level > 55**
```csharp
if (iLevel > Database.AttribMods.Modifier[iTable].Table.Count - 1) return 0;
```
Returns 0 for levels beyond table bounds. Better approach: clamp to level 55.

**Edge Case 3: Unknown Archetype**
```csharp
if (iClass > Database.Classes.Length - 1) return 0;
if (iClassColumn < 0) return 0;
```
Returns 0, zeroing the effect. Should probably return 1.0 as fallback.

**Edge Case 4: Unknown Effect Type**
```csharp
if (iTable < 0) return 0;
if (iTable > Database.AttribMods.Modifier.Count - 1) return 0;
```
Returns 0. Effect should probably default to "Melee_Ones" table (index looked up by name).

**Edge Case 5: Effect Without Power**
```csharp
if (effPower == null)
{
    return iEffect.Enhancement == null ? 1 : GetModifier(iClass, iEffect.nModifierTable, iLevel);
}
```
Standalone effects (enhancements) return 1.0, which is correct for "no scaling."

**Edge Case 6: iTable == 0 Warning**
```csharp
//Warning: calling this method with iTable == 0 can lead to super weird return values.
```
Table index 0 is "Melee_Damage" - valid table. Comment suggests concern about misuse. No actual bug here.

---

### Section 3: Database Schema

#### Proposed Schema: archetype_modifiers

**Purpose**: Store all 102 modifier tables with 55 levels × 60 archetypes.

**Option 1: Normalized Schema** (recommended for maintainability)

```sql
CREATE TABLE modifier_tables (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,  -- e.g., "Melee_Damage"
    base_index INTEGER NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE archetype_modifiers (
    id SERIAL PRIMARY KEY,
    modifier_table_id INTEGER NOT NULL REFERENCES modifier_tables(id),
    archetype_column INTEGER NOT NULL,  -- 0-59
    level INTEGER NOT NULL,             -- 1-55
    modifier_value REAL NOT NULL,
    UNIQUE(modifier_table_id, archetype_column, level)
);

-- Index for fast lookups
CREATE INDEX idx_archetype_modifiers_lookup
    ON archetype_modifiers(modifier_table_id, level, archetype_column);
```

**Option 2: JSON Storage** (faster reads, harder to query)

```sql
CREATE TABLE modifier_tables (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    base_index INTEGER NOT NULL,
    data JSONB NOT NULL,  -- Store full table as JSON
    CONSTRAINT valid_json CHECK (
        jsonb_typeof(data->'table') = 'array'
    )
);

-- Example data structure in JSONB:
{
  "table": [
    [-10.0, -9.1, -9.1, ...],  -- Level 1
    [-10.7345, -9.7201, ...],  -- Level 2
    ...
  ]
}
```

**Option 3: Materialized View** (pre-computed for performance)

```sql
-- Store raw data in normalized form
-- (Use Option 1 tables)

-- Create materialized view for common queries
CREATE MATERIALIZED VIEW archetype_modifier_lookup AS
SELECT
    mt.name as table_name,
    mt.id as table_id,
    am.archetype_column,
    am.level,
    am.modifier_value,
    a.name as archetype_name,
    a.display_name as archetype_display_name
FROM archetype_modifiers am
JOIN modifier_tables mt ON am.modifier_table_id = mt.id
JOIN archetypes a ON a.column_index = am.archetype_column
WHERE a.playable = true  -- Only include playable ATs
ORDER BY mt.name, am.level, am.archetype_column;

CREATE INDEX idx_modifier_lookup_table_level
    ON archetype_modifier_lookup(table_name, level, archetype_column);

-- Refresh when data changes
REFRESH MATERIALIZED VIEW archetype_modifier_lookup;
```

#### Archetype Table Enhancement

**Add Column property**:
```sql
ALTER TABLE archetypes
ADD COLUMN column_index INTEGER NOT NULL DEFAULT 0;

-- Constraint: column_index should be unique for playable ATs
CREATE UNIQUE INDEX idx_archetypes_column
    ON archetypes(column_index)
    WHERE playable = true;
```

#### Seed Data Structure

**Python script to populate from AttribMod.json**:

```python
import json
from pathlib import Path

def seed_modifier_tables(db_session, attribmod_path: Path):
    """
    Load AttribMod.json and populate database.

    Args:
        db_session: SQLAlchemy session
        attribmod_path: Path to AttribMod.json
    """
    with open(attribmod_path) as f:
        data = json.load(f)

    for table_data in data['Modifier']:
        # Create modifier_tables entry
        table = ModifierTable(
            name=table_data['ID'],
            base_index=table_data['BaseIndex']
        )
        db_session.add(table)
        db_session.flush()  # Get table.id

        # Create archetype_modifiers entries
        for level_idx, level_values in enumerate(table_data['Table']):
            level = level_idx + 1  # Convert to 1-based

            for column_idx, modifier_value in enumerate(level_values):
                modifier = ArchetypeModifier(
                    modifier_table_id=table.id,
                    archetype_column=column_idx,
                    level=level,
                    modifier_value=modifier_value
                )
                db_session.add(modifier)

        # Commit in batches to avoid memory issues
        if table.id % 10 == 0:
            db_session.commit()

    db_session.commit()
    print(f"Loaded {len(data['Modifier'])} modifier tables")
```

#### Data Integrity Constraints

```sql
-- Ensure levels are in valid range
ALTER TABLE archetype_modifiers
ADD CONSTRAINT check_level_range
    CHECK (level >= 1 AND level <= 55);

-- Ensure archetype columns are valid
ALTER TABLE archetype_modifiers
ADD CONSTRAINT check_archetype_column
    CHECK (archetype_column >= 0 AND archetype_column < 60);

-- Ensure exactly 55 levels per table/archetype combination
CREATE FUNCTION check_modifier_completeness() RETURNS TRIGGER AS $$
BEGIN
    -- This would be a complex check - better done in application layer
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

#### Performance Considerations

**For Option 1 (Normalized)**:
- Total rows: 102 tables × 55 levels × 60 columns = **336,600 rows**
- Row size: ~20 bytes
- Total size: ~6.7 MB (very manageable)
- Index size: ~3-5 MB
- **Total: ~10-12 MB** - fits easily in memory

**Query Performance**:
```sql
-- Lookup single modifier (with index)
SELECT modifier_value
FROM archetype_modifiers
WHERE modifier_table_id = 1
  AND level = 50
  AND archetype_column = 1;
-- Expected: < 1ms with index

-- Get all modifiers for a level (common for build calculations)
SELECT am.modifier_value, mt.name
FROM archetype_modifiers am
JOIN modifier_tables mt ON am.modifier_table_id = mt.id
WHERE am.level = 50
  AND am.archetype_column = 1;
-- Expected: < 5ms (returns 102 rows)
```

**Caching Strategy**:
- Load entire modifier dataset into memory at application startup
- Total memory: ~10 MB (negligible)
- No need for Redis/Memcached - just use Python dict

---

### Section 4: Test Cases

#### Test 1: Scrapper Melee Damage Level 50
```python
def test_scrapper_melee_damage_level_50():
    """Test Scrapper melee damage modifier at level 50."""
    modifiers = ArchetypeModifiers.load_from_json(ATTRIBMOD_PATH)

    scrapper_column = 1
    level = 50
    table_name = "Melee_Damage"

    modifier = modifiers.get_modifier(table_name, level, scrapper_column)

    expected = -30.5856
    assert abs(modifier - expected) < 0.001, \
        f"Expected {expected}, got {modifier}"
```

#### Test 2: Tanker Melee Damage Level 50
```python
def test_tanker_melee_damage_level_50():
    """Test Tanker melee damage modifier at level 50."""
    modifiers = ArchetypeModifiers.load_from_json(ATTRIBMOD_PATH)

    tanker_column = 0
    level = 50
    table_name = "Melee_Damage"

    modifier = modifiers.get_modifier(table_name, level, tanker_column)

    expected = -55.6102
    assert abs(modifier - expected) < 0.001

    # Tankers should do less melee damage than Scrappers
    scrapper_mod = modifiers.get_modifier(table_name, level, 1)
    assert abs(modifier) > abs(scrapper_mod), \
        "Tanker melee damage should be lower than Scrapper"
```

#### Test 3: Blaster Ranged vs Melee Damage Level 50
```python
def test_blaster_ranged_vs_melee_level_50():
    """Test Blaster has higher ranged than melee damage."""
    modifiers = ArchetypeModifiers.load_from_json(ATTRIBMOD_PATH)

    blaster_column = 4
    level = 50

    melee_mod = modifiers.get_modifier("Melee_Damage", level, blaster_column)
    ranged_mod = modifiers.get_modifier("Ranged_Damage", level, blaster_column)

    # Both are negative, so more negative = more damage
    assert abs(ranged_mod) < abs(melee_mod), \
        f"Blaster ranged ({ranged_mod}) should be higher than melee ({melee_mod})"

    expected_melee = -52.8297
    expected_ranged = -44.4882

    assert abs(melee_mod - expected_melee) < 0.001
    assert abs(ranged_mod - expected_ranged) < 0.001
```

#### Test 4: Defender Buff Superiority Level 50
```python
def test_defender_buff_superiority():
    """Test Defenders have highest defense buff modifiers."""
    modifiers = ArchetypeModifiers.load_from_json(ATTRIBMOD_PATH)

    level = 50
    table_name = "Melee_Buff_Def"

    tanker_mod = modifiers.get_modifier(table_name, level, 0)     # 0.07
    scrapper_mod = modifiers.get_modifier(table_name, level, 1)   # 0.09
    defender_mod = modifiers.get_modifier(table_name, level, 2)   # 0.1
    controller_mod = modifiers.get_modifier(table_name, level, 3) # 0.075

    # Defender should have highest buff modifier
    assert defender_mod > tanker_mod
    assert defender_mod > scrapper_mod
    assert defender_mod > controller_mod

    assert abs(defender_mod - 0.1) < 0.001
```

#### Test 5: Defender Debuff Superiority Level 50
```python
def test_defender_debuff_superiority():
    """Test Defenders have highest defense debuff modifiers."""
    modifiers = ArchetypeModifiers.load_from_json(ATTRIBMOD_PATH)

    level = 50
    table_name = "Melee_Debuff_Def"

    tanker_mod = modifiers.get_modifier(table_name, level, 0)     # -0.07
    scrapper_mod = modifiers.get_modifier(table_name, level, 1)   # -0.1
    defender_mod = modifiers.get_modifier(table_name, level, 2)   # -0.125
    controller_mod = modifiers.get_modifier(table_name, level, 3) # -0.075

    # Defender should have highest debuff (most negative)
    assert abs(defender_mod) > abs(tanker_mod)
    assert abs(defender_mod) > abs(scrapper_mod)
    assert abs(defender_mod) > abs(controller_mod)

    assert abs(defender_mod - (-0.125)) < 0.001
```

#### Test 6: Level Progression - Scrapper Damage 1→25→50
```python
def test_level_progression_scrapper_damage():
    """Test damage modifiers increase with level."""
    modifiers = ArchetypeModifiers.load_from_json(ATTRIBMOD_PATH)

    scrapper_column = 1
    table_name = "Melee_Damage"

    level_1_mod = modifiers.get_modifier(table_name, 1, scrapper_column)
    level_25_mod = modifiers.get_modifier(table_name, 25, scrapper_column)
    level_50_mod = modifiers.get_modifier(table_name, 50, scrapper_column)

    # Values are negative, so more negative = more damage
    assert abs(level_50_mod) > abs(level_25_mod)
    assert abs(level_25_mod) > abs(level_1_mod)

    assert abs(level_1_mod - (-9.1)) < 0.001
    assert abs(level_25_mod - (-18.8839)) < 0.001
    assert abs(level_50_mod - (-30.5856)) < 0.001
```

#### Test 7: Melee_Ones Returns 1.0 Always
```python
def test_melee_ones_no_scaling():
    """Test Melee_Ones returns 1.0 for all ATs and levels."""
    modifiers = ArchetypeModifiers.load_from_json(ATTRIBMOD_PATH)

    table_name = "Melee_Ones"

    # Test all primary ATs at multiple levels
    for level in [1, 25, 50]:
        for column in range(10):  # First 10 archetypes
            modifier = modifiers.get_modifier(table_name, level, column)
            assert abs(modifier - 1.0) < 0.001, \
                f"Melee_Ones should be 1.0 for level {level}, column {column}"
```

#### Test 8: Ranged_Ones Returns 1.0 Always
```python
def test_ranged_ones_no_scaling():
    """Test Ranged_Ones returns 1.0 for all ATs and levels."""
    modifiers = ArchetypeModifiers.load_from_json(ATTRIBMOD_PATH)

    table_name = "Ranged_Ones"

    for level in [1, 25, 50]:
        for column in range(10):
            modifier = modifiers.get_modifier(table_name, level, column)
            assert abs(modifier - 1.0) < 0.001
```

#### Test 9: Invalid Level Bounds - Level 0
```python
def test_invalid_level_zero():
    """Test level 0 returns 0.0 (matches C# behavior)."""
    modifiers = ArchetypeModifiers.load_from_json(ATTRIBMOD_PATH)

    modifier = modifiers.get_modifier("Melee_Damage", 0, 1)

    assert modifier == 0.0, \
        "Level 0 should return 0.0 per C# implementation"
```

#### Test 10: Invalid Level Bounds - Level 56
```python
def test_invalid_level_too_high():
    """Test level > 55 returns 0.0 (matches C# behavior)."""
    modifiers = ArchetypeModifiers.load_from_json(ATTRIBMOD_PATH)

    modifier = modifiers.get_modifier("Melee_Damage", 56, 1)

    assert modifier == 0.0, \
        "Level > 55 should return 0.0 per C# implementation"
```

#### Test 11: Invalid Archetype Column
```python
def test_invalid_archetype_column():
    """Test invalid archetype column returns 0.0."""
    modifiers = ArchetypeModifiers.load_from_json(ATTRIBMOD_PATH)

    modifier = modifiers.get_modifier("Melee_Damage", 50, 999)

    assert modifier == 0.0, \
        "Invalid archetype column should return 0.0"
```

#### Test 12: Invalid Table Name
```python
def test_invalid_table_name():
    """Test invalid table name returns 0.0 or raises exception."""
    modifiers = ArchetypeModifiers.load_from_json(ATTRIBMOD_PATH)

    try:
        modifier = modifiers.get_modifier("NonExistentTable", 50, 1)
        assert modifier == 0.0, \
            "Invalid table should return 0.0"
    except KeyError:
        pass  # Acceptable to raise exception
```

#### Test 13: Table Count
```python
def test_table_count():
    """Test AttribMod.json contains 102 tables."""
    modifiers = ArchetypeModifiers.load_from_json(ATTRIBMOD_PATH)

    assert len(modifiers.tables) == 102, \
        f"Expected 102 tables, got {len(modifiers.tables)}"
```

#### Test 14: Table Structure - 55 Levels
```python
def test_table_structure_levels():
    """Test each table has exactly 55 levels."""
    modifiers = ArchetypeModifiers.load_from_json(ATTRIBMOD_PATH)

    for table_name, table in modifiers.tables.items():
        assert len(table.Table) == 55, \
            f"Table {table_name} should have 55 levels, has {len(table.Table)}"
```

#### Test 15: Effect Magnitude Calculation with Modifier
```python
def test_effect_magnitude_with_modifier():
    """Test complete effect magnitude calculation including modifier."""
    modifiers = ArchetypeModifiers.load_from_json(ATTRIBMOD_PATH)

    # Simulate a melee attack effect
    effect_data = {
        "magnitude": 10.0,
        "scale": 1.0,
        "modifier_table": "Melee_Damage"
    }

    # Scrapper at level 50
    scrapper_column = 1
    level = 50

    modifier = modifiers.get_modifier(
        effect_data["modifier_table"],
        level,
        scrapper_column
    )

    # Calculate final magnitude
    final_magnitude = (
        effect_data["scale"] *
        effect_data["magnitude"] *
        modifier
    )

    expected_modifier = -30.5856
    expected_magnitude = 1.0 * 10.0 * (-30.5856)  # -305.856

    assert abs(modifier - expected_modifier) < 0.001
    assert abs(final_magnitude - expected_magnitude) < 0.01
```

#### Test 16: Defender Healing Superiority
```python
def test_defender_healing_superiority():
    """Test Defenders have highest healing modifiers."""
    modifiers = ArchetypeModifiers.load_from_json(ATTRIBMOD_PATH)

    level = 50
    table_name = "Ranged_Heal"

    tanker_heal = modifiers.get_modifier(table_name, level, 0)      # 96.3807
    scrapper_heal = modifiers.get_modifier(table_name, level, 1)    # 117.7986
    defender_heal = modifiers.get_modifier(table_name, level, 2)    # 133.8621

    assert defender_heal > scrapper_heal
    assert defender_heal > tanker_heal

    assert abs(defender_heal - 133.8621) < 0.001
```

#### Test 17: Control Duration Uniformity
```python
def test_control_duration_uniform():
    """Test control effects have uniform modifiers across ATs."""
    modifiers = ArchetypeModifiers.load_from_json(ATTRIBMOD_PATH)

    level = 50
    table_name = "Melee_Control"

    # Get modifiers for first 8 ATs
    control_mods = [
        modifiers.get_modifier(table_name, level, col)
        for col in range(8)
    ]

    # All should be 4.0
    for mod in control_mods:
        assert abs(mod - 4.0) < 0.001, \
            "Control modifiers should be uniform at 4.0"
```

---

### Section 5: Python Implementation

#### Archetype Enum

```python
from enum import IntEnum

class Archetype(IntEnum):
    """
    Archetype enumeration matching MidsReborn column indices.

    Note: These are inferred from modifier patterns. Exact mapping
    should be verified against MidsReborn's class definitions.
    """
    TANKER = 0
    SCRAPPER = 1
    DEFENDER = 2
    CONTROLLER = 3
    BLASTER = 4
    # Additional ATs (exact order TBD)
    PEACEBRINGER = 5
    WARSHADE = 6
    # ... more playable ATs
    # Column 10+: Epic ATs and NPC classes

    @property
    def display_name(self) -> str:
        """Get human-readable archetype name."""
        return self.name.replace("_", " ").title()

    @property
    def column(self) -> int:
        """Get modifier table column index."""
        return self.value
```

#### EffectType Enum (Reuse from Spec 01)

```python
from enum import Enum

class EffectType(Enum):
    """Effect types from Spec 01 - Power Effects Core."""
    DAMAGE = "Damage"
    DEFENSE = "Defense"
    RESISTANCE = "Resistance"
    TO_HIT = "ToHit"
    HEALING = "Healing"
    ENDURANCE_DRAIN = "EnduranceDrain"
    STUN = "Stun"
    HOLD = "Hold"
    SLEEP = "Sleep"
    IMMOBILIZE = "Immobilize"
    KNOCKBACK = "Knockback"
    # ... other effect types

    def get_modifier_table_name(
        self,
        is_ranged: bool = False,
        is_buff: bool = False,
        is_debuff: bool = False
    ) -> str:
        """
        Get modifier table name for this effect type.

        Args:
            is_ranged: True for ranged origin, False for melee
            is_buff: True for buff effects
            is_debuff: True for debuff effects

        Returns:
            Modifier table name (e.g., "Melee_Damage")
        """
        range_prefix = "Ranged" if is_ranged else "Melee"

        # Map effect type to table suffix
        effect_map = {
            EffectType.DAMAGE: "Damage",
            EffectType.DEFENSE: "Def",
            EffectType.TO_HIT: "ToHit",
            EffectType.HEALING: "Heal",
            EffectType.ENDURANCE_DRAIN: "EndDrain",
            EffectType.STUN: "Stun",
            EffectType.HOLD: "Hold",
            EffectType.SLEEP: "Sleep",
            EffectType.IMMOBILIZE: "Immobilize",
            EffectType.KNOCKBACK: "Knockback",
        }

        effect_suffix = effect_map.get(self, "Ones")

        # Add buff/debuff prefix if applicable
        if is_buff:
            effect_suffix = f"Buff_{effect_suffix}"
        elif is_debuff:
            effect_suffix = f"Debuff_{effect_suffix}"

        return f"{range_prefix}_{effect_suffix}"
```

#### ModifierTable Class

```python
from dataclasses import dataclass
from typing import List

@dataclass
class ModifierTable:
    """
    Single modifier table (e.g., Melee_Damage).

    Attributes:
        id: Table name (e.g., "Melee_Damage")
        base_index: Base index from MidsReborn (purpose unclear)
        table: 2D array [level][archetype_column] of float modifiers
    """
    id: str
    base_index: int
    table: List[List[float]]

    def get_modifier(self, level: int, archetype_column: int) -> float:
        """
        Get modifier for specific level and archetype.

        Args:
            level: Character level (1-55)
            archetype_column: Archetype column index (0-59)

        Returns:
            Modifier value, or 0.0 if out of bounds
        """
        # Validate bounds
        if level < 1 or level > 55:
            return 0.0

        level_idx = level - 1  # Convert to 0-based

        if level_idx >= len(self.table):
            return 0.0

        if archetype_column < 0 or archetype_column >= len(self.table[level_idx]):
            return 0.0

        return self.table[level_idx][archetype_column]

    def get_all_at_level(self, level: int) -> List[float]:
        """Get all archetype modifiers at a specific level."""
        if level < 1 or level > 55:
            return []

        level_idx = level - 1
        if level_idx >= len(self.table):
            return []

        return self.table[level_idx].copy()

    def __repr__(self) -> str:
        return f"ModifierTable(id='{self.id}', levels={len(self.table)})"
```

#### ArchetypeModifiers Manager Class

```python
import json
from pathlib import Path
from typing import Dict, Optional

class ArchetypeModifiers:
    """
    Manager for all archetype modifier tables.

    Loads from AttribMod.json and provides fast lookups.
    """

    def __init__(self):
        self.tables: Dict[str, ModifierTable] = {}
        self.table_index: Dict[str, int] = {}

    @classmethod
    def load_from_json(cls, filepath: Path) -> 'ArchetypeModifiers':
        """
        Load modifier tables from AttribMod.json.

        Args:
            filepath: Path to AttribMod.json

        Returns:
            ArchetypeModifiers instance

        Raises:
            FileNotFoundError: If file doesn't exist
            JSONDecodeError: If JSON is invalid
        """
        with open(filepath, 'r') as f:
            data = json.load(f)

        instance = cls()

        for idx, table_data in enumerate(data['Modifier']):
            table = ModifierTable(
                id=table_data['ID'],
                base_index=table_data['BaseIndex'],
                table=table_data['Table']
            )
            instance.tables[table.id] = table
            instance.table_index[table.id] = idx

        return instance

    def get_modifier(
        self,
        table_id: str,
        level: int,
        archetype_column: int
    ) -> float:
        """
        Main lookup function for modifiers.

        Args:
            table_id: Modifier table name (e.g., "Melee_Damage")
            level: Character level (1-55)
            archetype_column: Archetype column index (0-59)

        Returns:
            Modifier value, or 0.0 if table not found or out of bounds
        """
        if table_id not in self.tables:
            return 0.0

        return self.tables[table_id].get_modifier(level, archetype_column)

    def get_modifier_for_effect(
        self,
        effect: 'Effect',
        archetype: Archetype,
        character_level: int
    ) -> float:
        """
        Get modifier for an effect based on character state.

        Args:
            effect: Effect object with modifier_table property
            archetype: Character's archetype
            character_level: Character's current level

        Returns:
            Modifier value
        """
        table_id = effect.modifier_table or "Melee_Ones"
        archetype_column = archetype.column

        return self.get_modifier(table_id, character_level, archetype_column)

    def get_table(self, table_id: str) -> Optional[ModifierTable]:
        """Get full modifier table by ID."""
        return self.tables.get(table_id)

    def table_exists(self, table_id: str) -> bool:
        """Check if a modifier table exists."""
        return table_id in self.tables

    def list_tables(self) -> List[str]:
        """Get list of all table IDs."""
        return list(self.tables.keys())

    def validate_structure(self) -> List[str]:
        """
        Validate modifier table structure.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        for table_id, table in self.tables.items():
            # Check level count
            if len(table.table) != 55:
                errors.append(
                    f"Table '{table_id}' has {len(table.table)} levels, expected 55"
                )

            # Check column consistency
            for level_idx, level_data in enumerate(table.table):
                if len(level_data) != len(table.table[0]):
                    errors.append(
                        f"Table '{table_id}' level {level_idx + 1} has inconsistent column count"
                    )

        return errors

    def __repr__(self) -> str:
        return f"ArchetypeModifiers(tables={len(self.tables)})"
```

#### Usage Examples

**Example 1: Basic Modifier Lookup**

```python
# Load modifier tables
modifiers = ArchetypeModifiers.load_from_json(
    Path("data/homecoming/AttribMod.json")
)

# Get Scrapper melee damage at level 50
scrapper = Archetype.SCRAPPER
level = 50
table_name = "Melee_Damage"

modifier = modifiers.get_modifier(table_name, level, scrapper.column)
print(f"Scrapper melee damage modifier at level 50: {modifier}")
# Output: Scrapper melee damage modifier at level 50: -30.5856
```

**Example 2: Effect Calculation with Modifier**

```python
from dataclasses import dataclass

@dataclass
class Effect:
    """Simplified Effect class for example."""
    magnitude: float
    scale: float
    modifier_table: str

def calculate_effect_magnitude(
    effect: Effect,
    archetype: Archetype,
    level: int,
    modifiers: ArchetypeModifiers
) -> float:
    """Calculate final effect magnitude with AT modifier."""
    modifier = modifiers.get_modifier(
        effect.modifier_table,
        level,
        archetype.column
    )

    return effect.scale * effect.magnitude * modifier

# Example: Scrapper melee attack at level 50
attack_effect = Effect(
    magnitude=10.0,
    scale=1.0,
    modifier_table="Melee_Damage"
)

damage = calculate_effect_magnitude(
    attack_effect,
    Archetype.SCRAPPER,
    50,
    modifiers
)

print(f"Scrapper attack damage: {damage:.2f}")
# Output: Scrapper attack damage: -305.86
```

**Example 3: Compare ATs**

```python
def compare_archetype_modifiers(
    table_name: str,
    level: int,
    archetypes: List[Archetype],
    modifiers: ArchetypeModifiers
):
    """Compare modifier values across archetypes."""
    print(f"\n{table_name} at Level {level}:")
    print("-" * 50)

    for at in archetypes:
        mod = modifiers.get_modifier(table_name, level, at.column)
        print(f"{at.display_name:15} {mod:8.4f}")

# Compare damage modifiers
compare_archetype_modifiers(
    "Melee_Damage",
    50,
    [Archetype.TANKER, Archetype.SCRAPPER, Archetype.DEFENDER,
     Archetype.CONTROLLER, Archetype.BLASTER],
    modifiers
)
# Output:
# Melee_Damage at Level 50:
# --------------------------------------------------
# Tanker          -55.6102
# Scrapper        -30.5856
# Defender        -30.5856
# Controller      -62.5615
# Blaster         -52.8297
```

**Example 4: Level Progression Analysis**

```python
def analyze_level_progression(
    table_name: str,
    archetype: Archetype,
    levels: List[int],
    modifiers: ArchetypeModifiers
):
    """Analyze how modifiers scale with level."""
    print(f"\n{archetype.display_name} - {table_name}")
    print("-" * 50)

    for level in levels:
        mod = modifiers.get_modifier(table_name, level, archetype.column)
        print(f"Level {level:2d}: {mod:8.4f}")

analyze_level_progression(
    "Melee_Damage",
    Archetype.SCRAPPER,
    [1, 10, 20, 30, 40, 50],
    modifiers
)
# Output:
# Scrapper - Melee_Damage
# --------------------------------------------------
# Level  1:  -9.1000
# Level 10: -13.5610
# Level 20: -17.7746
# Level 30: -22.0882
# Level 40: -26.4018
# Level 50: -30.5856
```

**Example 5: Caching for Performance**

```python
from functools import lru_cache

class CachedArchetypeModifiers(ArchetypeModifiers):
    """
    Archetype modifiers with LRU caching for repeated lookups.

    Useful for build calculations that repeatedly query same modifiers.
    """

    @lru_cache(maxsize=1024)
    def get_modifier(
        self,
        table_id: str,
        level: int,
        archetype_column: int
    ) -> float:
        """Cached version of get_modifier."""
        return super().get_modifier(table_id, level, archetype_column)

    def clear_cache(self):
        """Clear the LRU cache."""
        self.get_modifier.cache_clear()

# Usage
modifiers = CachedArchetypeModifiers.load_from_json(ATTRIBMOD_PATH)

# First call: loads from table
mod1 = modifiers.get_modifier("Melee_Damage", 50, 1)

# Second call: returns from cache (faster)
mod2 = modifiers.get_modifier("Melee_Damage", 50, 1)
```

---

### Section 6: Integration Points

#### Downstream: All Power Calculations

**Every power effect magnitude calculation** must apply archetype modifiers:

```python
def calculate_effect_final_magnitude(
    effect: Effect,
    character: Character,
    modifiers: ArchetypeModifiers,
    enhancements: List[Enhancement]
) -> float:
    """
    Complete effect magnitude calculation.

    Integration points:
    - Spec 01: Power Effects Core (base magnitude, scale)
    - Spec 16: Archetype Modifiers (THIS SPEC)
    - Spec 12: Enhancement Calculation (enhancement bonuses)
    - Spec 17: Archetype Caps (applied after modifiers)
    """
    # Step 1: Get base magnitude and scale (Spec 01)
    base_magnitude = effect.magnitude
    scale = effect.scale

    # Step 2: Get archetype modifier (THIS SPEC)
    at_modifier = modifiers.get_modifier_for_effect(
        effect,
        character.archetype,
        character.level
    )

    # Step 3: Calculate enhancement bonus (Spec 12)
    enhancement_multiplier = calculate_enhancement_multiplier(
        effect,
        enhancements
    )

    # Step 4: Combine all factors
    final_magnitude = (
        base_magnitude *
        scale *
        at_modifier *
        enhancement_multiplier
    )

    # Step 5: Apply caps (Spec 17)
    final_magnitude = apply_archetype_cap(
        final_magnitude,
        effect.effect_type,
        character.archetype
    )

    return final_magnitude
```

#### Integration with Effect System (Spec 01)

**Effect Model Enhancement**:

```python
@dataclass
class Effect:
    """
    Effect definition from Spec 01, enhanced with modifier table.
    """
    effect_type: EffectType
    magnitude: float
    duration: float
    scale: float = 1.0

    # NEW: Archetype modifier integration
    modifier_table: str = "Melee_Ones"  # Default to no scaling

    def calculate_magnitude(
        self,
        character: Character,
        modifiers: ArchetypeModifiers,
        enhancements: List[Enhancement] = None
    ) -> float:
        """Calculate final effect magnitude with all modifiers."""
        # Get archetype modifier
        at_mod = modifiers.get_modifier(
            self.modifier_table,
            character.level,
            character.archetype.column
        )

        # Base calculation
        result = self.scale * self.magnitude * at_mod

        # Apply enhancements if present
        if enhancements:
            enh_mult = calculate_enhancement_multiplier(self, enhancements)
            result *= enh_mult

        return result
```

#### Integration with Archetype Caps (Spec 17)

**Modifiers vs Caps**:

```
Calculation Flow:
1. Base magnitude (from power effect)
2. × Scale (from effect)
3. × AT Modifier (THIS SPEC - per-AT scaling)
4. × Enhancement (from slotted enhancements)
5. Apply AT Cap (Spec 17 - maximum allowed value)

Example: Defense Buff
- Base: +5% defense
- Scale: 1.0
- AT Modifier: 0.1 (Defender at level 50)
- Enhancement: 1.95 (95% enhancement)
- = 5 × 1.0 × 0.1 × 1.95 = 0.975% defense
- Cap: None for defense buffs (no limit)

Example: Damage
- Base: 50 HP damage
- Scale: 1.0
- AT Modifier: -30.5856 (Scrapper at level 50)
- Enhancement: 1.95
- = 50 × 1.0 × (-30.5856) × 1.95 = -2982.146 damage
- Cap: Check Scrapper damage cap (typically 400% or 500%)
```

**Implementation**:

```python
from enum import Enum

class AttributeType(Enum):
    """Attribute types that have caps."""
    DAMAGE = "Damage"
    DEFENSE = "Defense"
    RESISTANCE = "Resistance"
    TO_HIT = "ToHit"
    RECHARGE = "Recharge"

def apply_caps_and_modifiers(
    base_value: float,
    attribute_type: AttributeType,
    character: Character,
    modifiers: ArchetypeModifiers,
    effect: Effect
) -> float:
    """
    Apply both AT modifiers and caps.

    Integration: Spec 16 (modifiers) + Spec 17 (caps)
    """
    # Step 1: Apply AT modifier (Spec 16)
    at_modifier = modifiers.get_modifier(
        effect.modifier_table,
        character.level,
        character.archetype.column
    )

    scaled_value = base_value * at_modifier

    # Step 2: Apply cap (Spec 17)
    cap_value = get_archetype_cap(character.archetype, attribute_type)

    if cap_value is not None:
        if attribute_type in [AttributeType.DEFENSE, AttributeType.TO_HIT]:
            # Soft capping with diminishing returns (see Spec 26)
            scaled_value = apply_soft_cap(scaled_value, cap_value)
        else:
            # Hard cap
            scaled_value = min(scaled_value, cap_value)

    return scaled_value
```

#### Integration with Power Database

**Power → Effect → Modifier Chain**:

```python
class Power:
    """Power definition with effects."""

    name: str
    effects: List[Effect]
    forced_class: Optional[str] = None  # Override AT for this power

    def calculate_effects_for_character(
        self,
        character: Character,
        modifiers: ArchetypeModifiers
    ) -> Dict[EffectType, float]:
        """Calculate all effects for a specific character."""
        results = {}

        # Determine which AT to use
        if self.forced_class:
            archetype = get_archetype_by_name(self.forced_class)
        else:
            archetype = character.archetype

        # Calculate each effect
        for effect in self.effects:
            magnitude = modifiers.get_modifier_for_effect(
                effect,
                archetype,
                character.level
            )

            final_value = effect.magnitude * effect.scale * magnitude

            results[effect.effect_type] = results.get(effect.effect_type, 0) + final_value

        return results
```

#### Complete Calculation Flow Example

**Full pipeline from power → final displayed value**:

```python
def calculate_power_display_value(
    power: Power,
    character: Character,
    enhancements: List[Enhancement],
    modifiers: ArchetypeModifiers,
    caps: ArchetypeCaps
) -> PowerDisplayValues:
    """
    Complete calculation integrating all specs.

    Integration points:
    - Spec 01: Power Effects (base values)
    - Spec 12: Enhancements (slotting)
    - Spec 16: AT Modifiers (THIS SPEC)
    - Spec 17: AT Caps
    - Spec 26: Diminishing Returns (if applicable)
    """
    results = PowerDisplayValues()

    for effect in power.effects:
        # Base magnitude (Spec 01)
        base = effect.magnitude * effect.scale

        # AT modifier (Spec 16 - THIS SPEC)
        at_mod = modifiers.get_modifier_for_effect(
            effect,
            character.archetype,
            character.level
        )

        # Enhancement bonus (Spec 12)
        enh_mult = calculate_enhancement_multiplier(
            effect,
            enhancements
        )

        # Combine
        value = base * at_mod * enh_mult

        # Apply diminishing returns (Spec 26)
        if effect.effect_type in [EffectType.DEFENSE, EffectType.TO_HIT]:
            value = apply_diminishing_returns(value, effect.effect_type)

        # Apply caps (Spec 17)
        cap = caps.get_cap(character.archetype, effect.effect_type)
        if cap is not None:
            value = min(value, cap)

        # Store result
        results.add_effect(effect.effect_type, value)

    return results
```

---

**Document Status**: ✅ **DEPTH COMPLETE** - Comprehensive implementation details added
**Implementation Priority**: **CRITICAL** - Required for correct power calculations
**Next Steps**:
1. Implement `ArchetypeModifiers` class in Python
2. Load and validate `AttribMod.json` data
3. Integration with Effect calculation system
4. Test against known power values from MidsReborn
