# Suppression Mechanics

## Overview
- **Purpose**: Effects that are temporarily disabled or reduced when certain conditions are met (combat, movement, power activation, stealth breaking)
- **Used By**: Power effect calculations, build planning, UI display
- **Complexity**: Moderate
- **Priority**: Low
- **Status**: 🟡 Breadth Complete

## MidsReborn Implementation

### Primary Location
- **File**: `Core/Base/Data_Classes/Effect.cs`
- **Property**: `Suppression` (type: `Enums.eSuppress`)
- **Related Files**:
  - `Core/Enums.cs` - `eSuppress` enum definition (lines 1132-1148)
  - `Core/Base/Data_Classes/Power.cs` - Suppression checks in power calculations
  - `Core/ConfigData.cs` - Global suppression settings
  - `Forms/OptionsMenuItems/frmCalcOpt.cs` - User configuration UI

### Suppression Types

The `eSuppress` enum in `Core/Enums.cs` (lines 1132-1148) defines suppression conditions as flags:

```csharp
[Flags]
public enum eSuppress
{
    None = 0,
    Held = 1,                     // Suppressed when held
    Sleep = 2,                    // Suppressed when asleep
    Stunned = 4,                  // Suppressed when stunned
    Immobilized = 8,              // Suppressed when immobilized
    Terrorized = 16,              // Suppressed when feared
    Knocked = 32,                 // Suppressed when knocked down/back
    Attacked = 64,                // Suppressed when attacking (combat)
    HitByFoe = 128,               // Suppressed when hit by enemy (combat)
    MissionObjectClick = 256,     // Suppressed when clicking objectives
    ActivateAttackClick = 512,    // Suppressed during power activation
    Damaged = 1024,               // Suppressed when taking damage
    Phased1 = 2048,               // Suppressed when phased
    Confused = 4096               // Suppressed when confused
}
```

**Note**: This is a `[Flags]` enum, so multiple suppression conditions can be combined using bitwise OR operations.

### High-Level Algorithm

```
Suppression Check Process:

1. Effect has Suppression field (Enums.eSuppress flags)
   - Default: eSuppress.None (no suppression)
   - Can be combination of multiple flags

2. Global suppression config (MidsContext.Config.Suppression)
   - User-configurable "active suppression scenarios"
   - Defaults to None (suppression disabled for build planning)
   - UI checkbox list in Options > Calculation Options

3. Effect evaluation with suppression:

   For each effect in power:
     IF (effect.Suppression & Config.Suppression) != eSuppress.None:
       // This effect is currently suppressed
       SKIP effect in calculations
     ELSE:
       // Effect is active, include in calculations
       INCLUDE effect normally

4. Common suppression patterns:

   a) Combat Suppression:
      - Flags: Attacked | HitByFoe | ActivateAttackClick
      - Use case: Travel powers (Super Speed, Super Jump, Fly)
      - Behavior: Movement bonuses suppressed when attacking/attacked

   b) Mez Suppression:
      - Flags: Held | Sleep | Stunned | Immobilized | Terrorized
      - Use case: Toggle powers that drop when mezzed
      - Behavior: Effects stop while character is controlled

   c) Stealth Suppression:
      - Flags: ActivateAttackClick | Attacked
      - Use case: Stealth/Hide powers
      - Behavior: Stealth breaks when attacking (but not when attacked)

5. Display logic (Effect.cs lines 1295-1342):
   - Detailed mode: Lists specific suppression conditions
   - Simple mode: Shows "Combat Suppression" for combat flags
   - UI shows when effects are inactive due to suppression
```

### Key Implementation Details

**Effect Filtering in Power Calculations** (`Power.cs` line 1207):
```csharp
// When calculating power effects, check suppression flags
if ((MidsContext.Config.Suppression & effect.Suppression) == Enums.eSuppress.None)
{
    // Effect is NOT suppressed, include it
    includeEffect = true;
}
else
{
    // Effect IS suppressed, skip it
    includeEffect = false;
}
```

