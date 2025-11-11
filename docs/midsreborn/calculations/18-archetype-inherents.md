# Archetype Inherents

## Overview
- **Purpose**: Model archetype-specific inherent powers that define each AT's unique combat mechanics and playstyle
- **Used By**: Damage calculations, buff/debuff totals, build planning, archetype differentiation
- **Complexity**: High (varies by inherent - some simple, some complex/situational)
- **Priority**: High
- **Status**: 🟡 Breadth Complete

## MidsReborn Implementation

### Primary Location
- **File**: `Core/Base/Data_Classes/Character.cs` - Character state flags for inherents
- **File**: `Core/Base/Data_Classes/Effect.cs` - Effect validation and special case handling
- **File**: `Core/Enums.cs` - `eSpecialCase` enum defines inherent types
- **Related Files**:
  - `Core/GroupedFx.cs` - Special handling for Defiance and other conditional effects
  - Power database - Inherent powers stored as `"Inherent.Inherent.{PowerName}"`

### Character State Flags

From `Character.cs`, the following inherent toggles are tracked:

```csharp
public bool Assassination { get; private set; }
public bool Domination { get; private set; }
public bool Containment { get; private set; }
public bool Scourge { get; private set; }
public bool CriticalHits { get; private set; }
public bool Defiance { get; private set; }
public bool Supremacy { get; private set; }
public bool SupremacyAndBuffPwr { get; private set; }
```

These are set via conditional expressions parsed from power data (e.g., `"DOMINATION"`, `"SCOURGE"`, `"CONTAINMENT"`).

### Special Case Enum

The `eSpecialCase` enum defines when effects should activate:

```csharp
public enum eSpecialCase
{
    None,
    Hidden,              // Stalker hide
    Domination,          // Dominator inherent active
    Scourge,             // Corruptor inherent active
    CriticalHit,         // Scrapper critical (any target)
    CriticalBoss,        // Scrapper critical vs boss
    CriticalMinion,      // Scrapper critical vs minion
    Assassination,       // Stalker critical from hide
    Containment,         // Controller double damage
    Defiance,            // Blaster damage buff
    Supremacy,           // Mastermind pet buff
    SupremacyAndBuffPwr, // Mastermind with upgrade powers
    // ... other special cases
}
```

### Effect Validation

From `Effect.cs`, the `ValidateConditional()` method checks if an effect should apply based on character state:

```csharp
case Enums.eSpecialCase.Domination:
    if (MidsContext.Character.Domination)
        return true;
    break;

case Enums.eSpecialCase.Scourge:
    if (MidsContext.Character.Scourge)
        return true;
    break;

case Enums.eSpecialCase.Containment:
    if (MidsContext.Character.Containment)
        return true;
    break;

case Enums.eSpecialCase.Defiance:
    if (MidsContext.Character.Defiance)
        return true;
    break;
```

This allows powers to have conditional effects that only apply when the inherent is "active" in the planner.

## Game Mechanics Context

### The 10 Primary Inherents

City of Heroes defines each archetype by a unique inherent power. These are automatic, always active (or conditionally triggered), and cannot be removed or modified.

#### 1. **Fury** (Brute)

**Mechanics**:
- Builds a Fury bar (0-100%) from taking damage and dealing damage
- Each 1% Fury = +1% damage buff (additive)
- At 100% Fury: +100% damage (double base damage)
- Decays slowly when not in combat
- Taking damage builds more Fury than dealing damage

**In MidsReborn**:
- **NOT directly modeled** - Fury is dynamic and combat-dependent
- Planner shows base damage without Fury
- Players must manually estimate Fury levels
- No special case flag or toggle for Fury

**Calculation Notes**:
```
Damage Multiplier = 1.0 + (Fury Percentage / 100)

Example at 75% Fury:
  Base Damage: 100
  Fury Bonus: +75%
  Total Damage: 175
```

**Python Considerations**:
- Could implement as optional buff: "Assume X% Fury"
- Typical values: 0% (start of fight), 50% (sustained combat), 75-85% (optimal play), 100% (theoretical max)
- Should NOT be default - requires user input

#### 2. **Defiance** (Blaster)

