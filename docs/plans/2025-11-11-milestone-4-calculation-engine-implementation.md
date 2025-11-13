# Milestone 4: Calculation Engine Implementation

**Created**: 2025-11-11
**Status**: In Progress
**Branch**: `feature/calculation-engine-foundation`
**Prerequisites**: Milestone 3 Complete (24 depth-level specs)
**Spec Location**: `/Users/w/code/mids-hero-web/docs/midsreborn/calculations/`
**Spec Mapping**: See `docs/plans/spec-to-implementation-mapping.md` for complete mapping

---

## Overview

Implement the Mids Hero Web calculation engine in Python based on 24 depth-complete specifications. This milestone transforms documentation into production-ready code with 100% MidsReborn compatibility.

### Success Criteria

✅ All calculator classes implemented with full type hints
✅ All database schemas created and migrated
✅ All test cases from specs passing (150+ tests)
✅ 100% compatibility with MidsReborn formulas
✅ FastAPI endpoints exposing calculation services

---

## Phase 1: Core Foundation (Week 1-2)

**Goal**: Implement foundational systems that all other calculations depend on.

### Batch 1A: Effect System (Spec 01)

**Files to Create**:

- `backend/app/calculations/core/effect_types.py` - 85 effect type enums
- `backend/app/calculations/core/effect.py` - IEffect dataclass (115 properties)
- `backend/app/calculations/core/grouped_fx.py` - GroupedFx aggregation
- `backend/app/calculations/core/enums.py` - ToWho, PvMode, etc.

**Database Migration**:

```sql
-- Create effect_types table (85 types)
-- Create effects table with 115 columns
-- Add indexes for fast lookups
```

**Tests** (from Spec 01 section 4):

- Test 1: Basic damage effect (50 magnitude, 0 duration, 100% probability)
- Test 2: DoT effect (10 magnitude, 10s duration, 0.5 probability)
- Test 3: GroupedFx sum aggregation (3 effects → 120 total)
- Test 4: GroupedFx max aggregation (3 effects → 50 max)
- Test 5: ToWho filtering (Self vs Target)
- Test 6: PvMode filtering (PvE vs PvP)

**Implementation Notes**:

```python
# From Spec 01, section 5
@dataclass
class Effect:
    effect_type: EffectType
    magnitude: float
    duration: float = 0.0
    probability: float = 1.0
    aspect: Optional[str] = None
    scale: float = 1.0
    to_who: ToWho = ToWho.TARGET
    pv_mode: PvMode = PvMode.PVE
    # ... 107 more properties
```

**Validation**: All 6 test cases must pass with exact values from Spec 01.

---

### Batch 1B: Enhancement Schedules (Spec 10)

**Files to Create**:

- `backend/app/calculations/core/enhancement_schedules.py` - ED curves (A, B, C, D)
- `backend/app/calculations/core/constants.py` - BASE_MAGIC, ED thresholds

**Database Migration**:

```sql
-- Create enhancement_schedules table
-- Insert 4 schedules with exact threshold values
```

**Tests** (from Spec 10 section 4):

- Test 1: Schedule A at 50% → 50.0% (no diminishing)
- Test 2: Schedule A at 75% → 73.0% (90% efficiency)
- Test 3: Schedule A at 95% → 88.75% (15% efficiency after 90%)
- Test 4: Schedule B at 100% → 56.0% (strict curve)
- Test 5: Schedule C at 150% → 97.5% (very strict)
- Test 6: Schedule D at 200% → 200.0% (no diminishing)

**Implementation Notes**:

```python
# From Spec 10, section 5 - Exact C# logic
def apply_schedule_a(total_enhancement: float) -> float:
    if total_enhancement <= 0.700:
        return total_enhancement
    elif total_enhancement <= 0.900:
        return 0.700 + (total_enhancement - 0.700) * 0.899999976158142
    else:
        return 0.880 + (total_enhancement - 0.900) * 0.150000005960464
```

**Validation**: All 6 test cases must match exact values from Spec 10.

---

### Batch 1C: Archetype Modifiers (Spec 16)

**Files to Create**:

- `backend/app/calculations/core/archetype_modifiers.py` - 102 modifier tables
- `backend/app/calculations/core/modifier_loader.py` - Load from AttribMod.json

**Database Migration**:

```sql
-- Create archetype_modifiers table
-- 102 tables × 50 levels = 5,100 rows
-- Add indexes on (archetype, table_name, level)
```

**Tests** (from Spec 16 section 4):

- Test 1: Scrapper melee damage at level 50 → -30.59
- Test 2: Blaster ranged damage at level 50 → -41.97
- Test 3: Tanker damage resistance at level 50 → -42.50
- Test 4: Controller hold duration at level 50 → -50.00
- Test 5: Defender heal at level 50 → -50.00
- Test 6: Brute damage at level 1 → -24.92 (scales with level)

