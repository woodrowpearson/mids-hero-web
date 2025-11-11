# Power Effects Core

## Overview
- **Purpose**: Foundation of all game effect calculations - IEffect interface and effect grouping/aggregation system
- **Used By**: All power calculations, build totals, set bonuses
- **Complexity**: Complex
- **Priority**: Critical
- **Status**: 🟡 Breadth Complete

## MidsReborn Implementation

### Primary Location
- **File**: `Core/Base/Data_Classes/Effect.cs`
- **Class**: `Effect` (implements `IEffect` interface)
- **Related Files**:
  - `Core/GroupedFx.cs` - Effect grouping and aggregation
  - `Core/Enums.cs` - `eEffectType` enumeration

### Effect Types

The `eEffectType` enum in `Core/Enums.cs` defines 50+ effect types including:

**Core Combat Effects**:
- Damage (by type: Smashing, Lethal, Fire, Cold, Energy, Negative, Toxic, Psionic)
- Defense (by type and position)
- Resistance (by damage type)
- Accuracy, ToHit
- DamageBuff

**Character Resources**:
- Heal, HitPoints, Regeneration
- Endurance, EnduranceDiscount, Recovery
- Meter (for inherent power bars)

**Control/Mez Effects**:
- Hold, Stun, Sleep, Immobilize, Confuse, Fear, Placate
- Knockback, Knockup, Repel
- Taunt, DropToggles

**Movement Effects**:
- Fly, SpeedFlying
- JumpHeight, SpeedJumping
- SpeedRunning
- Teleport

**Special Mechanics**:
- Recharge, InterruptTime
- Enhancement, GrantPower
- Stealth, StealthRadius
- Perception, PerceptionRadius
- Range, RangeBuff

### High-Level Algorithm

```
Effect Class Structure:
  - EffectType: eEffectType (what kind of effect)
  - Magnitude: float (strength of effect)
  - Duration: float (how long it lasts)
  - Probability: float (chance to occur, for procs)
  - Aspect: Enums enum (sub-type: damage type, defense type, etc.)
  - Scale: float (archetype scaling factor)
  - ToWho: Enums.eToWho (Target, Self, etc.)
  - PvMode: Enums.ePvX (PvE, PvP)
  - Suppression: Enums.eSuppression (combat, movement)

GroupedFx Class Structure:
  - FxId struct identifies unique effect combinations:
    - EffectType
    - MezType (for control effects)
    - DamageType (for damage effects)
    - ETModifies (for modifying effects)
    - ToWho (target)
    - PvMode (PvE/PvP)
    - SummonId (for pet effects)

Effect Aggregation Process:
  1. Collect all effects from all sources:
     - Base power effects
     - Slotted enhancement effects
     - Set bonus effects
     - Incarnate effects
     - Archetype inherent effects

  2. Group effects by FxId tuple (type, aspect, target, etc.)

  3. Apply stacking rules per effect type:
     - Additive: Most buffs/debuffs (sum all values)
     - Multiplicative: Some damage buffs (multiply factors)
     - Best-value-only: Some unique effects
     - Suppressed: Some effects don't stack (Rule of 5)

  4. Apply archetype scaling:
     - Multiply magnitude by AT's scale for that effect type
     - Different ATs have different buff/debuff/damage scales

  5. Apply caps:
     - Defense capped per archetype
     - Resistance capped per archetype
     - Damage buff capped per archetype

  6. Return aggregated effects per type
```

### Dependencies

**Base for all power calculations**:
- `PowerEntry.cs` uses Effect for individual power stats
- `Stats.cs` uses Effect for build-wide totals
- Set bonuses add Effect objects to global pool
- Incarnate abilities add Effect objects
- Archetype modifiers scale Effect magnitudes

**Effect Delivery Mechanisms**:
- Direct power effects (immediate)
- Toggle aura effects (continuous)
- Pseudopet delivered effects (location-based)
- Proc effects (probability-based)

## Game Mechanics Context

**Why This Exists:**

City of Heroes uses a unified effect system where all game mechanics (damage, buffs, debuffs, control, movement, resources) are represented as Effect objects implementing the IEffect interface. This design provides:

1. **Consistency**: One system handles all power mechanics
2. **Composability**: Effects from any source combine through same rules
3. **Flexibility**: New effect types can be added without changing core engine
4. **Transparency**: Same data structure used for calculation and UI display

**Historical Context:**

The effect system was fundamental to CoH's design from launch (2004). As the game evolved, new effect types were added:
- Issue 5 (2005): Enhancement Diversification added complex effect stacking rules
- Issue 9 (2006): Invention Origin enhancements added set bonuses, requiring effect aggregation with "Rule of 5" suppression
- Issue 18 (2010): Incarnate system added alpha shifts and new effect types
- Homecoming (2019+): Additional effects for new powersets and mechanics

**Known Quirks:**

1. **Stacking varies by type**: Some effects stack additively (defense), others multiplicatively (some damage buffs), others don't stack at all (unique IOs). Must check per effect type.

2. **Rule of 5 suppression**: When calculating set bonuses, only the 5 strongest instances of each bonus type count. This prevents excessive stacking of identical set bonuses.

3. **Pseudopets deliver differently**: Effects delivered by pseudopets (invisible entities created by powers) follow different rules than direct power effects. They can bypass some target limits and have separate enhancement rules.

4. **PvP vs PvE effects**: Many effects have different magnitudes in PvP vs PvE contexts. The PvMode field tracks this distinction.

