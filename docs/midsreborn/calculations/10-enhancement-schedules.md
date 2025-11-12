# Enhancement Schedules (ED Curves)

**Status:** CRITICAL - Foundation for ALL enhancement calculations
**Priority:** Must be implemented before any enhancement math
**Complexity:** High (piecewise functions with attribute-specific schedules)

## Overview

Enhancement Diversification (ED) is THE fundamental mechanic that determines how multiple enhancements stack. Introduced in Issue 5 (September 2005), ED applies diminishing returns to prevent players from "six-slotting" powers with the same enhancement type.

**This is the most important calculation in the entire system.** Every enhancement value must pass through ED curves before being applied to a power.

## Historical Context

### Before Issue 5 (Pre-ED Era)
- Enhancements stacked linearly without limit
- Players would slot 6 identical SOs (+33.3% each) = +200% total
- This created extreme power imbalance and trivialized content
- "Six-slot everything with damage" was the dominant strategy

### Issue 5 "The Great Nerf" (September 2005)
- ED introduced to force build diversity
- Player reaction was EXTREMELY negative initially
- Many players quit over this change
- Eventually accepted as necessary for game balance
- Cryptic's philosophy: "Reward diversification, punish specialization"

### Why ED Exists
1. Force players to diversify slotting (damage + accuracy + recharge)
2. Prevent trivial content from over-enhancement
3. Make set IOs more attractive (they often bypass ED with set bonuses)
4. Balance PvP encounters

## The Four ED Schedules

Each attribute type uses one of four ED curves, each with different thresholds where diminishing returns kick in.

### Schedule A - "Standard" (Most Offensive Attributes)
**Used by:** Damage, Accuracy, Endurance Cost Reduction, Heal, Recharge Time, Endurance Modification, Recovery, Regeneration, Hit Points, Speed (Run/Jump/Fly), Slow, Absorb

**Thresholds:**
- EDThresh_1: 70% (0.70)
- EDThresh_2: 90% (0.90)
- EDThresh_3: 100% (1.00)

**Why most attributes use A:** These are the primary "power" stats players want to maximize. Schedule A is moderately aggressive to prevent over-enhancement.

### Schedule B - "Defensive" (Defense/Accuracy/Resistance)
**Used by:** Defense, To-Hit Buff, Range, Resistance (Damage)

**Thresholds:**
- EDThresh_1: 40% (0.40) - MOST AGGRESSIVE
- EDThresh_2: 50% (0.50)
- EDThresh_3: 60% (0.60)

**Why defense uses B:** Defense is extremely powerful in CoH due to defense debuff resistance and cascading defense failure mechanics. Even small defense values are valuable, so ED hits hard and early.

### Schedule C - "Interrupt Time"
**Used by:** Interrupt Time Reduction (niche mechanic)

**Thresholds:**
- EDThresh_1: 80% (0.80) - LEAST AGGRESSIVE
- EDThresh_2: 100% (1.00)
- EDThresh_3: 120% (1.20)

**Why interrupt uses C:** Interrupt is a niche mechanic only affecting powers like Assassin's Strike and Snipes. Schedule C is lenient because it's already limited in application.

### Schedule D - "Special Mez" (Afraid/Confused Only)
**Used by:** Mez Duration for Afraid (Fear) and Confused (Confuse) effects only

**Thresholds:**
- EDThresh_1: 120% (1.20) - EXTREMELY LENIENT
- EDThresh_2: 150% (1.50)
- EDThresh_3: 180% (1.80)

**Why afraid/confused use D:** These are control effects. Fear is considered weak (enemies can still attack when damaged), and Confuse is PvE-only. Schedule D allows higher values before ED kicks in.

**Note:** Other mez types (Hold, Stun, Sleep, Immobilize) use Schedule A, NOT Schedule D!

## ED Curve Mathematics

### The Piecewise Function

For each schedule, ED applies a **piecewise linear function** with four regions:

```
Region 1 (Below Threshold 1): No ED
  output = input

Region 2 (Threshold 1 to 2): Light ED (90% efficiency)
  output = thresh1 + (input - thresh1) * 0.90

Region 3 (Threshold 2 to 3): Medium ED (70% efficiency)
  output = (thresh1 + (thresh2 - thresh1) * 0.90) + (input - thresh2) * 0.70

Region 4 (Above Threshold 3): Heavy ED (15% efficiency)
  output = (thresh1 + (thresh2 - thresh1) * 0.90 + (thresh3 - thresh2) * 0.70) + (input - thresh3) * 0.15
```

### Visual Representation

```
Schedule A (Damage/Accuracy/etc):
0%─────────70%─────90%──100%───────────────────→
   100%eff   │  90%  │  70% │      15%

Schedule B (Defense/Resistance):
0%──────40%──50%─60%──────────────────→
   100%  │ 90%│ 70%│      15%
   (ED hits EARLY and HARD)

Schedule C (Interrupt):
0%──────────────80%────────100%────120%───────→
   100%         │  90%     │  70%  │    15%
   (Lenient, hits late)

Schedule D (Afraid/Confused):
0%───────────────────────120%─────────150%──180%────→
   100%                    │  90%    │  70% │  15%
   (Very lenient, for weak mez types)
```

## Implementation from MidsReborn

### Schedule Assignment Logic

```csharp
public static Enums.eSchedule GetSchedule(Enums.eEnhance iEnh, int tSub = -1)
{
    switch (iEnh)
    {
        case Enums.eEnhance.Defense:
            return Enums.eSchedule.B;

        case Enums.eEnhance.Interrupt:
            return Enums.eSchedule.C;

        case Enums.eEnhance.Mez:
            // tSub: 0=Sleep, 1=Hold, 2=Stun, 3=Immob, 4=Afraid, 5=Confused
            return (tSub == 4 || tSub == 5) ? Enums.eSchedule.D : Enums.eSchedule.A;

        case Enums.eEnhance.Range:
        case Enums.eEnhance.Resistance:
        case Enums.eEnhance.ToHit:
            return Enums.eSchedule.B;

        default:
            // All other attributes (Damage, Accuracy, Recharge, Heal, etc.)
            return Enums.eSchedule.A;
    }
}
```

### ED Application Algorithm

```csharp
public static float ApplyED(Enums.eSchedule iSched, float iVal)
{
    if (iSched == Enums.eSchedule.None || iSched == Enums.eSchedule.Multiple)
        return 0.0f;

    // Load thresholds from database
    float thresh1 = Database.MultED[(int)iSched][0];
    float thresh2 = Database.MultED[(int)iSched][1];
    float thresh3 = Database.MultED[(int)iSched][2];

    // Region 1: Below first threshold - no ED
    if (iVal <= thresh1)
        return iVal;

    // Pre-calculate cumulative ED values at each threshold
    float edm1 = thresh1;
    float edm2 = thresh1 + (thresh2 - thresh1) * 0.90f;
    float edm3 = edm2 + (thresh3 - thresh2) * 0.70f;

    // Region 2: Light ED (90% efficiency)
    if (iVal <= thresh2)
        return edm1 + (iVal - thresh1) * 0.90f;

    // Region 3: Medium ED (70% efficiency)
    if (iVal <= thresh3)
        return edm2 + (iVal - thresh2) * 0.70f;

    // Region 4: Heavy ED (15% efficiency)
    return edm3 + (iVal - thresh3) * 0.15f;
}
```

### Threshold Data (from Maths.mhd)

```
ED Reduction Thresholds
EDRT    A      B      C      D
Thresh1 0.700  0.400  0.800  1.200
Thresh2 0.900  0.500  1.000  1.500
Thresh3 1.000  0.600  1.200  1.800
```

## Practical Examples

### Example 1: Three SOs in Damage (Schedule A)

**Input:** 3 × 33.3% = 99.9% ≈ 1.00 enhancement

**Calculation:**
1. Input (1.00) > Threshold 1 (0.70) → ED applies
2. Input (1.00) > Threshold 2 (0.90) → Medium ED applies
3. Input (1.00) ≤ Threshold 3 (1.00) → Stop at Region 3

```
output = 0.70 + (0.90 - 0.70) * 0.90 + (1.00 - 0.90) * 0.70
       = 0.70 + 0.18 + 0.07
       = 0.95 (95% damage instead of 100%)
```

**Result:** 95% damage enhancement (5% loss to ED)

### Example 2: Six SOs in Damage (Pre-ED vs Post-ED)

**Input:** 6 × 33.3% = 199.8% ≈ 2.00 enhancement

**Pre-ED (Linear):** 200% damage bonus

**Post-ED Calculation:**
1. Input (2.00) > Threshold 3 (1.00) → Heavy ED applies

```
output = 0.70 + (0.90 - 0.70) * 0.90 + (1.00 - 0.90) * 0.70 + (2.00 - 1.00) * 0.15
       = 0.70 + 0.18 + 0.07 + 0.15
       = 1.10 (110% damage)
```

**Result:** 110% damage enhancement instead of 200% (45% loss to ED!)

