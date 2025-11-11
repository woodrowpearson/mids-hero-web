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
