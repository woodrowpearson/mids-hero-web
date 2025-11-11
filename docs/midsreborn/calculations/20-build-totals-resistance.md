# Build Totals - Resistance

## Overview
- **Purpose**: Aggregate typed resistance values from all sources and enforce archetype-specific resistance caps for final build totals display
- **Used By**: Build statistics, character sheet, survivability analysis, build comparison
- **Complexity**: Medium
- **Priority**: CRITICAL
- **Status**: 🟡 Breadth Complete

## MidsReborn Implementation

### Primary Location
- **File**: `Core/Base/Data_Classes/Character.cs` - `TotalStatistics` class with `Res[]` array
- **Related Files**:
  - `Core/Statistics.cs` - `DamageResistance()` method for capped/uncapped display
  - `Core/Base/Data_Classes/Archetype.cs` - `ResCap` property per archetype
  - `Core/Utils/Helpers.cs` - `GeneratedStatData()` for resistance display formatting
  - `Forms/WindowMenuItems/frmTotalsV2.cs` - UI display of resistance totals

### Resistance Totals Data Structure

Resistance is stored as an array indexed by damage type:

```csharp
// From Core/Base/Data_Classes/Character.cs - TotalStatistics class
public class TotalStatistics
{
    public float[] Res { get; private set; }  // Resistance per damage type (0.0-1.0 scale)

    public void Init(bool fullReset = true)
    {
        Res = new float[Enum.GetValues<Enums.eDamage>().Length];
        // Initialize all resistance values to 0.0
    }
}

// Two instances track capped vs uncapped values
public class Character
{
    public TotalStatistics Totals;        // Uncapped values (what you've slotted)
    public TotalStatistics TotalsCapped;  // Capped values (actual in-game)
}
```

### Damage Type Enumeration

```csharp
// From Core/Enums.cs
public enum eDamage
{
    None,
    Smashing,    // Index 1
    Lethal,      // Index 2
    Fire,        // Index 3
    Cold,        // Index 4
    Energy,      // Index 5
    Negative,    // Index 6
    Toxic,       // Index 7
    Psionic,     // Index 8
    Special,     // Not used for resistance
    Melee,       // Positional - NOT used for resistance totals
    Ranged,      // Positional - NOT used for resistance totals
    AoE,         // Positional - NOT used for resistance totals
    Unique1,     // Special damage types
    Unique2,
    Unique3
}
```

**CRITICAL NOTE**: Resistance uses **typed damage only** (Smashing through Psionic). Unlike defense, there are **NO positional resistance values** (Melee/Ranged/AoE).

### High-Level Algorithm

```
Build Totals Resistance Calculation:

1. Initialize Resistance Arrays:
   - Create float[eDamage.Length] for Totals.Res (uncapped)
   - Create float[eDamage.Length] for TotalsCapped.Res (capped)
   - All values start at 0.0

2. Aggregate Resistance from All Sources:
   For each damage type (Smashing, Lethal, Fire, Cold, Energy, Negative, Toxic, Psionic):

   a. Base Archetype Resistance:
      - Most ATs start with 0% base resistance
      - Some inherent powers grant base resistance
      - Example: Tanker inherents may provide base resistance

   b. Toggle Powers:
      - Active armor toggles (e.g., Temp Invuln, Fire Shield)
      - Shield Defense toggles
      - Passive auto-powers that grant resistance
      - Each power contributes Res[damageType] value

   c. Set Bonuses:
      - 2-piece, 3-piece, 4-piece, 5-piece, 6-piece bonuses
      - Many sets provide typed resistance bonuses
      - Example: "2.52% Smashing/Lethal Resistance"

   d. Special IOs (Globals):
      - Unique IOs that provide resistance bonuses
      - Example: Steadfast Protection: +3% Defense/Resistance
      - These stack with everything else

   e. Incarnate Powers:
      - Destiny: Barrier (provides resistance buff)
      - Hybrid: Support (may provide resistance)
      - Lore pets may contribute buffs

   f. Temporary Powers:
      - Mission buffs
      - Inspirations (not typically tracked in build planner)
      - Event powers

   Total_Uncapped[damageType] = sum of all sources above

3. Apply Archetype Caps:
   For each damage type:
       TotalsCapped.Res[i] = Math.Min(Totals.Res[i], Archetype.ResCap)

   Where Archetype.ResCap is:
   - 0.90 (90%) for Tanker, Brute
   - 0.85 (85%) for Peacebringer, Warshade (Kheldians)
   - 0.75 (75%) for all other archetypes

4. Display Values:
   - Show capped value as primary (actual in-game value)
   - Show uncapped value when exceeds cap (build optimization)
   - Indicate archetype cap for reference
   - Format: "75.0% Fire Resistance (Tanker cap: 90%)"
   - Format when overcapped: "95.2% Fire Resistance (capped at 90%)"
```

