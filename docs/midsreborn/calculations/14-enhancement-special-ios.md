# Enhancement Special IOs

## Overview
- **Purpose**: Special IO behaviors including global recharge, stealth, unique restrictions, and special procs
- **Used By**: Build totals, slotting validation, enhancement effects
- **Complexity**: Medium
- **Priority**: High
- **Status**: 🟡 Breadth Complete

## MidsReborn Implementation

### Primary Location
- **File**: `Core/Enhancement.cs`
- **Class**: `Enhancement`
- **Key Properties**:
  - `Unique` (bool) - Lines vary (serialization in Read/Write methods)
  - `MutExID` (Enums.eEnhMutex) - Mutual exclusion group
  - `IsProc` (bool) - Marks as proc IO
  - `ProcsPerMinute` (float in Effect.cs) - PPM value for proc calculation

### Related Files
- **`Core/Build.cs`**: Unique and mutex validation during slotting
  - Unique validation: ~line checking `enhancement.Unique`
  - Stealth mutex: ~line checking `MutExID == Enums.eEnhMutex.Stealth`
  - Archetype mutex: ~line checking Superior vs normal ATO conflicts
- **`Core/Enums.cs`**: `eEnhMutex` enumeration
- **`Core/Base/Data_Classes/Effect.cs`**: Proc probability calculation
  - `ActualProbability` property
  - `MinProcChance` property
  - `MaxProcChance` constant (0.9f)

### Special IO Categories

**1. Unique IOs (Global Restriction)**:
- Property: `Unique = true`
- Behavior: Only one can be slotted in entire build
- Validation: Build.cs checks all slotted enhancements
- Examples:
  - Performance Shifter: Chance for +End
  - Miracle: +Recovery
  - Numina's Convalescence: +Regeneration/+Recovery
  - Theft of Essence: Chance for +End

**2. Mutually Exclusive IOs (Group Restriction)**:
- Property: `MutExID` (eEnhMutex enum)
- Types:
  - `None`: No restrictions
  - `Stealth`: Only one stealth IO allowed
  - `ArchetypeA-F`: Archetype origin IOs (Superior vs Normal)
- Validation: Build.cs checks by MutExID group

**3. Stealth IOs (Special Group)**:
- `MutExID = Enums.eEnhMutex.Stealth`
- Only one allowed in entire build
- Common IOs in this category:
  - Celerity: Stealth
  - Unbounded Leap: Stealth
  - Winter's Gift: Slow Resistance/Stealth
- Grant invisibility/stealth powers or effects

**4. Archetype Origin IOs (ATO Mutex)**:
- Superior vs Normal versions mutually exclusive
- `MutExID = ArchetypeA` through `ArchetypeF`
- Validation uses regex to strip "Attuned_" and "Superior_" prefixes
- Prevents slotting both Superior and normal versions of same ATO

**5. Global Recharge IOs**:
- Most famous: Luck of the Gambler: +7.5% Recharge
- Implemented as enhancement effects with:
  - `EffectType = Enhancement`
  - `ETModifies = Recharge`
  - Affects all powers globally (not just slotted power)
- Stacks with other global recharge bonuses

**6. Special Procs**:
- Property: `IsProc = true`
- Effect property: `ProcsPerMinute > 0`
- Calculation: PPM-based (Procs Per Minute) or flat chance
- Notable special cases:
  - **Proc120**: Procs with 120-second cooldown
  - **Performance Shifter +End**: Unique proc, 20% chance
  - **Miracle +Regen/+Recovery**: Unique, constant effect (not a "proc")
  - **Numina +Regen/+Recovery**: Unique, constant effect

### Algorithm Pseudocode

