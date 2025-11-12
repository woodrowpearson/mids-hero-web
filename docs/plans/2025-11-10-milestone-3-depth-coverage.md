# Milestone 3: Depth Coverage - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add implementation-ready depth detail to 27 high-priority calculation specifications (8 Critical + 19 High priority specs)

**Architecture:** Enhance breadth-level specs with exact formulas, complete test cases, database schemas, validation rules, and implementation-ready pseudocode. Transform specs from "what and where" to "exactly how with all edge cases".

**Tech Stack:** Markdown documentation, MidsReborn C# deep analysis, Python type hints, pytest test design

**Context:** This builds on Milestone 2 (100% breadth coverage). We're taking high-priority specs from overview level to implementation-ready detail, enabling direct Python coding from specs.

---

## Overview

Milestone 3 adds **depth-level detail** to 27 high-priority specs. Each enhanced spec will have:

**Breadth Level** (already complete from Milestone 2):
- ✅ Overview (purpose, dependencies, complexity, priority)
- ✅ Primary location (file, class, method names)
- ✅ High-level pseudocode (major steps)
- ✅ Game mechanics context (what and why)

**Depth Level** (adding in Milestone 3):
- ➕ Exact formulas with all coefficients and constants
- ➕ Complete algorithm pseudocode with edge cases
- ➕ C# code snippets showing key implementation details
- ➕ Database schema definitions (tables, columns, types)
- ➕ Full test cases with expected input/output values
- ➕ Validation rules and error handling
- ➕ Python implementation guide (step-by-step with types)
- ➕ Integration points and dependencies

**Total Work:** 27 specifications to enhance (from 43 total)

**Estimated Effort:** 4-6 weeks (4-8 hours per spec average for depth)

---

## Priority Selection

### Critical Priority Specs (8 specs) - Must Do First

These are foundational calculations that everything else depends on:

1. **Spec 01**: Power Effects Core - IEffect interface, effect grouping
2. **Spec 10**: Enhancement Schedules - ED curves (4 schedules with exact thresholds)
3. **Spec 16**: Archetype Modifiers - 102 modifier tables
4. **Spec 17**: Archetype Caps - Defense/resistance/damage caps by AT
5. **Spec 19**: Build Totals - Defense (typed + positional aggregation)
6. **Spec 20**: Build Totals - Resistance (typed resistance aggregation)
7. **Spec 21**: Build Totals - Recharge (global recharge calculation)
8. **Spec 22**: Build Totals - Damage (global damage buff aggregation)

### High Priority Specs (19 specs) - Do After Critical

These are frequently used calculations needed for core functionality:

9. **Spec 02**: Power Damage
10. **Spec 03**: Power Buffs/Debuffs
11. **Spec 04**: Power Control Effects
12. **Spec 05**: Power Healing/Absorption
13. **Spec 06**: Power Endurance/Recovery
14. **Spec 07**: Power Recharge Modifiers
15. **Spec 08**: Power Accuracy/ToHit
16. **Spec 09**: Power Defense/Resistance
17. **Spec 11**: Enhancement Slotting
18. **Spec 13**: Enhancement Set Bonuses
19. **Spec 23**: Build Totals - Accuracy
20. **Spec 24**: Build Totals - Other Stats
21. **Spec 25**: Buff Stacking Rules
22. **Spec 29**: Incarnate Alpha Shifts
23. **Spec 32**: Pet Calculations
24. **Spec 34**: Proc Chance Formulas

**Medium/Low Priority Specs (16 specs):** Defer to future milestones

---

## Batch Strategy

Work through specs in **dependency order** within priority tiers:

**Phase 1: Foundation (Critical Specs 1-8)** - 2-3 weeks
- Batch 1A: Effect System & Enhancement Curves (Specs 01, 10)
- Batch 1B: Archetype System (Specs 16, 17)
- Batch 1C: Build Aggregation Core (Specs 19-22)

**Phase 2: Power Calculations (High Priority 9-16)** - 2-3 weeks
- Batch 2A: Core Power Effects (Specs 02-05)
- Batch 2B: Power Mechanics (Specs 06-09)

**Phase 3: Enhancement & Endgame (High Priority 17-24)** - 1-2 weeks
- Batch 3A: Enhancement Details (Specs 11, 13)
- Batch 3B: Build Totals Remaining (Specs 23, 24)
- Batch 3C: Stacking & Incarnates (Specs 25, 29, 32, 34)

---

## Depth Enhancement Template

For each spec, add the following sections after existing breadth content:

### New Section 1: Detailed Algorithm

