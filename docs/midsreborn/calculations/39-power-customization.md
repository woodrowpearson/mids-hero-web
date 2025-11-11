# Power Customization

## Overview
- **Purpose**: Handle optional power customization including VFX color themes, alternate animations, null FX modes, power replacement pools (Sorcery/Experimentation), and patron pool selection for villain archetypes
- **Used By**: Character builds, power selection UI, import/export systems, data validation
- **Complexity**: Medium
- **Priority**: Low
- **Status**: 🟡 Breadth Complete

## MidsReborn Implementation

### Primary Location
- **File**: `Core/PowersReplTable.cs` - Power replacement table (power pool substitutions, patron selections)
- **File**: `Core/Base/CrypticReplTable.cs` - Cryptic power name replacements (alternate names/IDs)
- **Data Files**:
  - `PowersReplTable.mhd` - Numeric power ID replacement table
  - `CrypticPowerNames.mhd` - String-based power name replacement table

### Key Classes

**PowersReplTable**:
```csharp
public class PowersReplTable
{
    private struct AlternateEntry
    {
        public int SourcePowerId;    // Original power ID
        public int TargetPowerId;    // Replacement power ID
        public string Archetype;     // AT-specific (patron pools) or "" (global)
    }

    public int FetchAlternate(int oldId, string archetype = "");
    public bool KeyExists(int id);
}
```

**CrypticReplTable**:
```csharp
public class CrypticReplTable
{
    private Dictionary<string, string> _table;  // Original name -> Replacement name

    public string FetchAlternate(string id);    // Get replacement power name
    public string FetchSource(string id);       // Get original power name
}
```

### High-Level Algorithm

```
Power Customization System:

1. POWER REPLACEMENT (Mechanical Effect):
   Load PowersReplTable from PowersReplTable.mhd:
     - Parse file format: [Archetype] sections followed by "oldId, newId" pairs
     - [Global] section applies to all archetypes
     - [Brute], [Tanker], etc. sections are AT-specific
     - Store as list of (SourcePowerId, TargetPowerId, Archetype) tuples

   When character selects a power:
     - Check PowersReplTable.KeyExists(powerId)
     - If replacement exists:
         replacementId = FetchAlternate(powerId, characterArchetype)
         If AT-specific replacement found: use replacementId
         Else if global replacement found: use replacementId
         Else: use original powerId

   Use cases:
     - Patron pool selection (4 patron choices per villain AT)
     - Power pool replacement (Sorcery, Experimentation, etc.)
     - Power substitution when powers are removed/renamed

2. POWER NAME REMAPPING:
   Load CrypticReplTable from CrypticPowerNames.mhd:
     - Parse file format: "oldName, newName" pairs
     - Store as Dictionary<string, string>

   When importing builds or matching power names:
     - Check if power name exists in table
     - Use FetchAlternate(powerName) to get current name
     - Use FetchSource(powerName) to get original name

   Purpose:
     - Map obsolete power names to current names
     - Handle power renames across game versions
     - Support legacy build imports

3. VFX CUSTOMIZATION (No Mechanical Effect):
   Color themes:
     - Bright, Dark, Light
     - Per-powerset color tints
     - Stored in character build data
     - NO effect on power mechanics, damage, or timing

   Null/Minimal FX:
     - Reduces visual effects for performance
     - No mechanical effect
     - Client-side only preference

4. ALTERNATE ANIMATIONS (Potential Timing Effect):
   Some alternate animations have different timing:
     - CastTime may differ from original
     - ActivatePeriod may differ
     - Root time may differ

   Implementation note:
     - MidsReborn Power class stores CastTime, ActivatePeriod
     - Alternate animations would need separate power entries
       OR alternate timing stored in power data
     - Current implementation: appears to use separate power IDs
       for animations with different mechanics

5. CONSISTENCY VALIDATION:
   CheckConsistency():
     - Verify no duplicate source power IDs
     - Verify target power IDs exist in database
     - Remove invalid replacement pairs
     - Show warnings to user for data issues
```

### Power Replacement File Format

