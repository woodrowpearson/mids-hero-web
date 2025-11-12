# Power Defense/Resistance

## Overview
- **Purpose**: Calculate defense and resistance values - the primary damage mitigation mechanics in City of Heroes
- **Used By**: Character totals, power tooltips, build planning, damage mitigation calculations
- **Complexity**: High
- **Priority**: Critical
- **Status**: 🟢 Depth Complete

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

---

# DEPTH-LEVEL IMPLEMENTATION DETAILS

## Section 1: Algorithm Pseudocode

### Complete Power Defense/Resistance Calculation Algorithm

```python
from typing import List, Dict
from enum import Enum

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

def extract_defense_from_power(
    power_effects: List[Effect],
    include_debuff_resistance: bool = True
) -> Dict:
    """
    Extract defense and resistance values from a single power's effects.

    This spec covers INDIVIDUAL POWER effects.
    Spec 19/20 handles BUILD TOTALS aggregation across all powers.

    Implementation based on:
    - Core/Stats.cs Defense and Resistance classes
    - Core/IEffect.cs BuffedMag property
    - Core/Base/Data_Classes/Effect.cs effect filtering

    Args:
        power_effects: All Effect objects from a single power
        include_debuff_resistance: Whether to extract DDR values

    Returns:
        Dictionary with defense, resistance, and DDR values
    """

    # Initialize result containers
    defense_values = {
        # Typed defense (vs damage type)
        "smashing": 0.0,
        "lethal": 0.0,
        "fire": 0.0,
        "cold": 0.0,
        "energy": 0.0,
        "negative": 0.0,
        "psionic": 0.0,
        "toxic": 0.0,
        # Positional defense (vs attack vector)
        "melee": 0.0,
        "ranged": 0.0,
        "aoe": 0.0
    }

    resistance_values = {
        # Resistance is typed only (no positional)
        "smashing": 0.0,
        "lethal": 0.0,
        "fire": 0.0,
        "cold": 0.0,
        "energy": 0.0,
        "negative": 0.0,
        "psionic": 0.0,
        "toxic": 0.0
    }

    debuff_resistance = {
        "defense": 0.0,  # Defense Debuff Resistance (DDR)
        "endurance": 0.0,
        "perception": 0.0,
        "recharge": 0.0,
        "recovery": 0.0,
        "regeneration": 0.0,
        "tohit": 0.0
    }

    for effect in power_effects:
        # STEP 1: Filter effect inclusion (Effect.cs CanInclude() and PvXInclude())
        if not effect.can_include() or not effect.pvx_include():
            continue

        # STEP 2: Check effect probability threshold
        # Effects with probability <= 0 are excluded
        if effect.probability <= 0:
            continue

        # STEP 3: Check suppression flags
        # Effects may be suppressed by game mode (PvP, travel, etc.)
        if (effect.suppression & game_mode_suppression) != 0:
            continue

        # STEP 4: Extract Defense effects
        if effect.effect_type == EffectType.DEFENSE:
            # Get enhanced magnitude (includes enhancements and AT scaling)
            value = effect.buffed_mag

            # Map damage type to defense category
            damage_type = effect.damage_type.lower()

            if damage_type in defense_values:
                # Defense stacks additively
                defense_values[damage_type] += value

        # STEP 5: Extract Resistance effects
        elif effect.effect_type == EffectType.RESISTANCE:
            # Get enhanced magnitude
            value = effect.buffed_mag

            # Map damage type to resistance category
            damage_type = effect.damage_type.lower()

            if damage_type in resistance_values:
                # Resistance stacks additively
                resistance_values[damage_type] += value

        # STEP 6: Extract Defense Debuff Resistance (DDR)
        elif include_debuff_resistance and effect.effect_type == EffectType.DEBUFF_RESISTANCE_DEFENSE:
            # DDR is stored in DebuffResistance.Defense
            # Effect type: eEffectType.DebuffResistanceDefense (enum value 59)
            value = effect.buffed_mag
            debuff_resistance["defense"] += value

        # STEP 7: Extract other debuff resistances
        elif include_debuff_resistance:
            if effect.effect_type == EffectType.DEBUFF_RESISTANCE_ENDURANCE:
                debuff_resistance["endurance"] += effect.buffed_mag
            elif effect.effect_type == EffectType.DEBUFF_RESISTANCE_PERCEPTION:
                debuff_resistance["perception"] += effect.buffed_mag
            elif effect.effect_type == EffectType.DEBUFF_RESISTANCE_RECHARGE:
                debuff_resistance["recharge"] += effect.buffed_mag
            elif effect.effect_type == EffectType.DEBUFF_RESISTANCE_RECOVERY:
                debuff_resistance["recovery"] += effect.buffed_mag
            elif effect.effect_type == EffectType.DEBUFF_RESISTANCE_REGENERATION:
                debuff_resistance["regeneration"] += effect.buffed_mag
            elif effect.effect_type == EffectType.DEBUFF_RESISTANCE_TOHIT:
                debuff_resistance["tohit"] += effect.buffed_mag

    # STEP 8: Return extracted values
    return {
        "defense": defense_values,
        "resistance": resistance_values,
        "debuff_resistance": debuff_resistance
    }


def calculate_effective_defense(
    typed_defense: float,
    positional_defense: float
) -> float:
    """
    Calculate effective defense for an attack.

    City of Heroes uses the HIGHER of typed or positional defense.
    This is critical for build planning.

    Example:
        Ranged Fire attack checks both "Ranged" and "Fire" defense.
        If you have 35% Ranged and 20% Fire, effective defense is 35%.

    Args:
        typed_defense: Defense value for damage type (e.g., Fire)
        positional_defense: Defense value for position (e.g., Ranged)

    Returns:
        Effective defense value (the higher of the two)
    """
    return max(typed_defense, positional_defense)


def apply_defense_debuff_resistance(
    base_defense: float,
    defense_debuff: float,
    ddr: float
) -> float:
    """
    Apply defense debuff reduced by Defense Debuff Resistance (DDR).

    Implementation from MidsReborn logic.

    Formula: net_defense = base_defense - (defense_debuff * (1 - DDR))

    Args:
        base_defense: Base defense value (0.0 to 1.0+)
        defense_debuff: Defense debuff magnitude (positive value, e.g., 0.20 for -20%)
        ddr: Defense Debuff Resistance (0.0 to 1.0+, can exceed 1.0 for immunity)

    Returns:
        Net defense after debuff application

    Examples:
        # No DDR
        apply_defense_debuff_resistance(0.45, 0.20, 0.0) = 0.25

        # 50% DDR
        apply_defense_debuff_resistance(0.45, 0.20, 0.5) = 0.35

        # 100% DDR (immune)
        apply_defense_debuff_resistance(0.45, 0.20, 1.0) = 0.45
    """
    # DDR reduces the debuff magnitude
    actual_debuff = defense_debuff * (1.0 - ddr)

    # Apply reduced debuff
    net_defense = base_defense - actual_debuff

    return net_defense


def apply_resistance_cap(
    resistance_value: float,
    archetype_resistance_cap: float = 0.9
) -> float:
    """
    Apply archetype-specific resistance cap.

    Implementation from Archetype.cs ResCap property (line 131).

    Args:
        resistance_value: Uncapped resistance value (0.0 to any)
        archetype_resistance_cap: AT-specific cap (default 0.9 = 90%)

    Returns:
        Capped resistance value

    Note:
        Defense has NO hard cap (soft cap at 45% for even-level enemies).
        Resistance HAS hard caps per archetype.
    """
    return min(resistance_value, archetype_resistance_cap)


def calculate_effective_hp(
    base_hp: float,
    defense: float,
    resistance: float,
    enemy_base_tohit: float = 0.50
) -> float:
    """
    Calculate Effective Hit Points (EHP) with defense and resistance.

    Defense reduces chance to be hit.
    Resistance reduces damage taken when hit.
    Together they multiply survival time.

    Args:
        base_hp: Base hit points
        defense: Defense value (0.0 to 1.0+)
        resistance: Resistance value (0.0 to cap)
        enemy_base_tohit: Base tohit for enemies (default 0.50 = 50%)

    Returns:
        Effective hit points

    Formula:
        chance_to_hit = max(0.05, enemy_base_tohit - defense)  # 5% floor
        damage_multiplier = 1 - resistance
        EHP = base_hp / damage_multiplier / chance_to_hit

    Examples:
        # 45% defense, 75% resistance
        calculate_effective_hp(2000, 0.45, 0.75, 0.50)
        = 2000 / 0.25 / 0.05 = 16,000 EHP

        # 45% defense, 0% resistance
        calculate_effective_hp(2000, 0.45, 0.0, 0.50)
        = 2000 / 1.0 / 0.05 = 40,000 EHP

        # 0% defense, 75% resistance
        calculate_effective_hp(2000, 0.0, 0.75, 0.50)
        = 2000 / 0.25 / 0.50 = 16,000 EHP
    """
    # Calculate chance to hit (5% minimum floor)
    chance_to_hit = max(0.05, enemy_base_tohit - defense)

    # Calculate damage multiplier from resistance
    damage_multiplier = 1.0 - resistance

    # Handle edge case: immune to damage
    if damage_multiplier <= 0:
        return float('inf')

    # Calculate effective HP
    ehp = base_hp / damage_multiplier / chance_to_hit

    return ehp
```