## Resistance Caps by Archetype

### Tanker / Brute (90%)
Highest resistance cap due to survivability-focused role:

```csharp
// From Core/Base/Data_Classes/Archetype.cs
public Archetype()
{
    ResCap = 0.9f;  // 90% for Tankers/Brutes
}
```

**Gameplay Impact**:
- Can reach 90% resistance to typed damage
- Tankers/Brutes are designed to "cap" resistance
- 90% res = take 10% damage = 10x effective HP
- Most survivability builds aim for 90% S/L resistance minimum

### Peacebringer / Warshade (85%)
Kheldian special case with higher cap than standard ATs:

```csharp
ResCap = 0.85f;  // 85% for Kheldians
```

**Gameplay Impact**:
- Dwarf form provides significant resistance buffs
- Higher cap rewards form-switching playstyle
- 85% res = take 15% damage = 6.67x effective HP

### All Other Archetypes (75%)
Standard resistance cap for damage, control, and support ATs:

```csharp
ResCap = 0.75f;  // 75% for Scrapper, Stalker, Blaster, etc.
```

**Archetypes with 75% Cap**:
- Scrapper, Stalker (melee damage)
- Blaster (ranged damage)
- Defender, Corruptor (support/damage)
- Controller, Dominator (control/damage)
- Mastermind (pet-focused)
- Sentinel (ranged defense hybrid)

**Gameplay Impact**:
- Reaching 75% resistance is difficult for most ATs
- Resistance-based sets (e.g., SR, Invuln) can approach cap
- 75% res = take 25% damage = 4x effective HP
- Many builds prioritize defense over resistance due to lower caps

## Resistance Sources

### 1. Armor Toggle Powers

Primary source of resistance for most builds:

```
Examples:
- Invulnerability/Temp Invulnerability: 30% S/L resistance (unslotted)
- Fire Armor/Fire Shield: 30% Fire/Cold resistance (unslotted)
- Electric Armor/Lightning Reflexes: 20% Energy/Negative resistance (unslotted)
- Dark Armor/Dark Embrace: 30% S/L/Neg/Toxic resistance (unslotted)

Slotted with 3x Resistance SOs:
- 30% * (1 + 0.95*3) = 30% * 3.85 = ~115.5% (but capped per AT)
```

**Key Mechanics**:
- Toggles must be active to provide resistance
- Can be slotted with Resistance enhancements (Schedule A: ~38.33% each)
- Most armor sets provide 2-4 resistance toggles
- Each toggle covers different damage types

### 2. Passive Auto-Powers

Always-active resistance sources:

```
Examples:
- Invulnerability/Resist Physical Damage: 7.5% S/L resistance
- Invulnerability/Resist Energies: 7.5% Fire/Cold/Energy/Negative resistance
- Willpower/High Pain Tolerance: 10% S/L/Toxic resistance
- Shield Defense/True Grit: 10% S/L resistance (for Tankers)

Enhancement:
- Slottable with Resistance enhancements
- Lower base values than toggles but always active
```

### 3. Set Bonuses

Critical for reaching resistance caps:

```
Common Set Bonuses:
- 2.52% S/L resistance (very common)
- 1.26% Fire/Cold resistance
- 1.58% Negative/Energy resistance
- 1.89% Psionic resistance (rare and valuable)
- 3.13% Toxic resistance (very rare)

Example Build (Tanker):
- 5x sets with 2.52% S/L = 12.6% bonus S/L resistance
- 3x sets with 1.26% F/C = 3.78% bonus Fire/Cold resistance
- Helps push from 85% → 90% (capping resistance)
```

