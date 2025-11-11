# Power Buffs/Debuffs

## Overview
- **Purpose**: Calculate buff and debuff effects that modify character attributes (damage, defense, resistance, accuracy, recharge, etc.) - includes magnitude, duration, target determination, and stacking behavior
- **Used By**: Build totals, power calculations, set bonuses, archetype inherents
- **Complexity**: Medium
- **Priority**: Critical
- **Status**: 🟡 Breadth Complete

## MidsReborn Implementation

### Primary Location
- **File**: `Core/Base/Data_Classes/Effect.cs`
- **Class**: `Effect` (implements `IEffect` interface)
- **Related Files**:
  - `Core/GroupedFx.cs` - Buff/debuff aggregation and stacking
  - `Core/Enums.cs` - `eEffectType` enumeration (defines all buff/debuff types)
  - `Core/PowerEntry.cs` - Applies buffs/debuffs to power calculations

### Buff vs Debuff Distinction

**In City of Heroes, "buff" and "debuff" are not separate effect types** - they are the same effects with different targets and magnitudes:

- **Buff**: Positive effect applied to self or allies (ToWho = Self, Team)
- **Debuff**: Negative effect applied to enemies (ToWho = Target)
- **Magnitude Sign**: Damage effects use negative magnitude for debuffs, most other effects use positive magnitude for both buffs and debuffs (the game engine handles the difference based on ToWho)

### Common Buff/Debuff Effect Types

From `eEffectType` enum in `Core/Enums.cs`:

**Primary Buff/Debuff Types**:
- `DamageBuff` - Increases/decreases damage output
- `Defense` - Increases/decreases defense by damage type or position
- `Resistance` - Increases/decreases resistance by damage type
- `ToHit` - Increases/decreases chance to hit
- `Accuracy` - Increases/decreases accuracy (different from ToHit)
- `RechargeTime` - Increases/decreases power recharge speed
- `EnduranceDiscount` - Reduces/increases endurance cost
- `Recovery` - Increases/decreases endurance recovery rate
- `Regeneration` - Increases/decreases HP regeneration rate
- `HitPoints` - Increases/decreases maximum HP
- `SpeedRunning`, `SpeedFlying`, `SpeedJumping` - Movement speed buffs/debuffs
- `Range` - Increases/decreases power range
- `Perception`, `PerceptionRadius` - Detection range buffs/debuffs
- `Stealth`, `StealthRadius` - Stealth buffs

**Control/Mez Resistance**:
- `MezResist` - Resistance to control effects (reduces magnitude or duration)

**Special Modifier Types**:
- `ResEffect` - Debuff resistance (resistance to debuffs)
- `Enhancement` - Enhances another effect's magnitude
- `ModifyAttrib` - Dynamic attribute modification

### Key Properties for Buffs/Debuffs

From `Effect.cs`:

**Core Properties**:
- `EffectType` - Type of buff/debuff (from eEffectType enum)
- `Mag` / `nMagnitude` - Base magnitude of the effect
- `BuffedMag` - Calculated magnitude after enhancements and modifiers
- `Duration` / `nDuration` - How long the effect lasts (0 = instant/permanent)
- `ToWho` - Target: Self, Target (enemy), Team, Area, All
- `Aspect` - Sub-type (damage type for Defense/Resistance, specific attribute for others)
- `DamageType` - Specific damage type affected (for Defense, Resistance, DamageBuff)

**Stacking/Interaction Properties**:
- `Stacking` - Can multiple applications stack? (Yes, No)
- `Buffable` - Can this effect be enhanced by enhancements? (bool)
- `Resistible` - Can this effect be resisted by target? (bool)
- `Suppression` - Is effect suppressed in certain situations? (Combat, Movement, etc.)
- `IgnoreScaling` - Bypass archetype scaling? (bool)

**Scaling Properties**:
- `Scale` - Base scaling factor applied to magnitude
- `AttribType` - How to calculate magnitude: Magnitude (direct), Duration (time-based), Expression (formula)
- `ModifierTable` - Reference to modifier table for scaling (e.g., "Melee_Ones")

### High-Level Algorithm