**User Configuration** (`frmCalcOpt.cs` lines 167-175):
- UI provides checklist of all suppression types
- User selects which scenarios to simulate
- Build planning typically leaves all unchecked (no suppression)
- Combat simulation might enable Attacked/HitByFoe flags

**Display Strings** (`Effect.cs` lines 1295-1342):
- "Suppressed when Attacking"
- "Suppressed when Attacked"
- "Suppressed when Hit"
- "Suppressed when Mezzed" (any mez type)
- "Suppressed when Knocked"
- "Suppressed when Confused"
- "Combat Suppression" (shorthand for attack-related flags)

## Game Mechanics Context

**Why This Exists:**

City of Heroes has complex power interaction rules where some effects are temporarily disabled based on character state. This prevents certain power combinations from being too strong and adds tactical depth:

1. **Travel Power Balance**: Sprint + Super Speed together would be extremely fast. Combat suppression reduces movement bonuses when attacking/attacked, preventing hit-and-run tactics.

2. **Stealth Gameplay**: Hide/Stealth powers would be overpowered if maintained during combat. Suppression when attacking forces tactical positioning before engagement.

3. **Mez Protection**: Toggle powers providing mez protection should drop when the character is actually mezzed (held, stunned, etc.), creating counterplay.

4. **Resource Management**: Some effects (endurance recovery buffs) may suppress during specific conditions to balance power usage.

**Historical Context:**

- **Issue 1 (2004)**: Original travel power suppression introduced to prevent "jousting" (attacking while at full speed)
- **Issue 2 (2004)**: Stealth suppression refined - Hide breaks on attack, but Stealth only partially suppresses
- **Issue 7 (2005)**: Movement suppression duration standardized (4 seconds after combat action)
- **Homecoming (2019+)**: Some suppression rules relaxed (PvE travel suppression reduced from 4s to 0s in some cases)

**Known Quirks:**

1. **Suppression Duration**: In-game, suppression lasts for a duration after the trigger (e.g., 4 seconds after attacking). Mids doesn't model time-based suppression - it's binary on/off based on scenario selection.

2. **Partial Suppression**: Some powers have partial suppression (reduced to 40% effectiveness) rather than full suppression. Mids treats suppression as binary (100% or 0%), not partial values.

3. **Sprint + Travel Power**: In-game, Sprint and a Travel power together face suppression, but individual effects interact complexly. Mids simplifies by checking suppression flags per effect.

4. **Stealth Stacking**: Multiple stealth powers stack, but all break on attack. Suppression applies to all stealth effects with `ActivateAttackClick` flag.

5. **Build Planning Context**: Mids typically runs with all suppression flags OFF because build planning shows "peak performance", not "in-combat performance". Users enable suppression scenarios manually for specific analysis.

6. **PvP Differences**: Suppression rules differ between PvE and PvP. Mids uses same suppression flags but effect magnitudes may differ based on PvMode field (see Spec 01).

7. **MissionObjectClick**: This suppression type is rare and specific to certain mission mechanics. Most players never encounter it.

## Python Implementation Notes

**Proposed Architecture:**

