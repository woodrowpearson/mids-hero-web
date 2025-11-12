# Proc Interactions

## Overview
- **Purpose**: Handle edge cases when multiple proc IOs are slotted in the same power - independent rolling, unique restrictions, and simultaneous activation
- **Used By**: Enhancement slotting validation, proc chance calculations, effect application
- **Complexity**: Low to Moderate
- **Priority**: Low
- **Status**: 🟡 Breadth Complete

## MidsReborn Implementation

### Primary Location
- **File**: `Core/Build.cs`
- **Method**: `SetEnhancement()` - Lines 1100-1250 (validates unique/mutex constraints)
- **Related Files**:
  - `Core/Enhancement.cs` - Lines 205, 207 (`Unique` flag, `MutExID` property)
  - `Core/Enums.cs` - Lines 653-663 (`eEnhMutex` enumeration)
  - `Core/Base/Data_Classes/Effect.cs` - Proc probability calculation (independent per proc)
  - `Core/PowerEntry.cs` - `HasProc()`, `ProcInclude` for proc toggling

### Enhancement Uniqueness System

**Unique Flag** (`Enhancement.Unique` property):
- Boolean flag marking enhancements that can only be slotted once per entire build
- Checked at slotting time in `Build.SetEnhancement()` line 1143
- Prevents slotting multiple copies across ALL powers
- Common examples: Most proc IOs, special globals like Stealth IOs

**Mutex System** (`Enhancement.MutExID` property):
- Enum-based mutual exclusion system for related enhancements
- Prevents slotting normal and superior versions of same set
- Prevents slotting multiple stealth IOs simultaneously

```csharp
// Core/Enums.cs - Lines 653-663
public enum eEnhMutex
{
    None,              // No restrictions
    Stealth,           // Stealth IO mutex
    ArchetypeA,        // ATO mutex group A
    ArchetypeB,        // ATO mutex group B
    ArchetypeC,        // ATO mutex group C
    ArchetypeD,        // ATO mutex group D
    ArchetypeE,        // ATO mutex group E
    ArchetypeF         // ATO mutex group F
}
```

### High-Level Algorithm

```
Multiple Proc Validation (Build.SetEnhancement):

1. Check Basic Slotting Rules:
   - Verify enhancement type allowed in power (SetTypes)
   - Check slot range validity

2. Check Unique Constraint (lines 1143-1154):
   IF enhancement.Unique == true:
     FOR each power in build:
       FOR each slot in power:
         IF slot contains same enhancement ID:
           RETURN false (reject slotting)
           SHOW error: "unique enhancement, only one per build"

3. Check Mutex Constraints (lines 1156-1194):
   IF enhancement.MutExID != None:
     IF enhancement is Superior:
       Check for regular version already slotted
     ELSE IF enhancement is regular:
       Check for superior version already slotted

     IF enhancement.MutExID == Stealth:
       Check for any other stealth IO already slotted

   IF mutex violation found:
     RETURN false (reject slotting)

4. Allow Slotting:
   Enhancement passes validation
   Can be slotted in power

Independent Proc Rolling (implicit in Effect.cs):

FOR each proc IO slotted in power:
  1. Calculate proc chance independently:
     - Use PPM formula (Spec 12)
     - Apply area factor
     - Apply recharge modifiers
     - Clamp to min/max caps

  2. Roll separately on power activation:
     roll = random(0, 1)
     IF roll < proc_chance:
       Activate proc effect

  3. No suppression between different procs:
     - Proc A activating doesn't affect Proc B's chance
     - Both can activate simultaneously
     - Order of effect application is deterministic

Set Bonus + Proc Interaction:

Proc IOs provide TWO independent benefits:
  1. Proc effect:
     - Rolls on power activation
     - Grants temporary effect if successful

  2. Set bonus contribution:
     - Always active when slotted
     - Counts toward set bonus totals
     - Subject to Rule of 5 (Spec 13)
```

## Game Mechanics Context

### Why This System Exists

**Historical Context**:
- Issue 9 introduced Invention Origin enhancements (IOs)
- Early proc IOs were extremely powerful with no restrictions
- Players could slot multiple procs in fast-recharging powers for massive damage
- Unique flag added to prevent stacking same proc multiple times
- PPM system (Issue 24) further balanced proc performance

**Unique Restriction Purpose**:
- Prevents degenerate builds with 6 copies of same proc across build
- Forces build diversity and strategic choices
- Most proc IOs are marked unique because of their power level
- Regular set IOs (non-procs) typically not unique