**PowersReplTable.mhd**:
```
# Comments start with #
# Global replacements apply to all ATs
[Global]
1234, 5678  # PowerID 1234 -> PowerID 5678

# AT-specific replacements (patron pools)
[Brute]
2000, 2001  # Patron choice 1
2000, 2002  # Patron choice 2 (same source, different replacement)

[Corruptor]
2000, 2003
2000, 2004
```

**CrypticPowerNames.mhd**:
```
# Old power name -> Current power name
Power.Blaster_Melee.Power_Punch, Power.Blaster_Manipulation.Power_Punch
Power.Old_Set.Old_Power, Power.New_Set.New_Power
```

## Game Mechanics Context

### Historical Context

**Power Customization Evolution**:
- **Issue 16 (August 2009)**: Power customization introduced
  - Color tinting for most powers (VFX only)
  - Bright, Dark, Light theme options
  - No mechanical changes, purely cosmetic

- **Alternate Animations**: Added gradually over time
  - Most alternate animations are cosmetic only
  - Some have different cast times/root times (mechanical effect!)
  - Examples: Martial Combat alternate animations for some powersets

- **Power Pool Replacements**: Added in later issues
  - Sorcery (replaces Presence, Concealment, Experimentation, or other pool)
  - Experimentation (replaces pool power slot)
  - Players choose replacement at power selection

- **Patron Pools** (Villain-only, Issue 7+):
  - Level 41+ Epic Pools for villains
  - 4 patron choices per villain archetype
  - Choice was permanent in original game (locked after first pick)
  - Later made respecable

### Power Replacement Use Cases

**1. Patron Pool Selection** (Most Common):
- Villain archetypes get 4 patron pool choices at level 41+
- Example for Brute:
  - Mace Mastery (Black Scorpion)
  - Mu Mastery (Scirocco)
  - Soul Mastery (Ghost Widow)
  - Leviathan Mastery (Captain Mako)
- Each patron pool occupies same "slot" but provides different powers
- PowersReplTable maps source patron pool ID to selected variant

**2. Power Pool Replacement**:
- Newer power pools replace other pools
- Sorcery and Experimentation are examples
- Character can take replacement pool instead of standard pool
- Uses same replacement table mechanism

**3. Power Renames/Removals**:
- When devs rename or remove powers
- Replacement table ensures old builds still load
- Maps obsolete power IDs to current power IDs

### VFX vs Mechanical Customization

**VFX Only (No Calculation Effect)**:
- Color tinting (bright/dark/light themes)
- Null FX / Minimal FX modes
- Particle effect density
- These are purely visual, ignore for calculations

**Mechanical Effect (Affects Calculations)**:
- Alternate animations with different cast times
- Power replacement pools (different powers entirely)
- Patron pool selection (different power sets)
- These change actual power mechanics!

### Known Quirks

**Alternate Animation Timing**:
- Most alternate animations are cosmetic
- Some DO change cast time or root time
- Example: Martial Combat alternates may have shorter/longer animations
- MidsReborn must track this if animations affect DPS calculations

**Patron Pool Locking**:
- Original game: patron choice was permanent
- Modern game: can respec patron pools
- Build planner should allow patron reselection

**Power Pool Replacement Stacking**:
- Can't take both Sorcery AND the pool it replaces
- Mutually exclusive choices
- Validation required when building character

**CastTime vs ActivatePeriod**:
- Alternate animations affect `CastTime` (activation time)
- Toggle powers use `ActivatePeriod` (tick rate)
- Both stored in Power class, need separate tracking for alternates

## Python Implementation Notes

### Proposed Architecture

