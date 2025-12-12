# Epic 4.2: HP, Endurance, Recharge Displays - Summary

**Date**: 2025-11-18
**Status**: Planning Complete
**Epic**: 4.2 - HP, Endurance, Recharge Displays
**Detailed Plan**: 2025-11-18-epic-4.2-hp-endurance-recharge.md

---

## What This Epic Accomplishes

Epic 4.2 implements the **HP, Endurance, Recharge, and Misc stats display system** for Mids Hero Web, continuing the Build Totals & Stats Display series (Epic 4). This epic completes the core stat panels by adding health, endurance, and recharge displays to complement the defense and resistance panels from Epic 4.1.

**Key Features**:
1. **HP Panel**: Max HP, Regeneration % with per-second sub-value, Absorb (conditional)
2. **Endurance Panel**: Max End, Recovery/s, Usage/s
3. **Recharge Panel**: Global Recharge % with perma-Hasten milestone indicator
4. **Misc Stats Panel**: Accuracy, ToHit, Damage bonuses (text list)
5. **Component Reuse**: Extends StatBar from Epic 4.1 with new color themes and formats

This epic **builds directly on Epic 4.1** by reusing the StatBar component, TotalsPanel container, characterStore integration, and auto-recalculation system. No new API endpoints or state management is needed.

---

## Key Components Created

### New Components (4 files)

**HPPanel** (`components/stats/HPPanel.tsx`):
- Displays Max HP (whole number), Regeneration % (with per-second sub-value), and Absorb (conditional)
- Uses green gradient color theme (`from-green-500 to-green-700`)
- Reuses StatBar component from Epic 4.1
- Absorb only shown when > 0 (light cyan gradient)

**EndurancePanel** (`components/stats/EndurancePanel.tsx`):
- Displays Max End, End Rec (recovery/s), End Use (usage/s)
- Uses blue gradient color theme (`from-blue-500 to-blue-700`)
- Usage bar uses red gradient (negative stat)
- Reuses StatBar component with /s suffix formatting

**RechargePanel** (`components/stats/RechargePanel.tsx`):
- Displays Global Recharge % from set bonuses and IOs
- Uses orange gradient color theme (`from-orange-500 to-orange-700`)
- Shows perma-Hasten milestone indicator at +70% threshold
- Format: "+125.0%" (offset percentage with + sign)

**MiscStatsPanel** (`components/stats/MiscStatsPanel.tsx`):
- Displays Accuracy, ToHit, Damage bonuses
- Simple text list (no bars) matching MidsReborn "Misc Effects"
- Format: "+15.0%" for positive values
- 2-column grid layout

### Extended Components (1 file)

**StatBar** (extend `components/stats/StatBar.tsx` from Epic 4.1):
- **New formats**: 'number' (whole numbers), 'decimal' (1-2 decimals), 'percent-offset' (+X%)
- **New props**: `suffix` ("/s"), `showSubValue` (per-second below main), `showMilestone`
- **New color themes**: hp (green), hp-absorb (cyan), endurance (blue), endurance-usage (red), recharge (orange)
- Maintains backward compatibility with Epic 4.1 defense/resistance panels

**TotalsPanel** (extend `components/stats/TotalsPanel.tsx` from Epic 4.1):
- Add 4 new panels to existing layout
- Update grid from 2 columns to 3 columns on desktop
- Responsive: 3 cols (desktop), 2 cols (tablet), 1 col (mobile)
- All 6 panels (Defense, Resistance, HP, Endurance, Recharge, Misc)

---

## State Management Approach

### TanStack Query (Server State)

**Endpoint**: `POST /api/calculations/totals` (already exists from Epic 4.1)

**Status**: ✅ No new endpoints needed

**Response includes** (from Epic 4.1):
```json
{
  "defense": { ... },
  "resistance": { ... },
  "hp": {
    "max": 1205,
    "regen_percent": 140.0,
    "regen_per_second": 2.8,
    "absorb": 0
  },
  "endurance": {
    "max": 100,
    "recovery_per_second": 2.08,
    "usage_per_second": 0.0
  },
  "recharge": {
    "global_percent": 125.0
  },
  "misc": {
    "accuracy": 15.0,
    "tohit": 10.0,
    "damage": 50.0
  }
}
```

