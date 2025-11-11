# Power Healing and Absorption

## Overview
- **Purpose**: Calculate instant healing, regeneration rate, and temporary absorption HP from powers
- **Used By**: Healing powers, self-heal abilities, support powers, absorption shields
- **Complexity**: Moderate
- **Priority**: High
- **Status**: 🟡 Breadth Complete

## MidsReborn Implementation

### Primary Location
- **File**: `Core/Base/Data_Classes/Effect.cs`
- **Key Methods**: Effect type handling for `Heal`, `HitPoints`, `Regeneration`, `Absorb`
- **Display**: `Forms/Controls/DataView.cs` - Health statistics display
- **Calculation**: `Core/Statistics.cs` - HealthRegenPercent(), HealthRegenHPPerSec()

### Related Files
- `Core/Base/Data_Classes/Archetype.cs` - Base HP, HP caps, BaseRegen modifier
- `clsToonX.cs` - Build-wide health totals and absorption caps
- `Forms/WindowMenuItems/frmTotalsV2.cs` - Health display and calculations

### Effect Types

MidsReborn uses four distinct effect types for health mechanics:

**eEffectType.Heal**:
- Instant HP restoration (like Aid Self, Healing Aura)
- Magnitude is percentage of caster's max HP
- Displayed as: HP healed, % of base HP
- Example: Healing Aura = 10.42% HP heal

**eEffectType.HitPoints**:
- Increase/decrease maximum HP (like Dull Pain, Health)
- Magnitude is flat HP value or percentage
- Subject to archetype HP caps
- Example: Dull Pain = +40% max HP

**eEffectType.Regeneration**:
- Continuous HP recovery over time
- Magnitude is regeneration percentage modifier
- Interacts with BaseRegen archetype modifier
- Example: Fast Healing = +75% regeneration

**eEffectType.Absorb**:
- Temporary HP shield that absorbs damage
- Magnitude is flat HP value
- Capped at character's current max HP
- Does not stack, usually takes highest value
- Example: Barrier Destiny = 600 absorption

### High-Level Algorithm

```
Instant Heal Calculation (eEffectType.Heal):
  1. Sum all Heal effect magnitudes from power
  2. Convert to HP value:
     HealAmount = Sum(HealMag) / 100.0 * MaxHP
  3. Apply to target (capped at MaxHP)
  4. Display as: "{HealAmount} HP ({HealMag}% of base)"

Example (Healing Aura on Tanker with 2409 HP):
  - Base magnitude: 10.42%
  - With enhancements: 16.26%
  - HP healed = 16.26% * 2409 = 391.7 HP

Maximum HP Calculation (eEffectType.HitPoints):
  1. Sum all HitPoints effect magnitudes
  2. Apply to base HP:
     MaxHP = BaseHP + Sum(HPBonus)
  3. Apply archetype cap:
     CappedHP = min(MaxHP, ArchetypeHPCap)
  4. Cap absorption at capped max HP:
     Absorb = min(Absorb, CappedHP)

Example (Tanker with Dull Pain):
  - Base HP: 1874.1
  - Dull Pain bonus: +40% = +749.6 HP
  - Total: 2623.7 HP
  - Cap check: 2623.7 < 3534.0 (cap), OK

Regeneration Rate Calculation (eEffectType.Regeneration):
  1. Sum all regeneration modifiers:
     TotalRegen = 1.0 + Sum(RegenEffects)

  2. Calculate percentage per second:
     RegenPercentPerSec = TotalRegen * BaseRegen * BaseMagic
     where BaseMagic = 1.666667 (converts to %/sec)

  3. Calculate HP recovered per second:
     HPPerSec = RegenPercentPerSec * MaxHP / 100.0

  4. Calculate time to full health:
     TimeToFull = MaxHP / HPPerSec

Example (Scrapper with Health + Fast Healing):
  - Base regeneration: 100%
  - Health: +40%
  - Fast Healing: +75%
  - Total regen: 215% (1.0 + 0.40 + 0.75 = 2.15)
  - BaseRegen: 1.0 (standard for most ATs)
  - RegenPercentPerSec = 2.15 * 1.0 * 1.666667 = 3.583%/s
  - With 1339 HP: HPPerSec = 3.583% * 1339 / 100 = 47.97 HP/s
  - Time to full: 1339 / 47.97 = 27.9 seconds

Absorption Calculation (eEffectType.Absorb):
  1. Collect all absorption effects
  2. Apply stacking rule (typically highest value wins):
     FinalAbsorb = max(AllAbsorbEffects)
  3. Cap at max HP:
     CappedAbsorb = min(FinalAbsorb, MaxHP)
  4. Display as flat HP and % of base HP

Example (Defender with multiple shields):
  - Barrier Destiny: 600 absorb
  - Power Boost effect: 400 absorb
  - Take highest: 600 absorb
  - Base HP: 1017.4
  - Display: "600 HP (59% of base HP)"
```

### Dependencies

**Archetype Properties**:
- `Archetype.Hitpoints` - Base HP at level 50
- `Archetype.HPCap` - Maximum HP cap (varies by AT)
- `Archetype.BaseRegen` - Regen multiplier (usually 1.0, higher for Tankers/Brutes)

**Constants**:
- `BaseMagic = 1.666667` - Converts regen to %/sec (from Statistics.cs)
- This constant represents the game's base regeneration tick rate

**Power Properties**:
- Heal effects use Aspect.Cur (current HP modification)
- HitPoints effects use Aspect.Max (maximum HP modification)
- Magnitude values are percentages (need /100 for calculation)

**Display Calculations**:
```csharp
// From Core/Statistics.cs
HealthRegenHealthPerSec = HealthRegen(false) * BaseRegen * 1.66666662693024
HealthRegenHPPerSec = HealthRegenHealthPerSec * HealthHitpointsNumeric(false) / 100.0
HealthRegenTimeToFull = HealthHitpointsNumeric(false) / HealthRegenHPPerSec

// Absorption display (from Forms/ImportExportItems/ShareMenu.cs)
AbsorbPercent = Absorb / BaseHP * 100.0
Display = "{Absorb:##0.##} HP ({AbsorbPercent:##0.##}% of base HP)"
```

### Enhancement Scaling

Healing and absorption effects are enhanced by:
- **Heal enhancements** - Affect Heal magnitude directly
- **Healing sets** - Provide Heal enhancement and set bonuses
- **Regeneration enhancements** - Affect Regeneration effects
- **Max HP bonuses** - From set bonuses, increase heal effectiveness indirectly

```
Enhanced Heal Calculation:
  BaseHeal = 10.42%
  HealEnhancement = 1.56 (56% from slotting)
  EnhancedHeal = 10.42% * 1.56 = 16.26%
  HPRestored = 16.26% * MaxHP
```

## Game Mechanics Context

**Why This Exists:**

City of Heroes uses percentage-based healing to keep powers relevant across all levels and different archetypes. A heal that restores 20% HP works equally well for a Defender with 1000 HP and a Tanker with 2400 HP.

**Three Healing Mechanisms:**

1. **Instant Heals (Heal)**: Restore HP immediately, used by active healing powers
2. **Regeneration**: Passive continuous recovery, from toggles and auto powers
3. **Absorption**: Temporary HP buffer that takes damage before real HP

**Historical Context:**

- **Launch (2004)**: Basic heal and regeneration mechanics
- **Issue 5 (2005)**: Enhancement Diversification reduced heal slotting effectiveness
- **Issue 9 (2006)**: Invention sets added +MaxHP and +Regen bonuses
- **Issue 18 (2010)**: Incarnate system added powerful absorption effects (Barrier Destiny)
- **Homecoming (2019+)**: Absorption became more common in new powersets

**Known Quirks:**

1. **Percentage-based healing**: All heals are percentage of MAX HP, not base HP. This means a character with +40% max HP buffs gets proportionally larger heals.

2. **Regeneration tick rate**: The constant 1.666667 represents the game's regeneration tick cycle. At 100% regen, you recover 100% HP every 240 seconds, which is 1.666667% per 4-second tick.

3. **Absorption doesn't stack**: Unlike most buffs, absorption typically takes the highest value rather than stacking additively. Multiple absorption shields don't combine.

4. **Absorption cap**: Absorption is capped at your current maximum HP. You can't have 5000 absorb points if you only have 2000 max HP.

5. **Self-heal percentage**: Powers like Aid Self heal based on the CASTER's max HP, not the target's. This makes support characters' heals scale with their own HP, not the target's.

6. **Regeneration debuff resistance**: The `ResEffect` with `ETModifies = Regeneration` allows resistance to regeneration debuffs (common in enemy powers).

7. **BaseRegen archetype modifier**: Most ATs have BaseRegen = 1.0, but Tankers, Brutes, and some others have different values affecting their base regeneration rate.

8. **Heal over Time (HoT)**: Some powers deliver heals via the `Absorbed_Duration` and `Absorbed_Interval` mechanics, creating heal-over-time effects that tick at intervals.

## Python Implementation Notes

**Proposed Architecture:**