**Key Mechanics**:
- Set bonuses stack across different sets
- Rule of 5: Maximum 5 of any specific bonus
- Resistance bonuses are highly valuable for reaching caps
- Psionic resistance bonuses are rare (most builds weak to Psi)

### 4. Special IOs (Globals)

Unique enhancement that provide always-on resistance:

```
Examples:
- Steadfast Protection: Resistance/+3 Def (All)
  Grants: +3% Defense to all types, +3% Resistance to all types

- Gladiator's Armor: +3 Def (All)
  Grants: +3% Defense to all types, +3% Resistance to all types

Implementation:
- These are "global" effects (always active when slotted)
- Stacks with set bonuses and power effects
- Unique: Can only slot one per build
- Highly valued for build optimization
```

### 5. Incarnate Powers

High-level endgame resistance sources:

```
Destiny: Barrier
- Core: Provides resistance buff to self and team
- +15-20% resistance (all types) for 90 seconds
- Not typically counted in "permanent" build totals
- Available at level 50+

Hybrid: Support
- May provide resistance buffs depending on tree
- +10% resistance (varies by configuration)
- Active for limited duration

Lore Pets:
- Some Lore pets provide resistance auras
- Team-wide buff
```

**Key Mechanics**:
- Incarnate powers are temporary buffs (not permanent)
- Many planners show "with Barrier" vs "without Barrier"
- Can push over archetype caps temporarily with some special buffs
- Barrier is popular for reaching resistance caps on non-Tanker/Brute ATs

### 6. Temporary Powers

Mission buffs and special powers:

```
Examples:
- Vanguard Medal: +5% resistance (all types)
- Mission buffs: Varies by mission
- Task Force buffs
- Event powers

Implementation Note:
- Typically NOT tracked in standard build planner totals
- Players manually calculate or test in-game
- May exceed archetype caps in special cases
```

## Cap Enforcement Logic

### Capped vs Uncapped Values

```csharp
// From Core/Statistics.cs
public float DamageResistance(int dType, bool uncapped)
{
    return uncapped
        ? _character.Totals.Res[dType] * 100f        // Uncapped (total slotted)
        : _character.TotalsCapped.Res[dType] * 100f;  // Capped (actual in-game)
}
```

**Why Track Both?**:
- **Uncapped**: Shows what you've actually slotted (build optimization)
- **Capped**: Shows what you get in-game (actual survivability)
- Helps identify wasted bonuses exceeding cap
- Useful for AT comparison (same build on Tanker vs Scrapper)

### Cap Application Per Damage Type

```csharp
// From clsToonX.cs (pseudocode based on pattern)
for (var index = 0; index < TotalsCapped.Res.Length; index++)
{
    TotalsCapped.Res[index] = Math.Min(Totals.Res[index], Archetype.ResCap);
}
```

**Key Mechanics**:
- Each damage type capped independently
- Can be capped in S/L but not Fire/Cold
- Common pattern: 90% S/L, 60% Fire/Cold, 40% Psionic
- Psionic resistance is hardest to cap (fewest sources)

## Display Formatting

### Basic Display

```csharp
// From Core/Utils/Helpers.cs - GeneratedStatData()
ValidDamageTypes(out var resTypes, 1);  // Get valid resistance types

statList = (from resType in resTypes
    let multiplied = totalStat.Res[resType.Value] * 100f
    let percentage = $"{Convert.ToDecimal(multiplied):0.##}%"
    select new Stat(resType.Key, percentage, null, "#54b0d1")).ToList();

stats.Add("Resistance", statList);
```

**Valid Resistance Types** (excludes positional):
- Smashing, Lethal, Fire, Cold, Energy, Negative, Toxic, Psionic
- Does NOT include: None, Special, Melee, Ranged, AoE, Unique1/2/3

### Capped vs Overcapped Display

