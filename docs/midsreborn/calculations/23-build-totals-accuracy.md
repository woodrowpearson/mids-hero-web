# Build Totals - Accuracy/ToHit

## Overview
- **Purpose**: Calculate global accuracy (multiplicative) and tohit (additive) bonuses from set bonuses, Incarnate abilities, and special IOs that apply to all powers in a build
- **Used By**: Power accuracy calculations (Spec 08), build statistics display, totals window, combat effectiveness analysis
- **Complexity**: Simple
- **Priority**: Critical
- **Status**: 🟢 Depth Complete

## MidsReborn Implementation

### Primary Location
- **File**: `clsToonX.cs`
- **Method**: `GenerateBuildBuffs()` - Aggregates global accuracy/tohit from all sources
- **Key Totals Assignment**: `CalcStatTotals()` - Lines aggregating BuffAcc and BuffToHit
- **Related Files**:
  - `Core/Base/Data_Classes/Character.cs` - `TotalStatistics` class with `BuffAcc` and `BuffToHit` properties
  - `Core/Statistics.cs` - `BuffAccuracy` and `BuffToHit` properties for display (multiplies by 100 for percentage)
  - `Forms/WindowMenuItems/frmTotals.cs` - Displays accuracy and tohit in totals window with explanatory tooltips
  - `Forms/WindowMenuItems/frmTotalsV2.cs` - Modern totals display
  - `Core/Enums.cs` - `eStatType.BuffAcc` enum value

### Critical Distinction: Accuracy vs ToHit

**CRITICAL DIFFERENCE** that defines build optimization strategy:

**Accuracy (Multiplicative Buff)**:
- Stored in: `Totals.BuffAcc` (as decimal, e.g., 0.09 = 9%)
- Source: `_selfEnhance.Effect[(int)Enums.eStatType.BuffAcc]` + `_selfBuffs.Effect[(int)Enums.eStatType.BuffAcc]`
- Comes from:
  - Enhancement set bonuses (e.g., "3.13% Accuracy")
  - Some Incarnate abilities
- Effect: Multiplies the final accuracy calculation
- Applied in power calculation as: `(1 + enhancement_accuracy + global_accuracy_buff)`
- Variable: `nAcc` in `GBPA_Pass4_ApplyAccuracy()`
- Display: Percentage (e.g., "9.00%" in totals window)
- Tooltip: "This effect increases the accuracy of all your powers. Accuracy buffs are usually applied as invention set bonuses."

**ToHit (Additive Buff)**:
- Stored in: `Totals.BuffToHit` (as decimal, e.g., 0.20 = 20%)
- Source: `_selfBuffs.Effect[(int)Enums.eStatType.ToHit]`
- Comes from:
  - Power buffs (Build Up, Aim, Focused Accuracy)
  - Team buffs (Tactics, Vengeance)
  - Special IOs (Kismet +ToHit IO grants +6% tohit)
  - Enhancement set bonuses (e.g., "3% ToHit")
  - Some Incarnate abilities
- Effect: Adds to hit chance after accuracy multiplier
- Applied in power calculation as: `* (ScalingToHit + global_tohit_buff)`
- Variable: `nToHit` in `GBPA_Pass4_ApplyAccuracy()`
- Display: Percentage (e.g., "7.00%" in totals window)
- Tooltip: "This effect increases the accuracy of all your powers. ToHit values are added together before being multiplied by Accuracy."

### Key Data Structures

**TotalStatistics Class** (`Core/Base/Data_Classes/Character.cs`):
```csharp
public class TotalStatistics
{
    // ... other stats ...
    public float BuffAcc { get; set; }      // Global accuracy (multiplicative)
    public float BuffToHit { get; set; }    // Global tohit (additive)
    // ... other stats ...
}
```

**Statistics Display Properties** (`Core/Statistics.cs`):
```csharp
public float BuffToHit => _character.Totals.BuffToHit * 100f;     // Convert to percentage
public float BuffAccuracy => _character.Totals.BuffAcc * 100f;    // Convert to percentage
```

## High-Level Algorithm

```
Build Totals - Accuracy/ToHit Aggregation Process:

1. Initialize Totals:
   Totals.BuffAcc = 0.0
   Totals.BuffToHit = 0.0

2. Aggregate Accuracy Bonuses (GenerateBuildBuffs):
   For each power in build:
     For each slotted enhancement in power:
       For each effect in enhancement:
         If effect.EffectType != ResEffect AND
            effect.ETModifies == Accuracy AND
            NOT enhancement_pass:
           // This is a global accuracy bonus (set bonus or special IO)
           nBuffs.Effect[(int)eStatType.BuffAcc] += effect.magnitude

   // Also includes enhancements that directly grant global accuracy
   For each enhancement effect modifying accuracy:
     If NOT in power context (global effect):
       _selfEnhance.Effect[(int)eStatType.BuffAcc] += effect.magnitude

3. Aggregate ToHit Bonuses (GenerateBuildBuffs):
   For each active power in build:
     For each effect in power:
       If effect.EffectType == ToHitBuff:
         _selfBuffs.Effect[(int)eStatType.ToHit] += effect.magnitude

   For each slotted enhancement:
     For each effect in enhancement:
       If effect grants global tohit:
         _selfBuffs.Effect[(int)eStatType.ToHit] += effect.magnitude

4. Calculate Final Totals (CalcStatTotals):
   // Combine enhancement-based accuracy and buff-based accuracy
   Totals.BuffAcc = _selfEnhance.Effect[(int)eStatType.BuffAcc] +
                    _selfBuffs.Effect[(int)eStatType.BuffAcc]

   // ToHit only comes from buffs
   Totals.BuffToHit = _selfBuffs.Effect[(int)eStatType.ToHit]

5. Display Conversion:
   // For display in UI (Statistics.cs)
   BuffAccuracy_display = Totals.BuffAcc * 100  // e.g., 0.09 → 9.00%
   BuffToHit_display = Totals.BuffToHit * 100   // e.g., 0.20 → 20.00%

6. Application to Powers (GBPA_Pass4_ApplyAccuracy):
   // When calculating individual power accuracy
   nAcc = power.IgnoreBuff(Accuracy) ? 0 : Totals.BuffAcc
   nToHit = power.IgnoreBuff(ToHit) ? 0 : Totals.BuffToHit

   // Final accuracy formula (multiplicative then additive)
   powerBuffed.Accuracy = powerBuffed.Accuracy *
                          (1 + enhancement_accuracy + nAcc) *
                          (ScalingToHit + nToHit)

   // Accuracy multiplier without base tohit scaling
   powerBuffed.AccuracyMult = powerBuffed.Accuracy *
                              (1 + enhancement_accuracy + nAcc)

7. No Hard Caps:
   // Unlike resistance and defense, accuracy/tohit have no hard caps in aggregation
   // Hit chance is capped at 5%-95% in game, but that's applied per-attack
   // Enhancement Diversification applies to slotted accuracy enhancements,
   // but global accuracy bonuses are NOT subject to ED
```

### Key Calculation Code

**Aggregating Global Accuracy** (`clsToonX.cs:GenerateBuildBuffs`):
```csharp
// When processing enhancement effects
if (effect.EffectType != Enums.eEffectType.ResEffect &
    effect.ETModifies == Enums.eEffectType.Accuracy &
    !enhancementPass)
{
    nBuffs.Effect[(int)Enums.eStatType.BuffAcc] += shortFx.Value[shortFxIdx];
}
```

**Calculating Final Totals** (`clsToonX.cs:CalcStatTotals`):
```csharp
Totals.BuffAcc = _selfEnhance.Effect[(int)Enums.eStatType.BuffAcc] +
                 _selfBuffs.Effect[(int)Enums.eStatType.BuffAcc];
Totals.BuffToHit = _selfBuffs.Effect[(int)Enums.eStatType.ToHit];
```

**Display in Totals Window** (`Forms/WindowMenuItems/frmTotals.cs`):
```csharp
// ToHit display
graphToHit.AddItem(
    $"ToHit|{displayStats.BuffToHit:##0.##}%",
    Math.Max(0, displayStats.BuffToHit),
    0,
    "This effect increases the accuracy of all your powers.\r\nToHit values are added together before being multiplied by Accuracy."
);

// Accuracy display
graphAcc.AddItem(
    $"Accuracy|{displayStats.BuffAccuracy:##0.##}%",
    Math.Max(0, displayStats.BuffAccuracy),
    0,
    "This effect increases the accuracy of all your powers.\r\nAccuracy buffs are usually applied as invention set bonuses."
);
```

**Application to Power** (`clsToonX.cs:GBPA_Pass4_ApplyAccuracy`):
```csharp
var nToHit = !powerMath.IgnoreBuff(Enums.eEnhance.ToHit) ?
             0 : _selfBuffs.Effect[(int)Enums.eStatType.ToHit];
var nAcc = !powerMath.IgnoreBuff(Enums.eEnhance.Accuracy) ?
           0 : _selfBuffs.Effect[(int)Enums.eStatType.BuffAcc];

powerBuffed.Accuracy = powerBuffed.Accuracy *
                       (1 + powerMath.Accuracy + nAcc) *
                       (MidsContext.Config.ScalingToHit + nToHit);

powerBuffed.AccuracyMult = powerBuffed.Accuracy *
                           (1 + powerMath.Accuracy + nAcc);
```

## Game Mechanics Context

**Why This Exists:**

