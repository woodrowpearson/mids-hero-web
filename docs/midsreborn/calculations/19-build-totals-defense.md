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