**This is why "six-slotting" died with Issue 5.**

### Example 3: Three SOs in Defense (Schedule B - Aggressive)

**Input:** 3 × 33.3% = 99.9% ≈ 1.00 enhancement

**Calculation:**
1. Input (1.00) > Threshold 3 (0.60) → Heavy ED applies

```
output = 0.40 + (0.50 - 0.40) * 0.90 + (0.60 - 0.50) * 0.70 + (1.00 - 0.60) * 0.15
       = 0.40 + 0.09 + 0.07 + 0.06
       = 0.62 (62% defense)
```

**Result:** 62% defense enhancement instead of 100% (38% loss!)

**Defense is MUCH more heavily penalized than damage.**

### Example 4: Comparing Schedules at 100%

| Schedule | Input | Output | Loss to ED | Attribute Examples |
|----------|-------|--------|------------|-------------------|
| **A** | 100% | 95% | 5% | Damage, Accuracy, Recharge |
| **B** | 100% | 62% | 38% | Defense, Resistance, To-Hit |
| **C** | 100% | 92% | 8% | Interrupt Time |
| **D** | 100% | 100% | 0% | Afraid, Confused |

**Key Insight:** Defense/Resistance lose 7.6× more to ED than Damage at 100%!

## Edge Cases and Special Behaviors

### 1. Multiple Schedule Enhancements
When an enhancement has effects on multiple schedules (e.g., Recharge/Accuracy IO):
- Each effect is calculated independently with its own schedule
- The enhancement property `Schedule` returns `Enums.eSchedule.Multiple`
- Never mix ED calculations across schedules

### 2. Post-ED Sources
Some buffs are explicitly marked as "post-ED" (set bonuses, incarnate powers):
- These bypass ED entirely
- Applied AFTER ED calculations on slotted enhancements
- Example: 5-piece defense bonus adds after ED

### 3. ED Penalties Below 100%
ED can technically apply even at values like 50% if schedule B is aggressive enough:
```
Schedule B with 50% input:
  50% > Threshold 2 (40%) → Light ED applies
  output = 0.40 + (0.50 - 0.40) * 0.90 = 0.49 (49%)
  Loss: 1% to ED
```

**Even moderate slotting gets hit by Schedule B.**

### 4. Negative Values
ED never applies to negative values (debuffs on enemies):
```python
if value < 0:
    return value  # No ED on debuffs
```

## Database Schema

### Enhancement Effect Structure
```python
@dataclass
class EnhancementEffect:
    enhance_type: str  # e.g., "Damage", "Defense"
    enhance_subtype: Optional[int]  # For Mez: 0=Sleep, 4=Afraid, 5=Confused
    schedule: str  # "A", "B", "C", "D"
    multiplier: float  # Usually 1.0, but can vary
    magnitude: float  # Base enhancement value (before ED)
```

### ED Threshold Table
```sql
CREATE TABLE ed_schedules (
    schedule CHAR(1) PRIMARY KEY,  -- 'A', 'B', 'C', 'D'
    threshold_1 REAL NOT NULL,      -- First ED breakpoint
    threshold_2 REAL NOT NULL,      -- Second ED breakpoint
    threshold_3 REAL NOT NULL,      -- Third ED breakpoint
    description TEXT
);

INSERT INTO ed_schedules VALUES
    ('A', 0.70, 0.90, 1.00, 'Standard - Most offensive attributes'),
    ('B', 0.40, 0.50, 0.60, 'Defensive - Defense/Resistance/ToHit'),
    ('C', 0.80, 1.00, 1.20, 'Interrupt - Interrupt time only'),
    ('D', 1.20, 1.50, 1.80, 'Special Mez - Afraid/Confused only');
```

## Python Implementation

```python
from enum import Enum
from typing import Optional

class EDSchedule(Enum):
    """Enhancement Diversification schedules."""
    NONE = -1
    A = 0  # Standard: Damage, Accuracy, Recharge, etc.
    B = 1  # Defensive: Defense, Resistance, ToHit, Range
    C = 2  # Interrupt: Interrupt time reduction
    D = 3  # Special Mez: Afraid, Confused only
    MULTIPLE = 4  # Multiple schedules in one enhancement

# ED thresholds from Maths.mhd
ED_THRESHOLDS = {
    EDSchedule.A: (0.70, 0.90, 1.00),
    EDSchedule.B: (0.40, 0.50, 0.60),
    EDSchedule.C: (0.80, 1.00, 1.20),
    EDSchedule.D: (1.20, 1.50, 1.80),
}

def apply_ed(schedule: EDSchedule, value: float) -> float:
    """
    Apply Enhancement Diversification to an enhancement value.

    Args:
        schedule: Which ED curve to use (A/B/C/D)
        value: Total enhancement value (e.g., 0.999 for three SOs)

    Returns:
        Enhancement value after ED diminishing returns

    Examples:
        >>> apply_ed(EDSchedule.A, 1.0)  # Three SOs in damage
        0.95
        >>> apply_ed(EDSchedule.B, 1.0)  # Three SOs in defense
        0.62
        >>> apply_ed(EDSchedule.A, 2.0)  # Six SOs in damage
        1.10
    """
    if schedule in (EDSchedule.NONE, EDSchedule.MULTIPLE):
        return 0.0

    thresh1, thresh2, thresh3 = ED_THRESHOLDS[schedule]

    # Region 1: Below first threshold - no ED
    if value <= thresh1:
        return value

    # Pre-calculate cumulative ED values at thresholds
    edm1 = thresh1
    edm2 = thresh1 + (thresh2 - thresh1) * 0.90
    edm3 = edm2 + (thresh3 - thresh2) * 0.70

    # Region 2: Light ED (90% efficiency)
    if value <= thresh2:
        return edm1 + (value - thresh1) * 0.90

    # Region 3: Medium ED (70% efficiency)
    if value <= thresh3:
        return edm2 + (value - thresh2) * 0.70

    # Region 4: Heavy ED (15% efficiency)
    return edm3 + (value - thresh3) * 0.15


def get_schedule(enhance_type: str, enhance_subtype: Optional[int] = None) -> EDSchedule:
    """
    Determine which ED schedule applies to an enhancement type.

    Args:
        enhance_type: Enhancement attribute (e.g., "Damage", "Defense")
        enhance_subtype: For Mez, the mez type (4=Afraid, 5=Confused)

    Returns:
        EDSchedule enum value

    Examples:
        >>> get_schedule("Damage")
        EDSchedule.A
        >>> get_schedule("Defense")
        EDSchedule.B
        >>> get_schedule("Mez", 4)  # Afraid
        EDSchedule.D
        >>> get_schedule("Mez", 1)  # Hold
        EDSchedule.A
    """
    if enhance_type == "Defense":
        return EDSchedule.B
    elif enhance_type == "Interrupt":
        return EDSchedule.C
    elif enhance_type == "Mez":
        # Afraid (4) and Confused (5) use Schedule D
        # All other mez types use Schedule A
        if enhance_subtype in (4, 5):
            return EDSchedule.D
        return EDSchedule.A
    elif enhance_type in ("Range", "Resistance", "ToHit"):
        return EDSchedule.B
    else:
        # All other attributes: Damage, Accuracy, Recharge, Heal, etc.
        return EDSchedule.A


def calculate_ed_loss(schedule: EDSchedule, value: float) -> tuple[float, float, float]:
    """
    Calculate how much enhancement value is lost to ED.

    Returns:
        (post_ed_value, pre_ed_value, percent_lost)

    Examples:
        >>> calculate_ed_loss(EDSchedule.A, 2.0)
        (1.10, 2.0, 45.0)  # Six-slotting loses 45%!
    """
    post_ed = apply_ed(schedule, value)
    loss = value - post_ed
    percent_lost = (loss / value * 100) if value > 0 else 0.0
    return post_ed, value, percent_lost
```

## Testing Requirements

### Unit Tests

```python
def test_ed_schedule_a_three_sos():
    """Three SOs (100% enhancement) on Schedule A."""
    result = apply_ed(EDSchedule.A, 1.0)
    assert abs(result - 0.95) < 0.01

def test_ed_schedule_a_six_sos():
    """Six SOs (200% enhancement) on Schedule A - the classic case."""
    result = apply_ed(EDSchedule.A, 2.0)
    assert abs(result - 1.10) < 0.01

def test_ed_schedule_b_aggressive():
    """Schedule B hits harder - defense at 100% = 62%."""
    result = apply_ed(EDSchedule.B, 1.0)
    assert abs(result - 0.62) < 0.01

def test_ed_schedule_d_lenient():
    """Schedule D is lenient - no ED until 120%."""
    result = apply_ed(EDSchedule.D, 1.0)
    assert result == 1.0  # No ED yet!

    result = apply_ed(EDSchedule.D, 1.5)
    assert abs(result - 1.47) < 0.01  # Only 3% loss at 150%

def test_ed_below_threshold():
    """No ED applied below first threshold."""
    result = apply_ed(EDSchedule.A, 0.5)
    assert result == 0.5

    result = apply_ed(EDSchedule.B, 0.3)
    assert result == 0.3

def test_schedule_assignment():
    """Verify correct schedule for each attribute."""
    assert get_schedule("Damage") == EDSchedule.A
    assert get_schedule("Defense") == EDSchedule.B
    assert get_schedule("Interrupt") == EDSchedule.C
    assert get_schedule("Mez", 4) == EDSchedule.D  # Afraid
    assert get_schedule("Mez", 1) == EDSchedule.A  # Hold
    assert get_schedule("Resistance") == EDSchedule.B
```