**Dataclasses**:
```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, List

class CustomizationType(Enum):
    """Types of power customization."""
    VFX_ONLY = "vfx_only"              # Color/FX, no mechanical effect
    ALTERNATE_ANIMATION = "alternate"   # May affect timing
    POWER_REPLACEMENT = "replacement"   # Different power entirely
    PATRON_POOL = "patron"              # Villain epic pool selection

@dataclass
class PowerReplacement:
    """Power replacement entry (patron pools, power pool replacements)."""
    source_power_id: int
    target_power_id: int
    archetype: Optional[str] = None  # None = global, else AT-specific
    replacement_type: CustomizationType = CustomizationType.POWER_REPLACEMENT

@dataclass
class AlternateAnimation:
    """Alternate animation with potential timing changes."""
    power_id: int
    animation_name: str
    cast_time: Optional[float] = None      # If different from base
    activate_period: Optional[float] = None # If different from base
    root_time: Optional[float] = None       # If different from base

@dataclass
class PowerCustomization:
    """Power customization state for a character build."""
    # VFX customization (no mechanical effect)
    color_theme: str = "default"  # "default", "bright", "dark", "light"
    null_fx: bool = False          # Minimal FX mode

    # Mechanical customizations
    power_replacements: Dict[int, int] = None  # powerId -> replacementId
    alternate_animations: Dict[int, str] = None # powerId -> animationName
    selected_patron_pool: Optional[str] = None  # For villain ATs

    def __post_init__(self):
        if self.power_replacements is None:
            self.power_replacements = {}
        if self.alternate_animations is None:
            self.alternate_animations = {}
```

### Key Functions

