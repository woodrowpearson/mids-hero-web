# Pseudopet Mechanics

## Overview
- **Purpose**: Model invisible pseudopet entities that deliver power effects from a location (patches, auras, location-based AoE)
- **Used By**: Location-based powers (Burn, Ice Patch, Tar Patch, Rain of Fire, Freezing Rain), some auras, location-targeted AoE effects
- **Complexity**: Complex
- **Priority**: Medium
- **Status**: 🟡 Breadth Complete

## MidsReborn Implementation

### Primary Location
- **File**: `Core/Base/Data_Classes/Effect.cs` (EntCreate/EntCreate_x effect types)
- **Supporting Files**:
  - `Core/SummonedEntity.cs` - Entity definition (shared with pets, but different usage)
  - `Core/GroupedFx.cs` - Effect grouping with SummonId tracking
  - `Core/Enums.cs` - `eEffectType.EntCreate` and `eEffectType.EntCreate_x`
  - `Core/IPower.cs` - `HasEntity` property, `AbsorbSummonEffects` flag

### Key Distinction: Pseudopets vs Pets

**Pseudopets** (this spec):
- **Invisible** entities spawned by powers
- **NOT controllable** by player
- Created at a **specific location** (under feet, at target location)
- Purpose: **Deliver effects from that location**
- Examples: Burn patch, Ice Patch, Tar Patch, Rain of Fire drops, caltrops
- Players never see them in pet window
- Typically short-lived (duration of patch effect)

**Pets** (Spec 32 - Pet Calculations):
- **Visible** entities summoned by powers
- **Controllable** by player (attack, follow, stay, etc.)
- Follow player or stay at location
- Purpose: **Independent combat entities**
- Examples: Mastermind henchmen, Controller pets (Fire Imps, etc.)
- Show in pet window with controls
- Persist until dismissed or defeated

### Entity Creation Effect Types

From `Core/Enums.cs` (lines 427, 460):

```csharp
public enum eEffectType
{
    // ... other types ...
    EntCreate = 27,      // Original entity creation
    // ... other types ...
    EntCreate_x = 60,    // Extended entity creation
    // ... other types ...
}
```

### Effect Properties for Pseudopets

From `Core/IEffect.cs`:
```csharp
interface IEffect
{
    Enums.eEffectType EffectType { get; set; }  // EntCreate or EntCreate_x
    string Summon { get; set; }                  // Entity UID reference
    int nSummon { get; set; }                    // Entity numeric ID
    Enums.eToWho ToWho { get; set; }             // Target, Self, Location
    Enums.eStacking Stacking { get; set; }       // Can multiple stack at same location?
    float Duration { get; set; }                 // How long pseudopet exists
    float DelayedTime { get; set; }              // Delay before pseudopet spawns
    int Ticks { get; set; }                      // How many times pseudopet pulses effects
}
```

### High-Level Algorithm

```
Pseudopet Creation and Effect Delivery:

1. Power Activation:
   - Player activates power (e.g., "Burn")
   - Power has EntCreate effect
   - Effect specifies:
     - Summon entity UID (references SummonedEntity)
     - Location: at caster feet, at target, at ground target
     - Duration: how long patch lasts
     - Ticks: how often effects pulse

2. Pseudopet Spawning:
   - Create invisible entity at specified location
   - Entity is NOT added to pet window
   - Entity is NOT controllable
   - Entity has its own powerset (defined in SummonedEntity)
   - Apply DelayedTime if specified (some patches have spawn delay)

3. Effect Delivery Loop:
   FOR duration of pseudopet:
     EVERY tick interval:
       - Pseudopet activates its power(s)
       - Effects delivered to targets in range FROM pseudopet location
       - Each target checked independently
       - Can hit same target multiple times (bypasses some target limits)
       - Apply probability checks per pulse
   END LOOP

4. Enhancement Interactions:
   - Enhancements in ORIGINAL power affect pseudopet:
     - Duration enhancements → extend pseudopet lifetime
     - Recharge enhancements → reduce power recharge (not pseudopet)
   - Enhancements MAY NOT affect pseudopet's effects directly
   - Some pseudopets inherit damage/accuracy from original power
   - Complex interaction: AbsorbSummonEffects flag

5. Pseudopet Despawning:
   - Duration expires → pseudopet vanishes
   - Original caster moves out of range → may despawn (power-specific)
   - Caster defeated → pseudopet despawns
   - Zone change → all pseudopets despawn

Special Case: Absorbed Effects
  IF power has AbsorbSummonEffects = true:
    - Display pseudopet effects AS IF they were power effects
    - In UI: "Burn deals X damage per tick"
    - Reality: Burn creates pseudopet that deals X damage per tick
    - Simplifies display for players
```