**Implementation Notes**:

```python
# From Spec 16, section 5
def get_modifier(archetype: str, table_name: str, level: int) -> float:
    # Load from database or cache
    return modifier_value  # e.g., -30.59 for Scrapper melee at 50
```

**Validation**: All 6 test cases must match exact values from AttribMod.json.

---

### Batch 1D: Archetype Caps (Spec 17)

**Files to Create**:

- `backend/app/calculations/core/archetype_caps.py` - Cap limits per AT
- `backend/app/calculations/core/cap_loader.py` - Load from .mhd files

**Database Migration**:

```sql
-- Create archetype_caps table
-- 15 archetypes × ~20 cap types = 300 rows
```

**Tests** (from Spec 17 section 4):

- Test 1: Tanker resistance cap → 0.90 (90%)
- Test 2: Brute damage cap → 7.75 (775%)
- Test 3: Blaster damage cap → 5.0 (500%)
- Test 4: Scrapper defense cap → 2.25 (225%)
- Test 5: Controller recharge cap → 4.0 (400%)
- Test 6: Defender ToHit cap → 5.95 (595%)

**Implementation Notes**:

```python
# From Spec 17, section 5
@dataclass
class ArchetypeCaps:
    archetype: str
    damage_cap: float = 4.0  # Default 400%
    resistance_cap: float = 0.75  # Default 75%
    defense_cap: float = 2.25  # Default 225%
    recharge_cap: float = 4.0  # Default 400%
    tohit_cap: float = 5.95  # Default 595%
    # ... more caps
```

**Validation**: All 6 test cases must match exact values from .mhd files.

---

## Phase 2: Build Aggregation (Week 3)

**Goal**: Implement build-level totals for all attribute types.

### Batch 2A: Defense & Resistance (Specs 19, 20)

**Files to Create**:

- `backend/app/calculations/build/defense_aggregator.py` - "Highest wins" logic
- `backend/app/calculations/build/resistance_aggregator.py` - Additive stacking
- `backend/app/calculations/build/build_totals.py` - Main aggregation class

**Tests** (12 total: 6 from Spec 19, 6 from Spec 20):

- Defense Test 1: Smashing typed only → 30.0%
- Defense Test 2: Melee positional only → 40.0%
- Defense Test 3: Both sources → 40.0% (highest wins!)
- Defense Test 4: Defense debuff resistance (DDR) → 23% effective debuff
- Resistance Test 1: Power only → 30.0%
- Resistance Test 2: Multiple sources → 75.0% (additive)

**Validation**: All tests must implement exact formulas from specs.

---

### Batch 2B: Recharge & Damage (Specs 21, 22)

**Files to Create**:

- `backend/app/calculations/build/recharge_aggregator.py` - Global recharge
- `backend/app/calculations/build/damage_aggregator.py` - Damage buff heuristic

**Tests** (12 total: 6 from Spec 21, 6 from Spec 22):

- Recharge Test 1: 70% global recharge → Hasten 120s → 70.6s (perma-ready)
- Recharge Test 2: 400% cap enforcement
- Damage Test 1: Max/avg/min heuristic selection

**Validation**: All tests must match MidsReborn TotalBuilder.cs logic.

---

### Batch 2C: Accuracy & Other Stats (Specs 23, 24)

**Files to Create**:

- `backend/app/calculations/build/accuracy_aggregator.py` - Global accuracy/tohit
- `backend/app/calculations/build/other_stats_aggregator.py` - 30+ stats

**Tests** (12 total: 6 from Spec 23, 6 from Spec 24):

- Accuracy Test 1: Kismet IO → +6% tohit
- Other Stats Test 1: HP calculation with accolades

**Validation**: All tests must use exact formulas from specs.

---

## Phase 3: Power Calculations (Week 4-5)

**Goal**: Implement all power effect calculations.

### Batch 3A: Damage & Buffs (Specs 02, 03)

**Files to Create**:

- `backend/app/calculations/powers/damage_calculator.py` - DPA/DPS modes
- `backend/app/calculations/powers/buff_calculator.py` - Multiplicative stacking

**Tests** (12 total):

- Damage Test 1: Basic attack with probability threshold (0.999)
- Damage Test 2: Toggle enhancement (10s tick duration)
- Buff Test 1: Multiple buffs with multiplicative stacking

**Validation**: All tests must match exact values from specs.

---

### Batch 3B: Control & Healing (Specs 04, 05)

**Files to Create**:

- `backend/app/calculations/powers/control_calculator.py` - Magnitude > protection
- `backend/app/calculations/powers/healing_calculator.py` - BASE_MAGIC (1.666667)

