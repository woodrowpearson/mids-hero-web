# Epic 2.3: Character Sheet Display - Summary

**Date**: 2025-11-18
**Status**: Planning Complete
**Epic**: 2.3 - Character Sheet Display
**Detailed Plan**: 2025-11-18-epic-2.3-character-sheet-display.md

---

## What This Epic Accomplishes

Epic 2.3 implements the character sheet display functionality for Mids Hero Web, providing users with a comprehensive view of their character information, archetype modifiers, caps, and inherent powers. This epic creates 5 React components (1 container + 1 summary + 3 detail displays) that integrate with the characterStore (from Epic 2.1) to display character summary in MidsReborn format, archetype base modifiers (HP, regen, recovery, threat), archetype caps (7 types: HP, damage, resistance, defense, regen, recovery, recharge), and inherent powers list with icons and descriptions.

The implementation closely mirrors MidsReborn's character info panel while adding modern web enhancements like tabbed interface, editable name/level fields, formatted tables, and responsive design. Most data is read from the existing characterStore with inherent powers fetched from the backend API (`/api/archetypes/{id}/powersets?powerset_type=inherent`).

**Key Enhancement Required**: Backend API needs to be updated to include archetype caps and base modifiers in the `GET /api/archetypes/{id}` response (data already exists in `archetype_caps.py`, just needs to be added to API response).

---

## Key Components Created

### React Components

1. **CharacterSheet** (`components/character/CharacterSheet.tsx`)
   - Main container component with tabbed interface
   - Composes CharacterSummary, ATModifiersDisplay, CapsDisplay, InherentPowersDisplay
   - Tabs: Base Modifiers | Caps | Inherent Powers
   - Props: `mode` (view/edit), `className`

2. **CharacterSummary** (`components/character/CharacterSummary.tsx`)
   - Displays character info in MidsReborn format: `"{Name}: Level {level} {Origin} {Archetype} ({Primary} / {Secondary})"`
   - Edit mode for name and level (toggle with Edit button)
   - Integrates with characterStore via actions: `setName`, `setLevel`
   - Input validation: level must be 1-50

3. **ATModifiersDisplay** (`components/character/ATModifiersDisplay.tsx`)
   - Table showing 4 base modifiers from archetype
   - Base HP (at level 50), Base Regeneration, Base Recovery, Base Threat
   - Formatted values: HP as number, others as percentages
   - Props: `archetype`, `className`

4. **CapsDisplay** (`components/character/CapsDisplay.tsx`)
   - Table showing 7 archetype caps
   - HP Cap, Damage Cap, Resistance Cap, Defense Cap, Regen Cap, Recovery Cap, Recharge Cap
   - All formatted as percentages
   - Includes descriptions for each cap
   - Props: `archetype`, `className`

5. **InherentPowersDisplay** (`components/character/InherentPowersDisplay.tsx`)
   - Card list showing archetype inherent powers
   - Fetched via `useInherentPowers` hook (TanStack Query)
   - Displays power icons, names, descriptions
   - Sorted by priority (MidsReborn behavior)
   - Tooltips for full descriptions
   - Props: `archetype`, `className`

### Custom Hooks

- **useInherentPowers** (`hooks/useInherentPowers.ts`)
  - TanStack Query hook for fetching inherent powers by archetype
  - Endpoint: `GET /api/archetypes/{id}/powersets?powerset_type=inherent`
  - Extracts powers from inherent powerset response
  - Caches data forever (static game data)
  - Error handling and loading states

---

## State Management Approach

### Server State (TanStack Query)

**Query**: `['inherent-powers', archetypeId]`
- **Endpoint**: `GET /api/archetypes/{id}/powersets?powerset_type=inherent`
- **Cache**: Forever (staleTime: Infinity) - static game data
- **Purpose**: Fetch inherent powers for selected archetype
- **Response**: Powerset with type="Inherent" and powers array

### Client State (Zustand characterStore)

**No changes needed** - all required state already exists from Epic 2.1:

```typescript
{
  name: string;
  level: number;
  archetype: Archetype | null;
  origin: Origin | null;
  alignment: Alignment | null;
  primaryPowerset: Powerset | null;
  secondaryPowerset: Powerset | null;
}
```

**Actions used**:
- `setName(name: string)` - Update character name
- `setLevel(level: number)` - Update character level

### Derived State

- **Inherent Powers**: Fetched via `useInherentPowers(archetype.id)`
- **Base Modifiers**: Read from `archetype.baseHP`, `archetype.baseRegen`, etc.
- **Caps**: Read from `archetype.hpCap`, `archetype.damageCap`, etc.

---

## API Endpoints Used

### 1. GET /api/archetypes/{id}

- **Status**: ⚠️ **Requires Enhancement**
- **Purpose**: Fetch archetype with caps and base modifiers
- **Current**: Returns archetype name, display name, powersets
- **Required Enhancement**: Add 11 new fields (4 base modifiers + 7 caps)

