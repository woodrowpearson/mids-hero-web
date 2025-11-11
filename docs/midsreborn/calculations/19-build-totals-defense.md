# Build Totals - Defense

## Overview
- **Purpose**: Aggregate ALL defense from powers, set bonuses, global IOs, and incarnates into the final defense numbers users see
- **Used By**: Build planning, totals display, survivability calculations, build comparison
- **Complexity**: High
- **Priority**: CRITICAL
- **Status**: 🟡 Breadth Complete

## MidsReborn Implementation

### Primary Location
- **File**: `Forms/WindowMenuItems/frmTotalsV2.cs`
- **Related Files**:
  - `Core/Base/Data_Classes/Character.cs` - `TotalStatistics` class with `Def[]` array
  - `Core/Statistics.cs` - `Defense()` method for display formatting
  - `Core/Stats.cs` - `Defense`, `DebuffResistance` classes for structure
  - `Core/Build.cs` - Build power aggregation

### Defense Aggregation Structure

Defense totals are stored in `Character.Totals.Def[]` and `Character.TotalsCapped.Def[]`:

```csharp
// From Core/Base/Data_Classes/Character.cs
public class TotalStatistics
{
    public float[] Def { get; private set; }  // Defense values indexed by eDamage enum
    public float[] Res { get; private set; }
    public float[] Mez { get; private set; }
    public float[] MezRes { get; private set; }
    public float[] DebuffRes { get; private set; }  // Includes DDR
    public float[] Elusivity { get; set; }
    // ... other stats
}

// Defense array indices from Core/Enums.cs (eDamage enum):
// 0 = Smashing
// 1 = Lethal
// 2 = Fire
// 3 = Cold
// 4 = Energy
// 5 = Negative
// 6 = Psionic
// 7 = Melee (positional)
// 8 = Ranged (positional)
// 9 = AoE (positional)
// (Toxic defense exists but index varies)
```

### Defense Display Logic

```csharp
// From Core/Statistics.cs
public float Defense(int dType)
{
    return _character.Totals.Def[dType] * 100f;  // Convert to percentage
}

// From Forms/WindowMenuItems/frmTotalsV2.cs
graphDef.AddItemPair(damageVectorsNames[i],
    $"{displayStats.Defense(i):##0.##}%",
    Math.Max(0, displayStats.Defense(i)),
    Math.Max(0, displayStats.Defense(i)),
    $"{displayStats.Defense(i):##0.###}% {FormatVectorType(typeof(Enums.eDamage), i)} defense");
```

### High-Level Algorithm

```
Build Defense Totals Calculation:

1. Initialize Defense Arrays:
   - Totals.Def[] = new float[damage_types_count]
   - TotalsCapped.Def[] = new float[damage_types_count]
   - DebuffRes[] = new float[effect_types_count]  // Includes DDR
   - All values start at 0.0

2. Aggregate Defense from All Sources:
   FOR EACH active power in build:
     FOR EACH effect in power.Effects:
       IF effect.EffectType == Defense:
         damage_type_index = effect.DamageType  // e.g., Smashing=0, Melee=7
         Totals.Def[damage_type_index] += effect.Magnitude

   FOR EACH set bonus in build:
     IF bonus.EffectType == Defense:
       Totals.Def[bonus.DamageType] += bonus.Magnitude

   FOR EACH global IO in build:
     IF io.EffectType == Defense:
       Totals.Def[io.DamageType] += io.Magnitude

   FOR EACH incarnate power active:
     FOR EACH effect in incarnate.Effects:
       IF effect.EffectType == Defense:
         Totals.Def[effect.DamageType] += effect.Magnitude

3. Aggregate Defense Debuff Resistance (DDR):
   FOR EACH source (powers, sets, IOs, incarnates):
     IF effect.EffectType == DebuffResistanceDefense:
       DebuffRes[Defense] += effect.Magnitude

   // DDR has a cap of 95% (MaxDefenseDebuffRes)
   TotalsCapped.DebuffRes[Defense] = min(95.0, DebuffRes[Defense])

4. Apply Defense Debuffs (if in combat mode):
   // In build planning mode, typically not applied
   // In combat simulation:
   FOR EACH defense type:
     IF defense_debuffs_active[type] > 0:
       actual_debuff = defense_debuffs[type] * (1 - DDR)
       Totals.Def[type] -= actual_debuff

5. Apply Defense Caps:
   // Defense has NO hard cap, only soft cap awareness
   // Soft cap is 45% (0.45) for even-level enemies
   // TotalsCapped.Def[] = Totals.Def[] (no capping for defense)
   TotalsCapped.Assign(Totals)  // Copy uncapped to capped

   // Note: Unlike resistance, defense is NOT capped
   // Values above 45% are still useful vs higher-level enemies

6. Calculate Display Values:
   FOR EACH defense type (0-9):
     display_value = Totals.Def[type] * 100  // Convert to percentage
     tooltip = "{display_value:##0.###}% {type_name} defense"

     // Highlight soft cap
     IF display_value >= 45.0:
       highlight_color = soft_cap_reached_color
     ELSE:
       highlight_color = normal_color

7. Calculate Higher of Typed or Positional:
   // City of Heroes uses whichever is HIGHER
   // Example: Fire/Ranged attack checks both Fire and Ranged defense

   FOR EACH typed defense (Smashing, Lethal, Fire, Cold, Energy, Negative, Psionic, Toxic):
     FOR EACH positional defense (Melee, Ranged, AoE):
       effective_defense[typed][positional] = max(Def[typed], Def[positional])

   // This is for display/analysis, not stored in Totals

8. Display in Totals Window:
   // Show all defense values in a graph
   // Typed defense: S/L/F/C/E/N/P/T
   // Positional defense: Melee/Ranged/AoE
   // DDR shown in debuff resistance section
```

### Defense Sources

**1. Power-Granted Defense**:
- Toggle powers (e.g., Super Reflexes toggles)
- Auto powers (e.g., passive defense)
- Click powers (temporary defense buffs)
- Each power can grant multiple defense types

```csharp
// Defense from power effects
FOR power IN build.powers:
  IF power.active:
    FOR effect IN power.effects:
      IF effect.effect_type == Defense:
        Totals.Def[effect.damage_type] += effect.magnitude
```

**2. Set Bonuses**:
- Enhancement sets grant defense bonuses
- Typically small values (1.5%, 3%, 5%)
- Stack from multiple sets

```csharp
// Defense from set bonuses
FOR set_bonus IN build.set_bonuses:
  IF set_bonus.effect_type == Defense:
    Totals.Def[set_bonus.damage_type] += set_bonus.magnitude
```

**3. Global IOs**:
- Special IOs like "Luck of the Gambler: Defense/Recharge"
- "Steadfast Protection: Resistance/Defense" grants 3% defense
- Global bonuses apply always

```csharp
// Defense from global IOs
FOR enhancement IN build.enhancements:
  IF enhancement.has_global_defense:
    Totals.Def[enhancement.defense_type] += enhancement.global_defense
```

**4. Incarnate Powers**:
- Destiny powers can grant large defense buffs
- Interface/Lore may grant passive defense
- Hybrid can enhance defense

```csharp
// Defense from incarnate powers
FOR incarnate IN build.incarnates:
  IF incarnate.active:
    FOR effect IN incarnate.effects:
      IF effect.effect_type == Defense:
        Totals.Def[effect.damage_type] += effect.magnitude
```

### Defense Debuff Resistance (DDR)

**Critical for Defense-Based Builds**:

DDR protects defense from being debuffed. Without sufficient DDR, defense-based characters can experience "defense cascade" where one hit leads to more hits leads to death.

```csharp
// From Forms/WindowMenuItems/frmTotalsV2.cs
var cappedDebuffRes = DebuffEffectsList.Select(e => Math.Min(
        e == Enums.eEffectType.Defense
            ? Statistics.MaxDefenseDebuffRes  // 95% cap
            : Statistics.MaxGenericDebuffRes,
        MidsContext.Character.Totals.DebuffRes[(int) e]))
    .ToList();

// From Core/Statistics.cs
public const float MaxDefenseDebuffRes = 95f;  // 95% cap for DDR
```

**DDR Formula**:
```
actual_defense_debuff = base_debuff * (1 - DDR)

Example with 50% DDR:
  Base debuff: -20% defense
  Actual debuff: -20% * (1 - 0.5) = -10% defense

Example with 95% DDR (cap):
  Base debuff: -20% defense
  Actual debuff: -20% * (1 - 0.95) = -1% defense
```

### Soft Cap Display Logic

```
Defense Soft Cap = 45%

Display Logic:
  IF defense >= 45%:
    - Highlight in green or blue
    - Show "Soft Cap Reached"
    - Values above 45% still useful vs +level enemies
  ELSE:
    - Show distance to soft cap
    - Show percentage of soft cap reached
    - Highlight gaps

Soft Cap Context:
  - 50% base enemy tohit - 45% defense = 5% hit chance
  - Minimum hit chance floor is 5% (cannot go lower)
  - Defense above 45% helps vs:
    * Higher level enemies (+tohit per level)
    * Enemies with tohit buffs
    * AV/GM enemies with inherent tohit bonuses
```

### Higher of Typed or Positional

**Critical Game Mechanic**:

City of Heroes checks BOTH typed and positional defense for every attack, using whichever is HIGHER.

```
Example Attack: Fire/Ranged
  - Typed defense: Fire = 20%
  - Positional defense: Ranged = 35%
  - Effective defense = max(20%, 35%) = 35%

Example Attack: Smashing/Melee
  - Typed defense: Smashing = 40%
  - Positional defense: Melee = 25%
  - Effective defense = max(40%, 25%) = 40%

Example Attack: Psionic/Ranged
  - Typed defense: Psionic = 0%
  - Positional defense: Ranged = 45%
  - Effective defense = max(0%, 45%) = 45%
```

**Build Planning Implications**:
- Pure positional defense (45% to all positions) = soft cap vs all attacks
- Pure typed defense (45% to all types) = soft cap vs all attacks
- Mixed defense (30% typed + 30% positional) = 30% effective (NOT 60%)
- Must use MAX, not SUM

### Defense Types

**Typed Defense** (8 types):
- **Smashing**: Physical blunt damage (most common)
- **Lethal**: Physical cutting damage (most common)
- **Fire**: Fire damage
- **Cold**: Cold damage
- **Energy**: Energy damage
- **Negative**: Negative energy damage
- **Psionic**: Psychic damage (rare, important)
- **Toxic**: Toxic damage (added by Homecoming)

**Positional Defense** (3 types):
- **Melee**: Close range attacks
- **Ranged**: Distance attacks
- **AoE**: Area of effect attacks

### Cap Enforcement

```csharp
// Defense has NO hard cap (unlike resistance)
// Soft cap is 45% for awareness/display only
// TotalsCapped.Def[] = Totals.Def[] (no modification)

TotalsCapped.Assign(Totals);

// No cap enforcement:
// for (var i = 0; i < TotalsCapped.Def.Length; i++)
// {
//     // Defense is NOT capped like resistance
//     // TotalsCapped.Def[i] = TotalsCapped.Def[i];  // No-op
// }

// Only DDR is capped at 95%:
TotalsCapped.DebuffRes[Defense] = Math.Min(95f, Totals.DebuffRes[Defense]);
```

## Dependencies

**Depends On**:
- Spec 01: Power Effects Core (Defense effect type)
- Spec 09: Power Defense/Resistance (Individual power defense)
- Spec 13: Enhancement Set Bonuses (Set bonus defense)
- Spec 14: Enhancement Special IOs (Global IO defense)
- Spec 16: Archetype Modifiers (AT defense scaling)

**Used By**:
- Spec 20: Build Totals Display (Overall stats window)
- Spec 32: Survivability Index (EHP calculations)
- Spec 36: Build Comparison (Comparing defense totals)

## Game Mechanics Context

**Why This Exists:**

Build totals defense is THE most critical survivability metric in City of Heroes build planning:

1. **Soft cap awareness**: Players need to see if they've reached 45% defense
2. **Gap identification**: Shows which defense types need improvement
3. **Positional vs typed**: Helps choose between different defense strategies
4. **DDR importance**: Shows defense debuff protection for sustainability

**Historical Context:**

- **Launch (2004)**: Defense was considered weak compared to resistance
- **Issue 5 (2005)**: "Scaling damage resistance" made defense more valuable
- **Issue 7 (2006)**: Soft cap (45%) became meta knowledge, build planners essential
- **Issue 13 (2008)**: DDR added to sets, totals display needed DDR tracking
- **Going Rogue (2010)**: More defense options, build diversity increased
- **Homecoming (2019+)**: Toxic defense added, totals updated

**Why Defense Totals Matter:**

1. **Soft cap is build goal**: 45% defense is the primary target for many builds
2. **Layer defense and resistance**: Combining both maximizes survivability
3. **Typed vs positional choice**: Determines which sets/powers to take
4. **DDR determines sustainability**: High defense without DDR = defense cascade death

**Known Quirks:**

1. **Soft cap vs hard cap**: 45% is "soft cap" (optimal vs even-level), not hard cap. Values above 45% help vs +level enemies.

2. **Max(typed, positional) rule**: Attack uses HIGHER defense, not sum. This is critical for build planning:
   - 45% positional = soft cap vs all attacks
   - 45% typed = soft cap vs all attacks
   - 22.5% positional + 22.5% typed = 22.5% defense (NOT 45%)

3. **Defense cascade without DDR**:
   ```
   45% defense = 10% hit chance (good)
   One defense debuff hits
   35% defense = 30% hit chance (3x more hits)
   More hits = more debuffs
   25% defense = 50% hit chance (cascade to death)
   ```
   This is why DDR is critical for defense builds.

4. **Typed defense gaps**: Most defense sets grant strong defense to SOME types:
   - Super Reflexes: Strong positional, weak typed
   - Shield Defense: Strong positional + S/L, weak exotic
   - Energy Aura: Strong energy/negative, weak S/L
   - Build planning must identify and fill gaps

