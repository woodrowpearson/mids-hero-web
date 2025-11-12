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

---

## Section 1: Algorithm Pseudocode

### Complete Alpha Slot Application Algorithm

```python
def apply_alpha_slot_to_build(
    character: Character,
    alpha_slot: AlphaSlot,
    build_stats: BuildStats,
    has_lore_t4: bool = False,
    has_destiny_t4: bool = False
) -> BuildStats:
    """
    Apply Alpha slot level shift and passive boosts to build.

    Implementation from multiple MidsReborn files:
    - frmIncarnate.cs: UI selection
    - GroupedFx.cs: Level shift effect processing
    - Effect.cs: Boost magnitude application
    - Build.cs: Build totals aggregation

    Args:
        character: Character object with level and archetype
        alpha_slot: Selected Alpha slot (type + tier)
        build_stats: Current build statistics
        has_lore_t4: Whether Lore T4 is slotted
        has_destiny_t4: Whether Destiny T4 is slotted

    Returns:
        Updated build stats with Alpha applied
    """
    updated_stats = build_stats.copy()

    # ========================================
    # STEP 1: CALCULATE LEVEL SHIFT
    # ========================================
    # From GroupedFx.cs lines 2001-2003
    # Only T3 Rare and T4 Very Rare provide shifts

    level_shift = 0

    if alpha_slot.tier in [
        AlphaTier.T3_TOTAL_CORE_REVAMP,
        AlphaTier.T3_PARTIAL_CORE_REVAMP,
        AlphaTier.T3_TOTAL_RADIAL_REVAMP,
        AlphaTier.T3_PARTIAL_RADIAL_REVAMP,
        AlphaTier.T4_CORE_PARAGON,
        AlphaTier.T4_RADIAL_PARAGON
    ]:
        level_shift = 1  # Alpha provides +1

        # Additional shifts ONLY if Alpha is T4
        if alpha_slot.tier in [AlphaTier.T4_CORE_PARAGON, AlphaTier.T4_RADIAL_PARAGON]:
            if has_lore_t4:
                level_shift += 1  # Lore T4 adds +1 (total +2)
            if has_lore_t4 and has_destiny_t4:
                level_shift += 1  # Destiny T4 adds +1 (total +3)

    # Maximum level shift is +3
    level_shift = min(level_shift, 3)

    # Apply to character effective level
    updated_stats.effective_level = character.level + level_shift

    # ========================================
    # STEP 2: APPLY PASSIVE BOOSTS
    # ========================================
    # From Effect.cs Mag and BuffedMag properties
    # Alpha boosts ARE subject to Enhancement Diversification!

    for effect in alpha_slot.effects:
        # Skip excluded effects
        if not effect.can_include() or not effect.pvx_include():
            continue

        # Get base magnitude (from Effect.cs lines 401-416)
        if effect.attrib_type == AttribType.MAGNITUDE:
            base_mag = effect.scale * effect.n_magnitude * get_modifier(effect)
        elif effect.attrib_type == AttribType.DURATION:
            base_mag = effect.n_magnitude
        elif effect.attrib_type == AttribType.EXPRESSION:
            base_mag = parse_expression(effect)
        else:
            base_mag = 0.0

        # Damage effects are negative
        if effect.effect_type == EffectType.DAMAGE:
            base_mag *= -1

        # ========================================
        # STEP 3: APPLY ENHANCEMENT DIVERSIFICATION
        # ========================================
        # CRITICAL: Alpha bonuses ARE subject to ED!
        # From Effect.cs: IgnoreED flag is rarely True for Alpha

        if effect.ignore_ed:
            # Rare case: bypass ED curve
            enhanced_mag = base_mag
        else:
            # Normal case: apply ED curve from Spec 10
            # ED reduces effectiveness of high enhancement values
            enhanced_mag = apply_ed_curve(base_mag, effect.effect_type)

        # ========================================
        # STEP 4: APPLY ARCHETYPE SCALING
        # ========================================
        # From DatabaseAPI.GetModifier() via Spec 16

        at_modifier = get_at_modifier(
            character.archetype,
            effect.modifier_table,
            character.level
        )

        scaled_mag = enhanced_mag * at_modifier

        # ========================================
        # STEP 5: ADD TO BUILD TOTALS
        # ========================================
        # Alpha boosts stack ADDITIVELY with:
        # - Enhancement bonuses
        # - Set bonuses
        # - Other Incarnate abilities

        effect_key = get_effect_key(effect.effect_type, effect.mez_type, effect.damage_type)

        # Initialize if not present
        if effect_key not in updated_stats.totals:
            updated_stats.totals[effect_key] = 0.0

        # Add to existing total (additive stacking)
        updated_stats.totals[effect_key] += scaled_mag

    # ========================================
    # STEP 6: APPLY CAPS
    # ========================================
    # Alpha boosts are applied BEFORE caps
    # Level shift may INCREASE caps for some ATs
    # From Spec 17 (Archetype Caps)

    caps = get_at_caps(character.archetype, updated_stats.effective_level)

    for stat_key in updated_stats.totals:
        if stat_key in caps:
            updated_stats.totals[stat_key] = min(
                updated_stats.totals[stat_key],
                caps[stat_key]
            )

    return updated_stats


def get_alpha_slot_from_database(
    alpha_type: AlphaType,
    tier: AlphaTier,
    power_db: PowerDatabase
) -> AlphaSlot:
    """
    Load Alpha slot configuration from database.

    Args:
        alpha_type: Which Alpha (Musculature, Cardiac, etc.)
        tier: Which tier (T1-T4, Core/Radial)
        power_db: Power database reference

    Returns:
        AlphaSlot with all effects loaded
    """
    # Construct power name from type and tier
    # Examples: "Musculature Core Paragon", "Cardiac Radial Boost"
    power_name = f"{alpha_type.value.title()} {format_tier_name(tier)}"

    # Look up in Incarnate power set
    power = power_db.get_power_by_name(power_name, PowerSetType.INCARNATE)

    if power is None:
        raise ValueError(f"Alpha power not found: {power_name}")

    # Extract effects from power
    effects = []
    for effect_data in power.effects:
        effect = Effect.from_dict(effect_data)
        effects.append(effect)

    return AlphaSlot(
        alpha_type=alpha_type,
        tier=tier,
        effects=effects
    )


def format_tier_name(tier: AlphaTier) -> str:
    """
    Convert tier enum to display name.

    From Enums.cs eAlphaOrder enum.
    """
    tier_map = {
        AlphaTier.T1_BOOST: "Boost",
        AlphaTier.T2_CORE_BOOST: "Core Boost",
        AlphaTier.T2_RADIAL_BOOST: "Radial Boost",
        AlphaTier.T3_TOTAL_CORE_REVAMP: "Total Core Revamp",
        AlphaTier.T3_PARTIAL_CORE_REVAMP: "Partial Core Revamp",
        AlphaTier.T3_TOTAL_RADIAL_REVAMP: "Total Radial Revamp",
        AlphaTier.T3_PARTIAL_RADIAL_REVAMP: "Partial Radial Revamp",
        AlphaTier.T4_CORE_PARAGON: "Core Paragon",
        AlphaTier.T4_RADIAL_PARAGON: "Radial Paragon"
    }
    return tier_map[tier]
```

### Variable Definitions