### Pseudopet Multi-Hit Mechanics

**Critical Difference from Direct Powers**:

```
Direct Power (normal):
  - Hits target once per activation
  - MaxTargets limit applied strictly
  - 16 target AoE cap typical

Pseudopet Power:
  - Can hit same target EVERY tick
  - Bypasses some target limits
  - Multiple pseudopets can hit same target simultaneously
  - Example: Overlapping Rain of Fire drops
  - Each pseudopet checks targets independently
```

This is why location-based AoE patches can be very powerful - they effectively bypass the 16-target AoE cap by hitting targets repeatedly over time.

### Stacking and ToWho

From `Core/Base/Data_Classes/Effect.cs` (line 501):
```csharp
// Special scaling for pseudopets
if ((EffectType == Enums.eEffectType.EntCreate) &
    (ToWho == Enums.eToWho.Target) &
    (Stacking == Enums.eStacking.Yes) &
    !IgnoreScaling)
{
    // Apply special scaling rules
    flag = true;
}
```

**ToWho determines spawn location**:
- `ToWho.Self` → Spawn at caster location (under feet)
- `ToWho.Target` → Spawn at target location (where you clicked)
- `ToWho.Location` → Spawn at ground-targeted location

**Stacking determines multiple instances**:
- `Stacking.Yes` → Multiple pseudopets can exist simultaneously
- `Stacking.No` → Only one pseudopet at a time (new one replaces old)

### Power Flags

From `Core/IPower.cs`:
```csharp
interface IPower
{
    bool HasEntity { get; }              // Power creates entity (pet or pseudopet)
    bool AbsorbSummonEffects { get; set; }   // Display entity effects as power effects
    bool AbsorbSummonAttributes { get; set; } // Inherit entity attributes
    bool ShowSummonAnyway { get; set; }      // Show entity even if absorbed
}
```

**AbsorbSummonEffects = true**:
- Common for pseudopets
- Makes UI simpler: shows "Burn deals 10 fire damage per tick"
- Reality: Burn creates pseudopet, pseudopet deals damage
- MidsReborn pulls pseudopet's power effects into main power display

**AbsorbSummonAttributes = false** (typically):
- Pseudopets don't inherit caster's attributes
- They use their own power definitions
- Exception: Some pseudopets inherit accuracy/damage from original power

## Game Mechanics Context

**Why Pseudopets Exist:**

City of Heroes uses pseudopets as an elegant solution to location-based effects:

1. **Unified Entity System**: Both pets and pseudopets use the same `SummonedEntity` structure, but pseudopets are invisible and uncontrollable
2. **Location-Based Delivery**: Effects need to originate from a location, not the caster (who may move away)
3. **Persistent Effects**: Patches/auras need to persist after caster moves/dies (within limits)
4. **Independent Targeting**: Each pseudopet checks targets independently, allowing repeated hits on same target
5. **Separation of Concerns**: Original power handles creation/placement, pseudopet handles effect delivery

**Historical Context:**

- **Launch (2004)**: Pseudopets existed from day one for location patches
- **Issue 5 (2005)**: ED affected pseudopet enhancement interactions, created complexity
- **Issue 9 (2006)**: IO procs in pseudopet powers became powerful (multiple proc chances per target)
- **Issue 18 (2010)**: Incarnate abilities added more complex pseudopet interactions
- **Homecoming (2019+)**: Refined pseudopet mechanics, fixed some exploits

**Common Pseudopet Powers:**

**Fire Control/Manipulation**:
- Burn → Damage patch under feet
- Bonfire → Knockback patch
- Hot Feet → Damage aura (technically pseudopet)

**Ice Control**:
- Ice Patch → Knockdown patch at location
- Ice Slick → Knockdown patch

**Traps/Devices**:
- Caltrops → Slow/damage patch
- Trip Mine → Delayed explosion (pseudopet waits for trigger)
- Poison Trap → Location-based effect

**Storm Summoning**:
- Freezing Rain → Multiple effects (defense debuff, slow, damage)
- Ice Storm → Damage patch
- Sleet → Defense/resistance debuff patch