```
SPECIAL IO TYPES AND BEHAVIORS:

1. UNIQUE IO VALIDATION (Build.cs):
   When slotting enhancement:
     IF enhancement.Unique == true:
       FOR each slotted_enhancement in build:
         IF slotted_enhancement.Enh == enhancement.Enh:
           REJECT: "Enhancement is unique, already slotted"
           RETURN false

2. MUTUAL EXCLUSION VALIDATION (Build.cs):
   When slotting enhancement:
     IF enhancement.MutExID != None:
       CASE enhancement.MutExID:

         STEALTH:
           FOR each slotted_enh in build:
             IF slotted_enh.MutExID == Stealth:
               REJECT: "Only one Stealth IO allowed"
               RETURN false

         ARCHETYPE (Superior check):
           IF enhancement.Superior:
             stripped_uid = RemovePrefix(enhancement.UID, "Attuned_|Superior_")
             FOR each slotted_enh in build:
               IF slotted_enh.UID contains stripped_uid:
                 REJECT: "Superior ATO conflicts with normal"
                 RETURN false

           ELSE (Normal ATO check):
             stripped_uid = RemovePrefix(enhancement.UID, "Attuned_|Superior_")
             FOR each slotted_enh in build:
               IF slotted_enh.UID contains ("Superior_Attuned_" + stripped_uid):
                 REJECT: "Normal ATO conflicts with Superior"
                 RETURN false

3. GLOBAL ENHANCEMENT EFFECTS:
   When calculating build totals:
     FOR each power in build:
       FOR each slot in power.slots:
         FOR each effect in slot.enhancement.effects:
           IF effect.EffectType == Enhancement:
             // This modifies another attribute
             target_type = effect.ETModifies

             IF effect applies globally:
               // Add to build-wide totals (e.g., LotG +Recharge)
               build_totals[target_type] += effect.magnitude
             ELSE:
               // Add to power-specific enhancement
               power.enhancement_values[target_type] += effect.magnitude

4. PROC PROBABILITY (Effect.cs):
   GET proc_chance:
     base_prob = effect.BaseProbability

     IF effect.ProcsPerMinute > 0 AND power exists:
       // PPM calculation
       area_factor = power.AoEModifier * 0.75 + 0.25
       activation_time = MAX(power.ActivatePeriod, ARCANE_TIME)

       probability = (ProcsPerMinute * area_factor * activation_time) / 60.0

       min_chance = ProcsPerMinute * 0.015 + 0.05
       max_chance = 0.9

       RETURN CLAMP(probability, min_chance, max_chance)

     ELSE:
       // Flat percentage
       RETURN base_prob

5. SPECIAL PROC TYPES:
   Performance Shifter +End:
     - Unique: true
     - IsProc: true
     - BaseProbability: 0.20 (20%)
     - Effect: Restore endurance

   Miracle/Numina +Recovery:
     - Unique: true
     - IsProc: false (constant effect)
     - Effect: Continuous recovery bonus

   Proc120 IOs:
     - IsProc: true
     - ProcsPerMinute > 0 OR special flag
     - Internal cooldown: 120 seconds
     - Only one proc per 120s even if slotted multiple times
```

### Key Logic Snippets

**Enhancement Class Properties** (`Core/Enhancement.cs`):
```csharp
public class Enhancement
{
    public bool Unique { get; set; }
    public Enums.eEnhMutex MutExID { get; set; }
    public bool IsProc { get; set; }
    public bool IsScalable { get; set; }

    // Serialization
    public void Read(BinaryReader reader)
    {
        // ... other properties ...
        Unique = reader.ReadBoolean();
        MutExID = (Enums.eEnhMutex)reader.ReadInt32();
        // ... later additions ...
        IsProc = reader.ReadBoolean();
        IsScalable = reader.ReadBoolean();
    }
}
```

**Mutual Exclusion Enum** (`Core/Enums.cs`):
```csharp
public enum eEnhMutex
{
    None,
    Stealth,
    ArchetypeA,
    ArchetypeB,
    ArchetypeC,
    ArchetypeD,
    ArchetypeE,
    ArchetypeF
}
```