**Mechanics**:
- **Defiance 1.0** (original): Damage buff when at low HP (outdated, removed)
- **Defiance 2.0** (current):
  - Damage buff scales with HP remaining (higher HP = higher buff in modern version)
  - Can use Tier 1/2 attacks while mezzed
  - Builds Defiance bar from attacks (similar to Fury)
  - Grants small amount of mez protection

**In MidsReborn**:
```csharp
public bool Defiance { get; private set; }

// Special handling in GroupedFx.cs:
var defiancePower = DatabaseAPI.GetPowerByFullName("Inherent.Inherent.Defiance");
var isDefiance = effectSource.SpecialCase == Enums.eSpecialCase.Defiance &&
                 effectSource.ValidateConditional("Active", "Defiance") |
                 MidsContext.Character.CurrentBuild.PowerActive(defiancePower);
```

- Defiance effects are **conditionally shown** based on toggle state
- Stored as `DamageBuff` effects with `SpecialCase = Defiance`
- Can be toggled on/off in planner

**Calculation Notes**:
```
Defiance 2.0 Damage Buff = varies by attack used
  - Tier 1/2 attacks grant temporary +damage buff
  - Stacks with other damage buffs
  - Typical range: +5% to +15% damage
```

**Python Considerations**:
- Should model as toggleable option
- Needs to track which powers are "active" to calculate buff
- Defiance effects marked with special case flag

#### 3. **Containment** (Controller)

**Mechanics**:
- Deals **double damage** on targets affected by control effects
- Control effects that trigger Containment:
  - Hold, Sleep, Stun, Immobilize, Terrorize, Confuse
  - Effects YOU applied (not team members)
- Does NOT require maintaining the control - just needs to be active on target
- Critical for Controller damage output

**In MidsReborn**:
```csharp
public bool Containment { get; private set; }

case Enums.eSpecialCase.Containment:
    if (MidsContext.Character.Containment)
        return true;
    break;
```

- Toggle on/off to see damage with Containment active
- When active, damage effects with `SpecialCase = Containment` apply
- Typically shows damage powers with 2x multiplier

**Calculation Notes**:
```
if (target_is_controlled):
    Damage = Base_Damage * 2.0
else:
    Damage = Base_Damage
```

**Python Considerations**:
- Simple boolean toggle
- Apply 2x multiplier to damage when enabled
- Should be OFF by default (conservative estimate)
- User can toggle ON to see "optimal" damage

#### 4. **Critical Hit** (Scrapper)

**Mechanics**:
- Chance for attacks to deal **double damage** (critical hit)
- Base chance: 5% vs minions, 10% vs lieutenants/bosses
- Some powers have higher/lower critical chances
- Critical chance can be buffed by certain powers
- Always active - random chance

**In MidsReborn**:
```csharp
public bool CriticalHits { get; private set; }

case Enums.eSpecialCase.CriticalHit:
    if (MidsContext.Character.CriticalHits || MidsContext.Character.IsStalker)
        return true;
    break;

case Enums.eSpecialCase.CriticalBoss:
    if (MidsContext.Character.CriticalHits)
        return true;
    break;
```

- Multiple special cases: `CriticalHit`, `CriticalBoss`, `CriticalMinion`
- Toggle shows "average" damage including critical chance
- Powers may have different critical rates

**Calculation Notes**:
```
Expected Damage = Base_Damage * (1.0 + Critical_Chance)

Example with 10% crit chance:
  Base Damage: 100
  Expected Damage: 100 * 1.10 = 110

Actual damage on critical: 200 (2x base)
```

**Python Considerations**:
- Should calculate expected value (probability-weighted average)
- Different critical rates for different target ranks
- May need per-power critical chance overrides
- Toggle to show "with crits" vs "without crits"

#### 5. **Assassination** (Stalker)

**Mechanics**:
- **From Hide**: First attack deals critical damage (guaranteed)
  - Melee attacks: 2x-6x damage (varies by power)
  - Ranged attacks: Reduced critical multiplier
- **Out of Hide**: Higher base critical chance than Scrappers
  - ~10-15% critical chance vs all targets
  - Scales up when on teams (more teammates = higher crit chance)

**In MidsReborn**:
```csharp
public bool Assassination { get; private set; }

case Enums.eSpecialCase.Assassination:
    if (MidsContext.Character.IsStalker && MidsContext.Character.Assassination)
        return true;
    break;

case Enums.eSpecialCase.Hidden:
    if (MidsContext.Character.IsStalker || MidsContext.Character.IsArachnos)
        return true;
    break;
```