**No new API work** - Backend already returns all required data.

### Zustand (Client State)

**Store**: characterStore (already exists from Epic 4.1)

**State already available**:
- `totals: CalculatedTotals | null` - Includes hp, endurance, recharge, misc
- `isCalculating: boolean` - Loading state flag
- `recalculate(): Promise<void>` - Auto-recalculation action

**No new state needed** - Epic 4.2 just reads from existing characterStore.totals.

### Component State

**All derived** - No local component state needed:
- Bar widths calculated from values (e.g., `regen_percent / regenCap * 100`)
- Color classes selected based on colorTheme prop
- Milestone indicators shown based on value thresholds (e.g., `>= 70%`)

---

## MidsReborn Reference Implementation

From `MIDSREBORN-UI-ANALYSIS-epic-4.2.md`:

**MidsReborn Components Analyzed**:
- `frmTotals.cs` - Original totals window
- `frmTotalsV2.cs` - Modern redesigned totals window
- `CtlMultiGraph.cs` - SkiaSharp bar graph control (for HP/End bars)

**Visual Design Extracted**:
- HP bars: Green gradient (`#00C000` → `#008000`)
- Endurance bars: Blue gradient (`#0000C0` → `#000080`)
- Recharge bar: Orange gradient labeled "Haste"
- Layout: Sections with horizontal bars, labels left, values right
- Formatting: 1 decimal for percentages ("140.0%"), 1-2 decimals for per-second ("2.08/s")

**Screenshots Referenced**:
- `view-total-window.png` - Full totals window showing all sections
- `total-screen-1.png` - Inline compact totals with Misc Effects

**Key Behaviors**:
1. Real-time updates on build changes (handled by Epic 4.1 auto-recalc)
2. Conditional display (Absorb only when > 0)
3. Sub-values shown below main (Regen per-second below Regen %)
4. Per-second formatting ("/s" suffix)
5. Offset percentage formatting ("+X%" for recharge)

---

## API Integration

### Backend Endpoint

**Endpoint**: `POST /api/calculations/totals`

**Status**: ✅ Already exists (implemented in Epic 1.4, used in Epic 4.1)

**Request**: BuildData (powers, slots, enhancements, level, archetype)

**Response**: CalculatedTotals (includes hp, endurance, recharge, misc)

**No new backend work needed** - All fields already returned.

### Frontend Integration

**Hook**: `useCalculations` (already exists from Epic 1.4)

**Usage** (from Epic 4.1):
```typescript
const { mutate: recalculate, isError, error } = useCalculations();

recalculate(buildData, {
  onSuccess: (totals) => {
    characterStore.setState({ totals, isCalculating: false });
  },
});
```

**Auto-recalculation** (from Epic 4.1):
- Triggers on: setArchetype, addPower, removePower, slotEnhancement, removeEnhancement
- Debounced to prevent excessive API calls
- Loading state shown during calculation

**Epic 4.2 just reads** from characterStore.totals.hp/endurance/recharge/misc - no new API calls.

---

## Implementation Tasks Summary

### Phase 1: Extend StatBar (45 min)
- Add format options: number, decimal, percent-offset
- Add props: suffix, showSubValue, showMilestone
- Add color themes: hp, hp-absorb, endurance, endurance-usage, recharge
- Write 10+ tests

### Phase 2: Create HPPanel (30 min)
- Build component with 2-3 StatBars (Max HP, Regen %, Absorb)
- Apply green color theme
- Handle conditional Absorb display
- Write 5+ tests

### Phase 3: Create EndurancePanel (30 min)
- Build component with 3 StatBars (Max End, Recovery, Usage)
- Apply blue color theme
- Add /s suffix formatting
- Write 5+ tests

### Phase 4: Create RechargePanel (20 min)
- Build component with single StatBar (Global Recharge %)
- Apply orange color theme
- Add perma-Hasten milestone indicator (+70%)
- Write 5+ tests

### Phase 5: Create MiscStatsPanel (20 min)
- Build simple text list component (no bars)
- Format stats with + sign for positive values
- 2-column grid layout
- Write 5+ tests

