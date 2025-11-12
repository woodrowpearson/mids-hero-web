# Power Endurance and Recovery

## Overview
- **Purpose**: Calculate endurance cost of powers, endurance recovery rate, and max endurance modifications
- **Used By**: All powers (cost), endurance management builds, recovery powers, stamina effects
- **Complexity**: Simple
- **Priority**: Critical
- **Status**: 🟡 Breadth Complete

## MidsReborn Implementation

### Primary Location
- **File**: `Core/Base/Data_Classes/Power.cs`
- **Key Properties**: `EndCost`, `ToggleCost`, `ActivatePeriod`
- **Calculation**: `Core/Statistics.cs` - EnduranceRecoveryNumeric, EnduranceMaxEnd, EnduranceUsage
- **Enhancement**: `clsToonX.cs` - Endurance cost reduction via EnduranceDiscount

### Related Files
- `Core/Base/Data_Classes/Archetype.cs` - BaseRecovery (default 1.67 end/sec)
- `Core/Base/Data_Classes/Effect.cs` - Recovery and Endurance effect types
- `Core/Enums.cs` - eEffectType.Endurance (max end), eEffectType.Recovery, eEffectType.EnduranceDiscount
- `clsToonX.cs` - Build-wide endurance totals and cost calculations

### Effect Types

MidsReborn uses three distinct effect types for endurance mechanics:

**eEffectType.EnduranceDiscount**:
- Reduces endurance cost of powers (like Endurance Reduction enhancements)
- Magnitude is percentage reduction (positive values reduce cost)
- Applied to power's EndCost before use
- Subject to Enhancement Diversification (ED)
- Enhancement class: "EndRdx" (Endurance Reduction)

**eEffectType.Recovery**:
- Increases endurance recovery rate (like Stamina, Physical Perfection)
- Magnitude is percentage modifier to base recovery
- Stacks additively with other recovery bonuses
- Example: Stamina = +25% recovery (0.25 magnitude)

**eEffectType.Endurance**:
- Increases maximum endurance (like set bonuses, Accolades)
- Magnitude is flat endurance increase (not percentage)
- Base max endurance: 100.0
- Common from IO set bonuses: +2.25%, +4.5%, +7.5%
- Display: Shows as "MaxEnd" in some UI contexts

### High-Level Algorithm

```
Power Endurance Cost (Click/Auto Powers):
  1. Get base EndCost from power data
  2. Apply EnduranceDiscount effects (enhancements):
     ModifiedCost = BaseCost * (1 - EndDiscountTotal)
  3. Apply Enhancement Diversification (ED):
     FinalCost = ApplyED(Schedule.EnduranceDiscount, ModifiedCost)
  4. Power costs this much endurance when activated

Example (Footstomp with 3x EndRdx SOs):
  - Base cost: 13.0 endurance
  - 3x EndRdx SO = 95.66% reduction total (before ED)
  - After ED: ~56% actual reduction
  - Final cost: 13.0 * (1 - 0.56) = 5.72 endurance

Power Endurance Cost (Toggle Powers):
  1. Get base EndCost and ActivatePeriod from power data
  2. Calculate cost per second:
     ToggleCost = EndCost / ActivatePeriod
  3. Apply EnduranceDiscount effects (same as click powers)
  4. Apply ED to the reduced cost
  5. This is endurance drained per second while toggle active

Example (Tough with 1x EndRdx IO):
  - Base cost: 0.26 endurance
  - Activate period: 0.5 seconds
  - ToggleCost = 0.26 / 0.5 = 0.52 end/sec
  - With 42% EndRdx: 0.52 * (1 - 0.42) = 0.30 end/sec

Endurance Recovery Calculation:
  1. Start with base recovery percentage (100% = 1.0)

  2. Add all recovery modifiers:
     TotalRecovery = 1.0 + Sum(RecoveryEffects)

  3. Calculate numeric recovery per second:
     RecoveryNumeric = TotalRecovery * BaseRecovery * BaseMagic * MaxEndMultiplier
     where:
       BaseRecovery = 1.67 (from archetype, usually same for all ATs)
       BaseMagic = 1.666667 (game constant)
       MaxEndMultiplier = (MaxEnd / 100 + 1)

  4. Calculate net recovery (after usage):
     NetRecovery = RecoveryNumeric - EnduranceUsage

  5. Calculate time to full endurance:
     TimeToFull = MaxEnd / RecoveryNumeric

Example (Scrapper with Stamina + Physical Perfection):
  - Base recovery: 100% (1.0)
  - Stamina: +25% (0.25)
  - Physical Perfection: +10% (0.10)
  - Total recovery: 135% (1.35)
  - Max endurance: 100.0 (base)
  - BaseRecovery: 1.67
  - BaseMagic: 1.666667
  - MaxEndMultiplier: (100/100 + 1) = 2.0
  - RecoveryNumeric = 1.35 * 1.67 * 1.666667 * 2.0 = 7.53 end/sec
  - With 2.5 end/sec usage: NetRecovery = 7.53 - 2.5 = 5.03 end/sec
  - Time to full: 100 / 7.53 = 13.3 seconds

Maximum Endurance Calculation:
  1. Start with base max endurance: 100.0

  2. Sum all Endurance effect magnitudes:
     MaxEnd = 100.0 + Sum(EnduranceEffects)

  3. Display as percentage:
     MaxEndPercent = MaxEnd (since base is 100)

  4. Affects recovery calculation:
     Higher MaxEnd = More endurance to recover = Slower time to full
     But also = More recovery per second (due to MaxEndMultiplier)

Example (Character with +10% max endurance from set bonuses):
  - Base: 100.0
  - IO bonuses: +10.0
  - Total MaxEnd: 110.0
  - Display: "110% Max End" or "110.0 Maximum Endurance"
  - Recovery multiplier: (110/100 + 1) = 2.1 vs base 2.0
  - 5% more endurance recovered per tick
```

### Dependencies

**Archetype Properties**:
- `Archetype.BaseRecovery` - Base recovery rate (typically 1.67 for all ATs)
- This represents endurance recovered at 100% recovery with base max endurance

**Constants**:
- `BaseMagic = 1.666667` - Converts recovery percentage to numeric value (from Statistics.cs)
- Base max endurance = 100.0
- This constant is consistent with the regeneration calculation

**Power Properties**:
- `Power.EndCost` - Base endurance cost
- `Power.ActivatePeriod` - For toggles, seconds between effect applications
- `Power.PowerType` - Determines if ToggleCost calculation applies
- `Power.ToggleCost` - Computed property: `EndCost / ActivatePeriod`

**Enhancement Schedule**:
- EnduranceDiscount uses Schedule A (same as most enhancements)
- ED applies after summing all EndRdx bonuses
- Formula: `Enhancement.ApplyED(Enhancement.GetSchedule(Enums.eEnhance.EnduranceDiscount), powerMath.EndCost)`

**Build Totals**:
```csharp
// From Core/Statistics.cs
EnduranceMaxEnd = _character.Totals.EndMax + 100f

EnduranceRecoveryNumeric = EnduranceRecovery(uncapped: false)
    * (_character.Archetype.BaseRecovery * BaseMagic)
    * (_character.TotalsCapped.EndMax / 100 + 1)

EnduranceRecoveryPercentage = (1.0 + EndRec) * 100f

EnduranceUsage = _character.Totals.EndUse  // Sum of all toggle costs

EnduranceRecoveryNet = EnduranceRecoveryNumeric - EnduranceUsage

EnduranceTimeToFull = EnduranceMaxEnd / EnduranceRecoveryNumeric

EnduranceTimeToZero = EnduranceMaxEnd / -(EnduranceRecoveryNumeric - EnduranceUsage)
```

### Enhancement Scaling

Endurance cost reduction (EnduranceDiscount) is enhanced by:
- **Endurance Reduction enhancements** - Direct cost reduction
- **EndRdx IO sets** - Common in most power categories
- **Set bonuses** - Some sets grant endurance cost reduction
- **Global effects** - Rare, but some powers grant global EndRdx

Enhancement Diversification (ED) significantly impacts endurance reduction:
```
EndRdx Enhancement Levels:
  1 SO (33.33%): ~33% reduction - Effective
  2 SOs (66.66%): ~55% reduction - Good
  3 SOs (100%): ~68% reduction - Diminishing returns
  4+ SOs: Minimal additional benefit

Practical Slotting:
  - 1-2 EndRdx: Good cost reduction
  - 3 EndRdx: Approaching ED penalty
  - 4+ EndRdx: Wasteful, better to improve recovery
```

Recovery enhancement works similarly:
```
Recovery Enhancement (rare, mainly from set bonuses):
  - Affects powers that grant +Recovery
  - Examples: Stamina, Physical Perfection
  - Also subject to ED if slotting multiple enhancements
```

## Game Mechanics Context

**Why This Exists:**

Endurance is City of Heroes' resource management system. Unlike mana in other games, endurance:
1. Is universal (all powers use it, not separate resource pools)
2. Recovers passively at a steady rate
3. Can be modified significantly through powers and enhancements
4. Creates meaningful build choices (damage vs endurance efficiency)

**Three Endurance Mechanisms:**

1. **Power Cost**: How much endurance each power drains
2. **Recovery Rate**: How fast endurance returns (passive)
3. **Max Endurance**: Total endurance pool size

**Historical Context:**

- **Launch (2004)**: Basic endurance system, recovery very slow
- **Issue 2 (2004)**: Stamina made available at level 20 (Fitness pool)
- **Issue 5 (2005)**: Enhancement Diversification reduced effectiveness of EndRdx slotting
- **Issue 19 (2010)**: Fitness pool (Stamina) made inherent for all ATs
- **Issue 19+ (2010)**: Recovery became less critical, focus shifted to efficiency
- **Homecoming (2019+)**: Further endurance cost adjustments, some powersets rebalanced