**Mutex System Purpose**:
- Prevents slotting both regular and superior versions of same set
- Prevents exploiting multiple stealth IOs (diminishing returns)
- Archetype Origin (ATO) mutex groups prevent mixing ATO sets

### Independent Proc Rolling

**Key Rule**: Each proc rolls independently
- No suppression between different proc types
- No interference between procs in same power
- Multiple procs can all trigger on same activation
- Order of effect application follows power effect ordering rules

**Example Scenario**:
```
Power: Blaze (single-target attack)
Slotted Procs:
  - Gladiator's Javelin: Chance for Toxic Damage (3.5 PPM)
  - Apocalypse: Chance for Negative Damage (4.5 PPM)
  - Shield Breaker: Chance for -Res (2.0 PPM)

On each activation:
  1. Calculate each proc's chance independently (using power's recharge/cast time)
  2. Roll separately for each proc
  3. Apply effects of all procs that succeed
  4. No interaction or suppression between the three procs
```

### Force Feedback Special Case

**Force Feedback: Chance for +Recharge** (unique proc):
- Grants +100% recharge buff for 5 seconds
- Can briefly stack with itself (due to 5-second duration)
- If power recharged fast enough, previous buff may still be active
- Maximum practical stacking: 2 applications (extremely rare)
- Most other procs don't stack with themselves (instant effects or long duration)

### Proc vs Set Bonus Interaction

**Dual Nature of Proc IOs**:
```
Apocalypse: Chance for Negative Damage (proc IO):
  1. Proc Effect:
     - 4.5 PPM chance to deal negative damage
     - Rolls each time power activates
     - Temporary effect when triggered

  2. Set Bonus Contribution:
     - Part of Apocalypse 6-piece set
     - Counts as 1 of 6 pieces for set bonuses
     - Always active when slotted
     - 2-piece: +9% Accuracy
     - 3-piece: +3% Max Endurance
     - etc.
```

**No Interference**:
- Proc activation doesn't affect set bonus
- Set bonus doesn't affect proc chance (except through global recharge)
- Both systems operate independently
- Build optimization considers both benefits

### Known Quirks

1. **Unique Check Timing**:
   - Checked at slotting time only
   - Not enforced if database modified post-slot
   - Validation runs before enhancement placed

2. **Mutex Across Versions**:
   - Regular and superior versions mutex with each other
   - Attuned versions also participate in mutex system
   - Prevents "upgrading" by slotting both

3. **Proc Order of Effect**:
   - Effects applied in enhancement slot order (typically)
   - Deterministic within single activation
   - Matters for effects that modify same attribute

4. **Multiple Procs in Auto/Toggle Powers**:
   - Each proc checks independently every 10 seconds
   - Can create significant passive DPS/utility
   - Common build strategy for auras and toggles

## Python Implementation Notes

### Proposed Architecture

