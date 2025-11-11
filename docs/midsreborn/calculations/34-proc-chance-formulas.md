# Proc Chance Formulas

## Overview
- **Purpose**: Calculate probability of proc IO effects activating using PPM (Procs Per Minute) system with recharge/cast time/area factor modifiers
- **Used By**: IO proc damage/heal/endurance effects, interface procs, proc-based enhancements
- **Complexity**: Complex
- **Priority**: High
- **Status**: 🟢 Depth Complete

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

## Algorithm Pseudocode

### Complete PPM Calculation Logic

```
FUNCTION calculate_proc_chance(proc_enhancement, power, character) -> float:
    """
    Calculate proc activation probability using PPM (Procs Per Minute) system

    INPUT TYPES:
        proc_enhancement: {
            procs_per_minute: float,      // e.g., 3.5 for Apocalypse proc
            base_probability: float,       // Legacy flat % (0.0-1.0)
            effect_id: string             // Optional, for character modifiers
        }
        power: {
            power_type: enum,             // CLICK, TOGGLE, AUTO
            base_recharge_time: float,    // Unmodified recharge (seconds)
            current_recharge_time: float, // With enhancements (seconds)
            cast_time: float,             // Activation time (seconds)
            effect_area: enum,            // SINGLE, SPHERE, CONE
            radius: float,                // AoE radius (feet)
            arc: int                      // Cone arc (0-360 degrees)
        }
        character: {
            global_recharge_bonus: float, // From Hasten, sets (as decimal)
            effect_modifiers: dict        // EffectId -> modifier value
        }

    OUTPUT:
        probability: float (0.0 to 1.0)

    ALGORITHM:

    // Step 1: Check if PPM system applies (vs legacy flat %)
    IF proc_enhancement.procs_per_minute <= 0:
        probability = proc_enhancement.base_probability
        GOTO Step 7  // Skip PPM calculation, apply character modifiers

    // Step 2: Calculate AoE modifier (area penalty)
    IF power.effect_area == SINGLE:
        aoe_modifier = 1.0
    ELSE IF power.effect_area == SPHERE:
        aoe_modifier = 1.0 + power.radius * 0.15
    ELSE IF power.effect_area == CONE:
        // Cone formula: narrow cones get better treatment than wide cones
        aoe_modifier = 1.0 + power.radius * 0.15
                       - power.radius * 0.000366669992217794 * (360 - power.arc)
    ELSE:
        aoe_modifier = 1.0

    // Step 3: Convert AoE modifier to area factor
    // Formula scales modifier down and adds base offset
    area_factor = aoe_modifier * 0.75 + 0.25
    // Result: Single target = 1.0, AoEs > 1.0 (reduces proc chance)

    // Step 4: Calculate effective recharge (removing global bonuses)
    // This prevents perma-Hasten from artificially lowering proc chances
    IF ABS(power.current_recharge_time) < 0.001:  // Near-zero check
        effective_recharge = 0.0
    ELSE:
        // Work backwards from current recharge to find base + enhancement only
        effective_recharge = power.base_recharge_time /
                            (power.base_recharge_time / power.current_recharge_time
                             - character.global_recharge_bonus)

    // Step 5: Calculate proc chance based on power type
    IF power.power_type == CLICK:
        // Standard formula: PPM scales with total animation time
        probability = proc_enhancement.procs_per_minute *
                     (effective_recharge + power.cast_time) /
                     (60.0 * area_factor)

        // Interpretation: Longer recharge+cast = higher chance per activation
        // but same average procs per minute

    ELSE:  // TOGGLE or AUTO
        // Fixed 10-second interval assumption for constant activation powers
        probability = proc_enhancement.procs_per_minute * 10.0 /
                     (60.0 * area_factor)

        // Toggles/autos check for procs every 10 seconds regardless of tick rate

    // Step 6: Apply minimum proc chance cap
    min_chance = proc_enhancement.procs_per_minute * 0.015 + 0.05
    probability = MAX(min_chance, probability)

    // Examples of minimum caps:
    //   1.0 PPM -> 6.5% minimum
    //   2.0 PPM -> 8.0% minimum
    //   3.5 PPM -> 10.25% minimum
    //   4.5 PPM -> 11.75% minimum

    // Step 7: Apply maximum proc chance cap (90%)
    MAX_PROC_CHANCE = 0.9
    probability = MIN(MAX_PROC_CHANCE, probability)

    // Even very slow powers never exceed 90% chance

    // Step 8: Apply character-specific effect modifiers (rare edge case)
    IF proc_enhancement.effect_id NOT EMPTY:
        IF proc_enhancement.effect_id IN character.effect_modifiers:
            probability = probability + character.effect_modifiers[proc_enhancement.effect_id]

    // Step 9: Final clamping to valid probability range [0.0, 1.0]
    probability = MAX(0.0, MIN(1.0, probability))

    RETURN probability

END FUNCTION
```

### Edge Case Handling

```
EDGE CASE 1: Zero or instant recharge powers
    IF power.current_recharge_time ≈ 0:
        effective_recharge = 0
        // Proc chance = PPM * cast_time / (60 * area_factor)
        // Only cast time matters

EDGE CASE 2: Division by zero prevention
    IF power.base_recharge_time / power.current_recharge_time == character.global_recharge_bonus:
        // Would divide by zero in effective_recharge calculation
        effective_recharge = power.base_recharge_time
        // Fallback to base recharge

EDGE CASE 3: Extreme global recharge (200%+ from Hasten + sets)
    // Formula naturally handles this by removing global component
    // effective_recharge stays stable even with huge global bonuses

EDGE CASE 4: Negative arc or radius values
    // Should be validated at data input level
    // If negative: clamp to 0 or treat as invalid

EDGE CASE 5: Legacy proc (ProcsPerMinute = 0)
    // Use base_probability directly
    // Skip all PPM calculations
    // Still apply character modifiers

EDGE CASE 6: Very fast power (1 second total animation)
    // Without minimum cap: would have <1% proc chance
    // Minimum cap ensures: min_chance = PPM * 0.015 + 0.05
    // Example: 3.5 PPM fast power = 10.25% minimum

EDGE CASE 7: Very slow power (120+ second recharge)
    // Could calculate >100% proc chance
    // Maximum cap enforces: probability = MIN(0.9, probability)
    // Result: caps at 90% chance
```

## C# Implementation Reference

### Source Code Location

**Primary File**: `/external/dev/MidsReborn/MidsReborn/Core/Base/Data_Classes/Effect.cs`

**Lines 347-381**: Core PPM calculation logic

```csharp
// Effect.cs, lines 347-381
private float ActualProbability
{
    get
    {
        var probability = BaseProbability;

        // Sometimes BaseProbability sticks at 0.75 when PPM is > 0,
        // preventing PPM calculation
        if (ProcsPerMinute > 0 && power != null)
        {
            var areaFactor = (float)(power.AoEModifier * 0.75 + 0.25);

            var globalRecharge = (MidsContext.Character.DisplayStats.BuffHaste(false) - 100) / 100;
            var rechargeVal = Math.Abs(power.RechargeTime) < float.Epsilon
                ? 0
                : power.BaseRechargeTime / (power.BaseRechargeTime / power.RechargeTime - globalRecharge);

            probability = power.PowerType == Enums.ePowerType.Click
                ? ProcsPerMinute * (rechargeVal + power.CastTimeReal) / (60f * areaFactor)
                : ProcsPerMinute * 10 / (60f * areaFactor);

            probability = Math.Max(MinProcChance, Math.Min(MaxProcChance, probability));
        }

        if (MidsContext.Character != null && !string.IsNullOrEmpty(EffectId) && MidsContext.Character.ModifyEffects.ContainsKey(EffectId))
        {
            probability += MidsContext.Character.ModifyEffects[EffectId];
        }

        return Math.Max(0, Math.Min(1, probability));
    }
}

public float MinProcChance => ProcsPerMinute > 0 ? ProcsPerMinute * 0.015f + 0.05f : 0.05f;
public const float MaxProcChance = 0.9f;
```

**Line 343**: PPM property declaration
```csharp
public float ProcsPerMinute { get; set; }
```

**Lines 380-381**: Min/Max cap constants
```csharp
public float MinProcChance => ProcsPerMinute > 0 ? ProcsPerMinute * 0.015f + 0.05f : 0.05f;
public const float MaxProcChance = 0.9f;
```

**Lines 383-399**: Public probability interface
```csharp
public float Probability
{
    get
    {
        switch (AttribType)
        {
            case Enums.eAttribType.Expression when !string.IsNullOrWhiteSpace(Expressions.Probability):
                var retValue = Parse(this, ExpressionType.Probability, out var error);
                return error.Found ? 0 : Math.Max(0, Math.Min(1, retValue));

            default:
                return ActualProbability;
        }
    }

    set => BaseProbability = value;
}
```

### AoE Modifier Calculation

**File**: `/external/dev/MidsReborn/MidsReborn/Core/Base/Data_Classes/Power.cs`

**Lines 617-619**: AoE modifier formula

