# Incarnate Alpha Shifts

## Overview
- **Purpose**: Alpha slot level shifts and passive boosts - increases effective combat level by +1 to +3 and provides passive enhancement bonuses
- **Used By**: Build totals, effective level calculations, power scaling, damage/defense/resistance caps
- **Complexity**: Medium
- **Priority**: High
- **Status**: 🟡 Breadth Complete

## MidsReborn Implementation

### Primary Location
- **Files**:
  - `Forms/frmIncarnate.cs` - UI for selecting Alpha slot powers (lines 68-76)
  - `Core/Enums.cs` - `eAlphaOrder` enumeration (lines 99-110)
  - `Core/GroupedFx.cs` - Level shift effect processing (lines 2001-2003)
  - `Core/Enums.cs` - `eEffectType.LevelShift` (line 435)
- **Classes**:
  - `FrmIncarnate` - Incarnate power selection form
  - `Enums.eAlphaOrder` - Defines tier/branch ordering
  - `GroupedFx` - Effect aggregation with level shift handling

### Alpha Slot Types

MidsReborn implements **8 Alpha types**, each with different passive boost focus:

1. **Agility** - Endurance Discount, Defense, Recharge
2. **Cardiac** - Endurance Modification, Resistance, Endurance Discount
3. **Intuition** - ToHit, Accuracy, Range
4. **Musculature** - Damage, Endurance Discount
5. **Nerve** - Accuracy, Confusion/Hold/Defense Debuff/ToHit Debuff
6. **Resilient** - Resistance, Endurance Discount, Healing
7. **Spiritual** - Healing, Recharge, Slow Resistance
8. **Vigor** - Max HP, Endurance Recovery, Regeneration

Each Alpha type has **9 tiers** defined by `eAlphaOrder` enum:
```csharp
public enum eAlphaOrder
{
    Boost,                    // T1 - Uncommon - no level shift
    Core_Boost,              // T2 - Uncommon - no level shift
    Radial_Boost,            // T2 - Uncommon - no level shift
    Total_Core_Revamp,       // T3 - Rare - +1 level shift
    Partial_Core_Revamp,     // T3 - Rare - +1 level shift
    Total_Radial_Revamp,     // T3 - Rare - +1 level shift
    Partial_Radial_Revamp,   // T3 - Rare - +1 level shift
    Core_Paragon,            // T4 - Very Rare - +1 level shift (stacks to +2)
    Radial_Paragon           // T4 - Very Rare - +1 level shift (stacks to +2)
}
```

### Level Shift Mechanics

**Level Shift Effect Type** (from `Core/Enums.cs` line 435):
```csharp
eEffectType.LevelShift
```

**Effect Processing** (from `Core/GroupedFx.cs` lines 2001-2003):
```csharp
case Enums.eEffectType.LevelShift:
    rankedEffect.Name = "LvlShift";
    rankedEffect.Value = $"{(effectSource.Mag > 0 ? "+" : "")}{effectSource.Mag:##0.##}";
```

**Level Shift Magnitude**:
- T1-T2 (Uncommon): No level shift (Mag = 0)
- T3 (Rare): +1 level shift (Mag = +1)
- T4 (Very Rare): +1 level shift (Mag = +1)
- **Maximum combined**: +3 level shift (Alpha +1, plus Lore/Destiny unlocks +1 each)

### Core vs Radial Branches

Each Alpha type splits at T2 into two branches:

**Core Branch** (Total_Core, Core_Paragon):
- Focuses on **primary boost** at higher magnitude
- Example: Musculature Core = higher damage bonus
- Better for builds focused on one aspect

**Radial Branch** (Total_Radial, Radial_Paragon):
- Provides **balanced boosts** across multiple attributes
- Example: Musculature Radial = damage + endurance discount
- Better for builds needing versatility

**"Total" vs "Partial"** (T3 tier):
- Total = All aspects at higher magnitude
- Partial = Selective aspects at maximum magnitude
- Both provide +1 level shift

### High-Level Algorithm

