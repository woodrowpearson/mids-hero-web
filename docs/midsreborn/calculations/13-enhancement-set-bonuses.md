# Enhancement Set Bonuses

## Overview
- **Purpose**: Calculate set bonuses granted by slotting multiple pieces of an Invention Origin enhancement set
- **Used By**: Build totals, power display, set bonus tracking, build optimization
- **Complexity**: Complex
- **Priority**: High
- **Status**: 🟡 Breadth Complete

## MidsReborn Implementation

### Primary Location
- **File**: `Core/EnhancementSet.cs`
- **Class**: `EnhancementSet`
- **Key Structures**:
  - `BonusItem` struct - Lines 412-432
  - `Bonus[]` array (5 slots for 2-6 piece bonuses) - Line 14
  - `SpecialBonus[]` array (6 slots for per-enhancement bonuses) - Line 25

### Related Files
- **File**: `Core/I9SetData.cs`
  - **Class**: `I9SetData` - Tracks slotted sets per power
  - **Struct**: `sSetInfo` - Lines 130-136
  - **Method**: `BuildEffects()` - Lines 73-128 (activates bonuses based on slotted count)

- **File**: `Core/Build.cs`
  - **Property**: `SetBonuses` - List of all set bonus data
  - **Method**: `GetSetBonusPowers()` - Lines 88-115 (implements Rule of 5)

- **File**: `Core/Enhancement.cs`
  - **Property**: `Superior` - Marks superior/ATO sets
  - **Property**: `IsScalable` - Marks attuned enhancements

### Data Structures

```csharp
// Core/EnhancementSet.cs
public class EnhancementSet
{
    public BonusItem[] Bonus = new BonusItem[5];        // 2, 3, 4, 5, 6 piece bonuses
    public BonusItem[] SpecialBonus = new BonusItem[6]; // Per-enhancement bonuses
    public string DisplayName;
    public string ShortName;
    public int SetType;                                  // eSetType enum
    public int[] Enhancements;                          // Enhancement IDs in set
    public int LevelMin;
    public int LevelMax;
}

// BonusItem structure - Lines 412-432
public struct BonusItem
{
    public int Special;          // Special flag
    public string[] Name;        // Bonus power names
    public int[] Index;          // Power indices in database
    public string AltString;     // Alternative display string
    public Enums.ePvX PvMode;    // PvE/PvP/Any
    public int Slotted;          // Number of pieces required (2-6)
}
```

### Set Types

```csharp
// Core/Enums.cs - eSetType enumeration
public enum eSetType
{
    Untyped,
    MeleeST,         // Melee Single Target
    RangedST,        // Ranged Single Target
    RangedAoE,       // Ranged Area of Effect
    MeleeAoE,        // Melee Area of Effect
    Snipe,
    Pets,
    Defense,
    Resistance,
    Heal,
    Hold,
    Stun,
    Immob,
    Slow,
    Sleep,
    Fear,
    Confuse,
    Flight,
    Jump,
    Run,
    Teleport,
    DefDebuff,
    EndMod,
    Knockback,
    Threat,
    ToHit,
    ToHitDeb,
    PetRech,
    Travel,
    // ... more types
}
```

## High-Level Algorithm

```
Set Bonus Calculation Process:

1. Track Slotted Sets Per Power:
   FOR each power in build:
     FOR each slot in power:
       IF enhancement is SetO type:
         Add to I9SetData for that power
         Track set ID and slotted count

2. Activate Set Bonuses Based on Thresholds:
   FOR each I9SetData entry:
     FOR each set tracked:
       slottedCount = number of pieces from that set

       IF slottedCount >= 2:
         Activate 2-piece bonus (Bonus[0])
       IF slottedCount >= 3:
         Activate 3-piece bonus (Bonus[1])
       IF slottedCount >= 4:
         Activate 4-piece bonus (Bonus[2])
       IF slottedCount >= 5:
         Activate 5-piece bonus (Bonus[3])
       IF slottedCount >= 6:
         Activate 6-piece bonus (Bonus[4])

3. Check PvE/PvP Mode:
   FOR each activated bonus:
     IF bonus.PvMode == PvE AND in PvP mode:
       Skip bonus
     IF bonus.PvMode == PvP AND in PvE mode:
       Skip bonus
     IF bonus.PvMode == Any:
       Apply bonus

4. Apply Special Bonuses (Per-Enhancement):
   FOR each slotted enhancement:
     IF enhancement has SpecialBonus entry:
       Apply that specific bonus
       (Common for proc IOs and unique bonuses)

5. Apply Rule of 5 Limit:
   countByPower = array tracking each bonus power

   FOR each set bonus in build:
     FOR each power granted by bonus:
       powerIndex = bonus power index

       IF countByPower[powerIndex] < 5:
         Add power to active bonuses
         countByPower[powerIndex]++
       ELSE:
         Suppress bonus (Rule of 5 limit reached)

6. Aggregate Into Build Totals:
   Apply all non-suppressed set bonus powers
   Add to character's total stats
```

