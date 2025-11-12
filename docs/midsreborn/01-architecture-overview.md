# MidsReborn Calculation Engine - Architecture Overview

**Purpose**: System-wide understanding of how calculations flow through the MidsReborn codebase
**Last Updated**: 2025-11-10
**Prerequisites**: Read `00-navigation-map.md` first

---

## Executive Summary

The MidsReborn calculation engine is a **top-down orchestrated system** where:
1. **Build.cs** coordinates all calculations
2. **PowerEntry.cs** calculates individual power stats
3. **Enhancement.cs** applies enhancement modifications with ED curves
4. **GroupedFx.cs** aggregates effects from multiple sources
5. **Stats.cs** sums everything into build-wide totals

This document traces the complete calculation flow from user action to final displayed stats.

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      USER ACTIONS                            │
│  (Select Power, Slot Enhancement, Change AT, etc.)          │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                   clsToonX.cs                                │
│              Character/Build State                           │
│  • Maintains current build configuration                    │
│  • Triggers recalculation on state changes                  │
│  • Manages power picks and level progression                │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                     Build.cs                                 │
│              Master Calculation Orchestrator                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Powers List:  List<PowerEntry>                      │   │
│  │ SetBonuses:   List<I9SetData>                       │   │
│  │                                                       │   │
│  │ Key Methods:                                         │   │
│  │  • Recalculate() - Full build recalc               │   │
│  │  • CalculatePower(PowerEntry) - Single power       │   │
│  │  • CalculateSetBonuses() - Set bonus activation     │   │
│  │  • GetBuildTotals() - Aggregate stats              │   │
│  └─────────────────────────────────────────────────────┘   │
└──────┬──────────────┬────────────────┬──────────────────────┘
       │              │                │
       ↓              ↓                ↓
┌────────────┐  ┌────────────┐  ┌─────────────┐
│ PowerEntry │  │ Enhancement│  │   Stats     │
│  Per Power │  │   System   │  │ Aggregation │
└────────────┘  └────────────┘  └─────────────┘
```

---

## Core Subsystems

### 1. Build State Management (clsToonX.cs)

**Purpose**: Maintains character configuration and triggers recalculations

**Responsibilities**:
- Tracks archetype, origin, powersets
- Manages power selection by level
- Monitors build changes that require recalculation
- Provides interface for UI to modify build

**Key Data**:
```csharp
Archetype CurrentArchetype
Powerset[] Powersets  // Primary, Secondary, Pools, Epic
Build CurrentBuild
```

**Trigger Points** (when recalculation needed):
- Power selected/deselected
- Enhancement slotted/removed
- Archetype changed
- Level changed
- Set bonus activation/deactivation

---

### 2. Build Orchestration (Build.cs)

**Purpose**: Coordinates all calculation subsystems

**Architecture**:
```csharp
public class Build
{
    private readonly Character _character;
    public readonly List<PowerEntry?> Powers;        // All powers in build
    public readonly List<I9SetData> SetBonuses;      // Active set bonuses

    // Main orchestration methods
    public void Recalculate()                        // Full recalc
    public void CalculatePower(PowerEntry entry)     // Single power
    public void CalculateSetBonuses()                // Set bonus system
    public Stats GetBuildTotals()                    // Aggregate totals
}
```

**Calculation Flow**:
```
Recalculate() Called
├─> For each PowerEntry in Powers:
│   ├─> CalculatePower(entry)
│   │   ├─> PowerEntry.Calculate()
│   │   ├─> Apply Enhancement ED curves
│   │   ├─> Apply Archetype modifiers
│   │   └─> Update power final stats
│   └─> Add power effects to global pool
├─> CalculateSetBonuses()
│   ├─> Scan all slotted enhancements
│   ├─> Determine set completion (2/3/4/5/6 pieces)
│   ├─> Apply Rule of 5 suppression
│   └─> Add set bonus effects to global pool
└─> GetBuildTotals()
    ├─> Sum all defense from all sources
    ├─> Sum all resistance from all sources
    ├─> Sum all damage bonuses
    ├─> Apply archetype caps
    └─> Return final Stats object
```

---

### 3. Individual Power Calculations (PowerEntry.cs)

**Purpose**: Calculate single power's final stats with all modifiers

**Data Structure**:
```csharp
public class PowerEntry
{
    public IPower? Power;                  // Base power data
    public I9Slot[] Slots;                 // Enhancement slots
    public int Level;                      // Level taken
    public bool Chosen;                    // Is this power selected?

    // Calculated values
    public float FinalDamage;
    public float FinalAccuracy;
    public float FinalRecharge;
    public float FinalEndCost;
    // ... etc for all power attributes
}
```

**Calculation Steps**:
```
1. Load base power data from Power.cs
   ├─> Base damage, accuracy, recharge, endurance, etc.
   └─> Effect list (buffs, debuffs, control, etc.)

