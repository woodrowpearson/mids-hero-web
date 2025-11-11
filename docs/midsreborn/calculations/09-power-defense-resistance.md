# Power Defense/Resistance

## Overview
- **Purpose**: Calculate defense and resistance values - the primary damage mitigation mechanics in City of Heroes
- **Used By**: Character totals, power tooltips, build planning, damage mitigation calculations
- **Complexity**: High
- **Priority**: Critical
- **Status**: 🟡 Breadth Complete

## MidsReborn Implementation

### Primary Location
- **File**: `Core/Stats.cs`
- **Classes**: `Defense`, `Resistance`, `DebuffResistance`, `DefenseDebuff`, `ResistanceDebuff`
- **Related Files**:
  - `Core/Base/Data_Classes/Effect.cs` - Effect type handling
  - `Core/Base/Data_Classes/Archetype.cs` - Archetype caps (`ResCap`, `HPCap`)
  - `Core/Statistics.cs` - Defense/resistance display calculations
  - `clsToonX.cs` - Cap application in `TotalsCapped` calculation

### Defense Structure

Defense in City of Heroes has two systems that work in parallel:

**Typed Defense** (8 damage types):
- Smashing
- Lethal
- Fire
- Cold
- Energy
- Negative
- Psionic
- Toxic

**Positional Defense** (3 attack vectors):
- Melee (close range attacks)
- Ranged (distance attacks)
- AoE (area of effect attacks)

```csharp
// From Core/Stats.cs
public class Defense
{
    public Smashing Smashing { get; set; }
    public Lethal Lethal { get; set; }
    public Fire Fire { get; set; }
    public Cold Cold { get; set; }
    public Energy Energy { get; set; }
    public Negative Negative { get; set; }
    public Psionic Psionic { get; set; }
    public Toxic Toxic { get; set; }
    public Melee Melee { get; set; }
    public Ranged Ranged { get; set; }
    public Aoe Aoe { get; set; }
}

// Each defense type is a stat with Base/Current/Maximum
public class Smashing
{
    public float Base { get; set; }
    public float Current { get; set; }
    public float Maximum { get; set; }
}
```

### Resistance Structure

Resistance only uses **typed resistance** (8 damage types, no positional):
- Smashing
- Lethal
- Fire
- Cold
- Energy
- Negative
- Psionic
- Toxic

```csharp
// From Core/Stats.cs
public class Resistance
{
    public Smashing Smashing { get; set; }
    public Lethal Lethal { get; set; }
    public Fire Fire { get; set; }
    public Cold Cold { get; set; }
    public Energy Energy { get; set; }
    public Negative Negative { get; set; }
    public Psionic Psionic { get; set; }
    public Toxic Toxic { get; set; }
}
```

### High-Level Algorithm

```
Defense/Resistance Calculation Process:

1. Aggregate Defense/Resistance Effects:
   - Collect all Defense/Resistance effects from:
     * Active powers (toggles, auto powers)
     * Set bonuses
     * Incarnate abilities
     * Temporary buffs
   - Group by damage type or position
   - Sum all values (defense and resistance stack additively)

2. Apply Defense Debuff Resistance (DDR):
   - DDR reduces the magnitude of defense debuffs
   - Formula: actual_debuff = base_debuff * (1 - DDR)
   - DDR does NOT have a cap (can exceed 100%)
   - Example: 100% DDR makes you immune to defense debuffs

3. Calculate Net Defense After Debuffs:
   - net_defense = base_defense - (debuffs * (1 - DDR))
   - Defense debuffs reduce your defense value
   - DDR protects against this reduction

4. Apply Defense Caps:
   - Most archetypes: No hard defense cap
   - Soft cap: 45% defense (enemy 50% base tohit - 45% = 5% hit chance)
   - Display shows both capped and uncapped values
   - Game rule: Defense has diminishing returns past soft cap

5. Apply Resistance Caps:
   - Resistance HAS archetype-specific caps
   - From Core/Base/Data_Classes/Archetype.cs:
     * Default: ResCap = 90% (0.9)
     * Different ATs have different caps:
       - Tankers/Brutes: 90% resistance cap
       - Scrappers/Stalkers: 75% resistance cap
       - Other ATs: 75% resistance cap
   - Formula: capped_res = min(total_res, archetype.ResCap)

6. Calculate Effective Hit Points (EHP):
   - Defense reduces chance to be hit
   - Resistance reduces damage taken when hit
   - Formula: EHP = HP / (1 - resistance) * (1 / (1 - defense/100))
   - Example: 2000 HP, 45% def, 75% res = 32,000 EHP

7. Store in Character.Totals and Character.TotalsCapped:
   - Totals: Uncapped values (for display/analysis)
   - TotalsCapped: Capped values (actual game values)
```