### Integration Tests

```python
def test_realistic_build_damage():
    """Simulate a realistic damage slotting: 1 Acc, 3 Damage SOs."""
    # Damage enhancements only
    damage_value = 3 * 0.333  # Three damage SOs = 99.9%
    post_ed = apply_ed(EDSchedule.A, damage_value)

    # Should be ~95% after ED
    assert 0.94 < post_ed < 0.96

def test_realistic_build_defense():
    """Defense slotting is heavily penalized - shows why defense sets are valuable."""
    # Three defense SOs
    defense_value = 3 * 0.333
    post_ed = apply_ed(EDSchedule.B, defense_value)

    # Should be ~62% after ED (38% loss!)
    assert 0.61 < post_ed < 0.63

def test_frankenslotting():
    """Frankenslotting: Mix of IOs to hit ED threshold exactly."""
    # Try to hit 94% damage (right at edge of heavy ED)
    # Use different level IOs
    value = 0.42 + 0.38 + 0.15  # Level 50 + 45 + 25 IOs = 95%
    post_ed = apply_ed(EDSchedule.A, value)

    # Should stay close to input (optimized for ED)
    assert post_ed > 0.90
```

## UI/UX Considerations

### Display ED Warnings

**When to warn:**
- Light ED (Threshold 1-2): Yellow/orange indicator
- Medium ED (Threshold 2-3): Orange/red indicator
- Heavy ED (Above Threshold 3): Red indicator + tooltip warning

**Example tooltip:**
```
"Enhancement Diversification is reducing this value.
Current: 62% (after ED)
Without ED: 100%
Loss to ED: 38%

Consider diversifying slots (add Recharge, Endurance, etc.)"
```

### Visual ED Indicator

```
[████████░░] 95% Damage (+100% before ED, -5% to light ED)
[██████░░░░] 62% Defense (+100% before ED, -38% to HEAVY ED!)
```

### ED Comparison Table
```
| Slotting | Pre-ED | Post-ED | Loss | Efficiency |
|----------|--------|---------|------|------------|
| 1 SO     | 33.3%  | 33.3%   | 0%   | 100%       |
| 2 SOs    | 66.6%  | 66.6%   | 0%   | 100%       |
| 3 SOs    | 100%   | 95%     | 5%   | 95%        |
| 4 SOs    | 133%   | 100%    | 25%  | 75%        |
| 5 SOs    | 166%   | 105%    | 37%  | 63%        |
| 6 SOs    | 200%   | 110%    | 45%  | 55%        |
```

**Key message:** "3-4 slots optimal, 5-6 slots wasteful"

## Related Specs

- **[02] Power Effects System**: Where ED gets applied to effect magnitudes
- **[03] Base Values & Caps**: ED works with attribute caps
- **[11] Enhancement Types**: Different enhancement types, same ED rules
- **[19] Set Bonuses**: Set bonuses bypass ED (post-ED application)
- **[31] Build Totals**: ED calculated per attribute, then aggregated

## Common Pitfalls

1. **Applying ED twice**: ED is applied once per attribute when summing enhancements, NOT per enhancement
2. **Forgetting schedule differences**: Defense ED ≠ Damage ED
3. **Ignoring post-ED sources**: Set bonuses add AFTER ED
4. **Mixing pre/post ED**: Never add pre-ED and post-ED values directly
5. **Negative values**: ED doesn't apply to debuffs (negative enhancements)

## Performance Notes

- ED calculation is cheap (4 comparisons, 3 multiplications max)
- Pre-calculate threshold lookup table on startup
- Cache schedule assignments per attribute type
- Only calculate ED once per attribute when aggregating enhancements

## References

- `MidsReborn/Core/Enhancement.cs`: `ApplyED()` and `GetSchedule()`
- `MidsReborn/Data/Homecoming/Maths.mhd`: ED threshold data
- City of Heroes Issue 5 patch notes (September 2005)
- Red name posts explaining ED rationale (archived CoH forums)
- ParagonWiki: "Enhancement Diversification" article

---

**CRITICAL IMPLEMENTATION NOTE:** This spec must be implemented FIRST before any other enhancement calculations. All enhancement values MUST flow through ED before being applied to powers. There is no bypassing ED except for explicitly marked post-ED sources.

---

# DEPTH-LEVEL IMPLEMENTATION DETAILS

## Section 1: Detailed Algorithm Specification

### Complete ED Formula with Exact Coefficients

The Enhancement Diversification algorithm applies a **four-region piecewise linear function** with exact floating-point coefficients extracted from MidsReborn:

```
Given:
  - schedule: One of {A, B, C, D}
  - value: Total enhancement value (sum of all enhancements)
  - T1, T2, T3: Thresholds for the schedule

Algorithm:
  1. IF value <= T1:
       RETURN value  // No ED applied

  2. Pre-calculate cumulative breakpoints:
       EDM1 = T1
       EDM2 = T1 + (T2 - T1) × 0.90
       EDM3 = EDM2 + (T3 - T2) × 0.70

  3. IF value <= T2:
       RETURN EDM1 + (value - T1) × 0.90  // Light ED: 90% efficiency

  4. IF value <= T3:
       RETURN EDM2 + (value - T2) × 0.70  // Medium ED: 70% efficiency

  5. ELSE:
       RETURN EDM3 + (value - T3) × 0.15  // Heavy ED: 15% efficiency
```

### Exact Efficiency Factors

These are the **exact floating-point constants** from Enhancement.cs line 477-484:

```
Region 1 (below T1):     Multiplier = 1.00  (100% efficiency - no ED)
Region 2 (T1 to T2):     Multiplier = 0.899999976158142  (≈ 0.90)
Region 3 (T2 to T3):     Multiplier = 0.699999988079071  (≈ 0.70)
Region 4 (above T3):     Multiplier = 0.150000005960464  (≈ 0.15)
```

**Note:** MidsReborn uses these slightly imprecise floating-point literals. For practical purposes, use `0.90`, `0.70`, and `0.15` as they are functionally identical.

### Complete Schedule Specification Table

From Maths.mhd (Homecoming/Rebirth/Generic - all identical):

| Schedule | Threshold 1 | Threshold 2 | Threshold 3 | Attributes Using This Schedule |
|----------|-------------|-------------|-------------|--------------------------------|
| **A** | 0.700 (70%) | 0.900 (90%) | 1.000 (100%) | Damage, Accuracy, Recharge, Heal, EndMod, Recovery, Regen, MaxHP, Speed (Run/Jump/Fly), Slow, Absorb, Hold, Stun, Sleep, Immobilize |
| **B** | 0.400 (40%) | 0.500 (50%) | 0.600 (60%) | Defense, Resistance, ToHit, Range |
| **C** | 0.800 (80%) | 1.000 (100%) | 1.200 (120%) | Interrupt Time |
| **D** | 1.200 (120%) | 1.500 (150%) | 1.800 (180%) | Mez Duration: Afraid (Fear), Confused only |

### Enhancement Type to Schedule Mapping

Complete mapping extracted from Enhancement.cs `GetSchedule()` method (lines 434-458):

```
Defense           → Schedule B
Interrupt         → Schedule C
Range             → Schedule B
Resistance        → Schedule B
ToHit             → Schedule B

Mez (with subtype):
  - Afraid (4)    → Schedule D
  - Confused (5)  → Schedule D
  - All others    → Schedule A
    (Sleep=0, Hold=1, Stun=2, Immobilize=3)

All Other Types   → Schedule A
  - Damage
  - Accuracy
  - EnduranceCost (EndRdx)
  - Heal
  - RechargeTime
  - EnduranceModification
  - Recovery
  - Regeneration
  - MaxHP (Hit Points)
  - Speed (Run, Jump, Fly)
  - Slow
  - Absorb
```

### Pseudocode for Complete ED Application