The dual accuracy/tohit system in City of Heroes creates strategic depth in build planning:

1. **Multiplicative vs Additive**: The key distinction between accuracy (multiplicative) and tohit (additive) means they have different value in different scenarios:
   - **Accuracy** is more valuable against high-defense enemies because it multiplies the entire hit calculation
   - **ToHit** is more valuable when you need to hit the 95% cap because it adds directly to hit chance
   - Example: Against 45% defense enemy with 75% base tohit:
     - Without buffs: 75% - 45% = 30% hit chance
     - With +9% accuracy: 81.75% - 45% = 36.75% hit chance (6.75% gain)
     - With +9% tohit: 84% - 45% = 39% hit chance (9% gain)

2. **No Enhancement Diversification**: Unlike slotted accuracy enhancements (which are subject to ED), global accuracy and tohit bonuses are NOT diminished. This makes set bonuses extremely valuable - you can stack them without penalty.

3. **Set Bonus Stacking**: Most accuracy set bonuses are unique per set, but you can slot multiple different sets to stack accuracy bonuses. Common strategy is to get 5-9% global accuracy from set bonuses.

4. **Build Strategy Implications**:
   - **Soft-capped defense builds** (45% def) benefit more from global accuracy for offense since enemies will have high defense
   - **Offensive builds** stack accuracy to maintain hit rate against +4 enemies with high defense
   - **Global tohit** is limited but valuable - Tactics (5-7%), Kismet IO (6%), and a few set bonuses

**Historical Context:**

- **Launch (2004)**: Original system had accuracy but tohit was less common. Most accuracy came from slotting.

- **Issue 5 (2005)**: Enhancement Diversification introduced. Slotting 3 accuracy SOs became standard (95% bonus after ED). This made global accuracy bonuses more valuable since they bypassed ED.

- **Issue 7 (2006)**: Invention sets introduced with accuracy bonuses. Build planners discovered stacking accuracy set bonuses was more effective than over-slotting accuracy in powers.

- **Issue 9 (2007)**: Kismet +ToHit IO introduced. The "Kismet: Accuracy/ToHit/+ToHit" unique proc grants +6% tohit (additive), which matches its name. It became a staple of builds providing valuable global tohit.

- **Issue 13 (2008)**: More set bonuses with accuracy/tohit introduced. High-end builds could reach 15-20% global accuracy.

- **Homecoming (2019+)**: Meta shifted to softcap defense on many ATs. Global accuracy became even more valuable for maintaining offense while investing heavily in defense.

**Known Quirks:**

1. **Kismet IO**: The "Kismet: Accuracy/ToHit/+ToHit" proc grants +6% tohit (additive), which correctly matches its name. It provides valuable global tohit that stacks with other sources.

2. **No Hard Cap on Aggregation**: Unlike defense (capped at 45% for most ATs) and resistance (capped at 75-90%), there's no cap on how much global accuracy/tohit you can aggregate. However, final hit chance is still capped at 5%-95%.

3. **Ignores Enhancement Diversification**: Global accuracy bonuses from sets completely bypass ED. A power with 95% accuracy from slotted enhancements (3 SOs) AND 9% global accuracy gets the full benefit of both (not subject to ED curve).

4. **Different Sources Mix Differently**:
   - Slotted accuracy enhancements: Subject to ED, multiplies base accuracy
   - Global accuracy (set bonuses): Not subject to ED, multiplies base accuracy
   - ToHit buffs (powers): Adds to base tohit, can exceed 100% before enemy defense subtraction
   - Both accuracy and tohit bonuses combine additively within their own category

5. **Power-Specific Ignore Flags**: Some powers ignore accuracy/tohit buffs (e.g., auto-hit powers, certain pet summons). These use `Power.IgnoreBuff(Accuracy)` or `Power.IgnoreBuff(ToHit)` flags.

6. **Temporary Buffs vs Permanent**: ToHit bonuses are typically temporary (Build Up lasts 10s, Tactics requires endurance), while accuracy bonuses from sets are permanent passive bonuses.

7. **Display Can Be Misleading**: Totals window shows global bonuses, but actual hit chance depends on enemy level (ScalingToHit) and enemy defense. A displayed "109% accuracy" doesn't mean 109% hit chance - it's the multiplier applied to base tohit.

8. **Order of Operations Matters**: The formula is `base_accuracy * (1 + slotted + global_accuracy) * (base_tohit + global_tohit)`. This means tohit benefits from accuracy multiplication, making accuracy bonuses generally more valuable.

9. **Rule of 5 Does NOT Apply**: Unlike most set bonuses, accuracy bonuses from different sets stack without the Rule of 5 limitation. Each set's accuracy bonus applies independently. The Rule of 5 only applies to *identical* bonuses from *identical* sets.

10. **PvP vs PvE Values**: In PvP, accuracy calculations use different diminishing returns. MidsReborn doesn't distinguish between PvP and PvE accuracy display, showing PvE values.

## Algorithm Pseudocode