2. Apply Archetype modifiers
   ├─> Damage scale (Tanker vs Scrapper)
   ├─> Buff/debuff modifiers
   └─> Control duration modifiers

3. Calculate enhancement bonuses
   ├─> Sum all slotted enhancements by attribute
   ├─> Apply Enhancement Diminishing Returns (ED)
   ├─> Multiply base × (1 + ED_bonus)

4. Apply global modifiers
   ├─> Set bonuses
   ├─> Global recharge
   ├─> Global accuracy
   └─> Other global buffs

5. Store final calculated values
   ├─> FinalDamage, FinalAccuracy, etc.
   └─> Ready for display or aggregation
```

---

### 4. Enhancement System (Enhancement.cs, EnhancementSet.cs, I9Slot.cs)

#### 4A. Enhancement Diminishing Returns (Enhancement.cs)

**Purpose**: Apply ED curves to prevent excessive enhancement stacking

**Critical Function**:
```csharp
public static float ApplyED(float bonusTotal, Schedule schedule)
{
    // Schedule A (Damage, Recharge, etc.): Steeper diminishing returns
    // Schedule B (Defense, etc.): Moderate diminishing returns
    // Schedule C: Light diminishing returns
    // Schedule D: Minimal diminishing returns

    // Returns actual bonus after ED applied
}
```

**ED Curve Structure**:
```
Input Bonus     Schedule A    Schedule B    Schedule C    Schedule D
0-70%           100%          100%          100%          100%
70-100%         90%           85%           95%           98%
100-150%        75%           70%           85%           90%
150%+           50%           50%           65%           75%
```

#### 4B. Set Bonuses (EnhancementSet.cs)

**Purpose**: Calculate set bonus activation and Rule of 5 suppression

**Activation Logic**:
```
For each power:
    Count enhancements by set
    If >= 2 from same set: Activate 2-piece bonus
    If >= 3 from same set: Activate 3-piece bonus
    ... etc up to 6-piece

Apply Rule of 5:
    For each unique bonus type (e.g., +3% Defense):
        If > 5 instances: Suppress weakest instances beyond 5th
```

#### 4C. Slotting (I9Slot.cs)

**Purpose**: Manage enhancement placement in power slots

**Slot Data**:
```csharp
public class I9Slot
{
    public Enhancement? Enhancement;       // What's slotted
    public int Level;                      // Enhancement level
    public bool Boosted;                   // +5 from catalyst?
    public bool Attuned;                   // Scales with level?
}
```

---

### 5. Effect System (Effect.cs, GroupedFx.cs)

#### 5A. IEffect Interface (Effect.cs)

**Purpose**: Unified interface for all game effects

**Effect Types**:
```csharp
public enum eEffectType
{
    Damage,              // Damage dealt
    Defense,             // Defense buff/debuff
    Resistance,          // Damage resistance
    Heal,                // HP restoration
    Endurance,           // Endurance drain/restore
    ToHit,               // ToHit buff/debuff
    Accuracy,            // Accuracy modifier
    Recharge,            // Recharge time modifier
    Hold, Stun, Sleep,   // Control effects
    // ... 50+ effect types total
}
```

**IEffect Structure**:
```csharp
public interface IEffect
{
    eEffectType EffectType { get; }
    float Magnitude { get; }
    float Duration { get; }
    float Probability { get; }
    eAspect Aspect { get; }  // Damage type, etc.
}
```

#### 5B. Effect Grouping (GroupedFx.cs)

**Purpose**: Combine effects from multiple sources using correct stacking rules

**Grouping Logic**:
```
1. Collect all effects from:
   ├─> Powers (primary, secondary, pools, epic)
   ├─> Set bonuses
   ├─> Global IOs (LotG, etc.)
   └─> Incarnate abilities

2. Group by effect type + aspect
   ├─> All "Defense (Smashing)" effects together
   ├─> All "Resistance (Fire)" effects together
   └─> All "Damage (All)" effects together

3. Apply stacking rules:
   ├─> Additive: Defense, Resistance (sum all values)
   ├─> Multiplicative: Some damage buffs (multiply)
   ├─> Best-value-only: Some unique effects
   └─> Special rules: Per effect type

4. Return combined values per type
```

**Example - Defense Aggregation**:
```
Defense (Smashing) Sources:
  Power A: +10%
  Power B: +8%
  Set Bonus 1: +3%
  Set Bonus 2: +3%
  Set Bonus 3: +3% (suppressed by Rule of 5 if 6th)

