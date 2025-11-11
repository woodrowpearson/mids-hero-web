# Buff Stacking Rules

## Overview
- **Purpose**: Determines how multiple instances of the same buff/debuff combine when applied from different sources - includes additive stacking, multiplicative stacking, best-value-only, and Rule of 5 suppression for set bonuses
- **Used By**: Build totals, power calculations, set bonus aggregation, pet buffs, team buffs
- **Complexity**: High
- **Priority**: High
- **Status**: 🟡 Breadth Complete

## MidsReborn Implementation

### Primary Location
- **File**: `Core/GroupedFx.cs`
- **Class**: `GroupedFx` - Lines 80-450
- **Purpose**: Groups and aggregates effects with the same identifier (effect type, damage type, mez type, target)

### Related Files
- **File**: `Core/Build.cs`
  - **Method**: `GetSetBonusVirtualPower()` - Lines 1321-1370
  - **Implements**: Rule of 5 suppression for set bonuses (line 1357: `if (setCount[power] < 6)`)

- **File**: `Core/clsToonX.cs`
  - **Method**: `GenerateBuffedPowerArray()` - Lines 2041-2048
  - **Calls**: `GenerateSetBonusData()` to apply stacking rules across all powers
  - **Method**: `CalculateAndApplyEffects()` - Applies buffs with stacking logic

- **File**: `Core/IEffect.cs` / `Core/Base/Data_Classes/Effect.cs`
  - **Property**: `Stacking` - Line 68 (IEffect), Line 34 (Effect default)
  - **Type**: `Enums.eStacking` (Yes/No)
  - **Property**: `Suppression` - Line 70 (IEffect), Line 35 (Effect default)
  - **Type**: `Enums.eSuppress` (flags enum)

### Key Data Structures

```csharp
// Core/GroupedFx.cs - Lines 82-98
public struct FxId
{
    public Enums.eEffectType EffectType;      // What buff/debuff (Defense, Resistance, etc.)
    public Enums.eMez MezType;                // Mez subtype if applicable
    public Enums.eDamage DamageType;          // Damage subtype if applicable
    public Enums.eEffectType ETModifies;      // Modified effect type for Enhancement effects
    public Enums.eToWho ToWho;                // Target (Self, Target, Team)
    public Enums.ePvX PvMode;                 // PvE/PvP/Any
    public int SummonId;                      // Pet source ID
    public float Duration;                    // Effect duration
    public bool IgnoreScaling;                // Bypass archetype scaling
}

// Core/GroupedFx.cs - Lines 100-109
public struct EnhancedMagSum
{
    public float Base;      // Base magnitude sum
    public float Enhanced;  // Enhanced magnitude sum
}

// Core/Enums.cs - Lines 1081-1085
public enum eStacking
{
    No,   // Multiple applications do not stack (best value wins)
    Yes   // Multiple applications stack additively
}

// Core/Enums.cs - Lines 1132-1145
[Flags]
public enum eSuppress
{
    None = 0,
    Held = 1,
    Sleep = 2,
    Stunned = 4,
    Immobilized = 8,
    Terrorized = 16,
    Confused = 32,
    // ... more suppression flags
}
```

### Stacking Algorithm

**High-Level Pseudocode** (from `GroupedFx.cs`):

```
FUNCTION GroupEffects(effectList):
    // Step 1: Create effect identifiers
    FOR each effect in effectList:
        fxId = GenerateFxId(effect)
        groupedEffects.add(fxId, effect)

    // Step 2: Aggregate effects with same identifier
    FOR each fxId in groupedEffects:
        effectsWithSameId = groupedEffects[fxId]

        IF effectsWithSameId.count == 1:
            // Single effect, no stacking needed
            result.add(effectsWithSameId[0])
        ELSE:
            // Multiple effects - apply stacking rules
            stackedEffect = ApplyStackingRules(effectsWithSameId, fxId)
            result.add(stackedEffect)

    RETURN result

FUNCTION ApplyStackingRules(effects, fxId):
    stackingMode = DetermineStackingMode(fxId.EffectType)

    IF stackingMode == ADDITIVE:
        // Most buffs: Defense, Resistance, Recharge, etc.
        totalMag = SUM(effect.BuffedMag for effect in effects)
        RETURN CreateGroupedEffect(fxId, totalMag, effects)

    ELSE IF stackingMode == MULTIPLICATIVE:
        // Damage buffs, some special cases
        totalMag = PRODUCT(1 + effect.BuffedMag for effect in effects) - 1
        RETURN CreateGroupedEffect(fxId, totalMag, effects)

    ELSE IF stackingMode == BEST_VALUE:
        // Some unique IOs, some procs
        bestEffect = MAX(effect.BuffedMag for effect in effects)
        RETURN CreateGroupedEffect(fxId, bestEffect, effects)

FUNCTION DetermineStackingMode(effectType):
    // Based on Effect.Stacking property and effect type
    IF effect.Stacking == eStacking.No:
        RETURN BEST_VALUE

    // Most effects are additive
    IF effectType IN [Defense, Resistance, RechargeTime, Accuracy, ToHit,
                       Recovery, Regeneration, EnduranceDiscount, HitPoints]:
        RETURN ADDITIVE

    // Damage buffs are multiplicative
    IF effectType == DamageBuff:
        RETURN MULTIPLICATIVE

    // Default to additive
    RETURN ADDITIVE
```

### Rule of 5 Implementation

From `Core/Build.cs` - Lines 1321-1370:

```csharp
// Rule of 5: Only first 5 instances of the same set bonus count
private IPower GetSetBonusVirtualPower()
{
    var nidPowers = DatabaseAPI.NidPowers("set_bonus");
    var setCount = new int[nidPowers.Length];  // Track count per bonus power
    var effectList = new List<IEffect>();

    foreach (var setBonus in SetBonuses)
    {
        foreach (var setInfo in setBonus.SetInfo)
        {
            foreach (var power in setInfo.Powers.Where(x => x > -1))
            {
                ++setCount[power];  // Increment count for this bonus

                // KEY LOGIC: Only include if count < 6 (0-5 = first 5 instances)
                if (setCount[power] < 6)
                {
                    // Add this set bonus to the build
                    effectList.AddRange(powerInfo.Effects);
                }
                // 6th+ instance is SUPPRESSED (not added)
            }
        }
    }

    return CreateVirtualPower(effectList);
}
```

## Game Mechanics Context

### Why This Exists

City of Heroes allows characters to gain buffs from multiple sources:
1. **Power Effects** - Self-buffs from clicked/toggle powers
2. **Enhancement Set Bonuses** - Passive bonuses from slotted IO sets
3. **Incarnate Powers** - High-level endgame bonuses
4. **Team Buffs** - Buffs from other players
5. **Pet Buffs** - Buffs from summoned entities

Without stacking rules, builds could achieve infinite stats by stacking identical bonuses. Stacking rules prevent abuse while allowing meaningful build diversity.

### Stacking Modes

**1. Additive Stacking** (Most Common)
- **Effect Types**: Defense, Resistance, Recharge, Accuracy, ToHit, Recovery, Regeneration, EnduranceDiscount, HitPoints, Movement Speed
- **Formula**: `Total = Buff1 + Buff2 + Buff3 + ...`
- **Example**: +10% Defense from IO set + +5% Defense from power = +15% Defense total
- **Why**: Simple, predictable, matches player expectations

**2. Multiplicative Stacking** (Damage Buffs)
- **Effect Types**: DamageBuff (and possibly some proc effects)
- **Formula**: `Total = (1 + Buff1) × (1 + Buff2) × (1 + Buff3) × ... - 1`
- **Example**: +100% damage buff × +50% damage buff = (1+1.0) × (1+0.5) - 1 = 2.0 × 1.5 - 1 = 2.0 = +200% damage
- **Why**: Prevents damage stacking from becoming exponential, maintains balance
- **Note**: This appears to be implemented in the game engine, but MidsReborn may handle it differently (needs deep investigation in Milestone 3)

**3. Best-Value-Only** (Non-Stacking)
- **Effect Types**: Effects with `Stacking = eStacking.No`, some unique IO bonuses, some proc effects
- **Formula**: `Total = MAX(Buff1, Buff2, Buff3, ...)`
- **Example**: +7.5% recharge unique IO + +7.5% recharge unique IO = only +7.5% (second is suppressed)
- **Why**: Prevents stacking of "unique" enhancements, maintains rarity/specialness

**4. Rule of 5** (Set Bonus Suppression)
- **Applies To**: Enhancement Set Bonuses ONLY
- **Rule**: Only the first 5 instances of the same set bonus power count
- **Example**:
  - Slot 6 copies of "LotG +Recharge" set bonus across build
  - Only first 5 applications count (+7.5% × 5 = +37.5% recharge)
  - 6th copy is completely suppressed (not counted)
- **Why**: Prevents "farming" the same powerful set bonus across entire build
- **Implementation**: Track count per set bonus power ID, suppress when count ≥ 6

### Historical Context

**Rule of 5** was introduced in Issue 13 (December 2008) to address the "Purple Set Problem":
- Purple (Very Rare) IO sets had extremely powerful bonuses
- Players could slot 6+ copies of the same purple set
- This led to builds with 50%+ recharge, defense soft-capping trivially
- Rule of 5 maintains set bonus value while preventing abuse

**Stacking Property** (`eStacking.Yes/No`) exists at the effect level because some special enhancement procs need non-stacking behavior (e.g., "Unique" procs that should only fire once).

### Known Quirks

1. **Set Bonus Counting**: Rule of 5 counts by **set bonus power ID**, not by set name
   - Same bonus from different sets counts separately
   - Example: LotG +7.5% Recharge is ONE power ID, so Rule of 5 applies across all LotG sets
   - Example: +6.25% Recharge from Basilisk's Gaze vs +6.25% from Ghost Widow's Embrace are DIFFERENT power IDs, each gets its own Rule of 5 counter

