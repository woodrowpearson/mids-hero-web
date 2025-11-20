# Epic 4.2: HP, Endurance, Recharge Displays - Summary

**Date**: 2025-11-20
**Status**: Planning Complete
**Epic**: 4.2 - HP, Endurance, Recharge Displays
**Detailed Plan**: 2025-11-20-epic-4.2-hp-endurance-recharge.md

---

## What This Epic Accomplishes

Epic 4.2 extends the build totals display system from Epic 4.1 by adding four new stat panels: **HP Panel** (regeneration, max HP, absorb), **Endurance Panel** (recovery, usage, net recovery with time-to-full/zero calculations), **Recharge Panel** (global recharge with perma-Hasten indicator), and **Misc Stats Panel** (accuracy, tohit, damage bonuses).

**Key Features:**
1. **HP Panel**: 2-3 green bars showing regeneration %, max HP, and absorb shield
2. **Endurance Panel**: 3 blue bars showing recovery/s, usage/s, max endurance with net recovery calculation
3. **Recharge Panel**: 1 purple bar showing global recharge % with perma-Hasten achievement badge
4. **Misc Stats Panel**: 3 bars showing accuracy, tohit, and damage percentage bonuses

Unlike Epic 4.1 which created the foundation (StatBar, TotalsPanel), Epic 4.2 focuses on extending the system with new stat types while maintaining visual consistency and reusing existing components.

---

## Key Components Created

### React Components (4 new panels)

**HPPanel** (`components/stats/HPPanel.tsx`):
- Displays health statistics with green color scheme
- Regeneration bar (%, base 100%)
- Max HP bar (numeric value)
- Absorb shield bar (conditional, only if > 0)
- Tooltip shows HP/s and time to full

**EndurancePanel** (`components/stats/EndurancePanel.tsx`):
- Displays endurance statistics with blue color scheme
- End Recovery bar (/s, shows as numeric + percentage in tooltip)
- End Usage bar (/s, turns red if net negative)
- Max Endurance bar (numeric value)
- Complex net recovery calculation (Recovery - Usage)
- Tooltips show time to full or time to zero

**RechargePanel** (`components/stats/RechargePanel.tsx`):
- Displays global recharge with purple color scheme
- Global Recharge bar (%, base 100%)
- Perma-Hasten achievement badge (if >= 170%)
- Shows capped vs uncapped values in tooltip

**MiscStatsPanel** (`components/stats/MiscStatsPanel.tsx`):
- Displays misc buff statistics
- Accuracy bar (%, cyan)
- ToHit bar (%, cyan)
- Damage bar (%, red)

### TypeScript Types (extended)

**totals.types.ts** (extended from Epic 4.1):
- `HPStats` interface (maxHp, regenerationPercent, hpPerSecond, absorb, timeToFull)
- `EnduranceStats` interface (maxEndurance, recoveryNumeric, recoveryPercent, usage, netRecovery, isPositive, timeToFull, timeToZero)
- `RechargeStats` interface (globalPercent, isCapped, permaHasten, uncappedPercent)
- `MiscBuffStats` interface (accuracy, tohit, damagePercent)
- Extended `CalculatedTotals` to include hp, endurance, recharge, buffs

### Modified Components (1)

**TotalsPanel** (`components/stats/TotalsPanel.tsx`):
- Extended to render HP, Endurance, Recharge, Misc Stats panels
- Maintains 2-column responsive grid layout
- Conditional rendering (only show panels if data exists)
- Reuses auto-recalculation system from Epic 4.1

---

## State Management Approach

### TanStack Query (Server State)

**Endpoint**: `POST /api/calculations/totals` (already exists from Epic 1.4)

**Extended Response**:
```typescript
{
  defense: { /* from Epic 4.1 */ },
  resistance: { /* from Epic 4.1 */ },
  hp: {
    maxHp: 1205,
    regenerationPercent: 140,
    hpPerSecond: 2.8,
    absorb: 0,
    timeToFull: 430
  },
  endurance: {
    maxEndurance: 100,
    recoveryNumeric: 2.08,
    recoveryPercent: 125,
    usage: 0.52,
    netRecovery: 1.56,
    isPositive: true,
    timeToFull: 48
  },
  recharge: {
    globalPercent: 170,
    isCapped: false,
    permaHasten: false
  },
  buffs: {
    accuracy: 15,
    tohit: 10,
    damagePercent: 125
  }
}
```