**Known Quirks:**

1. **BaseRecovery constant (1.67)**: At 100% recovery with base max endurance (100), you recover 100 endurance in approximately 60 seconds. The calculation is: 1.0 * 1.67 * 1.666667 * 2.0 = 5.56 end/sec, or 100 end in ~18 seconds. The "60 seconds to full" is a misconception - actual time is much faster.

2. **BaseMagic (1.666667)**: Same constant used for regeneration calculations. Represents the game's recovery tick rate system (4-second ticks).

3. **Toggle cost per second**: Toggles drain endurance continuously. ActivatePeriod determines tick rate. Most toggles: 0.5 seconds (2 ticks/sec). The ToggleCost property automatically divides EndCost by ActivatePeriod.

4. **Max endurance affects recovery**: Higher max endurance means you recover MORE endurance per second (due to MaxEndMultiplier), but takes longer to fill the larger bar. The net effect is beneficial.

5. **Endurance discount vs Recovery**:
   - Reducing power costs (EndRdx) helps spike endurance users (attack chains)
   - Increasing recovery helps sustained users (toggle-heavy builds)
   - Most builds need balance of both

6. **ED's impact on endurance**: The Enhanced Diversification system heavily penalizes stacking EndRdx enhancements. 3 SOs gives ~68% reduction instead of the 100% you'd expect. This makes recovery bonuses more valuable.

7. **Zero endurance doesn't detoggle**: In modern CoH (post-Issue 13), running out of endurance doesn't automatically drop your toggles. Toggles only drop if you take sufficient damage or are mezzed. However, you can't activate new powers at 0 endurance.

8. **Endurance Modification vs Endurance Discount**:
   - "EndMod" (Endurance Modification) enhancement class affects powers that drain or restore endurance in TARGETS
   - "EndRdx" (Endurance Reduction/Discount) affects the cost of YOUR powers
   - These are distinct enhancement types with different purposes

9. **Recovery caps**: While there's no hard cap on recovery percentage, practical caps exist due to ED limiting slotting effectiveness. Set bonuses and global effects can push recovery well beyond what slotting achieves.

10. **Activate period variations**: Most toggles use 0.5s activate period, but some use different values (1.0s, 2.0s). This affects the END/sec display but not total endurance efficiency over time.

## Python Implementation Notes

**Proposed Architecture:**

```python
# backend/app/calculations/endurance.py

from dataclasses import dataclass
from typing import Optional
from .effects import Effect, EffectType
from .enhancements import EnhancementSchedule, apply_ed

@dataclass
class ArchetypeEnduranceStats:
    """Endurance-related archetype properties"""
    base_recovery: float = 1.67  # Standard for all ATs in CoH

# Game constants from Statistics.cs
BASE_MAGIC = 1.666667  # Converts recovery to numeric value
BASE_MAX_ENDURANCE = 100.0

class EnduranceCalculator:
    """
    Calculate power endurance costs and recovery rates
    Maps to MidsReborn's Statistics.cs endurance calculations
    """

    def calculate_power_cost(
        self,
        base_cost: float,
        end_discount_effects: list[Effect],
        is_toggle: bool = False,
        activate_period: float = 0.0
    ) -> float:
        """
        Calculate modified endurance cost for a power

        Args:
            base_cost: Power's base endurance cost
            end_discount_effects: List of eEffectType.EnduranceDiscount effects
            is_toggle: Whether this is a toggle power
            activate_period: For toggles, seconds between applications

        Returns:
            Modified endurance cost (per activation for clicks, per second for toggles)
        """
        # For toggles, convert to cost per second first
        if is_toggle and activate_period > 0:
            base_cost = base_cost / activate_period

        # Sum all endurance discount bonuses (as percentages)
        total_discount = sum(e.magnitude for e in end_discount_effects)

        # Apply ED to the discount total
        ed_discount = apply_ed(EnhancementSchedule.A, total_discount)

        # Apply discount to cost (discount reduces cost)
        # In MidsReborn: powerMath.EndCost += effect.BuffedMag
        # where BuffedMag is negative for cost reduction
        modified_cost = base_cost * (1.0 - ed_discount)

        return max(0.0, modified_cost)  # Cost can't be negative

    def calculate_recovery_rate(
        self,
        at_stats: ArchetypeEnduranceStats,
        recovery_effects: list[Effect],
        max_endurance: float
    ) -> dict:
        """
        Calculate endurance recovery rate

        Args:
            at_stats: Archetype endurance statistics
            recovery_effects: List of eEffectType.Recovery effects
            max_endurance: Character's current maximum endurance

        Returns:
            Dictionary with:
            - recovery_total: Total recovery percentage (e.g., 1.35 = 135%)
            - recovery_numeric: Endurance recovered per second
            - recovery_percentage: As display percentage (e.g., 135%)
        """
        # Start at 100% base recovery
        recovery_total = 1.0

        # Add all recovery modifiers
        for effect in recovery_effects:
            recovery_total += effect.magnitude

        # Calculate max endurance multiplier
        # This makes higher max endurance recover more end/sec
        max_end_multiplier = (max_endurance / BASE_MAX_ENDURANCE) + 1.0

        # Calculate numeric recovery per second
        # Formula from Statistics.cs:
        # EnduranceRecoveryNumeric = EnduranceRecovery(false)
        #     * (Archetype.BaseRecovery * BaseMagic)
        #     * (TotalsCapped.EndMax / 100 + 1)
        recovery_numeric = (recovery_total
                           * at_stats.base_recovery
                           * BASE_MAGIC
                           * max_end_multiplier)

        # Display percentage
        recovery_percentage = recovery_total * 100.0

        return {
            'recovery_total': recovery_total,
            'recovery_numeric': recovery_numeric,
            'recovery_percentage': recovery_percentage
        }

    def calculate_max_endurance(
        self,
        endurance_effects: list[Effect]
    ) -> float:
        """
        Calculate maximum endurance from Endurance effects

        Args:
            endurance_effects: List of eEffectType.Endurance effects

        Returns:
            Maximum endurance value
        """
        # Start with base max endurance
        max_end = BASE_MAX_ENDURANCE

        # Add all endurance bonuses
        for effect in endurance_effects:
            max_end += effect.magnitude

        return max_end

    def calculate_endurance_usage(
        self,
        toggle_costs: list[float]
    ) -> float:
        """
        Calculate total endurance usage from all active toggles

        Args:
            toggle_costs: List of toggle power costs (already in end/sec)

        Returns:
            Total endurance drained per second
        """
        return sum(toggle_costs)

    def calculate_net_recovery(
        self,
        recovery_numeric: float,
        endurance_usage: float
    ) -> dict:
        """
        Calculate net endurance recovery (recovery - usage)

        Args:
            recovery_numeric: Endurance recovered per second
            endurance_usage: Endurance used per second (toggle costs)

        Returns:
            Dictionary with:
            - net_recovery: End/sec after usage (can be negative)
            - is_positive: Whether net gain or net loss
            - time_to_full: Seconds to full endurance (if positive)
            - time_to_zero: Seconds to empty (if negative)
        """
        net_recovery = recovery_numeric - endurance_usage
        is_positive = net_recovery > 0

        return {
            'net_recovery': net_recovery,
            'is_positive': is_positive
        }

    def calculate_time_to_full(
        self,
        max_endurance: float,
        recovery_numeric: float
    ) -> float:
        """
        Calculate time to recover from 0 to max endurance

        Args:
            max_endurance: Maximum endurance value
            recovery_numeric: Endurance recovered per second

        Returns:
            Seconds to full endurance (or infinity if no recovery)
        """
        if recovery_numeric <= 0:
            return float('inf')

        return max_endurance / recovery_numeric

    def calculate_time_to_zero(
        self,
        max_endurance: float,
        net_recovery: float
    ) -> float:
        """
        Calculate time to drain from max to 0 endurance (net loss scenario)

        Args:
            max_endurance: Maximum endurance value
            net_recovery: Net endurance change per second (negative for drain)

        Returns:
            Seconds to zero endurance (or infinity if net positive)
        """
        if net_recovery >= 0:
            return float('inf')

        # net_recovery is negative, so we need to negate it
        return max_endurance / abs(net_recovery)

    def format_endurance_display(
        self,
        cost: float,
        is_toggle: bool = False
    ) -> str:
        """
        Format endurance cost for display matching MidsReborn style

        Returns:
            "{cost}" or "{cost}/s" for toggles
        """
        if is_toggle:
            return f"{cost:.2f}/s"
        else:
            return f"{cost:.2f}"
```

**Implementation Priority:**

**CRITICAL** - Endurance calculations are fundamental to all power usage and build planning.

**Key Implementation Steps:**

1. Implement ArchetypeEnduranceStats dataclass with BaseRecovery constant
2. Create EnduranceCalculator.calculate_power_cost() with ED integration
3. Create EnduranceCalculator.calculate_recovery_rate() with BaseMagic constant
4. Create EnduranceCalculator.calculate_max_endurance() for max end bonuses
5. Create EnduranceCalculator.calculate_endurance_usage() for toggle totals
6. Create EnduranceCalculator.calculate_net_recovery() for build endurance management
7. Add time-to-full and time-to-zero calculations for build planning
8. Add display formatting methods matching MidsReborn output
9. Integration with enhancement system (Spec 10-11) for EndRdx
10. Integration with archetype data (Spec 16) for BaseRecovery

**Testing Strategy:**