```python
def apply_enhancement_diversification(
    enhancement_type: str,
    enhancement_subtype: Optional[int],
    total_value: float
) -> float:
    """
    Apply ED curve to enhancement value.

    Args:
        enhancement_type: e.g., "Damage", "Defense", "Mez"
        enhancement_subtype: For Mez: 0=Sleep, 1=Hold, 2=Stun, 3=Immob,
                             4=Afraid, 5=Confused
        total_value: Sum of all enhancement values BEFORE ED

    Returns:
        Enhancement value AFTER ED curve
    """
    # Step 1: Determine schedule
    schedule = get_schedule(enhancement_type, enhancement_subtype)

    # Step 2: Load thresholds for schedule
    T1, T2, T3 = THRESHOLDS[schedule]

    # Step 3: Apply piecewise function
    if total_value <= T1:
        return total_value  # Region 1: No ED

    # Pre-calculate cumulative values
    EDM1 = T1
    EDM2 = T1 + (T2 - T1) * 0.90
    EDM3 = EDM2 + (T3 - T2) * 0.70

    if total_value <= T2:
        return EDM1 + (total_value - T1) * 0.90  # Region 2: Light ED

    if total_value <= T3:
        return EDM2 + (total_value - T2) * 0.70  # Region 3: Medium ED

    # Region 4: Heavy ED
    return EDM3 + (total_value - T3) * 0.15
```

## Section 2: C# Implementation Details from MidsReborn

### Source File Location
`/MidsReborn/Core/Enhancement.cs`

### ED Application Method (Lines 460-486)

```csharp
public static float ApplyED(Enums.eSchedule iSched, float iVal)
{
    switch (iSched)
    {
        case Enums.eSchedule.None:
            return 0.0f;
        case Enums.eSchedule.Multiple:
            return 0.0f;
        default:
            // Load thresholds from database
            var ed = new float[3];
            for (var index = 0; index <= 2; ++index)
                ed[index] = DatabaseAPI.Database.MultED[(int) iSched][index];

            // Region 1: Below first threshold - no ED
            if (iVal <= (double) ed[0])
                return iVal;

            // Pre-calculate cumulative ED values at each threshold
            float[] edm =
            {
                ed[0],  // EDM1
                ed[0] + (float) ((ed[1] - (double) ed[0]) * 0.899999976158142),  // EDM2
                (float) (ed[0] + (ed[1] - (double) ed[0]) * 0.899999976158142 +
                         (ed[2] - (double) ed[1]) * 0.699999988079071)  // EDM3
            };

            // Region 2: Light ED (90% efficiency)
            return iVal > (double) ed[1]
                // Region 3: Medium ED (70% efficiency)
                ? iVal > (double) ed[2]
                    // Region 4: Heavy ED (15% efficiency)
                    ? edm[2] + (float) ((iVal - (double) ed[2]) * 0.150000005960464)
                    : edm[1] + (float) ((iVal - (double) ed[1]) * 0.699999988079071)
                // Return Region 2
                : edm[0] + (float) ((iVal - (double) ed[0]) * 0.899999976158142);
    }
}
```

**Key Implementation Notes:**
- Uses ternary operators for compactness (not recommended for Python port)
- Database.MultED is a `float[4][3]` array (4 schedules, 3 thresholds each)
- Casts to `double` for intermediate calculations, returns `float`
- Returns `0.0f` for `None` and `Multiple` schedules

### Schedule Assignment Method (Lines 434-458)

```csharp
public static Enums.eSchedule GetSchedule(Enums.eEnhance iEnh, int tSub = -1)
{
    Enums.eSchedule eSchedule;
    switch (iEnh)
    {
        case Enums.eEnhance.Defense:
            eSchedule = Enums.eSchedule.B;
            break;
        case Enums.eEnhance.Interrupt:
            return Enums.eSchedule.C;
        case Enums.eEnhance.Mez:
            // tSub: 0=Sleep, 1=Hold, 2=Stun, 3=Immobilize, 4=Afraid, 5=Confused
            return tSub <= -1 || !((tSub == 4) | (tSub == 5))
                ? Enums.eSchedule.A   // All mez except Afraid/Confused
                : Enums.eSchedule.D;  // Afraid/Confused only
        case Enums.eEnhance.Range:
            return Enums.eSchedule.B;
        case Enums.eEnhance.Resistance:
            return Enums.eSchedule.B;
        case Enums.eEnhance.ToHit:
            return Enums.eSchedule.B;
        default:
            eSchedule = Enums.eSchedule.A;
            break;
    }
    return eSchedule;
}
```

**Implementation Notes:**
- `tSub` parameter is optional (default -1)
- Uses bitwise OR (`|`) instead of logical OR (`||`) for the mez check
- Defense, Range, Resistance, ToHit all use Schedule B
- Default case returns Schedule A (covers 90% of enhancement types)

### Database MultED Array Loading (DatabaseAPI.cs, Lines 2696-2806)

```csharp
private static void InitializeMaths()
{
    // Initialize MultED as 4 schedules × 3 thresholds
    Database.MultED = new float[4][];
    for (var index = 0; index < 4; ++index)
    {
        Database.MultED[index] = new float[3];
    }

    // Default values (overwritten by Maths.mhd load)
    for (var index1 = 0; index1 <= 2; ++index1)
    {
        for (var index2 = 0; index2 < 4; ++index2)
        {
            Database.MultED[index2][index1] = 1;
        }
    }
    // ... initialization of MultTO, MultDO, MultSO, MultHO, MultIO ...
}

public static bool LoadMaths(string? iPath)
{
    // ... file loading code ...

    // Seek to "EDRT" section in Maths.mhd
    if (!FileIO.IOSeek(streamReader, "EDRT"))
    {
        // Error handling
        return false;
    }

    InitializeMaths();

    // Load 3 rows (thresholds) × 4 columns (schedules)
    for (var index1 = 0; index1 <= 2; ++index1)  // Thresholds 1-3
    {
        var strArray = FileIO.IOGrab(streamReader);  // Read tab-delimited line
        for (var index2 = 0; index2 < 4; ++index2)   // Schedules A-D
        {
            var ret = float.TryParse(strArray[index2 + 1],
                                     out Database.MultED[index2][index1]);
            if (!ret)
            {
                loadErrorDetectedPass = 1;
            }
        }
    }
    // ... continue loading TO/DO/SO/HO/IO data ...
}
```

**Data Source:** `Maths.mhd` file format:
```
ED Reduction Thresholds
EDRT    A      B      C      D
EDThresh_1  0.700  0.400  0.800  1.200
EDThresh_2  0.900  0.500  1.000  1.500
EDThresh_3  1.000  0.600  1.200  1.800
```

### Edge Cases from C# Code

1. **Schedule.None or Schedule.Multiple:**
   - Returns `0.0f` immediately
   - Used when enhancement has no schedule or mixed schedules

2. **Negative Values:**
   - Not explicitly handled in ApplyED (assumes positive)
   - Game data never has negative enhancement values
   - Debuffs are applied to enemies, not players

3. **Zero Value:**
   - Passes through Region 1 check (`0 <= T1`)
   - Returns `0.0f` unchanged

4. **Extreme Values (>500%):**
   - Algorithm continues to work (no upper bound check)
   - Follows Region 4 formula: `EDM3 + (value - T3) × 0.15`
   - Example: 5.0 on Schedule A → 0.95 + (4.0 × 0.15) = 1.55

## Section 3: Database Schema

### Primary Table: `enhancement_schedules`

```sql
-- Enhancement Diversification Schedule Definitions
CREATE TABLE enhancement_schedules (
    schedule_id CHAR(1) PRIMARY KEY,  -- 'A', 'B', 'C', 'D'
    schedule_name VARCHAR(50) NOT NULL,
    threshold_1 REAL NOT NULL CHECK (threshold_1 > 0 AND threshold_1 < 3.0),
    threshold_2 REAL NOT NULL CHECK (threshold_2 > threshold_1 AND threshold_2 < 3.0),
    threshold_3 REAL NOT NULL CHECK (threshold_3 > threshold_2 AND threshold_3 < 3.0),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed data from Maths.mhd
INSERT INTO enhancement_schedules (schedule_id, schedule_name, threshold_1, threshold_2, threshold_3, description) VALUES
    ('A', 'Standard', 0.700, 0.900, 1.000, 'Most offensive attributes: Damage, Accuracy, Recharge, Heal, EndMod, Recovery, Regen, MaxHP, Speed, Slow, Absorb, and most Mez types'),
    ('B', 'Defensive', 0.400, 0.500, 0.600, 'Defensive attributes: Defense, Resistance, ToHit, Range - applies ED aggressively due to power of these stats'),
    ('C', 'Interrupt', 0.800, 1.000, 1.200, 'Interrupt Time reduction only - lenient schedule for niche mechanic'),
    ('D', 'Special Mez', 1.200, 1.500, 1.800, 'Mez Duration for Afraid and Confused only - very lenient for weak control effects');

-- Index for fast lookups
CREATE INDEX idx_enhancement_schedules_id ON enhancement_schedules(schedule_id);
```

### Lookup Table: `enhancement_type_schedules`