```markdown
## Detailed Algorithm

### Complete Pseudocode

```python
def calculate_feature(inputs: InputType) -> OutputType:
    """
    Complete algorithm with all edge cases.

    Args:
        inputs: Description with exact types

    Returns:
        Description with exact types

    Raises:
        ErrorType: When specific condition
    """
    # Step 1: Validation
    if invalid_condition:
        raise ValueError("specific message")

    # Step 2: Core calculation with exact formula
    result = (input_value * COEFFICIENT + CONSTANT) * multiplier

    # Step 3: Apply caps/floors
    result = max(FLOOR, min(result, CAP))

    # Step 4: Edge case handling
    if special_condition:
        result = special_formula(result)

    return result
```

### Constants and Coefficients

| Name | Value | Source | Notes |
|------|-------|--------|-------|
| MAX_SLOTS | 6 | Game constant | Hard cap on power slots |
| ED_THRESHOLD_1 | 0.70 | Schedule A | First diminishing return |
```

### New Section 2: C# Implementation Details

```markdown
## C# Implementation Snippets

### Key Method from MidsReborn

```csharp
// File: Core/PowerEntry.cs:145-167
public float CalculateDamage(int level)
{
    float baseDamage = this.BaseDamage;
    float scale = this.Archetype.DamageScale[level];
    float enhanced = baseDamage * scale * (1 + this.GetEnhancement(eEnhType.Damage));
    return Math.Min(enhanced, this.Archetype.DamageCap);
}
```

### Edge Cases Handled

1. **Null archetype**: Returns 0 damage
2. **Level out of range**: Clamps to 1-50
3. **Negative enhancement**: Allows (can happen with debuffs)
```

### New Section 3: Database Schema

```markdown
## Database Schema

### Primary Table: `power_effects`

```sql
CREATE TABLE power_effects (
    id SERIAL PRIMARY KEY,
    power_id INTEGER NOT NULL REFERENCES powers(id),
    effect_type VARCHAR(50) NOT NULL,  -- 'damage', 'defense', etc.
    magnitude FLOAT NOT NULL,
    duration FLOAT DEFAULT 0,  -- 0 = instant/permanent
    probability FLOAT DEFAULT 1.0,  -- 1.0 = always
    aspect VARCHAR(50),  -- 'smashing', 'melee', etc.
    scale FLOAT DEFAULT 1.0,  -- AT scaling
    to_who VARCHAR(20) DEFAULT 'target',  -- 'target', 'self', 'team'
    pv_mode VARCHAR(10) DEFAULT 'pve',  -- 'pve', 'pvp', 'any'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_effect_type CHECK (effect_type IN ('damage', 'defense', ...)),
    CONSTRAINT valid_probability CHECK (probability >= 0 AND probability <= 1)
);

CREATE INDEX idx_power_effects_power_id ON power_effects(power_id);
CREATE INDEX idx_power_effects_type ON power_effects(effect_type);
```

### Related Tables

- `powers` - Foreign key reference
- `effect_modifiers` - Archetype-specific scaling
```

### New Section 4: Test Cases

```markdown
## Test Cases

### Test 1: Basic Damage Calculation

```python
def test_basic_damage_calculation():
    """
    Given: Power with 100 base damage, level 50 Scrapper (1.125 scale)
    When: No enhancements
    Then: Damage = 100 * 1.125 = 112.5
    """
    power = Power(base_damage=100.0)
    archetype = Archetype.SCRAPPER
    level = 50

    result = calculate_damage(power, archetype, level, enhancements=[])

    assert result == 112.5

### Test 2: Damage with Enhancement

```python
def test_damage_with_enhancement():
    """
    Given: Same power, 3 level 50 damage IOs (95.9% total)
    When: Apply enhancement
    Then: Damage = 100 * 1.125 * (1 + 0.959) = 220.3875
    """
    power = Power(base_damage=100.0)
    archetype = Archetype.SCRAPPER
    level = 50
    enhancements = [
        Enhancement(type='damage', value=0.4218),  # SO+3 from Spec 10
        Enhancement(type='damage', value=0.4218),
        Enhancement(type='damage', value=0.4218)
    ]

    result = calculate_damage(power, archetype, level, enhancements)

    assert abs(result - 220.39) < 0.01  # Floating point tolerance

### Test 3: Damage Cap

```python
def test_damage_cap():
    """
    Given: Power with 100 base damage, excessive enhancements
    When: Enhancement total = 500% (way over cap)
    Then: Damage capped at AT damage cap (400% for Scrappers)
    """
    power = Power(base_damage=100.0)
    archetype = Archetype.SCRAPPER  # 400% damage cap
    level = 50
    enhancements = [Enhancement(type='damage', value=5.0)]  # Unrealistic

    result = calculate_damage(power, archetype, level, enhancements)

    # Cap at 400%: 100 * 1.125 * 4.0 = 450
    assert result == 450.0

### Test 4: Edge Case - Level 1 Character