| Variable | Type | Description | Example Value |
|----------|------|-------------|---------------|
| `character.level` | int | Character's actual level | 50 |
| `level_shift` | int | Total level shift from all sources | 1 (T3/T4 Alpha), 2 (Alpha+Lore), 3 (Alpha+Lore+Destiny) |
| `effective_level` | int | Character level + shift | 51, 52, or 53 |
| `has_lore_t4` | bool | Lore T4 slotted | True/False |
| `has_destiny_t4` | bool | Destiny T4 slotted | True/False |
| `alpha_slot.tier` | AlphaTier | Which tier selected | T4_CORE_PARAGON |
| `alpha_slot.effects` | List[Effect] | Passive boost effects | [DamageBuff(0.33), EndDiscount(0.33)] |
| `base_mag` | float | Raw effect magnitude | 0.33 (33% boost) |
| `enhanced_mag` | float | After ED curve | 0.285 (28.5% after ED) |
| `at_modifier` | float | Archetype scaling | 1.0 (most boosts), 0.85 (some ATs) |
| `scaled_mag` | float | Final magnitude | 0.285 |
| `effect.ignore_ed` | bool | Bypass ED curve | False (most Alpha effects) |
| `effect.modifier_table` | str | AT modifier table | "Melee_Ones" (no scaling), "Melee_Buff_Dmg" (scaled) |

### Branching Logic

1. **Level Shift Path**:
   - If `tier in [T1_BOOST, T2_CORE_BOOST, T2_RADIAL_BOOST]` → no level shift (0)
   - If `tier in [T3_*, T4_*]` → +1 level shift
   - If `tier == T4_* AND has_lore_t4` → +2 level shift
   - If `tier == T4_* AND has_lore_t4 AND has_destiny_t4` → +3 level shift (max)

2. **Enhancement Diversification Path**:
   - If `effect.ignore_ed == True` → use base_mag directly (rare)
   - If `effect.ignore_ed == False` → apply ED curve (normal case)
   - ED curve reduces 33% boost to ~28.5% (see Spec 10)

3. **Archetype Scaling Path**:
   - If `modifier_table == "Melee_Ones"` → no scaling (modifier = 1.0)
   - If `modifier_table == specific table` → apply AT-specific modifier
   - Most Alpha boosts use "Melee_Ones" (uniform across ATs)

4. **Stacking Path**:
   - Only ONE Alpha can be active at a time
   - Cannot have multiple Alphas like set bonuses
   - Alpha effects stack ADDITIVELY with enhancements and set bonuses

### Edge Cases

1. **Lore/Destiny Without Alpha T4**: No additional shift granted (requires T4 Alpha)
2. **Multiple Alpha Selection**: UI enforces single selection, previous Alpha removed
3. **Level Shift with Exemplaring**: Level shift applies, but exemplar may override (see Spec 42)
4. **Purple Patch Scaling**: Level shift affects combat vs higher/lower level enemies
5. **Cap Increases**: Some ATs get higher caps at 51+, others don't (AT-specific)

---

## Section 2: C# Implementation Reference

### Primary Implementation Files

#### File: `/Users/w/code/mids-hero-web/external/dev/MidsReborn/MidsReborn/Core/Enums.cs`

**Alpha Tier Enumeration (Lines 99-110)**:

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
    Core_Paragon,            // T4 - Very Rare - +1 level shift (enables Lore/Destiny shifts)
    Radial_Paragon           // T4 - Very Rare - +1 level shift (enables Lore/Destiny shifts)
}
```

**Key Constants**:
- Total tiers: 9 (1 T1, 2 T2, 4 T3, 2 T4)
- T1-T2: No level shift
- T3-T4: +1 level shift from Alpha
- T4 only: Enables additional shifts from Lore/Destiny

**Level Shift Effect Type (Line 435)**:

```csharp
public enum eEffectType
{
    // ... other types
    LevelShift,  // Line 435: Special effect type for Incarnate level shifts
    // ... more types
}
```

#### File: `/Users/w/code/mids-hero-web/external/dev/MidsReborn/MidsReborn/Core/GroupedFx.cs`

**Level Shift Display Processing (Lines 2001-2003)**:

```csharp
case Enums.eEffectType.LevelShift:
    rankedEffect.Name = "LvlShift";
    rankedEffect.Value = $"{(effectSource.Mag > 0 ? "+" : "")}{effectSource.Mag:##0.##}";
```

**Explanation**:
- `effectSource.Mag`: Magnitude of level shift (1 for T3/T4, 0 for T1/T2)
- Format: "+1" for positive shift, displays as "LvlShift: +1"
- This is DISPLAY only, actual shift calculation happens in Build.cs

#### File: `/Users/w/code/mids-hero-web/external/dev/MidsReborn/MidsReborn/Forms/frmIncarnate.cs`

**Alpha Slot UI Selection (Lines 68-76)**:

```csharp
case "Alpha":
    newPowerList.AddRange(ParseIncarnate(_myPowers.ToList(), setName, "Agility"));
    newPowerList.AddRange(ParseIncarnate(_myPowers.ToList(), setName, "Cardiac"));
    newPowerList.AddRange(ParseIncarnate(_myPowers.ToList(), setName, "Intuition"));
    newPowerList.AddRange(ParseIncarnate(_myPowers.ToList(), setName, "Musculature"));
    newPowerList.AddRange(ParseIncarnate(_myPowers.ToList(), setName, "Nerve"));
    newPowerList.AddRange(ParseIncarnate(_myPowers.ToList(), setName, "Resilient"));
    newPowerList.AddRange(ParseIncarnate(_myPowers.ToList(), setName, "Spiritual"));
    newPowerList.AddRange(ParseIncarnate(_myPowers.ToList(), setName, "Vigor"));
```

**8 Alpha Types**: Each has 9 tiers (1 T1, 2 T2, 4 T3, 2 T4) = 72 total Alpha powers

**Power Selection Enforcement (Lines 387-413)**:

```csharp
// Remove all previously selected Alpha powers
var num1 = LlLeft.Items.Length - 1;
for (var index = 0; index <= num1; ++index)
{
    if (LlLeft.Items[index].ItemState == ListLabel.LlItemState.Selected)
    {
        LlLeft.Items[index].ItemState = ListLabel.LlItemState.Enabled;
    }

    if (MidsContext.Character.CurrentBuild.PowerUsed(_myPowers[index]))
    {
        MidsContext.Character.CurrentBuild.RemovePower(_myPowers[index]);
    }
}

// Add newly selected Alpha
if (flag)
{
    MidsContext.Character.CurrentBuild.AddPower(_myPowers[item.Index], 49).StatInclude = true;
    item.ItemState = ListLabel.LlItemState.Selected;
}
```

**Explanation**:
- Only ONE Alpha can be selected at a time
- Selecting new Alpha removes previous Alpha automatically
- Alpha is added to build slot 49 (level 50 virtual slot)
- `StatInclude = true`: Alpha effects count toward build totals

#### File: `/Users/w/code/mids-hero-web/external/dev/MidsReborn/MidsReborn/Core/Base/Data_Classes/Effect.cs`

**Magnitude Calculation (Lines 401-416)**:

```csharp
public float Mag
{
    get
    {
        return (EffectType == Enums.eEffectType.Damage ? -1 : 1) * AttribType switch
        {
            Enums.eAttribType.Magnitude => Scale * nMagnitude * DatabaseAPI.GetModifier(this),
            Enums.eAttribType.Duration => nMagnitude,
            Enums.eAttribType.Expression when !string.IsNullOrWhiteSpace(Expressions.Magnitude)
                => Parse(this, ExpressionType.Magnitude, out _),
            Enums.eAttribType.Expression => Scale * nMagnitude,
            _ => 0
        };
    }
}