Test cases to validate against MidsReborn:

1. **Click Power Cost Test**:
   - Power: Footstomp (13.0 base cost)
   - No enhancements: 13.0 endurance
   - 1x EndRdx SO (33.33%): ~8.67 endurance
   - 3x EndRdx SO (100% before ED): ~4.16 endurance (ED applied)

2. **Toggle Cost Test**:
   - Power: Tough (0.26 base cost, 0.5s activate period)
   - Base: 0.52 end/sec
   - With 1x EndRdx IO (42%): 0.30 end/sec
   - With 3x EndRdx SO: 0.17 end/sec

3. **Recovery Rate Test**:
   - No recovery bonuses: ~5.56 end/sec (base)
   - With Stamina (+25%): ~7.53 end/sec
   - With Stamina + Physical Perfection (+35%): ~8.48 end/sec

4. **Max Endurance Test**:
   - Base: 100.0
   - With +10% from set bonuses: 110.0
   - With +20% from Accolades: 120.0
   - Verify recovery multiplier changes accordingly

5. **Net Recovery Test**:
   - Recovery: 7.53 end/sec (Stamina)
   - Toggle usage: 2.5 end/sec (3-4 toggles)
   - Net: +5.03 end/sec (positive)
   - Time to full: ~13.3 seconds

6. **Net Loss Test**:
   - Recovery: 5.56 end/sec (base)
   - Toggle usage: 6.0 end/sec (many toggles)
   - Net: -0.44 end/sec (negative)
   - Time to zero: ~227 seconds (nearly 4 minutes)

## References

- **Related Specs**:
  - Spec 01 (Power Effects Core) - Effect system foundation
  - Spec 10 (Enhancement Schedules) - ED application to EndRdx
  - Spec 11 (Enhancement Slotting) - EndRdx enhancement mechanics
  - Spec 16 (Archetype Modifiers) - BaseRecovery values
  - Spec 19 (Build Totals) - Aggregating endurance stats across build
- **MidsReborn Files**:
  - `Core/Statistics.cs` - EnduranceRecoveryNumeric, EnduranceMaxEnd calculations
  - `Core/Base/Data_Classes/Power.cs` - EndCost, ToggleCost properties
  - `Core/Base/Data_Classes/Archetype.cs` - BaseRecovery value
  - `clsToonX.cs` - EnduranceDiscount enhancement application
  - `Core/Enhancement.cs` - ApplyED function for EndRdx
- **Game Documentation**:
  - City of Heroes Wiki - "Endurance", "Recovery", "Stamina"
  - Paragon Wiki - "Endurance Reduction", "Enhancement Diversification"

---

# DEPTH-LEVEL IMPLEMENTATION DETAILS

## Section 1: Algorithm Pseudocode

### Complete Endurance Cost Calculation Algorithm

```python
from typing import List
from enum import Enum

class PowerType(Enum):
    """Power activation types"""
    CLICK = "click"
    TOGGLE = "toggle"
    AUTO = "auto"
    BOOST = "boost"

def calculate_power_endurance_cost(
    base_end_cost: float,
    activate_period: float,
    power_type: PowerType,
    end_discount_effects: List[Effect]
) -> float:
    """
    Calculate modified endurance cost for a power.

    Implementation from:
    - Power.cs lines 270, 391-392 (EndCost, ToggleCost properties)
    - Statistics.cs lines 35-51 (EnduranceUsage aggregation)

    Args:
        base_end_cost: Power's base endurance cost (from Power.EndCost)
        activate_period: For toggles, seconds between ticks (from Power.ActivatePeriod)
        power_type: Click, Toggle, Auto, etc.
        end_discount_effects: List of eEffectType.EnduranceDiscount effects

    Returns:
        Modified endurance cost (per activation for clicks, per second for toggles)
    """
    # STEP 1: For toggles, convert to cost per second
    if power_type == PowerType.TOGGLE and activate_period > 0:
        cost_per_second = base_end_cost / activate_period
    else:
        cost_per_second = base_end_cost

    # STEP 2: Sum all endurance discount bonuses
    # In MidsReborn, EnduranceDiscount effects add to total discount
    # Positive magnitudes reduce cost
    total_discount = 0.0
    for effect in end_discount_effects:
        if effect.effect_type == EffectType.ENDURANCE_DISCOUNT:
            # Effects are already buffed (include enhancements + ED)
            total_discount += effect.buffed_mag

    # STEP 3: Apply discount to cost
    # Discount is percentage reduction: 0.33 = 33% reduction
    modified_cost = cost_per_second * (1.0 - total_discount)

    # STEP 4: Ensure non-negative
    final_cost = max(0.0, modified_cost)

    return final_cost


def calculate_endurance_recovery(
    archetype_base_recovery: float,
    recovery_effects: List[Effect],
    max_endurance: float
) -> dict:
    """
    Calculate endurance recovery rate.

    Implementation from Statistics.cs lines 37-39:
    - EnduranceRecoveryNumeric (line 37)
    - EnduranceRecoveryNumericUncapped (line 39)

    Args:
        archetype_base_recovery: BaseRecovery from Archetype (typically 1.67)
        recovery_effects: List of eEffectType.Recovery effects
        max_endurance: Character's current maximum endurance

    Returns:
        Dictionary with recovery calculations
    """
    # Constants from Statistics.cs line 22
    BASE_MAGIC = 1.666667
    BASE_MAX_ENDURANCE = 100.0

    # STEP 1: Start at 100% base recovery (1.0)
    recovery_total = 1.0

    # STEP 2: Add all recovery modifiers
    for effect in recovery_effects:
        if effect.effect_type == EffectType.RECOVERY:
            # Recovery effects are percentages
            # Example: Stamina = +0.25 (25%)
            recovery_total += effect.magnitude

    # STEP 3: Calculate max endurance multiplier
    # Formula from Statistics.cs line 37:
    # (_character.TotalsCapped.EndMax / 100 + 1)
    max_end_multiplier = (max_endurance / BASE_MAX_ENDURANCE) + 1.0

    # STEP 4: Calculate numeric recovery per second
    # Formula: recovery_total * base_recovery * BASE_MAGIC * max_end_multiplier
    recovery_numeric = (
        recovery_total
        * archetype_base_recovery
        * BASE_MAGIC
        * max_end_multiplier
    )

    # STEP 5: Calculate display percentage
    recovery_percentage = recovery_total * 100.0

    return {
        'recovery_total': recovery_total,           # e.g., 1.35 = 135%
        'recovery_numeric': recovery_numeric,       # e.g., 7.53 end/sec
        'recovery_percentage': recovery_percentage  # e.g., 135.0%
    }


def calculate_max_endurance(
    endurance_effects: List[Effect]
) -> float:
    """
    Calculate maximum endurance.

    Implementation from Statistics.cs line 35:
    EnduranceMaxEnd = _character.Totals.EndMax + 100f

    Args:
        endurance_effects: List of eEffectType.Endurance effects

    Returns:
        Maximum endurance value
    """
    BASE_MAX_ENDURANCE = 100.0

    # STEP 1: Start with base
    max_end = BASE_MAX_ENDURANCE

    # STEP 2: Add all endurance bonuses
    # These are flat additions (not percentages)
    for effect in endurance_effects:
        if effect.effect_type == EffectType.ENDURANCE:
            max_end += effect.magnitude

    return max_end


def calculate_net_recovery(
    recovery_numeric: float,
    toggle_costs: List[float],
    max_endurance: float
) -> dict:
    """
    Calculate net endurance recovery after toggle usage.

    Implementation from Statistics.cs lines 43-49:
    - EnduranceRecoveryNet (line 43)
    - EnduranceTimeToFull (line 41)
    - EnduranceTimeToZero (line 47)

    Args:
        recovery_numeric: Endurance recovered per second
        toggle_costs: List of all active toggle costs (end/sec)
        max_endurance: Maximum endurance

    Returns:
        Dictionary with net calculations
    """
    # STEP 1: Sum toggle usage
    # From Statistics.cs line 51: EnduranceUsage = _character.Totals.EndUse
    endurance_usage = sum(toggle_costs)

    # STEP 2: Calculate net recovery
    # From line 43: EnduranceRecoveryNet = EnduranceRecoveryNumeric - EnduranceUsage
    net_recovery = recovery_numeric - endurance_usage

    # STEP 3: Determine if positive or negative
    is_positive = net_recovery > 0

    # STEP 4: Calculate time to full (if positive)
    # From line 41: EnduranceTimeToFull = EnduranceMaxEnd / EnduranceRecoveryNumeric
    if recovery_numeric > 0:
        time_to_full = max_endurance / recovery_numeric
    else:
        time_to_full = float('inf')

    # STEP 5: Calculate time to zero (if negative)
    # From line 47: EnduranceTimeToZero = EnduranceMaxEnd / -(EnduranceRecoveryNumeric - EnduranceUsage)
    if net_recovery < 0:
        time_to_zero = max_endurance / abs(net_recovery)
    else:
        time_to_zero = float('inf')

    return {
        'endurance_usage': endurance_usage,
        'net_recovery': net_recovery,
        'is_positive': is_positive,
        'time_to_full': time_to_full,
        'time_to_zero': time_to_zero
    }
```

### Edge Cases and Special Handling

**1. Toggle Cost Calculation**
- Must divide by ActivatePeriod to get end/sec
- Most toggles use 0.5s period (2 ticks per second)
- Some toggles use 1.0s or 2.0s periods
- Formula from Power.cs line 391-392:
  ```csharp
  public float ToggleCost
      => !((PowerType == Enums.ePowerType.Toggle) & (ActivatePeriod > 0.0))
          ? EndCost
          : EndCost / ActivatePeriod;
  ```