**New Fields Needed**:
```json
{
  // Base modifiers (NEW)
  "baseHP": 1204.8,
  "baseRegen": 0.02,
  "baseRecovery": 0.0167,
  "baseThreat": 1.0,

  // Caps (NEW)
  "hpCap": 1.606,
  "damageCap": 5.0,
  "resistanceCap": 0.75,
  "defenseCap": 2.25,
  "regenCap": 30.0,
  "recoveryCap": 6.0,
  "rechargeCap": 4.0
}
```

**Backend Implementation**:
- Data already exists in `backend/app/calculations/core/archetype_caps.py`
- Add fields to Archetype SQLAlchemy model
- Update API schema to include new fields
- Populate via migration or seed data

### 2. GET /api/archetypes/{id}/powersets?powerset_type=inherent

- **Status**: ✅ Already implemented
- **Purpose**: Fetch inherent powers for archetype
- **Response**: Powerset with type="Inherent" and powers array
- **No changes needed**

---

## MidsReborn Reference Implementation

From MIDSREBORN-UI-ANALYSIS-epic-2.3.md:

**Character Display** (frmMain.cs):
- Single label showing: `"{Name}: Level {level} {Origin} {Archetype} ({Primary} / {Secondary})"`
- Name, level editable via separate controls in top panel

**Archetype Caps** (Archetype.cs):
- 7 cap types stored in Archetype class
- Varies by AT (e.g., Brute damage cap = 775%, Tanker resistance cap = 90%)
- Used for display and calculation limits

**Inherent Powers** (Character.cs, DatabaseAPI.cs):
- Retrieved via `DatabaseAPI.GetInherentPowerset()`
- Stored in `Character.InherentDisplayList` sorted by priority
- Examples: Fury (Brute), Defiance (Blaster), Gauntlet (Tanker)

**Translation to Web**:
- Single label → CharacterSummary with MidsReborn format
- Multiple panels → Tabbed interface (Modifiers | Caps | Inherents)
- Tables → shadcn/ui Table components with proper formatting
- Icons → Next.js Image components with fallback

---

## Testing Strategy

### Component Tests (~25 total)

**CharacterSheet** (3 tests):
- Renders all child components
- Switches between tabs
- Updates when archetype changes

**CharacterSummary** (6 tests):
- Displays summary in MidsReborn format
- Enters edit mode on Edit button click
- Updates name in store on input change
- Updates level in store on input change (validates 1-50)
- Exits edit mode on Done button click
- Handles missing data gracefully

**ATModifiersDisplay** (5 tests):
- Renders table with 4 base modifiers
- Formats values correctly (HP as number, others as %)
- Shows different values for different archetypes
- Shows placeholder when no archetype
- Updates when archetype changes

**CapsDisplay** (6 tests):
- Renders table with 7 cap types
- Formats all values as percentages
- Shows description for each cap
- Different caps for different ATs (Tanker vs Blaster)
- Shows placeholder when no archetype
- Updates when archetype changes

**InherentPowersDisplay** (9 tests):
- Fetches inherent powers from API
- Displays powers in priority order
- Shows power icons (with fallback)
- Shows power names and descriptions
- Displays tooltips on info button hover
- Shows loading state while fetching
- Shows error state on API failure
- Shows placeholder when no archetype
- Updates when archetype changes

**useInherentPowers Hook** (4 tests):
- Fetches from API by archetype ID
- Returns loading state
- Returns data on success
- Handles errors

---

## Implementation Tasks Summary

1. ⚠️ **Backend API Enhancement** - Add caps and modifiers to archetype response (2-3 hours)
2. ✅ **Update TypeScript Types** - Add cap/modifier fields to Archetype interface (30 min)
3. ✅ **Create useInherentPowers Hook** - TanStack Query for inherent powers (1 hour)
4. ✅ **Create ATModifiersDisplay** - Table showing base modifiers (2 hours)
5. ✅ **Create CapsDisplay** - Table showing archetype caps (2 hours)
6. ✅ **Create InherentPowersDisplay** - Card list of inherent powers (3 hours)
7. ✅ **Create CharacterSummary** - MidsReborn format with edit mode (2-3 hours)
8. ✅ **Create CharacterSheet** - Main container with tabs (2 hours)
9. ✅ **Integration & Visual Testing** - Add to builder page, verify against MidsReborn (2-3 hours)
10. ✅ **Documentation & Cleanup** - JSDoc, CHANGELOG, code review (1 hour)

**Estimated Time**: 16-20 hours (includes backend enhancement)

---

## Acceptance Criteria

### Functional