### Phase 6: Extend TotalsPanel (15 min)
- Add 4 new panels to grid
- Update layout to 3 columns on desktop
- Maintain responsive behavior
- Write 4+ tests

### Phase 7: Integration Testing (30 min)
- Test all panels with mock data
- Verify loading/error states
- Test responsive layout
- Verify auto-recalculation

### Phase 8: Visual Verification (30 min)
- Compare with MidsReborn screenshots
- Verify color schemes match
- Capture implementation screenshot
- Document UX improvements

**Total Estimated Time**: 4-5 hours

---

## Component Reuse from Epic 4.1

### Reused Components

✅ **StatBar.tsx** - Core horizontal bar component
- Just extend with new formats and color themes
- No breaking changes to Epic 4.1 usage
- Maintains backward compatibility

✅ **TotalsPanel.tsx** - Container for all stat panels
- Extend grid layout to include new panels
- Loading/error state handling already works
- Auto-recalculation integration already works

✅ **characterStore** - Global state store
- totals.hp, totals.endurance, totals.recharge already exist
- No new state fields needed
- recalculate() action already works

✅ **useCalculations hook** - API integration
- Already calls POST /api/calculations/totals
- Already handles loading/error states
- No modifications needed

### New Components (Epic 4.2 Only)

🆕 **HPPanel.tsx** - HP stats wrapper
🆕 **EndurancePanel.tsx** - Endurance stats wrapper
🆕 **RechargePanel.tsx** - Recharge display
🆕 **MiscStatsPanel.tsx** - Misc stats list

---

## Visual Design

### Color Themes

- **HP bars**: `bg-gradient-to-r from-green-500 to-green-700`
- **Absorb**: `bg-gradient-to-r from-cyan-400 to-cyan-600`
- **Endurance bars**: `bg-gradient-to-r from-blue-500 to-blue-700`
- **End usage**: `bg-gradient-to-r from-red-500 to-red-700`
- **Recharge**: `bg-gradient-to-r from-orange-500 to-orange-700`

### Layout

**Desktop (3-column grid)**:
```
[Defense]      [HP]          [Recharge]
[Resistance]   [Endurance]   [Misc]
```

**Tablet (2-column grid)**:
```
[Defense]      [HP]
[Resistance]   [Endurance]
               [Recharge]
               [Misc]
```

**Mobile (1-column)**:
```
[Defense]
[Resistance]
[HP]
[Endurance]
[Recharge]
[Misc]
```

### Formatting

- **Percentages**: "140.0%" (1 decimal)
- **Decimals**: "2.08" (1-2 decimals)
- **Whole numbers**: "1205" (no decimals)
- **Per-second**: "2.08/s" (with suffix)
- **Offset percentages**: "+125.0%" (with + sign)

---

## Acceptance Criteria

### Functional

✅ **HP display works**:
- Max HP as whole number (1205)
- Regen % with 1 decimal (140.0%)
- Regen per-second as sub-value (2.8/s)
- Absorb conditional (only when > 0)
- Real-time updates on build changes

✅ **Endurance display works**:
- Max End as whole number (100)
- Recovery/s with 1-2 decimals (2.08/s)
- Usage/s with 1-2 decimals (0.0/s)
- Real-time updates on build changes

✅ **Recharge display works**:
- Global Recharge % with 1 decimal (+125.0%)
- Offset formatting (+ sign for positive)
- Perma-Hasten indicator at >= 70%
- Real-time updates on build changes

✅ **Misc stats display works**:
- Accuracy, ToHit, Damage with 1 decimal
- + sign for positive values
- Simple text list (no bars)
- Real-time updates on build changes

✅ **Component reuse works**:
- StatBar handles all bar displays
- TotalsPanel includes all 6 panels
- characterStore.totals provides all data
- useCalculations triggers recalculation

### Visual

✅ **Colors match MidsReborn theme**:
- Green for HP
- Blue for Endurance
- Orange for Recharge
- Appropriate cap indicators

✅ **Layout responsive**:
- 3 columns on desktop (>= 1024px)
- 2 columns on tablet (768-1024px)
- 1 column on mobile (< 768px)

✅ **Typography correct**:
- 1 decimal for percentages
- 1-2 decimals for per-second values
- Whole numbers for Max HP/End
- + sign for positive offset percentages