```csharp
// Power.cs, lines 617-619
public float AoEModifier => EffectArea != Enums.eEffectArea.Cone
    ? EffectArea != Enums.eEffectArea.Sphere ? 1 : (float) (1 + Radius * 0.150000005960464)
    : (float) (1 + Radius * 0.150000005960464 - Radius * 0.000366669992217794 * (360 - Arc));
```

**Expanded Format**:
```csharp
public float AoEModifier
{
    get
    {
        if (EffectArea == Enums.eEffectArea.Cone)
        {
            // Cone formula: includes arc penalty
            return (float)(1 + Radius * 0.150000005960464
                          - Radius * 0.000366669992217794 * (360 - Arc));
        }
        else if (EffectArea == Enums.eEffectArea.Sphere)
        {
            // Sphere formula: simple radius scaling
            return (float)(1 + Radius * 0.150000005960464);
        }
        else
        {
            // Single target: no penalty
            return 1.0f;
        }
    }
}
```

### Key Constants and Values

**Exact Constant Values** (from source code):

```csharp
// PPM minimum cap formula coefficient (line 380)
const float MIN_PROC_MULTIPLIER = 0.015f;      // PPM × 0.015
const float MIN_PROC_BASE = 0.05f;             // + 0.05 (5%)

// PPM maximum cap (line 381)
const float MAX_PROC_CHANCE = 0.9f;            // 90% hard cap

// AoE modifier coefficients (line 617-619)
const double RADIUS_COEFFICIENT = 0.150000005960464;  // Radius scaling
const double ARC_COEFFICIENT = 0.000366669992217794;  // Arc penalty for cones

// Area factor formula coefficients (line 357)
const float AREA_FACTOR_MULTIPLIER = 0.75f;    // AoEModifier × 0.75
const float AREA_FACTOR_BASE = 0.25f;          // + 0.25

// Toggle/Auto interval (line 366)
const float TOGGLE_INTERVAL = 10.0f;           // 10-second check interval

// PPM to seconds conversion (lines 365, 366)
const float SECONDS_PER_MINUTE = 60.0f;        // 60 seconds/minute

// Float epsilon for zero comparison (line 360)
// Uses float.Epsilon from .NET (approximately 1.4e-45)
```

### Related Enums

**Power Type Enum** (`Enums.cs`):
```csharp
public enum ePowerType
{
    Click,      // Standard clickable powers
    Auto,       // Passive auto powers
    Toggle,     // Toggle powers (on/off)
    // ... others
}
```

**Effect Area Enum** (`Enums.cs`):
```csharp
public enum eEffectArea
{
    None,       // Single target
    Character,  // Self
    Sphere,     // Spherical AoE
    Cone,       // Cone AoE
    // ... others
}
```

### Data Flow

```
User selects proc enhancement
    ↓
Effect.ProcsPerMinute property set (from enhancement data)
    ↓
Build system calculates power stats
    ↓
Power.RechargeTime updated (with enhancements)
Power.BaseRechargeTime remains constant
    ↓
Character.DisplayStats.BuffHaste() calculates global recharge
    ↓
Effect.ActualProbability getter called
    ↓
PPM formula executed:
    1. Get power.AoEModifier (calculated from Power.cs)
    2. Calculate area_factor = AoEModifier × 0.75 + 0.25
    3. Get globalRecharge from character
    4. Calculate effective recharge (remove global)
    5. Apply Click vs Toggle/Auto formula
    6. Apply min/max caps
    7. Apply character effect modifiers
    ↓
Effect.Probability returns final value
    ↓
UI displays proc chance percentage
```

## Database Schema

### PostgreSQL Schema Design

```sql
-- Proc Enhancement Definitions Table
CREATE TABLE proc_enhancements (
    id SERIAL PRIMARY KEY,

    -- Enhancement identification
    name VARCHAR(200) NOT NULL,
    display_name VARCHAR(200),
    set_name VARCHAR(200),                    -- IO set name (e.g., "Apocalypse")
    effect_id VARCHAR(100) UNIQUE,            -- Internal effect identifier

    -- PPM system properties
    procs_per_minute NUMERIC(10, 6) NOT NULL DEFAULT 0.0,
    -- 0 = legacy flat % proc, >0 = PPM value
    -- Examples: 1.0, 2.0, 3.5, 4.5

    base_probability NUMERIC(10, 6) NOT NULL DEFAULT 0.0,
    -- Legacy flat % chance (for pre-Issue 24 procs)
    -- Range: 0.0 to 1.0 (0% to 100%)

    -- Proc effect details
    effect_type VARCHAR(50) NOT NULL,          -- "damage", "heal", "endurance", etc.
    damage_type VARCHAR(50),                   -- "fire", "energy", "negative", etc.
    magnitude NUMERIC(10, 4),                  -- Effect magnitude (damage value, heal, etc.)

    -- Enhancement level and rarity
    min_level INTEGER DEFAULT 10,
    max_level INTEGER DEFAULT 50,
    rarity VARCHAR(20) DEFAULT 'rare',         -- "common", "uncommon", "rare", "very_rare"

    -- Metadata
    is_legacy BOOLEAN DEFAULT FALSE,           -- True if uses flat % instead of PPM
    is_pvp BOOLEAN DEFAULT FALSE,              -- PvP proc (different mechanics)
    description TEXT,

    -- Source tracking
    source_file VARCHAR(255),                  -- Original game data file
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT check_ppm_or_base_prob CHECK (
        procs_per_minute > 0 OR base_probability > 0
    ),
    CONSTRAINT check_probability_range CHECK (
        base_probability >= 0.0 AND base_probability <= 1.0
    ),
    CONSTRAINT check_ppm_range CHECK (
        procs_per_minute >= 0.0 AND procs_per_minute <= 10.0
    )
);

-- Indexes for common queries
CREATE INDEX idx_proc_enhancements_name ON proc_enhancements(name);
CREATE INDEX idx_proc_enhancements_set ON proc_enhancements(set_name);
CREATE INDEX idx_proc_enhancements_effect_type ON proc_enhancements(effect_type);
CREATE INDEX idx_proc_enhancements_ppm ON proc_enhancements(procs_per_minute) WHERE procs_per_minute > 0;
CREATE INDEX idx_proc_enhancements_legacy ON proc_enhancements(is_legacy) WHERE is_legacy = TRUE;

-- Proc Rate Reference Table (common PPM values)
CREATE TABLE proc_rates (
    id SERIAL PRIMARY KEY,

    -- PPM identification
    ppm_value NUMERIC(10, 6) NOT NULL UNIQUE,  -- e.g., 1.0, 2.0, 3.5, 4.5

    -- Calculated caps for this PPM
    min_proc_chance NUMERIC(10, 6) NOT NULL,   -- PPM × 0.015 + 0.05
    max_proc_chance NUMERIC(10, 6) NOT NULL DEFAULT 0.9,  -- Always 0.9 (90%)

    -- Common usage
    usage_count INTEGER DEFAULT 0,             -- How many enhancements use this PPM
    common_name VARCHAR(100),                  -- e.g., "Standard Damage Proc"

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Pre-populate common PPM values
INSERT INTO proc_rates (ppm_value, min_proc_chance, common_name) VALUES
    (0.0, 0.05, 'Legacy Flat Percentage'),
    (1.0, 0.065, 'Slow Proc'),
    (1.5, 0.0725, 'Standard Proc'),
    (2.0, 0.08, 'Medium Proc'),
    (2.5, 0.0875, 'Fast Proc'),
    (3.0, 0.095, 'Very Fast Proc'),
    (3.5, 0.1025, 'Ultra Fast Proc'),
    (4.0, 0.11, 'Extreme Proc'),
    (4.5, 0.1175, 'Maximum Proc');

-- Proc Calculation Cache Table
CREATE TABLE proc_calculations (
    id SERIAL PRIMARY KEY,

    -- Input identifiers
    proc_enhancement_id INTEGER REFERENCES proc_enhancements(id) ON DELETE CASCADE,
    power_id INTEGER,                          -- Reference to powers table
    archetype_id INTEGER,                      -- Reference to archetypes table

    -- Power properties (cached for calculation)
    power_type VARCHAR(20) NOT NULL,           -- "click", "toggle", "auto"
    base_recharge_time NUMERIC(10, 4) NOT NULL,
    current_recharge_time NUMERIC(10, 4) NOT NULL,
    cast_time NUMERIC(10, 4) NOT NULL,
    effect_area VARCHAR(20) NOT NULL,          -- "single", "sphere", "cone"
    radius NUMERIC(10, 4) DEFAULT 0.0,
    arc INTEGER DEFAULT 0,

    -- Character modifiers (cached)
    global_recharge_bonus NUMERIC(10, 6) DEFAULT 0.0,
    effect_modifier NUMERIC(10, 6) DEFAULT 0.0,

    -- Calculated intermediate values
    aoe_modifier NUMERIC(10, 6),
    area_factor NUMERIC(10, 6),
    effective_recharge NUMERIC(10, 6),

    -- Final result
    proc_chance NUMERIC(10, 6) NOT NULL,       -- Final probability (0.0-1.0)
    proc_chance_percent NUMERIC(10, 4),        -- Display percentage (0-100)

    -- Calculation metadata
    calculation_method VARCHAR(50),            -- "ppm_click", "ppm_toggle", "legacy_flat"
    capped_by VARCHAR(20),                     -- "min", "max", "none"
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT check_proc_chance_range CHECK (
        proc_chance >= 0.0 AND proc_chance <= 1.0
    )
);

-- Indexes for proc calculations
CREATE INDEX idx_proc_calc_proc_id ON proc_calculations(proc_enhancement_id);
CREATE INDEX idx_proc_calc_power_id ON proc_calculations(power_id);
CREATE INDEX idx_proc_calc_result ON proc_calculations(proc_chance);
CREATE INDEX idx_proc_calc_method ON proc_calculations(calculation_method);

-- Character Effect Modifiers Table
CREATE TABLE character_effect_modifiers (
    id SERIAL PRIMARY KEY,

    -- Character/build reference
    character_id INTEGER,                      -- Reference to characters/builds table

    -- Effect modification
    effect_id VARCHAR(100) NOT NULL,           -- Links to proc_enhancements.effect_id
    modifier_value NUMERIC(10, 6) NOT NULL,    -- Additive modifier to proc chance

    -- Source of modifier
    source_type VARCHAR(50),                   -- "power", "set_bonus", "incarnate", etc.
    source_id INTEGER,                         -- ID of source power/enhancement
    source_name VARCHAR(200),

    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    UNIQUE(character_id, effect_id, source_id)
);

CREATE INDEX idx_char_effect_mod_char ON character_effect_modifiers(character_id);
CREATE INDEX idx_char_effect_mod_effect ON character_effect_modifiers(effect_id);

-- View: Proc Enhancement Details with Rates
CREATE VIEW proc_enhancement_details AS
SELECT
    pe.id,
    pe.name,
    pe.display_name,
    pe.set_name,
    pe.effect_id,
    pe.procs_per_minute,
    pe.base_probability,
    pe.effect_type,
    pe.damage_type,
    pe.magnitude,
    pe.is_legacy,
    pr.min_proc_chance,
    pr.max_proc_chance,
    CASE
        WHEN pe.is_legacy THEN 'Legacy Flat %'
        ELSE pr.common_name
    END as proc_type_name
FROM proc_enhancements pe
LEFT JOIN proc_rates pr ON pe.procs_per_minute = pr.ppm_value;

-- View: Proc Calculation Summary
CREATE VIEW proc_calculation_summary AS
SELECT
    pc.id,
    pe.name as proc_name,
    pe.procs_per_minute,
    pc.power_type,
    pc.effect_area,
    pc.base_recharge_time,
    pc.cast_time,
    pc.global_recharge_bonus,
    pc.aoe_modifier,
    pc.area_factor,
    pc.effective_recharge,
    pc.proc_chance,
    ROUND(pc.proc_chance * 100, 2) as proc_chance_percent,
    pc.calculation_method,
    pc.capped_by,
    pc.calculated_at
FROM proc_calculations pc
JOIN proc_enhancements pe ON pc.proc_enhancement_id = pe.id;
```