**Unique IO Validation** (`Core/Build.cs`):
```csharp
if (enhancement.Unique && Powers[powerIdx].Slots[slotIndex].Enhancement.Enh == iEnh)
{
    if (!silent)
    {
        // Show error: "enhancement.LongName is a unique enhancement.
        // You can only slot one of these across your entire build."
    }
    return false;
}
```

**Stealth IO Mutex** (`Core/Build.cs`):
```csharp
else if (enhancement.MutExID == Enums.eEnhMutex.Stealth)
{
    foreach (var item in MidsContext.Character.PEnhancementsList)
    {
        if (DatabaseAPI.Database.Enhancements[DatabaseAPI.GetEnhancementByUIDName(item)]
            .MutExID == Enums.eEnhMutex.Stealth)
        {
            foundEnh = DatabaseAPI.Database.Enhancements[
                DatabaseAPI.GetEnhancementByUIDName(item)].LongName;
            mutexType = 1;
            foundMutex = true;
        }
    }
}
```

**ATO Superior/Normal Mutex** (`Core/Build.cs`):
```csharp
if (enhancement.Superior && enhancement.MutExID != Enums.eEnhMutex.None)
{
    var nVersion = Regex.Replace(enhancement.UID, @"(Attuned_|Superior_)", "");
    foreach (var item in MidsContext.Character.PEnhancementsList)
    {
        if (item.Contains(nVersion))
        {
            foundEnh = DatabaseAPI.Database.Enhancements[
                DatabaseAPI.GetEnhancementByUIDName(item)].LongName;
            // Conflict found
        }
    }
}
```

**Proc Probability Calculation** (`Core/Base/Data_Classes/Effect.cs`):
```csharp
private float ActualProbability
{
    get
    {
        var probability = BaseProbability;

        // Sometimes BaseProbability sticks at 0.75 when PPM is > 0,
        // preventing PPM calculation
        if (ProcsPerMinute > 0 && power != null)
        {
            var areaFactor = (float)(power.AoEModifier * 0.75 + 0.25);
            var activationTime = Math.Max(power.ActivatePeriod,
                MidsContext.Config.DamageMath.ArcaneActivationTime);

            probability = (float)((ProcsPerMinute * areaFactor * activationTime) / 60.0);

            probability = Math.Max(MinProcChance, Math.Min(MaxProcChance, probability));
        }

        return probability;
    }
}

public float MinProcChance => ProcsPerMinute > 0 ? ProcsPerMinute * 0.015f + 0.05f : 0.05f;
public const float MaxProcChance = 0.9f;
```

## Game Mechanics Context

### Why Special IOs Exist

**Unique IOs** were introduced to prevent overpowered stacking:
- Multiple Performance Shifter +End procs would trivialize endurance management
- Multiple Miracle +Recovery IOs would provide excessive regeneration
- These IOs are intentionally powerful but limited to one per build

**Stealth IOs** grant stealth powers when slotted:
- Celerity in Sprint gives partial invisibility
- Unbounded Leap in Combat Jumping gives stealth
- Only one allowed to prevent full invisibility stacking
- Uses `GrantPower` effect type to add stealth power to character

**Global Recharge IOs** like Luck of the Gambler +7.5%:
- Apply to ALL powers, not just the slotted power
- Stack with set bonuses and other global recharge sources
- Most sought-after IO in the game
- Unlike normal enhancements, work globally via `Enhancement` effect type with `ETModifies = Recharge`

**Archetype Origin Sets** (ATOs):
- Superior versions available at level 50
- Cannot slot both Superior and normal versions
- Superior versions have better values
- Mutex prevents "double-dipping" on set bonuses

### PPM vs Flat Proc Chance

**PPM (Procs Per Minute)**:
- Modern proc system introduced in Issue 24
- Proc chance = (PPM × AreaFactor × ActivationTime) / 60
- AreaFactor prevents abuse in AoE powers: `AoEModifier * 0.75 + 0.25`
- Minimum chance: `PPM * 0.015 + 0.05`
- Maximum chance: 90%
- Benefits slow-recharging, high-damage powers