- Toggle for "Assassination" (from hide) vs normal criticals
- Separate from regular critical hit mechanics
- Stalker-specific validation

**Calculation Notes**:
```
From Hide (Assassination Active):
  Damage = Base_Damage * Assassination_Multiplier
  Where Assassination_Multiplier = 2.0 to 6.0 (power-specific)

Out of Hide:
  Expected Damage = Base_Damage * (1.0 + Team_Critical_Chance)
  Team_Critical_Chance = 10% + (2% per teammate), capped at 30%
```

**Python Considerations**:
- Two modes: "From Hide" and "Out of Hide"
- From Hide needs per-power multiplier data
- Out of Hide needs team size assumption (1-8 players)
- Complex interaction with Hide status

#### 6. **Gauntlet** (Tanker)

**Mechanics**:
- All attacks apply **AoE taunt** to nearby enemies
- Taunt affects enemies in small radius around primary target
- Duration: ~13.5 seconds
- Magnitude: High (overrides most other aggro)
- Does NOT affect damage or survivability directly

**In MidsReborn**:
- **NOT explicitly modeled** in special cases enum
- Gauntlet is implemented as inherent taunt effects on Tanker powers
- No toggle or character state flag
- Effects are baked into power data

**Calculation Notes**:
```
Gauntlet is not a damage or buff calculation
  - It's a taunt effect applied to all Tanker attacks
  - Planner shows it as "Taunt" effect on power tooltips
  - No numeric calculation needed beyond effect display
```

**Python Considerations**:
- No special calculation required
- Just ensure Tanker powers show taunt effects
- Duration and magnitude stored in power effect data

#### 7. **Vigilance** (Defender)

**Mechanics**:
- **Endurance Discount** based on team HP
- Lower team HP = lower endurance cost for powers
- Formula (approximate):
  - Solo: No benefit (0% discount)
  - Team at 100% HP: 0% discount
  - Team at 50% HP: ~25% discount
  - Team at 25% HP: ~40% discount
- Only affects endurance cost, not damage or healing

**In MidsReborn**:
- **NOT explicitly modeled** in special cases enum
- No character state flag for Vigilance
- Dynamic mechanic that can't be reliably modeled in static planner

**Calculation Notes**:
```
Endurance Cost Multiplier = 1.0 - (Vigilance Discount)

Vigilance Discount = function(team_average_hp_percentage)
  - Highly situational and team-dependent
  - Not practical to model statically
```

**Python Considerations**:
- **Recommend NOT implementing** - too situational
- Could add optional "Assume X% Vigilance discount" setting
- Most defenders plan builds assuming NO Vigilance (worst case)
- If implemented, apply multiplier to EnduranceCost of all powers

#### 8. **Scourge** (Corruptor)

**Mechanics**:
- Chance to deal **double damage** on targets below 50% HP
- Scales linearly with target HP:
  - 100% HP: 0% scourge chance
  - 50% HP: ~10% scourge chance
  - 25% HP: ~30% scourge chance
  - <5% HP: ~50% scourge chance
- Applies to most damaging attacks
- Critical for finishing off hard targets

**In MidsReborn**:
```csharp
public bool Scourge { get; private set; }

case Enums.eSpecialCase.Scourge:
    if (MidsContext.Character.Scourge)
        return true;
    break;
```

- Toggle to show damage "with scourge" active
- When enabled, applies scourge bonus to damage calculations
- Typically shows average damage including scourge chance

**Calculation Notes**:
```
Scourge Chance = function(target_hp_percentage)
  - Linear scale from 0% to ~50%
  - Most players assume ~25% average scourge chance (target at ~25% HP)

Expected Damage = Base_Damage * (1.0 + Scourge_Chance)

Example with 25% scourge chance:
  Base Damage: 100
  Expected Damage: 100 * 1.25 = 125
```

**Python Considerations**:
- Should be toggleable with assumed scourge rate
- Default OFF or ~10-15% (conservative)
- Allow user to set expected scourge percentage (0-50%)
- Apply as damage multiplier

#### 9. **Domination** (Dominator)

**Mechanics**:
- Builds Domination bar from attacks and control powers
- When full, can activate **Domination** (90 second duration):
  - All control powers have +magnitude (more powerful)
  - All control powers have +duration
  - +damage buff to all attacks
  - Full endurance refill on activation
  - Mez protection while active