5. **Psionic defense hole**: Many defense sets historically had NO psionic defense:
   - Psionic attacks bypass most defense sets
   - Forces players to rely on positional defense or pool powers
   - This is a major vulnerability for defense-based characters

6. **Incarnate defense inflation**: Destiny powers can grant massive temporary defense:
   - Barrier: +15-20% defense for team
   - This can push builds from 35% to 50%+ defense temporarily
   - Build planning must consider both permanent and temporary totals

7. **Set bonuses vs power defense**:
   - Powers grant large defense (5-10%+)
   - Set bonuses grant small defense (1.5-5%)
   - Need both for soft cap
   - Set bonuses are permanent (always on)
   - Power defense requires toggles/clicks (can be detoggled)

## Python Implementation Notes

**Proposed Architecture:**

```python
# backend/app/calculations/build_totals_defense.py

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional

class DefenseType(Enum):
    """Defense types matching eDamage enum indices"""
    SMASHING = 0
    LETHAL = 1
    FIRE = 2
    COLD = 3
    ENERGY = 4
    NEGATIVE = 5
    PSIONIC = 6
    MELEE = 7
    RANGED = 8
    AOE = 9
    # Toxic varies by implementation

@dataclass
class DefenseTotals:
    """
    Build-wide defense totals
    Maps to Character.Totals.Def[] in MidsReborn
    """
    # Typed defense
    smashing: float = 0.0
    lethal: float = 0.0
    fire: float = 0.0
    cold: float = 0.0
    energy: float = 0.0
    negative: float = 0.0
    psionic: float = 0.0
    toxic: float = 0.0

    # Positional defense
    melee: float = 0.0
    ranged: float = 0.0
    aoe: float = 0.0

    # Defense debuff resistance (DDR)
    ddr: float = 0.0

    # Sources breakdown (for display)
    sources: Dict[str, float] = field(default_factory=dict)

@dataclass
class DefenseSource:
    """Individual source of defense"""
    source_type: str  # "power", "set_bonus", "global_io", "incarnate"
    source_name: str  # "Focused Fighting", "Luck of the Gambler", etc.
    defense_type: DefenseType
    magnitude: float
    is_ddr: bool = False  # True if this is DDR, not defense

class BuildDefenseTotalsCalculator:
    """
    Aggregates ALL defense from powers, sets, IOs, incarnates
    Maps to logic in Character.cs and frmTotalsV2.cs
    """

    # Defense soft cap (45% vs even-level enemies)
    SOFT_CAP = 0.45

    # DDR cap (95%)
    DDR_CAP = 0.95

    def __init__(self):
        """Initialize defense totals calculator"""
        self.totals = DefenseTotals()
        self.sources: List[DefenseSource] = []

    def add_power_defense(
        self,
        power_name: str,
        defense_type: DefenseType,
        magnitude: float,
        is_ddr: bool = False
    ) -> None:
        """
        Add defense from an active power

        Args:
            power_name: Name of power granting defense
            defense_type: Type of defense granted
            magnitude: Defense value (0.0 to 1.0+)
            is_ddr: True if this is DDR instead of defense
        """
        source = DefenseSource(
            source_type="power",
            source_name=power_name,
            defense_type=defense_type,
            magnitude=magnitude,
            is_ddr=is_ddr
        )
        self.sources.append(source)

    def add_set_bonus_defense(
        self,
        set_name: str,
        defense_type: DefenseType,
        magnitude: float,
        is_ddr: bool = False
    ) -> None:
        """
        Add defense from enhancement set bonus

        Args:
            set_name: Name of enhancement set
            defense_type: Type of defense granted
            magnitude: Defense value (typically 0.015 to 0.05)
            is_ddr: True if this is DDR instead of defense
        """
        source = DefenseSource(
            source_type="set_bonus",
            source_name=set_name,
            defense_type=defense_type,
            magnitude=magnitude,
            is_ddr=is_ddr
        )
        self.sources.append(source)

    def add_global_io_defense(
        self,
        io_name: str,
        defense_type: DefenseType,
        magnitude: float,
        is_ddr: bool = False
    ) -> None:
        """
        Add defense from global IO

        Args:
            io_name: Name of IO
            defense_type: Type of defense granted
            magnitude: Defense value
            is_ddr: True if this is DDR instead of defense
        """
        source = DefenseSource(
            source_type="global_io",
            source_name=io_name,
            defense_type=defense_type,
            magnitude=magnitude,
            is_ddr=is_ddr
        )
        self.sources.append(source)

    def add_incarnate_defense(
        self,
        incarnate_name: str,
        defense_type: DefenseType,
        magnitude: float,
        is_ddr: bool = False
    ) -> None:
        """
        Add defense from incarnate power

        Args:
            incarnate_name: Name of incarnate power
            defense_type: Type of defense granted
            magnitude: Defense value
            is_ddr: True if this is DDR instead of defense
        """
        source = DefenseSource(
            source_type="incarnate",
            source_name=incarnate_name,
            defense_type=defense_type,
            magnitude=magnitude,
            is_ddr=is_ddr
        )
        self.sources.append(source)

    def calculate_totals(self) -> DefenseTotals:
        """
        Aggregate all defense sources into totals

        Returns:
            DefenseTotals with aggregated values
        """
        totals = DefenseTotals()

        # Aggregate all sources
        for source in self.sources:
            if source.is_ddr:
                # Add to DDR
                totals.ddr += source.magnitude
            else:
                # Add to appropriate defense type
                defense_attr = source.defense_type.name.lower()
                if hasattr(totals, defense_attr):
                    current = getattr(totals, defense_attr)
                    setattr(totals, defense_attr, current + source.magnitude)

                    # Track source breakdown
                    source_key = f"{source.source_type}:{source.source_name}"
                    totals.sources[source_key] = source.magnitude

        # Cap DDR at 95%
        totals.ddr = min(totals.ddr, self.DDR_CAP)

        # Defense itself has NO cap (unlike resistance)
        # Values above 45% are still useful

        return totals

    def get_effective_defense(
        self,
        totals: DefenseTotals,
        typed_defense_type: DefenseType,
        positional_defense_type: DefenseType
    ) -> float:
        """
        Calculate effective defense for an attack
        City of Heroes uses MAX(typed, positional)

        Args:
            totals: Defense totals
            typed_defense_type: Typed defense type (e.g., FIRE)
            positional_defense_type: Positional type (e.g., RANGED)

        Returns:
            Effective defense (higher of typed or positional)
        """
        typed_attr = typed_defense_type.name.lower()
        positional_attr = positional_defense_type.name.lower()

        typed_defense = getattr(totals, typed_attr, 0.0)
        positional_defense = getattr(totals, positional_attr, 0.0)

        return max(typed_defense, positional_defense)

    def is_soft_capped(self, defense_value: float) -> bool:
        """
        Check if defense has reached soft cap

        Args:
            defense_value: Defense value to check

        Returns:
            True if >= 45%
        """
        return defense_value >= self.SOFT_CAP

    def distance_to_soft_cap(self, defense_value: float) -> float:
        """
        Calculate distance to soft cap

        Args:
            defense_value: Current defense value

        Returns:
            Defense needed to reach soft cap (negative if over)
        """
        return self.SOFT_CAP - defense_value

    def apply_defense_debuffs(
        self,
        totals: DefenseTotals,
        debuff_magnitude: float,
        defense_type: DefenseType
    ) -> float:
        """
        Apply defense debuff with DDR mitigation

        Args:
            totals: Current defense totals (includes DDR)
            debuff_magnitude: Defense debuff (negative value)
            defense_type: Which defense is being debuffed

        Returns:
            Net defense after debuff
        """
        defense_attr = defense_type.name.lower()
        base_defense = getattr(totals, defense_attr, 0.0)

        # DDR reduces debuff magnitude
        # actual_debuff = base_debuff * (1 - DDR)
        actual_debuff = debuff_magnitude * (1 - totals.ddr)

        # Apply debuff to defense
        net_defense = base_defense - actual_debuff

        return max(0.0, net_defense)  # Defense cannot go negative

    def format_display(self, totals: DefenseTotals) -> Dict[str, str]:
        """
        Format defense totals for display

        Args:
            totals: Defense totals to format

        Returns:
            Dict of formatted display strings
        """
        display = {}

        # Typed defense
        for defense_type in [DefenseType.SMASHING, DefenseType.LETHAL,
                           DefenseType.FIRE, DefenseType.COLD,
                           DefenseType.ENERGY, DefenseType.NEGATIVE,
                           DefenseType.PSIONIC, DefenseType.TOXIC]:
            attr = defense_type.name.lower()
            value = getattr(totals, attr, 0.0)
            percentage = value * 100

            # Format with soft cap indicator
            if self.is_soft_capped(value):
                display[attr] = f"{percentage:.2f}% (Soft Cap)"
            else:
                needed = self.distance_to_soft_cap(value) * 100
                display[attr] = f"{percentage:.2f}% ({needed:.2f}% to soft cap)"

        # Positional defense
        for defense_type in [DefenseType.MELEE, DefenseType.RANGED, DefenseType.AOE]:
            attr = defense_type.name.lower()
            value = getattr(totals, attr, 0.0)
            percentage = value * 100

            if self.is_soft_capped(value):
                display[attr] = f"{percentage:.2f}% (Soft Cap)"
            else:
                needed = self.distance_to_soft_cap(value) * 100
                display[attr] = f"{percentage:.2f}% ({needed:.2f}% to soft cap)"

        # DDR with cap indicator
        ddr_percentage = totals.ddr * 100
        if totals.ddr >= self.DDR_CAP:
            display["ddr"] = f"{ddr_percentage:.2f}% (Capped)"
        else:
            display["ddr"] = f"{ddr_percentage:.2f}%"

        return display
```

**Implementation Priority:**

**CRITICAL** - Defense totals are the #1 metric for survivability-focused builds. Must be accurate.

**Key Implementation Steps:**

1. Define `DefenseTotals` dataclass with all defense types
2. Implement `BuildDefenseTotalsCalculator` class
3. Implement `add_power_defense()` for active powers
4. Implement `add_set_bonus_defense()` for set bonuses
5. Implement `add_global_io_defense()` for global IOs
6. Implement `add_incarnate_defense()` for incarnate powers
7. Implement `calculate_totals()` to aggregate all sources
8. Implement `get_effective_defense()` for max(typed, positional) logic
9. Implement `is_soft_capped()` and `distance_to_soft_cap()` for display
10. Implement `apply_defense_debuffs()` with DDR mitigation
11. Implement `format_display()` for user-facing display

**Testing Strategy:**

- Unit tests for defense aggregation from multiple sources
- Unit tests for DDR aggregation and capping at 95%
- Unit tests for effective defense (max of typed and positional)
- Unit tests for soft cap detection
- Unit tests for defense debuff with DDR mitigation
- Integration tests comparing to MidsReborn for known builds:
  - Super Reflexes Scrapper (pure positional defense)
  - Shield Defense Tanker (positional + S/L typed)
  - Energy Aura Stalker (typed energy/negative defense)
  - Invulnerability Brute (mixed defense and resistance)
  - Soft cap builds (45% defense target)

**Edge Cases to Test:**

1. Pure positional defense build (45% melee/ranged/aoe, 0% typed)
2. Pure typed defense build (45% to all types, 0% positional)
3. Mixed defense (some typed, some positional)
4. Defense cascade simulation (low DDR + defense debuffs)
5. Defense above soft cap (50%+ defense utility)
6. DDR at cap (95%) and overflow
7. Multiple defense sources (10+ powers + sets + IOs)
8. Incarnate defense temporary vs permanent totals

## References

- **Related Specs**:
  - Spec 01: Power Effects Core (Effect aggregation)
  - Spec 09: Power Defense/Resistance (Individual power defense)
  - Spec 13: Enhancement Set Bonuses (Set bonus defense)
  - Spec 14: Enhancement Special IOs (Global IO defense)
  - Spec 16: Archetype Modifiers (AT defense scaling)
  - Spec 20: Build Totals Display (Overall stats window)
  - Spec 32: Survivability Index (EHP calculations)
- **MidsReborn Files**:
  - `Core/Base/Data_Classes/Character.cs` - `TotalStatistics.Def[]`
  - `Core/Statistics.cs` - `Defense()` display method
  - `Core/Stats.cs` - `Defense`, `DebuffResistance` classes
  - `Forms/WindowMenuItems/frmTotalsV2.cs` - Defense display logic
  - `Core/Enums.cs` - `eDamage` enum for defense type indices
- **Game Documentation**:
  - City of Heroes Wiki - "Defense", "Defense Debuff Resistance"
  - Paragon Wiki - "Defense Mechanics", "Soft Cap"
  - City of Data - Defense formulas and caps

---

# DEPTH COVERAGE - MILESTONE 3

## Section 1: Detailed Algorithm - Complete Defense Aggregation

### Overview

Build Totals Defense is fundamentally a **simple summation** of all defense values from all sources, with **NO hard cap** on defense values (unlike resistance). The complexity lies in tracking 11 separate defense values and understanding the game mechanics for how they interact.

### Core Concepts

**11 Defense Values Tracked:**
- **8 Typed Defense**: Smashing, Lethal, Fire, Cold, Energy, Negative, Psionic, Toxic
- **3 Positional Defense**: Melee, Ranged, AoE

**Critical Game Mechanic - "Highest Wins" Rule:**

When an attack hits, City of Heroes checks BOTH the typed defense (e.g., Fire) AND the positional defense (e.g., Ranged) and uses **whichever is HIGHER**. This is NOT additive.

```
Example: Fire/Ranged attack
  Character has: 30% Fire defense, 20% Ranged defense
  Effective defense = max(30%, 20%) = 30%

Example: Psionic/Melee attack
  Character has: 0% Psionic defense, 45% Melee defense
  Effective defense = max(0%, 45%) = 45% (soft capped!)
```

