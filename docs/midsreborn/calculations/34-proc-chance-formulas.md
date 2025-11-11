# Proc Chance Formulas

## Overview
- **Purpose**: Calculate probability of proc IO effects activating using PPM (Procs Per Minute) system with recharge/cast time/area factor modifiers
- **Used By**: IO proc damage/heal/endurance effects, interface procs, proc-based enhancements
- **Complexity**: Complex
- **Priority**: High
- **Status**: 🟡 Breadth Complete

## MidsReborn Implementation

### Primary Location
- **File**: `Core/Base/Data_Classes/Effect.cs`
- **Property**: `ProcsPerMinute` (float)
- **Calculation**: `ActualProbability` property (private getter)
- **Related Files**:
  - `Core/Base/Data_Classes/Power.cs` - `AoEModifier` calculation
  - `Core/IEffect.cs` - `MinProcChance` property interface
  - `Forms/OptionsMenuItems/DbEditor/frmPowerEffect.cs` - UI for PPM editing

### Key Properties

```csharp
// Effect.cs properties
public float ProcsPerMinute { get; set; }  // 0 = legacy flat %, >0 = PPM system
public float BaseProbability { get; set; }  // Legacy flat % chance (0.0-1.0)
public float MinProcChance => ProcsPerMinute > 0 ? ProcsPerMinute * 0.015f + 0.05f : 0.05f;
public const float MaxProcChance = 0.9f;

// Power.cs property for AoE penalty
public float AoEModifier => EffectArea != Enums.eEffectArea.Cone
    ? EffectArea != Enums.eEffectArea.Sphere ? 1 : (float)(1 + Radius * 0.15)
    : (float)(1 + Radius * 0.15 - Radius * 0.000366669992217794 * (360 - Arc));
```

### High-Level Algorithm

```
PPM Proc Chance Calculation:

INPUT:
  - ProcsPerMinute (PPM): float from proc IO enhancement (e.g., 3.5 PPM)
  - Power properties:
    - RechargeTime: float (current recharge with global modifiers)
    - BaseRechargeTime: float (base unmodified recharge)
    - CastTimeReal: float (activation time)
    - PowerType: enum (Click, Toggle, Auto)
    - AoEModifier: float (area factor penalty)
  - Character properties:
    - GlobalRecharge: float (from Hasten, set bonuses, etc.)

ALGORITHM:

1. Check if PPM system applies:
   IF ProcsPerMinute <= 0:
     RETURN BaseProbability  // Legacy flat % proc (pre-Issue 24)

2. Calculate area factor penalty:
   areaFactor = AoEModifier * 0.75 + 0.25

   WHERE AoEModifier is:
   - IF EffectArea is Single Target: 1.0
   - IF EffectArea is Sphere: 1 + Radius * 0.15
   - IF EffectArea is Cone: 1 + Radius * 0.15 - Radius * 0.000366669992217794 * (360 - Arc)

   RESULT: Larger AoEs have higher areaFactor, reducing proc chance per target

3. Calculate effective recharge accounting for global recharge:
   globalRecharge = (Character.BuffHaste - 100) / 100

   rechargeVal = IF power.RechargeTime ≈ 0:
                   0
                 ELSE:
                   BaseRechargeTime / (BaseRechargeTime / RechargeTime - globalRecharge)

   NOTE: This calculates the "base" recharge before global bonuses were applied

4. Calculate proc chance based on power type:
   IF PowerType == Click:
     // Standard formula: PPM scales with power's total animation time
     probability = PPM * (rechargeVal + CastTimeReal) / (60 * areaFactor)

   ELSE:  // Toggle or Auto
     // Fixed 10-second interval for constant activation powers
     probability = PPM * 10 / (60 * areaFactor)

5. Apply minimum proc chance cap:
   minChance = PPM * 0.015 + 0.05
   probability = MAX(minChance, probability)

   EXAMPLE: 3.5 PPM proc has minimum of 3.5 * 0.015 + 0.05 = 10.25%

6. Apply maximum proc chance cap:
   probability = MIN(MaxProcChance, probability)
   WHERE MaxProcChance = 0.9 (90% hard cap)

7. Apply character-specific effect modifiers (if any):
   IF EffectId exists in Character.ModifyEffects:
     probability += Character.ModifyEffects[EffectId]

8. Final clamping to valid probability range:
   probability = MAX(0, MIN(1, probability))

OUTPUT: probability (0.0 to 1.0)
```

