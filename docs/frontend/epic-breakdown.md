# Mids Hero Web - Frontend Epic Breakdown

**Created**: 2025-11-13
**Status**: Draft
**Version**: 1.0

---

## Overview

This document breaks down the Mids Hero Web frontend development into discrete Epics and Stages, following the `verified-stage-development` pattern.

**Development Approach**:
- Each Epic = Major feature area
- Each Stage = Verifiable deliverable with planning, execution, and approval gates
- Use `/frontend-development epic-X.Y` to orchestrate each stage
- Visual verification against MidsReborn for UX parity

**Estimated Timeline**: 8-12 weeks (assuming 1-2 stages per week)

---

## Epic Structure

```
Epic 1: Foundation & Setup (1-2 weeks)
Epic 2: Character Creation (1 week)
Epic 3: Power Selection & Slotting (2-3 weeks)
Epic 4: Build Totals & Stats Display (1-2 weeks)
Epic 5: Set Bonuses & Advanced Features (1 week)
Epic 6: Build Persistence & Sharing (1-2 weeks)
Epic 7: Polish & Performance (1 week)
```

---

## Epic 1: Foundation & Setup

**Goal**: Establish Next.js project with design system, state management, and API integration

### Epic 1.1: Next.js Migration + Design System Setup

**Objectives**:
- Set up Next.js 14 (App Router) project
- Install and configure shadcn/ui + Tailwind CSS
- Create base layout components
- Set up TypeScript strict mode

**Deliverables**:
- Next.js project initialized
- shadcn/ui components installed (Button, Dialog, Select, etc.)
- Tailwind config with custom theme (hero blue, villain red)
- Base layout: `RootLayout`, `TopNav`, `Footer`
- TypeScript configured (strict mode)

**Components Created**:
- `app/layout.tsx` - Root layout with providers
- `app/page.tsx` - Landing page (placeholder)
- `components/layout/TopNav.tsx`
- `components/layout/Footer.tsx`
- `components/ui/*` - shadcn/ui components

**Tests**:
- Layout components render correctly
- Navigation works
- Tailwind classes apply

**Success Criteria**:
- Dev server runs without errors
- Homepage displays with layout
- All components have TypeScript types
- Tests pass

---

### Epic 1.2: State Management Setup

**Objectives**:
- Install and configure TanStack Query
- Create Zustand character store
- Set up undo/redo with temporal middleware
- Create API client service

**Deliverables**:
- TanStack Query provider configured
- Zustand store: `characterStore.ts`
- Temporal middleware for undo/redo
- API client: `services/api.ts`
- Type definitions: `types/character.types.ts`, `types/api.types.ts`

**Components Created**:
- `app/providers.tsx` - QueryClientProvider wrapper
- `stores/characterStore.ts` - Main character state
- `stores/uiStore.ts` - UI preferences
- `services/api.ts` - Axios wrapper
- `hooks/useCharacter.ts` - Character store hook
- `hooks/useKeyboardShortcuts.ts` - Undo/redo shortcuts

**Tests**:
- CharacterStore actions work correctly
- Undo/redo functions correctly
- API client handles errors
- Keyboard shortcuts trigger undo/redo

**Success Criteria**:
- Store state updates correctly
- Undo/redo works (Cmd/Ctrl+Z)
- API client configured with interceptors
- All hooks have tests

---

### Epic 1.3: Layout Shell + Navigation

**Objectives**:
- Create main build editor layout
- Implement column layout system (2-6 columns configurable)
- Add top control panel structure
- Set up routing (home, builder, build/:id)

**Deliverables**:
- Builder page: `app/builder/page.tsx`
- Build viewer page: `app/build/[id]/page.tsx`
- Main layout component: `BuildLayout.tsx`
- Column configuration: `UIStore` with layout preferences
- Responsive breakpoints

**Components Created**:
- `components/layout/BuildLayout.tsx` - Main grid layout
- `components/layout/TopPanel.tsx` - Character info + controls
- `components/layout/SidePanel.tsx` - Optional side panel
- `components/ui/ColumnLayoutSelector.tsx` - 2/3/4/5/6 column toggle

**Tests**:
- Layout renders at different column counts
- Responsive breakpoints work
- Routing navigates correctly

**Success Criteria**:
- Can toggle between 2-6 columns
- Layout adapts to screen size
- All routes work

---

### Epic 1.4: API Client Integration

**Objectives**:
- Connect to FastAPI backend
- Create API service layers for powers, enhancements, archetypes
- Implement TanStack Query hooks for data fetching
- Add loading and error states