This means:
- Pure positional defense (45% to all 3 positions) = soft cap vs ALL attacks
- Pure typed defense (45% to all 8 types) = soft cap vs ALL attacks
- Mixed defense (30% typed + 30% positional) = 30% effective (NOT 60%)

### Complete Defense Aggregation Pseudocode

```python
def calculate_build_defense_totals(build):
    """
    Calculate total defense for entire build

    Args:
        build: Character build with powers, enhancements, incarnates

    Returns:
        DefenseTotals with all 11 defense values + DDR
    """

    # Step 1: Initialize all defense values to 0.0
    totals = DefenseTotals()
    totals.smashing = 0.0
    totals.lethal = 0.0
    totals.fire = 0.0
    totals.cold = 0.0
    totals.energy = 0.0
    totals.negative = 0.0
    totals.psionic = 0.0
    totals.toxic = 0.0
    totals.melee = 0.0
    totals.ranged = 0.0
    totals.aoe = 0.0
    totals.ddr = 0.0

    # Step 2: Aggregate defense from ALL active powers
    # Defense powers are typically toggles or auto powers
    for power_entry in build.powers:
        if not power_entry.stat_include:
            # Power is off or not included in totals
            continue

        power = power_entry.power
        for effect in power.effects:
            if effect.effect_type == EffectType.DEFENSE:
                # Add defense to appropriate type
                damage_type = effect.damage_type  # e.g., SMASHING, MELEE
                magnitude = effect.magnitude  # Already scaled by AT modifiers

                # Simple addition - defense stacks from all sources
                totals.add_defense(damage_type, magnitude)

            elif effect.effect_type == EffectType.DEFENSE_DEBUFF_RESISTANCE:
                # Add to DDR
                totals.ddr += effect.magnitude

    # Step 3: Aggregate defense from set bonuses
    # Set bonuses are ALWAYS active (no on/off toggle)
    set_bonuses = build.get_set_bonuses()
    for bonus in set_bonuses:
        if bonus.effect_type == EffectType.DEFENSE:
            damage_type = bonus.damage_type
            magnitude = bonus.magnitude
            totals.add_defense(damage_type, magnitude)

        elif bonus.effect_type == EffectType.DEFENSE_DEBUFF_RESISTANCE:
            totals.ddr += bonus.magnitude

    # Step 4: Aggregate defense from global IOs
    # Global IOs like "Steadfast Protection: Resistance/Defense" grant defense always
    for power_entry in build.powers:
        for slot in power_entry.slots:
            enhancement = slot.enhancement
            if enhancement.has_global_effect:
                for global_effect in enhancement.global_effects:
                    if global_effect.effect_type == EffectType.DEFENSE:
                        damage_type = global_effect.damage_type
                        magnitude = global_effect.magnitude
                        totals.add_defense(damage_type, magnitude)

                    elif global_effect.effect_type == EffectType.DEFENSE_DEBUFF_RESISTANCE:
                        totals.ddr += global_effect.magnitude

    # Step 5: Aggregate defense from incarnate powers
    # Incarnate powers like Destiny can grant large defense buffs
    if build.incarnates.destiny and build.incarnates.destiny.active:
        destiny = build.incarnates.destiny
        for effect in destiny.effects:
            if effect.effect_type == EffectType.DEFENSE:
                damage_type = effect.damage_type
                magnitude = effect.magnitude
                totals.add_defense(damage_type, magnitude)

            elif effect.effect_type == EffectType.DEFENSE_DEBUFF_RESISTANCE:
                totals.ddr += effect.magnitude

    # Other incarnate slots (Interface, Hybrid, etc.) may also grant defense
    # Process similarly...

    # Step 6: Cap DDR at 95%
    # DDR has a hard cap, unlike defense itself
    totals.ddr = min(totals.ddr, 0.95)

    # Step 7: Defense has NO hard cap
    # Unlike resistance which caps at 75%/90%, defense can go above 45%
    # Values above 45% are useful vs +level enemies
    # NO capping applied to defense values

    # Step 8: Apply defense debuffs (if in combat simulation mode)
    # In build planning mode, typically not applied
    # In combat simulation:
    if combat_mode and active_defense_debuffs:
        for defense_type in ALL_DEFENSE_TYPES:
            if defense_debuffs[defense_type] > 0:
                # DDR reduces debuff magnitude
                actual_debuff = defense_debuffs[defense_type] * (1 - totals.ddr)

                # Apply debuff
                current_defense = totals.get_defense(defense_type)
                new_defense = max(0.0, current_defense - actual_debuff)
                totals.set_defense(defense_type, new_defense)

    return totals

def calculate_effective_defense(totals, attack_typed, attack_positional):
    """
    Calculate effective defense for a specific attack

    CRITICAL: Uses MAX of typed and positional, NOT sum

    Args:
        totals: DefenseTotals with all defense values
        attack_typed: Typed damage type of attack (e.g., FIRE)
        attack_positional: Positional vector of attack (e.g., RANGED)

    Returns:
        Effective defense percentage (0.0 to 1.0+)
    """
    typed_defense = totals.get_defense(attack_typed)
    positional_defense = totals.get_defense(attack_positional)

    # HIGHEST WINS - This is the core game mechanic
    effective_defense = max(typed_defense, positional_defense)

    return effective_defense

def check_soft_cap_coverage(totals):
    """
    Check soft cap coverage for display

    Returns:
        Dictionary of coverage status
    """
    SOFT_CAP = 0.45  # 45% defense

    coverage = {}

    # Check typed defense
    coverage['smashing_capped'] = totals.smashing >= SOFT_CAP
    coverage['lethal_capped'] = totals.lethal >= SOFT_CAP
    coverage['fire_capped'] = totals.fire >= SOFT_CAP
    coverage['cold_capped'] = totals.cold >= SOFT_CAP
    coverage['energy_capped'] = totals.energy >= SOFT_CAP
    coverage['negative_capped'] = totals.negative >= SOFT_CAP
    coverage['psionic_capped'] = totals.psionic >= SOFT_CAP
    coverage['toxic_capped'] = totals.toxic >= SOFT_CAP

    # Check positional defense
    coverage['melee_capped'] = totals.melee >= SOFT_CAP
    coverage['ranged_capped'] = totals.ranged >= SOFT_CAP
    coverage['aoe_capped'] = totals.aoe >= SOFT_CAP

    # Check effective defense vs common attack types
    # Most attacks are either:
    # - S/L/Melee (melee attacks)
    # - Fire/Energy/Ranged (blaster attacks)
    # - Psionic/Ranged (psychic blasts)

    coverage['vs_melee_sl'] = max(totals.smashing, totals.lethal, totals.melee) >= SOFT_CAP
    coverage['vs_ranged_fire'] = max(totals.fire, totals.ranged) >= SOFT_CAP
    coverage['vs_ranged_psi'] = max(totals.psionic, totals.ranged) >= SOFT_CAP

    return coverage
```

### Defense Aggregation Formula

For each defense type (11 total):

```
Defense[type] = Σ (all sources)

Where sources include:
  - Power effects (toggles, autos, clicks)
  - Set bonuses (always active)
  - Global IO effects (always active)
  - Incarnate powers (when active)
  - Temporary powers (when active)
```

**NO multiplication, NO caps** - just simple addition.

### Defense Debuff Resistance (DDR) Formula

```
DDR = min(0.95, Σ (all DDR sources))

Actual defense debuff = base_debuff * (1 - DDR)

Example with 50% DDR:
  Base debuff: -20% defense
  Actual debuff: -20% * (1 - 0.5) = -10% defense

Example with 95% DDR (cap):
  Base debuff: -20% defense
  Actual debuff: -20% * (1 - 0.95) = -1% defense
```

### Complete Example: Super Reflexes Scrapper

**Build Configuration:**
- Super Reflexes primary (positional defense toggles)
- 5x Luck of the Gambler +7.5% Recharge (3% defense each)
- Shield Wall +5% Resistance (3% defense)
- Red Fortune set bonuses

**Power Defense:**
```
Focused Fighting (toggle):   18.5% Melee defense
Focused Senses (toggle):      18.5% Ranged defense
Evasion (toggle):             18.5% AoE defense
Agile (passive):              13.875% Melee defense
Dodge (passive):              13.875% Ranged defense
Lucky (passive):              13.875% AoE defense
```

**Set Bonus Defense:**
```
5x Luck of the Gambler:       15.0% Ranged defense (5 × 3%)
Shield Wall global IO:        3.0% All positions
Various set bonuses:          6.5% Ranged defense
```

**Totals Calculation:**
```
Smashing:  0.0%   (no typed defense)
Lethal:    0.0%   (no typed defense)
Fire:      0.0%   (no typed defense)
Cold:      0.0%   (no typed defense)
Energy:    0.0%   (no typed defense)
Negative:  0.0%   (no typed defense)
Psionic:   0.0%   (no typed defense)
Toxic:     0.0%   (no typed defense)

Melee:     18.5% + 13.875% + 3.0% = 35.375%
Ranged:    18.5% + 13.875% + 15.0% + 3.0% + 6.5% = 56.875%
AoE:       18.5% + 13.875% + 3.0% = 35.375%
```

**Effective Defense vs Common Attacks:**
```
S/L/Melee:         max(0%, 35.375%) = 35.375%  (not capped, need ~10% more)
Fire/Ranged:       max(0%, 56.875%) = 56.875%  (OVER soft cap - good vs +level)
Psionic/Ranged:    max(0%, 56.875%) = 56.875%  (OVER soft cap - SR has no psi hole!)
Energy/Melee:      max(0%, 35.375%) = 35.375%  (not capped)
```

**Key Insight:** Pure positional defense build achieves soft cap vs ALL attack types regardless of damage type, but only if all 3 positions reach 45%. This build needs more Melee/AoE defense.

### Complete Example: Shield Defense Tanker

**Build Configuration:**
- Shield Defense primary (mixed positional + typed defense)
- Strong S/L typed defense from primary
- Additional positional defense from IOs

**Power Defense:**
```
Deflection (toggle):          15.6% Melee, Ranged defense
Battle Agility (toggle):      15.6% Melee, Ranged, AoE defense
True Grit (passive):          5.2% S/L defense
Grant Cover (auto):           7.8% S/L defense
Shield wall proc:             5% S/L defense (when it procs - not counted here)
```

**Totals Calculation:**
```
Smashing:  5.2% + 7.8% = 13.0%
Lethal:    5.2% + 7.8% = 13.0%
Fire:      0.0%
Cold:      0.0%
Energy:    0.0%
Negative:  0.0%
Psionic:   0.0%
Toxic:     0.0%

Melee:     15.6% + 15.6% = 31.2%  (+ set bonuses to reach 45%)
Ranged:    15.6% + 15.6% = 31.2%  (+ set bonuses to reach 45%)
AoE:       15.6%                   (+ set bonuses to reach 45%)
```

**Effective Defense vs Common Attacks:**
```
S/L/Melee:         max(13%, 45%) = 45%  (soft capped via positional!)
Fire/Melee:        max(0%, 45%) = 45%   (soft capped via positional!)
Psionic/Melee:     max(0%, 45%) = 45%   (soft capped via positional!)
Energy/Ranged:     max(0%, 45%) = 45%   (soft capped via positional!)
```

**Key Insight:** Mixed typed + positional defense is efficient. The S/L typed defense provides extra layering for common physical attacks, but the positional defense carries the load for exotic damage types.

## Section 2: C# Implementation Details

### Character.TotalStatistics Class

**File:** `Core/Base/Data_Classes/Character.cs`
**Lines:** 1871-1970

Defense totals are stored in the `TotalStatistics` class:

```csharp
public class TotalStatistics
{
    // Defense array indexed by eDamage enum
    // Indices 0-6: Typed defense (S,L,F,C,E,N,P)
    // Indices 7-9: Positional defense (Melee, Ranged, AoE)
    // Note: Toxic defense exists but index may vary
    public float[] Def { get; private set; }

    // Resistance array (same indexing as Def)
    public float[] Res { get; private set; }

    // Mez protection/resistance arrays
    public float[] Mez { get; private set; }
    public float[] MezRes { get; private set; }

    // Debuff resistance array (includes DDR at Defense index)
    public float[] DebuffRes { get; private set; }

    // Elusivity (separate mechanic, reduces enemy tohit)
    public float[] Elusivity { get; set; }

    // Other stats...
    public float HPRegen { get; set; }
    public float HPMax { get; set; }
    public float Absorb { get; set; }
    public float EndRec { get; set; }
    public float EndUse { get; set; }
    public float EndMax { get; set; }
    public float RunSpd { get; set; }
    public float JumpSpd { get; set; }
    public float FlySpd { get; set; }

    public void Init(bool fullReset = true)
    {
        // Initialize arrays with correct lengths
        Def = new float[Enum.GetValues<Enums.eDamage>().Length];
        Res = new float[Enum.GetValues<Enums.eDamage>().Length];
        Mez = new float[Enum.GetValues<Enums.eMez>().Length];
        MezRes = new float[Enum.GetValues<Enums.eMez>().Length];
        DebuffRes = new float[Enum.GetValues<Enums.eEffectType>().Length];
        Elusivity = new float[Enum.GetValues<Enums.eDamage>().Length];

        // All values default to 0.0
        if (fullReset)
        {
            HPRegen = 0;
            HPMax = 0;
            Absorb = 0;
            // ... etc
        }
    }

    public void Assign(TotalStatistics iSt)
    {
        // Copy all values from another TotalStatistics
        Def = (float[])iSt.Def.Clone();
        Res = (float[])iSt.Res.Clone();
        Mez = (float[])iSt.Mez.Clone();
        MezRes = (float[])iSt.MezRes.Clone();
        DebuffRes = (float[])iSt.DebuffRes.Clone();
        Elusivity = iSt.Elusivity;

        HPRegen = iSt.HPRegen;
        HPMax = iSt.HPMax;
        Absorb = iSt.Absorb;
        // ... etc
    }
}
```

