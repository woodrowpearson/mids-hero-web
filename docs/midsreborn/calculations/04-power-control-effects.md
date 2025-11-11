# Power Control Effects (Mez/Status Effects)

## Overview
- **Purpose**: Control/mez effect calculations including magnitude vs protection, duration, stacking, and resistance mechanics
- **Used By**: Power effect calculations, build totals, status protection displays
- **Complexity**: High
- **Priority**: High
- **Status**: 🟡 Breadth Complete

## MidsReborn Implementation

### Primary Location
- **File**: `Core/Base/Data_Classes/Effect.cs`
- **Enums**: `Core/Enums.cs` - `eMez`, `eMezShort`, `eMezResist`
- **Related Files**:
  - `Core/Build.cs` - Mez enhancement and ED calculations
  - `Core/Stats.cs` - Status protection and resistance tracking

### Mez Types

The `eMez` enum in `Core/Enums.cs` defines all control/status effect types:

**Primary Control Effects**:
- `Confused` - Confuse/confusion
- `Held` - Hold (full control, no actions)
- `Immobilized` - Immobilize (cannot move)
- `Sleep` - Sleep (full control until damaged)
- `Stunned` - Stun (cannot act)
- `Terrorized` - Fear/terrorize (run away)

**Knockback/Movement**:
- `Knockback` - Knockback
- `Knockup` - Knockup (straight up)
- `Repel` - Continuous repel

**Special Status**:
- `Placate` - Placate (stealth from target)
- `Taunt` - Taunt (force aggro)
- `Untouchable` - Untouchable/phased
- `Teleport` - Forced teleport
- `ToggleDrop` - Force toggle drop
- `Afraid` - Afraid status
- `Avoid` - Avoid status
- `CombatPhase` - Combat phasing
- `OnlyAffectsSelf` - Self-only flag

### High-Level Algorithm

```
Mez Effect Application:
  1. Calculate total mez magnitude:
     - Base magnitude from power
     - Apply archetype scale factor
     - Apply enhancement bonuses (for duration-enhanceable mezzes)

  2. Check target protection:
     - Sum all active protection sources
     - Protection magnitude counters mez magnitude
     - If (mez_mag > protection_mag): apply mez

  3. Apply duration:
     - Base duration from power
     - Apply archetype duration scale
     - Apply duration enhancements (if mez type is duration-enhanceable)
     - Apply target's mez resistance (reduces duration)

  4. Handle stacking:
     - Multiple applications stack magnitude
     - Duration refreshes on new application
     - Stacking determined by effect.Stacking property

Duration-Enhanceable Mezzes:
  From Enums.MezDurationEnhanceable():
    - Confused
    - Held
    - Immobilized
    - Placate
    - Sleep
    - Stunned
    - Taunt
    - Terrorized
    - Untouchable

  NOT duration-enhanceable:
    - Knockback (magnitude-based distance)
    - Knockup (magnitude-based distance)
    - Repel (continuous)
    - ToggleDrop (instant)
    - Other special mezzes

Magnitude vs Protection:
  Applied = MezMagnitude > ProtectionMagnitude

  Example:
    - Controller Hold: Mag 3
    - Target protection: Mag 2
    - Result: Hold applied (3 > 2)

  Stacking:
    - Two Mag 2 holds = Mag 4 total
    - Can break through higher protection

Mez Resistance:
  Reduces duration, not magnitude

  Formula:
    ActualDuration = BaseDuration * (1 - MezResistance)

  Example:
    - Base Hold Duration: 10 seconds
    - Target has 50% hold resistance (0.5)
    - Actual Duration: 10 * (1 - 0.5) = 5 seconds
```

### Key Data Structures