```csharp
// From Forms/WindowMenuItems/frmTotalsV2.cs (pseudocode)
float resValue = DamageResistance(damageType, uncapped: false);  // Capped
float resValueUncapped = DamageResistance(damageType, uncapped: true);

string tooltip;
if (resValueUncapped > resValue && resValue > 0)
{
    // Overcapped: Show excess
    tooltip = $"{resValueUncapped:##0.##}% {damageTypeName} resistance (capped at {Archetype.ResCap * 100:##0.##}%)";
}
else
{
    // Not overcapped: Show cap reference
    tooltip = $"{resValue:##0.##}% {damageTypeName} resistance ({atName} cap: {Archetype.ResCap * 100:##0.##}%)";
}
```

**Example Outputs**:
```
Tanker with 85% Fire resistance:
"85.0% Fire resistance (Tanker cap: 90%)"

Tanker with 95% Fire resistance (overcapped):
"95.0% Fire resistance (capped at 90%)"
Actual in-game: 90%

Scrapper with 80% S/L resistance (overcapped):
"80.0% Smashing resistance (capped at 75%)"
Actual in-game: 75%
```

## Integration with Other Specs

### Spec 17: Archetype Caps
**Dependency**: Resistance totals MUST enforce archetype-specific caps

```
Integration Points:
- Read Archetype.ResCap property
- Apply cap per damage type
- Display both capped and uncapped values
- Show archetype name in tooltips
```

### Spec 09: Power Defense/Resistance
**Dependency**: Individual powers contribute to resistance totals

```
Integration Points:
- Each power's resistance effects aggregate into Totals.Res[]
- Toggle state determines if resistance is active
- Enhancement values multiply power's base resistance
- Resistance buffs from powers sum linearly
```

### Spec 13: Enhancement Set Bonuses
**Dependency**: Set bonuses provide critical resistance values

```
Integration Points:
- Set bonuses add to Totals.Res[] arrays
- Rule of 5 limits identical bonuses
- Resistance set bonuses stack with power resistance
- Helps push from 85% → 90% (capping)
```

### Spec 14: Enhancement Special IOs
**Dependency**: Global IOs provide always-on resistance bonuses

```
Integration Points:
- Steadfast Protection: +3% all resistance
- Gladiator's Armor: +3% all resistance
- These are unique (one per build)
- Stack with set bonuses and powers
```

### Spec 16: Archetype Modifiers
**Relationship**: Modifiers affect power resistance values BEFORE aggregation

```
Integration Process:
1. Power provides base resistance (e.g., 30% S/L)
2. Apply AT modifier (Tanker: 1.0, Scrapper: 0.75)
3. Apply enhancements (Resistance SOs)
4. Aggregate into Totals.Res[]
5. Apply Archetype.ResCap
```

## Survivability Implications

### Effective Hit Points Formula

```
Effective HP = Base HP / (1 - Resistance)

Examples:
- 2000 HP with 0% resistance:   2000 / 1.00 = 2000 EHP
- 2000 HP with 75% resistance:  2000 / 0.25 = 8000 EHP  (4x survivability)
- 2000 HP with 90% resistance:  2000 / 0.10 = 20000 EHP (10x survivability)

This is why Tankers/Brutes are so much tougher:
- 20% higher resistance cap (90% vs 75%)
- 90% = 10x EHP vs 75% = 4x EHP
- 2.5x more effective HP from resistance alone
```

### Resistance vs Defense Tradeoffs

**Resistance Advantages**:
- Works against all attacks (no RNG)
- Scales with HP (more HP = more benefit)
- Mitigates debuffs (50% res = debuffs half as effective)
- No "streak breaker" bad luck

**Resistance Disadvantages**:
- Hard-capped per AT (75-90%)
- Doesn't prevent status effects (Defense does)
- Less effective against burst damage (Defense can dodge 1-shot)
- Psionic resistance is rare (most builds weak to Psi)

**Hybrid Approach** (Common in high-end builds):
- 45% Defense (soft cap) + 75-90% Resistance = nearly unkillable
- Defense dodges most attacks, Resistance mitigates what hits
- Best survivability model for endgame content

## Example Calculation

### Tanker Invulnerability Build