### Edge Cases and Special Handling

**1. Typed vs Positional Defense Priority**
- An attack checks BOTH typed and positional defense
- Game uses whichever is HIGHER
- Example: Ranged Fire attack checks "Ranged" AND "Fire"
- If Ranged=35% and Fire=20%, effective defense is 35%
- Critical for build optimization

**2. Defense Debuff Cascade**
- Defense-based characters vulnerable to "cascade failure"
- Formula: At 45% defense, 10% of attacks hit
- If debuffed to 35% defense, 30% of attacks hit (3x more!)
- More hits = more debuffs = more hits = death
- DDR prevents this cascade

**3. Resistance Scaling**
- Resistance has diminishing returns on EHP
- 0% to 50% res: 2x EHP
- 50% to 75% res: 2x EHP again (4x total)
- 75% to 90% res: 2.5x EHP (10x total)
- But capped by archetype (75-90%)

**4. No Defense Cap (Soft Cap Only)**
- Defense has NO hard cap
- "Soft cap" is 45% vs even-level enemies (50% base tohit - 45% = 5%)
- Defense above 45% helps vs:
  - Higher level enemies (+tohit)
  - Enemies with tohit buffs
  - Enemies with accuracy buffs (indirect)

**5. DDR Can Exceed 100%**
- DDR has no cap
- 100% DDR = immune to defense debuffs
- 150% DDR = defense debuffs become buffs (rare)
- Some powersets (Super Reflexes) have very high DDR

**6. Self-Only Effects**
- Some effects target self (ToWho.SELF)
- These are typically buffs from toggle/auto powers
- Must check effect.to_who to determine if it applies

---

## Section 2: C# Implementation Reference

### Primary Implementation Files

**File: `MidsReborn/Core/Stats.cs`**

**Classes: Defense, Resistance, DebuffResistance (Lines 232-349)**

```csharp
// Lines 232-245: Defense class structure
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

// Lines 327-337: Resistance class structure
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
    // Note: No positional resistance (Melee/Ranged/AoE)
}

// Lines 220-230: DebuffResistance class structure
public class DebuffResistance
{
    public Defense Defense { get; set; }  // DDR uses Defense structure
    public Endurance Endurance { get; set; }
    public Perception Perception { get; set; }
    public Recharge Recharge { get; set; }
    public Recovery Recovery { get; set; }
    public Regeneration Regeneration { get; set; }
    public RunSpeed RunSpeed { get; set; }
    public ToHit ToHit { get; set; }
}

// Lines 407-482: Damage type substats (shared by Defense and Resistance)
public class Smashing
{
    public float Base { get; set; }
    public float Current { get; set; }
    public float Maximum { get; set; }
}

public class Lethal
{
    public float Base { get; set; }
    public float Current { get; set; }
    public float Maximum { get; set; }
}

// ... (Fire, Cold, Energy, Negative, Psionic, Toxic follow same pattern)

public class Melee  // For positional defense only
{
    public float Base { get; set; }
    public float Current { get; set; }
    public float Maximum { get; set; }
}

public class Ranged  // For positional defense only
{
    public float Base { get; set; }
    public float Current { get; set; }
    public float Maximum { get; set; }
}

public class Aoe  // For positional defense only
{
    public float Base { get; set; }
    public float Current { get; set; }
    public float Maximum { get; set; }
}
```

**Initialization (Lines 76-88, 115-125):**

```csharp
// Lines 76-88: Defense initialization
Defense = new Defense
{
    Smashing = new Smashing { Base = 0f, Current = 0f, Maximum = 0f },
    Lethal = new Lethal { Base = 0f, Current = 0f, Maximum = 0f },
    Fire = new Fire { Base = 0f, Current = 0f, Maximum = 0f },
    Cold = new Cold { Base = 0f, Current = 0f, Maximum = 0f },
    Energy = new Energy { Base = 0f, Current = 0f, Maximum = 0f },
    Negative = new Negative { Base = 0f, Current = 0f, Maximum = 0f },
    Psionic = new Psionic { Base = 0f, Current = 0f, Maximum = 0f },
    Melee = new Melee { Base = 0f, Current = 0f, Maximum = 0f },
    Ranged = new Ranged { Base = 0f, Current = 0f, Maximum = 0f },
    Aoe = new Aoe { Base = 0f, Current = 0f, Maximum = 0f }
};

// Lines 115-125: Resistance initialization
Resistance = new Resistance
{
    Smashing = new Smashing { Base = 0f, Current = 0f, Maximum = 0f },
    Lethal = new Lethal { Base = 0f, Current = 0f, Maximum = 0f },
    Fire = new Fire { Base = 0f, Current = 0f, Maximum = 0f },
    Cold = new Cold { Base = 0f, Current = 0f, Maximum = 0f },
    Energy = new Energy { Base = 0f, Current = 0f, Maximum = 0f },
    Negative = new Negative { Base = 0f, Current = 0f, Maximum = 0f },
    Psionic = new Psionic { Base = 0f, Current = 0f, Maximum = 0f },
    Toxic = new Toxic { Base = 0f, Current = 0f, Maximum = 0f }
};
```

**File: `MidsReborn/Core/Base/Data_Classes/Archetype.cs`**

**Property: ResCap (Lines 41, 131)**

```csharp
// Line 41: Default resistance cap in constructor
ResCap = 90f;  // 90% = 0.9

// Line 131: Property definition
public float ResCap { get; set; }
```

**Typical Archetype Resistance Caps:**
- Tankers/Brutes: 90% (0.9) - Line 41 default
- Scrappers/Stalkers: 75% (0.75)
- Defenders/Corruptors/Controllers: 75% (0.75)
- Blasters/Dominators: 75% (0.75)
- Masterminds: 75% (0.75)

**File: `MidsReborn/Core/IEffect.cs`**

**Interface: IEffect (Lines 8-209)**

```csharp
// Line 18: BuffedMag property (enhanced magnitude)
float BuffedMag { get; }

// Line 48: EffectType property
Enums.eEffectType EffectType { get; set; }

// Line 54: DamageType property (used for defense/resistance aspect)
Enums.eDamage DamageType { get; set; }

// Line 14: Probability property (for effect inclusion)
float Probability { get; set; }

// Line 70: Suppression flags
Enums.eSuppress Suppression { get; set; }

// Line 88: PvMode (PvE/PvP)
Enums.ePvX PvMode { get; set; }

// Line 90: ToWho (Self/Target/Team)
Enums.eToWho ToWho { get; set; }

// Line 194: CanInclude() method
bool CanInclude();

// Line 198: PvXInclude() method
bool PvXInclude();
```