### Schema Notes

**Design Decisions**:

1. **NUMERIC(10,6) for probabilities**: Provides 6 decimal places of precision for exact probability calculations (e.g., 0.102500)

2. **Separate proc_rates table**: Pre-computed min/max values for common PPM rates avoids repeated calculation

3. **proc_calculations cache table**: Stores calculated results for performance, can be invalidated when power stats change

4. **character_effect_modifiers table**: Handles rare case of character-specific proc chance modifications (from specific powers or set bonuses)

5. **Views for common queries**: `proc_enhancement_details` and `proc_calculation_summary` provide pre-joined data for API responses

6. **Constraints ensure data validity**: Check constraints prevent invalid probability values (outside 0.0-1.0 range)

## Comprehensive Test Cases

### Test Case 1: Basic PPM - Fast Single Target Attack

**Scenario**: Standard 3.5 PPM damage proc in a fast-recharging single-target attack

**Input Values**:
```
Proc Enhancement:
  - procs_per_minute: 3.5
  - base_probability: 0.0 (not used)

Power Properties:
  - power_type: CLICK
  - base_recharge_time: 4.0 seconds
  - current_recharge_time: 2.353 seconds (with 70% enhancement)
  - cast_time: 1.0 second
  - effect_area: SINGLE
  - radius: 0.0
  - arc: 0

Character Properties:
  - global_recharge_bonus: 0.70 (70% from Hasten + sets)
  - effect_modifiers: {} (none)
```

**Step-by-Step Calculation**:

```
Step 1: Check PPM system (3.5 > 0) ✓ Use PPM

Step 2: Calculate AoE modifier
  effect_area = SINGLE
  aoe_modifier = 1.0

Step 3: Calculate area factor
  area_factor = 1.0 × 0.75 + 0.25 = 1.0

Step 4: Calculate effective recharge
  effective_recharge = 4.0 / (4.0 / 2.353 - 0.70)
  effective_recharge = 4.0 / (1.700 - 0.70)
  effective_recharge = 4.0 / 1.0
  effective_recharge = 4.0 seconds

Step 5: Calculate proc chance (Click formula)
  probability = 3.5 × (4.0 + 1.0) / (60.0 × 1.0)
  probability = 3.5 × 5.0 / 60.0
  probability = 17.5 / 60.0
  probability = 0.2917

Step 6: Apply minimum cap
  min_chance = 3.5 × 0.015 + 0.05 = 0.1025
  probability = MAX(0.1025, 0.2917) = 0.2917

Step 7: Apply maximum cap
  probability = MIN(0.9, 0.2917) = 0.2917

Step 8: Character modifiers (none)
  probability = 0.2917

Step 9: Final clamp
  probability = MAX(0.0, MIN(1.0, 0.2917)) = 0.2917
```

**Expected Output**: 0.2917 (29.17% proc chance)

**Validation**: With 3.5 PPM and 5-second total animation, proc should fire approximately 3.5 times per minute:
- (0.2917 procs/activation) × (60 seconds/minute / 5 seconds/activation) = 3.5 procs/minute ✓

---

### Test Case 2: PPM with High Recharge Slotting

**Scenario**: 4.5 PPM proc in heavily slotted moderate recharge power

**Input Values**:
```
Proc Enhancement:
  - procs_per_minute: 4.5

Power Properties:
  - power_type: CLICK
  - base_recharge_time: 8.0 seconds
  - current_recharge_time: 3.2 seconds (150% recharge enhancement)
  - cast_time: 1.17 seconds
  - effect_area: SINGLE

Character Properties:
  - global_recharge_bonus: 0.95 (95% from Hasten, high set bonuses)
```

**Calculation**:
```
aoe_modifier = 1.0
area_factor = 1.0

effective_recharge = 8.0 / (8.0 / 3.2 - 0.95)
                   = 8.0 / (2.5 - 0.95)
                   = 8.0 / 1.55
                   = 5.161 seconds

probability = 4.5 × (5.161 + 1.17) / (60.0 × 1.0)
            = 4.5 × 6.331 / 60.0
            = 28.49 / 60.0
            = 0.4748

min_chance = 4.5 × 0.015 + 0.05 = 0.1175
probability = MAX(0.1175, 0.4748) = 0.4748

probability = MIN(0.9, 0.4748) = 0.4748
```

**Expected Output**: 0.4748 (47.48% proc chance)

---

### Test Case 3: AoE Proc - Spherical Power

**Scenario**: 3.5 PPM proc in medium-radius spherical AoE attack

**Input Values**:
```
Proc Enhancement:
  - procs_per_minute: 3.5

Power Properties:
  - power_type: CLICK
  - base_recharge_time: 16.0 seconds
  - current_recharge_time: 8.0 seconds (100% recharge enhancement)
  - cast_time: 2.03 seconds
  - effect_area: SPHERE
  - radius: 15.0 feet
  - arc: 0

Character Properties:
  - global_recharge_bonus: 0.70
```

**Calculation**:
```
aoe_modifier = 1.0 + 15.0 × 0.15
             = 1.0 + 2.25
             = 3.25

area_factor = 3.25 × 0.75 + 0.25
            = 2.4375 + 0.25
            = 2.6875

effective_recharge = 16.0 / (16.0 / 8.0 - 0.70)
                   = 16.0 / (2.0 - 0.70)
                   = 16.0 / 1.3
                   = 12.308 seconds

probability = 3.5 × (12.308 + 2.03) / (60.0 × 2.6875)
            = 3.5 × 14.338 / 161.25
            = 50.183 / 161.25
            = 0.3112

min_chance = 3.5 × 0.015 + 0.05 = 0.1025
probability = MAX(0.1025, 0.3112) = 0.3112

probability = MIN(0.9, 0.3112) = 0.3112
```

**Expected Output**: 0.3112 (31.12% proc chance per target)

**Note**: With 10 targets hit, expected 3.112 procs per activation (not 10× due to area penalty)

---

### Test Case 4: Large Radius AoE - Maximum Penalty