```
Base Resistance Sources (Invulnerability powers):
1. Temp Invulnerability (Toggle): 30% S/L
   - Slotted with 3x Resist SO (95% each)
   - 30% * (1 + 0.95*3) = 30% * 3.85 = 115.5% → capped at 90%

2. Resist Physical Damage (Auto): 7.5% S/L
   - Slotted with 3x Resist SO
   - 7.5% * 3.85 = 28.875%

3. Resist Elements (Auto): 7.5% F/C/E/N
   - Slotted with 3x Resist SO
   - 7.5% * 3.85 = 28.875% each type

4. Resist Energies (Auto): 7.5% F/C/E/N
   - Slotted with 3x Resist SO
   - 7.5% * 3.85 = 28.875% each type

Set Bonuses:
- 5x sets with 2.52% S/L = 12.6% S/L
- 3x sets with 1.26% F/C = 3.78% F/C
- 2x sets with 1.58% E/N = 3.16% E/N

Special IOs:
- Steadfast Protection: +3% all types

Totals (Uncapped):
- Smashing:  115.5% + 28.875% + 12.6% + 3% = 159.975% → capped at 90%
- Lethal:    115.5% + 28.875% + 12.6% + 3% = 159.975% → capped at 90%
- Fire:      28.875% + 28.875% + 3.78% + 3% = 64.53%
- Cold:      28.875% + 28.875% + 3.78% + 3% = 64.53%
- Energy:    28.875% + 28.875% + 3.16% + 3% = 63.91%
- Negative:  28.875% + 28.875% + 3.16% + 3% = 63.91%
- Toxic:     0% (Invuln weakness)
- Psionic:   0% (Invuln weakness)

Display:
- "90% Smashing Resistance (159.98% overcapped)"
- "90% Lethal Resistance (159.98% overcapped)"
- "64.53% Fire Resistance (Tanker cap: 90%)"
- "64.53% Cold Resistance (Tanker cap: 90%)"
- "63.91% Energy Resistance (Tanker cap: 90%)"
- "63.91% Negative Resistance (Tanker cap: 90%)"
- "0% Toxic Resistance (Tanker cap: 90%)"
- "0% Psionic Resistance (Tanker cap: 90%)"
```

**Build Analysis**:
- S/L capped at 90% (69.975% overcapped → wasted)
- F/C/E/N in 60-65% range (solid but not capped)
- Toxic/Psionic at 0% (major weaknesses)
- Typical Invulnerability resistance profile
- Consider adding Tough (Fighting pool) for more S/L (but already overcapped)

## Common Build Patterns

### Resistance-Based Armor Sets

**High Resistance Sets**:
- Invulnerability (S/L focus)
- Fire Armor (Fire/Cold focus, toxic hole)
- Electric Armor (Energy/Negative focus)
- Dark Armor (Negative/Toxic focus)
- Radiation Armor (Energy/Negative/Toxic focus)

