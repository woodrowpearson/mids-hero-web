# Incarnate Abilities

## Overview
- **Purpose**: Non-alpha Incarnate slot abilities (Interface, Judgment, Destiny, Lore, Hybrid, Genesis, Vitae, Omega, Stance) - the 9 additional Incarnate slots beyond Alpha
- **Used By**: Character builds at level 50+, build totals, power selection UI
- **Complexity**: Medium-High
- **Priority**: Medium
- **Status**: 🟡 Breadth Complete

## MidsReborn Implementation

### Primary Location
- **File**: `Forms/frmIncarnate.cs`
- **Related Files**:
  - `Core/Enums.cs` - Order enums for each slot type
  - Database files - Incarnate power definitions (accessed via `DatabaseAPI.GetPowersetByName(..., Enums.ePowerSetType.Incarnate)`)

### Incarnate Slot Types

MidsReborn implements 10 total Incarnate slots (Alpha covered in Spec 29):

1. **Alpha** - See Spec 29 (Level Shift + attribute boosts)
2. **Interface** - DoT procs and debuffs applied to attacks
3. **Judgment** - AoE damage powers with large radius
4. **Destiny** - Team-wide buffs, barriers, and heals
5. **Lore** - Summonable pet allies
6. **Hybrid** - Toggle mode powers that provide temp bonuses
7. **Genesis** - Additional buffs (Homecoming-era addition)
8. **Vitae** - Additional functionality (Homecoming-era)
9. **Omega** - Additional functionality (Homecoming-era)
10. **Stance** - Additional functionality (Homecoming-era)

### Button Array Implementation

From `frmIncarnate.cs` lines 256-265:
```csharp
_buttonArray[0] = _alphaBtn;
_buttonArray[1] = _destinyBtn;
_buttonArray[2] = _hybridBtn;
_buttonArray[3] = _interfaceBtn;
_buttonArray[4] = _judgementBtn;
_buttonArray[5] = _loreBtn;
_buttonArray[6] = _genesisButton;
_buttonArray[7] = _stanceButton;
_buttonArray[8] = _vitaeButton;
_buttonArray[9] = _omegaButton;
```

Each button is enabled/disabled based on `DatabaseAPI.ServerData.EnabledIncarnates[button.TextOn]`, allowing server-specific Incarnate slot availability.

### Tier System

All Incarnate abilities follow a 9-tier progression system:

**Tier 1 - Uncommon (Boost/Basic)**:
- Base ability

**Tier 2 - Rare (Core/Radial Branch Split)**:
- Core Boost
- Radial Boost

**Tier 3 - Very Rare (Mid-tier upgrades)**:
- Total Core Revamp/Conversion/Improved/etc.
- Partial Core Revamp/Conversion/Improved/etc.
- Total Radial Revamp/Conversion/Improved/etc.
- Partial Radial Revamp/Conversion/Improved/etc.

**Tier 4 - Ultimate (Top-tier)**:
- Core Paragon/Flawless/Final/Superior/Epiphany/Embodiment
- Radial Paragon/Flawless/Final/Superior/Epiphany/Embodiment

### Order Enums

From `Core/Enums.cs`, each slot type has an ordering enum for UI display:

```csharp
public enum eJudgementOrder
{
    Judgement,               // T1
    Core_Judgement,          // T2 Core
    Radial_Judgement,        // T2 Radial
    Total_Core_Judgement,    // T3 Total Core
    Partial_Core_Judgement,  // T3 Partial Core
    Total_Radial_Judgement,  // T3 Total Radial
    Partial_Radial_Judgement,// T3 Partial Radial
    Core_Final_Judgement,    // T4 Core
    Radial_Final_Judgement   // T4 Radial
}

public enum eInterfaceOrder { ... }  // Similar structure
public enum eLoreOrder { ... }       // Similar structure
public enum eDestinyOrder { ... }    // Similar structure
public enum eHybridOrder { ... }     // Similar structure
public enum eGenesisOrder { ... }    // Similar structure
```

### High-Level Algorithm