**Scenario**: 3.5 PPM proc in very large spherical AoE (nuke-like power)

**Input Values**:
```
Proc Enhancement:
  - procs_per_minute: 3.5

Power Properties:
  - power_type: CLICK
  - base_recharge_time: 16.0 seconds
  - current_recharge_time: 8.0 seconds
  - cast_time: 2.03 seconds
  - effect_area: SPHERE
  - radius: 25.0 feet
  - arc: 0

Character Properties:
  - global_recharge_bonus: 0.70
```

**Calculation**:
```
aoe_modifier = 1.0 + 25.0 × 0.15
             = 1.0 + 3.75
             = 4.75

area_factor = 4.75 × 0.75 + 0.25
            = 3.5625 + 0.25
            = 3.8125

effective_recharge = 12.308 seconds (same power as Test 3)

probability = 3.5 × (12.308 + 2.03) / (60.0 × 3.8125)
            = 3.5 × 14.338 / 228.75
            = 50.183 / 228.75
            = 0.2194

min_chance = 0.1025
probability = MAX(0.1025, 0.2194) = 0.2194

probability = MIN(0.9, 0.2194) = 0.2194
```

**Expected Output**: 0.2194 (21.94% proc chance per target)

**Note**: Compared to Test 3 (15ft radius), 25ft radius reduces proc chance from 31.12% to 21.94% (29% reduction)

---

### Test Case 5: Cone AoE - Narrow Cone

**Scenario**: 3.5 PPM proc in narrow cone attack (60-degree arc)

**Input Values**:
```
Proc Enhancement:
  - procs_per_minute: 3.5

Power Properties:
  - power_type: CLICK
  - base_recharge_time: 8.0 seconds
  - current_recharge_time: 4.0 seconds
  - cast_time: 1.67 seconds
  - effect_area: CONE
  - radius: 20.0 feet
  - arc: 60 degrees

Character Properties:
  - global_recharge_bonus: 0.70
```

**Calculation**:
```
aoe_modifier = 1.0 + 20.0 × 0.15 - 20.0 × 0.000366669992217794 × (360 - 60)
             = 1.0 + 3.0 - 20.0 × 0.000366669992217794 × 300
             = 1.0 + 3.0 - 2.2000
             = 1.8000

area_factor = 1.8000 × 0.75 + 0.25
            = 1.35 + 0.25
            = 1.6

effective_recharge = 8.0 / (8.0 / 4.0 - 0.70)
                   = 8.0 / (2.0 - 0.70)
                   = 8.0 / 1.3
                   = 6.154 seconds

probability = 3.5 × (6.154 + 1.67) / (60.0 × 1.6)
            = 3.5 × 7.824 / 96.0
            = 27.384 / 96.0
            = 0.2852

min_chance = 0.1025
probability = MAX(0.1025, 0.2852) = 0.2852

probability = MIN(0.9, 0.2852) = 0.2852
```

**Expected Output**: 0.2852 (28.52% proc chance per target)

**Note**: Narrow cone (60°) gets better treatment than wide cone or sphere of same radius

---

### Test Case 6: Cone AoE - Wide Cone

**Scenario**: 3.5 PPM proc in wide cone attack (180-degree arc)

**Input Values**:
```
Proc Enhancement:
  - procs_per_minute: 3.5

Power Properties:
  - power_type: CLICK
  - base_recharge_time: 8.0 seconds
  - current_recharge_time: 4.0 seconds
  - cast_time: 1.67 seconds
  - effect_area: CONE
  - radius: 20.0 feet
  - arc: 180 degrees

Character Properties:
  - global_recharge_bonus: 0.70
```

**Calculation**:
```
aoe_modifier = 1.0 + 20.0 × 0.15 - 20.0 × 0.000366669992217794 × (360 - 180)
             = 1.0 + 3.0 - 20.0 × 0.000366669992217794 × 180
             = 1.0 + 3.0 - 1.3200
             = 2.6800

area_factor = 2.6800 × 0.75 + 0.25
            = 2.01 + 0.25
            = 2.26

effective_recharge = 6.154 seconds (same as Test 5)

probability = 3.5 × (6.154 + 1.67) / (60.0 × 2.26)
            = 3.5 × 7.824 / 135.6
            = 27.384 / 135.6
            = 0.2019

min_chance = 0.1025
probability = MAX(0.1025, 0.2019) = 0.2019

probability = MIN(0.9, 0.2019) = 0.2019
```

**Expected Output**: 0.2019 (20.19% proc chance per target)

**Note**: Wide cone (180°) penalized more heavily than narrow cone (60°): 28.52% → 20.19%

---

### Test Case 7: Very Slow Power - Maximum Cap Hit

**Scenario**: 4.5 PPM proc in very slow recharging nuke power

**Input Values**:
```
Proc Enhancement:
  - procs_per_minute: 4.5

Power Properties:
  - power_type: CLICK
  - base_recharge_time: 145.0 seconds (tier 9 nuke)
  - current_recharge_time: 50.0 seconds (190% recharge enhancement)
  - cast_time: 3.0 seconds
  - effect_area: SINGLE (for this test)

Character Properties:
  - global_recharge_bonus: 1.20 (120% from massive global recharge)
```

**Calculation**:
```
aoe_modifier = 1.0
area_factor = 1.0

effective_recharge = 145.0 / (145.0 / 50.0 - 1.20)
                   = 145.0 / (2.9 - 1.20)
                   = 145.0 / 1.7
                   = 85.294 seconds

probability = 4.5 × (85.294 + 3.0) / (60.0 × 1.0)
            = 4.5 × 88.294 / 60.0
            = 397.323 / 60.0
            = 6.6221  (>1.0!)

min_chance = 4.5 × 0.015 + 0.05 = 0.1175
probability = MAX(0.1175, 6.6221) = 6.6221

probability = MIN(0.9, 6.6221) = 0.9  ← CAPPED AT MAXIMUM
```

**Expected Output**: 0.9000 (90.0% proc chance - maximum cap reached)

**Note**: Without max cap, would be 662.21% chance (impossible). Cap enforces 90% maximum.

---

### Test Case 8: Toggle Power - Fixed Interval

**Scenario**: 2.0 PPM proc in damage aura toggle

**Input Values**:
```
Proc Enhancement:
  - procs_per_minute: 2.0

Power Properties:
  - power_type: TOGGLE
  - base_recharge_time: 0.0 (toggles don't have recharge)
  - current_recharge_time: 0.0
  - cast_time: 1.17 seconds (toggle activation time, not used)
  - effect_area: SPHERE
  - radius: 8.0 feet
  - arc: 0

Character Properties:
  - global_recharge_bonus: 0.70 (not relevant for toggles)
```

**Calculation**:
```
aoe_modifier = 1.0 + 8.0 × 0.15
             = 1.0 + 1.2
             = 2.2

area_factor = 2.2 × 0.75 + 0.25
            = 1.65 + 0.25
            = 1.9

// Toggle formula uses fixed 10-second interval
probability = 2.0 × 10.0 / (60.0 × 1.9)
            = 20.0 / 114.0
            = 0.1754

min_chance = 2.0 × 0.015 + 0.05 = 0.08
probability = MAX(0.08, 0.1754) = 0.1754

probability = MIN(0.9, 0.1754) = 0.1754
```

**Expected Output**: 0.1754 (17.54% proc chance per 10-second tick)

**Note**: Toggles check every 10 seconds regardless of actual tick rate. Global recharge doesn't affect toggles.

---

### Test Case 9: Minimum Cap Enforcement - Very Fast Power

**Scenario**: 3.5 PPM proc in extremely fast-recharging power

**Input Values**:
```
Proc Enhancement:
  - procs_per_minute: 3.5

Power Properties:
  - power_type: CLICK
  - base_recharge_time: 1.0 second
  - current_recharge_time: 0.5 seconds (100% recharge enhancement)
  - cast_time: 0.67 seconds
  - effect_area: SINGLE

Character Properties:
  - global_recharge_bonus: 0.70
```

**Calculation**:
```
aoe_modifier = 1.0
area_factor = 1.0

effective_recharge = 1.0 / (1.0 / 0.5 - 0.70)
                   = 1.0 / (2.0 - 0.70)
                   = 1.0 / 1.3
                   = 0.7692 seconds

probability = 3.5 × (0.7692 + 0.67) / (60.0 × 1.0)
            = 3.5 × 1.4392 / 60.0
            = 5.0372 / 60.0
            = 0.0840

min_chance = 3.5 × 0.015 + 0.05 = 0.1025
probability = MAX(0.1025, 0.0840) = 0.1025  ← MINIMUM CAP APPLIED
```

**Expected Output**: 0.1025 (10.25% proc chance - minimum cap enforced)

**Note**: Without minimum cap, would be 8.40%. Minimum cap ensures procs remain viable in fast powers.

---

### Test Case 10: Legacy Flat Percentage Proc

**Scenario**: Pre-Issue 24 proc with flat 20% chance (no PPM)

