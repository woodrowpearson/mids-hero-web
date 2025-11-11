# Exemplar/Sidekick Mechanics

## Overview
- **Purpose**: Handle temporary level changes (exemplar down, sidekick up) that affect power availability, enhancement effectiveness, and set bonuses
- **Used By**: Build totals, power availability checks, enhancement value calculations, set bonus aggregation, UI display
- **Complexity**: Medium
- **Priority**: Low
- **Status**: 🟡 Breadth Complete

## MidsReborn Implementation

### Primary Location
- **File**: `Core/ConfigData.cs`
- **Properties**: `ExempHigh` (line 18), `ExempLow` (line 20), `ForceLevel` (line 21)
- **Related Files**:
  - `Forms/frmMain.cs` - Exemplar display logic (lines showing "Exemped from X to Y")
  - `Core/Base/Master_Classes/MidsContext.cs` - Math level constants (lines 7-8: MathLevelBase=49, MathLevelExemp=-1)
  - `Controls/clsDrawX.cs` - Enhancement penalty visualization (ForceLevel checks)
  - `Core/Build.cs` - Power availability by ForceLevel
  - `clsToonX.cs` - Enhancement level checks vs ForceLevel

### Key Properties and Constants

**ConfigData Properties** (`ConfigData.cs`):
```csharp
public int ExempHigh { get; set; } = 50;  // Original level before exemplar
public int ExempLow { get; set; } = 50;   // Target exemplar level
public int ForceLevel { get; set; } = 50; // Effective level for calculations
```

**Math Level Constants** (`MidsContext.cs`):
```csharp
public const int MathLevelBase = 49;    // Normal max level (0-based: 49 = level 50)
public const int MathLevelExemp = -1;   // Exemplar mode flag
```

### High-Level Algorithm

```
Exemplar/Sidekick Detection:
  INPUT: ExempHigh, ExempLow (from ConfigData)

  IF ExempLow < ExempHigh:
      Mode = EXEMPLAR  // Character reduced to lower level
  ELSE IF ExempLow > ExempHigh:
      Mode = SIDEKICK  // Character increased to higher level (rare in build planner)
  ELSE:
      Mode = NORMAL   // No level adjustment

  OUTPUT: Effective level mode

Power Availability Check:
  INPUT: Power, ForceLevel

  FOR each power in build:
      IF power.Level > ForceLevel:
          power.Available = FALSE  // Power becomes grayed out
      ELSE:
          power.Available = TRUE

  OUTPUT: Available power list

Enhancement Penalty Check:
  INPUT: Slot, Enhancement, ForceLevel

  FOR each slotted enhancement:
      // Standard IOs and Set IOs subject to level check
      IF enhancement is attuned IO:
          // NO PENALTY - See Spec 37
          penalty = NONE
      ELSE IF enhancement is purple IO OR pvp IO:
          // NO PENALTY - See Spec 38
          penalty = NONE
      ELSE:
          // Standard IO level check
          enhancementLevel = slot.Level

          // Enhancement works if within exemplar level + 3
          // (Note: Some sources suggest +5, code shows ForceLevel checks)
          IF enhancementLevel > ForceLevel:
              penalty = DISABLED  // Enhancement grayed out, no effect
          ELSE:
              penalty = NONE      // Enhancement works normally

  OUTPUT: Active enhancement list

Set Bonus Availability:
  INPUT: EnhancementSet, ForceLevel

  FOR each enhancement set:
      // Get minimum level of set
      setLevel = enhancementSet.LevelMin

      // Standard sets lose bonuses if exemplared below set level
      IF enhancementSet is purple OR pvp:
          // NO PENALTY - Purple/PvP sets work at all levels
          setBonusActive = TRUE
      ELSE IF enhancementSet contains attuned IOs:
          // Attuned sets maintain bonuses when exemplared
          setBonusActive = TRUE
      ELSE:
          // Standard set bonus rule: Works if exemplar >= (setLevel - 3)
          IF ForceLevel >= (setLevel - 3):
              setBonusActive = TRUE
          ELSE:
              setBonusActive = FALSE

  OUTPUT: Active set bonus list

Display Logic (frmMain.cs):
  IF ExempLow < ExempHigh:
      DisplayText = "Exemped from {ExempHigh} to {ExempLow}"
      // Show in character label

  // Visual indicators:
  // - Powers above ForceLevel: Grayed out
  // - Enhancements above ForceLevel: Grayed out with red circle
  // - Set bonuses: Faded if inactive
```

