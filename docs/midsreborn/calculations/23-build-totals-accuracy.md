# Build Totals - Accuracy/ToHit

## Overview
- **Purpose**: Calculate global accuracy (multiplicative) and tohit (additive) bonuses from set bonuses, Incarnate abilities, and special IOs that apply to all powers in a build
- **Used By**: Power accuracy calculations (Spec 08), build statistics display, totals window, combat effectiveness analysis
- **Complexity**: Simple
- **Priority**: Critical
- **Status**: 🟡 Breadth Complete

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
  - Special IOs (e.g., Kismet +ToHit IO - despite the name, grants +6% accuracy)
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

- **Issue 9 (2007)**: Kismet +ToHit IO introduced. Despite the name "Kismet: Accuracy/ToHit/+ToHit", the unique proc grants +6% accuracy (multiplicative), not +6% tohit (additive). This naming confusion persists today but became a staple of builds.

- **Issue 13 (2008)**: More set bonuses with accuracy/tohit introduced. High-end builds could reach 15-20% global accuracy.

- **Homecoming (2019+)**: Meta shifted to softcap defense on many ATs. Global accuracy became even more valuable for maintaining offense while investing heavily in defense.

**Known Quirks:**

1. **Kismet IO Misnomer**: The "Kismet: Accuracy/ToHit/+ToHit" proc grants +6% accuracy (multiplicative), NOT +6% tohit (additive). This is the opposite of what the name suggests and confuses new players.

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

## Python Implementation Notes

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
    Individual contribution to global accuracy or tohit
    Used for detailed breakdowns in UI
    """
    source_name: str           # e.g., "Thunderstrike", "Kismet +ToHit", "Tactics"
    source_type: AccuracySource
    is_accuracy: bool          # True = accuracy (multiplicative), False = tohit (additive)
    magnitude: float           # e.g., 0.09 for 9%
    power_name: Optional[str] = None  # If from power buff, which power

@dataclass
class GlobalAccuracyTotals:
    """
    Aggregated global accuracy and tohit bonuses
    Maps to MidsReborn's Totals.BuffAcc and Totals.BuffToHit
    """
    accuracy: float            # Total global accuracy (multiplicative) - e.g., 0.09 = 9%
    tohit: float              # Total global tohit (additive) - e.g., 0.20 = 20%
    accuracy_contributions: List[AccuracyContribution]  # Detailed breakdown
    tohit_contributions: List[AccuracyContribution]     # Detailed breakdown

    @property
    def accuracy_percentage(self) -> float:
        """Display value for UI"""
        return self.accuracy * 100.0

    @property
    def tohit_percentage(self) -> float:
        """Display value for UI"""
        return self.tohit * 100.0

    def get_accuracy_for_power(self, power_ignores_buffs: bool) -> float:
        """
        Get accuracy bonus for specific power
        Some powers ignore global accuracy buffs
        """
        return 0.0 if power_ignores_buffs else self.accuracy

    def get_tohit_for_power(self, power_ignores_buffs: bool) -> float:
        """
        Get tohit bonus for specific power
        Some powers ignore global tohit buffs
        """
        return 0.0 if power_ignores_buffs else self.tohit

    def __str__(self) -> str:
        """Format like MidsReborn totals display"""
        return f"Accuracy: {self.accuracy_percentage:.2f}%, ToHit: {self.tohit_percentage:.2f}%"

class BuildTotalsAccuracyCalculator:
    """
    Calculates global accuracy and tohit from all sources in a build
    Maps to MidsReborn's GenerateBuildBuffs and CalcStatTotals for accuracy/tohit
    """

    def calculate_accuracy_totals(self,
                                  set_bonuses: List[dict],
                                  special_ios: List[dict],
                                  power_buffs: List[dict],
                                  incarnate_bonuses: List[dict]) -> GlobalAccuracyTotals:
        """
        Aggregate global accuracy and tohit from all sources

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
        """
        accuracy_total = 0.0
        tohit_total = 0.0
        accuracy_contributions = []
        tohit_contributions = []

        # 1. Aggregate set bonus accuracy
        for bonus in set_bonuses:
            if bonus.get("type") == "accuracy":
                magnitude = bonus["magnitude"]
                accuracy_total += magnitude
                accuracy_contributions.append(AccuracyContribution(
                    source_name=bonus["name"],
                    source_type=AccuracySource.SET_BONUS,
                    is_accuracy=True,
                    magnitude=magnitude
                ))
            elif bonus.get("type") == "tohit":
                magnitude = bonus["magnitude"]
                tohit_total += magnitude
                tohit_contributions.append(AccuracyContribution(
                    source_name=bonus["name"],
                    source_type=AccuracySource.SET_BONUS,
                    is_accuracy=False,
                    magnitude=magnitude
                ))

        # 2. Aggregate special IO accuracy/tohit
        for io in special_ios:
            if io.get("type") == "accuracy":
                magnitude = io["magnitude"]
                accuracy_total += magnitude
                accuracy_contributions.append(AccuracyContribution(
                    source_name=io["name"],
                    source_type=AccuracySource.SPECIAL_IO,
                    is_accuracy=True,
                    magnitude=magnitude
                ))
            elif io.get("type") == "tohit":
                magnitude = io["magnitude"]
                tohit_total += magnitude
                tohit_contributions.append(AccuracyContribution(
                    source_name=io["name"],
                    source_type=AccuracySource.SPECIAL_IO,
                    is_accuracy=False,
                    magnitude=magnitude
                ))

        # 3. Aggregate power buff tohit (typically temporary buffs)
        for buff in power_buffs:
            if buff.get("type") == "tohit":
                magnitude = buff["magnitude"]
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
                magnitude = buff["magnitude"]
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
            if bonus.get("type") == "accuracy":
                magnitude = bonus["magnitude"]
                accuracy_total += magnitude
                accuracy_contributions.append(AccuracyContribution(
                    source_name=bonus.get("slot", "Incarnate"),
                    source_type=AccuracySource.INCARNATE,
                    is_accuracy=True,
                    magnitude=magnitude
                ))
            elif bonus.get("type") == "tohit":
                magnitude = bonus["magnitude"]
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
        Format detailed breakdown for display
        Useful for "hover to see sources" tooltip
        """
        lines = []
        lines.append(f"Total Accuracy: {totals.accuracy_percentage:.2f}%")
        if totals.accuracy_contributions:
            for contrib in totals.accuracy_contributions:
                lines.append(f"  {contrib.source_name}: +{contrib.magnitude * 100:.2f}%")

        lines.append(f"\nTotal ToHit: {totals.tohit_percentage:.2f}%")
        if totals.tohit_contributions:
            for contrib in totals.tohit_contributions:
                power_info = f" ({contrib.power_name})" if contrib.power_name else ""
                lines.append(f"  {contrib.source_name}{power_info}: +{contrib.magnitude * 100:.2f}%")

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