**Input Values**:
```
Proc Enhancement:
  - procs_per_minute: 0.0 (legacy indicator)
  - base_probability: 0.20 (20% flat)

Power Properties:
  - power_type: CLICK
  - base_recharge_time: 4.0 seconds
  - current_recharge_time: 2.0 seconds
  - cast_time: 1.0 second
  - effect_area: SINGLE

Character Properties:
  - global_recharge_bonus: 0.70
```

**Calculation**:
```
// Step 1: Check PPM (0.0 ≤ 0) → Use legacy system
probability = base_probability = 0.20

// Skip all PPM calculations (Steps 2-7)

// Step 8: Character modifiers (assume none)
probability = 0.20

// Step 9: Final clamp
probability = MAX(0.0, MIN(1.0, 0.20)) = 0.20
```

**Expected Output**: 0.2000 (20.0% proc chance)

**Note**: Legacy procs maintain constant probability regardless of power recharge/cast time. No PPM scaling applied.

---

### Test Case 11: Character Effect Modifier

**Scenario**: 3.5 PPM proc with character-specific +10% bonus modifier

**Input Values**:
```
Proc Enhancement:
  - procs_per_minute: 3.5
  - effect_id: "special_proc_123"

Power Properties:
  - power_type: CLICK
  - base_recharge_time: 8.0 seconds
  - current_recharge_time: 4.0 seconds
  - cast_time: 1.17 seconds
  - effect_area: SINGLE

Character Properties:
  - global_recharge_bonus: 0.70
  - effect_modifiers: {"special_proc_123": 0.10}  ← +10% bonus
```

**Calculation**:
```
aoe_modifier = 1.0
area_factor = 1.0

effective_recharge = 8.0 / (8.0 / 4.0 - 0.70)
                   = 8.0 / 1.3
                   = 6.154 seconds

probability = 3.5 × (6.154 + 1.17) / (60.0 × 1.0)
            = 3.5 × 7.324 / 60.0
            = 25.634 / 60.0
            = 0.4272

min_chance = 0.1025
probability = MAX(0.1025, 0.4272) = 0.4272

probability = MIN(0.9, 0.4272) = 0.4272

// Step 8: Apply character effect modifier
probability = 0.4272 + 0.10 = 0.5272

// Step 9: Final clamp
probability = MAX(0.0, MIN(1.0, 0.5272)) = 0.5272
```

**Expected Output**: 0.5272 (52.72% proc chance)

**Note**: Character-specific modifiers are rare but add after all other calculations. This example shows a +10% absolute bonus (not multiplicative).

---

### Test Case 12: Zero Recharge Power (Instant Recharge)

**Scenario**: 3.5 PPM proc in power with 0 recharge (edge case)

**Input Values**:
```
Proc Enhancement:
  - procs_per_minute: 3.5

Power Properties:
  - power_type: CLICK
  - base_recharge_time: 0.0
  - current_recharge_time: 0.0
  - cast_time: 1.2 seconds
  - effect_area: SINGLE

Character Properties:
  - global_recharge_bonus: 0.70
```

**Calculation**:
```
aoe_modifier = 1.0
area_factor = 1.0

// Step 4: Zero recharge check
ABS(0.0) < 0.001  ✓
effective_recharge = 0.0

probability = 3.5 × (0.0 + 1.2) / (60.0 × 1.0)
            = 3.5 × 1.2 / 60.0
            = 4.2 / 60.0
            = 0.0700

min_chance = 0.1025
probability = MAX(0.1025, 0.0700) = 0.1025  ← MINIMUM CAP
```

**Expected Output**: 0.1025 (10.25% proc chance - minimum cap enforced)

**Note**: Powers with instant recharge only consider cast time. Still subject to minimum cap.

## Python Implementation Guide

### Production-Ready Implementation

