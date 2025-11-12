# Diminishing Returns

## Overview
- **Purpose**: Systems that reduce effectiveness of stacking attributes beyond thresholds (beyond Enhancement Diversification curves)
- **Used By**: PvP combat, debuff resistance, proc chance calculations, mez duration calculations
- **Complexity**: Medium
- **Priority**: Medium
- **Status**: 🟡 Breadth Complete

## MidsReborn Implementation

### Primary Locations

**Debuff Resistance System**:
- **File**: `clsToonX.cs`
- **Class**: `clsToonX.SummonBuffs` struct
- **Related Files**:
  - `Core/Enums.cs` - `eEffectType.ResEffect`, `DebuffResistance` enum values
  - `Core/Stats.cs` - Totals tracking for debuff resistance

**Proc Chance Diminishing Returns**:
- **File**: `Core/Base/Data_Classes/Effect.cs`
- **Class**: `Effect`
- **Properties**: `ProcsPerMinute`, `MinProcChance`, `MaxProcChance`

**Elusivity (PvP Defense DR)**:
- **File**: `clsToonX.cs`
- **Related Files**:
  - `Core/Enums.cs` - `eEffectType.Elusivity`
  - `Forms/ImportExportItems/ShareMenu.cs` - Display calculations

### Diminishing Returns Types

MidsReborn implements several diminishing returns systems:

#### 1. Debuff Resistance (ResEffect)

**Effect Type**: `eEffectType.ResEffect`

Provides resistance to specific debuff types. When a character has debuff resistance, incoming debuffs are reduced by that percentage.

**Supported Debuff Types** (from `Enums.cs`):
```csharp
DebuffResistanceDefense = 59,
DebuffResistanceEndurance = 60,
DebuffResistanceRecovery = 61,
DebuffResistancePerception = 62,
DebuffResistanceToHit = 63,
DebuffResistanceRechargeTime = 64,
DebuffResistanceSpeedRunning = 65,
DebuffResistanceRegen = 66
```

**Implementation in clsToonX.cs**:
```csharp
// When processing effects:
case Enums.eEffectType.ResEffect:
    nBuffs.DebuffResistance[(int)effect.ETModifies] += shortFx.Value[shortFxIdx];
    break;

// Later aggregated into totals:
for (var index = 0; index < _selfBuffs.DebuffResistance.Length; index++)
{
    Totals.DebuffRes[index] = _selfBuffs.DebuffResistance[index] * 100;
}
```

**Key Fields**:
- `EffectType` = `ResEffect`
- `ETModifies` = The effect type being resisted (Defense, ToHit, Recharge, etc.)
- `Magnitude` = Resistance strength (0.0-1.0 scale, where 0.75 = 75% resistance)

#### 2. Elusivity (PvP Defense DR)

**Effect Type**: `eEffectType.Elusivity`

Elusivity is a PvP-only mechanic that provides defense-like protection that's separate from defense caps and calculated differently. It stacks with Defense but uses a different formula for hit chance.

**Implementation**:
```csharp
// In clsToonX.cs buff accumulation:
else if ((iEffect == Enums.eEffectType.Elusivity && effect.DamageType != Enums.eDamage.None) & !enhancementPass)
{
    nBuffs.Elusivity[(int)effect.DamageType] += shortFx.Value[shortFxIdx];
}

// Aggregated into totals:
for (var index = 0; index < _selfBuffs.Defense.Length; index++)
{
    Totals.Elusivity[index] = _selfBuffs.Elusivity[index];
}
```

**Display Formula** (from `ShareMenu.cs`):
```csharp
var elValue = (MidsContext.Character.Totals.Elusivity[i] + 0.4f) * 100;
```

The base Elusivity is -40% (displayed as 0%), and it stacks additively.

#### 3. Proc Chance Diminishing Returns

**PPM System** (Procs Per Minute):

Enhancement procs use a PPM (Procs Per Minute) system that enforces minimum and maximum proc chances, creating effective diminishing returns on recharge reduction.