```
Incarnate Selection Algorithm (frmIncarnate.cs):

Initialize:
  - Create 10 buttons for each Incarnate slot
  - Enable/disable buttons based on server config
  - Load Alpha slot powers by default

On Slot Button Click:
  1. Set clicked button as checked
  2. Uncheck all other buttons
  3. Load powerset for clicked slot:
     _myPowers = DatabaseAPI.GetPowersetByID(slotName, ePowerSetType.Incarnate).Powers
  4. Call FillLists(slotName)

FillLists(slotName):
  1. Create empty power list
  2. For each ability tree in slot:
     - Parse all tiers using ParseIncarnate()
     - Add to power list in order
  3. Split list into left/right columns
  4. Display in UI with selection state:
     - Enabled: Available for selection
     - Selected: Currently selected in build
     - Disabled: Cannot select (e.g., "Nothing" option)

ParseIncarnate(powerList, slotType, abilityName):
  1. Find all powers matching abilityName
  2. Parse tier from power DisplayName
  3. Use order enum to sort by tier progression
  4. Return sorted list

On Power Click:
  1. Remove all other powers in this slot from build
  2. Add clicked power to build at level 49
  3. Mark power as StatInclude = true
  4. Refresh UI and recalculate stats
```

## Game Mechanics Context

### Incarnate System History

The Incarnate system was introduced in Issue 19 (City of Heroes: Going Rogue) as end-game content for level 50+ characters. It provides additional power and customization through 10 specialized slots.

**Original 5 Slots (Issue 19-20)**:
- Alpha (Issue 19)
- Interface, Judgment, Destiny, Lore (Issue 20)

**Issue 23 Addition**:
- Hybrid

**Homecoming Additions**:
- Genesis, Vitae, Omega, Stance (later additions to private servers)

### Level Shift Mechanics

Certain Incarnate powers provide **Level Shifts** - effectively increasing character level for combat calculations:

- **Alpha T4**: +1 Level Shift (see Spec 29)
- **Lore T4**: +1 Level Shift
- **Destiny T4**: +1 Level Shift

Maximum of **+3 Level Shifts** total, making a level 50 character effectively level 53.

Level shifts affect:
- Hit chance calculations
- Enemy level comparisons
- Combat effectiveness vs. higher-level enemies

Implemented via `Enums.eEffectType.LevelShift` effect type.

### Interface Slot

**Purpose**: Adds proc-based DoT (Damage over Time) and debuffs to attacks

**Available Abilities**:
- Cognitive (Confusion, Psionic damage)
- Degenerative (-Regen, Toxic damage)
- Diamagnetic (-ToHit, -Regen)
- Gravitic (-DMG, -SPD)
- Paralytic (Immobilize, Energy damage)
- Preemptive (-Absorb, -Heal)
- Reactive (Fire damage, -Res)
- Spectral (Negative damage, -DMG)

**Core vs Radial**:
- **Core**: Higher proc chance, lower magnitude
- **Radial**: Lower proc chance, higher magnitude + additional effects

### Judgment Slot

**Purpose**: Powerful AoE (Area of Effect) damage powers with large radius

**Available Abilities**:
- Cryonic (Cold damage)
- Ion (Energy damage, chain effect)
- Mighty (Smashing damage, knockback)
- Pyronic (Fire damage)
- Void (Negative energy damage)
- Vorpal (Lethal damage)

**Core vs Radial**:
- **Core**: Focused damage, smaller radius, higher DPA
- **Radial**: Wider radius, additional effects (DoT, debuffs)

**Mechanics**:
- Long recharge (90-120 seconds base)
- Extremely high damage (200+ mag)
- Very large radius (25-40 feet)

### Destiny Slot

**Purpose**: Team-wide buffs, barriers, and support powers

**Available Abilities**:
- Ageless (+Recharge, +Recovery, +Regen, -Mez)
- Barrier (+Defense, +Resistance, +Absorb)
- Clarion (+Damage, +ToHit, Mez protection)
- Incandescence (+Resistance, +HP, +Regen, Revive)
- Rebirth (+Heal, +Regen, +Recovery)

**Core vs Radial**:
- **Core**: Higher magnitude, shorter duration
- **Radial**: Lower magnitude, longer duration, more gradual

**Mechanics**:
- Two-stage buff: Strong initial buff + weaker lingering buff
- Affects entire team within range
- T4 abilities provide +1 Level Shift

### Lore Slot

**Purpose**: Summon powerful pet allies to fight alongside character