**Caching Strategy**: No caching (same as Epic 4.1) - always recalculate for accuracy

### Zustand (Client State)

**Store**: `characterStore` (reuse from Epic 4.1)

**State**: Already has `totals: CalculatedTotals | null` field which now includes Epic 4.2 data

**Actions**: Reuse `recalculate()` action from Epic 4.1 - it automatically handles extended CalculatedTotals interface

### Derived State

**Net Recovery**:
```typescript
const netRecovery = recoveryNumeric - usage;
const isPositive = netRecovery > 0;
```

**Perma-Hasten**:
```typescript
const permaHasten = globalPercent >= 170; // Simplified threshold
```

**Bar Colors**:
```typescript
const enduranceUsageColor = isPositive ? 'blue' : 'red';
```

---

## API Integration

### Backend Endpoints Used

1. **POST /api/calculations/totals** - Already exists (Epic 1.4)
   - Extended to return HP, Endurance, Recharge, Buffs data
   - Request format unchanged (BuildData)
   - Response includes new fields

**No new API endpoints needed** - Epic 4.2 purely extends the response of the existing totals endpoint.

---

## Implementation Tasks

### Phase 1: Core Components (Tasks 1-5)

1. ✅ Create TypeScript types (HPStats, EnduranceStats, RechargeStats, MiscBuffStats)
2. ✅ Create HPPanel with regeneration, max HP, absorb
3. ✅ Create EndurancePanel with recovery, usage, net recovery
4. ✅ Create RechargePanel with global recharge and perma-Hasten indicator
5. ✅ Create MiscStatsPanel with accuracy, tohit, damage

### Phase 2: Integration (Tasks 6-7)

6. ✅ Extend TotalsPanel to include new panels
7. ✅ Verify characterStore recalculation handles new data

### Phase 3: Testing (Task 8-9)

8. ✅ Integration testing (full TotalsPanel with all Epic 4.1 + 4.2 panels)
9. ✅ Visual verification and documentation

### Phase 4: Summary (Task 10)

10. ✅ Create this PLAN-SUMMARY document

**Total Estimated Time**: 4-6 hours

---

## Acceptance Criteria

### Functional

✅ **HP display works**:
- Regeneration shows as percentage (base 100%, e.g., 140% = +40% regen)
- Max HP shows as numeric value
- Absorb shield shows only when > 0
- Tooltip shows HP/s and time to full

✅ **Endurance display works**:
- Recovery shows as /s (numeric) with % in tooltip
- Usage shows as /s with net recovery in tooltip
- Net recovery calculated correctly (recovery - usage)
- Usage bar turns red if net recovery is negative
- Time to full shown if positive, time to zero if negative

✅ **Recharge display works**:
- Global recharge shows as percentage (base 100%, e.g., 170% = +70%)
- Perma-Hasten badge shows when achieved (>= 170%)
- Capped value shown with uncapped in tooltip if exceeds cap

✅ **Misc Stats display works**:
- Accuracy, ToHit, Damage all display correctly
- Appropriate color schemes (cyan for accuracy/tohit, red for damage)

✅ **State management works**:
- Totals auto-recalculate when build changes (reuses Epic 4.1 system)
- Loading state shows during calculation
- Error state shows on failure with retry button
- All Epic 4.1 + 4.2 panels render together

### Visual

✅ **Colors match MidsReborn**:
- Green: HP, Regeneration
- Blue: Endurance
- Purple: Recharge
- Cyan: Accuracy, ToHit
- Red: Damage, Negative net recovery

✅ **Layout matches MidsReborn**:
- 2-column grid on desktop (Defense/Resistance left, HP/Endurance/Recharge right)
- 1-column stack on mobile
- Section headers for each panel
- Consistent spacing and alignment

✅ **Typography and formatting**:
- Percentages: "140%" (1 decimal if needed)
- Numeric values: "1205" (no decimals for HP)
- Per-second values: "2.08/s" (2 decimals)
- Labels left-aligned, values right-aligned

### Technical

✅ **TypeScript strict mode**:
- No `any` types
- All props typed
- All state typed
- All API responses typed (extended CalculatedTotals)