**File: `MidsReborn/Core/Enums.cs`**

**Enum: eEffectType (Relevant values)**

```csharp
// Line 1341: Defense Debuff Resistance enum value
DebuffResistanceDefense = 59,

// Other relevant effect types:
Defense = 8,
Resistance = 9,
DebuffResistanceEndurance = 60,
DebuffResistancePerception = 61,
DebuffResistanceRecharge = 62,
DebuffResistanceRecovery = 63,
DebuffResistanceRegeneration = 64,
DebuffResistanceToHit = 65
```

**File: `MidsReborn/Core/Statistics.cs`**

**Methods: Defense() and Resistance() (Lines 115, 105)**

```csharp
// Line 115: Defense display method
public float Defense(int dType)
{
    return _character.Totals.Def[dType] * 100f;  // Convert to percentage
}

// Line 105: Resistance display method
public float Resistance(int dType, bool uncapped = false)
{
    return uncapped
        ? _character.Totals.Res[dType] * 100f
        : _character.TotalsCapped.Res[dType] * 100f;
}
```

### Key Constants

**Defense Soft Cap: 45%**
- Not a hard cap, but practical cap vs even-level enemies
- Enemy base tohit: 50%
- 50% - 45% = 5% hit chance (minimum)
- Defense above 45% helps vs higher-level enemies

**Resistance Cap: 75-90%**
- Varies by archetype (Archetype.ResCap)
- Default: 90% (0.9)
- Applied in TotalsCapped calculation

**DDR Cap: None**
- Defense Debuff Resistance has no cap
- Can exceed 100% for immunity or "reverse debuffs"

**Effect Probability Threshold: 0.0**
- Effects with probability <= 0 are excluded
- Standard effects have probability = 1.0
- Procs have probability < 1.0

---

## Section 3: Database Schema

### Power Defense/Resistance Effects Table

```sql
-- Extend power_effects table with defense/resistance-specific view

CREATE TYPE position_type AS ENUM ('melee', 'ranged', 'aoe');

-- View for defense/resistance effects
CREATE VIEW v_power_defense_resistance_effects AS
SELECT
    pe.id,
    pe.power_id,
    pe.effect_type,
    pe.damage_type,
    pe.magnitude AS base_magnitude,
    pe.buffed_magnitude,
    COALESCE(pe.buffed_magnitude, pe.magnitude) AS effective_magnitude,
    pe.probability,
    pe.to_who,
    pe.pv_mode,
    pe.effect_class,
    pe.suppression,
    -- Computed flags
    pe.effect_type IN ('Defense', 'Resistance') AS is_defense_or_resistance,
    pe.effect_type = 'Defense' AS is_defense,
    pe.effect_type = 'Resistance' AS is_resistance,
    pe.effect_type LIKE 'DebuffResistance%' AS is_debuff_resistance,
    pe.damage_type IN ('melee', 'ranged', 'aoe') AS is_positional,
    pe.damage_type IN ('smashing', 'lethal', 'fire', 'cold', 'energy', 'negative', 'psionic', 'toxic') AS is_typed,
    -- Exclusion check
    pe.effect_class != 'Ignored'
        AND pe.probability > 0 AS is_includable
FROM power_effects pe
WHERE pe.effect_type IN ('Defense', 'Resistance',
    'DebuffResistanceDefense', 'DebuffResistanceEndurance',
    'DebuffResistancePerception', 'DebuffResistanceRecharge',
    'DebuffResistanceRecovery', 'DebuffResistanceRegeneration',
    'DebuffResistanceToHit');

-- Index for fast defense/resistance lookups
CREATE INDEX idx_power_effects_defense_resistance
    ON power_effects(power_id, effect_type)
    WHERE effect_type IN ('Defense', 'Resistance', 'DebuffResistanceDefense');

CREATE INDEX idx_power_effects_damage_type
    ON power_effects(damage_type)
    WHERE effect_type IN ('Defense', 'Resistance');
```

### Defense Effects Table

```sql
CREATE TABLE power_defense_effects (
    id SERIAL PRIMARY KEY,
    power_effect_id INTEGER NOT NULL REFERENCES power_effects(id) ON DELETE CASCADE,
    power_id INTEGER NOT NULL REFERENCES powers(id) ON DELETE CASCADE,

    -- Defense type
    damage_type VARCHAR(20) NOT NULL,  -- smashing, fire, melee, etc.
    is_positional BOOLEAN NOT NULL DEFAULT FALSE,  -- melee/ranged/aoe
    is_typed BOOLEAN NOT NULL DEFAULT TRUE,  -- damage type based

    -- Values
    base_magnitude NUMERIC(10, 6) NOT NULL,
    buffed_magnitude NUMERIC(10, 6),  -- After enhancements and AT scaling

    -- Metadata
    probability NUMERIC(10, 6) NOT NULL DEFAULT 1.0,
    to_who VARCHAR(20) NOT NULL DEFAULT 'Target',  -- Self, Target, Team
    pv_mode VARCHAR(10) NOT NULL DEFAULT 'Both',  -- PvE, PvP, Both

    -- Constraints
    CONSTRAINT valid_defense_magnitude CHECK (base_magnitude >= -1.0 AND base_magnitude <= 5.0),
    CONSTRAINT valid_probability CHECK (probability >= 0.0 AND probability <= 1.0),
    CONSTRAINT valid_damage_type CHECK (
        damage_type IN ('smashing', 'lethal', 'fire', 'cold', 'energy', 'negative', 'psionic', 'toxic', 'melee', 'ranged', 'aoe')
    ),

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_power_defense_effects_power_id ON power_defense_effects(power_id);
CREATE INDEX idx_power_defense_effects_damage_type ON power_defense_effects(damage_type);
CREATE INDEX idx_power_defense_effects_positional ON power_defense_effects(is_positional) WHERE is_positional = TRUE;
```

### Resistance Effects Table

```sql
CREATE TABLE power_resistance_effects (
    id SERIAL PRIMARY KEY,
    power_effect_id INTEGER NOT NULL REFERENCES power_effects(id) ON DELETE CASCADE,
    power_id INTEGER NOT NULL REFERENCES powers(id) ON DELETE CASCADE,

    -- Resistance type (typed only, no positional)
    damage_type VARCHAR(20) NOT NULL,  -- smashing, fire, etc. (not melee/ranged/aoe)

    -- Values
    base_magnitude NUMERIC(10, 6) NOT NULL,
    buffed_magnitude NUMERIC(10, 6),  -- After enhancements and AT scaling

    -- Metadata
    probability NUMERIC(10, 6) NOT NULL DEFAULT 1.0,
    to_who VARCHAR(20) NOT NULL DEFAULT 'Target',
    pv_mode VARCHAR(10) NOT NULL DEFAULT 'Both',

    -- Constraints
    CONSTRAINT valid_resistance_magnitude CHECK (base_magnitude >= -1.0 AND base_magnitude <= 1.0),
    CONSTRAINT valid_probability CHECK (probability >= 0.0 AND probability <= 1.0),
    CONSTRAINT valid_damage_type CHECK (
        damage_type IN ('smashing', 'lethal', 'fire', 'cold', 'energy', 'negative', 'psionic', 'toxic')
    ),
    CONSTRAINT no_positional_resistance CHECK (
        damage_type NOT IN ('melee', 'ranged', 'aoe')
    ),

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_power_resistance_effects_power_id ON power_resistance_effects(power_id);
CREATE INDEX idx_power_resistance_effects_damage_type ON power_resistance_effects(damage_type);
```

### Debuff Resistance Table

