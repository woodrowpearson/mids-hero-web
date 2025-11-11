# Level Scaling

## Overview

- **Purpose**: Scales power effectiveness based on character level and applies Purple Patch level difference mechanics between attacker and target
- **Used By**: All power calculations (damage, ToHit, defense, resistance), combat effectiveness, level-based modifier table lookups
- **Complexity**: Medium-High
- **Priority**: Medium
- **Status**: 🟡 Breadth Complete

**Why This Matters**: City of Heroes has two major level scaling systems: (1) Power effectiveness scales with character level via modifier tables with breakpoints at certain levels, and (2) The "Purple Patch" system modifies ToHit chance, damage, and debuff effectiveness based on level difference between attacker and target. Higher-level enemies are harder to hit and take less damage, while lower-level enemies are easier to defeat.

---

## MidsReborn Implementation

### Primary Location

**Modifier Table Lookup**:
- **File**: `Core/DatabaseAPI.cs`
- **Methods**:
  - `GetModifier(IEffect iEffect)` - Main entry point for level-based scaling (lines 2947-2968)
  - `GetModifier(int iClass, int iTable, int iLevel)` - Core lookup with level parameter (lines 2970-2985)
- **Key Logic**:
  - Uses `MidsContext.MathLevelBase` as the default calculation level (constant = 49, zero-based = level 50)
  - Looks up modifier from 2D table indexed by [level][archetype]
  - Level parameter is zero-based (0-54 for character levels 1-55)

**Level Constants**:
- **File**: `Core/Base/Master_Classes/MidsContext.cs`
- **Constants**:
  - `MathLevelBase = 49` - Default level for calculations (line 21)
  - `MathLevelExemp = -1` - Exemplar level marker (line 22)

**Modifier Tables**:
- **File**: `Core/Modifiers.cs`
- **Class**: `Modifiers` and `ModifierTable`
- **Structure**: 2D array `Table[level][archetype]` with 55 levels × 60+ archetypes
- **Data Files**: `Data/Homecoming/AttribMod.json`, `Data/Rebirth/AttribMod.json`

### Level Shift Integration

**Incarnate Level Shifts**:
- **File**: `Core/GroupedFx.cs`
- **Effect Type**: `Enums.eEffectType.LevelShift` (lines 2001-2005)
- **Logic**:
  ```csharp
  case Enums.eEffectType.LevelShift:
      rankedEffect.Name = "LvlShift";
      rankedEffect.Value = $"{(effectSource.Mag > 0 ? "+" : "")}{effectSource.Mag:##0.##}";
  ```
- **Magnitude**: +1 to +3 level shift from Alpha/Lore/Destiny slots
- **Effect**: Increases effective combat level for Purple Patch calculations

### Effect Scaling Application

**Base Magnitude Calculation**:
- **File**: `Core/Base/Data_Classes/Effect.cs`
- **Property**: `Scale` (line 622) - Per-effect scale multiplier
- **Method**: Effect magnitude calculation (lines 407-412):
  ```csharp
  Enums.eAttribType.Magnitude => Scale * nMagnitude * DatabaseAPI.GetModifier(this)
  ```
- **Flow**: `base_magnitude × scale × level_modifier = final_magnitude`

**IgnoreScaling Flag**:
- **File**: `Core/Base/Data_Classes/Effect.cs`, `Core/IEffect.cs`
- **Property**: `IgnoreScaling` (boolean)
- **Purpose**: Some effects bypass level scaling (set bonuses, temp powers, etc.)
- **Usage**: Found in 20+ files including power effect editors, totals calculations

---

## Game Mechanics Context

### Power Scaling by Level

**Modifier Table System**:
- Each effect has an associated modifier table (e.g., "Melee_Damage", "Ranged_Buff_Def")
- Tables have 55 rows (levels 1-55) and ~60 columns (one per archetype/class)
- Values scale differently based on power type and archetype
- **Example**: Melee damage at level 1 might be -10.0, level 25 might be -8.5, level 50 might be -10.0 (negative values are normalized internally)

**Breakpoints**:
- Most scaling is NOT linear - there are specific breakpoints where values change
- Common breakpoints: levels 10, 20, 30, 40, 50
- Early levels (1-20): Powers often have reduced effectiveness
- Mid levels (20-40): Gradual improvement
- Cap levels (41-50): Maximum base effectiveness
- Incarnate levels (50+): Additional scaling through level shifts