**Targeted AoE Rains**:
- Rain of Fire → Multiple pseudopet drops over duration
- Blizzard → Multiple pseudopet drops
- Any "rain" power → Usually 10-15 pseudopet drops over 15 seconds

**Known Quirks:**

1. **Enhancement Application Varies**:
   - Some pseudopets inherit accuracy/damage from original power
   - Some don't inherit anything
   - No consistent rule - must check per power
   - AbsorbSummonEffects flag controls display, not mechanics

2. **Proc Abuse Potential**:
   - Each pseudopet tick = separate proc chance
   - Long duration patches = many proc chances per target
   - Rain powers with multiple drops = many simultaneous proc chances
   - Historically led to "proc monster" builds (IO procs in rain powers)

3. **Target Cap Bypass**:
   - Direct AoE: 16 target cap (typically)
   - Pseudopet patch: Can hit same target every tick
   - Multiple patches: Stack damage multiplicatively
   - Example: 3 overlapping Burn patches = 3x damage on targets in overlap

4. **Movement and Range**:
   - Some pseudopets despawn if caster moves too far away
   - Some persist regardless of caster location
   - Some follow caster (auras)
   - Power-specific behavior, not consistent rule

5. **PvP Differences**:
   - Many pseudopet powers behave differently in PvP
   - Reduced tick rates or damage in PvP
   - Some patches don't work at all in PvP
   - Balance mechanism for repeated-hit potential

6. **Incarnate Interactions**:
   - Interface procs can apply on EVERY pseudopet tick
   - Degenerative/Reactive Interface = multiple applications per target
   - Destiny buffs may or may not affect pseudopets
   - Complex interaction with Lore pets vs pseudopets

## Python Implementation Notes

**Proposed Architecture:**