### Key Logic Snippets

**Exemplar Display** (frmMain.cs):
```csharp
if (MidsContext.Config.ExempLow < MidsContext.Config.ExempHigh)
{
    str4 += $" - Exemped from {MidsContext.Config.ExempHigh} to {MidsContext.Config.ExempLow}";
}
```

**Enhancement Level Check** (clsDrawX.cs, multiple locations):
```csharp
// Check if enhancement is disabled by force level
if (slot.Level > MidsContext.Config.ForceLevel)
{
    // Gray out enhancement, show disabled indicator
    grey = true;
}

// Alternative check with CalcEnhLevel mode
if (MidsContext.Config.CalcEnhLevel == 0 | slot.Level > MidsContext.Config.ForceLevel)
{
    // Don't include in calculations
}
```

**Power Availability Check** (Build.cs):
```csharp
if (Powers[index1] != null && Powers[index1].Level <= MidsContext.Config.ForceLevel)
{
    // Power is available at this exemplar level
    // Include in calculations
}
```

**Enhancement in Slot Check** (clsToonX.cs):
```csharp
if (!(CurrentBuild.Powers[hIDX].Slots[index].Enhancement.Enh > -1 &
      CurrentBuild.Powers[hIDX].Slots[index].Level < MidsContext.Config.ForceLevel))
{
    continue;  // Skip enhancements above force level
}
```

### Dependencies

**Used By**:
- Build totals calculation (must exclude disabled powers/enhancements)
- Power display UI (gray out unavailable powers)
- Enhancement display UI (gray out disabled enhancements)
- Set bonus calculation (determine which bonuses are active)
- Build import/export (preserve exemplar settings)

**Depends On**:
- Character level tracking
- Power level requirements
- Enhancement level tracking
- Set bonus level requirements
- Attuned IO detection (Spec 37)
- Purple/PvP IO detection (Spec 38)

## Game Mechanics Context

### Why This Exists

**Problem**: City of Heroes has content spanning levels 1-50, but high-level characters couldn't meaningfully play with low-level friends. A level 50 character in a level 10 zone would trivialize all content.

**Solution**: The Exemplar/Sidekick system temporarily adjusts character level:
- **Exemplar**: High-level character reduces to teammate's level (or mission level)
- **Sidekick**: Low-level character increases to teammate's level (up to level 49)

This allows players of different levels to team effectively while maintaining appropriate challenge.

### Historical Context

**Initial Implementation (Issue 0, 2004)**:
- Sidekick system launched with game
- Higher-level player could sidekick a lower-level player (up to -3 levels)
- Sidekicked player gained temporary level boost

**Exemplar System (Issue 2, July 2004)**:
- Added exemplar system for high-level players to play low-level content
- Exemplared players maintained all their powers and enhancements (overpowered)
- Rewards scaled to exemplar level

**Enhancement Penalties (Issue 9, May 2007)**:
- Invention Origin enhancements introduced with level-based effectiveness
- Rule established: Enhancements work if within exemplar level + 3
- Example: Level 35 IO works when exemplared to level 32, but not level 31

**Set Bonus Rules (Issue 9+)**:
- Set bonuses remain active if exemplared within 3 levels of set's minimum level
- Example: Level 30 set works at level 27+, inactive at level 26 and below
- Exception: Purple and PvP sets work at ALL levels (no penalty)

**Attuned IOs (Issue 21, September 2011)**:
- Attuned IOs introduced to bypass exemplar penalties
- Scale dynamically to character level (even when exemplared)
- Premium feature to address exemplar frustration

**Homecoming Changes (2019+)**:
- Super Sidekick system: Team automatically exemplars/sidekicks to mission level
- Attuned IOs more accessible (no longer premium-only)
- Purple/PvP IO exemption remains (reward for rare IOs)

### Key Rules