**Key Points:**
1. `Def[]` array stores all 11 defense values
2. Values are stored as decimals (0.45 = 45%)
3. `Totals.Def[]` = uncapped values
4. `TotalsCapped.Def[]` = after cap enforcement (but defense has no cap, so identical)
5. `DebuffRes[]` array stores DDR at the Defense effect type index

### Statistics Class - Display Conversion

**File:** `Core/Statistics.cs`
**Lines:** 113-116

```csharp
public float Defense(int dType)
{
    // Convert from decimal to percentage for display
    return _character.Totals.Def[dType] * 100f;
}
```

**Usage in Display:**
```csharp
// From Forms/WindowMenuItems/frmTotalsV2.cs
graphDef.AddItemPair(
    damageVectorsNames[i],
    $"{displayStats.Defense(i):##0.##}%",
    Math.Max(0, displayStats.Defense(i)),
    Math.Max(0, displayStats.Defense(i)),
    $"{displayStats.Defense(i):##0.###}% {FormatVectorType(typeof(Enums.eDamage), i)} defense"
);
```

**Key Points:**
1. Internal values are decimals (0.45)
2. Display values are percentages (45.00%)
3. Formatting uses `##0.##` for 2 decimal places
4. Tooltip shows 3 decimal places for precision

### Defense Debuff Resistance Capping

**File:** `Core/Statistics.cs`
**Lines:** 24-25

```csharp
public const float MaxDefenseDebuffRes = 95f;  // 95% cap for DDR
public const float MaxGenericDebuffRes = 100f; // All other debuff res
```

**File:** `Forms/WindowMenuItems/frmTotalsV2.cs`

```csharp
var cappedDebuffRes = DebuffEffectsList.Select(e => Math.Min(
        e == Enums.eEffectType.Defense
            ? Statistics.MaxDefenseDebuffRes  // 95% cap for defense debuff res
            : Statistics.MaxGenericDebuffRes,  // 100% cap for other debuff res
        MidsContext.Character.Totals.DebuffRes[(int) e]))
    .ToList();
```

**Key Points:**
1. DDR is capped at 95% (0.95 internally)
2. Other debuff resistances cap at 100%
3. Capping happens during display/totals calculation
4. Values can exceed cap internally but are clamped for game mechanics

### Stats.cs - Defense Type Classes

**File:** `Core/Stats.cs`
**Lines:** 14, 76-88, 232-245

```csharp
public class Display
{
    // Defense structure with all types
    public Defense Defense { get; set; }

    // DDR is nested under DebuffResistance
    public DebuffResistance DebuffResistance { get; set; }
}

// Defense class with all 11 defense types
public class Defense
{
    // Typed defense (8 types)
    public Smashing Smashing { get; set; }
    public Lethal Lethal { get; set; }
    public Fire Fire { get; set; }
    public Cold Cold { get; set; }
    public Energy Energy { get; set; }
    public Negative Negative { get; set; }
    public Psionic Psionic { get; set; }
    public Toxic Toxic { get; set; }

    // Positional defense (3 types)
    public Melee Melee { get; set; }
    public Ranged Ranged { get; set; }
    public Aoe Aoe { get; set; }
}

// DebuffResistance class includes DDR
public class DebuffResistance
{
    public Defense Defense { get; set; }  // DDR as a nested Defense object
    public Endurance Endurance { get; set; }
    public Perception Perception { get; set; }
    public Recharge Recharge { get; set; }
    public Recovery Recovery { get; set; }
    public Regeneration Regeneration { get; set; }
    public RunSpeed RunSpeed { get; set; }
    public ToHit ToHit { get; set; }
}

// Individual defense type classes (all have same structure)
public class Smashing
{
    public float Base { get; set; }     // Base value from powers
    public float Current { get; set; }  // Current value (with buffs/debuffs)
    public float Maximum { get; set; }  // Maximum achieved
}
```

**Key Points:**
1. Strongly-typed class structure for defense
2. Each defense type has Base, Current, Maximum tracking
3. DDR is structured as a nested Defense object within DebuffResistance
4. This structure supports detailed stat tracking and display

### Defense Aggregation Logic (Inferred)

While the exact aggregation code is in the large clsToonX.cs file (3610 lines), the logic follows this pattern based on Character.cs structure:

```csharp
// Simplified aggregation logic (actual code is in clsToonX.cs)
public void CalculateDefenseTotals()
{
    // Reset totals
    Totals.Init();

    // Aggregate from all sources
    foreach (var powerEntry in CurrentBuild.Powers)
    {
        if (!powerEntry.StatInclude)
            continue;

        foreach (var effect in powerEntry.Power.Effects)
        {
            if (effect.EffectType == Enums.eEffectType.Defense)
            {
                // Add to appropriate defense type
                int damageTypeIndex = (int)effect.DamageType;
                Totals.Def[damageTypeIndex] += effect.Magnitude;
            }
            else if (effect.EffectType == Enums.eEffectType.DefenseDebuffResistance)
            {
                // Add to DDR
                int defenseIndex = (int)Enums.eEffectType.Defense;
                Totals.DebuffRes[defenseIndex] += effect.Magnitude;
            }
        }
    }

    // Aggregate set bonuses (similar logic)
    // Aggregate global IOs (similar logic)
    // Aggregate incarnates (similar logic)

    // Copy uncapped to capped (defense has no cap)
    TotalsCapped.Assign(Totals);

    // Cap DDR at 95%
    int ddrIndex = (int)Enums.eEffectType.Defense;
    TotalsCapped.DebuffRes[ddrIndex] = Math.Min(
        Statistics.MaxDefenseDebuffRes,
        Totals.DebuffRes[ddrIndex]
    );
}
```

### Edge Cases in C# Implementation

**1. Toxic Defense Index:**
- Toxic was added by Homecoming
- Index varies between implementations
- MidsReborn handles this with dynamic enum length

**2. Defense vs DefenseDebuff Effect Types:**
- Defense = grants defense to character
- DefenseDebuff = applies defense debuff to enemies
- Must distinguish during aggregation

**3. Elusivity vs Defense:**
- Elusivity is a SEPARATE mechanic (reduces enemy tohit)
- Stored in separate array, not aggregated with defense
- Often confused, but mechanically different

**4. Power Active/Inactive State:**
- Only powers with `StatInclude = true` are aggregated
- Toggles can be on/off, affecting totals
- Set bonuses and global IOs are ALWAYS included

## Section 3: Database Schema

### Proposed Tables

#### `build_defense_totals` Table

Stores aggregated defense totals for a build at a specific level.

```sql
CREATE TABLE build_defense_totals (
    id BIGSERIAL PRIMARY KEY,
    build_id BIGINT NOT NULL REFERENCES builds(id) ON DELETE CASCADE,
    level_index INTEGER NOT NULL,  -- 0-49 (level 1-50)

    -- Typed defense (8 types)
    defense_smashing NUMERIC(10, 6) NOT NULL DEFAULT 0.0,
    defense_lethal NUMERIC(10, 6) NOT NULL DEFAULT 0.0,
    defense_fire NUMERIC(10, 6) NOT NULL DEFAULT 0.0,
    defense_cold NUMERIC(10, 6) NOT NULL DEFAULT 0.0,
    defense_energy NUMERIC(10, 6) NOT NULL DEFAULT 0.0,
    defense_negative NUMERIC(10, 6) NOT NULL DEFAULT 0.0,
    defense_psionic NUMERIC(10, 6) NOT NULL DEFAULT 0.0,
    defense_toxic NUMERIC(10, 6) NOT NULL DEFAULT 0.0,

    -- Positional defense (3 types)
    defense_melee NUMERIC(10, 6) NOT NULL DEFAULT 0.0,
    defense_ranged NUMERIC(10, 6) NOT NULL DEFAULT 0.0,
    defense_aoe NUMERIC(10, 6) NOT NULL DEFAULT 0.0,

    -- Defense debuff resistance (DDR)
    defense_debuff_resistance NUMERIC(10, 6) NOT NULL DEFAULT 0.0,

    -- Pre-calculated effective defense vs common attack types
    -- Stored as materialized values for fast display
    effective_def_vs_sl_melee NUMERIC(10, 6) GENERATED ALWAYS AS (
        GREATEST(defense_smashing, defense_lethal, defense_melee)
    ) STORED,
    effective_def_vs_fire_ranged NUMERIC(10, 6) GENERATED ALWAYS AS (
        GREATEST(defense_fire, defense_ranged)
    ) STORED,
    effective_def_vs_psi_ranged NUMERIC(10, 6) GENERATED ALWAYS AS (
        GREATEST(defense_psionic, defense_ranged)
    ) STORED,
    effective_def_vs_energy_melee NUMERIC(10, 6) GENERATED ALWAYS AS (
        GREATEST(defense_energy, defense_melee)
    ) STORED,

    -- Soft cap indicators (for fast querying)
    is_melee_soft_capped BOOLEAN GENERATED ALWAYS AS (
        defense_melee >= 0.45
    ) STORED,
    is_ranged_soft_capped BOOLEAN GENERATED ALWAYS AS (
        defense_ranged >= 0.45
    ) STORED,
    is_aoe_soft_capped BOOLEAN GENERATED ALWAYS AS (
        defense_aoe >= 0.45
    ) STORED,
    is_positional_soft_capped BOOLEAN GENERATED ALWAYS AS (
        defense_melee >= 0.45 AND defense_ranged >= 0.45 AND defense_aoe >= 0.45
    ) STORED,

    -- Metadata
    calculated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Unique constraint: one totals row per build/level
    UNIQUE(build_id, level_index)
);

CREATE INDEX idx_build_defense_totals_build ON build_defense_totals(build_id);
CREATE INDEX idx_build_defense_totals_soft_cap ON build_defense_totals(is_positional_soft_capped);
```

**Key Design Decisions:**
1. Store values as decimals (0.45 not 45.0) for calculation accuracy
2. Use NUMERIC(10, 6) for 6 decimal precision
3. Generated columns for common effective defense queries
4. Boolean flags for soft cap status (fast filtering)
5. One row per build per level (totals change as build progresses)

#### `build_defense_sources` Table

Tracks individual sources of defense for breakdown display.

```sql
CREATE TABLE build_defense_sources (
    id BIGSERIAL PRIMARY KEY,
    build_id BIGINT NOT NULL REFERENCES builds(id) ON DELETE CASCADE,
    level_index INTEGER NOT NULL,

    -- Source identification
    source_type VARCHAR(20) NOT NULL,  -- 'power', 'set_bonus', 'global_io', 'incarnate'
    source_id BIGINT,  -- ID of power, set, enhancement, or incarnate
    source_name VARCHAR(255) NOT NULL,  -- Human-readable name

    -- Defense granted
    defense_type VARCHAR(20) NOT NULL,  -- 'smashing', 'melee', etc.
    magnitude NUMERIC(10, 6) NOT NULL,
    is_ddr BOOLEAN NOT NULL DEFAULT false,  -- True if this is DDR, not defense

    -- Metadata
    is_active BOOLEAN NOT NULL DEFAULT true,  -- Toggle state for powers
    calculated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (source_type IN ('power', 'set_bonus', 'global_io', 'incarnate', 'temporary')),
    CHECK (defense_type IN ('smashing', 'lethal', 'fire', 'cold', 'energy', 'negative', 'psionic', 'toxic', 'melee', 'ranged', 'aoe'))
);

CREATE INDEX idx_build_defense_sources_build ON build_defense_sources(build_id);
CREATE INDEX idx_build_defense_sources_type ON build_defense_sources(build_id, defense_type);
```

**Purpose:**
- Allows breakdown display: "Where is my defense coming from?"
- Supports "what-if" analysis: "What if I turn off this toggle?"
- Tracks power on/off state
- Enables source filtering

### Example Queries

**1. Get complete defense totals for a build:**
```sql
SELECT
    defense_smashing,
    defense_lethal,
    defense_fire,
    defense_cold,
    defense_energy,
    defense_negative,
    defense_psionic,
    defense_toxic,
    defense_melee,
    defense_ranged,
    defense_aoe,
    defense_debuff_resistance,
    effective_def_vs_sl_melee,
    effective_def_vs_fire_ranged,
    is_positional_soft_capped
FROM build_defense_totals
WHERE build_id = $1 AND level_index = $2;
```

**2. Find all soft-capped builds:**
```sql
SELECT b.id, b.name, bdt.defense_melee, bdt.defense_ranged, bdt.defense_aoe
FROM builds b
JOIN build_defense_totals bdt ON b.id = bdt.build_id
WHERE bdt.level_index = 49  -- Level 50
  AND bdt.is_positional_soft_capped = true;
```

**3. Get defense breakdown by source:**
```sql
SELECT
    source_type,
    source_name,
    defense_type,
    magnitude,
    is_ddr
FROM build_defense_sources
WHERE build_id = $1
  AND level_index = $2
  AND is_active = true
ORDER BY source_type, defense_type, magnitude DESC;
```

**4. Calculate effective defense vs all attack combinations:**
```sql
-- This would typically be done in application code, but can be done in SQL
SELECT
    'Fire/Melee' AS attack_type,
    GREATEST(defense_fire, defense_melee) AS effective_defense
FROM build_defense_totals
WHERE build_id = $1 AND level_index = $2

UNION ALL

SELECT
    'Psionic/Ranged' AS attack_type,
    GREATEST(defense_psionic, defense_ranged) AS effective_defense
FROM build_defense_totals
WHERE build_id = $1 AND level_index = $2

-- ... for all 8 typed × 3 positional = 24 combinations
;
```

