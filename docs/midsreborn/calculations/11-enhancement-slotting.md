# Enhancement Slotting

## Overview
- **Purpose**: Manage how multiple enhancements are slotted into powers and calculate their combined effects
- **Used By**: Power calculations, build validation, enhancement UI, slot management
- **Complexity**: Medium-High
- **Priority**: Critical
- **Status**: 🟡 Breadth Complete

## MidsReborn Implementation

### Primary Location
- **File**: `Core/I9Slot.cs`
- **Class**: `I9Slot` - Represents a single slotted enhancement (Issue 9+ system)
- **Related Files**:
  - `Core/SlotEntry.cs` - Wrapper for slot-level data (level, inherent status, primary/flipped enhancement)
  - `Core/PowerEntry.cs` - Power instance with slots array
  - `Core/Enhancement.cs` - Enhancement database entries
  - `Core/Enums.cs` - Enhancement grades, schedules, relative levels

### I9Slot Class Structure

The `I9Slot` class represents a single slotted enhancement:

```csharp
public class I9Slot : ICloneable
{
    private const float SuperiorMult = 1.25f;

    public int Enh;                           // Enhancement ID (-1 if empty)
    public Enums.eEnhGrade Grade;             // None, TrainingO, DualO, SingleO
    public int IOLevel;                       // Invention Origin level (1-53)
    public Enums.eEnhRelative RelativeLevel;  // -3 to +5 relative to character
    public bool Obtained;                     // Whether player has acquired it
}
```

**Enhancement Grades** (`eEnhGrade`):
- `None` - Empty slot
- `TrainingO` - Training Origin (weakest)
- `DualO` - Dual Origin (medium)
- `SingleO` - Single Origin (standard SOs)

**Relative Level** (`eEnhRelative`):
- Ranges from `MinusThree` (-3) to `PlusFive` (+5)
- Affects enhancement effectiveness via multiplier:
  - Below Even (0): `multiplier = 1.0 + (relative_level * 0.1)`
    Example: -1 = 90%, -2 = 80%, -3 = 70%
  - At or Above Even: `multiplier = 1.0 + (relative_level * 0.05)`
    Example: +1 = 105%, +3 = 115%, +5 = 125%

### SlotEntry Structure

Each power has an array of `SlotEntry` structs:

```csharp
public struct SlotEntry
{
    public int Level;                      // Character level when slot added
    public bool IsInherent;                // True if automatic/inherent slot
    public I9Slot Enhancement;             // Primary enhancement
    public I9Slot FlippedEnhancement;      // Alternate enhancement (dual build)
}
```

### PowerEntry Slots

```csharp
public class PowerEntry
{
    public SlotEntry[] Slots;              // Array of slots
    public int SlotCount => Slots?.Length ?? 0;
    public int InherentSlotsUsed { get; set; }
}
```

## High-Level Algorithm

### Slot Initialization

```
When Power is Created:
1. If power is slottable AND not Incarnate:
   - Create 1 default slot (base slot)
   - Initialize with empty I9Slot instances
   - Set level to power's chosen level
   - Mark as not inherent

2. If power is not slottable:
   - Slots = empty array
```

### Slot Limits

```
Slot Validation Rules:
1. Default Maximum: 6 slots per power
   - Code enforces via: if SlotCount > 6 then Slots = Slots.Take(6)

2. If power is not slottable:
   - Maximum = 0 slots

3. Enhancement sets can define custom slot counts (2-11)
   - Visible in set editor UI

4. First slot is typically inherent (comes with power)
   - Cannot be removed without removing power
```

### Inherent Slots

Special rules for automatic slots:

```
Inherent Slot System:
1. First slot when power is chosen:
   - SlotEntry.IsInherent = false
   - This is the BASE slot (not technically inherent)

2. Special inherent powers (Fitness powers):
   - Health, Stamina get additional inherent slots at specific levels
   - Check: DatabaseAPI.ServerData.EnableInherentSlotting
   - Removal restricted in Normal mode
   - Can reassign in Respec mode (assumes power was 6-slotted in-game)

3. InherentSlotsUsed counter:
   - Tracks how many inherent slots are active
   - Used for build validation
```

### Enhancement Validation

```
IsEnhancementValid(enhancementId):
1. Check enhancement ID is in valid range
2. Get enhancement TypeID (Normal, InventO, SetO, SpecialO)
3. Get valid enhancements for this power:
   a. For SetO: Check power.SetTypes matches enhancement set type
   b. For other types: Check enhancement.ClassID matches power.Enhancements list
4. Return true if enhancement ID is in valid list
```