**Implementation in Effect.cs**:
```csharp
public float ProcsPerMinute { get; set; }

private float ActualProbability
{
    get
    {
        var probability = BaseProbability;

        if (ProcsPerMinute > 0 && power != null)
        {
            var areaFactor = (float)(power.AoEModifier * 0.75 + 0.25);

            var globalRecharge = (MidsContext.Character.DisplayStats.BuffHaste(false) - 100) / 100;
            var rechargeVal = Math.Abs(power.RechargeTime) < float.Epsilon
                ? 0
                : power.BaseRechargeTime / (power.BaseRechargeTime / power.RechargeTime - globalRecharge);

            probability = power.PowerType == Enums.ePowerType.Click
                ? ProcsPerMinute * (rechargeVal + power.CastTimeReal) / (60f * areaFactor)
                : ProcsPerMinute * 10 / (60f * areaFactor);

            // Apply min/max bounds (diminishing returns)
            probability = Math.Max(MinProcChance, Math.Min(MaxProcChance, probability));
        }

        return Math.Max(0, Math.Min(1, probability));
    }
}

public float MinProcChance => ProcsPerMinute > 0 ? ProcsPerMinute * 0.015f + 0.05f : 0.05f;
public const float MaxProcChance = 0.9f;
```

**Diminishing Returns Mechanics**:
- **Minimum**: `PPM * 0.015 + 0.05` (e.g., 3.5 PPM = 10.25% minimum)
- **Maximum**: 90% hard cap
- As recharge increases, proc chance would increase linearly, but caps prevent extreme values
- AoE powers have reduced proc chances (`areaFactor` penalty)

#### 4. Mez Duration Enhancement Diminishing Returns

Mez (control) effects apply Enhancement Diversification to duration enhancements, but only certain mez types have enhanceable durations.

**Implementation in clsToonX.cs**:
```csharp
if (eEffectType == Enums.eEffectType.Mez)
{
    eff.Math_Mag = Enhancement.ApplyED(Enhancement.GetSchedule(iEnh, (int)eff.MezType), eff.Math_Mag);
    eff.Math_Duration = Enhancement.ApplyED(Enhancement.GetSchedule(iEnh, (int)eff.MezType), eff.Math_Duration);
}
```

**Enhanceable Mez Types** (from `Enums.cs`):
```csharp
public static bool MezDurationEnhanceable(eMez mezEnum)
{
    return mezEnum is eMez.Confused or eMez.Held or eMez.Immobilized or
                     eMez.Placate or eMez.Sleep or eMez.Stunned or
                     eMez.Taunt or eMez.Terrorized or eMez.Untouchable;
}
```

This applies standard ED curves (see Spec 10) to both magnitude and duration.

#### 5. Status Resistance vs Status Protection

**Status Protection**: Prevents mez effects below a threshold (magnitude-based)
**Status Resistance**: Reduces duration of mez effects that break through protection

Both are tracked separately in the `SummonBuffs` struct:
```csharp
public float[] StatusProtection;  // Magnitude threshold
public float[] StatusResistance;  // Duration reduction (0.0-1.0)
```

Status Resistance effectively creates diminishing returns on incoming mez duration.

### High-Level Algorithm

```
Debuff Resistance Application:
  1. Character receives debuff with magnitude M
  2. Look up character's DebuffResistance for that effect type
  3. Apply resistance: effective_debuff = M * (1 - resistance)
  4. Example: 50% defense debuff with 60% DDR = 50% * 0.4 = 20% actual debuff

Elusivity Calculation (PvP):
  1. Accumulate Elusivity bonuses by damage type
  2. Base elusivity is -0.4 (-40%)
  3. Display value: (elusivity + 0.4) * 100
  4. Hit chance formula uses elusivity separately from defense
     (Exact hit formula would be in combat resolution spec)

Proc Chance with PPM:
  1. Calculate base proc chance from PPM formula
  2. Apply area factor: areaFactor = AoEModifier * 0.75 + 0.25
  3. For click powers: chance = PPM * (recharge + cast_time) / (60 * areaFactor)
  4. For toggle/auto: chance = PPM * 10 / (60 * areaFactor)
  5. Clamp to [MinProcChance, MaxProcChance]
  6. Return final probability

Mez Duration with Resistance:
  1. Calculate base mez duration
  2. Apply enhancement (with ED curves on duration enhancement)
  3. If target has status resistance for that mez type:
     effective_duration = base_duration * (1 - status_resistance)
  4. Mez only applies if magnitude exceeds target's protection
```

