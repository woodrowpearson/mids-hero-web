# Power Damage

## Overview
- **Purpose**: Calculate damage output for attack powers including base damage, archetype scaling, and enhancement bonuses
- **Used By**: Power display, DPS calculations, build totals, damage comparison tools
- **Complexity**: Medium
- **Priority**: Critical
- **Status**: 🟡 Breadth Complete

## MidsReborn Implementation

### Primary Location
- **File**: `Core/Base/Data_Classes/Power.cs`
- **Classes**:
  - `Power` class - Contains base damage data and damage calculation methods
  - `Effect.cs` - `GetDamage()` method, `Damage` and `DamageExt` structs
- **Related Files**:
  - `Core/Base/Data_Classes/Archetype.cs` - AT damage scaling and damage caps
  - `Core/Enums.cs` - `eDamage` enum for damage types
  - `Core/PowerEntry.cs` - Enhancement-modified damage calculations

### Damage Type System

The `eDamage` enum in `Core/Enums.cs` defines damage types:

**Primary Damage Types** (actual HP loss):
- Smashing
- Lethal
- Fire
- Cold
- Energy
- Negative
- Toxic
- Psionic

**Special Categories**:
- Special - Unique damage types (untyped)
- Melee - Positional indicator (not a damage type)
- Ranged - Positional indicator (not a damage type)
- AoE - Area of effect indicator (not a damage type)

### Data Structures

**Damage Struct** (`Effect.cs`):
```csharp
public struct Damage
{
    public Enums.eDamage Type;  // Which damage type
    public float Value;         // Amount of damage
}

public struct DamageExt
{
    public Enums.eDamage Type;
    public float Value;
    public int Ticks;           // For DoT (damage over time)
    public bool HasPercentage;  // For percentage-based damage
}
```

**Archetype Damage Cap** (`Archetype.cs`):
```csharp
public float DamageCap { get; set; }  // Default: 4.0 (400% damage buff cap)
```

## High-Level Algorithm

```
Power Damage Calculation Process:

1. Get Base Damage from Power.Effects:
   For each effect in power.Effects:
     If effect.EffectType == Damage:
       base_damage = effect.Magnitude
       damage_type = effect.DamageType  (Smashing, Fire, etc.)

2. Apply Probability (for proc-based or chance-to-hit damage):
   If ConfigData.DamageMath.Calculate == Average:
     base_damage *= effect.Probability
   Else if ConfigData.DamageMath.Calculate == Minimum:
     Skip this effect if Probability < 1.0

3. Apply Archetype Damage Scale:
   // Each AT has different damage output multiplier
   scaled_damage = base_damage * archetype_scale
   // Note: AT scale not directly visible in provided code,
   // but implied by effect.Scale field in Effect class

4. Apply Enhancement Bonuses:
   // Enhancements from slots boost damage
   total_enhancement = Sum of all damage enhancement bonuses in slots
   // Subject to Enhancement Diversification (see Spec 10)
   enhanced_damage = scaled_damage * (1.0 + total_enhancement)

5. Apply Damage Buffs (from other powers):
   // Global damage buffs from Build Up, Aim, set bonuses, etc.
   total_damage_buff = Sum of all active damage buff effects
   // Capped by archetype.DamageCap (typically 400%)
   capped_buff = min(total_damage_buff, archetype.DamageCap)
   final_damage = enhanced_damage * (1.0 + capped_buff)

6. Aggregate by Damage Type:
   // Many powers deal multiple damage types
   damage_totals = {}  // Dictionary keyed by damage type
   For each damage effect in power:
     damage_totals[damage_type] += final_damage

7. Return Damage Summary:
   // Example: "Fire(42.5), Energy(28.3)" or "Total: 70.8"
```

### Key Calculation Methods

**Power.FXGetDamageValue()** - Calculates total damage value across all types

**Power.FXGetDamageString()** - Returns formatted damage display string with type breakdown

**Power.GetDamageTip()** - Generates tooltip showing damage by type with totals

**Effect.GetDamage()** - Extracts damage type and value from individual effect

## Game Mechanics Context

**Why This Exists:**

In City of Heroes, damage is the primary offensive mechanic. The damage calculation system provides:

1. **Archetype Balance**: Different ATs (Blasters, Scrappers, Tankers, etc.) have different damage scales to balance offensive vs defensive capabilities. Blasters deal the most damage but are fragile; Tankers deal less damage but are durable.

2. **Enhancement Choices**: Players slot damage enhancements to boost their attacks, creating meaningful enhancement decisions.

3. **Damage Type Diversity**: Eight damage types create rock-paper-scissors mechanics where different enemy types resist different damage types, encouraging diverse attack selections.