### Defense vs Resistance Interaction

**Defense** (avoidance):
- Reduces chance to be hit
- Each 1% defense = 1% less chance to be hit
- Soft cap at 45% (vs even-level enemies with 50% base tohit)
- No hard cap, but diminishing returns past soft cap
- Affects ALL damage types equally if positional
- More valuable at higher values (45% def >> 22.5% def)

**Resistance** (mitigation):
- Reduces damage taken when hit
- Each 1% resistance = 1% less damage
- Hard cap per archetype (75-90%)
- Linear scaling (50% res = 2x EHP, 75% res = 4x EHP)
- Type-specific (must match damage type)

**Together**:
- Defense reduces hit frequency
- Resistance reduces hit severity
- Combined: Multiplicative benefit
  - 45% def + 75% res = ~20x effective hit points
  - 45% def + 0% res = ~10x effective hit points
  - 0% def + 75% res = 4x effective hit points

### Defense Debuff Resistance (DDR)

**Purpose**: Protects defense from being debuffed

**How it works**:
```
Base defense: 45%
Defense debuff: -20%
DDR: 50%

Without DDR: 45% - 20% = 25% defense
With DDR: 45% - (20% * (1 - 0.5)) = 45% - 10% = 35% defense
```

**Key properties**:
- No cap (can exceed 100% for immunity)
- Critical for maintaining defense in combat
- Some sets have high DDR (e.g., Super Reflexes)
- Effect type: `DebuffResistanceDefense` (enum value 59)

```csharp
// From Core/Stats.cs
public class DebuffResistance
{
    public Defense Defense { get; set; }
    public Endurance Endurance { get; set; }
    public Perception Perception { get; set; }
    public Recharge Recharge { get; set; }
    public Recovery Recovery { get; set; }
    public Regeneration Regeneration { get; set; }
    public ToHit ToHit { get; set; }
}
```

### Archetype Caps

```csharp
// From Core/Base/Data_Classes/Archetype.cs
public class Archetype
{
    public float ResCap { get; set; }  // Default: 0.9 (90%)
    public float HPCap { get; set; }   // Default: 5000
    // ... other caps
}

// Applied in clsToonX.cs
TotalsCapped.Assign(Totals);
for (var index = 0; index < TotalsCapped.Res.Length; index++)
{
    TotalsCapped.Res[index] = Math.Min(TotalsCapped.Res[index], Archetype.ResCap);
}
```

**Typical Archetype Caps**:
- **Tankers/Brutes**: 90% resistance, highest HP cap
- **Scrappers/Stalkers**: 75% resistance
- **Defenders/Corruptors/Controllers**: 75% resistance
- **Blasters/Dominators**: 75% resistance
- **Defense**: No hard cap (soft cap at 45% for even-level enemies)

### Display and Tooltips

Defense/resistance display shows:
- Uncapped values (for build analysis)
- Capped values (actual in-game values)
- Per-type breakdown
- Archetype cap reference

```csharp
// From Forms/WindowMenuItems/frmTotalsV2.cs
resValueUncapped > resValue & resValue > 0
    ? $"{resValueUncapped:##0.##}% {FormatVectorType(typeof(Enums.eDamage), i)} resistance (capped at {MidsContext.Character.Archetype.ResCap * 100:##0.##}%)"
    : $"{resValue:##0.##}% {FormatVectorType(typeof(Enums.eDamage), i)} resistance ({atName} resistance cap: {MidsContext.Character.Archetype.ResCap * 100:##0.##}%)");
```

## Dependencies

**Depends On**:
- Spec 01: Power Effects Core (Effect aggregation)
- Spec 03: Power Buffs/Debuffs (Defense/resistance as buff effects)
- Spec 16: Archetype Stats (AT-specific caps)
- Spec 17: Archetype Modifiers (Defense/resistance scaling per AT)

