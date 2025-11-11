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

**References**:
- Core implementation: `Core/GroupedFx.cs`
- Rule of 5: `Core/Build.cs` lines 1321-1370
- Stacking enum: `Core/Enums.cs` lines 1081-1085
- Effect properties: `Core/IEffect.cs` lines 68-70
- Related specs: Spec 13 (Set Bonuses), Spec 24 (Build Totals), Spec 03 (Buffs/Debuffs)