```
FUNCTION calculate_build_accuracy_totals(build) -> GlobalAccuracyTotals:
    """
    Aggregate global accuracy and tohit from all sources in a build.

    Key Distinction:
    - Accuracy (multiplicative): Affects the accuracy multiplier, bypasses ED
    - ToHit (additive): Adds directly to base tohit before enemy defense

    Args:
        build: Build object containing powers, enhancements, set bonuses, incarnates

    Returns:
        GlobalAccuracyTotals with accuracy, tohit, and detailed contributions
    """

    # Initialize accumulators
    accuracy_total: float = 0.0
    tohit_total: float = 0.0
    accuracy_contributions: List[AccuracyContribution] = []
    tohit_contributions: List[AccuracyContribution] = []

    # Variables mirror MidsReborn's _selfEnhance.Effect and _selfBuffs.Effect
    # Map to clsToonX.cs lines 764, 767
    enhance_accuracy: float = 0.0  # _selfEnhance.Effect[(int)eStatType.BuffAcc]
    buff_accuracy: float = 0.0     # _selfBuffs.Effect[(int)eStatType.BuffAcc]
    buff_tohit: float = 0.0        # _selfBuffs.Effect[(int)eStatType.ToHit]


    # STEP 1: Aggregate Accuracy from Set Bonuses
    # Set bonuses are the primary source of global accuracy
    FOR EACH set_bonus IN build.active_set_bonuses:
        IF set_bonus.effect_type == "accuracy":
            magnitude = set_bonus.magnitude  # e.g., 0.09 for 9%

            # Accumulate (set bonuses stack additively)
            buff_accuracy += magnitude

            # Track for detailed breakdown
            accuracy_contributions.append(AccuracyContribution(
                source_name=set_bonus.set_name,  # e.g., "Thunderstrike"
                source_type=AccuracySource.SET_BONUS,
                is_accuracy=True,
                magnitude=magnitude
            ))

        ELSE IF set_bonus.effect_type == "tohit":
            magnitude = set_bonus.magnitude  # e.g., 0.03 for 3%

            # Accumulate tohit
            buff_tohit += magnitude

            # Track for detailed breakdown
            tohit_contributions.append(AccuracyContribution(
                source_name=set_bonus.set_name,
                source_type=AccuracySource.SET_BONUS,
                is_accuracy=False,
                magnitude=magnitude
            ))


    # STEP 2: Aggregate Accuracy/ToHit from Special IOs
    # Special IOs like Kismet +ToHit grant global bonuses
    FOR EACH power IN build.powers:
        FOR EACH slot IN power.slots:
            IF slot.enhancement IS NOT NULL:
                enhancement = slot.enhancement

                # Check for global effects
                FOR EACH effect IN enhancement.effects:
                    # Check if this is a global accuracy effect
                    # Corresponds to clsToonX.cs lines 660-662
                    IF (effect.effect_type != ResEffect AND
                        effect.modifies == Accuracy AND
                        NOT is_enhancement_pass):

                        magnitude = effect.magnitude

                        # Global accuracy IOs
                        enhance_accuracy += magnitude

                        accuracy_contributions.append(AccuracyContribution(
                            source_name=enhancement.name,
                            source_type=AccuracySource.SPECIAL_IO,
                            is_accuracy=True,
                            magnitude=magnitude
                        ))

                    # Check for global tohit effects (including Kismet)
                    ELSE IF effect.effect_type == ToHitBuff:
                        magnitude = effect.magnitude

                        buff_tohit += magnitude

                        tohit_contributions.append(AccuracyContribution(
                            source_name=enhancement.name,
                            source_type=AccuracySource.SPECIAL_IO,
                            is_accuracy=False,
                            magnitude=magnitude
                        ))


    # STEP 3: Aggregate ToHit from Power Buffs
    # Active powers like Tactics, Build Up, Aim grant tohit
    FOR EACH power IN build.powers:
        IF power.is_active:  # Toggle ON or auto power
            FOR EACH effect IN power.effects:
                IF effect.effect_type == ToHitBuff:
                    magnitude = effect.magnitude  # e.g., 0.07 for Tactics

                    buff_tohit += magnitude

                    tohit_contributions.append(AccuracyContribution(
                        source_name=power.name,
                        source_type=AccuracySource.POWER_BUFF,
                        is_accuracy=False,
                        magnitude=magnitude,
                        power_name=power.name
                    ))

                # Rare: Some powers grant accuracy buffs
                ELSE IF (effect.effect_type != ResEffect AND
                         effect.modifies == Accuracy):
                    magnitude = effect.magnitude

                    buff_accuracy += magnitude

                    accuracy_contributions.append(AccuracyContribution(
                        source_name=power.name,
                        source_type=AccuracySource.POWER_BUFF,
                        is_accuracy=True,
                        magnitude=magnitude,
                        power_name=power.name
                    ))


    # STEP 4: Aggregate Accuracy/ToHit from Incarnate Powers
    # Incarnate slots (especially Alpha) can grant accuracy
    FOR EACH incarnate_slot IN build.incarnate_slots:
        IF incarnate_slot.has_power_selected:
            incarnate_power = incarnate_slot.selected_power

            FOR EACH effect IN incarnate_power.effects:
                IF effect.effect_type == AccuracyBuff:
                    magnitude = effect.magnitude  # e.g., 0.05 for Alpha

                    buff_accuracy += magnitude

                    accuracy_contributions.append(AccuracyContribution(
                        source_name=f"{incarnate_slot.name} - {incarnate_power.name}",
                        source_type=AccuracySource.INCARNATE,
                        is_accuracy=True,
                        magnitude=magnitude
                    ))

                ELSE IF effect.effect_type == ToHitBuff:
                    magnitude = effect.magnitude

                    buff_tohit += magnitude

                    tohit_contributions.append(AccuracyContribution(
                        source_name=f"{incarnate_slot.name} - {incarnate_power.name}",
                        source_type=AccuracySource.INCARNATE,
                        is_accuracy=False,
                        magnitude=magnitude
                    ))


    # STEP 5: Calculate Final Totals
    # Maps to clsToonX.cs lines 764, 767
    # Totals.BuffAcc = _selfEnhance.Effect[BuffAcc] + _selfBuffs.Effect[BuffAcc]
    # Totals.BuffToHit = _selfBuffs.Effect[ToHit]

    accuracy_total = enhance_accuracy + buff_accuracy
    tohit_total = buff_tohit

    # No caps or diminishing returns!
    # Unlike defense (45% soft cap) or resistance (75-90% hard cap),
    # accuracy and tohit have no aggregation limits
    # Final hit chance is capped at 5%-95% per attack, but totals are uncapped


    # STEP 6: Return Results
    RETURN GlobalAccuracyTotals(
        accuracy=accuracy_total,
        tohit=tohit_total,
        accuracy_contributions=accuracy_contributions,
        tohit_contributions=tohit_contributions
    )


FUNCTION get_accuracy_for_power(global_totals, power) -> float:
    """
    Get accuracy bonus for specific power, respecting ignore flags.

    Some powers ignore global accuracy buffs (auto-hit powers, pet summons).
    Maps to clsToonX.cs lines 1995-1996 (GBPA_Pass6_MultiplyPostBuff).

    Args:
        global_totals: GlobalAccuracyTotals from calculate_build_accuracy_totals
        power: Power object to check

    Returns:
        Accuracy bonus to apply (0.0 if power ignores buffs)
    """

    # Check if power ignores accuracy buffs
    # Corresponds to: !powerMath.IgnoreBuff(Enums.eEnhance.Accuracy)
    IF power.ignores_buff(BuffType.ACCURACY):
        RETURN 0.0
    ELSE:
        RETURN global_totals.accuracy


FUNCTION get_tohit_for_power(global_totals, power) -> float:
    """
    Get tohit bonus for specific power, respecting ignore flags.

    Maps to clsToonX.cs line 1995.

    Args:
        global_totals: GlobalAccuracyTotals from calculate_build_accuracy_totals
        power: Power object to check

    Returns:
        ToHit bonus to apply (0.0 if power ignores buffs)
    """

    # Check if power ignores tohit buffs
    # Corresponds to: !powerMath.IgnoreBuff(Enums.eEnhance.ToHit)
    IF power.ignores_buff(BuffType.TOHIT):
        RETURN 0.0
    ELSE:
        RETURN global_totals.tohit


FUNCTION format_accuracy_breakdown(global_totals) -> str:
    """
    Format detailed breakdown for tooltip display.
    Shows all sources contributing to accuracy and tohit totals.
    """

    lines = []

    # Accuracy section
    lines.append(f"Total Accuracy: {global_totals.accuracy * 100:.2f}%")

    IF global_totals.accuracy_contributions.is_empty():
        lines.append("  (No accuracy bonuses)")
    ELSE:
        # Group by source type
        FOR contrib IN global_totals.accuracy_contributions:
            lines.append(f"  {contrib.source_name}: +{contrib.magnitude * 100:.2f}%")

    lines.append("")  # Blank line separator

    # ToHit section
    lines.append(f"Total ToHit: {global_totals.tohit * 100:.2f}%")

    IF global_totals.tohit_contributions.is_empty():
        lines.append("  (No tohit bonuses)")
    ELSE:
        FOR contrib IN global_totals.tohit_contributions:
            power_info = f" ({contrib.power_name})" IF contrib.power_name ELSE ""
            lines.append(f"  {contrib.source_name}{power_info}: +{contrib.magnitude * 100:.2f}%")

    RETURN join(lines, "\n")
```

### Edge Cases

1. **Kismet IO**:
   - Enhancement named "Kismet: Accuracy/ToHit/+ToHit"
   - Grants **tohit** (additive), as the name suggests
   - Treated as special IO tohit source
   - Value: +6% tohit (0.06)

2. **Power Ignore Flags**:
   - Auto-hit powers: `power.IgnoreBuff(Accuracy) == True`
   - Pet summons: Often ignore accuracy buffs
   - Check before applying global totals to power calculation
   - Return 0.0 instead of global total

3. **No Enhancement Diversification**:
   - Slotted accuracy enhancements: Subject to ED (~95% from 3 SOs)
   - Global accuracy bonuses: **NOT subject to ED**
   - Both combine additively in final formula
   - Full benefit of both: (1 + 0.95_slotted + 0.09_global)

4. **Temporary vs Permanent**:
   - Accuracy from sets/IOs: Permanent, always active
   - ToHit from powers: May be temporary (Build Up: 10s duration)
   - ToHit from toggles: Active only while toggle is on (Tactics)
   - Build planner typically assumes toggles ON for totals display

5. **Zero Base Case**:
   - Build with no accuracy/tohit bonuses: Both totals = 0.0
   - Still functional - powers use only slotted accuracy
   - Common for early-level builds without sets

6. **Very High Values**:
   - No caps during aggregation (unlike defense at 45% or resistance at 75-90%)
   - Theoretically could exceed 100% accuracy bonus
   - Practical limit: ~15-20% accuracy from sets in high-end builds
   - Final hit chance capped at 95% per attack (game engine)

7. **Mixed Sources**:
   - Set bonuses (5 different sets): Stack additively within accuracy category
   - Special IOs (Kismet): Adds to tohit total
   - Power buffs (Tactics): Adds to tohit total
   - All accuracy sources sum together, all tohit sources sum together
   - Categories remain separate (not mixed)

8. **Incarnate Shift Interaction**:
   - Incarnate level shifts don't directly affect accuracy totals
   - Level shifts modify effective ScalingToHit (base tohit vs enemy level)
   - Accuracy totals remain the same regardless of shifts
   - But final hit chance improved due to better tohit against lower-relative enemies

## C# Implementation Reference

### File Locations

**Primary Files**:
- `/Users/w/code/mids-hero-web/external/dev/MidsReborn/MidsReborn/clsToonX.cs`
  - Lines 660-662: Accuracy aggregation from enhancements
  - Line 764: Final BuffAcc calculation
  - Line 767: Final BuffToHit calculation
  - Lines 1995-1999: Application to individual powers

- `/Users/w/code/mids-hero-web/external/dev/MidsReborn/MidsReborn/Core/Base/Data_Classes/Character.cs`
  - Lines 1904-1905: TotalStatistics.BuffAcc and BuffToHit properties
  - Lines 1934-1935: Initialization to 0.0

- `/Users/w/code/mids-hero-web/external/dev/MidsReborn/MidsReborn/Core/Statistics.cs`
  - Line 61: BuffToHit display property (multiply by 100 for percentage)
  - Line 63: BuffAccuracy display property (multiply by 100 for percentage)

- `/Users/w/code/mids-hero-web/external/dev/MidsReborn/MidsReborn/Forms/WindowMenuItems/frmTotals.cs`
  - Line 644: ToHit display in totals window
  - Line 649: Accuracy display in totals window

### Key Code Snippets

**TotalStatistics Class Definition** (Character.cs, lines 1904-1905):
```csharp
public class TotalStatistics
{
    // ... other properties ...
    public float BuffAcc { get; set; }      // Global accuracy bonus (e.g., 0.09 = 9%)
    public float BuffToHit { get; set; }    // Global tohit bonus (e.g., 0.20 = 20%)
    // ... other properties ...
}
```

**Initialization** (Character.cs, lines 1934-1935):
```csharp
public void Init(bool fullReset = true)
{
    // ... other initializations ...
    BuffAcc = 0;
    BuffToHit = 0;
    // ... other initializations ...
}
```

**Accuracy Aggregation from Enhancements** (clsToonX.cs, lines 660-662):
```csharp
// Inside enhancement processing loop
if (effect.EffectType != Enums.eEffectType.ResEffect &
    effect.ETModifies == Enums.eEffectType.Accuracy &
    !enhancementPass)
{
    // This is a global accuracy bonus (set bonus or special IO)
    nBuffs.Effect[(int)Enums.eStatType.BuffAcc] += shortFx.Value[shortFxIdx];
}
```