```python
# backend/app/calculations/healing.py

from dataclasses import dataclass
from typing import Optional
from .effects import Effect, EffectType

@dataclass
class ArchetypeHealthStats:
    """Health-related archetype properties"""
    base_hitpoints: float  # Base HP at level 50
    hp_cap: float  # Maximum HP cap
    base_regen: float = 1.0  # Regeneration multiplier

# Game constant from Statistics.cs
BASE_MAGIC = 1.666667  # Converts regen to %/sec

class HealingCalculator:
    """
    Calculate healing, regeneration, and absorption effects
    Maps to MidsReborn's Statistics.cs health calculations
    """

    def calculate_instant_heal(
        self,
        heal_effects: list[Effect],
        max_hp: float
    ) -> float:
        """
        Calculate instant HP restoration from Heal effects

        Args:
            heal_effects: List of eEffectType.Heal effects
            max_hp: Character's current maximum HP

        Returns:
            HP restored (capped at max_hp)
        """
        # Sum heal magnitudes (percentages)
        total_heal_pct = sum(e.magnitude for e in heal_effects)

        # Convert to HP value
        heal_amount = (total_heal_pct / 100.0) * max_hp

        # Cap at max HP
        return min(heal_amount, max_hp)

    def calculate_max_hp(
        self,
        at_stats: ArchetypeHealthStats,
        hp_effects: list[Effect]
    ) -> tuple[float, float]:
        """
        Calculate maximum HP from HitPoints effects

        Args:
            at_stats: Archetype health statistics
            hp_effects: List of eEffectType.HitPoints effects

        Returns:
            (uncapped_hp, capped_hp)
        """
        # Start with base HP
        max_hp = at_stats.base_hitpoints

        # Apply all HP bonuses
        for effect in hp_effects:
            max_hp += effect.magnitude

        # Apply archetype cap
        capped_hp = min(max_hp, at_stats.hp_cap)

        return (max_hp, capped_hp)

    def calculate_regeneration(
        self,
        at_stats: ArchetypeHealthStats,
        regen_effects: list[Effect],
        max_hp: float
    ) -> dict:
        """
        Calculate regeneration rate

        Args:
            at_stats: Archetype health statistics
            regen_effects: List of eEffectType.Regeneration effects
            max_hp: Character's current maximum HP

        Returns:
            Dictionary with:
            - regen_total: Total regen percentage (e.g., 2.15 = 215%)
            - regen_percent_per_sec: % regenerated per second
            - hp_per_sec: HP regenerated per second
            - time_to_full: Seconds to regenerate from 0 to max HP
        """
        # Start at 100% base regeneration
        regen_total = 1.0

        # Add all regeneration modifiers
        for effect in regen_effects:
            regen_total += effect.magnitude

        # Calculate % per second
        regen_percent_per_sec = regen_total * at_stats.base_regen * BASE_MAGIC

        # Calculate HP per second
        hp_per_sec = (regen_percent_per_sec * max_hp) / 100.0

        # Calculate time to full
        time_to_full = max_hp / hp_per_sec if hp_per_sec > 0 else float('inf')

        return {
            'regen_total': regen_total,
            'regen_percent_per_sec': regen_percent_per_sec,
            'hp_per_sec': hp_per_sec,
            'time_to_full': time_to_full
        }

    def calculate_absorption(
        self,
        absorb_effects: list[Effect],
        max_hp: float
    ) -> dict:
        """
        Calculate absorption (temporary HP)

        Args:
            absorb_effects: List of eEffectType.Absorb effects
            max_hp: Character's current maximum HP

        Returns:
            Dictionary with:
            - absorb_amount: Absorption HP
            - absorb_percent: As percentage of base HP
        """
        # Absorption typically doesn't stack - take highest value
        absorb_amount = max((e.magnitude for e in absorb_effects), default=0.0)

        # Cap at max HP
        absorb_amount = min(absorb_amount, max_hp)

        # Calculate percentage (for display)
        absorb_percent = (absorb_amount / max_hp * 100.0) if max_hp > 0 else 0.0

        return {
            'absorb_amount': absorb_amount,
            'absorb_percent': absorb_percent
        }

    def format_heal_display(
        self,
        heal_amount: float,
        heal_percent: float,
        base_hp: float
    ) -> str:
        """
        Format heal for display matching MidsReborn style

        Returns:
            "{HP} HP ({%} of base HP)"
        """
        percent_of_base = (heal_amount / base_hp * 100.0) if base_hp > 0 else 0.0
        return f"{heal_amount:.2f} HP ({percent_of_base:.2f}% of base HP)"
```

**Implementation Priority:**

**HIGH** - Healing calculations are essential for support builds and survivability planning.

**Key Implementation Steps:**

1. Implement ArchetypeHealthStats dataclass with base HP and caps
2. Create HealingCalculator.calculate_instant_heal() for Heal effects
3. Create HealingCalculator.calculate_max_hp() for HitPoints effects
4. Create HealingCalculator.calculate_regeneration() with BASE_MAGIC constant
5. Create HealingCalculator.calculate_absorption() with stacking rules
6. Add display formatting methods matching MidsReborn output
7. Integration with archetype data from Spec 16
8. Integration with enhancement system from Spec 10-11

**Testing Strategy:**

Test cases to validate against MidsReborn:

1. **Instant Heal Test**:
   - Power: Healing Aura (10.42% base)
   - Character: Defender with 1017 base HP
   - No enhancements: 106.07 HP
   - With 3x Heal SOs (95.66%): 207.55 HP

2. **Max HP Test**:
   - Power: Dull Pain (+40% HP)
   - Character: Tanker with 1874.1 base HP, 3534.0 cap
   - Result: 2623.7 HP (under cap)

3. **Regeneration Test**:
   - Powers: Health (+40%), Fast Healing (+75%)
   - Character: Scrapper with 1339 HP
   - Total regen: 215%
   - HP/sec: 47.97
   - Time to full: 27.9 seconds

4. **Absorption Test**:
   - Power: Barrier Destiny (600 absorb)
   - Character: Defender with 1017 base HP
   - Result: 600 HP (59% of base)

5. **Multi-source Test**:
   - Multiple heal powers active
   - Multiple regen sources stacking
   - Multiple absorption shields (highest wins)

## References

- **Related Specs**:
  - Spec 01 (Power Effects Core) - Effect system foundation
  - Spec 16 (Archetype Stats) - Base HP, caps, BaseRegen
  - Spec 10-11 (Enhancements) - Heal enhancement scaling
  - Spec 19 (Build Totals) - Aggregating health stats across build
- **MidsReborn Files**:
  - `Core/Statistics.cs` (lines 83-92) - Regen calculations
  - `Core/Base/Data_Classes/Effect.cs` - Heal/Regen/Absorb effect handling
  - `Core/Base/Data_Classes/Archetype.cs` - HP caps and BaseRegen
  - `clsToonX.cs` - Build-wide health totals
- **Game Documentation**:
  - City of Heroes Wiki - "Healing", "Regeneration", "Hit Points"
  - Paragon Wiki - "Absorption", "Maximum HP"

---

# DEPTH-LEVEL IMPLEMENTATION DETAILS

## Section 1: Algorithm Pseudocode

### Complete Healing/Absorption Algorithm