### Dependencies

**Required Data**:
- `Effect.ETModifies` - Specifies which effect type a ResEffect applies to
- `Effect.ProcsPerMinute` - PPM value for proc-based effects
- `Character.Totals.DebuffRes[]` - Array of debuff resistance values
- `Character.Totals.Elusivity[]` - Array of elusivity values by damage type

**Used By**:
- Combat calculations (applying debuffs with resistance)
- PvP hit chance calculations (elusivity)
- Enhancement proc probability display
- Build totals display (showing debuff resistance values)

## Game Mechanics Context

### Why This Exists

Diminishing returns systems exist to prevent degenerate gameplay:

1. **Debuff Resistance (DDR)**: Without DDR, debuff-heavy enemies could completely shut down characters, making the game unwinnable. DDR ensures characters can maintain some effectiveness even when heavily debuffed.

2. **Elusivity (PvP)**: In PvP, defense-based characters were nearly impossible to hit when they reached defense caps. Elusivity provides a PvP-specific layer that works differently than defense to balance PvP combat without affecting PvE balance.

3. **Proc Chance Caps**: Without caps, extreme recharge builds could achieve 100%+ proc rates, making procs more powerful than primary powers. Caps prevent proc-based builds from becoming overpowered.

4. **Mez Duration Resistance**: Control effects lasting their full duration on every character type would make controllers/dominators too powerful and melee characters too vulnerable. Duration resistance gives different archetypes different vulnerability levels.

### Historical Context

**Issue 5 (2005) - Enhancement Diversification**: Introduced the first major diminishing returns system (ED curves covered in Spec 10). This set the precedent for limiting extreme stacking.

**Issue 7 (2006) - PvP Revamp**: Added Elusivity as a PvP-specific mechanic. Defense-based characters were dominating PvP, so Elusivity provided a counter-mechanic that only exists in PvP zones.

**Issue 9 (2006) - Invention System**: Introduced PPM procs. The PPM system itself is a diminishing returns mechanic - as you add more recharge, proc chances don't scale linearly due to min/max caps.

**Issue 13 (2008) - Shields and DDR**: Defense Debuff Resistance became more prominent with the Shield Defense powerset. Previously, defense-based sets had no counter to defense debuffs (a major weakness). DDR provided counterplay.

**Homecoming (2019+)**: Expanded debuff resistance to more effect types (recharge debuff resistance, recovery debuff resistance) to improve quality of life against specific enemy groups.

### Known Quirks

1. **DDR is Highly Variable by AT**:
   - Tankers/Brutes: High DDR (60-95% in defense sets)
   - Scrappers: Medium DDR (30-60%)
   - Squishies: Little to no DDR (0-10%)
   - This creates huge differences in how defense sets perform under debuff pressure

2. **Elusivity Doesn't Stack with Defense Caps**:
   - Defense caps at 45% (PvE) or varies by AT (PvP)
   - Elusivity is a separate layer, so you can have 45% defense + high elusivity
   - The two values combine in the hit formula but are tracked separately

3. **Proc Caps Penalize Fast-Recharging Powers**:
   - A 3.5 PPM proc in a 4-second recharge power might be at 90% cap
   - Same proc in a 120-second recharge power might be at 15% chance
   - This creates a "sweet spot" for proc usage (medium-recharge powers)

4. **Multiple Procs Don't Interfere**:
   - Unlike some games, multiple different procs in the same power each roll independently
   - No "proc budget" or shared probability pool
   - Each proc just has its own PPM-based chance with individual min/max caps

5. **ResEffect Stacks Additively**:
   - Multiple sources of debuff resistance stack additively
   - Can exceed 100% resistance (making you immune to that debuff type)
   - Some powersets grant 95%+ recharge debuff resistance (essentially immunity to -recharge)

6. **Mez Resistance vs Protection Confusion**:
   - Protection is magnitude-based (threshold)
   - Resistance is duration-based (percentage reduction)
   - Both exist simultaneously but do different things
   - Common player confusion: "Why did I still get stunned with high resistance?" (Because protection was overcome)