**Available Abilities**:
- Arachnos (Tarantula/Bane Spider pets)
- Banished Pantheon (Spirit pets)
- Carnival (Mask/Strongman pets)
- Cimeroran (Roman soldier pets)
- Clockwork (Robot pets)
- Demons (Demon pets)
- IDF (Imperial Defense Force soldier pets)
- Knives of Vengeance (Assassin pets)
- Longbow (Hero organization pets)
- Nemesis (Steampunk soldier pets)
- Phantom (Spectral pets)
- Polar Lights (Cold-themed pets)
- Rikti (Alien invader pets)
- Robotic Drones (Tech pets)
- Rularuu (Dimensional entity pets)
- Seers (Psychic pets)
- Storm Elemental (Storm-themed pets)
- Talons of Vengeance (Warrior pets)
- Tsoo (Martial artist pets)
- Vanguard (Elite soldier pets)
- Warworks (Advanced robot pets)

**Core vs Radial**:
- **Core**: Superior versions of pets (higher tier, more powerful)
- **Radial**: Improved versions with additional abilities

**Mechanics**:
- Summons 2 pets (rare/very rare) or 2-3 pets (ultimate)
- Pets last until defeated or unsummoned
- Long recharge (600+ seconds)
- T4 abilities provide +1 Level Shift

**Special Parsing**:
Multi-word ability names require special handling in `ParseIncarnate()` (lines 207-225):
- "Banished Pantheon" → strip first 2 words
- "Knives of Vengeance" → strip first 3 words
- "Polar Lights" → strip first 2 words
- "Robotic Drones" → strip first 2 words
- "Storm Elemental" → strip first 2 words
- "Talons of Vengeance" → strip first 3 words

### Hybrid Slot

**Purpose**: Toggle mode powers that provide temporary enhanced capabilities

**Available Abilities**:
- Assault (Offensive toggle - +DMG, +ToHit)
- Control (Mez and control enhancement)
- Melee (Melee combat bonuses)
- Support (Team support and buff enhancement)

**Core vs Radial**:
- **Core**: Embodiment - stronger self-buffs
- **Radial**: Embodiment - team-friendly effects

**Mechanics**:
- Toggle power that drains over time
- Provides strong buffs while active
- 2-minute duration at T4
- Cannot be perma (has downtime even with max recharge)

### Genesis Slot

**Purpose**: Additional buff category (Homecoming server addition)

**Available Abilities**:
- Data (Computation/analysis themed)
- Fate (Destiny-themed)
- Socket (Connection-themed)
- Verdict (Judgment-themed)

**Note**: Less widely documented than original 5 slots due to being a private server addition.

### Vitae, Omega, Stance Slots

**Status**: Homecoming-era additions with limited documentation in MidsReborn source

**Implementation Notes**:
- Buttons present in UI (`_vitaeButton`, `_omegaButton`, `_stanceButton`)
- Enabled/disabled via server config
- Methods present: `VitaeButton_ButtonClicked()`, `OmegaButton_ButtonClicked()`, `StanceButton_ButtonClicked()`
- Power loading works same as other slots: `SetPowerSet("Vitae", ref vitaeButton)`

**Database Status**: Powers may not be fully implemented in all MidsReborn database versions.

### Known Quirks

1. **Single Selection**: Only one ability per slot can be active (enforced in UI click handlers)

2. **Level 49 Assignment**: All Incarnate powers added at level 49 in build:
   ```csharp
   MidsContext.Character.CurrentBuild.AddPower(_myPowers[pIdx], 49).StatInclude = true;
   ```

3. **Interface Proc Mechanics**: Interface procs can trigger on any damage-dealing power, including:
   - Direct attacks
   - Pet attacks
   - Pseudopet attacks (like rain powers)
   - DoT ticks from other powers

4. **Judgment Crash**: Some Judgment powers originally had endurance crash penalties (removed in later balance passes)

5. **Destiny Duration**: Two-stage duration:
   - Strong buff: 30-90 seconds
   - Lingering buff: Additional 30-90 seconds at reduced magnitude

6. **Lore Pet Persistence**: Lore pets persist through zone changes (unlike most other summoned pets)

7. **Hybrid Toggle Drain**: Hybrid powers have both a duration limit AND an endurance cost, making them semi-permanent buffs rather than true toggles

8. **Core vs Radial Choice**: Once selected, Core/Radial branch choice persists through tier upgrades (cannot change from Core to Radial or vice versa without crafting a new ability from scratch)

9. **Level Shift Stacking**: Level Shifts from different sources stack, but cap at +3 total:
   - Alpha T4: +1
   - Lore T4: +1
   - Destiny T4: +1
   - Maximum: Level 50 → Effective Level 53