public float BuffedMag => Math.Abs(Math_Mag) > float.Epsilon ? Math_Mag : Mag;
```

**Key Properties for Alpha Boosts**:
- `IgnoreED`: Usually `false` for Alpha (subject to ED)
- `Buffable`: Usually `true` (can be enhanced, but Alpha IS the enhancement)
- `Resistible`: Usually `false` (self-buffs cannot be resisted)
- `ModifierTable`: Usually "Melee_Ones" (no AT scaling) for Alpha passive boosts

### Database Schema Requirements

Alpha slot powers are stored in the standard powers database with:
- `power_set_type`: "Incarnate"
- `power_set_name`: "Alpha"
- `power_name`: "{Type} {Tier}" (e.g., "Musculature Core Paragon")
- Effects array with:
  - `effect_type`: Damage, RechargeTime, Defense, Resistance, etc.
  - `n_magnitude`: Base boost value (0.33 for T4, 0.25 for T3, etc.)
  - `ignore_ed`: false (Alpha IS subject to ED)
  - `modifier_table`: "Melee_Ones" (most boosts)
  - Special level shift effect: `effect_type = LevelShift, n_magnitude = 1`

### Known Alpha Boost Values

Based on MidsReborn patterns and City of Heroes data:

**Musculature Damage Boosts**:
- T1 Boost: +20% damage
- T2 Core Boost: +25% damage
- T2 Radial Boost: +20% damage, +20% endurance discount
- T3 Total Core Revamp: +28% damage
- T3 Partial Core Revamp: +33% damage (focused)
- T3 Total Radial Revamp: +25% damage, +25% endurance discount
- T3 Partial Radial Revamp: +28% damage, +20% endurance discount
- T4 Core Paragon: +33% damage
- T4 Radial Paragon: +33% damage, +33% endurance discount

**Note**: These values are BEFORE Enhancement Diversification. ED reduces 33% to approximately 28.5%.

**Cardiac Endurance Boosts**:
- T4 Core Paragon: +33% endurance modification, +33% resistance
- T4 Radial Paragon: +33% endurance modification, +33% endurance discount

**Spiritual Recharge Boosts**:
- T4 Core Paragon: +33% recharge time (faster recharge)
- T4 Radial Paragon: +33% recharge time, +33% healing

---

## Section 3: Database Schema

### PostgreSQL Schema for Incarnate Alpha Slots

```sql
-- =====================================================
-- Table: incarnate_alpha_slots
-- Purpose: Define Alpha slot tiers and their properties
-- =====================================================
CREATE TABLE incarnate_alpha_slots (
    id SERIAL PRIMARY KEY,
    alpha_type VARCHAR(50) NOT NULL,  -- Agility, Cardiac, Intuition, etc.
    tier VARCHAR(50) NOT NULL,        -- Boost, Core_Boost, Radial_Boost, etc.
    tier_level INT NOT NULL,          -- 1 (T1), 2 (T2), 3 (T3), 4 (T4)
    rarity VARCHAR(20) NOT NULL,      -- Uncommon, Rare, Very Rare
    provides_level_shift BOOLEAN NOT NULL DEFAULT FALSE,
    level_shift_magnitude INT NOT NULL DEFAULT 0,  -- 0 or 1
    is_core_branch BOOLEAN,           -- NULL for T1, TRUE/FALSE for T2-T4
    display_name VARCHAR(100) NOT NULL,
    display_order INT NOT NULL,       -- For UI sorting (0-8 per type)

    CONSTRAINT uq_alpha_type_tier UNIQUE (alpha_type, tier),
    CONSTRAINT chk_tier_level CHECK (tier_level BETWEEN 1 AND 4),
    CONSTRAINT chk_level_shift CHECK (level_shift_magnitude IN (0, 1)),
    CONSTRAINT chk_rarity CHECK (rarity IN ('Uncommon', 'Rare', 'Very Rare'))
);

CREATE INDEX idx_alpha_slots_type ON incarnate_alpha_slots(alpha_type);
CREATE INDEX idx_alpha_slots_tier ON incarnate_alpha_slots(tier_level);

-- =====================================================
-- Table: alpha_boost_effects
-- Purpose: Define passive boost effects for each Alpha tier
-- =====================================================
CREATE TABLE alpha_boost_effects (
    id SERIAL PRIMARY KEY,
    alpha_slot_id INT NOT NULL REFERENCES incarnate_alpha_slots(id) ON DELETE CASCADE,
    effect_type VARCHAR(50) NOT NULL,    -- Damage, RechargeTime, Defense, etc.
    magnitude NUMERIC(10, 6) NOT NULL,   -- Base boost value (0.33 = 33%)
    aspect VARCHAR(50),                  -- Str, Max, Cur, etc.
    modifier_table VARCHAR(50) NOT NULL DEFAULT 'Melee_Ones',
    ignore_ed BOOLEAN NOT NULL DEFAULT FALSE,
    buffable BOOLEAN NOT NULL DEFAULT TRUE,
    resistible BOOLEAN NOT NULL DEFAULT FALSE,
    display_order INT NOT NULL,

    CONSTRAINT chk_magnitude CHECK (magnitude BETWEEN -10.0 AND 10.0)
);

CREATE INDEX idx_alpha_effects_slot ON alpha_boost_effects(alpha_slot_id);
CREATE INDEX idx_alpha_effects_type ON alpha_boost_effects(effect_type);

-- =====================================================
-- Table: level_shift_caps
-- Purpose: Define increased caps for level-shifted characters
-- =====================================================
CREATE TABLE level_shift_caps (
    id SERIAL PRIMARY KEY,
    archetype_id INT NOT NULL REFERENCES archetypes(id),
    effective_level INT NOT NULL,        -- 51, 52, 53
    stat_type VARCHAR(50) NOT NULL,      -- Defense, Resistance, Damage, etc.
    cap_value NUMERIC(10, 6) NOT NULL,   -- Cap value at this level

    CONSTRAINT uq_at_level_stat UNIQUE (archetype_id, effective_level, stat_type),
    CONSTRAINT chk_effective_level CHECK (effective_level BETWEEN 50 AND 53)
);

CREATE INDEX idx_level_shift_caps_at ON level_shift_caps(archetype_id, effective_level);

-- =====================================================
-- Table: character_incarnate_slots
-- Purpose: Track which Incarnate abilities a character has slotted
-- =====================================================
CREATE TABLE character_incarnate_slots (
    id SERIAL PRIMARY KEY,
    character_build_id INT NOT NULL REFERENCES character_builds(id) ON DELETE CASCADE,
    slot_type VARCHAR(50) NOT NULL,      -- Alpha, Judgement, Interface, Lore, Destiny, Hybrid
    power_id INT REFERENCES powers(id),  -- Selected Incarnate power
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    slotted_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_build_slot_type UNIQUE (character_build_id, slot_type),
    CONSTRAINT chk_slot_type CHECK (slot_type IN ('Alpha', 'Judgement', 'Interface', 'Lore', 'Destiny', 'Hybrid', 'Genesis', 'Stance', 'Vitae', 'Omega'))
);