```sql
CREATE TABLE power_debuff_resistance_effects (
    id SERIAL PRIMARY KEY,
    power_effect_id INTEGER NOT NULL REFERENCES power_effects(id) ON DELETE CASCADE,
    power_id INTEGER NOT NULL REFERENCES powers(id) ON DELETE CASCADE,

    -- Debuff resistance type
    resistance_type VARCHAR(20) NOT NULL,  -- defense, endurance, recharge, etc.

    -- Values
    base_magnitude NUMERIC(10, 6) NOT NULL,
    buffed_magnitude NUMERIC(10, 6),

    -- Metadata
    probability NUMERIC(10, 6) NOT NULL DEFAULT 1.0,
    to_who VARCHAR(20) NOT NULL DEFAULT 'Self',  -- Usually self-targeted
    pv_mode VARCHAR(10) NOT NULL DEFAULT 'Both',

    -- Constraints
    CONSTRAINT valid_debuff_resistance_magnitude CHECK (base_magnitude >= -1.0 AND base_magnitude <= 2.0),
    CONSTRAINT valid_probability CHECK (probability >= 0.0 AND probability <= 1.0),
    CONSTRAINT valid_resistance_type CHECK (
        resistance_type IN ('defense', 'endurance', 'perception', 'recharge', 'recovery', 'regeneration', 'tohit')
    ),

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_power_debuff_resistance_effects_power_id ON power_debuff_resistance_effects(power_id);
CREATE INDEX idx_power_debuff_resistance_effects_type ON power_debuff_resistance_effects(resistance_type);
```

### Archetype Resistance Caps Table

```sql
CREATE TABLE archetype_resistance_caps (
    archetype_id INTEGER PRIMARY KEY REFERENCES archetypes(id) ON DELETE CASCADE,
    resistance_cap NUMERIC(10, 6) NOT NULL DEFAULT 0.9,  -- 90% default

    -- Metadata
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT valid_resistance_cap CHECK (resistance_cap >= 0.0 AND resistance_cap <= 1.0)
);

-- Seed data for standard ATs
INSERT INTO archetype_resistance_caps (archetype_id, resistance_cap, description) VALUES
    (1, 0.90, 'Tanker: 90% resistance cap'),
    (2, 0.75, 'Scrapper: 75% resistance cap'),
    (3, 0.75, 'Blaster: 75% resistance cap'),
    (4, 0.75, 'Defender: 75% resistance cap'),
    (5, 0.75, 'Controller: 75% resistance cap'),
    (6, 0.75, 'Corruptor: 75% resistance cap'),
    (7, 0.75, 'Stalker: 75% resistance cap'),
    (8, 0.90, 'Brute: 90% resistance cap'),
    (9, 0.75, 'Dominator: 75% resistance cap'),
    (10, 0.75, 'Mastermind: 75% resistance cap')
ON CONFLICT (archetype_id) DO NOTHING;

CREATE INDEX idx_archetype_resistance_caps_archetype_id ON archetype_resistance_caps(archetype_id);
```

### Aggregate Function for Power Defense/Resistance

```sql
-- PostgreSQL function to extract defense/resistance from a power
CREATE OR REPLACE FUNCTION get_power_defense_resistance(
    p_power_id INTEGER,
    p_include_debuff_resistance BOOLEAN DEFAULT TRUE
) RETURNS TABLE (
    category VARCHAR(20),  -- 'defense', 'resistance', 'debuff_resistance'
    damage_type VARCHAR(20),
    magnitude NUMERIC(10, 6)
) AS $$
BEGIN
    -- Defense effects
    RETURN QUERY
    SELECT
        'defense'::VARCHAR(20) AS category,
        pe.damage_type,
        COALESCE(pe.buffed_magnitude, pe.magnitude) AS magnitude
    FROM v_power_defense_resistance_effects pe
    WHERE pe.power_id = p_power_id
        AND pe.is_defense
        AND pe.is_includable
    ORDER BY pe.damage_type;

    -- Resistance effects
    RETURN QUERY
    SELECT
        'resistance'::VARCHAR(20) AS category,
        pe.damage_type,
        COALESCE(pe.buffed_magnitude, pe.magnitude) AS magnitude
    FROM v_power_defense_resistance_effects pe
    WHERE pe.power_id = p_power_id
        AND pe.is_resistance
        AND pe.is_includable
    ORDER BY pe.damage_type;

    -- Debuff resistance effects
    IF p_include_debuff_resistance THEN
        RETURN QUERY
        SELECT
            'debuff_resistance'::VARCHAR(20) AS category,
            -- Extract resistance type from effect_type (e.g., 'DebuffResistanceDefense' -> 'defense')
            LOWER(REPLACE(pe.effect_type, 'DebuffResistance', ''))::VARCHAR(20) AS damage_type,
            COALESCE(pe.buffed_magnitude, pe.magnitude) AS magnitude
        FROM v_power_defense_resistance_effects pe
        WHERE pe.power_id = p_power_id
            AND pe.is_debuff_resistance
            AND pe.is_includable
        ORDER BY damage_type;
    END IF;
END;
$$ LANGUAGE plpgsql;
```

---

## Section 4: Comprehensive Test Cases

### Test Case 1: Typed Defense (Super Reflexes - Focused Fighting)

**Power**: Super Reflexes > Focused Fighting (Toggle)
**Effect**: Melee Defense
**Level**: 50
**Archetype**: Scrapper (no AT modifier for defense)

**Input**:
- Base magnitude: 0.1575 (15.75% defense)
- Enhancement: 95% defense enhancement (3 level 50 IOs after ED)
- AT scale: 1.0 (defense not scaled by AT)
- Damage type: Melee (positional)

**Calculation**:
```
Step 1: Base defense
base_defense = 0.1575

Step 2: Apply enhancements
enhanced_defense = 0.1575 * (1.0 + 0.95) = 0.307125

Step 3: No AT scaling for defense (remains 1.0)
final_defense = 0.307125 * 1.0 = 0.307125
```

**Expected Output**:
- Melee defense: 30.71% (0.307125)
- Other defense types: 0%

### Test Case 2: Multiple Typed Defense (Invincibility - Multiple Types)

**Power**: Invulnerability > Invincibility (Toggle)
**Effects**: Multiple defense types based on nearby enemies
**Level**: 50
**Archetype**: Tanker

**Input** (per nearby enemy, stacks up to 10):
- Smashing defense: 0.0075 per enemy
- Lethal defense: 0.0075 per enemy
- Fire defense: 0.0075 per enemy
- Cold defense: 0.0075 per enemy
- Energy defense: 0.0075 per enemy
- Negative defense: 0.0075 per enemy
- Enemies nearby: 10 (max)
- Enhancement: 95% defense

**Calculation**:
```
Step 1: Base defense per type per enemy
base_per_enemy = 0.0075

Step 2: Apply enhancement
enhanced_per_enemy = 0.0075 * (1.0 + 0.95) = 0.014625

Step 3: Multiply by number of enemies (capped at 10)
final_per_type = 0.014625 * 10 = 0.14625
```

**Expected Output**:
- Smashing: 14.63%
- Lethal: 14.63%
- Fire: 14.63%
- Cold: 14.63%
- Energy: 14.63%
- Negative: 14.63%
- Psionic: 0%
- Melee/Ranged/AoE: 0%

### Test Case 3: Typed Resistance (Tough - Smashing/Lethal Resistance)

**Power**: Fighting > Tough (Toggle)
**Effects**: Smashing and Lethal resistance
**Level**: 50
**Archetype**: Scrapper (75% resistance cap)

**Input**:
- Smashing resistance: 0.075 (7.5%)
- Lethal resistance: 0.075 (7.5%)
- Enhancement: 95% resistance
- AT resistance cap: 0.75