**Deliverables**:
- API services: `powerApi.ts`, `enhancementApi.ts`, `calculationApi.ts`
- Query hooks: `usePowers`, `useArchetypes`, `useEnhancements`
- Error handling components
- Loading state components

**Components Created**:
- `services/powerApi.ts`
- `services/enhancementApi.ts`
- `services/archetypeApi.ts`
- `services/calculationApi.ts`
- `hooks/usePowers.ts`
- `hooks/useArchetypes.ts`
- `hooks/useEnhancements.ts`
- `hooks/useCalculations.ts`
- `components/ui/LoadingSpinner.tsx`
- `components/ui/ErrorMessage.tsx`

**Tests**:
- API services call correct endpoints
- Query hooks cache data correctly
- Error states display properly
- Loading states display

**Success Criteria**:
- Can fetch archetypes from backend
- Can fetch powersets from backend
- Can fetch enhancements from backend
- Error handling works
- Data caches correctly

---

## Epic 2: Character Creation

**Goal**: Implement character creation flow (archetype, origin, powersets)

### Epic 2.1: Archetype & Origin Selection

**Objectives**:
- Create archetype selector component
- Create origin selector component
- Create alignment selector component
- Integrate with character store

**Deliverables**:
- Archetype dropdown with icons
- Origin dropdown with icons
- Alignment dropdown
- Character name input
- Visual feedback for selections

**Components Created**:
- `components/character/ArchetypeSelector.tsx`
- `components/character/OriginSelector.tsx`
- `components/character/AlignmentSelector.tsx`
- `components/character/CharacterNameInput.tsx`

**Tests**:
- Archetype selection updates store
- Origin selection updates store
- Alignment selection updates store
- Name input updates store
- Invalid selections prevented

**Success Criteria**:
- Can select archetype and see it in store
- Can select origin and see it in store
- Can input character name
- Selections persist in store

**MidsReborn Reference**: Main window top panel, archetype/origin dropdowns

---

### Epic 2.2: Powerset Selection

**Objectives**:
- Create primary powerset selector (filtered by archetype)
- Create secondary powerset selector (filtered by archetype)
- Create pool power selectors (4 slots)
- Create ancillary/epic selector
- Implement powerset prerequisites and locking

**Deliverables**:
- Primary powerset dropdown
- Secondary powerset dropdown
- 4 pool power dropdowns
- Ancillary/epic dropdown
- Automatic filtering based on archetype

**Components Created**:
- `components/character/PowersetSelector.tsx` (reusable)
- `components/character/PrimaryPowersetSelector.tsx`
- `components/character/SecondaryPowersetSelector.tsx`
- `components/character/PoolPowerSelector.tsx`
- `components/character/AncillarySelector.tsx`

**Tests**:
- Primary powerset filtered by archetype
- Secondary powerset filtered by archetype
- Pool powers show correct options
- Ancillary unlocks at level 35+
- Incompatible selections cleared on archetype change

**Success Criteria**:
- Archetype change filters available powersets
- Can select primary and secondary
- Can select up to 4 pool powers
- Can select ancillary at level 35+
- All selections update store

**MidsReborn Reference**: Main window powerset dropdowns, pool power selectors

---

### Epic 2.3: Character Sheet Display

**Objectives**:
- Create summary display of character info
- Show archetype modifiers and caps
- Display inherent powers
- Implement edit mode vs. view mode

**Deliverables**:
- Character sheet component
- Inherent powers display
- AT modifier display
- Caps display (defense, resistance, damage, etc.)

**Components Created**:
- `components/character/CharacterSheet.tsx`
- `components/character/InherentPowersDisplay.tsx`
- `components/character/ATModifiersDisplay.tsx`
- `components/character/CapsDisplay.tsx`

**Tests**:
- Character sheet displays all info
- Inherent powers shown for archetype
- AT modifiers correct for archetype
- Caps correct for archetype

**Success Criteria**:
- Character info displayed clearly
- Inherent powers visible
- AT info accurate

**MidsReborn Reference**: Top panel character info, inherent powers list

---

## Epic 3: Power Selection & Slotting

**Goal**: Implement power picking, slotting, and enhancement selection

### Epic 3.1: Available Powers Panel

**Objectives**:
- Create power list component (vertical scrollable)
- Display powers from selected powersets
- Show power availability (level, prerequisites)
- Visual indicators (available, locked, taken)
- Implement power picking interaction

**Deliverables**:
- Power list component (scrollable)
- Power availability logic
- Power picking flow
- Level-based unlock logic