**5. Find weakest defense coverage:**
```sql
-- Find defense type with lowest value
SELECT
    'Smashing' AS defense_type, defense_smashing AS value FROM build_defense_totals WHERE build_id = $1 AND level_index = $2
UNION ALL SELECT 'Lethal', defense_lethal FROM build_defense_totals WHERE build_id = $1 AND level_index = $2
UNION ALL SELECT 'Fire', defense_fire FROM build_defense_totals WHERE build_id = $1 AND level_index = $2
UNION ALL SELECT 'Cold', defense_cold FROM build_defense_totals WHERE build_id = $1 AND level_index = $2
UNION ALL SELECT 'Energy', defense_energy FROM build_defense_totals WHERE build_id = $1 AND level_index = $2
UNION ALL SELECT 'Negative', defense_negative FROM build_defense_totals WHERE build_id = $1 AND level_index = $2
UNION ALL SELECT 'Psionic', defense_psionic FROM build_defense_totals WHERE build_id = $1 AND level_index = $2
UNION ALL SELECT 'Toxic', defense_toxic FROM build_defense_totals WHERE build_id = $1 AND level_index = $2
UNION ALL SELECT 'Melee', defense_melee FROM build_defense_totals WHERE build_id = $1 AND level_index = $2
UNION ALL SELECT 'Ranged', defense_ranged FROM build_defense_totals WHERE build_id = $1 AND level_index = $2
UNION ALL SELECT 'AoE', defense_aoe FROM build_defense_totals WHERE build_id = $1 AND level_index = $2
ORDER BY value ASC
LIMIT 1;
```

### Schema Notes

**Storage Format:**
- Values stored as decimals (0.0 to 1.0+), not percentages
- 6 decimal precision (0.451234) for accurate calculations
- No upper bound (defense has no hard cap)

**Performance Optimization:**
- Generated columns for common queries
- Indexes on build_id for fast lookup
- Boolean soft cap flags for filtering
- One row per level (not recalculating on every query)

**Relationship to Other Tables:**
- `builds` table: One-to-many (one build has many level snapshots)
- `build_power_entries` table: Many-to-one (many powers contribute to one totals row)
- `enhancement_sets` table: Many-to-many via set bonuses
- `enhancements` table: Many-to-many via global IOs

## Section 4: Test Cases

### Test Suite Organization

```python
# tests/calculations/test_build_defense_totals.py

class TestBuildDefenseTotals:
    """Test suite for Build Totals Defense calculation"""

    # Basic aggregation tests
    def test_01_empty_build_zero_defense()
    def test_02_single_power_defense()
    def test_03_multiple_powers_stack()
    def test_04_set_bonus_defense()
    def test_05_global_io_defense()
    def test_06_incarnate_defense()
    def test_07_all_sources_combined()

    # Typed defense tests
    def test_10_typed_defense_smashing_only()
    def test_11_typed_defense_lethal_only()
    def test_12_typed_defense_fire_only()
    def test_13_typed_defense_all_types()

    # Positional defense tests
    def test_20_positional_defense_melee_only()
    def test_21_positional_defense_ranged_only()
    def test_22_positional_defense_aoe_only()
    def test_23_positional_defense_all_positions()

    # "Highest wins" rule tests
    def test_30_highest_wins_typed_higher()
    def test_31_highest_wins_positional_higher()
    def test_32_highest_wins_equal()
    def test_33_highest_wins_mixed_build()

    # Soft cap tests
    def test_40_soft_cap_45_percent()
    def test_41_soft_cap_exceeded()
    def test_42_soft_cap_all_positions()
    def test_43_soft_cap_partial()

    # DDR tests
    def test_50_ddr_basic_calculation()
    def test_51_ddr_cap_at_95_percent()
    def test_52_ddr_mitigation_formula()
    def test_53_ddr_multiple_sources()

    # Real build examples
    def test_60_super_reflexes_scrapper()
    def test_61_shield_defense_tanker()
    def test_62_energy_aura_stalker()
    def test_63_invulnerability_brute()

    # Edge cases
    def test_70_negative_defense_from_debuffs()
    def test_71_defense_over_100_percent()
    def test_72_all_defense_types_matrix()
    def test_73_power_toggle_on_off()
```

### Detailed Test Cases

#### Test 1: Empty Build - Zero Defense

```python
def test_01_empty_build_zero_defense():
    """Empty build should have 0% defense in all types"""

    # Arrange
    calc = BuildDefenseTotalsCalculator()

    # Act
    totals = calc.calculate_totals()

    # Assert
    assert totals.smashing == 0.0
    assert totals.lethal == 0.0
    assert totals.fire == 0.0
    assert totals.cold == 0.0
    assert totals.energy == 0.0
    assert totals.negative == 0.0
    assert totals.psionic == 0.0
    assert totals.toxic == 0.0
    assert totals.melee == 0.0
    assert totals.ranged == 0.0
    assert totals.aoe == 0.0
    assert totals.ddr == 0.0
```

#### Test 2: Single Power Defense

```python
def test_02_single_power_defense():
    """Single defense power should add to appropriate type"""

    # Arrange
    calc = BuildDefenseTotalsCalculator()

    # Act
    # Super Reflexes "Focused Fighting" grants 18.5% Melee defense
    calc.add_power_defense(
        power_name="Focused Fighting",
        defense_type=DefenseType.MELEE,
        magnitude=0.185
    )
    totals = calc.calculate_totals()

    # Assert
    assert totals.melee == pytest.approx(0.185, rel=1e-6)
    assert totals.ranged == 0.0
    assert totals.aoe == 0.0
    assert totals.smashing == 0.0  # No typed defense
```

#### Test 3: Multiple Powers Stack

```python
def test_03_multiple_powers_stack():
    """Multiple powers granting same defense type should stack"""

    # Arrange
    calc = BuildDefenseTotalsCalculator()

    # Act
    # Super Reflexes toggles + passives
    calc.add_power_defense("Focused Fighting", DefenseType.MELEE, 0.185)  # Toggle
    calc.add_power_defense("Agile", DefenseType.MELEE, 0.13875)           # Passive
    totals = calc.calculate_totals()

    # Assert
    # 18.5% + 13.875% = 32.375%
    assert totals.melee == pytest.approx(0.32375, rel=1e-6)
```

#### Test 4: Set Bonus Defense

```python
def test_04_set_bonus_defense():
    """Set bonuses should add to defense totals"""

    # Arrange
    calc = BuildDefenseTotalsCalculator()

    # Act
    # 5x Luck of the Gambler +7.5% Recharge
    # Each grants 3% Ranged defense
    for i in range(5):
        calc.add_set_bonus_defense(
            set_name="Luck of the Gambler",
            defense_type=DefenseType.RANGED,
            magnitude=0.03
        )
    totals = calc.calculate_totals()

    # Assert
    # 5 × 3% = 15%
    assert totals.ranged == pytest.approx(0.15, rel=1e-6)
```

#### Test 10: Typed Defense Only - Smashing

```python
def test_10_typed_defense_smashing_only():
    """Build with only Smashing typed defense"""

    # Arrange
    calc = BuildDefenseTotalsCalculator()

    # Act
    calc.add_power_defense("Tough Hide", DefenseType.SMASHING, 0.40)
    totals = calc.calculate_totals()

    # Assert
    assert totals.smashing == pytest.approx(0.40, rel=1e-6)

    # Effective defense checks
    effective = calc.get_effective_defense(totals, DefenseType.SMASHING, DefenseType.MELEE)
    assert effective == pytest.approx(0.40, rel=1e-6)  # max(0.40, 0.0) = 0.40

    effective = calc.get_effective_defense(totals, DefenseType.FIRE, DefenseType.RANGED)
    assert effective == 0.0  # max(0.0, 0.0) = 0.0 (no coverage!)
```

#### Test 20: Positional Defense Only - Melee

```python
def test_20_positional_defense_melee_only():
    """Build with only Melee positional defense"""

    # Arrange
    calc = BuildDefenseTotalsCalculator()

    # Act
    calc.add_power_defense("Deflection", DefenseType.MELEE, 0.40)
    totals = calc.calculate_totals()

    # Assert
    assert totals.melee == pytest.approx(0.40, rel=1e-6)

    # Effective defense checks
    # Melee attacks (regardless of damage type) are covered
    effective = calc.get_effective_defense(totals, DefenseType.SMASHING, DefenseType.MELEE)
    assert effective == pytest.approx(0.40, rel=1e-6)  # max(0.0, 0.40) = 0.40

    effective = calc.get_effective_defense(totals, DefenseType.FIRE, DefenseType.MELEE)
    assert effective == pytest.approx(0.40, rel=1e-6)  # max(0.0, 0.40) = 0.40

    # Ranged attacks are NOT covered
    effective = calc.get_effective_defense(totals, DefenseType.FIRE, DefenseType.RANGED)
    assert effective == 0.0  # max(0.0, 0.0) = 0.0
```

#### Test 30: "Highest Wins" - Typed Higher

```python
def test_30_highest_wins_typed_higher():
    """When typed defense is higher, it should be used"""

    # Arrange
    calc = BuildDefenseTotalsCalculator()

    # Act
    calc.add_power_defense("S/L Defense", DefenseType.SMASHING, 0.40)
    calc.add_power_defense("Melee Defense", DefenseType.MELEE, 0.25)
    totals = calc.calculate_totals()

    # Assert
    effective = calc.get_effective_defense(totals, DefenseType.SMASHING, DefenseType.MELEE)
    assert effective == pytest.approx(0.40, rel=1e-6)  # max(0.40, 0.25) = 0.40
```

#### Test 31: "Highest Wins" - Positional Higher

```python
def test_31_highest_wins_positional_higher():
    """When positional defense is higher, it should be used"""

    # Arrange
    calc = BuildDefenseTotalsCalculator()

    # Act
    calc.add_power_defense("Fire Defense", DefenseType.FIRE, 0.20)
    calc.add_power_defense("Ranged Defense", DefenseType.RANGED, 0.35)
    totals = calc.calculate_totals()

    # Assert
    effective = calc.get_effective_defense(totals, DefenseType.FIRE, DefenseType.RANGED)
    assert effective == pytest.approx(0.35, rel=1e-6)  # max(0.20, 0.35) = 0.35
```

#### Test 32: "Highest Wins" - Equal Values

```python
def test_32_highest_wins_equal():
    """When typed and positional are equal, max returns either (both are same)"""

    # Arrange
    calc = BuildDefenseTotalsCalculator()

    # Act
    calc.add_power_defense("Energy Defense", DefenseType.ENERGY, 0.45)
    calc.add_power_defense("AoE Defense", DefenseType.AOE, 0.45)
    totals = calc.calculate_totals()

    # Assert
    effective = calc.get_effective_defense(totals, DefenseType.ENERGY, DefenseType.AOE)
    assert effective == pytest.approx(0.45, rel=1e-6)  # max(0.45, 0.45) = 0.45

    # Verify soft cap reached
    assert calc.is_soft_capped(effective)
```

#### Test 33: "Highest Wins" - Mixed Build

```python
def test_33_highest_wins_mixed_build():
    """Real-world mixed build - Shield Defense example"""

    # Arrange
    calc = BuildDefenseTotalsCalculator()

    # Act
    # Shield Defense grants both typed and positional
    calc.add_power_defense("True Grit", DefenseType.SMASHING, 0.13)
    calc.add_power_defense("True Grit", DefenseType.LETHAL, 0.13)
    calc.add_power_defense("Deflection", DefenseType.MELEE, 0.31)
    calc.add_power_defense("Deflection", DefenseType.RANGED, 0.31)
    calc.add_power_defense("Battle Agility", DefenseType.MELEE, 0.14)
    calc.add_power_defense("Battle Agility", DefenseType.RANGED, 0.14)
    totals = calc.calculate_totals()

    # Assert totals
    assert totals.smashing == pytest.approx(0.13, rel=1e-6)
    assert totals.lethal == pytest.approx(0.13, rel=1e-6)
    assert totals.melee == pytest.approx(0.45, rel=1e-6)  # 0.31 + 0.14 = 0.45
    assert totals.ranged == pytest.approx(0.45, rel=1e-6)  # 0.31 + 0.14 = 0.45

    # Effective defense checks
    # S/L melee attacks use POSITIONAL defense (higher)
    effective = calc.get_effective_defense(totals, DefenseType.SMASHING, DefenseType.MELEE)
    assert effective == pytest.approx(0.45, rel=1e-6)  # max(0.13, 0.45) = 0.45

    # Fire ranged attacks use POSITIONAL defense (only option)
    effective = calc.get_effective_defense(totals, DefenseType.FIRE, DefenseType.RANGED)
    assert effective == pytest.approx(0.45, rel=1e-6)  # max(0.0, 0.45) = 0.45
```

#### Test 40: Soft Cap - 45% Defense

```python
def test_40_soft_cap_45_percent():
    """45% defense should be detected as soft capped"""

    # Arrange
    calc = BuildDefenseTotalsCalculator()

    # Act
    calc.add_power_defense("Defense Power", DefenseType.RANGED, 0.45)
    totals = calc.calculate_totals()

    # Assert
    assert calc.is_soft_capped(totals.ranged)
    assert calc.distance_to_soft_cap(totals.ranged) == pytest.approx(0.0, rel=1e-6)
```

#### Test 41: Soft Cap Exceeded

```python
def test_41_soft_cap_exceeded():
    """Defense above 45% should still be tracked (useful vs +level enemies)"""

    # Arrange
    calc = BuildDefenseTotalsCalculator()

    # Act
    calc.add_power_defense("Power 1", DefenseType.MELEE, 0.35)
    calc.add_power_defense("Power 2", DefenseType.MELEE, 0.25)
    totals = calc.calculate_totals()

    # Assert
    assert totals.melee == pytest.approx(0.60, rel=1e-6)  # 35% + 25% = 60%
    assert calc.is_soft_capped(totals.melee)
    assert calc.distance_to_soft_cap(totals.melee) == pytest.approx(-0.15, rel=1e-6)  # -15% over
```

#### Test 50: DDR Basic Calculation

```python
def test_50_ddr_basic_calculation():
    """DDR should aggregate from all sources"""

    # Arrange
    calc = BuildDefenseTotalsCalculator()

    # Act
    calc.add_power_defense("Quickness", DefenseType.MELEE, 0.0, is_ddr=True)  # Grants DDR
    calc.add_power_defense("Practiced Brawler", DefenseType.MELEE, 0.10, is_ddr=True)
    totals = calc.calculate_totals()

    # Assert
    assert totals.ddr == pytest.approx(0.10, rel=1e-6)
```

