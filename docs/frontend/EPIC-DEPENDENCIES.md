# Mids Hero Web - Frontend Epic Dependencies & Status

**Created**: 2025-11-18
**Purpose**: Track epic completion status and dependencies
**Last Updated**: 2025-11-18 (Epic 4.2 complete)

---

## Epic Status Overview

| Epic | Status | Completion | Dependencies Met |
|------|--------|------------|------------------|
| **Epic 1: Foundation & Setup** | ✅ Complete | 100% | N/A (foundation) |
| **Epic 2: Character Creation** | ⏳ Pending | 0% | Epic 1 ✅ |
| **Epic 3: Power Selection & Slotting** | ⏳ Pending | 0% | Epic 2 ❌ |
| **Epic 4: Build Totals & Stats** | 🟡 In Progress | 67% | Epic 1 ✅ |
| **Epic 5: Set Bonuses & Advanced** | ⏳ Pending | 0% | Epic 3 ❌, Epic 4 🟡 |
| **Epic 6: Build Persistence & Sharing** | ⏳ Pending | 0% | Epic 2 ❌, Epic 3 ❌ |
| **Epic 7: Polish & Performance** | ⏳ Pending | 0% | All epics ❌ |

**Overall Progress**: 2.67 / 7 epics (38%)

---

## Epic 1: Foundation & Setup ✅ COMPLETE

**Status**: ✅ All stages complete
**Completion**: 100% (4/4 stages)

### Stages

| Stage | Status | Components Created |
|-------|--------|-------------------|
| **1.1: Next.js + Design System** | ✅ Complete | Next.js 14, shadcn/ui, Tailwind, TypeScript |
| **1.2: State Management** | ✅ Complete | TanStack Query, Zustand, temporal middleware |
| **1.3: Layout Shell + Navigation** | ✅ Complete | BuildLayout, TopPanel, routing |
| **1.4: API Client Integration** | ✅ Complete | API services, hooks, error handling |

### Dependencies

**Depends on**: None (foundation epic)

**Enables**:
- Epic 2 (needs state management, API client)
- Epic 4 (needs TanStack Query, Zustand)

### Key Deliverables

- ✅ Next.js 14 App Router configured
- ✅ shadcn/ui components installed
- ✅ Zustand character store with undo/redo
- ✅ TanStack Query configured
- ✅ API client services created
- ✅ Base layout components

---

## Epic 2: Character Creation ⏳ PENDING

**Status**: ⏳ Not started
**Completion**: 0% (0/3 stages)
**Ready to start**: ✅ Yes (Epic 1 complete)

### Stages

| Stage | Status | Dependencies | Estimated Time |
|-------|--------|--------------|----------------|
| **2.1: Archetype & Origin Selection** | ⏳ Pending | Epic 1.2 (state), Epic 1.4 (API) | 4-5 hours |
| **2.2: Powerset Selection** | ⏳ Pending | Epic 2.1 | 5-6 hours |
| **2.3: Character Sheet Display** | ⏳ Pending | Epic 2.1, Epic 2.2 | 3-4 hours |

**Total Estimated Time**: 12-15 hours (1.5-2 days)

### Dependencies

**Requires**:
- Epic 1.2: State Management ✅
- Epic 1.4: API Client Integration ✅