```
Alpha Slot Application Process:

1. LEVEL SHIFT CALCULATION:
   IF tier >= T3_Rare:
       effective_level = character_level + 1
       IF tier == T4_VeryRare AND has_lore_unlocked:
           effective_level += 1  // Max +2 from Alpha alone
       IF tier == T4_VeryRare AND has_lore_AND_destiny_unlocked:
           effective_level += 1  // Max +3 total (Alpha +1, Lore +1, Destiny +1)

   // Level shift affects:
   // - Damage scaling vs lower level enemies (+1 level = +5% damage per shift)
   // - ToHit scaling vs lower level enemies
   // - Resistance/Defense caps (higher effective level = higher caps)
   // - Purple patch calculations (level difference effects)

2. PASSIVE BOOST APPLICATION:
   FOR each_boost_type in alpha_power.effects:
       IF boost_type.EffectType in [Damage, Defense, Resistance, Recharge, etc]:
           // Alpha bonuses are subject to Enhancement Diversification!
           IF NOT boost_type.IgnoreED:
               boost_magnitude = ApplyEDCurve(boost_type.Mag)
           ELSE:
               boost_magnitude = boost_type.Mag

           // Add to build totals
           build_totals[boost_type.EffectType] += boost_magnitude

3. STACKING RULES:
   // Only ONE Alpha slot can be active at a time
   // Cannot have multiple Alphas like set bonuses

   // Alpha boosts stack with:
   // - Enhancement bonuses (both subject to ED)
   // - Set bonuses (additively)
   // - Incarnate Interface/Destiny/Hybrid (additively)

   // Level shifts from different sources stack:
   // - Alpha T3/T4: +1
   // - Lore T4: +1 (if Alpha T4 slotted)
   // - Destiny T4: +1 (if Alpha T4 and Lore T4 slotted)
   // - Maximum: +3 level shift total

4. CAP APPLICATION:
   // Alpha boosts are applied BEFORE caps
   // Level shift may increase caps themselves (higher effective level)

   final_stat = MIN(stat_with_alpha, cap_for_effective_level)
```

### Dependencies

**Depends On**:
- Effect system (`Effect.cs`, `GroupedFx.cs`) - for boost delivery
- Enhancement Diversification (`MultED` curves) - Alpha bonuses are subject to ED
- Archetype modifiers - Alpha boosts scaled by AT like other effects
- Build totals - Alpha boosts added to global stats
- Level scaling - Level shift affects power scaling

**Used By**:
- Damage calculations - Level shift increases damage vs lower level enemies
- ToHit calculations - Level shift improves hit chance vs lower level enemies
- Defense/Resistance caps - Higher effective level = higher caps for some ATs
- Build display - Shows effective level and Alpha bonuses
- Purple patch - Level difference calculations use effective level

## Game Mechanics Context

**Why This Exists:**

The Incarnate system was City of Heroes' endgame progression content, introduced in Issue 18-20 (2010-2011) during the game's "Going Rogue" expansion. The Alpha slot was the first Incarnate ability players could unlock.

**Purpose in Game Design**:
1. **Level Shift**: Increases effective combat level beyond the 50 cap, making level 50 characters more powerful against level 50+ enemies
2. **Passive Boosts**: Provides always-on enhancement bonuses that help overcome Enhancement Diversification limits
3. **Build Specialization**: 8 different Alpha types let players customize their character's power curve
4. **Progressive Power**: T1 through T4 tiers provide incremental power increases requiring increasingly rare materials

**Historical Context:**

- **Issue 18 "Shades of Gray"** (July 2010): Alpha slot introduced as first Incarnate ability
- **Issue 19 "Incarnates"** (November 2010): Full Incarnate system with Judgment, Interface, Lore, Destiny
- **Issue 20 "Incarnates Ascend"** (April 2011): Additional Incarnate content and level 54 enemies

The Alpha slot was designed to:
- Reward level 50 players with continued progression
- Allow builds to overcome Enhancement Diversification restrictions slightly
- Make Incarnate Trial content (level 50+1 to 50+4 enemies) accessible
- Provide meaningful choice between 8 different power focuses