### PPM Formula Breakdown

**Core Formula (Click Powers)**:
```
chance = PPM × (recharge + cast) / (60 × areaFactor)
```

Where:
- **PPM**: Procs Per Minute value from the enhancement (e.g., 3.5)
- **recharge**: Base recharge time in seconds (before global modifiers)
- **cast**: Activation/cast time in seconds
- **60**: Converts minutes to seconds (60 seconds/minute)
- **areaFactor**: Penalty for AoE powers = `AoEModifier × 0.75 + 0.25`

**Interpretation**: A power used more frequently (low recharge+cast) has lower proc chance per activation, but more chances per minute. The PPM value ensures the proc fires approximately that many times per minute on average.

**Toggle/Auto Formula**:
```
chance = PPM × 10 / (60 × areaFactor)
```

Where:
- **10**: Assumed 10-second activation interval for toggles/autos

### Area Factor Calculation

The area factor penalty reduces proc chance in AoE powers to prevent excessive proc spam:

```
AoEModifier calculation (from Power.cs):
  - Single Target: 1.0
  - Sphere AoE: 1 + Radius × 0.15
  - Cone AoE: 1 + Radius × 0.15 - Radius × 0.000366669992217794 × (360 - Arc)

areaFactor = AoEModifier × 0.75 + 0.25

Examples:
  - Single target (Radius=0): AoEModifier=1.0, areaFactor=1.0
  - Small AoE (Radius=10): AoEModifier=2.5, areaFactor=2.125
  - Large AoE (Radius=25): AoEModifier=4.75, areaFactor=3.8125
```

**Result**: Large AoE powers have proc chances divided by 3-4x compared to single-target powers with same recharge.

### Minimum Proc Chance Cap

```
minChance = PPM × 0.015 + 0.05

Examples:
  - 1.0 PPM: minChance = 0.015 + 0.05 = 6.5%
  - 2.0 PPM: minChance = 0.03 + 0.05 = 8.0%
  - 3.5 PPM: minChance = 0.0525 + 0.05 = 10.25%
  - 4.5 PPM: minChance = 0.0675 + 0.05 = 11.75%
```

**Purpose**: Ensures procs have reasonable minimum activation chance even in very fast-recharging powers.

### Maximum Proc Chance Cap

```
maxChance = 0.9 (90% hard cap)
```

**Purpose**: Prevents any proc from being guaranteed. Even very slow powers (long recharge/cast) cap at 90%.

## Game Mechanics Context

**Why This Exists:**

The PPM (Procs Per Minute) system was introduced in Issue 24 (2012) to replace the legacy flat percentage proc system. The old system had major problems:

1. **Fast-recharge powers**: 20% proc in a 2-second recharge power = 6 procs/minute average
2. **Slow-recharge powers**: Same 20% proc in a 30-second power = 0.4 procs/minute average

This massive discrepancy made procs worthless in slow powers and overpowered in fast powers. The PPM system normalizes this: a 3 PPM proc fires approximately 3 times per minute regardless of power recharge, making all procs viable in all powers.

**Historical Context:**

- **Pre-Issue 24 (2004-2012)**: Flat percentage procs (typically 10-33%)
  - Players slotted procs only in fast-recharging powers
  - Slow powers (snipes, nukes) couldn't use procs effectively
  - Proc-heavy builds exploited fast-activating powers

- **Issue 24 (2012)**: PPM system introduced by Paragon Studios
  - Most procs converted to PPM values (1.0 to 4.5 typical)
  - Formula accounts for recharge and activation time
  - Area factor added to prevent AoE proc spam
  - Min/max caps prevent edge case abuse