**Used By**:
- Spec 19: Build Totals Display (Overall defense/resistance)
- Spec 20: Power Tooltips (Per-power defense/resistance grants)
- Spec 21: Enhancement Display (Defense/resistance enhancement values)
- Spec 32: Survivability Index (EHP calculations)

## Game Mechanics Context

**Why This Exists:**

Defense and resistance are the two primary damage mitigation mechanics in City of Heroes:

1. **Defense** represents the ability to avoid attacks entirely
2. **Resistance** represents the ability to absorb damage from attacks that hit
3. Together they define a character's survivability

**Historical Context:**

- **Launch (2004)**: Defense and resistance introduced as parallel mitigation systems
- **Issue 5 (2005)**: Defense made more valuable via "scaling damage resistance" (purple patch)
- **Issue 7 (2006)**: Defense soft cap (45%) becomes widely known meta
- **Issue 13 (2008)**: Defense debuff resistance added to some sets (Super Reflexes buff)
- **Going Rogue (2010)**: Resistance sets gain some defense options
- **Homecoming (2019+)**: Further balance between defense and resistance sets

**Why Two Systems:**

1. **Build diversity**: Some sets focus on defense, others on resistance, some on both
2. **Enemy variety**: Different enemies have different tohit and damage capabilities
3. **Counterplay**: Defense is countered by tohit buffs, resistance by unresistable damage
4. **Player choice**: Allows for different playstyles and build strategies

**Known Quirks:**

1. **Defense soft cap vs hard cap**: 45% defense is the "soft cap" (vs even-level enemies) but there's no hard cap. Defense past 45% helps vs higher-level enemies or tohit-buffed enemies.

2. **Positional vs Typed**: An attack checks BOTH positional and typed defense, using whichever is HIGHER. This is critical for build planning.
   - Example: Ranged Fire attack checks both "Ranged" and "Fire" defense
   - If you have 35% Ranged and 20% Fire, the attack uses 35% defense

3. **Resistance has diminishing returns**: Going from 0% to 50% res doubles your EHP. Going from 50% to 75% res doubles it again. But you can only reach 75-90% depending on AT.

4. **Defense debuff cascade**: Defense-based characters can die in a "cascade" if defense drops below soft cap:
   - 45% def = 10% of attacks hit
   - 35% def = 30% of attacks hit (3x more)
   - More hits = more defense debuffs = more hits = death
   - This is why DDR is critical for defense-based builds

5. **Tohit vs Accuracy**: Enemy tohit buffs directly counter defense. Enemy accuracy buffs do not. This matters for power selection (defense debuff resistance vs defense).

6. **Toxic defense**: City of Heroes originally didn't have toxic defense (Issue 1-24). Homecoming added it, but many powers still don't grant it, making toxic damage a weakness for defense-based builds.

7. **PvP differences**: In PvP, defense has diminishing returns and resistance is more valuable. This affects build choices for PvP-focused characters.

## Python Implementation Notes

**Proposed Architecture:**