### Enhancement Effect Calculation

Each slotted enhancement contributes bonuses based on schedules:

```
GetEnhancementEffect(effectType, subEffect, magnitude):
1. If slot is empty (Enh == -1): return 0
2. Get enhancement from database
3. For each effect in enhancement.Effect[]:
   a. Skip if effect.Mode != Enhancement
   b. Skip if effect.Schedule == None
   c. Skip if wrong effect type or sub-effect
   d. Calculate schedule multiplier:
      scheduleMult = GetScheduleMult(enhancement.TypeID, effect.Schedule)
   e. If effect has multiplier: scheduleMult *= effect.Multiplier
   f. Add to total
4. Return total enhancement value
```

### Schedule Multiplier Calculation

Enhancement effectiveness varies by type and schedule:

```
GetScheduleMult(enhType, schedule):
1. Validate and clamp Grade (None to SingleO)
2. Validate and clamp RelativeLevel (None to PlusFive)
3. Validate and clamp IOLevel (0 to max IO level)
4. Skip if schedule == None or Multiple

5. Get base multiplier by type:
   - Normal (TO/DO/SO):
     * TrainingO: MultTO[0][schedule_index]
     * DualO: MultDO[0][schedule_index]
     * SingleO: MultSO[0][schedule_index]

   - InventO: MultIO[IOLevel][schedule_index]
   - SpecialO: MultSO[0][schedule_index]  (same as SO)
   - SetO: MultIO[IOLevel][schedule_index]  (same as IO)

6. Apply relative level multiplier:
   baseMult *= GetRelativeLevelMultiplier()

7. If Superior enhancement:
   baseMult *= 1.25  (Superior multiplier)

8. Return final multiplier
```

### Enhancement Schedules

Schedules determine enhancement strength (database-driven values):

- **Schedule A**: Typically used for primary enhancement types (highest values)
- **Schedule B**: Secondary enhancement types (medium values)
- **Schedule C**: Tertiary enhancement types (lower values)
- **Schedule D**: Quaternary enhancement types (lowest values)
- **None**: Not enhanceable
- **Multiple**: Complex calculation (not handled by standard multiplier)

**Example Schedule Values** (loaded from `Maths.mhd` file):
- SO Schedule A: ~38.3% per enhancement
- SO Schedule B: ~25.5% per enhancement
- IO Level 50 Schedule A: ~42.4% per enhancement

### Combining Multiple Enhancements

```
Total Power Enhancement Calculation:
1. For each slot in power.Slots[]:
   a. Get enhancement effect for this slot:
      slotBonus = slot.Enhancement.GetEnhancementEffect(effectType, subEffect, magnitude)
   b. Add to running total (ADDITIVE before ED):
      totalBonus += slotBonus

2. Apply Enhancement Diversification (ED):
   // See Spec 10 for ED curve details
   // ED reduces effectiveness of stacking same-type enhancements
   finalBonus = ApplyEDCurve(totalBonus)

3. Return final enhancement multiplier:
   power.magnitude *= (1.0 + finalBonus)
```

**Key Point**: Enhancements of the same type are **additive** before ED is applied:
- 3x Level 50 Damage IOs (Schedule A ~42.4% each)
- Before ED: 42.4% + 42.4% + 42.4% = 127.2%
- After ED: ~95% (ED curve reduces high values)

### IO vs SO/HO Slotting Differences

```
Enhancement Type Comparisons:

Training/Dual/Single Origin (TO/DO/SO):
- Grade-based (eEnhGrade enum)
- Relative level affects power (-3 to +5)
- Schedule-based values from MultTO/MultDO/MultSO tables
- Fixed values per grade/schedule
- Example: SO Schedule A = 38.3%

Invention Origin (IO):
- Level-based (IOLevel 1-53)
- Uses MultIO[level][schedule] table
- Higher levels = stronger bonuses
- Not affected by relative level
- Example: Level 50 IO Schedule A = 42.4%

Set IO:
- Same as regular IO for individual enhancement power
- Additional set bonuses when multiple pieces slotted
- Can be Superior (1.25x multiplier)
- Level-locked (don't degrade with level)

Special Origin (HO - Hamidon Origin):
- Uses SO multiplier table (MultSO)
- Typically dual-aspect or triple-aspect
- Example: Hamidon Damage/Accuracy affects both
- Not affected by relative level
```

### Dual Build Support

Each slot has two enhancement references:
- `Enhancement` - Primary build's enhancement
- `FlippedEnhancement` - Secondary build's enhancement