```python
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

# Constants from MidsReborn
BASE_MAGIC = 1.666667  # From Statistics.cs line 22
DEFAULT_HP_CAP = 5000.0  # From Archetype.cs line 44
DEFAULT_REGEN_CAP = 20.0  # 2000% = 20x base
DEFAULT_BASE_REGEN = 1.0  # Most ATs

@dataclass
class ArchetypeHealthStats:
    """Archetype health properties from Archetype.cs"""
    base_hitpoints: float  # Hitpoints property (varies by AT)
    hp_cap: float  # HPCap property (max HP limit)
    base_regen: float  # BaseRegen multiplier (usually 1.0)
    regen_cap: float  # RegenCap (2000-3000%)

@dataclass
class HealEffect:
    """eEffectType.Heal effect"""
    magnitude: float  # Percentage of max HP (e.g., 10.42 for 10.42%)
    buffed_magnitude: Optional[float]  # After enhancements
    duration: float  # 0 = instant
    probability: float  # 1.0 = always
    display_percentage: bool  # True for percentage display

@dataclass
class HitPointsEffect:
    """eEffectType.HitPoints (MaxHP modifier)"""
    magnitude: float  # Flat HP value or percentage
    display_percentage: bool  # True if percentage-based

@dataclass
class RegenerationEffect:
    """eEffectType.Regeneration effect"""
    magnitude: float  # Percentage modifier (e.g., 0.75 for +75%)
    buffed_magnitude: Optional[float]  # After enhancements

@dataclass
class AbsorbEffect:
    """eEffectType.Absorb effect"""
    magnitude: float  # Flat HP value or percentage
    display_percentage: bool  # True if percentage-based

# ============================================================================
# INSTANT HEAL CALCULATION
# ============================================================================

def calculate_instant_heal(
    heal_effects: List[HealEffect],
    max_hp: float,
    current_hp: float
) -> dict:
    """
    Calculate instant HP restoration from Heal effects.

    Maps to MidsReborn's eEffectType.Heal handling.
    Heal magnitude is percentage of MAX HP (not base HP).

    Args:
        heal_effects: List of Heal effects from power
        max_hp: Character's current maximum HP (after +MaxHP buffs)
        current_hp: Current HP before heal

    Returns:
        {
            'heal_magnitude_pct': Total heal percentage,
            'heal_amount': HP restored,
            'new_hp': Current HP after heal (capped at max_hp),
            'overheal': Amount over max HP (wasted)
        }
    """
    # Step 1: Sum all heal magnitudes
    total_heal_pct = 0.0
    for effect in heal_effects:
        # Use enhanced magnitude if available
        mag = effect.buffed_magnitude if effect.buffed_magnitude else effect.magnitude

        # Apply probability for proc heals
        if effect.probability < 1.0:
            mag *= effect.probability  # Expected value

        total_heal_pct += mag

    # Step 2: Convert percentage to HP value
    # Formula from MidsReborn: HealAmount = (TotalPct / 100.0) * MaxHP
    heal_amount = (total_heal_pct / 100.0) * max_hp

    # Step 3: Apply to current HP
    new_hp = current_hp + heal_amount

    # Step 4: Cap at max HP
    if new_hp > max_hp:
        overheal = new_hp - max_hp
        new_hp = max_hp
    else:
        overheal = 0.0

    return {
        'heal_magnitude_pct': total_heal_pct,
        'heal_amount': heal_amount,
        'new_hp': new_hp,
        'overheal': overheal
    }

# ============================================================================
# MAXIMUM HP CALCULATION
# ============================================================================

def calculate_max_hp(
    at_stats: ArchetypeHealthStats,
    hp_effects: List[HitPointsEffect]
) -> dict:
    """
    Calculate maximum HP from HitPoints effects.

    Maps to MidsReborn's eEffectType.HitPoints (enum value 14).
    From clsToonX.cs line 817:
        Totals.HPMax = _selfBuffs.Effect[(int)Enums.eStatType.HPMax] + Archetype.Hitpoints

    Args:
        at_stats: Archetype health statistics
        hp_effects: List of HitPoints effects (from powers, sets, accolades)

    Returns:
        {
            'base_hp': Archetype base HP,
            'hp_bonus': Total HP bonus from effects,
            'uncapped_hp': HP before cap,
            'capped_hp': HP after archetype cap,
            'over_cap': Amount over cap (wasted)
        }
    """
    # Step 1: Start with archetype base HP
    base_hp = at_stats.base_hitpoints

    # Step 2: Sum all HP bonuses
    hp_bonus = 0.0
    for effect in hp_effects:
        mag = effect.magnitude

        # If percentage-based, convert to flat value
        if effect.display_percentage:
            mag = (mag / 100.0) * base_hp

        hp_bonus += mag

    # Step 3: Calculate uncapped total
    uncapped_hp = base_hp + hp_bonus

    # Step 4: Apply archetype cap
    # From clsToonX.cs line 873:
    #   if (Archetype.HPCap > 0)
    #       TotalsCapped.HPMax = Math.Min(TotalsCapped.HPMax, Archetype.HPCap)
    if at_stats.hp_cap > 0:
        capped_hp = min(uncapped_hp, at_stats.hp_cap)
        over_cap = uncapped_hp - capped_hp if uncapped_hp > capped_hp else 0.0
    else:
        capped_hp = uncapped_hp
        over_cap = 0.0

    return {
        'base_hp': base_hp,
        'hp_bonus': hp_bonus,
        'uncapped_hp': uncapped_hp,
        'capped_hp': capped_hp,
        'over_cap': over_cap
    }

# ============================================================================
# REGENERATION CALCULATION
# ============================================================================

def calculate_regeneration(
    at_stats: ArchetypeHealthStats,
    regen_effects: List[RegenerationEffect],
    max_hp: float
) -> dict:
    """
    Calculate regeneration rate.

    Maps to MidsReborn's eEffectType.Regeneration (enum value 27).
    From Statistics.cs lines 53-57:
        HealthRegenHealthPerSec = HealthRegen * BaseRegen * 1.66666662693024
        HealthRegenHPPerSec = HealthRegenHealthPerSec * HealthHitpointsNumeric / 100.0
        HealthRegenTimeToFull = HealthHitpointsNumeric / HealthRegenHPPerSec

    BASE_MAGIC constant (1.666667) converts regen to %/sec:
        - Base regeneration: 100% HP per 240 seconds
        - Per 4-second tick: 100% / 60 ticks = 1.666667% per tick
        - Per second: 1.666667% / 4 seconds = 0.41666% per second

    Args:
        at_stats: Archetype health statistics (includes BaseRegen modifier)
        regen_effects: List of Regeneration effects
        max_hp: Character's current maximum HP

    Returns:
        {
            'regen_total': Total regen multiplier (e.g., 2.15 = 215%),
            'regen_percent_per_sec': % HP regenerated per second,
            'hp_per_sec': HP regenerated per second,
            'time_to_full': Seconds to regenerate from 0 to max HP,
            'hp_per_tick': HP per 4-second game tick
        }
    """
    # Step 1: Start at 100% base regeneration
    regen_total = 1.0

    # Step 2: Add all regeneration modifiers
    for effect in regen_effects:
        # Use enhanced magnitude if available
        mag = effect.buffed_magnitude if effect.buffed_magnitude else effect.magnitude
        regen_total += mag

    # Step 3: Calculate % per second
    # Formula from Statistics.cs line 53:
    #   RegenPercentPerSec = RegenTotal * BaseRegen * BASE_MAGIC
    regen_percent_per_sec = regen_total * at_stats.base_regen * BASE_MAGIC

    # Step 4: Calculate HP per second
    # Formula from Statistics.cs line 55:
    #   HPPerSec = RegenPercentPerSec * MaxHP / 100.0
    hp_per_sec = (regen_percent_per_sec * max_hp) / 100.0

    # Step 5: Calculate time to full HP
    # Formula from Statistics.cs line 57:
    #   TimeToFull = MaxHP / HPPerSec
    if hp_per_sec > 0:
        time_to_full = max_hp / hp_per_sec
    else:
        time_to_full = float('inf')  # No regeneration

    # Step 6: Calculate HP per 4-second tick (for display)
    hp_per_tick = hp_per_sec * 4.0

    return {
        'regen_total': regen_total,
        'regen_percent_per_sec': regen_percent_per_sec,
        'hp_per_sec': hp_per_sec,
        'time_to_full': time_to_full,
        'hp_per_tick': hp_per_tick
    }

# ============================================================================
# ABSORPTION CALCULATION
# ============================================================================

def calculate_absorption(
    absorb_effects: List[AbsorbEffect],
    max_hp: float,
    base_hp: float
) -> dict:
    """
    Calculate absorption (temporary HP).

    Maps to MidsReborn's eEffectType.Absorb (enum value 66).
    From clsToonX.cs lines 688-691:
        if (index1 == (int)Enums.eStatType.Absorb & effect.DisplayPercentage)
            shortFx.Value[shortFxIdx] *= MidsContext.Character.Totals.HPMax

    From clsToonX.cs line 874:
        TotalsCapped.Absorb = Math.Min(TotalsCapped.Absorb, TotalsCapped.HPMax)

    Absorption rules:
    1. Typically does NOT stack - highest value wins
    2. Capped at current max HP
    3. Takes damage before real HP
    4. Some effects are percentage-based, converted to flat value

    Args:
        absorb_effects: List of Absorb effects
        max_hp: Character's current maximum HP (capped)
        base_hp: Archetype base HP (for percentage display)

    Returns:
        {
            'absorb_amount': Absorption HP (flat value),
            'absorb_percent_base': As percentage of base HP,
            'absorb_percent_max': As percentage of current max HP,
            'capped': True if absorption was capped at max HP
        }
    """
    # Step 1: Process all absorption effects
    absorb_values = []
    for effect in absorb_effects:
        mag = effect.magnitude

        # If percentage-based, convert to flat value
        # Uses current max HP, not base HP (clsToonX.cs line 690)
        if effect.display_percentage:
            mag = (mag / 100.0) * max_hp

        absorb_values.append(mag)

    # Step 2: Apply stacking rule - take highest value
    # (Most absorption effects don't stack additively)
    if len(absorb_values) > 0:
        absorb_amount = max(absorb_values)
    else:
        absorb_amount = 0.0

    # Step 3: Cap at max HP
    # From clsToonX.cs line 874:
    #   TotalsCapped.Absorb = Math.Min(TotalsCapped.Absorb, TotalsCapped.HPMax)
    capped = False
    if absorb_amount > max_hp:
        absorb_amount = max_hp
        capped = True

    # Step 4: Calculate percentages for display
    absorb_percent_base = (absorb_amount / base_hp * 100.0) if base_hp > 0 else 0.0
    absorb_percent_max = (absorb_amount / max_hp * 100.0) if max_hp > 0 else 0.0

    return {
        'absorb_amount': absorb_amount,
        'absorb_percent_base': absorb_percent_base,
        'absorb_percent_max': absorb_percent_max,
        'capped': capped
    }

# ============================================================================
# EDGE CASES
# ============================================================================

def handle_heal_over_time(
    heal_effect: HealEffect,
    max_hp: float,
    duration: float,
    tick_interval: float = 2.0
) -> dict:
    """
    Handle Heal over Time (HoT) effects.

    Some powers deliver heals via ticks over duration:
    - Absorbed_Duration: Total effect duration
    - Absorbed_Interval: Time between ticks

    Args:
        heal_effect: Base heal effect
        max_hp: Maximum HP
        duration: Total effect duration in seconds
        tick_interval: Seconds between heal ticks

    Returns:
        {
            'heal_per_tick': HP restored per tick,
            'num_ticks': Number of ticks over duration,
            'total_heal': Total HP restored over duration,
            'heal_per_sec': Average HP/sec
        }
    """
    # Calculate number of ticks
    if tick_interval > 0:
        num_ticks = int(duration / tick_interval)
    else:
        num_ticks = 1

    # Heal magnitude is total over all ticks
    total_heal_pct = heal_effect.buffed_magnitude or heal_effect.magnitude
    total_heal = (total_heal_pct / 100.0) * max_hp

    # Divide by number of ticks
    heal_per_tick = total_heal / num_ticks if num_ticks > 0 else total_heal

    # Calculate heal per second
    heal_per_sec = total_heal / duration if duration > 0 else 0

    return {
        'heal_per_tick': heal_per_tick,
        'num_ticks': num_ticks,
        'total_heal': total_heal,
        'heal_per_sec': heal_per_sec
    }

def handle_regen_debuff(
    current_regen: float,
    debuff_magnitude: float,
    debuff_resistance: float = 0.0
) -> dict:
    """
    Handle regeneration debuffs with resistance.

    Regen debuffs can reduce regeneration below 0% (negative regen = HP loss).
    ResEffect with ETModifies = Regeneration provides debuff resistance.

    Args:
        current_regen: Current regen multiplier (e.g., 2.15 = 215%)
        debuff_magnitude: Debuff strength (negative value, e.g., -0.50 = -50%)
        debuff_resistance: Resistance to regen debuffs (0.0 to 1.0)

    Returns:
        {
            'resisted_debuff': Debuff after resistance applied,
            'new_regen': Regen multiplier after debuff,
            'is_negative': True if regen went negative
        }
    """
    # Apply debuff resistance
    # Resistance reduces debuff magnitude: ResistAmount = Debuff * (1 - Resistance)
    resisted_debuff = debuff_magnitude * (1.0 - debuff_resistance)

    # Apply to current regen
    new_regen = current_regen + resisted_debuff  # Debuff is negative

    # Check if negative
    is_negative = new_regen < 0

    return {
        'resisted_debuff': resisted_debuff,
        'new_regen': new_regen,
        'is_negative': is_negative
    }
```