```python
# backend/app/calculations/defense_resistance.py

from enum import Enum
from dataclasses import dataclass
from typing import Optional

class DamageType(Enum):
    """Damage types for typed defense/resistance"""
    SMASHING = "smashing"
    LETHAL = "lethal"
    FIRE = "fire"
    COLD = "cold"
    ENERGY = "energy"
    NEGATIVE = "negative"
    PSIONIC = "psionic"
    TOXIC = "toxic"

class PositionType(Enum):
    """Position types for positional defense"""
    MELEE = "melee"
    RANGED = "ranged"
    AOE = "aoe"

@dataclass
class DefenseValues:
    """
    Character defense values
    Maps to MidsReborn's Defense class in Core/Stats.cs
    """
    # Typed defense (vs damage type)
    smashing: float = 0.0
    lethal: float = 0.0
    fire: float = 0.0
    cold: float = 0.0
    energy: float = 0.0
    negative: float = 0.0
    psionic: float = 0.0
    toxic: float = 0.0

    # Positional defense (vs attack vector)
    melee: float = 0.0
    ranged: float = 0.0
    aoe: float = 0.0

    def get_typed(self, damage_type: DamageType) -> float:
        """Get typed defense for a damage type"""
        return getattr(self, damage_type.value)

    def get_positional(self, position: PositionType) -> float:
        """Get positional defense for an attack vector"""
        return getattr(self, position.value)

    def get_effective(self, damage_type: DamageType, position: PositionType) -> float:
        """
        Get effective defense against an attack
        City of Heroes uses the HIGHER of typed or positional defense
        """
        typed = self.get_typed(damage_type)
        positional = self.get_positional(position)
        return max(typed, positional)

@dataclass
class ResistanceValues:
    """
    Character resistance values
    Maps to MidsReborn's Resistance class in Core/Stats.cs
    """
    smashing: float = 0.0
    lethal: float = 0.0
    fire: float = 0.0
    cold: float = 0.0
    energy: float = 0.0
    negative: float = 0.0
    psionic: float = 0.0
    toxic: float = 0.0

    def get(self, damage_type: DamageType) -> float:
        """Get resistance for a damage type"""
        return getattr(self, damage_type.value)

@dataclass
class DebuffResistanceValues:
    """
    Defense debuff resistance (DDR) and other debuff resistances
    Maps to MidsReborn's DebuffResistance class
    """
    defense: float = 0.0  # DDR - reduces defense debuffs
    endurance: float = 0.0  # Reduces endurance drain
    perception: float = 0.0  # Reduces perception debuffs
    recharge: float = 0.0  # Reduces recharge debuffs
    recovery: float = 0.0  # Reduces recovery debuffs
    regeneration: float = 0.0  # Reduces regeneration debuffs
    tohit: float = 0.0  # Reduces tohit debuffs

class DefenseResistanceCalculator:
    """
    Calculates defense and resistance values including debuffs and caps
    Maps to logic in clsToonX.cs and Statistics.cs
    """

    # Defense soft cap (45% vs even-level enemies)
    DEFENSE_SOFT_CAP = 0.45

    def __init__(self, archetype_resistance_cap: float = 0.9):
        """
        Initialize with archetype-specific caps

        Args:
            archetype_resistance_cap: Resistance cap (0.75-0.9 depending on AT)
        """
        self.resistance_cap = archetype_resistance_cap

    def aggregate_defense(self, effects: list) -> DefenseValues:
        """
        Aggregate defense effects into total defense values
        Defense stacks additively from all sources

        Args:
            effects: List of Effect objects with effect_type=DEFENSE

        Returns:
            DefenseValues with aggregated defense
        """
        defense = DefenseValues()

        for effect in effects:
            if effect.effect_type.value != "defense":
                continue

            # Add defense value to appropriate type
            damage_type = effect.aspect  # "smashing", "melee", etc.
            if hasattr(defense, damage_type):
                current = getattr(defense, damage_type)
                setattr(defense, damage_type, current + effect.magnitude)

        return defense

    def aggregate_resistance(self, effects: list) -> ResistanceValues:
        """
        Aggregate resistance effects into total resistance values
        Resistance stacks additively from all sources

        Args:
            effects: List of Effect objects with effect_type=RESISTANCE

        Returns:
            ResistanceValues with aggregated resistance
        """
        resistance = ResistanceValues()

        for effect in effects:
            if effect.effect_type.value != "resistance":
                continue

            damage_type = effect.aspect
            if hasattr(resistance, damage_type):
                current = getattr(resistance, damage_type)
                setattr(resistance, damage_type, current + effect.magnitude)

        return resistance

    def apply_defense_debuffs(
        self,
        base_defense: DefenseValues,
        defense_debuffs: DefenseValues,
        ddr: float
    ) -> DefenseValues:
        """
        Apply defense debuffs reduced by defense debuff resistance (DDR)

        Args:
            base_defense: Base defense values
            defense_debuffs: Defense debuff magnitudes (negative values)
            ddr: Defense debuff resistance (0.0 to 1.0+, can exceed 1.0)

        Returns:
            Net defense after debuffs
        """
        net_defense = DefenseValues()

        # Apply DDR formula: net = base - (debuff * (1 - DDR))
        for damage_type in DamageType:
            attr = damage_type.value
            base = getattr(base_defense, attr)
            debuff = getattr(defense_debuffs, attr)
            # DDR reduces the debuff magnitude
            actual_debuff = debuff * (1 - ddr)
            setattr(net_defense, attr, base - actual_debuff)

        # Same for positional
        for position in PositionType:
            attr = position.value
            base = getattr(base_defense, attr)
            debuff = getattr(defense_debuffs, attr)
            actual_debuff = debuff * (1 - ddr)
            setattr(net_defense, attr, base - actual_debuff)

        return net_defense

    def apply_resistance_cap(self, resistance: ResistanceValues) -> ResistanceValues:
        """
        Apply archetype-specific resistance cap

        Args:
            resistance: Uncapped resistance values

        Returns:
            Capped resistance values
        """
        capped = ResistanceValues()

        for damage_type in DamageType:
            attr = damage_type.value
            value = getattr(resistance, attr)
            setattr(capped, attr, min(value, self.resistance_cap))

        return capped

    def calculate_effective_hp(
        self,
        base_hp: float,
        defense: float,
        resistance: float
    ) -> float:
        """
        Calculate effective hit points (EHP) given defense and resistance

        Args:
            base_hp: Base hit points
            defense: Defense value (0.0 to 1.0+)
            resistance: Resistance value (0.0 to cap)

        Returns:
            Effective hit points

        Formula:
            EHP = HP / (1 - resistance) / (chance_to_be_hit)

        Where chance_to_be_hit assumes 50% base tohit (even level enemy):
            chance_to_be_hit = max(0.05, 0.50 - defense)
        """
        # Minimum 5% hit chance (floor)
        chance_to_hit = max(0.05, 0.50 - defense)

        # Resistance reduces damage taken
        damage_multiplier = 1 - resistance

        # EHP formula
        if damage_multiplier <= 0:
            return float('inf')  # Immune to damage

        ehp = base_hp / damage_multiplier / chance_to_hit
        return ehp
```