```python
def test_level_1_damage():
    """
    Given: Level 1 character (lower AT scaling)
    When: Calculate damage
    Then: Uses level 1 modifier (typically ~0.5x)
    """
    power = Power(base_damage=100.0)
    archetype = Archetype.SCRAPPER
    level = 1

    result = calculate_damage(power, archetype, level, enhancements=[])

    # Level 1 Scrapper scale ≈ 0.5625 (50% of level 50)
    assert abs(result - 56.25) < 0.01
```

### Test 5: Invalid Input Handling

```python
def test_invalid_level():
    """
    Given: Invalid level (0 or negative)
    When: Calculate damage
    Then: Raises ValueError
    """
    power = Power(base_damage=100.0)
    archetype = Archetype.SCRAPPER

    with pytest.raises(ValueError, match="Level must be between 1 and 50"):
        calculate_damage(power, archetype, level=0, enhancements=[])
```
```

### New Section 5: Python Implementation Guide

```markdown
## Python Implementation Guide

### Step 1: Define Types

```python
# backend/app/calculations/types.py

from enum import Enum
from dataclasses import dataclass
from typing import Optional

class EffectType(Enum):
    DAMAGE = "damage"
    DEFENSE = "defense"
    RESISTANCE = "resistance"
    # ... all 50+ types from Spec 01

class DamageType(Enum):
    SMASHING = "smashing"
    LETHAL = "lethal"
    # ... all 8 types

@dataclass
class Effect:
    """Represents a single game effect."""
    effect_type: EffectType
    magnitude: float
    duration: float = 0.0
    probability: float = 1.0
    aspect: Optional[str] = None  # DamageType, DefenseType, etc.
    scale: float = 1.0
    to_who: str = "target"
    pv_mode: str = "pve"

    def __post_init__(self):
        """Validate effect data."""
        if not 0 <= self.probability <= 1:
            raise ValueError(f"Probability must be 0-1, got {self.probability}")
        if self.duration < 0:
            raise ValueError(f"Duration cannot be negative, got {self.duration}")
```

### Step 2: Implement Core Calculator

```python
# backend/app/calculations/damage.py

from typing import List
from .types import Effect, EffectType, Archetype
from .modifiers import get_modifier  # From Spec 16
from .enhancement import apply_ed_curve  # From Spec 10

class DamageCalculator:
    """Calculate power damage with all modifiers."""

    def calculate(
        self,
        base_damage: float,
        archetype: Archetype,
        level: int,
        enhancements: List[Enhancement],
        buffs: Optional[List[Effect]] = None
    ) -> float:
        """
        Calculate final damage value.

        Args:
            base_damage: Power's base damage from database
            archetype: Character archetype (for scaling)
            level: Character level (1-50)
            enhancements: List of damage enhancements slotted
            buffs: Optional damage buff effects

        Returns:
            Final damage value after all modifiers

        Raises:
            ValueError: If level out of range or invalid inputs
        """
        # Step 1: Validate inputs
        if not 1 <= level <= 50:
            raise ValueError(f"Level must be between 1 and 50, got {level}")
        if base_damage < 0:
            raise ValueError(f"Base damage cannot be negative, got {base_damage}")

        # Step 2: Get AT damage scale for level
        scale = get_modifier(archetype, 'damage', level)

        # Step 3: Calculate enhancement bonus with ED
        enh_total = sum(e.value for e in enhancements if e.type == 'damage')
        enh_bonus = apply_ed_curve(enh_total, schedule='A')  # Damage uses Schedule A

        # Step 4: Calculate buff bonus (additive with enhancements)
        buff_total = sum(b.magnitude for b in buffs or [] if b.effect_type == EffectType.DAMAGE_BUFF)

        # Step 5: Apply formula
        damage = base_damage * scale * (1 + enh_bonus + buff_total)

        # Step 6: Apply damage cap
        cap = archetype.damage_cap  # From Spec 17
        damage = min(damage, base_damage * scale * cap)

        return damage
```

### Step 3: Integration with Database

```python
# backend/app/calculations/power_service.py

from sqlalchemy.orm import Session
from app.models import Power, PowerEffect
from .damage import DamageCalculator

class PowerCalculationService:
    """Service for calculating power statistics."""

    def __init__(self, db: Session):
        self.db = db
        self.damage_calc = DamageCalculator()

    def get_power_damage(
        self,
        power_id: int,
        archetype: Archetype,
        level: int,
        enhancements: List[Enhancement]
    ) -> float:
        """
        Get calculated damage for a power.

        Args:
            power_id: Database ID of power
            archetype: Character archetype
            level: Character level
            enhancements: Slotted enhancements

        Returns:
            Calculated damage value
        """
        # Load power from database
        power = self.db.query(Power).filter(Power.id == power_id).first()
        if not power:
            raise ValueError(f"Power {power_id} not found")

        # Get damage effects
        damage_effects = (
            self.db.query(PowerEffect)
            .filter(
                PowerEffect.power_id == power_id,
                PowerEffect.effect_type == 'damage'
            )
            .all()
        )

        # Sum base damage from all damage effects
        base_damage = sum(e.magnitude for e in damage_effects)

        # Calculate with enhancements and modifiers
        return self.damage_calc.calculate(
            base_damage=base_damage,
            archetype=archetype,
            level=level,
            enhancements=enhancements
        )
```

