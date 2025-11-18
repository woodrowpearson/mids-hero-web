# Epic 2.2: Powerset Selection - Summary

**Date**: 2025-11-18
**Status**: Planning Complete
**Epic**: 2.2 - Powerset Selection
**Detailed Plan**: 2025-11-18-epic-2.2-powerset-selection.md

---

## What This Epic Accomplishes

Epic 2.2 implements powerset selection functionality for Mids Hero Web, enabling users to choose their character's power sources: primary powerset, secondary powerset, up to 4 pool power slots, and an ancillary/epic powerset (unlocked at level 35+). This epic creates 6 React components that integrate with the characterStore (from Epic 2.1) to manage powerset selections, automatically filter available options based on archetype compatibility, enforce validation rules (no duplicate pools, level requirements), and handle state updates when selections change.

The implementation closely mirrors MidsReborn's powerset selection UI while adding modern web enhancements like searchable dropdowns, visual icons, and responsive design. All powerset data is fetched from the existing FastAPI backend (`/api/archetypes/{id}/powersets`) and cached via TanStack Query.

---

## Key Components Created

### React Components

1. **PowersetSelector** (`components/character/PowersetSelector.tsx`)
   - Reusable base component for all powerset dropdowns
   - shadcn/ui Select with Command (searchable)
   - Displays powerset icons and names
   - Props: `type`, `powersets`, `selected`, `onChange`, `disabled`, `placeholder`

2. **PrimaryPowersetSelector** (`components/character/PrimaryPowersetSelector.tsx`)
   - Wraps PowersetSelector
   - Filters powersets by `archetype.primaryPowersets[]`
   - Disabled until archetype selected
   - Shows confirmation dialog when changing mid-build

3. **SecondaryPowersetSelector** (`components/character/SecondaryPowersetSelector.tsx`)
   - Wraps PowersetSelector
   - Filters powersets by `archetype.secondaryPowersets[]`
   - Handles linked secondaries (auto-select, disable dropdown)
   - Disabled until archetype selected

4. **PoolPowerSelector** (`components/character/PoolPowerSelector.tsx`)
   - Wraps PowersetSelector
   - Used 4 times (pool slots 1-4)
   - Filters out already-selected pools from other slots
   - Shows pool prerequisites and mutual exclusivity rules
   - Can be cleared (set to null)

5. **AncillarySelector** (`components/character/AncillarySelector.tsx`)
   - Wraps PowersetSelector
   - Disabled when level < 35
   - Hidden for Epic ATs (Peacebringer, Warshade, etc.)
   - Filters by archetype-compatible ancillary/epic powersets

6. **PowersetSelectionPanel** (`components/character/PowersetSelectionPanel.tsx`)
   - Container component composing all selectors
   - Layout: Primary, Secondary, 4 Pools (vertical), Ancillary
   - Coordinates state updates via characterStore
   - Integrates with CharacterCreationPanel from Epic 2.1

### Custom Hooks

- **usePowersets** (`hooks/usePowersets.ts`)
  - TanStack Query hook for fetching powersets by archetype
  - Endpoint: `GET /api/archetypes/{id}/powersets`
  - Caches data forever (static game data)
  - Error handling and loading states

### State Management

- **CharacterStore Updates** (`stores/characterStore.ts`)
  - New state fields:
    - `primaryPowerset: Powerset | null`
    - `secondaryPowerset: Powerset | null`
    - `poolPowersets: (Powerset | null)[]` (array of 4)
    - `ancillaryPowerset: Powerset | null`
    - `level: number` (for ancillary unlock)
  - New actions:
    - `setPrimaryPowerset(powerset)` - Updates primary, clears powers
    - `setSecondaryPowerset(powerset)` - Updates secondary, clears powers
    - `setPoolPowerset(index, powerset)` - Updates pool at index
    - `setAncillaryPowerset(powerset)` - Updates ancillary (if level >= 35)
    - `setLevel(level)` - Updates level (enables ancillary at 35+)
  - Enhanced `setArchetype()` - Resets all powersets when archetype changes
  - Persistence to localStorage (already configured in Epic 1.2)

---

## State Management Approach

### Server State (TanStack Query)

**Query**: `['powersets', archetypeId]`
- **Endpoint**: `GET /api/archetypes/{archetypeId}/powersets`
- **Cache**: Forever (staleTime: Infinity) - static game data
- **Purpose**: Fetch all powersets available to the selected archetype

**Alternative queries** (if needed):
- `GET /api/archetypes/{id}/powersets?powerset_type=primary` - Primary only
- `GET /api/archetypes/{id}/powersets?powerset_type=secondary` - Secondary only
- `GET /api/powersets` - All powersets (pool powers)

### Client State (Zustand characterStore)

**State Shape** (additions to Epic 2.1):
```typescript
{
  // Existing from Epic 2.1
  archetype: Archetype | null;

  // New for Epic 2.2
  primaryPowerset: Powerset | null;
  secondaryPowerset: Powerset | null;
  poolPowersets: (Powerset | null)[]; // Array of 4, initially [null, null, null, null]
  ancillaryPowerset: Powerset | null;
  level: number; // Default: 1
}
```