## Game Mechanics Context

### Set Bonus Overview

Enhancement sets in City of Heroes provide bonuses when multiple pieces from the same set are slotted in a single power. These bonuses are a fundamental part of build optimization.

**Set Bonus Activation**:
- **2-piece**: Slot any 2 enhancements from the set
- **3-piece**: Slot any 3 enhancements from the set
- **4-piece**: Slot any 4 enhancements from the set
- **5-piece**: Slot any 5 enhancements from the set
- **6-piece**: Slot all 6 enhancements from the set (if available)

**Important**: Set bonuses are activated **per power**, not globally. If you slot 3 pieces of a set in Power A and 3 pieces of the same set in Power B, you get the 2-piece AND 3-piece bonuses TWICE (once from each power).

### The Rule of 5

**Critical Mechanic**: Only 5 instances of any identical bonus can be active at once.

**How It Works**:
- Each set bonus grants specific powers (e.g., "+1.5% Ranged Defense")
- The system counts how many times each bonus power is granted across ALL set bonuses
- Once a bonus power is granted 5 times, additional instances are suppressed

**Example**:
```
Character has slotted multiple sets:
- 3x Thunderstrike sets (each grants +1.5% Ranged Defense at 2-piece)
- 2x Decimation sets (each grants +1.5% Ranged Defense at 3-piece)
- 1x Sting of the Manticore (grants +1.5% Ranged Defense at 2-piece)

Result: Only 5 instances of "+1.5% Ranged Defense" count
  Instance 1: Thunderstrike #1 ✅
  Instance 2: Thunderstrike #2 ✅
  Instance 3: Thunderstrike #3 ✅
  Instance 4: Decimation #1 ✅
  Instance 5: Decimation #2 ✅
  Instance 6: Sting of Manticore ❌ SUPPRESSED (Rule of 5)
```

**Implementation Detail** (Build.cs lines 88-115):
```csharp
private List<IPower> GetSetBonusPowers()
{
    var powerList = new List<IPower>();
    var nidPowers = DatabaseAPI.NidPowers("set_bonus");
    var setCount = new int[nidPowers.Length];  // Tracks count per bonus power

    foreach (var setBonus in SetBonuses)
    {
        foreach (var info in setBonus.SetInfo)
        {
            foreach (var powerIndex in info.Powers)
            {
                ++setCount[powerIndex];

                // Rule of 5: Only add if count < 6
                if (setCount[powerIndex] >= 6) continue;

                var power = DatabaseAPI.Database.Power[powerIndex];
                if (power != null) powerList.Add(power.Clone());
            }
        }
    }

    return powerList;
}
```

Note: The code uses `>= 6` to allow 5 instances (count 1-5 are added, count 6+ are skipped).

### Common Set Bonuses

**Defense Bonuses**:
- Ranged Defense (+1.5%, +3.13%, +5%)
- Melee Defense (+1.5%, +3.13%, +5%)
- AoE Defense (+1.5%, +3.13%, +5%)
- Smashing/Lethal Defense (+1.88%, +3.75%)
- Energy/Negative Defense (+1.88%, +3.75%)
- Fire/Cold Defense (+1.88%, +3.75%)

**Recharge Bonuses**:
- +5% Recharge (very common at 5-piece)
- +6.25% Recharge
- +7.5% Recharge
- +10% Recharge (rare, purple sets)

**Accuracy/ToHit Bonuses**:
- +9% Accuracy (common)
- +7% ToHit (less common)

**Recovery/Endurance**:
- +1.5% Recovery
- +2.5% Recovery
- +2% Max Endurance

**Hit Points**:
- +1.13% Max HP
- +1.88% Max HP