### Step 4: Write Tests

See Test Cases section above for complete test suite.

### Step 5: API Endpoint

```python
# backend/app/api/v1/endpoints/calculations.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.calculations.power_service import PowerCalculationService
from pydantic import BaseModel

router = APIRouter()

class DamageRequest(BaseModel):
    power_id: int
    archetype: str
    level: int
    enhancements: List[dict]

class DamageResponse(BaseModel):
    power_id: int
    base_damage: float
    calculated_damage: float
    archetype_scale: float
    enhancement_bonus: float

@router.post("/calculate/damage", response_model=DamageResponse)
def calculate_power_damage(
    request: DamageRequest,
    db: Session = Depends(get_db)
):
    """Calculate damage for a power with given parameters."""
    service = PowerCalculationService(db)

    try:
        damage = service.get_power_damage(
            power_id=request.power_id,
            archetype=Archetype[request.archetype.upper()],
            level=request.level,
            enhancements=parse_enhancements(request.enhancements)
        )

        return DamageResponse(
            power_id=request.power_id,
            calculated_damage=damage,
            # ... other response fields
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```
```

### New Section 6: Integration & Dependencies

```markdown
## Integration Points

### Upstream Dependencies (Must Be Implemented First)

1. **Spec 16: Archetype Modifiers** - Provides `get_modifier(at, type, level)`
2. **Spec 10: Enhancement Schedules** - Provides `apply_ed_curve(value, schedule)`
3. **Spec 01: Power Effects Core** - Provides `Effect` dataclass

### Downstream Consumers (Will Use This)

1. **Spec 19: Build Totals - Defense** - Uses damage calculations for DPS estimates
2. **Spec 32: Pet Calculations** - Uses damage for pet power calculations
3. **UI Components** - Power tooltip displays, build comparisons

### Integration Test

```python
def test_integration_with_modifiers():
    """Test that damage calculation correctly uses AT modifiers."""
    # This test requires Spec 16 to be implemented
    from app.calculations.modifiers import get_modifier

    power = Power(base_damage=100.0)
    archetype = Archetype.SCRAPPER
    level = 50

    # Get scale from modifier system
    scale = get_modifier(archetype, 'damage', level)
    assert scale == 1.125  # Known Scrapper scale

    # Calculate damage
    damage = calculate_damage(power, archetype, level, [])
    assert damage == 112.5
```
```

---

## Phase 1: Foundation (Critical Specs)

### Batch 1A: Effect System & Enhancement Curves

#### Task 1: Enhance Spec 01 - Power Effects Core

**Files:**
- Modify: `docs/midsreborn/calculations/01-power-effects-core.md`
- Reference: MidsReborn `Core/Base/Data_Classes/Effect.cs:1-450`
- Reference: MidsReborn `Core/GroupedFx.cs:1-800`

**Step 1: Deep dive into IEffect interface**

```bash
cd /Users/w/code/mids-hero-web/external/dev/MidsReborn/MidsReborn
rg "interface IEffect" Core/Base/Data_Classes/Effect.cs -A 50
rg "class Effect.*:.*IEffect" Core/Base/Data_Classes/Effect.cs -A 100
```

Expected: Full IEffect property list with types, getters/setters

**Step 2: Extract all effect type enum values**

```bash
rg "enum.*eEffectType" Core/Enums.cs -A 200 | head -100
```

Expected: Complete list of 50+ effect types with comments

**Step 3: Analyze GroupedFx aggregation algorithm**

```bash
rg "class GroupedFx" Core/GroupedFx.cs -A 50
rg "Add.*Effect|Aggregate.*Effect" Core/GroupedFx.cs -C 10
```

Expected: Exact grouping and stacking logic

**Step 4: Add detailed algorithm section**

Add to spec after "Game Mechanics Context" section:

```markdown
## Detailed Algorithm

### Complete Effect Aggregation Pseudocode

[Insert complete pseudocode from template above]

### Constants and Coefficients

