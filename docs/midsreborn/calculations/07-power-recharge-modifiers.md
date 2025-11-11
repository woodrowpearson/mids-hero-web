# Power Recharge Modifiers

## Overview
- **Purpose**: Calculate actual recharge time for powers based on base recharge, local enhancements, and global recharge bonuses
- **Used By**: Power display system, DPS/DPA calculations, rotation planning, combat timeline, endurance usage
- **Complexity**: Medium
- **Priority**: Critical
- **Status**: 🟡 Breadth Complete

## MidsReborn Implementation

### Primary Location
- **File**: `clsToonX.cs`
- **Class**: `clsToonX`
- **Methods**:
  - `GBPA_Pass1_EnhancePreED()` - Adds local recharge enhancements before ED
  - `GBPA_Pass2_ApplyED()` - Applies Enhancement Diversification (ED) to recharge
  - `GBPA_Pass5_MultiplyPreBuff()` - Divides base recharge by enhancement multiplier (includes local recharge)
  - `GetBuffedPower()` - Final power calculation that produces actual recharge time

### Dependencies
- **Core/Enhancement.cs**:
  - `GetSchedule()` - Returns ED schedule for recharge (Schedule A)
  - `ApplyED()` - Applies ED curve to local recharge bonuses
- **Core/Statistics.cs**:
  - `BuffHaste()` - Returns global recharge bonus percentage (capped or uncapped)
- **Core/Base/Data_Classes/Power.cs**:
  - `RechargeTime` - Current (enhanced) recharge time
  - `BaseRechargeTime` - Original power recharge before any enhancements
- **Core/Base/Data_Classes/Character.cs**:
  - `TotalsCapped.BuffHaste` - Global recharge bonus (multiplicative factor, capped)
  - `Totals.BuffHaste` - Global recharge bonus (multiplicative factor, uncapped)

### Algorithm Pseudocode

```
CALCULATE_POWER_RECHARGE(power, characterStats, slottedEnhancements):
    # Step 1: Get base recharge time
    baseRecharge = power.BaseRechargeTime

    # Step 2: Sum local recharge enhancements (pre-ED)
    localRechargeBonus = 0.0
    FOR each enhancement in slottedEnhancements:
        IF enhancement has recharge component:
            localRechargeBonus += enhancement.RechargeValue

    # Step 3: Apply Enhancement Diversification (ED) to local bonuses
    schedule = GetSchedule(Enums.eEnhance.RechargeTime)  # Returns Schedule A
    localRechargeBonusAfterED = ApplyED(schedule, localRechargeBonus)

    # Step 4: Convert bonus to multiplier (1 + bonus)
    localRechargeMultiplier = 1.0 + localRechargeBonusAfterED

    # Step 5: Get global recharge bonus (from set bonuses, Hasten, etc.)
    # BuffHaste is stored as multiplicative factor, e.g., 0.70 for +70% recharge
    globalRechargeFactor = characterStats.TotalsCapped.BuffHaste

    # Step 6: Calculate final recharge time
    # Formula: ActualRecharge = BaseRecharge / (LocalMultiplier * GlobalMultiplier)
    # Note: Global is stored as factor, so (1 + globalFactor) gives multiplier
    actualRecharge = baseRecharge / (localRechargeMultiplier * (1 + globalRechargeFactor))

    # Step 7: Apply archetype recharge cap if needed
    IF actualRecharge exceeds archetype.RechargeCap:
        actualRecharge = archetype.RechargeCap

    RETURN actualRecharge
```

### Key Logic Snippets

**Enhancement Diversification for Recharge (Schedule A):**
```csharp
// clsToonX.cs - GBPA_Pass2_ApplyED()
powerMath.RechargeTime = Enhancement.ApplyED(
    Enhancement.GetSchedule(Enums.eEnhance.RechargeTime),
    powerMath.RechargeTime
);

// Core/Enhancement.cs - GetSchedule()
// RechargeTime uses default Schedule A (same as most enhancements)
public static Enums.eSchedule GetSchedule(Enums.eEnhance iEnh, int tSub = -1)
{
    switch (iEnh)
    {
        case Enums.eEnhance.Defense:
            eSchedule = Enums.eSchedule.B;
            break;
        case Enums.eEnhance.Interrupt:
            return Enums.eSchedule.C;
        // ... other special cases ...
        default:
            eSchedule = Enums.eSchedule.A;  // RechargeTime falls here
            break;
    }
    return eSchedule;
}
```

