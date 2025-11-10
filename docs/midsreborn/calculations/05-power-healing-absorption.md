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