```
Buff/Debuff Calculation Flow:

1. Determine Effect Properties:
   - EffectType (what attribute is being modified)
   - Aspect/DamageType (specific sub-type if applicable)
   - ToWho (who receives the effect: self, ally, enemy)
   - PvMode (PvE or PvP - different magnitudes)

2. Calculate Base Magnitude:
   - Start with nMagnitude (from power data)
   - Apply Scale factor (from effect properties)
   - Apply ModifierTable scaling (e.g., archetype-specific)
   - Result: Base magnitude before enhancements

3. Apply Enhancements (if Buffable = true):
   - Calculate enhancement bonus (with ED applied)
   - Multiply base magnitude by (1 + enhancement bonus)
   - Result: BuffedMag

4. Calculate Duration:
   - Start with nDuration (from power data)
   - Apply duration enhancements if applicable
   - 0 duration = instant/permanent effect
   - >0 duration = temporary effect

5. Target Application:
   - If ToWho = Self: Apply to caster
   - If ToWho = Target: Apply to enemy (check Resistible flag)
   - If ToWho = Team: Apply to all team members
   - If ToWho = Area: Apply to all in area of effect

6. Check Resistibility (for debuffs):
   - If Resistible = true and target has resistance:
     - Apply target's debuff resistance
     - Reduce magnitude based on resistance
   - Result: Final applied magnitude

7. Apply Stacking Rules:
   - If Stacking = Yes: Multiple applications add together
   - If Stacking = No: Only strongest application applies
   - Specific stacking rules vary by effect type (see Spec 25)

8. Check Suppression:
   - If Suppression != None:
     - Check combat state, movement state, etc.
     - Suppress effect if conditions met
   - Result: Active or suppressed

9. Aggregate with Other Effects:
   - Group effects by (EffectType, Aspect, ToWho, PvMode)
   - Combine magnitudes based on stacking rules
   - Apply archetype caps (see Spec 17)
   - Result: Total buff/debuff value
```

### Target Types (eToWho enum)

```
eToWho.Unspecified - No target specified
eToWho.Target      - Enemy target (typical for debuffs)
eToWho.Self        - Caster (typical for self-buffs)
eToWho.All         - All entities in area (ally and enemy)
```

**Note**: Team and Area targeting are handled differently in different parts of the codebase but generally follow these patterns:
- Ally buffs use ToWho = Self with AoE radius
- Enemy debuffs use ToWho = Target with AoE radius

### Buffable vs Resistible Flags

**Buffable = true** (most buffs/debuffs):
- Effect can be enhanced by slotted enhancements
- Subject to Enhancement Diversification (ED)
- Magnitude scales with enhancement bonuses
- Example: Defense buff, Damage buff, Recharge buff

**Buffable = false** (some special effects):
- Effect magnitude is fixed
- Enhancements don't affect magnitude
- Example: Some special mechanic effects, certain procs