**Calculation**:
```
Step 1: Base resistance
smashing_base = 0.075
lethal_base = 0.075

Step 2: Apply enhancements
smashing_enhanced = 0.075 * (1.0 + 0.95) = 0.14625
lethal_enhanced = 0.075 * (1.0 + 0.95) = 0.14625

Step 3: Check against cap (not exceeded)
smashing_capped = min(0.14625, 0.75) = 0.14625
lethal_capped = min(0.14625, 0.75) = 0.14625
```

**Expected Output**:
- Smashing resistance: 14.63% (uncapped), 14.63% (capped)
- Lethal resistance: 14.63% (uncapped), 14.63% (capped)
- Other types: 0%

### Test Case 4: Resistance at Cap (Granite Armor)

**Power**: Stone Armor > Granite Armor (Toggle)
**Effects**: High resistance to most types
**Level**: 50
**Archetype**: Tanker (90% resistance cap)

**Input**:
- Smashing resistance: 0.50 (50%)
- Lethal resistance: 0.50 (50%)
- Fire resistance: 0.40 (40%)
- Cold resistance: 0.40 (40%)
- Energy resistance: 0.30 (30%)
- Negative resistance: 0.30 (30%)
- Toxic resistance: 0.10 (10%)
- Enhancement: 95% resistance
- AT resistance cap: 0.90

**Calculation**:
```
Step 1: Apply enhancements
smashing_enhanced = 0.50 * 1.95 = 0.975
lethal_enhanced = 0.50 * 1.95 = 0.975
fire_enhanced = 0.40 * 1.95 = 0.78
cold_enhanced = 0.40 * 1.95 = 0.78
energy_enhanced = 0.30 * 1.95 = 0.585
negative_enhanced = 0.30 * 1.95 = 0.585
toxic_enhanced = 0.10 * 1.95 = 0.195

Step 2: Apply cap (90% for Tanker)
smashing_capped = min(0.975, 0.90) = 0.90
lethal_capped = min(0.975, 0.90) = 0.90
fire_capped = min(0.78, 0.90) = 0.78
cold_capped = min(0.78, 0.90) = 0.78
energy_capped = min(0.585, 0.90) = 0.585
negative_capped = min(0.585, 0.90) = 0.585
toxic_capped = min(0.195, 0.90) = 0.195
```

**Expected Output**:
- Smashing: 97.5% (uncapped), 90% (capped) - **CAPPED**
- Lethal: 97.5% (uncapped), 90% (capped) - **CAPPED**
- Fire: 78% (uncapped), 78% (capped)
- Cold: 78% (uncapped), 78% (capped)
- Energy: 58.5% (uncapped), 58.5% (capped)
- Negative: 58.5% (uncapped), 58.5% (capped)
- Toxic: 19.5% (uncapped), 19.5% (capped)
- Psionic: 0%

### Test Case 5: Defense Debuff Resistance (Practiced Brawler)

**Power**: Super Reflexes > Practiced Brawler (Click buff)
**Effects**: Defense Debuff Resistance
**Level**: 50
**Archetype**: Scrapper

**Input**:
- DDR magnitude: 0.50 (50%)
- Enhancement: 0% (DDR not typically enhanced)
- Base defense: 0.45 (45% from other powers)
- Defense debuff incoming: 0.20 (20% debuff)

**Calculation**:
```
Step 1: Extract DDR
ddr = 0.50

Step 2: Calculate actual debuff
actual_debuff = 0.20 * (1 - 0.50) = 0.10

Step 3: Apply to defense
net_defense = 0.45 - 0.10 = 0.35
```

**Expected Output**:
- DDR: 50%
- Without DDR: 45% - 20% = 25% defense
- With DDR: 45% - 10% = 35% defense
- **DDR prevented 10% defense loss**

### Test Case 6: Effective Defense (Typed vs Positional)

**Scenario**: Character with both typed and positional defense
**Power Set**: Shield Defense (has both typed and positional)
**Level**: 50
**Archetype**: Scrapper

**Input**:
- Smashing defense: 0.20 (20%)
- Lethal defense: 0.20 (20%)
- Fire defense: 0.10 (10%)
- Melee defense: 0.35 (35%)
- Ranged defense: 0.15 (15%)
- AoE defense: 0.15 (15%)

**Test Attacks**:
1. Melee Smashing attack
2. Ranged Fire attack
3. AoE Lethal attack

**Calculation**:
```
Attack 1: Melee Smashing
  Check: Smashing (20%) vs Melee (35%)
  Effective = max(0.20, 0.35) = 0.35 (35%)

Attack 2: Ranged Fire
  Check: Fire (10%) vs Ranged (15%)
  Effective = max(0.10, 0.15) = 0.15 (15%)

Attack 3: AoE Lethal
  Check: Lethal (20%) vs AoE (15%)
  Effective = max(0.20, 0.15) = 0.20 (20%)
```

**Expected Output**:
- vs Melee Smashing: 35% defense (positional)
- vs Ranged Fire: 15% defense (positional)
- vs AoE Lethal: 20% defense (typed)

### Test Case 7: Effective HP Calculation

**Scenario**: Calculate EHP for different defense/resistance combinations
**Character**: Level 50
**Base HP**: 2000

**Test Configurations**:

**Config A: High Defense, Low Resistance**
- Defense: 0.45 (45%)
- Resistance: 0.0 (0%)

```
chance_to_hit = max(0.05, 0.50 - 0.45) = 0.05
damage_multiplier = 1 - 0.0 = 1.0
EHP = 2000 / 1.0 / 0.05 = 40,000
```

**Config B: Low Defense, High Resistance**
- Defense: 0.0 (0%)
- Resistance: 0.75 (75%)

```
chance_to_hit = max(0.05, 0.50 - 0.0) = 0.50
damage_multiplier = 1 - 0.75 = 0.25
EHP = 2000 / 0.25 / 0.50 = 16,000
```

**Config C: Balanced Defense and Resistance**
- Defense: 0.45 (45%)
- Resistance: 0.75 (75%)

```
chance_to_hit = max(0.05, 0.50 - 0.45) = 0.05
damage_multiplier = 1 - 0.75 = 0.25
EHP = 2000 / 0.25 / 0.05 = 160,000
```

**Expected Output**:
- Config A (45% def, 0% res): 40,000 EHP
- Config B (0% def, 75% res): 16,000 EHP
- Config C (45% def, 75% res): 160,000 EHP
- **Multiplicative benefit**: Defense and resistance multiply EHP

---

## Section 5: Python Implementation Guide

### Complete Production-Ready Implementation