```csharp
// From Core/Enums.cs
public enum eMez
{
    None,
    Confused,      // Index 1
    Held,          // Index 2
    Immobilized,   // Index 3
    Knockback,     // Index 4
    Knockup,       // Index 5
    OnlyAffectsSelf,
    Placate,       // Index 7
    Repel,         // Index 8
    Sleep,         // Index 9
    Stunned,       // Index 10
    Taunt,         // Index 11
    Terrorized,    // Index 12
    Untouchable,   // Index 13
    Teleport,      // Index 14
    ToggleDrop,    // Index 15
    Afraid,        // Index 16
    Avoid,         // Index 17
    CombatPhase    // Index 18
}

public enum eMezResist
{
    None,
    All,
    Confused,
    Held,
    Immobilized,
    Knockback,
    Knockup,
    Placate,
    Repel,
    Sleep,
    Stunned,
    Taunt,
    Terrorized,
    Teleport
}

// Status protection and resistance arrays
public class clsTotalV20
{
    public float[] Mez;              // Current mez values
    public float[] MezRes;           // Mez resistance
    public float[] StatusProtection; // Protection magnitudes
    public float[] StatusResistance; // Additional resistance
}
```

### Effect Properties

```csharp
// From Core/Base/Data_Classes/Effect.cs
public class Effect : IEffect
{
    // For Mez effects:
    public Enums.eEffectType EffectType;  // Must be Mez or MezResist
    public Enums.eMez MezType;            // Which mez type
    public float nMagnitude;              // Base magnitude
    public float nDuration;               // Base duration
    public float Scale;                   // AT scaling factor
    public Enums.eStacking Stacking;      // Does it stack?

    // Calculated values:
    public float Mag => AttribType switch
    {
        Magnitude => Scale * nMagnitude * DatabaseAPI.GetModifier(this),
        Duration => nMagnitude,
        Expression => Parse(this, ExpressionType.Magnitude, out _),
        _ => Scale * nMagnitude
    };
}
```

### Knockback Special Handling

Knockback and Knockup are distance-based, not duration-based:

```csharp
// From Effect.cs BuildEffectString()
if (MezType is eMez.Knockback or eMez.Knockup)
{
    // Display format shows magnitude as distance
    if (MidsContext.Config.CoDEffectFormat)
    {
        sMag = $"{Scale * nMagnitude:####0.####} x {ModifierTable}";
    }
    else
    {
        sMag = $"Mag {sMag}";
    }

    // Duration shown differently: "For X seconds:"
    sDuration = "For " + duration + " seconds: ";
}

// Magnitude determines knockback distance:
// Higher magnitude = greater distance
// Protection works same way: magnitude vs magnitude
```

### Enhancement and ED

From `Core/Build.cs`, mez enhancements are tracked separately:

```csharp
var eMezzes = Enum.GetValues(typeof(Enums.eMez)).Length;
var mezValues = new List<float>(eMezzes);
var mezSchedules = new List<Enums.eSchedule>(eMezzes);
var mezValuesAfterED = new List<float>(eMezzes);

// Initialize mez values and schedules
for (var tSub = 0; tSub < eMezzes; tSub++)
{
    mezValues[tSub] = 0;
    mezSchedules[tSub] = Enhancement.GetSchedule(Enums.eEnhance.Mez, tSub);
}

// Add mez enhancements from slots
if (effects[index2].Enhance.ID == (int)Enums.eEnhance.Mez)
{
    mezValues[effects[index2].Enhance.SubID] +=
        slot.Enhancement.GetEnhancementEffect(
            Enums.eEnhance.Mez,
            effects[index2].Enhance.SubID,
            1
        );
}

// Add mez from power effects
case Enums.eBuffMode.Mez:
    if (effect.IgnoreED)
    {
        mezValuesAfterED[(int)effect.MezType] += effect.BuffedMag;
    }
    else
    {
        mezValues[(int)effect.MezType] += effect.BuffedMag;
    }
    break;

// Apply ED to mez enhancements
for (var i = 0; i < eMezzes; i++)
{
    if (Math.Abs(mezValues[i]) > float.Epsilon)
    {
        var edSettings = BuildEDItem(mezValues[i], mezSchedules[i],
                                     statNames[i], mezValuesAfterED[i]);
        ret.Mez.Add(new EDWeightedItem
        {
            StatName = statNames[i],
            Value = mezValues[i],
            Schedule = mezSchedules[i],
            PostEDValue = mezValuesAfterED[i],
            EDStrength = edSettings.EDStrength,
            EDSettings = edSettings
        });
    }
}
```

### Dependencies

**Depends on:**
- Power Effects Core (Spec 01) - Base effect system
- Archetype Modifiers (Spec 16) - AT-specific mez scales
- Enhancement Diversification (Spec 13) - ED on mez duration enhancements