[Table of all stacking mode constants]
```

**Step 5: Extract C# code snippets**

Copy key methods with line numbers from:
- `Effect.cs` - IEffect properties (lines X-Y)
- `GroupedFx.cs` - Add/Aggregate methods (lines X-Y)

**Step 6: Define database schema**

Design `power_effects` table (see template above)

**Step 7: Write 10+ test cases**

Cover:
- Basic effect creation
- Effect grouping by type+aspect
- Additive stacking
- Multiplicative stacking
- Best-value stacking
- Edge cases (null, negative, zero magnitude)

**Step 8: Add Python implementation guide**

Full step-by-step with types (see template)

**Step 9: Document integration points**

Dependencies: None (foundation)
Consumers: All other specs

**Step 10: Update spec status and commit**

```bash
# Update spec header status from 🟡 Breadth Complete to 🟢 Depth Complete
git add docs/midsreborn/calculations/01-power-effects-core.md
git commit -m "docs: add depth detail to Spec 01 - Power Effects Core (1/27)"
```

---

#### Task 2: Enhance Spec 10 - Enhancement Schedules (ED Curves)

**Files:**
- Modify: `docs/midsreborn/calculations/10-enhancement-schedules.md`
- Reference: MidsReborn `Core/Enhancement.cs:400-600` (ED implementation)

**Step 1: Extract exact ED curve formulas**

```bash
rg "SCHEDULE_A|SCHEDULE_B|SCHEDULE_C|SCHEDULE_D" Core/Enhancement.cs -C 15
rg "ApplyED|CalculateED" Core/Enhancement.cs -C 20
```

Expected: Exact threshold values and diminishing return formulas

**Step 2: Document all 4 schedules**

For each schedule (A, B, C, D):
- Threshold 1 value
- Threshold 2 value
- Diminishing return factor 1
- Diminishing return factor 2
- Which attributes use this schedule

**Step 3: Create exact formula table**

| Schedule | Attributes | Threshold 1 | Threshold 2 | Factor 1 | Factor 2 |
|----------|-----------|-------------|-------------|----------|----------|
| A | Damage, ... | 0.70 | 1.00 | 0.85 | 0.75 |
| ... | ... | ... | ... | ... | ... |

**Step 4: Write pseudocode with exact math**

```python
def apply_ed_curve(total_enhancement: float, schedule: str) -> float:
    """Apply Enhancement Diversification curve."""
    thresholds = SCHEDULES[schedule]

    if total_enhancement <= thresholds['t1']:
        # No diminishing returns below first threshold
        return total_enhancement
    elif total_enhancement <= thresholds['t2']:
        # Partial diminishing returns between thresholds
        base = thresholds['t1']
        excess = total_enhancement - thresholds['t1']
        return base + (excess * thresholds['factor1'])
    else:
        # Full diminishing returns above second threshold
        base = thresholds['t1'] + ((thresholds['t2'] - thresholds['t1']) * thresholds['factor1'])
        excess = total_enhancement - thresholds['t2']
        return base + (excess * thresholds['factor2'])
```

**Step 5: Create test cases with exact values**

Test Schedule A with known inputs/outputs:
- 0.50 → 0.50 (below threshold)
- 0.95 → ? (between thresholds)
- 2.00 → ? (above threshold)

Get expected values from MidsReborn or community sources

**Step 6: Add C# code snippets**

Extract exact ED calculation from Enhancement.cs

**Step 7: Complete all depth sections**

**Step 8: Commit**

```bash
git add docs/midsreborn/calculations/10-enhancement-schedules.md
git commit -m "docs: add depth detail to Spec 10 - ED Curves (2/27) - CRITICAL"
```

---

### Batch 1B: Archetype System

#### Task 3: Enhance Spec 16 - Archetype Modifiers

**Files:**
- Modify: `docs/midsreborn/calculations/16-archetype-modifiers.md`
- Reference: MidsReborn `Core/Base/Data_Classes/Archetype.cs`
- Reference: MidsReborn `Core/DatabaseAPI.cs` (modifier lookups)

**Step 1: Find modifier table structure**

```bash
rg "class Archetype" Core/Base/Data_Classes/Archetype.cs -A 100
rg "Modifier\[|ModTable" Core/Base/Data_Classes/Archetype.cs
```

**Step 2: Document 102 modifier table structure**

- 55 levels (0-54, level 50 at index 49)
- 60+ archetype columns
- Float values (scaling factors)

**Step 3: Extract sample modifier values**

For Scrapper at level 50:
- Damage modifier: 1.125
- Defense modifier: 0.75
- Resistance modifier: 0.75
- ToHit modifier: 1.0

**Step 4: Create lookup algorithm**

```python
def get_modifier(archetype: Archetype, effect_type: str, level: int) -> float:
    """
    Get AT modifier for effect type at level.

    Loads from modifier_tables table in database.
    """
    # Validate level (1-55)
    if not 1 <= level <= 55:
        raise ValueError(f"Level must be 1-55, got {level}")

    # Query database
    row = db.query(ModifierTable).filter(
        ModifierTable.archetype == archetype.value,
        ModifierTable.effect_type == effect_type,
        ModifierTable.level == level
    ).first()

    if not row:
        # Default to 1.0 if not found
        return 1.0

    return row.modifier_value