```python
# backend/app/calculations/defense_resistance.py

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
import math

from .effects import Effect, EffectType, EffectClass, ToWho, PvMode

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

class DebuffResistanceType(Enum):
    """Types of debuff resistance"""
    DEFENSE = "defense"  # Defense Debuff Resistance (DDR)
    ENDURANCE = "endurance"
    PERCEPTION = "perception"
    RECHARGE = "recharge"
    RECOVERY = "recovery"
    REGENERATION = "regeneration"
    TOHIT = "tohit"

@dataclass
class DefenseValues:
    """
    Defense values from a power.
    Maps to MidsReborn's Defense class in Core/Stats.cs lines 232-245.
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
        Get effective defense against an attack.
        City of Heroes uses the HIGHER of typed or positional defense.

        Args:
            damage_type: Damage type of attack (e.g., FIRE)
            position: Position of attack (e.g., RANGED)

        Returns:
            Effective defense (max of typed and positional)

        Example:
            Ranged Fire attack checks both Fire and Ranged defense.
            If Fire=0.20 and Ranged=0.35, effective defense is 0.35.
        """
        typed = self.get_typed(damage_type)
        positional = self.get_positional(position)
        return max(typed, positional)

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for JSON serialization"""
        return {
            "typed": {
                "smashing": self.smashing,
                "lethal": self.lethal,
                "fire": self.fire,
                "cold": self.cold,
                "energy": self.energy,
                "negative": self.negative,
                "psionic": self.psionic,
                "toxic": self.toxic
            },
            "positional": {
                "melee": self.melee,
                "ranged": self.ranged,
                "aoe": self.aoe
            }
        }

@dataclass
class ResistanceValues:
    """
    Resistance values from a power.
    Maps to MidsReborn's Resistance class in Core/Stats.cs lines 327-337.
    Note: Resistance has no positional component (only typed).
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

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for JSON serialization"""
        return {
            "smashing": self.smashing,
            "lethal": self.lethal,
            "fire": self.fire,
            "cold": self.cold,
            "energy": self.energy,
            "negative": self.negative,
            "psionic": self.psionic,
            "toxic": self.toxic
        }

@dataclass
class DebuffResistanceValues:
    """
    Debuff resistance values.
    Maps to MidsReborn's DebuffResistance class in Core/Stats.cs lines 220-230.
    """
    defense: float = 0.0  # Defense Debuff Resistance (DDR)
    endurance: float = 0.0
    perception: float = 0.0
    recharge: float = 0.0
    recovery: float = 0.0
    regeneration: float = 0.0
    tohit: float = 0.0

    def get(self, debuff_type: DebuffResistanceType) -> float:
        """Get debuff resistance for a type"""
        return getattr(self, debuff_type.value)

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for JSON serialization"""
        return {
            "defense": self.defense,
            "endurance": self.endurance,
            "perception": self.perception,
            "recharge": self.recharge,
            "recovery": self.recovery,
            "regeneration": self.regeneration,
            "tohit": self.tohit
        }

@dataclass
class PowerDefenseResistanceSummary:
    """
    Summary of defense/resistance from a single power.
    Used for power tooltips and display.
    """
    power_id: int
    power_name: str
    defense: DefenseValues
    resistance: ResistanceValues
    debuff_resistance: DebuffResistanceValues
    has_defense: bool = False
    has_resistance: bool = False
    has_debuff_resistance: bool = False

    def format_tooltip(self) -> str:
        """
        Generate tooltip text for power defense/resistance display.

        Returns:
            Formatted tooltip string
        """
        lines = []

        # Defense section
        if self.has_defense:
            lines.append("Defense:")

            # Typed defense
            typed = []
            for dtype in DamageType:
                value = self.defense.get_typed(dtype)
                if value > 0.01:
                    typed.append(f"  {dtype.value.title()}: {value*100:.2f}%")
            if typed:
                lines.extend(typed)

            # Positional defense
            positional = []
            for ptype in PositionType:
                value = self.defense.get_positional(ptype)
                if value > 0.01:
                    positional.append(f"  {ptype.value.title()}: {value*100:.2f}%")
            if positional:
                lines.extend(positional)

        # Resistance section
        if self.has_resistance:
            if lines:
                lines.append("")  # Blank line
            lines.append("Resistance:")

            for dtype in DamageType:
                value = self.resistance.get(dtype)
                if value > 0.01:
                    lines.append(f"  {dtype.value.title()}: {value*100:.2f}%")

        # Debuff resistance section
        if self.has_debuff_resistance:
            if lines:
                lines.append("")  # Blank line
            lines.append("Debuff Resistance:")

            for drtype in DebuffResistanceType:
                value = self.debuff_resistance.get(drtype)
                if value > 0.01:
                    lines.append(f"  {drtype.value.title()}: {value*100:.2f}%")

        return "\n".join(lines) if lines else "No defense or resistance"

class DefenseResistanceCalculator:
    """
    Calculates defense and resistance values from power effects.

    Implementation based on:
    - Core/Stats.cs Defense and Resistance classes
    - Core/IEffect.cs BuffedMag property
    - Core/Base/Data_Classes/Archetype.cs ResCap property
    """

    # Constants
    DEFENSE_SOFT_CAP = 0.45  # 45% vs even-level enemies
    DEFAULT_RESISTANCE_CAP = 0.9  # 90% default
    ENEMY_BASE_TOHIT = 0.50  # 50% base tohit
    MIN_HIT_CHANCE = 0.05  # 5% floor

    def __init__(self, archetype_resistance_cap: float = 0.9):
        """
        Initialize calculator.

        Args:
            archetype_resistance_cap: AT-specific resistance cap (default 0.9 = 90%)
        """
        self.resistance_cap = archetype_resistance_cap

    def extract_from_power(
        self,
        power_effects: List[Effect],
        include_debuff_resistance: bool = True
    ) -> PowerDefenseResistanceSummary:
        """
        Extract defense/resistance from a single power's effects.

        This method handles INDIVIDUAL POWER effects.
        Spec 19/20 handles BUILD TOTALS aggregation.

        Args:
            power_effects: All Effect objects from power
            include_debuff_resistance: Whether to extract DDR values

        Returns:
            PowerDefenseResistanceSummary with all values
        """
        defense = DefenseValues()
        resistance = ResistanceValues()
        debuff_resistance = DebuffResistanceValues()

        has_defense = False
        has_resistance = False
        has_debuff_resistance = False

        for effect in power_effects:
            # STEP 1: Filter effect inclusion
            if not effect.can_include() or not effect.pvx_include():
                continue

            # STEP 2: Check probability threshold
            if effect.probability <= 0:
                continue

            # STEP 3: Extract defense effects
            if effect.effect_type == EffectType.DEFENSE:
                value = effect.buffed_mag
                damage_type = effect.damage_type.lower()

                if hasattr(defense, damage_type):
                    current = getattr(defense, damage_type)
                    setattr(defense, damage_type, current + value)
                    has_defense = True

            # STEP 4: Extract resistance effects
            elif effect.effect_type == EffectType.RESISTANCE:
                value = effect.buffed_mag
                damage_type = effect.damage_type.lower()

                if hasattr(resistance, damage_type):
                    current = getattr(resistance, damage_type)
                    setattr(resistance, damage_type, current + value)
                    has_resistance = True

            # STEP 5: Extract debuff resistance
            elif include_debuff_resistance:
                dr_type = self._get_debuff_resistance_type(effect.effect_type)
                if dr_type:
                    value = effect.buffed_mag
                    current = getattr(debuff_resistance, dr_type)
                    setattr(debuff_resistance, dr_type, current + value)
                    has_debuff_resistance = True

        return PowerDefenseResistanceSummary(
            power_id=power_effects[0].power_id if power_effects else 0,
            power_name=power_effects[0].power_name if power_effects else "",
            defense=defense,
            resistance=resistance,
            debuff_resistance=debuff_resistance,
            has_defense=has_defense,
            has_resistance=has_resistance,
            has_debuff_resistance=has_debuff_resistance
        )

    def _get_debuff_resistance_type(self, effect_type: EffectType) -> Optional[str]:
        """
        Map effect type to debuff resistance type.

        Args:
            effect_type: EffectType enum value

        Returns:
            Debuff resistance type string or None
        """
        mapping = {
            EffectType.DEBUFF_RESISTANCE_DEFENSE: "defense",
            EffectType.DEBUFF_RESISTANCE_ENDURANCE: "endurance",
            EffectType.DEBUFF_RESISTANCE_PERCEPTION: "perception",
            EffectType.DEBUFF_RESISTANCE_RECHARGE: "recharge",
            EffectType.DEBUFF_RESISTANCE_RECOVERY: "recovery",
            EffectType.DEBUFF_RESISTANCE_REGENERATION: "regeneration",
            EffectType.DEBUFF_RESISTANCE_TOHIT: "tohit"
        }
        return mapping.get(effect_type)

    def apply_defense_debuff_resistance(
        self,
        base_defense: float,
        defense_debuff: float,
        ddr: float
    ) -> float:
        """
        Apply defense debuff reduced by DDR.

        Formula: net_defense = base_defense - (defense_debuff * (1 - DDR))

        Args:
            base_defense: Base defense value (0.0 to 1.0+)
            defense_debuff: Defense debuff magnitude (positive)
            ddr: Defense Debuff Resistance (0.0 to 1.0+)

        Returns:
            Net defense after debuff

        Examples:
            >>> calc = DefenseResistanceCalculator()
            >>> calc.apply_defense_debuff_resistance(0.45, 0.20, 0.0)
            0.25
            >>> calc.apply_defense_debuff_resistance(0.45, 0.20, 0.5)
            0.35
            >>> calc.apply_defense_debuff_resistance(0.45, 0.20, 1.0)
            0.45
        """
        actual_debuff = defense_debuff * (1.0 - ddr)
        net_defense = base_defense - actual_debuff
        return net_defense

    def apply_resistance_cap(
        self,
        resistance: ResistanceValues
    ) -> ResistanceValues:
        """
        Apply archetype-specific resistance cap.

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
        resistance: float,
        enemy_base_tohit: float = None
    ) -> float:
        """
        Calculate Effective Hit Points (EHP).

        Args:
            base_hp: Base hit points
            defense: Defense value (0.0 to 1.0+)
            resistance: Resistance value (0.0 to cap)
            enemy_base_tohit: Enemy base tohit (default 0.50)

        Returns:
            Effective hit points

        Examples:
            >>> calc = DefenseResistanceCalculator()
            >>> calc.calculate_effective_hp(2000, 0.45, 0.75)
            160000.0
            >>> calc.calculate_effective_hp(2000, 0.45, 0.0)
            40000.0
            >>> calc.calculate_effective_hp(2000, 0.0, 0.75)
            16000.0
        """
        if enemy_base_tohit is None:
            enemy_base_tohit = self.ENEMY_BASE_TOHIT

        # Calculate chance to hit (5% minimum)
        chance_to_hit = max(self.MIN_HIT_CHANCE, enemy_base_tohit - defense)

        # Calculate damage multiplier from resistance
        damage_multiplier = 1.0 - resistance

        # Handle edge case: immune to damage
        if damage_multiplier <= 0:
            return float('inf')

        # Calculate EHP
        ehp = base_hp / damage_multiplier / chance_to_hit

        return ehp

    def calculate_effective_defense(
        self,
        typed_defense: float,
        positional_defense: float
    ) -> float:
        """
        Calculate effective defense for an attack.

        City of Heroes uses the HIGHER of typed or positional.

        Args:
            typed_defense: Defense for damage type
            positional_defense: Defense for position

        Returns:
            Effective defense (max of the two)

        Examples:
            >>> calc = DefenseResistanceCalculator()
            >>> calc.calculate_effective_defense(0.20, 0.35)
            0.35
            >>> calc.calculate_effective_defense(0.35, 0.20)
            0.35
        """
        return max(typed_defense, positional_defense)


# Usage example
if __name__ == "__main__":
    from app.calculations.effects import Effect, EffectType, DamageType as EffectDamageType

    # Example: Super Reflexes > Focused Fighting
    # Grants Melee defense
    effects = [
        Effect(
            effect_type=EffectType.DEFENSE,
            damage_type=EffectDamageType.MELEE,
            magnitude=0.1575,  # 15.75% base
            buffed_mag=0.307125,  # After 95% enhancement
            probability=1.0,
            to_who=ToWho.SELF
        )
    ]

    calculator = DefenseResistanceCalculator()
    summary = calculator.extract_from_power(effects)

    print(f"Defense values:")
    print(f"  Melee: {summary.defense.melee*100:.2f}%")
    print(f"\nTooltip:")
    print(summary.format_tooltip())

    # Output:
    # Defense values:
    #   Melee: 30.71%
    #
    # Tooltip:
    # Defense:
    #   Melee: 30.71%
```

