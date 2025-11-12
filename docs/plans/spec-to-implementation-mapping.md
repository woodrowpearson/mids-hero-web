# Specification to Implementation Mapping

**Created**: 2025-11-11
**Purpose**: Map calculation specification documents to implementation batches and files
**Spec Location**: `/Users/w/code/mids-hero-web/docs/midsreborn/calculations/`
**Implementation Location**: `/Users/w/code/mids-hero-web/backend/app/calculations/`

---

## Quick Reference

| Spec # | Spec Document | Implementation Batch | Implementation Files | Status |
|--------|---------------|---------------------|---------------------|---------|
| 01 | `01-power-effects-core.md` | Phase 1, Batch 1A | `core/effect*.py`, `core/grouped_fx.py` | ✅ Complete |
| 10 | `10-enhancement-schedules.md` | Phase 1, Batch 1B | `core/enhancement_schedules.py` | ✅ Complete |
| 16 | `16-archetype-modifiers.md` | Phase 1, Batch 1C | `core/archetype_modifiers.py` | ✅ Complete |
| 17 | `17-archetype-caps.md` | Phase 1, Batch 1D | `core/archetype_caps.py` | ✅ Complete |
| 19 | `19-build-totals-defense.md` | Phase 2, Batch 2A | `build/defense_aggregator.py` | ✅ Complete |
| 20 | `20-build-totals-resistance.md` | Phase 2, Batch 2A | `build/resistance_aggregator.py` | ✅ Complete |
| 21 | `21-build-totals-recharge.md` | Phase 2, Batch 2B | `build/recharge_aggregator.py` | ✅ Complete |
| 22 | `22-build-totals-damage.md` | Phase 2, Batch 2B | `build/damage_aggregator.py` | ✅ Complete |
| 23 | `23-build-totals-accuracy.md` | Phase 2, Batch 2C | `build/accuracy_aggregator.py` | ⏳ Next |
| 24 | `24-build-totals-other-stats.md` | Phase 2, Batch 2C | `build/other_stats_aggregator.py` | ⏳ Next |
| 02 | `02-power-damage.md` | Phase 3, Batch 3A | `powers/damage_calculator.py` | 📋 Planned |
| 03 | `03-power-buffs-debuffs.md` | Phase 3, Batch 3A | `powers/buff_calculator.py` | 📋 Planned |
| 04 | `04-power-control-effects.md` | Phase 3, Batch 3B | `powers/control_calculator.py` | 📋 Planned |
| 05 | `05-power-healing-absorption.md` | Phase 3, Batch 3B | `powers/healing_calculator.py` | 📋 Planned |
| 06 | `06-power-endurance-recovery.md` | Phase 3, Batch 3C | `powers/endurance_calculator.py` | 📋 Planned |
| 07 | `07-power-recharge-modifiers.md` | Phase 3, Batch 3C | `powers/recharge_calculator.py` | 📋 Planned |
| 08 | `08-power-accuracy-tohit.md` | Phase 3, Batch 3D | `powers/accuracy_calculator.py` | 📋 Planned |
| 09 | `09-power-defense-resistance.md` | Phase 3, Batch 3D | `powers/defense_calculator.py` | 📋 Planned |
| 11 | `11-enhancement-slotting.md` | Phase 4, Batch 4A | `enhancements/slotting.py` | 📋 Planned |
| 13 | `13-enhancement-set-bonuses.md` | Phase 4, Batch 4A | `enhancements/set_bonuses.py` | 📋 Planned |
| 25 | `25-buff-stacking-rules.md` | Phase 4, Batch 4B | `build/stacking_rules.py` | 📋 Planned |
| 29 | `29-incarnate-alpha-shifts.md` | Phase 4, Batch 4B | `incarnates/alpha_calculator.py` | 📋 Planned |
| 32 | `32-pet-calculations.md` | Phase 4, Batch 4C | `powers/pet_calculator.py` | 📋 Planned |
| 34 | `34-proc-chance-formulas.md` | Phase 4, Batch 4C | `enhancements/proc_calculator.py` | 📋 Planned |

---

## Phase 1: Core Foundation (COMPLETE ✅)

### Batch 1A: Effect System
**Spec**: `01-power-effects-core.md`

**Implementation Files**:
- `backend/app/calculations/core/effect_types.py` - 85 effect type enums
- `backend/app/calculations/core/effect.py` - IEffect dataclass (115 properties)
- `backend/app/calculations/core/grouped_fx.py` - GroupedFx aggregation
- `backend/app/calculations/core/enums.py` - ToWho, PvMode, etc.