**Known Quirks:**

1. **ED Still Applies**: Unlike what many players expected, Alpha slot bonuses ARE subject to Enhancement Diversification. They work like slotted enhancements, not like set bonuses. This was a deliberate design choice to prevent excessive power creep.

2. **Level Shift Stacking Requirements**:
   - T3 Rare = +1 shift automatically
   - T4 Very Rare = +1 shift (NOT +2 on its own!)
   - To get +2 shift: Need T4 Alpha AND T4 Lore
   - To get +3 shift: Need T4 Alpha AND T4 Lore AND T4 Destiny
   - This dependency was designed to gate progression behind multiple Incarnate slots

3. **Core vs Radial Not Always Clear**: The naming convention (Total vs Partial, Core vs Radial) confused many players. "Total Core" sounds like it should be better than "Partial Core", but "Partial" often meant "maximum boost to selected attributes" while "Total" meant "all attributes at lower boost".

4. **Different Alphas for Different Content**:
   - **Musculature**: Most popular for damage dealers
   - **Cardiac**: Popular for endurance-heavy builds (toggles, AoE farmers)
   - **Spiritual**: Popular for support characters (healing/recharge)
   - **Nerve**: Less popular, niche use for control-heavy builds
   - **Agility/Resilient/Vigor/Intuition**: Situational based on build gaps

5. **Respec Costs**: Alpha slot could be respecced freely in-game, but required Incarnate Salvage to craft each new Alpha. This made theorycrafting expensive in practice.

6. **Purple Patch Interaction**: Level shift affects the "purple patch" (level difference penalties/bonuses). A level 50+1 character fighting level 50 enemies gets a damage bonus, while a level 50 fighting 50+1 enemies takes a damage penalty. This made level shifts extremely valuable in Incarnate content.