✅ Character summary displays in MidsReborn format
✅ Character name and level are editable in edit mode
✅ Level validation enforces 1-50 range
✅ Archetype base modifiers display correctly (4 types)
✅ Archetype caps display correctly (7 types)
✅ Inherent powers list displays with icons and descriptions
✅ Inherent powers sorted by priority
✅ All data updates when archetype changes
✅ All selections persist across page refreshes (characterStore)

### Visual

✅ Components match MidsReborn functional layout
✅ Modern web aesthetic (tabs, cards, tables)
✅ Tables formatted correctly (percentages, numbers)
✅ Icons display for inherent powers (with fallback)
✅ Responsive on mobile/tablet/desktop
✅ Smooth transitions between tabs

### Technical

✅ All TypeScript strict mode compliant (no `any`)
✅ All tests passing (>80% coverage)
✅ ESLint and Prettier passing
✅ No console errors or warnings
✅ TanStack Query caching working correctly
✅ Backend API returns caps and modifiers

---

## Key Design Decisions

### 1. Tabbed Interface for Archetype Data
**Decision**: Use tabs (Modifiers | Caps | Inherents) instead of single panel
**Rationale**: Reduces visual clutter, organizes data logically, better for responsive design

### 2. Edit Mode for Name/Level
**Decision**: Toggle edit mode with Edit button, not always-editable
**Rationale**: Cleaner view mode, prevents accidental edits, matches common web patterns

### 3. Inherent Powers via API
**Decision**: Fetch inherent powers from backend API, not store in characterStore
**Rationale**: Inherent powers are static archetype data, not build state. API is source of truth.

### 4. Backend API Enhancement Required
**Decision**: Add caps/modifiers to archetype API response
**Rationale**: Data already exists in backend, simple to add fields, avoids separate endpoints

### 5. Component Reusability
**Decision**: Separate components for Modifiers, Caps, Inherents (not single component)
**Rationale**: Each has different data structure and formatting, easier to test and maintain separately

### 6. MidsReborn Format Preservation
**Decision**: Keep exact MidsReborn summary format: `"{Name}: Level {level} {Origin} {Archetype} ({Primary} / {Secondary})"`
**Rationale**: Familiar to existing users, compact, informative

---

## Dependencies

### From Previous Epics
- ✅ Epic 1.2: CharacterStore foundation (name, level, archetype, origin)
- ✅ Epic 1.3: Layout components (Card, Tabs, Table)
- ✅ Epic 1.4: API client, TanStack Query setup
- ✅ Epic 2.1: Archetype selection, ArchetypeSelector component
- ✅ Epic 2.2: Powerset selection (for summary display)

### Backend API
- ⚠️ `GET /api/archetypes/{id}` - Requires enhancement with caps/modifiers
- ✅ `GET /api/archetypes/{id}/powersets?powerset_type=inherent` - Already implemented

### shadcn/ui Components
Required components (should all be installed):
- Card
- Tabs (TabsList, TabsTrigger, TabsContent)
- Table (TableHeader, TableRow, TableHead, TableBody, TableCell)
- Input
- Button
- Tooltip (TooltipProvider, Tooltip, TooltipTrigger, TooltipContent)
- Label
- Icons (PencilIcon, InfoIcon, ZapIcon, Loader2)

---

## Next Epic Preview

**Epic 3.1**: Available Powers Panel - Display powers from selected powersets

Epic 2.3 provides the character sheet foundation:
- ✅ Character fully configured (archetype, origin, powersets, name, level)
- ✅ Archetype data accessible (caps, modifiers, inherents)
- ✅ CharacterStore ready for power selection

**Next steps**:
- Epic 3.1: Available Powers Panel - Display powers from selected powersets
- Epic 3.2: Power Picker UI - Add powers to build at specific levels

**Prerequisites Met**:
- ✅ Character info displayed
- ✅ Powersets selected (Epic 2.2)
- ✅ Layout ready for power lists
- ✅ API endpoints for powers (`GET /api/powersets/{id}/powers`)

---

## Summary

Epic 2.3 delivers character sheet display for Mids Hero Web:
- **5 React components** for character info, caps, modifiers, inherent powers
- **CharacterSummary** in MidsReborn format with edit mode
- **ATModifiersDisplay** showing 4 base modifiers
- **CapsDisplay** showing 7 archetype caps
- **InherentPowersDisplay** showing inherent powers with icons
- **State management** via Zustand characterStore + TanStack Query
- **API integration** requires backend enhancement (2-3 hours)
- **~25 tests** covering all components and hooks

The implementation closely follows MidsReborn's character info panel while adding modern web UX enhancements (tabs, responsive design, better formatting, edit mode).

---

**Status**: ✅ Planning Complete - Ready for Execution
**Components**: 5 React components + 1 custom hook
**Tests**: ~25 tests
**Estimated Time**: 16-20 hours
**Dependencies**: Backend API enhancement (2-3 hours), all other dependencies met
**Next**: Execute plan via implementation (Phase 4)