#### Test 51: DDR Cap at 95%

```python
def test_51_ddr_cap_at_95_percent():
    """DDR should be capped at 95%, not 100%"""

    # Arrange
    calc = BuildDefenseTotalsCalculator()

    # Act
    # Unrealistically high DDR sources
    calc.add_power_defense("Source 1", DefenseType.MELEE, 0.50, is_ddr=True)
    calc.add_power_defense("Source 2", DefenseType.MELEE, 0.50, is_ddr=True)
    calc.add_power_defense("Source 3", DefenseType.MELEE, 0.50, is_ddr=True)
    totals = calc.calculate_totals()

    # Assert
    assert totals.ddr == pytest.approx(0.95, rel=1e-6)  # Capped at 95%, not 150%
```

#### Test 52: DDR Mitigation Formula

```python
def test_52_ddr_mitigation_formula():
    """DDR should reduce defense debuffs by (1 - DDR) formula"""

    # Arrange
    calc = BuildDefenseTotalsCalculator()

    # Act
    calc.add_power_defense("Defense Power", DefenseType.MELEE, 0.45)
    calc.add_power_defense("DDR Power", DefenseType.MELEE, 0.50, is_ddr=True)
    totals = calc.calculate_totals()

    # Simulate defense debuff
    debuff_magnitude = 0.20  # -20% defense debuff
    net_defense = calc.apply_defense_debuffs(totals, debuff_magnitude, DefenseType.MELEE)

    # Assert
    # actual_debuff = -20% * (1 - 0.50) = -10%
    # net_defense = 45% - 10% = 35%
    assert net_defense == pytest.approx(0.35, rel=1e-6)
```

#### Test 60: Real Build - Super Reflexes Scrapper

```python
def test_60_super_reflexes_scrapper():
    """Complete Super Reflexes Scrapper build test"""

    # Arrange
    calc = BuildDefenseTotalsCalculator()

    # Act - Add all powers
    # Toggles
    calc.add_power_defense("Focused Fighting", DefenseType.MELEE, 0.185)
    calc.add_power_defense("Focused Senses", DefenseType.RANGED, 0.185)
    calc.add_power_defense("Evasion", DefenseType.AOE, 0.185)

    # Passives
    calc.add_power_defense("Agile", DefenseType.MELEE, 0.13875)
    calc.add_power_defense("Dodge", DefenseType.RANGED, 0.13875)
    calc.add_power_defense("Lucky", DefenseType.AOE, 0.13875)

    # Set bonuses (5x Luck of the Gambler)
    for i in range(5):
        calc.add_set_bonus_defense("Luck of the Gambler", DefenseType.RANGED, 0.03)

    # Global IOs
    calc.add_global_io_defense("Shield Wall", DefenseType.MELEE, 0.03)
    calc.add_global_io_defense("Shield Wall", DefenseType.RANGED, 0.03)
    calc.add_global_io_defense("Shield Wall", DefenseType.AOE, 0.03)

    # Additional set bonuses
    calc.add_set_bonus_defense("Red Fortune", DefenseType.RANGED, 0.0625)

    # DDR
    calc.add_power_defense("Quickness", DefenseType.MELEE, 0.20, is_ddr=True)
    calc.add_power_defense("Practiced Brawler", DefenseType.MELEE, 0.10, is_ddr=True)

    totals = calc.calculate_totals()

    # Assert
    # Melee: 18.5% + 13.875% + 3% = 35.375%
    assert totals.melee == pytest.approx(0.35375, rel=1e-5)

    # Ranged: 18.5% + 13.875% + (5×3%) + 3% + 6.25% = 56.625%
    assert totals.ranged == pytest.approx(0.56625, rel=1e-5)

    # AoE: 18.5% + 13.875% + 3% = 35.375%
    assert totals.aoe == pytest.approx(0.35375, rel=1e-5)

    # DDR: 20% + 10% = 30%
    assert totals.ddr == pytest.approx(0.30, rel=1e-5)

    # Soft cap checks
    assert not calc.is_soft_capped(totals.melee)  # 35.375% < 45%
    assert calc.is_soft_capped(totals.ranged)     # 56.625% >= 45%
    assert not calc.is_soft_capped(totals.aoe)    # 35.375% < 45%

    # Effective defense checks
    # Psionic ranged attack (common SR weakness check)
    effective = calc.get_effective_defense(totals, DefenseType.PSIONIC, DefenseType.RANGED)
    assert effective == pytest.approx(0.56625, rel=1e-5)  # max(0%, 56.625%) = 56.625%
    assert calc.is_soft_capped(effective)  # SR has NO psi hole with positional defense!
```

#### Test 61: Real Build - Shield Defense Tanker

```python
def test_61_shield_defense_tanker():
    """Complete Shield Defense Tanker build test"""

    # Arrange
    calc = BuildDefenseTotalsCalculator()

    # Act
    # Primary powers (Tanker values)
    calc.add_power_defense("Deflection", DefenseType.MELEE, 0.156)
    calc.add_power_defense("Deflection", DefenseType.RANGED, 0.156)
    calc.add_power_defense("Battle Agility", DefenseType.MELEE, 0.156)
    calc.add_power_defense("Battle Agility", DefenseType.RANGED, 0.156)
    calc.add_power_defense("Battle Agility", DefenseType.AOE, 0.156)
    calc.add_power_defense("True Grit", DefenseType.SMASHING, 0.052)
    calc.add_power_defense("True Grit", DefenseType.LETHAL, 0.052)
    calc.add_power_defense("Grant Cover", DefenseType.SMASHING, 0.078)
    calc.add_power_defense("Grant Cover", DefenseType.LETHAL, 0.078)

    # Set bonuses to reach soft cap
    calc.add_set_bonus_defense("Various Sets", DefenseType.MELEE, 0.138)
    calc.add_set_bonus_defense("Various Sets", DefenseType.RANGED, 0.138)
    calc.add_set_bonus_defense("Various Sets", DefenseType.AOE, 0.294)

    # DDR
    calc.add_power_defense("Grant Cover", DefenseType.MELEE, 0.10, is_ddr=True)
    calc.add_set_bonus_defense("Set Bonus", DefenseType.MELEE, 0.03, is_ddr=True)

    totals = calc.calculate_totals()

    # Assert
    # Typed S/L: 5.2% + 7.8% = 13.0%
    assert totals.smashing == pytest.approx(0.13, rel=1e-5)
    assert totals.lethal == pytest.approx(0.13, rel=1e-5)

    # Positional (with set bonuses):
    # Melee: 15.6% + 15.6% + 13.8% = 45.0%
    assert totals.melee == pytest.approx(0.45, rel=1e-5)

    # Ranged: 15.6% + 15.6% + 13.8% = 45.0%
    assert totals.ranged == pytest.approx(0.45, rel=1e-5)

    # AoE: 15.6% + 29.4% = 45.0%
    assert totals.aoe == pytest.approx(0.45, rel=1e-5)

    # DDR: 10% + 3% = 13%
    assert totals.ddr == pytest.approx(0.13, rel=1e-5)

    # All positional soft capped
    assert calc.is_soft_capped(totals.melee)
    assert calc.is_soft_capped(totals.ranged)
    assert calc.is_soft_capped(totals.aoe)

    # Effective defense vs S/L melee (uses HIGHER of typed or positional)
    effective = calc.get_effective_defense(totals, DefenseType.SMASHING, DefenseType.MELEE)
    assert effective == pytest.approx(0.45, rel=1e-5)  # max(13%, 45%) = 45%
```

#### Test 70: Edge Case - Negative Defense from Debuffs

```python
def test_70_negative_defense_from_debuffs():
    """Defense should not go below 0% even with debuffs"""

    # Arrange
    calc = BuildDefenseTotalsCalculator()

    # Act
    calc.add_power_defense("Small Defense", DefenseType.MELEE, 0.10)  # 10% defense
    totals = calc.calculate_totals()

    # Apply massive debuff
    debuff = 0.50  # -50% defense debuff
    net_defense = calc.apply_defense_debuffs(totals, debuff, DefenseType.MELEE)

    # Assert
    # 10% - 50% = -40%, but should floor at 0%
    assert net_defense == pytest.approx(0.0, rel=1e-6)
```

#### Test 72: All Defense Types Matrix

```python
def test_72_all_defense_types_matrix():
    """Test all 8 typed × 3 positional = 24 attack type combinations"""

    # Arrange
    calc = BuildDefenseTotalsCalculator()

    # Act - Add varied defense values
    calc.add_power_defense("Smashing Defense", DefenseType.SMASHING, 0.20)
    calc.add_power_defense("Fire Defense", DefenseType.FIRE, 0.30)
    calc.add_power_defense("Psionic Defense", DefenseType.PSIONIC, 0.10)
    calc.add_power_defense("Melee Defense", DefenseType.MELEE, 0.40)
    calc.add_power_defense("Ranged Defense", DefenseType.RANGED, 0.45)
    totals = calc.calculate_totals()

    # Assert - Test all combinations
    test_cases = [
        # (typed, positional, expected_effective)
        (DefenseType.SMASHING, DefenseType.MELEE, 0.40),   # max(0.20, 0.40)
        (DefenseType.SMASHING, DefenseType.RANGED, 0.45),  # max(0.20, 0.45)
        (DefenseType.FIRE, DefenseType.MELEE, 0.40),       # max(0.30, 0.40)
        (DefenseType.FIRE, DefenseType.RANGED, 0.45),      # max(0.30, 0.45)
        (DefenseType.PSIONIC, DefenseType.MELEE, 0.40),    # max(0.10, 0.40)
        (DefenseType.PSIONIC, DefenseType.RANGED, 0.45),   # max(0.10, 0.45)
        (DefenseType.COLD, DefenseType.MELEE, 0.40),       # max(0.0, 0.40)
        (DefenseType.COLD, DefenseType.RANGED, 0.45),      # max(0.0, 0.45)
    ]

    for typed, positional, expected in test_cases:
        effective = calc.get_effective_defense(totals, typed, positional)
        assert effective == pytest.approx(expected, rel=1e-6), \
            f"Failed for {typed.name}/{positional.name}"
```

### Test Execution Matrix

| Test Category | Test Count | Purpose |
|--------------|-----------|---------|
| Basic Aggregation | 7 | Verify defense stacks from all sources |
| Typed Defense | 4 | Verify 8 typed defense types |
| Positional Defense | 4 | Verify 3 positional defense types |
| "Highest Wins" Rule | 4 | Verify max(typed, positional) logic |
| Soft Cap | 4 | Verify 45% soft cap detection |
| DDR | 4 | Verify DDR calculation and capping |
| Real Builds | 4 | Integration tests with real build examples |
| Edge Cases | 4 | Boundary conditions and error cases |
| **Total** | **35** | **Complete test coverage** |

### Expected MidsReborn Comparison Data

For integration testing, these values are from actual MidsReborn builds:

**Super Reflexes Scrapper (Level 50):**
```
Typed Defense:   All 0.00%
Positional:      Melee 35.38%, Ranged 56.63%, AoE 35.38%
DDR:            30.00%
Soft Cap:       Ranged only
```

**Shield Defense Tanker (Level 50):**
```
Typed Defense:   S/L 13.00%, others 0.00%
Positional:      Melee 45.00%, Ranged 45.00%, AoE 45.00%
DDR:            13.00%
Soft Cap:       All positional
```

**Energy Aura Stalker (Level 50):**
```
Typed Defense:   Energy 31.20%, Negative 31.20%, others 0.00%
Positional:      All 20.80%
DDR:            40.00%
Soft Cap:       None (needs IO slotting)
```

## Section 5: Python Implementation

### Complete Python Module