**2. Max Endurance Multiplier Effect**
- Higher max endurance increases recovery rate
- Formula: `(max_end / 100) + 1`
- Example: 110 max end → multiplier = 2.1 (vs base 2.0)
- This means 5% more endurance recovered per tick

**3. Zero Endurance Handling**
- Modern CoH doesn't detoggle at 0 endurance (post-Issue 13)
- Cannot activate new powers at 0 endurance
- Toggles remain active but no new clicks possible

**4. Endurance Discount Stacking**
- All EndRdx enhancements sum additively
- Subject to Enhancement Diversification (ED)
- ED applied after summing all bonuses
- Example: 3x SO EndRdx = 95.66% before ED → ~56% after ED

**5. Recovery Cap**
- RecoveryCap from Archetype (default 5.0 = 500%)
- Caps recovery percentage, not numeric value
- From Archetype.cs line 37: `RecoveryCap = 5f;`

---

## Section 2: C# Implementation Reference

### Primary Implementation Files

**File: `MidsReborn/Core/Base/Data_Classes/Archetype.cs`**

**Property: `BaseRecovery` (Lines 25, 111, 167)**

```csharp
// Line 25: Default value in constructor
BaseRecovery = 1.67f;

// Line 111: Loaded from binary
BaseRecovery = reader.ReadSingle();

// Line 167: Property definition
public float BaseRecovery { get; set; }
```

**Typical AT BaseRecovery Values:**
- All standard ATs: 1.67 (same across all archetypes)
- This is the base endurance recovery rate at 100% recovery

**File: `MidsReborn/Core/Statistics.cs`**

**Constant: `BaseMagic` (Line 22)**

```csharp
internal const float BaseMagic = 1.666667f;
```

**Property: `EnduranceMaxEnd` (Line 35)**

```csharp
public float EnduranceMaxEnd => _character.Totals.EndMax + 100f;
```
- Adds character's endurance bonuses to base 100
- Example: 10 bonus → 110 max endurance

**Property: `EnduranceRecoveryNumeric` (Line 37)**

```csharp
public float EnduranceRecoveryNumeric =>
    EnduranceRecovery(false)
    * (_character.Archetype.BaseRecovery * BaseMagic)
    * (_character.TotalsCapped.EndMax / 100 + 1);
```

**Method: `EnduranceRecovery()` (Lines 69-72)**

```csharp
private float EnduranceRecovery(bool uncapped)
{
    return uncapped
        ? _character.Totals.EndRec + 1f
        : _character.TotalsCapped.EndRec + 1f;
}
```
- Returns recovery percentage as decimal (1.0 = 100%)
- Adds 1.0 to represent base 100% recovery
- Capped version respects RecoveryCap (line 37 uses capped)

**Property: `EnduranceRecoveryNumericUncapped` (Line 39)**

```csharp
public float EnduranceRecoveryNumericUncapped =>
    EnduranceRecovery(true)
    * (_character.Archetype.BaseRecovery * BaseMagic)
    * (_character.Totals.EndMax / 100 + 1);
```
- Same formula but uses uncapped values
- For display purposes (shows what recovery would be without cap)

**Property: `EnduranceTimeToFull` (Line 41)**

```csharp
public float EnduranceTimeToFull => EnduranceMaxEnd / EnduranceRecoveryNumeric;
```
- Time in seconds to recover from 0 to max endurance
- Assumes no toggle usage

**Property: `EnduranceRecoveryNet` (Line 43)**

```csharp
public float EnduranceRecoveryNet => EnduranceRecoveryNumeric - EnduranceUsage;
```
- Net end/sec after subtracting toggle costs
- Can be negative if toggles consume more than recovery

**Property: `EnduranceTimeToZero` (Line 47)**

```csharp
public float EnduranceTimeToZero =>
    EnduranceMaxEnd / (float)-(EnduranceRecoveryNumeric - (double)EnduranceUsage);
```
- Time to drain from max to 0 with current toggle usage
- Only valid when net recovery is negative

**Property: `EnduranceUsage` (Line 51)**

```csharp
public float EnduranceUsage => _character.Totals.EndUse;
```
- Sum of all active toggle costs (end/sec)
- Aggregated from character totals

**File: `MidsReborn/Core/Base/Data_Classes/Power.cs`**

**Property: `EndCost` (Lines 138, 270)**

```csharp
// Line 138: Constructor copy
EndCost = template.EndCost;

// Line 270: Binary reader
EndCost = reader.ReadSingle();

// Property definition (interface IPower)
public float EndCost { get; set; }
```
- Base endurance cost for the power
- For click powers: cost per activation
- For toggle powers: cost per activate period (not per second)

**Property: `ActivatePeriod` (Lines 143, 275)**

```csharp
// Line 143: Constructor copy
ActivatePeriod = template.ActivatePeriod;

// Line 275: Binary reader
ActivatePeriod = reader.ReadSingle();

// Property definition (interface IPower)
public float ActivatePeriod { get; set; }
```
- For toggles: time in seconds between effect applications
- Most toggles: 0.5 seconds
- Some toggles: 1.0 or 2.0 seconds

**Property: `ToggleCost` (Lines 391-392)**

```csharp
public float ToggleCost
    => !((PowerType == Enums.ePowerType.Toggle) & (ActivatePeriod > 0.0))
        ? EndCost
        : EndCost / ActivatePeriod;
```
- Computed property (not stored)
- For toggles: converts EndCost to end/sec by dividing by ActivatePeriod
- For non-toggles: returns EndCost unchanged
- This is the key formula for toggle endurance consumption

### Key Constants

**BASE_MAGIC: `1.666667`**
- From Statistics.cs line 22
- Converts recovery percentage to numeric end/sec
- Same constant used for regeneration calculations
- Represents game's 4-second tick system (60s / 4s = 15 ticks, but adjusted)

**BASE_RECOVERY: `1.67`**
- From Archetype.cs line 25
- Standard across all archetypes
- At 100% recovery with 100 max endurance:
  - Formula: 1.0 * 1.67 * 1.666667 * 2.0 = 5.56 end/sec
  - Time to full: 100 / 5.56 = ~18 seconds

**BASE_MAX_ENDURANCE: `100.0`**
- Implied constant (not explicitly defined)
- All characters start with 100 max endurance
- Bonuses add to this base

**RECOVERY_CAP: `5.0` (500%)**
- From Archetype.cs line 37
- Most archetypes use 5.0 (500% max recovery)
- Caps recovery percentage, not numeric recovery

---

## Section 3: Database Schema

### Primary Tables

**Table: `endurance_effects`**

```sql
-- Extends power_effects for endurance-specific data
CREATE VIEW v_endurance_effects AS
SELECT
    pe.id,
    pe.power_id,
    pe.effect_type,
    pe.magnitude AS base_magnitude,
    pe.buffed_magnitude,
    COALESCE(pe.buffed_magnitude, pe.magnitude) AS effective_magnitude,
    pe.duration,
    pe.to_who,
    pe.pv_mode,
    pe.effect_class,
    -- Computed flags
    pe.effect_type = 'EnduranceDiscount' AS is_end_discount,
    pe.effect_type = 'Recovery' AS is_recovery,
    pe.effect_type = 'Endurance' AS is_max_end_bonus,
    -- Exclusion check
    pe.effect_class != 'Ignored' AS is_includable
FROM power_effects pe
WHERE pe.effect_type IN ('EnduranceDiscount', 'Recovery', 'Endurance');

-- Index for fast lookups
CREATE INDEX idx_power_effects_endurance_type
    ON power_effects(power_id, effect_type)
    WHERE effect_type IN ('EnduranceDiscount', 'Recovery', 'Endurance');
```

**Table: `archetype_endurance_stats`**

```sql
CREATE TABLE archetype_endurance_stats (
    archetype_id INTEGER PRIMARY KEY REFERENCES archetypes(id) ON DELETE CASCADE,
    base_recovery NUMERIC(10, 6) NOT NULL DEFAULT 1.67,
    recovery_cap NUMERIC(10, 6) NOT NULL DEFAULT 5.0,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT valid_base_recovery CHECK (base_recovery >= 0 AND base_recovery <= 10.0),
    CONSTRAINT valid_recovery_cap CHECK (recovery_cap >= 0 AND recovery_cap <= 10.0)
);

-- Seed data for standard ATs (all have same base recovery)
INSERT INTO archetype_endurance_stats (archetype_id, base_recovery, recovery_cap) VALUES
    (1, 1.67, 5.0),   -- Blaster
    (2, 1.67, 5.0),   -- Scrapper
    (3, 1.67, 5.0),   -- Tanker
    (4, 1.67, 5.0),   -- Corruptor
    (5, 1.67, 5.0),   -- Controller
    (6, 1.67, 5.0),   -- Defender
    (7, 1.67, 5.0),   -- Stalker
    (8, 1.67, 5.0),   -- Brute
    (9, 1.67, 5.0),   -- Dominator
    (10, 1.67, 5.0);  -- Mastermind

CREATE INDEX idx_archetype_endurance_stats_archetype_id
    ON archetype_endurance_stats(archetype_id);
```

**Table: `power_endurance_costs`**

```sql
-- View for power endurance costs (click and toggle)
CREATE VIEW v_power_endurance_costs AS
SELECT
    p.id AS power_id,
    p.power_name,
    p.power_type,
    p.end_cost AS base_end_cost,
    p.activate_period,
    -- Calculate toggle cost (end/sec)
    CASE
        WHEN p.power_type = 'Toggle' AND p.activate_period > 0
            THEN p.end_cost / p.activate_period
        ELSE p.end_cost
    END AS cost_per_second,
    -- Flags
    p.power_type = 'Toggle' AS is_toggle,
    p.power_type IN ('Click', 'Auto') AS is_click,
    p.activate_period AS toggle_tick_rate
FROM powers p
WHERE p.end_cost > 0;

CREATE INDEX idx_powers_end_cost
    ON powers(id, end_cost)
    WHERE end_cost > 0;
```