**Flat Chance**:
- Older proc system
- Fixed percentage (e.g., 20% for Performance Shifter)
- No adjustment for activation time or AoE
- Simpler but can be exploited in fast-activating powers

**Proc120 Special Case**:
- Procs with 120-second internal cooldown
- Can only fire once every 2 minutes
- Even if proc chance is high, cooldown limits frequency
- Prevents spamming powerful procs in fast-recharging powers

### Common Special IOs

**Performance Shifter: Chance for +End**:
- Unique: Can only slot one
- 20% chance to restore endurance
- Most popular unique proc
- Critical for endurance-heavy builds

**Luck of the Gamber: +7.5% Recharge**:
- Not unique (can slot multiple)
- Global recharge bonus
- Applies to all powers
- Standard to slot 5 in a build (expensive!)

**Miracle: +Recovery / Numina's Convalescence: +Regen/+Recovery**:
- Unique IOs with constant effects (not procs)
- Always active when slotted
- Popular in Health auto-power
- Significant QoL improvement

**Stealth IOs**:
- Celerity: Stealth (in Sprint)
- Unbounded Leap: Stealth (in Combat Jumping/Super Jump)
- Winter's Gift: Slow Resistance (includes stealth component)
- Grant invisibility powers via `GrantPower` effect

**Superior ATOs**:
- Each archetype has 2 ATO sets
- Superior versions available at 50
- Cannot mix Superior and normal versions
- Often include archetype-specific procs

### Known Edge Cases

**Stealth Stacking**:
- Only one stealth IO allowed via MutExID
- But stealth powers and pool powers can stack
- Stealth IO + Stealth pool power + Stealth AT power = full invisibility
- MutExID only restricts IO slotting, not power selection

**Global Recharge Math**:
- Global recharge from LotG IOs is additive with set bonuses
- Example: 5× LotG +7.5% = +37.5% recharge
- Combines with set bonuses, Hasten, other global sources
- Applied before ED to power-specific recharge slotting

**ATO Attuned Confusion**:
- ATOs can be attuned (level-scaled) or level-locked
- Superior ATOs are always attuned
- Regex strips "Attuned_" and "Superior_" to find conflicts
- Must handle: "Attuned_Superior_", "Superior_Attuned_", plain UIDs

**Proc120 Not Explicitly Flagged**:
- No `IsProc120` property in Enhancement class
- Determined by effect flags or data configuration
- Must track separately or infer from proc behavior
- Implementation may vary by specific IO

## Python Implementation Guide

### Proposed Architecture

**Location**: `mids_hero_web/calculators/enhancements/`

**Module**: `special_ios.py`

**Classes**:
```python
class SpecialIOValidator:
    """Validates special IO slotting rules"""

    def validate_unique(self, build, enhancement_id):
        """Check if unique IO already slotted"""

    def validate_mutex(self, build, enhancement_id):
        """Check mutual exclusion groups"""

    def validate_stealth(self, build, enhancement_id):
        """Check stealth IO restrictions"""

    def validate_ato(self, build, enhancement_id):
        """Check ATO Superior/Normal conflicts"""

class ProcCalculator:
    """Calculate proc probabilities"""

    def calculate_proc_chance(self, effect, power):
        """Determine proc chance using PPM or flat"""

    def calculate_ppm_chance(self, ppm, power):
        """PPM-based calculation with AoE factor"""

    def get_min_proc_chance(self, ppm):
        """Calculate minimum proc chance"""

class GlobalEffectApplicator:
    """Apply global enhancement effects"""

    def apply_global_recharge(self, build, enhancement):
        """Apply LotG-style global recharge"""

    def apply_stealth_power(self, build, enhancement):
        """Grant stealth power from IO"""
```

### Database Schema