```
Flip():
  Swap Enhancement and FlippedEnhancement
  Used when switching between dual builds
```

## Key Data Structures

### Enhancement Effect Structure

```csharp
public struct sEffect
{
    public Enums.eEffMode Mode;        // Enhancement, FX, PowerEnh, PowerProc
    public Enums.eBuffDebuff BuffMode; // BuffOnly, DeBuffOnly, Any
    public sEnhance Enhance;           // Which attribute to enhance
    public Enums.eSchedule Schedule;   // A, B, C, D (strength tier)
    public float Multiplier;           // Additional multiplier on schedule
    public IEffect? FX;                // Associated effect (for procs)
}

public struct sEnhance
{
    public int ID;        // eEnhance enum value
    public int SubID;     // Sub-type (e.g., specific mez type)
}
```

### Enhancement Types

```csharp
public enum eType
{
    Normal,     // TO/DO/SO
    InventO,    // IOs
    SpecialO,   // HOs
    SetO        // Set IOs
}

public enum eSchedule
{
    None = -1,
    A = 0,      // Strongest
    B = 1,      // Medium
    C = 2,      // Weak
    D = 3,      // Weakest
    Multiple = 4 // Complex
}
```

## Critical Implementation Notes

### 1. Empty Slot Detection
```csharp
// Empty slot check
if (Enh < 0) return 0.0f;
```

### 2. Slot Limit Enforcement
```csharp
// In PowerEntry.ValidateSlots()
Slots = SlotCount switch
{
    > 0 when (Power == null && !Chosen || Power is {Slottable: false})
        => Array.Empty<SlotEntry>(),
    > 6 => Slots.Take(6).ToArray(),  // Enforce 6-slot max
    _ => Slots
};
```

### 3. Enhancement Validation
```csharp
// Invalid enhancements are cleared
if (!Power.IsEnhancementValid(Slots[index].Enhancement.Enh))
{
    Slots[index].Enhancement = new I9Slot();  // Reset to empty
}
```

### 4. Superior Enhancement Bonus
```csharp
private const float SuperiorMult = 1.25f;

// Applied after schedule and relative level multipliers
if (Enh > -1 && DatabaseAPI.Database.Enhancements[Enh].Superior)
{
    scheduleMult *= SuperiorMult;  // 25% bonus
}
```

### 5. First Slot Special Handling
```csharp
// First slot typically cannot be removed
if (SlotCount == 1 && Slots[0].Enhancement.Enh == -1)
{
    Slots = Array.Empty<SlotEntry>();  // Remove empty base slot
}
```

## Enhancement String Display

The system generates detailed enhancement descriptions:

```
GetEnhancementStringLong() output examples:

Normal Enhancement:
  "+1 Single Origin - Schedule: A (40.3%)"

Set IO:
  "Damage enhancement (Sched. A: 42.4%)"
  "Accuracy/Damage enhancement (Sched. A: 26.5%)"

Proc Enhancement:
  "Effect: Chance for Fire Damage"
  "  33% chance for 71.75 fire damage"
```

## Edge Cases

### 1. Incarnate Powers
```csharp
// Incarnate powers are NOT slottable
if (power.Slottable & (power.GetPowerSet()?.GroupName != "Incarnate"))
{
    // Create default slot
}
```

### 2. Toggle Power Enhancement Effects
```csharp
// Toggle powers apply enhancement effects per activation period
if (power.PowerType == Toggle && isEnhancementEffect)
{
    effectValue *= power.ActivatePeriod / 10.0;
}
```

### 3. Build Mode Restrictions
```csharp
// Inherent slots behave differently by mode
if (slotEntry.IsInherent && BuildMode == Normal)
{
    // Cannot remove inherent slots in Normal mode
}
else if (slotEntry.IsInherent && BuildMode == Respec)
{
    // Can reassign in Respec (assumes 6-slotted in-game)
}
```

## Related Systems

- **Spec 10 - Enhancement Diversification (ED)**: Applies curve to combined enhancement totals
- **Spec 1 - Power Effects Core**: Where enhancement bonuses are applied to effect magnitudes
- **Spec 12 - Enhancement Sets**: Set bonuses from multiple slotted pieces
- **Spec 2 - Power Damage**: How damage enhancements modify damage output
- **Spec 7 - Recharge Modifiers**: How recharge enhancements reduce power cooldowns

## Python Implementation Considerations