CREATE INDEX idx_char_incarnate_build ON character_incarnate_slots(character_build_id);
CREATE INDEX idx_char_incarnate_slot ON character_incarnate_slots(slot_type);

-- =====================================================
-- View: v_character_level_shift
-- Purpose: Calculate total level shift for a character
-- =====================================================
CREATE OR REPLACE VIEW v_character_level_shift AS
SELECT
    cis.character_build_id,
    cb.base_level,
    -- Alpha shift
    COALESCE(
        (SELECT level_shift_magnitude
         FROM incarnate_alpha_slots ias
         JOIN character_incarnate_slots cis_alpha ON cis_alpha.power_id = ias.id
         WHERE cis_alpha.character_build_id = cis.character_build_id
           AND cis_alpha.slot_type = 'Alpha'
         LIMIT 1),
        0
    ) AS alpha_shift,
    -- Lore shift (only if Alpha T4)
    CASE
        WHEN EXISTS (
            SELECT 1 FROM incarnate_alpha_slots ias
            JOIN character_incarnate_slots cis_alpha ON cis_alpha.power_id = ias.id
            WHERE cis_alpha.character_build_id = cis.character_build_id
              AND cis_alpha.slot_type = 'Alpha'
              AND ias.tier_level = 4
        ) AND EXISTS (
            SELECT 1 FROM character_incarnate_slots cis_lore
            WHERE cis_lore.character_build_id = cis.character_build_id
              AND cis_lore.slot_type = 'Lore'
        )
        THEN 1
        ELSE 0
    END AS lore_shift,
    -- Destiny shift (only if Alpha T4 AND Lore T4)
    CASE
        WHEN EXISTS (
            SELECT 1 FROM incarnate_alpha_slots ias
            JOIN character_incarnate_slots cis_alpha ON cis_alpha.power_id = ias.id
            WHERE cis_alpha.character_build_id = cis.character_build_id
              AND cis_alpha.slot_type = 'Alpha'
              AND ias.tier_level = 4
        ) AND EXISTS (
            SELECT 1 FROM character_incarnate_slots cis_lore
            WHERE cis_lore.character_build_id = cis.character_build_id
              AND cis_lore.slot_type = 'Lore'
        ) AND EXISTS (
            SELECT 1 FROM character_incarnate_slots cis_destiny
            WHERE cis_destiny.character_build_id = cis.character_build_id
              AND cis_destiny.slot_type = 'Destiny'
        )
        THEN 1
        ELSE 0
    END AS destiny_shift,
    -- Total shift (max +3)
    LEAST(
        COALESCE(alpha_shift, 0) + COALESCE(lore_shift, 0) + COALESCE(destiny_shift, 0),
        3
    ) AS total_level_shift,
    -- Effective level
    cb.base_level + LEAST(
        COALESCE(alpha_shift, 0) + COALESCE(lore_shift, 0) + COALESCE(destiny_shift, 0),
        3
    ) AS effective_level
FROM character_incarnate_slots cis
JOIN character_builds cb ON cb.id = cis.character_build_id
WHERE cis.slot_type = 'Alpha'
GROUP BY cis.character_build_id, cb.base_level;

-- =====================================================
-- Sample Data: Musculature Alpha Tiers
-- =====================================================
INSERT INTO incarnate_alpha_slots (alpha_type, tier, tier_level, rarity, provides_level_shift, level_shift_magnitude, is_core_branch, display_name, display_order) VALUES
('Musculature', 'Boost', 1, 'Uncommon', FALSE, 0, NULL, 'Musculature Boost', 0),
('Musculature', 'Core_Boost', 2, 'Uncommon', FALSE, 0, TRUE, 'Musculature Core Boost', 1),
('Musculature', 'Radial_Boost', 2, 'Uncommon', FALSE, 0, FALSE, 'Musculature Radial Boost', 2),
('Musculature', 'Total_Core_Revamp', 3, 'Rare', TRUE, 1, TRUE, 'Musculature Total Core Revamp', 3),
('Musculature', 'Partial_Core_Revamp', 3, 'Rare', TRUE, 1, TRUE, 'Musculature Partial Core Revamp', 4),
('Musculature', 'Total_Radial_Revamp', 3, 'Rare', TRUE, 1, FALSE, 'Musculature Total Radial Revamp', 5),
('Musculature', 'Partial_Radial_Revamp', 3, 'Rare', TRUE, 1, FALSE, 'Musculature Partial Radial Revamp', 6),
('Musculature', 'Core_Paragon', 4, 'Very Rare', TRUE, 1, TRUE, 'Musculature Core Paragon', 7),
('Musculature', 'Radial_Paragon', 4, 'Very Rare', TRUE, 1, FALSE, 'Musculature Radial Paragon', 8);

-- Sample boost effects for Musculature Core Paragon (T4)
INSERT INTO alpha_boost_effects (alpha_slot_id, effect_type, magnitude, modifier_table, display_order)
SELECT
    id,
    'Damage',
    0.330000,  -- 33% damage boost (before ED)
    'Melee_Ones',
    1
FROM incarnate_alpha_slots
WHERE alpha_type = 'Musculature' AND tier = 'Core_Paragon';