7. **Display Issues**: Some Alphas provide boosts to attributes not normally slotted (like Nerve's confusion duration or hold duration). These bonuses might not display correctly in all build planner contexts.

## Python Implementation Notes

### Proposed Architecture

**Location**: `backend/app/calculations/incarnate/alpha_slot.py`

```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List
from ..effects.effect import Effect, EffectType
from ..enhancement.ed_curve import apply_ed_curve


class AlphaType(Enum):
    """8 Alpha slot types with different boost focuses"""
    AGILITY = "agility"           # Endurance Discount, Defense, Recharge
    CARDIAC = "cardiac"           # Endurance Mod, Resistance, Endurance Discount
    INTUITION = "intuition"       # ToHit, Accuracy, Range
    MUSCULATURE = "musculature"   # Damage, Endurance Discount
    NERVE = "nerve"               # Accuracy, Confusion/Hold/Debuff
    RESILIENT = "resilient"       # Resistance, Endurance Discount, Healing
    SPIRITUAL = "spiritual"       # Healing, Recharge, Slow Resistance
    VIGOR = "vigor"               # Max HP, Recovery, Regeneration


class AlphaTier(Enum):
    """Alpha slot tiers - T1/T2 no shift, T3/T4 have level shift"""
    T1_BOOST = "boost"                          # Uncommon, no shift
    T2_CORE_BOOST = "core_boost"                # Uncommon, no shift
    T2_RADIAL_BOOST = "radial_boost"            # Uncommon, no shift
    T3_TOTAL_CORE_REVAMP = "total_core_revamp"  # Rare, +1 shift
    T3_PARTIAL_CORE_REVAMP = "partial_core"     # Rare, +1 shift
    T3_TOTAL_RADIAL_REVAMP = "total_radial"     # Rare, +1 shift
    T3_PARTIAL_RADIAL_REVAMP = "partial_radial" # Rare, +1 shift
    T4_CORE_PARAGON = "core_paragon"            # Very Rare, +1 shift
    T4_RADIAL_PARAGON = "radial_paragon"        # Very Rare, +1 shift


@dataclass
class AlphaSlot:
    """Represents an Incarnate Alpha slot ability"""
    alpha_type: AlphaType
    tier: AlphaTier
    effects: List[Effect]  # Passive boost effects

    def get_level_shift(self) -> int:
        """
        Calculate level shift provided by this Alpha.

        Returns:
            0 for T1-T2, 1 for T3-T4

        Note: Maximum combined level shift is +3 total:
        - Alpha: +1 (from T3 or T4)
        - Lore T4: +1 (requires Alpha T4)
        - Destiny T4: +1 (requires Alpha T4 + Lore T4)
        """
        if self.tier in [
            AlphaTier.T3_TOTAL_CORE_REVAMP,
            AlphaTier.T3_PARTIAL_CORE_REVAMP,
            AlphaTier.T3_TOTAL_RADIAL_REVAMP,
            AlphaTier.T3_PARTIAL_RADIAL_REVAMP,
            AlphaTier.T4_CORE_PARAGON,
            AlphaTier.T4_RADIAL_PARAGON,
        ]:
            return 1
        return 0

    def get_effective_level(self, base_level: int, has_lore_t4: bool = False,
                           has_destiny_t4: bool = False) -> int:
        """
        Calculate effective character level including Alpha shift.

        Args:
            base_level: Character's actual level (typically 50)
            has_lore_t4: Whether T4 Lore slot is unlocked (adds +1)
            has_destiny_t4: Whether T4 Destiny is unlocked (adds +1)

        Returns:
            Effective level (base + shift, max +3 total)
        """
        shift = self.get_level_shift()

        # Additional shifts from Lore/Destiny only if Alpha is T4
        if self.tier in [AlphaTier.T4_CORE_PARAGON, AlphaTier.T4_RADIAL_PARAGON]:
            if has_lore_t4:
                shift += 1
            if has_lore_t4 and has_destiny_t4:
                shift += 1

        return min(base_level + shift, base_level + 3)  # Max +3

    def apply_to_build(self, build_stats: dict, archetype_mods: dict) -> dict:
        """
        Apply Alpha slot boosts to build totals.

        Args:
            build_stats: Current build statistics
            archetype_mods: AT modifiers for scaling

        Returns:
            Updated build statistics with Alpha bonuses

        Note: Alpha bonuses ARE subject to Enhancement Diversification!
        """
        updated_stats = build_stats.copy()

        for effect in self.effects:
            # Alpha boosts are subject to ED (IgnoreED flag is rarely true)
            if not effect.ignore_ed:
                magnitude = apply_ed_curve(effect.magnitude, effect.effect_type)
            else:
                magnitude = effect.magnitude

            # Apply archetype scaling
            at_scale = archetype_mods.get(effect.effect_type, 1.0)
            scaled_magnitude = magnitude * at_scale

            # Add to build totals (additive with set bonuses)
            stat_key = effect.effect_type.value
            updated_stats[stat_key] = updated_stats.get(stat_key, 0.0) + scaled_magnitude

        return updated_stats


class AlphaSlotFactory:
    """Factory for creating Alpha slot configurations"""

    @staticmethod
    def create_alpha(alpha_type: AlphaType, tier: AlphaTier,
                    power_data: dict) -> AlphaSlot:
        """
        Create Alpha slot from database power data.

        Args:
            alpha_type: Which Alpha type (Musculature, Cardiac, etc.)
            tier: Which tier (T1 through T4, Core/Radial)
            power_data: Power data from database with effects

        Returns:
            AlphaSlot instance with all effects configured
        """
        effects = []
        for effect_data in power_data.get('effects', []):
            effect = Effect.from_dict(effect_data)
            effects.append(effect)

        return AlphaSlot(
            alpha_type=alpha_type,
            tier=tier,
            effects=effects
        )


class LevelShiftCalculator:
    """Calculates level shift effects on combat"""

    @staticmethod
    def get_damage_multiplier(attacker_level: int, target_level: int) -> float:
        """
        Calculate purple patch damage multiplier based on level difference.

        The "purple patch" is level difference scaling:
        - Higher level attacker = damage bonus
        - Lower level attacker = damage penalty

        Args:
            attacker_level: Effective level (including shifts)
            target_level: Enemy level

        Returns:
            Damage multiplier (1.0 = even level, >1.0 = bonus, <1.0 = penalty)

        Note: Defer exact purple patch formula to Spec 41 (Level Scaling)
        """
        level_diff = attacker_level - target_level

        # Simplified - full formula in level-scaling.md
        if level_diff > 0:
            return 1.0 + (level_diff * 0.05)  # +5% per level above
        elif level_diff < 0:
            return 1.0 + (level_diff * 0.10)  # -10% per level below (penalty)
        else:
            return 1.0  # Even level

    @staticmethod
    def get_tohit_modifier(attacker_level: int, target_level: int) -> float:
        """
        Calculate ToHit modifier based on level difference.

        Args:
            attacker_level: Effective level (including shifts)
            target_level: Enemy level

        Returns:
            ToHit modifier (additive to base 75% ToHit)
        """
        level_diff = attacker_level - target_level

        # Simplified - full formula in accuracy-tohit.md
        if level_diff > 0:
            return level_diff * 0.05  # +5% ToHit per level above
        elif level_diff < 0:
            return level_diff * 0.075  # -7.5% ToHit per level below
        else:
            return 0.0
```

### Key Implementation Considerations

1. **Enhancement Diversification**: Alpha bonuses MUST go through ED curve - use `apply_ed_curve()` from Spec 10
2. **Stacking**: Only ONE Alpha can be active - no multi-Alpha stacking like set bonuses
3. **Level Shift Dependencies**: Track Lore/Destiny T4 status to calculate total shift correctly
4. **Database Storage**: Alpha powers stored in `powers` table with `power_set_type = 'Incarnate'`
5. **Effect Processing**: Use existing `Effect` class, add `LevelShift` to `EffectType` enum
6. **Purple Patch**: Defer full level difference calculations to Spec 41 (Level Scaling)
7. **AT Modifiers**: Defer archetype scaling to Spec 16 (Archetype Modifiers)

### Data Model

Alpha slot data should be stored in database with:
- `power_name`: "Musculature Core Paragon", "Cardiac Radial Boost", etc.
- `power_set_name`: "Alpha" (part of Incarnate power set type)
- `effects`: Array of Effect objects (damage boost, endurance discount, etc.)
- `level_shift_magnitude`: 0 for T1-T2, 1 for T3-T4
- `tier`: T1/T2/T3/T4 designation
- `branch`: Core/Radial designation (null for T1)

### Testing Strategy (Breadth Level)

**Test Cases** (defer to Milestone 3 depth):
1. T3 Rare Alpha provides +1 level shift
2. T4 Very Rare Alpha provides +1 level shift (not +2)
3. T4 Alpha + T4 Lore provides +2 level shift
4. T4 Alpha + T4 Lore + T4 Destiny provides +3 level shift (maximum)
5. Alpha bonuses subject to ED curve
6. Level shift increases damage vs lower level enemies
7. Only one Alpha slot can be active at a time

### Related Specifications

- **Spec 01** (Power Effects Core): Effect system foundation
- **Spec 10** (Enhancement Diversification): ED curve applied to Alpha bonuses
- **Spec 16** (Archetype Modifiers): AT scaling for Alpha effects
- **Spec 19-24** (Build Totals): Alpha bonuses added to build stats
- **Spec 25** (Buff Stacking): Alpha stacking rules (one at a time)
- **Spec 30** (Incarnate Abilities): Other Incarnate slots (Judgment, Interface, etc.)
- **Spec 31** (Core vs Radial): Detailed Core/Radial branch differences
- **Spec 41** (Level Scaling): Purple patch level difference calculations

---

**Document Status**: 🟡 Breadth Complete - Overview, high-level algorithm, game context, and Python design provided. Full implementation details deferred to Milestone 3 depth phase.

**Next Steps for Depth**:
1. Document exact ED curve values for each Alpha boost type
2. Provide complete purple patch damage/ToHit formulas
3. Document all 8 Alpha types' effect magnitudes per tier
4. Create test cases comparing MidsReborn calculations
5. Implement full Python calculation engine with test coverage