- Requires building bar, then manually activating

**In MidsReborn**:
```csharp
public bool Domination { get; private set; }

case Enums.eSpecialCase.Domination:
    if (MidsContext.Character.Domination)
        return true;
    break;
```

- Toggle to show stats "with Domination active"
- When enabled:
  - Control powers show increased magnitude/duration
  - Damage powers show damage buff
- Stored in power effects with `SpecialCase = Domination`

**Calculation Notes**:
```
With Domination Active:
  Control Magnitude *= 2.0
  Control Duration *= 2.0
  Damage Buff = +damage (varies by power, typically +10-20%)
```

**Python Considerations**:
- Toggle for "Domination Active" mode
- Apply multipliers to control effects when toggled
- Apply damage buffs to attacks
- Should be OFF by default (not always active in combat)

#### 10. **Supremacy** (Mastermind)

**Mechanics**:
- Passive **AoE buff** to all pets within range
- Buffs pet accuracy, damage, and resistance
- Always active when pets are nearby
- Stacks with upgrade powers (Equip, Upgrade):
  - Base Supremacy: +25% damage, +10% tohit, +resist
  - With Equip: Enhanced effects
  - With Upgrade: Further enhanced effects

**In MidsReborn**:
```csharp
public bool Supremacy { get; private set; }
public bool SupremacyAndBuffPwr { get; private set; }

case Enums.eSpecialCase.Supremacy:
    if (MidsContext.Character.Supremacy && !MidsContext.Character.PackMentality)
        return true;
    break;

case Enums.eSpecialCase.SupremacyAndBuffPwr:
    if (MidsContext.Character.Supremacy && MidsContext.Character.PackMentality)
        return true;
    break;
```

- Two modes: `Supremacy` (base) and `SupremacyAndBuffPwr` (with upgrades)
- Affects pet powers (damage, tohit, resistance)
- Toggle to show pet stats with/without Supremacy

**Calculation Notes**:
```
Supremacy Buffs (applied to pets):
  Base:
    +25% Damage
    +10% ToHit
    +resist (varies by tier)

  With Upgrades (SupremacyAndBuffPwr):
    Enhanced versions of above
    Additional pet powers unlocked
```

**Python Considerations**:
- Should be ON by default (always active for Masterminds)
- Two-state toggle: Base Supremacy vs With Upgrades
- Apply buffs to pet stats, not player stats
- Requires pet data modeling

### Other Inherents (Not in Primary 10)

**Epic Archetypes** have unique inherents:
- **Kheldian Form Shifts** (Peacebringer/Warshade): Stance changes with different stats
- **Cosmic Balance/Dark Sustenance**: Buffs based on team composition
- **Soldiers of Arachnos**: Leadership-style team buffs

**These are NOT covered in this spec** - they are extremely complex, AT-specific, and rarely used.

## MidsReborn Modeling Capabilities

### What MidsReborn CAN Model

| Inherent | Modeled? | How |
|----------|----------|-----|
| **Fury** | ❌ No | Too dynamic, combat-dependent |
| **Defiance** | ✅ Yes | Toggle + special case effects |
| **Containment** | ✅ Yes | Toggle, 2x damage multiplier |
| **Critical Hit** | ✅ Yes | Toggle, probability-weighted damage |
| **Assassination** | ✅ Partial | Toggle for "from hide", hard to model team scaling |
| **Gauntlet** | ✅ Yes | Taunt effects in power data |
| **Vigilance** | ❌ No | Too situational, team-dependent |
| **Scourge** | ✅ Yes | Toggle + assumed scourge rate |
| **Domination** | ✅ Yes | Toggle for active state |
| **Supremacy** | ✅ Yes | Toggle for base/upgraded modes |

### Modeling Strategy

**Three tiers of inherent modeling:**

1. **Always Active** (baked into AT):
   - Gauntlet (Tanker taunt effects)
   - Supremacy base (Mastermind pet buffs)

2. **Toggleable/Conditional** (user can enable/disable):
   - Defiance (Blaster damage buff)
   - Containment (Controller 2x damage)
   - Critical Hit (Scrapper average damage)
   - Assassination (Stalker from-hide damage)
   - Scourge (Corruptor assumed scourge rate)
   - Domination (Dominator active state)