**Power Availability**:
1. Powers above exemplar level become unavailable (grayed out)
2. Powers at or below exemplar level remain available
3. Inherent powers and pool powers follow same rules
4. Accolade powers may be lost if requirements not met at exemplar level

**Enhancement Effectiveness**:
1. Standard IOs: Work if enhancement level <= exemplar level + 3 (or +5, varies by source)
2. Attuned IOs: ALWAYS work, scale to current exemplar level (Spec 37)
3. Purple IOs: ALWAYS work, no exemplar penalty (Spec 38)
4. PvP IOs: ALWAYS work, no exemplar penalty (Spec 38)
5. Special Origin Enhancements: Follow standard IO rules

**Set Bonuses**:
1. Standard sets: Work if exemplar level >= (set minimum level - 3)
2. Purple sets: Work at ALL levels (level 1 to 50)
3. PvP sets: Work at ALL levels
4. Attuned sets: Work at ALL levels (if all IOs in set are attuned)
5. Mixed sets (some attuned, some not): May lose bonuses if any non-attuned IO is disabled

**The "+3 Rule" vs "+5 Rule"**:
- Most documentation says "+3 levels" (exemplar to 30, level 33 IO works)
- Some code suggests comparison with ForceLevel (no explicit +3/+5 offset)
- MidsReborn uses direct ForceLevel comparison: `slot.Level > ForceLevel`
- This implies the level check happens AFTER ForceLevel is set appropriately

### Known Quirks

1. **Enhancement Boosters and Exemplar**: A level 35+5 (boosted to 40) IO may work at higher exemplar level than unboosted level 35 IO, depending on implementation.

2. **Partial Set Bonuses**: If a 6-piece set loses 2 enhancements due to exemplar penalties, you keep bonuses for 4 pieces slotted (if those 4 enhancements are still active).

3. **Purple Set Advantage**: Purple sets working at level 1 is a HUGE advantage. A fully purpled-out build maintains all set bonuses regardless of exemplar level.

4. **Attuned Value Scaling**: Attuned IOs don't just "stay on" when exemplared - they actually REDUCE in effectiveness to match the lower level. A level 50 attuned IO exemplared to level 20 provides level 20 IO values, not level 50 values.

5. **Sidekick Power Gaps**: If sidekicked from level 10 to level 40, you only have powers you picked at level 10. You gain level 40 HP/damage/etc., but not level 40 powers.

6. **ForceLevel vs ExempLow**: MidsContext.Config.ForceLevel is the "effective level" used for all calculations. It's set based on ExempLow (or character level if not exemplared).

7. **MathLevelExemp Constant**: The `MathLevelExemp = -1` constant suggests a special "exemplar mode" flag, but actual implementation uses ForceLevel for calculations.

8. **Gray-Out Visual Indicators**: MidsReborn uses multiple visual cues:
   - Powers: Grayed out if above ForceLevel
   - Enhancements: Grayed out + red circle if disabled
   - Set bonuses: Faded text if inactive

## Python Implementation Notes

### Proposed Architecture

**Location**: `backend/app/calculations/character/exemplar.py`

**Related Modules**:
- `character/level.py` - Character level tracking
- `powers/availability.py` - Power availability checks
- `enhancements/penalties.py` - Enhancement effectiveness
- `enhancements/attuned.py` - Attuned IO exemption (Spec 37)
- `enhancements/purple_pvp.py` - Purple/PvP IO exemption (Spec 38)
- `sets/bonuses.py` - Set bonus activation

### Data Classes