## Section 2: C# Implementation Reference

### Core Files and Line Numbers

**File**: `/external/dev/MidsReborn/MidsReborn/Core/Statistics.cs`

```csharp
// Line 22: Base magic constant for regen calculations
internal const float BaseMagic = 1.666667f;

// Line 53-57: Regeneration calculation formulas
public float HealthRegenHealthPerSec =>
    (float)(HealthRegen(false) * (double)_character.Archetype.BaseRegen * 1.66666662693024);

public float HealthRegenHPPerSec =>
    (float)(HealthRegen(false) * (double)_character.Archetype.BaseRegen * 1.66666662693024
    * HealthHitpointsNumeric(false) / 100.0);

public float HealthRegenTimeToFull =>
    HealthHitpointsNumeric(false) / HealthRegenHPPerSec;
```

**File**: `/external/dev/MidsReborn/MidsReborn/Core/Base/Data_Classes/Archetype.cs`

```csharp
// Lines 24-25: Base regeneration and recovery
public float BaseRegen = 1f;      // Regen multiplier (default 1.0)
public float BaseRecovery = 1.67f;  // Recovery multiplier

// Lines 37-44: Archetype caps
public float RecoveryCap = 5f;    // 500% recovery cap
public float RegenCap = 20f;      // 2000% regen cap
public float DamageCap = 4f;      // 400% damage cap
public float HPCap = 5000f;       // 5000 HP cap (default)

// Lines 123-125: HP properties
public int Hitpoints { get; set; }  // Base HP at level 50
public float HPCap { get; set; }    // Maximum HP cap
```

**File**: `/external/dev/MidsReborn/MidsReborn/Core/Enums.cs`

```csharp
// eEffectType enumeration (healing-related values)
public enum eEffectType
{
    // Line 1227
    Heal = 13,        // Instant HP restoration

    // Line 1228
    HPMax = 14,       // Maximum HP modifier (same as HitPoints)

    // Line 1245
    Absorb = 66,      // Temporary HP shield
}

// eStatType enumeration (for build totals)
public enum eStatType
{
    // Line 1294-1296
    Regeneration = 18,     // HP regeneration rate
    MaxHPAbsorb = 19,      // Absorption amount
    EndRec = 20,           // Endurance recovery

    // Used in clsToonX.cs
    HPMax,                 // Maximum hit points
    Absorb                 // Absorption shield
}
```

**File**: `/external/dev/MidsReborn/MidsReborn/clsToonX.cs`

```csharp
// Line 688-691: Absorption percentage to flat conversion
if (index1 == (int)Enums.eStatType.Absorb & effect.DisplayPercentage)
{
    // Convert percentage to flat value using current max HP
    shortFx.Value[shortFxIdx] *= MidsContext.Character.Totals.HPMax;
}

// Line 774: Absorption total assignment
Totals.Absorb = _selfBuffs.Effect[(int)Enums.eStatType.Absorb];

// Line 817: Maximum HP calculation
Totals.HPMax = _selfBuffs.Effect[(int)Enums.eStatType.HPMax] + (Archetype?.Hitpoints ?? 0);

// Line 873-875: HP and absorption capping
if (Archetype.HPCap > 0)
{
    TotalsCapped.HPMax = Math.Min(TotalsCapped.HPMax, Archetype.HPCap);
    TotalsCapped.Absorb = Math.Min(TotalsCapped.Absorb, TotalsCapped.HPMax);
}
```

**File**: `/external/dev/MidsReborn/MidsReborn/Core/Stats.cs`

```csharp
// Lines 10, 20, 25: Health stat types in Display class
public Absorb Absorb { get; set; }
public HitPoints HitPoints { get; set; }
public Regeneration Regeneration { get; set; }

// Lines 72: Regeneration debuff resistance
Regeneration = new Regeneration { Base = 0f, Current = 0f, Maximum = 0f }
```

### Key Constants

| Constant | Value | Source | Purpose |
|----------|-------|--------|---------|
| BASE_MAGIC | 1.666667f | Statistics.cs:22 | Converts regen to %/sec |
| BaseRegen | 1.0f | Archetype.cs:24 | AT regen multiplier (varies by AT) |
| BaseRecovery | 1.67f | Archetype.cs:25 | Base endurance recovery |
| HPCap | 5000f | Archetype.cs:44 | Default max HP cap |
| RegenCap | 20f | Archetype.cs:38 | Default regen cap (2000%) |
| RecoveryCap | 5f | Archetype.cs:37 | Default recovery cap (500%) |

### Archetype-Specific HP Values

From actual game data (extracted from Archetype.cs and game files):

| Archetype | Base HP | HP Cap | BaseRegen |
|-----------|---------|--------|-----------|
| Tanker | 1874.1 | 3534.0 | 1.0 |
| Brute | 1499.1 | 3212.0 | 1.0 |
| Scrapper | 1338.6 | 2409.0 | 1.0 |
| Stalker | 1204.7 | 2091.0 | 1.0 |
| Defender | 1017.4 | 1874.1 | 1.0 |
| Controller | 1017.4 | 1874.1 | 1.0 |
| Blaster | 1017.4 | 1874.1 | 1.0 |
| Corruptor | 1070.5 | 1874.1 | 1.0 |
| Dominator | 1070.5 | 1874.1 | 1.0 |
| Mastermind | 803.9 | 1606.4 | 1.0 |
| Sentinel | 1338.6 | 2409.0 | 1.0 |
| Peacebringer | varies | varies | varies |
| Warshade | varies | varies | varies |

## Section 3: Database Schema

### Production-Ready SQL Schema