### Endurance Calculation Functions

**Function: `calculate_power_end_cost`**

```sql
CREATE OR REPLACE FUNCTION calculate_power_end_cost(
    p_power_id INTEGER,
    p_end_discount_total NUMERIC(10, 6) DEFAULT 0.0
) RETURNS NUMERIC(10, 6) AS $$
DECLARE
    v_base_cost NUMERIC(10, 6);
    v_power_type VARCHAR(20);
    v_activate_period NUMERIC(10, 6);
    v_cost_per_second NUMERIC(10, 6);
    v_modified_cost NUMERIC(10, 6);
BEGIN
    -- Get power properties
    SELECT end_cost, power_type, activate_period
    INTO v_base_cost, v_power_type, v_activate_period
    FROM powers
    WHERE id = p_power_id;

    -- Convert to cost per second for toggles
    IF v_power_type = 'Toggle' AND v_activate_period > 0 THEN
        v_cost_per_second := v_base_cost / v_activate_period;
    ELSE
        v_cost_per_second := v_base_cost;
    END IF;

    -- Apply endurance discount
    v_modified_cost := v_cost_per_second * (1.0 - p_end_discount_total);

    -- Ensure non-negative
    RETURN GREATEST(0.0, v_modified_cost);
END;
$$ LANGUAGE plpgsql IMMUTABLE;
```

**Function: `calculate_endurance_recovery`**

```sql
CREATE OR REPLACE FUNCTION calculate_endurance_recovery(
    p_archetype_id INTEGER,
    p_recovery_percentage NUMERIC(10, 6),  -- e.g., 1.35 for 135%
    p_max_endurance NUMERIC(10, 6)
) RETURNS TABLE (
    recovery_total NUMERIC(10, 6),
    recovery_numeric NUMERIC(10, 6),
    recovery_percentage NUMERIC(10, 6)
) AS $$
DECLARE
    v_base_recovery NUMERIC(10, 6);
    v_recovery_cap NUMERIC(10, 6);
    BASE_MAGIC CONSTANT NUMERIC(10, 6) := 1.666667;
    BASE_MAX_ENDURANCE CONSTANT NUMERIC(10, 6) := 100.0;
    v_max_end_multiplier NUMERIC(10, 6);
    v_capped_recovery NUMERIC(10, 6);
BEGIN
    -- Get archetype recovery stats
    SELECT base_recovery, recovery_cap
    INTO v_base_recovery, v_recovery_cap
    FROM archetype_endurance_stats
    WHERE archetype_id = p_archetype_id;

    -- Cap recovery percentage
    v_capped_recovery := LEAST(p_recovery_percentage, v_recovery_cap);

    -- Calculate max endurance multiplier
    v_max_end_multiplier := (p_max_endurance / BASE_MAX_ENDURANCE) + 1.0;

    -- Calculate numeric recovery
    RETURN QUERY
    SELECT
        v_capped_recovery AS recovery_total,
        v_capped_recovery * v_base_recovery * BASE_MAGIC * v_max_end_multiplier AS recovery_numeric,
        v_capped_recovery * 100.0 AS recovery_percentage;
END;
$$ LANGUAGE plpgsql STABLE;
```

**Function: `calculate_net_endurance`**

```sql
CREATE OR REPLACE FUNCTION calculate_net_endurance(
    p_recovery_numeric NUMERIC(10, 6),
    p_endurance_usage NUMERIC(10, 6),
    p_max_endurance NUMERIC(10, 6)
) RETURNS TABLE (
    endurance_usage NUMERIC(10, 6),
    net_recovery NUMERIC(10, 6),
    is_positive BOOLEAN,
    time_to_full NUMERIC(10, 6),
    time_to_zero NUMERIC(10, 6)
) AS $$
DECLARE
    v_net_recovery NUMERIC(10, 6);
    v_time_to_full NUMERIC(10, 6);
    v_time_to_zero NUMERIC(10, 6);
BEGIN
    -- Calculate net recovery
    v_net_recovery := p_recovery_numeric - p_endurance_usage;

    -- Calculate time to full
    IF p_recovery_numeric > 0 THEN
        v_time_to_full := p_max_endurance / p_recovery_numeric;
    ELSE
        v_time_to_full := 'Infinity'::NUMERIC;
    END IF;

    -- Calculate time to zero
    IF v_net_recovery < 0 THEN
        v_time_to_zero := p_max_endurance / ABS(v_net_recovery);
    ELSE
        v_time_to_zero := 'Infinity'::NUMERIC;
    END IF;

    RETURN QUERY
    SELECT
        p_endurance_usage,
        v_net_recovery,
        v_net_recovery > 0 AS is_positive,
        v_time_to_full,
        v_time_to_zero;
END;
$$ LANGUAGE plpgsql IMMUTABLE;
```

---

## Section 4: Comprehensive Test Cases

### Test Case 1: Basic Click Power Endurance Cost

**Power**: Footstomp (Footstomp from Super Strength)
**Level**: 50
**Power Type**: Click

**Input**:
- Base EndCost: 13.0
- ActivatePeriod: N/A (click power)
- EnduranceDiscount effects: None (unslotted)
- Power type: Click

**Calculation**:
```
Step 1: Click power, cost_per_second = base_cost
cost_per_second = 13.0

Step 2: No endurance discount
total_discount = 0.0

Step 3: Apply discount
modified_cost = 13.0 * (1.0 - 0.0) = 13.0

Step 4: Ensure non-negative
final_cost = max(0.0, 13.0) = 13.0
```

**Expected Output**:
- Endurance cost: 13.0 endurance per activation

---

### Test Case 2: Click Power with EndRdx Slotting

**Power**: Footstomp (Super Strength)
**Level**: 50
**Power Type**: Click

**Input**:
- Base EndCost: 13.0
- EnduranceDiscount effects:
  - 3x level 50 Endurance Reduction SOs
  - Pre-ED total: 95.66% (3 × 33.33%)
  - Post-ED total: 56% (after Schedule A ED)
- Power type: Click

**Calculation**:
```
Step 1: Click power
cost_per_second = 13.0

Step 2: Sum endurance discount (after ED)
total_discount = 0.56 (56%)

Step 3: Apply discount
modified_cost = 13.0 * (1.0 - 0.56) = 13.0 * 0.44 = 5.72

Step 4: Ensure non-negative
final_cost = 5.72
```

**Expected Output**:
- Endurance cost: 5.72 endurance per activation
- Reduction: 56% (7.28 endurance saved)

---

### Test Case 3: Toggle Power Base Cost

**Power**: Tough (Fighting pool toggle)
**Level**: 50
**Power Type**: Toggle

**Input**:
- Base EndCost: 0.26
- ActivatePeriod: 0.5 seconds
- EnduranceDiscount effects: None (unslotted)
- Power type: Toggle

**Calculation**:
```
Step 1: Toggle power, convert to end/sec
cost_per_second = 0.26 / 0.5 = 0.52 end/sec

Step 2: No endurance discount
total_discount = 0.0

Step 3: Apply discount
modified_cost = 0.52 * (1.0 - 0.0) = 0.52

Step 4: Ensure non-negative
final_cost = 0.52
```

**Expected Output**:
- Endurance cost: 0.52 end/sec
- Raw cost: 0.26 per 0.5s tick

---

### Test Case 4: Toggle Power with EndRdx Slotting

**Power**: Tough (Fighting pool toggle)
**Level**: 50
**Power Type**: Toggle

**Input**:
- Base EndCost: 0.26
- ActivatePeriod: 0.5 seconds
- EnduranceDiscount effects:
  - 1x level 50 Endurance Reduction IO (42%)
- Power type: Toggle

**Calculation**:
```
Step 1: Toggle power, convert to end/sec
cost_per_second = 0.26 / 0.5 = 0.52 end/sec

Step 2: Sum endurance discount
total_discount = 0.42 (42%)

Step 3: Apply discount
modified_cost = 0.52 * (1.0 - 0.42) = 0.52 * 0.58 = 0.3016

Step 4: Ensure non-negative
final_cost = 0.30
```

**Expected Output**:
- Endurance cost: 0.30 end/sec
- Reduction: 42% (0.22 end/sec saved)

---

### Test Case 5: Base Endurance Recovery (No Bonuses)

**Character**: Scrapper, level 50
**Recovery Bonuses**: None

**Input**:
- Archetype BaseRecovery: 1.67
- Recovery effects: None (no Stamina or other bonuses)
- Max endurance: 100.0 (base)

**Calculation**:
```
Constants:
BASE_MAGIC = 1.666667
BASE_MAX_ENDURANCE = 100.0

Step 1: Base recovery
recovery_total = 1.0 (100%)

Step 2: No recovery modifiers
recovery_total = 1.0

Step 3: Max endurance multiplier
max_end_multiplier = (100.0 / 100.0) + 1.0 = 2.0

Step 4: Calculate numeric recovery
recovery_numeric = 1.0 * 1.67 * 1.666667 * 2.0
recovery_numeric = 5.566667 end/sec

Step 5: Display percentage
recovery_percentage = 1.0 * 100.0 = 100.0%
```

**Expected Output**:
- Recovery total: 1.0 (100%)
- Recovery numeric: 5.57 end/sec
- Recovery percentage: 100%
- Time to full: 100 / 5.57 = 17.95 seconds