```python
from dataclasses import dataclass
from enum import Enum

class LevelAdjustmentMode(Enum):
    """Type of level adjustment applied to character."""
    NORMAL = 0      # No adjustment
    EXEMPLAR = 1    # Reduced to lower level
    SIDEKICK = 2    # Increased to higher level

@dataclass
class ExemplarSettings:
    """Exemplar/Sidekick configuration for a build."""

    original_level: int  # Character's actual level (1-50)
    target_level: int    # Exemplar/sidekick target level (1-49)
    force_level: int     # Effective level for calculations
    mode: LevelAdjustmentMode

    @classmethod
    def create_normal(cls, character_level: int) -> 'ExemplarSettings':
        """Create settings for normal (non-exemplared) character."""
        return cls(
            original_level=character_level,
            target_level=character_level,
            force_level=character_level,
            mode=LevelAdjustmentMode.NORMAL
        )

    @classmethod
    def create_exemplar(cls, original_level: int, exemplar_to: int) -> 'ExemplarSettings':
        """Create settings for exemplared character."""
        return cls(
            original_level=original_level,
            target_level=exemplar_to,
            force_level=exemplar_to,
            mode=LevelAdjustmentMode.EXEMPLAR
        )

    @classmethod
    def create_sidekick(cls, original_level: int, sidekick_to: int) -> 'ExemplarSettings':
        """Create settings for sidekicked character."""
        return cls(
            original_level=original_level,
            target_level=sidekick_to,
            force_level=sidekick_to,
            mode=LevelAdjustmentMode.SIDEKICK
        )

    def is_exemplared(self) -> bool:
        """Check if character is currently exemplared."""
        return self.mode == LevelAdjustmentMode.EXEMPLAR

    def is_sidekicked(self) -> bool:
        """Check if character is currently sidekicked."""
        return self.mode == LevelAdjustmentMode.SIDEKICK

    def is_level_adjusted(self) -> bool:
        """Check if any level adjustment is active."""
        return self.mode != LevelAdjustmentMode.NORMAL

    def get_display_text(self) -> str:
        """Get display string for UI (e.g., 'Exemped from 50 to 25')."""
        if self.mode == LevelAdjustmentMode.EXEMPLAR:
            return f"Exemped from {self.original_level} to {self.target_level}"
        elif self.mode == LevelAdjustmentMode.SIDEKICK:
            return f"Sidekicked from {self.original_level} to {self.target_level}"
        else:
            return ""

@dataclass
class PowerAvailability:
    """Tracks whether a power is available at current exemplar level."""

    power_id: int
    power_name: str
    power_level: int      # Level when power was picked
    available: bool       # Available at current force level?
    reason: str = ""      # Why unavailable (if applicable)

    @classmethod
    def check(cls, power_level: int, force_level: int, power_id: int, power_name: str) -> 'PowerAvailability':
        """Check if power is available at force level."""
        available = power_level <= force_level
        reason = "" if available else f"Power requires level {power_level}, exemplared to {force_level}"

        return cls(
            power_id=power_id,
            power_name=power_name,
            power_level=power_level,
            available=available,
            reason=reason
        )

@dataclass
class EnhancementAvailability:
    """Tracks whether an enhancement is active at current exemplar level."""

    enhancement_id: int
    enhancement_level: int
    is_attuned: bool
    is_purple: bool
    is_pvp: bool
    available: bool
    reason: str = ""

    @classmethod
    def check(
        cls,
        enhancement_id: int,
        enhancement_level: int,
        force_level: int,
        is_attuned: bool = False,
        is_purple: bool = False,
        is_pvp: bool = False
    ) -> 'EnhancementAvailability':
        """
        Check if enhancement is active at force level.

        Rules:
        - Attuned IOs: Always active, scale to force level
        - Purple IOs: Always active, no penalty
        - PvP IOs: Always active, no penalty
        - Standard IOs: Active if enhancement_level <= force_level (or +3/+5)
        """
        # Exemptions
        if is_attuned:
            return cls(
                enhancement_id=enhancement_id,
                enhancement_level=enhancement_level,
                is_attuned=True,
                is_purple=False,
                is_pvp=False,
                available=True,
                reason="Attuned IO - no exemplar penalty"
            )

        if is_purple or is_pvp:
            return cls(
                enhancement_id=enhancement_id,
                enhancement_level=enhancement_level,
                is_attuned=False,
                is_purple=is_purple,
                is_pvp=is_pvp,
                available=True,
                reason="Purple/PvP IO - no exemplar penalty"
            )

        # Standard IO check (MidsReborn uses direct comparison with ForceLevel)
        available = enhancement_level <= force_level
        reason = "" if available else f"Enhancement level {enhancement_level} exceeds force level {force_level}"

        return cls(
            enhancement_id=enhancement_id,
            enhancement_level=enhancement_level,
            is_attuned=False,
            is_purple=False,
            is_pvp=False,
            available=available,
            reason=reason
        )

@dataclass
class SetBonusAvailability:
    """Tracks whether set bonuses are active at current exemplar level."""

    set_id: int
    set_name: str
    set_min_level: int
    is_purple_set: bool
    is_pvp_set: bool
    has_attuned_ios: bool
    available: bool
    reason: str = ""

    @classmethod
    def check(
        cls,
        set_id: int,
        set_name: str,
        set_min_level: int,
        force_level: int,
        is_purple_set: bool = False,
        is_pvp_set: bool = False,
        has_attuned_ios: bool = False
    ) -> 'SetBonusAvailability':
        """
        Check if set bonuses are active at force level.

        Rules:
        - Purple sets: Always active
        - PvP sets: Always active
        - Attuned sets: Always active (if all IOs attuned)
        - Standard sets: Active if force_level >= (set_min_level - 3)
        """
        # Exemptions
        if is_purple_set or is_pvp_set:
            reason = "Purple/PvP set - no exemplar penalty"
            return cls(
                set_id=set_id,
                set_name=set_name,
                set_min_level=set_min_level,
                is_purple_set=is_purple_set,
                is_pvp_set=is_pvp_set,
                has_attuned_ios=has_attuned_ios,
                available=True,
                reason=reason
            )

        if has_attuned_ios:
            return cls(
                set_id=set_id,
                set_name=set_name,
                set_min_level=set_min_level,
                is_purple_set=False,
                is_pvp_set=False,
                has_attuned_ios=True,
                available=True,
                reason="Attuned set - no exemplar penalty"
            )

        # Standard set rule: force_level >= (set_min_level - 3)
        available = force_level >= (set_min_level - 3)
        reason = "" if available else f"Set requires level {set_min_level}, exemplared to {force_level}"

        return cls(
            set_id=set_id,
            set_name=set_name,
            set_min_level=set_min_level,
            is_purple_set=False,
            is_pvp_set=False,
            has_attuned_ios=False,
            available=available,
            reason=reason
        )
```