**Tests**: `backend/tests/calculations/core/test_effect.py`

---

### Batch 1B: Enhancement Schedules
**Spec**: `10-enhancement-schedules.md`

**Implementation Files**:
- `backend/app/calculations/core/enhancement_schedules.py` - ED curves (A, B, C, D)
- `backend/app/calculations/core/constants.py` - BASE_MAGIC, ED thresholds

**Tests**: `backend/tests/calculations/core/test_enhancement_schedules.py`

---

### Batch 1C: Archetype Modifiers
**Spec**: `16-archetype-modifiers.md`

**Implementation Files**:
- `backend/app/calculations/core/archetype_modifiers.py` - 102 modifier tables
- `backend/app/calculations/core/modifier_loader.py` - Load from AttribMod.json

**Tests**: `backend/tests/calculations/core/test_archetype_modifiers.py`

---

### Batch 1D: Archetype Caps
**Spec**: `17-archetype-caps.md`

**Implementation Files**:
- `backend/app/calculations/core/archetype_caps.py` - Cap limits per AT
- `backend/app/calculations/core/cap_loader.py` - Load from .mhd files

**Tests**: `backend/tests/calculations/core/test_archetype_caps.py`

---

## Phase 2: Build Aggregation (PARTIAL 🟡)

### Batch 2A: Defense & Resistance (COMPLETE ✅)
**Specs**:
- `19-build-totals-defense.md`
- `20-build-totals-resistance.md`

**Implementation Files**:
- `backend/app/calculations/build/defense_aggregator.py` - "Highest wins" logic
- `backend/app/calculations/build/resistance_aggregator.py` - Additive stacking
- `backend/app/calculations/build/build_totals.py` - Main aggregation class

**Tests**:
- `backend/tests/calculations/build/test_defense_aggregator.py`
- `backend/tests/calculations/build/test_resistance_aggregator.py`

---

### Batch 2B: Recharge & Damage (COMPLETE ✅)
**Specs**:
- `21-build-totals-recharge.md`
- `22-build-totals-damage.md`

**Implementation Files**:
- `backend/app/calculations/build/recharge_aggregator.py` - Global recharge
- `backend/app/calculations/build/damage_aggregator.py` - Damage buff heuristic

**Tests**:
- `backend/tests/calculations/build/test_recharge_aggregator.py`
- `backend/tests/calculations/build/test_damage_aggregator.py`

---

### Batch 2C: Accuracy & Other Stats (NEXT ⏳)
**Specs**:
- `23-build-totals-accuracy.md`
- `24-build-totals-other-stats.md`

**Implementation Files TO CREATE**:
- `backend/app/calculations/build/accuracy_aggregator.py` - Global accuracy/tohit
- `backend/app/calculations/build/other_stats_aggregator.py` - 30+ stats

**Tests TO CREATE**:
- `backend/tests/calculations/build/test_accuracy_aggregator.py`
- `backend/tests/calculations/build/test_other_stats_aggregator.py`

**Key Test Cases** (from specs):
- Accuracy Test 1: Kismet IO → +6% accuracy (NOT tohit!)
- Other Stats Test 1: HP calculation with accolades

---

## Phase 3: Power Calculations (PLANNED 📋)

### Batch 3A: Damage & Buffs
**Specs**:
- `02-power-damage.md`
- `03-power-buffs-debuffs.md`

**Files TO CREATE**:
- `backend/app/calculations/powers/damage_calculator.py` - DPA/DPS modes
- `backend/app/calculations/powers/buff_calculator.py` - Multiplicative stacking

---

### Batch 3B: Control & Healing
**Specs**:
- `04-power-control-effects.md`
- `05-power-healing-absorption.md`

**Files TO CREATE**:
- `backend/app/calculations/powers/control_calculator.py` - Magnitude > protection
- `backend/app/calculations/powers/healing_calculator.py` - BASE_MAGIC (1.666667)

---

### Batch 3C: Endurance & Recharge
**Specs**:
- `06-power-endurance-recovery.md`
- `07-power-recharge-modifiers.md`

**Files TO CREATE**:
- `backend/app/calculations/powers/endurance_calculator.py` - Toggle cost formula
- `backend/app/calculations/powers/recharge_calculator.py` - Local × global

---

### Batch 3D: Accuracy & Defense
**Specs**:
- `08-power-accuracy-tohit.md`
- `09-power-defense-resistance.md`

**Files TO CREATE**:
- `backend/app/calculations/powers/accuracy_calculator.py` - Final accuracy formula
- `backend/app/calculations/powers/defense_calculator.py` - Effective defense

---