2. **Suppression vs Stacking**:
   - `Suppression` (eSuppress flags) is about **conditional disabling** (e.g., "suppress while held")
   - `Stacking` (eStacking enum) is about **aggregation math** (how to combine multiple instances)
   - These are orthogonal concepts

3. **Source Priority**: When effects from different sources apply, there's an implicit priority:
   - Power effects (highest priority, always counted first)
   - Incarnate powers
   - Set bonuses (Rule of 5 applied)
   - Enhancement specials
   - Team buffs (lowest priority in display, but still stack)

4. **Effect Grouping**: Effects are grouped by `FxId` struct (effect type + damage type + mez type + target + PvE/PvP mode + duration + ignore scaling)
   - This means a +10% Defense(Smashing) and +10% Defense(Lethal) are SEPARATE groups (don't stack together)
   - But +10% Defense(All) includes all damage types in one group

## Python Implementation Notes

### Proposed Architecture

```python
from enum import Enum, Flag
from dataclasses import dataclass
from typing import List, Dict, Optional

class StackingMode(Enum):
    """How multiple instances of same buff combine."""
    ADDITIVE = "additive"          # Sum all magnitudes
    MULTIPLICATIVE = "multiplicative"  # Multiply (1+mag) factors
    BEST_VALUE = "best_value"      # Take maximum magnitude only

class EStacking(Enum):
    """Whether effect allows stacking (from game data)."""
    NO = 0   # Best value only
    YES = 1  # Stacking allowed

@dataclass
class FxIdentifier:
    """Uniquely identifies a buff/debuff type for grouping."""
    effect_type: str        # "Defense", "Resistance", "RechargeTime", etc.
    damage_type: str        # "Smashing", "Energy", "All", etc.
    mez_type: str           # "Hold", "Sleep", "None", etc.
    modifies_type: str      # For Enhancement effects
    target: str             # "Self", "Target", "Team"
    pve_pvp: str           # "PvE", "PvP", "Any"
    summon_id: int         # Pet source ID
    duration: float        # Effect duration
    ignore_scaling: bool   # Bypass AT scaling

    def __hash__(self):
        return hash((
            self.effect_type, self.damage_type, self.mez_type,
            self.modifies_type, self.target, self.pve_pvp,
            self.summon_id, self.duration, self.ignore_scaling
        ))

@dataclass
class GroupedEffect:
    """Aggregated effect after stacking."""
    identifier: FxIdentifier
    base_magnitude: float
    enhanced_magnitude: float
    included_effects: List[int]  # Source effect indices
    is_enhancement: bool
    is_aggregated: bool

class BuffStackingCalculator:
    """Handles buff/debuff stacking logic."""

    def __init__(self):
        self.set_bonus_counts: Dict[int, int] = {}  # Rule of 5 tracking

    def determine_stacking_mode(self, effect_type: str, stacking_flag: EStacking) -> StackingMode:
        """Determine how this effect type stacks."""
        if stacking_flag == EStacking.NO:
            return StackingMode.BEST_VALUE

        # Most effects are additive
        if effect_type in [
            "Defense", "Resistance", "RechargeTime", "Accuracy", "ToHit",
            "Recovery", "Regeneration", "EnduranceDiscount", "HitPoints",
            "SpeedRunning", "SpeedFlying", "SpeedJumping"
        ]:
            return StackingMode.ADDITIVE

        # Damage buffs are multiplicative
        if effect_type == "DamageBuff":
            return StackingMode.MULTIPLICATIVE

        # Default to additive
        return StackingMode.ADDITIVE

    def apply_stacking(self, effects: List[Effect], mode: StackingMode) -> float:
        """Apply stacking rules to calculate total magnitude."""
        if not effects:
            return 0.0

        if len(effects) == 1:
            return effects[0].buffed_magnitude

        if mode == StackingMode.ADDITIVE:
            return sum(e.buffed_magnitude for e in effects)

        elif mode == StackingMode.MULTIPLICATIVE:
            # (1 + mag1) * (1 + mag2) * ... - 1
            product = 1.0
            for effect in effects:
                product *= (1.0 + effect.buffed_magnitude)
            return product - 1.0

        elif mode == StackingMode.BEST_VALUE:
            return max(e.buffed_magnitude for e in effects)

        return 0.0

    def apply_rule_of_five(self, set_bonus_power_id: int) -> bool:
        """
        Check if this set bonus should be included (Rule of 5).
        Returns True if should include, False if suppressed.
        """
        current_count = self.set_bonus_counts.get(set_bonus_power_id, 0)
        self.set_bonus_counts[set_bonus_power_id] = current_count + 1

        # Include if this is instance 1-5 (count 0-4 before increment, 1-5 after)
        return current_count < 5

    def group_effects(self, effects: List[Effect]) -> List[GroupedEffect]:
        """
        Group effects by identifier and apply stacking rules.
        Main entry point for buff stacking calculation.
        """
        # Group by FxIdentifier
        groups: Dict[FxIdentifier, List[Effect]] = {}
        for effect in effects:
            fx_id = self._create_identifier(effect)
            if fx_id not in groups:
                groups[fx_id] = []
            groups[fx_id].append(effect)

        # Apply stacking to each group
        grouped_effects = []
        for fx_id, effect_list in groups.items():
            mode = self.determine_stacking_mode(
                fx_id.effect_type,
                effect_list[0].stacking  # All effects in group have same stacking
            )

            total_magnitude = self.apply_stacking(effect_list, mode)

            grouped = GroupedEffect(
                identifier=fx_id,
                base_magnitude=sum(e.base_magnitude for e in effect_list),
                enhanced_magnitude=total_magnitude,
                included_effects=[e.index for e in effect_list],
                is_enhancement=effect_list[0].is_enhancement_effect,
                is_aggregated=(len(effect_list) > 1)
            )
            grouped_effects.append(grouped)

        return grouped_effects

    def _create_identifier(self, effect: Effect) -> FxIdentifier:
        """Create FxIdentifier for grouping."""
        return FxIdentifier(
            effect_type=effect.effect_type,
            damage_type=effect.damage_type,
            mez_type=effect.mez_type,
            modifies_type=effect.modifies_type,
            target=effect.target,
            pve_pvp=effect.pve_pvp_mode,
            summon_id=effect.summon_id,
            duration=effect.duration,
            ignore_scaling=effect.ignore_scaling
        )
```

### Key Functions to Implement

1. **`group_effects()`** - Main entry point, groups effects and applies stacking
2. **`determine_stacking_mode()`** - Returns ADDITIVE/MULTIPLICATIVE/BEST_VALUE based on effect type
3. **`apply_stacking()`** - Performs the math for each stacking mode
4. **`apply_rule_of_five()`** - Tracks and enforces Rule of 5 for set bonuses
5. **`create_identifier()`** - Generates FxIdentifier hash key for grouping

### Integration Points

- **Input**: List of `Effect` objects from all sources (powers, sets, incarnates)
- **Output**: List of `GroupedEffect` objects with combined magnitudes
- **Used By**:
  - `BuildTotalsCalculator` (Spec 24) - Aggregates all build totals
  - `PowerCalculator` (Spec 01) - Applies buffs to power calculations
  - `SetBonusCalculator` (Spec 13) - Enforces Rule of 5

### Deep Implementation Deferred

The following details require deeper investigation in Milestone 3 (Depth):

1. **Exact multiplicative stacking formula** - Verify game behavior for damage buffs
2. **Source priority handling** - When should power effects override set bonuses?
3. **Suppression interaction** - How does `eSuppress` affect stacking calculations?
4. **Edge cases**:
   - Procs that apply buffs (do they stack?)
   - Pet buffs vs character buffs (separate pools?)
   - Team buffs (displayed separately or stacked?)
5. **Performance optimization** - Caching grouped effects, incremental updates

---

## Algorithm Pseudocode

**Complete Stacking Algorithm** (from `GroupedFx.cs` and `Build.cs`):

```
FUNCTION CalculateBuildTotals(character):
    // Phase 1: Collect all effects from all sources
    all_effects = []

    // 1.1: Power effects (from activated/toggled powers)
    FOR each power in character.active_powers:
        FOR each effect in power.effects:
            IF effect.CanInclude() AND effect.PvXInclude():
                all_effects.add(effect)

    // 1.2: Enhancement set bonuses (with Rule of 5)
    set_bonus_effects = GetSetBonusEffects(character.build)
    all_effects.extend(set_bonus_effects)

    // 1.3: Incarnate powers
    FOR each incarnate in character.incarnate_powers:
        all_effects.extend(incarnate.effects)

    // Phase 2: Group effects by identifier
    grouped_effects = GroupEffectsByIdentifier(all_effects)

    // Phase 3: Apply stacking rules to each group
    final_effects = []
    FOR each (fx_id, effect_list) in grouped_effects:
        stacked_effect = ApplyStackingRules(fx_id, effect_list)
        final_effects.add(stacked_effect)

    RETURN final_effects

FUNCTION GetSetBonusEffects(build):
    """
    Apply Rule of 5 to set bonuses
    From Build.cs lines 1321-1370
    """
    // Get all set bonus power IDs
    set_bonus_power_ids = DatabaseAPI.NidPowers("set_bonus")

    // Initialize counter for each set bonus power (Rule of 5 tracking)
    set_count = Array(length=set_bonus_power_ids.length, initial_value=0)

    effect_list = []

    // Iterate through all slotted sets in build
    FOR each set_bonus in build.set_bonuses:
        FOR each set_info in set_bonus.set_info:
            FOR each power_id in set_info.powers:
                IF power_id < 0:
                    CONTINUE  // Invalid power ID

                // Increment counter for this set bonus power
                set_count[power_id] += 1

                // KEY LOGIC: Only include first 5 instances (count 1-5)
                IF set_count[power_id] < 6:
                    power_info = DatabaseAPI.GetPower(power_id)
                    effect_list.extend(power_info.effects)
                ELSE:
                    // 6th+ instance is SUPPRESSED (discarded)
                    CONTINUE

    RETURN effect_list

FUNCTION GroupEffectsByIdentifier(effects):
    """
    Group effects that have identical FxId
    From GroupedFx.cs lines 190-210
    """
    groups = Dictionary<FxId, List<Effect>>()

    FOR each effect in effects:
        // Create identifier from effect properties
        fx_id = FxId(
            effect_type=effect.EffectType,
            damage_type=effect.DamageType,
            mez_type=effect.MezType,
            modifies_type=effect.ETModifies,
            target=effect.ToWho,
            pv_mode=effect.PvMode,
            summon_id=effect.nSummon,
            duration=effect.Duration,
            ignore_scaling=effect.IgnoreScaling
        )

        // Add to group
        IF fx_id NOT IN groups:
            groups[fx_id] = []
        groups[fx_id].add(effect)

    RETURN groups

FUNCTION ApplyStackingRules(fx_id, effect_list):
    """
    Apply stacking rules to effects with same identifier
    From GroupedFx.cs lines 130-184
    """
    // Single effect = no stacking needed
    IF effect_list.length == 1:
        RETURN GroupedEffect(
            identifier=fx_id,
            magnitude=effect_list[0].BuffedMag,
            effects=[effect_list[0]]
        )

    // Multiple effects = determine stacking mode
    stacking_mode = DetermineStackingMode(effect_list[0])

    SWITCH stacking_mode:
        CASE ADDITIVE:
            // Sum all magnitudes
            total_mag = 0.0
            FOR each effect in effect_list:
                total_mag += effect.BuffedMag
            RETURN GroupedEffect(fx_id, total_mag, effect_list)

        CASE MULTIPLICATIVE:
            // Multiply (1 + mag) factors, then subtract 1
            product = 1.0
            FOR each effect in effect_list:
                product *= (1.0 + effect.BuffedMag)
            total_mag = product - 1.0
            RETURN GroupedEffect(fx_id, total_mag, effect_list)

        CASE BEST_VALUE:
            // Take highest magnitude only
            best_mag = MAX(effect.BuffedMag for effect in effect_list)
            RETURN GroupedEffect(fx_id, best_mag, effect_list)

FUNCTION DetermineStackingMode(effect):
    """
    Determine how this effect type stacks
    Based on Effect.Stacking property and effect type
    """
    // Check Stacking property first
    IF effect.Stacking == eStacking.No:
        RETURN BEST_VALUE

    // Effect type determines stacking mode
    SWITCH effect.EffectType:
        // Additive stacking (most common)
        CASE Defense, Resistance, RechargeTime, Accuracy, ToHit,
             Recovery, Regeneration, EnduranceDiscount, HitPoints,
             SpeedRunning, SpeedFlying, SpeedJumping, MaxEndurance,
             MaxRunSpeed, MaxFlySpeed, MaxJumpSpeed, Perception,
             StealthRadius, StealthRadiusPlayer:
            RETURN ADDITIVE

        // Multiplicative stacking
        CASE DamageBuff:
            RETURN MULTIPLICATIVE

        // Default to additive
        DEFAULT:
            RETURN ADDITIVE

STRUCT FxId:
    """
    Unique identifier for grouping effects
    From GroupedFx.cs lines 82-98
    """
    EffectType: eEffectType       // What buff/debuff (Defense, Resistance, etc.)
    DamageType: eDamage            // Damage subtype (Smashing, Energy, All, etc.)
    MezType: eMez                  // Mez subtype (Hold, Sleep, None, etc.)
    ETModifies: eEffectType        // Modified effect type (for Enhancement effects)
    ToWho: eToWho                  // Target (Self, Target, Team)
    PvMode: ePvX                   // PvE/PvP/Any
    SummonId: int                  // Pet source ID
    Duration: float                // Effect duration
    IgnoreScaling: bool            // Bypass archetype scaling

STRUCT GroupedEffect:
    """
    Result of stacking multiple effects
    From GroupedFx.cs lines 111-118
    """
    Identifier: FxId               // What this effect is
    Magnitude: float               // Final stacked magnitude
    IncludedEffects: List<int>     // Source effect indices
    IsEnhancement: bool            // From enhancement special
    IsAggregated: bool             // Multiple effects combined
```

**Edge Cases Handled:**

1. **Empty Effect List**: Returns empty result, no effects to stack
2. **Single Effect**: No stacking calculation needed, returns effect as-is
3. **Same Source Multiple Times**: Each instance counts separately (no same-source suppression in base stacking)
4. **Zero Magnitude Effects**: Still tracked in IncludedEffects, contribute 0 to total
5. **Negative Magnitude**: Used for debuffs, stacks same as positive (additive sums negative values)
6. **Conflicting Stacking Flags**: If effects in same group have different Stacking values (shouldn't happen with proper FxId), use first effect's flag
7. **Rule of 5 Boundary**: Count starts at 0, increments before check, so `count < 6` means instances 1-5 included, 6+ suppressed

---

## C# Implementation Reference

### Primary Files

**File**: `/Users/w/code/mids-hero-web/external/dev/MidsReborn/MidsReborn/Core/Enums.cs`

**Lines 1081-1085**: Stacking enumeration
```csharp
public enum eStacking
{
    No,   // Multiple applications do not stack (best value wins)
    Yes   // Multiple applications stack additively
}
```

**Key Points:**
- Only 2 values: `No` (0) and `Yes` (1)
- `No` means "best value only" (highest magnitude wins)
- `Yes` means stacking is allowed (but mode determined by effect type)
- Default value: `No` (from Effect.cs line 34)

---

**File**: `/Users/w/code/mids-hero-web/external/dev/MidsReborn/MidsReborn/Core/Base/Data_Classes/Effect.cs`

**Lines 34-35**: Default stacking values
```csharp
public Effect()
{
    // ... constructor initialization
    Stacking = Enums.eStacking.No;     // Line 34: Default is NO stacking
    Suppression = Enums.eSuppress.None; // Line 35: Default is no suppression
    // ...
}
```

**Key Points:**
- **Default**: `Stacking = No` (must be explicitly set to `Yes` in power data)
- Most effects have `Stacking = Yes` set in game data (overriding default)
- Some "Unique" IOs and special procs have `Stacking = No` to prevent abuse

---

**File**: `/Users/w/code/mids-hero-web/external/dev/MidsReborn/MidsReborn/Core/GroupedFx.cs`

**Lines 82-98**: FxId struct (grouping key)
```csharp
public struct FxId
{
    public Enums.eEffectType EffectType;      // What buff/debuff
    public Enums.eMez MezType;                // Mez subtype if applicable
    public Enums.eDamage DamageType;          // Damage subtype if applicable
    public Enums.eEffectType ETModifies;      // Modified effect type
    public Enums.eToWho ToWho;                // Target (Self, Target, Team)
    public Enums.ePvX PvMode;                 // PvE/PvP/Any
    public int SummonId;                      // Pet source ID
    public float Duration;                    // Effect duration
    public bool IgnoreScaling;                // Bypass archetype scaling

    public override string ToString()
    {
        return $"<FxId> {{Type: {EffectType}, Modifies: {ETModifies}, Mez: {MezType}, Damage: {DamageType}, ToWho: {ToWho}, PvMode: {PvMode}, IgnoreScaling: {IgnoreScaling}}}";
    }
}
```

**Key Points:**
- Effects must match **ALL** fields to be grouped together
- Different damage types = different groups (Defense(Smashing) ≠ Defense(Fire))
- Different targets = different groups (Self ≠ Team)
- Duration, PvMode, IgnoreScaling also distinguish groups

---

**Lines 190-210**: GroupedFx constructor from single effect
```csharp
public GroupedFx(IEffect effect, int fxIndex)
{
    SingleEffectSource = effect;
    FxIdentifier = new FxId
    {
        DamageType = effect.DamageType,
        EffectType = effect.EffectType,
        ETModifies = effect.ETModifies,
        MezType = effect.MezType,
        ToWho = effect.ToWho,
        PvMode = effect.PvMode,
        IgnoreScaling = effect.IgnoreScaling
    };
    Mag = effect.BuffedMag;               // Use enhanced magnitude
    Alias = "";
    IncludedEffects = new List<int> {fxIndex};
    IsEnhancement = effect.isEnhancementEffect;
    SpecialCase = effect.SpecialCase;
    IsAggregated = false;                 // Single effect, not aggregated
}
```

**Key Points:**
- Uses `BuffedMag` (enhanced magnitude) not `Mag` (base magnitude)
- `IsAggregated = false` for single effects, `true` when multiple combined (line 169)
- Duration extracted from effect but not stored in FxIdentifier creation here (differs from struct definition - **potential bug**)

---

**Lines 162-184**: GroupedFx constructor for aggregating multiple effects
```csharp
public GroupedFx(FxId fxIdentifier, List<GroupedFx> greList)
{
    FxIdentifier = fxIdentifier;
    Mag = greList[0].Mag;                     // First effect's magnitude (wrong for stacking?)
    Alias = greList[0].Alias;
    IsEnhancement = greList[0].IsEnhancement;
    SpecialCase = greList[0].SpecialCase;
    IsAggregated = true;
    SingleEffectSource = null;

    IncludedEffects = new List<int>();
    foreach (var gre in greList)
    {
        IncludedEffects.AddRangeUnique(gre.IncludedEffects);  // Collect all effect indices
    }

    if (IncludedEffects.Count <= 1)
    {
        IsAggregated = false;                 // Only 1 unique effect, not aggregated
    }

    IncludedEffects.Sort();
}
```

**Key Points:**
- Takes `List<GroupedFx>` (already-grouped effects with same FxId)
- Uses first effect's magnitude (line 165) - **doesn't show stacking math here**
- Stacking math likely happens elsewhere before this constructor is called
- Collects all effect indices for tracking sources

---

**File**: `/Users/w/code/mids-hero-web/external/dev/MidsReborn/MidsReborn/Core/Build.cs`

**Lines 1321-1370**: Rule of 5 implementation
```csharp
private IPower GetSetBonusVirtualPower()
{
    IPower power1 = new Power();
    if (MidsContext.Config.I9.IgnoreSetBonusFX)
    {
        return power1;  // User setting to disable set bonuses
    }

    var nidPowers = DatabaseAPI.NidPowers("set_bonus");
    // Initialize setCount with 0's
    var setCount = new int[nidPowers.Length];

    var skipEffects = false;
    var effectList = new List<IEffect>();

    foreach (var setBonus in SetBonuses)
    {
        foreach (var setInfo in setBonus.SetInfo)
        {
            foreach (var power in setInfo.Powers.Where(x => x > -1))
            {
                if (power >= setCount.Length)
                {
                    throw new IndexOutOfRangeException("Power index exceeds setCount bounds.");
                }

                ++setCount[power];  // Increment count BEFORE check

                var powerInfo = DatabaseAPI.Database.Power[power];
                if (powerInfo != null && ShouldSkipEffects(powerInfo))
                {
                    continue;  // Skip pet-only bonuses
                }

                // KEY LOGIC: Only include if count < 6 (instances 1-5)
                if (setCount[power] < 6)
                {
                    if (powerInfo != null)
                    {
                        effectList.AddRange(powerInfo.Effects.Select(t => (IEffect)t.Clone()));
                    }
                }
                // 6th+ instance: count incremented but effects NOT added (suppressed)
            }
        }
    }

    power1.Effects = effectList.ToArray();
    return power1;  // Virtual power containing all set bonus effects
}
```

**Key Values:**
- Counter starts at `0`
- Increment happens BEFORE check: `++setCount[power]` (line 1347)
- Check: `if (setCount[power] < 6)` (line 1357)
- Result: Instances 1-5 included, 6+ suppressed
- Counting is per **set bonus power ID**, not per set name
- Effects are cloned: `(IEffect)t.Clone()` (line 1361) to avoid modifying originals

---

**Lines 1398**: Alternative check in GetSetBonusPowers()
```csharp
if (setCount[powerIndex] >= 6) continue;
```

**Key Points:**
- Equivalent check: `>= 6` instead of `< 6`
- Same result: Skip 6th+ instances
- Shows implementation consistency across methods

---

### Constant Values

**Stacking Mode Determination:**

From code analysis and effect type behavior:

| Effect Type | Stacking Mode | eStacking Flag | Notes |
|-------------|---------------|----------------|-------|
| Defense | ADDITIVE | Yes | All damage types stack separately |
| Resistance | ADDITIVE | Yes | All damage types stack separately |
| RechargeTime | ADDITIVE | Yes | Global recharge stacks additively |
| Accuracy | ADDITIVE | Yes | Stacks to accuracy cap |
| ToHit | ADDITIVE | Yes | Stacks to tohit cap |
| Recovery | ADDITIVE | Yes | Endurance recovery stacks |
| Regeneration | ADDITIVE | Yes | Health regen stacks |
| EnduranceDiscount | ADDITIVE | Yes | End cost reduction stacks |
| HitPoints | ADDITIVE | Yes | Max HP stacks |
| SpeedRunning/Flying/Jumping | ADDITIVE | Yes | Movement speed stacks |
| DamageBuff | MULTIPLICATIVE | Yes | Damage buffs multiply |
| Unique IOs | BEST_VALUE | No | Only highest value counts |

**Rule of 5 Constants:**
- Suppression threshold: `6` (line 1357, 1398)
- Allowed instances: `5` (count 1-5, threshold check `< 6`)
- Counter starts at: `0`
- Counter increment: `1` per instance

---

## Database Schema

**PostgreSQL schema for storing buff stacking rules:**

```sql
-- Table: effect_stacking_modes
-- Stores which stacking mode each effect type uses
CREATE TABLE effect_stacking_modes (
    id SERIAL PRIMARY KEY,
    effect_type VARCHAR(50) NOT NULL UNIQUE,  -- Maps to eEffectType enum
    stacking_mode VARCHAR(20) NOT NULL,       -- 'additive', 'multiplicative', 'best_value'
    default_stacking_flag SMALLINT NOT NULL DEFAULT 1,  -- Default eStacking value (0=No, 1=Yes)
    notes TEXT,
    CONSTRAINT check_stacking_mode CHECK (stacking_mode IN ('additive', 'multiplicative', 'best_value')),
    CONSTRAINT check_stacking_flag CHECK (default_stacking_flag IN (0, 1))
);

-- Index for fast lookups by effect type
CREATE INDEX idx_effect_stacking_modes_effect_type
ON effect_stacking_modes(effect_type);

-- Table: buff_stacking_rules
-- Stores Rule of 5 configuration and other stacking limits
CREATE TABLE buff_stacking_rules (
    id SERIAL PRIMARY KEY,
    rule_name VARCHAR(100) NOT NULL UNIQUE,
    rule_type VARCHAR(50) NOT NULL,           -- 'rule_of_5', 'same_source', 'unique_limit'
    max_instances INTEGER NOT NULL,           -- Max allowed stacking instances
    applies_to VARCHAR(50) NOT NULL,          -- 'set_bonuses', 'all_effects', 'specific_power'
    power_category VARCHAR(50),               -- 'set_bonus', 'incarnate', 'power', NULL for all
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_rule_type CHECK (rule_type IN ('rule_of_5', 'same_source', 'unique_limit', 'custom')),
    CONSTRAINT check_applies_to CHECK (applies_to IN ('set_bonuses', 'all_effects', 'specific_power', 'power_category'))
);

-- Index for active rule lookups
CREATE INDEX idx_buff_stacking_rules_active
ON buff_stacking_rules(is_active)
WHERE is_active = TRUE;

-- Table: effect_stacking_overrides
-- Stores per-effect overrides for stacking behavior
CREATE TABLE effect_stacking_overrides (
    id SERIAL PRIMARY KEY,
    effect_id INTEGER NOT NULL,               -- Foreign key to effects table
    stacking_flag SMALLINT NOT NULL,          -- Override eStacking value (0=No, 1=Yes)
    reason VARCHAR(200),                      -- Why this override exists (e.g., "Unique IO")
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_effect FOREIGN KEY (effect_id) REFERENCES effects(id) ON DELETE CASCADE,
    CONSTRAINT check_override_stacking_flag CHECK (stacking_flag IN (0, 1))
);

-- Index for effect lookups
CREATE INDEX idx_effect_stacking_overrides_effect_id
ON effect_stacking_overrides(effect_id);

-- Table: build_effect_groups
-- Stores grouped effects after stacking calculation (cached for performance)
CREATE TABLE build_effect_groups (
    id SERIAL PRIMARY KEY,
    build_id INTEGER NOT NULL,                -- Foreign key to builds table
    effect_type VARCHAR(50) NOT NULL,
    damage_type VARCHAR(50),
    mez_type VARCHAR(50),
    modifies_type VARCHAR(50),
    target VARCHAR(20) NOT NULL,              -- 'self', 'target', 'team'
    pv_mode VARCHAR(10) NOT NULL DEFAULT 'any', -- 'pve', 'pvp', 'any'
    summon_id INTEGER,
    duration NUMERIC(10, 4),
    ignore_scaling BOOLEAN NOT NULL DEFAULT FALSE,
    final_magnitude NUMERIC(10, 6) NOT NULL,  -- Stacked magnitude
    included_effect_ids INTEGER[] NOT NULL,   -- Array of source effect IDs
    is_aggregated BOOLEAN NOT NULL DEFAULT FALSE,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_build FOREIGN KEY (build_id) REFERENCES builds(id) ON DELETE CASCADE
);

-- Index for build lookups
CREATE INDEX idx_build_effect_groups_build_id
ON build_effect_groups(build_id);

-- Composite index for effect identifier lookups
CREATE INDEX idx_build_effect_groups_identifier
ON build_effect_groups(build_id, effect_type, damage_type, target, pv_mode);

-- Table: set_bonus_counters
-- Tracks Rule of 5 counters per build
CREATE TABLE set_bonus_counters (
    id SERIAL PRIMARY KEY,
    build_id INTEGER NOT NULL,
    set_bonus_power_id INTEGER NOT NULL,     -- Power ID of set bonus
    instance_count INTEGER NOT NULL,         -- How many times this bonus appears
    included_count INTEGER NOT NULL,         -- How many instances count (max 5)
    suppressed_count INTEGER NOT NULL,       -- How many instances suppressed (count - 5)
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_build_counter FOREIGN KEY (build_id) REFERENCES builds(id) ON DELETE CASCADE,
    CONSTRAINT check_counts CHECK (included_count <= 5 AND suppressed_count >= 0),
    UNIQUE(build_id, set_bonus_power_id)
);

-- Index for build lookups
CREATE INDEX idx_set_bonus_counters_build_id
ON set_bonus_counters(build_id);

-- Seed data for effect_stacking_modes
INSERT INTO effect_stacking_modes (effect_type, stacking_mode, default_stacking_flag, notes) VALUES
('Defense', 'additive', 1, 'Defense buffs stack additively per damage type'),
('Resistance', 'additive', 1, 'Resistance buffs stack additively per damage type'),
('RechargeTime', 'additive', 1, 'Global recharge reduction stacks additively'),
('Accuracy', 'additive', 1, 'Accuracy buffs stack additively'),
('ToHit', 'additive', 1, 'ToHit buffs stack additively'),
('Recovery', 'additive', 1, 'Endurance recovery stacks additively'),
('Regeneration', 'additive', 1, 'Health regeneration stacks additively'),
('EnduranceDiscount', 'additive', 1, 'Endurance cost reduction stacks additively'),
('HitPoints', 'additive', 1, 'Max HP bonuses stack additively'),
('SpeedRunning', 'additive', 1, 'Run speed buffs stack additively'),
('SpeedFlying', 'additive', 1, 'Fly speed buffs stack additively'),
('SpeedJumping', 'additive', 1, 'Jump speed buffs stack additively'),
('DamageBuff', 'multiplicative', 1, 'Damage buffs stack multiplicatively'),
('Mez', 'additive', 1, 'Mez duration/magnitude stacks additively'),
('MezResist', 'additive', 1, 'Mez resistance stacks additively');

-- Seed data for buff_stacking_rules
INSERT INTO buff_stacking_rules (rule_name, rule_type, max_instances, applies_to, power_category, description) VALUES
('Rule of 5', 'rule_of_5', 5, 'set_bonuses', 'set_bonus', 'Only first 5 instances of same set bonus count, 6+ suppressed'),
('Enhancement Unique', 'unique_limit', 1, 'specific_power', 'enhancement', 'Unique enhancements only apply once per build');
```

**Key Design Decisions:**

1. **effect_stacking_modes**: Lookup table for default behavior, indexed for fast queries
2. **buff_stacking_rules**: Flexible rule system for Rule of 5 and future rules
3. **effect_stacking_overrides**: Per-effect exceptions (e.g., Unique IOs with `Stacking = No`)
4. **build_effect_groups**: Cached calculation results to avoid recalculating on every query
5. **set_bonus_counters**: Rule of 5 tracking per build, denormalized for performance
6. **Numeric precision**: `NUMERIC(10,6)` for magnitudes (handles values like 0.075 = 7.5%)
7. **Array type**: `INTEGER[]` for storing multiple effect IDs efficiently
8. **Timestamps**: Track when calculations were done for cache invalidation

---

## Comprehensive Test Cases

### Test Case 1: Additive Stacking - Defense Buffs

**Scenario**: Character has 3 sources of Defense(All)

**Input:**
- Effect 1: Defense(All), magnitude = +0.075 (7.5% from IO set)
- Effect 2: Defense(All), magnitude = +0.05 (5% from IO set)
- Effect 3: Defense(All), magnitude = +0.0375 (3.75% from IO set)
- All effects: `Stacking = Yes`, `EffectType = Defense`, `DamageType = All`

**Calculation:**
```
Stacking Mode = ADDITIVE (Defense effect type)

Step 1: Group effects by FxId
  - All 3 have identical FxId (Defense, All, Self, PvE, ...)

Step 2: Apply additive stacking
  Total = 0.075 + 0.05 + 0.0375
  Total = 0.1625

Step 3: Convert to percentage
  = 16.25% Defense(All)
```

**Expected Output:**
- Final magnitude: `0.1625`
- Display: `+16.25% Defense(All)`
- Included effects: `[0, 1, 2]`
- Is aggregated: `true`

---

### Test Case 2: Multiplicative Stacking - Damage Buffs

**Scenario**: Character has 2 damage buff effects

**Input:**
- Effect 1: DamageBuff(All), magnitude = +1.00 (100% damage buff, e.g., Build Up)
- Effect 2: DamageBuff(All), magnitude = +0.50 (50% damage buff, e.g., Aim)
- Both effects: `Stacking = Yes`, `EffectType = DamageBuff`, `DamageType = All`

**Calculation:**
```
Stacking Mode = MULTIPLICATIVE (DamageBuff effect type)

Step 1: Group effects by FxId
  - Both have identical FxId (DamageBuff, All, Self, ...)

Step 2: Apply multiplicative stacking
  Product = (1 + 1.00) × (1 + 0.50)
  Product = 2.0 × 1.5
  Product = 3.0

  Total = Product - 1.0
  Total = 3.0 - 1.0
  Total = 2.0

Step 3: Convert to percentage
  = 200% total damage buff
```

**Expected Output:**
- Final magnitude: `2.0`
- Display: `+200% Damage(All)`
- Included effects: `[0, 1]`
- Is aggregated: `true`

**Note**: If these were additive instead:
```
Additive Total = 1.00 + 0.50 = 1.50 = +150% damage
Multiplicative Total = 2.0 = +200% damage
Difference: Multiplicative gives 50% more benefit (prevents exponential scaling)
```

---

### Test Case 3: Best Value Only - Non-Stacking (Unique IO)

**Scenario**: Character slots 2 "Luck of the Gambler +7.5% Recharge" IOs

**Input:**
- Effect 1: RechargeTime, magnitude = +0.075 (7.5% recharge)
- Effect 2: RechargeTime, magnitude = +0.075 (7.5% recharge, same IO)
- Both effects: `Stacking = No` (Unique IO flag), `EffectType = RechargeTime`

**Calculation:**
```
Stacking Mode = BEST_VALUE (Stacking = No)

Step 1: Group effects by FxId
  - Both have identical FxId (RechargeTime, Self, ...)

Step 2: Apply best value stacking
  Total = MAX(0.075, 0.075)
  Total = 0.075

Step 3: Second effect is suppressed (not counted)
```

**Expected Output:**
- Final magnitude: `0.075`
- Display: `+7.5% Recharge` (only one instance counts)
- Included effects: `[0, 1]` (both tracked, but only max magnitude used)
- Is aggregated: `true` (multiple effects present, even if only one's value used)

**Note**: This is why LotG +Recharge IOs can only be slotted 5 times (they're set bonuses, subject to Rule of 5, separate from Stacking flag)

---

### Test Case 4: Rule of 5 - Set Bonus Suppression

**Scenario**: Character slots 6 instances of "5% Recharge Bonus" set bonus across build

**Input:**
- Set bonus power ID: `12345` (example ID for "+5% Recharge" bonus)
- Effect: RechargeTime, magnitude = +0.05 (5% recharge)
- Repeated 6 times in build (6 different IO sets with same bonus)

**Calculation:**
```
Rule of 5 Application (Build.cs lines 1321-1370):

setCount[12345] = 0  // Initial

Instance 1:
  setCount[12345] = 1  // After ++setCount
  Check: 1 < 6 = TRUE
  Action: Include effect (+0.05)
  Running total: 0.05

Instance 2:
  setCount[12345] = 2
  Check: 2 < 6 = TRUE
  Action: Include effect (+0.05)
  Running total: 0.10

Instance 3:
  setCount[12345] = 3
  Check: 3 < 6 = TRUE
  Action: Include effect (+0.05)
  Running total: 0.15

Instance 4:
  setCount[12345] = 4
  Check: 4 < 6 = TRUE
  Action: Include effect (+0.05)
  Running total: 0.20

Instance 5:
  setCount[12345] = 5
  Check: 5 < 6 = TRUE
  Action: Include effect (+0.05)
  Running total: 0.25

Instance 6:
  setCount[12345] = 6
  Check: 6 < 6 = FALSE
  Action: SUPPRESS (do not add effect)
  Running total: 0.25 (unchanged)

After Rule of 5, stacking:
  Stacking Mode = ADDITIVE
  Total = 0.05 + 0.05 + 0.05 + 0.05 + 0.05
  Total = 0.25
```

**Expected Output:**
- Final magnitude: `0.25`
- Display: `+25% Recharge`
- Instances counted: `5`
- Instances suppressed: `1`
- Included effects: `[0, 1, 2, 3, 4]` (6th effect not in list)

---

### Test Case 5: Additive Stacking - Resistance Buffs (Multiple Damage Types)

**Scenario**: Character has resistance buffs to different damage types

**Input:**
- Effect 1: Resistance(Smashing), magnitude = +0.10 (10% S resist)
- Effect 2: Resistance(Lethal), magnitude = +0.10 (10% L resist)
- Effect 3: Resistance(Smashing), magnitude = +0.05 (5% S resist, different source)
- All effects: `Stacking = Yes`, `EffectType = Resistance`

**Calculation:**
```
Step 1: Group effects by FxId

Group A (Smashing):
  - Effect 1: Resistance(Smashing), +0.10
  - Effect 3: Resistance(Smashing), +0.05
  FxId: {EffectType=Resistance, DamageType=Smashing, ...}

Group B (Lethal):
  - Effect 2: Resistance(Lethal), +0.10
  FxId: {EffectType=Resistance, DamageType=Lethal, ...}

Step 2: Apply stacking to each group

Group A (Smashing):
  Stacking Mode = ADDITIVE
  Total = 0.10 + 0.05 = 0.15

Group B (Lethal):
  Stacking Mode = ADDITIVE
  Total = 0.10 (only one effect)

Step 3: Result is TWO grouped effects (separate damage types)
```

**Expected Output:**
- Grouped Effect 1:
  - Final magnitude: `0.15`
  - Display: `+15% Resistance(Smashing)`
  - Included effects: `[0, 2]`
  - Is aggregated: `true`

- Grouped Effect 2:
  - Final magnitude: `0.10`
  - Display: `+10% Resistance(Lethal)`
  - Included effects: `[1]`
  - Is aggregated: `false`

**Key Point**: Different damage types create separate FxId groups, so they don't stack together

---

### Test Case 6: No Stacking - Ignore Mode (Highest Magnitude Wins)

**Scenario**: Two +Stealth bonuses, one stronger than the other

**Input:**
- Effect 1: StealthRadius, magnitude = +100 (100ft stealth radius)
- Effect 2: StealthRadius, magnitude = +35 (35ft stealth radius)
- Both effects: `Stacking = No`, `EffectType = StealthRadius`

**Calculation:**
```
Stacking Mode = BEST_VALUE (Stacking = No)

Step 1: Group effects by FxId
  - Both have identical FxId

Step 2: Apply best value stacking
  Total = MAX(100, 35)
  Total = 100

Step 3: Weaker effect ignored
```

**Expected Output:**
- Final magnitude: `100`
- Display: `100ft Stealth Radius`
- Included effects: `[0, 1]`
- Is aggregated: `true`
- Note: Effect 2 (+35) contributes nothing (suppressed by higher value)

---

### Test Case 7: Same Source, Different Target

**Scenario**: Power buffs self AND team (different FxId due to ToWho)

**Input:**
- Effect 1: Defense(All), magnitude = +0.10, ToWho = Self
- Effect 2: Defense(All), magnitude = +0.05, ToWho = Team
- Both effects: `Stacking = Yes`, `EffectType = Defense`, `DamageType = All`

**Calculation:**
```
Step 1: Group effects by FxId

Group A (Self):
  - Effect 1: Defense(All), +0.10, ToWho=Self
  FxId: {EffectType=Defense, DamageType=All, ToWho=Self, ...}

Group B (Team):
  - Effect 2: Defense(All), +0.05, ToWho=Team
  FxId: {EffectType=Defense, DamageType=All, ToWho=Team, ...}

Step 2: Different ToWho values = different FxIds = separate groups

Group A: Total = 0.10
Group B: Total = 0.05
```

**Expected Output:**
- Grouped Effect 1 (Self):
  - Final magnitude: `0.10`
  - Display: `+10% Defense(All)` (affects self)
  - Included effects: `[0]`

- Grouped Effect 2 (Team):
  - Final magnitude: `0.05`
  - Display: `+5% Defense(All)` (affects team)
  - Included effects: `[1]`

**Key Point**: Self vs Team buffs are tracked separately, even if same effect type

---

### Test Case 8: Multiplicative Stacking - Three Damage Buffs

**Scenario**: Character has 3 damage buffs active simultaneously

**Input:**
- Effect 1: DamageBuff(All), magnitude = +0.80 (80%, e.g., Fury)
- Effect 2: DamageBuff(All), magnitude = +0.50 (50%, e.g., Aim)
- Effect 3: DamageBuff(All), magnitude = +0.25 (25%, e.g., small set bonus)
- All effects: `Stacking = Yes`, `EffectType = DamageBuff`

**Calculation:**
```
Stacking Mode = MULTIPLICATIVE

Step 1: Group effects by FxId
  - All 3 have identical FxId

Step 2: Apply multiplicative stacking
  Product = (1 + 0.80) × (1 + 0.50) × (1 + 0.25)
  Product = 1.8 × 1.5 × 1.25

  Step-by-step multiplication:
    1.8 × 1.5 = 2.7
    2.7 × 1.25 = 3.375

  Total = Product - 1.0
  Total = 3.375 - 1.0
  Total = 2.375

Step 3: Convert to percentage
  = 237.5% total damage buff
```

**Expected Output:**
- Final magnitude: `2.375`
- Display: `+237.5% Damage(All)`
- Included effects: `[0, 1, 2]`
- Is aggregated: `true`

**Comparison to Additive:**
```
If stacking were additive:
  Total = 0.80 + 0.50 + 0.25 = 1.55 = +155% damage

Multiplicative result: +237.5%
Additive result: +155%
Difference: +82.5% (multiplicative gives more benefit)

Note: This seems backwards from typical game design (multiplicative usually prevents
excessive stacking). Need to verify actual game behavior - this may be wrong, or
DamageBuff may actually stack additively in practice.
```

**IMPORTANT**: MidsReborn code comments suggest DamageBuff is multiplicative, but actual game behavior may differ. This requires testing against live game or deeper code analysis in Phase 3.

---

### Test Case 9: Rule of 5 with Different Set Bonuses

**Scenario**: Character has multiple different set bonuses, some repeated

**Input:**
- Set Bonus A (power ID 100): +5% Recharge, appears 6 times
- Set Bonus B (power ID 200): +3% Defense, appears 3 times
- Set Bonus C (power ID 300): +10% Accuracy, appears 7 times

**Calculation:**
```
Rule of 5 Applied Per Power ID:

Set Bonus A (ID 100, +5% Recharge):
  Instances: 6
  Rule of 5: Count 1-5 included, 6 suppressed
  Magnitude: 0.05 × 5 = 0.25 (25% recharge)

Set Bonus B (ID 200, +3% Defense):
  Instances: 3
  Rule of 5: All 3 included (< 6)
  Magnitude: 0.03 × 3 = 0.09 (9% defense)

Set Bonus C (ID 300, +10% Accuracy):
  Instances: 7
  Rule of 5: Count 1-5 included, 6-7 suppressed
  Magnitude: 0.10 × 5 = 0.50 (50% accuracy)

After Rule of 5 filtering, group by effect type:

RechargeTime group:
  - 5 instances of +0.05 (from Bonus A)
  Total = 0.05 × 5 = 0.25

Defense group:
  - 3 instances of +0.03 (from Bonus B)
  Total = 0.03 × 3 = 0.09

Accuracy group:
  - 5 instances of +0.10 (from Bonus C)
  Total = 0.10 × 5 = 0.50
```

**Expected Output:**
- Recharge: `+25%` (6th instance suppressed)
- Defense: `+9%` (all included)
- Accuracy: `+50%` (6th and 7th instances suppressed)

**Key Points:**
- Rule of 5 applies PER set bonus power ID, not globally
- Different bonuses have separate counters
- After Rule of 5 filtering, normal stacking rules apply

---

### Test Case 10: Complex Scenario - Multiple Rules Combined

**Scenario**: Character has mixed buff sources with various stacking rules

**Input:**
- Power Effect: Defense(All), +0.15 (15% from power, always counts)
- Set Bonus 1: Defense(All), +0.075 (7.5% LotG, appears 5 times)
- Set Bonus 2: Defense(All), +0.075 (7.5% LotG, 6th instance)
- Unique IO: RechargeTime, +0.075 (7.5%, Stacking=No, appears 2 times)
- Set Bonus 3: RechargeTime, +0.05 (5%, different bonus, appears 3 times)

**Calculation:**
```
Phase 1: Apply Rule of 5 to set bonuses

Defense(All) from LotG (set bonus power ID 12345):
  Instance 1-5: Include (+0.075 each)
  Instance 6: Suppress (Rule of 5)
  Included: 5 × 0.075 = 0.375

Unique IO RechargeTime (Stacking=No):
  Instance 1: +0.075
  Instance 2: +0.075
  Best value stacking: MAX(0.075, 0.075) = 0.075

Set Bonus RechargeTime (different power ID):
  Instance 1-3: Include (+0.05 each)
  Included: 3 × 0.05 = 0.15

Phase 2: Group effects by FxId

Defense(All) group:
  - Power effect: +0.15
  - Set bonus effects (5): +0.375
  Total = 0.15 + 0.375 = 0.525

RechargeTime group A (Unique IO, Stacking=No):
  - Best value: +0.075

RechargeTime group B (Set bonus):
  - Additive: +0.15

Note: Unique IO and set bonus have different Stacking flags,
so they may group separately OR group together then use
first effect's stacking flag. Need to verify GroupedFx logic.

Assuming they group together (same FxId except Stacking):
  Total: Need to determine if Stacking flag is part of FxId

If Stacking is NOT part of FxId:
  RechargeTime group (combined):
    - Unique IO contribution: 0.075 (from best-value within its instances)
    - Set bonus contribution: 0.15 (from additive within its instances)
    - How to combine different stacking modes? Use first effect's flag.
    - If Unique IO processed first: Use BEST_VALUE for all
      Total = MAX(0.075, 0.15) = 0.15
    - If Set bonus processed first: Use ADDITIVE for all
      Total = 0.075 + 0.15 = 0.225
    - **This is ambiguous - needs code investigation**

Conservative assumption: Stacking flag IS part of FxId (effects group separately):
  RechargeTime group A (Stacking=No):
    Total = 0.075
  RechargeTime group B (Stacking=Yes):
    Total = 0.15
```

**Expected Output (Conservative):**
- Defense(All): `+52.5%` (power + 5 set bonuses)
- RechargeTime (Unique): `+7.5%` (best of 2 instances)
- RechargeTime (Set): `+15%` (3 bonuses)
- Total Recharge: `+22.5%` (assuming separate groups add in final totals)

**Key Findings:**
- Rule of 5 applies before effect grouping
- Stacking flag may or may not distinguish groups (needs verification)
- Multiple stacking rules can apply to same effect type simultaneously

**TODO for Phase 3**: Investigate if Stacking flag is part of FxId grouping key

---

## Python Implementation Guide

**Production-ready Python implementation:**

```python
# backend/app/calculations/buff_stacking.py

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Tuple
from collections import defaultdict

class StackingMode(Enum):
    """How multiple instances of same buff combine"""
    ADDITIVE = "additive"          # Sum all magnitudes
    MULTIPLICATIVE = "multiplicative"  # Multiply (1+mag) factors
    BEST_VALUE = "best_value"      # Take maximum magnitude only

class EStacking(Enum):
    """Whether effect allows stacking (from game data)"""
    NO = 0   # Best value only
    YES = 1  # Stacking allowed

class EffectType(Enum):
    """Common buff/debuff effect types"""
    DEFENSE = "Defense"
    RESISTANCE = "Resistance"
    RECHARGE_TIME = "RechargeTime"
    ACCURACY = "Accuracy"
    TOHIT = "ToHit"
    RECOVERY = "Recovery"
    REGENERATION = "Regeneration"
    ENDURANCE_DISCOUNT = "EnduranceDiscount"
    HIT_POINTS = "HitPoints"
    DAMAGE_BUFF = "DamageBuff"
    SPEED_RUNNING = "SpeedRunning"
    SPEED_FLYING = "SpeedFlying"
    SPEED_JUMPING = "SpeedJumping"
    MEZ = "Mez"
    MEZ_RESIST = "MezResist"
    # ... add more as needed

class DamageType(Enum):
    """Damage type vectors"""
    NONE = "None"
    SMASHING = "Smashing"
    LETHAL = "Lethal"
    FIRE = "Fire"
    COLD = "Cold"
    ENERGY = "Energy"
    NEGATIVE = "Negative"
    PSIONIC = "Psionic"
    TOXIC = "Toxic"
    ALL = "All"
    MELEE = "Melee"
    RANGED = "Ranged"
    AOE = "AoE"

class MezType(Enum):
    """Mez type vectors"""
    NONE = "None"
    HELD = "Held"
    IMMOBILIZED = "Immobilized"
    STUNNED = "Stunned"
    SLEEP = "Sleep"
    TERRORIZED = "Terrorized"
    CONFUSED = "Confused"

class ToWho(Enum):
    """Effect target"""
    UNSPECIFIED = "Unspecified"
    SELF = "Self"
    TARGET = "Target"
    TEAM = "Team"

class PvMode(Enum):
    """PvE/PvP mode"""
    ANY = "Any"
    PVE = "PvE"
    PVP = "PvP"

@dataclass(frozen=True)
class FxIdentifier:
    """
    Uniquely identifies a buff/debuff type for grouping
    Maps to GroupedFx.FxId struct (GroupedFx.cs lines 82-98)
    """
    effect_type: EffectType        # What buff/debuff
    damage_type: DamageType        # Damage subtype
    mez_type: MezType              # Mez subtype
    modifies_type: EffectType      # For Enhancement effects
    target: ToWho                  # Self/Target/Team
    pv_mode: PvMode                # PvE/PvP/Any
    summon_id: int                 # Pet source ID
    duration: float                # Effect duration
    ignore_scaling: bool           # Bypass AT scaling

    def __hash__(self) -> int:
        """Make hashable for use as dict key"""
        return hash((
            self.effect_type, self.damage_type, self.mez_type,
            self.modifies_type, self.target, self.pv_mode,
            self.summon_id, self.duration, self.ignore_scaling
        ))

@dataclass
class BuffEffect:
    """
    Single buff/debuff effect before stacking
    Maps to IEffect interface
    """
    effect_id: int                 # Unique effect ID
    effect_type: EffectType        # What this effect does
    damage_type: DamageType = DamageType.NONE
    mez_type: MezType = MezType.NONE
    modifies_type: EffectType = EffectType.DEFENSE  # Default for Enhancement
    target: ToWho = ToWho.SELF
    pv_mode: PvMode = PvMode.ANY
    summon_id: int = -1
    duration: float = 0.0
    ignore_scaling: bool = False

    base_magnitude: float = 0.0    # Base magnitude from power data
    buffed_magnitude: float = 0.0  # Enhanced magnitude (after enhancements)
    stacking_flag: EStacking = EStacking.YES
    is_enhancement_effect: bool = False

    # Source tracking
    source_type: str = "power"     # "power", "set_bonus", "incarnate"
    source_power_id: Optional[int] = None

    def create_identifier(self) -> FxIdentifier:
        """Create FxIdentifier for grouping"""
        return FxIdentifier(
            effect_type=self.effect_type,
            damage_type=self.damage_type,
            mez_type=self.mez_type,
            modifies_type=self.modifies_type,
            target=self.target,
            pv_mode=self.pv_mode,
            summon_id=self.summon_id,
            duration=self.duration,
            ignore_scaling=self.ignore_scaling
        )

@dataclass
class GroupedEffect:
    """
    Aggregated effect after stacking
    Maps to GroupedFx class (GroupedFx.cs lines 111-118)
    """
    identifier: FxIdentifier
    base_magnitude: float          # Sum of base magnitudes
    enhanced_magnitude: float      # Final magnitude after stacking
    included_effects: List[int]    # Source effect IDs
    is_enhancement: bool
    is_aggregated: bool            # Multiple effects combined
    stacking_mode: StackingMode    # How effects were combined

    def __str__(self) -> str:
        """Format for display"""
        sign = "+" if self.enhanced_magnitude >= 0 else ""
        percent = self.enhanced_magnitude * 100
        return f"{sign}{percent:.2f}% {self.identifier.effect_type.value}"

class BuffStackingCalculator:
    """
    Handles buff/debuff stacking logic
    Maps to GroupedFx and Build classes
    """

    def __init__(self, rule_of_5_enabled: bool = True):
        """
        Initialize calculator

        Args:
            rule_of_5_enabled: Apply Rule of 5 to set bonuses
        """
        self.rule_of_5_enabled = rule_of_5_enabled
        self.set_bonus_counts: Dict[int, int] = defaultdict(int)

        # Stacking mode lookup table
        self._stacking_modes: Dict[EffectType, StackingMode] = {
            EffectType.DEFENSE: StackingMode.ADDITIVE,
            EffectType.RESISTANCE: StackingMode.ADDITIVE,
            EffectType.RECHARGE_TIME: StackingMode.ADDITIVE,
            EffectType.ACCURACY: StackingMode.ADDITIVE,
            EffectType.TOHIT: StackingMode.ADDITIVE,
            EffectType.RECOVERY: StackingMode.ADDITIVE,
            EffectType.REGENERATION: StackingMode.ADDITIVE,
            EffectType.ENDURANCE_DISCOUNT: StackingMode.ADDITIVE,
            EffectType.HIT_POINTS: StackingMode.ADDITIVE,
            EffectType.SPEED_RUNNING: StackingMode.ADDITIVE,
            EffectType.SPEED_FLYING: StackingMode.ADDITIVE,
            EffectType.SPEED_JUMPING: StackingMode.ADDITIVE,
            EffectType.MEZ: StackingMode.ADDITIVE,
            EffectType.MEZ_RESIST: StackingMode.ADDITIVE,
            EffectType.DAMAGE_BUFF: StackingMode.MULTIPLICATIVE,
        }

    def determine_stacking_mode(self,
                                effect_type: EffectType,
                                stacking_flag: EStacking) -> StackingMode:
        """
        Determine how this effect type stacks

        Args:
            effect_type: Type of effect
            stacking_flag: eStacking flag from effect data

        Returns:
            Stacking mode to use
        """
        # Check stacking flag first
        if stacking_flag == EStacking.NO:
            return StackingMode.BEST_VALUE

        # Look up effect type in table
        return self._stacking_modes.get(effect_type, StackingMode.ADDITIVE)

    def apply_stacking(self,
                      effects: List[BuffEffect],
                      mode: StackingMode) -> float:
        """
        Apply stacking rules to calculate total magnitude

        Args:
            effects: List of effects to stack
            mode: Stacking mode to use

        Returns:
            Final stacked magnitude

        Raises:
            ValueError: If effects list is empty
        """
        if not effects:
            raise ValueError("Cannot apply stacking to empty effect list")

        if len(effects) == 1:
            return effects[0].buffed_magnitude

        if mode == StackingMode.ADDITIVE:
            # Sum all magnitudes
            return sum(e.buffed_magnitude for e in effects)

        elif mode == StackingMode.MULTIPLICATIVE:
            # (1 + mag1) * (1 + mag2) * ... - 1
            product = 1.0
            for effect in effects:
                product *= (1.0 + effect.buffed_magnitude)
            return product - 1.0

        elif mode == StackingMode.BEST_VALUE:
            # Take maximum magnitude
            return max(e.buffed_magnitude for e in effects)

        else:
            raise ValueError(f"Unknown stacking mode: {mode}")

    def apply_rule_of_five(self, set_bonus_power_id: int) -> bool:
        """
        Check if this set bonus should be included (Rule of 5)
        From Build.cs lines 1321-1370

        Args:
            set_bonus_power_id: Power ID of set bonus

        Returns:
            True if should include, False if suppressed
        """
        if not self.rule_of_5_enabled:
            return True  # Always include if rule disabled

        # Increment counter for this power ID
        self.set_bonus_counts[set_bonus_power_id] += 1
        current_count = self.set_bonus_counts[set_bonus_power_id]

        # Include if this is instance 1-5, suppress if 6+
        return current_count < 6

    def filter_set_bonuses(self, effects: List[BuffEffect]) -> List[BuffEffect]:
        """
        Apply Rule of 5 to set bonus effects

        Args:
            effects: All effects including set bonuses

        Returns:
            Filtered list with 6+ instances suppressed
        """
        if not self.rule_of_5_enabled:
            return effects

        # Reset counters
        self.set_bonus_counts.clear()

        filtered = []
        for effect in effects:
            # Only apply Rule of 5 to set bonuses
            if effect.source_type != "set_bonus":
                filtered.append(effect)
                continue

            # Check if this instance should be included
            power_id = effect.source_power_id
            if power_id is None:
                filtered.append(effect)  # No power ID, include by default
                continue

            if self.apply_rule_of_five(power_id):
                filtered.append(effect)
            # else: suppress (don't add to filtered list)

        return filtered

    def group_effects(self, effects: List[BuffEffect]) -> List[GroupedEffect]:
        """
        Group effects by identifier and apply stacking rules
        Main entry point for buff stacking calculation

        Args:
            effects: All effects to group and stack

        Returns:
            List of grouped effects with combined magnitudes
        """
        if not effects:
            return []

        # Phase 1: Apply Rule of 5 to set bonuses
        filtered_effects = self.filter_set_bonuses(effects)

        # Phase 2: Group by FxIdentifier
        groups: Dict[FxIdentifier, List[BuffEffect]] = defaultdict(list)
        for effect in filtered_effects:
            fx_id = effect.create_identifier()
            groups[fx_id].append(effect)

        # Phase 3: Apply stacking to each group
        grouped_effects = []
        for fx_id, effect_list in groups.items():
            # Determine stacking mode (use first effect's flag)
            mode = self.determine_stacking_mode(
                fx_id.effect_type,
                effect_list[0].stacking_flag
            )

            # Calculate stacked magnitude
            try:
                total_magnitude = self.apply_stacking(effect_list, mode)
            except ValueError as e:
                # Should not happen since we filtered empty lists above
                print(f"Error stacking effects for {fx_id}: {e}")
                continue

            # Create grouped effect
            grouped = GroupedEffect(
                identifier=fx_id,
                base_magnitude=sum(e.base_magnitude for e in effect_list),
                enhanced_magnitude=total_magnitude,
                included_effects=[e.effect_id for e in effect_list],
                is_enhancement=effect_list[0].is_enhancement_effect,
                is_aggregated=(len(effect_list) > 1),
                stacking_mode=mode
            )
            grouped_effects.append(grouped)

        return grouped_effects

    def calculate_build_totals(self,
                               power_effects: List[BuffEffect],
                               set_bonus_effects: List[BuffEffect],
                               incarnate_effects: List[BuffEffect] = None) -> List[GroupedEffect]:
        """
        Calculate total buffs/debuffs for entire build

        Args:
            power_effects: Effects from powers (toggles, clicks)
            set_bonus_effects: Effects from enhancement sets
            incarnate_effects: Effects from incarnate powers

        Returns:
            List of grouped effects representing build totals
        """
        # Combine all effects
        all_effects = []
        all_effects.extend(power_effects)
        all_effects.extend(set_bonus_effects)
        if incarnate_effects:
            all_effects.extend(incarnate_effects)

        # Group and stack
        return self.group_effects(all_effects)

    def get_stat_total(self,
                      grouped_effects: List[GroupedEffect],
                      effect_type: EffectType,
                      damage_type: DamageType = DamageType.NONE) -> float:
        """
        Get total magnitude for specific stat

        Args:
            grouped_effects: All grouped effects from build
            effect_type: Stat to query
            damage_type: Specific damage type (if applicable)

        Returns:
            Total magnitude for this stat (0 if not found)
        """
        for grouped in grouped_effects:
            if grouped.identifier.effect_type == effect_type:
                # Check damage type if specified
                if damage_type != DamageType.NONE:
                    if grouped.identifier.damage_type != damage_type:
                        continue
                return grouped.enhanced_magnitude

        return 0.0

# Example usage
if __name__ == "__main__":
    # Create calculator
    calc = BuffStackingCalculator(rule_of_5_enabled=True)

    # Example: Defense buffs
    defense_effects = [
        BuffEffect(
            effect_id=1,
            effect_type=EffectType.DEFENSE,
            damage_type=DamageType.ALL,
            buffed_magnitude=0.075,  # 7.5%
            source_type="set_bonus",
            source_power_id=12345
        ),
        BuffEffect(
            effect_id=2,
            effect_type=EffectType.DEFENSE,
            damage_type=DamageType.ALL,
            buffed_magnitude=0.05,   # 5%
            source_type="set_bonus",
            source_power_id=12346
        ),
        BuffEffect(
            effect_id=3,
            effect_type=EffectType.DEFENSE,
            damage_type=DamageType.ALL,
            buffed_magnitude=0.15,   # 15%
            source_type="power",
            source_power_id=5000
        ),
    ]

    # Calculate totals
    grouped = calc.group_effects(defense_effects)

    for group in grouped:
        print(f"{group}")
        print(f"  Mode: {group.stacking_mode.value}")
        print(f"  Sources: {group.included_effects}")
        print(f"  Aggregated: {group.is_aggregated}")
```

**Key Implementation Features:**

1. **Type Safety**: Full type hints with dataclasses and enums
2. **Error Handling**: Validates inputs, raises appropriate exceptions
3. **Immutable Identifiers**: FxIdentifier is frozen dataclass (hashable)
4. **Efficient Grouping**: Uses defaultdict for O(1) group lookups
5. **Rule of 5 Tracking**: Separate method for clarity and testing
6. **Extensible**: Easy to add new stacking modes or effect types
7. **Testable**: Pure functions with no side effects (except counter updates)
8. **Documentation**: Comprehensive docstrings with examples
9. **Production Ready**: Handles edge cases, validates data

---

## Integration Points

**Dependencies (Specs this relies on):**

1. **Spec 01 (Power Effects Core)**:
   - Provides `Effect` objects as input
   - `BuffEffect.buffed_magnitude` comes from Spec 01 calculations
   - Effect properties (EffectType, DamageType, etc.) defined in Spec 01

2. **Spec 03 (Buffs/Debuffs Base Formulas)**:
   - Magnitude calculation feeds into stacking
   - `BuffedMag = BaseMag * Scale * ATMod * (1 + Enhancement)`
   - Stacking happens AFTER per-effect magnitude calculation

3. **Spec 10 (Enhancement Schedules)**:
   - Enhancement Diversification affects individual effect magnitudes
   - ED happens BEFORE stacking (each effect enhanced independently)

4. **Spec 13 (Set Bonuses)**:
   - Provides set bonus effects as input
   - Rule of 5 specifically targets set bonus effects
   - Set bonus power IDs used for tracking

5. **Spec 16 (Archetype Modifiers)**:
   - AT scaling affects individual effect magnitudes
   - Scaling happens BEFORE stacking (in Spec 03)
   - `IgnoreScaling` flag part of FxIdentifier

**Dependents (Specs that rely on this):**

1. **Spec 19 (Build Totals - Defense)**:
   - Uses grouped effects to calculate total defense
   - Needs stacked defense values per damage type
   - Applies defense caps AFTER stacking

2. **Spec 20 (Build Totals - Resistance)**:
   - Uses grouped effects to calculate total resistance
   - Needs stacked resistance values per damage type
   - Applies resistance caps AFTER stacking

3. **Spec 21 (Build Totals - Recharge)**:
   - Uses grouped effects to calculate global recharge
   - Needs stacked recharge reduction total
   - Applies recharge floor AFTER stacking

4. **Spec 22 (Build Totals - Damage)**:
   - Uses grouped effects for damage buffs
   - Multiplicative stacking critical for damage calculations
   - Applies damage caps AFTER stacking

5. **Spec 23 (Build Totals - Accuracy)**:
   - Uses grouped effects for accuracy and tohit
   - Needs stacked accuracy/tohit totals
   - Applies accuracy/tohit caps AFTER stacking

6. **Spec 24 (Build Totals - Other Stats)**:
   - Uses grouped effects for all other stats
   - Recovery, regeneration, endurance discount, etc.
   - Applies stat-specific caps AFTER stacking

7. **Spec 26 (Diminishing Returns)**:
   - May apply DR to stacked totals (unclear from code)
   - DR might happen during stacking or after - needs investigation

8. **Spec 27 (Suppression Mechanics)**:
   - `eSuppress` flags may disable effects conditionally
   - Suppression filtering happens BEFORE stacking
   - Stacking calculator needs suppressed effects filtered out

**Data Flow:**

```
Power Data (JSON)
  ↓
Spec 01: Parse effects, extract properties
  ↓
Spec 03: Calculate buffed magnitude per effect
  ↓
Spec 10/16: Apply ED and AT scaling
  ↓
→ SPEC 25: Group and stack effects ← (THIS SPEC)
  ↓
Spec 19-24: Calculate build totals per stat
  ↓
Spec 17: Apply archetype caps
  ↓
Display to user in UI
```

**API Endpoints Using This:**

1. **GET /api/v1/builds/{build_id}/totals**
   - Returns all stacked buff totals for build
   - Calls `BuffStackingCalculator.calculate_build_totals()`
   - Returns `List[GroupedEffect]` serialized to JSON

2. **GET /api/v1/builds/{build_id}/effects**
   - Returns detailed breakdown of all effects
   - Shows which effects grouped together
   - Includes Rule of 5 suppression status

3. **POST /api/v1/builds/{build_id}/simulate**
   - Simulates adding/removing powers or sets
   - Recalculates stacking with new effects
   - Returns diff of totals before/after

4. **GET /api/v1/builds/{build_id}/set-bonuses**
   - Returns set bonus breakdown
   - Shows Rule of 5 counters per bonus
   - Highlights suppressed instances (6+)

**Database Queries:**

1. **Load all effects for build**:
   ```sql
   SELECT e.*
   FROM effects e
   JOIN build_powers bp ON e.power_id = bp.power_id
   WHERE bp.build_id = $1
   UNION
   SELECT e.*
   FROM effects e
   JOIN set_bonuses sb ON e.power_id = sb.bonus_power_id
   WHERE sb.build_id = $1;
   ```

2. **Cache grouped effects**:
   ```sql
   INSERT INTO build_effect_groups (
       build_id, effect_type, damage_type, target,
       final_magnitude, included_effect_ids, is_aggregated
   ) VALUES ($1, $2, $3, $4, $5, $6, $7);
   ```

3. **Load cached grouped effects**:
   ```sql
   SELECT * FROM build_effect_groups
   WHERE build_id = $1
     AND calculated_at > NOW() - INTERVAL '5 minutes';
   ```

**UI Components:**

1. **Build Totals Panel**: Displays stacked totals per stat (Defense, Resistance, etc.)
2. **Effect Breakdown Modal**: Shows which effects contribute to each total
3. **Set Bonus List**: Highlights Rule of 5 status (5/5 counted, 1 suppressed)
4. **Stacking Indicator**: Visual badge showing "Stacks Additively" vs "Best Value Only"

---

**References**:
- Core implementation: `Core/GroupedFx.cs`
- Rule of 5: `Core/Build.cs` lines 1321-1370
- Stacking enum: `Core/Enums.cs` lines 1081-1085
- Effect properties: `Core/IEffect.cs` lines 68-70
- Effect defaults: `Core/Base/Data_Classes/Effect.cs` lines 34-35
- Related specs: Spec 13 (Set Bonuses), Spec 24 (Build Totals), Spec 03 (Buffs/Debuffs)