```sql
-- Maps enhancement types to their ED schedules
CREATE TABLE enhancement_type_schedules (
    type_id SERIAL PRIMARY KEY,
    enhancement_type VARCHAR(50) NOT NULL UNIQUE,
    enhancement_subtype INTEGER,  -- NULL for non-Mez, 0-5 for Mez types
    schedule_id CHAR(1) NOT NULL REFERENCES enhancement_schedules(schedule_id),
    notes TEXT,
    UNIQUE(enhancement_type, enhancement_subtype)
);

-- Seed complete mapping from GetSchedule() method
INSERT INTO enhancement_type_schedules (enhancement_type, enhancement_subtype, schedule_id, notes) VALUES
    -- Schedule A (Standard) - Most attributes
    ('Damage', NULL, 'A', 'Primary damage enhancement'),
    ('Accuracy', NULL, 'A', 'ToHit chance enhancement'),
    ('EnduranceCost', NULL, 'A', 'Endurance cost reduction'),
    ('Heal', NULL, 'A', 'Healing effectiveness'),
    ('RechargeTime', NULL, 'A', 'Recharge speed reduction'),
    ('EnduranceModification', NULL, 'A', 'Endurance drain/recovery'),
    ('Recovery', NULL, 'A', 'Endurance recovery rate'),
    ('Regeneration', NULL, 'A', 'HP regeneration rate'),
    ('MaxHP', NULL, 'A', 'Maximum hit points'),
    ('RunSpeed', NULL, 'A', 'Running speed'),
    ('JumpSpeed', NULL, 'A', 'Jumping speed'),
    ('FlySpeed', NULL, 'A', 'Flying speed'),
    ('Slow', NULL, 'A', 'Slow effect magnitude'),
    ('Absorb', NULL, 'A', 'Absorb shield strength'),

    -- Mez types using Schedule A
    ('Mez', 0, 'A', 'Sleep duration'),
    ('Mez', 1, 'A', 'Hold duration'),
    ('Mez', 2, 'A', 'Stun duration'),
    ('Mez', 3, 'A', 'Immobilize duration'),

    -- Schedule B (Defensive) - Powerful attributes
    ('Defense', NULL, 'B', 'Defense to hit - very powerful, aggressive ED'),
    ('Resistance', NULL, 'B', 'Damage resistance - aggressive ED'),
    ('ToHit', NULL, 'B', 'ToHit buff - aggressive ED'),
    ('Range', NULL, 'B', 'Power range - aggressive ED'),

    -- Schedule C (Interrupt)
    ('Interrupt', NULL, 'C', 'Interrupt time reduction - niche mechanic'),

    -- Schedule D (Special Mez) - Weak control effects
    ('Mez', 4, 'D', 'Afraid (Fear) duration - weak mez, lenient ED'),
    ('Mez', 5, 'D', 'Confused duration - PvE only, lenient ED');

-- Indexes for fast schedule lookups
CREATE INDEX idx_enhancement_type_schedules_type ON enhancement_type_schedules(enhancement_type);
CREATE INDEX idx_enhancement_type_schedules_type_subtype ON enhancement_type_schedules(enhancement_type, enhancement_subtype);
```

### Materialized View: `ed_curve_lookup`

```sql
-- Pre-calculated ED curve values for common enhancement percentages
-- Useful for UI display and validation
CREATE MATERIALIZED VIEW ed_curve_lookup AS
SELECT
    s.schedule_id,
    s.schedule_name,
    e.enhancement_pct,
    e.enhancement_value,
    CASE
        WHEN e.enhancement_value <= s.threshold_1 THEN e.enhancement_value
        WHEN e.enhancement_value <= s.threshold_2 THEN
            s.threshold_1 + (e.enhancement_value - s.threshold_1) * 0.90
        WHEN e.enhancement_value <= s.threshold_3 THEN
            s.threshold_1 + (s.threshold_2 - s.threshold_1) * 0.90 +
            (e.enhancement_value - s.threshold_2) * 0.70
        ELSE
            s.threshold_1 + (s.threshold_2 - s.threshold_1) * 0.90 +
            (s.threshold_3 - s.threshold_2) * 0.70 +
            (e.enhancement_value - s.threshold_3) * 0.15
    END AS post_ed_value,
    CASE
        WHEN e.enhancement_value <= s.threshold_1 THEN 'None'
        WHEN e.enhancement_value <= s.threshold_2 THEN 'Light'
        WHEN e.enhancement_value <= s.threshold_3 THEN 'Medium'
        ELSE 'Heavy'
    END AS ed_severity
FROM enhancement_schedules s
CROSS JOIN (
    -- Generate test values from 0% to 300% in 5% increments
    SELECT
        n * 0.05 AS enhancement_value,
        n * 5 AS enhancement_pct
    FROM generate_series(0, 60) AS n
) e
ORDER BY s.schedule_id, e.enhancement_pct;

CREATE INDEX idx_ed_curve_lookup_schedule_pct
    ON ed_curve_lookup(schedule_id, enhancement_pct);
```

## Section 4: Comprehensive Test Cases

All test cases use **exact calculated values** from the ED formula. Expected values are precise to 4 decimal places.

### Test Group 1: Schedule A - Standard (Damage/Accuracy/Recharge)