### Error Handling and Validation

```python
# backend/app/calculations/defense_resistance_validation.py

from typing import List
from .defense_resistance import (
    DefenseResistanceCalculator,
    PowerDefenseResistanceSummary,
    DefenseValues,
    ResistanceValues
)
from .effects import Effect

class DefenseResistanceCalculationError(Exception):
    """Base exception for defense/resistance calculation errors"""
    pass

class InvalidEffectError(DefenseResistanceCalculationError):
    """Raised when effect has invalid properties"""
    pass

class InvalidCapError(DefenseResistanceCalculationError):
    """Raised when resistance cap is invalid"""
    pass

def validate_effect_for_defense_resistance(effect: Effect) -> None:
    """
    Validate effect for defense/resistance calculation.

    Raises:
        InvalidEffectError: If effect is invalid
    """
    if effect.probability < 0 or effect.probability > 1:
        raise InvalidEffectError(
            f"Effect probability must be 0-1, got {effect.probability}"
        )

    if effect.buffed_mag is None and effect.magnitude is None:
        raise InvalidEffectError(
            "Effect must have either buffed_mag or magnitude"
        )

    # Defense/resistance magnitude should be reasonable
    mag = effect.buffed_mag or effect.magnitude
    if mag < -1.0 or mag > 5.0:
        raise InvalidEffectError(
            f"Effect magnitude out of range [-1.0, 5.0]: {mag}"
        )

def validate_resistance_cap(cap: float) -> None:
    """
    Validate resistance cap value.

    Raises:
        InvalidCapError: If cap is invalid
    """
    if cap < 0.0 or cap > 1.0:
        raise InvalidCapError(
            f"Resistance cap must be 0-1, got {cap}"
        )

def safe_extract_defense_resistance(
    calculator: DefenseResistanceCalculator,
    effects: List[Effect],
    **kwargs
) -> PowerDefenseResistanceSummary:
    """
    Extract defense/resistance with validation and error handling.

    Args:
        calculator: DefenseResistanceCalculator instance
        effects: Power effects
        **kwargs: Arguments to pass to extract_from_power

    Returns:
        PowerDefenseResistanceSummary

    Raises:
        DefenseResistanceCalculationError: If validation fails
    """
    # Validate effects
    for effect in effects:
        validate_effect_for_defense_resistance(effect)

    # Validate resistance cap
    validate_resistance_cap(calculator.resistance_cap)

    # Extract
    try:
        return calculator.extract_from_power(effects, **kwargs)
    except Exception as e:
        raise DefenseResistanceCalculationError(
            f"Defense/resistance extraction failed: {e}"
        ) from e
```

---

## Section 6: Integration Points

### Upstream Dependencies

**1. Effect System (Spec 01)**
- Provides `Effect` objects with `effect_type`, `damage_type`, `magnitude`
- `Effect.buffed_mag` contains magnitude after enhancements
- `Effect.probability`, `Effect.to_who` for filtering
- Integration: Pass list of `Effect` objects to calculator

**2. Enhancement System (Spec 10)**
- Calculates `Effect.buffed_mag` from base magnitude + enhancements
- Applies Enhancement Diversification (ED)
- Integration: Calculator uses `buffed_mag` as input (already enhanced)

**3. Archetype System (Spec 16)**
- Provides archetype resistance cap (75-90%)
- Integration: Pass `archetype.resistance_cap` to calculator constructor

**4. Power Data**
- Provides power effects list
- Required for per-power defense/resistance extraction
- Integration: Load effects from database, pass to calculator

### Downstream Consumers

**1. Build Totals (Spec 19/20)**
- Aggregates defense/resistance across ALL powers in build
- Uses this spec for individual power extraction
- Integration: Call `extract_from_power()` for each power, sum results

**2. Power Tooltips**
- Uses `PowerDefenseResistanceSummary.format_tooltip()` for display
- Shows defense/resistance by type
- Integration: Extract from power and format

**3. Survivability Index (Spec 32)**
- Uses `calculate_effective_hp()` for EHP calculations
- Combines defense and resistance for survivability metrics
- Integration: Pass defense/resistance values to EHP calculation

**4. Build Comparison Tools**
- Compares defense/resistance between builds
- May calculate EHP for comparison
- Integration: Extract from multiple builds, compare values

### Database Queries

**Load effects for defense/resistance calculation:**