**Damage Bonuses**:
- +2% Damage (all types)
- +3% Damage (typed)
- +4% Damage (rare)

**Status Protection** (for non-melee ATs):
- Hold protection
- Stun protection
- Immobilize protection
- Sleep protection

### Superior vs Regular Sets

**Superior Sets** (ATOs - Archetype Origin Enhancements):
- Only available for specific archetypes
- Typically have better bonuses than regular sets
- Often include unique proc effects
- Marked by `Enhancement.Superior = true`

**Regular Sets**:
- Available to all archetypes (if power accepts set type)
- Standard bonus values
- Most common set type

### Attuned vs Fixed-Level Sets

**Attuned IOs** (`Enhancement.IsScalable = true`):
- Scale to character's combat level
- Always provide full enhancement values
- Set bonuses always active (no level restrictions)
- Cannot be enhanced with boosters
- Common for purchased sets

**Fixed-Level IOs**:
- Crafted at specific level (10, 15, 20, 25, 30, 35, 40, 45, 50)
- Enhancement values depend on crafted level
- Set bonuses require character level >= (crafted level - 3)
- Can be enhanced with boosters (+1 through +5)
- More powerful when boosted

**Example**:
```
Level 50 Thunderstrike (fixed):
- Set bonuses require character level 47+ (50 - 3)
- Can be boosted to +5 for better enhancement values
- Set bonuses same as attuned version

Attuned Thunderstrike:
- Set bonuses always active at any level
- Enhancement values scale with combat level
- Cannot be boosted
- More flexible for exemplaring
```

### Set Bonus Suppression vs Rule of 5

**Rule of 5** (described above):
- Limits identical bonuses across different sets
- Prevents stacking the same bonus more than 5 times
- Global limit across entire build

**Set Bonus Suppression** (different mechanic, not fully shown in provided code):
- Can occur during exemplaring (level reduction)
- Some bonuses may suppress in PvP zones
- Special case suppression for certain powers

### Special Enhancement Bonuses

**SpecialBonus Array** (per-enhancement bonuses):
- Some sets grant bonuses for slotting specific enhancements
- Most common in Pet sets (6th enhancement often has special pet buff)
- Proc IOs often have their proc in SpecialBonus
- Activated when that specific enhancement is slotted (not just any from set)

**Example from code** (I9SetData.cs lines 100-126):
```csharp
// Process special bonuses per enhancement
for (var index2 = 0; index2 <= EnhancementSets[setIdx].Enhancements.Length - 1; ++index2)
{
    if (EnhancementSets[setIdx].SpecialBonus[index2].Index.Length <= -1)
        continue;

    for (var index3 = 0; index3 <= SetInfo[index1].EnhIndexes.Length - 1; ++index3)
    {
        if (SetInfo[index1].EnhIndexes[index3] ==
            EnhancementSets[setIdx].Enhancements[index2])
        {
            // This specific enhancement is slotted - grant its special bonus
            AddSpecialBonusPowers(setIdx, index2);
        }
    }
}
```

## Python Implementation Guide

### Proposed Architecture

**Module**: `backend/app/calculations/set_bonuses.py`