### Key Functions

```python
class ExemplarCalculator:
    """Calculate exemplar/sidekick effects on build."""

    def __init__(self, settings: ExemplarSettings):
        self.settings = settings

    def get_available_powers(self, powers: list[Power]) -> list[PowerAvailability]:
        """
        Determine which powers are available at current exemplar level.

        Args:
            powers: List of all powers in build

        Returns:
            List of PowerAvailability results

        Example:
            # Character exemplared from 50 to 25
            settings = ExemplarSettings.create_exemplar(50, 25)
            calc = ExemplarCalculator(settings)
            available = calc.get_available_powers(build.powers)
            # Powers picked at level 26+ will be unavailable=False
        """
        results = []

        for power in powers:
            availability = PowerAvailability.check(
                power_level=power.level,
                force_level=self.settings.force_level,
                power_id=power.power_id,
                power_name=power.display_name
            )
            results.append(availability)

        return results

    def apply_enhancement_penalties(
        self,
        slotted_enhancements: list[SlottedEnhancement],
        attuned_detector,  # From Spec 37
        purple_pvp_detector  # From Spec 38
    ) -> list[EnhancementAvailability]:
        """
        Determine which enhancements are active at current exemplar level.

        Args:
            slotted_enhancements: List of enhancements in all power slots
            attuned_detector: Detector for attuned IOs
            purple_pvp_detector: Detector for purple/PvP IOs

        Returns:
            List of EnhancementAvailability results

        Example:
            # Character exemplared to level 30
            # Level 35 standard IO: INACTIVE
            # Level 35 attuned IO: ACTIVE (scales to 30)
            # Level 50 purple IO: ACTIVE (no penalty)
        """
        results = []

        for slot_enh in slotted_enhancements:
            # Check exemptions
            is_attuned = attuned_detector.is_naturally_attuned(
                slot_enh.enhancement_uid,
                slot_enh.enhancement_set_name,
                slot_enh.enhancement_set_type_name
            )

            is_purple = purple_pvp_detector.is_purple_io(slot_enh.enhancement_id)
            is_pvp = purple_pvp_detector.is_pvp_io(slot_enh.enhancement_id)

            availability = EnhancementAvailability.check(
                enhancement_id=slot_enh.enhancement_id,
                enhancement_level=slot_enh.level,
                force_level=self.settings.force_level,
                is_attuned=is_attuned,
                is_purple=is_purple,
                is_pvp=is_pvp
            )
            results.append(availability)

        return results

    def check_set_bonuses(
        self,
        slotted_sets: list[SlottedSet],
        purple_pvp_detector  # From Spec 38
    ) -> list[SetBonusAvailability]:
        """
        Determine which set bonuses are active at current exemplar level.

        Args:
            slotted_sets: List of enhancement sets slotted in build
            purple_pvp_detector: Detector for purple/PvP sets

        Returns:
            List of SetBonusAvailability results

        Example:
            # Character exemplared to level 22
            # Level 25 standard set: ACTIVE (22 >= 25-3=22)
            # Level 30 standard set: INACTIVE (22 < 30-3=27)
            # Level 50 purple set: ACTIVE (no penalty)
        """
        results = []

        for slotted_set in slotted_sets:
            is_purple = purple_pvp_detector.is_purple_set(slotted_set.set_id)
            is_pvp = purple_pvp_detector.is_pvp_set(slotted_set.set_id)

            # Check if all IOs in set are attuned
            has_attuned = all(
                enh.is_attuned for enh in slotted_set.enhancements
            )

            availability = SetBonusAvailability.check(
                set_id=slotted_set.set_id,
                set_name=slotted_set.set_name,
                set_min_level=slotted_set.level_min,
                force_level=self.settings.force_level,
                is_purple_set=is_purple,
                is_pvp_set=is_pvp,
                has_attuned_ios=has_attuned
            )
            results.append(availability)

        return results

    def calculate_effective_build_stats(
        self,
        full_build_stats: BuildStats,
        available_powers: list[PowerAvailability],
        available_enhancements: list[EnhancementAvailability],
        available_set_bonuses: list[SetBonusAvailability]
    ) -> BuildStats:
        """
        Calculate build statistics with exemplar penalties applied.

        This is the main entry point for exemplar calculations.

        Args:
            full_build_stats: Stats calculated at full level (no exemplar)
            available_powers: Power availability results
            available_enhancements: Enhancement availability results
            available_set_bonuses: Set bonus availability results

        Returns:
            BuildStats with only available powers/enhancements/bonuses

        Algorithm:
        1. Start with base character stats at force_level
        2. Add effects from available powers only
        3. Add effects from available enhancements only
        4. Add effects from available set bonuses only
        5. Apply archetype caps at force_level

        Example:
            settings = ExemplarSettings.create_exemplar(50, 25)
            calc = ExemplarCalculator(settings)

            powers = calc.get_available_powers(build.powers)
            enhancements = calc.apply_enhancement_penalties(
                build.enhancements, attuned_det, purple_det
            )
            set_bonuses = calc.check_set_bonuses(
                build.sets, purple_det
            )

            exemp_stats = calc.calculate_effective_build_stats(
                build.full_stats, powers, enhancements, set_bonuses
            )
            # exemp_stats contains only stats from available sources
        """
        # Implementation deferred to Milestone 3 (depth phase)
        # This is the integration point for all exemplar logic
        pass
```