**ED Curve Application:**
```csharp
// Core/Enhancement.cs - ApplyED()
public static float ApplyED(Enums.eSchedule iSched, float iVal)
{
    var ed = new float[3];
    for (var index = 0; index <= 2; ++index)
        ed[index] = DatabaseAPI.Database.MultED[(int) iSched][index];

    if (iVal <= ed[0])
        return iVal;  // No ED penalty below first threshold

    float[] edm = {
        ed[0],
        ed[0] + (ed[1] - ed[0]) * 0.9f,       // 90% efficiency
        edm[1] + (ed[2] - ed[1]) * 0.7f        // 70% efficiency
    };

    return iVal > ed[1]
        ? iVal > ed[2]
            ? edm[2] + (iVal - ed[2]) * 0.15f  // 15% efficiency above ed[2]
            : edm[1] + (iVal - ed[1]) * 0.7f   // 70% efficiency ed[1]-ed[2]
        : edm[0] + (iVal - ed[0]) * 0.9f;      // 90% efficiency ed[0]-ed[1]
}
```

**Global Recharge Bonus (BuffHaste):**
```csharp
// Core/Statistics.cs - BuffHaste()
public const float MaxHaste = 400f;  // 400% is the hard cap

public float BuffHaste(bool uncapped)
{
    return !uncapped
        ? Math.Min(MaxHaste, (_character.TotalsCapped.BuffHaste + 1) * 100)
        : (_character.Totals.BuffHaste + 1) * 100;
}

// clsToonX.cs - Building BuffHaste from all sources
Totals.BuffHaste = _selfEnhance.Effect[(int)Enums.eStatType.Haste] +
                   _selfBuffs.Effect[(int)Enums.eStatType.Haste];

TotalsCapped.BuffHaste = Math.Min(TotalsCapped.BuffHaste,
                                  Archetype.RechargeCap - 1);
```

**Final Recharge Calculation:**
```csharp
// clsToonX.cs - GBPA_Pass5_MultiplyPreBuff()
// Note: powerMath.RechargeTime contains the local enhancement multiplier (1 + bonus)
// This divides base by local multiplier
powerBuffed.RechargeTime /= powerMath.RechargeTime;

// Global recharge is applied separately via character stats
// From Core/Base/Data_Classes/Effect.cs (proc calculations)
var globalRecharge = (MidsContext.Character.DisplayStats.BuffHaste(false) - 100) / 100;
var rechargeVal = Math.Abs(power.RechargeTime) < float.Epsilon
    ? 0
    : power.BaseRechargeTime / (power.BaseRechargeTime / power.RechargeTime - globalRecharge);
```

## Game Mechanics Context

### Why This Calculation Exists

Recharge time determines how frequently a power can be activated, making it one of the most important stats in City of Heroes. The calculation has two components:

1. **Local Recharge**: Enhancement slots in the power itself
2. **Global Recharge**: Bonuses from set IOs, Hasten power, and other buffs

### Historical Context

- **Pre-Issue 5**: No Enhancement Diversification - recharge could be slotted to extreme levels
- **Issue 5 (ED)**: Introduced diminishing returns to prevent excessive slotting
- **Post-Issue 5**: Global recharge bonuses became crucial for builds
  - Hasten (Speed pool power): +70% global recharge
  - Set bonuses: Common source of +recharge bonuses (often +5% to +10% per set)
  - Purple sets: Can provide +10% recharge bonuses

### Recharge Caps

Different archetypes have different recharge speed caps:

- **Most ATs**: 400% (4x base speed, or 75% reduction)
- **Some ATs**: 500% (5x base speed, or 80% reduction)

At the cap, a 60-second recharge power recharges in 15 seconds (400% cap) or 12 seconds (500% cap).

### Enhancement Diversification (ED) for Recharge

Recharge uses **Schedule A** (same as most enhancements):

| Total Bonus | Effectiveness |
|-------------|---------------|
| 0% - 70%    | 100% efficient |
| 70% - 100%  | 90% efficient |
| 100% - 130% | 70% efficient |
| Above 130%  | 15% efficient |

Example: Slotting three level 50 Recharge IOs (+42.4% each = 127.2% total):
- First 70%: 70% × 100% = 70%
- Next 30%: 30% × 90% = 27%
- Remaining 27.2%: 27.2% × 70% = 19.04%
- **Effective Total**: 70% + 27% + 19.04% = 116.04% recharge (not 127.2%)

### Known Quirks

1. **Hasten Stacking**: Hasten's +70% global recharge stacks with set bonuses additively
2. **Perma-Hasten**: A common build goal requiring ~120% global recharge to make Hasten permanent
3. **Base vs Enhanced**: Game displays enhanced recharge time, not base
4. **Zero Recharge Powers**: Some powers have 0 second recharge (auto powers, toggles) - division by zero must be avoided
5. **Recharge Intensive Sets**: Some power categories (like pet summons) benefit more from recharge than others