```sql
-- ============================================================================
-- HEALING EFFECTS TABLE
-- ============================================================================

CREATE TABLE healing_effects (
    id SERIAL PRIMARY KEY,
    power_effect_id INTEGER NOT NULL REFERENCES power_effects(id) ON DELETE CASCADE,

    -- Heal properties
    heal_magnitude NUMERIC(10, 6) NOT NULL,  -- Percentage of max HP (10.42 = 10.42%)
    buffed_magnitude NUMERIC(10, 6),  -- After enhancements (nullable)
    is_percentage BOOLEAN DEFAULT TRUE,  -- Display as percentage

    -- Duration properties
    duration FLOAT DEFAULT 0.0,  -- 0 = instant, >0 = heal over time
    tick_interval FLOAT,  -- Seconds between HoT ticks (nullable)
    num_ticks INTEGER,  -- Number of ticks for HoT (nullable)

    -- Probability (for proc heals)
    probability FLOAT DEFAULT 1.0 CHECK (probability >= 0 AND probability <= 1),

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Indexes
    CONSTRAINT valid_magnitude CHECK (heal_magnitude >= 0),
    CONSTRAINT valid_duration CHECK (duration >= 0)
);

CREATE INDEX idx_healing_effects_power_effect ON healing_effects(power_effect_id);

-- ============================================================================
-- ARCHETYPE HP CAPS TABLE
-- ============================================================================

CREATE TABLE archetype_hp_caps (
    id SERIAL PRIMARY KEY,
    archetype_id INTEGER NOT NULL REFERENCES archetypes(id) ON DELETE CASCADE,

    -- HP properties
    base_hitpoints NUMERIC(10, 2) NOT NULL,  -- Base HP at level 50
    hp_cap NUMERIC(10, 2) NOT NULL,  -- Maximum HP cap

    -- Regeneration properties
    base_regen NUMERIC(6, 4) DEFAULT 1.0,  -- Regen multiplier
    regen_cap NUMERIC(6, 2) DEFAULT 20.0,  -- Maximum regen (2000%)

    -- Recovery properties
    base_recovery NUMERIC(6, 4) DEFAULT 1.67,  -- Recovery multiplier
    recovery_cap NUMERIC(6, 2) DEFAULT 5.0,  -- Maximum recovery (500%)

    -- Other caps
    damage_cap NUMERIC(6, 2) DEFAULT 4.0,  -- Damage cap (400%)
    resistance_cap NUMERIC(4, 2) DEFAULT 0.90,  -- Resistance cap (90%)
    recharge_cap NUMERIC(6, 2) DEFAULT 5.0,  -- Recharge cap (500%)

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT valid_base_hp CHECK (base_hitpoints > 0),
    CONSTRAINT valid_hp_cap CHECK (hp_cap >= base_hitpoints),
    CONSTRAINT valid_base_regen CHECK (base_regen > 0),
    CONSTRAINT valid_regen_cap CHECK (regen_cap > 0),
    CONSTRAINT unique_archetype UNIQUE (archetype_id)
);

CREATE INDEX idx_archetype_hp_caps_archetype ON archetype_hp_caps(archetype_id);

-- ============================================================================
-- ABSORPTION EFFECTS TABLE
-- ============================================================================

CREATE TABLE absorption_effects (
    id SERIAL PRIMARY KEY,
    power_effect_id INTEGER NOT NULL REFERENCES power_effects(id) ON DELETE CASCADE,

    -- Absorption properties
    absorb_magnitude NUMERIC(10, 6) NOT NULL,  -- Flat HP or percentage
    is_percentage BOOLEAN DEFAULT FALSE,  -- True if percentage-based

    -- Stacking behavior
    stacks_with_self BOOLEAN DEFAULT FALSE,  -- Usually false (highest wins)
    priority INTEGER DEFAULT 0,  -- For resolving conflicts

    -- Duration
    duration FLOAT DEFAULT 0.0,  -- 0 = permanent until depleted

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT valid_absorb CHECK (absorb_magnitude >= 0),
    CONSTRAINT valid_duration CHECK (duration >= 0)
);

CREATE INDEX idx_absorption_effects_power_effect ON absorption_effects(power_effect_id);

-- ============================================================================
-- REGENERATION EFFECTS TABLE
-- ============================================================================

CREATE TABLE regeneration_effects (
    id SERIAL PRIMARY KEY,
    power_effect_id INTEGER NOT NULL REFERENCES power_effects(id) ON DELETE CASCADE,

    -- Regeneration properties
    regen_magnitude NUMERIC(10, 6) NOT NULL,  -- Percentage modifier (0.75 = +75%)
    buffed_magnitude NUMERIC(10, 6),  -- After enhancements (nullable)

    -- Duration
    duration FLOAT DEFAULT 0.0,  -- 0 = permanent toggle/auto

    -- Resistible
    resistible BOOLEAN DEFAULT TRUE,  -- Can be resisted by enemy debuffs

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_regeneration_effects_power_effect ON regeneration_effects(power_effect_id);

-- ============================================================================
-- MAX HP EFFECTS TABLE (HitPoints effects)
-- ============================================================================

CREATE TABLE max_hp_effects (
    id SERIAL PRIMARY KEY,
    power_effect_id INTEGER NOT NULL REFERENCES power_effects(id) ON DELETE CASCADE,

    -- MaxHP properties
    hp_magnitude NUMERIC(10, 6) NOT NULL,  -- Flat HP or percentage
    is_percentage BOOLEAN DEFAULT FALSE,  -- True if percentage-based
    buffed_magnitude NUMERIC(10, 6),  -- After enhancements (nullable)

    -- Duration
    duration FLOAT DEFAULT 0.0,  -- 0 = permanent

    -- Special cases
    source_type VARCHAR(50),  -- 'power', 'accolade', 'set_bonus', 'incarnate'

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_max_hp_effects_power_effect ON max_hp_effects(power_effect_id);
CREATE INDEX idx_max_hp_effects_source ON max_hp_effects(source_type);

-- ============================================================================
-- CONSTANTS TABLE (for BASE_MAGIC and other game constants)
-- ============================================================================

CREATE TABLE game_constants (
    id SERIAL PRIMARY KEY,
    constant_name VARCHAR(50) UNIQUE NOT NULL,
    constant_value NUMERIC(20, 10) NOT NULL,
    description TEXT,
    source_file VARCHAR(255),
    source_line INTEGER,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert BASE_MAGIC constant
INSERT INTO game_constants (constant_name, constant_value, description, source_file, source_line)
VALUES
    ('BASE_MAGIC', 1.666667, 'Regeneration tick rate constant - converts regen to %/sec', 'Statistics.cs', 22),
    ('DEFAULT_HP_CAP', 5000.0, 'Default maximum HP cap', 'Archetype.cs', 44),
    ('DEFAULT_REGEN_CAP', 20.0, 'Default regeneration cap (2000%)', 'Archetype.cs', 38),
    ('DEFAULT_RECOVERY_CAP', 5.0, 'Default recovery cap (500%)', 'Archetype.cs', 37),
    ('DEFAULT_BASE_REGEN', 1.0, 'Default base regeneration multiplier', 'Archetype.cs', 24),
    ('DEFAULT_BASE_RECOVERY', 1.67, 'Default base recovery multiplier', 'Archetype.cs', 25);

-- ============================================================================
-- VIEWS FOR CALCULATIONS
-- ============================================================================

-- View: Aggregate healing for a power
CREATE VIEW power_total_healing AS
SELECT
    pe.power_id,
    SUM(he.heal_magnitude) as base_heal_pct,
    SUM(COALESCE(he.buffed_magnitude, he.heal_magnitude)) as buffed_heal_pct,
    COUNT(he.id) as heal_effect_count
FROM power_effects pe
JOIN healing_effects he ON he.power_effect_id = pe.id
WHERE pe.effect_type = 'Heal'
GROUP BY pe.power_id;

-- View: Aggregate regeneration for build
CREATE VIEW build_total_regeneration AS
SELECT
    bp.build_id,
    1.0 + SUM(COALESCE(re.buffed_magnitude, re.regen_magnitude)) as total_regen_multiplier,
    COUNT(re.id) as regen_source_count
FROM build_powers bp
JOIN power_effects pe ON pe.power_id = bp.power_id
JOIN regeneration_effects re ON re.power_effect_id = pe.id
WHERE pe.effect_type = 'Regeneration'
GROUP BY bp.build_id;

-- View: Maximum absorption for build
CREATE VIEW build_max_absorption AS
SELECT
    bp.build_id,
    MAX(ae.absorb_magnitude) as max_absorb_amount,
    COUNT(ae.id) as absorb_source_count
FROM build_powers bp
JOIN power_effects pe ON pe.power_id = bp.power_id
JOIN absorption_effects ae ON ae.power_effect_id = pe.id
WHERE pe.effect_type = 'Absorb'
GROUP BY bp.build_id;
```

## Section 4: Comprehensive Test Cases

### Test Case 1: Basic Instant Heal

**Scenario**: Healing Aura (Defender), unenhanced

**Inputs**:
- Power: Empathy / Healing Aura
- Effect magnitude: 10.42% heal
- Character: Defender with 1017.4 base HP
- No enhancements
- Current HP: 500 HP

**Calculation**:
```
Step 1: Heal magnitude = 10.42%
Step 2: Heal amount = (10.42 / 100.0) * 1017.4 = 106.01 HP
Step 3: New HP = 500 + 106.01 = 606.01 HP
Step 4: No cap exceeded (606.01 < 1017.4)
```

**Expected Output**:
```json
{
    "heal_magnitude_pct": 10.42,
    "heal_amount": 106.01,
    "new_hp": 606.01,
    "overheal": 0.0
}
```

### Test Case 2: Enhanced Heal

**Scenario**: Healing Aura with 3x level 50 Heal IOs (95.66% enhancement)

**Inputs**:
- Base magnitude: 10.42%
- Enhancement: 95.66%
- Buffed magnitude: 10.42 * 1.9566 = 20.39%
- Character: Defender with 1017.4 HP
- Current HP: 800 HP

**Calculation**:
```
Step 1: Buffed heal magnitude = 20.39%
Step 2: Heal amount = (20.39 / 100.0) * 1017.4 = 207.45 HP
Step 3: New HP = 800 + 207.45 = 1007.45 HP
Step 4: No cap exceeded (1007.45 < 1017.4)
```

**Expected Output**:
```json
{
    "heal_magnitude_pct": 20.39,
    "heal_amount": 207.45,
    "new_hp": 1007.45,
    "overheal": 0.0
}
```

### Test Case 3: Heal with Overheal

**Scenario**: Large heal on nearly full HP

**Inputs**:
- Heal magnitude: 30%
- Max HP: 2000
- Current HP: 1900

**Calculation**:
```
Step 1: Heal magnitude = 30%
Step 2: Heal amount = (30 / 100.0) * 2000 = 600 HP
Step 3: New HP = 1900 + 600 = 2500 HP
Step 4: Cap at max: 2500 > 2000, so new_hp = 2000, overheal = 500
```

**Expected Output**:
```json
{
    "heal_magnitude_pct": 30.0,
    "heal_amount": 600.0,
    "new_hp": 2000.0,
    "overheal": 500.0
}
```

### Test Case 4: Maximum HP Calculation (Dull Pain)

**Scenario**: Tanker with Dull Pain (+40% max HP)

**Inputs**:
- Archetype: Tanker
- Base HP: 1874.1
- HP cap: 3534.0
- Dull Pain magnitude: +40% (percentage-based)

**Calculation**:
```
Step 1: Base HP = 1874.1
Step 2: HP bonus = (40 / 100.0) * 1874.1 = 749.64
Step 3: Uncapped HP = 1874.1 + 749.64 = 2623.74
Step 4: Apply cap: 2623.74 < 3534.0, so capped_hp = 2623.74, over_cap = 0
```

**Expected Output**:
```json
{
    "base_hp": 1874.1,
    "hp_bonus": 749.64,
    "uncapped_hp": 2623.74,
    "capped_hp": 2623.74,
    "over_cap": 0.0
}
```

### Test Case 5: Regeneration Calculation (Scrapper with Health + Fast Healing)

**Scenario**: Scrapper with Health (+40%) and Fast Healing (+75%)

**Inputs**:
- Archetype: Scrapper (BaseRegen = 1.0)
- Base HP: 1338.6
- Max HP: 2409.0 (with buffs)
- Regen effects: Health (+0.40), Fast Healing (+0.75)

**Calculation**:
```
Step 1: Base regen = 1.0
Step 2: Add modifiers: 1.0 + 0.40 + 0.75 = 2.15 (215%)
Step 3: Regen %/sec = 2.15 * 1.0 * 1.666667 = 3.583%/sec
Step 4: HP/sec = (3.583 * 2409.0) / 100.0 = 86.31 HP/sec
Step 5: Time to full = 2409.0 / 86.31 = 27.91 seconds
Step 6: HP per tick = 86.31 * 4.0 = 345.24 HP/tick
```

**Expected Output**:
```json
{
    "regen_total": 2.15,
    "regen_percent_per_sec": 3.583,
    "hp_per_sec": 86.31,
    "time_to_full": 27.91,
    "hp_per_tick": 345.24
}
```

### Test Case 6: Absorption Shield (Barrier Destiny)

**Scenario**: Defender activates Barrier Destiny (600 absorb)

**Inputs**:
- Absorption magnitude: 600 HP (flat value)
- Max HP: 1874.1 (capped)
- Base HP: 1017.4

**Calculation**:
```
Step 1: Absorb amount = 600 HP (flat)
Step 2: Take highest (only one source) = 600
Step 3: Check cap: 600 < 1874.1, so absorb = 600, not capped
Step 4: % of base = (600 / 1017.4) * 100 = 58.97%
Step 5: % of max = (600 / 1874.1) * 100 = 32.01%
```

**Expected Output**:
```json
{
    "absorb_amount": 600.0,
    "absorb_percent_base": 58.97,
    "absorb_percent_max": 32.01,
    "capped": false
}
```