**Components Created**:
- `components/powers/PowerList.tsx`
- `components/powers/PowerListItem.tsx`
- `components/powers/PowerAvailability.tsx`

**Tests**:
- Power list displays powers from powerset
- Powers locked until correct level
- Prerequisites prevent power selection
- Clicking power adds to build

**Success Criteria**:
- Can see all powers in powerset
- Can click available power to add
- Locked powers cannot be selected
- Powers added to build at correct level

**MidsReborn Reference**: Primary/Secondary power lists (llPrimary, llSecondary)

---

### Epic 3.2: Power Picker UI

**Objectives**:
- Create main build display (central panel)
- Display selected powers in grid layout
- Show power level taken
- Show power slots (visual indicators)
- Implement power removal/respec

**Deliverables**:
- Build display grid (2-6 columns)
- Power card component
- Slot display (empty vs filled)
- Power context menu (remove, add slot)

**Components Created**:
- `components/powers/BuildDisplay.tsx`
- `components/powers/PowerCard.tsx`
- `components/powers/SlotIndicator.tsx`
- `components/powers/PowerContextMenu.tsx`

**Tests**:
- Powers display in grid
- Can add slots to power
- Can remove power from build
- Slots display correctly

**Success Criteria**:
- Selected powers appear in grid
- Can add up to 6 slots per power
- Can remove powers
- Visual matches MidsReborn layout

**MidsReborn Reference**: Central display (pnlGFXFlow), power cards with slots

---

### Epic 3.3: Enhancement Browser

**Objectives**:
- Create enhancement browsing UI
- Filter enhancements by type (TO/DO/SO, IO)
- Display enhancement sets
- Show enhancement details
- Implement search/filter

**Deliverables**:
- Enhancement browser component
- Type filters (Normal, Set, Special)
- Grade selector (TO/DO/SO, IO levels 10-50)
- Search functionality
- Enhancement detail view

**Components Created**:
- `components/enhancements/EnhancementBrowser.tsx`
- `components/enhancements/EnhancementTypeFilter.tsx`
- `components/enhancements/EnhancementGradeSelector.tsx`
- `components/enhancements/EnhancementSearch.tsx`
- `components/enhancements/EnhancementDetail.tsx`

**Tests**:
- Filter by type works
- Filter by grade works
- Search finds enhancements
- Enhancement details display

**Success Criteria**:
- Can browse all enhancements
- Can filter by type and grade
- Can search by name
- Details show for selected enhancement

**MidsReborn Reference**: I9Picker tabs, type/grade selectors

---

### Epic 3.4: Slot Editor (Enhancement Picker)

**Objectives**:
- Create enhancement picker popup (complex)
- Tabbed interface (Normal, Set, Special)
- Grid-based enhancement display
- Relative level selector (+3 to -3)
- Slot enhancement on selection
- Show active set bonuses

**Deliverables**:
- Enhancement picker dialog (custom)
- Tab system (Normal/Set/Special)
- Enhancement grid with icons
- Relative level selector
- Slotting logic with validation

**Components Created**:
- `components/enhancements/EnhancementPicker.tsx` (main dialog)
- `components/enhancements/EnhancementTabs.tsx`
- `components/enhancements/EnhancementGrid.tsx`
- `components/enhancements/RelativeLevelSelector.tsx`
- `components/enhancements/EnhancementIcon.tsx`

**Tests**:
- Picker opens on slot click
- Tabs switch correctly
- Enhancement selection slots enhancement
- Relative level applies
- Set bonuses update

**Success Criteria**:
- Picker opens and displays enhancements
- Can select enhancement and slot it
- Set bonuses activate correctly
- Visual matches MidsReborn I9Picker

**MidsReborn Reference**: I9Picker dialog, tabs, grid, selectors

---

## Epic 4: Build Totals & Stats Display

**Goal**: Display calculated build statistics with visual aids

### Epic 4.1: Defense & Resistance Displays

**Objectives**:
- Create defense stat panel
- Create resistance stat panel
- Multi-bar graph component
- Show typed and positional defense
- Color-code caps (soft-cap, hard-cap)

**Deliverables**:
- Defense panel with bars
- Resistance panel with bars
- Multi-bar graph component
- Cap indicators (yellow, red)

**Components Created**:
- `components/stats/DefensePanel.tsx`
- `components/stats/ResistancePanel.tsx`
- `components/stats/StatBar.tsx`
- `components/stats/MultiBarGraph.tsx`

**Tests**:
- Defense values display correctly
- Resistance values display correctly
- Bars render at correct widths
- Cap indicators show at correct thresholds