- **Post-Homecoming (2019+)**: PPM system refined
  - New procs use PPM system exclusively
  - Some legacy procs still use flat % for historical builds
  - Incarnate Interface procs use modified PPM (higher values)

**Known Quirks:**

1. **Legacy flat % procs**: Some old procs (pre-Issue 24 IOs) still use `BaseProbability` flat % instead of PPM. Check `ProcsPerMinute > 0` to distinguish.

2. **Global recharge interaction**: The formula removes global recharge effects to calculate "base" proc chance. This prevents perma-Hasten builds from having artificially low proc chances.

3. **Toggle/Auto fixed interval**: Toggles and autos use a fixed 10-second assumed interval rather than actual tick rate. This means fast-ticking auras use the same formula as slow-ticking auras.

4. **AoE factor is harsh**: Large radius AoE powers (Radius=25+) have proc chances divided by 3-4x. This is intentional to prevent 10-target AoE procs from firing 10x per activation.

5. **Cone vs Sphere difference**: Narrow cones (small arc) are treated as "more targeted" than full spheres, getting slightly better area factors. Wide cones (large arc) are penalized like spheres.

6. **Minimum cap prevents zero chance**: Without the `PPM × 0.015 + 0.05` minimum, extremely fast powers (1-second recharge) could have <1% proc chance. The cap ensures viability.

7. **90% maximum is strict**: Even a 4.5 PPM proc in a 120-second recharge nuke with 6-second cast time caps at 90%, not 100%. Procs are never guaranteed.

8. **Proc enhancement doesn't affect PPM**: Unlike regular IOs, proc enhancements don't benefit from enhancement bonuses. The PPM value is fixed per enhancement. Only the base effect (damage, heal, etc.) benefits from level/boosting.

## Python Implementation Notes

**Proposed Architecture:**