```python
# proc_interactions.py - Proc slotting validation and interaction

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Set
import random


class EnhancementMutex(Enum):
    """Enhancement mutual exclusion groups."""
    NONE = 0
    STEALTH = 1
    ARCHETYPE_A = 2
    ARCHETYPE_B = 3
    ARCHETYPE_C = 4
    ARCHETYPE_D = 5
    ARCHETYPE_E = 6
    ARCHETYPE_F = 7


@dataclass
class Enhancement:
    """Enhancement data including uniqueness flags."""
    id: int
    name: str
    is_unique: bool                    # Can only slot one per build
    mutex_id: EnhancementMutex         # Mutual exclusion group
    is_superior: bool                  # Superior/ATO version
    is_proc: bool                      # Has proc effect
    ppm: float                         # Procs per minute (0 if not PPM)


@dataclass
class SlotInfo:
    """Enhancement slot in a power."""
    power_index: int
    slot_index: int
    enhancement_id: int


class ProcInteractionValidator:
    """
    Validates proc slotting and handles multiple proc interactions.

    Enforces uniqueness and mutex constraints when slotting enhancements.
    Calculates independent proc chances for multiple procs in same power.
    """

    def __init__(self, enhancements_db: dict):
        """
        Initialize validator with enhancement database.

        Args:
            enhancements_db: Dict mapping enhancement_id to Enhancement
        """
        self.enhancements_db = enhancements_db

    def validate_proc_slotting(
        self,
        enhancement_id: int,
        target_power_idx: int,
        target_slot_idx: int,
        current_build: List[List[SlotInfo]]
    ) -> tuple[bool, Optional[str]]:
        """
        Validate if enhancement can be slotted given uniqueness constraints.

        Args:
            enhancement_id: ID of enhancement to slot
            target_power_idx: Power index to slot into
            target_slot_idx: Slot index within power
            current_build: List of powers, each containing list of SlotInfo

        Returns:
            (can_slot, error_message): True if valid, False with reason if invalid
        """
        enhancement = self.enhancements_db[enhancement_id]

        # Check unique constraint
        if enhancement.is_unique:
            if self._check_unique_violation(
                enhancement_id,
                target_power_idx,
                target_slot_idx,
                current_build
            ):
                return False, (
                    f"{enhancement.name} is a unique enhancement. "
                    "You can only slot one of these across your entire build."
                )

        # Check mutex constraint
        if enhancement.mutex_id != EnhancementMutex.NONE:
            conflict = self._check_mutex_violation(
                enhancement,
                target_power_idx,
                target_slot_idx,
                current_build
            )
            if conflict:
                return False, (
                    f"Cannot slot {enhancement.name} - conflicts with "
                    f"already slotted {conflict}"
                )

        return True, None

    def _check_unique_violation(
        self,
        enhancement_id: int,
        target_power_idx: int,
        target_slot_idx: int,
        current_build: List[List[SlotInfo]]
    ) -> bool:
        """Check if unique enhancement already slotted elsewhere."""
        for power_idx, power_slots in enumerate(current_build):
            for slot_idx, slot in enumerate(power_slots):
                # Skip target slot (we're replacing/checking it)
                if power_idx == target_power_idx and slot_idx == target_slot_idx:
                    continue

                if slot.enhancement_id == enhancement_id:
                    return True  # Violation found

        return False  # No violation

    def _check_mutex_violation(
        self,
        enhancement: Enhancement,
        target_power_idx: int,
        target_slot_idx: int,
        current_build: List[List[SlotInfo]]
    ) -> Optional[str]:
        """
        Check if enhancement conflicts with mutex group.

        Returns:
            Name of conflicting enhancement, or None if no conflict
        """
        for power_idx, power_slots in enumerate(current_build):
            for slot_idx, slot in enumerate(power_slots):
                # Skip target slot
                if power_idx == target_power_idx and slot_idx == target_slot_idx:
                    continue

                slotted_enh = self.enhancements_db[slot.enhancement_id]

                # Check stealth mutex
                if (enhancement.mutex_id == EnhancementMutex.STEALTH and
                    slotted_enh.mutex_id == EnhancementMutex.STEALTH):
                    return slotted_enh.name

                # Check superior/regular version conflicts
                if (enhancement.mutex_id == slotted_enh.mutex_id and
                    enhancement.mutex_id != EnhancementMutex.NONE):
                    # Same set, different version (superior vs regular)
                    if enhancement.is_superior != slotted_enh.is_superior:
                        return slotted_enh.name

        return None  # No conflict


class MultiProcRoller:
    """
    Handles rolling multiple independent procs in same power.

    Each proc rolls independently with no suppression or interference.
    """

    def __init__(self, proc_calculator):
        """
        Initialize with proc calculator (from Spec 12).

        Args:
            proc_calculator: PPMProcCalculator instance
        """
        self.proc_calculator = proc_calculator

    def roll_multiple_procs(
        self,
        power: 'Power',
        slotted_procs: List[Enhancement],
        character_state: dict
    ) -> List[tuple[Enhancement, bool]]:
        """
        Roll all procs in power independently.

        Args:
            power: Power being activated
            slotted_procs: List of proc enhancements in power
            character_state: Current character state (buffs, recharge, etc.)

        Returns:
            List of (enhancement, activated) tuples showing which procs triggered
        """
        results = []

        for proc in slotted_procs:
            # Calculate proc chance independently (from Spec 12)
            proc_chance = self.proc_calculator.calculate_proc_chance(
                proc=proc,
                power=power,
                character_state=character_state
            )

            # Roll independently
            roll = random.random()
            activated = roll < proc_chance

            results.append((proc, activated))

        return results

    def get_active_proc_effects(
        self,
        roll_results: List[tuple[Enhancement, bool]]
    ) -> List[Enhancement]:
        """
        Extract list of procs that successfully activated.

        Args:
            roll_results: Results from roll_multiple_procs()

        Returns:
            List of Enhancement objects that activated
        """
        return [proc for proc, activated in roll_results if activated]


# Key Functions for External Use

def validate_proc_slotting(
    enhancement_id: int,
    target_power_idx: int,
    target_slot_idx: int,
    current_build: List[List[SlotInfo]],
    enhancements_db: dict
) -> tuple[bool, Optional[str]]:
    """
    Validate if proc can be slotted given uniqueness constraints.

    Convenience function that creates validator and runs check.

    Args:
        enhancement_id: ID of enhancement to slot
        target_power_idx: Power index to slot into
        target_slot_idx: Slot index within power
        current_build: List of powers, each containing list of SlotInfo
        enhancements_db: Enhancement database

    Returns:
        (can_slot, error_message): Validation result
    """
    validator = ProcInteractionValidator(enhancements_db)
    return validator.validate_proc_slotting(
        enhancement_id,
        target_power_idx,
        target_slot_idx,
        current_build
    )


def roll_multiple_procs(
    power: 'Power',
    slotted_procs: List[Enhancement],
    character_state: dict,
    proc_calculator: 'PPMProcCalculator'
) -> List[Enhancement]:
    """
    Roll all procs in power and return activated ones.

    Convenience function that creates roller and runs rolls.

    Args:
        power: Power being activated
        slotted_procs: List of proc enhancements in power
        character_state: Current character state
        proc_calculator: PPM calculator instance

    Returns:
        List of Enhancement objects that successfully activated
    """
    roller = MultiProcRoller(proc_calculator)
    roll_results = roller.roll_multiple_procs(
        power, slotted_procs, character_state
    )
    return roller.get_active_proc_effects(roll_results)
```