**Final Totals Calculation** (clsToonX.cs, lines 764, 767):
```csharp
// Combine enhancement-based and buff-based accuracy
Totals.BuffAcc = _selfEnhance.Effect[(int)Enums.eStatType.BuffAcc] +
                 _selfBuffs.Effect[(int)Enums.eStatType.BuffAcc];

// ToHit only comes from buffs
Totals.BuffToHit = _selfBuffs.Effect[(int)Enums.eStatType.ToHit];
```

**Display Properties** (Statistics.cs, lines 61, 63):
```csharp
// Convert from decimal (0.09) to percentage (9.0) for display
public float BuffToHit => _character.Totals.BuffToHit * 100f;
public float BuffAccuracy => _character.Totals.BuffAcc * 100f;
```

**Application to Individual Powers** (clsToonX.cs, lines 1995-1999):
```csharp
// GBPA_Pass6_MultiplyPostBuff method
// Check if power ignores tohit/accuracy buffs
var nToHit = !powerMath.IgnoreBuff(Enums.eEnhance.ToHit) ?
             0 : _selfBuffs.Effect[(int)Enums.eStatType.ToHit];
var nAcc = !powerMath.IgnoreBuff(Enums.eEnhance.Accuracy) ?
           0 : _selfBuffs.Effect[(int)Enums.eStatType.BuffAcc];

// Apply to power accuracy
// Formula: base * (1 + slotted + global_acc) * (base_tohit + global_tohit)
powerBuffed.Accuracy = powerBuffed.Accuracy *
                       (1 + powerMath.Accuracy + nAcc) *
                       (MidsContext.Config.ScalingToHit + nToHit);

// Accuracy multiplier without tohit scaling (for display)
powerBuffed.AccuracyMult = powerBuffed.Accuracy * (1 + powerMath.Accuracy + nAcc);
```

**Totals Window Display** (frmTotals.cs, lines 644, 649):
```csharp
// ToHit graph
graphToHit.AddItem(
    $"ToHit|{displayStats.BuffToHit:##0.##}%",
    Math.Max(0, displayStats.BuffToHit),
    0,
    "This effect increases the accuracy of all your powers.\r\n" +
    "ToHit values are added together before being multiplied by Accuracy."
);

// Accuracy graph
graphAcc.AddItem(
    $"Accuracy|{displayStats.BuffAccuracy:##0.##}%",
    Math.Max(0, displayStats.BuffAccuracy),
    0,
    "This effect increases the accuracy of all your powers.\r\n" +
    "Accuracy buffs are usually applied as invention set bonuses."
);
```

### Constants

**No Constants for Caps**:
- Unlike defense (Statistics.MaxDefenseDebuffRes = 95f) or resistance caps, there are no caps for accuracy/tohit aggregation
- Values stored as decimals (0.09 = 9%, not 9.0)
- Display multiplies by 100 for percentage representation

**Related Constants** (used in power calculations, not aggregation):
- `ServerData.BaseToHit = 0.75` (75% base tohit vs even-level enemies)
- `MidsContext.Config.ScalingToHit` (varies by enemy level: 0.75, 0.65, 0.56, 0.48, 0.39)

## Database Schema

### Tables

```sql
-- Build accuracy totals storage
CREATE TABLE build_totals_accuracy (
    build_id INTEGER NOT NULL,
    accuracy_total NUMERIC(10, 6) NOT NULL DEFAULT 0.0,  -- Total global accuracy (e.g., 0.090000 = 9%)
    tohit_total NUMERIC(10, 6) NOT NULL DEFAULT 0.0,     -- Total global tohit (e.g., 0.070000 = 7%)
    calculated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (build_id),
    FOREIGN KEY (build_id) REFERENCES builds(id) ON DELETE CASCADE
);

CREATE INDEX idx_build_totals_accuracy_build ON build_totals_accuracy(build_id);

COMMENT ON TABLE build_totals_accuracy IS
'Stores aggregated global accuracy and tohit bonuses for builds. Maps to MidsReborn Totals.BuffAcc and Totals.BuffToHit.';

COMMENT ON COLUMN build_totals_accuracy.accuracy_total IS
'Total global accuracy bonus (multiplicative). Sum of all set bonuses and incarnate accuracy. Stored as decimal (0.09 = 9%).';

COMMENT ON COLUMN build_totals_accuracy.tohit_total IS
'Total global tohit bonus (additive). Sum of all power buffs (Tactics, Build Up), special IOs (Kismet), set bonuses, and incarnate tohit. Stored as decimal (0.07 = 7%).';


-- Individual accuracy/tohit contributions (for detailed breakdown)
CREATE TABLE build_accuracy_contributions (
    id SERIAL PRIMARY KEY,
    build_id INTEGER NOT NULL,
    source_name VARCHAR(255) NOT NULL,           -- e.g., "Thunderstrike", "Kismet +ToHit", "Tactics"
    source_type VARCHAR(50) NOT NULL,            -- 'set_bonus', 'special_io', 'power_buff', 'incarnate', 'enhancement'
    is_accuracy BOOLEAN NOT NULL,                -- TRUE = accuracy (multiplicative), FALSE = tohit (additive)
    magnitude NUMERIC(10, 6) NOT NULL,           -- e.g., 0.090000 for 9%
    power_id INTEGER,                            -- If from power buff, which power (NULL for sets/IOs)
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (build_id) REFERENCES builds(id) ON DELETE CASCADE,
    FOREIGN KEY (power_id) REFERENCES powers(id) ON DELETE SET NULL,

    CONSTRAINT chk_source_type CHECK (source_type IN ('set_bonus', 'special_io', 'power_buff', 'incarnate', 'enhancement')),
    CONSTRAINT chk_magnitude_range CHECK (magnitude >= 0.0 AND magnitude <= 2.0)  -- Sanity check: 0-200%
);

CREATE INDEX idx_build_accuracy_contributions_build ON build_accuracy_contributions(build_id);
CREATE INDEX idx_build_accuracy_contributions_type ON build_accuracy_contributions(build_id, is_accuracy);

COMMENT ON TABLE build_accuracy_contributions IS
'Tracks individual sources of accuracy and tohit bonuses for detailed breakdowns. Enables tooltip "hover to see sources" functionality.';

COMMENT ON COLUMN build_accuracy_contributions.is_accuracy IS
'TRUE = accuracy (multiplicative buff, applies to accuracy multiplier). FALSE = tohit (additive buff, adds to base tohit).';

COMMENT ON COLUMN build_accuracy_contributions.source_type IS
'Category of source: set_bonus (enhancement sets), special_io (Kismet etc), power_buff (Tactics, Build Up), incarnate (Alpha slot), enhancement (direct global from IO).';
```

### Views

```sql
-- Aggregated view with percentage display
CREATE VIEW v_build_accuracy_display AS
SELECT
    bta.build_id,
    bta.accuracy_total,
    bta.tohit_total,
    ROUND(bta.accuracy_total * 100, 2) AS accuracy_percentage,  -- Display: 9.00%
    ROUND(bta.tohit_total * 100, 2) AS tohit_percentage,        -- Display: 7.00%
    bta.calculated_at
FROM build_totals_accuracy bta;

COMMENT ON VIEW v_build_accuracy_display IS
'Converts accuracy/tohit totals to percentage for UI display. Maps to Statistics.BuffAccuracy and Statistics.BuffToHit properties.';


-- Detailed breakdown view
CREATE VIEW v_build_accuracy_breakdown AS
SELECT
    bac.build_id,
    bac.is_accuracy,
    CASE
        WHEN bac.is_accuracy THEN 'Accuracy'
        ELSE 'ToHit'
    END AS buff_type,
    bac.source_name,
    bac.source_type,
    bac.magnitude,
    ROUND(bac.magnitude * 100, 2) AS magnitude_percentage,
    p.name AS power_name,
    bac.created_at
FROM build_accuracy_contributions bac
LEFT JOIN powers p ON bac.power_id = p.id
ORDER BY bac.build_id, bac.is_accuracy DESC, bac.magnitude DESC;

COMMENT ON VIEW v_build_accuracy_breakdown IS
'Detailed breakdown of all accuracy and tohit sources for tooltip display. Ordered by buff type (accuracy first) and magnitude (largest first).';


-- Summary statistics view
CREATE VIEW v_build_accuracy_summary AS
SELECT
    bac.build_id,

    -- Accuracy aggregation
    SUM(CASE WHEN bac.is_accuracy THEN bac.magnitude ELSE 0 END) AS total_accuracy,
    COUNT(CASE WHEN bac.is_accuracy THEN 1 END) AS accuracy_source_count,

    -- ToHit aggregation
    SUM(CASE WHEN NOT bac.is_accuracy THEN bac.magnitude ELSE 0 END) AS total_tohit,
    COUNT(CASE WHEN NOT bac.is_accuracy THEN 1 END) AS tohit_source_count,

    -- By source type
    SUM(CASE WHEN bac.source_type = 'set_bonus' AND bac.is_accuracy THEN bac.magnitude ELSE 0 END) AS accuracy_from_sets,
    SUM(CASE WHEN bac.source_type = 'special_io' AND bac.is_accuracy THEN bac.magnitude ELSE 0 END) AS accuracy_from_ios,
    SUM(CASE WHEN bac.source_type = 'incarnate' AND bac.is_accuracy THEN bac.magnitude ELSE 0 END) AS accuracy_from_incarnates,

    SUM(CASE WHEN bac.source_type = 'power_buff' AND NOT bac.is_accuracy THEN bac.magnitude ELSE 0 END) AS tohit_from_powers,
    SUM(CASE WHEN bac.source_type = 'set_bonus' AND NOT bac.is_accuracy THEN bac.magnitude ELSE 0 END) AS tohit_from_sets,

    MAX(bac.created_at) AS last_updated
FROM build_accuracy_contributions bac
GROUP BY bac.build_id;

COMMENT ON VIEW v_build_accuracy_summary IS
'Summary statistics for accuracy and tohit by source category. Useful for build analysis and optimization recommendations.';
```