```python
# backend/app/calculations/proc_chance.py

from dataclasses import dataclass
from enum import Enum
from typing import Optional

class PowerType(Enum):
    CLICK = "click"
    TOGGLE = "toggle"
    AUTO = "auto"

class EffectArea(Enum):
    SINGLE = "single"
    SPHERE = "sphere"
    CONE = "cone"

@dataclass
class ProcEnhancement:
    """
    Represents a proc IO enhancement with PPM value
    Maps to Effect.ProcsPerMinute property
    """
    name: str
    procs_per_minute: float  # 0 = legacy flat %, >0 = PPM system
    base_probability: float = 0.0  # Legacy flat % (0.0-1.0)
    effect_id: str = ""  # For character-specific modifiers

@dataclass
class PowerProcContext:
    """
    Power properties needed for proc calculation
    Maps to Power.cs properties
    """
    power_type: PowerType
    base_recharge_time: float  # Unmodified recharge
    current_recharge_time: float  # With enhancements
    cast_time: float  # Activation time
    effect_area: EffectArea
    radius: float = 0.0  # For AoE powers
    arc: int = 0  # For cone powers (0-360 degrees)

@dataclass
class CharacterProcContext:
    """
    Character properties affecting proc chance
    """
    global_recharge_bonus: float = 0.0  # From Hasten, sets, etc. (as decimal, e.g., 0.7 = +70%)
    effect_modifiers: dict[str, float] = None  # EffectId -> modifier

    def __post_init__(self):
        if self.effect_modifiers is None:
            self.effect_modifiers = {}

class ProcChanceCalculator:
    """
    Calculates proc activation probability using PPM system
    Maps to Effect.ActualProbability calculation
    """

    MAX_PROC_CHANCE: float = 0.9  # 90% hard cap

    def calculate_aoe_modifier(self, power: PowerProcContext) -> float:
        """
        Calculate AoE modifier based on effect area
        Maps to Power.AoEModifier property
        """
        if power.effect_area == EffectArea.SINGLE:
            return 1.0

        elif power.effect_area == EffectArea.SPHERE:
            return 1.0 + power.radius * 0.15

        elif power.effect_area == EffectArea.CONE:
            # Cone formula: includes arc penalty for wide cones
            return (1.0 + power.radius * 0.15
                    - power.radius * 0.000366669992217794 * (360 - power.arc))

        return 1.0

    def calculate_area_factor(self, power: PowerProcContext) -> float:
        """
        Convert AoE modifier to area factor used in proc formula

        Formula: areaFactor = AoEModifier * 0.75 + 0.25

        This scales the modifier down (multiplies by 0.75) and adds base (0.25)
        Result: Single target = 1.0, AoEs have factor > 1.0 (reduces proc chance)
        """
        aoe_modifier = self.calculate_aoe_modifier(power)
        return aoe_modifier * 0.75 + 0.25

    def calculate_effective_recharge(self, power: PowerProcContext,
                                    character: CharacterProcContext) -> float:
        """
        Calculate power's effective recharge removing global bonuses

        This finds what the power's recharge would be with only enhancement
        slotting, before global recharge bonuses were applied. This prevents
        global recharge from artificially lowering proc chances.
        """
        if abs(power.current_recharge_time) < 0.001:
            return 0.0

        # Work backwards from current recharge to find base + enhancement
        return (power.base_recharge_time /
                (power.base_recharge_time / power.current_recharge_time
                 - character.global_recharge_bonus))

    def calculate_min_proc_chance(self, ppm: float) -> float:
        """
        Calculate minimum proc chance cap

        Formula: minChance = PPM × 0.015 + 0.05

        Ensures fast-recharging powers still have reasonable proc chance.
        """
        if ppm <= 0:
            return 0.05  # 5% minimum for legacy procs

        return ppm * 0.015 + 0.05

    def calculate_proc_chance(self, proc: ProcEnhancement,
                            power: PowerProcContext,
                            character: CharacterProcContext) -> float:
        """
        Calculate final proc activation probability

        Returns: float between 0.0 and 1.0 (probability of proc firing)
        """
        # Check for legacy flat % proc (pre-Issue 24 system)
        if proc.procs_per_minute <= 0:
            probability = proc.base_probability

        else:
            # PPM system calculation

            # Calculate area factor penalty for AoE powers
            area_factor = self.calculate_area_factor(power)

            # Calculate effective recharge (removing global bonuses)
            effective_recharge = self.calculate_effective_recharge(power, character)

            # Calculate proc chance based on power type
            if power.power_type == PowerType.CLICK:
                # Standard formula: scales with recharge + cast time
                probability = (proc.procs_per_minute *
                             (effective_recharge + power.cast_time) /
                             (60.0 * area_factor))

            else:  # Toggle or Auto
                # Fixed 10-second assumed interval
                probability = (proc.procs_per_minute * 10.0 /
                             (60.0 * area_factor))

            # Apply minimum cap
            min_chance = self.calculate_min_proc_chance(proc.procs_per_minute)
            probability = max(min_chance, probability)

            # Apply maximum cap (90%)
            probability = min(self.MAX_PROC_CHANCE, probability)

        # Apply character-specific effect modifiers (if any)
        if proc.effect_id and proc.effect_id in character.effect_modifiers:
            probability += character.effect_modifiers[proc.effect_id]

        # Final clamping to valid probability range
        return max(0.0, min(1.0, probability))

# Example usage
def example_proc_calculations():
    """
    Example proc chance calculations for common scenarios
    """
    calculator = ProcChanceCalculator()

    # Example 1: 3.5 PPM proc in fast single-target attack
    proc_35ppm = ProcEnhancement(
        name="Apoc Chance for Neg Damage",
        procs_per_minute=3.5
    )

    fast_attack = PowerProcContext(
        power_type=PowerType.CLICK,
        base_recharge_time=4.0,
        current_recharge_time=2.0,  # Slotted for recharge
        cast_time=1.0,
        effect_area=EffectArea.SINGLE
    )

    character = CharacterProcContext(
        global_recharge_bonus=0.7  # +70% from Hasten, sets, etc.
    )

    chance1 = calculator.calculate_proc_chance(proc_35ppm, fast_attack, character)
    print(f"3.5 PPM in fast attack: {chance1:.1%}")
    # Expected: ~20-30% (formula considers effective recharge)

    # Example 2: Same proc in slow single-target nuke
    slow_nuke = PowerProcContext(
        power_type=PowerType.CLICK,
        base_recharge_time=145.0,
        current_recharge_time=50.0,  # Heavy recharge slotting
        cast_time=3.0,
        effect_area=EffectArea.SINGLE
    )

    chance2 = calculator.calculate_proc_chance(proc_35ppm, slow_nuke, character)
    print(f"3.5 PPM in slow nuke: {chance2:.1%}")
    # Expected: 90% (hits max cap)

    # Example 3: Same proc in large AoE
    large_aoe = PowerProcContext(
        power_type=PowerType.CLICK,
        base_recharge_time=16.0,
        current_recharge_time=8.0,
        cast_time=2.0,
        effect_area=EffectArea.SPHERE,
        radius=25.0
    )

    chance3 = calculator.calculate_proc_chance(proc_35ppm, large_aoe, character)
    print(f"3.5 PPM in large AoE: {chance3:.1%}")
    # Expected: ~15-20% (area factor penalty reduces chance significantly)

    # Example 4: Legacy flat % proc
    legacy_proc = ProcEnhancement(
        name="Old Chance for Smashing",
        procs_per_minute=0.0,  # Legacy indicator
        base_probability=0.20  # 20% flat
    )

    chance4 = calculator.calculate_proc_chance(legacy_proc, fast_attack, character)
    print(f"Legacy 20% proc: {chance4:.1%}")
    # Expected: 20% (flat % doesn't change with power)
```