```python
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

class PvMode(Enum):
    PVE = "pve"
    PVP = "pvp"
    ANY = "any"

@dataclass
class BonusItem:
    """Represents a single set bonus tier (2-piece, 3-piece, etc.)"""
    slotted_required: int      # Number of pieces needed (2-6)
    power_ids: List[int]       # Bonus power IDs granted
    pv_mode: PvMode           # PvE/PvP/Any
    alt_string: Optional[str] = None  # Alternative display

@dataclass
class EnhancementSet:
    """Enhancement set definition"""
    id: int
    name: str
    short_name: str
    set_type: str
    level_min: int
    level_max: int
    enhancement_ids: List[int]
    bonuses: List[BonusItem]           # Regular bonuses (2-6 piece)
    special_bonuses: List[BonusItem]   # Per-enhancement bonuses

@dataclass
class SlottedSet:
    """Tracks a set slotted in a specific power"""
    power_id: int
    set_id: int
    slotted_count: int
    enhancement_ids: List[int]  # Specific enhancements slotted

class SetBonusCalculator:
    """Calculates active set bonuses with Rule of 5"""

    def __init__(self, pv_mode: PvMode = PvMode.PVE):
        self.pv_mode = pv_mode
        self.bonus_power_counts: Dict[int, int] = {}

    def calculate_set_bonuses(
        self,
        slotted_sets: List[SlottedSet],
        enhancement_sets: Dict[int, EnhancementSet]
    ) -> List[int]:
        """
        Returns list of active bonus power IDs with Rule of 5 applied.

        Args:
            slotted_sets: All sets slotted across all powers
            enhancement_sets: Set definitions

        Returns:
            List of bonus power IDs (may contain duplicates up to 5)
        """
        active_bonuses = []
        self.bonus_power_counts = {}

        for slotted in slotted_sets:
            set_def = enhancement_sets[slotted.set_id]

            # Check regular bonuses (2-6 piece)
            for bonus in set_def.bonuses:
                if slotted.slotted_count >= bonus.slotted_required:
                    if self._should_apply_bonus(bonus):
                        active_bonuses.extend(
                            self._apply_rule_of_5(bonus.power_ids)
                        )

            # Check special bonuses (per-enhancement)
            for i, enh_id in enumerate(set_def.enhancement_ids):
                if enh_id in slotted.enhancement_ids:
                    special = set_def.special_bonuses[i]
                    if special and self._should_apply_bonus(special):
                        active_bonuses.extend(
                            self._apply_rule_of_5(special.power_ids)
                        )

        return active_bonuses

    def _should_apply_bonus(self, bonus: BonusItem) -> bool:
        """Check if bonus applies in current PvE/PvP mode"""
        if bonus.pv_mode == PvMode.ANY:
            return True
        return bonus.pv_mode == self.pv_mode

    def _apply_rule_of_5(self, power_ids: List[int]) -> List[int]:
        """
        Apply Rule of 5: maximum 5 instances of any bonus power.

        Returns power IDs that should be added (may be empty if suppressed).
        """
        added = []
        for power_id in power_ids:
            count = self.bonus_power_counts.get(power_id, 0)
            if count < 5:
                added.append(power_id)
                self.bonus_power_counts[power_id] = count + 1
            # else: suppressed by Rule of 5

        return added

# Helper function for tracking sets in build
def track_slotted_sets(build_data: dict) -> List[SlottedSet]:
    """
    Extract slotted set information from build data.

    Returns list of SlottedSet objects, one per set per power.
    """
    slotted_sets = []

    for power in build_data['powers']:
        set_tracker = {}  # set_id -> list of enhancement_ids

        for slot in power['slots']:
            enh = slot['enhancement']
            if enh and enh['type'] == 'SetO':
                set_id = enh['set_id']
                if set_id not in set_tracker:
                    set_tracker[set_id] = []
                set_tracker[set_id].append(enh['id'])

        # Create SlottedSet for each set in this power
        for set_id, enh_ids in set_tracker.items():
            slotted_sets.append(SlottedSet(
                power_id=power['id'],
                set_id=set_id,
                slotted_count=len(enh_ids),
                enhancement_ids=enh_ids
            ))

    return slotted_sets
```

### Implementation Notes

**Key Considerations**:

1. **Rule of 5 Tracking**:
   - Must track bonus power counts globally across entire build
   - Order matters: first 5 instances are kept, rest suppressed
   - Reset counts when recalculating entire build

2. **PvE vs PvP Mode**:
   - Some bonuses only apply in PvE
   - Some bonuses only apply in PvP
   - Many bonuses apply in both (PvMode.ANY)
   - Mode must be specified at calculation time

3. **Set Identification**:
   - Sets are identified by their set_id, not name
   - Multiple powers can slot the same set (bonuses stack)
   - Each power's sets are tracked independently

4. **Special Bonuses**:
   - SpecialBonus array is parallel to Enhancements array
   - Index i in SpecialBonus corresponds to index i in Enhancements
   - Only granted when that specific enhancement is slotted
   - Common for proc IOs (the proc is the special bonus)

5. **Attuned vs Fixed Level**:
   - Attuned: bonuses always active, no level check
   - Fixed: bonuses require character level >= (IO level - 3)
   - For initial implementation, focus on attuned (simpler)
   - Add level checking later for fixed-level IOs

6. **Database Structure**:
   - Enhancement sets stored in separate table
   - Link: Enhancement -> set_id -> EnhancementSet
   - Bonus powers stored as power entries (special "set_bonus" powerset)
   - Special query: `DatabaseAPI.NidPowers("set_bonus")` gets all bonus powers

### Edge Cases to Test