### Migration

```sql
-- Migration: Add accuracy totals tables
-- Version: 2024XXXX_add_build_accuracy_totals.sql

BEGIN;

-- Create tables
-- (SQL from above)

-- Populate from existing builds (if applicable)
INSERT INTO build_totals_accuracy (build_id, accuracy_total, tohit_total)
SELECT
    id AS build_id,
    0.0 AS accuracy_total,
    0.0 AS tohit_total
FROM builds
WHERE id NOT IN (SELECT build_id FROM build_totals_accuracy);

COMMIT;
```

## Comprehensive Test Cases

### Test Case 1: Base Build (No Bonuses)

**Scenario**: Level 50 character with no set bonuses, no special IOs, no active buffs.

**Input**:
- Set bonuses: []
- Special IOs: []
- Power buffs: []
- Incarnate bonuses: []

**Calculation**:
```
Step 1: Initialize
  accuracy_total = 0.0
  tohit_total = 0.0

Step 2-5: Process sources (all empty)
  No contributions

Step 6: Final totals
  accuracy_total = 0.0
  tohit_total = 0.0
```

**Expected Output**:
- `GlobalAccuracyTotals.accuracy = 0.0` (0.00%)
- `GlobalAccuracyTotals.tohit = 0.0` (0.00%)
- `accuracy_contributions = []`
- `tohit_contributions = []`

**Database**:
```sql
build_totals_accuracy: (build_id=1, accuracy_total=0.0, tohit_total=0.0)
build_accuracy_contributions: (empty)
```

---

### Test Case 2: Thunderstrike 5-Set Accuracy Bonus

**Scenario**: Build has Thunderstrike slotted in one power (5 pieces), granting +9% accuracy set bonus.

**Input**:
- Set bonuses: [{"set_name": "Thunderstrike", "effect_type": "accuracy", "magnitude": 0.09}]
- Special IOs: []
- Power buffs: []
- Incarnate bonuses: []

**Calculation**:
```
Step 1: Initialize
  accuracy_total = 0.0
  tohit_total = 0.0

Step 2: Process set bonuses
  Thunderstrike: accuracy, magnitude = 0.09
  buff_accuracy += 0.09
  accuracy_total = 0.09

Steps 3-5: No other sources

Step 6: Final totals
  accuracy_total = 0.09
  tohit_total = 0.0
```

**Expected Output**:
- `GlobalAccuracyTotals.accuracy = 0.09` (9.00%)
- `GlobalAccuracyTotals.tohit = 0.0` (0.00%)
- `accuracy_contributions = [AccuracyContribution("Thunderstrike", SET_BONUS, True, 0.09)]`
- `tohit_contributions = []`

**Database**:
```sql
build_totals_accuracy: (build_id=2, accuracy_total=0.09, tohit_total=0.0)
build_accuracy_contributions:
  (id=1, build_id=2, source_name='Thunderstrike', source_type='set_bonus',
   is_accuracy=TRUE, magnitude=0.09, power_id=NULL)
```

---

### Test Case 3: Kismet +ToHit IO

**Scenario**: Build has Kismet: Accuracy/ToHit/+ToHit IO slotted (the unique proc).

**Input**:
- Set bonuses: []
- Special IOs: [{"name": "Kismet: Accuracy/ToHit/+ToHit", "effect_type": "tohit", "magnitude": 0.06}]
- Power buffs: []
- Incarnate bonuses: []

**Calculation**:
```
Step 1: Initialize
  accuracy_total = 0.0
  tohit_total = 0.0

Step 2: Skip (no set bonuses)

Step 3: Process special IOs
  Kismet: effect_type = "tohit", magnitude = 0.06
  buff_tohit += 0.06
  tohit_total = 0.06

Steps 4-5: No other sources

Step 6: Final totals
  accuracy_total = 0.0
  tohit_total = 0.06
```

**Expected Output**:
- `GlobalAccuracyTotals.accuracy = 0.0` (0.00%)
- `GlobalAccuracyTotals.tohit = 0.06` (6.00%)
- `accuracy_contributions = []`
- `tohit_contributions = [AccuracyContribution("Kismet +ToHit", SPECIAL_IO, False, 0.06)]`

**Database**:
```sql
build_totals_accuracy: (build_id=3, accuracy_total=0.0, tohit_total=0.06)
build_accuracy_contributions:
  (id=2, build_id=3, source_name='Kismet +ToHit', source_type='special_io',
   is_accuracy=FALSE, magnitude=0.06, power_id=NULL)
```

---

### Test Case 4: Tactics Toggle (ToHit Buff)

**Scenario**: Leadership pool power Tactics slotted with 3 ToHit IOs (95% enhancement after ED), active (toggle ON).

**Input**:
- Set bonuses: []
- Special IOs: []
- Power buffs: [{"power_name": "Tactics", "effect_type": "tohit", "magnitude": 0.07}]
  - Base Tactics: ~5.5% tohit, enhanced to ~7% with slotting
- Incarnate bonuses: []

**Calculation**:
```
Step 1: Initialize
  accuracy_total = 0.0
  tohit_total = 0.0

Steps 2-3: Skip (no set bonuses or special IOs)

Step 4: Process power buffs
  Tactics: effect_type = "tohit", magnitude = 0.07
  buff_tohit += 0.07
  tohit_total = 0.07

Step 5: Skip (no incarnates)

Step 6: Final totals
  accuracy_total = 0.0
  tohit_total = 0.07
```

**Expected Output**:
- `GlobalAccuracyTotals.accuracy = 0.0` (0.00%)
- `GlobalAccuracyTotals.tohit = 0.07` (7.00%)
- `accuracy_contributions = []`
- `tohit_contributions = [AccuracyContribution("Tactics", POWER_BUFF, False, 0.07, "Tactics")]`

**Database**:
```sql
build_totals_accuracy: (build_id=4, accuracy_total=0.0, tohit_total=0.07)
build_accuracy_contributions:
  (id=3, build_id=4, source_name='Tactics', source_type='power_buff',
   is_accuracy=FALSE, magnitude=0.07, power_id=42)
```

---

### Test Case 5: Alpha Incarnate Accuracy

**Scenario**: Musculature Core Paragon Alpha slotted (grants various bonuses including accuracy).

**Input**:
- Set bonuses: []
- Special IOs: []
- Power buffs: []
- Incarnate bonuses: [{"slot": "Alpha", "name": "Musculature Core Paragon", "effect_type": "accuracy", "magnitude": 0.05}]

**Calculation**:
```
Step 1: Initialize
  accuracy_total = 0.0
  tohit_total = 0.0

Steps 2-4: Skip (no other sources)

Step 5: Process incarnate bonuses
  Alpha - Musculature: effect_type = "accuracy", magnitude = 0.05
  buff_accuracy += 0.05
  accuracy_total = 0.05

Step 6: Final totals
  accuracy_total = 0.05
  tohit_total = 0.0
```

**Expected Output**:
- `GlobalAccuracyTotals.accuracy = 0.05` (5.00%)
- `GlobalAccuracyTotals.tohit = 0.0` (0.00%)
- `accuracy_contributions = [AccuracyContribution("Alpha - Musculature Core Paragon", INCARNATE, True, 0.05)]`
- `tohit_contributions = []`

**Database**:
```sql
build_totals_accuracy: (build_id=5, accuracy_total=0.05, tohit_total=0.0)
build_accuracy_contributions:
  (id=4, build_id=5, source_name='Alpha - Musculature Core Paragon',
   source_type='incarnate', is_accuracy=TRUE, magnitude=0.05, power_id=NULL)
```

---

### Test Case 6: Combined Multiple Sources (Realistic High-End Build)

**Scenario**: Heavily IO'd level 50+ build with multiple accuracy/tohit sources.

**Input**:
- Set bonuses:
  - Thunderstrike (5 pieces): +9% accuracy
  - Decimation (5 pieces): +9% accuracy
  - Adjusted Targeting (5 pieces): +9% accuracy
- Special IOs:
  - Kismet +ToHit: +6% tohit
- Power buffs:
  - Tactics (slotted): +7% tohit
- Incarnate bonuses:
  - Alpha (Musculature): +5% accuracy

**Calculation**:
```
Step 1: Initialize
  accuracy_total = 0.0
  tohit_total = 0.0

Step 2: Process set bonuses
  Thunderstrike: +0.09 accuracy
  Decimation: +0.09 accuracy
  Adjusted Targeting: +0.09 accuracy
  buff_accuracy = 0.09 + 0.09 + 0.09 = 0.27

Step 3: Process special IOs
  Kismet: +0.06 tohit
  buff_tohit = 0.06

Step 4: Process power buffs
  Tactics: +0.07 tohit
  buff_tohit += 0.07
  buff_tohit = 0.06 + 0.07 = 0.13

Step 5: Process incarnate bonuses
  Alpha: +0.05 accuracy
  buff_accuracy += 0.05
  buff_accuracy = 0.27 + 0.05 = 0.32

Step 6: Final totals
  accuracy_total = buff_accuracy
                 = 0.32
  tohit_total = 0.13
```