---

### Test Case 6: Endurance Recovery with Stamina

**Character**: Scrapper, level 50
**Recovery Bonuses**: Stamina (+25%)

**Input**:
- Archetype BaseRecovery: 1.67
- Recovery effects:
  - Stamina: +0.25 (25% recovery)
- Max endurance: 100.0 (base)

**Calculation**:
```
Step 1: Base recovery
recovery_total = 1.0

Step 2: Add recovery modifiers
recovery_total = 1.0 + 0.25 = 1.25 (125%)

Step 3: Max endurance multiplier
max_end_multiplier = (100.0 / 100.0) + 1.0 = 2.0

Step 4: Calculate numeric recovery
recovery_numeric = 1.25 * 1.67 * 1.666667 * 2.0
recovery_numeric = 6.958334 end/sec

Step 5: Display percentage
recovery_percentage = 1.25 * 100.0 = 125.0%
```

**Expected Output**:
- Recovery total: 1.25 (125%)
- Recovery numeric: 6.96 end/sec
- Recovery percentage: 125%
- Time to full: 100 / 6.96 = 14.37 seconds

---

### Test Case 7: Recovery with Stamina + Physical Perfection

**Character**: Scrapper, level 50
**Recovery Bonuses**: Stamina + Physical Perfection

**Input**:
- Archetype BaseRecovery: 1.67
- Recovery effects:
  - Stamina: +0.25 (25%)
  - Physical Perfection: +0.10 (10%)
- Max endurance: 100.0 (base)

**Calculation**:
```
Step 1: Base recovery
recovery_total = 1.0

Step 2: Add recovery modifiers
recovery_total = 1.0 + 0.25 + 0.10 = 1.35 (135%)

Step 3: Max endurance multiplier
max_end_multiplier = (100.0 / 100.0) + 1.0 = 2.0

Step 4: Calculate numeric recovery
recovery_numeric = 1.35 * 1.67 * 1.666667 * 2.0
recovery_numeric = 7.530001 end/sec

Step 5: Display percentage
recovery_percentage = 1.35 * 100.0 = 135.0%
```

**Expected Output**:
- Recovery total: 1.35 (135%)
- Recovery numeric: 7.53 end/sec
- Recovery percentage: 135%
- Time to full: 100 / 7.53 = 13.28 seconds

---

### Test Case 8: Max Endurance with Bonuses

**Character**: Scrapper, level 50
**Endurance Bonuses**: IO set bonuses

**Input**:
- Endurance effects:
  - 5× +2.25% max endurance IO bonuses = +11.25 total

**Calculation**:
```
BASE_MAX_ENDURANCE = 100.0

Step 1: Start with base
max_end = 100.0

Step 2: Add bonuses (flat additions, not percentages)
max_end = 100.0 + 11.25 = 111.25
```

**Expected Output**:
- Max endurance: 111.25 (displayed as "111.25% Max End")

---

### Test Case 9: Recovery with Increased Max Endurance

**Character**: Scrapper, level 50
**Recovery Bonuses**: Stamina
**Max Endurance**: 110.0 (+10 from set bonuses)

**Input**:
- Archetype BaseRecovery: 1.67
- Recovery effects: Stamina (+0.25)
- Max endurance: 110.0

**Calculation**:
```
Step 1-2: Recovery total
recovery_total = 1.25 (125%)

Step 3: Max endurance multiplier (INCREASED)
max_end_multiplier = (110.0 / 100.0) + 1.0 = 2.1

Step 4: Calculate numeric recovery
recovery_numeric = 1.25 * 1.67 * 1.666667 * 2.1
recovery_numeric = 7.306251 end/sec

Compare to 100 max end:
With 100 max: 6.96 end/sec
With 110 max: 7.31 end/sec
Increase: 5% more recovery per second
```

**Expected Output**:
- Recovery numeric: 7.31 end/sec
- Max endurance: 110.0
- Time to full: 110 / 7.31 = 15.05 seconds
- Note: More end/sec BUT takes longer to fill the bar (110 vs 100)

---

### Test Case 10: Net Recovery (Positive)

**Character**: Scrapper, level 50
**Recovery**: Stamina (7.53 end/sec)
**Toggle Usage**: 3 toggles (2.5 end/sec total)

**Input**:
- Recovery numeric: 7.53 end/sec
- Toggle costs:
  - Tough: 0.30 end/sec (with 42% EndRdx)
  - Weave: 0.26 end/sec (with 42% EndRdx)
  - Combat Jumping: 0.07 end/sec (unslotted)
  - Total: 0.63 end/sec
- Max endurance: 100.0

**Calculation**:
```
Step 1: Sum toggle usage
endurance_usage = 0.30 + 0.26 + 0.07 = 0.63 end/sec

Step 2: Calculate net recovery
net_recovery = 7.53 - 0.63 = 6.90 end/sec

Step 3: Determine if positive
is_positive = True (6.90 > 0)

Step 4: Time to full
time_to_full = 100.0 / 7.53 = 13.28 seconds

Step 5: Time to zero
time_to_zero = Infinity (net positive)
```

**Expected Output**:
- Endurance usage: 0.63 end/sec
- Net recovery: +6.90 end/sec (positive)
- Time to full: 13.28 seconds
- Time to zero: N/A (never drains)

---

### Test Case 11: Net Recovery (Negative)

**Character**: Scrapper, level 50
**Recovery**: Base only (5.57 end/sec, no Stamina)
**Toggle Usage**: Many toggles (6.0 end/sec total)

**Input**:
- Recovery numeric: 5.57 end/sec
- Toggle costs:
  - Multiple armor toggles: 6.0 end/sec total
- Max endurance: 100.0

**Calculation**:
```
Step 1: Sum toggle usage
endurance_usage = 6.0 end/sec

Step 2: Calculate net recovery
net_recovery = 5.57 - 6.0 = -0.43 end/sec

Step 3: Determine if positive
is_positive = False (-0.43 < 0)

Step 4: Time to full
time_to_full = 100.0 / 5.57 = 17.95 seconds

Step 5: Time to zero (NEGATIVE DRAIN)
time_to_zero = 100.0 / abs(-0.43) = 232.56 seconds (3.88 minutes)
```

**Expected Output**:
- Endurance usage: 6.0 end/sec
- Net recovery: -0.43 end/sec (negative, draining)
- Time to zero: 232.56 seconds (~3.9 minutes)
- Time to full: N/A (never fills, always draining)

---

### Test Case 12: Recovery at Cap

**Character**: Scrapper, level 50
**Recovery Bonuses**: Extreme recovery build

**Input**:
- Archetype BaseRecovery: 1.67
- RecoveryCap: 5.0 (500%)
- Recovery effects:
  - Stamina: +0.25
  - Physical Perfection: +0.10
  - Set bonuses: +0.50
  - Other powers: +3.50
  - Total uncapped: +4.35 → 5.35 (535%)
- Max endurance: 100.0

**Calculation**:
```
Step 1: Base recovery
recovery_total = 1.0

Step 2: Add recovery modifiers
recovery_total_uncapped = 1.0 + 4.35 = 5.35 (535%)

Step 2b: Apply cap
recovery_total_capped = min(5.35, 5.0) = 5.0 (500%, capped)

Step 3: Max endurance multiplier
max_end_multiplier = (100.0 / 100.0) + 1.0 = 2.0

Step 4: Calculate numeric recovery
recovery_numeric = 5.0 * 1.67 * 1.666667 * 2.0
recovery_numeric = 27.833335 end/sec

Step 5: Display percentage
recovery_percentage = 5.0 * 100.0 = 500.0%
```

**Expected Output**:
- Recovery total: 5.0 (500%, CAPPED)
- Recovery numeric: 27.83 end/sec
- Recovery percentage: 500% (at cap)
- Uncapped would be: 535% → 29.74 end/sec (wasted)
- Time to full: 100 / 27.83 = 3.59 seconds

---

## Section 5: Python Implementation Guide

### Complete Production-Ready Implementation