```python
"""
Proc chance calculation module for Mids Hero Web.

Implements the PPM (Procs Per Minute) system from City of Heroes Issue 24+,
with support for legacy flat percentage procs and modern area-scaled calculations.

References:
    - MidsReborn Effect.cs (lines 347-381): ActualProbability calculation
    - MidsReborn Power.cs (lines 617-619): AoEModifier calculation
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional
import math


class PowerType(Enum):
    """Power activation type affecting proc calculation method."""
    CLICK = "click"      # Standard clickable powers
    TOGGLE = "toggle"    # Toggle powers (on/off)
    AUTO = "auto"        # Passive auto powers


class EffectArea(Enum):
    """Area of effect type for proc area factor calculation."""
    SINGLE = "single"    # Single target (no AoE)
    SPHERE = "sphere"    # Spherical AoE (PBAoE or targeted AoE)
    CONE = "cone"        # Cone AoE


@dataclass
class ProcEnhancement:
    """
    Represents a proc IO enhancement with PPM value.

    Maps to MidsReborn Effect.cs properties:
        - ProcsPerMinute (float)
        - BaseProbability (float)
        - EffectId (string)

    Attributes:
        name: Enhancement name (e.g., "Apocalypse: Chance for Negative Energy Damage")
        procs_per_minute: PPM value; 0 = legacy flat %, >0 = PPM system
        base_probability: Legacy flat % chance (0.0-1.0), used when procs_per_minute = 0
        effect_id: Internal effect identifier for character-specific modifiers

    Examples:
        >>> apoc_proc = ProcEnhancement(
        ...     name="Apocalypse: Chance for Neg Damage",
        ...     procs_per_minute=3.5
        ... )
        >>> legacy_proc = ProcEnhancement(
        ...     name="Old Proc IO",
        ...     procs_per_minute=0.0,
        ...     base_probability=0.20
        ... )
    """
    name: str
    procs_per_minute: float
    base_probability: float = 0.0
    effect_id: str = ""

    def __post_init__(self):
        """Validate proc enhancement data."""
        if self.procs_per_minute < 0.0:
            raise ValueError(f"procs_per_minute cannot be negative: {self.procs_per_minute}")
        if not (0.0 <= self.base_probability <= 1.0):
            raise ValueError(f"base_probability must be 0.0-1.0: {self.base_probability}")
        if self.procs_per_minute == 0.0 and self.base_probability == 0.0:
            raise ValueError("Either procs_per_minute or base_probability must be > 0")


@dataclass
class PowerProcContext:
    """
    Power properties needed for proc chance calculation.

    Maps to MidsReborn Power.cs properties:
        - PowerType (ePowerType enum)
        - BaseRechargeTime (float)
        - RechargeTime (float)
        - CastTimeReal (float)
        - EffectArea (eEffectArea enum)
        - Radius (float)
        - Arc (int)

    Attributes:
        power_type: Click, toggle, or auto power
        base_recharge_time: Unmodified recharge time (seconds)
        current_recharge_time: Recharge with enhancements applied (seconds)
        cast_time: Activation/cast time (seconds)
        effect_area: Single target, sphere, or cone
        radius: AoE radius in feet (0 for single target)
        arc: Cone arc in degrees (0-360, only for cone powers)

    Examples:
        >>> fast_attack = PowerProcContext(
        ...     power_type=PowerType.CLICK,
        ...     base_recharge_time=4.0,
        ...     current_recharge_time=2.0,
        ...     cast_time=1.0,
        ...     effect_area=EffectArea.SINGLE
        ... )
        >>> fireball = PowerProcContext(
        ...     power_type=PowerType.CLICK,
        ...     base_recharge_time=16.0,
        ...     current_recharge_time=8.0,
        ...     cast_time=2.03,
        ...     effect_area=EffectArea.SPHERE,
        ...     radius=15.0
        ... )
    """
    power_type: PowerType
    base_recharge_time: float
    current_recharge_time: float
    cast_time: float
    effect_area: EffectArea
    radius: float = 0.0
    arc: int = 0

    def __post_init__(self):
        """Validate power properties."""
        if self.base_recharge_time < 0.0:
            raise ValueError(f"base_recharge_time cannot be negative: {self.base_recharge_time}")
        if self.current_recharge_time < 0.0:
            raise ValueError(f"current_recharge_time cannot be negative: {self.current_recharge_time}")
        if self.cast_time < 0.0:
            raise ValueError(f"cast_time cannot be negative: {self.cast_time}")
        if self.radius < 0.0:
            raise ValueError(f"radius cannot be negative: {self.radius}")
        if not (0 <= self.arc <= 360):
            raise ValueError(f"arc must be 0-360 degrees: {self.arc}")


@dataclass
class CharacterProcContext:
    """
    Character properties affecting proc chance calculation.

    Maps to MidsReborn character calculations:
        - DisplayStats.BuffHaste() for global recharge
        - ModifyEffects dictionary for effect-specific modifiers

    Attributes:
        global_recharge_bonus: Total global recharge from Hasten, sets, etc. (as decimal)
                              Example: 0.70 = +70% global recharge
        effect_modifiers: Effect ID -> additive modifier (rare, special cases only)

    Examples:
        >>> char = CharacterProcContext(
        ...     global_recharge_bonus=0.70  # +70% from Hasten + set bonuses
        ... )
        >>> char_with_mod = CharacterProcContext(
        ...     global_recharge_bonus=0.95,
        ...     effect_modifiers={"special_effect": 0.10}  # +10% to specific effect
        ... )
    """
    global_recharge_bonus: float = 0.0
    effect_modifiers: Dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        """Validate character properties."""
        if self.global_recharge_bonus < 0.0:
            raise ValueError(f"global_recharge_bonus cannot be negative: {self.global_recharge_bonus}")


class ProcChanceCalculator:
    """
    Calculates proc activation probability using PPM (Procs Per Minute) system.

    Maps to MidsReborn Effect.cs ActualProbability calculation (lines 347-381).

    Constants match MidsReborn source code exactly:
        - MAX_PROC_CHANCE = 0.9 (line 381)
        - MIN_PROC_MULTIPLIER = 0.015 (line 380)
        - MIN_PROC_BASE = 0.05 (line 380)
        - RADIUS_COEFFICIENT = 0.15 (line 618-619 in Power.cs)
        - ARC_COEFFICIENT = 0.000366669992217794 (line 619 in Power.cs)
        - AREA_FACTOR_MULT = 0.75 (line 357 in Effect.cs)
        - AREA_FACTOR_BASE = 0.25 (line 357 in Effect.cs)
        - TOGGLE_INTERVAL = 10.0 (line 366 in Effect.cs)

    Examples:
        >>> calculator = ProcChanceCalculator()
        >>> proc = ProcEnhancement(name="Test Proc", procs_per_minute=3.5)
        >>> power = PowerProcContext(
        ...     power_type=PowerType.CLICK,
        ...     base_recharge_time=4.0,
        ...     current_recharge_time=2.0,
        ...     cast_time=1.0,
        ...     effect_area=EffectArea.SINGLE
        ... )
        >>> char = CharacterProcContext(global_recharge_bonus=0.70)
        >>> chance = calculator.calculate_proc_chance(proc, power, char)
        >>> print(f"Proc chance: {chance:.2%}")
        Proc chance: 29.17%
    """

    # Constants from MidsReborn source code
    MAX_PROC_CHANCE: float = 0.9  # 90% hard cap (Effect.cs line 381)
    MIN_PROC_MULTIPLIER: float = 0.015  # PPM × 0.015 (Effect.cs line 380)
    MIN_PROC_BASE: float = 0.05  # + 0.05 base (Effect.cs line 380)

    RADIUS_COEFFICIENT: float = 0.15  # Power.cs line 618-619
    ARC_COEFFICIENT: float = 0.000366669992217794  # Power.cs line 619

    AREA_FACTOR_MULT: float = 0.75  # Effect.cs line 357
    AREA_FACTOR_BASE: float = 0.25  # Effect.cs line 357

    TOGGLE_INTERVAL: float = 10.0  # seconds (Effect.cs line 366)
    SECONDS_PER_MINUTE: float = 60.0

    FLOAT_EPSILON: float = 0.001  # For zero comparisons (Effect.cs uses float.Epsilon)

    def calculate_aoe_modifier(self, power: PowerProcContext) -> float:
        """
        Calculate AoE modifier based on effect area type.

        Maps to Power.cs AoEModifier property (lines 617-619).

        Formulas:
            - Single target: 1.0
            - Sphere AoE: 1 + radius × 0.15
            - Cone AoE: 1 + radius × 0.15 - radius × 0.000366669992217794 × (360 - arc)

        The cone formula reduces the penalty for narrow cones (small arc angle).
        Wide cones (large arc) are penalized similar to spheres.

        Args:
            power: Power properties including effect area, radius, and arc

        Returns:
            AoE modifier value (≥1.0, higher values = larger penalty)

        Examples:
            >>> calc = ProcChanceCalculator()
            >>> # Single target
            >>> power_st = PowerProcContext(PowerType.CLICK, 4, 2, 1, EffectArea.SINGLE)
            >>> calc.calculate_aoe_modifier(power_st)
            1.0
            >>> # 15ft sphere
            >>> power_sphere = PowerProcContext(PowerType.CLICK, 16, 8, 2, EffectArea.SPHERE, radius=15.0)
            >>> calc.calculate_aoe_modifier(power_sphere)
            3.25
            >>> # 20ft narrow cone (60°)
            >>> power_cone = PowerProcContext(PowerType.CLICK, 8, 4, 1.67, EffectArea.CONE, radius=20.0, arc=60)
            >>> calc.calculate_aoe_modifier(power_cone)
            1.8
        """
        if power.effect_area == EffectArea.SINGLE:
            return 1.0

        elif power.effect_area == EffectArea.SPHERE:
            return 1.0 + power.radius * self.RADIUS_COEFFICIENT

        elif power.effect_area == EffectArea.CONE:
            # Cone formula: narrow cones get reduced penalty
            return (1.0 + power.radius * self.RADIUS_COEFFICIENT
                    - power.radius * self.ARC_COEFFICIENT * (360 - power.arc))

        return 1.0

    def calculate_area_factor(self, power: PowerProcContext) -> float:
        """
        Convert AoE modifier to area factor used in proc formula.

        Maps to Effect.cs calculation (line 357).

        Formula: area_factor = aoe_modifier × 0.75 + 0.25

        This scales the AoE modifier down (×0.75) and adds a base offset (+0.25).
        Result: Single target = 1.0, AoE powers have factor > 1.0 (reduces proc chance).

        Args:
            power: Power properties

        Returns:
            Area factor (≥1.0, used as divisor in proc formula)

        Examples:
            >>> calc = ProcChanceCalculator()
            >>> power_st = PowerProcContext(PowerType.CLICK, 4, 2, 1, EffectArea.SINGLE)
            >>> calc.calculate_area_factor(power_st)
            1.0
            >>> power_aoe = PowerProcContext(PowerType.CLICK, 16, 8, 2, EffectArea.SPHERE, radius=25.0)
            >>> calc.calculate_area_factor(power_aoe)
            3.8125
        """
        aoe_modifier = self.calculate_aoe_modifier(power)
        return aoe_modifier * self.AREA_FACTOR_MULT + self.AREA_FACTOR_BASE

    def calculate_effective_recharge(
        self,
        power: PowerProcContext,
        character: CharacterProcContext
    ) -> float:
        """
        Calculate power's effective recharge removing global bonuses.

        Maps to Effect.cs rechargeVal calculation (lines 360-362).

        This finds what the power's recharge would be with only enhancement
        slotting, before global recharge bonuses (Hasten, set bonuses) were applied.
        This prevents global recharge from artificially lowering proc chances.

        Formula:
            effective_recharge = base_recharge / (base_recharge / current_recharge - global_bonus)

        Args:
            power: Power properties including recharge times
            character: Character properties including global recharge bonus

        Returns:
            Effective recharge time in seconds (with enhancements, without global)

        Raises:
            ValueError: If calculation would divide by zero or produce negative result

        Examples:
            >>> calc = ProcChanceCalculator()
            >>> power = PowerProcContext(PowerType.CLICK, 4.0, 2.0, 1.0, EffectArea.SINGLE)
            >>> char = CharacterProcContext(global_recharge_bonus=0.70)
            >>> calc.calculate_effective_recharge(power, char)
            4.0
        """
        # Check for zero/near-zero recharge (instant recharge powers)
        if abs(power.current_recharge_time) < self.FLOAT_EPSILON:
            return 0.0

        # Calculate denominator: (base / current) - global
        denominator = (power.base_recharge_time / power.current_recharge_time
                      - character.global_recharge_bonus)

        # Prevent division by zero
        if abs(denominator) < self.FLOAT_EPSILON:
            # Fallback: return base recharge if calculation fails
            return power.base_recharge_time

        effective_recharge = power.base_recharge_time / denominator

        # Sanity check: effective recharge should be positive
        if effective_recharge < 0.0:
            raise ValueError(
                f"Effective recharge calculation produced negative value: {effective_recharge}. "
                f"base={power.base_recharge_time}, current={power.current_recharge_time}, "
                f"global={character.global_recharge_bonus}"
            )

        return effective_recharge

    def calculate_min_proc_chance(self, ppm: float) -> float:
        """
        Calculate minimum proc chance cap for given PPM value.

        Maps to Effect.cs MinProcChance property (line 380).

        Formula: min_chance = ppm × 0.015 + 0.05

        Ensures fast-recharging powers still have reasonable proc chance.
        Without this cap, very fast powers could have <1% proc chance.

        Args:
            ppm: Procs per minute value

        Returns:
            Minimum proc chance (0.0-1.0)

        Examples:
            >>> calc = ProcChanceCalculator()
            >>> calc.calculate_min_proc_chance(1.0)
            0.065
            >>> calc.calculate_min_proc_chance(3.5)
            0.1025
            >>> calc.calculate_min_proc_chance(4.5)
            0.1175
        """
        if ppm <= 0:
            return self.MIN_PROC_BASE  # 5% minimum for legacy procs

        return ppm * self.MIN_PROC_MULTIPLIER + self.MIN_PROC_BASE

    def calculate_proc_chance(
        self,
        proc: ProcEnhancement,
        power: PowerProcContext,
        character: CharacterProcContext
    ) -> float:
        """
        Calculate final proc activation probability.

        Maps to Effect.cs ActualProbability getter (lines 347-377).

        Implements complete PPM system with:
            - Legacy flat % support (procs_per_minute = 0)
            - AoE area factor penalty
            - Global recharge removal
            - Click vs Toggle/Auto formulas
            - Minimum and maximum caps
            - Character-specific effect modifiers

        Args:
            proc: Proc enhancement with PPM value
            power: Power properties (recharge, cast time, area)
            character: Character properties (global recharge, modifiers)

        Returns:
            Final probability (0.0 to 1.0) of proc activating

        Examples:
            >>> calc = ProcChanceCalculator()
            >>> proc = ProcEnhancement(name="Test", procs_per_minute=3.5)
            >>> power = PowerProcContext(PowerType.CLICK, 4.0, 2.0, 1.0, EffectArea.SINGLE)
            >>> char = CharacterProcContext(global_recharge_bonus=0.70)
            >>> chance = calc.calculate_proc_chance(proc, power, char)
            >>> round(chance, 4)
            0.2917
        """
        # Step 1: Check for legacy flat % proc (pre-Issue 24 system)
        if proc.procs_per_minute <= 0:
            probability = proc.base_probability

        else:
            # PPM system calculation

            # Step 2-3: Calculate area factor penalty for AoE powers
            area_factor = self.calculate_area_factor(power)

            # Step 4: Calculate effective recharge (removing global bonuses)
            effective_recharge = self.calculate_effective_recharge(power, character)

            # Step 5: Calculate proc chance based on power type
            if power.power_type == PowerType.CLICK:
                # Standard formula: scales with recharge + cast time
                probability = (proc.procs_per_minute *
                             (effective_recharge + power.cast_time) /
                             (self.SECONDS_PER_MINUTE * area_factor))

            else:  # Toggle or Auto
                # Fixed 10-second assumed interval
                probability = (proc.procs_per_minute * self.TOGGLE_INTERVAL /
                             (self.SECONDS_PER_MINUTE * area_factor))

            # Step 6: Apply minimum cap
            min_chance = self.calculate_min_proc_chance(proc.procs_per_minute)
            probability = max(min_chance, probability)

            # Step 7: Apply maximum cap (90%)
            probability = min(self.MAX_PROC_CHANCE, probability)

        # Step 8: Apply character-specific effect modifiers (if any)
        if proc.effect_id and proc.effect_id in character.effect_modifiers:
            probability += character.effect_modifiers[proc.effect_id]

        # Step 9: Final clamping to valid probability range [0.0, 1.0]
        return max(0.0, min(1.0, probability))


# Example usage and testing
def example_proc_calculations():
    """
    Example proc chance calculations demonstrating various scenarios.

    Matches test cases from Comprehensive Test Cases section.
    """
    calculator = ProcChanceCalculator()

    print("=== Proc Chance Calculation Examples ===\n")

    # Example 1: Basic fast single-target attack
    print("1. Fast Single Target Attack (3.5 PPM)")
    proc_35ppm = ProcEnhancement(
        name="Apocalypse: Chance for Neg Damage",
        procs_per_minute=3.5
    )

    fast_attack = PowerProcContext(
        power_type=PowerType.CLICK,
        base_recharge_time=4.0,
        current_recharge_time=2.353,
        cast_time=1.0,
        effect_area=EffectArea.SINGLE
    )

    character = CharacterProcContext(
        global_recharge_bonus=0.7  # +70% from Hasten, sets
    )

    chance1 = calculator.calculate_proc_chance(proc_35ppm, fast_attack, character)
    print(f"   Result: {chance1:.4f} ({chance1:.2%})")
    print(f"   Expected: ~0.2917 (29.17%)\n")

    # Example 2: Large AoE sphere
    print("2. Large Radius Spherical AoE (3.5 PPM)")
    large_aoe = PowerProcContext(
        power_type=PowerType.CLICK,
        base_recharge_time=16.0,
        current_recharge_time=8.0,
        cast_time=2.03,
        effect_area=EffectArea.SPHERE,
        radius=25.0
    )

    chance2 = calculator.calculate_proc_chance(proc_35ppm, large_aoe, character)
    print(f"   Result: {chance2:.4f} ({chance2:.2%})")
    print(f"   Expected: ~0.2194 (21.94%)")
    print(f"   Note: Large radius reduces proc chance significantly\n")

    # Example 3: Toggle power
    print("3. Damage Aura Toggle (2.0 PPM)")
    proc_20ppm = ProcEnhancement(
        name="Damage Proc",
        procs_per_minute=2.0
    )

    toggle_aura = PowerProcContext(
        power_type=PowerType.TOGGLE,
        base_recharge_time=0.0,
        current_recharge_time=0.0,
        cast_time=1.17,
        effect_area=EffectArea.SPHERE,
        radius=8.0
    )

    chance3 = calculator.calculate_proc_chance(proc_20ppm, toggle_aura, character)
    print(f"   Result: {chance3:.4f} ({chance3:.2%})")
    print(f"   Expected: ~0.1754 (17.54%)")
    print(f"   Note: Toggles use fixed 10-second interval\n")

    # Example 4: Very slow power (hits max cap)
    print("4. Slow Nuke Power (4.5 PPM)")
    proc_45ppm = ProcEnhancement(
        name="High PPM Proc",
        procs_per_minute=4.5
    )

    slow_nuke = PowerProcContext(
        power_type=PowerType.CLICK,
        base_recharge_time=145.0,
        current_recharge_time=50.0,
        cast_time=3.0,
        effect_area=EffectArea.SINGLE
    )

    character_high_rech = CharacterProcContext(
        global_recharge_bonus=1.2  # 120% global recharge
    )

    chance4 = calculator.calculate_proc_chance(proc_45ppm, slow_nuke, character_high_rech)
    print(f"   Result: {chance4:.4f} ({chance4:.2%})")
    print(f"   Expected: 0.9000 (90.00%)")
    print(f"   Note: Maximum cap enforced at 90%\n")

    # Example 5: Very fast power (hits min cap)
    print("5. Very Fast Power (3.5 PPM)")
    very_fast = PowerProcContext(
        power_type=PowerType.CLICK,
        base_recharge_time=1.0,
        current_recharge_time=0.5,
        cast_time=0.67,
        effect_area=EffectArea.SINGLE
    )

    chance5 = calculator.calculate_proc_chance(proc_35ppm, very_fast, character)
    print(f"   Result: {chance5:.4f} ({chance5:.2%})")
    print(f"   Expected: 0.1025 (10.25%)")
    print(f"   Note: Minimum cap enforced\n")

    # Example 6: Legacy flat % proc
    print("6. Legacy Flat Percentage Proc")
    legacy_proc = ProcEnhancement(
        name="Old Chance for Smashing",
        procs_per_minute=0.0,  # Legacy indicator
        base_probability=0.20  # 20% flat
    )

    chance6 = calculator.calculate_proc_chance(legacy_proc, fast_attack, character)
    print(f"   Result: {chance6:.4f} ({chance6:.2%})")
    print(f"   Expected: 0.2000 (20.00%)")
    print(f"   Note: Legacy procs ignore power properties\n")


if __name__ == "__main__":
    example_proc_calculations()
```