**Success Criteria**:
- Defense stats display (typed + positional)
- Resistance stats display
- Bars color-coded correctly
- Values update on build change

**MidsReborn Reference**: frmTotals defense and resistance graphs

---

### Epic 4.2: HP, Endurance, Recharge Displays

**Objectives**:
- Create HP & regen display
- Create endurance & recovery display
- Create recharge (haste) display
- Create accuracy, tohit, damage displays

**Deliverables**:
- HP panel (max HP, regen %, absorb)
- Endurance panel (max end, recovery/s, usage/s)
- Recharge panel (global recharge %)
- Misc panel (accuracy, tohit, damage)

**Components Created**:
- `components/stats/HPPanel.tsx`
- `components/stats/EndurancePanel.tsx`
- `components/stats/RechargePanel.tsx`
- `components/stats/MiscStatsPanel.tsx`

**Tests**:
- HP stats display correctly
- Endurance stats display correctly
- Recharge calculates correctly
- Misc stats display

**Success Criteria**:
- All stats calculate correctly via backend
- Panels display values clearly
- Updates happen automatically

**MidsReborn Reference**: frmTotals HP/Regen/Endurance/Recharge sections

---

### Epic 4.3: Visual Aids (Improved)

**Objectives**:
- Create visual stat indicators (better than MidsReborn)
- Add stat comparison tooltips
- Create mini stat cards
- Implement collapsible stat sections

**Deliverables**:
- Enhanced stat visualizations
- Comparison tooltips (before/after slotting)
- Mini stat cards for quick view
- Collapsible sections

**Components Created**:
- `components/stats/StatCard.tsx`
- `components/stats/StatComparisonTooltip.tsx`
- `components/stats/CollapsibleStatSection.tsx`
- `components/stats/StatSummaryCards.tsx`

**Tests**:
- Visualizations render correctly
- Tooltips show comparisons
- Sections collapse/expand

**Success Criteria**:
- Stats easier to read than MidsReborn
- Visual improvements clear
- User testing positive

---

## Epic 5: Set Bonuses & Advanced Features

**Goal**: Display enhancement set bonuses and additional features

### Epic 5.1: Active Set Bonuses Display

**Objectives**:
- Create set bonus tracker
- Show active bonuses from slotted sets
- Highlight Rule of 5 suppression
- Display bonus totals by category

**Deliverables**:
- Set bonus panel
- Active bonuses list
- Rule of 5 warnings
- Bonus aggregation

**Components Created**:
- `components/enhancements/SetBonusPanel.tsx`
- `components/enhancements/ActiveSetBonuses.tsx`
- `components/enhancements/SetBonusAggregation.tsx`
- `components/enhancements/RuleOfFiveIndicator.tsx`

**Tests**:
- Active bonuses display correctly
- Rule of 5 suppression works
- Totals calculate correctly

**Success Criteria**:
- Set bonuses tracked accurately
- Rule of 5 enforced
- Visual display clear

**MidsReborn Reference**: frmSetViewer, set bonus lists

---

### Epic 5.2: Set Bonus Browser

**Objectives**:
- Create enhancement set viewer
- Display all available sets
- Show set bonus details
- Filter sets by type

**Deliverables**:
- Set browser component
- Set detail view
- Set filtering

**Components Created**:
- `components/enhancements/SetBrowser.tsx`
- `components/enhancements/SetDetail.tsx`
- `components/enhancements/SetFilter.tsx`

**Tests**:
- Set browser displays all sets
- Filtering works
- Details accurate

**Success Criteria**:
- Can browse all sets
- Details show bonuses
- Filtering helpful

---

## Epic 6: Build Persistence & Sharing

**Goal**: Save, load, and share builds

### Epic 6.1: Save/Load Builds

**Objectives**:
- Implement build save to backend
- Implement build load from backend
- Auto-save functionality
- Local storage fallback

**Deliverables**:
- Save build API integration
- Load build API integration
- Auto-save with debounce (2s)
- LocalStorage for draft builds

**Components Created**:
- `hooks/useAutoSave.ts`
- `hooks/useBuildPersistence.ts`
- `components/build/SaveDialog.tsx`
- `components/build/LoadDialog.tsx`

**Tests**:
- Save builds correctly
- Load builds correctly
- Auto-save triggers on change
- LocalStorage works

**Success Criteria**:
- Builds persist to backend
- Auto-save works seamlessly
- Load restores build state

---

### Epic 6.2: Permalink Generation