7. **PvP DR Exists Beyond These Systems**:
   - PvP has additional diminishing returns on many stats (damage, healing, etc.) that are separate from these mechanics
   - Those would be covered in a separate "PvP Combat Modifiers" spec
   - This spec focuses on the specific named DR systems in MidsReborn

## Python Implementation Notes

### Proposed Architecture

```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class DebuffResistanceType(Enum):
    """Types of debuff resistance"""
    DEFENSE = 59
    ENDURANCE = 60
    RECOVERY = 61
    PERCEPTION = 62
    TO_HIT = 63
    RECHARGE_TIME = 64
    SPEED_RUNNING = 65
    REGEN = 66

@dataclass
class DebuffResistance:
    """Debuff resistance values by type"""
    defense: float = 0.0      # Defense Debuff Resistance (DDR)
    endurance: float = 0.0    # Endurance debuff resistance
    recovery: float = 0.0     # Recovery debuff resistance
    perception: float = 0.0   # Perception debuff resistance
    to_hit: float = 0.0       # ToHit debuff resistance
    recharge_time: float = 0.0  # Recharge debuff resistance
    speed_running: float = 0.0  # Slow resistance
    regen: float = 0.0        # Regeneration debuff resistance

    def apply_resistance(self, debuff_type: DebuffResistanceType,
                        debuff_magnitude: float) -> float:
        """Apply debuff resistance to incoming debuff"""
        resistance = getattr(self, debuff_type.name.lower())
        return debuff_magnitude * (1.0 - resistance)

@dataclass
class ElusivityValues:
    """Elusivity by damage type (PvP only)"""
    smashing: float = -0.4
    lethal: float = -0.4
    fire: float = -0.4
    cold: float = -0.4
    energy: float = -0.4
    negative: float = -0.4
    toxic: float = -0.4
    psionic: float = -0.4

    def display_value(self, damage_type: str) -> float:
        """Convert internal elusivity to display percentage"""
        value = getattr(self, damage_type)
        return (value + 0.4) * 100.0

@dataclass
class ProcChanceConfig:
    """Configuration for proc chance calculations"""
    procs_per_minute: float
    recharge_time: float
    cast_time: float
    aoe_modifier: float = 1.0
    is_click_power: bool = True
    global_recharge_bonus: float = 0.0  # As percentage (e.g., 70.0 for +70%)

    @property
    def min_proc_chance(self) -> float:
        """Calculate minimum proc chance"""
        if self.procs_per_minute <= 0:
            return 0.05
        return self.procs_per_minute * 0.015 + 0.05

    @property
    def max_proc_chance(self) -> float:
        """Maximum proc chance is hard-capped"""
        return 0.90

    def calculate_proc_chance(self) -> float:
        """Calculate actual proc chance with diminishing returns"""
        if self.procs_per_minute <= 0:
            return 0.0

        # Area factor calculation
        area_factor = self.aoe_modifier * 0.75 + 0.25

        # Global recharge adjustment
        global_recharge = self.global_recharge_bonus / 100.0

        if abs(self.recharge_time) < 0.001:
            recharge_val = 0.0
        else:
            base_recharge = self.recharge_time  # Would need base recharge from power data
            recharge_val = base_recharge / (base_recharge / self.recharge_time - global_recharge)

        # PPM formula
        if self.is_click_power:
            probability = (self.procs_per_minute * (recharge_val + self.cast_time)) / (60.0 * area_factor)
        else:
            probability = (self.procs_per_minute * 10.0) / (60.0 * area_factor)

        # Apply min/max caps (diminishing returns)
        return max(self.min_proc_chance, min(self.max_proc_chance, probability))

@dataclass
class StatusResistance:
    """Resistance to mez effect durations"""
    hold: float = 0.0
    stun: float = 0.0
    immobilize: float = 0.0
    sleep: float = 0.0
    confuse: float = 0.0
    fear: float = 0.0
    terrorized: float = 0.0
    taunt: float = 0.0
    placate: float = 0.0

    def apply_to_duration(self, mez_type: str, base_duration: float) -> float:
        """Apply status resistance to mez duration"""
        resistance = getattr(self, mez_type, 0.0)
        return base_duration * (1.0 - resistance)
```