```python
def test_schedule_a_zero():
    """Zero enhancement should pass through unchanged."""
    assert apply_ed('A', 0.0) == 0.0

def test_schedule_a_below_threshold():
    """Below first threshold (70%) - no ED applied."""
    assert apply_ed('A', 0.50) == 0.5000
    assert apply_ed('A', 0.70) == 0.7000  # Exactly at T1

def test_schedule_a_light_ed():
    """Between T1 (70%) and T2 (90%) - 90% efficiency."""
    result = apply_ed('A', 0.80)
    expected = 0.70 + (0.80 - 0.70) * 0.90  # = 0.79
    assert abs(result - 0.7900) < 0.0001

def test_schedule_a_three_sos():
    """Classic case: Three SOs (33.3% each = 99.9%)."""
    result = apply_ed('A', 0.999)
    # EDM2 = 0.70 + 0.18 = 0.88
    # result = 0.88 + (0.999 - 0.90) * 0.70 = 0.88 + 0.0693 = 0.9493
    assert abs(result - 0.9493) < 0.0001

def test_schedule_a_exactly_100():
    """Exactly 100% enhancement - boundary case."""
    result = apply_ed('A', 1.0)
    # EDM2 = 0.88, result = 0.88 + 0.10 * 0.70 = 0.95
    assert abs(result - 0.9500) < 0.0001

def test_schedule_a_heavy_ed():
    """150% enhancement - heavy ED region."""
    result = apply_ed('A', 1.50)
    # EDM3 = 0.88 + 0.07 = 0.95
    # result = 0.95 + (1.50 - 1.00) * 0.15 = 0.95 + 0.075 = 1.025
    assert abs(result - 1.0250) < 0.0001

def test_schedule_a_six_sos():
    """Classic pre-ED comparison: Six SOs (200%)."""
    result = apply_ed('A', 1.998)  # 6 × 33.3% = 199.8%
    # result = 0.95 + (1.998 - 1.00) * 0.15 = 0.95 + 0.1497 = 1.0997
    assert abs(result - 1.0997) < 0.0001

    # Verify 45% loss
    loss_pct = ((1.998 - result) / 1.998) * 100
    assert abs(loss_pct - 45.0) < 0.1

def test_schedule_a_extreme():
    """Extreme over-enhancement: 250% (theoretical max slotting)."""
    result = apply_ed('A', 2.50)
    # result = 0.95 + (2.50 - 1.00) * 0.15 = 0.95 + 0.225 = 1.175
    assert abs(result - 1.1750) < 0.0001

### Test Group 2: Schedule B - Defensive (Defense/Resistance)

def test_schedule_b_below_threshold():
    """Below first threshold (40%) - no ED applied."""
    assert apply_ed('B', 0.30) == 0.3000

def test_schedule_b_light_ed():
    """Between T1 (40%) and T2 (50%) - light ED."""
    result = apply_ed('B', 0.45)
    # result = 0.40 + (0.45 - 0.40) * 0.90 = 0.445
    assert abs(result - 0.4450) < 0.0001

def test_schedule_b_three_sos():
    """Three SOs in defense - demonstrates aggressive ED."""
    result = apply_ed('B', 0.999)
    # T1=0.40, T2=0.50, T3=0.60
    # EDM2 = 0.40 + 0.09 = 0.49
    # EDM3 = 0.49 + 0.07 = 0.56
    # result = 0.56 + (0.999 - 0.60) * 0.15 = 0.56 + 0.05985 = 0.6198
    assert abs(result - 0.6198) < 0.0001

    # Verify ~38% loss (much worse than Schedule A's 5%)
    loss_pct = ((0.999 - result) / 0.999) * 100
    assert abs(loss_pct - 38.0) < 0.5

def test_schedule_b_exactly_100():
    """100% defense enhancement."""
    result = apply_ed('B', 1.0)
    # result = 0.56 + (1.0 - 0.60) * 0.15 = 0.56 + 0.06 = 0.62
    assert abs(result - 0.6200) < 0.0001

def test_schedule_b_heavy_defense():
    """Heavy defense slotting (150%) - shows why defense is hard to stack."""
    result = apply_ed('B', 1.50)
    # result = 0.56 + (1.50 - 0.60) * 0.15 = 0.56 + 0.135 = 0.695
    assert abs(result - 0.6950) < 0.0001

    # 53.7% loss!
    loss_pct = ((1.50 - result) / 1.50) * 100
    assert abs(loss_pct - 53.7) < 0.5

### Test Group 3: Schedule C - Interrupt

def test_schedule_c_below_threshold():
    """Below first threshold (80%) - no ED."""
    assert apply_ed('C', 0.75) == 0.7500

def test_schedule_c_light_ed():
    """Between T1 (80%) and T2 (100%) - light ED."""
    result = apply_ed('C', 0.90)
    # result = 0.80 + (0.90 - 0.80) * 0.90 = 0.89
    assert abs(result - 0.8900) < 0.0001

def test_schedule_c_medium_ed():
    """Between T2 (100%) and T3 (120%) - medium ED."""
    result = apply_ed('C', 1.10)
    # EDM2 = 0.80 + 0.18 = 0.98
    # result = 0.98 + (1.10 - 1.00) * 0.70 = 0.98 + 0.07 = 1.05
    assert abs(result - 1.0500) < 0.0001

def test_schedule_c_heavy_ed():
    """Heavy ED region (150%)."""
    result = apply_ed('C', 1.50)
    # EDM3 = 0.98 + 0.14 = 1.12
    # result = 1.12 + (1.50 - 1.20) * 0.15 = 1.12 + 0.045 = 1.165
    assert abs(result - 1.1650) < 0.0001

### Test Group 4: Schedule D - Special Mez (Afraid/Confused)

def test_schedule_d_no_ed_at_100():
    """100% enhancement - NO ED applied (below T1=120%)!"""
    result = apply_ed('D', 1.0)
    assert result == 1.0000  # No loss!

def test_schedule_d_light_ed():
    """Between T1 (120%) and T2 (150%) - light ED."""
    result = apply_ed('D', 1.35)
    # result = 1.20 + (1.35 - 1.20) * 0.90 = 1.20 + 0.135 = 1.335
    assert abs(result - 1.3350) < 0.0001

def test_schedule_d_medium_ed():
    """Between T2 (150%) and T3 (180%) - medium ED."""
    result = apply_ed('D', 1.65)
    # EDM2 = 1.20 + 0.27 = 1.47
    # result = 1.47 + (1.65 - 1.50) * 0.70 = 1.47 + 0.105 = 1.575
    assert abs(result - 1.5750) < 0.0001

def test_schedule_d_heavy_ed():
    """Heavy ED region (200%)."""
    result = apply_ed('D', 2.0)
    # EDM3 = 1.47 + 0.21 = 1.68
    # result = 1.68 + (2.0 - 1.80) * 0.15 = 1.68 + 0.03 = 1.71
    assert abs(result - 1.7100) < 0.0001

    # Only 14.5% loss (vs 45% for Schedule A!)
    loss_pct = ((2.0 - result) / 2.0) * 100
    assert abs(loss_pct - 14.5) < 0.5

### Test Group 5: Schedule Assignment Tests

def test_schedule_damage():
    """Damage uses Schedule A."""
    assert get_schedule("Damage") == 'A'

def test_schedule_defense():
    """Defense uses Schedule B."""
    assert get_schedule("Defense") == 'B'

def test_schedule_interrupt():
    """Interrupt uses Schedule C."""
    assert get_schedule("Interrupt") == 'C'

def test_schedule_mez_afraid():
    """Afraid (subtype 4) uses Schedule D."""
    assert get_schedule("Mez", 4) == 'D'

def test_schedule_mez_confused():
    """Confused (subtype 5) uses Schedule D."""
    assert get_schedule("Mez", 5) == 'D'

def test_schedule_mez_hold():
    """Hold (subtype 1) uses Schedule A, NOT D."""
    assert get_schedule("Mez", 1) == 'A'

def test_schedule_resistance():
    """Resistance uses Schedule B."""
    assert get_schedule("Resistance") == 'B'

### Test Group 6: Comparative Tests

def test_compare_schedules_at_100pct():
    """Compare all schedules at 100% enhancement."""
    results = {
        'A': apply_ed('A', 1.0),  # 0.95
        'B': apply_ed('B', 1.0),  # 0.62
        'C': apply_ed('C', 1.0),  # 0.98
        'D': apply_ed('D', 1.0),  # 1.00
    }

    assert abs(results['A'] - 0.9500) < 0.01
    assert abs(results['B'] - 0.6200) < 0.01
    assert abs(results['C'] - 0.9800) < 0.01
    assert abs(results['D'] - 1.0000) < 0.01

    # Schedule B loses 7.6× more than Schedule A
    loss_A = 1.0 - results['A']  # 0.05
    loss_B = 1.0 - results['B']  # 0.38
    assert abs((loss_B / loss_A) - 7.6) < 0.5

### Test Group 7: Edge Cases

def test_ed_at_exact_thresholds():
    """Test behavior exactly at threshold boundaries."""
    # Schedule A thresholds
    assert apply_ed('A', 0.700) == 0.7000  # T1 - no ED
    assert abs(apply_ed('A', 0.900) - 0.8800) < 0.0001  # T2
    assert abs(apply_ed('A', 1.000) - 0.9500) < 0.0001  # T3

def test_ed_one_percent_over_threshold():
    """Test +1% over each threshold to verify region transitions."""
    # Schedule A: 71% (just over T1=70%)
    result = apply_ed('A', 0.71)
    expected = 0.70 + (0.01 * 0.90)  # = 0.709
    assert abs(result - 0.7090) < 0.0001

def test_ed_negative_value():
    """Negative values should pass through (debuffs on enemies)."""
    # Note: C# code doesn't explicitly check, but game never uses negative
    # Python implementation should handle this
    result = apply_ed('A', -0.5)
    assert result == -0.5  # No ED on debuffs

def test_ed_schedule_none():
    """Schedule 'None' should return 0."""
    result = apply_ed('None', 1.0)
    assert result == 0.0

def test_ed_schedule_multiple():
    """Schedule 'Multiple' should return 0."""
    result = apply_ed('Multiple', 1.0)
    assert result == 0.0
```

## Section 5: Python Implementation Guide

### Complete Implementation Module