```

**Step 5: Define database schema**

```sql
CREATE TABLE modifier_tables (
    id SERIAL PRIMARY KEY,
    archetype VARCHAR(50) NOT NULL,
    effect_type VARCHAR(50) NOT NULL,
    level INTEGER NOT NULL,
    modifier_value FLOAT NOT NULL,
    CONSTRAINT unique_modifier UNIQUE (archetype, effect_type, level),
    CONSTRAINT valid_level CHECK (level >= 1 AND level <= 55)
);

CREATE INDEX idx_modifier_lookup ON modifier_tables(archetype, effect_type, level);
```

**Step 6: Write test cases**

- Test Scrapper damage at level 50 = 1.125
- Test Tanker damage at level 50 = 0.8
- Test invalid level raises error
- Test unknown AT defaults to 1.0

**Step 7: Complete depth sections and commit**

```bash
git commit -m "docs: add depth detail to Spec 16 - Archetype Modifiers (3/27) - CRITICAL"
```

---

#### Task 4: Enhance Spec 17 - Archetype Caps

**Files:**
- Modify: `docs/midsreborn/calculations/17-archetype-caps.md`
- Reference: MidsReborn `Core/Base/Data_Classes/Archetype.cs` (cap properties)

**Step 1: Extract all cap values**

```bash
rg "Cap|Max.*Resist|Max.*Defense|Max.*Damage" Core/Base/Data_Classes/Archetype.cs
```

**Step 2: Create comprehensive cap table**

| Archetype | Defense Cap | Resistance Cap | Damage Cap | Regen Cap | Recovery Cap |
|-----------|-------------|----------------|------------|-----------|--------------|
| Blaster | 175% | 75% | 500% | 2400% | 300% |
| Scrapper | 175% | 75% | 400% | 2400% | 300% |
| Tanker | 225% | 90% | 300% | 2400% | 300% |
| ... | ... | ... | ... | ... | ... |

**Step 3: Implement cap application algorithm**

**Step 4: Write test cases for each AT**

**Step 5: Complete and commit**

```bash
git commit -m "docs: add depth detail to Spec 17 - Archetype Caps (4/27) - CRITICAL"
```

---

### Batch 1C: Build Aggregation Core

#### Task 5: Enhance Spec 19 - Build Totals Defense

**Files:**
- Modify: `docs/midsreborn/calculations/19-build-totals-defense.md`
- Reference: MidsReborn `Core/Stats.cs` (defense totals)

**Step 1: Analyze defense calculation**

```bash
rg "Defense.*Total|CalculateDefense" Core/Stats.cs -C 20
```

**Step 2: Document typed vs positional defense**

- Typed: Smashing, Lethal, Fire, Cold, Energy, Negative, Toxic, Psionic
- Positional: Melee, Ranged, AoE

**Step 3: Explain stacking rule**

Defense uses highest of typed OR positional (not both)

**Step 4: Create aggregation algorithm**

**Step 5: Add 45% soft cap documentation**

**Step 6: Write comprehensive tests**

**Step 7: Complete and commit**

```bash
git commit -m "docs: add depth detail to Spec 19 - Build Totals Defense (5/27) - CRITICAL"
```

---

#### Task 6-8: Enhance Specs 20-22 (Resistance, Recharge, Damage)

Follow similar pattern to Spec 19 for:
- Spec 20: Resistance (typed, caps by AT)
- Spec 21: Recharge (global + per-power, 400% cap)
- Spec 22: Damage (global buff, caps by AT)

**Commits:**

```bash
git commit -m "docs: add depth detail to Spec 20 - Build Totals Resistance (6/27) - CRITICAL"
git commit -m "docs: add depth detail to Spec 21 - Build Totals Recharge (7/27) - CRITICAL"
git commit -m "docs: add depth detail to Spec 22 - Build Totals Damage (8/27) - CRITICAL"
```

---

## Phase 1 Checkpoint

After Task 8, verify:
- ✅ 8 Critical specs enhanced with depth detail
- ✅ Each spec has: exact formulas, database schemas, test cases, Python guide
- ✅ Status changed from 🟡 Breadth to 🟢 Depth Complete
- ✅ All committed with descriptive messages

**Progress: 8 / 27 depth specs (30%)**

**Pause for review** before proceeding to Phase 2.

---

## Phase 2: Power Calculations (High Priority)

### Batch 2A: Core Power Effects

#### Task 9: Enhance Spec 02 - Power Damage

Follow same depth template as Phase 1 specs:
1. Extract exact damage formula from PowerEntry.cs
2. Document all damage types (8 types)
3. Create damage scale lookup integration
4. Write 10+ test cases
5. Complete Python implementation guide

**Commit:**

```bash
git commit -m "docs: add depth detail to Spec 02 - Power Damage (9/27)"
```

---

#### Task 10-12: Enhance Specs 03-05

- Spec 03: Power Buffs/Debuffs (magnitude, duration calculations)
- Spec 04: Power Control Effects (mez magnitude, protection vs resistance)
- Spec 05: Power Healing/Absorption (heal amount, absorption caps)

**Commits:**

```bash
git commit -m "docs: add depth detail to Spec 03 - Power Buffs/Debuffs (10/27)"
git commit -m "docs: add depth detail to Spec 04 - Power Control Effects (11/27)"
git commit -m "docs: add depth detail to Spec 05 - Power Healing/Absorption (12/27)"
```

---

### Batch 2B: Power Mechanics

#### Task 13-16: Enhance Specs 06-09

- Spec 06: Power Endurance/Recovery (endurance cost, recovery rate)
- Spec 07: Power Recharge Modifiers (per-power + global recharge)
- Spec 08: Power Accuracy/ToHit (multiplicative vs additive)
- Spec 09: Power Defense/Resistance (power-granted def/res)

**Commits:**

```bash
git commit -m "docs: add depth detail to Spec 06 - Power Endurance/Recovery (13/27)"
git commit -m "docs: add depth detail to Spec 07 - Power Recharge Modifiers (14/27)"
git commit -m "docs: add depth detail to Spec 08 - Power Accuracy/ToHit (15/27)"
git commit -m "docs: add depth detail to Spec 09 - Power Defense/Resistance (16/27)"
```

---

## Phase 2 Checkpoint

After Task 16, verify:
- ✅ 16 specs total enhanced (8 Critical + 8 High)
- ✅ All power calculation specs have depth detail
- ✅ Committed with clear messages

**Progress: 16 / 27 depth specs (59%)**

**Pause for review** before Phase 3.

---

## Phase 3: Enhancement & Endgame

### Batch 3A: Enhancement Details

#### Task 17: Enhance Spec 11 - Enhancement Slotting

**Focus:**
- I9Slot class structure
- Combining multiple enhancement aspects
- IO vs SO vs HO differences

**Commit:**

```bash
git commit -m "docs: add depth detail to Spec 11 - Enhancement Slotting (17/27)"
```

---

#### Task 18: Enhance Spec 13 - Enhancement Set Bonuses

**Focus:**
- Set bonus activation thresholds (2/6, 3/6, 4/6, 5/6, 6/6)
- Rule of 5 suppression exact algorithm
- Set bonus stacking rules

**Commit:**

```bash
git commit -m "docs: add depth detail to Spec 13 - Enhancement Set Bonuses (18/27)"
```

---

### Batch 3B: Build Totals Remaining

#### Task 19-20: Enhance Specs 23-24

- Spec 23: Build Totals - Accuracy (accuracy vs tohit distinction)
- Spec 24: Build Totals - Other Stats (HP, regen, endurance, recovery, movement)

**Commits:**

```bash
git commit -m "docs: add depth detail to Spec 23 - Build Totals Accuracy (19/27)"
git commit -m "docs: add depth detail to Spec 24 - Build Totals Other Stats (20/27)"
```

---

### Batch 3C: Stacking & Incarnates

#### Task 21: Enhance Spec 25 - Buff Stacking Rules

**Focus:**
- Additive stacking exact formula
- Multiplicative stacking exact formula
- Best-value-only selection algorithm
- Rule of 5 implementation

**Commit:**

```bash
git commit -m "docs: add depth detail to Spec 25 - Buff Stacking Rules (21/27)"
```

---

#### Task 22: Enhance Spec 29 - Incarnate Alpha Shifts

**Focus:**
- Level shift calculation (+1/+2/+3 total)
- Alpha boost application (subject to ED)
- Effective level calculation
- Purple Patch integration

**Commit:**

```bash
git commit -m "docs: add depth detail to Spec 29 - Incarnate Alpha Shifts (22/27)"
```

---

#### Task 23: Enhance Spec 32 - Pet Calculations

**Focus:**
- Stat inheritance rules (what pets inherit, what they don't)
- Pet enhancement separate from caster
- Pet power calculation
- Mastermind upgrade mechanics

**Commit:**

```bash
git commit -m "docs: add depth detail to Spec 32 - Pet Calculations (23/27)"
```

---

#### Task 24: Enhance Spec 34 - Proc Chance Formulas

**Focus:**
- PPM formula exact coefficients
- Area factor calculation
- Min/max proc caps
- Toggle/Auto vs Click differences

**Commit:**

```bash
git commit -m "docs: add depth detail to Spec 34 - Proc Chance Formulas (24/27)"
```

---

## Phase 3 Checkpoint

After Task 24, verify:
- ✅ 24 specs total enhanced
- ✅ All high-priority enhancement and endgame specs complete
- ✅ Progress: 24 / 27 (89%)

**3 specs remaining** (from High priority list, if any were missed)

---

## Final Tasks (25-27)

Complete any remaining High priority specs from the list that haven't been covered yet.

**Final Commits:**

```bash
git commit -m "docs: add depth detail to Spec [X] - [Name] (25/27)"
git commit -m "docs: add depth detail to Spec [X] - [Name] (26/27)"
git commit -m "docs: add depth detail to Spec [X] - [Name] (27/27) - MILESTONE 3 COMPLETE"
```

---

## Milestone 3 Completion Criteria

✅ **All tasks complete when:**

1. All 27 high-priority specs (8 Critical + 19 High) have depth detail:
   - ✅ Exact formulas with coefficients
   - ✅ Complete algorithm pseudocode
   - ✅ C# code snippets with line numbers
   - ✅ Database schema definitions
   - ✅ Comprehensive test cases (10+ per spec)
   - ✅ Python implementation guide (step-by-step)
   - ✅ Integration points documented

2. Each enhanced spec:
   - ✅ Status changed from 🟡 Breadth to 🟢 Depth Complete
   - ✅ Contains 8-12 pages of implementation-ready detail
   - ✅ Test cases have expected values (not just placeholders)
   - ✅ Database schemas are CREATE-ready SQL

3. Quality checks:
   - ✅ Formulas verified against MidsReborn C# code
   - ✅ Test cases reference known game values when possible
   - ✅ Python code follows type hints and best practices
   - ✅ All specs committed with clear messages

---

## Estimated Timeline

**Assumptions:**
- 4-8 hours per spec for depth enhancement
- Work in phases (foundation → power → enhancement)
- Review checkpoints between phases
- Some specs faster (similar patterns), some slower (complex mechanics)

**Schedule:**

- **Week 1-2**: Phase 1 - Foundation (8 Critical specs)
  - Batch 1A: Effect System & ED (2 specs, 2-3 days)
  - Batch 1B: Archetype System (2 specs, 2-3 days)
  - Batch 1C: Build Aggregation (4 specs, 4-6 days)

- **Week 3-4**: Phase 2 - Power Calculations (8 High priority specs)
  - Batch 2A: Core Effects (4 specs, 4-5 days)
  - Batch 2B: Power Mechanics (4 specs, 4-5 days)

- **Week 5-6**: Phase 3 - Enhancement & Endgame (11 High priority specs)
  - Batch 3A: Enhancement Details (2 specs, 2-3 days)
  - Batch 3B: Build Totals (2 specs, 2-3 days)
  - Batch 3C: Stacking & Incarnates (4 specs, 4-5 days)
  - Final Tasks (3 specs, 3-4 days)

**Total: 4-6 weeks for depth coverage of 27 high-priority specs**

---

## Next Steps After Milestone 3

With 27 high-priority specs at depth level:

1. **Begin Python Implementation** - Start coding calculation engine
   - Follow specs as implementation blueprints
   - Write tests from spec test cases
   - Implement in dependency order

2. **Create FastAPI Endpoints** - Expose calculations via API
   - `/calculate/damage`
   - `/calculate/defense`
   - `/calculate/build-totals`
   - etc.

3. **Milestone 4: Medium Priority Depth** (Optional)
   - Add depth to 14 Medium priority specs
   - Based on actual implementation needs

4. **Integration Testing** - Full build calculation workflows
   - Load build from database
   - Calculate all stats
   - Compare to MidsReborn output
   - Validate accuracy

---

## Notes for Executor

**Remember:**
- **Exact values required** - No "approximately" or "roughly"
- **Test cases must pass** - Expected values from game data or MidsReborn
- **C# line numbers** - Include specific line ranges in snippets
- **SQL CREATE-ready** - Database schemas must be executable
- **Type hints always** - Python code must have full type annotations
- **Commit per spec** - Never batch multiple specs in one commit
- **Review between phases** - Pause at checkpoints for quality check

**MidsReborn deep analysis:**
- Use `rg -C 20` for context around key methods
- Extract exact constant values (not "about 0.7")
- Copy C# code snippets with `// File:Line` comments
- Cross-reference multiple files to confirm formulas

**Quality bar:**
- Could a developer implement directly from spec? ✅
- Do test cases have real expected values? ✅
- Are formulas exact (not approximate)? ✅
- Is database schema production-ready? ✅

---

**This plan creates implementation-ready specifications that enable direct Python coding without needing to reference MidsReborn C# code.**