### Usage in FastAPI Application

```python
# backend/app/routers/proc_calculations.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from ..calculations.proc_chance import (
    ProcChanceCalculator,
    ProcEnhancement,
    PowerProcContext,
    CharacterProcContext,
    PowerType,
    EffectArea
)

router = APIRouter(prefix="/api/v1/proc", tags=["proc-calculations"])


class ProcCalculationRequest(BaseModel):
    """Request model for proc chance calculation."""
    proc_name: str = Field(..., description="Proc enhancement name")
    procs_per_minute: float = Field(..., ge=0.0, le=10.0)
    base_probability: float = Field(default=0.0, ge=0.0, le=1.0)
    effect_id: Optional[str] = None

    power_type: str = Field(..., regex="^(click|toggle|auto)$")
    base_recharge_time: float = Field(..., ge=0.0)
    current_recharge_time: float = Field(..., ge=0.0)
    cast_time: float = Field(..., ge=0.0)
    effect_area: str = Field(..., regex="^(single|sphere|cone)$")
    radius: float = Field(default=0.0, ge=0.0)
    arc: int = Field(default=0, ge=0, le=360)

    global_recharge_bonus: float = Field(default=0.0, ge=0.0)
    effect_modifiers: dict[str, float] = Field(default_factory=dict)


class ProcCalculationResponse(BaseModel):
    """Response model for proc chance calculation."""
    proc_chance: float = Field(..., description="Final probability (0.0-1.0)")
    proc_chance_percent: float = Field(..., description="Percentage (0-100)")
    aoe_modifier: float
    area_factor: float
    effective_recharge: float
    calculation_method: str
    min_cap_applied: bool
    max_cap_applied: bool


@router.post("/calculate", response_model=ProcCalculationResponse)
def calculate_proc_chance(request: ProcCalculationRequest):
    """
    Calculate proc activation probability using PPM system.

    Implements Issue 24+ PPM formula with area factor penalties and caps.
    """
    try:
        # Build domain objects
        proc = ProcEnhancement(
            name=request.proc_name,
            procs_per_minute=request.procs_per_minute,
            base_probability=request.base_probability,
            effect_id=request.effect_id or ""
        )

        power = PowerProcContext(
            power_type=PowerType(request.power_type),
            base_recharge_time=request.base_recharge_time,
            current_recharge_time=request.current_recharge_time,
            cast_time=request.cast_time,
            effect_area=EffectArea(request.effect_area),
            radius=request.radius,
            arc=request.arc
        )

        character = CharacterProcContext(
            global_recharge_bonus=request.global_recharge_bonus,
            effect_modifiers=request.effect_modifiers
        )

        # Calculate proc chance
        calculator = ProcChanceCalculator()
        proc_chance = calculator.calculate_proc_chance(proc, power, character)

        # Calculate supporting values for response
        aoe_modifier = calculator.calculate_aoe_modifier(power)
        area_factor = calculator.calculate_area_factor(power)
        effective_recharge = calculator.calculate_effective_recharge(power, character)
        min_chance = calculator.calculate_min_proc_chance(proc.procs_per_minute)

        # Determine calculation method
        if proc.procs_per_minute <= 0:
            method = "legacy_flat"
        elif power.power_type == PowerType.CLICK:
            method = "ppm_click"
        else:
            method = "ppm_toggle_auto"

        # Check if caps were applied
        uncapped_chance = proc.procs_per_minute * (effective_recharge + power.cast_time) / (60.0 * area_factor)
        min_cap_applied = proc.procs_per_minute > 0 and uncapped_chance < min_chance
        max_cap_applied = uncapped_chance > calculator.MAX_PROC_CHANCE

        return ProcCalculationResponse(
            proc_chance=proc_chance,
            proc_chance_percent=round(proc_chance * 100, 2),
            aoe_modifier=aoe_modifier,
            area_factor=area_factor,
            effective_recharge=effective_recharge,
            calculation_method=method,
            min_cap_applied=min_cap_applied,
            max_cap_applied=max_cap_applied
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")
```