**Enhancement Table Additions**:
```sql
ALTER TABLE enhancements ADD COLUMN is_unique BOOLEAN DEFAULT FALSE;
ALTER TABLE enhancements ADD COLUMN mutex_group VARCHAR(50); -- 'none', 'stealth', 'ato_a', etc.
ALTER TABLE enhancements ADD COLUMN is_proc BOOLEAN DEFAULT FALSE;
ALTER TABLE enhancements ADD COLUMN is_scalable BOOLEAN DEFAULT FALSE;
```

**Enhancement Effects**:
```sql
-- Effects with global flag
ALTER TABLE enhancement_effects ADD COLUMN is_global BOOLEAN DEFAULT FALSE;
ALTER TABLE enhancement_effects ADD COLUMN procs_per_minute FLOAT;
```

### Implementation Notes

**Unique IO Tracking**:
```python
def validate_unique_io(build, enhancement_id):
    """
    Check if unique IO already slotted in build.

    Returns:
        (bool, str): (is_valid, error_message)
    """
    enhancement = db.get_enhancement(enhancement_id)

    if not enhancement.is_unique:
        return True, None

    # Check all slotted enhancements
    slotted = build.get_all_slotted_enhancements()
    if enhancement_id in slotted:
        return False, f"{enhancement.name} is unique and already slotted"

    return True, None
```

**Mutex Group Validation**:
```python
def validate_mutex_group(build, enhancement_id):
    """
    Check mutual exclusion groups (stealth, ATO, etc).

    Returns:
        (bool, str, str): (is_valid, conflicting_io, mutex_type)
    """
    enhancement = db.get_enhancement(enhancement_id)

    if enhancement.mutex_group == 'none':
        return True, None, None

    # Stealth IOs
    if enhancement.mutex_group == 'stealth':
        for slotted in build.get_all_slotted_enhancements():
            slotted_enh = db.get_enhancement(slotted)
            if slotted_enh.mutex_group == 'stealth':
                return False, slotted_enh.name, 'stealth'

    # ATO Superior/Normal
    if enhancement.mutex_group.startswith('ato_'):
        # Strip prefixes and check conflicts
        base_uid = strip_ato_prefixes(enhancement.uid)
        for slotted in build.get_all_slotted_enhancements():
            slotted_uid = strip_ato_prefixes(db.get_enhancement(slotted).uid)
            if base_uid == slotted_uid and slotted != enhancement_id:
                return False, db.get_enhancement(slotted).name, 'ato'

    return True, None, None
```

**PPM Proc Calculation**:
```python
def calculate_ppm_proc_chance(ppm, power):
    """
    Calculate proc chance using PPM formula.

    Args:
        ppm: Procs per minute value
        power: Power being slotted into

    Returns:
        float: Proc chance (0.0 to 0.9)
    """
    # Area factor reduces proc chance in AoE
    area_factor = power.aoe_modifier * 0.75 + 0.25

    # Activation time (with arcane time minimum)
    activation_time = max(power.activation_time, ARCANE_TIME)

    # PPM formula
    probability = (ppm * area_factor * activation_time) / 60.0

    # Clamp to min/max
    min_chance = ppm * 0.015 + 0.05
    max_chance = 0.9

    return max(min_chance, min(max_chance, probability))
```

**Global Recharge Application**:
```python
def apply_global_recharge(build, enhancement):
    """
    Apply global recharge bonus (e.g., LotG +7.5%).

    Global recharge affects ALL powers, not just slotted power.
    """
    for effect in enhancement.effects:
        if effect.type == 'enhancement' and effect.modifies == 'recharge':
            if effect.is_global:
                # Add to build-wide global recharge
                build.global_recharge += effect.magnitude
                # This will be applied to all powers in build totals
```

### Edge Cases to Test

1. **Multiple Unique IOs**:
   - Attempt to slot two Performance Shifter +End procs
   - Should reject with clear error message

2. **Stealth IO Conflicts**:
   - Slot Celerity stealth, then try Unbounded Leap stealth
   - Should reject due to mutex