**Actions**:
- `setPrimaryPowerset(powerset: Powerset | null)` - Update primary
- `setSecondaryPowerset(powerset: Powerset | null)` - Update secondary
- `setPoolPowerset(index: number, powerset: Powerset | null)` - Update pool at index (0-3)
- `setAncillaryPowerset(powerset: Powerset | null)` - Update ancillary
- `setLevel(level: number)` - Update level
- Enhanced `setArchetype(archetype: Archetype)` - Reset all powersets

**Persistence**: All state automatically saved to localStorage via Zustand persist middleware (Epic 1.2).

### Derived State

- **Available Primary Powersets**: Filter from query by `type === 'Primary'`
- **Available Secondary Powersets**: Filter from query by `type === 'Secondary'`
- **Available Pool Powers**: All pool powersets minus already-selected in other slots
- **Ancillary Enabled**: `level >= 35 && !isEpicAT`

---

## API Endpoints Used

### 1. GET /api/archetypes/{archetypeId}/powersets
- **Status**: ✅ Already implemented in backend
- **Purpose**: Fetch all powersets available to the archetype
- **Response**: `Powerset[]` with `{ id, name, displayName, description, type, icon, levelAvailable, ... }`
- **Caching**: Forever (static game data)

### 2. GET /api/powersets (all pool powers)
- **Status**: ✅ Already implemented in backend
- **Purpose**: Fetch all pool powersets (universal to all ATs)
- **Response**: `Powerset[]` with `type === 'Pool'`
- **Caching**: Forever

### 3. Powerset Types
Backend should return powersets with `type` field:
- `'Primary'` - Primary powersets
- `'Secondary'` - Secondary powersets
- `'Pool'` - Pool powers (4 slots)
- `'Ancillary'` - Ancillary powersets (level 35+)
- `'Epic'` - Epic powersets (level 35+, alternative to Ancillary)

---

## MidsReborn Reference Implementation

From MIDSREBORN-UI-ANALYSIS-epic-2.2.md:

**Powerset Selection UI** (frmMain.cs):
- 6 ComboBox controls: `cbPrimary`, `cbSecondary`, `cbPool0-3`, `cbAncillary`
- Primary/Secondary: Filtered by archetype using `DatabaseAPI.GetPowersetIndexes(archetype.ClassName, type)`
- Pool Powers: Universal (all ATs), 4 slots, must prevent duplicate selection
- Ancillary: Archetype-specific, disabled until level 35+, hidden for Epic ATs