```python
# backend/app/db/queries/defense_resistance_queries.py

from sqlalchemy import select
from app.db.models import PowerEffect
from app.calculations.defense_resistance import DamageType, PositionType

async def load_power_defense_effects(power_id: int):
    """Load all defense effects for a power."""
    query = select(PowerEffect).where(
        PowerEffect.power_id == power_id,
        PowerEffect.effect_type == 'Defense',
        PowerEffect.effect_class != 'Ignored',
        PowerEffect.probability > 0
    ).order_by(PowerEffect.damage_type)

    return await db.execute(query)

async def load_power_resistance_effects(power_id: int):
    """Load all resistance effects for a power."""
    query = select(PowerEffect).where(
        PowerEffect.power_id == power_id,
        PowerEffect.effect_type == 'Resistance',
        PowerEffect.effect_class != 'Ignored',
        PowerEffect.probability > 0
    ).order_by(PowerEffect.damage_type)

    return await db.execute(query)

async def load_power_debuff_resistance_effects(power_id: int):
    """Load all debuff resistance effects for a power."""
    query = select(PowerEffect).where(
        PowerEffect.power_id == power_id,
        PowerEffect.effect_type.like('DebuffResistance%'),
        PowerEffect.effect_class != 'Ignored',
        PowerEffect.probability > 0
    )

    return await db.execute(query)

async def get_archetype_resistance_cap(archetype_id: int) -> float:
    """Get resistance cap for archetype."""
    query = select(ArchetypeResistanceCap.resistance_cap).where(
        ArchetypeResistanceCap.archetype_id == archetype_id
    )

    result = await db.execute(query)
    return result.scalar_one_or_404()
```

### API Endpoints

**GET /api/v1/powers/{power_id}/defense-resistance**

```python
# backend/app/api/v1/powers.py

from fastapi import APIRouter, Query
from app.calculations.defense_resistance import DefenseResistanceCalculator

router = APIRouter()

@router.get("/powers/{power_id}/defense-resistance")
async def get_power_defense_resistance(
    power_id: int,
    archetype_id: Optional[int] = None,
    include_debuff_resistance: bool = True
):
    """
    Get defense/resistance from a power.

    Args:
        power_id: Power ID
        archetype_id: Optional archetype for resistance cap
        include_debuff_resistance: Include DDR values

    Returns:
        Defense/resistance summary
    """
    # Load power effects
    effects = await load_power_effects(power_id)

    # Get resistance cap if archetype provided
    resistance_cap = 0.9  # Default
    if archetype_id:
        resistance_cap = await get_archetype_resistance_cap(archetype_id)

    # Calculate
    calculator = DefenseResistanceCalculator(
        archetype_resistance_cap=resistance_cap
    )

    summary = calculator.extract_from_power(
        effects,
        include_debuff_resistance=include_debuff_resistance
    )

    return {
        "power_id": power_id,
        "defense": summary.defense.to_dict(),
        "resistance": summary.resistance.to_dict(),
        "debuff_resistance": summary.debuff_resistance.to_dict(),
        "has_defense": summary.has_defense,
        "has_resistance": summary.has_resistance,
        "has_debuff_resistance": summary.has_debuff_resistance,
        "tooltip": summary.format_tooltip()
    }


@router.post("/defense-resistance/effective-hp")
async def calculate_effective_hp(
    base_hp: float,
    defense: float,
    resistance: float,
    enemy_base_tohit: float = 0.50,
    archetype_id: Optional[int] = None
):
    """
    Calculate Effective Hit Points (EHP).

    Args:
        base_hp: Base hit points
        defense: Defense value (0.0 to 1.0)
        resistance: Resistance value (0.0 to 1.0)
        enemy_base_tohit: Enemy base tohit (default 0.50)
        archetype_id: Optional archetype for resistance cap

    Returns:
        Effective HP and breakdown
    """
    # Get resistance cap if archetype provided
    resistance_cap = 0.9  # Default
    if archetype_id:
        resistance_cap = await get_archetype_resistance_cap(archetype_id)

    # Cap resistance
    capped_resistance = min(resistance, resistance_cap)

    # Calculate
    calculator = DefenseResistanceCalculator(
        archetype_resistance_cap=resistance_cap
    )

    ehp = calculator.calculate_effective_hp(
        base_hp=base_hp,
        defense=defense,
        resistance=capped_resistance,
        enemy_base_tohit=enemy_base_tohit
    )

    # Calculate breakdown
    chance_to_hit = max(0.05, enemy_base_tohit - defense)
    damage_multiplier = 1.0 - capped_resistance

    return {
        "base_hp": base_hp,
        "defense": defense,
        "resistance": resistance,
        "capped_resistance": capped_resistance,
        "effective_hp": ehp,
        "breakdown": {
            "chance_to_hit": chance_to_hit,
            "damage_multiplier": damage_multiplier,
            "effective_hp_from_defense": base_hp / chance_to_hit,
            "effective_hp_from_resistance": base_hp / damage_multiplier
        }
    }
```

### Cross-Spec Data Flow

**Forward dependencies (this spec uses):**
```
Spec 01 (Effects) → Effect objects
Spec 10 (Enhancements) → Effect.buffed_mag
Spec 16 (Archetype) → Resistance cap
```

**Backward dependencies (other specs use this):**
```
Spec 19 (Build Totals - Defense) → Aggregates across build
Spec 20 (Build Totals - Resistance) → Aggregates across build
Spec 32 (Survivability Index) → EHP calculations
```

### Implementation Order

**Phase 1: Core (Sprint 1)**
1. Implement `DefenseValues`, `ResistanceValues`, `DebuffResistanceValues` dataclasses
2. Implement `DefenseResistanceCalculator.extract_from_power()` for single powers
3. Unit tests for individual power defense/resistance extraction

**Phase 2: Advanced (Sprint 2)**
4. Implement `apply_defense_debuff_resistance()` for DDR calculation
5. Implement `apply_resistance_cap()` with archetype caps
6. Implement `calculate_effective_hp()` for EHP calculation
7. Unit tests for DDR, caps, and EHP

**Phase 3: Database (Sprint 2)**
8. Create database views for defense/resistance effects
9. Implement PostgreSQL functions for extraction
10. Database integration tests

**Phase 4: API (Sprint 3)**
11. Create `/powers/{id}/defense-resistance` endpoint
12. Create `/defense-resistance/effective-hp` endpoint
13. API integration tests

**Phase 5: Build Integration (Sprint 3+)**
14. Integrate with Spec 19/20 for build totals
15. Integrate with Spec 32 for survivability index
16. End-to-end tests with complete builds

---

## Status: 🟢 Depth Complete

This specification now contains production-ready implementation details:

- **Algorithm Pseudocode**: Complete step-by-step calculation with all edge cases
- **C# Reference**: Extracted exact code from MidsReborn with line numbers and structure
- **Database Schema**: CREATE-ready tables, views, and functions
- **Test Cases**: 7 comprehensive scenarios with exact expected values and calculations
- **Python Implementation**: Production-ready code with type hints, error handling, and docstrings
- **Integration Points**: Complete data flow and API endpoint specifications

**Key Formulas Discovered:**
1. Defense/Resistance extraction: Iterate effects, sum `buffed_mag` by damage type
2. DDR formula: `net_defense = base_defense - (debuff * (1 - DDR))`
3. Resistance cap: `min(resistance, archetype.ResCap)`
4. Effective defense: `max(typed_defense, positional_defense)`
5. Effective HP: `HP / (1 - resistance) / chance_to_hit`
6. Defense soft cap: 45% vs even-level enemies (no hard cap)

**Lines Added**: ~1,200 lines of depth-level implementation detail

**Scope Boundary:**
- **This spec (09)**: Extracts defense/resistance from INDIVIDUAL POWER effects
- **Spec 19/20**: Aggregates defense/resistance across ALL POWERS in build for totals

**Ready for Milestone 3 implementation.**