**Expected Output**:
- `GlobalAccuracyTotals.accuracy = 0.32` (32.00%)
- `GlobalAccuracyTotals.tohit = 0.13` (13.00%)
- `accuracy_contributions = [
    AccuracyContribution("Thunderstrike", SET_BONUS, True, 0.09),
    AccuracyContribution("Decimation", SET_BONUS, True, 0.09),
    AccuracyContribution("Adjusted Targeting", SET_BONUS, True, 0.09),
    AccuracyContribution("Alpha - Musculature Core Paragon", INCARNATE, True, 0.05)
  ]`
- `tohit_contributions = [
    AccuracyContribution("Kismet +ToHit", SPECIAL_IO, False, 0.06),
    AccuracyContribution("Tactics", POWER_BUFF, False, 0.07, "Tactics")
  ]`

**Database**:
```sql
build_totals_accuracy: (build_id=6, accuracy_total=0.32, tohit_total=0.13)
build_accuracy_contributions:
  (id=5, build_id=6, source_name='Thunderstrike', source_type='set_bonus',
   is_accuracy=TRUE, magnitude=0.09, power_id=NULL),
  (id=6, build_id=6, source_name='Decimation', source_type='set_bonus',
   is_accuracy=TRUE, magnitude=0.09, power_id=NULL),
  (id=7, build_id=6, source_name='Adjusted Targeting', source_type='set_bonus',
   is_accuracy=TRUE, magnitude=0.09, power_id=NULL),
  (id=8, build_id=6, source_name='Kismet +ToHit', source_type='special_io',
   is_accuracy=FALSE, magnitude=0.06, power_id=NULL),
  (id=9, build_id=6, source_name='Alpha - Musculature Core Paragon',
   source_type='incarnate', is_accuracy=TRUE, magnitude=0.05, power_id=NULL),
  (id=10, build_id=6, source_name='Tactics', source_type='power_buff',
   is_accuracy=FALSE, magnitude=0.07, power_id=42)
```

**Integration with Power Calculation** (Test Case 6 continued):

When applying these global totals to a specific power with:
- Base accuracy: 1.0
- Slotted accuracy: 95% (0.95) - 3 SO-equivalent IOs after ED
- Base ScalingToHit: 0.48 (+4 level enemy)

```
Application (from clsToonX.cs lines 1995-1999):
  nAcc = 0.32 (global accuracy)
  nToHit = 0.13 (global tohit)

  powerBuffed.Accuracy = 1.0 * (1 + 0.95 + 0.32) * (0.48 + 0.13)
                       = 1.0 * 2.27 * 0.61
                       = 1.3847
                       = 138.47%

  powerBuffed.AccuracyMult = 1.0 * (1 + 0.95 + 0.32)
                           = 1.0 * 2.27
                           = 2.27
                           = 227% (accuracy multiplier)
```

This demonstrates how global accuracy (32%) and global tohit (13%) combine with slotted accuracy (95%) to dramatically increase hit chance, especially against high-level enemies.

---

### Test Case 7: Power with Ignore Buff Flag

**Scenario**: Auto-hit power (e.g., pet summon) that ignores accuracy/tohit buffs.

**Input**:
- Global accuracy total: 0.32 (from Test Case 6)
- Global tohit total: 0.13 (from Test Case 6)
- Power: Dark Servant (Mastermind pet summon)
- Power.IgnoreBuff(Accuracy) = True
- Power.IgnoreBuff(ToHit) = True

**Calculation**:
```
get_accuracy_for_power(global_totals, power):
  IF power.ignores_buff(ACCURACY):  // True for Dark Servant
    RETURN 0.0

get_tohit_for_power(global_totals, power):
  IF power.ignores_buff(TOHIT):  // True for Dark Servant
    RETURN 0.0

Application:
  nAcc = 0.0 (ignored)
  nToHit = 0.0 (ignored)

  power.Accuracy = 1.0 * (1 + 0.0 + 0.0) * (0.75 + 0.0)
                 = 1.0 * 1.0 * 0.75
                 = 0.75
                 = 75% (base tohit only)
```

**Expected Output**:
- Accuracy applied to power: 0.0 (ignored)
- ToHit applied to power: 0.0 (ignored)
- Final hit chance: 75% (base only, no bonuses)

This demonstrates that global accuracy/tohit totals exist in the build, but certain powers don't benefit from them due to ignore flags.

## Python Implementation Guide

**Proposed Architecture:**