**Key Behaviors**:
- Archetype change → Reset all powersets → Show confirmation if powers selected
- Powerset change → Clear selected powers from that set → Show confirmation
- Pool validation → Can't select same pool twice across 4 slots
- Linked secondaries → Some ATs have secondary auto-selected based on primary
- Epic ATs → Hide pool/ancillary selectors (they don't have them)

**Translation to Web**:
- ComboBox → shadcn/ui Select with Command (searchable)
- OwnerDraw icons → Next.js Image components in Select options
- Tooltip → shadcn/ui Popover or Tooltip
- Disabled state → `disabled` prop on Select

---

## Testing Strategy

### Component Tests (~30 total)

**PowersetSelector** (5 tests):
- Renders with powersets from props
- Filters powersets on search
- Calls onChange when powerset selected
- Displays powerset icons
- Shows disabled state

**PrimaryPowersetSelector** (6 tests):
- Renders disabled when no archetype
- Shows archetypes's primary powersets
- Updates store on selection
- Shows confirmation when changing mid-build
- Handles loading state
- Handles error state

**SecondaryPowersetSelector** (6 tests):
- Renders disabled when no archetype
- Shows archetype's secondary powersets
- Updates store on selection
- Handles linked secondaries (auto-select, disable)
- Shows confirmation when changing mid-build
- Resets when archetype changes

**PoolPowerSelector** (7 tests):
- Renders all pool powersets
- Filters out already-selected pools
- Updates store at correct index
- Can be cleared (set to null)
- Shows mutual exclusivity warnings
- Multiple instances don't interfere
- Validation prevents duplicate pools

**AncillarySelector** (5 tests):
- Renders disabled when level < 35
- Enables when level >= 35
- Hidden for Epic ATs
- Shows archetype's ancillary powersets
- Updates store on selection

**PowersetSelectionPanel** (3 tests):
- Renders all child components
- Coordinates state updates
- Resets powersets when archetype changes

**usePowersets Hook** (4 tests):
- Fetches from API by archetype
- Returns loading state
- Returns data on success
- Handles errors

---

## Implementation Tasks Summary

1. ✅ **Update CharacterStore** - Add powerset state fields and actions
2. ✅ **Create usePowersets Hook** - TanStack Query for powerset fetching
3. ✅ **Create PowersetSelector** - Reusable base component
4. ✅ **Create PrimaryPowersetSelector** - Filtered primary selector
5. ✅ **Create SecondaryPowersetSelector** - Filtered secondary selector with linked logic
6. ✅ **Create PoolPowerSelector** - Pool selector with validation
7. ✅ **Create AncillarySelector** - Level-gated selector
8. ✅ **Create PowersetSelectionPanel** - Container component
9. ✅ **Integrate into Builder Page** - Add to CharacterCreationPanel
10. ✅ **Run Tests & Quality Checks** - Ensure all passing

**Estimated Time**: 10-14 hours

---

## Acceptance Criteria

### Functional

✅ Primary powerset selector displays archetype's primary powersets
✅ Secondary powerset selector displays archetype's secondary powersets
✅ Pool power selectors (4 slots) display all pool powers
✅ Pool validation prevents selecting same pool twice
✅ Ancillary selector disabled when level < 35
✅ Ancillary selector hidden for Epic ATs
✅ Archetype change resets all powersets (with confirmation)
✅ Powerset change clears selected powers (with confirmation, deferred to next epic)
✅ All selections update characterStore
✅ All selections persist across page refreshes (localStorage)

### Visual

✅ Components match MidsReborn functional layout
✅ Modern web aesthetic (not pixel-perfect copy)
✅ Icons display for powersets
✅ Searchable dropdowns for easy selection
✅ Responsive on mobile/tablet/desktop
✅ Smooth transitions and interactions

### Technical

✅ All TypeScript strict mode compliant (no `any`)
✅ All tests passing (>80% coverage)
✅ ESLint and Prettier passing
✅ No console errors or warnings
✅ TanStack Query caching working correctly
✅ Zustand persistence working correctly

---

## Key Design Decisions

### 1. Powerset Data Source
**Decision**: Fetch from `/api/archetypes/{id}/powersets` endpoint
**Rationale**: Backend already implements filtered powersets by archetype. No duplication needed.

### 2. Pool Power Validation
**Decision**: Client-side validation to prevent duplicate pool selection
**Rationale**: Simple logic (filter already-selected pools). No backend validation needed.

### 3. Ancillary Level Unlock
**Decision**: Conditional enable based on `level >= 35`
**Rationale**: Matches MidsReborn behavior. Simple prop-based disable.

### 4. Epic AT Special Handling
**Decision**: Hide pool/ancillary selectors if Epic AT selected
**Rationale**: Epic ATs don't have pool/epic powersets. Conditional rendering based on archetype.

### 5. Component Reusability
**Decision**: Single PowersetSelector base component, specialized wrappers
**Rationale**: DRY principle. All selectors share 90% of logic. Props differentiate behavior.

### 6. Linked Secondary Logic
**Decision**: Auto-select secondary if archetype has linked secondary, disable dropdown
**Rationale**: Some ATs (like Kheldians) have forced secondary. Matches MidsReborn.

---

## Dependencies

### From Previous Epics
- ✅ Epic 1.2: CharacterStore foundation, Zustand setup
- ✅ Epic 1.3: BuildLayout, SidePanel components
- ✅ Epic 1.4: API client, TanStack Query setup
- ✅ Epic 2.1: ArchetypeSelector, CharacterCreationPanel, archetype selection working

### Backend API
- ✅ `GET /api/archetypes/{id}/powersets` - Already implemented
- ✅ `GET /api/powersets` - Already implemented

### shadcn/ui Components
Required components:
- Select (with Command for search)
- Popover or Tooltip (for powerset info)
- Dialog (for confirmation on powerset change)
- Icons (for powerset icons)

---

## Next Epic Preview

**Epic 2.3**: (TBD - Could be "Character Sheet Display" or start Epic 3 "Power Selection")

Epic 2.2 sets the foundation for power selection:
- ✅ Powersets selected (primary, secondary, pools, ancillary)
- ✅ CharacterStore ready for power arrays
- ✅ Layout ready for power picker UI

**Next steps**:
- Epic 3.1: Available Powers Panel - Display powers from selected powersets
- Epic 3.2: Power Picker UI - Add powers to build at specific levels

**Prerequisites Met**:
- ✅ Powersets selected (provides power lists)
- ✅ CharacterStore ready for `powers: PowerEntry[]`
- ✅ API endpoints for powers (`GET /api/powersets/{id}/powers`)

---

## Summary

Epic 2.2 delivers powerset selection for Mids Hero Web:
- **6 React components** for powerset configuration
- **Primary/Secondary selectors** filtered by archetype
- **4 pool power slots** with duplicate validation
- **Ancillary selector** unlocked at level 35+
- **State management** via Zustand with localStorage persistence
- **API integration** via TanStack Query with forever caching
- **~30 tests** covering all components and hooks

The implementation closely follows MidsReborn's powerset selection flow while adding modern web UX enhancements (search, icons, responsive design, better validation feedback).

---

**Status**: ✅ Planning Complete - Ready for Execution
**Components**: 6 React components + 1 custom hook
**Tests**: ~30 tests
**Estimated Time**: 10-14 hours
**Dependencies**: All met (Epic 1.2 ✅, Epic 1.3 ✅, Epic 1.4 ✅, Epic 2.1 ✅, Backend API ✅)
**Next**: Execute plan via implementation