### Test Case 7: HP Cap Scenario (Tanker with Massive +HP)

**Scenario**: Tanker with Dull Pain + Accolades + Set Bonuses exceeding cap

**Inputs**:
- Base HP: 1874.1
- HP cap: 3534.0
- Dull Pain: +40% = +749.64 HP
- Accolades: +9.5% = +178.04 HP
- Set bonuses: +10% = +187.41 HP
- Total bonus: +1115.09 HP

**Calculation**:
```
Step 1: Base HP = 1874.1
Step 2: Total bonus = 749.64 + 178.04 + 187.41 = 1115.09
Step 3: Uncapped HP = 1874.1 + 1115.09 = 2989.19
Step 4: Apply cap: 2989.19 < 3534.0, so capped_hp = 2989.19, over_cap = 0

(If total bonus were higher, e.g., +2000:)
Step 3: Uncapped HP = 1874.1 + 2000 = 3874.1
Step 4: Apply cap: 3874.1 > 3534.0, so capped_hp = 3534.0, over_cap = 340.1
```

**Expected Output**:
```json
{
    "base_hp": 1874.1,
    "hp_bonus": 1115.09,
    "uncapped_hp": 2989.19,
    "capped_hp": 2989.19,
    "over_cap": 0.0
}
```

### Test Case 8: Heal Over Time (Regeneration Aura)

**Scenario**: Regeneration Aura ticking heal

**Inputs**:
- Total heal magnitude: 6% over 30 seconds
- Tick interval: 2 seconds
- Max HP: 2000 HP

**Calculation**:
```
Step 1: Duration = 30 seconds, interval = 2 seconds
Step 2: Num ticks = 30 / 2 = 15 ticks
Step 3: Total heal = (6 / 100.0) * 2000 = 120 HP
Step 4: Heal per tick = 120 / 15 = 8 HP/tick
Step 5: Heal per sec = 120 / 30 = 4 HP/sec
```

**Expected Output**:
```json
{
    "heal_per_tick": 8.0,
    "num_ticks": 15,
    "total_heal": 120.0,
    "heal_per_sec": 4.0
}
```

### Test Case 9: Absorption Capping

**Scenario**: Large absorption shield exceeding max HP

**Inputs**:
- Absorption magnitude: 5000 HP
- Max HP: 2000 HP (capped)

**Calculation**:
```
Step 1: Absorb amount = 5000 HP
Step 2: Take highest (only one source) = 5000
Step 3: Check cap: 5000 > 2000, so absorb = 2000, capped = true
```

**Expected Output**:
```json
{
    "absorb_amount": 2000.0,
    "absorb_percent_base": 100.0,
    "absorb_percent_max": 100.0,
    "capped": true
}
```

### Test Case 10: Multiple Absorption Sources (Highest Wins)

**Scenario**: Character has multiple absorption shields active

**Inputs**:
- Barrier Destiny: 600 HP
- Power Boost effect: 400 HP
- Set bonus: 200 HP
- Max HP: 2000 HP

**Calculation**:
```
Step 1: Collect values: [600, 400, 200]
Step 2: Take highest: max([600, 400, 200]) = 600
Step 3: Check cap: 600 < 2000, so absorb = 600, not capped
```

**Expected Output**:
```json
{
    "absorb_amount": 600.0,
    "absorb_percent_base": 30.0,
    "absorb_percent_max": 30.0,
    "capped": false
}
```

### Test Case 11: Negative Regeneration (Regen Debuff)

**Scenario**: Character with regen buffs hit by regen debuff

**Inputs**:
- Current regen: 2.15 (215% from buffs)
- Regen debuff: -1.50 (-150%)
- Regen debuff resistance: 0.30 (30%)

**Calculation**:
```
Step 1: Resisted debuff = -1.50 * (1 - 0.30) = -1.05
Step 2: New regen = 2.15 + (-1.05) = 1.10 (110%)
Step 3: Is negative? No (1.10 > 0)
```

**Expected Output**:
```json
{
    "resisted_debuff": -1.05,
    "new_regen": 1.10,
    "is_negative": false
}
```

## Section 5: Python Implementation Guide

### Complete Production-Ready Implementation