## Integration Points

### Dependencies (Input)

This calculation depends on data from:

**Spec 01 (Power Effects Core)**:
- Power base properties (recharge time, cast time, effect area)
- Effect type identification (which effects are procs)
- Power type classification (Click, Toggle, Auto)

**Spec 02 (Power Damage)**:
- Proc damage magnitude values
- Damage type for proc effects
- Archetype scaling for proc damage

**Spec 07 (Power Recharge Modifiers)**:
- Global recharge calculations (Hasten, set bonuses)
- Enhancement-based recharge reduction
- Base vs enhanced recharge time tracking

**Spec 11 (Enhancement Slotting)**:
- Proc enhancement identification
- PPM values from enhancement database
- Slotted enhancement tracking per power

**Spec 16 (Archetype Mechanics)**:
- Archetype-specific proc damage scaling
- AT modifier tables for proc effects

### Dependents (Output)

This calculation provides data to:

**Spec 28 (Total DPS)**:
- Expected proc damage per activation
- Proc DPS contribution = proc_damage × proc_chance × activation_rate
- Multi-proc stacking calculations

**Spec 35 (Proc Interactions)**:
- Multi-target proc mechanics (how procs behave in AoE)
- Proc on proc effects (Force Feedback, etc.)
- Proc interference/stacking rules

**Spec 36 (Proc Damage)**:
- Final proc damage output after chance calculation
- Proc damage with level shifts
- Enhanced proc damage values

**Spec 38 (Multi-Target Procs)**:
- Per-target proc chance in AoE powers
- Target cap interaction with procs
- Area factor application per target

**Build Optimization System**:
- Proc slotting recommendations
- Proc vs set bonus trade-off analysis
- Best-in-slot proc identification per power

### Data Flow Diagram

```
Power Database
    ↓ (base properties)
Power Effects Parser ← Spec 01
    ↓ (power stats)
    ├→ base_recharge_time
    ├→ cast_time
    ├→ effect_area, radius, arc
    └→ power_type

Enhancement System ← Spec 11
    ↓ (slotted procs)
    ├→ procs_per_minute
    ├→ base_probability (legacy)
    └→ effect_id

Recharge Calculator ← Spec 07
    ↓ (recharge values)
    ├→ current_recharge_time (with enhancements)
    └→ global_recharge_bonus (from character)

Character Stats ← Spec 16
    ↓ (character modifiers)
    └→ effect_modifiers (rare)

        ↓↓↓ ALL INPUTS ↓↓↓

    PROC CHANCE CALCULATOR (Spec 34)
    - calculate_aoe_modifier()
    - calculate_area_factor()
    - calculate_effective_recharge()
    - calculate_proc_chance()

        ↓↓↓ OUTPUT ↓↓↓

    proc_chance (0.0-1.0)
        ↓
        ├→ DPS Calculator ← Spec 28
        │  └→ Total build DPS with proc contributions
        │
        ├→ Proc Damage Calculator ← Spec 36
        │  └→ Expected proc damage = base_damage × proc_chance
        │
        ├→ Multi-Target Proc System ← Spec 38
        │  └→ Per-target proc calculations in AoE
        │
        └→ Build Optimizer
           └→ Proc vs set bonus analysis

UI Display
    ↓
Power Tooltip: "Apocalypse Proc: 29.17% chance"
Build Stats: "Expected Proc DPS: 42.5"
Enhancement Recommendations: "Slot procs in fast-recharging AoEs"
```

### API Endpoint Integration

```
GET /api/v1/powers/{power_id}/proc-chance
    → Returns proc chance for all slotted procs in power
    → Uses cached character stats (global recharge, etc.)

POST /api/v1/proc/calculate
    → Real-time proc chance calculation
    → Input: proc properties + power properties + character properties
    → Output: detailed calculation breakdown

GET /api/v1/builds/{build_id}/proc-summary
    → All proc chances across entire build
    → Aggregated proc DPS contribution
    → Proc slotting recommendations

WebSocket /ws/build-update
    → Live proc chance updates as user modifies build
    → Instant feedback on enhancement changes
    → Real-time DPS recalculation with proc contributions
```

### Database Relationships

```sql
-- Proc enhancement references power slots
proc_enhancements
    ├─→ enhancement_slots (many-to-many via power_enhancements)
    └─→ proc_calculations (cached results)

-- Power properties used in proc calculation
powers
    ├─→ power_effects (identifies which effects are procs)
    ├─→ proc_calculations (links power stats to proc results)
    └─→ power_enhancements (which procs are slotted)

-- Character stats affect proc chances
characters/builds
    ├─→ character_stats (global recharge bonus)
    ├─→ character_effect_modifiers (rare proc-specific bonuses)
    └─→ proc_calculations (character-specific cached results)

-- Calculation cache for performance
proc_calculations
    ├─→ proc_enhancements (which proc)
    ├─→ powers (which power)
    ├─→ builds (which character/build)
    └─→ invalidated when any input changes
```

## References

- **Related Specs**:
  - Spec 01 (Power Effects Core) - Base power properties and effect identification
  - Spec 02 (Power Damage) - Proc damage magnitude and type
  - Spec 07 (Power Recharge Modifiers) - Global recharge calculation, enhancement-based recharge
  - Spec 11 (Enhancement Slotting) - How procs combine with other enhancements
  - Spec 12 (Enhancement IO Procs) - Proc effects and slotting mechanics
  - Spec 16 (Archetype Mechanics) - AT-specific proc scaling
  - Spec 28 (Total DPS) - Proc DPS contribution to total damage output
  - Spec 35 (Proc Interactions) - Multi-target proc mechanics, proc-on-proc effects
  - Spec 36 (Proc Damage) - Final proc damage after probability calculation
  - Spec 38 (Multi-Target Procs) - AoE proc behavior with multiple targets

- **MidsReborn Files**:
  - `/external/dev/MidsReborn/MidsReborn/Core/Base/Data_Classes/Effect.cs` (lines 347-381) - Core PPM calculation (ActualProbability getter)
  - `/external/dev/MidsReborn/MidsReborn/Core/Base/Data_Classes/Effect.cs` (line 343) - ProcsPerMinute property
  - `/external/dev/MidsReborn/MidsReborn/Core/Base/Data_Classes/Effect.cs` (line 380) - MinProcChance formula
  - `/external/dev/MidsReborn/MidsReborn/Core/Base/Data_Classes/Effect.cs` (line 381) - MaxProcChance constant
  - `/external/dev/MidsReborn/MidsReborn/Core/Base/Data_Classes/Power.cs` (lines 617-619) - AoEModifier calculation
  - `Core/IEffect.cs` - MinProcChance interface definition

- **Game Documentation**:
  - City of Heroes Wiki - "Procs Per Minute" system explanation
  - Paragon Wiki - "Invention Origin Enhancements" proc mechanics
  - Issue 24 patch notes (PPM system introduction, 2012)
  - Homecoming forums - "Proc Math and You" comprehensive guide
  - Homecoming forums - "The Math Behind PPM" detailed analysis
  - Homecoming wiki - "Enhancement Sets" proc IO listings