**Blocks**:
- Epic 3 (can't select powers without character)
- Epic 6 (can't save builds without character)

### Key Deliverables

- Archetype selector component
- Origin selector component
- Alignment selector component
- Primary/Secondary powerset selectors
- Pool power selectors (4 slots)
- Ancillary/Epic selector
- Character sheet display
- AT modifiers and caps display
- Inherent powers display

### MidsReborn Reference

**UI Components**:
- Main window top panel (archetype/origin dropdowns)
- Powerset dropdowns (primary, secondary, pools, epic)

**Data Flow**:
- GET /api/archetypes
- GET /api/powersets (filtered by archetype)
- Zustand: characterStore.setArchetype(), setPowerset()

---

## Epic 3: Power Selection & Slotting ⏳ PENDING

**Status**: ⏳ Not started
**Completion**: 0% (0/4 stages)
**Ready to start**: ❌ No (needs Epic 2)

### Stages

| Stage | Status | Dependencies | Estimated Time |
|-------|--------|--------------|----------------|
| **3.1: Available Powers Panel** | ⏳ Pending | Epic 2.2 (powersets) | 5-6 hours |
| **3.2: Power Picker UI** | ⏳ Pending | Epic 3.1 | 6-7 hours |
| **3.3: Enhancement Browser** | ⏳ Pending | Epic 1.4 (API) | 5-6 hours |
| **3.4: Slot Editor (Enhancement Picker)** | ⏳ Pending | Epic 3.2, Epic 3.3 | 8-10 hours |

**Total Estimated Time**: 24-29 hours (3-4 days)

### Dependencies

**Requires**:
- Epic 2.2: Powerset Selection ❌ (must complete first)
- Epic 1.4: API Client Integration ✅

**Blocks**:
- Epic 4 (stats display needs powers slotted to calculate)
- Epic 5 (set bonuses need enhancements slotted)
- Epic 6 (can't save builds without powers)

### Key Deliverables

**Powers**:
- PowerList component (scrollable, availability logic)
- PowerListItem component
- PowerAvailability logic (level, prerequisites)
- BuildDisplay grid (2-6 columns)
- PowerCard component (with slot indicators)
- Power context menu (remove, add slot)

**Enhancements**:
- EnhancementBrowser component
- EnhancementTypeFilter (Normal, Set, Special)
- EnhancementGradeSelector (TO/DO/SO, IO levels)
- EnhancementSearch
- EnhancementPicker dialog (complex, tabbed)
- EnhancementGrid with icons
- RelativeLevelSelector (+3 to -3)

### MidsReborn Reference

**UI Components**:
- llPrimary, llSecondary (power lists)
- pnlGFXFlow (central build display)
- I9Picker dialog (enhancement picker)

**Complexity**:
- Most complex epic (enhancement picker is intricate)
- Lots of state management (power picks, slots, enhancements)
- Critical path epic (blocks most other epics)

---

## Epic 4: Build Totals & Stats Display 🟡 IN PROGRESS

**Status**: 🟡 In progress (67% complete)
**Completion**: 67% (2/3 stages)
**Ready to start**: ✅ Yes (Epic 1 complete)

### Stages

| Stage | Status | Dependencies | Estimated Time |
|-------|--------|--------------|----------------|
| **4.1: Defense & Resistance Displays** | ✅ Complete | Epic 1.4 (API) | 6-8 hours ✅ |
| **4.2: HP, Endurance, Recharge Displays** | ✅ Complete | Epic 4.1 | 4-5 hours ✅ |
| **4.3: Visual Aids (Improved)** | ⏳ Pending | Epic 4.1, Epic 4.2 | 6-8 hours |

**Total Estimated Time**: 16-21 hours (2-3 days)
**Completed**: 10-13 hours
**Remaining**: 6-8 hours

### Dependencies

**Requires**:
- Epic 1.4: API Client Integration ✅
- POST /api/calculations/totals endpoint ✅

**Optional Enhancement**:
- Epic 3 (to have actual powers for calculations)
- Without Epic 3: Can still display totals with mock/test data

**Blocks**:
- Epic 5 (set bonuses display may reference totals)

### Completed Deliverables (4.1 + 4.2)

✅ **StatBar component** - Reusable horizontal bar
✅ **DefensePanel** - 11 defense values (typed + positional)
✅ **ResistancePanel** - 8 resistance values
✅ **HPPanel** - Max HP, Regen %, Absorb
✅ **EndurancePanel** - Max End, Recovery, Usage
✅ **RechargePanel** - Global Recharge %
✅ **MiscStatsPanel** - Accuracy, ToHit, Damage
✅ **TotalsPanel** - Container with 3-column responsive grid

### Remaining Deliverables (4.3)

**Visual Aids (Improved)**:
- Enhanced stat visualizations
- Comparison tooltips (before/after slotting)
- Mini stat cards for quick view
- Collapsible stat sections
- Stat trend indicators

### Next Stage: Epic 4.3

**Ready to start**: ✅ Yes (Epic 4.1 and 4.2 complete)

**Objectives**:
- Improve stat displays beyond MidsReborn
- Add comparison mode (before/after values)
- Create summary cards
- Add expand/collapse functionality

**Estimated**: 6-8 hours

---

## Epic 5: Set Bonuses & Advanced Features ⏳ PENDING

**Status**: ⏳ Not started
**Completion**: 0% (0/2 stages)
**Ready to start**: ❌ No (needs Epic 3 and Epic 4)

### Stages

| Stage | Status | Dependencies | Estimated Time |
|-------|--------|--------------|----------------|
| **5.1: Active Set Bonuses Display** | ⏳ Pending | Epic 3.4 (slotting), Epic 4.3 (totals) | 6-7 hours |
| **5.2: Set Bonus Browser** | ⏳ Pending | Epic 5.1 | 4-5 hours |

**Total Estimated Time**: 10-12 hours (1.5 days)

### Dependencies

**Requires**:
- Epic 3.4: Slot Editor ❌ (must slot enhancements to get set bonuses)
- Epic 4 (complete): Totals Display 🟡 (set bonuses contribute to totals)

**Blocks**:
- None (enhancement feature)

### Key Deliverables

**Active Set Bonuses**:
- SetBonusPanel component
- ActiveSetBonuses component
- SetBonusAggregation logic
- RuleOfFiveIndicator (suppression warnings)
- Set bonus totals by category

**Set Browser**:
- SetBrowser component
- SetDetail view
- SetFilter component
- Display all available sets
- Show set bonus details

### MidsReborn Reference

**UI Components**:
- frmSetViewer (set viewer window)
- Set bonus lists
- Rule of 5 suppression indicators

**Complexity**:
- Medium complexity
- Depends on slotting logic from Epic 3.4
- Integrates with totals from Epic 4

---

## Epic 6: Build Persistence & Sharing ⏳ PENDING

**Status**: ⏳ Not started
**Completion**: 0% (0/3 stages)
**Ready to start**: ❌ No (needs Epic 2 and Epic 3)

### Stages

| Stage | Status | Dependencies | Estimated Time |
|-------|--------|--------------|----------------|
| **6.1: Save/Load Builds** | ⏳ Pending | Epic 2, Epic 3 | 5-6 hours |
| **6.2: Permalink Generation** | ⏳ Pending | Epic 6.1 | 6-7 hours |
| **6.3: Auto-Save + Undo/Redo** | ⏳ Pending | Epic 6.1 | 4-5 hours |

**Total Estimated Time**: 15-18 hours (2 days)

### Dependencies

**Requires**:
- Epic 2: Character Creation ❌ (must have character to save)
- Epic 3: Power Selection ❌ (must have powers to save)
- Epic 1.2: Zustand temporal middleware ✅ (for undo/redo)

**Blocks**:
- None (sharing feature)

### Key Deliverables

**Save/Load**:
- Save build API integration
- Load build API integration
- Auto-save with debounce (2s)
- LocalStorage fallback
- useAutoSave hook
- useBuildPersistence hook
- SaveDialog, LoadDialog components

**Permalinks**:
- Share build API integration
- Permalink URLs (/build/:id)
- SSR for Open Graph tags
- Twitter Card metadata
- ShareDialog component
- PermalinkDisplay component
- DiscordExport component

**Auto-Save + Undo/Redo**:
- Polished auto-save implementation
- Undo/redo UI indicators
- Keyboard shortcuts (Cmd/Ctrl+Z)
- UndoHistory viewer (optional)
- UndoRedoButtons component

### MidsReborn Reference

**UI Components**:
- ShareMenu
- API submission flow
- Discord markdown format

**Backend**:
- POST /api/builds (create/share)
- GET /api/builds/:id (fetch shared build)

---

## Epic 7: Polish & Performance ⏳ PENDING

**Status**: ⏳ Not started
**Completion**: 0% (0/3 stages)
**Ready to start**: ❌ No (needs all other epics)

### Stages

| Stage | Status | Dependencies | Estimated Time |
|-------|--------|--------------|----------------|
| **7.1: Loading States & Error Boundaries** | ⏳ Pending | All epics | 4-5 hours |
| **7.2: Performance Optimization** | ⏳ Pending | All epics | 6-8 hours |
| **7.3: Accessibility & Keyboard Shortcuts** | ⏳ Pending | All epics | 6-7 hours |

**Total Estimated Time**: 16-20 hours (2-3 days)

### Dependencies

**Requires**:
- Epic 1-6: All complete ❌ (polish applied to finished features)

**Blocks**:
- None (final epic)

### Key Deliverables

**Loading & Errors**:
- Loading components for all async operations
- Error boundary components
- Better error messaging
- Retry logic
- ErrorBoundary, LoadingState, ErrorDisplay components

**Performance**:
- Debounced calculations optimization
- React.memo for expensive components
- useCallback for functions
- useMemo for derived values
- Code splitting (dynamic imports)
- Image optimization
- Lighthouse score >90

**Accessibility**:
- Full keyboard navigation
- ARIA labels throughout
- Focus management
- Screen reader support
- Keyboard shortcut documentation
- KeyboardShortcutsHelp component
- SkipLink component
- WCAG 2.1 AA compliance

### MidsReborn Reference

**Improvements over MidsReborn**:
- MidsReborn lacks keyboard shortcuts documentation
- MidsReborn not screen reader compatible
- Web version should exceed desktop accessibility

---

## Critical Path Analysis

### Main Development Path (Required for MVP)

```
Epic 1: Foundation (COMPLETE) ✅
  ↓
Epic 2: Character Creation (PENDING) ⏳
  ↓
Epic 3: Power Selection & Slotting (PENDING) ⏳
  ↓
Epic 4: Build Totals (67% COMPLETE) 🟡
  ↓
Epic 6: Build Persistence (PENDING) ⏳
  ↓
Epic 7: Polish (PENDING) ⏳
```

**Critical Path Time**: ~67-82 hours (~8-10 days)

### Optional Enhancement Path

```
Epic 3: Power Selection (from critical path)
  ↓
Epic 5: Set Bonuses (ENHANCEMENT) ⏳
  ↓
Epic 7: Polish (from critical path)
```

**Enhancement Time**: +10-12 hours

### Parallel Development Opportunities

**Can work in parallel**:
- Epic 4.3 (Visual Aids) can proceed NOW ✅
- Epic 2 (Character Creation) can proceed NOW ✅
- Epic 4 and Epic 2 are independent (until calculations need real data)

**Cannot parallelize**:
- Epic 3 requires Epic 2 complete
- Epic 5 requires Epic 3 complete
- Epic 6 requires Epic 2 and Epic 3 complete
- Epic 7 requires all epics complete

---

## Recommended Development Order

### Phase 1: Complete Stats Display (Current)

**Now**: Epic 4.3 - Visual Aids (6-8 hours)
- ✅ Epic 4.1 and 4.2 already complete
- Can proceed immediately
- Completes Epic 4 entirely

### Phase 2: Enable Character Creation

**Next**: Epic 2.1 - Archetype & Origin Selection (4-5 hours)
- Dependencies met (Epic 1 complete)
- Enables character state
- Quick win

**Then**: Epic 2.2 - Powerset Selection (5-6 hours)
- Depends on Epic 2.1
- Enables power selection flow

**Then**: Epic 2.3 - Character Sheet Display (3-4 hours)
- Depends on Epic 2.1, 2.2
- Completes Epic 2

**Phase 2 Total**: 12-15 hours (~2 days)

### Phase 3: Power Selection & Slotting (Critical Path)

**Epic 3.1 → 3.2 → 3.3 → 3.4**: 24-29 hours (3-4 days)
- Most complex epic
- Critical for build functionality
- Blocks Epic 5, Epic 6

### Phase 4: Enhancements (Optional but Recommended)

**Epic 5.1 → 5.2**: 10-12 hours (1.5 days)
- Set bonuses display
- Enhances build optimization experience

### Phase 5: Build Sharing

**Epic 6.1 → 6.2 → 6.3**: 15-18 hours (2 days)
- Save/load builds
- Permalinks and sharing
- Auto-save

### Phase 6: Final Polish

**Epic 7.1 → 7.2 → 7.3**: 16-20 hours (2-3 days)
- Error handling
- Performance optimization
- Accessibility

**Total Remaining**: ~77-94 hours (10-12 days)

---

## Dependencies Matrix

| Epic | Depends On | Blocks | Can Start When |
|------|------------|--------|----------------|
| 1 | None | 2, 4 | ✅ Started (complete) |
| 2 | 1 | 3, 6 | ✅ Now (Epic 1 done) |
| 3 | 2 | 5, 6 | ❌ Epic 2 complete |
| 4 | 1 | 5 (soft) | ✅ Now (Epic 1 done) |
| 5 | 3, 4 | None | ❌ Epic 3, 4 complete |
| 6 | 2, 3 | None | ❌ Epic 2, 3 complete |
| 7 | 1-6 (all) | None | ❌ All epics complete |

**Soft dependency**: Epic 5 can technically start before Epic 4 completes, but set bonuses contribute to totals, so better to finish Epic 4 first.

---

## Progress Tracking

### Completed

- ✅ Epic 1.1: Next.js + Design System
- ✅ Epic 1.2: State Management
- ✅ Epic 1.3: Layout Shell + Navigation
- ✅ Epic 1.4: API Client Integration
- ✅ Epic 4.1: Defense & Resistance Displays
- ✅ Epic 4.2: HP, Endurance, Recharge Displays

**Total Complete**: 6/23 stages (26%)

### In Progress

- 🟡 Epic 4.3: Visual Aids (Improved) - Ready to start

### Next Up (Recommended Order)

1. Epic 4.3: Visual Aids (ready now)
2. Epic 2.1: Archetype & Origin Selection (ready now)
3. Epic 2.2: Powerset Selection (needs 2.1)
4. Epic 2.3: Character Sheet Display (needs 2.1, 2.2)
5. Epic 3.1-3.4: Power Selection & Slotting (needs Epic 2)

---

## Milestones

### Milestone 1: Foundation Complete ✅

**Completed**: Epic 1 (all stages)
**Date**: Before Epic 4.1
**Achievement**: Next.js app, state management, API client all working

### Milestone 2: Stats Display Complete 🟡

**Target**: Complete Epic 4 (4.1, 4.2, 4.3)
**Progress**: 67% (2/3 stages)
**Remaining**: Epic 4.3 (6-8 hours)
**Achievement**: All stat panels working (defense, resistance, HP, endurance, recharge, misc)

### Milestone 3: Character Creation Complete ⏳

**Target**: Complete Epic 2 (2.1, 2.2, 2.3)
**Progress**: 0% (0/3 stages)
**Estimated**: 12-15 hours
**Achievement**: Can create character, select archetype, origin, powersets

### Milestone 4: Power Selection Complete ⏳

**Target**: Complete Epic 3 (3.1, 3.2, 3.3, 3.4)
**Progress**: 0% (0/4 stages)
**Estimated**: 24-29 hours
**Achievement**: Can pick powers, slot enhancements, build complete builds

### Milestone 5: MVP Complete ⏳

**Target**: Complete Epics 1-4, 6 (skip Epic 5 set bonuses for MVP)
**Progress**: 38% (Epic 1, partial Epic 4)
**Remaining**: Epic 2, 3, 4.3, 6
**Estimated**: ~67-82 hours total
**Achievement**: Functional build planner with save/share

### Milestone 6: Full Feature Complete ⏳

**Target**: Complete all Epics 1-7
**Progress**: 26% (6/23 stages)
**Remaining**: 17 stages
**Estimated**: ~77-94 hours remaining
**Achievement**: Feature parity with MidsReborn + enhancements

---

## Risk Assessment

### High Risk Items

**Epic 3.4: Slot Editor (Enhancement Picker)**
- Most complex UI component
- Critical path blocker
- Estimated 8-10 hours (could be 12-15 if issues arise)
- **Mitigation**: Break into smaller sub-tasks, test incrementally

**Epic 6.2: Permalink Generation (SSR)**
- Next.js SSR complexity
- Open Graph metadata
- Build serialization/deserialization
- **Mitigation**: Study Next.js SSR best practices, test with small builds first

### Medium Risk Items

**Epic 5.1: Active Set Bonuses**
- Rule of 5 suppression logic
- Set bonus aggregation
- **Mitigation**: Reference MidsReborn code closely, test edge cases

**Epic 7.2: Performance Optimization**
- React.memo, useCallback, useMemo placement
- Code splitting strategy
- **Mitigation**: Profile first, optimize hotspots, measure impact

### Low Risk Items

- Epic 2: Character Creation (straightforward dropdowns)
- Epic 4.3: Visual Aids (enhancement of existing)
- Epic 6.1: Save/Load (standard CRUD)
- Epic 7.1, 7.3: Polish items (incremental improvements)

---

## Summary

**Current Status**: Epic 4 in progress (67% complete)

**Ready to Start Now**:
- ✅ Epic 4.3: Visual Aids (6-8 hours)
- ✅ Epic 2.1: Archetype & Origin Selection (4-5 hours)

**Critical Path**:
1. Complete Epic 4.3
2. Complete Epic 2 (2.1 → 2.2 → 2.3)
3. Complete Epic 3 (3.1 → 3.2 → 3.3 → 3.4) ← Bottleneck
4. Complete Epic 6 (6.1 → 6.2 → 6.3)
5. Complete Epic 7 (7.1 → 7.2 → 7.3)

**Optional Enhancement**:
- Epic 5 (set bonuses) can be inserted after Epic 3

**Total Remaining Time**: ~77-94 hours (10-12 days of focused work)

**Recommendation**: Start Epic 4.3 next to complete Epic 4, then pivot to Epic 2 to unblock Epic 3.

---

**Document Status**: ✅ Complete
**Last Updated**: 2025-11-18 (after Epic 4.2 completion)
**Next Review**: After Epic 4.3 completion