```python
# backend/app/calculations/suppression.py

from enum import IntFlag
from dataclasses import dataclass
from typing import Optional

class SuppressionType(IntFlag):
    """
    Suppression conditions that can disable effects
    Maps to MidsReborn's Enums.eSuppress

    This is an IntFlag so multiple conditions can be combined:
    combat_suppression = SuppressionType.ATTACKED | SuppressionType.HIT_BY_FOE
    """
    NONE = 0
    HELD = 1
    SLEEP = 2
    STUNNED = 4
    IMMOBILIZED = 8
    TERRORIZED = 16
    KNOCKED = 32
    ATTACKED = 64
    HIT_BY_FOE = 128
    MISSION_OBJECT_CLICK = 256
    ACTIVATE_ATTACK_CLICK = 512
    DAMAGED = 1024
    PHASED = 2048
    CONFUSED = 4096

    @classmethod
    def combat_suppression(cls) -> "SuppressionType":
        """Common combination: effect suppressed in combat"""
        return cls.ATTACKED | cls.HIT_BY_FOE | cls.ACTIVATE_ATTACK_CLICK

    @classmethod
    def mez_suppression(cls) -> "SuppressionType":
        """Common combination: effect suppressed when mezzed"""
        return cls.HELD | cls.SLEEP | cls.STUNNED | cls.IMMOBILIZED | cls.TERRORIZED


@dataclass
class SuppressionConfig:
    """
    Global suppression scenario configuration
    Maps to MidsContext.Config.Suppression

    Represents which suppression conditions are currently "active"
    for calculation purposes.
    """
    active_conditions: SuppressionType = SuppressionType.NONE

    def is_in_combat(self) -> bool:
        """Check if combat suppression is active"""
        combat_flags = SuppressionType.combat_suppression()
        return bool(self.active_conditions & combat_flags)

    def is_mezzed(self) -> bool:
        """Check if mez suppression is active"""
        mez_flags = SuppressionType.mez_suppression()
        return bool(self.active_conditions & mez_flags)


def is_effect_suppressed(
    effect_suppression: SuppressionType,
    global_config: SuppressionConfig
) -> bool:
    """
    Check if an effect is currently suppressed

    Args:
        effect_suppression: Suppression flags on the effect
        global_config: Current suppression scenario

    Returns:
        True if effect is suppressed (should be ignored in calculations)
        False if effect is active (should be included in calculations)

    Logic:
        If (effect.suppression & config.active_conditions) != NONE:
            Effect is suppressed
        Else:
            Effect is active

    Example:
        effect_suppression = SuppressionType.ATTACKED | SuppressionType.HIT_BY_FOE
        global_config.active_conditions = SuppressionType.ATTACKED

        # Bitwise AND: 0x40 & 0x40 = 0x40 (non-zero)
        is_suppressed = (effect_suppression & global_config.active_conditions) != SuppressionType.NONE
        # Returns True - effect is suppressed
    """
    if effect_suppression == SuppressionType.NONE:
        # Effect has no suppression conditions, always active
        return False

    # Check if any of the effect's suppression conditions are currently active
    overlap = effect_suppression & global_config.active_conditions
    return overlap != SuppressionType.NONE


def get_suppression_description(suppression: SuppressionType, simple: bool = False) -> str:
    """
    Generate human-readable description of suppression conditions

    Args:
        suppression: Suppression flags
        simple: If True, use shorthand descriptions

    Returns:
        Description string for UI display

    Maps to Effect.cs BuildEffectString logic (lines 1295-1342)
    """
    if suppression == SuppressionType.NONE:
        return ""

    if simple:
        # Shorthand for common patterns
        combat_flags = SuppressionType.ATTACKED | SuppressionType.HIT_BY_FOE | SuppressionType.ACTIVATE_ATTACK_CLICK
        if suppression & combat_flags:
            return "Combat Suppression"
        return "Suppressed"

    # Detailed descriptions
    descriptions = []

    if suppression & SuppressionType.ACTIVATE_ATTACK_CLICK:
        descriptions.append("Suppressed when Attacking")
    if suppression & SuppressionType.ATTACKED:
        descriptions.append("Suppressed when Attacked")
    if suppression & SuppressionType.HIT_BY_FOE:
        descriptions.append("Suppressed when Hit")
    if suppression & SuppressionType.MISSION_OBJECT_CLICK:
        descriptions.append("Suppressed when MissionObjectClick")

    # Grouped mez conditions
    mez_flags = SuppressionType.HELD | SuppressionType.IMMOBILIZED | SuppressionType.SLEEP | SuppressionType.STUNNED | SuppressionType.TERRORIZED
    if suppression & mez_flags:
        descriptions.append("Suppressed when Mezzed")

    if suppression & SuppressionType.KNOCKED:
        descriptions.append("Suppressed when Knocked")
    if suppression & SuppressionType.CONFUSED:
        descriptions.append("Suppressed when Confused")
    if suppression & SuppressionType.DAMAGED:
        descriptions.append("Suppressed when Damaged")
    if suppression & SuppressionType.PHASED:
        descriptions.append("Suppressed when Phased")

    return "\n".join(descriptions)


# Example usage in effect filtering
def filter_active_effects(effects: list, config: SuppressionConfig) -> list:
    """
    Filter effect list to only include non-suppressed effects

    This is the core function used in power calculations to determine
    which effects are currently active.
    """
    active_effects = []

    for effect in effects:
        if not is_effect_suppressed(effect.suppression, config):
            # Effect is active, include it
            active_effects.append(effect)
        # else: effect is suppressed, skip it

    return active_effects
```