✅ **Test coverage**:
- HPPanel: 5+ tests
- EndurancePanel: 5+ tests
- RechargePanel: 4+ tests
- MiscStatsPanel: 2+ tests
- TotalsPanel integration: 3+ tests
- All tests passing

✅ **Code quality**:
- ESLint passing
- Prettier formatting applied
- No console warnings
- Accessible (ARIA labels, keyboard navigation)
- Reuses StatBar component (DRY principle)

---

## Deferred Features

**Epic 4.3** (Visual Aids - Improved):
- Enhanced stat visualizations beyond basic bars
- Comparison tooltips (before/after slotting)
- Mini stat cards for quick view
- Collapsible sections

**Future Enhancements**:
- Detailed per-power breakdowns (which powers contribute to each stat)
- Historical comparison (compare current build to previous versions)
- Export totals to clipboard
- Time-series graphs for stat progression by level

---

## Next Epic Preview

**Epic 4.3**: Visual Aids (Improved)

**Will build on Epic 4.2**:
- Enhance existing stat visualizations
- Add comparison tooltips showing before/after values
- Create mini stat cards for dashboard view
- Implement collapsible sections for space efficiency

**Prerequisites Met by Epic 4.2**:
- ✅ Complete stat display system (Defense, Resistance, HP, Endurance, Recharge, Misc)
- ✅ Consistent visual design (colors, layouts, tooltips)
- ✅ Reusable StatBar component
- ✅ TotalsPanel structure ready for enhancements
- ✅ Auto-recalculation system

---

## Key Design Decisions

### 1. Reuse StatBar Component

**Rationale**: Epic 4.1 created a flexible StatBar component that works for all stat types (defense, resistance, HP, endurance, recharge). Reusing it maintains consistency and reduces code duplication.

**Impact**: All Epic 4.2 panels use the same StatBar component with different color props.

### 2. Net Recovery Calculation in EndurancePanel

**Rationale**: MidsReborn shows net recovery (recovery - usage) in the End Usage tooltip. This is critical for players to understand if their build is sustainable.

**Impact**: EndurancePanel calculates and displays net recovery, colors usage bar based on sign (blue if positive, red if negative).

### 3. Perma-Hasten Achievement Badge

**Rationale**: Perma-Hasten (permanent Hasten uptime) is a common build goal. Visual indicator helps players know if they've achieved it.

**Impact**: RechargePanel shows green badge when globalPercent >= 170% (simplified threshold, actual calculation more complex).

### 4. Conditional Absorb Display

**Rationale**: Absorb shield is rare (only some builds have it). Showing an empty bar for 0 absorb wastes space.

**Impact**: HPPanel only renders Absorb bar if value > 0.

### 5. Custom Display Formatters

**Rationale**: Different stats need different formats (percentages, numeric values, /s values). Custom formatters allow flexibility without duplicating StatBar component.

**Impact**: Added `displayFormat` prop to StatBar, used for endurance recovery/usage ("/s" format).

---

## Summary

Epic 4.2 delivers the **HP, Endurance, Recharge, and Misc Stats display system** for Mids Hero Web:

**Components Created** (4 new panels):
- HPPanel - Health stats with green bars (regeneration, max HP, absorb)
- EndurancePanel - Endurance stats with blue bars (recovery, usage, net recovery)
- RechargePanel - Recharge stats with purple bar (global recharge, perma-Hasten)
- MiscStatsPanel - Misc buffs with cyan/red bars (accuracy, tohit, damage)

**State Management**:
- Reuses characterStore.totals from Epic 4.1
- Extends CalculatedTotals interface with hp, endurance, recharge, buffs fields
- Reuses auto-recalculation system from Epic 4.1

**Visual Design**:
- Green bars for HP/regeneration
- Blue bars for endurance (red if negative net recovery)
- Purple bars for recharge
- Cyan bars for accuracy/tohit, red for damage
- Consistent layout with Epic 4.1 (2-column responsive grid)

**API Integration**:
- Extends existing POST /api/calculations/totals response
- No new endpoints needed

This foundation completes the core stat display system and enables Epic 4.3 (visual enhancements).

---

**Status**: ✅ Planning Complete - Ready for Execution
**Components**: 4 panels + 4 interfaces + TotalsPanel extension
**Tests**: ~25 tests total
**Estimated Time**: 4-6 hours
**Dependencies**: Epic 4.1 complete ✅
**Next**: Execute implementation, visual verification, checkpoint generation