## Python Implementation Guide

### Proposed Architecture

**Location**: `backend/app/game_logic/calculations/power_recharge.py`

**Module Structure**:
```python
# power_recharge.py
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class RechargeCalculationResult:
    """Result of recharge time calculation."""
    base_recharge: float
    local_recharge_bonus: float
    local_recharge_after_ed: float
    global_recharge_bonus: float
    actual_recharge: float
    is_capped: bool
    archetype_cap: float

class PowerRechargeCalculator:
    """Calculates power recharge times with local and global bonuses."""

    def __init__(self, ed_calculator):
        """Initialize with ED calculator dependency."""
        self.ed_calculator = ed_calculator

    def calculate_recharge(
        self,
        base_recharge: float,
        local_bonuses: List[float],
        global_bonus: float,
        archetype_cap: float = 400.0
    ) -> RechargeCalculationResult:
        """Calculate actual recharge time for a power."""
        pass

    def calculate_global_recharge(
        self,
        set_bonuses: List[float],
        hasten_active: bool = False,
        other_buffs: List[float] = None
    ) -> float:
        """Calculate total global recharge bonus."""
        pass

    def get_recharge_for_perma_hasten(self) -> float:
        """Calculate global recharge needed for permanent Hasten."""
        # Hasten: 120s duration, 120s base recharge
        # Need: 120s / (1 + global) <= 120s - cast_time
        pass
```

### Dependencies on Other Calculations

- **Spec 10** (Enhancement Schedules): ED curve implementation required
- **Spec 11** (Enhancement Slotting): How to sum enhancement values
- **Spec 17** (Archetype Caps): Recharge caps by archetype
- **Spec 21** (Build Totals Recharge): Aggregating global recharge from all sources

### Implementation Notes

#### C# vs Python Gotchas

1. **Multiplicative Factor Storage**:
   - C# stores BuffHaste as decimal (0.70 for +70%)
   - Display shows percentage (BuffHaste + 1) × 100 = 170%
   - Python should maintain same storage format for consistency

2. **Division by Zero**:
   - Check for zero recharge before calculating (auto powers, toggles)
   - Return 0 or special value for non-rechargeable powers

3. **Float Precision**:
   - ED calculations involve multiple small multipliers
   - Use appropriate precision for game accuracy (2 decimal places typical)

#### Edge Cases to Test

1. **Zero Recharge Powers**: Auto powers, toggle powers (base_recharge = 0)
2. **No Enhancements**: Power with no recharge slotted (local_bonus = 0)
3. **ED Caps**: Power with 3+ recharge SOs (tests ED curve)
4. **Global Recharge Only**: Power with no local recharge but high global recharge
5. **Hasten Active**: Testing +70% global recharge bonus
6. **Archetype Cap**: Build exceeding 400% recharge cap
7. **Perma-Hasten**: ~120% global recharge making Hasten permanent
8. **Negative Recharge**: Debuffs that slow recharge (rare but possible)

#### Performance Considerations

- Cache ED calculations for common enhancement combinations
- Pre-calculate archetype caps (static data)
- Consider batch calculation for entire build's powers
- Global recharge calculated once per build, not per power

#### Validation Strategy

**Test Against MidsReborn**:
1. Create test power with known base recharge (e.g., 60s)
2. Add known enhancements (e.g., 3× Level 50 Recharge IO = +42.4% each)
3. Add known global recharge (e.g., Hasten = +70%)
4. Compare final recharge time with MidsReborn display

**Example Test Case**:
```python
def test_recharge_with_hasten():
    # Power: Foot Stomp (base recharge: 20s)
    # Slotting: 2× Level 50 Recharge IO (+42.4% each = 84.8% total)
    # Global: Hasten active (+70%)

    calc = PowerRechargeCalculator(ed_calculator)
    result = calc.calculate_recharge(
        base_recharge=20.0,
        local_bonuses=[0.424, 0.424],
        global_bonus=0.70,
        archetype_cap=400.0
    )

    # Expected calculation:
    # Local bonus: 84.8% pre-ED
    # After ED (Schedule A): 70% + (14.8% * 0.9) = 83.32%
    # Local multiplier: 1 + 0.8332 = 1.8332
    # Global multiplier: 1 + 0.70 = 1.70
    # Total multiplier: 1.8332 * 1.70 = 3.116
    # Actual recharge: 20 / 3.116 = 6.42 seconds

    assert abs(result.actual_recharge - 6.42) < 0.1
```

### Test Cases

