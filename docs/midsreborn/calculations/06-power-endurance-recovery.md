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