### Key Design Decisions

1. **Validation at Slotting Time**:
   - `validate_proc_slotting()` called before adding enhancement to build
   - Returns clear error messages for user feedback
   - Prevents invalid builds from being created

2. **Independent Rolling**:
   - Each proc rolled separately with own probability calculation
   - No cross-proc interference or suppression
   - Simple random.random() comparison per proc

3. **Mutex System**:
   - Enum-based for clear group identification
   - Separate checks for stealth vs version conflicts
   - Extensible for future mutex groups

4. **Integration Points**:
   - `proc_calculator` from Spec 12 (PPM calculation)
   - `Power` and `Enhancement` from base data structures
   - `character_state` provides buffs/recharge for proc calculation

### Testing Considerations

**Unique Validation Tests**:
- Reject slotting same unique proc twice
- Allow slotting different unique procs
- Allow replacing unique proc with itself (same slot)

**Mutex Validation Tests**:
- Reject superior + regular version of same set
- Reject multiple stealth IOs
- Allow different mutex groups simultaneously

**Multi-Proc Rolling Tests**:
- Verify independent rolling (no correlation)
- Verify all procs can activate simultaneously
- Verify correct probability calculation per proc

### Implementation Priority

**Phase 1** (Milestone 3 - Core):
- `validate_proc_slotting()` - Needed for build validation
- Unique and mutex checking logic

**Phase 2** (Milestone 4 - Calculations):
- `roll_multiple_procs()` - Needed for combat simulation
- Integration with PPM calculator (Spec 12)

**Phase 3** (Milestone 5 - Optimization):
- Performance optimization for validation checks
- Caching of mutex group memberships

## Related Specifications

- **Spec 12**: Enhancement IO Procs - PPM calculation used by each proc
- **Spec 13**: Enhancement Set Bonuses - Set bonus interaction with proc IOs
- **Spec 34**: Proc Calculation - PPM formula and proc chance calculation
- **Spec 11**: Enhancement Slotting - Overall slotting system architecture

## References

### MidsReborn Source Files
- `Core/Build.cs` - Lines 1100-1250 (SetEnhancement validation)
- `Core/Enhancement.cs` - Lines 205, 207 (Unique and MutExID properties)
- `Core/Enums.cs` - Lines 653-663 (eEnhMutex enumeration)
- `Core/Base/Data_Classes/Effect.cs` - Proc probability calculation

### Game Mechanics
- City of Heroes Wiki: Invention Origin Enhancements
- Issue 24 Patch Notes: PPM system introduction
- Enhancement Diversification (ED) and proc balancing
- Rule of Five (set bonus stacking limits)
