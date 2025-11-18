# Epic 2.1: Archetype & Origin Selection - Summary

**Date**: 2025-11-16
**Status**: Planning Complete
**Epic**: 2.1 - Archetype & Origin Selection
**Detailed Plan**: 2025-11-16-epic-2.1-archetype-origin-selection.md

---

## What This Epic Accomplishes

Epic 2.1 implements the foundational character creation UI for Mids Hero Web, enabling users to configure their character's core identity: name, archetype, origin, and alignment. This epic creates six React components that work together to provide a modern web experience matching MidsReborn's character creation functionality, including an archetype selector with search and info display, origin selector filtered by archetype, alignment selector, and character name input. All selections are stored in the characterStore (Zustand) and persist across sessions via localStorage.

---

## Key Components Created

### React Components

1. **CharacterNameInput** (`components/character/CharacterNameInput.tsx`)
   - Simple text input for character name
   - Real-time updates to characterStore
   - No validation required

2. **ArchetypeSelector** (`components/character/ArchetypeSelector.tsx`)
   - Select component with search (shadcn/ui Select + Command)
   - Fetches archetypes from `GET /api/archetypes` via TanStack Query
   - Displays archetype icons and names
   - Shows confirmation dialog when changing archetype with existing powersets
   - Info popover with archetype description, inherent powers, modifiers, caps

3. **OriginSelector** (`components/character/OriginSelector.tsx`)
   - Select component for origin (Magic, Mutation, Natural, Science, Technology)
   - Filtered to show only archetype's allowed origins
   - Disabled until archetype selected
   - Auto-resets when archetype changes

4. **AlignmentSelector** (`components/character/AlignmentSelector.tsx`)
   - RadioGroup or ToggleGroup for alignment (Hero/Villain/Vigilante/Rogue)
   - Auto-sets default from archetype type (Hero AT → Hero alignment)
   - User can override default

5. **ArchetypeInfoDisplay** (`components/character/ArchetypeInfoDisplay.tsx`)
   - Card component displaying selected archetype details
   - Shows description, inherent powers, modifiers, and caps
   - Empty state when no archetype selected

6. **CharacterCreationPanel** (`components/character/CharacterCreationPanel.tsx`)
   - Container component composing all child components
   - Handles coordination logic (archetype changes reset origin)
   - Integrates with SidePanel from Epic 1.3

### Custom Hooks

- **useArchetypes** (`hooks/useArchetypes.ts`)
  - TanStack Query hook for fetching archetypes
  - Caches data forever (static game data)
  - Error handling and loading states

### State Management

- **CharacterStore Updates** (`stores/characterStore.ts`)
  - Enhanced `setArchetype` with origin reset logic
  - New `setOrigin` action
  - New `setAlignment` action
  - Persistence to localStorage (already configured in Epic 1.2)

---

## State Management Approach

### Server State (TanStack Query)

**Query**: `['archetypes']`
- **Endpoint**: `GET /api/archetypes`
- **Cache**: Forever (staleTime: Infinity)
- **Purpose**: Fetch all playable archetypes with full data

### Client State (Zustand characterStore)

**State Shape**:
```typescript
{
  name: string;
  archetype: Archetype | null;
  origin: string | null;
  alignment: Alignment | null;
}
```

**Actions**:
- `setName(name: string)` - Update character name
- `setArchetype(archetype: Archetype)` - Update archetype, reset origin
- `setOrigin(origin: string)` - Update origin
- `setAlignment(alignment: Alignment)` - Update alignment

**Persistence**: All state automatically saved to localStorage via Zustand persist middleware (Epic 1.2).

---

## API Endpoints Used

### 1. GET /api/archetypes
- **Status**: ✅ Already implemented in backend
- **Purpose**: Fetch all playable archetypes
- **Response**: `Archetype[]` with full data (modifiers, caps, allowed powersets, etc.)
- **Caching**: Forever (static game data)

### 2. Origins Data
- **Source**: Derived from archetype data (`archetype.origin[]`)
- **No separate endpoint needed** - origins are archetype-specific
- **Default origins**: Magic, Mutation, Natural, Science, Technology

---

## MidsReborn Reference Implementation

From MIDSREBORN-UI-ANALYSIS-epic-2.1.md:

**Character Creation UI** (frmMain.cs):
- Compact top panel with stacked controls
- Name: TextBox (144px width)
- Archetype: ComboBox with OwnerDraw icons (15 playable ATs)
- Origin: ComboBox filtered by archetype (5 origins)
- Alignment: Toggle button cycling through Hero/Villain/Rogue/Vigilante

**Key Behaviors**:
- Archetype change → Reset origin to first allowed origin
- Archetype change with powersets → Show confirmation, clear powersets
- Origin limited to archetype's allowed origins
- Alignment auto-set from archetype type, user can override

**Translation to Web**:
- ComboBox → shadcn/ui Select with Command (search)
- TextBox → shadcn/ui Input
- Toggle button → shadcn/ui RadioGroup or ToggleGroup
- OwnerDraw icons → Next.js Image components

---

## Testing Strategy

### Component Tests (~25 total)