**Used by:**
- Power Calculations (Spec 02) - Individual power mez effects
- Build Totals (Spec 19) - Total status protection/resistance
- Combat Calculations - Determining if mezzes land

## Game Mechanics Context

**Why This Exists:**

Control effects (mezzes) are a fundamental game mechanic in City of Heroes, especially for Controller and Dominator archetypes. The magnitude vs protection system allows for:

1. **Scalable difficulty**: Bosses have higher protection, requiring stacked mezzes or team coordination
2. **Tactical depth**: Players must stack mezzes or reduce protection to control tough targets
3. **Build variety**: Status protection is crucial for melee characters in PvP
4. **Power balance**: Duration enhancements vs magnitude scaling creates build choices

**Historical Context:**

- **Launch (2004)**: Basic mag vs protection system established
  - Minions: Mag 1 protection
  - Lieutenants: Mag 2 protection
  - Bosses: Mag 3 protection (initially Mag 1)

- **Issue 3 (2004)**: Boss buff
  - Bosses upgraded to Mag 3 protection
  - Required Controllers to stack holds or team up
  - Major controversy at the time

- **Issue 5 (2005)**: Enhancement Diversification
  - Capped mez duration enhancements
  - Made perma-hold builds harder to achieve

- **Issue 7 (2006)**: PvP mez changes
  - Mez suppression introduced
  - Mez resistance added to most sets
  - Prevented permanent mezz locks in PvP

- **Issue 13 (2008)**: PvP 2.0
  - Major PvP mez overhaul
  - Reduced mez durations across the board
  - Increased mez resistance in PvP

**Known Quirks:**

1. **Protection vs Resistance**: Protection prevents application (magnitude check), resistance reduces duration. Both are needed for full mez protection.

2. **Stacking rules**: Some mezzes stack from same source, others don't. Effect.Stacking property determines this per-power.

3. **Knockback magnitude = distance**: Unlike other mezzes where magnitude is just strength, knockback magnitude directly determines knockback distance. Higher mag = further knockback.

4. **Sleep breaks on damage**: Sleep is unique - any damage breaks it immediately. This makes it weaker than other mezzes despite same magnitude requirements.

5. **Suppression not combat**: From Effect.cs, some effects show "Suppressed when Mezzed" - certain powers don't work while you're mezzed (toggle suppression).

6. **Confuse stacking**: Confused is special - it can stack with itself, making targets attack faster/harder under multiple confuses.

7. **Boss one-shot prevention**: Many boss mezzes are Mag 2 (one application) but players need Mag 3 to mez bosses, requiring stacking or team coordination.

## Python Implementation Notes

**Proposed Architecture:**