### Implementation Notes

**C# vs Python Differences**:
1. **ForceLevel vs Character.Level**: C# uses Config.ForceLevel for calculations. Python should use ExemplarSettings.force_level consistently.
2. **Level Indexing**: Be careful with 0-based vs 1-based levels. Character levels are 1-50, but array indices are 0-49.
3. **UI Graying Logic**: C# has complex visual graying logic. Python API should return availability flags; UI handles display.

**Edge Cases to Test**:
1. **Exemplar to Level 1**: All powers above level 1 unavailable, only veteran/inherent powers work
2. **Exemplar by 1 Level**: Character at 49 exemplared to 50 (no effect)
3. **Purple Set at Level 1**: All bonuses active even at minimum exemplar
4. **Mixed Attuned/Standard Set**: Set bonuses depend on whether ALL IOs are attuned
5. **Boosted Enhancement**: Level 35+5 IO treated as level 40 for exemplar purposes
6. **Power with Attuned IO**: Power available, attuned IO active and scaled

**Performance Considerations**:
- Cache availability checks (only recalculate when exemplar settings change)
- Pre-filter power/enhancement lists rather than checking every calculation
- Use set lookups for purple/PvP/attuned detection (O(1) vs repeated checks)

**Validation Strategy**:
1. Create test builds at various levels with different IO types
2. Exemplar to different levels, compare stats with MidsReborn
3. Verify power graying matches MidsReborn UI
4. Check set bonus activation/deactivation at boundary levels
5. Test exemption logic for attuned/purple/PvP IOs