**Tests** (12 total):

- Control Test 1: Mag 3 vs Mag 12 protection → No effect
- Healing Test 1: Regeneration with BASE_MAGIC conversion

**Validation**: All tests must use exact constants from specs.

---

### Batch 3C: Endurance & Recharge (Specs 06, 07)

**Files to Create**:

- `backend/app/calculations/powers/endurance_calculator.py` - Toggle cost formula
- `backend/app/calculations/powers/recharge_calculator.py` - Local × global

**Tests** (12 total):

- Endurance Test 1: Toggle cost with 30s tick
- Recharge Test 1: Power recharge with global buffs

**Validation**: All tests must match exact formulas from specs.

---

### Batch 3D: Accuracy & Defense (Specs 08, 09)

**Files to Create**:

- `backend/app/calculations/powers/accuracy_calculator.py` - Final accuracy formula
- `backend/app/calculations/powers/defense_calculator.py` - Effective defense

**Tests** (12 total):

- Accuracy Test 1: Base × (1 + enh + globalAcc) × (scalingToHit + globalToHit)
- Defense Test 1: Highest of typed/positional

**Validation**: All tests must match exact formulas from specs.

---

## Phase 4: Advanced Features (Week 6-7)

**Goal**: Implement enhancements, incarnates, pets, and procs.

### Batch 4A: Enhancement System (Specs 11, 13)

**Files to Create**:

- `backend/app/calculations/enhancements/slotting.py` - Max 6 slots, attuned/catalyzed
- `backend/app/calculations/enhancements/set_bonuses.py` - Rule of 5

**Tests** (12 total):

- Slotting Test 1: Boosted IO (+5.2% per level)
- Set Bonus Test 1: Rule of 5 (6th instance suppressed)

**Validation**: All tests must implement exact rules from specs.

---

### Batch 4B: Stacking & Incarnates (Specs 25, 29)

**Files to Create**:

- `backend/app/calculations/build/stacking_rules.py` - 6 eStacking modes
- `backend/app/calculations/incarnates/alpha_calculator.py` - T1-T4 tiers, level shifts

**Tests** (12 total):

- Stacking Test 1: Additive vs multiplicative modes
- Alpha Test 1: T4 Musculature (+33% damage → ~28.5% after ED)

**Validation**: All tests must match exact formulas from specs.

---

### Batch 4C: Pets & Procs (Specs 32, 34)

**Files to Create**:

- `backend/app/calculations/powers/pet_calculator.py` - Selective inheritance
- `backend/app/calculations/enhancements/proc_calculator.py` - PPM formula

**Tests** (12 total):

- Pet Test 1: Inherits accuracy/damage (NOT recharge/defense)
- Proc Test 1: PPM × (recharge + cast) / (60 × area_factor)

**Validation**: All tests must match exact formulas from specs.

---

## Phase 5: API Integration (Week 8)

**Goal**: Expose calculation services via FastAPI endpoints.

### API Endpoints to Create

**Core Calculations**:

- `POST /api/v1/calculations/power/damage` - Calculate power damage
- `POST /api/v1/calculations/power/buffs` - Calculate buff effects
- `POST /api/v1/calculations/power/control` - Calculate control effects
- `POST /api/v1/calculations/power/healing` - Calculate healing/regen
- `POST /api/v1/calculations/power/accuracy` - Calculate accuracy/tohit

**Build Calculations**:

- `POST /api/v1/calculations/build/totals` - Calculate all build totals
- `POST /api/v1/calculations/build/defense` - Calculate defense totals
- `POST /api/v1/calculations/build/resistance` - Calculate resistance totals
- `GET /api/v1/calculations/constants` - Get all game constants

**Enhancement Calculations**:

- `POST /api/v1/calculations/enhancements/slotting` - Calculate slotted values
- `POST /api/v1/calculations/enhancements/set-bonuses` - Calculate set bonuses
- `POST /api/v1/calculations/enhancements/procs` - Calculate proc chances

### Testing Strategy

Each endpoint must have:

- Unit tests with exact values from specs
- Integration tests with full builds
- Performance tests (< 100ms response time)

---

## Implementation Guidelines

### Code Quality Standards

1. **Type Safety**: All Python code uses dataclasses and full type hints
2. **Error Handling**: Custom exceptions for validation errors
3. **Documentation**: Comprehensive docstrings with Args/Returns/Raises
4. **Testing**: pytest with exact expected values (not approximations)
5. **Performance**: Cache frequently accessed data (modifiers, caps)

### Test-Driven Development (TDD)

For each batch:

1. Write tests FIRST using exact values from specs
2. Watch tests FAIL (Red)
3. Implement minimal code to pass (Green)
4. Refactor for clarity (Refactor)
5. Repeat for next test

