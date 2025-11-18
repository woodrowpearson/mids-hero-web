# Technical Debt Remediation - Quick Reference

**Full Plan**: `2025-11-18-technical-debt-remediation.md`
**Status**: Planning Phase
**Total Issues**: 28 TS errors + 11 test failures

---

## Quick Stats by Epic

| Epic | Component | TS Errors | Test Failures | Est. Time |
|------|-----------|-----------|---------------|-----------|
| 1.2 | State Management | 11 | 11 | 90 min |
| 1.3 | Layout Shell | 1 | 4 | 2.5 hours |
| 1.4 | API Client | 4 | 3 | 2 hours |
| 4.1 | Stats Displays | 0 | 4 | 2 hours |
| **Total** | | **28** | **11** | **8-12 hours** |

---

## Critical Path Items

### 1. characterStore Power Handling (Epic 1.2)
**Impact**: HIGH - Affects all power selection functionality

```typescript
// BEFORE (6 errors)
const power = getPowerById(id);
power.id  // ERROR: possibly undefined

// AFTER
const power = getPowerById(id);
if (!power) return;  // Guard clause
power.id  // Safe
```

**Files**: `stores/characterStore.ts` (lines 153,161,163,173,179,188,189)

---

### 2. BuildData Type Mismatch (Epic 1.2)
**Impact**: HIGH - Affects API contract

```typescript
// BEFORE
totals: CalculatedTotals | null  // Store uses null

// AFTER
totals: CalculatedTotals | undefined  // Match BuildData type
```

**Files**: `stores/characterStore.ts:217`, `types/character.types.ts`

---

### 3. useAutoCalculate Arguments (Epic 1.4)
**Impact**: MEDIUM - Calculation auto-trigger broken

```typescript
// BEFORE (1 error)
calculateTotals(buildData, { onSuccess, onError })

// AFTER
calculateTotals({ buildData }, { onSuccess, onError })
```

**Files**: `hooks/useAutoCalculate.ts:74`

---

## Test Failures by Category

### Layout Issues (6 failures)
- BuildLayout: TopPanel not rendering → Need mock store state
- BuildLayout: Sidebar collapse → Width 0 vs not in DOM
- SidePanel: Collapse width → CSS class vs inline style
- SidePanel: aria-hidden → Add to component
- builder/page: Sidebar → Same as BuildLayout

### Stats Display Issues (4 failures)
- DefensePanel: Multiple elements → Use getAllByText or testId
- StatBar: Negative values → Add Math.max(0, value)
- TotalsPanel: Multiple elements → Same as DefensePanel
- TotalsPanel: Missing totals → archetype=null prevents auto-calc

### API Hook Issues (1 failure)
- usePowersets: Query not executing → Fix mock setup

---

## Quick Fix Commands

```bash
# Run type-check only
npm run type-check

# Run specific test file
npm test -- BuildLayout.test.tsx --run

# Run all tests for one Epic
npm test -- components/layout --run
npm test -- components/stats --run
npm test -- stores/characterStore --run

# Run full quality check
just quality
```

---

## Implementation Order

**Phase 1**: TypeScript Errors (3-4 hours)
1. Epic 1.2: characterStore (90 min) ← **START HERE**
2. Epic 1.3: BuildLayout (30 min)
3. Epic 1.4: Hooks (60 min)

**Phase 2**: Component Tests (4-5 hours)
1. Epic 1.3: Layout tests (2 hours)
2. Epic 1.4: Hook tests (1 hour)
3. Epic 4.1: Stats tests (2 hours)

**Phase 3**: Validation (1 hour)
1. Full CI/CD test
2. Documentation

---

## Success Metrics

```bash
# Before
npm run type-check  # 28 errors
npm test -- --run   # 11 failures

# After
npm run type-check  # 0 errors ✅
npm test -- --run   # 0 failures ✅
gh pr checks        # All green ✅
```

---

## Context for Code Review

When the `superpowers:code-reviewer` agent reviews this:

1. **Epic 1.2**: Check commit `58ef19e87` for original characterStore design
2. **Epic 1.3**: Check commit `d30851a7c` for layout implementation
3. **Epic 1.4**: Check commit `0f80bd207` for API client setup
4. **Epic 4.1**: Check PR #350 for stats display implementation

Each section links to original context for understanding design intent.

---

**See Full Plan**: `2025-11-18-technical-debt-remediation.md` for:
- Detailed code examples
- Root cause analysis
- Multiple fix options
- Verification commands
- Rollback procedures