**Historical Context**:
- Originally designed to prevent low-level characters from being too powerful
- Ensures high-level content remains challenging
- Balances power acquisition across the leveling experience
- Level 50 became the "standard" for calculations (MathLevelBase = 49 zero-indexed)

### Purple Patch System

**Name Origin**: Named after purple-colored con levels (enemies +4 levels or higher appear purple)

**Core Mechanics**:
1. **ToHit Modification**: Level difference affects base ToHit chance
   - Fighting +3 enemies: ToHit penalty (~-30% final ToHit)
   - Fighting -3 enemies: ToHit bonus (~+30% final ToHit)
   - Formula applies exponential curve, not linear

2. **Damage Scaling**: Damage dealt/received scales with level difference
   - Fighting +4 enemies: Deal ~48% damage
   - Fighting -4 enemies: Deal ~200% damage
   - Caps prevent extreme scaling (minimum ~48%, maximum ~200%)

3. **Debuff Effectiveness**: Debuffs on higher-level targets have reduced magnitude
   - Defense debuffs against +3 enemies: ~65% effectiveness
   - Resistance debuffs against +5 enemies: ~48% effectiveness
   - Buffs on allies are NOT affected (only hostile debuffs)

**Level Difference Ranges**:
- `-5 to -1`: Enemies below your level (easier)
- `0`: Even level
- `+1 to +4`: Enemies above your level (harder)
- `+5 and higher`: Extreme penalties (purple/red con)

**Incarnate Interaction**:
- Level shifts from Alpha/Lore/Destiny affect effective level for Purple Patch
- A level 50+3 character fighting a level 54 enemy = effective +1 difference (not +4)
- This is CRITICAL for Incarnate content (level 54 enemies are standard in trials)

### Enhancement Effectiveness by Level

**Training/Dual Origin/Single Origin Enhancements**:
- These scale with level (level 25 SO ≠ level 50 SO)
- MidsReborn primarily calculates at level 50 where SOs give ~33% boost
- Lower levels have proportionally weaker enhancement values

**Invention Origin Enhancements**:
- IOs have fixed effectiveness based on crafting level
- Level 50 common IOs give ~42.4% boost (better than SOs)
- Level 25 IOs give ~25.5% boost
- Set IOs also have level-dependent values
- Attuned IOs scale with character level dynamically

### Level Floor Effects

**Minimum Values**:
- Powers maintain minimum effectiveness even at low levels
- Prevents powers from becoming completely useless at level 1
- Example: A level 50 power slotted at level 10 still does reasonable damage
- MidsReborn generally assumes level 50 calculations, so floor effects are less prominent

**Known Quirks**:
1. **Base Level 50 Assumption**: MidsReborn uses `MathLevelBase = 49` (level 50 zero-indexed) for all calculations by default
2. **Exemplar Mode**: `MathLevelExemp = -1` exists but limited implementation for exemplaring down
3. **Table Index 0 Warning**: `GetModifier()` has comment: "calling this method with iTable == 0 can lead to super weird return values"
4. **Pet Scaling**: Pets may use different level scaling based on summoning power level
5. **Temp Power Scaling**: Temporary powers often have `IgnoreScaling = true`

---

## Python Implementation Notes

### Proposed Architecture