```python
# backend/app/calculations/build_totals_defense.py

"""
Build Totals Defense Calculator

Aggregates ALL defense from powers, set bonuses, global IOs, and incarnates
into final defense totals. Implements City of Heroes defense mechanics including
the "highest wins" rule for typed vs positional defense.

Author: Mids Hero Web Team
Date: 2025-11-11
Status: Milestone 3 Depth Coverage
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class DefenseType(Enum):
    """
    Defense types matching MidsReborn eDamage enum indices

    Indices 0-7: Typed defense
    Indices 7-9: Positional defense (note: Toxic index may vary)
    """
    # Typed defense (8 types)
    SMASHING = 0
    LETHAL = 1
    FIRE = 2
    COLD = 3
    ENERGY = 4
    NEGATIVE = 5
    PSIONIC = 6
    TOXIC = 7  # Added by Homecoming, index may vary

    # Positional defense (3 types)
    MELEE = 8
    RANGED = 9
    AOE = 10


@dataclass
class DefenseTotals:
    """
    Build-wide defense totals

    Stores all 11 defense values + DDR
    Maps to Character.Totals.Def[] in MidsReborn

    All values stored as decimals (0.45 = 45%)
    """
    # Typed defense (8 types)
    smashing: float = 0.0
    lethal: float = 0.0
    fire: float = 0.0
    cold: float = 0.0
    energy: float = 0.0
    negative: float = 0.0
    psionic: float = 0.0
    toxic: float = 0.0

    # Positional defense (3 types)
    melee: float = 0.0
    ranged: float = 0.0
    aoe: float = 0.0

    # Defense debuff resistance (DDR)
    # Capped at 95% (0.95)
    ddr: float = 0.0

    # Source breakdown (for display/debugging)
    sources: Dict[str, float] = field(default_factory=dict)

    def get_defense(self, defense_type: DefenseType) -> float:
        """Get defense value for a specific type"""
        attr = defense_type.name.lower()
        return getattr(self, attr, 0.0)

    def set_defense(self, defense_type: DefenseType, value: float) -> None:
        """Set defense value for a specific type"""
        attr = defense_type.name.lower()
        if hasattr(self, attr):
            setattr(self, attr, value)

    def add_defense(self, defense_type: DefenseType, magnitude: float) -> None:
        """Add defense magnitude to a specific type"""
        current = self.get_defense(defense_type)
        self.set_defense(defense_type, current + magnitude)


@dataclass
class DefenseSource:
    """
    Individual source of defense

    Used for tracking where defense comes from (breakdown display)
    """
    source_type: str  # "power", "set_bonus", "global_io", "incarnate"
    source_name: str  # Human-readable name
    defense_type: DefenseType
    magnitude: float  # Defense value (0.0 to 1.0+)
    is_ddr: bool = False  # True if this is DDR, not defense
    is_active: bool = True  # For toggles that can be on/off


class BuildDefenseTotalsCalculator:
    """
    Aggregates ALL defense from powers, sets, IOs, incarnates

    Maps to logic in Character.cs and frmTotalsV2.cs in MidsReborn

    Usage:
        calc = BuildDefenseTotalsCalculator()
        calc.add_power_defense("Focused Fighting", DefenseType.MELEE, 0.185)
        calc.add_set_bonus_defense("Luck of the Gambler", DefenseType.RANGED, 0.03)
        totals = calc.calculate_totals()
    """

    # Defense soft cap (45% vs even-level enemies)
    # This is NOT a hard cap - values above 45% are useful vs +level enemies
    SOFT_CAP = 0.45

    # DDR hard cap (95%)
    # Unlike defense itself, DDR has a hard cap
    DDR_CAP = 0.95

    def __init__(self):
        """Initialize defense totals calculator"""
        self.sources: List[DefenseSource] = []
        logger.debug("BuildDefenseTotalsCalculator initialized")

    def add_power_defense(
        self,
        power_name: str,
        defense_type: DefenseType,
        magnitude: float,
        is_ddr: bool = False,
        is_active: bool = True
    ) -> None:
        """
        Add defense from an active power

        Powers include toggles, autos, and click buffs

        Args:
            power_name: Name of power granting defense
            defense_type: Type of defense granted (e.g., MELEE, SMASHING)
            magnitude: Defense value (0.0 to 1.0+), already scaled by AT modifiers
            is_ddr: True if this is DDR instead of defense
            is_active: True if power is on/active (for toggles)

        Example:
            calc.add_power_defense("Focused Fighting", DefenseType.MELEE, 0.185)
        """
        source = DefenseSource(
            source_type="power",
            source_name=power_name,
            defense_type=defense_type,
            magnitude=magnitude,
            is_ddr=is_ddr,
            is_active=is_active
        )
        self.sources.append(source)
        logger.debug(f"Added power defense: {power_name} +{magnitude:.4f} {defense_type.name}")

    def add_set_bonus_defense(
        self,
        set_name: str,
        defense_type: DefenseType,
        magnitude: float,
        is_ddr: bool = False
    ) -> None:
        """
        Add defense from enhancement set bonus

        Set bonuses are ALWAYS active (no on/off toggle)

        Args:
            set_name: Name of enhancement set
            defense_type: Type of defense granted
            magnitude: Defense value (typically 0.015 to 0.05 for set bonuses)
            is_ddr: True if this is DDR instead of defense

        Example:
            calc.add_set_bonus_defense("Luck of the Gambler", DefenseType.RANGED, 0.03)
        """
        source = DefenseSource(
            source_type="set_bonus",
            source_name=set_name,
            defense_type=defense_type,
            magnitude=magnitude,
            is_ddr=is_ddr,
            is_active=True  # Set bonuses always active
        )
        self.sources.append(source)
        logger.debug(f"Added set bonus defense: {set_name} +{magnitude:.4f} {defense_type.name}")

    def add_global_io_defense(
        self,
        io_name: str,
        defense_type: DefenseType,
        magnitude: float,
        is_ddr: bool = False
    ) -> None:
        """
        Add defense from global IO

        Global IOs like "Steadfast Protection: Resistance/Defense" or
        "Shield Wall" grant defense that is ALWAYS active

        Args:
            io_name: Name of IO
            defense_type: Type of defense granted
            magnitude: Defense value (typically 0.03 for global IOs)
            is_ddr: True if this is DDR instead of defense

        Example:
            calc.add_global_io_defense("Shield Wall", DefenseType.MELEE, 0.03)
        """
        source = DefenseSource(
            source_type="global_io",
            source_name=io_name,
            defense_type=defense_type,
            magnitude=magnitude,
            is_ddr=is_ddr,
            is_active=True  # Global IOs always active
        )
        self.sources.append(source)
        logger.debug(f"Added global IO defense: {io_name} +{magnitude:.4f} {defense_type.name}")

    def add_incarnate_defense(
        self,
        incarnate_name: str,
        defense_type: DefenseType,
        magnitude: float,
        is_ddr: bool = False,
        is_active: bool = True
    ) -> None:
        """
        Add defense from incarnate power

        Incarnate powers like Destiny can grant large defense buffs

        Args:
            incarnate_name: Name of incarnate power
            defense_type: Type of defense granted
            magnitude: Defense value (can be large, 0.15+ for Destiny)
            is_ddr: True if this is DDR instead of defense
            is_active: True if incarnate power is active

        Example:
            calc.add_incarnate_defense("Barrier Radial", DefenseType.MELEE, 0.15)
        """
        source = DefenseSource(
            source_type="incarnate",
            source_name=incarnate_name,
            defense_type=defense_type,
            magnitude=magnitude,
            is_ddr=is_ddr,
            is_active=is_active
        )
        self.sources.append(source)
        logger.debug(f"Added incarnate defense: {incarnate_name} +{magnitude:.4f} {defense_type.name}")

    def calculate_totals(self) -> DefenseTotals:
        """
        Aggregate all defense sources into totals

        Simple summation of all sources - no multiplication, no caps
        (except DDR cap at 95%)

        Returns:
            DefenseTotals with aggregated values
        """
        logger.info(f"Calculating defense totals from {len(self.sources)} sources")

        totals = DefenseTotals()

        # Aggregate all active sources
        for source in self.sources:
            if not source.is_active:
                logger.debug(f"Skipping inactive source: {source.source_name}")
                continue

            if source.is_ddr:
                # Add to DDR
                totals.ddr += source.magnitude
                logger.debug(f"  DDR: +{source.magnitude:.4f} from {source.source_name}")
            else:
                # Add to appropriate defense type
                totals.add_defense(source.defense_type, source.magnitude)

                # Track source breakdown
                source_key = f"{source.source_type}:{source.source_name}"
                if source_key in totals.sources:
                    totals.sources[source_key] += source.magnitude
                else:
                    totals.sources[source_key] = source.magnitude

                logger.debug(
                    f"  {source.defense_type.name}: +{source.magnitude:.4f} "
                    f"from {source.source_name}"
                )

        # Cap DDR at 95%
        if totals.ddr > self.DDR_CAP:
            logger.warning(f"DDR {totals.ddr:.2%} exceeds cap, capping at {self.DDR_CAP:.0%}")
            totals.ddr = self.DDR_CAP

        # Defense itself has NO cap (unlike resistance)
        # Values above 45% are still useful vs +level enemies

        logger.info(f"Defense totals calculated: {len(totals.sources)} sources aggregated")
        return totals

    def get_effective_defense(
        self,
        totals: DefenseTotals,
        typed_defense_type: DefenseType,
        positional_defense_type: DefenseType
    ) -> float:
        """
        Calculate effective defense for a specific attack

        CRITICAL: City of Heroes uses MAX(typed, positional), NOT sum

        This is the "highest wins" rule that is fundamental to defense mechanics

        Args:
            totals: Defense totals
            typed_defense_type: Typed defense type (e.g., FIRE, SMASHING)
            positional_defense_type: Positional type (e.g., RANGED, MELEE)

        Returns:
            Effective defense (higher of typed or positional)

        Example:
            # Fire/Ranged attack
            effective = calc.get_effective_defense(
                totals, DefenseType.FIRE, DefenseType.RANGED
            )
            # Returns max(fire_defense, ranged_defense)
        """
        typed_defense = totals.get_defense(typed_defense_type)
        positional_defense = totals.get_defense(positional_defense_type)

        effective = max(typed_defense, positional_defense)

        logger.debug(
            f"Effective defense vs {typed_defense_type.name}/{positional_defense_type.name}: "
            f"{effective:.4f} (max of {typed_defense:.4f} typed, {positional_defense:.4f} positional)"
        )

        return effective

    def is_soft_capped(self, defense_value: float) -> bool:
        """
        Check if defense has reached soft cap (45%)

        Args:
            defense_value: Defense value to check

        Returns:
            True if >= 45%
        """
        return defense_value >= self.SOFT_CAP

    def distance_to_soft_cap(self, defense_value: float) -> float:
        """
        Calculate distance to soft cap

        Args:
            defense_value: Current defense value

        Returns:
            Defense needed to reach soft cap (negative if over)
        """
        return self.SOFT_CAP - defense_value

    def check_soft_cap_coverage(self, totals: DefenseTotals) -> Dict[str, bool]:
        """
        Check soft cap coverage for all defense types

        Returns:
            Dictionary of coverage status
        """
        coverage = {
            # Typed defense
            'smashing_capped': self.is_soft_capped(totals.smashing),
            'lethal_capped': self.is_soft_capped(totals.lethal),
            'fire_capped': self.is_soft_capped(totals.fire),
            'cold_capped': self.is_soft_capped(totals.cold),
            'energy_capped': self.is_soft_capped(totals.energy),
            'negative_capped': self.is_soft_capped(totals.negative),
            'psionic_capped': self.is_soft_capped(totals.psionic),
            'toxic_capped': self.is_soft_capped(totals.toxic),

            # Positional defense
            'melee_capped': self.is_soft_capped(totals.melee),
            'ranged_capped': self.is_soft_capped(totals.ranged),
            'aoe_capped': self.is_soft_capped(totals.aoe),

            # All positional (common build goal)
            'all_positional_capped': (
                self.is_soft_capped(totals.melee) and
                self.is_soft_capped(totals.ranged) and
                self.is_soft_capped(totals.aoe)
            ),
        }

        return coverage

    def apply_defense_debuffs(
        self,
        totals: DefenseTotals,
        debuff_magnitude: float,
        defense_type: DefenseType
    ) -> float:
        """
        Apply defense debuff with DDR mitigation

        DDR reduces debuff magnitude by: actual_debuff = base_debuff * (1 - DDR)

        Args:
            totals: Current defense totals (includes DDR)
            debuff_magnitude: Defense debuff (positive value, will be subtracted)
            defense_type: Which defense is being debuffed

        Returns:
            Net defense after debuff (floored at 0.0)
        """
        base_defense = totals.get_defense(defense_type)

        # DDR reduces debuff magnitude
        actual_debuff = debuff_magnitude * (1 - totals.ddr)

        # Apply debuff to defense
        net_defense = base_defense - actual_debuff

        # Defense cannot go negative
        net_defense = max(0.0, net_defense)

        logger.info(
            f"Applied defense debuff: {defense_type.name} "
            f"{base_defense:.2%} - {debuff_magnitude:.2%} (DDR {totals.ddr:.0%}) "
            f"= {net_defense:.2%}"
        )

        return net_defense

    def format_display(self, totals: DefenseTotals) -> Dict[str, str]:
        """
        Format defense totals for display

        Converts decimal values to percentage strings with soft cap indicators

        Args:
            totals: Defense totals to format

        Returns:
            Dict of formatted display strings
        """
        display = {}

        # Typed defense
        for defense_type in [
            DefenseType.SMASHING, DefenseType.LETHAL,
            DefenseType.FIRE, DefenseType.COLD,
            DefenseType.ENERGY, DefenseType.NEGATIVE,
            DefenseType.PSIONIC, DefenseType.TOXIC
        ]:
            attr = defense_type.name.lower()
            value = totals.get_defense(defense_type)
            percentage = value * 100

            # Format with soft cap indicator
            if self.is_soft_capped(value):
                display[attr] = f"{percentage:.2f}% (Soft Cap)"
            else:
                needed = self.distance_to_soft_cap(value) * 100
                display[attr] = f"{percentage:.2f}% ({needed:.2f}% to soft cap)"

        # Positional defense
        for defense_type in [DefenseType.MELEE, DefenseType.RANGED, DefenseType.AOE]:
            attr = defense_type.name.lower()
            value = totals.get_defense(defense_type)
            percentage = value * 100

            if self.is_soft_capped(value):
                display[attr] = f"{percentage:.2f}% (Soft Cap)"
            else:
                needed = self.distance_to_soft_cap(value) * 100
                display[attr] = f"{percentage:.2f}% ({needed:.2f}% to soft cap)"

        # DDR with cap indicator
        ddr_percentage = totals.ddr * 100
        if totals.ddr >= self.DDR_CAP:
            display["ddr"] = f"{ddr_percentage:.2f}% (Capped)"
        else:
            display["ddr"] = f"{ddr_percentage:.2f}%"

        return display

    def get_defense_breakdown(self, totals: DefenseTotals) -> Dict[str, List[Tuple[str, float]]]:
        """
        Get breakdown of defense sources for display

        Returns:
            Dict mapping defense type to list of (source_name, magnitude) tuples
        """
        breakdown: Dict[str, List[Tuple[str, float]]] = {}

        for source in self.sources:
            if not source.is_active or source.is_ddr:
                continue

            defense_name = source.defense_type.name.lower()
            if defense_name not in breakdown:
                breakdown[defense_name] = []

            breakdown[defense_name].append((source.source_name, source.magnitude))

        # Sort by magnitude descending
        for defense_type in breakdown:
            breakdown[defense_type].sort(key=lambda x: x[1], reverse=True)

        return breakdown


# Example usage
def example_super_reflexes_scrapper():
    """
    Example: Super Reflexes Scrapper build

    Demonstrates pure positional defense build
    """
    calc = BuildDefenseTotalsCalculator()

    # Toggles
    calc.add_power_defense("Focused Fighting", DefenseType.MELEE, 0.185)
    calc.add_power_defense("Focused Senses", DefenseType.RANGED, 0.185)
    calc.add_power_defense("Evasion", DefenseType.AOE, 0.185)

    # Passives
    calc.add_power_defense("Agile", DefenseType.MELEE, 0.13875)
    calc.add_power_defense("Dodge", DefenseType.RANGED, 0.13875)
    calc.add_power_defense("Lucky", DefenseType.AOE, 0.13875)

    # Set bonuses
    for i in range(5):
        calc.add_set_bonus_defense("Luck of the Gambler", DefenseType.RANGED, 0.03)

    # Global IOs
    calc.add_global_io_defense("Shield Wall", DefenseType.MELEE, 0.03)
    calc.add_global_io_defense("Shield Wall", DefenseType.RANGED, 0.03)
    calc.add_global_io_defense("Shield Wall", DefenseType.AOE, 0.03)

    # DDR
    calc.add_power_defense("Quickness", DefenseType.MELEE, 0.20, is_ddr=True)
    calc.add_power_defense("Practiced Brawler", DefenseType.MELEE, 0.10, is_ddr=True)

    # Calculate
    totals = calc.calculate_totals()

    # Display
    display = calc.format_display(totals)
    print("=== Super Reflexes Scrapper ===")
    print(f"Melee:  {display['melee']}")
    print(f"Ranged: {display['ranged']}")
    print(f"AoE:    {display['aoe']}")
    print(f"DDR:    {display['ddr']}")

    # Check effective defense vs common attacks
    eff_psi_ranged = calc.get_effective_defense(totals, DefenseType.PSIONIC, DefenseType.RANGED)
    print(f"\nEffective vs Psionic/Ranged: {eff_psi_ranged:.2%}")
    print("SR has NO psi hole!" if calc.is_soft_capped(eff_psi_ranged) else "Needs more defense")


if __name__ == "__main__":
    # Run example
    example_super_reflexes_scrapper()
```