### Database Schema Standards

All calculation-related tables:

- Use `NUMERIC(10,6)` for precise floating-point values
- Include proper indexes for fast lookups
- Add foreign keys for referential integrity
- Document with SQL comments

### Git Workflow

Each batch completion:

```bash
git add .
git commit -m "feat(calcs): implement [Batch Name] - [Specs]"
git push origin feature/calculation-engine-foundation
```

Final PR after Phase 5:

```bash
gh pr create --title "Milestone 4: Calculation Engine Implementation" \
  --body "Implements 24 calculation specs with 150+ tests passing"
```

---

## Dependencies Between Batches

```
Phase 1 (Foundation)
└── Phase 2 (Build Aggregation) - Depends on Effect system, ED curves, AT modifiers/caps
    └── Phase 3 (Power Calculations) - Depends on Build Aggregation
        └── Phase 4 (Advanced Features) - Depends on Power Calculations
            └── Phase 5 (API Integration) - Depends on all calculators
```

**Critical Path**: Must complete Phase 1 before starting Phase 2.

---

## Success Metrics

### Code Metrics

- ✅ 150+ tests passing (all from specs)
- ✅ 95%+ code coverage
- ✅ 0 type errors (mypy strict mode)
- ✅ 0 linting errors (ruff)

### Compatibility Metrics

- ✅ 100% formula compatibility with MidsReborn
- ✅ All test cases match exact expected values
- ✅ All constants match C# source exactly

### Performance Metrics

- ✅ < 100ms API response time (95th percentile)
- ✅ < 1s build total calculation
- ✅ < 10ms single power calculation

---

## Risk Mitigation

### High-Risk Areas

1. **Archetype Modifier Loading** (102 tables × 50 levels = 5,100 values)

   - Mitigation: Cache in memory, validate against known values

2. **GroupedFx Aggregation** (Complex sum/max/average logic)

   - Mitigation: Extensive unit tests with edge cases

3. **Defense "Highest Wins"** (Common player misconception)

   - Mitigation: Document clearly, add explicit tests

4. **Enhancement Diversification** (Exact floating-point thresholds)
   - Mitigation: Use exact constants from C# source

### Testing Strategy

- Unit tests: Each calculator in isolation
- Integration tests: Full build calculations
- Compatibility tests: Compare with MidsReborn output
- Performance tests: Benchmark against targets

---

## Completion Checklist

### Phase 1: Core Foundation ✅ COMPLETE

- [x] Batch 1A: Effect System (Spec 01) - `docs/midsreborn/calculations/01-power-effects-core.md`
- [x] Batch 1B: Enhancement Schedules (Spec 10) - `docs/midsreborn/calculations/10-enhancement-schedules.md`
- [x] Batch 1C: Archetype Modifiers (Spec 16) - `docs/midsreborn/calculations/16-archetype-modifiers.md`
- [x] Batch 1D: Archetype Caps (Spec 17) - `docs/midsreborn/calculations/17-archetype-caps.md`

### Phase 2: Build Aggregation ✅ COMPLETE

- [x] Batch 2A: Defense & Resistance - `docs/midsreborn/calculations/19-build-totals-defense.md`, `20-build-totals-resistance.md`
- [x] Batch 2B: Recharge & Damage - `docs/midsreborn/calculations/21-build-totals-recharge.md`, `22-build-totals-damage.md`
- [x] Batch 2C: Accuracy & Other Stats - `docs/midsreborn/calculations/23-build-totals-accuracy.md`, `24-build-totals-other-stats.md`

### Phase 3: Power Calculations ⏳ IN PROGRESS

- [x] Batch 3A: Damage & Buffs (Specs 02, 03) ✅ COMPLETE
- [ ] Batch 3B: Control & Healing (Specs 04, 05) ⏳ NEXT
- [x] Batch 3C: Endurance & Recharge (Specs 06, 07) ✅ COMPLETE
- [ ] Batch 3D: Accuracy & Defense (Specs 08, 09)

### Phase 4: Advanced Features

- [ ] Batch 4A: Enhancement System (Specs 11, 13)
- [ ] Batch 4B: Stacking & Incarnates (Specs 25, 29)
- [ ] Batch 4C: Pets & Procs (Specs 32, 34)

### Phase 5: API Integration

- [ ] Create FastAPI endpoints
- [ ] Add integration tests
- [ ] Performance optimization
- [ ] API documentation

---

**Plan Status**: Ready to Execute
**Estimated Duration**: 8 weeks (1 developer)
**Estimated LOC**: ~15,000 lines Python + ~5,000 lines tests
**Next Step**: Execute using superpowers:executing-plans skill