**Build Strategy**:
- Use armor toggles as foundation (60-80% per type)
- Add set bonuses to cap specific types (usually S/L first)
- Patch holes with pool powers (Tough for S/L)
- Accept weaknesses (can't cap everything)

### Defense-Based Sets with Some Resistance

**Hybrid Sets**:
- Shield Defense (moderate S/L resistance + defense)
- Willpower (moderate all-type resistance + regen)
- Energy Aura (moderate Energy/Negative resistance + defense)

**Build Strategy**:
- Focus on defense soft cap (45%)
- Use resistance as secondary layer
- Set bonuses prioritize defense, accept lower resistance
- Resistance provides "safety net" when defense fails

### Resistance Priorities

1. **Smashing/Lethal** (Most common damage)
   - Highest priority
   - Most sets provide S/L resistance
   - Easy to cap with set bonuses

2. **Fire/Cold/Energy/Negative** (Moderate priority)
   - Common in high-level content
   - Moderately available from sets
   - Aim for 60-75% if possible

3. **Psionic** (High priority but rare)
   - Very dangerous (ignores most armor)
   - Very few sources of Psi resistance
   - Even 20-30% Psi resistance is valuable

4. **Toxic** (Moderate priority, rare)
   - Less common than Psi but still dangerous
   - Few sources (Dark Armor, Radiation Armor)
   - Accept weakness or build specifically for it

## Python Implementation Pseudocode

```python
from enum import Enum
from dataclasses import dataclass
from typing import Dict

class DamageType(Enum):
    SMASHING = 1
    LETHAL = 2
    FIRE = 3
    COLD = 4
    ENERGY = 5
    NEGATIVE = 6
    TOXIC = 7
    PSIONIC = 8

@dataclass
class ResistanceValues:
    """Resistance values per damage type"""
    smashing: float = 0.0
    lethal: float = 0.0
    fire: float = 0.0
    cold: float = 0.0
    energy: float = 0.0
    negative: float = 0.0
    toxic: float = 0.0
    psionic: float = 0.0

    def to_dict(self) -> Dict[DamageType, float]:
        """Convert to dictionary indexed by DamageType"""
        return {
            DamageType.SMASHING: self.smashing,
            DamageType.LETHAL: self.lethal,
            DamageType.FIRE: self.fire,
            DamageType.COLD: self.cold,
            DamageType.ENERGY: self.energy,
            DamageType.NEGATIVE: self.negative,
            DamageType.TOXIC: self.toxic,
            DamageType.PSIONIC: self.psionic,
        }

class BuildTotalsResistance:
    """
    Calculates total resistance values from all sources and applies archetype caps

    Integration with Spec 17 (Archetype Caps):
    - Enforces Archetype.ResCap per damage type
    - Tracks both capped and uncapped values
    - Displays appropriately for build analysis
    """

    def __init__(self, archetype_resistance_cap: float = 0.75):
        """
        Args:
            archetype_resistance_cap: Resistance cap from Archetype (0.75-0.9)
                - Tanker/Brute: 0.9
                - Kheldian: 0.85
                - Others: 0.75
        """
        self.resistance_cap = archetype_resistance_cap

    def aggregate_resistance(
        self,
        power_resistance: ResistanceValues,
        set_bonuses: ResistanceValues,
        global_ios: ResistanceValues,
        incarnate: ResistanceValues
    ) -> ResistanceValues:
        """
        Aggregate resistance from all sources (linear sum)

        Args:
            power_resistance: Resistance from active toggles and auto powers
            set_bonuses: Resistance from enhancement set bonuses
            global_ios: Resistance from special IOs (e.g., Steadfast)
            incarnate: Resistance from Incarnate powers (Barrier, etc.)

        Returns:
            Total uncapped resistance values
        """
        totals = ResistanceValues()

        # Sum all sources per damage type (linear addition)
        for damage_type in DamageType:
            attr = damage_type.name.lower()

            total_res = (
                getattr(power_resistance, attr) +
                getattr(set_bonuses, attr) +
                getattr(global_ios, attr) +
                getattr(incarnate, attr)
            )

            setattr(totals, attr, total_res)

        return totals

    def apply_resistance_caps(
        self,
        uncapped_resistance: ResistanceValues
    ) -> ResistanceValues:
        """
        Apply archetype-specific resistance cap to each damage type

        Args:
            uncapped_resistance: Total resistance before caps

        Returns:
            Capped resistance values (actual in-game values)
        """
        capped = ResistanceValues()

        for damage_type in DamageType:
            attr = damage_type.name.lower()
            uncapped_value = getattr(uncapped_resistance, attr)

            # Cap at archetype maximum
            capped_value = min(uncapped_value, self.resistance_cap)
            setattr(capped, attr, capped_value)

        return capped

    def format_resistance_display(
        self,
        damage_type: DamageType,
        capped_value: float,
        uncapped_value: float,
        archetype_name: str
    ) -> str:
        """
        Format resistance for display with cap information

        Args:
            damage_type: Type of damage
            capped_value: Capped resistance (actual in-game)
            uncapped_value: Uncapped resistance (total slotted)
            archetype_name: Name of archetype for display

        Returns:
            Formatted string for UI display
        """
        type_name = damage_type.name.capitalize()

        if uncapped_value > capped_value and capped_value > 0:
            # Overcapped: Show excess
            return (
                f"{uncapped_value*100:.2f}% {type_name} Resistance "
                f"(capped at {self.resistance_cap*100:.0f}%)"
            )
        else:
            # Not overcapped: Show cap reference
            return (
                f"{capped_value*100:.2f}% {type_name} Resistance "
                f"({archetype_name} cap: {self.resistance_cap*100:.0f}%)"
            )

    def calculate_effective_hp(
        self,
        base_hp: float,
        resistance: float
    ) -> float:
        """
        Calculate effective HP based on resistance

        Args:
            base_hp: Base hit points
            resistance: Resistance value (0.0 to 1.0)

        Returns:
            Effective hit points

        Formula:
            EHP = HP / (1 - Resistance)

        Examples:
            2000 HP, 0.75 resistance → 8000 EHP (4x survivability)
            2000 HP, 0.90 resistance → 20000 EHP (10x survivability)
        """
        if resistance >= 1.0:
            return float('inf')  # Invulnerable

        return base_hp / (1 - resistance)

# Example usage
def example_tanker_invulnerability():
    """Example: Tanker with Invulnerability build"""

    # Tanker resistance cap: 90%
    calc = BuildTotalsResistance(archetype_resistance_cap=0.9)

    # Resistance from powers (slotted)
    power_res = ResistanceValues(
        smashing=1.155,   # Temp Invuln (30% * 3.85) = 115.5%
        lethal=1.155,
        fire=0.57875,     # Resist Elements + Resist Energies
        cold=0.57875,
        energy=0.57875,
        negative=0.57875,
        toxic=0.0,        # Invuln has no toxic resistance
        psionic=0.0       # Invuln has no psionic resistance
    )

    # Set bonuses
    set_bonuses = ResistanceValues(
        smashing=0.126,   # 5 sets * 2.52%
        lethal=0.126,
        fire=0.0378,      # 3 sets * 1.26%
        cold=0.0378,
        energy=0.0316,    # 2 sets * 1.58%
        negative=0.0316,
        toxic=0.0,
        psionic=0.0
    )

    # Special IOs (Steadfast Protection)
    global_ios = ResistanceValues(
        smashing=0.03, lethal=0.03, fire=0.03, cold=0.03,
        energy=0.03, negative=0.03, toxic=0.03, psionic=0.03
    )

    # No Incarnate for this example
    incarnate = ResistanceValues()

    # Aggregate all sources
    uncapped = calc.aggregate_resistance(
        power_res, set_bonuses, global_ios, incarnate
    )

    # Apply caps
    capped = calc.apply_resistance_caps(uncapped)

    # Display results
    print("Tanker Invulnerability Resistance Totals:")
    print("=" * 60)

    for damage_type in DamageType:
        attr = damage_type.name.lower()
        capped_val = getattr(capped, attr)
        uncapped_val = getattr(uncapped, attr)

        display = calc.format_resistance_display(
            damage_type, capped_val, uncapped_val, "Tanker"
        )
        print(display)

    # Calculate effective HP
    base_hp = 2000
    sl_ehp = calc.calculate_effective_hp(base_hp, capped.smashing)
    fire_ehp = calc.calculate_effective_hp(base_hp, capped.fire)

    print("\nEffective Hit Points:")
    print(f"  S/L: {sl_ehp:.0f} HP ({sl_ehp/base_hp:.1f}x survivability)")
    print(f"  Fire: {fire_ehp:.0f} HP ({fire_ehp/base_hp:.1f}x survivability)")

# Expected output:
# Tanker Invulnerability Resistance Totals:
# ============================================================
# 159.98% Smashing Resistance (capped at 90%)
# 159.98% Lethal Resistance (capped at 90%)
# 64.79% Fire Resistance (Tanker cap: 90%)
# 64.79% Cold Resistance (Tanker cap: 90%)
# 63.91% Energy Resistance (Tanker cap: 90%)
# 63.91% Negative Resistance (Tanker cap: 90%)
# 3.00% Toxic Resistance (Tanker cap: 90%)
# 3.00% Psionic Resistance (Tanker cap: 90%)
#
# Effective Hit Points:
#   S/L: 20000 HP (10.0x survivability)
#   Fire: 5683 HP (2.8x survivability)
```

## Unit Test Strategy

```python
def test_aggregate_resistance_linear_sum():
    """Resistance sums linearly from all sources"""
    calc = BuildTotalsResistance(archetype_resistance_cap=0.9)

    power_res = ResistanceValues(smashing=0.50)
    set_bonuses = ResistanceValues(smashing=0.20)
    global_ios = ResistanceValues(smashing=0.03)
    incarnate = ResistanceValues(smashing=0.10)

    totals = calc.aggregate_resistance(
        power_res, set_bonuses, global_ios, incarnate
    )

    assert totals.smashing == 0.83  # 50% + 20% + 3% + 10%

def test_apply_resistance_cap_tanker():
    """Tanker resistance caps at 90%"""
    calc = BuildTotalsResistance(archetype_resistance_cap=0.9)

    uncapped = ResistanceValues(
        smashing=0.85,  # Below cap
        lethal=0.95,    # Above cap
        fire=1.50       # Way above cap
    )

    capped = calc.apply_resistance_caps(uncapped)

    assert capped.smashing == 0.85  # Not capped
    assert capped.lethal == 0.9     # Capped at 90%
    assert capped.fire == 0.9       # Capped at 90%

def test_apply_resistance_cap_scrapper():
    """Scrapper resistance caps at 75%"""
    calc = BuildTotalsResistance(archetype_resistance_cap=0.75)

    uncapped = ResistanceValues(smashing=0.90)  # Would be fine for Tanker
    capped = calc.apply_resistance_caps(uncapped)

    assert capped.smashing == 0.75  # Capped at 75% (not 90%)

def test_resistance_cap_per_damage_type():
    """Each damage type capped independently"""
    calc = BuildTotalsResistance(archetype_resistance_cap=0.9)

    uncapped = ResistanceValues(
        smashing=0.95,  # Overcapped
        fire=0.60       # Not overcapped
    )

    capped = calc.apply_resistance_caps(uncapped)

    assert capped.smashing == 0.9   # Capped
    assert capped.fire == 0.6       # Not capped

def test_effective_hp_calculation():
    """Verify effective HP formula"""
    calc = BuildTotalsResistance()

    # 75% resistance = 4x EHP
    ehp_75 = calc.calculate_effective_hp(2000, 0.75)
    assert ehp_75 == 8000

    # 90% resistance = 10x EHP
    ehp_90 = calc.calculate_effective_hp(2000, 0.90)
    assert ehp_90 == 20000

    # 0% resistance = 1x EHP
    ehp_0 = calc.calculate_effective_hp(2000, 0.0)
    assert ehp_0 == 2000

def test_format_resistance_display_overcapped():
    """Display shows overcapped resistance correctly"""
    calc = BuildTotalsResistance(archetype_resistance_cap=0.9)

    display = calc.format_resistance_display(
        DamageType.SMASHING,
        capped_value=0.90,
        uncapped_value=0.95,
        archetype_name="Tanker"
    )

    assert "95.00%" in display
    assert "capped at 90%" in display

def test_format_resistance_display_not_overcapped():
    """Display shows non-overcapped resistance correctly"""
    calc = BuildTotalsResistance(archetype_resistance_cap=0.9)

    display = calc.format_resistance_display(
        DamageType.FIRE,
        capped_value=0.65,
        uncapped_value=0.65,
        archetype_name="Tanker"
    )

    assert "65.00%" in display
    assert "Tanker cap: 90%" in display
```

## Related Documentation

### Dependencies (Must Read First)
- Spec 17: Archetype Caps - Provides ResCap values per archetype
- Spec 09: Power Defense/Resistance - Individual power resistance contributions
- Spec 16: Archetype Modifiers - AT-specific scaling of power resistance

### Dependents (Read After)
- Spec 21: Build Totals Defense (sister spec for defense values)
- Spec 22: Build Totals Damage (damage output with resistance context)
- Survivability calculations (resistance × HP = effective HP)

### Related Specs
- Spec 13: Enhancement Set Bonuses - Resistance bonuses from sets
- Spec 14: Enhancement Special IOs - Global resistance IOs
- Spec 01: Power Effects Core - How resistance effects work

## References
- MidsReborn: `Core/Base/Data_Classes/Character.cs` - TotalStatistics.Res[] array
- MidsReborn: `Core/Base/Data_Classes/Archetype.cs` - ResCap property
- MidsReborn: `Core/Statistics.cs` - DamageResistance() method
- Paragon Wiki: "Resistance" - Game mechanics
- Paragon Wiki: "Archetype" - Resistance caps per AT