### Test Cases

```python
# Test Case 1: Power availability
# Character level 50 with powers at 1, 6, 8, 20, 28, 35, 41, 49
# Exemplar to level 30
settings = ExemplarSettings.create_exemplar(50, 30)
calc = ExemplarCalculator(settings)
available = calc.get_available_powers(powers)
assert available[0].available == True   # Level 1 power
assert available[6].available == True   # Level 28 power
assert available[7].available == False  # Level 35 power
assert available[8].available == False  # Level 41 power

# Test Case 2: Standard IO penalties
# Level 35 IO in level 30 exemplar
enh_check = EnhancementAvailability.check(
    enhancement_id=123,
    enhancement_level=35,
    force_level=30,
    is_attuned=False,
    is_purple=False,
    is_pvp=False
)
assert enh_check.available == False  # 35 > 30

# Test Case 3: Attuned IO exemption
# Level 35 attuned IO in level 30 exemplar
enh_check = EnhancementAvailability.check(
    enhancement_id=456,
    enhancement_level=35,
    force_level=30,
    is_attuned=True
)
assert enh_check.available == True   # Attuned bypasses penalty

# Test Case 4: Set bonus rules
# Level 30 standard set at exemplar 27
set_check = SetBonusAvailability.check(
    set_id=1,
    set_name="Crushing Impact",
    set_min_level=30,
    force_level=27,
    is_purple_set=False
)
assert set_check.available == True   # 27 >= (30-3)

# Level 30 standard set at exemplar 26
set_check = SetBonusAvailability.check(
    set_id=1,
    set_name="Crushing Impact",
    set_min_level=30,
    force_level=26,
    is_purple_set=False
)
assert set_check.available == False  # 26 < (30-3)

# Test Case 5: Purple set exemption
# Level 50 purple set at exemplar 1
set_check = SetBonusAvailability.check(
    set_id=99,
    set_name="Apocalypse",
    set_min_level=50,
    force_level=1,
    is_purple_set=True
)
assert set_check.available == True   # Purple sets work at all levels

# Test Case 6: Display text
settings_exemplar = ExemplarSettings.create_exemplar(50, 25)
assert settings_exemplar.get_display_text() == "Exemped from 50 to 25"

settings_normal = ExemplarSettings.create_normal(50)
assert settings_normal.get_display_text() == ""
```

## References

- **Related Specs**:
  - Spec 37: Attuned IOs (exemption from exemplar penalties)
  - Spec 38: Purple/PvP IOs (exemption from exemplar penalties)
  - Spec 13: Enhancement Set Bonuses (set bonus activation rules)
  - Spec 36: Enhancement Boosters (boosted level affects exemplar threshold)

- **MidsReborn Files**:
  - `Core/ConfigData.cs` - Exemplar settings storage
  - `Forms/frmMain.cs` - Exemplar display
  - `Controls/clsDrawX.cs` - Enhancement graying logic
  - `Core/Build.cs` - Power availability by ForceLevel

- **Game Mechanics**:
  - City of Heroes Wiki: "Exemplar System"
  - Homecoming Wiki: "Sidekick System"
  - Paragon Wiki: "Enhancement Sets and Exemplaring"

---

**Document Status**: ✅ Breadth Complete - High-level overview, algorithm, game context, Python design documented
**Next Step**: Update calculation index, commit changes