4. **Buff Synergy**: Temporary damage buffs (Build Up, Aim, Fury, etc.) stack multiplicatively with enhancements, creating powerful temporary damage spikes.

**Historical Context:**

- **Launch (2004)**: Original damage system with simple base × enhancement × buff formula
- **Issue 5 (2005)**: Enhancement Diversification added diminishing returns to slotted enhancements, preventing 6-slotting damage from being overwhelming
- **Issue 9 (2006)**: Invention Origin enhancements added set bonuses that could boost damage globally
- **Issue 13 (2008)**: Damage buff caps standardized across archetypes (though values differ per AT)
- **Homecoming (2019+)**: Archetype balance passes adjusted damage scales for several ATs

**Known Quirks:**

1. **DoT vs Direct Damage**: Damage over time (DoT) effects calculate slightly differently - total damage is divided across ticks. The `DamageExt.Ticks` field tracks this.

2. **Percentage Damage**: Some effects deal damage as percentage of target's max HP (rare). These use `DisplayPercentage` or `Aspect == Str` flags and bypass normal enhancement rules.

3. **Damage Caps Vary**: Each AT has a different damage buff cap (stored in `Archetype.DamageCap`). Blasters: 500%, Scrappers: 400%, Tankers: 300%, etc. This prevents over-buffing.

4. **PvE vs PvP Damage**: Many powers have different damage values in PvP contexts. The `Effect.PvMode` field tracks this distinction.

5. **Average vs Minimum Damage Math**: MidsReborn offers two damage calculation modes:
   - Average: Probability-based damage is multiplied by chance (realistic DPS)
   - Minimum: Probability-based damage is excluded (guaranteed damage only)

6. **Pseudopet Damage**: Some powers deliver damage via invisible pseudopets. These follow special rules and may have different enhancement interactions (see Spec 33).

## Python Implementation Notes

**Proposed Architecture:**

```python
# backend/app/calculations/damage.py

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional
from .effects import Effect, EffectType

class DamageType(Enum):
    """Damage types from MidsReborn eDamage enum"""
    NONE = "none"
    SMASHING = "smashing"
    LETHAL = "lethal"
    FIRE = "fire"
    COLD = "cold"
    ENERGY = "energy"
    NEGATIVE = "negative"
    TOXIC = "toxic"
    PSIONIC = "psionic"
    SPECIAL = "special"
    # Positional indicators (not actual damage types)
    MELEE = "melee"
    RANGED = "ranged"
    AOE = "aoe"

@dataclass
class DamageValue:
    """
    Represents damage amount of specific type
    Maps to MidsReborn's Damage struct
    """
    damage_type: DamageType
    value: float
    ticks: int = 0  # For DoT effects, 0 = instant damage
    is_percentage: bool = False  # For %HP damage

    @property
    def per_tick(self) -> float:
        """Damage per tick for DoT"""
        return self.value / self.ticks if self.ticks > 0 else self.value

@dataclass
class DamageSummary:
    """
    Aggregated damage across all types from a power
    Maps to output of Power.GetDamageTip()
    """
    by_type: Dict[DamageType, float]  # Damage totals by type
    total: float  # Sum of all damage
    has_pvp_difference: bool = False  # True if PvE/PvP differ

    def __str__(self) -> str:
        """Format like MidsReborn: 'Fire(42.5), Energy(28.3)'"""
        parts = [f"{dtype.value.title()}({val:.2f})"
                 for dtype, val in self.by_type.items() if val > 0]
        return ", ".join(parts) if parts else "0"

class DamageCalculator:
    """
    Calculates power damage output
    Maps to MidsReborn's Power.FXGetDamageValue() and related methods
    """

    def __init__(self,
                 archetype_damage_scale: float = 1.0,
                 archetype_damage_cap: float = 4.0,
                 use_average_damage: bool = True):
        """
        Args:
            archetype_damage_scale: AT modifier for base damage (Spec 16)
            archetype_damage_cap: Max damage buff (400% default)
            use_average_damage: If True, multiply by probability (realistic)
                              If False, exclude probabilistic damage
        """
        self.at_scale = archetype_damage_scale
        self.damage_cap = archetype_damage_cap
        self.use_average = use_average_damage

    def calculate_power_damage(self,
                              power_effects: List[Effect],
                              enhancement_bonus: float = 0.0,
                              global_damage_buffs: float = 0.0) -> DamageSummary:
        """
        Calculate total damage output from power

        Args:
            power_effects: All effects from the power
            enhancement_bonus: Total damage enhancement from slots (after ED)
            global_damage_buffs: Sum of all damage buff effects from build

        Returns:
            DamageSummary with totals by type
        """
        damage_by_type: Dict[DamageType, float] = {}

        # Step 1: Extract all damage effects
        for effect in power_effects:
            if effect.effect_type != EffectType.DAMAGE:
                continue

            # Step 2: Apply probability filtering
            if not self.use_average and effect.probability < 1.0:
                continue  # Skip probabilistic damage in "minimum" mode

            # Step 3: Get base damage
            base_damage = effect.magnitude

            # Apply probability for average damage mode
            if self.use_average:
                base_damage *= effect.probability

            # Step 4: Apply AT scale (from effect.scale or archetype modifier)
            scaled_damage = base_damage * self.at_scale * effect.scale

            # Step 5: Apply enhancement bonus
            # enhancement_bonus already incorporates ED (see Spec 10)
            enhanced_damage = scaled_damage * (1.0 + enhancement_bonus)

            # Step 6: Apply global damage buffs (capped)
            capped_buffs = min(global_damage_buffs, self.damage_cap)
            final_damage = enhanced_damage * (1.0 + capped_buffs)

            # Step 7: Aggregate by damage type
            damage_type = DamageType(effect.aspect or "none")
            if damage_type not in damage_by_type:
                damage_by_type[damage_type] = 0.0
            damage_by_type[damage_type] += final_damage

        # Calculate total
        total = sum(damage_by_type.values())

        return DamageSummary(
            by_type=damage_by_type,
            total=total
        )

    def calculate_damage_effect(self, effect: Effect) -> Optional[DamageValue]:
        """
        Extract damage from single effect
        Maps to Effect.GetDamage()

        Returns None if effect is not damage or filtered by probability
        """
        if effect.effect_type != EffectType.DAMAGE:
            return None

        if not self.use_average and effect.probability < 1.0:
            return None

        damage_value = effect.magnitude
        if self.use_average:
            damage_value *= effect.probability

        return DamageValue(
            damage_type=DamageType(effect.aspect or "none"),
            value=damage_value,
            # TODO: Extract ticks and percentage info from effect metadata
            ticks=0,
            is_percentage=False
        )
```

