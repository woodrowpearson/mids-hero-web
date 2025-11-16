# Epic 1.3: Layout Shell + Navigation - Summary

**Date**: 2025-11-16
**Status**: Planning Complete
**Epic**: 1.3 - Layout Shell + Navigation
**Detailed Plan**: 2025-11-16-epic-1.3-layout-shell-navigation.md

---

## What This Epic Accomplishes

Epic 1.3 establishes the foundational layout structure for Mids Hero Web, creating:
1. **Main Build Layout** with configurable 2-6 column grid system
2. **Top Control Panel** with character info and navigation
3. **Optional Sidebar** for future character creation controls (Epic 2)
4. **Routing Structure** for home, builder, and shared build pages

This epic focuses purely on layout structure with placeholder content. Actual power selection, character creation, and build functionality will be implemented in subsequent epics.

---

## Key Components Created

### Layout Components

**BuildLayout** (`components/layout/BuildLayout.tsx`):
- Main layout wrapper using CSS Grid
- Configurable column count (2-6)
- Responsive breakpoints (mobile: 1 column, tablet: max 3, desktop: full control)
- Fixed top panel + optional sidebar + scrollable main area

**TopPanel** (`components/layout/TopPanel.tsx`):
- Fixed 77px header (matches MidsReborn proportions)
- Left: Character info (name, archetype, level) - reads from characterStore
- Center: Action buttons (New, Save, Load, Export) - placeholders for future epics
- Right: ColumnLayoutSelector + settings icon

**SidePanel** (`components/layout/SidePanel.tsx`):
- Collapsible 250px left sidebar (matches MidsReborn)
- Placeholder content for Epic 2 (character creation)
- Smooth collapse/expand transition
- Controlled by uiStore.layout.sidebarCollapsed

**ColumnLayoutSelector** (`components/ui/ColumnLayoutSelector.tsx`):
- Toggle group with options 2-6
- Highlights current selection
- Updates uiStore.layout.columnCount
- Persists to localStorage

### Page Components

**Home Page** (`app/page.tsx`):
- Landing page with hero section
- "Create New Build" button → /builder
- Feature list

**Builder Page** (`app/builder/page.tsx`):
- Main build editor (client-side component)
- Uses BuildLayout with uiStore column count
- Empty state placeholder for Epic 3

**Build Viewer Page** (`app/build/[id]/page.tsx`):
- Shared build display (SSR for rich previews)
- generateMetadata for OpenGraph/Twitter Cards
- Placeholder for Epic 6 (build loading)

---

## State Management Approach

### UIStore Extension

Extends existing `uiStore` from Epic 1.2 with new `layout` object:

```typescript
interface UIStore {
  theme: 'light' | 'dark';    // Existing from Epic 1.2

  layout: {                    // NEW for Epic 1.3
    columnCount: number;       // 2-6, default 3
    sidebarCollapsed: boolean; // Default false
    topPanelVisible: boolean;  // Always true for v1
  };

  setColumnCount: (count: number) => void;
  toggleSidebar: () => void;
}
```

**Persistence**: Layout preferences persist to localStorage via Zustand persist middleware (already configured in Epic 1.2).

**Validation**: `setColumnCount` validates range 2-6, rejects out-of-range values.

---

## MidsReborn Reference Implementation

From `MIDSREBORN-UI-ANALYSIS-epic-1.3.md`:

**Layout Structure** (frmMain.cs):
- **Top**: 77px fixed (24px menu + 53px control panel)
- **Left**: ~250px sidebar with character controls
- **Center**: FlowLayoutPanel with 2-6 columns (default: 3)

**Column System**:
- User-selectable via View menu (View > 2 Col, 3 Col, etc.)
- Default: 3 columns
- Persisted in app configuration

**Power Grid**:
- 24 max powers per column
- 15px horizontal padding, 25px vertical padding
- Custom drawing with ClsDrawX

**Translation to Web**:
- Form → Next.js page
- Panel → div + Tailwind
- FlowLayoutPanel → CSS Grid
- ToolStrip → Fixed header with flex
- Menu bar → Button group

---

## Responsive Design

### Breakpoints

**Mobile** (<640px):
- Force single column
- Collapse sidebar to drawer (future enhancement)
- Stack controls vertically

**Tablet** (640px - 1024px):
- Max 3 columns
- Collapsible sidebar
- Touch-friendly controls

**Desktop** (1024px+):
- Full 2-6 column control
- All panels visible by default
- Optimized for mouse input

### Implementation

```javascript
// Tailwind classes
'grid-cols-1 md:grid-cols-2 lg:grid-cols-${columnCount}'
```

Responsive column count calculated based on screen size and user preference.

---

## API Integration