```python
# backend/app/calculations/pseudopets.py

from dataclasses import dataclass
from typing import Optional, List
from enum import Enum

class PseudopetLocation(Enum):
    """Where pseudopet spawns"""
    CASTER = "caster"          # At caster's feet (Burn)
    TARGET = "target"          # At target location (Ice Patch)
    GROUND_TARGET = "ground"   # Ground-targeted location (Tar Patch)

class PseudopetStacking(Enum):
    """Can multiple pseudopets exist simultaneously?"""
    YES = "yes"    # Multiple instances allowed
    NO = "no"      # Only one at a time, new replaces old

@dataclass
class PseudopetDefinition:
    """
    Defines a pseudopet entity that delivers effects from a location
    Maps to MidsReborn's SummonedEntity (for pseudopets, not controllable pets)
    """
    uid: str                      # Unique identifier
    display_name: str             # "Burn Patch", "Ice Patch", etc.
    entity_type: str              # "pseudopet" (vs "pet" for controllable summons)

    # Powersets that pseudopet uses to deliver effects
    powerset_fullnames: List[str]  # e.g., ["Fire_Manipulation.Burn_Patch"]

    # How long pseudopet exists
    duration: float                # Seconds (0 = instant/permanent)

    # How often pseudopet pulses effects
    tick_interval: float           # Seconds between effect deliveries

    # Spawn delay
    delayed_spawn: float = 0.0     # Seconds before pseudopet appears

    # Location behavior
    location_type: PseudopetLocation = PseudopetLocation.CASTER
    follows_caster: bool = False   # Some auras follow caster
    despawn_on_distance: bool = False  # Despawns if caster moves away
    max_distance: float = 0.0      # Max range before despawn (if applicable)

    # Stacking behavior
    stacking: PseudopetStacking = PseudopetStacking.YES
    max_instances: int = 0         # 0 = unlimited, else max simultaneous instances

@dataclass
class PseudopetCreationEffect:
    """
    Effect that creates a pseudopet (EntCreate/EntCreate_x)
    Maps to MidsReborn's Effect with EffectType = EntCreate
    """
    effect_type: str = "EntCreate"  # or "EntCreate_x"
    pseudopet_uid: str              # References PseudopetDefinition

    # Override properties (if different from pseudopet defaults)
    duration_override: Optional[float] = None
    location_override: Optional[PseudopetLocation] = None

    # Enhancement inheritance
    inherit_accuracy: bool = False   # Does pseudopet inherit power's accuracy?
    inherit_damage: bool = False     # Does pseudopet inherit power's damage buffs?

    def get_effective_duration(self, base_duration: float,
                              duration_enhancement: float) -> float:
        """
        Calculate actual pseudopet duration with enhancements
        Duration enhancements in original power extend pseudopet lifetime
        """
        effective = self.duration_override or base_duration
        return effective * (1.0 + duration_enhancement)

class PseudopetEffectCalculator:
    """
    Calculates effects delivered by pseudopets
    Handles multi-hit, tick-based delivery, proc chances per tick
    """

    def calculate_total_damage(self,
                              pseudopet: PseudopetDefinition,
                              base_damage: float,
                              damage_enhancement: float,
                              duration_enhancement: float) -> float:
        """
        Calculate total damage from pseudopet over its lifetime

        Args:
            pseudopet: Pseudopet definition
            base_damage: Base damage per tick
            damage_enhancement: Damage buff (may or may not apply)
            duration_enhancement: Extends pseudopet lifetime

        Returns:
            Total damage delivered over pseudopet lifetime
        """
        # Duration affected by duration enhancements
        effective_duration = pseudopet.duration * (1.0 + duration_enhancement)

        # Number of ticks
        num_ticks = int(effective_duration / pseudopet.tick_interval)

        # Damage per tick (may or may not be enhanced)
        # Depends on inherit_damage flag in creation effect
        damage_per_tick = base_damage
        # Note: Enhancement application is complex and power-specific
        # Defer to Milestone 3 for detailed rules

        # Total damage
        total = damage_per_tick * num_ticks

        return total

    def calculate_proc_chances_per_target(self,
                                         pseudopet: PseudopetDefinition,
                                         duration_enhancement: float) -> int:
        """
        Calculate how many times a proc can trigger per target
        This is why procs in pseudopet powers are so strong

        Args:
            pseudopet: Pseudopet definition
            duration_enhancement: Extends lifetime = more chances

        Returns:
            Number of proc chances per target in pseudopet range
        """
        effective_duration = pseudopet.duration * (1.0 + duration_enhancement)
        num_ticks = int(effective_duration / pseudopet.tick_interval)

        # Each tick = separate proc chance against each target in range
        return num_ticks

    def check_multi_pseudopet_overlap(self,
                                     pseudopet: PseudopetDefinition,
                                     num_instances: int) -> float:
        """
        Calculate damage multiplier from overlapping pseudopets

        For powers that create multiple pseudopets (Rain of Fire drops),
        targets in overlap zone take damage from all pseudopets

        Args:
            pseudopet: Pseudopet definition
            num_instances: Number of simultaneous pseudopets

        Returns:
            Damage multiplier (1.0 = single pseudopet, 3.0 = triple overlap)
        """
        if pseudopet.stacking == PseudopetStacking.NO:
            return 1.0

        # In reality, depends on area overlap and target location
        # Full analysis deferred to Milestone 3
        # For now, return max theoretical overlap
        return float(num_instances)

class PowerWithPseudopet:
    """
    Power that creates pseudopet(s)
    Maps to MidsReborn's Power with AbsorbSummonEffects flag
    """

    def __init__(self, power_data: dict):
        self.power_name = power_data["name"]
        self.pseudopet_effect = None  # PseudopetCreationEffect
        self.pseudopet_def = None     # PseudopetDefinition
        self.absorb_effects = power_data.get("absorb_summon_effects", False)

    def create_pseudopet(self,
                        location: tuple[float, float, float],
                        duration_enhancement: float = 0.0) -> dict:
        """
        Create pseudopet instance at location

        Args:
            location: (x, y, z) coordinates
            duration_enhancement: Duration bonus from enhancements

        Returns:
            Pseudopet instance data
        """
        if not self.pseudopet_effect or not self.pseudopet_def:
            return {}

        effective_duration = self.pseudopet_effect.get_effective_duration(
            self.pseudopet_def.duration,
            duration_enhancement
        )

        return {
            "pseudopet_uid": self.pseudopet_def.uid,
            "location": location,
            "duration": effective_duration,
            "tick_interval": self.pseudopet_def.tick_interval,
            "spawn_time": 0.0,  # Would be current game time
            "despawn_time": effective_duration,
            "visible": False,   # Always invisible
            "controllable": False,  # Never controllable
        }

    def deliver_effects(self,
                       pseudopet_instance: dict,
                       targets_in_range: List[dict]) -> List[dict]:
        """
        Deliver effects from pseudopet to targets in range
        Called every tick interval

        Args:
            pseudopet_instance: Active pseudopet instance
            targets_in_range: Targets within pseudopet's effect range

        Returns:
            List of applied effects (one per target)
        """
        # Get pseudopet's powers and their effects
        # Apply each effect to each target
        # Each target is checked independently
        # Can hit same target every tick (unlike direct powers)

        applied_effects = []

        for target in targets_in_range:
            # Apply effects from pseudopet's powersets
            # Check accuracy, apply damage, apply debuffs, etc.
            # Roll proc chances (separate per target, per tick)

            effect = {
                "target_id": target["id"],
                "source": "pseudopet",
                "pseudopet_uid": pseudopet_instance["pseudopet_uid"],
                "tick_number": 0,  # Would track which tick this is
                # ... effect details ...
            }
            applied_effects.append(effect)

        return applied_effects

    def get_display_effects(self) -> List[dict]:
        """
        Get effects for UI display

        If absorb_effects = True:
            Return pseudopet's effects as if they were power's effects
            Example: "Burn deals 10.5 fire damage per tick for 30 seconds"

        If absorb_effects = False:
            Return just "Creates Burn Patch"
            User must look at pseudopet separately

        Returns:
            List of effects to display in UI
        """
        if not self.absorb_effects:
            return [{
                "description": f"Creates {self.pseudopet_def.display_name}",
                "duration": self.pseudopet_def.duration,
            }]

        # Fetch pseudopet's power effects and return as if they were this power's
        # This is the common case for most pseudopet powers
        # Simplifies UI for players
        return []  # Would fetch from pseudopet powersets

# Usage Example
def analyze_burn_power():
    """
    Example: Fire Manipulation's Burn creates damage patch
    """

    # Define the Burn pseudopet
    burn_pseudopet = PseudopetDefinition(
        uid="Fire_Manipulation.Burn_Pseudopet",
        display_name="Burn Patch",
        entity_type="pseudopet",
        powerset_fullnames=["Fire_Manipulation.Burn_Patch_Power"],
        duration=30.0,          # 30 second patch
        tick_interval=0.25,     # Damages every 0.25 seconds
        location_type=PseudopetLocation.CASTER,  # Under caster's feet
        stacking=PseudopetStacking.NO,  # Only one Burn patch at a time
    )

    # Define the creation effect
    burn_creation = PseudopetCreationEffect(
        effect_type="EntCreate",
        pseudopet_uid="Fire_Manipulation.Burn_Pseudopet",
        inherit_damage=False,  # Burn damage not affected by damage buffs
    )

    # Calculate total damage
    calculator = PseudopetEffectCalculator()
    base_damage_per_tick = 3.5  # Fire damage per tick
    duration_enhancement = 0.95  # 95% duration enhancement slotted

    total_damage = calculator.calculate_total_damage(
        burn_pseudopet,
        base_damage_per_tick,
        damage_enhancement=0.0,  # Doesn't inherit
        duration_enhancement=duration_enhancement
    )

    print(f"Burn patch total damage: {total_damage}")
    print(f"Tick rate: {burn_pseudopet.tick_interval}s")
    print(f"Duration: {burn_pseudopet.duration * (1 + duration_enhancement)}s")

    # Calculate proc chances
    proc_chances = calculator.calculate_proc_chances_per_target(
        burn_pseudopet,
        duration_enhancement
    )
    print(f"Proc chances per target: {proc_chances}")
```

**Key Design Decisions:**

1. **Separate pseudopets from pets**: Different classes/flags, different behavior
2. **PseudopetDefinition**: Reusable definition (like SummonedEntity but clearer purpose)
3. **PseudopetCreationEffect**: Effect that creates the pseudopet
4. **PowerWithPseudopet**: Power that spawns pseudopets, handles absorption flag
5. **Effect delivery loop**: Tick-based delivery with independent target checks
6. **Enhancement inheritance**: Explicit flags for what inherits, what doesn't
7. **Proc abuse tracking**: Explicit calculation of proc chances per target

**Defer to Milestone 3 (Depth)**:
- Exact enhancement inheritance rules per power
- PvP vs PvE pseudopet differences
- Incarnate Interface interaction with pseudopet ticks
- Geometry calculations for overlapping patches
- Range/despawn distance mechanics
- Complex rain power drop patterns
- Edge cases and special pseudopet powers

**Critical for Python Implementation:**
- Pseudopets are NOT visible/controllable pets (different UI treatment)
- Tick-based delivery requires time simulation or simplified calculation
- Proc chances multiply with tick count (balance consideration)
- Target cap bypass is intentional game design (not bug)
- AbsorbSummonEffects flag critical for UI display