**Implementation Priority:**

**CRITICAL** - Implement in Phase 1 (Foundation). Required for:
- Power tooltips showing damage
- DPS calculations
- Build comparison tools
- Attack chain analysis

**Key Implementation Steps:**

1. Define `DamageType` enum matching MidsReborn's `eDamage`
2. Create `DamageValue` and `DamageSummary` dataclasses
3. Implement `DamageCalculator.calculate_power_damage()` with basic formula
4. Integrate with Enhancement Diversification (Spec 10) for enhancement bonus calculation
5. Integrate with Archetype system (Spec 16) for AT damage scale
6. Add damage cap enforcement from Archetype (Spec 17)
7. Handle DoT ticking - defer to depth phase
8. Handle percentage-based damage - defer to depth phase or Spec 43

**Testing Strategy:**

- Unit tests with known power damage values from game data
- Test damage scaling with different AT scales (Blaster 1.125, Scrapper 1.0, Tanker 0.8, etc.)
- Test enhancement bonus application (95% damage enhancement = 1.95x multiplier)
- Test damage buff capping (Blaster cap 500%, Scrapper cap 400%)
- Integration tests comparing Python output to MidsReborn damage display for sample powers:
  - Single-type damage: Power Bolt (Energy Blast, pure energy damage)
  - Multi-type damage: Headsplitter (Battle Axe, smashing + lethal)
  - DoT damage: Flares (Fire Blast, fire damage + fire DoT)
  - Probabilistic damage: Radioactive Smash (Radiation Melee, 80% chance for -def proc)

**Validation Data Sources:**

- MidsReborn damage tooltips for specific powers
- In-game Combat Attributes window "Damage" values
- City of Data website power listings
- CoH Wiki power tables

## References

- **Related Specs**:
  - Spec 01 (Power Effects Core) - Effect data structure
  - Spec 10 (Enhancement Schedules) - ED curves for damage enhancement
  - Spec 16 (Archetype Modifiers) - AT damage scaling
  - Spec 17 (Archetype Caps) - Damage buff caps
  - Spec 22 (Build Totals - Damage) - Global damage buff aggregation
  - Spec 33 (Pseudopet Mechanics) - Special damage delivery
- **MidsReborn Files**:
  - `Core/Base/Data_Classes/Power.cs` (FXGetDamageValue, GetDamageTip)
  - `Core/Base/Data_Classes/Effect.cs` (GetDamage, Damage struct)
  - `Core/Base/Data_Classes/Archetype.cs` (DamageCap)
  - `Core/Enums.cs` (eDamage enum)
- **Game Documentation**:
  - City of Heroes Wiki - "Damage", "Enhancement Diversification"
  - Homecoming Wiki - "Damage" mechanics
  - City of Data - Power damage values database