```python
class PowerReplacementTable:
    """Manages power replacement mappings."""

    def __init__(self):
        self.replacements: List[PowerReplacement] = []
        self._global_map: Dict[int, int] = {}
        self._at_maps: Dict[str, Dict[int, int]] = {}

    def load_from_file(self, filepath: str) -> None:
        """
        Load PowersReplTable.mhd format.

        Format:
            # Comments
            [Global]
            sourceId, targetId

            [Archetype]
            sourceId, targetId
        """
        current_at = None

        for line in read_file_lines(filepath):
            line = remove_comments(line).strip()
            if not line:
                continue

            # Check for [Section] headers
            if match := re.match(r'\[([^\]]+)\]', line):
                current_at = match.group(1).lower()
                if current_at == "global":
                    current_at = None
                continue

            # Parse "sourceId, targetId" pairs
            if ',' in line:
                parts = [p.strip() for p in line.split(',')]
                if len(parts) == 2:
                    source_id = int(parts[0])
                    target_id = int(parts[1])
                    self.add_replacement(source_id, target_id, current_at)

    def add_replacement(self, source_id: int, target_id: int,
                       archetype: Optional[str] = None) -> None:
        """Add a power replacement mapping."""
        replacement = PowerReplacement(
            source_power_id=source_id,
            target_power_id=target_id,
            archetype=archetype
        )
        self.replacements.append(replacement)

        if archetype is None:
            self._global_map[source_id] = target_id
        else:
            if archetype not in self._at_maps:
                self._at_maps[archetype] = {}
            self._at_maps[archetype][source_id] = target_id

    def fetch_alternate(self, power_id: int,
                       archetype: Optional[str] = None) -> int:
        """
        Get replacement power ID.

        Args:
            power_id: Original power ID
            archetype: Character's archetype (for patron pools)

        Returns:
            Replacement power ID, or original if no replacement exists
        """
        # Check AT-specific replacements first
        if archetype:
            at_lower = archetype.lower()
            if at_lower in self._at_maps:
                if power_id in self._at_maps[at_lower]:
                    return self._at_maps[at_lower][power_id]

        # Check global replacements
        if power_id in self._global_map:
            return self._global_map[power_id]

        # No replacement, return original
        return power_id

    def key_exists(self, power_id: int) -> bool:
        """Check if power has any replacement."""
        if power_id in self._global_map:
            return True
        for at_map in self._at_maps.values():
            if power_id in at_map:
                return True
        return False


class CrypticNameTable:
    """Manages power name remapping for imports."""

    def __init__(self):
        self._name_map: Dict[str, str] = {}  # old name -> new name
        self._reverse_map: Dict[str, str] = {}  # new name -> old name

    def load_from_file(self, filepath: str) -> None:
        """
        Load CrypticPowerNames.mhd format.

        Format:
            # Comments
            oldPowerName, newPowerName
        """
        for line in read_file_lines(filepath):
            line = remove_comments(line).strip()
            if not line or ',' not in line:
                continue

            parts = [p.strip() for p in line.split(',', 1)]
            if len(parts) == 2:
                old_name = parts[0]
                new_name = parts[1]
                self._name_map[old_name] = new_name
                self._reverse_map[new_name] = old_name

    def fetch_alternate(self, power_name: str) -> str:
        """Get current power name from old name."""
        return self._name_map.get(power_name, power_name)

    def fetch_source(self, power_name: str) -> str:
        """Get original power name from current name."""
        return self._reverse_map.get(power_name, power_name)


def select_patron_pool(character: 'Character',
                       patron_pool_id: int,
                       replacement_table: PowerReplacementTable) -> None:
    """
    Select a patron pool for villain archetype.

    Args:
        character: Character build
        patron_pool_id: ID of selected patron pool (1-4)
        replacement_table: Power replacement table

    Side effects:
        Updates character.customization.selected_patron_pool
        Updates character.customization.power_replacements
    """
    if character.archetype.alignment != "Villain":
        raise ValueError("Patron pools only available for villain archetypes")

    if character.level < 41:
        raise ValueError("Patron pools available at level 41+")

    # Get patron pool base ID for this AT
    base_patron_id = get_patron_base_id(character.archetype)

    # Calculate selected patron ID (base + patron_pool_id offset)
    selected_id = base_patron_id + patron_pool_id

    # Use replacement table to map generic patron slot to specific patron
    actual_patron_id = replacement_table.fetch_alternate(
        base_patron_id,
        character.archetype.name
    )

    # Update character customization
    character.customization.selected_patron_pool = get_patron_name(patron_pool_id)
    character.customization.power_replacements[base_patron_id] = actual_patron_id


def get_effective_cast_time(power: 'Power',
                           customization: PowerCustomization) -> float:
    """
    Get effective cast time considering alternate animations.

    Args:
        power: Base power data
        customization: Character's customization settings

    Returns:
        Cast time in seconds (may differ from base if alternate animation)
    """
    # Check if alternate animation selected
    if power.power_id in customization.alternate_animations:
        anim_name = customization.alternate_animations[power.power_id]

        # Look up alternate animation data
        alt_anim = get_alternate_animation(power.power_id, anim_name)

        # Return alternate cast time if different, else base
        if alt_anim and alt_anim.cast_time is not None:
            return alt_anim.cast_time

    # No alternate or no timing change, use base cast time
    return power.cast_time


def validate_power_selection(character: 'Character',
                             power_id: int,
                             replacement_table: PowerReplacementTable) -> int:
    """
    Validate and resolve power selection.

    Checks for:
    - Power replacements (patron pools, pool replacements)
    - Mutual exclusions (can't take Sorcery + replaced pool)

    Args:
        character: Character build
        power_id: Requested power ID
        replacement_table: Power replacement table

    Returns:
        Actual power ID to use (may be replacement)

    Raises:
        ValueError: If power selection is invalid
    """
    # Check for replacement
    actual_id = replacement_table.fetch_alternate(
        power_id,
        character.archetype.name
    )

    # Check mutual exclusions for pool replacements
    if is_pool_replacement(actual_id):
        replaced_pools = get_replaced_pools(actual_id)
        for pool_id in replaced_pools:
            if character.has_power_from_pool(pool_id):
                raise ValueError(
                    f"Cannot take {get_power_name(actual_id)}: "
                    f"replaces {get_pool_name(pool_id)} which is already selected"
                )

    return actual_id
```

### Integration Points

**Build Import/Export**:
```python
# When importing build, remap obsolete power names
cryptic_table = CrypticNameTable()
cryptic_table.load_from_file("CrypticPowerNames.mhd")

for power_entry in imported_powers:
    # Resolve old power names to current names
    current_name = cryptic_table.fetch_alternate(power_entry.name)
    power_entry.name = current_name
```

**Power Selection**:
```python
# When character selects power, check for replacements
replacement_table = PowerReplacementTable()
replacement_table.load_from_file("PowersReplTable.mhd")

actual_power_id = replacement_table.fetch_alternate(
    selected_power_id,
    character.archetype.name
)

character.add_power(actual_power_id, level)
```

**DPS Calculations**:
```python
# When calculating DPS, use effective cast time
cast_time = get_effective_cast_time(power, character.customization)

dps = total_damage / (recharge_time + cast_time)
```