```python
# backend/app/calculations/build_totals.py

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class AccuracySource(Enum):
    """Source of accuracy/tohit bonus"""
    SET_BONUS = "set_bonus"
    SPECIAL_IO = "special_io"
    POWER_BUFF = "power_buff"
    INCARNATE = "incarnate"
    ENHANCEMENT = "enhancement"

@dataclass
class AccuracyContribution:
    """
    Individual contribution to global accuracy or tohit.
    Used for detailed breakdowns in UI tooltips.

    Maps to entries in build_accuracy_contributions table.
    """
    source_name: str                    # e.g., "Thunderstrike", "Kismet +ToHit", "Tactics"
    source_type: AccuracySource         # Category: SET_BONUS, SPECIAL_IO, POWER_BUFF, etc.
    is_accuracy: bool                   # True = accuracy (multiplicative), False = tohit (additive)
    magnitude: float                    # e.g., 0.09 for 9% (stored as decimal)
    power_name: Optional[str] = None    # If from power buff, which power granted it

@dataclass
class GlobalAccuracyTotals:
    """
    Aggregated global accuracy and tohit bonuses.
    Maps to MidsReborn's Totals.BuffAcc and Totals.BuffToHit.

    Stored in build_totals_accuracy table with detailed contributions
    in build_accuracy_contributions table.
    """
    accuracy: float                                     # Total global accuracy (multiplicative) - e.g., 0.09 = 9%
    tohit: float                                        # Total global tohit (additive) - e.g., 0.20 = 20%
    accuracy_contributions: List[AccuracyContribution]  # Detailed breakdown for accuracy
    tohit_contributions: List[AccuracyContribution]     # Detailed breakdown for tohit

    @property
    def accuracy_percentage(self) -> float:
        """
        Display value for UI (convert decimal to percentage).
        Maps to Statistics.BuffAccuracy in MidsReborn.
        """
        return self.accuracy * 100.0

    @property
    def tohit_percentage(self) -> float:
        """
        Display value for UI (convert decimal to percentage).
        Maps to Statistics.BuffToHit in MidsReborn.
        """
        return self.tohit * 100.0

    def get_accuracy_for_power(self, power_ignores_buffs: bool) -> float:
        """
        Get accuracy bonus for specific power, respecting ignore flags.

        Some powers ignore global accuracy buffs (auto-hit powers, pet summons).
        Maps to clsToonX.cs line 1996.

        Args:
            power_ignores_buffs: True if power has IgnoreBuff(Accuracy) flag

        Returns:
            Accuracy bonus to apply (0.0 if power ignores buffs)
        """
        return 0.0 if power_ignores_buffs else self.accuracy

    def get_tohit_for_power(self, power_ignores_buffs: bool) -> float:
        """
        Get tohit bonus for specific power, respecting ignore flags.

        Maps to clsToonX.cs line 1995.

        Args:
            power_ignores_buffs: True if power has IgnoreBuff(ToHit) flag

        Returns:
            ToHit bonus to apply (0.0 if power ignores buffs)
        """
        return 0.0 if power_ignores_buffs else self.tohit

    def __str__(self) -> str:
        """
        Format like MidsReborn totals display.
        Matches frmTotals.cs display format.
        """
        return f"Accuracy: {self.accuracy_percentage:.2f}%, ToHit: {self.tohit_percentage:.2f}%"

class BuildTotalsAccuracyCalculator:
    """
    Calculates global accuracy and tohit from all sources in a build.
    Maps to MidsReborn's GenerateBuildBuffs and CalcStatTotals for accuracy/tohit.

    Usage:
        calculator = BuildTotalsAccuracyCalculator()
        totals = calculator.calculate_accuracy_totals(
            set_bonuses=build.active_set_bonuses,
            special_ios=build.special_ios,
            power_buffs=build.active_power_buffs,
            incarnate_bonuses=build.incarnate_bonuses
        )
        print(totals)  # "Accuracy: 38.00%, ToHit: 7.00%"
    """

    def calculate_accuracy_totals(
        self,
        set_bonuses: List[dict],
        special_ios: List[dict],
        power_buffs: List[dict],
        incarnate_bonuses: List[dict]
    ) -> GlobalAccuracyTotals:
        """
        Aggregate global accuracy and tohit from all sources.

        Implements algorithm from clsToonX.cs lines 660-662 (aggregation)
        and lines 764, 767 (final totals calculation).

        Args:
            set_bonuses: List of active set bonus effects
                Format: [{"name": "Thunderstrike", "type": "accuracy", "magnitude": 0.09}, ...]
            special_ios: List of special IO effects (Kismet, etc.)
                Format: [{"name": "Kismet +ToHit", "type": "accuracy", "magnitude": 0.06}, ...]
            power_buffs: List of active power buffs (Tactics, Build Up, etc.)
                Format: [{"power": "Tactics", "type": "tohit", "magnitude": 0.07}, ...]
            incarnate_bonuses: List of incarnate accuracy/tohit bonuses
                Format: [{"slot": "Alpha", "type": "accuracy", "magnitude": 0.05}, ...]

        Returns:
            GlobalAccuracyTotals with aggregated values and detailed breakdown

        Raises:
            ValueError: If magnitude values are invalid (negative or > 2.0)
        """
        accuracy_total = 0.0
        tohit_total = 0.0
        accuracy_contributions = []
        tohit_contributions = []

        # 1. Aggregate set bonus accuracy
        for bonus in set_bonuses:
            magnitude = bonus["magnitude"]
            if magnitude < 0.0 or magnitude > 2.0:
                raise ValueError(f"Invalid set bonus magnitude: {magnitude}")

            if bonus.get("type") == "accuracy":
                accuracy_total += magnitude
                accuracy_contributions.append(AccuracyContribution(
                    source_name=bonus["name"],
                    source_type=AccuracySource.SET_BONUS,
                    is_accuracy=True,
                    magnitude=magnitude
                ))
            elif bonus.get("type") == "tohit":
                tohit_total += magnitude
                tohit_contributions.append(AccuracyContribution(
                    source_name=bonus["name"],
                    source_type=AccuracySource.SET_BONUS,
                    is_accuracy=False,
                    magnitude=magnitude
                ))

        # 2. Aggregate special IO accuracy/tohit
        for io in special_ios:
            magnitude = io["magnitude"]
            if magnitude < 0.0 or magnitude > 2.0:
                raise ValueError(f"Invalid special IO magnitude: {magnitude}")

            if io.get("type") == "accuracy":
                accuracy_total += magnitude
                accuracy_contributions.append(AccuracyContribution(
                    source_name=io["name"],
                    source_type=AccuracySource.SPECIAL_IO,
                    is_accuracy=True,
                    magnitude=magnitude
                ))
            elif io.get("type") == "tohit":
                tohit_total += magnitude
                tohit_contributions.append(AccuracyContribution(
                    source_name=io["name"],
                    source_type=AccuracySource.SPECIAL_IO,
                    is_accuracy=False,
                    magnitude=magnitude
                ))

        # 3. Aggregate power buff tohit (typically temporary buffs)
        for buff in power_buffs:
            magnitude = buff["magnitude"]
            if magnitude < 0.0 or magnitude > 2.0:
                raise ValueError(f"Invalid power buff magnitude: {magnitude}")

            if buff.get("type") == "tohit":
                tohit_total += magnitude
                tohit_contributions.append(AccuracyContribution(
                    source_name=buff.get("power", "Unknown"),
                    source_type=AccuracySource.POWER_BUFF,
                    is_accuracy=False,
                    magnitude=magnitude,
                    power_name=buff.get("power")
                ))
            # Some powers grant accuracy buffs (rare)
            elif buff.get("type") == "accuracy":
                accuracy_total += magnitude
                accuracy_contributions.append(AccuracyContribution(
                    source_name=buff.get("power", "Unknown"),
                    source_type=AccuracySource.POWER_BUFF,
                    is_accuracy=True,
                    magnitude=magnitude,
                    power_name=buff.get("power")
                ))

        # 4. Aggregate incarnate accuracy/tohit
        for bonus in incarnate_bonuses:
            magnitude = bonus["magnitude"]
            if magnitude < 0.0 or magnitude > 2.0:
                raise ValueError(f"Invalid incarnate magnitude: {magnitude}")

            if bonus.get("type") == "accuracy":
                accuracy_total += magnitude
                accuracy_contributions.append(AccuracyContribution(
                    source_name=bonus.get("slot", "Incarnate"),
                    source_type=AccuracySource.INCARNATE,
                    is_accuracy=True,
                    magnitude=magnitude
                ))
            elif bonus.get("type") == "tohit":
                tohit_total += magnitude
                tohit_contributions.append(AccuracyContribution(
                    source_name=bonus.get("slot", "Incarnate"),
                    source_type=AccuracySource.INCARNATE,
                    is_accuracy=False,
                    magnitude=magnitude
                ))

        return GlobalAccuracyTotals(
            accuracy=accuracy_total,
            tohit=tohit_total,
            accuracy_contributions=accuracy_contributions,
            tohit_contributions=tohit_contributions
        )

    def format_accuracy_breakdown(self, totals: GlobalAccuracyTotals) -> str:
        """
        Format detailed breakdown for display.
        Useful for "hover to see sources" tooltip in totals window.

        Matches frmTotals.cs tooltip formatting.

        Args:
            totals: GlobalAccuracyTotals to format

        Returns:
            Multi-line string with formatted breakdown

        Example:
            Total Accuracy: 38.00%
              Thunderstrike: +9.00%
              Decimation: +9.00%
              Kismet +ToHit: +6.00%

            Total ToHit: 7.00%
              Tactics: +7.00%
        """
        lines = []
        lines.append(f"Total Accuracy: {totals.accuracy_percentage:.2f}%")
        if totals.accuracy_contributions:
            for contrib in totals.accuracy_contributions:
                lines.append(f"  {contrib.source_name}: +{contrib.magnitude * 100:.2f}%")
        else:
            lines.append("  (No accuracy bonuses)")

        lines.append(f"\nTotal ToHit: {totals.tohit_percentage:.2f}%")
        if totals.tohit_contributions:
            for contrib in totals.tohit_contributions:
                power_info = f" ({contrib.power_name})" if contrib.power_name else ""
                lines.append(f"  {contrib.source_name}{power_info}: +{contrib.magnitude * 100:.2f}%")
        else:
            lines.append("  (No tohit bonuses)")

        return "\n".join(lines)
```

**Implementation Priority:**

**CRITICAL** - Implement in Phase 2 (Build Totals). Required for:
- Displaying build statistics in totals window
- Calculating accurate power hit chances
- Build optimization and comparison
- Integration with power accuracy calculations (Spec 08)

**Key Implementation Steps:**

1. Define `AccuracySource` enum for categorizing sources
2. Create `AccuracyContribution` dataclass for detailed tracking
3. Implement `GlobalAccuracyTotals` with display properties
4. Create `BuildTotalsAccuracyCalculator.calculate_accuracy_totals()` to aggregate from all sources
5. Handle set bonuses, special IOs (especially Kismet), power buffs, and Incarnate bonuses separately
6. Implement power-specific ignore flags (`get_accuracy_for_power()` / `get_tohit_for_power()`)
7. Add formatting method for detailed breakdown tooltips
8. NO caps or diminishing returns - just simple addition within each category
9. Integration with Spec 08 (power accuracy) for final hit chance calculations

**Testing Strategy:**

- Unit tests with known builds:
  - Zero accuracy/tohit: 0% / 0%
  - Thunderstrike 5-set: +9% accuracy
  - Kismet +ToHit IO: +6% accuracy (NOT tohit despite name)
  - Tactics (Maneuvers slotted): ~7% tohit
  - Combined set bonuses: Multiple sets with accuracy bonuses stack additively

- Test accuracy vs tohit distinction:
  - Verify accuracy marked as multiplicative (is_accuracy=True)
  - Verify tohit marked as additive (is_accuracy=False)

- Test power ignore flags:
  - Auto-hit power with ignore buffs: should return 0.0 for both
  - Normal power: should return full values

- Test detailed breakdown:
  - Verify all contributions tracked
  - Verify formatting for UI display
  - Verify source categorization

- Integration tests with Spec 08:
  - Build with +9% global accuracy, power with 1.0 base, 95% slotted accuracy, vs +4 enemy
  - Expected: base * (1 + 0.95 + 0.09) * (0.48) = 1.0 * 2.04 * 0.48 = 97.92% accuracy
  - Build with +7% tohit, same power
  - Expected: base * (1 + 0.95) * (0.48 + 0.07) = 1.0 * 1.95 * 0.55 = 107.25% accuracy

- Compare Python output to MidsReborn totals window for sample builds

**Validation Data Sources:**