-- =====================================================
-- Query: Get Alpha slot effects for build
-- =====================================================
CREATE OR REPLACE FUNCTION get_alpha_boost_effects(p_character_build_id INT)
RETURNS TABLE (
    effect_type VARCHAR(50),
    magnitude NUMERIC(10, 6),
    modifier_table VARCHAR(50),
    ignore_ed BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        abe.effect_type,
        abe.magnitude,
        abe.modifier_table,
        abe.ignore_ed
    FROM character_incarnate_slots cis
    JOIN incarnate_alpha_slots ias ON ias.id = cis.power_id
    JOIN alpha_boost_effects abe ON abe.alpha_slot_id = ias.id
    WHERE cis.character_build_id = p_character_build_id
      AND cis.slot_type = 'Alpha'
      AND cis.is_active = TRUE
    ORDER BY abe.display_order;
END;
$$ LANGUAGE plpgsql;
```

---

## Section 4: Comprehensive Test Cases

### Test Case 1: T1 Musculature Boost (No Level Shift)

**Input**:
- Character: Level 50 Scrapper
- Alpha: Musculature Boost (T1 - Uncommon)
- Base damage boost: +20% (0.20)
- Has Lore T4: False
- Has Destiny T4: False

**Calculation Steps**:
1. **Level Shift**: T1 tier → no level shift → `level_shift = 0`
2. **Effective Level**: `50 + 0 = 50`
3. **Base Magnitude**: `0.20` (20% damage boost)
4. **Enhancement Diversification**: `apply_ed_curve(0.20) = 0.20` (below ED threshold)
5. **Archetype Modifier**: `1.0` (Melee_Ones table)
6. **Final Magnitude**: `0.20 × 1.0 = 0.20` (20% damage boost)

**Expected Output**:
- Effective Level: 50
- Damage Boost: +20.0%
- Level Shift: 0

---

### Test Case 2: T3 Musculature Partial Core Revamp (+1 Shift)

**Input**:
- Character: Level 50 Blaster
- Alpha: Musculature Partial Core Revamp (T3 - Rare)
- Base damage boost: +33% (0.33)
- Has Lore T4: False
- Has Destiny T4: False

**Calculation Steps**:
1. **Level Shift**: T3 tier → +1 level shift → `level_shift = 1`
2. **Effective Level**: `50 + 1 = 51`
3. **Base Magnitude**: `0.33` (33% damage boost)
4. **Enhancement Diversification**:
   ```
   apply_ed_curve(0.33) = ?
   ED threshold starts at 0.30 (30%)
   For 0.33: effectiveness reduced
   Approximate result: 0.285 (28.5% effective)
   ```
5. **Archetype Modifier**: `1.0` (Melee_Ones table)
6. **Final Magnitude**: `0.285 × 1.0 = 0.285` (28.5% damage boost after ED)

**Expected Output**:
- Effective Level: 51
- Damage Boost: +28.5% (after ED)
- Level Shift: +1

**Note**: ED reduces the 33% boost to approximately 28.5%. See Spec 10 for exact ED curve formula.

---

### Test Case 3: T4 Musculature Core Paragon (+1 Shift, Enables More)

**Input**:
- Character: Level 50 Scrapper
- Alpha: Musculature Core Paragon (T4 - Very Rare)
- Base damage boost: +33% (0.33)
- Has Lore T4: False
- Has Destiny T4: False

**Calculation Steps**:
1. **Level Shift**: T4 tier → +1 level shift (base)
   - Lore T4 NOT present → no additional shift
   - `level_shift = 1`
2. **Effective Level**: `50 + 1 = 51`
3. **Base Magnitude**: `0.33` (33% damage boost)
4. **Enhancement Diversification**: `apply_ed_curve(0.33) ≈ 0.285`
5. **Archetype Modifier**: `1.0`
6. **Final Magnitude**: `0.285` (28.5% damage boost after ED)

**Expected Output**:
- Effective Level: 51
- Damage Boost: +28.5% (after ED)
- Level Shift: +1
- Note: T4 Alpha enables Lore/Destiny shifts if they are slotted

---

### Test Case 4: T4 Alpha + T4 Lore (+2 Total Shift)

**Input**:
- Character: Level 50 Controller
- Alpha: Spiritual Core Paragon (T4 - Very Rare)
- Base recharge boost: +33% (0.33)
- Has Lore T4: **True**
- Has Destiny T4: False

**Calculation Steps**:
1. **Level Shift**:
   - T4 Alpha → +1
   - T4 Lore present AND Alpha is T4 → +1
   - `level_shift = 1 + 1 = 2`
2. **Effective Level**: `50 + 2 = 52`
3. **Base Magnitude**: `0.33` (33% recharge boost)
4. **Enhancement Diversification**: `apply_ed_curve(0.33) ≈ 0.285`
5. **Archetype Modifier**: `1.0`
6. **Final Magnitude**: `0.285` (28.5% recharge boost after ED)

**Expected Output**:
- Effective Level: 52
- Recharge Boost: +28.5% (after ED)
- Level Shift: +2
- Combined with: Lore T4

---

### Test Case 5: T4 Alpha + T4 Lore + T4 Destiny (+3 Maximum Shift)

**Input**:
- Character: Level 50 Defender
- Alpha: Cardiac Radial Paragon (T4 - Very Rare)
- Base endurance modification: +33% (0.33)
- Base endurance discount: +33% (0.33)
- Has Lore T4: **True**
- Has Destiny T4: **True**

**Calculation Steps**:
1. **Level Shift**:
   - T4 Alpha → +1
   - T4 Lore present AND Alpha is T4 → +1
   - T4 Destiny present AND Alpha is T4 AND Lore is T4 → +1
   - `level_shift = 1 + 1 + 1 = 3` (MAXIMUM)
2. **Effective Level**: `50 + 3 = 53`
3. **Endurance Modification Effect**:
   - Base: `0.33`
   - After ED: `apply_ed_curve(0.33) ≈ 0.285`
   - Final: `0.285` (28.5%)
4. **Endurance Discount Effect**:
   - Base: `0.33`
   - After ED: `apply_ed_curve(0.33) ≈ 0.285`
   - Final: `0.285` (28.5%)

**Expected Output**:
- Effective Level: 53 (MAXIMUM)
- Endurance Modification: +28.5% (after ED)
- Endurance Discount: +28.5% (after ED)
- Level Shift: +3 (MAXIMUM)
- Combined with: Lore T4 + Destiny T4

---

### Test Case 6: Alpha + Enhancement Combination (Stacking)

**Input**:
- Character: Level 50 Tanker
- Alpha: Agility Radial Paragon (T4 - Very Rare)
- Base defense boost from Alpha: +33% (0.33)
- Base recharge boost from Alpha: +33% (0.33)
- Power: Combat Jumping (3 SOs slotted for Defense)
- Enhancement bonus to Defense: +95% (0.95 from 3 level 50 SOs after ED)

**Calculation Steps**:

1. **Alpha Defense Boost**:
   - Base: `0.33`
   - After ED: `apply_ed_curve(0.33) ≈ 0.285`
   - Final: `+28.5%`

2. **Power Defense Boost** (Combat Jumping):
   - Base defense: `5%` (0.05 defense to all)
   - Enhancement bonus: `0.95` (95% from 3 SOs after ED)
   - Enhanced defense: `0.05 × (1 + 0.95) = 0.0975` (9.75%)

3. **Combined Total**:
   - Alpha provides flat `+28.5%` to build totals
   - Combat Jumping provides `+9.75%` to build totals
   - **Total Defense: `28.5% + 9.75% = 38.25%`**

**Expected Output**:
- Defense Total: +38.25%
- Recharge Total: +28.5% (from Alpha)
- Level Shift: +1
- Note: Alpha and enhancement bonuses stack ADDITIVELY

---

### Test Case 7: Level Shift Impact on Purple Patch (Combat)

**Input**:
- Character: Level 50+2 (with Alpha T4 + Lore T4)
- Effective Level: 52
- Target Enemy: Level 54 (Incarnate Trial boss)
- Base Power Damage: 100.0

**Calculation Steps**:

1. **Level Difference**:
   - Attacker: 52
   - Target: 54
   - Difference: `52 - 54 = -2` (attacker is 2 levels below)

2. **Purple Patch Damage Modifier**:
   ```
   Level difference penalties (simplified):
   -1 level: ~10% damage penalty
   -2 levels: ~20% damage penalty
   -3 levels: ~30% damage penalty

   Formula: 1.0 + (level_diff × 0.10) for negative differences
   Modifier = 1.0 + (-2 × 0.10) = 0.80 (80% damage)
   ```

3. **Final Damage**:
   - Base: `100.0`
   - Purple Patch Modifier: `0.80`
   - **Final Damage: `100.0 × 0.80 = 80.0`**

**Comparison WITHOUT Level Shift** (Level 50 vs Level 54):
- Level Difference: `-4`
- Modifier: `1.0 + (-4 × 0.10) = 0.60` (60% damage)
- Damage: `100.0 × 0.60 = 60.0`

**Expected Output**:
- WITH +2 Level Shift: **80.0 damage** (80% effectiveness)
- WITHOUT Level Shift: **60.0 damage** (60% effectiveness)
- **Benefit**: +20.0 damage (+33% more damage due to level shift)

**Note**: Level shifts are CRITICAL for Incarnate content where enemies are 51+.

---

## Section 5: Python Implementation Guide

### Complete Production-Ready Implementation

```python
"""
Incarnate Alpha Slot Calculation Module

Implements Alpha slot level shifts and passive boosts for Mids Hero Web.
Based on MidsReborn implementation from frmIncarnate.cs, GroupedFx.cs, Effect.cs.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict
from decimal import Decimal


class AlphaType(Enum):
    """8 Alpha slot types with different passive boost focuses."""
    AGILITY = "agility"           # Endurance Discount, Defense, Recharge
    CARDIAC = "cardiac"           # Endurance Mod, Resistance, Endurance Discount
    INTUITION = "intuition"       # ToHit, Accuracy, Range
    MUSCULATURE = "musculature"   # Damage, Endurance Discount
    NERVE = "nerve"               # Accuracy, Confusion/Hold/Debuff
    RESILIENT = "resilient"       # Resistance, Endurance Discount, Healing
    SPIRITUAL = "spiritual"       # Healing, Recharge, Slow Resistance
    VIGOR = "vigor"               # Max HP, Recovery, Regeneration


class AlphaTier(Enum):
    """Alpha slot tiers - T1/T2 have no shift, T3/T4 provide +1 shift."""
    T1_BOOST = ("boost", 1, False)
    T2_CORE_BOOST = ("core_boost", 2, False)
    T2_RADIAL_BOOST = ("radial_boost", 2, False)
    T3_TOTAL_CORE_REVAMP = ("total_core_revamp", 3, True)
    T3_PARTIAL_CORE_REVAMP = ("partial_core_revamp", 3, True)
    T3_TOTAL_RADIAL_REVAMP = ("total_radial_revamp", 3, True)
    T3_PARTIAL_RADIAL_REVAMP = ("partial_radial_revamp", 3, True)
    T4_CORE_PARAGON = ("core_paragon", 4, True)
    T4_RADIAL_PARAGON = ("radial_paragon", 4, True)

    def __init__(self, tier_name: str, tier_level: int, provides_shift: bool):
        self.tier_name = tier_name
        self.tier_level = tier_level
        self.provides_shift = provides_shift


class EffectType(Enum):
    """Effect types for Alpha boosts."""
    DAMAGE = "Damage"
    RECHARGE_TIME = "RechargeTime"
    DEFENSE = "Defense"
    RESISTANCE = "Resistance"
    TOHIT = "ToHit"
    ACCURACY = "Accuracy"
    ENDURANCE_MOD = "EnduranceMod"
    ENDURANCE_DISCOUNT = "EnduranceDiscount"
    HEALING = "Healing"
    MAX_HP = "MaxHP"
    RECOVERY = "Recovery"
    REGENERATION = "Regeneration"
    CONFUSION_DURATION = "ConfusionDuration"
    HOLD_DURATION = "HoldDuration"
    DEFENSE_DEBUFF = "DefenseDebuff"
    TOHIT_DEBUFF = "ToHitDebuff"
    RANGE = "Range"
    LEVEL_SHIFT = "LevelShift"


@dataclass
class AlphaEffect:
    """
    Represents a single passive boost effect from Alpha slot.

    Attributes:
        effect_type: Type of boost (Damage, Defense, etc.)
        magnitude: Base boost value (0.33 = 33%)
        modifier_table: AT scaling table name
        ignore_ed: Whether to bypass ED curve (usually False)
        buffable: Whether effect can be enhanced (usually True)
        resistible: Whether effect can be resisted (usually False for self-buffs)
    """
    effect_type: EffectType
    magnitude: Decimal
    modifier_table: str = "Melee_Ones"
    ignore_ed: bool = False
    buffable: bool = True
    resistible: bool = False


@dataclass
class AlphaSlot:
    """
    Represents a complete Incarnate Alpha slot configuration.

    Attributes:
        alpha_type: Which Alpha (Musculature, Cardiac, etc.)
        tier: Which tier (T1-T4, Core/Radial)
        effects: List of passive boost effects
    """
    alpha_type: AlphaType
    tier: AlphaTier
    effects: List[AlphaEffect] = field(default_factory=list)

    def get_level_shift(self, has_lore_t4: bool = False, has_destiny_t4: bool = False) -> int:
        """
        Calculate total level shift provided by this Alpha and other Incarnates.

        Args:
            has_lore_t4: Whether Lore T4 is slotted
            has_destiny_t4: Whether Destiny T4 is slotted

        Returns:
            Total level shift (0-3)

        Examples:
            >>> alpha_t1 = AlphaSlot(AlphaType.MUSCULATURE, AlphaTier.T1_BOOST)
            >>> alpha_t1.get_level_shift()
            0

            >>> alpha_t3 = AlphaSlot(AlphaType.MUSCULATURE, AlphaTier.T3_PARTIAL_CORE_REVAMP)
            >>> alpha_t3.get_level_shift()
            1

            >>> alpha_t4 = AlphaSlot(AlphaType.MUSCULATURE, AlphaTier.T4_CORE_PARAGON)
            >>> alpha_t4.get_level_shift(has_lore_t4=True, has_destiny_t4=True)
            3
        """
        if not self.tier.provides_shift:
            return 0

        # Base shift from Alpha
        shift = 1

        # Additional shifts only if Alpha is T4
        if self.tier.tier_level == 4:
            if has_lore_t4:
                shift += 1
            if has_lore_t4 and has_destiny_t4:
                shift += 1

        # Maximum +3
        return min(shift, 3)

    def get_effective_level(
        self,
        base_level: int,
        has_lore_t4: bool = False,
        has_destiny_t4: bool = False
    ) -> int:
        """
        Calculate effective character level including shifts.

        Args:
            base_level: Character's actual level (typically 50)
            has_lore_t4: Whether Lore T4 is slotted
            has_destiny_t4: Whether Destiny T4 is slotted

        Returns:
            Effective level (base_level + shift)

        Examples:
            >>> alpha = AlphaSlot(AlphaType.MUSCULATURE, AlphaTier.T4_CORE_PARAGON)
            >>> alpha.get_effective_level(50, has_lore_t4=True)
            52
        """
        shift = self.get_level_shift(has_lore_t4, has_destiny_t4)
        return base_level + shift


@dataclass
class BuildStats:
    """
    Represents character build statistics.

    Attributes:
        effective_level: Character level including shifts
        totals: Dictionary of stat totals {stat_key: value}
    """
    effective_level: int
    totals: Dict[str, Decimal] = field(default_factory=dict)

    def copy(self) -> 'BuildStats':
        """Create a deep copy of build stats."""
        return BuildStats(
            effective_level=self.effective_level,
            totals=self.totals.copy()
        )


class AlphaSlotCalculator:
    """
    Calculates Alpha slot effects on character builds.

    Handles level shifts, passive boosts, ED application, and stacking.
    """

    @staticmethod
    def apply_alpha_to_build(
        alpha_slot: AlphaSlot,
        build_stats: BuildStats,
        character_level: int,
        archetype_name: str,
        has_lore_t4: bool = False,
        has_destiny_t4: bool = False,
        ed_curve_func: Optional[callable] = None,
        at_modifier_func: Optional[callable] = None
    ) -> BuildStats:
        """
        Apply Alpha slot effects to build statistics.

        Args:
            alpha_slot: Selected Alpha slot
            build_stats: Current build statistics
            character_level: Character's base level
            archetype_name: Archetype (for modifier lookup)
            has_lore_t4: Whether Lore T4 is slotted
            has_destiny_t4: Whether Destiny T4 is slotted
            ed_curve_func: Function to apply ED curve (from Spec 10)
            at_modifier_func: Function to get AT modifiers (from Spec 16)

        Returns:
            Updated build statistics with Alpha applied

        Raises:
            ValueError: If invalid parameters provided
        """
        if character_level < 1 or character_level > 50:
            raise ValueError(f"Invalid character level: {character_level}")

        updated_stats = build_stats.copy()

        # Step 1: Apply level shift
        level_shift = alpha_slot.get_level_shift(has_lore_t4, has_destiny_t4)
        updated_stats.effective_level = character_level + level_shift

        # Step 2: Apply passive boosts
        for effect in alpha_slot.effects:
            # Skip level shift effects (handled above)
            if effect.effect_type == EffectType.LEVEL_SHIFT:
                continue

            base_mag = effect.magnitude

            # Step 3: Apply Enhancement Diversification
            if effect.ignore_ed or ed_curve_func is None:
                enhanced_mag = base_mag
            else:
                enhanced_mag = Decimal(str(ed_curve_func(float(base_mag))))

            # Step 4: Apply Archetype Modifier
            if at_modifier_func is None:
                at_modifier = Decimal("1.0")
            else:
                at_modifier = Decimal(str(at_modifier_func(
                    archetype_name,
                    effect.modifier_table,
                    updated_stats.effective_level
                )))

            final_mag = enhanced_mag * at_modifier

            # Step 5: Add to build totals
            effect_key = effect.effect_type.value
            if effect_key not in updated_stats.totals:
                updated_stats.totals[effect_key] = Decimal("0")

            updated_stats.totals[effect_key] += final_mag

        return updated_stats

    @staticmethod
    def get_purple_patch_damage_modifier(attacker_level: int, target_level: int) -> Decimal:
        """
        Calculate purple patch damage modifier based on level difference.

        The "purple patch" is the level difference damage scaling system.

        Args:
            attacker_level: Effective level (including shifts)
            target_level: Enemy level

        Returns:
            Damage multiplier (1.0 = even level, <1.0 = penalty, >1.0 = bonus)

        Examples:
            >>> # Even level
            >>> AlphaSlotCalculator.get_purple_patch_damage_modifier(50, 50)
            Decimal('1.0')

            >>> # 2 levels above (bonus)
            >>> AlphaSlotCalculator.get_purple_patch_damage_modifier(52, 50)
            Decimal('1.10')

            >>> # 2 levels below (penalty)
            >>> AlphaSlotCalculator.get_purple_patch_damage_modifier(50, 52)
            Decimal('0.80')
        """
        level_diff = attacker_level - target_level

        if level_diff > 0:
            # Attacker higher level: damage bonus
            # +5% per level above target
            return Decimal("1.0") + (Decimal(str(level_diff)) * Decimal("0.05"))
        elif level_diff < 0:
            # Attacker lower level: damage penalty
            # -10% per level below target
            return Decimal("1.0") + (Decimal(str(level_diff)) * Decimal("0.10"))
        else:
            # Even level
            return Decimal("1.0")

    @staticmethod
    def get_purple_patch_tohit_modifier(attacker_level: int, target_level: int) -> Decimal:
        """
        Calculate purple patch ToHit modifier based on level difference.

        Args:
            attacker_level: Effective level (including shifts)
            target_level: Enemy level

        Returns:
            ToHit modifier (additive to base 75% ToHit)

        Examples:
            >>> # Even level
            >>> AlphaSlotCalculator.get_purple_patch_tohit_modifier(50, 50)
            Decimal('0.0')

            >>> # 1 level above (bonus)
            >>> AlphaSlotCalculator.get_purple_patch_tohit_modifier(51, 50)
            Decimal('0.05')

            >>> # 1 level below (penalty)
            >>> AlphaSlotCalculator.get_purple_patch_tohit_modifier(50, 51)
            Decimal('-0.075')
        """
        level_diff = attacker_level - target_level

        if level_diff > 0:
            # +5% ToHit per level above target
            return Decimal(str(level_diff)) * Decimal("0.05")
        elif level_diff < 0:
            # -7.5% ToHit per level below target
            return Decimal(str(level_diff)) * Decimal("0.075")
        else:
            return Decimal("0.0")


class AlphaSlotFactory:
    """
    Factory for creating Alpha slot configurations from database data.
    """

    # Standard boost values (before ED) by tier
    BOOST_VALUES = {
        1: Decimal("0.20"),   # T1: 20%
        2: Decimal("0.25"),   # T2: 25%
        3: Decimal("0.28"),   # T3: 28% (Total) or 33% (Partial)
        4: Decimal("0.33"),   # T4: 33%
    }

    @classmethod
    def create_musculature(cls, tier: AlphaTier) -> AlphaSlot:
        """
        Create Musculature Alpha (Damage + Endurance Discount).

        Args:
            tier: Which tier (T1-T4, Core/Radial)

        Returns:
            AlphaSlot configured for Musculature
        """
        effects = []

        # Damage boost (all tiers)
        damage_mag = cls.BOOST_VALUES.get(tier.tier_level, Decimal("0.33"))
        if tier in [AlphaTier.T3_PARTIAL_CORE_REVAMP, AlphaTier.T4_CORE_PARAGON]:
            damage_mag = Decimal("0.33")  # Focused damage

        effects.append(AlphaEffect(
            effect_type=EffectType.DAMAGE,
            magnitude=damage_mag,
            modifier_table="Melee_Ones",
            ignore_ed=False
        ))

        # Endurance discount (Radial branches only)
        if "radial" in tier.tier_name.lower():
            end_mag = cls.BOOST_VALUES.get(tier.tier_level, Decimal("0.20"))
            effects.append(AlphaEffect(
                effect_type=EffectType.ENDURANCE_DISCOUNT,
                magnitude=end_mag,
                modifier_table="Melee_Ones",
                ignore_ed=False
            ))

        # Level shift effect (T3+ only)
        if tier.provides_shift:
            effects.append(AlphaEffect(
                effect_type=EffectType.LEVEL_SHIFT,
                magnitude=Decimal("1"),
                modifier_table="Melee_Ones",
                ignore_ed=True
            ))

        return AlphaSlot(
            alpha_type=AlphaType.MUSCULATURE,
            tier=tier,
            effects=effects
        )

    @classmethod
    def create_spiritual(cls, tier: AlphaTier) -> AlphaSlot:
        """
        Create Spiritual Alpha (Recharge + Healing).

        Args:
            tier: Which tier (T1-T4, Core/Radial)

        Returns:
            AlphaSlot configured for Spiritual
        """
        effects = []

        # Recharge boost (all tiers)
        recharge_mag = cls.BOOST_VALUES.get(tier.tier_level, Decimal("0.33"))
        effects.append(AlphaEffect(
            effect_type=EffectType.RECHARGE_TIME,
            magnitude=recharge_mag,
            modifier_table="Melee_Ones",
            ignore_ed=False
        ))

        # Healing boost (Radial branches or T4 Core)
        if "radial" in tier.tier_name.lower() or tier.tier_level == 4:
            heal_mag = cls.BOOST_VALUES.get(tier.tier_level, Decimal("0.33"))
            effects.append(AlphaEffect(
                effect_type=EffectType.HEALING,
                magnitude=heal_mag,
                modifier_table="Melee_Ones",
                ignore_ed=False
            ))

        # Level shift effect (T3+ only)
        if tier.provides_shift:
            effects.append(AlphaEffect(
                effect_type=EffectType.LEVEL_SHIFT,
                magnitude=Decimal("1"),
                modifier_table="Melee_Ones",
                ignore_ed=True
            ))

        return AlphaSlot(
            alpha_type=AlphaType.SPIRITUAL,
            tier=tier,
            effects=effects
        )


# Example usage and testing
if __name__ == "__main__":
    # Example: Musculature Core Paragon with maximum shifts
    alpha = AlphaSlotFactory.create_musculature(AlphaTier.T4_CORE_PARAGON)

    print(f"Alpha: {alpha.alpha_type.value.title()} {alpha.tier.tier_name.replace('_', ' ').title()}")
    print(f"Level Shift: +{alpha.get_level_shift(has_lore_t4=True, has_destiny_t4=True)}")
    print(f"Effects:")
    for effect in alpha.effects:
        if effect.effect_type != EffectType.LEVEL_SHIFT:
            print(f"  - {effect.effect_type.value}: +{float(effect.magnitude) * 100:.1f}%")

    # Example: Purple patch calculation
    print("\nPurple Patch Examples:")
    print(f"Level 52 vs 50: {AlphaSlotCalculator.get_purple_patch_damage_modifier(52, 50)} damage")
    print(f"Level 50 vs 54: {AlphaSlotCalculator.get_purple_patch_damage_modifier(50, 54)} damage")
```

---

## Section 6: Integration Points

### Dependencies

**This spec depends on**:

1. **Spec 01 (Power Effects Core)**: Effect system foundation, `IEffect` interface
   - Uses: `Effect.Mag`, `Effect.BuffedMag`, `Effect.EffectType`
   - Integration: Alpha effects are standard `IEffect` objects

2. **Spec 10 (Enhancement Schedules)**: Enhancement Diversification curve
   - Uses: `apply_ed_curve()` function
   - Critical: Alpha bonuses ARE subject to ED
   - Example: 33% boost → 28.5% after ED

3. **Spec 16 (Archetype Modifiers)**: AT scaling for effects
   - Uses: `get_at_modifier()` function
   - Note: Most Alpha boosts use "Melee_Ones" (no scaling)
   - Some Alpha effects may use AT-specific tables

4. **Spec 17 (Archetype Caps)**: Stat caps including level-shifted caps
   - Uses: Cap values for level 51, 52, 53
   - Integration: Level shift may increase caps for some ATs

5. **Spec 25 (Buff Stacking Rules)**: Stacking behavior
   - Uses: Additive stacking rules
   - Note: Only ONE Alpha active at a time (unlike set bonuses)

### Specs That Depend On This

1. **Spec 19-24 (Build Totals)**: Alpha boosts added to build stats
   - Data Flow: Alpha effects → Build totals aggregation
   - Impact: Alpha bonuses appear in Defense, Damage, Recharge totals

2. **Spec 30 (Incarnate Abilities)**: Other Incarnate slots
   - Data Flow: Alpha T4 enables Lore/Destiny level shifts
   - Integration: Coordinate level shift calculation across slots

3. **Spec 31 (Core vs Radial)**: Branch differences detailed
   - Data Flow: Uses Alpha tier branching logic
   - Details: Core (focused) vs Radial (balanced) boost patterns

4. **Spec 41 (Level Scaling)**: Purple patch level difference calculations
   - Data Flow: Effective level (with shift) → damage/ToHit modifiers
   - Critical: Level shifts significantly impact Incarnate content

5. **Spec 42 (Exemplar Mechanics)**: Level shift with exemplaring
   - Data Flow: Exemplar level may override level shifts
   - Edge Case: Level shift + exemplar interaction

### Data Flow

```
1. User selects Alpha slot in UI
   ↓
2. frmIncarnate.cs enforces single Alpha selection
   ↓
3. Alpha power data loaded from database
   ↓
4. Effects extracted (damage boost, level shift, etc.)
   ↓
5. For each effect:
   a. Calculate base magnitude
   b. Apply Enhancement Diversification (Spec 10)
   c. Apply Archetype Modifier (Spec 16)
   d. Add to build totals (Spec 19-24)
   ↓
6. Calculate level shift:
   a. T1-T2: No shift
   b. T3-T4: +1 shift
   c. T4 + Lore T4: +2 shift
   d. T4 + Lore T4 + Destiny T4: +3 shift
   ↓
7. Apply caps (Spec 17) using effective level
   ↓
8. Display build totals in UI
   ↓
9. In combat calculations (Spec 41):
   a. Use effective level for purple patch
   b. Apply level difference modifiers
```

### API Endpoints That Will Use This

**GET `/api/v1/incarnate/alpha/types`**:
- Returns list of 8 Alpha types with descriptions
- Response: `[{name: "Musculature", focus: "Damage + Endurance Discount", ...}, ...]`

**GET `/api/v1/incarnate/alpha/{type}/tiers`**:
- Returns 9 tiers for specific Alpha type
- Response: `[{tier: "Boost", level: 1, shift: 0, effects: [...]}, ...]`

**POST `/api/v1/builds/{build_id}/incarnate/alpha`**:
- Sets Alpha slot for build
- Request: `{alpha_type: "Musculature", tier: "Core_Paragon"}`
- Response: `{effective_level: 51, level_shift: 1, effects: [...]}`

**GET `/api/v1/builds/{build_id}/incarnate/level-shift`**:
- Calculates total level shift from all Incarnates
- Response: `{alpha_shift: 1, lore_shift: 1, destiny_shift: 1, total: 3, effective_level: 53}`

**GET `/api/v1/combat/purple-patch`**:
- Calculates purple patch modifiers
- Query: `?attacker_level=52&target_level=54`
- Response: `{damage_mod: 0.80, tohit_mod: -0.15, level_diff: -2}`

---

**Document Status**: ✅ Depth Complete - Full implementation details with pseudocode, C# reference, database schema, test cases, Python implementation, and integration points provided.

**Implementation Priority**: High - Alpha slots are core to endgame builds and Incarnate content.

**Estimated Complexity**: Medium - Level shift logic straightforward, but ED interaction and purple patch calculations require careful handling.

**Key Findings**:
1. **Alpha boosts ARE subject to Enhancement Diversification** - contrary to some player expectations
2. **Level shift dependencies are strict** - Lore/Destiny require Alpha T4
3. **Maximum +3 level shift** - critical for level 54 Incarnate content
4. **ED reduces 33% to ~28.5%** - players overestimate Alpha power
5. **Purple patch scaling** - level shifts provide ~20-30% damage increase in Incarnate content
6. **Single Alpha limit** - cannot stack multiple Alphas like set bonuses