```python
# backend/app/calculations/mez.py

from enum import Enum
from dataclasses import dataclass
from typing import Optional

class MezType(Enum):
    """All mez/control effect types"""
    NONE = "none"
    CONFUSED = "confused"
    HELD = "held"
    IMMOBILIZED = "immobilized"
    KNOCKBACK = "knockback"
    KNOCKUP = "knockup"
    PLACATE = "placate"
    REPEL = "repel"
    SLEEP = "sleep"
    STUNNED = "stunned"
    TAUNT = "taunt"
    TERRORIZED = "terrorized"
    UNTOUCHABLE = "untouchable"
    TELEPORT = "teleport"
    TOGGLE_DROP = "toggle_drop"
    AFRAID = "afraid"
    AVOID = "avoid"
    COMBAT_PHASE = "combat_phase"
    ONLY_AFFECTS_SELF = "only_affects_self"

# Mezzes where duration can be enhanced
DURATION_ENHANCEABLE_MEZZES = {
    MezType.CONFUSED,
    MezType.HELD,
    MezType.IMMOBILIZED,
    MezType.PLACATE,
    MezType.SLEEP,
    MezType.STUNNED,
    MezType.TAUNT,
    MezType.TERRORIZED,
    MezType.UNTOUCHABLE
}

@dataclass
class MezEffect:
    """
    Represents a mez/control effect
    Extends base Effect with mez-specific properties
    """
    mez_type: MezType
    magnitude: float
    duration: float = 0.0
    scale: float = 1.0
    stacks: bool = False
    ignore_ed: bool = False

    def is_duration_enhanceable(self) -> bool:
        """Check if this mez type can have duration enhanced"""
        return self.mez_type in DURATION_ENHANCEABLE_MEZZES

    def scaled_magnitude(self, at_scale: float = 1.0) -> float:
        """
        Calculate final magnitude with archetype scaling

        Args:
            at_scale: Archetype's mez scale modifier

        Returns:
            Final magnitude value
        """
        return self.magnitude * self.scale * at_scale

    def effective_duration(
        self,
        at_duration_scale: float = 1.0,
        duration_enhancement: float = 0.0,
        target_resistance: float = 0.0
    ) -> float:
        """
        Calculate effective duration after all modifiers

        Args:
            at_duration_scale: Archetype's duration scale
            duration_enhancement: Total duration enhancement bonus (e.g., 0.95 for 95%)
            target_resistance: Target's mez resistance (0.0 to 1.0)

        Returns:
            Effective duration in seconds
        """
        # Base duration with AT scale
        base = self.duration * at_duration_scale

        # Apply duration enhancement (only if mez type allows it)
        if self.is_duration_enhanceable():
            base = base * (1.0 + duration_enhancement)

        # Apply target resistance (reduces duration)
        final = base * (1.0 - target_resistance)

        return max(0.0, final)

@dataclass
class MezProtection:
    """
    Status protection values (magnitude-based)
    Protection prevents mez from being applied
    """
    confused: float = 0.0
    held: float = 0.0
    immobilized: float = 0.0
    knockback: float = 0.0
    knockup: float = 0.0
    sleep: float = 0.0
    stunned: float = 0.0
    terrorized: float = 0.0
    # ... other mez types

    def get_protection(self, mez_type: MezType) -> float:
        """Get protection value for specific mez type"""
        protection_map = {
            MezType.CONFUSED: self.confused,
            MezType.HELD: self.held,
            MezType.IMMOBILIZED: self.immobilized,
            MezType.KNOCKBACK: self.knockback,
            MezType.KNOCKUP: self.knockup,
            MezType.SLEEP: self.sleep,
            MezType.STUNNED: self.stunned,
            MezType.TERRORIZED: self.terrorized,
        }
        return protection_map.get(mez_type, 0.0)

@dataclass
class MezResistance:
    """
    Status resistance values (percentage-based)
    Resistance reduces duration, not magnitude
    """
    confused: float = 0.0
    held: float = 0.0
    immobilized: float = 0.0
    knockback: float = 0.0
    knockup: float = 0.0
    sleep: float = 0.0
    stunned: float = 0.0
    terrorized: float = 0.0
    # ... other mez types

    def get_resistance(self, mez_type: MezType) -> float:
        """Get resistance value for specific mez type (0.0 to 1.0)"""
        resistance_map = {
            MezType.CONFUSED: self.confused,
            MezType.HELD: self.held,
            MezType.IMMOBILIZED: self.immobilized,
            MezType.KNOCKBACK: self.knockback,
            MezType.KNOCKUP: self.knockup,
            MezType.SLEEP: self.sleep,
            MezType.STUNNED: self.stunned,
            MezType.TERRORIZED: self.terrorized,
        }
        return resistance_map.get(mez_type, 0.0)

class MezCalculator:
    """Calculate mez application and duration"""

    def applies(
        self,
        mez: MezEffect,
        protection: MezProtection,
        at_scale: float = 1.0
    ) -> bool:
        """
        Check if mez magnitude overcomes protection

        Args:
            mez: The mez effect being applied
            protection: Target's status protection
            at_scale: Caster's archetype mez scale

        Returns:
            True if mez will be applied
        """
        mez_mag = mez.scaled_magnitude(at_scale)
        prot_mag = protection.get_protection(mez.mez_type)

        return mez_mag > prot_mag

    def calculate_duration(
        self,
        mez: MezEffect,
        resistance: MezResistance,
        at_duration_scale: float = 1.0,
        duration_enhancement: float = 0.0
    ) -> float:
        """
        Calculate final mez duration

        Args:
            mez: The mez effect
            resistance: Target's mez resistance
            at_duration_scale: Caster's AT duration scale
            duration_enhancement: Total duration enhancement

        Returns:
            Final duration in seconds
        """
        target_res = resistance.get_resistance(mez.mez_type)

        return mez.effective_duration(
            at_duration_scale=at_duration_scale,
            duration_enhancement=duration_enhancement,
            target_resistance=target_res
        )

    def stack_magnitude(self, mezzes: list[MezEffect]) -> dict[MezType, float]:
        """
        Stack mez magnitudes for same type

        Args:
            mezzes: List of active mez effects

        Returns:
            Dict mapping MezType to total stacked magnitude
        """
        stacked = {}

        for mez in mezzes:
            if mez.stacks:
                if mez.mez_type not in stacked:
                    stacked[mez.mez_type] = 0.0
                stacked[mez.mez_type] += mez.magnitude

        return stacked

class KnockbackCalculator:
    """Special handling for knockback/knockup distance calculations"""

    @staticmethod
    def calculate_knockback_distance(magnitude: float) -> float:
        """
        Calculate knockback distance from magnitude

        In CoH, knockback magnitude directly determines distance.
        Exact formula may need refinement based on game data.

        Args:
            magnitude: Knockback magnitude value

        Returns:
            Approximate knockback distance in game units
        """
        # TODO: Verify exact formula from game data
        # This is a placeholder - actual game uses more complex formula
        return magnitude * 10.0  # Rough approximation

    @staticmethod
    def knockback_to_knockdown(kb_magnitude: float, kb_protection: float) -> bool:
        """
        Check if knockback is reduced to knockdown

        In CoH, some KB protection doesn't prevent KB entirely,
        but reduces it to knockdown (minimal animation, no distance)

        Args:
            kb_magnitude: Incoming knockback magnitude
            kb_protection: Target's KB protection magnitude

        Returns:
            True if KB becomes knockdown (protection partial but not total)
        """
        # If protection is negative (knockdown enhancement)
        # or protection is very close to magnitude
        # knockback becomes knockdown
        return (kb_protection < 0) or (
            kb_protection > 0 and
            kb_protection < kb_magnitude and
            kb_magnitude - kb_protection < 1.0
        )
```