```python
from dataclasses import dataclass
from enum import IntEnum
from typing import Optional

@dataclass
class LevelScalingConfig:
    """Configuration for level-based calculations."""
    base_level: int = 50  # Default calculation level
    use_level_shifts: bool = True  # Include Incarnate shifts
    apply_purple_patch: bool = False  # Apply level difference modifiers
    target_level: Optional[int] = None  # Target enemy level for Purple Patch


class CombatLevel:
    """Represents effective combat level including shifts."""

    def __init__(self, base_level: int, level_shift: int = 0):
        self.base_level = base_level
        self.level_shift = level_shift

    @property
    def effective_level(self) -> int:
        """Effective level including shifts (capped at 55)."""
        return min(55, self.base_level + self.level_shift)

    @property
    def modifier_table_index(self) -> int:
        """Zero-based index for modifier table lookup."""
        return self.effective_level - 1


@dataclass
class PurplePatchModifiers:
    """Purple Patch scaling factors for level difference."""
    tohit_modifier: float  # Additive ToHit bonus/penalty
    damage_scale: float  # Multiplicative damage modifier
    debuff_scale: float  # Multiplicative debuff effectiveness

    @classmethod
    def for_level_difference(cls, level_diff: int) -> "PurplePatchModifiers":
        """
        Calculate Purple Patch modifiers for given level difference.

        Args:
            level_diff: Target level - attacker level (positive = higher enemy)

        Returns:
            PurplePatchModifiers with ToHit/damage/debuff scaling
        """
        # Placeholder formulas - need actual Purple Patch curves from game data
        # These are approximations based on known mechanics

        # ToHit penalty/bonus (~10% per level difference)
        tohit_mod = -0.10 * level_diff

        # Damage scaling (exponential curve with floor at 48%, cap at 200%)
        if level_diff >= 0:
            # Fighting higher level: reduced damage
            damage = max(0.48, 1.0 - (0.13 * level_diff))
        else:
            # Fighting lower level: increased damage
            damage = min(2.0, 1.0 + (0.25 * abs(level_diff)))

        # Debuff effectiveness (similar to damage scaling)
        debuff = max(0.48, 1.0 - (0.13 * max(0, level_diff)))

        return cls(
            tohit_modifier=tohit_mod,
            damage_scale=damage,
            debuff_scale=debuff
        )


class LevelScalingCalculator:
    """Handles all level-based scaling calculations."""

    def __init__(self, modifier_tables: dict[str, list[list[float]]]):
        """
        Initialize with loaded modifier tables.

        Args:
            modifier_tables: Dict mapping table names to 2D arrays [level][archetype]
        """
        self.modifier_tables = modifier_tables

    def get_modifier(
        self,
        table_name: str,
        archetype_column: int,
        level: int
    ) -> float:
        """
        Look up level-based modifier from tables.

        Args:
            table_name: Modifier table name (e.g., "Melee_Damage")
            archetype_column: Column index for archetype
            level: Character level (1-55)

        Returns:
            Modifier value for this level/archetype combination
        """
        if table_name not in self.modifier_tables:
            return 1.0  # Default if table not found

        table = self.modifier_tables[table_name]
        level_index = level - 1  # Convert to zero-based

        # Bounds checking
        if level_index < 0 or level_index >= len(table):
            return 1.0
        if archetype_column < 0 or archetype_column >= len(table[level_index]):
            return 1.0

        return table[level_index][archetype_column]

    def apply_purple_patch(
        self,
        base_value: float,
        attacker_level: CombatLevel,
        target_level: int,
        value_type: str = "damage"
    ) -> float:
        """
        Apply Purple Patch scaling to a value.

        Args:
            base_value: Unmodified value (damage, ToHit, debuff magnitude)
            attacker_level: Attacker's effective combat level
            target_level: Target's level
            value_type: Type of value ("damage", "tohit", "debuff")

        Returns:
            Modified value after Purple Patch scaling
        """
        level_diff = target_level - attacker_level.effective_level
        modifiers = PurplePatchModifiers.for_level_difference(level_diff)

        if value_type == "damage":
            return base_value * modifiers.damage_scale
        elif value_type == "tohit":
            return base_value + modifiers.tohit_modifier
        elif value_type == "debuff":
            return base_value * modifiers.debuff_scale
        else:
            return base_value

    def scale_effect_magnitude(
        self,
        base_magnitude: float,
        scale: float,
        modifier_table: str,
        archetype_column: int,
        level: int,
        ignore_scaling: bool = False
    ) -> float:
        """
        Calculate final effect magnitude with level scaling.

        Args:
            base_magnitude: Effect's base nMagnitude value
            scale: Effect's Scale multiplier
            modifier_table: Name of modifier table to use
            archetype_column: Archetype column index
            level: Character level
            ignore_scaling: If True, skip modifier table lookup

        Returns:
            Final scaled magnitude
        """
        if ignore_scaling:
            return base_magnitude * scale

        modifier = self.get_modifier(modifier_table, archetype_column, level)
        return base_magnitude * scale * modifier
```

### Key Functions

1. **`CombatLevel` class**: Encapsulates base level + level shifts
   - `effective_level` property: Total level including shifts (capped at 55)
   - `modifier_table_index` property: Zero-based index for table lookups

2. **`PurplePatchModifiers` dataclass**: Holds ToHit/damage/debuff modifiers
   - `for_level_difference()` factory: Calculates modifiers from level delta
   - Separate scaling for ToHit (additive), damage (multiplicative), debuffs (multiplicative)

3. **`LevelScalingCalculator.get_modifier()`**: Core table lookup
   - Input: table name, archetype column, level (1-55)
   - Output: Modifier value (typically negative float like -10.0)
   - Bounds checking with safe defaults (1.0 if out of range)

4. **`LevelScalingCalculator.apply_purple_patch()`**: Purple Patch scaling
   - Input: base value, attacker/target levels, value type
   - Output: Scaled value after level difference modifiers
   - Different formulas for damage vs ToHit vs debuffs