**Implementation Priority:**

**HIGH** - Proc IOs are a major part of build optimization. Understanding proc chance is critical for:
- Damage proc slotting decisions
- Heal proc builds (Preventive Medicine, Panacea)
- Endurance proc management
- Proc-heavy builds vs set bonus builds

**Key Implementation Steps:**

1. Implement `calculate_aoe_modifier()` for single/sphere/cone areas
2. Implement `calculate_area_factor()` transformation
3. Implement `calculate_effective_recharge()` to remove global bonuses
4. Implement core PPM formula for Click powers
5. Implement Toggle/Auto formula with fixed 10-second interval
6. Implement min cap formula (`PPM × 0.015 + 0.05`)
7. Implement max cap (90%) clamping
8. Add support for legacy flat % procs (`ProcsPerMinute == 0`)
9. Add character-specific effect modifier support (rare edge case)

**Testing Strategy:**

- Unit tests for area factor calculation (single, sphere, cone with various radii/arcs)
- Unit tests for min/max cap enforcement
- Unit tests for legacy vs PPM proc distinction
- Integration tests comparing Python proc chances to MidsReborn output for:
  - Fast single-target attacks
  - Slow single-target nukes
  - Small AoEs (10ft radius)
  - Large AoEs (25ft radius)
  - Narrow cones vs wide cones
  - Toggle powers
- Validate against known proc values from game testing

**Edge Cases to Test:**

1. Zero recharge powers (instant recharge)
2. Very fast powers (1-2 second total animation)
3. Very slow powers (120+ second recharge)
4. Extreme AoE radius (30+ feet)
5. Narrow cone (30 degree arc)
6. Character with extreme global recharge (200%+)
7. Legacy flat % procs mixed with PPM procs

## References

- **Related Specs**:
  - Spec 12 (Enhancement IO Procs) - Proc effects and slotting
  - Spec 35 (Proc Interactions) - Multi-target proc mechanics
  - Spec 07 (Power Recharge Modifiers) - Global recharge calculation
  - Spec 11 (Enhancement Slotting) - How procs combine with other enhancements
- **MidsReborn Files**:
  - `Core/Base/Data_Classes/Effect.cs` - PPM properties and calculation
  - `Core/Base/Data_Classes/Power.cs` - AoEModifier calculation
  - `Core/IEffect.cs` - MinProcChance interface
- **Game Documentation**:
  - City of Heroes Wiki - "Procs Per Minute"
  - Paragon Wiki - "Invention Origin Enhancements"
  - Issue 24 patch notes (PPM system introduction, 2012)
  - Homecoming forums - "Proc Math and You" guide