## Python Implementation Notes

### Proposed Architecture

```python
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List

class IncarnateSlot(Enum):
    """The 10 Incarnate ability slots."""
    ALPHA = "Alpha"
    INTERFACE = "Interface"
    JUDGMENT = "Judgment"
    DESTINY = "Destiny"
    LORE = "Lore"
    HYBRID = "Hybrid"
    GENESIS = "Genesis"
    VITAE = "Vitae"
    OMEGA = "Omega"
    STANCE = "Stance"

class IncarnateTier(Enum):
    """Incarnate ability tier levels."""
    T1_UNCOMMON = 1  # Boost/Basic
    T2_RARE_CORE = 2
    T2_RARE_RADIAL = 3
    T3_VERY_RARE_TOTAL_CORE = 4
    T3_VERY_RARE_PARTIAL_CORE = 5
    T3_VERY_RARE_TOTAL_RADIAL = 6
    T3_VERY_RARE_PARTIAL_RADIAL = 7
    T4_ULTIMATE_CORE = 8
    T4_ULTIMATE_RADIAL = 9

class IncarnateBranch(Enum):
    """Core vs Radial branch choice."""
    NONE = "none"  # T1 only
    CORE = "core"
    RADIAL = "radial"

@dataclass
class IncarnateAbility:
    """Represents a single Incarnate ability option."""
    slot: IncarnateSlot
    ability_name: str  # e.g., "Musculature", "Reactive", "Ion"
    tier: IncarnateTier
    branch: IncarnateBranch
    power_id: int  # Reference to power in database
    display_name: str  # Full name like "Reactive Radial Flawless Interface"
    provides_level_shift: bool = False

    @property
    def tier_number(self) -> int:
        """Get numeric tier (1-4)."""
        if self.tier == IncarnateTier.T1_UNCOMMON:
            return 1
        elif self.tier in [IncarnateTier.T2_RARE_CORE, IncarnateTier.T2_RARE_RADIAL]:
            return 2
        elif self.tier.name.startswith("T3_"):
            return 3
        else:
            return 4

@dataclass
class IncarnateSlotSelection:
    """Represents a character's selection in one Incarnate slot."""
    slot: IncarnateSlot
    ability: Optional[IncarnateAbility]
    enabled: bool  # Server config allows this slot

    def is_selected(self) -> bool:
        """Check if any ability is selected."""
        return self.ability is not None

class IncarnateManager:
    """Manages Incarnate ability selections for a character build."""

    def __init__(self):
        self.slots: dict[IncarnateSlot, IncarnateSlotSelection] = {}
        self._initialize_slots()

    def _initialize_slots(self) -> None:
        """Initialize all 10 Incarnate slots."""
        for slot in IncarnateSlot:
            self.slots[slot] = IncarnateSlotSelection(
                slot=slot,
                ability=None,
                enabled=True  # Default enabled, override from server config
            )

    def select_ability(self, slot: IncarnateSlot, ability: IncarnateAbility) -> None:
        """
        Select an ability for a slot.
        Automatically clears any previous selection in that slot.
        """
        if slot not in self.slots:
            raise ValueError(f"Invalid Incarnate slot: {slot}")

        # Clear previous selection
        self.slots[slot].ability = ability

    def clear_slot(self, slot: IncarnateSlot) -> None:
        """Clear selection from a slot."""
        if slot in self.slots:
            self.slots[slot].ability = None

    def get_level_shift_total(self) -> int:
        """
        Calculate total level shift from all Incarnate abilities.
        Capped at +3.
        """
        shifts = 0
        for slot_selection in self.slots.values():
            if slot_selection.ability and slot_selection.ability.provides_level_shift:
                shifts += 1
        return min(shifts, 3)

    def get_selected_abilities(self) -> List[IncarnateAbility]:
        """Get list of all selected abilities."""
        return [
            sel.ability
            for sel in self.slots.values()
            if sel.ability is not None
        ]

    def get_selection(self, slot: IncarnateSlot) -> Optional[IncarnateAbility]:
        """Get selected ability for a specific slot."""
        return self.slots.get(slot, IncarnateSlotSelection(slot, None, False)).ability
```

### Key Classes and Functions

**IncarnateSlot Enum**:
- Defines all 10 Incarnate slots
- Used for slot identification and UI ordering

**IncarnateTier Enum**:
- Represents the 9-tier progression system
- T1 (Uncommon), T2 (Rare), T3 (Very Rare), T4 (Ultimate)
- Separate entries for Core/Radial branches