**Design Notes:**

1. **IntFlag Enum**: Python's `IntFlag` provides the same bitwise flag functionality as C#'s `[Flags]` enum, allowing multiple suppression types to be combined.

2. **Global Configuration**: Like Mids, maintain a global `SuppressionConfig` that represents the current scenario being calculated. Default is all flags OFF (no suppression).

3. **Effect Filtering**: Apply suppression checks during effect aggregation (see Spec 01). Suppressed effects are excluded from calculations entirely.

4. **UI Integration**: Frontend should provide checkbox UI for users to select suppression scenarios, matching Mids' "Calculation Options" dialog.

5. **Build Planning Default**: Default config should be `SuppressionType.NONE` to show "peak performance" builds, matching Mids' behavior.

6. **Time-Based Suppression**: DO NOT implement duration-based suppression (e.g., "4 seconds after attack"). Mids treats suppression as instantaneous binary state, not time-series simulation.

**Implementation Priority:**

**LOW** - This is a specialized feature primarily used for advanced combat simulation. Most users calculate builds with suppression OFF to see maximum performance. Can be deferred to Milestone 3 (depth implementation).

**Key Implementation Steps:**

1. Define `SuppressionType` enum with all flags from `eSuppress`
2. Add `suppression` field to `Effect` dataclass (see Spec 01)
3. Create `SuppressionConfig` class for global scenario settings
4. Implement `is_effect_suppressed()` check function
5. Integrate suppression filtering into effect aggregation (Spec 01)
6. Add UI controls for suppression scenario selection
7. Implement display functions for showing suppression status

**Testing Strategy:**

- Unit tests for bitwise flag operations (combining multiple suppression types)
- Unit tests for `is_effect_suppressed()` with various flag combinations
- Integration test: Super Speed power with combat suppression ON vs OFF
- Integration test: Hide power with `ACTIVATE_ATTACK_CLICK` suppression
- Verify default config (NONE) matches Mids' build planning behavior

## References

- **Related Specs**:
  - Spec 01 (Power Effects Core) - Effect aggregation and filtering
  - Spec 02 (Power Types) - Toggle powers and suppression interaction
  - Spec 08 (Stealth Powers) - Stealth-specific suppression rules
  - Spec 05 (Movement Powers) - Travel power combat suppression
- **MidsReborn Files**:
  - `Core/Enums.cs` (lines 1132-1148) - `eSuppress` enum definition
  - `Core/Base/Data_Classes/Effect.cs` (lines 34, 102, 266, 602, 1295-1342) - Suppression property and display
  - `Core/Base/Data_Classes/Power.cs` (lines 1207, 1345, 1638, 1702, 1707, 1781, 1844) - Suppression checks
  - `Forms/OptionsMenuItems/frmCalcOpt.cs` (lines 167-175, 264-271) - UI configuration
- **Game Documentation**:
  - City of Heroes Wiki - "Travel Suppression"
  - City of Heroes Wiki - "Stealth Mechanics"
  - Homecoming Forums - "Issue 7 Travel Suppression Changes"