### Data Storage

**Database Schema**:
```sql
-- Power replacement table
CREATE TABLE power_replacements (
    id SERIAL PRIMARY KEY,
    source_power_id INTEGER NOT NULL,
    target_power_id INTEGER NOT NULL,
    archetype VARCHAR(50),  -- NULL for global
    replacement_type VARCHAR(50),
    UNIQUE(source_power_id, archetype)
);

-- Alternate animations (if different timing)
CREATE TABLE alternate_animations (
    id SERIAL PRIMARY KEY,
    power_id INTEGER NOT NULL,
    animation_name VARCHAR(100) NOT NULL,
    cast_time REAL,          -- NULL if same as base
    activate_period REAL,    -- NULL if same as base
    root_time REAL,          -- NULL if same as base
    UNIQUE(power_id, animation_name)
);

-- Character build customization
CREATE TABLE build_customization (
    build_id INTEGER PRIMARY KEY REFERENCES builds(id),
    color_theme VARCHAR(20) DEFAULT 'default',
    null_fx BOOLEAN DEFAULT FALSE,
    selected_patron_pool VARCHAR(50),
    -- JSON field for power replacements
    power_replacements JSONB,
    -- JSON field for alternate animations
    alternate_animations JSONB
);
```

### Testing Considerations

**Unit Tests**:
```python
def test_power_replacement_global():
    """Test global power replacement."""
    table = PowerReplacementTable()
    table.add_replacement(1000, 2000)  # Global

    assert table.fetch_alternate(1000) == 2000
    assert table.fetch_alternate(1000, "Brute") == 2000

def test_power_replacement_at_specific():
    """Test AT-specific replacement (patron pools)."""
    table = PowerReplacementTable()
    table.add_replacement(1000, 2001, "Brute")
    table.add_replacement(1000, 2002, "Corruptor")

    assert table.fetch_alternate(1000, "Brute") == 2001
    assert table.fetch_alternate(1000, "Corruptor") == 2002
    assert table.fetch_alternate(1000, "Tanker") == 1000  # No replacement

def test_patron_pool_selection():
    """Test patron pool selection for villain AT."""
    character = create_villain_brute(level=41)
    table = PowerReplacementTable()
    # ... load patron mappings ...

    select_patron_pool(character, patron_pool_id=1, replacement_table=table)

    assert character.customization.selected_patron_pool == "Mace Mastery"
    assert 1000 in character.customization.power_replacements

def test_alternate_animation_cast_time():
    """Test alternate animation affecting cast time."""
    power = create_power(cast_time=1.32)
    customization = PowerCustomization()
    customization.alternate_animations[power.power_id] = "martial_alt"

    # Mock alternate animation with different cast time
    alt_anim = AlternateAnimation(
        power_id=power.power_id,
        animation_name="martial_alt",
        cast_time=1.0  # Faster than base
    )

    effective_time = get_effective_cast_time(power, customization)
    assert effective_time == 1.0  # Uses alternate cast time

def test_vfx_customization_no_mechanical_effect():
    """Verify VFX customization doesn't affect calculations."""
    power = create_power(damage=100)
    customization1 = PowerCustomization(color_theme="default")
    customization2 = PowerCustomization(color_theme="dark", null_fx=True)

    damage1 = calculate_power_damage(power, customization1)
    damage2 = calculate_power_damage(power, customization2)

    assert damage1 == damage2  # VFX changes don't affect damage
```

### Performance Considerations

**Caching**:
- Load replacement tables once at startup
- Cache resolved power IDs to avoid repeated lookups
- Index AT-specific maps by archetype for O(1) lookup

**Memory**:
- Replacement tables are small (hundreds of entries)
- Store as dictionaries for fast lookup
- No need for complex data structures

### Future Extensibility

**Deferred to Milestone 3 (Depth)**:
- Complete alternate animation timing database
- UI for patron pool selection
- Validation of mutually exclusive pool replacements
- Import/export of customization settings
- Migration of legacy builds with obsolete power names

**Not Implemented**:
- VFX color customization (no mechanical effect)
- Null FX mode (client-side only)
- Power recoloring UI (visual only)