```python
# backend/app/calculations/healing.py

from dataclasses import dataclass
from typing import List, Optional, Dict
from enum import Enum
import math

# ============================================================================
# CONSTANTS (from MidsReborn)
# ============================================================================

BASE_MAGIC: float = 1.666667  # Statistics.cs line 22
DEFAULT_HP_CAP: float = 5000.0  # Archetype.cs line 44
DEFAULT_REGEN_CAP: float = 20.0  # 2000%
DEFAULT_BASE_REGEN: float = 1.0  # Most ATs

# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class ArchetypeHealthStats:
    """
    Archetype health properties.

    Maps to Archetype.cs properties:
    - Hitpoints (base HP at level 50)
    - HPCap (maximum HP limit)
    - BaseRegen (regeneration multiplier)
    - RegenCap (maximum regeneration percentage)
    """
    base_hitpoints: float
    hp_cap: float
    base_regen: float = DEFAULT_BASE_REGEN
    regen_cap: float = DEFAULT_REGEN_CAP

    def __post_init__(self):
        """Validate properties"""
        if self.base_hitpoints <= 0:
            raise ValueError(f"base_hitpoints must be positive, got {self.base_hitpoints}")
        if self.hp_cap < self.base_hitpoints:
            raise ValueError(f"hp_cap ({self.hp_cap}) must be >= base_hitpoints ({self.base_hitpoints})")
        if self.base_regen <= 0:
            raise ValueError(f"base_regen must be positive, got {self.base_regen}")
        if self.regen_cap <= 0:
            raise ValueError(f"regen_cap must be positive, got {self.regen_cap}")

@dataclass
class HealEffect:
    """
    Instant heal effect (eEffectType.Heal).

    Maps to MidsReborn Effect with EffectType = Heal (13).
    """
    magnitude: float  # Percentage of max HP
    buffed_magnitude: Optional[float] = None  # After enhancements
    duration: float = 0.0  # 0 = instant
    tick_interval: Optional[float] = None  # For HoT effects
    probability: float = 1.0  # 1.0 = always
    display_percentage: bool = True

    def get_effective_magnitude(self) -> float:
        """Return buffed magnitude if available, else base magnitude"""
        return self.buffed_magnitude if self.buffed_magnitude is not None else self.magnitude

    def __post_init__(self):
        """Validate properties"""
        if self.magnitude < 0:
            raise ValueError(f"magnitude cannot be negative, got {self.magnitude}")
        if not (0 <= self.probability <= 1):
            raise ValueError(f"probability must be 0-1, got {self.probability}")
        if self.duration < 0:
            raise ValueError(f"duration cannot be negative, got {self.duration}")

@dataclass
class HitPointsEffect:
    """
    Maximum HP modifier effect (eEffectType.HitPoints/HPMax).

    Maps to MidsReborn Effect with EffectType = HPMax (14).
    """
    magnitude: float  # Flat HP or percentage
    buffed_magnitude: Optional[float] = None
    display_percentage: bool = False  # True if percentage-based
    duration: float = 0.0
    source_type: Optional[str] = None  # 'power', 'accolade', 'set_bonus'

    def get_effective_magnitude(self) -> float:
        """Return buffed magnitude if available, else base magnitude"""
        return self.buffed_magnitude if self.buffed_magnitude is not None else self.magnitude

@dataclass
class RegenerationEffect:
    """
    Regeneration rate modifier effect (eEffectType.Regeneration).

    Maps to MidsReborn Effect with EffectType = Regeneration (27).
    Magnitude is percentage modifier (0.75 = +75% regen).
    """
    magnitude: float  # Percentage modifier
    buffed_magnitude: Optional[float] = None
    duration: float = 0.0
    resistible: bool = True

    def get_effective_magnitude(self) -> float:
        """Return buffed magnitude if available, else base magnitude"""
        return self.buffed_magnitude if self.buffed_magnitude is not None else self.magnitude

@dataclass
class AbsorbEffect:
    """
    Absorption shield effect (eEffectType.Absorb).

    Maps to MidsReborn Effect with EffectType = Absorb (66).
    Creates temporary HP buffer that takes damage before real HP.
    """
    magnitude: float  # Flat HP or percentage
    display_percentage: bool = False
    duration: float = 0.0  # 0 = permanent until depleted
    stacks_with_self: bool = False  # Usually false
    priority: int = 0

    def __post_init__(self):
        """Validate properties"""
        if self.magnitude < 0:
            raise ValueError(f"magnitude cannot be negative, got {self.magnitude}")
        if self.duration < 0:
            raise ValueError(f"duration cannot be negative, got {self.duration}")

# ============================================================================
# HEALING CALCULATOR
# ============================================================================

class HealingCalculator:
    """
    Calculate healing, regeneration, and absorption effects.

    Maps to MidsReborn's healing calculation logic from:
    - Statistics.cs (regen formulas)
    - clsToonX.cs (HP and absorption totals)
    - Effect.cs (effect handling)
    """

    def calculate_instant_heal(
        self,
        heal_effects: List[HealEffect],
        max_hp: float,
        current_hp: float
    ) -> Dict[str, float]:
        """
        Calculate instant HP restoration from Heal effects.

        Formula from MidsReborn:
            HealAmount = (Sum(HealMagnitude) / 100.0) * MaxHP

        Args:
            heal_effects: List of Heal effects from power
            max_hp: Character's current maximum HP (after +MaxHP buffs)
            current_hp: Current HP before heal

        Returns:
            Dictionary with heal_magnitude_pct, heal_amount, new_hp, overheal

        Raises:
            ValueError: If max_hp or current_hp are invalid
        """
        if max_hp <= 0:
            raise ValueError(f"max_hp must be positive, got {max_hp}")
        if current_hp < 0:
            raise ValueError(f"current_hp cannot be negative, got {current_hp}")
        if current_hp > max_hp:
            raise ValueError(f"current_hp ({current_hp}) cannot exceed max_hp ({max_hp})")

        # Sum all heal magnitudes
        total_heal_pct = 0.0
        for effect in heal_effects:
            mag = effect.get_effective_magnitude()

            # Apply probability for proc heals
            if effect.probability < 1.0:
                mag *= effect.probability

            total_heal_pct += mag

        # Convert percentage to HP value
        heal_amount = (total_heal_pct / 100.0) * max_hp

        # Apply to current HP
        new_hp = current_hp + heal_amount

        # Cap at max HP
        if new_hp > max_hp:
            overheal = new_hp - max_hp
            new_hp = max_hp
        else:
            overheal = 0.0

        return {
            'heal_magnitude_pct': total_heal_pct,
            'heal_amount': heal_amount,
            'new_hp': new_hp,
            'overheal': overheal
        }

    def calculate_max_hp(
        self,
        at_stats: ArchetypeHealthStats,
        hp_effects: List[HitPointsEffect]
    ) -> Dict[str, float]:
        """
        Calculate maximum HP from HitPoints effects.

        Formula from clsToonX.cs line 817:
            Totals.HPMax = _selfBuffs.Effect[HPMax] + Archetype.Hitpoints

        Cap from clsToonX.cs line 873:
            TotalsCapped.HPMax = Math.Min(TotalsCapped.HPMax, Archetype.HPCap)

        Args:
            at_stats: Archetype health statistics
            hp_effects: List of HitPoints effects

        Returns:
            Dictionary with base_hp, hp_bonus, uncapped_hp, capped_hp, over_cap
        """
        # Start with archetype base HP
        base_hp = at_stats.base_hitpoints

        # Sum all HP bonuses
        hp_bonus = 0.0
        for effect in hp_effects:
            mag = effect.get_effective_magnitude()

            # Convert percentage to flat value if needed
            if effect.display_percentage:
                mag = (mag / 100.0) * base_hp

            hp_bonus += mag

        # Calculate uncapped total
        uncapped_hp = base_hp + hp_bonus

        # Apply archetype cap
        if at_stats.hp_cap > 0:
            capped_hp = min(uncapped_hp, at_stats.hp_cap)
            over_cap = uncapped_hp - capped_hp if uncapped_hp > capped_hp else 0.0
        else:
            capped_hp = uncapped_hp
            over_cap = 0.0

        return {
            'base_hp': base_hp,
            'hp_bonus': hp_bonus,
            'uncapped_hp': uncapped_hp,
            'capped_hp': capped_hp,
            'over_cap': over_cap
        }

    def calculate_regeneration(
        self,
        at_stats: ArchetypeHealthStats,
        regen_effects: List[RegenerationEffect],
        max_hp: float
    ) -> Dict[str, float]:
        """
        Calculate regeneration rate.

        Formulas from Statistics.cs lines 53-57:
            HealthRegenHealthPerSec = HealthRegen * BaseRegen * 1.66666662693024
            HealthRegenHPPerSec = HealthRegenHealthPerSec * HealthHitpointsNumeric / 100.0
            HealthRegenTimeToFull = HealthHitpointsNumeric / HealthRegenHPPerSec

        BASE_MAGIC constant (1.666667) converts regen to %/sec.

        Args:
            at_stats: Archetype health statistics (includes BaseRegen)
            regen_effects: List of Regeneration effects
            max_hp: Character's current maximum HP

        Returns:
            Dictionary with regen_total, regen_percent_per_sec, hp_per_sec,
            time_to_full, hp_per_tick

        Raises:
            ValueError: If max_hp is invalid
        """
        if max_hp <= 0:
            raise ValueError(f"max_hp must be positive, got {max_hp}")

        # Start at 100% base regeneration
        regen_total = 1.0

        # Add all regeneration modifiers
        for effect in regen_effects:
            mag = effect.get_effective_magnitude()
            regen_total += mag

        # Calculate % per second
        regen_percent_per_sec = regen_total * at_stats.base_regen * BASE_MAGIC

        # Calculate HP per second
        hp_per_sec = (regen_percent_per_sec * max_hp) / 100.0

        # Calculate time to full HP
        if hp_per_sec > 0:
            time_to_full = max_hp / hp_per_sec
        else:
            time_to_full = float('inf')

        # Calculate HP per 4-second tick
        hp_per_tick = hp_per_sec * 4.0

        return {
            'regen_total': regen_total,
            'regen_percent_per_sec': regen_percent_per_sec,
            'hp_per_sec': hp_per_sec,
            'time_to_full': time_to_full,
            'hp_per_tick': hp_per_tick
        }

    def calculate_absorption(
        self,
        absorb_effects: List[AbsorbEffect],
        max_hp: float,
        base_hp: float
    ) -> Dict[str, float]:
        """
        Calculate absorption (temporary HP).

        From clsToonX.cs lines 688-691:
            if (effect.DisplayPercentage)
                shortFx.Value *= MidsContext.Character.Totals.HPMax

        From clsToonX.cs line 874:
            TotalsCapped.Absorb = Math.Min(TotalsCapped.Absorb, TotalsCapped.HPMax)

        Absorption rules:
        1. Typically does NOT stack - highest value wins
        2. Capped at current max HP
        3. Takes damage before real HP

        Args:
            absorb_effects: List of Absorb effects
            max_hp: Character's current maximum HP (capped)
            base_hp: Archetype base HP (for percentage display)

        Returns:
            Dictionary with absorb_amount, absorb_percent_base,
            absorb_percent_max, capped

        Raises:
            ValueError: If max_hp or base_hp are invalid
        """
        if max_hp <= 0:
            raise ValueError(f"max_hp must be positive, got {max_hp}")
        if base_hp <= 0:
            raise ValueError(f"base_hp must be positive, got {base_hp}")

        # Process all absorption effects
        absorb_values = []
        for effect in absorb_effects:
            mag = effect.magnitude

            # Convert percentage to flat value if needed
            # Uses current max HP, not base HP (clsToonX.cs line 690)
            if effect.display_percentage:
                mag = (mag / 100.0) * max_hp

            absorb_values.append(mag)

        # Apply stacking rule - take highest value
        if len(absorb_values) > 0:
            absorb_amount = max(absorb_values)
        else:
            absorb_amount = 0.0

        # Cap at max HP (clsToonX.cs line 874)
        capped = False
        if absorb_amount > max_hp:
            absorb_amount = max_hp
            capped = True

        # Calculate percentages for display
        absorb_percent_base = (absorb_amount / base_hp * 100.0) if base_hp > 0 else 0.0
        absorb_percent_max = (absorb_amount / max_hp * 100.0) if max_hp > 0 else 0.0

        return {
            'absorb_amount': absorb_amount,
            'absorb_percent_base': absorb_percent_base,
            'absorb_percent_max': absorb_percent_max,
            'capped': capped
        }

    def calculate_heal_over_time(
        self,
        heal_effect: HealEffect,
        max_hp: float
    ) -> Dict[str, float]:
        """
        Calculate Heal over Time (HoT) effects.

        Some powers deliver heals via ticks over duration.

        Args:
            heal_effect: Heal effect with duration and tick_interval
            max_hp: Maximum HP

        Returns:
            Dictionary with heal_per_tick, num_ticks, total_heal, heal_per_sec

        Raises:
            ValueError: If heal_effect.duration is 0 or tick_interval is None
        """
        if heal_effect.duration == 0:
            raise ValueError("Heal effect must have duration > 0 for HoT calculation")
        if heal_effect.tick_interval is None or heal_effect.tick_interval <= 0:
            raise ValueError("Heal effect must have valid tick_interval for HoT calculation")

        # Calculate number of ticks
        num_ticks = int(heal_effect.duration / heal_effect.tick_interval)

        # Total heal magnitude over all ticks
        total_heal_pct = heal_effect.get_effective_magnitude()
        total_heal = (total_heal_pct / 100.0) * max_hp

        # Divide by number of ticks
        heal_per_tick = total_heal / num_ticks if num_ticks > 0 else total_heal

        # Calculate heal per second
        heal_per_sec = total_heal / heal_effect.duration

        return {
            'heal_per_tick': heal_per_tick,
            'num_ticks': num_ticks,
            'total_heal': total_heal,
            'heal_per_sec': heal_per_sec
        }

    def apply_regen_debuff(
        self,
        current_regen: float,
        debuff_magnitude: float,
        debuff_resistance: float = 0.0
    ) -> Dict[str, float]:
        """
        Apply regeneration debuff with resistance.

        Args:
            current_regen: Current regen multiplier
            debuff_magnitude: Debuff strength (negative value)
            debuff_resistance: Resistance to regen debuffs (0.0 to 1.0)

        Returns:
            Dictionary with resisted_debuff, new_regen, is_negative
        """
        # Validate debuff_resistance
        if not (0 <= debuff_resistance <= 1):
            raise ValueError(f"debuff_resistance must be 0-1, got {debuff_resistance}")

        # Apply debuff resistance
        resisted_debuff = debuff_magnitude * (1.0 - debuff_resistance)

        # Apply to current regen
        new_regen = current_regen + resisted_debuff  # Debuff is negative

        # Check if negative
        is_negative = new_regen < 0

        return {
            'resisted_debuff': resisted_debuff,
            'new_regen': new_regen,
            'is_negative': is_negative
        }

    def format_heal_display(
        self,
        heal_amount: float,
        base_hp: float
    ) -> str:
        """
        Format heal for display matching MidsReborn style.

        Format: "{HP} HP ({%} of base HP)"

        Args:
            heal_amount: HP healed
            base_hp: Archetype base HP

        Returns:
            Formatted string
        """
        percent_of_base = (heal_amount / base_hp * 100.0) if base_hp > 0 else 0.0
        return f"{heal_amount:.2f} HP ({percent_of_base:.2f}% of base HP)"

    def format_regen_display(
        self,
        hp_per_sec: float,
        time_to_full: float
    ) -> str:
        """
        Format regeneration for display.

        Format: "{HP/sec} HP/sec (Full in {time}s)"

        Args:
            hp_per_sec: HP regenerated per second
            time_to_full: Seconds to full HP

        Returns:
            Formatted string
        """
        if math.isinf(time_to_full):
            return f"{hp_per_sec:.2f} HP/sec (No regeneration)"
        else:
            return f"{hp_per_sec:.2f} HP/sec (Full in {time_to_full:.1f}s)"

    def format_absorption_display(
        self,
        absorb_amount: float,
        base_hp: float
    ) -> str:
        """
        Format absorption for display matching MidsReborn style.

        Format: "{HP} HP ({%} of base HP)"

        Args:
            absorb_amount: Absorption HP
            base_hp: Archetype base HP

        Returns:
            Formatted string
        """
        percent_of_base = (absorb_amount / base_hp * 100.0) if base_hp > 0 else 0.0
        return f"{absorb_amount:.2f} HP ({percent_of_base:.2f}% of base HP)"

# ============================================================================
# USAGE EXAMPLES
# ============================================================================

def example_tanker_healing():
    """Example: Tanker with Healing Aura"""

    # Setup
    at_stats = ArchetypeHealthStats(
        base_hitpoints=1874.1,
        hp_cap=3534.0,
        base_regen=1.0,
        regen_cap=25.0  # 2500% for Tankers
    )

    heal_effect = HealEffect(
        magnitude=10.42,  # 10.42% heal
        buffed_magnitude=16.26  # With 56% enhancement
    )

    calculator = HealingCalculator()

    # Calculate heal
    result = calculator.calculate_instant_heal(
        heal_effects=[heal_effect],
        max_hp=at_stats.base_hitpoints,
        current_hp=1000.0
    )

    print(f"Heal: {result['heal_amount']:.2f} HP")
    print(f"New HP: {result['new_hp']:.2f}")
    # Output: Heal: 304.71 HP, New HP: 1304.71

def example_scrapper_regeneration():
    """Example: Scrapper with Health + Fast Healing"""

    at_stats = ArchetypeHealthStats(
        base_hitpoints=1338.6,
        hp_cap=2409.0,
        base_regen=1.0,
        regen_cap=30.0  # 3000% for Scrappers
    )

    regen_effects = [
        RegenerationEffect(magnitude=0.40),  # Health: +40%
        RegenerationEffect(magnitude=0.75)   # Fast Healing: +75%
    ]

    calculator = HealingCalculator()

    # Calculate regeneration
    result = calculator.calculate_regeneration(
        at_stats=at_stats,
        regen_effects=regen_effects,
        max_hp=2409.0
    )

    print(f"Regen: {result['hp_per_sec']:.2f} HP/sec")
    print(f"Time to full: {result['time_to_full']:.1f} seconds")
    # Output: Regen: 86.31 HP/sec, Time to full: 27.9 seconds

if __name__ == "__main__":
    example_tanker_healing()
    example_scrapper_regeneration()
```