1. **Rule of 5 Suppression**:
   ```python
   # 6 instances of same bonus - 6th should be suppressed
   assert len([b for b in bonuses if b == "+1.5% Ranged Def"]) == 5
   ```

2. **Multiple Sets Per Power**:
   ```python
   # Can slot 3 from Set A and 3 from Set B in same power
   # Should get bonuses from both sets
   ```

3. **Incomplete Sets**:
   ```python
   # Slot only 2 pieces from 6-piece set
   # Should only get 2-piece bonus
   ```

4. **PvE/PvP Mode Switching**:
   ```python
   # Some bonuses disappear when switching modes
   pve_bonuses = calc.calculate_set_bonuses(sets, PvMode.PVE)
   pvp_bonuses = calc.calculate_set_bonuses(sets, PvMode.PVP)
   assert pve_bonuses != pvp_bonuses  # Some sets have different bonuses
   ```

5. **Special Enhancement Bonuses**:
   ```python
   # Pet set 6th enhancement grants special pet buff
   # Only active when that specific enhancement is slotted
   ```

### Test Cases

**Test Case 1: Basic Set Activation**:
```python
Input:
  Power A: 3x Thunderstrike enhancements

Expected:
  - 2-piece bonus active: +2% Damage (all types)
  - 3-piece bonus active: +9% Accuracy
  - 4-piece bonus NOT active
  - 5-piece bonus NOT active
  - 6-piece bonus NOT active
```

**Test Case 2: Rule of 5**:
```python
Input:
  Power A: 2x Set X (grants +1.5% Ranged Def)
  Power B: 2x Set X (grants +1.5% Ranged Def)
  Power C: 2x Set Y (grants +1.5% Ranged Def)
  Power D: 2x Set Z (grants +1.5% Ranged Def)
  Power E: 2x Set W (grants +1.5% Ranged Def)
  Power F: 2x Set V (grants +1.5% Ranged Def)

Expected:
  - Only 5 instances of "+1.5% Ranged Def" active
  - 6th instance suppressed
  - Final total: +7.5% Ranged Defense (5 × 1.5%)
```

**Test Case 3: PvE vs PvP**:
```python
Input:
  Power A: Full PvP IO set (6 pieces)
  Mode: PvE

Expected:
  - PvE-specific bonuses active
  - PvP-specific bonuses suppressed
  - "Any" mode bonuses active
```

**Test Case 4: Special Enhancement Bonus**:
```python
Input:
  Power A (Pet): 6x Call of the Sandman (Pet Damage set)
  Enhancement 6: "Chance for Heal" proc

Expected:
  - Regular set bonuses (2, 3, 4, 5, 6 piece) active
  - Special bonus from 6th enhancement (heal proc) active
```

### Validation Strategy

1. **Load MidsReborn Database**:
   - Import enhancement set definitions
   - Verify bonus power IDs match
   - Check PvE/PvP flags

2. **Compare Simple Builds**:
   - Create build with 1 complete set
   - Verify all bonuses activate correctly
   - Compare to MidsReborn display

3. **Test Rule of 5**:
   - Create build with 6+ instances of same bonus
   - Verify only 5 are active
   - Compare suppression to MidsReborn

4. **Validate Common Sets**:
   - Test popular sets (Thunderstrike, Crushing Impact, etc.)
   - Verify bonus values and thresholds
   - Check against known builds

## References

- Related Specs:
  - **Spec 10**: Enhancement Schedules (ED curves)
  - **Spec 11**: Enhancement Slotting
  - **Spec 12**: IO Procs
  - **Spec 19-24**: Build Totals (consume set bonuses)
  - **Spec 25**: Buff Stacking Rules

- MidsReborn Files:
  - `Core/EnhancementSet.cs` - Set definitions
  - `Core/I9SetData.cs` - Set tracking per power
  - `Core/Build.cs` - Rule of 5 implementation
  - `Core/Enhancement.cs` - Superior/Attuned flags
  - `Core/Enums.cs` - eSetType enumeration

- Game Mechanics:
  - City of Heroes Wiki: Invention Origin Enhancements
  - Paragon Wiki: Set Bonuses
  - HC Wiki: Enhancement Sets

---

**Document Status**: ✅ Breadth Complete - High-level structure documented
**Next Steps**: Await Milestone 3 for depth detail (full Python implementation, comprehensive test suite)