## Phase 4: Advanced Features (PLANNED 📋)

### Batch 4A: Enhancement System
**Specs**:
- `11-enhancement-slotting.md`
- `13-enhancement-set-bonuses.md`

**Files TO CREATE**:
- `backend/app/calculations/enhancements/slotting.py` - Max 6 slots, attuned/catalyzed
- `backend/app/calculations/enhancements/set_bonuses.py` - Rule of 5

---

### Batch 4B: Stacking & Incarnates
**Specs**:
- `25-buff-stacking-rules.md`
- `29-incarnate-alpha-shifts.md`

**Files TO CREATE**:
- `backend/app/calculations/build/stacking_rules.py` - 6 eStacking modes
- `backend/app/calculations/incarnates/alpha_calculator.py` - T1-T4 tiers, level shifts

---

### Batch 4C: Pets & Procs
**Specs**:
- `32-pet-calculations.md`
- `34-proc-chance-formulas.md`

**Files TO CREATE**:
- `backend/app/calculations/powers/pet_calculator.py` - Selective inheritance
- `backend/app/calculations/enhancements/proc_calculator.py` - PPM formula

---

## Phase 5: API Integration (PLANNED 📋)

**Specs**: Multiple (all above specs inform API design)

**Endpoints TO CREATE**:
- `POST /api/v1/calculations/power/damage`
- `POST /api/v1/calculations/power/buffs`
- `POST /api/v1/calculations/power/control`
- `POST /api/v1/calculations/power/healing`
- `POST /api/v1/calculations/power/accuracy`
- `POST /api/v1/calculations/build/totals`
- `POST /api/v1/calculations/build/defense`
- `POST /api/v1/calculations/build/resistance`
- `GET /api/v1/calculations/constants`
- `POST /api/v1/calculations/enhancements/slotting`
- `POST /api/v1/calculations/enhancements/set-bonuses`
- `POST /api/v1/calculations/enhancements/procs`

---

## Additional Specs (Not in Milestone 4)

These specs are documented but not part of the current milestone:

| Spec # | Spec Document | Priority | Notes |
|--------|---------------|----------|-------|
| 12 | `12-enhancement-io-procs.md` | Medium | Covered by Spec 34 |
| 14 | `14-enhancement-special-ios.md` | Low | Special case handling |
| 15 | `15-enhancement-frankenslotting.md` | Low | Advanced optimization |
| 18 | `18-archetype-inherents.md` | Medium | AT-specific mechanics |
| 26 | `26-diminishing-returns.md` | Medium | Covered by Spec 10 |
| 27 | `27-suppression-mechanics.md` | Low | PvP-specific |
| 28 | `28-combat-attributes.md` | Medium | UI display logic |
| 30 | `30-incarnate-abilities.md` | Medium | Future milestone |
| 31 | `31-incarnate-core-radial.md` | Medium | Future milestone |
| 33 | `33-pseudopet-mechanics.md` | Low | Special case handling |
| 35 | `35-proc-interactions.md` | Low | Edge cases |
| 36 | `36-enhancement-boosters.md` | Low | Covered by Spec 11 |
| 37 | `37-attuned-ios.md` | Low | Covered by Spec 11 |
| 38 | `38-purple-pvp-ios.md` | Low | Special case handling |
| 39 | `39-power-customization.md` | Low | UI concern |
| 40 | `40-powerset-relationships.md` | Medium | Cross-powerset logic |
| 41 | `41-level-scaling.md` | Medium | Covered by other specs |
| 42 | `42-exemplar-mechanics.md` | Low | Special case handling |
| 43 | `43-special-cases.md` | Low | Edge cases |

---

## How to Use This Document

### For Implementation:
1. Check current batch to determine which specs are needed
2. Read spec document(s) from `docs/midsreborn/calculations/`
3. Implement files according to mapping
4. Write tests using exact values from spec Section 4
5. Verify formulas match spec Section 5

### For Testing:
Each spec document contains:
- **Section 4**: Test cases with exact expected values
- **Section 5**: Formulas and algorithms
- **Section 6**: Edge cases and special conditions

### For Code Review:
1. Check implementation matches spec formulas exactly
2. Verify all test cases from spec are implemented
3. Confirm file locations match this mapping
4. Ensure constants match C# source exactly

---

## Status Legend

- ✅ Complete - Implementation done and tested
- ⏳ Next - Currently in progress or next up
- 🟡 Partial - Some work done, not complete
- 📋 Planned - Not yet started
- ❌ Blocked - Cannot proceed (dependency missing)

---

**Last Updated**: 2025-11-11
**Maintained By**: Calculation Engine Team