#### Test Case 1: No Enhancements
```
Input:
- Base Recharge: 60.0s
- Local Bonuses: []
- Global Bonus: 0.0
- Archetype Cap: 400.0

Expected Output:
- Actual Recharge: 60.0s
- Local Bonus After ED: 0.0
- Is Capped: False
```

#### Test Case 2: Three Recharge SOs (Tests ED)
```
Input:
- Base Recharge: 60.0s
- Local Bonuses: [0.385, 0.385, 0.385]  # Three +38.5% SOs
- Global Bonus: 0.0
- Archetype Cap: 400.0

Calculation:
- Total Local Bonus: 115.5% (1.155)
- After ED Schedule A:
  - First 70%: 70% × 100% = 70%
  - Next 30%: 30% × 90% = 27%
  - Remaining 15.5%: 15.5% × 70% = 10.85%
  - Total: 107.85%
- Actual Recharge: 60 / (1 + 1.0785) = 28.88s

Expected Output:
- Actual Recharge: ~28.88s
- Local Bonus After ED: 1.0785
- Is Capped: False
```

#### Test Case 3: Hasten + Set Bonuses
```
Input:
- Base Recharge: 120.0s (Hasten itself)
- Local Bonuses: [0.424, 0.424]  # Two Level 50 Recharge IOs
- Global Bonus: 1.00  # +100% from set bonuses (not including Hasten)
- Archetype Cap: 400.0

Calculation:
- Total Local Bonus: 84.8%
- After ED: 70% + (14.8% × 0.9) = 83.32%
- Local Multiplier: 1.8332
- Global Multiplier: 2.00
- Total: 1.8332 × 2.00 = 3.6664
- Actual Recharge: 120 / 3.6664 = 32.73s

Expected Output:
- Actual Recharge: ~32.73s
- Is Capped: False
```

#### Test Case 4: Exceeding Archetype Cap
```
Input:
- Base Recharge: 60.0s
- Local Bonuses: [0.424, 0.424, 0.424]  # Three Level 50 Recharge IOs
- Global Bonus: 2.50  # +250% global recharge
- Archetype Cap: 400.0

Calculation:
- Local After ED: ~116% (see Test Case 2)
- Uncapped Total: (1 + 1.16) × (1 + 2.50) = 7.56
- Exceeds cap: 7.56 > 4.00
- Capped multiplier: 4.00
- Actual Recharge: 60 / 4.00 = 15.0s

Expected Output:
- Actual Recharge: 15.0s
- Is Capped: True
- Archetype Cap: 400.0
```

#### Test Case 5: Zero Recharge Power (Toggle/Auto)
```
Input:
- Base Recharge: 0.0s
- Local Bonuses: [0.424]  # Enhancement present but irrelevant
- Global Bonus: 0.70
- Archetype Cap: 400.0

Expected Output:
- Actual Recharge: 0.0s
- Local Bonus After ED: N/A
- Is Capped: False
```

## References

### Related Calculation Specs
- **Spec 10**: Enhancement Schedules (ED curves)
- **Spec 11**: Enhancement Slotting (combining bonuses)
- **Spec 17**: Archetype Caps (recharge speed caps)
- **Spec 21**: Build Totals Recharge (global recharge aggregation)
- **Spec 34**: Proc Chance Formulas (PPM uses recharge time)

### MidsReborn Code References
- `clsToonX.cs`: Lines 1400-2000 (GBPA power calculation pipeline)
- `Core/Enhancement.cs`: Lines 434-486 (GetSchedule, ApplyED)
- `Core/Statistics.cs`: Lines 231-236 (BuffHaste)
- `Core/Base/Data_Classes/Effect.cs`: Proc PPM calculations using recharge

### Forum Posts & Wikis
- Paragon Wiki: [Enhancement Diversification](https://archive.paragonwiki.com/wiki/Enhancement_Diversification)
- Homecoming Forums: [Recharge Calculation Guide](https://forums.homecomingservers.com/)
- City of Data: [Power Recharge Attributes](https://cod.uberguy.net/)

### Game Constants
- **Schedule A ED Breakpoints**: 70%, 100%, 130%
- **Schedule A ED Multipliers**: 100%, 90%, 70%, 15%
- **Recharge Hard Cap**: 400% (most ATs), 500% (some ATs)
- **Hasten Bonus**: +70% global recharge
- **Hasten Duration**: 120 seconds
- **Hasten Base Recharge**: 120 seconds

---

**Document Status**: 🟡 Breadth Complete - High-level spec with pseudocode and game context
**Last Updated**: 2025-11-10
**Next Steps**: Add full implementation detail in Milestone 3 (depth pass)