3. **ATO Superior/Normal**:
   - Slot normal Scrapper's Strike, then try Superior Scrapper's Strike
   - Test with various prefix combinations: "Attuned_Superior_", etc.

4. **Global Recharge Stacking**:
   - Slot 5× LotG +7.5% Recharge
   - Verify total global recharge = +37.5%
   - Ensure applies to all powers

5. **PPM in Fast vs Slow Powers**:
   - 3.5 PPM proc in 1-second activation power
   - Same proc in 10-second activation power
   - Verify different proc chances

6. **PPM Min/Max Clamping**:
   - High PPM in very slow power → should cap at 90%
   - Low PPM in very fast power → should respect minimum

7. **AoE Factor**:
   - PPM proc in single-target power (AoE modifier = 1.0)
   - Same proc in large AoE (AoE modifier = 2.5+)
   - Verify reduced chance in AoE

### Validation Strategy

**Test Data Sources**:
- MidsReborn database exports (enhancement definitions)
- Known IO behaviors (LotG, Performance Shifter, etc.)
- Forum posts documenting proc chances
- In-game testing data

**Unit Tests**:
```python
def test_unique_io_validation():
    # Create build with Performance Shifter
    # Attempt to slot second one
    # Assert rejection

def test_lotg_global_recharge():
    # Slot 5× LotG +7.5%
    # Calculate build totals
    # Assert global_recharge == 0.375

def test_ppm_proc_calculation():
    # Known PPM value and power stats
    # Calculate proc chance
    # Compare to MidsReborn output

def test_stealth_mutex():
    # Slot stealth IO
    # Attempt to slot another
    # Assert rejection
```

**Integration Tests**:
- Import full build with special IOs from MidsReborn
- Validate all special IO rules applied
- Compare calculated totals with MidsReborn totals

### Performance Considerations

**Validation Efficiency**:
- Cache slotted enhancement list per build
- Don't re-scan entire build for every validation
- Use set membership for O(1) unique checks

**Global Effect Application**:
- Calculate global recharge once, store in build totals
- Don't recalculate for every power display
- Invalidate cache when enhancement changes

**Proc Chance Caching**:
- Proc chances don't change unless power or enhancement changes
- Cache calculated proc chances per (power, enhancement) pair
- Recalculate only on modification

## References

### Related Calculation Specs
- **Spec 01**: Power Effects Core (Effect types, GrantPower)
- **Spec 07**: Power Recharge Modifiers (global recharge interaction)
- **Spec 10**: Enhancement Schedules (how enhancement values apply)
- **Spec 11**: Enhancement Slotting (basic slotting mechanics)
- **Spec 12**: Enhancement IO Procs (general proc mechanics)
- **Spec 13**: Enhancement Set Bonuses (Rule of 5 for LotG stacking)

### MidsReborn Code References
- `Core/Enhancement.cs`: Enhancement class definition, properties
- `Core/Build.cs`: Unique and mutex validation logic
- `Core/Enums.cs`: eEnhMutex enumeration
- `Core/Base/Data_Classes/Effect.cs`: Proc probability calculation
- `Core/Base/Data_Classes/Power.cs`: ApplyGrantPowerEffects() for stealth IOs

### External Resources
- **City of Heroes Wiki**: Enhancement sets, special IOs
- **Homecoming Forums**: PPM formula discussions
- **ParagonWiki**: Historical IO mechanics
- **MidsReborn GitHub Issues**: Special IO bugs and behaviors

### Known Issues
- ATO prefix stripping can be fragile with various combinations
- Proc120 not explicitly flagged, must infer from data
- Stealth IO grants may need GrantPower implementation
- Global effects need careful ordering with set bonuses

---

**Document Status**: 🟡 Breadth Complete - High-level spec with locations, pseudocode, game context
**Next Steps**: Add detailed C# analysis, comprehensive Python test cases for depth completion
**Related Work**: Depends on procs (spec 12), set bonuses (spec 13), slotting validation (spec 11)