```python
"""
Enhancement Diversification (ED) Calculation Module

Implements the ED curve algorithm from City of Heroes Issue 5 (2005).
All values and formulas extracted from MidsReborn source code.

Reference: MidsReborn/Core/Enhancement.cs (ApplyED, GetSchedule)
Data Source: MidsReborn/Data/Homecoming/Maths.mhd
"""

from enum import Enum
from typing import Optional, Tuple
from dataclasses import dataclass


class EDSchedule(Enum):
    """Enhancement Diversification schedules.

    Each schedule defines three thresholds where ED applies progressively
    stronger diminishing returns.
    """
    NONE = -1      # No ED (should return 0)
    A = 0          # Standard: Most offensive attributes
    B = 1          # Defensive: Defense, Resistance, ToHit, Range
    C = 2          # Interrupt: Interrupt time reduction only
    D = 3          # Special Mez: Afraid, Confused only
    MULTIPLE = 4   # Multiple schedules (should return 0)


@dataclass(frozen=True)
class EDThresholds:
    """Threshold values for an ED schedule."""
    threshold_1: float  # First ED breakpoint (light ED starts)
    threshold_2: float  # Second ED breakpoint (medium ED starts)
    threshold_3: float  # Third ED breakpoint (heavy ED starts)

    def __post_init__(self):
        """Validate thresholds are in ascending order."""
        if not (0 < self.threshold_1 < self.threshold_2 < self.threshold_3 < 3.0):
            raise ValueError(
                f"Thresholds must be in ascending order: "
                f"{self.threshold_1} < {self.threshold_2} < {self.threshold_3}"
            )


# ED thresholds from Maths.mhd (exact values)
ED_THRESHOLDS: dict[EDSchedule, EDThresholds] = {
    EDSchedule.A: EDThresholds(0.700, 0.900, 1.000),
    EDSchedule.B: EDThresholds(0.400, 0.500, 0.600),
    EDSchedule.C: EDThresholds(0.800, 1.000, 1.200),
    EDSchedule.D: EDThresholds(1.200, 1.500, 1.800),
}

# Enhancement type to schedule mapping
# From Enhancement.cs GetSchedule() method
ENHANCEMENT_SCHEDULE_MAP: dict[str, EDSchedule] = {
    # Schedule A (Standard)
    "Damage": EDSchedule.A,
    "Accuracy": EDSchedule.A,
    "EnduranceCost": EDSchedule.A,
    "Heal": EDSchedule.A,
    "RechargeTime": EDSchedule.A,
    "EnduranceModification": EDSchedule.A,
    "Recovery": EDSchedule.A,
    "Regeneration": EDSchedule.A,
    "MaxHP": EDSchedule.A,
    "RunSpeed": EDSchedule.A,
    "JumpSpeed": EDSchedule.A,
    "FlySpeed": EDSchedule.A,
    "Slow": EDSchedule.A,
    "Absorb": EDSchedule.A,

    # Schedule B (Defensive)
    "Defense": EDSchedule.B,
    "Resistance": EDSchedule.B,
    "ToHit": EDSchedule.B,
    "Range": EDSchedule.B,

    # Schedule C (Interrupt)
    "Interrupt": EDSchedule.C,

    # Mez types handled separately by subtype
}

# Mez subtype definitions (from MidsReborn enums)
MEZ_SUBTYPE_SLEEP = 0
MEZ_SUBTYPE_HOLD = 1
MEZ_SUBTYPE_STUN = 2
MEZ_SUBTYPE_IMMOBILIZE = 3
MEZ_SUBTYPE_AFRAID = 4       # Uses Schedule D
MEZ_SUBTYPE_CONFUSED = 5     # Uses Schedule D


def get_schedule(
    enhancement_type: str,
    enhancement_subtype: Optional[int] = None
) -> EDSchedule:
    """
    Determine which ED schedule applies to an enhancement type.

    Args:
        enhancement_type: Enhancement attribute (e.g., "Damage", "Defense", "Mez")
        enhancement_subtype: For Mez type, specifies which mez:
            0=Sleep, 1=Hold, 2=Stun, 3=Immobilize, 4=Afraid, 5=Confused

    Returns:
        EDSchedule enum value

    Examples:
        >>> get_schedule("Damage")
        EDSchedule.A
        >>> get_schedule("Defense")
        EDSchedule.B
        >>> get_schedule("Mez", 4)  # Afraid
        EDSchedule.D
        >>> get_schedule("Mez", 1)  # Hold
        EDSchedule.A
    """
    # Special handling for Mez types
    if enhancement_type == "Mez":
        if enhancement_subtype in (MEZ_SUBTYPE_AFRAID, MEZ_SUBTYPE_CONFUSED):
            return EDSchedule.D
        else:
            return EDSchedule.A  # All other mez types use Schedule A

    # Look up in map, default to Schedule A (matches C# behavior)
    return ENHANCEMENT_SCHEDULE_MAP.get(enhancement_type, EDSchedule.A)


def apply_ed(schedule: EDSchedule, value: float) -> float:
    """
    Apply Enhancement Diversification to an enhancement value.

    This implements the exact algorithm from MidsReborn Enhancement.cs
    (ApplyED method, lines 460-486).

    Args:
        schedule: Which ED curve to use (A/B/C/D/NONE/MULTIPLE)
        value: Total enhancement value (e.g., 0.999 for three SOs)

    Returns:
        Enhancement value after ED diminishing returns

    Algorithm:
        1. If value <= T1: return value (no ED)
        2. If value <= T2: return T1 + (value - T1) × 0.90 (light ED)
        3. If value <= T3: return EDM2 + (value - T2) × 0.70 (medium ED)
        4. Else: return EDM3 + (value - T3) × 0.15 (heavy ED)

    Examples:
        >>> apply_ed(EDSchedule.A, 1.0)  # Three SOs in damage
        0.95
        >>> apply_ed(EDSchedule.B, 1.0)  # Three SOs in defense
        0.62
        >>> apply_ed(EDSchedule.A, 2.0)  # Six SOs in damage
        1.10
        >>> apply_ed(EDSchedule.D, 1.0)  # Afraid/Confused at 100%
        1.00
    """
    # Special cases: None and Multiple return 0
    if schedule in (EDSchedule.NONE, EDSchedule.MULTIPLE):
        return 0.0

    # Negative values pass through (debuffs on enemies)
    if value < 0:
        return value

    # Get thresholds for this schedule
    thresholds = ED_THRESHOLDS[schedule]
    t1 = thresholds.threshold_1
    t2 = thresholds.threshold_2
    t3 = thresholds.threshold_3

    # Region 1: Below first threshold - no ED
    if value <= t1:
        return value

    # Pre-calculate cumulative ED values at each threshold
    # This matches the C# implementation exactly
    edm1 = t1
    edm2 = t1 + (t2 - t1) * 0.90
    edm3 = edm2 + (t3 - t2) * 0.70

    # Region 2: Light ED (90% efficiency)
    if value <= t2:
        return edm1 + (value - t1) * 0.90

    # Region 3: Medium ED (70% efficiency)
    if value <= t3:
        return edm2 + (value - t2) * 0.70

    # Region 4: Heavy ED (15% efficiency)
    return edm3 + (value - t3) * 0.15


def calculate_ed_loss(
    schedule: EDSchedule,
    value: float
) -> Tuple[float, float, float]:
    """
    Calculate how much enhancement value is lost to ED.

    Args:
        schedule: ED schedule to use
        value: Pre-ED enhancement value

    Returns:
        Tuple of (post_ed_value, pre_ed_value, percent_lost)

    Examples:
        >>> calculate_ed_loss(EDSchedule.A, 2.0)
        (1.10, 2.0, 45.0)  # Six-slotting loses 45%!
        >>> calculate_ed_loss(EDSchedule.B, 1.0)
        (0.62, 1.0, 38.0)  # Defense loses 38% at 100%
    """
    post_ed = apply_ed(schedule, value)
    loss = value - post_ed
    percent_lost = (loss / value * 100) if value > 0 else 0.0
    return post_ed, value, percent_lost


def get_ed_severity(schedule: EDSchedule, value: float) -> str:
    """
    Determine the severity level of ED being applied.

    Args:
        schedule: ED schedule
        value: Enhancement value

    Returns:
        One of: "None", "Light", "Medium", "Heavy"

    Examples:
        >>> get_ed_severity(EDSchedule.A, 0.5)
        'None'
        >>> get_ed_severity(EDSchedule.A, 0.8)
        'Light'
        >>> get_ed_severity(EDSchedule.A, 0.95)
        'Medium'
        >>> get_ed_severity(EDSchedule.A, 1.5)
        'Heavy'
    """
    if schedule in (EDSchedule.NONE, EDSchedule.MULTIPLE):
        return "None"

    thresholds = ED_THRESHOLDS[schedule]

    if value <= thresholds.threshold_1:
        return "None"
    elif value <= thresholds.threshold_2:
        return "Light"
    elif value <= thresholds.threshold_3:
        return "Medium"
    else:
        return "Heavy"


# Convenience function for direct enhancement calculation
def apply_enhancement_ed(
    enhancement_type: str,
    total_value: float,
    enhancement_subtype: Optional[int] = None
) -> float:
    """
    Apply ED to an enhancement value (convenience wrapper).

    This is the main entry point for ED calculations. It determines
    the correct schedule and applies the ED curve.

    Args:
        enhancement_type: Type of enhancement (e.g., "Damage", "Defense")
        total_value: Sum of all enhancement values BEFORE ED
        enhancement_subtype: For Mez, the mez subtype (0-5)

    Returns:
        Enhancement value AFTER ED curve

    Examples:
        >>> apply_enhancement_ed("Damage", 1.0)
        0.95
        >>> apply_enhancement_ed("Defense", 1.0)
        0.62
        >>> apply_enhancement_ed("Mez", 1.5, enhancement_subtype=4)  # Afraid
        1.47
    """
    schedule = get_schedule(enhancement_type, enhancement_subtype)
    return apply_ed(schedule, total_value)
```

### Usage Examples

```python
# Example 1: Calculate ED for a power with three damage SOs
damage_enhancement = 3 * 0.333  # Three +33.3% SOs = 99.9%
post_ed_damage = apply_enhancement_ed("Damage", damage_enhancement)
print(f"Three damage SOs: {damage_enhancement:.1%} → {post_ed_damage:.1%}")
# Output: Three damage SOs: 99.9% → 94.9%

# Example 2: Compare damage vs defense at same enhancement level
value = 1.0
damage_post_ed = apply_enhancement_ed("Damage", value)
defense_post_ed = apply_enhancement_ed("Defense", value)
print(f"Damage at 100%: {damage_post_ed:.1%}")
print(f"Defense at 100%: {defense_post_ed:.1%}")
# Output:
# Damage at 100%: 95.0%
# Defense at 100%: 62.0%

# Example 3: Calculate ED loss for frankenslotting optimization
test_values = [0.70, 0.90, 0.95, 1.0, 1.1]
for val in test_values:
    post_ed, pre_ed, loss_pct = calculate_ed_loss(EDSchedule.A, val)
    severity = get_ed_severity(EDSchedule.A, val)
    print(f"{pre_ed:.0%}: {post_ed:.1%} (loss {loss_pct:.1f}%, {severity} ED)")
# Output:
# 70%: 70.0% (loss 0.0%, None ED)
# 90%: 88.0% (loss 2.2%, Light ED)
# 95%: 91.5% (loss 3.7%, Medium ED)
# 100%: 95.0% (loss 5.0%, Medium ED)
# 110%: 96.5% (loss 12.3%, Heavy ED)

# Example 4: Mez enhancement with different subtypes
afraid_value = 1.5
hold_value = 1.5

afraid_post_ed = apply_enhancement_ed("Mez", afraid_value, MEZ_SUBTYPE_AFRAID)
hold_post_ed = apply_enhancement_ed("Mez", hold_value, MEZ_SUBTYPE_HOLD)

print(f"Afraid (Schedule D): {afraid_value:.0%} → {afraid_post_ed:.1%}")
print(f"Hold (Schedule A): {hold_value:.0%} → {hold_post_ed:.1%}")
# Output:
# Afraid (Schedule D): 150% → 147.0%
# Hold (Schedule A): 150% → 102.5%
```

