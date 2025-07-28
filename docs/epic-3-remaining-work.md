# Epic 3: Remaining Calculation Work

## Current Status: 75-80% Complete

### ✅ Already Implemented
- Core calculation engine with proper orchestration
- Enhancement Diversification (all schedules)
- Defense calculations (positional/typed with caps)
- Resistance calculations (with AT-specific caps)
- Damage calculations (with crits and AT caps)
- Endurance/Recharge calculations
- Set bonus system with Rule of Five
- Comprehensive test coverage

### 🚧 Partially Implemented
- **Hit Points**: Base + caps work, missing power buffs
- **Movement**: Base values only, no enhancements
- **Accuracy**: Basic multiplier, missing ToHit buffs

### ❌ Not Implemented (Actual Gaps)

#### 1. Healing Calculations
**Priority**: High
**Files to create**: `backend/app/services/calc/heal.py`
```python
# Needs:
- Base heal amount calculation
- Heal enhancement with ED (Schedule A)
- Heal over time support
- Archetype heal modifiers
```

#### 2. ToHit/Accuracy System
**Priority**: High  
**Files to update**: `backend/app/services/calc/accuracy.py`
```python
# Needs:
- ToHit buff/debuff calculations
- Accuracy vs ToHit separation
- Defense cascade (ToHit floor)
- PvP ToHit modifications
```

#### 3. Buff/Debuff Powers
**Priority**: Medium
**Files to create**: `backend/app/services/calc/buffs.py`
```python
# Needs:
- Non-defense/resistance buffs (damage, recharge, etc)
- Debuff calculations
- Buff/debuff resistance
- Power effect stacking
```

#### 4. Movement Calculations
**Priority**: Medium
**Files to update**: `backend/app/services/calc/movement.py`
```python
# Needs:
- Movement power effects
- Movement enhancement support
- Speed caps (run/fly/jump)
- Slow debuff effects
```

#### 5. Status Effects (Mez)
**Priority**: Low
**Files to create**: `backend/app/services/calc/mez.py`
```python
# Needs:
- Mez protection/resistance
- Duration calculations
- Magnitude stacking
```

## Revised Implementation Plan

### Phase 1: Core Gaps (1 week)
1. Implement healing calculations with TDD
2. Complete ToHit/Accuracy system
3. Update existing tests

### Phase 2: Buff System (3-4 days)
1. Create buff/debuff calculator
2. Integrate with existing power effects
3. Add buff resistance calculations

### Phase 3: Movement & Status (3-4 days)
1. Enhance movement calculations
2. Basic mez protection/resistance
3. Integration testing

### Testing Requirements
- Add test cases for each new calculation type
- Validate against known game values
- Ensure performance <30ms maintained

### GitHub Issues to Create
1. Implement healing calculations (#TBD)
2. Complete ToHit/Accuracy system (#TBD)
3. Add buff/debuff power support (#TBD)
4. Enhance movement calculations (#TBD)
5. Basic mez system implementation (#TBD)

## Notes
The existing calculation infrastructure is solid and well-architected. These additions can be implemented incrementally without major refactoring. The test framework is already in place with good patterns to follow.