**No New Backend Endpoints Required**

Epic 1.3 uses only client-side state management:
- `characterStore` (Epic 1.2) - Character build state
- `uiStore` (Epic 1.3) - Layout preferences

**Future API Integration** (Epic 6):
- `POST /api/builds` - Save build
- `GET /api/builds/:id` - Load shared build

---

## Testing Strategy

### Component Tests (~35 total)

**Layout Components** (15 tests):
- BuildLayout: Column count, sidebar visibility, responsiveness
- TopPanel: Character info display, button rendering
- SidePanel: Collapse/expand, toggle button
- ColumnLayoutSelector: Option display, selection, persistence

**State Management** (10 tests):
- UIStore: Column count validation (2-6), sidebar toggle, persistence

**Page Components** (10 tests):
- Home page: Title, button link, feature list
- Builder page: BuildLayout integration, empty state
- Build viewer: Param display, metadata generation

**Test Coverage Goal**: >80% for all components and stores

---

## Implementation Tasks

1. **Update UIStore** with layout state + tests
2. **Create BuildLayout** component + tests
3. **Create TopPanel** component + tests
4. **Create SidePanel** component + tests
5. **Create ColumnLayoutSelector** component + tests
6. **Create Home page** + tests
7. **Create Builder page** + tests
8. **Create Build Viewer page** + tests
9. **Install shadcn/ui ToggleGroup** component
10. **Run all tests** and ensure passing

**Estimated Time**: 4-6 hours

---

## Acceptance Criteria

### Functional

✅ BuildLayout renders with 2-6 configurable columns
✅ Column count selector updates grid layout
✅ Sidebar collapses and expands smoothly
✅ TopPanel displays character info from store
✅ All three pages (Home, Builder, Viewer) render correctly
✅ Layout preferences persist across sessions
✅ Responsive breakpoints work on mobile/tablet/desktop

### Visual

✅ Layout structure matches MidsReborn proportions
✅ Empty state placeholders look reasonable
✅ Column spacing appropriate (15-25px)
✅ Smooth transitions on column count change
✅ No layout shift or overflow issues

### Technical

✅ All TypeScript strict mode compliant (no `any`)
✅ All tests passing (>80% coverage)
✅ ESLint and Prettier passing
✅ No console errors or warnings

---

## Deferred Features

**Epic 2** (Character Creation):
- Character creation controls in SidePanel
- Archetype/Origin/Powerset selectors

**Epic 3** (Power Selection):
- Power cards in main grid
- Power picking interaction

**Epic 4** (Build Totals):
- Totals panel (floating or embedded)
- Set bonus display

**Epic 6** (Build Persistence):
- Save/Load functionality
- Backend integration for shared builds

---

## Next Epic Preview

**Epic 1.4**: API Client Integration

**Will build on Epic 1.3**:
- Connect TopPanel action buttons to API calls
- Display loading states in main grid
- Handle API errors gracefully
- Test real data fetching

**Prerequisites Met**:
- ✅ Layout structure established
- ✅ State management ready
- ✅ Empty state placeholders in place

---

## Key Design Decisions

### 1. CSS Grid over Flexbox

**Rationale**: CSS Grid provides superior 2D layout control for power card grid, handles variable column counts elegantly.

### 2. Fixed Top Panel

**Rationale**: Unlike MidsReborn (scrollable), web UX benefits from fixed header keeping navigation always accessible.

### 3. Deferred Sidebar Content

**Rationale**: Epic 1.3 focuses on structure. Character creation controls (Epic 2) will populate sidebar.

### 4. Placeholder Action Buttons

**Rationale**: TopPanel includes buttons (New, Save, Load) as placeholders. Functionality added in Epics 4-6.

### 5. Single-Column Mobile

**Rationale**: Power cards need minimum width. Mobile (<640px) forces single column for readability.

### 6. SSR for Build Viewer

**Rationale**: generateMetadata enables rich preview cards on Discord/Twitter when sharing builds (Epic 6).

---

## Summary

Epic 1.3 delivers the layout foundation for Mids Hero Web:
- **Configurable layout** (2-6 columns with responsive breakpoints)
- **Three-page routing** (Home, Builder, Viewer)
- **Persistent preferences** (via Zustand + localStorage)
- **Empty state placeholders** (for future epics)

The layout structure closely follows MidsReborn's proven design while adding web-native enhancements (fixed header, responsive design, smooth transitions).

---

**Status**: ✅ Planning Complete - Ready for Execution
**Components**: 8 (4 layout + 1 UI + 3 pages)
**Tests**: ~35 tests
**Dependencies**: Epic 1.2 complete ✅
**Next**: Execute via superpowers plugin or direct implementation