**Implementation Priority:**

**HIGH** - Defense and resistance are the core survivability mechanics. Implement early.

**Key Implementation Steps:**

1. Define `DefenseValues` and `ResistanceValues` dataclasses
2. Implement `aggregate_defense()` and `aggregate_resistance()`
3. Implement `apply_defense_debuffs()` with DDR calculation
4. Implement `apply_resistance_cap()` with archetype caps
5. Implement `calculate_effective_hp()` for EHP calculation
6. Add defense/resistance to character totals calculation
7. Add display formatting for uncapped vs capped values

**Testing Strategy:**

- Unit tests for defense/resistance aggregation from multiple sources
- Unit tests for DDR calculation (0%, 50%, 100%, 150% DDR scenarios)
- Unit tests for resistance cap application per archetype
- Unit tests for EHP calculation with various def/res combinations
- Integration tests comparing to MidsReborn for known builds:
  - Super Reflexes Scrapper (high defense, low resistance)
  - Invulnerability Tanker (moderate defense, high resistance)
  - Willpower Brute (balanced defense and resistance)

**Edge Cases to Test:**

1. Defense over soft cap (45%+) vs higher level enemies
2. Resistance at cap (75-90%) and overflow
3. Defense debuff cascade with insufficient DDR
4. Positional vs typed defense priority
5. Combined defense + resistance EHP calculations

## References

- **Related Specs**:
  - Spec 01: Power Effects Core (Effect aggregation)
  - Spec 03: Power Buffs/Debuffs (Defense/resistance as buff/debuff effects)
  - Spec 16: Archetype Stats (AT caps)
  - Spec 17: Archetype Modifiers (AT scaling)
  - Spec 19: Build Totals Display (Overall defense/resistance display)
  - Spec 32: Survivability Index (EHP calculations)
- **MidsReborn Files**:
  - `Core/Stats.cs` - Defense/Resistance classes
  - `Core/Base/Data_Classes/Archetype.cs` - Archetype caps
  - `Core/Statistics.cs` - Display calculations
  - `clsToonX.cs` - Cap application
  - `Forms/WindowMenuItems/frmTotalsV2.cs` - Display formatting
- **Game Documentation**:
  - City of Heroes Wiki - "Defense", "Resistance", "Damage Mitigation"
  - Paragon Wiki - "Defense Mechanics", "Resistance Mechanics"
  - City of Data - Defense/resistance formulas