## Section 6: Integration Points and Data Flow

### Upstream Integration: Enhancement Slotting (Spec 11)

**Input:** Raw enhancement values from slotted enhancements

```python
# From Spec 11: Enhancement Types & Slotting
class SlottedEnhancement:
    enhancement_id: int
    level: int
    boost_level: int  # +0 to +5

    def get_enhancement_value(self, attribute: str) -> float:
        """Get base enhancement value for an attribute (before ED)."""
        # Returns value like 0.333 for a level 50 SO
        pass

# Aggregate all enhancements of same type in a power
def sum_enhancements(power: Power, attribute: str) -> float:
    """Sum all enhancement values for an attribute BEFORE ED."""
    total = 0.0
    for slot in power.slots:
        if slot.enhancement:
            total += slot.enhancement.get_enhancement_value(attribute)
    return total

# Apply ED to the summed value
def get_enhanced_attribute(power: Power, attribute: str) -> float:
    """Get final enhanced value for an attribute AFTER ED."""
    pre_ed_value = sum_enhancements(power, attribute)
    schedule = get_schedule(attribute, get_subtype(attribute, power))
    post_ed_value = apply_ed(schedule, pre_ed_value)
    return post_ed_value
```

**Critical Rule:** ED is applied ONCE to the sum of all enhancements, NOT per-enhancement.

**WRONG:**
```python
# DON'T DO THIS - ED applied per enhancement
total = 0.0
for enh in enhancements:
    total += apply_ed(schedule, enh.value)  # WRONG!
```

**CORRECT:**
```python
# DO THIS - Sum first, then apply ED
total = sum(enh.value for enh in enhancements)
post_ed = apply_ed(schedule, total)  # CORRECT!
```

### Downstream Integration: Power Calculations (Spec 02)

**Output:** Post-ED enhancement values feed into all power calculations

```python
# From Spec 02: Power Effects System
class PowerEffect:
    base_value: float  # Base value from power definition
    attribute: str     # e.g., "Damage", "Defense"

    def calculate_final_value(self, power: Power) -> float:
        """Calculate final effect value with enhancements."""
        # Step 1: Get base value
        base = self.base_value

        # Step 2: Get enhancement value AFTER ED
        enhancement_value = get_enhanced_attribute(power, self.attribute)

        # Step 3: Apply enhancement multiplier
        # Formula: final = base × (1 + enhancement_after_ED)
        final = base * (1.0 + enhancement_value)

        return final

# Example: Damage calculation
# Power has 100 base damage, slotted with 3 SOs (99.9% enhancement)
base_damage = 100.0
enhancement_sum = 0.999  # Three SOs
post_ed_enhancement = apply_ed(EDSchedule.A, enhancement_sum)  # 0.9493
final_damage = base_damage * (1.0 + post_ed_enhancement)  # 194.93
```

### Integration with Set Bonuses (Spec 19)

**Critical:** Set bonuses are **post-ED** and bypass the ED curve entirely.

```python
def calculate_total_attribute(power: Power, attribute: str) -> float:
    """Calculate total attribute value including set bonuses."""
    # Step 1: Calculate slotted enhancements WITH ED
    slotted_value = get_enhanced_attribute(power, attribute)

    # Step 2: Add set bonuses WITHOUT ED (post-ED application)
    set_bonus_value = calculate_set_bonuses(power, attribute)

    # Step 3: Sum (set bonuses bypass ED)
    total = slotted_value + set_bonus_value

    return total

# Example: Defense with slotted IOs + set bonuses
slotted_defense = apply_ed(EDSchedule.B, 0.999)  # 0.6198 (38% loss to ED!)
set_bonus_defense = 0.05  # 5% defense from set bonuses (no ED applied)
total_defense = slotted_defense + set_bonus_defense  # 0.6698

# This is why defense sets are so valuable - bonuses bypass ED!
```

### Integration with Build Totals (Spec 31)

**Per-Power vs Global Attributes:**

```python
class BuildCalculator:
    def calculate_power_attribute(self, power: Power, attribute: str) -> float:
        """Calculate attribute for a single power (with ED)."""
        # ED applies to slotted enhancements in THIS power
        return get_enhanced_attribute(power, attribute)

    def calculate_global_attribute(self, build: Build, attribute: str) -> float:
        """Calculate global attribute across all powers and bonuses."""
        total = 0.0

        # Sum all sources (each already has ED applied)
        for power in build.powers:
            # Slotted enhancements (post-ED)
            total += get_enhanced_attribute(power, attribute)

        # Set bonuses (no ED)
        total += calculate_all_set_bonuses(build, attribute)

        # Global IOs (no ED)
        total += calculate_global_io_bonuses(build, attribute)

        # Incarnate bonuses (no ED)
        total += calculate_incarnate_bonuses(build, attribute)

        return total
```

### Data Flow Diagram

```
┌─────────────────────┐
│ Slotted             │
│ Enhancements        │
│ (Spec 11)           │
└──────────┬──────────┘
           │
           ▼
  ┌────────────────────┐
  │ Sum by Attribute   │
  │ (per power)        │
  └────────┬───────────┘
           │
           ▼
  ┌─────────────────────┐
  │ Apply ED Curve      │◄── Enhancement Schedules (THIS SPEC)
  │ (THIS SPEC)         │
  └────────┬────────────┘
           │
           ▼
  ┌─────────────────────┐
  │ Post-ED Value       │
  └────────┬────────────┘
           │
           ├──────────────────────┐
           │                      │
           ▼                      ▼
  ┌────────────────┐    ┌──────────────────┐
  │ Power Effect   │    │ Build Totals     │
  │ Calculation    │    │ (Spec 31)        │
  │ (Spec 02)      │    │                  │
  └────────────────┘    └──────────────────┘
                                 │
                                 ▼
                        ┌────────────────────┐
                        │ Add Post-ED        │
                        │ Sources:           │
                        │ - Set Bonuses      │
                        │ - Global IOs       │
                        │ - Incarnate        │
                        └────────────────────┘
```

### Integration Test Example

```python
def test_full_enhancement_flow():
    """Integration test: From slotting to final damage."""
    # Setup: Power with base 100 damage
    power = Power(base_damage=100.0)

    # Step 1: Slot three damage SOs
    power.add_enhancement(SO_Damage, level=50)  # +33.3%
    power.add_enhancement(SO_Damage, level=50)  # +33.3%
    power.add_enhancement(SO_Damage, level=50)  # +33.3%
    # Total: 99.9% damage enhancement

    # Step 2: Sum enhancements (before ED)
    pre_ed = sum_enhancements(power, "Damage")
    assert abs(pre_ed - 0.999) < 0.001

    # Step 3: Apply ED
    post_ed = apply_ed(EDSchedule.A, pre_ed)
    assert abs(post_ed - 0.9493) < 0.001  # 5% loss to ED

    # Step 4: Calculate final damage
    final_damage = power.base_damage * (1.0 + post_ed)
    assert abs(final_damage - 194.93) < 0.1

    # Step 5: Add set bonus (post-ED)
    power.add_set_bonus("Damage", 0.10)  # +10% from 6-piece set
    total_damage_bonus = post_ed + 0.10  # 1.0493 (104.93%)
    final_with_bonus = power.base_damage * (1.0 + total_damage_bonus)
    assert abs(final_with_bonus - 204.93) < 0.1
```

### Error Handling

```python
class EDCalculationError(Exception):
    """Base exception for ED calculation errors."""
    pass

class InvalidScheduleError(EDCalculationError):
    """Raised when an invalid schedule is specified."""
    pass

class InvalidEnhancementValueError(EDCalculationError):
    """Raised when enhancement value is invalid."""
    pass

def apply_ed_safe(schedule: EDSchedule, value: float) -> float:
    """Apply ED with error handling and validation."""
    # Validate schedule
    if schedule not in ED_THRESHOLDS and schedule not in (EDSchedule.NONE, EDSchedule.MULTIPLE):
        raise InvalidScheduleError(f"Invalid schedule: {schedule}")

    # Validate value (negative OK for debuffs, but warn on extreme values)
    if value > 10.0:
        import warnings
        warnings.warn(
            f"Enhancement value {value} is extremely high (>1000%). "
            "This may indicate a calculation error.",
            UserWarning
        )

    return apply_ed(schedule, value)
```

---

**END OF DEPTH-LEVEL IMPLEMENTATION DETAILS**