**Objectives**:
- Implement build sharing API
- Generate permalink URLs
- Generate Discord markdown
- Server-side rendering for rich previews

**Deliverables**:
- Share build API integration
- Permalink URLs (/build/:id)
- SSR for Open Graph tags
- Twitter Card metadata

**Components Created**:
- `app/build/[id]/page.tsx` (SSR)
- `components/sharing/ShareDialog.tsx`
- `components/sharing/PermalinkDisplay.tsx`
- `components/sharing/DiscordExport.tsx`

**Tests**:
- Share generates permalink
- SSR renders build page
- OG tags correct
- Discord markdown correct

**Success Criteria**:
- Share creates permalink
- Rich preview cards work on Discord/Twitter
- Build loads from URL

**MidsReborn Reference**: ShareMenu, API submission, Discord format

---

### Epic 6.3: Auto-Save + Undo/Redo

**Objectives**:
- Refine auto-save implementation
- Polish undo/redo UX
- Add undo history visualization
- Implement keyboard shortcuts

**Deliverables**:
- Polished auto-save
- Undo/redo UI indicators
- Keyboard shortcuts (Cmd/Ctrl+Z)
- Undo history viewer (optional)

**Components Created**:
- `components/ui/UndoRedoButtons.tsx`
- `components/ui/UndoHistory.tsx` (optional)
- `hooks/useUndoRedo.ts`

**Tests**:
- Undo works correctly
- Redo works correctly
- Keyboard shortcuts work
- History accurate

**Success Criteria**:
- Undo/redo seamless
- No data loss
- User-friendly

---

## Epic 7: Polish & Performance

**Goal**: Final polish, optimization, and quality assurance

### Epic 7.1: Loading States & Error Boundaries

**Objectives**:
- Add loading states for all async operations
- Error boundaries for component failures
- Better error messaging
- Retry logic

**Deliverables**:
- Loading components
- Error boundary components
- Error messages
- Retry buttons

**Components Created**:
- `components/ui/ErrorBoundary.tsx`
- `components/ui/LoadingState.tsx`
- `components/ui/ErrorDisplay.tsx`

**Tests**:
- Error boundaries catch errors
- Loading states display
- Retry works

**Success Criteria**:
- No uncaught errors
- Loading states smooth
- Errors user-friendly

---

### Epic 7.2: Performance Optimization

**Objectives**:
- Optimize calculation debouncing
- Optimize rendering (React.memo)
- Code splitting
- Image optimization

**Deliverables**:
- Debounced calculations
- Memoized components
- Dynamic imports
- Optimized images

**Optimizations**:
- React.memo for expensive components
- useCallback for functions
- useMemo for derived values
- Dynamic imports for large components

**Tests**:
- Performance benchmarks
- Lighthouse scores
- No unnecessary re-renders

**Success Criteria**:
- Fast calculation updates
- Smooth UI interactions
- Lighthouse score >90

---

## Epic 7.3: Accessibility & Keyboard Shortcuts

**Objectives**:
- Full keyboard navigation
- ARIA labels
- Focus management
- Screen reader support
- Keyboard shortcut documentation

**Deliverables**:
- Keyboard navigation complete
- ARIA attributes added
- Focus traps in modals
- Shortcut reference

**Components Created**:
- `components/ui/KeyboardShortcutsHelp.tsx`
- `components/ui/SkipLink.tsx`

**Tests**:
- Keyboard navigation works
- Screen reader announces correctly
- Focus management correct

**Success Criteria**:
- WCAG 2.1 AA compliant
- Full keyboard access
- Screen reader compatible

---

## Summary

**Total Epics**: 7
**Total Stages**: ~23 stages
**Estimated Timeline**: 8-12 weeks

**Key Deliverables by Epic**:
1. **Epic 1**: Next.js project, state management, API integration
2. **Epic 2**: Character creation flow
3. **Epic 3**: Power selection and enhancement slotting
4. **Epic 4**: Build stats display
5. **Epic 5**: Set bonuses
6. **Epic 6**: Build sharing and permalinks
7. **Epic 7**: Polish and optimization

**Development Process**:
- Each stage uses `/frontend-development epic-X.Y`
- MidsReborn analysis → Planning → Execution → Visual verification → Approval
- All components tested
- Visual parity with MidsReborn (functional, not pixel-perfect)
- Modern web aesthetic

**Next Steps**:
1. Review this breakdown
2. Approve approach
3. Start Epic 1.1 (Next.js setup)

---

**Document Status**: ✅ Complete
**Last Updated**: 2025-11-13
**Ready for**: Epic 1.1 kickoff