**Implementation Priority:**

**HIGH** - Critical for power calculations involving control sets. Controllers, Dominators, and many defender/corruptor sets rely heavily on mez mechanics.

**Key Implementation Steps:**

1. Define MezType enum with all 18+ mez types
2. Create DURATION_ENHANCEABLE_MEZZES constant set
3. Implement MezEffect dataclass with magnitude/duration calculations
4. Implement MezProtection and MezResistance dataclasses
5. Create MezCalculator.applies() for mag vs protection checks
6. Create MezCalculator.calculate_duration() for final duration
7. Implement stacking logic for multiple mez applications
8. Add KnockbackCalculator for KB-specific distance calculations
9. Integrate with Enhancement Diversification for duration caps

**Testing Strategy:**

- Unit tests for each mez type's duration enhancability
- Test magnitude vs protection calculations (at breakpoints)
- Test duration with resistance (0%, 50%, 95% resistance)
- Test stacking (multiple applications of same mez)
- Compare knockback distance calculations to known values
- Integration test: Controller hold vs Boss (Mag 3 vs Mag 3 protection)
- Integration test: Duration enhancements with ED caps

**Edge Cases to Handle:**

1. **Sleep special case**: Breaks on damage (may need separate handling)
2. **Knockback to knockdown**: Partial protection reduces KB to knockdown
3. **Confuse self-stacking**: Confuse stacks from same source unlike other mezzes
4. **Purple patch**: Higher-level targets have mez resistance (level difference)
5. **PvP suppression**: Different rules in PvP (may defer to separate spec)

## References

- **Related Specs**:
  - Spec 01 (Power Effects Core) - Base effect system
  - Spec 13 (Enhancement Diversification) - ED on mez duration
  - Spec 16 (Archetype Modifiers) - AT mez scales
  - Spec 19 (Build Totals) - Status protection totals
- **MidsReborn Files**:
  - `Core/Enums.cs` - Mez enums and MezDurationEnhanceable()
  - `Core/Base/Data_Classes/Effect.cs` - Mez effect properties
  - `Core/Build.cs` - Mez enhancement calculations
  - `Core/Stats.cs` - Status protection/resistance tracking
- **Game Documentation**:
  - Paragon Wiki - "Status Effects", "Mezzing"
  - Homecoming Wiki - "Crowd Control", "Status Protection"