- MidsReborn totals window "Accuracy" and "ToHit" displays
- Set bonus data from City of Data (accuracy bonuses per set)
- Kismet IO data (verify it's accuracy not tohit)
- Power buff magnitudes (Tactics, Build Up, Aim, etc.)
- Player build exports with known accuracy/tohit values

## Integration Points

### Dependencies (Specs This Relies On)

1. **Spec 08 - Power Accuracy/ToHit** (CRITICAL)
   - Defines accuracy vs tohit distinction (multiplicative vs additive)
   - Provides formula for applying global totals to individual powers
   - Documents IgnoreBuff flags for powers
   - Data flow: Spec 08 defines mechanics → Spec 23 aggregates totals → Spec 08 applies to powers

2. **Spec 13 - Enhancement Set Bonuses** (HIGH)
   - Source of most accuracy bonuses (Thunderstrike, Decimation, etc.)
   - Set bonus data: effect type, magnitude, set name
   - Rule of 5 does NOT apply to accuracy bonuses (important distinction)
   - Data flow: Spec 13 identifies active set bonuses → Spec 23 aggregates accuracy/tohit from sets

3. **Spec 14 - Enhancement Special IOs** (HIGH)
   - Kismet +ToHit IO: Despite name, grants accuracy (not tohit)
   - Other special IOs with global accuracy/tohit effects
   - Must distinguish global effects from power-specific enhancements
   - Data flow: Spec 14 identifies special IOs → Spec 23 aggregates global effects

4. **Spec 29 - Incarnate System** (MEDIUM)
   - Alpha slot: Common source of accuracy bonuses (Musculature, Cardiac)
   - Other incarnate slots may grant accuracy/tohit
   - Level shifts affect effective tohit but NOT accuracy totals
   - Data flow: Spec 29 provides incarnate bonuses → Spec 23 aggregates

### Dependents (Specs That Rely On This)

1. **Spec 08 - Power Accuracy/ToHit** (CRITICAL - BIDIRECTIONAL)
   - Consumes global accuracy/tohit totals for individual power calculations
   - Formula: `powerBuffed.Accuracy = base * (1 + slotted + global_acc) * (base_tohit + global_tohit)`
   - Checks IgnoreBuff flags before applying
   - Data flow: Spec 23 calculates global totals → Spec 08 applies to each power

2. **Spec 19-22 - Other Build Totals** (MEDIUM)
   - Similar aggregation pattern for defense, resistance, damage, recharge
   - Consistency in calculation approach and display
   - Totals window displays all build stats together
   - Data flow: All build totals specs → Totals window unified display

3. **Spec 35 - Totals Window/Build Statistics Display** (HIGH)
   - Primary consumer of aggregated accuracy/tohit
   - Displays: "Accuracy: 38.00%", "ToHit: 7.00%"
   - Tooltips: Detailed breakdown by source (hover to see)
   - Data flow: Spec 23 → Totals window UI → User sees stats

4. **Spec 40 - Build Comparison** (MEDIUM)
   - Compares accuracy/tohit between builds
   - Highlights differences in global bonuses
   - Optimization suggestions based on accuracy gaps
   - Data flow: Spec 23 for each build → Comparison engine → UI diff display

5. **Spec 42 - Build Optimization Recommendations** (LOW)
   - Suggests set bonuses to increase accuracy
   - Recommends Kismet IO if missing
   - Identifies accuracy gaps vs tohit gaps
   - Data flow: Spec 23 totals → Optimization engine → Recommendations

### Data Flow

```
Input Sources:
  - Set Bonuses (Spec 13) ───┐
  - Special IOs (Spec 14) ────┤
  - Power Buffs (Powers DB) ─┼──> Spec 23 Aggregation ──> GlobalAccuracyTotals
  - Incarnate (Spec 29) ──────┘

Outputs:
  GlobalAccuracyTotals ──┬──> Spec 08 (Power Calculations)
                         ├──> Spec 35 (Totals Display)
                         ├──> Spec 40 (Build Comparison)
                         └──> Spec 42 (Optimization)

Database:
  build_totals_accuracy ────> accuracy_total, tohit_total (aggregated)
  build_accuracy_contributions ────> Detailed breakdown by source
```

### API Endpoints Using This Calculation

1. **GET /api/v1/builds/{build_id}/totals**
   - Returns all build totals including accuracy/tohit
   - Response: `{ "accuracy": 0.38, "tohit": 0.07, ... }`
   - Used by: Totals window, build display

2. **GET /api/v1/builds/{build_id}/totals/accuracy/breakdown**
   - Returns detailed accuracy/tohit breakdown
   - Response: List of AccuracyContribution objects
   - Used by: Tooltip hover, detailed stats

3. **POST /api/v1/builds/{build_id}/calculate**
   - Triggers full build calculation including accuracy totals
   - Updates: build_totals_accuracy table
   - Returns: Complete build statistics

4. **GET /api/v1/powers/{power_id}/accuracy?build_id={build_id}**
   - Returns power-specific accuracy with global bonuses applied
   - Consumes: GlobalAccuracyTotals from build
   - Used by: Power tooltips, attack chance display

### UI Components Consuming This Data

1. **TotalsWindow Component**
   - Displays: "Accuracy: 38.00%", "ToHit: 7.00%"
   - Graphs: Bar charts for accuracy and tohit
   - Tooltips: Hover to see detailed breakdown

2. **PowerTooltip Component**
   - Shows: Final hit chance with global bonuses applied
   - Example: "128.15% accuracy (base + slotted + global) vs +4 enemy"
   - Breakdown: Separates slotted vs global contributions

3. **BuildComparison Component**
   - Compares: Accuracy and tohit between two builds
   - Highlights: Differences in global bonuses
   - Suggestions: Which build has better hit chance

4. **OptimizationPanel Component**
   - Recommends: Set bonuses to increase accuracy
   - Flags: Missing Kismet IO if not slotted
   - Calculates: Expected accuracy improvement from suggestions

### Database Integration

**Write Operations**:
```python
# After calculating GlobalAccuracyTotals
async def save_accuracy_totals(build_id: int, totals: GlobalAccuracyTotals):
    # 1. Upsert build_totals_accuracy
    await db.execute(
        "INSERT INTO build_totals_accuracy (build_id, accuracy_total, tohit_total) "
        "VALUES ($1, $2, $3) "
        "ON CONFLICT (build_id) DO UPDATE SET "
        "accuracy_total = $2, tohit_total = $3, calculated_at = NOW()",
        build_id, totals.accuracy, totals.tohit
    )

    # 2. Delete old contributions
    await db.execute(
        "DELETE FROM build_accuracy_contributions WHERE build_id = $1",
        build_id
    )

    # 3. Insert new contributions
    for contrib in totals.accuracy_contributions + totals.tohit_contributions:
        await db.execute(
            "INSERT INTO build_accuracy_contributions "
            "(build_id, source_name, source_type, is_accuracy, magnitude, power_id) "
            "VALUES ($1, $2, $3, $4, $5, $6)",
            build_id, contrib.source_name, contrib.source_type.value,
            contrib.is_accuracy, contrib.magnitude, contrib.power_id
        )
```

**Read Operations**:
```python
# Retrieve accuracy totals for display
async def get_accuracy_totals(build_id: int) -> GlobalAccuracyTotals:
    # 1. Get totals
    row = await db.fetchrow(
        "SELECT accuracy_total, tohit_total FROM build_totals_accuracy WHERE build_id = $1",
        build_id
    )

    # 2. Get contributions
    rows = await db.fetch(
        "SELECT source_name, source_type, is_accuracy, magnitude, power_id "
        "FROM build_accuracy_contributions WHERE build_id = $1 "
        "ORDER BY is_accuracy DESC, magnitude DESC",
        build_id
    )

    # 3. Reconstruct GlobalAccuracyTotals
    return GlobalAccuracyTotals(
        accuracy=row['accuracy_total'],
        tohit=row['tohit_total'],
        accuracy_contributions=[...],
        tohit_contributions=[...]
    )
```

### Cross-Calculation Dependencies

1. **Enhancement Set Bonuses → Accuracy Totals**
   - Must calculate set bonuses first (Spec 13)
   - Then aggregate accuracy/tohit from sets
   - Order: Set detection → Set bonus calculation → Accuracy aggregation

2. **Power Buffs → Accuracy Totals → Power Accuracy**
   - Must determine which powers are active (toggles ON, auto powers)
   - Aggregate tohit from active powers (Tactics, Focused Accuracy)
   - Apply to individual power calculations
   - Order: Power activation state → Tohit aggregation → Power-specific accuracy

3. **Incarnate Bonuses → Accuracy Totals**
   - Must determine selected incarnate powers
   - Extract accuracy/tohit effects
   - Aggregate with other sources
   - Order: Incarnate selection → Effect extraction → Aggregation

### Performance Considerations

1. **Calculation Frequency**
   - Recalculate on:
     - Enhancement slot change
     - Power toggle on/off
     - Incarnate selection change
     - Set bonus activation/deactivation
   - Cache: Store in database, invalidate on changes
   - Typical: ~50-100ms calculation time for full build

2. **Database Queries**
   - Single query for totals: Fast (indexed by build_id)
   - Detailed breakdown: Slightly slower (join with powers table)
   - Optimization: Use views for common queries

3. **UI Updates**
   - Debounce: Wait 500ms after slot change before recalculating
   - Progressive: Show cached totals immediately, update in background
   - Optimistic: Assume changes succeed, revert on error

## References

- **Related Specs**:
  - Spec 08 (Power Accuracy/ToHit) - Consumes these global totals in power calculations
  - Spec 13 (Enhancement Set Bonuses) - Source of most global accuracy bonuses
  - Spec 14 (Enhancement Special IOs) - Kismet +ToHit and other special global IOs
  - Spec 22 (Build Totals - Damage) - Similar aggregation pattern for global damage
  - Spec 25 (Buff Stacking Rules) - How accuracy/tohit bonuses combine (additive within category)
- **MidsReborn Files**:
  - `clsToonX.cs` (GenerateBuildBuffs, CalcStatTotals, GBPA_Pass4_ApplyAccuracy)
  - `Core/Base/Data_Classes/Character.cs` (TotalStatistics with BuffAcc/BuffToHit)
  - `Core/Statistics.cs` (BuffAccuracy and BuffToHit display properties)
  - `Forms/WindowMenuItems/frmTotals.cs` (Totals window display with tooltips)
  - `Core/Enums.cs` (eStatType.BuffAcc enum)
- **Game Documentation**:
  - Paragon Wiki - "Accuracy", "ToHit", "Set Bonuses"
  - Homecoming Wiki - "Invention Sets", "Accuracy Mechanics"
  - City of Data - Set bonus values for accuracy
  - Player guides on accuracy vs tohit optimization