3. **Not Modeled** (too dynamic/situational):
   - Fury (Brute) - requires combat simulation
   - Vigilance (Defender) - requires team state tracking

## Python Implementation Considerations

### Data Model Requirements

```python
class ArchetypeInherent:
    """Model for archetype inherent power"""
    name: str                    # "Fury", "Defiance", etc.
    archetype: str              # "Brute", "Blaster", etc.
    modeling_type: str          # "always_on", "toggleable", "not_modeled"
    default_state: bool         # Default toggle state
    effects: List[Effect]       # Associated effects

class InherentState:
    """Character's inherent power states"""
    defiance_active: bool = False
    containment_active: bool = False
    critical_hits_active: bool = False
    assassination_active: bool = False
    scourge_active: bool = False
    domination_active: bool = False
    supremacy_mode: str = "base"  # "base", "upgraded", "none"
```

### Calculation Integration

```python
def apply_inherent_effects(power, character):
    """Apply archetype inherent effects to power calculations"""

    # Check archetype and inherent state
    if character.archetype == "Controller" and character.containment_active:
        # Double damage on controlled targets
        power.damage *= 2.0

    if character.archetype == "Scrapper" and character.critical_hits_active:
        # Apply average critical damage
        crit_chance = power.get_critical_chance()
        power.expected_damage *= (1.0 + crit_chance)

    if character.archetype == "Corruptor" and character.scourge_active:
        # Apply scourge bonus
        scourge_rate = character.assumed_scourge_rate or 0.15
        power.expected_damage *= (1.0 + scourge_rate)

    # ... handle other inherents
```

### User Interface Considerations

**Inherent Toggle Controls:**
```
Build Settings:
  [ ] Assume Containment active (Controller)
  [ ] Show critical hit average (Scrapper)
  [ ] Assume Domination active (Dominator)

  Scourge Rate (Corruptor): [____15____]% (0-50%)

  Supremacy Mode (Mastermind):
    ( ) Base
    (•) With Upgrades
    ( ) None
```

**Tooltip Display:**
```
Power: Blaze
  Base Damage: 102.6
  With Containment: 205.2 (2x)
  ^ Only shown if Containment toggle is ON
```

### Testing Requirements

**Test Cases:**

1. **Containment (Controller)**:
   - Verify damage doubles when toggle is ON
   - Verify normal damage when toggle is OFF
   - Verify only damage effects are doubled, not control effects

2. **Critical Hit (Scrapper)**:
   - Verify expected damage = base * (1 + crit_chance)
   - Verify different crit rates for different target types
   - Verify "Show Crits" toggle affects display correctly

3. **Scourge (Corruptor)**:
   - Verify damage boost applies when toggle is ON
   - Verify user can set scourge percentage
   - Verify reasonable default (10-15%)

4. **Domination (Dominator)**:
   - Verify control magnitude/duration boost when active
   - Verify damage buff applies to attacks
   - Verify effects only apply when toggle is ON

5. **Supremacy (Mastermind)**:
   - Verify pet buffs apply in "Base" mode
   - Verify enhanced buffs apply in "With Upgrades" mode
   - Verify no buffs in "None" mode

6. **Defiance (Blaster)**:
   - Verify damage buff effects toggle on/off
   - Verify special case handling works
   - Verify interaction with other damage buffs

## Summary

**Archetype inherents are the defining feature of each AT**, but they vary wildly in how they can be modeled:

- **Some are static** and always apply (Gauntlet taunt effects)
- **Some are toggleable** and can be reasonably modeled (Containment, Domination, Scourge)
- **Some are too dynamic** to model in a static planner (Fury, Vigilance)

**MidsReborn's approach:**
- Store inherent state flags in `Character` class
- Use `eSpecialCase` enum to mark conditional effects
- Validate effects based on character state and toggles
- Allow users to toggle inherents on/off to see "best case" vs "worst case"

**Our Python implementation should follow the same pattern:**
- Toggleable inherents for user control
- Conservative defaults (most toggles OFF)
- Clear UI to show which inherents are active
- Proper effect validation based on character state

**Next Steps:**
- Implement inherent state management in character model
- Add toggle controls to build UI
- Integrate inherent calculations into damage/buff/control formulas
- Test each inherent's effects thoroughly
- Document default assumptions and toggle meanings for users