### Key Functions

```python
def apply_debuff_with_resistance(
    debuff_magnitude: float,
    debuff_type: DebuffResistanceType,
    character_resistance: DebuffResistance
) -> float:
    """
    Apply debuff resistance to incoming debuff.

    Args:
        debuff_magnitude: Raw magnitude of incoming debuff (0.0-1.0)
        debuff_type: Type of debuff being resisted
        character_resistance: Character's debuff resistance values

    Returns:
        Effective debuff magnitude after resistance
    """
    return character_resistance.apply_resistance(debuff_type, debuff_magnitude)

def calculate_elusivity_display(
    elusivity_values: ElusivityValues,
    damage_type: str
) -> float:
    """
    Calculate display value for elusivity (PvP mechanic).

    Args:
        elusivity_values: Character's elusivity by damage type
        damage_type: Damage type to display

    Returns:
        Display percentage (0.0 = base, positive = better defense)
    """
    return elusivity_values.display_value(damage_type)

def calculate_proc_chance_with_dr(
    ppm: float,
    recharge: float,
    cast_time: float,
    aoe_modifier: float = 1.0,
    is_click: bool = True,
    global_recharge: float = 0.0
) -> float:
    """
    Calculate proc chance with PPM diminishing returns.

    Args:
        ppm: Procs per minute value
        recharge: Current recharge time (after enhancements)
        cast_time: Power cast/activation time
        aoe_modifier: Area effect modifier (>1.0 for AoE powers)
        is_click: True for click powers, False for toggles/autos
        global_recharge: Global recharge bonus as percentage

    Returns:
        Probability (0.0-1.0) clamped to min/max caps
    """
    config = ProcChanceConfig(
        procs_per_minute=ppm,
        recharge_time=recharge,
        cast_time=cast_time,
        aoe_modifier=aoe_modifier,
        is_click_power=is_click,
        global_recharge_bonus=global_recharge
    )
    return config.calculate_proc_chance()

def accumulate_debuff_resistance(
    effects: list,
    current_resistance: DebuffResistance
) -> DebuffResistance:
    """
    Accumulate debuff resistance from multiple effect sources.

    Args:
        effects: List of ResEffect type effects
        current_resistance: Starting resistance values

    Returns:
        Updated resistance values (additive stacking)
    """
    # Implementation would iterate effects where EffectType == ResEffect
    # and add magnitude to appropriate resistance field based on ETModifies
    pass

def apply_ddr(
    defense_debuff: float,
    defense_debuff_resistance: float
) -> float:
    """
    Apply Defense Debuff Resistance (DDR) to incoming defense debuff.

    Args:
        defense_debuff: Magnitude of defense debuff (positive = debuff)
        defense_debuff_resistance: DDR value (0.0-1.0+, can exceed 1.0)

    Returns:
        Effective defense debuff after DDR

    Example:
        >>> apply_ddr(0.50, 0.60)  # 50% defense debuff, 60% DDR
        0.20  # 20% effective debuff
    """
    return defense_debuff * (1.0 - min(defense_debuff_resistance, 1.0))
```

### Integration Points

1. **Effect Processing**:
   - When processing `ResEffect` type effects, accumulate into `DebuffResistance` struct
   - Track `ETModifies` field to determine which resistance type to increment

2. **Combat Resolution**:
   - When applying debuffs to character, look up appropriate debuff resistance
   - Calculate effective debuff: `original * (1 - resistance)`

3. **Build Totals**:
   - Display debuff resistance percentages in character stats
   - Show elusivity values in PvP mode

4. **Proc Display**:
   - Calculate actual proc chances using PPM formula with DR caps
   - Show both PPM value and effective percentage

### Deferred to Milestone 3 (Depth)

- Exact PvP hit chance formula incorporating elusivity
- PvP-wide diminishing returns system (separate from elusivity)
- Combat modifier tables for mez resistance by AT
- Interaction between multiple proc types in same power
- Edge cases: procs in auto powers, procs in pseudopets
- Status effect stacking and magnitude breakthrough mechanics
- Advanced: Resistance resistance (resisting resistance debuffs)