### Database Requirements
```python
class EnhancementSlot:
    """Represents a single enhancement slot"""
    enhancement_id: int = -1  # -1 = empty
    grade: EnhancementGrade  # TO, DO, SO
    io_level: int = 1  # 1-53 for IOs
    relative_level: int = 0  # -3 to +5
    obtained: bool = False

class SlotEntry:
    """Full slot information"""
    level: int
    is_inherent: bool
    enhancement: EnhancementSlot
    flipped_enhancement: EnhancementSlot  # For dual builds

class PowerInstance:
    """Power with slotting"""
    slots: list[SlotEntry]
    inherent_slots_used: int = 0

    @property
    def slot_count(self) -> int:
        return len(self.slots)
```

### Schedule Multiplier Tables
```python
# Load from database
mult_to: list[list[float]]  # [1][4] - Training Origin schedules
mult_do: list[list[float]]  # [1][4] - Dual Origin schedules
mult_so: list[list[float]]  # [1][4] - Single Origin schedules
mult_io: list[list[float]]  # [53][4] - IO by level schedules
mult_ed: list[list[float]]  # [4][3] - ED curve values

# Example values (from Maths.mhd)
# mult_so[0][SCHEDULE_A] ≈ 0.383  (38.3%)
# mult_io[50][SCHEDULE_A] ≈ 0.424 (42.4%)
```

### Enhancement Effect Calculation
```python
def get_enhancement_effect(
    slot: EnhancementSlot,
    effect_type: EnhanceType,
    sub_effect: int,
    magnitude: float
) -> float:
    """Calculate enhancement bonus from single slot"""
    if slot.enhancement_id < 0:
        return 0.0

    enhancement = db.enhancements[slot.enhancement_id]
    total = 0.0

    for effect in enhancement.effects:
        if effect.mode != EffectMode.ENHANCEMENT:
            continue
        if effect.schedule == Schedule.NONE:
            continue
        if effect.enhance_id != effect_type:
            continue
        if sub_effect >= 0 and effect.enhance_sub_id != sub_effect:
            continue

        # Get schedule multiplier
        sched_mult = get_schedule_mult(
            enhancement.type_id,
            effect.schedule,
            slot.grade,
            slot.io_level,
            slot.relative_level,
            enhancement.is_superior
        )

        if effect.multiplier > 0:
            sched_mult *= effect.multiplier

        total += sched_mult

    return total

def combine_enhancements(
    slots: list[SlotEntry],
    effect_type: EnhanceType,
    sub_effect: int = -1
) -> float:
    """Combine multiple enhancement bonuses (additive before ED)"""
    total = 0.0

    for slot in slots:
        bonus = get_enhancement_effect(
            slot.enhancement,
            effect_type,
            sub_effect,
            1.0  # magnitude for checking
        )
        total += bonus  # ADDITIVE

    # Apply ED curve (see Spec 10)
    final = apply_ed_curve(total)

    return final
```

### Validation
```python
def validate_slotting(power_instance: PowerInstance) -> list[str]:
    """Validate slotting rules"""
    errors = []

    # Check slot count
    if len(power_instance.slots) > 6:
        errors.append(f"Too many slots: {len(power_instance.slots)} > 6")

    # Check if power is slottable
    if not power_instance.power.slottable and len(power_instance.slots) > 0:
        errors.append("Power is not slottable")

    # Validate each enhancement
    for i, slot in enumerate(power_instance.slots):
        if slot.enhancement.enhancement_id < 0:
            continue  # Empty slot is valid

        if not is_enhancement_valid(
            power_instance.power,
            slot.enhancement.enhancement_id
        ):
            errors.append(
                f"Slot {i}: Invalid enhancement {slot.enhancement.enhancement_id}"
            )

    return errors
```

## Testing Recommendations

1. **Slot Limit Validation**
   - Verify 6-slot maximum enforcement
   - Test non-slottable powers reject slots
   - Test enhancement set custom slot counts

2. **Enhancement Effect Calculation**
   - Test empty slots return 0
   - Verify schedule multiplier lookups (TO/DO/SO/IO)
   - Test relative level multipliers (-3 to +5)
   - Verify Superior enhancement 1.25x bonus

3. **Enhancement Combining**
   - Test multiple same-type enhancements are additive
   - Verify ED is applied to combined total
   - Test different enhancement types combine correctly

4. **Validation**
   - Test invalid enhancements are rejected
   - Verify enhancement class restrictions
   - Test set IO validation against power set types

5. **Edge Cases**
   - Test Incarnate powers (not slottable)
   - Test inherent slot special rules
   - Test dual build slot flipping
   - Verify toggle power enhancement period adjustment
