# Special Cases and Edge Cases

## Overview
- **Purpose**: Document miscellaneous edge cases, one-off power mechanics, workarounds for game bugs, and special handling not covered by other calculation specs
- **Used By**: Build import, power validation, UI display, all calculation systems
- **Complexity**: Medium (individually simple, but many scattered cases)
- **Priority**: Low (doesn't affect core calculations, but required for full game compatibility)
- **Status**: 🟡 Breadth Complete

## MidsReborn Implementation

### Primary Locations

Special case handling is scattered throughout MidsReborn codebase:

**Import String Fixes**:
- **File**: `clsUniversalImport.cs`
- **Methods**:
  - `EnhNameFix()` - Lines 71-100+ - Fixes enhancement name mismatches
  - `PowerNameFix()` - Lines 428-434 - Fixes power name spelling differences

**Spelling/Name Corrections**:
- **File**: `clsToonX.cs`
- **Method**: `FixSpelling()` - Lines 338-343 - British vs American spelling

**Special Case Effects**:
- **File**: `Core/Base/Data_Classes/Effect.cs`
- **Property**: `SpecialCase` - Enums.eSpecialCase enum value
- **File**: `Core/Enums.cs`
- **Enum**: `eSpecialCase` - Lines 1006-1071 - 65 special case flags

**Power Prerequisites**:
- **File**: `Core/Base/Data_Classes/Power.cs`
- **Property**: `GroupMembership` - Array of group names for pool prerequisites
- **Property**: `Requires` - Requirement class for power dependencies

**Pool Power Padding**:
- **File**: `BuildImportTools.cs`
- **Method**: `PadPowerPools()` - Lines 305-327 - Ensures 4 pool slots exist

**Enhancement Level Fixing**:
- **File**: `Core/Build.cs`
- **Method**: `CheckAndFixAllEnhancements()` - Lines 681-699+ - Validates IO levels

**Arcana Time**:
- **File**: `Forms/frmRotationHelper.cs`
- **Method**: `CalcArcanaCastTime()` - Line 219-222 - Applies 132ms server tick rounding

### Special Case Categories

MidsReborn handles these categories of special cases:

**1. eSpecialCase Enum (65+ cases)**:
```
None, Hidden, Domination, Scourge, Mezzed, CriticalHit, CriticalBoss,
CriticalMinion, Robot, Assassination, Containment, Defiance,
TargetDroneActive, Combo, VersusSpecial, NotDisintegrated, Disintegrated,
NotAccelerated, Accelerated, NotDelayed, Delayed, ComboLevel0-3,
FastMode, NotAssassination, PerfectionOfBody0-3, PerfectionOfMind0-3,
PerfectionOfSoul0-3, TeamSize1-3, NotComboLevel3, ToHit97,
DefensiveAdaptation, EfficientAdaptation, OffensiveAdaptation,
NotDefensiveAdaptation, NotDefensiveNorOffensiveAdaptation,
BoxingBuff, KickBuff, Supremacy, SupremacyAndBuffPwr, PetTier2,
PetTier3, PackMentality, NotPackMentality, FastSnipe, NotFastSnipe,
CrossPunchBuff, NotCrossPunchBuff, NotBoxingBuff, NotKickBuff
```

**2. Power/Enhancement Name Fixes**:
- British spelling: "Armour" → "Armor"
- Power set naming: "Electric Mastery" → "Electrical Mastery"
- Power name fixes: "Gravity Emanation" → "Gravitic Emanation"
- Enhancement abbreviations: "Rechg" → "RechRdx", "TH_Buf" → "ToHit"

**3. Archetype Pseudo-Pets**:
- Special archetype entries for non-combatants: "OilSlickTarget", "Monument", "Sniper", "PracticeBot", "Underling"

**4. Power Pool Prerequisites**:
- Most pool powers require picking 2 powers from same pool first
- Travel powers typically locked behind 2 prerequisite powers
- Epic pools require level 35+

**5. Database Inconsistencies**:
- HACK comment in Character.cs line 1662: "assumes at least 8 powersets exist"
- Pool slot validation ensures exactly 4 pool slots (0-3 used)
- Enhancement IO level bounds checking

**6. Animation/Cast Time Quirks**:
- Arcana Time: Real cast times quantized to 132ms server ticks
- Formula: `ceil(castTime / 0.132) + 1) * 0.132`
- Example: 1.0s cast → 1.188s actual (9 ticks)

**7. Conditional Effects**:
- Effects can have `ActiveConditionals` that gate their activation
- Mutually exclusive with `SpecialCase` - cannot use both
- Example: Defiance damage buff only active when mezzed

### High-Level Algorithm

```
Special Case Handling Process:

1. String Import Fixes:
   - When importing build from game:
     - Apply PowerNameFix() to all power names
     - Apply EnhNameFix() to all enhancement names
     - Apply FixSpelling() to powerset names
   - Fixes ensure database lookup succeeds

2. Power Prerequisites Check:
   - For each power being picked:
     - If power has Requires.PowerIDList:
       - Verify all required powers are already picked
     - If power.GroupMembership is set:
       - Count powers from same group already picked
       - Verify meets minimum (usually 2 for travel powers)

3. Special Case Effect Evaluation:
   - For each effect with SpecialCase != None:
     - Check character's current special case flags:
       - Domination, Scourge, CriticalHit, etc.
     - Only include effect value if flag is active
     - Example: Defiance buff only adds if character.Defiance == true

4. Pool Power Validation:
   - When loading/importing build:
     - Count pool powersets (slots 3-6)
     - If < 4 pools, pad with empty "Pool.None" entries
     - Ensures consistent 8-slot powerset array

5. Enhancement Level Fixing:
   - After loading build:
     - For each slotted IO:
       - Call enhancement.CheckAndFixIOLevel(currentLevel)
       - Clamps to valid range for that IO (10-50 typically)

6. Arcana Time Calculation:
   - When displaying attack chains:
     - If UseArcanaTime flag enabled:
       - Real cast time = CalcArcanaCastTime(base cast time)
     - Else use base cast time
   - Affects DPS calculations

7. Archetype Inherent Conditionals:
   - Track character flags: Domination, Scourge, etc.
   - When calculating totals:
     - Include/exclude conditional effects based on flags
     - Example: Domination doubles mez duration when active

8. Hidden Power Effects:
   - Some effects flagged as SpecialCase.Hidden
   - Not shown in power info display
   - Still applied to calculations
   - Example: Behind-the-scenes accuracy adjustments

9. One-Off Power Mechanics:
   - Oil Slick Arrow creates "OilSlickTarget" pseudo-pet
   - Igniting it deals AoE damage
   - Requires special archetype entry in database

10. Database Workarounds:
    - If powersets array too short, extend with nulls
    - If pool slots missing, fill to 4 slots
    - If enhancement level invalid, clamp to bounds
```

### Key Logic Snippets

**Enhancement Name Fixes** (`clsUniversalImport.cs` lines 71-100):
```csharp
private static string EnhNameFix(string iStr)
{
    iStr = iStr.Replace("Fly", "Flight");
    iStr = iStr.Replace("Rechg", "RechRdx");
    iStr = iStr.Replace("TH_Buf", "ToHit");
    iStr = iStr.Replace("TH_DeBuf", "ToHitDeb");
    iStr = iStr.Replace("DmgRes", "ResDam");
    // ... many more replacements
    iStr = iStr.Replace("HO:", ""); // Hamidon Origin prefix
    iStr = iStr.Replace("CentiExp", "Centri"); // HO shorthand
    return iStr;
}
```

**Power Name Fixes** (`clsUniversalImport.cs` lines 428-434):
```csharp
private static string PowerNameFix(string iStr)
{
    return clsToonX.FixSpelling(iStr)
        .Replace("Gravity Emanation", "Gravitic Emanation")
        .Replace("Dark Matter Detonation", "Dark Detonation")
        .Replace("Dark Nova Emmanation", "Dark Nova Emanation");
}
```

**Spelling Fixes** (`clsToonX.cs` lines 338-343):
```csharp
public static string FixSpelling(string iString)
{
    iString = iString?.Replace("Armour", "Armor");
    iString = iString?.Replace("Electric Mastery", "Electrical Mastery");
    return iString;
}
```

**Arcana Time Calculation** (`Forms/frmRotationHelper.cs` lines 219-222):
```csharp
private float CalcArcanaCastTime(float castTime)
{
    // Server processes actions in 132ms ticks (server tick rate)
    // Formula: ceil(castTime / 0.132) ticks + 1 tick latency
    return (float)(Math.Ceiling(castTime / 0.132f) + 1) * 0.132f;
}
```

**Pool Power Padding** (`BuildImportTools.cs` lines 305-327):
```csharp
public static void PadPowerPools(ref UniqueList<string> listPowersets)
{
    var nbPools = CountPools(listPowersets);
    if (nbPools == 4) return; // Already have 4 pool slots

    // Get unused pool powersets from database
    var pickedPowerPools = listPowersets
        .Where(ps => ps.StartsWith("Pool.", StringComparison.OrdinalIgnoreCase))
        .ToArray();
    var dbPowerPools = Database.Instance.Powersets
        .Where(ps => ps != null &&
                     ps.FullName.StartsWith("Pool.") &&
                     !pickedPowerPools.Contains(ps.FullName))
        .OrderBy(e => e.DisplayName)
        .Select(e => e.FullName)
        .ToArray();

    // Pad to 4 pool slots with unused pools
    for (var i = 0; i < 4 - nbPools; i++)
    {
        listPowersets.Add(dbPowerPools[i]);
    }
}
```

**Special Case in Effect** (`clsToonX.cs` line 605):
```csharp
// Only include damage buff if it's NOT a Defiance special case
// OR if Defiance is actually active
if (!(effect.isEnhancementEffect &
      effect.EffectClass == Enums.eEffectClass.Tertiary |
      effect.ValidateConditional("Active", "Defiance") |
      effect.SpecialCase == Enums.eSpecialCase.Defiance))
{
    nBuffs.Damage[(int)effect.DamageType] += shortFx.Value[shortFxIdx];
}
```

**Database Size Hack** (`Character.cs` line 1662):
```csharp
// HACK: this assumes at least 8 powersets exist,
// but the database is fully editable.
PoolLocked[0] = PowersetUsed(Powersets[3]) & PoolUnique(Enums.PowersetType.Pool0);
PoolLocked[1] = PowersetUsed(Powersets[4]) & PoolUnique(Enums.PowersetType.Pool1);
// ... assumes Powersets[3-7] are valid pool/epic slots
```

## Game Mechanics Context

### Why Special Cases Exist

**Historical Context**:
1. **Game Evolution**: City of Heroes launched in 2004, evolved for 8+ years
   - Powers renamed during development
   - Mechanics changed but old data persisted
   - Import format never fully standardized

2. **Server Quirks**:
   - 132ms server tick rate creates animation time quantization
   - "Arcana Time" discovered by player Arcanaville through testing
   - Became official mechanic in later issues

3. **Database Inconsistencies**:
   - Multiple naming conventions over time
   - British vs American English in early data
   - Abbreviation changes in enhancement names

4. **One-Off Mechanics**:
   - Oil Slick Arrow needed pseudo-pet for ignition mechanic
   - Some AT inherents (Defiance, Domination) have complex conditionals
   - Combo systems added late, required special case flags

### Power Pool Prerequisites

**Standard Pattern**:
- Pool powers 1-2: Always available
- Pool power 3: Requires 1 previous power from pool
- Pool power 4 (travel): Requires 2 previous powers from pool
- Pool power 5: Requires 3 previous powers from pool (rare)

**Example - Speed Pool**:
1. Flurry (available at level 4)
2. Hasten (available at level 4)
3. Super Speed (requires 1 Speed power)
4. Whirlwind (requires 2 Speed powers)

**Epic Pools**:
- Require level 35+
- Locked to AT (different epics for Tanker vs Scrapper)
- Follow same prerequisite pattern within pool

### Archetype Inherents as Special Cases

Many AT inherents use `SpecialCase` flags:

**Dominator - Domination**:
- Builds Domination bar through attacks
- When activated: doubles mez duration, refills endurance
- Effects flagged with `SpecialCase.Domination`
- Only active when Domination button pressed

**Blaster - Defiance**:
- Damage buff scales with endurance depletion
- Additional buffs when mezzed
- Effects flagged with `SpecialCase.Defiance`

**Corruptor - Scourge**:
- Chance to deal double damage to low-HP targets
- Scales from 0% (full HP target) to 100% (near-death)
- Effects flagged with `SpecialCase.Scourge`

**Controller - Containment**:
- Double damage to controlled targets
- Effects flagged with `SpecialCase.Containment`

**Scrapper/Stalker - Critical Hits**:
- Random chance for double damage
- Higher vs minions (10%) than bosses (5%)
- `SpecialCase.CriticalHit`, `CriticalBoss`, `CriticalMinion`

**Sentinel - Opportunity**:
- Offensive/Defensive/Efficient adaptations
- Multiple `SpecialCase` flags for each mode

**Stalker - Assassination/Hidden**:
- Massive damage bonus from Hide
- `SpecialCase.Hidden`, `SpecialCase.Assassination`

### Known Quirks

**1. Arcana Time is NOT Optional**:
- All players experience 132ms quantization
- MidsReborn offers toggle for display purposes
- Real DPS calculations should ALWAYS use Arcana Time

**2. Enhancement Name Chaos**:
- Game export uses abbreviated names
- Database uses full names
- Multiple abbreviation conventions exist
- Import MUST apply fixes or lookups fail

**3. Pool Slot Assumptions**:
- Code assumes exactly 8 powerset slots:
  - Slots 0-1: Primary/Secondary
  - Slot 2: Inherent (auto-generated)
  - Slots 3-6: Four pool slots (may be unused)
  - Slot 7: Epic pool
- Import must pad to this structure

**4. Oil Slick Arrow**:
- Creates pseudo-entity with archetype "OilSlickTarget"
- Has HP, can be attacked
- When destroyed (ignited), deals AoE damage
- Only power with this mechanic

**5. Conditional vs Special Case Mutual Exclusion**:
- Effect cannot have both `ActiveConditionals` AND `SpecialCase`
- Database editor enforces this rule
- Represents two different conditional systems that don't mix

**6. Hidden Effects**:
- Some effects not shown in UI (`SpecialCase.Hidden`)
- Still apply to calculations
- Example: Behind-the-scenes accuracy modifiers
- Prevents player confusion about inconsistent numbers

**7. Team Size Scaling**:
- Some effects scale with team size
- `SpecialCase.TeamSize1`, `TeamSize2`, `TeamSize3`
- Example: Leadership pool buffs scale with nearby teammates
- MidsReborn allows setting team size for calculations

**8. Combo Systems**:
- Added in later issues (Dual Blades, Staff Fighting, etc.)
- `ComboLevel0-3` flags track combo state
- Powers have different effects at different combo levels
- `NotComboLevel3` for "if not at max combo" effects

## Python Implementation Notes

### Proposed Architecture

**Module**: `mids_hero_web/calculations/special_cases.py`

**Key Classes**:

```python
from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Set, Optional, Callable

class SpecialCase(Enum):
    """Mirrors MidsReborn's eSpecialCase enum"""
    NONE = auto()
    HIDDEN = auto()
    DOMINATION = auto()
    SCOURGE = auto()
    CRITICAL_HIT = auto()
    CONTAINMENT = auto()
    DEFIANCE = auto()
    ASSASSINATION = auto()
    FAST_SNIPE = auto()
    # ... all 65+ special cases

@dataclass
class CharacterFlags:
    """Tracks active special case flags for a character"""
    domination: bool = False
    scourge: bool = False
    critical_hits: bool = False
    containment: bool = False
    defiance: bool = False
    assassination: bool = False
    hidden: bool = False
    combo_level: int = 0
    team_size: int = 1
    defensive_adaptation: bool = False
    offensive_adaptation: bool = False
    efficient_adaptation: bool = False

    def has_special_case(self, case: SpecialCase) -> bool:
        """Check if character has specific special case active"""
        # Map special case enum to flag attribute
        pass

@dataclass
class PowerRequirement:
    """Power prerequisites and pool membership"""
    power_ids: list[str]  # Required power UIDs
    group_membership: list[str]  # Pool groups this power belongs to
    min_level: int = 1
    min_group_powers: int = 0  # Powers from same group needed first

class NameNormalizer:
    """Handles game import name fixes"""

    # Power name replacements
    POWER_NAME_FIXES: Dict[str, str] = {
        "Gravity Emanation": "Gravitic Emanation",
        "Dark Matter Detonation": "Dark Detonation",
        "Dark Nova Emmanation": "Dark Nova Emanation",
    }

    # Enhancement name replacements
    ENH_NAME_FIXES: Dict[str, str] = {
        "Fly": "Flight",
        "Rechg": "RechRdx",
        "TH_Buf": "ToHit",
        "TH_DeBuf": "ToHitDeb",
        "DmgRes": "ResDam",
        "HO:": "",  # Remove prefix
        "CentiExp": "Centri",
        # ... many more
    }

    # Spelling fixes
    SPELLING_FIXES: Dict[str, str] = {
        "Armour": "Armor",
        "Electric Mastery": "Electrical Mastery",
    }

    @staticmethod
    def normalize_power_name(name: str) -> str:
        """Apply all power name fixes"""
        result = name
        # Apply spelling fixes first
        for old, new in NameNormalizer.SPELLING_FIXES.items():
            result = result.replace(old, new)
        # Apply power-specific fixes
        for old, new in NameNormalizer.POWER_NAME_FIXES.items():
            result = result.replace(old, new)
        return result

    @staticmethod
    def normalize_enh_name(name: str) -> str:
        """Apply enhancement name fixes"""
        result = name
        for old, new in NameNormalizer.ENH_NAME_FIXES.items():
            result = result.replace(old, new)
        return result

class ArcanaTime:
    """Handles server tick quantization"""

    SERVER_TICK_MS = 132  # milliseconds
    SERVER_TICK_SEC = 0.132  # seconds

    @staticmethod
    def quantize_cast_time(base_cast_time: float) -> float:
        """
        Apply Arcana Time formula to cast time.

        Formula: ceil(castTime / 0.132) + 1 ticks * 0.132 sec/tick

        Args:
            base_cast_time: Base cast time in seconds

        Returns:
            Actual cast time accounting for server tick quantization

        Example:
            >>> ArcanaTime.quantize_cast_time(1.0)
            1.188  # (ceil(1.0/0.132) + 1) * 0.132 = 9 ticks
        """
        import math
        ticks = math.ceil(base_cast_time / ArcanaTime.SERVER_TICK_SEC) + 1
        return ticks * ArcanaTime.SERVER_TICK_SEC

class PoolValidator:
    """Validates power pool prerequisites and structure"""

    @staticmethod
    def validate_pool_prerequisites(
        power_to_pick: str,
        already_picked: Set[str],
        database
    ) -> tuple[bool, str]:
        """
        Check if power prerequisites are met.

        Returns:
            (valid, error_message)
        """
        power = database.get_power(power_to_pick)
        if not power:
            return False, f"Power not found: {power_to_pick}"

        # Check required powers
        if power.requires.power_ids:
            for req_power in power.requires.power_ids:
                if req_power not in already_picked:
                    return False, f"Requires power: {req_power}"

        # Check pool prerequisites (e.g., need 2 powers before travel)
        if power.requires.group_membership:
            group = power.requires.group_membership[0]
            group_count = sum(
                1 for p in already_picked
                if database.get_power(p).group_membership == [group]
            )
            if group_count < power.requires.min_group_powers:
                return False, (
                    f"Need {power.requires.min_group_powers} powers from "
                    f"{group} pool first"
                )

        return True, ""

    @staticmethod
    def pad_pool_slots(powersets: list[str], database) -> list[str]:
        """
        Ensure powersets array has 4 pool slots (indices 3-6).
        Pads with unused pools if needed.
        """
        # Count existing pool powersets
        pool_count = sum(1 for ps in powersets if ps.startswith("Pool."))

        if pool_count >= 4:
            return powersets

        # Get all pool powersets not already picked
        picked_pools = {ps for ps in powersets if ps.startswith("Pool.")}
        available_pools = [
            ps.uid for ps in database.get_powersets_by_type("Pool")
            if ps.uid not in picked_pools
        ]
        available_pools.sort()

        # Add padding
        result = powersets.copy()
        for i in range(4 - pool_count):
            result.append(available_pools[i])

        return result

class SpecialCaseHandler:
    """Main handler for all special case logic"""

    def __init__(self, database):
        self.database = database
        self.name_normalizer = NameNormalizer()
        self.pool_validator = PoolValidator()

    def should_include_effect(
        self,
        effect,
        character_flags: CharacterFlags
    ) -> bool:
        """
        Determine if effect should be included based on special case.

        Args:
            effect: Effect with possible SpecialCase flag
            character_flags: Current character state

        Returns:
            True if effect applies, False if conditional not met
        """
        if effect.special_case == SpecialCase.NONE:
            return True

        if effect.special_case == SpecialCase.HIDDEN:
            return True  # Still include, just don't show in UI

        # Check character flags
        return character_flags.has_special_case(effect.special_case)

    def validate_power_pick(
        self,
        power_uid: str,
        character_powers: Set[str]
    ) -> tuple[bool, str]:
        """Validate power can be picked given prerequisites"""
        return self.pool_validator.validate_pool_prerequisites(
            power_uid,
            character_powers,
            self.database
        )

    def normalize_import_string(self, import_str: str) -> str:
        """Apply all name fixes to import string"""
        # Parse import string, apply fixes to power/enh names
        pass

    def handle_special_power(self, power_uid: str):
        """Handle one-off special mechanics like Oil Slick Arrow"""
        if "Oil_Slick_Arrow" in power_uid:
            # Create pseudo-pet with OilSlickTarget archetype
            pass
```

### Implementation Notes

**1. Name Normalization**:
- Apply during build import BEFORE database lookups
- Must be comprehensive - missing fix = import failure
- Consider case-insensitive matching for robustness

**2. Arcana Time**:
- ALWAYS apply for DPS calculations
- Make toggle in UI for display purposes only
- Document the 132ms server tick rate clearly

**3. Special Case Flags**:
- Store as part of character/build state
- Update when AT inherents activated (Domination, etc.)
- Filter effects during aggregation based on flags

**4. Pool Prerequisites**:
- Validate during power picker UI
- Show grayed-out powers with tooltip explaining prerequisite
- Track pool power counts as user picks

**5. Database Padding**:
- Apply padding on import/load
- Maintain consistent 8-slot powerset structure
- Don't expose internal padding to user

**6. Enhancement Level Validation**:
- Clamp IO levels to valid range (usually 10-50)
- Some IOs have different ranges (ATOs 10-50, purples 50-only)
- Apply clamping on import and when user changes level

**7. Conditional Effects**:
- Effect has EITHER `special_case` flag OR `active_conditionals` list
- Never both (mutually exclusive)
- Different evaluation logic for each

**8. Testing Strategy**:
```python
def test_arcana_time():
    assert ArcanaTime.quantize_cast_time(1.0) == pytest.approx(1.188)
    assert ArcanaTime.quantize_cast_time(0.5) == pytest.approx(0.792)
    assert ArcanaTime.quantize_cast_time(2.0) == pytest.approx(2.244)

def test_name_normalization():
    assert NameNormalizer.normalize_power_name(
        "Gravity Emanation"
    ) == "Gravitic Emanation"
    assert NameNormalizer.normalize_enh_name("Rechg") == "RechRdx"

def test_pool_prerequisites():
    validator = PoolValidator()
    # Try to pick Super Speed without prerequisites
    valid, msg = validator.validate_pool_prerequisites(
        "Pool.Speed.Super_Speed",
        set(),  # No powers picked
        mock_database
    )
    assert not valid
    assert "Need 2 powers" in msg
```

### C# vs Python Considerations

**String Handling**:
- C#: Case-sensitive by default, explicit StringComparison options
- Python: Use `.lower()` for case-insensitive or `casefold()` for full Unicode
- Consider using `difflib` for fuzzy power name matching

**Enum Values**:
- C# enums are int-based, can cast freely
- Python Enums more strict - use `.value` for int conversion
- Consider IntEnum for C# compatibility

**Null vs None**:
- C# has nullable types (`string?`)
- Python uses `Optional[str]`
- Watch for null checks in requirement validation

**Performance**:
- String replacement in tight loops can be slow
- Pre-compile regex patterns if using
- Cache normalized names to avoid repeated fixes

**Type Safety**:
- Use dataclasses with type hints
- Mypy/Pyright for static checking
- Pydantic models for validation if needed

### Edge Cases to Test

1. **Import with ALL name variations**:
   - "Armour" vs "Armor"
   - "Electric Mastery" vs "Electrical Mastery"
   - All enhancement abbreviations

2. **Pool prerequisites**:
   - Picking travel power without 2 prior powers
   - Picking epic pool before level 35
   - Multiple pools at once

3. **Arcana Time edge cases**:
   - Very fast powers (< 0.132s base)
   - Instant powers (0s cast)
   - Powers with +recharge (< 0.132s effective)

4. **Special case combinations**:
   - Multiple AT inherents active
   - Conditional effects + special cases
   - Hidden effects in totals calculation

5. **Database edge cases**:
   - Missing powerset slots
   - Invalid IO levels
   - Powers without group membership

6. **Character state tracking**:
   - Domination activation/deactivation
   - Combo level transitions (0→1→2→3)
   - Adaptation mode switching

## References

### Related Specs
- **Spec 18**: Archetype Inherents - Documents AT-specific special cases (Defiance, Domination, etc.)
- **Spec 01**: Power Effects Core - Effect.SpecialCase property
- **Spec 10**: Enhancement Schedules - Enhancement level validation
- **Spec 32**: Power Pools - Pool prerequisite mechanics
- **Spec 33**: Epic Pools - Epic pool level requirements

### MidsReborn Code References
- `Core/Enums.cs` - eSpecialCase enum (lines 1006-1071)
- `clsUniversalImport.cs` - Name fixing functions (lines 71-434)
- `BuildImportTools.cs` - Pool padding logic (lines 305-327)
- `Forms/frmRotationHelper.cs` - Arcana Time implementation (lines 219-222)
- `Core/Base/Data_Classes/Character.cs` - AT inherent flags (lines 140-152)

### External References
- **Arcana Time**: Player Arcanaville's discovery of 132ms server tick quantization
- **Pool Prerequisites**: Standard CoH pattern - 2 powers before travel power
- **Oil Slick Arrow**: Only power with pseudo-pet ignition mechanic
- **Enhancement Diversification (ED)**: Why enhancement names needed normalization

### Implementation Priority

**Milestone 3 (Depth)**:
1. Implement `NameNormalizer` - CRITICAL for import
2. Implement `ArcanaTime` - Essential for accurate DPS
3. Implement `CharacterFlags` - Required for AT inherents
4. Implement `PoolValidator` - Needed for power picker UI
5. Implement `SpecialCaseHandler.should_include_effect()` - Ties to effect aggregation

**Testing Priority**:
1. Name normalization (breaks import if wrong)
2. Arcana Time (visible DPS errors if wrong)
3. Pool prerequisites (prevents invalid builds)
4. Special case filtering (wrong AT inherent values)

---

**Status**: 🟡 Breadth Complete - Ready for Milestone 3 deep implementation