5. **Suppression mechanics**: Some effects are suppressed in combat or when other powers activate. The Suppression field tracks these complex rules.

## Python Implementation Notes

**Proposed Architecture:**

```python
# backend/app/calculations/effects.py

from enum import Enum
from dataclasses import dataclass
from typing import Optional

class EffectType(Enum):
    NONE = "none"
    ACCURACY = "accuracy"
    DAMAGE = "damage"
    DAMAGE_BUFF = "damage_buff"
    DEFENSE = "defense"
    RESISTANCE = "resistance"
    HEAL = "heal"
    REGENERATION = "regeneration"
    ENDURANCE = "endurance"
    RECOVERY = "recovery"
    RECHARGE = "recharge"
    # ... all 50+ types from eEffectType

class DamageType(Enum):
    SMASHING = "smashing"
    LETHAL = "lethal"
    FIRE = "fire"
    COLD = "cold"
    ENERGY = "energy"
    NEGATIVE = "negative"
    TOXIC = "toxic"
    PSIONIC = "psionic"

class ToWho(Enum):
    TARGET = "target"
    SELF = "self"
    TEAM = "team"
    AREA = "area"

class PvMode(Enum):
    PVE = "pve"
    PVP = "pvp"
    ANY = "any"

@dataclass
class Effect:
    """
    Represents a single game effect (damage, buff, debuff, etc.)
    Maps to MidsReborn's Effect class
    """
    effect_type: EffectType
    magnitude: float
    duration: float = 0.0  # 0 = instant/permanent
    probability: float = 1.0  # 1.0 = always, <1.0 = proc chance
    aspect: Optional[str] = None  # "smashing", "melee", etc.
    scale: float = 1.0  # archetype scaling
    to_who: ToWho = ToWho.TARGET
    pv_mode: PvMode = PvMode.PVE

    def scaled_magnitude(self, at_scale: float = 1.0) -> float:
        """Apply archetype scaling to magnitude"""
        return self.magnitude * self.scale * at_scale

@dataclass
class EffectGroup:
    """
    Aggregated effects of same type/aspect
    Maps to MidsReborn's GroupedFx concept
    """
    effect_type: EffectType
    aspect: Optional[str]
    to_who: ToWho
    pv_mode: PvMode
    total_magnitude: float
    source_count: int  # how many sources contributed

class EffectAggregator:
    """
    Aggregates effects from multiple sources applying stacking rules
    Maps to MidsReborn's GroupedFx class
    """

    def group_effects(self, effects: list[Effect]) -> dict[tuple, EffectGroup]:
        """
        Group effects by (type, aspect, to_who, pv_mode) and aggregate

        Returns dict keyed by (effect_type, aspect, to_who, pv_mode) tuple
        """
        groups = {}

        for effect in effects:
            key = (effect.effect_type, effect.aspect, effect.to_who, effect.pv_mode)

            if key not in groups:
                groups[key] = EffectGroup(
                    effect_type=effect.effect_type,
                    aspect=effect.aspect,
                    to_who=effect.to_who,
                    pv_mode=effect.pv_mode,
                    total_magnitude=0.0,
                    source_count=0
                )

            # Apply stacking rules based on effect type
            groups[key].total_magnitude += self._apply_stacking_rule(
                effect.effect_type,
                effect.magnitude,
                groups[key].total_magnitude
            )
            groups[key].source_count += 1

        return groups

    def _apply_stacking_rule(self, effect_type: EffectType,
                            new_value: float, current_value: float) -> float:
        """
        Apply type-specific stacking rules
        Most effects are additive, but some have special rules
        """
        # Most effects stack additively
        # TODO: Implement special cases (multiplicative, best-value-only, etc.)
        return new_value

    def apply_caps(self, groups: dict, archetype_caps: dict) -> dict:
        """
        Apply archetype-specific caps to aggregated effects
        Different ATs have different defense/resistance/damage caps
        """
        capped_groups = {}

        for key, group in groups.items():
            capped_group = group

            # Check if this effect type has a cap for this archetype
            if group.effect_type in archetype_caps:
                cap = archetype_caps[group.effect_type]
                if group.total_magnitude > cap:
                    capped_group.total_magnitude = cap

            capped_groups[key] = capped_group

        return capped_groups
```

**Implementation Priority:**

**CRITICAL** - Implement first before any power calculations. This is the foundation that all other calculations depend on.

**Key Implementation Steps:**

1. Define all effect type enums matching MidsReborn's eEffectType
2. Create Effect dataclass with all required fields
3. Implement EffectAggregator.group_effects() for basic additive stacking
4. Add stacking rule variations (multiplicative, best-value, etc.) - defer to Spec 25
5. Implement archetype scaling integration - defer to Spec 16
6. Implement cap application - defer to Spec 17

**Testing Strategy:**

- Unit tests for Effect class creation
- Unit tests for EffectAggregator with simple additive stacking
- Integration tests comparing Python aggregation to MidsReborn output for known power combinations

## References

- **Related Specs**: All power specs (02-09), enhancement specs (10-15), archetype specs (16-18), build totals (19-24), buff stacking (25)
- **MidsReborn Files**: `Core/Base/Data_Classes/Effect.cs`, `Core/GroupedFx.cs`, `Core/Enums.cs`
- **Game Documentation**: City of Heroes Wiki - "Effects System", "Combat Mechanics"