**Resistible = true** (most debuffs):
- Target's resistance to debuffs can reduce magnitude
- Enemy's ResEffect attribute applies
- Example: Defense debuff on enemy (enemy's debuff resistance reduces effect)

**Resistible = false** (most buffs, some special debuffs):
- Effect cannot be resisted
- Full magnitude always applies
- Example: Self-buffs, unresistable debuffs

### Duration Mechanics

**Duration = 0**:
- Instant effect (damage, heal)
- Permanent effect (passive buffs from toggles/autos)

**Duration > 0**:
- Temporary buff/debuff
- Effect expires after duration seconds
- Duration can be enhanced if AttribType allows
- Duration can be reduced by target's mez resistance (for control effects)

### Magnitude Calculation Details

From `Effect.cs` - `BuffedMag` property:

```csharp
public float BuffedMag => Math.Abs(Math_Mag) > float.Epsilon ? Math_Mag : Mag;
```

And the `Mag` property calculation:

```csharp
return (EffectType == Enums.eEffectType.Damage ? -1 : 1) * AttribType switch
{
    Enums.eAttribType.Magnitude => Scale * nMagnitude * DatabaseAPI.GetModifier(this),
    Enums.eAttribType.Duration => nMagnitude,
    Enums.eAttribType.Expression => Parse(expression, ExpressionType.Magnitude),
    _ => 0
};
```

**Key Points**:
- Damage effects multiply by -1 (negative magnitude = damage)
- Most other effects use positive magnitude
- Modifier table lookup (DatabaseAPI.GetModifier) applies archetype scaling
- Expression type allows dynamic formula-based magnitude

## Game Mechanics Context

**Why Buffs/Debuffs Exist:**

City of Heroes' combat system is heavily buff/debuff focused compared to other MMOs. The game emphasizes:
1. **Force Multiplication**: Buffs and debuffs make teams more powerful than solo players
2. **Archetype Diversity**: Different ATs excel at different buff/debuff combinations
3. **Build Optimization**: Set bonuses and slotting choices create powerful buff stacking
4. **Tactical Gameplay**: Timing and layering of buffs/debuffs is core to strategy

**Historical Context:**

- **Launch (2004)**: Basic buff/debuff system with simple stacking
- **Issue 5 (2005)**: Enhancement Diversification affected buff/debuff slotting
- **Issue 9 (2006)**: Invention Origin sets added global buff bonuses (set bonuses)
- **Issue 18 (2010)**: Incarnate system added powerful buffs/debuffs
- **Homecoming (2019+)**: Balance adjustments to buff/debuff stacking and caps

**Known Quirks:**

1. **Buff vs Debuff Enhancement**: Some powers have both buffable self-buffs and non-buffable debuffs in the same power. Enhancements only affect the buffable component.

2. **Debuff Resistance**: High-level enemies (AVs, GMs) have significant debuff resistance, reducing player debuff effectiveness. This is separate from damage resistance.

3. **ToHit Debuff Special Case**: ToHit debuffs have a floor (minimum ToHit chance) that limits their effectiveness. Excessive ToHit debuffing hits diminishing returns.

4. **Damage Buff Stacking**: Most damage buffs stack additively, but some (like Fury, Defiance) stack multiplicatively or have special mechanics.

5. **Defense Buff Caps**: Defense buffs are capped per archetype (varies from 45% to 175% total defense). This affects how much benefit you get from stacking defense buffs.

6. **Resistance Buff Caps**: Similarly, resistance is capped (typically 75% for most ATs, 90% for Tankers/Brutes). Resistance debuffs can push enemies below 0% resistance (increasing damage taken).

7. **Recharge Buff Floor**: Recharge time cannot go below 0. Extreme recharge buffs (e.g., from Hasten + global recharge) can hit this floor for fast-recharging powers.

8. **Duration Zero Edge Case**: Duration = 0 is used for both instant effects (damage, heal) and permanent effects (toggle/auto buffs). Code must distinguish based on power type.

## Python Implementation Notes

**Proposed Architecture:**

```python
# backend/app/calculations/buffs_debuffs.py

from enum import Enum
from dataclasses import dataclass
from typing import Optional
from .effects import Effect, EffectType, ToWho, PvMode

class BuffDebuffType(Enum):
    """
    Common buff/debuff effect types
    Maps to relevant eEffectType values
    """
    DAMAGE_BUFF = "damage_buff"
    DEFENSE = "defense"
    RESISTANCE = "resistance"
    TOHIT = "tohit"
    ACCURACY = "accuracy"
    RECHARGE = "recharge"
    ENDURANCE_DISCOUNT = "endurance_discount"
    RECOVERY = "recovery"
    REGENERATION = "regeneration"
    HIT_POINTS = "hit_points"
    MEZ_RESIST = "mez_resist"
    RES_EFFECT = "res_effect"  # Debuff resistance

@dataclass
class BuffDebuff(Effect):
    """
    Represents a buff or debuff effect
    Extends base Effect class with buff/debuff specific properties
    """
    buffable: bool = True      # Can be enhanced by enhancements
    resistible: bool = True    # Can be resisted by target
    stacking: bool = True      # Can multiple instances stack

    def is_buff(self) -> bool:
        """
        Determine if this is a buff (positive effect on self/ally)
        vs debuff (negative effect on enemy)
        """
        return self.to_who in [ToWho.SELF, ToWho.TEAM]

    def is_debuff(self) -> bool:
        """Determine if this is a debuff (effect on enemy)"""
        return self.to_who == ToWho.TARGET

    def calculate_magnitude(self,
                          base_magnitude: float,
                          enhancement_bonus: float = 0.0,
                          at_scale: float = 1.0,
                          modifier_table_value: float = 1.0) -> float:
        """
        Calculate final buff/debuff magnitude

        Args:
            base_magnitude: Base magnitude from power data
            enhancement_bonus: Enhancement bonus (0.0 to 1.0+, after ED)
            at_scale: Archetype scaling factor
            modifier_table_value: Modifier table lookup value

        Returns:
            Final magnitude to apply
        """
        # Step 1: Base calculation with scaling
        magnitude = base_magnitude * self.scale * at_scale * modifier_table_value

        # Step 2: Apply enhancements if buffable
        if self.buffable:
            magnitude *= (1.0 + enhancement_bonus)

        # Step 3: Handle damage effect special case (negative magnitude)
        if self.effect_type == EffectType.DAMAGE:
            magnitude *= -1

        return magnitude

    def apply_resistance(self,
                        magnitude: float,
                        target_resistance: float) -> float:
        """
        Apply target's resistance to this buff/debuff

        Args:
            magnitude: Calculated magnitude
            target_resistance: Target's resistance to this effect type

        Returns:
            Magnitude after resistance applied
        """
        if not self.resistible:
            return magnitude

        # Debuff resistance reduces magnitude
        # resistance is typically 0.0 to 1.0+ (0% to 100%+)
        return magnitude * (1.0 - target_resistance)

    def calculate_duration(self,
                          base_duration: float,
                          enhancement_bonus: float = 0.0,
                          target_mez_resistance: float = 0.0) -> float:
        """
        Calculate effect duration

        Args:
            base_duration: Base duration from power data
            enhancement_bonus: Duration enhancement bonus (if applicable)
            target_mez_resistance: Target's mez resistance (for control effects)

        Returns:
            Final duration in seconds (0 = instant/permanent)
        """
        if base_duration == 0:
            return 0.0

        # Apply duration enhancements (for certain effect types)
        duration = base_duration * (1.0 + enhancement_bonus)

        # Apply target mez resistance (reduces duration)
        if target_mez_resistance > 0:
            duration *= (1.0 - target_mez_resistance)

        return max(0.0, duration)

class BuffDebuffCalculator:
    """
    Handles buff/debuff calculations for powers and builds
    """

    def calculate_buffed_effect(self,
                               buff_debuff: BuffDebuff,
                               base_magnitude: float,
                               enhancement_bonus: float = 0.0,
                               at_scale: float = 1.0,
                               modifier_table_value: float = 1.0,
                               target_resistance: float = 0.0) -> float:
        """
        Calculate final magnitude of a buff/debuff after all modifiers

        Returns:
            Final magnitude to apply to target
        """
        # Calculate base magnitude with enhancements and scaling
        magnitude = buff_debuff.calculate_magnitude(
            base_magnitude=base_magnitude,
            enhancement_bonus=enhancement_bonus,
            at_scale=at_scale,
            modifier_table_value=modifier_table_value
        )

        # Apply target resistance (for debuffs)
        if buff_debuff.is_debuff():
            magnitude = buff_debuff.apply_resistance(
                magnitude=magnitude,
                target_resistance=target_resistance
            )

        return magnitude

    def aggregate_buffs_debuffs(self,
                               effects: list[BuffDebuff]) -> dict[tuple, float]:
        """
        Aggregate multiple buff/debuff effects by type

        Groups effects by (effect_type, aspect, to_who, pv_mode)
        and applies stacking rules

        Returns:
            Dictionary mapping effect key to total magnitude
        """
        aggregated = {}

        for effect in effects:
            key = (effect.effect_type, effect.aspect, effect.to_who, effect.pv_mode)

            if key not in aggregated:
                aggregated[key] = 0.0

            # Apply stacking rules
            if effect.stacking:
                # Additive stacking (most buffs/debuffs)
                aggregated[key] += effect.magnitude
            else:
                # Best-value-only (some unique effects)
                aggregated[key] = max(aggregated[key], effect.magnitude)

        return aggregated
```

**Implementation Priority:**

**HIGH** - Buffs and debuffs are core to all power calculations. Implement early in Phase 1 alongside Power Effects Core (Spec 01).

**Key Implementation Steps:**

1. Create `BuffDebuff` class extending `Effect` with buff/debuff specific properties
2. Implement magnitude calculation with enhancement scaling
3. Implement target resistance application for debuffs
4. Implement duration calculation
5. Create aggregation logic for multiple buff/debuff sources
6. Integrate with power calculations (Spec 02) and archetype modifiers (Spec 16)
7. Add archetype cap application (Spec 17)
8. Implement detailed stacking rules (defer to Spec 25)

**Testing Strategy:**

- Unit tests for magnitude calculation with various enhancement levels
- Unit tests for resistance application (debuff resistance reducing effect)
- Unit tests for duration calculation
- Unit tests for buff vs debuff detection
- Integration tests comparing Python calculations to MidsReborn output for known powers:
  - Defense buffs (Force Field powers)
  - Damage buffs (Fulcrum Shift, Aim, Build Up)
  - Debuffs (Radiation Infection, Tar Patch, Darkest Night)
  - Resistance debuffs (Sonic Resonance powers)

## References

- **Related Specs**:
  - Spec 01 (Power Effects Core) - Base effect system
  - Spec 02 (Power Damage) - Damage buff effects
  - Spec 09 (Defense/Resistance) - Defense and resistance buffs/debuffs
  - Spec 16 (Archetype Modifiers) - AT scaling for buffs/debuffs
  - Spec 17 (Archetype Caps) - Buff caps per AT
  - Spec 25 (Buff Stacking Rules) - Detailed stacking mechanics
- **MidsReborn Files**:
  - `Core/Base/Data_Classes/Effect.cs` - Effect class with BuffedMag calculation
  - `Core/GroupedFx.cs` - Buff/debuff aggregation
  - `Core/Enums.cs` - eEffectType, eToWho enumerations
  - `Core/PowerEntry.cs` - Applying buffs/debuffs to powers
- **Game Documentation**:
  - City of Heroes Wiki - "Buffs and Debuffs"
  - Paragon Wiki - "Resistance (Mechanic)" for debuff resistance
  - Homecoming Forums - Archetype cap discussions