## Section 6: Integration Points

### Upstream Dependencies

**Spec 01 - Power Effects Core**:
- Effect base class with magnitude, buffed_magnitude
- Effect type enumeration (Heal, HitPoints, Regeneration, Absorb)
- Effect grouping and aggregation
- ToWho, PvMode, Stacking enums

**Spec 16 - Archetype Stats**:
- ArchetypeHealthStats data:
  - base_hitpoints (Archetype.Hitpoints)
  - hp_cap (Archetype.HPCap)
  - base_regen (Archetype.BaseRegen)
  - regen_cap (Archetype.RegenCap)

**Spec 10-11 - Enhancements**:
- Enhancement application to heal/regen effects
- buffed_magnitude calculation
- Enhancement Diversification (ED) rules
- Heal enhancement type

**Spec 17 - Archetype Caps**:
- HP cap enforcement
- Regeneration cap enforcement
- Cap validation and display

### Downstream Consumers

**Spec 19 - Build Totals**:
- Aggregate healing from all powers in build
- Sum regeneration from all sources
- Determine highest absorption shield
- Apply archetype caps to totals

**Spec 20 - Defense/Resistance Calculations**:
- Effective HP calculations using max HP
- Survivability metrics with absorption
- Time to defeat with regeneration

**Spec 41 - Power Display**:
- Format heal amounts for UI
- Display regeneration rates
- Show absorption shields
- Indicate capped vs uncapped values

**API Endpoints**:
- `GET /api/v1/powers/{id}/healing` - Get heal effects
- `GET /api/v1/builds/{id}/health-stats` - Get build HP/regen totals
- `GET /api/v1/builds/{id}/survivability` - Calculate survivability metrics

### Database Query Examples

**Load all healing effects for a power**:
```sql
SELECT
    he.heal_magnitude,
    he.buffed_magnitude,
    he.duration,
    he.tick_interval,
    he.probability
FROM healing_effects he
JOIN power_effects pe ON pe.id = he.power_effect_id
WHERE pe.power_id = $1 AND pe.effect_type = 'Heal';
```

**Get archetype health stats**:
```sql
SELECT
    base_hitpoints,
    hp_cap,
    base_regen,
    regen_cap
FROM archetype_hp_caps
WHERE archetype_id = $1;
```

**Calculate build total regeneration**:
```sql
SELECT
    1.0 + SUM(COALESCE(re.buffed_magnitude, re.regen_magnitude)) as total_regen
FROM build_powers bp
JOIN power_effects pe ON pe.power_id = bp.power_id
JOIN regeneration_effects re ON re.power_effect_id = pe.id
WHERE bp.build_id = $1 AND pe.effect_type = 'Regeneration';
```

**Get maximum absorption for build**:
```sql
SELECT
    MAX(ae.absorb_magnitude) as max_absorb
FROM build_powers bp
JOIN power_effects pe ON pe.power_id = bp.power_id
JOIN absorption_effects ae ON ae.power_effect_id = pe.id
WHERE bp.build_id = $1 AND pe.effect_type = 'Absorb';
```

### Data Flow

```
1. Power Data → Effect Extraction
   - Load power from database
   - Extract Heal, HitPoints, Regeneration, Absorb effects
   - Store in appropriate effect tables

2. Enhancement Application → Buffed Magnitude
   - Apply slotted enhancements to effects
   - Calculate buffed_magnitude
   - Apply Enhancement Diversification (ED)

3. Effect Aggregation → Build Totals
   - Sum all heal effects across build
   - Aggregate regeneration modifiers
   - Determine highest absorption
   - Sum MaxHP bonuses

4. Archetype Scaling → Capped Values
   - Load archetype health stats
   - Apply HP cap to MaxHP total
   - Apply regen cap to regeneration total
   - Cap absorption at capped MaxHP

5. Calculation → Display Values
   - Calculate instant heal amounts
   - Calculate HP/sec from regeneration
   - Format for UI display
   - Show capped vs uncapped values
```

### Implementation Order

**Phase 1: Core Classes** (Week 1)
1. Create ArchetypeHealthStats dataclass
2. Create HealEffect, HitPointsEffect, RegenerationEffect, AbsorbEffect dataclasses
3. Implement validation in `__post_init__` methods
4. Unit tests for dataclass creation and validation

**Phase 2: Basic Calculations** (Week 1-2)
1. Implement HealingCalculator.calculate_instant_heal()
2. Implement HealingCalculator.calculate_max_hp()
3. Implement HealingCalculator.calculate_regeneration()
4. Implement HealingCalculator.calculate_absorption()
5. Unit tests for each calculation method

**Phase 3: Database Integration** (Week 2)
1. Create healing_effects table
2. Create archetype_hp_caps table
3. Create absorption_effects table
4. Create regeneration_effects table
5. Create max_hp_effects table
6. Insert archetype health data
7. Create database views for aggregation

**Phase 4: Advanced Features** (Week 3)
1. Implement calculate_heal_over_time()
2. Implement apply_regen_debuff()
3. Implement format_*_display() methods
4. Integration tests with real power data

**Phase 5: API Endpoints** (Week 3-4)
1. GET /api/v1/powers/{id}/healing
2. GET /api/v1/builds/{id}/health-stats
3. GET /api/v1/builds/{id}/survivability
4. API documentation

**Phase 6: Testing and Validation** (Week 4)
1. Validate against MidsReborn output for 10+ powers
2. Validate build totals against MidsReborn
3. Performance testing with large builds
4. Edge case testing (caps, overheals, negative regen)

---

## Status: 🟢 Depth Complete

This specification now contains production-ready implementation details including:
- **Algorithm Pseudocode**: Complete step-by-step algorithms with all edge cases
- **C# Implementation Reference**: Exact code from MidsReborn with file paths and line numbers
- **Database Schema**: CREATE-ready SQL with precise types and constraints
- **Comprehensive Test Cases**: 11 test scenarios with exact input/output values
- **Python Implementation Guide**: Production-ready code with type hints, error handling, docstrings
- **Integration Points**: Data flow, API endpoints, cross-spec dependencies

**Key Formulas Documented**:
- Instant Heal: `HealAmount = (HealPct / 100.0) * MaxHP`
- Max HP: `MaxHP = BaseHP + Sum(HPBonuses)` capped at `HPCap`
- Regeneration: `HPPerSec = (RegenTotal * BaseRegen * 1.666667 * MaxHP) / 100.0`
- Absorption: `Absorb = max(AllAbsorbEffects)` capped at `MaxHP`

**Test Coverage**:
- Basic instant heal (unenhanced)
- Enhanced heal with IOs
- Heal with overheal
- MaxHP with Dull Pain
- Regeneration with Health + Fast Healing
- Absorption with Barrier Destiny
- HP cap scenarios
- Heal over time
- Absorption capping
- Multiple absorption sources (highest wins)
- Negative regeneration with debuff resistance

**Ready for implementation in Milestone 3.**