Stacking: Additive (sum all)
Final: 10 + 8 + 3 + 3 + 3 = 27% Defense (Smashing)
```

---

### 6. Build Totals Aggregation (Stats.cs)

**Purpose**: Sum individual power calculations into build-wide stats

**Stats Structure**:
```csharp
public class Stats
{
    // Defense totals (by damage type and position)
    public float Defense_Smashing { get; set; }
    public float Defense_Lethal { get; set; }
    public float Defense_Fire { get; set; }
    // ... etc for all damage types
    public float Defense_Melee { get; set; }
    public float Defense_Ranged { get; set; }
    public float Defense_AoE { get; set; }

    // Resistance totals
    public float Resistance_Smashing { get; set; }
    // ... etc

    // Global modifiers
    public float GlobalRecharge { get; set; }
    public float GlobalAccuracy { get; set; }
    public float GlobalDamage { get; set; }

    // HP/Endurance
    public float MaxHP { get; set; }
    public float MaxEndurance { get; set; }
    public float Regeneration { get; set; }
    public float Recovery { get; set; }
}
```

**Aggregation Process**:
```
UpdateDefense():
    defense_total = 0
    For each power in build:
        defense_total += power.DefenseBonus
    For each set bonus:
        defense_total += set.DefenseBonus
    Apply archetype cap
    Return capped_defense_total

UpdateResistance():
    Similar process for resistance

UpdateRecharge():
    recharge_bonus = 0
    For each set bonus with +Recharge:
        recharge_bonus += bonus_value
    For each global recharge IO:
        recharge_bonus += io_value
    Return recharge_bonus (usually shown as +X%)

UpdateDamage():
    Aggregate all damage bonuses
    Separate by damage type if needed
    Apply damage caps
```

---

### 7. Archetype Modifier System (Archetype.cs)

**Purpose**: Apply archetype-specific scaling to powers

**Modifiers by AT**:
```csharp
public class Archetype
{
    public string Name { get; }                    // "Tanker", "Scrapper", etc.

    // Damage scaling
    public float DamageScale { get; }              // Tanker: 0.8, Scrapper: 1.125

    // Buff/debuff modifiers
    public float BuffModifier { get; }             // Affects buff strength
    public float DebuffModifier { get; }           // Affects debuff strength

    // Control modifiers
    public float ControlDuration { get; }          // Hold/stun duration

    // Caps
    public float DefenseCap { get; }               // 45% for most, 50% for Tanker
    public float ResistanceCap { get; }            // 75% for most, 90% for Tanker
    public float DamageCap { get; }                // 400% for Tanker, 500% for Scrapper

    // Base stats
    public float BaseHP { get; }                   // HP at level 50
    public float BaseRegen { get; }
    public float BaseRecovery { get; }
}
```

**Application Example - Damage Calculation**:
```
Power: Build Up (Scrapper version)
Base damage buff: +80%
AT modifier: 0.85 (Scrapper buff mod)
Final buff: 80% × 0.85 = 68% damage buff

Same power, Tanker version:
Base damage buff: +80%
AT modifier: 0.75 (Tanker buff mod)
Final buff: 80% × 0.75 = 60% damage buff
```

---

### 8. Data Access Layer (DatabaseAPI.cs)

**Purpose**: Load power/archetype/set data from database

**Key Methods**:
```csharp
public static class DatabaseAPI
{
    public static IPower GetPowerByFullName(string fullName);
    public static Archetype GetArchetypeByName(string name);
    public static EnhancementSet GetSetByName(string name);
    public static List<IPower> GetPowersInPowerset(string powersetName);
}
```

**Note**: In Mids Hero Web, this is replaced by SQLAlchemy queries against PostgreSQL database.

---

## Complete Calculation Flow Example

Let's trace a complete example: **Slotting a damage enhancement in a power**

### Step-by-Step Flow:

```
1. USER ACTION: Slot Level 50 Damage IO (+42.4%) in Fire Blast
   ↓
2. clsToonX.cs: Build state updated
   ├─> Slot data modified
   └─> Triggers Build.Recalculate()
   ↓
3. Build.cs: Recalculate()
   ├─> CalculatePower(Fire Blast entry)
   │   ↓
   │   4. PowerEntry.cs: Calculate Fire Blast
   │   ├─> Base damage: 100 (from Power data)
   │   ├─> Archetype scale: 1.0 (Blaster)
   │   │   └─> Scaled damage: 100 × 1.0 = 100
   │   ├─> Enhancement bonuses:
   │   │   ├─> Damage enhancement: +42.4%
   │   │   ├─> Total bonus before ED: 42.4%
   │   │   ├─> Apply ED (Schedule A):
   │   │   │   └─> 42.4% < 70% threshold → no reduction
   │   │   └─> Final enhancement bonus: +42.4%
   │   ├─> Apply enhancements:
   │   │   └─> Final damage: 100 × (1 + 0.424) = 142.4
   │   └─> Store FinalDamage = 142.4
   ├─> Continue for all other powers...
   ├─> CalculateSetBonuses()
   │   └─> No set completion (single IO)
   └─> GetBuildTotals()
       ├─> Stats.UpdateDamage()
       │   └─> No global damage changes (this was a single power)
       └─> Return updated Stats
   ↓