5. **`LevelScalingCalculator.scale_effect_magnitude()`**: Full effect scaling
   - Combines base magnitude, Scale property, and modifier table lookup
   - Respects `IgnoreScaling` flag
   - This is the main method called by power effect calculations

### Data Model

**Modifier Tables** (loaded from AttribMod.json):
```python
{
    "Melee_Damage": [
        # Level 1 (index 0): [Tank, Scrapper, Blaster, ...]
        [-10.0, -9.1, -9.1, ...],
        # Level 2 (index 1):
        [-10.7345, -9.7201, -9.7201, ...],
        ...
        # Level 55 (index 54):
        [...]
    ],
    "Ranged_Buff_Def": [...],
    ...
}
```

**Level Shift Sources** (from Spec 29 - Incarnate Alpha Shifts):
- Alpha slot T3/T4: +1 level shift
- Lore slot unlock: +1 level shift
- Destiny slot unlock: +1 level shift
- Maximum total: +3 level shifts

### Integration Points

1. **Power Effect Calculations** (Specs 01-09):
   - Call `scale_effect_magnitude()` for every effect with level-dependent scaling
   - Pass effect's `ModifierTable` name, archetype, and calculation level

2. **Archetype Modifiers** (Spec 16):
   - Level scaling USES archetype modifiers (they're the same system)
   - Each archetype has a column index in modifier tables
   - Level scaling is just the vertical (level) dimension of the same tables

3. **Incarnate Alpha Shifts** (Spec 29):
   - Alpha slot effects include `EffectType.LevelShift` with magnitude
   - Sum all level shift magnitudes to get total shift (cap at +3)
   - Use `CombatLevel` class to track base + shift

4. **Build Totals** (Specs 19-24):
   - All totals are calculated at a specific level (default 50)
   - Level shifts affect caps and effective combat level
   - Purple Patch NOT typically applied to totals (those are self-buffs)

5. **Combat Calculations** (Spec 28):
   - Purple Patch applied to ToHit chance vs enemy level
   - Purple Patch applied to damage output vs enemy level
   - Purple Patch applied to debuffs on enemies

### Dependencies

**Required Data Structures**:
- `modifier_tables`: Dict of 2D arrays loaded from AttribMod.json
- `archetype.column`: Archetype's column index in tables
- `effect.modifier_table`: Table name for each effect
- `effect.scale`: Scale multiplier for each effect
- `effect.ignore_scaling`: Flag to bypass scaling

**Related Calculations**:
- Enhancement Diversification (Spec 10): Applied before level scaling
- Archetype Caps (Spec 17): Capped after level scaling
- Incarnate Shifts (Spec 29): Modify effective level for scaling
- Purple Patch formulas: Need game data for exact curves (use approximations for breadth)

---

## Notes for Milestone 3 (Depth Implementation)

**Deep Implementation Tasks**:
1. **Exact Purple Patch Formulas**: Research and implement precise ToHit/damage/debuff curves from game data or community documentation
2. **Exemplar Scaling**: Implement level reduction mechanics (reverse scaling when exemplared down)
3. **Enhancement Level Scaling**: Integrate IO level-dependent effectiveness (currently assumes level 50)
4. **Pet Level Scaling**: Handle pets summoned at power level vs character level
5. **PvP Purple Patch Differences**: PvP may use different curves than PvE
6. **Level Shift Interaction Testing**: Verify exact interaction between level shifts and modifier table lookups
7. **Minimum/Maximum Clamping**: Document and implement any hard floors/ceilings on scaled values
8. **Breakpoint Tables**: Create detailed documentation of all level breakpoints in modifier tables

**Testing Requirements**:
- Unit tests for `get_modifier()` with bounds checking
- Unit tests for Purple Patch formulas at known level differences (-4 to +4)
- Integration tests with archetype modifier system (same underlying tables)
- Validation against MidsReborn output for level 50 vs level 1 power effectiveness
- Edge cases: level shifts pushing above level 55, negative level indices

**Known Limitations**:
- MidsReborn defaults to level 50 calculations (breadth implementation will do same)
- Exact Purple Patch curves may require reverse engineering from game client
- Exemplar mode is minimally implemented in MidsReborn (`MathLevelExemp = -1`)
- Some effects may have special scaling rules not captured in modifier tables

---

**Status**: 🟡 Breadth Complete - High-level algorithm and data structures documented, exact Purple Patch formulas deferred to Milestone 3.