```python
# backend/app/calculations/endurance.py

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

from .effects import Effect, EffectType

class PowerType(Enum):
    """Power activation types from Enums.ePowerType"""
    CLICK = "click"
    TOGGLE = "toggle"
    AUTO = "auto"
    BOOST = "boost"

@dataclass
class ArchetypeEnduranceStats:
    """
    Endurance-related archetype properties.
    Maps to Archetype.cs BaseRecovery and RecoveryCap.
    """
    base_recovery: float = 1.67  # Standard for all ATs
    recovery_cap: float = 5.0    # 500% max recovery

@dataclass
class EnduranceCostResult:
    """Result of endurance cost calculation"""
    base_cost: float
    modified_cost: float
    cost_per_second: float  # For toggles
    discount_applied: float  # Percentage discount
    is_toggle: bool

@dataclass
class RecoveryResult:
    """Result of recovery calculation"""
    recovery_total: float       # e.g., 1.35 = 135%
    recovery_numeric: float     # e.g., 7.53 end/sec
    recovery_percentage: float  # e.g., 135.0%
    is_capped: bool
    uncapped_percentage: Optional[float] = None

@dataclass
class NetRecoveryResult:
    """Result of net recovery calculation"""
    endurance_usage: float
    net_recovery: float
    is_positive: bool
    time_to_full: float
    time_to_zero: float

# Game constants from MidsReborn
BASE_MAGIC = 1.666667  # From Statistics.cs line 22
BASE_MAX_ENDURANCE = 100.0
BASE_RECOVERY = 1.67   # From Archetype.cs line 25

class EnduranceCalculator:
    """
    Calculate power endurance costs and recovery rates.

    Implementation based on:
    - Statistics.cs (lines 22, 35-51)
    - Archetype.cs (lines 25, 167)
    - Power.cs (lines 391-392)
    """

    def __init__(self, archetype_stats: Optional[ArchetypeEnduranceStats] = None):
        """
        Args:
            archetype_stats: Archetype endurance properties (recovery, cap)
        """
        self.at_stats = archetype_stats or ArchetypeEnduranceStats()

    def calculate_power_cost(
        self,
        base_end_cost: float,
        activate_period: float,
        power_type: PowerType,
        end_discount_effects: List[Effect]
    ) -> EnduranceCostResult:
        """
        Calculate modified endurance cost for a power.

        Implementation from Power.cs lines 391-392 (ToggleCost property).

        Args:
            base_end_cost: Power's base endurance cost
            activate_period: For toggles, seconds between ticks
            power_type: Click, Toggle, Auto, etc.
            end_discount_effects: List of eEffectType.EnduranceDiscount effects

        Returns:
            EnduranceCostResult with cost details
        """
        is_toggle = power_type == PowerType.TOGGLE

        # STEP 1: For toggles, convert to cost per second
        if is_toggle and activate_period > 0:
            cost_per_second = base_end_cost / activate_period
        else:
            cost_per_second = base_end_cost

        # STEP 2: Sum all endurance discount bonuses
        total_discount = sum(
            e.buffed_mag for e in end_discount_effects
            if e.effect_type == EffectType.ENDURANCE_DISCOUNT
        )

        # STEP 3: Apply discount to cost
        modified_cost = cost_per_second * (1.0 - total_discount)

        # STEP 4: Ensure non-negative
        final_cost = max(0.0, modified_cost)

        return EnduranceCostResult(
            base_cost=base_end_cost,
            modified_cost=final_cost,
            cost_per_second=cost_per_second,
            discount_applied=total_discount,
            is_toggle=is_toggle
        )

    def calculate_recovery_rate(
        self,
        recovery_effects: List[Effect],
        max_endurance: float
    ) -> RecoveryResult:
        """
        Calculate endurance recovery rate.

        Implementation from Statistics.cs lines 37-39, 69-77.

        Args:
            recovery_effects: List of eEffectType.Recovery effects
            max_endurance: Character's current maximum endurance

        Returns:
            RecoveryResult with recovery calculations
        """
        # STEP 1: Start at 100% base recovery
        recovery_total = 1.0

        # STEP 2: Add all recovery modifiers
        for effect in recovery_effects:
            if effect.effect_type == EffectType.RECOVERY:
                recovery_total += effect.magnitude

        # Track uncapped value
        uncapped_percentage = recovery_total * 100.0

        # STEP 2b: Apply recovery cap
        recovery_total_capped = min(recovery_total, self.at_stats.recovery_cap)
        is_capped = recovery_total > self.at_stats.recovery_cap

        # STEP 3: Calculate max endurance multiplier
        max_end_multiplier = (max_endurance / BASE_MAX_ENDURANCE) + 1.0

        # STEP 4: Calculate numeric recovery per second
        # Formula from Statistics.cs line 37:
        # EnduranceRecoveryNumeric = EnduranceRecovery(false)
        #     * (_character.Archetype.BaseRecovery * BaseMagic)
        #     * (_character.TotalsCapped.EndMax / 100 + 1)
        recovery_numeric = (
            recovery_total_capped
            * self.at_stats.base_recovery
            * BASE_MAGIC
            * max_end_multiplier
        )

        # STEP 5: Calculate display percentage
        recovery_percentage = recovery_total_capped * 100.0

        return RecoveryResult(
            recovery_total=recovery_total_capped,
            recovery_numeric=recovery_numeric,
            recovery_percentage=recovery_percentage,
            is_capped=is_capped,
            uncapped_percentage=uncapped_percentage if is_capped else None
        )

    def calculate_max_endurance(
        self,
        endurance_effects: List[Effect]
    ) -> float:
        """
        Calculate maximum endurance from Endurance effects.

        Implementation from Statistics.cs line 35:
        EnduranceMaxEnd = _character.Totals.EndMax + 100f

        Args:
            endurance_effects: List of eEffectType.Endurance effects

        Returns:
            Maximum endurance value
        """
        max_end = BASE_MAX_ENDURANCE

        # Add all endurance bonuses (flat additions)
        for effect in endurance_effects:
            if effect.effect_type == EffectType.ENDURANCE:
                max_end += effect.magnitude

        return max_end

    def calculate_endurance_usage(
        self,
        toggle_costs: List[float]
    ) -> float:
        """
        Calculate total endurance usage from all active toggles.

        Implementation from Statistics.cs line 51:
        EnduranceUsage = _character.Totals.EndUse

        Args:
            toggle_costs: List of toggle power costs (already in end/sec)

        Returns:
            Total endurance drained per second
        """
        return sum(toggle_costs)

    def calculate_net_recovery(
        self,
        recovery_numeric: float,
        toggle_costs: List[float],
        max_endurance: float
    ) -> NetRecoveryResult:
        """
        Calculate net endurance recovery (recovery - usage).

        Implementation from Statistics.cs lines 41-49:
        - EnduranceRecoveryNet (line 43)
        - EnduranceTimeToFull (line 41)
        - EnduranceTimeToZero (line 47)

        Args:
            recovery_numeric: Endurance recovered per second
            toggle_costs: List of all active toggle costs (end/sec)
            max_endurance: Maximum endurance

        Returns:
            NetRecoveryResult with net calculations
        """
        # STEP 1: Sum toggle usage
        endurance_usage = self.calculate_endurance_usage(toggle_costs)

        # STEP 2: Calculate net recovery
        net_recovery = recovery_numeric - endurance_usage

        # STEP 3: Determine if positive or negative
        is_positive = net_recovery > 0

        # STEP 4: Calculate time to full
        # From Statistics.cs line 41:
        # EnduranceTimeToFull = EnduranceMaxEnd / EnduranceRecoveryNumeric
        if recovery_numeric > 0:
            time_to_full = max_endurance / recovery_numeric
        else:
            time_to_full = float('inf')

        # STEP 5: Calculate time to zero (if negative)
        # From Statistics.cs line 47:
        # EnduranceTimeToZero = EnduranceMaxEnd / -(EnduranceRecoveryNumeric - EnduranceUsage)
        if net_recovery < 0:
            time_to_zero = max_endurance / abs(net_recovery)
        else:
            time_to_zero = float('inf')

        return NetRecoveryResult(
            endurance_usage=endurance_usage,
            net_recovery=net_recovery,
            is_positive=is_positive,
            time_to_full=time_to_full,
            time_to_zero=time_to_zero
        )

    def format_endurance_display(
        self,
        cost: float,
        is_toggle: bool = False
    ) -> str:
        """
        Format endurance cost for display matching MidsReborn style.

        Returns:
            Formatted string: "{cost}" or "{cost}/s" for toggles
        """
        if is_toggle:
            return f"{cost:.2f}/s"
        else:
            return f"{cost:.2f}"


# Error Handling
class EnduranceCalculationError(Exception):
    """Base exception for endurance calculation errors"""
    pass

class InvalidPowerConfigError(EnduranceCalculationError):
    """Raised when power configuration is invalid"""
    pass

class InvalidRecoveryConfigError(EnduranceCalculationError):
    """Raised when recovery configuration is invalid"""
    pass

def validate_power_endurance_config(
    base_end_cost: float,
    activate_period: float,
    power_type: PowerType
) -> None:
    """
    Validate power endurance configuration.

    Raises:
        InvalidPowerConfigError: If configuration is invalid
    """
    if base_end_cost < 0:
        raise InvalidPowerConfigError(
            f"Base endurance cost cannot be negative: {base_end_cost}"
        )

    if power_type == PowerType.TOGGLE and activate_period <= 0:
        raise InvalidPowerConfigError(
            f"Toggle powers must have activate_period > 0, got {activate_period}"
        )

def validate_recovery_config(
    max_endurance: float,
    recovery_effects: List[Effect]
) -> None:
    """
    Validate recovery configuration.

    Raises:
        InvalidRecoveryConfigError: If configuration is invalid
    """
    if max_endurance <= 0:
        raise InvalidRecoveryConfigError(
            f"Max endurance must be positive: {max_endurance}"
        )

    for effect in recovery_effects:
        if effect.effect_type == EffectType.RECOVERY:
            if effect.magnitude < -1.0:
                raise InvalidRecoveryConfigError(
                    f"Recovery effect magnitude too negative: {effect.magnitude}"
                )


# Usage Example
if __name__ == "__main__":
    from app.calculations.effects import Effect, EffectType

    # Example: Scrapper with Stamina running Tough
    calculator = EnduranceCalculator(
        archetype_stats=ArchetypeEnduranceStats(
            base_recovery=1.67,
            recovery_cap=5.0
        )
    )

    # Power cost: Tough with EndRdx slotting
    tough_cost = calculator.calculate_power_cost(
        base_end_cost=0.26,
        activate_period=0.5,
        power_type=PowerType.TOGGLE,
        end_discount_effects=[
            Effect(
                effect_type=EffectType.ENDURANCE_DISCOUNT,
                magnitude=0.42,
                buffed_mag=0.42  # 42% from 1x EndRdx IO
            )
        ]
    )
    print(f"Tough cost: {calculator.format_endurance_display(tough_cost.modified_cost, True)}")

    # Recovery: Stamina
    max_end = 100.0
    recovery = calculator.calculate_recovery_rate(
        recovery_effects=[
            Effect(
                effect_type=EffectType.RECOVERY,
                magnitude=0.25  # Stamina: +25%
            )
        ],
        max_endurance=max_end
    )
    print(f"Recovery: {recovery.recovery_numeric:.2f} end/sec ({recovery.recovery_percentage:.1f}%)")

    # Net recovery
    net = calculator.calculate_net_recovery(
        recovery_numeric=recovery.recovery_numeric,
        toggle_costs=[tough_cost.modified_cost],
        max_endurance=max_end
    )
    print(f"Net recovery: {net.net_recovery:.2f} end/sec")
    print(f"Time to full: {net.time_to_full:.2f} seconds")
```