5. UI UPDATES: Display new damage value
```

---

## Subsystem Dependencies

```
Build.cs (Master Orchestrator)
├─> Depends on:
│   ├─> PowerEntry.cs (power calculations)
│   ├─> Enhancement.cs (ED curves)
│   ├─> EnhancementSet.cs (set bonuses)
│   ├─> Stats.cs (aggregation)
│   ├─> Archetype.cs (AT modifiers)
│   └─> GroupedFx.cs (effect combination)
│
PowerEntry.cs (Individual Power)
├─> Depends on:
│   ├─> Power.cs (base power data)
│   ├─> Enhancement.cs (ED application)
│   ├─> Archetype.cs (scaling)
│   └─> I9Slot.cs (slotted enhancements)
│
Enhancement.cs (Enhancement System)
├─> Depends on:
│   └─> (standalone - core ED logic)
│
EnhancementSet.cs (Set Bonuses)
├─> Depends on:
│   ├─> Enhancement.cs (set completion)
│   └─> GroupedFx.cs (bonus effects)
│
Stats.cs (Build Totals)
├─> Depends on:
│   ├─> PowerEntry.cs (individual power stats)
│   ├─> EnhancementSet.cs (set bonus contributions)
│   ├─> Archetype.cs (caps)
│   └─> GroupedFx.cs (effect aggregation)
│
GroupedFx.cs (Effect Combination)
├─> Depends on:
│   └─> Effect.cs (IEffect interface)
```

---

## Key Calculation Patterns

### Pattern 1: Base → Scale → Enhance → Cap

Used for most power attributes (damage, accuracy, recharge, etc.)

```
1. Get base value from Power data
2. Apply archetype scale modifier
3. Apply enhancement bonuses (with ED)
4. Apply global modifiers
5. Apply archetype caps (if applicable)
6. Return final value
```

### Pattern 2: Collect → Group → Stack → Sum

Used for build totals (defense, resistance, etc.)

```
1. Collect all sources (powers, sets, globals)
2. Group by effect type and aspect
3. Apply stacking rules (additive vs multiplicative)
4. Sum final values
5. Apply caps
6. Return totals
```

### Pattern 3: Scan → Count → Activate → Suppress

Used for set bonuses

```
1. Scan all slotted enhancements
2. Count pieces per set per power
3. Activate bonuses for completed sets
4. Apply Rule of 5 suppression
5. Add bonuses to global effect pool
```

---

## Python Implementation Roadmap

### Proposed Architecture for Mids Hero Web

```
backend/app/calculations/
├─> build_orchestrator.py        # Build.cs equivalent
│   └─> class BuildCalculator
│       ├─> recalculate()
│       ├─> calculate_power()
│       └─> calculate_set_bonuses()
│
├─> power_calculations.py        # PowerEntry.cs equivalent
│   └─> class PowerCalculator
│       ├─> calculate_damage()
│       ├─> calculate_accuracy()
│       └─> calculate_recharge()
│
├─> enhancement_schedules.py     # Enhancement.cs equivalent
│   └─> class EDCurve
│       ├─> apply_ed()
│       └─> get_schedule()
│
├─> set_bonuses.py                # EnhancementSet.cs equivalent
│   └─> class SetBonusCalculator
│       ├─> calculate_set_completion()
│       └─> apply_rule_of_five()
│
├─> effects.py                    # Effect.cs + GroupedFx.cs
│   ├─> class Effect (IEffect equivalent)
│   └─> class EffectAggregator
│       └─> group_and_stack()
│
└─> build_totals.py               # Stats.cs equivalent
    └─> class BuildTotals
        ├─> aggregate_defense()
        ├─> aggregate_resistance()
        └─> aggregate_damage()
```

---

## Next Steps

After understanding this architecture:

1. **Read Calculation Index**: `02-calculation-index.md` for list of all 43 calculations
2. **Dive into Specific Specs**: Browse `calculations/` directory for detailed implementation guides
3. **Start with Foundation**: Implement Effect system and ED curves first (they're dependencies for everything else)
4. **Build Bottom-Up**: PowerEntry → Enhancement → Build orchestration
5. **Test Continuously**: Compare Python output with MidsReborn for validation

---

## Maintenance Notes

**When to Update This Document**:
- Major refactoring of Build.cs calculation flow
- New calculation subsystems discovered
- Dependency relationships change

**Current Version**: Based on MidsReborn codebase as of 2025-07-26

---

**Document Status**: ✅ Complete - Architecture foundation established
**Related Documents**: `00-navigation-map.md`, `02-calculation-index.md`