**CharacterNameInput** (3 tests):
- Renders with label and input
- Displays current value
- Updates store on change

**ArchetypeSelector** (7 tests):
- Renders with archetypes from API
- Filters archetypes on search
- Shows confirmation when changing with powersets
- Updates store on selection
- Displays archetype info in popover
- Handles loading state
- Handles error state

**OriginSelector** (5 tests):
- Renders disabled when no archetype
- Shows archetype's allowed origins
- Updates store on selection
- Resets when archetype changes

**AlignmentSelector** (4 tests):
- Renders all alignment options
- Updates store on selection
- Auto-sets from archetype

**ArchetypeInfoDisplay** (4 tests):
- Shows empty state when no archetype
- Displays archetype details
- Shows inherent powers
- Shows modifiers and caps

**CharacterCreationPanel** (3 tests):
- Renders all child components
- Coordinates state updates
- Resets origin when archetype changes

**useArchetypes Hook** (4 tests):
- Fetches from API
- Returns loading state
- Returns data on success
- Handles errors

---

## Implementation Tasks Summary

1. ✅ **Update CharacterStore** - Add setArchetype, setOrigin, setAlignment actions
2. ✅ **Create useArchetypes Hook** - TanStack Query for archetype fetching
3. ✅ **Create CharacterNameInput** - Simple input component
4. ✅ **Create ArchetypeSelector** - Complex select with search and info
5. ✅ **Create OriginSelector** - Filtered select component
6. ✅ **Create AlignmentSelector** - RadioGroup component
7. ✅ **Create ArchetypeInfoDisplay** - Card with archetype details
8. ✅ **Create CharacterCreationPanel** - Container component
9. ✅ **Integrate into Builder Page** - Add to SidePanel
10. ✅ **Run Tests & Quality Checks** - Ensure all passing

**Estimated Time**: 8-12 hours

---

## Acceptance Criteria

### Functional

✅ Character name input updates store in real-time
✅ Archetype selector fetches and displays all playable archetypes
✅ Archetype selection updates store and resets origin
✅ Origin selector shows only archetype's allowed origins
✅ Origin selector disabled when no archetype selected
✅ Alignment selector updates store
✅ Archetype info displays description, inherents, modifiers, caps
✅ All selections persist across page refreshes (localStorage)

### Visual

✅ Components match MidsReborn functional layout
✅ Modern web aesthetic (not pixel-perfect copy)
✅ Icons display for archetypes and origins
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

### 1. Archetype Data Source
**Decision**: Fetch from `/api/archetypes` endpoint
**Rationale**: Backend already implements full archetype data. No duplication needed.

### 2. Origin Data Source
**Decision**: Derive from archetype data (`archetype.origin[]`)
**Rationale**: Origins are archetype-specific. Simpler than separate endpoint.

### 3. Archetype Change Confirmation
**Decision**: Show confirmation dialog if powersets selected
**Rationale**: MidsReborn behavior - changing AT resets incompatible powersets. Warn before destructive action.

### 4. Component Location
**Decision**: Place CharacterCreationPanel in SidePanel
**Rationale**: Collapsible sidebar provides better web UX than fixed top panel.

### 5. Search in Archetype Selector
**Decision**: Use shadcn/ui Command for search
**Rationale**: 15+ archetypes benefit from search/filter capability.

---

## Dependencies

### From Previous Epics
- ✅ Epic 1.2: CharacterStore foundation, Zustand setup
- ✅ Epic 1.3: BuildLayout, SidePanel components

### Backend API
- ✅ `GET /api/archetypes` - Already implemented

### shadcn/ui Components
Required components:
- Input
- Select
- RadioGroup or ToggleGroup
- Card
- Dialog (for confirmation)
- Popover (for archetype info)
- Command (for search)

---

## Next Epic Preview

**Epic 2.2**: Powerset Selection

Will build on Epic 2.1:
- Primary powerset selector (filtered by `archetype.primary[]`)
- Secondary powerset selector (filtered by `archetype.secondary[]`)
- Pool power selectors (4 slots)
- Ancillary/Epic selector (unlocks at level 35+)

**Prerequisites Met**:
- ✅ Archetype selected (provides powerset filters)
- ✅ CharacterStore ready for powerset arrays
- ✅ Layout ready for powerset UI

---

## Summary

Epic 2.1 delivers the character creation foundation for Mids Hero Web:
- **6 React components** for character identity configuration
- **Archetype selector** with search, icons, and rich info display
- **Origin selector** filtered by archetype compatibility
- **Alignment selector** for Hero/Villain/Vigilante/Rogue
- **State management** via Zustand with localStorage persistence
- **API integration** via TanStack Query with forever caching
- **~25 tests** covering all components and hooks

The implementation closely follows MidsReborn's character creation flow while adding modern web UX enhancements (search, responsive design, smooth transitions).

---

**Status**: ✅ Planning Complete - Ready for Execution
**Components**: 6 React components + 1 custom hook
**Tests**: ~25 tests
**Estimated Time**: 8-12 hours
**Dependencies**: All met (Epic 1.2 ✅, Epic 1.3 ✅, Backend API ✅)
**Next**: Execute plan via superpowers or direct implementation