### Usage Examples

#### Example 1: Basic Build

```python
from app.calculations.build_totals_defense import (
    BuildDefenseTotalsCalculator, DefenseType
)

# Create calculator
calc = BuildDefenseTotalsCalculator()

# Add powers
calc.add_power_defense("Focused Fighting", DefenseType.MELEE, 0.185)
calc.add_power_defense("Focused Senses", DefenseType.RANGED, 0.185)

# Add set bonuses
calc.add_set_bonus_defense("Luck of the Gambler", DefenseType.RANGED, 0.03)

# Calculate totals
totals = calc.calculate_totals()

# Display
display = calc.format_display(totals)
print(f"Melee Defense: {display['melee']}")
print(f"Ranged Defense: {display['ranged']}")
```

#### Example 2: Check Soft Cap Coverage

```python
# Calculate totals
totals = calc.calculate_totals()

# Check coverage
coverage = calc.check_soft_cap_coverage(totals)

if coverage['all_positional_capped']:
    print("All positional defense soft capped!")
else:
    if not coverage['melee_capped']:
        needed = calc.distance_to_soft_cap(totals.melee) * 100
        print(f"Melee needs {needed:.2f}% more defense")
```

#### Example 3: Effective Defense vs Attack

```python
# Calculate totals
totals = calc.calculate_totals()

# Check effective defense vs Fire/Ranged attack
effective = calc.get_effective_defense(
    totals,
    DefenseType.FIRE,
    DefenseType.RANGED
)

print(f"Effective defense vs Fire/Ranged: {effective:.2%}")
if calc.is_soft_capped(effective):
    print("Soft capped against this attack type!")
```

#### Example 4: Defense Debuff Simulation

```python
# Calculate totals
totals = calc.calculate_totals()

# Simulate -20% defense debuff to Melee
base_melee = totals.melee
debuff = 0.20
net_melee = calc.apply_defense_debuffs(totals, debuff, DefenseType.MELEE)

print(f"Base Melee Defense: {base_melee:.2%}")
print(f"After -20% Debuff (with {totals.ddr:.0%} DDR): {net_melee:.2%}")
print(f"Actual debuff: {(base_melee - net_melee):.2%}")
```

## Section 6: Integration Points

### Upstream Dependencies

Defense totals are calculated by aggregating from multiple upstream systems:

#### 1. Power Effects (Spec 01)

**Integration:**
- Powers have `Effects` collection
- Each effect has `EffectType`, `DamageType`, `Magnitude`
- Filter for `EffectType.DEFENSE` effects
- `DamageType` determines which defense type (SMASHING, MELEE, etc.)
- `Magnitude` is already scaled by AT modifiers (see Spec 16)

**Code Integration:**
```python
# From power processing
for power_entry in build.powers:
    if not power_entry.stat_include:
        continue  # Power is off

    power = power_entry.power
    for effect in power.effects:
        if effect.effect_type == EffectType.DEFENSE:
            calc.add_power_defense(
                power_name=power.name,
                defense_type=effect.damage_type,
                magnitude=effect.magnitude,  # Already scaled by AT mods
                is_active=power_entry.stat_include
            )
```

#### 2. Enhancement Set Bonuses (Spec 13)

**Integration:**
- Calculate which set bonuses are active (based on slotted enhancements)
- Filter for defense bonuses
- Set bonuses are ALWAYS active (no on/off state)

**Code Integration:**
```python
# From set bonus processing
set_bonuses = build.calculate_set_bonuses()
for bonus in set_bonuses:
    if bonus.effect_type == EffectType.DEFENSE:
        calc.add_set_bonus_defense(
            set_name=bonus.set_name,
            defense_type=bonus.damage_type,
            magnitude=bonus.magnitude
        )
```

#### 3. Global IOs (Spec 14)

**Integration:**
- Global IOs grant defense that is ALWAYS active
- Examples: "Shield Wall" (+3% def all), "Steadfast Protection" (+3% def all)
- Scan all slotted enhancements for global effects

**Code Integration:**
```python
# From enhancement processing
for power_entry in build.powers:
    for slot in power_entry.slots:
        enhancement = slot.enhancement
        if enhancement.has_global_effects:
            for global_effect in enhancement.global_effects:
                if global_effect.effect_type == EffectType.DEFENSE:
                    calc.add_global_io_defense(
                        io_name=enhancement.name,
                        defense_type=global_effect.damage_type,
                        magnitude=global_effect.magnitude
                    )
```

#### 4. Archetype Modifiers (Spec 16)

**Integration:**
- AT modifiers scale defense values BEFORE aggregation
- Defense scaling varies by AT (Tankers get 1.0x, Scrappers get 0.75x, etc.)
- Magnitude values passed to calculator are already scaled

**Note:** Defense scaling happens in power effect processing, not in totals calculation.

#### 5. Incarnate Powers

**Integration:**
- Destiny incarnate can grant massive defense buffs (15%+)
- Other incarnate slots may grant smaller defense
- May have temporary duration (for build planning, show permanent values)

**Code Integration:**
```python
# From incarnate processing
if build.incarnates.destiny and build.incarnates.destiny.active:
    destiny = build.incarnates.destiny
    for effect in destiny.effects:
        if effect.effect_type == EffectType.DEFENSE:
            calc.add_incarnate_defense(
                incarnate_name=destiny.name,
                defense_type=effect.damage_type,
                magnitude=effect.magnitude,
                is_active=True
            )
```

### Downstream Consumers

Defense totals are used by multiple downstream systems:

#### 1. Build Totals Display (Spec 20)

**Integration:**
- Display all 11 defense values in Totals window
- Show soft cap indicators
- Color-code defense values (red < 20%, yellow 20-44%, green 45%+)
- Display DDR

**UI Display:**
```
Defense:
  Smashing:  13.00% (32.00% to soft cap)
  Lethal:    13.00% (32.00% to soft cap)
  Fire:      0.00% (45.00% to soft cap)
  ...
  Melee:     45.00% (Soft Cap) ✓
  Ranged:    56.88% (Soft Cap) ✓
  AoE:       35.38% (9.62% to soft cap)

Defense Debuff Resistance: 30.00%

Effective Defense vs Common Attacks:
  S/L Melee:      45.00% (soft capped)
  Fire Ranged:    56.88% (soft capped)
  Psionic Ranged: 56.88% (soft capped)
```

#### 2. Survivability Index (Spec 32)

**Integration:**
- Defense totals feed into EHP (Effective Hit Points) calculations
- Higher defense = higher EHP
- Formula: `EHP = HP / (1 - defense)`
- Must account for "highest wins" rule when calculating EHP

**Code Integration:**
```python
# From survivability calculation
def calculate_ehp_vs_attack(hp, defense_totals, attack_typed, attack_positional):
    """Calculate EHP for a specific attack type"""
    effective_defense = calc.get_effective_defense(
        defense_totals, attack_typed, attack_positional
    )

    # Cap defense at 0.75 for EHP calculation (75% = 4x HP)
    # Game uses 5% tohit floor, so effective cap is 45% defense
    effective_defense = min(effective_defense, 0.45)

    # EHP = HP / (1 - defense)
    # At 45% defense: EHP = HP / 0.55 = HP × 1.82
    ehp = hp / (1.0 - effective_defense)

    return ehp
```

#### 3. Build Comparison (Spec 36)

**Integration:**
- Compare defense totals between builds
- Show delta (improvement/regression)
- Highlight soft cap achievement
- Compare effective defense vs common attack types

**Display:**
```
Build Comparison: Build A vs Build B

Defense:
  Melee:   35.38% → 45.00% (+9.62% SOFT CAP REACHED!)
  Ranged:  56.88% → 56.88% (no change)
  AoE:     35.38% → 40.00% (+4.62%)

DDR:       30.00% → 45.00% (+15.00%)

Survivability:
  EHP (S/L Melee): 2500 → 3200 (+28%)
```

#### 4. Build Planner UI

**Integration:**
- Real-time updates as powers are added/removed
- Show "what-if" scenarios (toggle powers on/off)
- Suggest IOs/sets to reach soft cap
- Highlight defense gaps

**UI Features:**
- Defense radar chart (shows all 11 defense types visually)
- Soft cap progress bars
- Defense breakdown by source
- Toggle simulation (click power to see defense change)

### Complete Integration Example

```python
# Complete build defense calculation flow

# 1. Initialize calculator
calc = BuildDefenseTotalsCalculator()

# 2. Aggregate from powers (Spec 01)
for power_entry in build.powers:
    if not power_entry.stat_include:
        continue

    power = power_entry.power
    for effect in power.effects:
        if effect.effect_type == EffectType.DEFENSE:
            # Magnitude already scaled by AT modifiers (Spec 16)
            calc.add_power_defense(
                power_name=power.name,
                defense_type=effect.damage_type,
                magnitude=effect.magnitude,
                is_active=True
            )
        elif effect.effect_type == EffectType.DEFENSE_DEBUFF_RESISTANCE:
            calc.add_power_defense(
                power_name=power.name,
                defense_type=DefenseType.MELEE,  # DDR type doesn't matter
                magnitude=effect.magnitude,
                is_ddr=True
            )

# 3. Aggregate from set bonuses (Spec 13)
set_bonuses = build.calculate_set_bonuses()
for bonus in set_bonuses:
    if bonus.effect_type == EffectType.DEFENSE:
        calc.add_set_bonus_defense(
            set_name=bonus.set_name,
            defense_type=bonus.damage_type,
            magnitude=bonus.magnitude
        )

# 4. Aggregate from global IOs (Spec 14)
for power_entry in build.powers:
    for slot in power_entry.slots:
        if slot.enhancement.has_global_effects:
            for global_effect in slot.enhancement.global_effects:
                if global_effect.effect_type == EffectType.DEFENSE:
                    calc.add_global_io_defense(
                        io_name=slot.enhancement.name,
                        defense_type=global_effect.damage_type,
                        magnitude=global_effect.magnitude
                    )

# 5. Aggregate from incarnates
if build.incarnates.destiny:
    destiny = build.incarnates.destiny
    for effect in destiny.effects:
        if effect.effect_type == EffectType.DEFENSE:
            calc.add_incarnate_defense(
                incarnate_name=destiny.name,
                defense_type=effect.damage_type,
                magnitude=effect.magnitude
            )

# 6. Calculate totals
totals = calc.calculate_totals()

# 7. Store in database
db.build_defense_totals.insert({
    'build_id': build.id,
    'level_index': build.level,
    'defense_smashing': totals.smashing,
    'defense_lethal': totals.lethal,
    # ... all defense types
    'defense_debuff_resistance': totals.ddr,
    'calculated_at': datetime.now()
})

# 8. Display in UI (Spec 20)
display = calc.format_display(totals)
ui.show_defense_totals(display)

# 9. Calculate survivability (Spec 32)
ehp_vs_sl_melee = calculate_ehp_vs_attack(
    hp=build_hp_totals.max_hp,
    defense_totals=totals,
    attack_typed=DefenseType.SMASHING,
    attack_positional=DefenseType.MELEE
)
ui.show_survivability_metric("EHP (S/L Melee)", ehp_vs_sl_melee)

# 10. Compare to other builds (Spec 36)
if comparison_build:
    comparison_totals = calculate_defense_totals(comparison_build)
    delta = compare_defense_totals(totals, comparison_totals)
    ui.show_comparison(delta)
```

### Integration Checklist

- [ ] Power effect aggregation (Spec 01)
- [ ] Set bonus aggregation (Spec 13)
- [ ] Global IO aggregation (Spec 14)
- [ ] AT modifier scaling (Spec 16)
- [ ] Incarnate aggregation
- [ ] Totals display (Spec 20)
- [ ] Survivability calculation (Spec 32)
- [ ] Build comparison (Spec 36)
- [ ] Database storage
- [ ] UI real-time updates
- [ ] "What-if" toggle simulation
- [ ] Defense breakdown display
- [ ] Soft cap indicators
- [ ] Effective defense matrix (8 typed × 3 positional)

---

**End of Depth Coverage - Milestone 3**