---

## Section 6: Integration Points

### Upstream Dependencies

**1. Effect System (Spec 01)**
- Provides `Effect` objects with `effect_type`, `magnitude`, `buffed_mag`
- Three endurance-related effect types:
  - `EffectType.ENDURANCE_DISCOUNT` - Reduces power cost
  - `EffectType.RECOVERY` - Increases recovery rate
  - `EffectType.ENDURANCE` - Increases max endurance
- Integration: Pass list of `Effect` objects to calculator methods

**2. Enhancement System (Spec 10)**
- Calculates `Effect.buffed_mag` from base magnitude + enhancements
- Applies Enhancement Diversification (ED) curves
- Integration: EnduranceCalculator uses `buffed_mag` as input (already enhanced)

**3. Archetype System (Spec 16)**
- Provides `BaseRecovery` (typically 1.67 for all ATs)
- Provides `RecoveryCap` (typically 5.0 = 500%)
- Integration: Pass `ArchetypeEnduranceStats` to calculator constructor

**4. Power Data**
- Provides `EndCost`, `ActivatePeriod`, `PowerType`
- Required for cost calculations
- Integration: Pass power properties to `calculate_power_cost()`

### Downstream Consumers

**1. Power Tooltips**
- Uses `EnduranceCostResult` for displaying power costs
- Shows "X.XX" for clicks, "X.XX/s" for toggles
- Integration: Call `calculate_power_cost()` and format result

**2. Build Totals (Spec 24)**
- Aggregates endurance stats across entire build
- Shows recovery rate, max endurance, net recovery
- Integration: Sum all toggle costs, calculate total recovery

**3. Build Planning Tools**
- Uses `NetRecoveryResult` for endurance sustainability analysis
- Shows time to full, time to zero
- Integration: Calculate net recovery for different toggle combinations

**4. Attack Chain Analysis**
- Considers endurance cost in attack chain viability
- Factors in recovery between attacks
- Integration: Track endurance expenditure over time

**5. Toggle Management**
- Helps players determine which toggles they can afford
- Shows endurance drain vs recovery
- Integration: Calculate usage for different toggle combinations

### Database Queries

**Load power endurance data:**
```python
# backend/app/db/queries/endurance_queries.py

from sqlalchemy import select
from app.db.models import Power, PowerEffect, ArchetypeEnduranceStats

async def load_power_endurance_info(power_id: int):
    """Load power endurance properties."""
    query = select(Power.end_cost, Power.power_type, Power.activate_period).where(
        Power.id == power_id
    )
    return await db.execute(query)

async def load_endurance_discount_effects(power_id: int):
    """Load EnduranceDiscount effects for a power."""
    query = select(PowerEffect).where(
        PowerEffect.power_id == power_id,
        PowerEffect.effect_type == 'EnduranceDiscount',
        PowerEffect.effect_class != 'Ignored'
    )
    return await db.execute(query)

async def load_archetype_endurance_stats(archetype_id: int):
    """Load archetype endurance properties."""
    query = select(ArchetypeEnduranceStats).where(
        ArchetypeEnduranceStats.archetype_id == archetype_id
    )
    return await db.execute(query)
```

### API Endpoints

**GET /api/v1/powers/{power_id}/endurance**
```python
# backend/app/api/v1/powers.py

from fastapi import APIRouter, Query
from app.calculations.endurance import EnduranceCalculator, PowerType

router = APIRouter()

@router.get("/powers/{power_id}/endurance")
async def get_power_endurance(
    power_id: int,
    end_discount: float = Query(0.0, ge=0.0, le=1.0)
):
    """
    Calculate endurance cost for a power.

    Args:
        power_id: Power ID
        end_discount: Total endurance discount (0.0-1.0)

    Returns:
        Endurance cost information
    """
    # Load power data
    power = await load_power_endurance_info(power_id)

    # Calculate cost
    calculator = EnduranceCalculator()
    result = calculator.calculate_power_cost(
        base_end_cost=power.end_cost,
        activate_period=power.activate_period,
        power_type=PowerType(power.power_type),
        end_discount_effects=[]  # Simplified for this example
    )

    return {
        "power_id": power_id,
        "base_cost": result.base_cost,
        "modified_cost": result.modified_cost,
        "is_toggle": result.is_toggle,
        "display": calculator.format_endurance_display(
            result.modified_cost,
            result.is_toggle
        )
    }
```

**GET /api/v1/builds/{build_id}/endurance-summary**
```python
@router.get("/builds/{build_id}/endurance-summary")
async def get_build_endurance_summary(
    build_id: int,
    archetype_id: int
):
    """
    Calculate endurance summary for entire build.

    Returns recovery rate, max endurance, toggle usage, net recovery
    """
    # Load build data
    recovery_effects = await load_build_recovery_effects(build_id)
    endurance_effects = await load_build_endurance_effects(build_id)
    toggle_costs = await load_build_toggle_costs(build_id)
    at_stats = await load_archetype_endurance_stats(archetype_id)

    # Calculate
    calculator = EnduranceCalculator(at_stats)

    max_end = calculator.calculate_max_endurance(endurance_effects)
    recovery = calculator.calculate_recovery_rate(recovery_effects, max_end)
    net = calculator.calculate_net_recovery(
        recovery.recovery_numeric,
        toggle_costs,
        max_end
    )

    return {
        "max_endurance": max_end,
        "recovery": {
            "numeric": recovery.recovery_numeric,
            "percentage": recovery.recovery_percentage,
            "is_capped": recovery.is_capped
        },
        "usage": net.endurance_usage,
        "net_recovery": net.net_recovery,
        "is_sustainable": net.is_positive,
        "time_to_full": net.time_to_full if net.is_positive else None,
        "time_to_zero": net.time_to_zero if not net.is_positive else None
    }
```

### Cross-Spec Data Flow

**Forward dependencies (this spec uses):**
```
Spec 01 (Effects) → Effect objects (EnduranceDiscount, Recovery, Endurance)
Spec 10 (Enhancements) → Effect.buffed_mag (ED applied)
Spec 16 (AT Modifiers) → BaseRecovery, RecoveryCap
```

**Backward dependencies (other specs use this):**
```
Spec 24 (Build Totals) → Aggregates endurance across build
Spec 41 (Attack Chains) → Tracks endurance consumption over time
```

### Implementation Order

**Phase 1: Core (Sprint 1)**
1. Implement `EnduranceCalculator.calculate_power_cost()` for power costs
2. Implement toggle cost conversion (EndCost / ActivatePeriod)
3. Unit tests for click and toggle powers with various EndRdx values

**Phase 2: Recovery (Sprint 1)**
4. Implement `EnduranceCalculator.calculate_recovery_rate()` for recovery
5. Implement max endurance calculation
6. Unit tests for recovery with Stamina and other bonuses

**Phase 3: Net Recovery (Sprint 2)**
7. Implement `EnduranceCalculator.calculate_net_recovery()` for build analysis
8. Add time to full and time to zero calculations
9. Unit tests for net recovery scenarios (positive and negative)

**Phase 4: Database (Sprint 2)**
10. Create database views for endurance effects
11. Implement PostgreSQL endurance calculation functions
12. Database integration tests

**Phase 5: API (Sprint 3)**
13. Create `/powers/{id}/endurance` endpoint
14. Create `/builds/{id}/endurance-summary` endpoint
15. API integration tests

---

## Status: 🟢 Depth Complete

This specification now contains production-ready implementation details:

- **Algorithm Pseudocode**: Complete step-by-step calculation with all edge cases
- **C# Reference**: Extracted exact code from MidsReborn with line numbers and constants
- **Database Schema**: CREATE-ready tables, views, and functions for PostgreSQL
- **Test Cases**: 12 comprehensive scenarios with exact expected values and full calculations
- **Python Implementation**: Production-ready code with type hints, error handling, and docstrings
- **Integration Points**: Complete data flow and API endpoint specifications

**Key Formulas Discovered:**
1. Toggle cost formula: `EndCost / ActivatePeriod` (Power.cs line 391-392)
2. Recovery numeric: `recovery_total × BaseRecovery × BaseMagic × max_end_multiplier` (Statistics.cs line 37)
3. Base recovery: `1.67` for all archetypes (Archetype.cs line 25)
4. Base magic: `1.666667` (Statistics.cs line 22)
5. Max endurance multiplier: `(max_end / 100) + 1` (Statistics.cs line 37)
6. Time to full: `max_end / recovery_numeric` (Statistics.cs line 41)
7. Time to zero: `max_end / abs(net_recovery)` (Statistics.cs line 47)
8. Recovery cap: `5.0` (500%) for most archetypes (Archetype.cs line 37)

**Lines Added**: ~1,680 lines of depth-level implementation detail

**Implementation Notes**:
- All endurance-related constants extracted from MidsReborn source
- Toggle cost calculation is key formula (divides by activate period)
- Max endurance affects recovery rate (higher max = more end/sec)
- Recovery cap prevents excessive stacking (500% max)
- Net recovery can be negative (toggles cost more than recovery)

**Ready for Milestone 3 implementation.**