**IncarnateBranch Enum**:
- Tracks Core vs Radial choice
- Used to determine which upgrade path is taken

**IncarnateAbility Dataclass**:
- Represents a single craftable Incarnate ability
- Links to underlying Power via `power_id`
- Tracks tier, branch, and level shift status

**IncarnateSlotSelection Dataclass**:
- Represents character's selection in one slot
- Tracks enabled/disabled status (server config)
- Holds selected ability or None

**IncarnateManager Class**:
- Manages all 10 Incarnate slots for a build
- Enforces single-selection-per-slot rule
- Calculates total level shift (capped at +3)
- Provides query methods for selections

### Integration Points

**With Power System**:
```python
def get_incarnate_powers(build: CharacterBuild) -> List[Power]:
    """Get all selected Incarnate powers as Power objects."""
    incarnate_manager = build.incarnate_manager
    powers = []
    for ability in incarnate_manager.get_selected_abilities():
        power = get_power_by_id(ability.power_id)
        powers.append(power)
    return powers
```

**With Build Totals**:
```python
def calculate_effective_level(build: CharacterBuild) -> int:
    """Calculate character's effective level with Incarnate shifts."""
    base_level = build.level
    if base_level == 50:
        shift = build.incarnate_manager.get_level_shift_total()
        return base_level + shift
    return base_level
```

**With Effect Aggregation**:
```python
def aggregate_incarnate_effects(build: CharacterBuild) -> List[Effect]:
    """Collect all effects from selected Incarnate abilities."""
    effects = []
    for power in get_incarnate_powers(build):
        effects.extend(power.effects)
    return effects
```

### Database Schema

```python
# Incarnate ability definitions in database
incarnate_abilities_table = {
    "ability_id": int,          # Unique ID
    "slot": str,                # Slot name
    "ability_name": str,        # Base ability name
    "tier": int,                # 1-4
    "branch": str,              # "none", "core", "radial"
    "power_id": int,            # FK to powers table
    "display_name": str,        # Full display name
    "provides_level_shift": bool,
    "tier_label": str,          # "Boost", "Core Paragon", etc.
}
```

### Validation Rules

```python
def validate_incarnate_selection(
    build: CharacterBuild,
    slot: IncarnateSlot,
    ability: IncarnateAbility
) -> tuple[bool, Optional[str]]:
    """
    Validate an Incarnate ability selection.
    Returns (is_valid, error_message).
    """
    # Check level requirement
    if build.level < 50:
        return False, "Incarnate abilities require level 50"

    # Check slot matches
    if ability.slot != slot:
        return False, f"Ability belongs to {ability.slot}, not {slot}"

    # Check server enables this slot
    if not build.incarnate_manager.slots[slot].enabled:
        return False, f"{slot.value} slot is not enabled on this server"

    # Check branch consistency (if upgrading existing ability)
    existing = build.incarnate_manager.get_selection(slot)
    if existing and existing.ability_name == ability.ability_name:
        # Same ability line - check branch consistency
        if existing.branch != IncarnateBranch.NONE and ability.branch != IncarnateBranch.NONE:
            if existing.branch != ability.branch:
                return False, f"Cannot change from {existing.branch.value} to {ability.branch.value} branch"

    return True, None
```

### Future Depth Implementation Notes

When implementing full Incarnate calculations in Milestone 3:

1. **Interface Proc Calculation**: Implement proc chance per attack, damage type, duration, stacking rules

2. **Judgment Damage Calculation**: Implement radius calculations, damage scaling, target caps, animation times

3. **Destiny Buff Mechanics**: Two-stage buff implementation (strong → lingering), team radius checks, buff magnitude curves

4. **Lore Pet Implementation**: Full pet AI, pet powers, pet scaling, duration tracking, persistence rules

5. **Hybrid Toggle Mechanics**: Duration tracking, endurance drain calculation, toggle state management, buff activation timing

6. **Level Shift Combat Math**: Integrate level shifts into hit chance, damage scale, enemy level comparison calculations

7. **Core vs Radial Effects**: Specific implementation of branch differences for each ability

8. **Server Configuration**: Load enabled/disabled slots from server data files

9. **UI Integration**: Ability tree display, tier progression visualization, branch choice UI

10. **Save/Load**: Serialize Incarnate selections in build format (.mbd files)