### Technical

✅ **TypeScript strict mode**:
- No `any` types
- All props typed
- All state typed

✅ **Test coverage**:
- 35+ tests total across all components
- All tests passing

✅ **Code quality**:
- ESLint passing
- Prettier formatting applied
- No console warnings
- Accessible (ARIA labels)

---

## Deferred Features

**Epic 4.3** (Visual Aids - Improved):
- Enhanced stat visualizations beyond MidsReborn
- Comparison tooltips (before/after slotting)
- Mini stat cards for quick view
- Collapsible stat sections

**Future Enhancements**:
- Detailed HP/End contribution breakdowns
- Endurance usage calculator (attack chains)
- Recharge source breakdown (which sets/IOs)
- Stat export to clipboard

---

## Next Epic Preview

**Epic 4.3**: Visual Aids (Improved)

**Will build on Epic 4.2**:
- All stat panels from Epic 4.1 + 4.2 complete
- Enhanced visualizations (better than MidsReborn)
- Comparison tooltips showing before/after values
- Mini stat cards for at-a-glance view
- Collapsible sections for cleaner UI

**Prerequisites Met by Epic 4.2**:
- ✅ All core stat panels (Defense, Resistance, HP, Endurance, Recharge, Misc)
- ✅ StatBar component fully featured
- ✅ TotalsPanel established
- ✅ Auto-recalculation working
- ✅ API integration complete

---

## Key Design Decisions

### 1. Reuse StatBar for All Displays

**Rationale**: HP and Endurance bars are structurally identical to Defense/Resistance bars from Epic 4.1. Just need different colors and formats.

**Impact**: Minimal new code (~45 min to extend StatBar vs. ~2 hours to build new component), consistent UX.

### 2. No New API Endpoints

**Rationale**: Backend already returns hp, endurance, recharge in totals response from Epic 4.1. Frontend just wasn't displaying them.

**Impact**: Zero backend work, faster implementation, no API versioning issues.

### 3. Conditional Absorb Display

**Rationale**: Most builds don't have absorb. Showing "0" clutters UI unnecessarily.

**Impact**: Cleaner UI for 90%+ of builds, matches MidsReborn behavior.

### 4. Perma-Hasten Milestone

**Rationale**: +70% recharge is a common build goal (perma-Hasten). Highlighting helps builders know when they've achieved it.

**Impact**: Better UX than MidsReborn, provides actionable feedback.

### 5. Simple Text List for Misc Stats

**Rationale**: MidsReborn shows Misc Effects as text list. These stats don't have meaningful caps for bar visualization.

**Impact**: Cleaner UI, faster to implement, matches MidsReborn UX.

---

## Summary

Epic 4.2 delivers **HP, Endurance, Recharge, and Misc stats displays** for Mids Hero Web:

**Components Created** (4 new + 2 extended):
- HPPanel - Max HP, Regen %, Absorb (green gradient)
- EndurancePanel - Max End, Recovery, Usage (blue gradient)
- RechargePanel - Global Recharge % (orange gradient)
- MiscStatsPanel - Accuracy, ToHit, Damage (text list)
- StatBar - Extended with formats and color themes
- TotalsPanel - Extended to include new panels

**Component Reuse**:
- StatBar.tsx reused for all bars
- TotalsPanel.tsx extended (not replaced)
- characterStore.totals reused (no new state)
- useCalculations hook reused (no new API)

**State Management**:
- No new Zustand state
- No new TanStack Query hooks
- Reads from existing characterStore.totals

**Visual Design**:
- Green gradients for HP
- Blue gradients for Endurance
- Orange gradient for Recharge
- Responsive 3-column layout

**API Integration**:
- POST /api/calculations/totals (reused from Epic 4.1)
- No new endpoints needed
- Backend already returns all data

This completes the core Build Totals & Stats Display system. Epic 4.3 will add enhanced visualizations on top of this foundation.

---

**Status**: ✅ Planning Complete - Ready for Execution
**Components**: 4 new + 2 extended
**Tests**: ~35 tests total
**Estimated Time**: 4-5 hours
**Dependencies**: Epic 4.1 complete ✅
**Next**: Execute implementation → Visual verification → Checkpoint generation
