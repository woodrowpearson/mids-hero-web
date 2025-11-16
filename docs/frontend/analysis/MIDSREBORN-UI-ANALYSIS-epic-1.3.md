# MidsReborn UI Analysis: Epic 1.3 - Layout Shell + Navigation

**Created**: 2025-11-16
**Epic**: 1.3 - Layout Shell + Navigation
**MidsReborn Forms Analyzed**: frmMain.cs, frmMain.Designer.cs, ClsDrawX.cs

## Executive Summary

MidsReborn implements its main build editor using a Windows Forms layout with a top menu bar, top control panel, left sidebar for power selection, and a central scrollable canvas for the build display. The layout supports 2-6 configurable columns for organizing powers, with a default of 3 columns. For web implementation, we'll translate this to a modern flexbox/CSS Grid layout with Next.js routing, maintaining functional parity while adding responsive design for mobile and tablet devices.

**Key Findings**:
- Main layout uses a docked top panel (53px height) with ImageButton controls
- Central build display area uses FlowLayoutPanel wrapping a custom PanelGfx control
- Column count (2-6) is user-configurable via View menu, persisted in config
- Powers are arranged in a grid with 24 slots per column maximum
- Layout constants: 15px horizontal padding, 25px vertical padding between powers
- Totals and Set Bonuses are separate floating windows (not embedded in main layout)

## MidsReborn Layout Components

### Main Application Form: frmMain

- **File**: `external/dev/MidsReborn/MidsReborn/Forms/frmMain.cs`, `frmMain.Designer.cs`
- **Purpose**: Main build editor window for creating and editing character builds
- **Layout Type**: Windows Forms with docked panels and absolute positioning
- **Window Size**: Default ~1180x900 (initial width 1180, form is resizable)
- **Main Regions**:
  - **Top**: MenuBar (24px) + topPanel (53px) = 77px total header
  - **Left**: Character creation controls (~250px width) - Name, Archetype, Origin, Primary/Secondary powersets
  - **Left-Middle**: Pool powers panel (~150px width) - scrollable, 4 pool selectors + ancillary
  - **Center-Right**: pnlGFXFlow (main build display) - starts at x:481, y:80

### Top Menu Bar (MenuBar)

- **Type**: MenuStrip (Windows Forms)
- **Height**: 24px
- **Location**: Docked to top (0, 0)
- **Menus**:
  - **File**: New, Open, Save, Save As, Export, Print, Quit
  - **Options**: Change Database, Configuration, Advanced
  - **Share**: View Shared Builds, Share Menu
  - **Slots/Enhancements**: Set IO levels, Set enhancement types, Clear/Flip slots
  - **View**: Column selector (2-6 columns), Display options (IO levels, SO levels, etc.)
  - **Window**: Totals, Sets, Graphs, Data, Recipe Viewer, Set Find, Rotation Helper
  - **Help**: Help, Patch Notes, Support, About, Ko-fi, Patreon, GitHub

### Top Panel/Control Area (topPanel)

- **Type**: Panel (docked)
- **Height**: 53px
- **Location**: Below MenuBar, docked top (0, 24)
- **Width**: Full window width (1180px initial)
- **Controls** (ImageButtonEx components):
  - `lblCharacter` - Character name/level display label
  - `ibTeamEx` - Team management button
  - `ibAlignmentEx` - Hero/Villain alignment toggle
  - `ibTempPowersEx` - Temporary powers button
  - `ibAccoladesEx` - Accolades button
  - `ibIncarnatePowersEx` - Incarnate powers button
  - `ibPrestigePowersEx` - Prestige powers button
  - `ibPvXEx` - PvP/PvE mode toggle
  - `ibRecipeEx` - Recipe viewer button
  - `ibPopupEx` - Info popup toggle button
  - `ibSlotInfoEx` - Slot info display button
  - `ibSetsEx` - Set viewer button
  - `ibSlotLevelsEx` - Slot level display toggle
  - `ibTotalsEx` - Totals window toggle
  - `ibModeEx` - Build mode selector
  - `ibDynMode` - Dynamic mode toggle

- **Layout**: Horizontal row of icon buttons (ImageButtonEx controls)
- **Styling**: Dark background, icon buttons with tooltips

### Left Side Panel (Character Creation Controls)

**Location**: Left side of form, starting at (16, 82)

**Controls**:
1. **Name Input** (txtName)
   - Location: (94, 82), Size: (144, 20)
   - TextBox for character name

2. **Archetype Dropdown** (cbAT)
   - Location: (94, 108), Size: (144, 23)
   - ComboBox with custom draw, max 15 items
   - Label: "Archetype" 

3. **Origin Dropdown** (cbOrigin)
   - Location: (94, 133), Size: (144, 23)
   - ComboBox with custom draw

4. **Primary Powerset** (cbPrimary + llPrimary)
   - Dropdown: (16, 182), Size: (144, 22)
   - Power list (SkList): Shows available primary powers

5. **Secondary Powerset** (cbSecondary + llSecondary)
   - Dropdown: (168, 182), Size: (144, 22)
   - Power list (SkList): Shows available secondary powers

### Pool Powers Panel (poolsPanel)

- **Type**: ScrollPanelEx (custom scrollable panel)
- **Location**: Below primary/secondary, left side
- **Contains**: 4 pool power selectors + ancillary/epic pool
- **Controls**:
  - `cbPool0` - Pool 1 dropdown (0, 21 relative), Size: (142, 22)
  - `cbPool1` - Pool 2 dropdown (0, 133 relative)
  - `cbPool2` - Pool 3 dropdown (0, 241 relative)
  - `cbPool3` - Pool 4 dropdown (0, 349 relative)
  - `cbAncillary` - Ancillary/Epic pool (0, 457 relative)
- **Each pool has**:
  - Label (e.g., "Pool 1", "Pool 2")
  - Dropdown selector
  - Power list (SkList) showing available powers from that pool
- **Scrollable**: Vertical scroll for long power lists

### Main Content Area (Build Display)

**Container: pnlGFXFlow**
- **Type**: FlowLayoutPanel
- **Location**: (481, 80) - right of power selection area
- **Size**: (850, 891) initial
- **Properties**:
  - AutoScroll: true
  - HorizontalScroll: disabled/hidden
  - VerticalScroll: enabled/visible
  - Anchor: Left | Top

**Inner Panel: pnlGFX**
- **Type**: PanelGfx (custom control, inherits from PictureBox-like control)
- **Location**: (3, 3) relative to pnlGFXFlow
- **Size**: (838, 885) initial
- **Purpose**: Canvas for drawing power grid
- **Events**: Handles drag/drop, mouse clicks, double-clicks for power interaction

**Drawing Logic (ClsDrawX.cs)**:
- Managed by `ClsDrawX` class (drawing controller)
- **Constants**:
  - `PaddingX = 15` - Horizontal space between power slots
  - `PaddingY = 25` - Vertical space between power slots
  - `OffsetY = 23` - Vertical offset for enhancement slots
  - `OffsetX = 30` - Horizontal offset for enhancement slots
  - `VcPowers = 24` - Maximum powers per column
- **Column System**:
  - `_vcCols` - Current column count (2-6)
  - `_vcRowsPowers` - Rows per column (24)
  - `ColumnsPowersLayout` - Dictionary mapping power index to position

### Column Layout System

**Configuration**:
- Stored in: `MidsContext.Config.Columns` (persisted)
- Default: 3 columns
- Range: 2-6 columns
- Also supports: `ColumnStackingMode` enum (None, Horizontal, Vertical)

**User Control**: View Menu
- `tsView2Col` - 2 columns
- `tsView3Col` - 3 columns  
- `tsView4Col` - 4 columns
- `tsView5Col` - 5 columns
- `tsView6Col` - 6 columns
- `tsView3ColH` - 3 columns horizontal stacking
- `tsView3ColV` - 3 columns vertical stacking

**Implementation** (`SetColumns` method in frmMain.cs):
```csharp
private void SetColumns(int columns, Enums.eColumnStacking stackingMode = Enums.eColumnStacking.None)
{
    MidsContext.Config.Columns = columns;
    MidsContext.Config.ColumnStackingMode = stackingMode;
    
    drawing.Columns = columns;
    drawing.ColumnStackingMode = stackingMode;
    
    drawing.GetPowersLayout(); // Recalculate power positions
    // ... resize window, redraw ...
}
```

**Column Behavior**:
- Powers flow top-to-bottom within each column
- Level progression: Levels 1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 35, 38, 41, 44, 47, 49 (23 levels)
- Each level slot can have 1 power
- Powers can have 1-6 enhancement slots
- Empty slots show level numbers (e.g., "(1)", "(10)", "(22)")

## Side Panels

MidsReborn does not have traditional collapsible side panels in the main window. Instead:

### "Side" Content Strategy

**Left Area** (always visible):
- Character creation controls (Name, AT, Origin)
- Primary/Secondary powerset selection
- Pool powers panel (scrollable)
- These are fixed controls, not a collapsible panel

**Right Area** (main build display):
- pnlGFXFlow - always visible
- Takes up majority of window width
- Scrolls vertically for long builds

**Separate Floating Windows** (Window menu):
- **Totals Window** (`frmTotals`) - Shows defense, resistance, HP, endurance, etc.
  - Trigger: View > Totals (or `ibTotalsEx` button)
  - Can be "anchored" (integrated into main window) or floating
  
- **Set Viewer Window** (`frmSetViewer`) - Shows active set bonuses
  - Trigger: Window > Sets (or `ibSetsEx` button)
  - Lists slotted sets and their bonuses
  
- **Data Window** (`frmData`) - Detailed power/enhancement info
  - Trigger: Window > Data
  - Shows detailed stats for selected power
  
- **Recipe Viewer** (`frmRecipeViewer`) - Crafting recipes
  - Trigger: Window > Recipe Viewer (or `ibRecipeEx` button)

**Design Note**: MidsReborn uses separate windows for secondary info (totals, sets) rather than embedding them in the main layout. For web, we could:
- Keep them as separate windows (modal dialogs or floating panels)
- OR embed them as collapsible side panels (more web-native)
- Recommendation: Start with collapsible panels for mobile-friendliness, add "pop out" feature later

## Feature Requirements

### MUST-HAVE Features

1. **Main Build Layout**
   - **Description**: Central area displaying selected powers in a grid layout with configurable columns
   - **MidsReborn Implementation**: FlowLayoutPanel (pnlGFXFlow) containing PanelGfx (pnlGFX) with custom drawing via ClsDrawX
   - **Web Equivalent**: CSS Grid with dynamic column count (`grid-template-columns: repeat(var(--column-count), minmax(0, 1fr))`)
   - **Behavior**: 
     - Powers arranged in columns, flow top-to-bottom
     - Each column shows level slots (1, 2, 4, 6, 8, ..., 49)
     - Empty slots display level number
     - Filled slots display power icon + name + enhancement slots

2. **Top Control Panel**
   - **Description**: Fixed header with character info display and utility buttons
   - **MidsReborn Implementation**: Panel docked to top (53px height) with ImageButtonEx controls in horizontal layout
   - **Web Equivalent**: Fixed header (`position: sticky; top: 0;`) with flex layout for buttons
   - **Controls to Include** (Epic 1.3 - placeholders only):
     - Character name/level display
     - Mode toggles (Hero/Villain alignment)
     - Window triggers (Totals, Sets, etc.) - buttons for future epics
   - **Styling**: Dark background, icon buttons with hover states

3. **Column Layout Selector**
   - **Description**: UI control to switch between 2-6 column layouts
   - **MidsReborn Implementation**: View menu with checkable items (tsView2Col through tsView6Col), only one checked at a time
   - **Web Equivalent**: 
     - Option 1: Button group (shadcn/ui ToggleGroup) with 2, 3, 4, 5, 6 options
     - Option 2: Dropdown selector (less visible but cleaner)
   - **Recommendation**: Button group in top panel (more discoverable)
   - **Behavior**: Click to change column count, layout reflows immediately

4. **Responsive Layout Adaptation**
   - **Description**: Adapt column count and layout for smaller screens
   - **MidsReborn Implementation**: None (desktop-only, fixed window size)
   - **Web Equivalent**: CSS breakpoints with automatic column reduction
   - **Breakpoints**:
     - Mobile (<640px): Force 1 column, stack all controls vertically
     - Tablet (640-1024px): Max 3 columns, collapsible sidebar
     - Desktop (1024-1920px): Full 2-6 column control
     - Large (>1920px): Full 2-6 column control
   - **Behavior**:
     - User's column preference respected within breakpoint limits
     - E.g., user selects 5 columns but on tablet it caps at 3

5. **Routing Structure**
   - **Description**: Next.js pages for home, builder, and shared build viewer
   - **MidsReborn Implementation**: Single window application, no routing
   - **Web Equivalent**: Next.js App Router pages
   - **Routes**:
     - `/` - Home/landing page with "Create Build" button
     - `/builder` - Main build editor (client-side interactive)
     - `/build/[id]` - Shared build viewer (SSR for rich previews)

### SHOULD-HAVE Features

1. **Collapsible Left Sidebar**
   - **Description**: Left power selection panel can collapse to icon-only mode
   - **MidsReborn Implementation**: Always visible, no collapse
   - **Web Enhancement**: Add collapse button to save horizontal space
   - **Behavior**: Collapse to icons only, expand on hover or click

2. **Top Panel Auto-Hide**
   - **Description**: Top control panel hides on scroll down, shows on scroll up
   - **MidsReborn Implementation**: Always visible
   - **Web Enhancement**: Hide on scroll down (common mobile pattern)
   - **Behavior**: Smooth slide up/down animation

3. **Keyboard Shortcuts for Column Count**
   - **Description**: Keyboard shortcuts to quickly change column layout
   - **MidsReborn Implementation**: None (must use View menu)
   - **Web Enhancement**: Add keyboard shortcuts (e.g., Cmd/Ctrl+1-6)

4. **Layout Preset Saving**
   - **Description**: Save custom layout presets (column count + panel visibility)
   - **MidsReborn Implementation**: Only saves last column count
   - **Web Enhancement**: Allow naming and saving multiple layout presets
   - **Storage**: localStorage or user account preferences

### COULD-SKIP Features

1. **3-Column Stacking Modes**
   - **Description**: Special horizontal/vertical stacking modes for 3 columns
   - **MidsReborn Implementation**: `tsView3ColH` and `tsView3ColV` menu items, `ColumnStackingMode` enum
   - **Web Decision**: Skip for v1, add if users request
   - **Rationale**: Rarely used feature, adds complexity

2. **Floating/Draggable Panels**
   - **Description**: Totals and Set panels can be detached and dragged around
   - **MidsReborn Implementation**: Separate floating windows with window controls
   - **Web Decision**: Start with modal dialogs or fixed side panels
   - **Future**: Add "pop out" to separate browser window

3. **Custom Panel Sizing**
   - **Description**: Resize panels by dragging borders
   - **MidsReborn Implementation**: Resizable floating windows
   - **Web Decision**: Fixed sizes for v1, add resize handles in v2

## Layout State Management

### UI Store (Zustand) Requirements

From Epic 1.2, we already have `uiStore` created. We need to extend it with:

```typescript
interface UIStore {
  // Existing from Epic 1.2
  theme: 'light' | 'dark';
  
  // NEW for Epic 1.3
  layout: {
    columnCount: number;          // 2-6, default 3
    sidebarCollapsed: boolean;    // Left sidebar collapsed state
    topPanelVisible: boolean;     // Top panel visibility (for auto-hide)
    
    // Panel visibility toggles (for future epics)
    totalsVisible: boolean;       // Show totals panel
    setsVisible: boolean;         // Show sets panel
    dataVisible: boolean;         // Show data panel
  };
  
  // Actions
  setColumnCount: (count: number) => void;
  toggleSidebar: () => void;
  toggleTopPanel: () => void;
  toggleTotalsPanel: () => void;
  toggleSetsPanel: () => void;
  toggleDataPanel: () => void;
  
  // Responsive helpers
  getEffectiveColumnCount: (screenWidth: number) => number;
}
```

### Persistence

- **Storage**: localStorage via Zustand persist middleware
- **Key**: `mids-hero-ui-layout`
- **Persisted Fields**:
  - `columnCount` - User's preferred column count
  - `sidebarCollapsed` - Sidebar state
  - `totalsVisible`, `setsVisible`, `dataVisible` - Panel visibility
- **Not Persisted**:
  - `topPanelVisible` - Always starts visible

### Default Values

```typescript
const defaultLayout = {
  columnCount: 3,
  sidebarCollapsed: false,
  topPanelVisible: true,
  totalsVisible: false,
  setsVisible: false,
  dataVisible: false,
};
```

### Responsive Column Logic

```typescript
function getEffectiveColumnCount(
  userColumnCount: number, 
  screenWidth: number
): number {
  if (screenWidth < 640) {
    // Mobile: force 1 column
    return 1;
  } else if (screenWidth < 1024) {
    // Tablet: max 3 columns
    return Math.min(userColumnCount, 3);
  } else {
    // Desktop: respect user preference
    return userColumnCount;
  }
}
```

## Web Component Mapping

| MidsReborn Pattern | Web Equivalent | Implementation |
|--------------------|----------------|----------------|
| **frmMain** (Form) | Next.js page | `app/builder/page.tsx` |
| **MenuBar** (MenuStrip) | Top navigation | `components/layout/TopNav.tsx` with dropdown menus |
| **topPanel** (Panel) | Fixed header | `components/layout/TopPanel.tsx` with flex layout |
| **ImageButtonEx** | Icon button | shadcn/ui Button with icon, or custom IconButton component |
| **pnlGFXFlow** (FlowLayoutPanel) | Scrollable container | `<div className="overflow-y-auto">` |
| **pnlGFX** (PanelGfx) | Grid container | `<div className="grid grid-cols-{n}">` |
| **ClsDrawX** drawing | React components | Individual PowerCard components in grid |
| **SkList** (power list) | Scrollable list | `<ScrollArea>` with list items |
| **ComboBox** (dropdown) | Select component | shadcn/ui Select |
| **Floating windows** | Modal dialogs or side panels | shadcn/ui Dialog or Sheet |
| **Docking** (DockStyle.Top) | Sticky positioning | `position: sticky; top: 0;` |
| **Panel** | Div with Tailwind | `<div className="bg-background border rounded-md p-4">` |

## Routing Structure

### Pages Needed

1. **Home Page** (`app/page.tsx`)
   - **Purpose**: Landing page and entry point
   - **Layout**: Simple centered layout
   - **Content**:
     - Hero section: "Build Your City of Heroes Character"
     - "Create New Build" button (links to `/builder`)
     - Recent builds list (future: from localStorage or account)
     - Link to view shared builds
   - **Rendering**: Static (SSG)

2. **Builder Page** (`app/builder/page.tsx`)
   - **Purpose**: Main build editor - interactive character builder
   - **Layout**: Full BuildLayout with TopPanel, Sidebar, MainBuildGrid
   - **Content**:
     - Character creation form (Epic 2)
     - Power selection interface (Epic 3)
     - Build display grid (Epic 1.3 - placeholder)
   - **Rendering**: Client-side only (`'use client'`)
   - **State**: Uses characterStore and uiStore
   - **Route**: `/builder`

3. **Build Viewer Page** (`app/build/[id]/page.tsx`)
   - **Purpose**: Shared build display for viewing others' builds
   - **Layout**: Read-only version of BuildLayout
   - **Content**:
     - Build data fetched from API
     - Character info display
     - Power grid (non-interactive)
     - Export/Download buttons
   - **Rendering**: Server-side (SSR) for rich preview cards
   - **Metadata**: OpenGraph and Twitter Card tags for link previews
   - **Route**: `/build/abc123xyz`
   - **Features**:
     - SEO-friendly title: "Magic Blaster - City of Heroes Build"
     - Meta description with AT, powersets, level
     - Open Graph image: Build screenshot (generated server-side)

### Navigation Flow

```
Home (/)
  ├─ "Create Build" button
  │   └─→ Builder (/builder)
  │       └─ "Share" button
  │           └─→ Build Viewer (/build/[id])
  │
  └─ "View Shared Builds" link
      └─→ Browse Builds (/builds) - future epic
          └─→ Build Viewer (/build/[id])
```

### URL Structure

- `/` - Home
- `/builder` - Build editor (no ID = new build)
- `/builder?build=local-123` - Resume local build from localStorage
- `/builder?fork=abc123` - Fork/copy a shared build
- `/build/abc123` - View shared build
- `/builds` - Browse public builds (future)
- `/builds?search=blaster` - Search builds (future)

## Screenshot Analysis

### Available Screenshots

Location: `/home/user/mids-hero-web/shared/user/midsreborn-screenshots`

1. **mids-new-build.png** (218 KB)
   - **Shows**: Full main window with new Magic Blaster build
   - **Layout Elements Visible**:
     - Top menu bar (File, Options, Build Sharing, etc.)
     - Top panel with icon buttons (Team Members, Hero, PvP, etc.)
     - Left sidebar: Name field, Archetype dropdown (Blaster selected), Origin (Magic)
     - Power selection: Primary (Archery dropdown), Secondary (Atomic Manipulation)
     - Pool selectors: Pool 1 (Concealment), Pool 2 (Experimentation), Pool 3 (Fighting), Pool 4 (Flight), Ancillary (Arsenal Mastery)
     - Main build grid: 4 columns visible
     - Level slots numbered: (1), (10), (22), (35) in columns
     - Left panel shows power lists for each pool
     - Bottom-left: "INFO", "EFFECTS", "TOTALS", "ENHANCE" tabs with power description
   - **Column Configuration**: 4 columns
   - **Relevant to**: BuildLayout, TopPanel, Sidebar, MainBuildGrid
   - **Notes**: 
     - Clear view of full layout structure
     - Shows empty build state with all slots visible
     - Good reference for spacing and proportions
     - Shows how pools are organized vertically on left
     - Data view panel at bottom-left (power info display)

2. **power-enh.png** (277 KB)
   - **Shows**: Full build with powers selected and enhancements slotted
   - **Layout Elements Visible**:
     - 4-column layout with multiple powers filled
     - Power cards show: Power icon, name, level, enhancement slots (filled circles)
     - One power ("Rain of Arrows" at level 26) is selected/highlighted
     - Enhancement info popup on right showing:
       - "Detonation: Damage/Endurance" enhancement details
       - Set information ("Detonation (1/6)")
       - Set bonuses list (2-piece, 3-piece, etc.)
     - Left sidebar with power selections
     - Bottom-left: Active power info with "Active Slotting" showing 6 enhancement slots
   - **Column Configuration**: 4 columns
   - **Relevant to**: PowerCard component, EnhancementSlot, InfoPopup
   - **Notes**:
     - Shows filled state with enhancements
     - Enhancement slots shown as colored circles/icons
     - Popup shows detailed enhancement and set bonus info
     - Good reference for power card design with slots

3. **build-active-sets-bonuses.png** (54 KB)
   - **Shows**: Separate "Active Sets & Bonuses" floating window
   - **Layout Elements Visible**:
     - Window title: "Active Sets & Bonuses"
     - Left panel: "Applied Bonus Effects" (list of set bonuses)
     - Right panel: "Effect Breakdown" (empty in this screenshot)
     - Bottom section: Table with columns "Set", "Power", "Slots"
     - One row shown: "Detonation" set, "Rain of Arrows" power, "1" slot
     - Expandable details showing "Detonation (20-50):" with set bonus percentages
     - Buttons: "FX Summary", "Keep On Top", "<< Shrink", "Close"
   - **Relevant to**: SetBonusPanel, floating window design
   - **Notes**:
     - This is a separate window, not embedded in main layout
     - For web: could be modal dialog, sheet panel, or floating panel
     - Shows set bonus breakdown UI

4. **view-total-window.png** (60 KB)
   - **Shows**: Separate "Totals for Self" floating window
   - **Layout Elements Visible**:
     - Window title: "Totals for Self"
     - Top tabs: Color-coded bars (red, orange, blue, etc.) - likely tab selector
     - **Defense** section: List of damage types (Smashing, Lethal, Fire, Cold, etc.) all showing 0%
     - **Resistance** section: Same damage types, all 0%
     - **Health** section: Regeneration 140%, Max HP 1205 with bar graph
     - **Endurance** section: End Rec 2.08/s, End Use 0/s, Max End 100 with bar graphs
     - Buttons: "Keep", "Close"
   - **Relevant to**: TotalsPanel/TotalsWindow component
   - **Notes**:
     - Floating window, not embedded
     - Clean display of character stats
     - Color-coded progress bars for visual feedback
     - Separate sections for Defense, Resistance, Health, Endurance

5. **total-screen-1.png** (33 KB)
   - **Shows**: Embedded totals display (bottom-left area of main window)
   - **Layout Elements Visible**:
     - Tabs: "F" (selected), "Cumulative Totals (For Self)"
     - Green header: "Cumulative Totals (For Self)"
     - **Defense**: Listed damage types (Smashing 0%, Fire 0%, etc.)
     - **Resistance**: Listed damage types
     - **Misc Effects**: Recovery 100%, Regen 100%, +EndRdx 0%, EndDrain 0/s, +Recharge 0%
     - Text: "Click the 'View Totals' button for more."
   - **Relevant to**: Inline totals display (alternative to floating window)
   - **Notes**:
     - This is the "DataView" panel (dvAnchored) at bottom-left of main window
     - Shows condensed totals view
     - Alternative to floating totals window
     - Tabs suggest multiple views (F = ???, likely "Full" or "Fast")

6. **pool-desc-mouse-over.png** (250 KB)
   - **Shows**: Mouse hover tooltip over pool power
   - **Relevant to**: Tooltip component (not layout)
   - **Notes**: Useful for later epics (power interaction)

7. **power-desc-mouse-over.png** (245 KB)
   - **Shows**: Mouse hover tooltip over primary power
   - **Relevant to**: Tooltip component (not layout)

8. **power-enh-slot-pick.png** (49 KB)
   - **Shows**: Enhancement picker dialog (I9Picker)
   - **Relevant to**: Enhancement selection (Epic 3), not layout

### Key Layout Insights from Screenshots

**Column Layout**:
- 4-column layout appears to be most common in screenshots
- Powers arranged in vertical columns
- Level numbers shown in empty slots: (1), (10), (22), (35), etc.
- Even spacing between columns and rows

**Left Sidebar**:
- ~250px width (estimated from screenshots)
- Contains: Name, AT, Origin, Primary, Secondary
- Pool selectors stacked vertically below
- Each pool has dropdown + power list
- Power lists show power names in colored text (availability indicators)

**Top Panel**:
- ~53px height (from code)
- Horizontal row of icon buttons
- Labels/tooltips on hover
- Dark background with light icons

**Main Build Grid**:
- Takes majority of horizontal space
- Scrollable vertically (long builds)
- Powers displayed as cards: icon + name + slots
- Enhancement slots shown as circles/icons below power

**Bottom-Left Data View** (dvAnchored):
- ~300x400px panel (from code)
- Shows: Selected power info, tabs for INFO/EFFECTS/TOTALS/ENHANCE
- Can be resized and floated (optional)

**Floating Windows**:
- Totals and Set Bonuses are separate windows
- Can be "kept on top" or anchored to main window
- Have standard window controls (close, minimize, etc.)

### Additional Screenshots Recommended

1. **Different Column Counts**
   - Filenames: `midsreborn-2-columns.png`, `midsreborn-3-columns.png`, `midsreborn-5-columns.png`, `midsreborn-6-columns.png`
   - Should show: How layout changes with different column counts
   - Needed for: Understanding column width calculations and responsive breakpoints
   - **Can be captured**: Use View menu to switch column counts, take screenshots

2. **View Menu Expanded**
   - Filename: `midsreborn-view-menu.png`
   - Should show: View menu with column options visible (2 Col, 3 Col, 4 Col, etc.)
   - Needed for: Confirming column selector UI pattern
   - **Can be captured**: Open View menu, screenshot

3. **Small Window Size**
   - Filename: `midsreborn-small-window.png`
   - Should show: How MidsReborn behaves when window is resized smaller
   - Needed for: Understanding minimum dimensions and scroll behavior
   - **Can be captured**: Resize window to ~800x600, screenshot

4. **Full Build (Level 50)**
   - Filename: `midsreborn-full-build.png`
   - Should show: Completed level 50 build with all powers and enhancements
   - Needed for: Understanding visual density and scroll extent
   - **Can be captured**: Create/load sample level 50 build

## Implementation Notes

### Key Behaviors to Replicate

1. **Column Layout Flexibility**
   - User can adjust column count (2-6) dynamically
   - Powers reflow automatically when column count changes
   - Empty slots maintain visual structure (don't collapse)
   - Vertical scroll for long builds, never horizontal scroll

2. **Top Panel Always Accessible**
   - Top panel (character info and controls) always visible at top
   - Does not scroll with build content
   - Fixed position or sticky positioning

3. **Responsive Adaptation** (Web Enhancement)
   - Mobile (<640px): Force 1 column, stack sidebar controls vertically
   - Tablet (640-1024px): Max 3 columns, sidebar may collapse
   - Desktop (1024+px): Full 2-6 column flexibility
   - User's column preference respected within breakpoint limits

4. **Build Grid Scrolling**
   - Only the build grid area scrolls vertically
   - Sidebar and top panel remain fixed
   - Smooth scrolling behavior

5. **Empty State**
   - Empty build shows level slot numbers in grid
   - Level progression: 1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 35, 38, 41, 44, 47, 49
   - 23 total level slots
   - Slots are clickable to open power selection (future epic)

### UX Improvements for Web

1. **Fixed Top Bar with Smooth Scroll**
   - Unlike Windows Forms, use `position: sticky` for top panel
   - Stays visible while scrolling build grid
   - Smooth CSS transitions for hover effects

2. **Animated Column Count Changes**
   - Use CSS transitions for smooth reflow when changing column count
   - Grid items animate to new positions
   - Duration: ~300ms for professional feel

3. **Keyboard Shortcuts**
   - `Ctrl/Cmd + 1-6`: Change column count
   - `Ctrl/Cmd + Z`: Undo (from Epic 1.2)
   - `Ctrl/Cmd + Shift + Z`: Redo
   - `Ctrl/Cmd + S`: Save build (future)
   - `Escape`: Close dialogs/panels

4. **Touch Support**
   - Touch-friendly button sizes (min 44x44px)
   - Swipe gestures for column selector (mobile)
   - Tap to select powers (future epic)

5. **Dark Mode**
   - Leverage web-native dark mode support
   - MidsReborn uses dark theme by default
   - Theme toggle in settings (already in uiStore from Epic 1.2)

6. **Loading States**
   - Skeleton screens while loading build data
   - Smooth fade-in for power cards
   - Progress indicators for API calls

### CSS Grid Layout Approach

**Basic Grid Structure**:

```css
.build-grid {
  display: grid;
  grid-template-columns: repeat(var(--column-count), minmax(0, 1fr));
  gap: 1rem; /* 16px gap between columns and rows */
  padding: 1rem;
  overflow-y: auto;
  max-height: calc(100vh - 150px); /* Account for header */
}
```

**Dynamic Column Count**:

```tsx
// BuildLayout.tsx
import { useUIStore } from '@/stores/uiStore';

export function BuildLayout() {
  const { layout } = useUIStore();
  const columnCount = layout.columnCount;
  
  return (
    <div 
      className="build-grid"
      style={{ '--column-count': columnCount } as React.CSSProperties}
    >
      {/* Power cards */}
    </div>
  );
}
```

**Responsive Breakpoints**:

```css
/* Mobile: Force 1 column */
@media (max-width: 640px) {
  .build-grid {
    --column-count: 1 !important;
  }
}

/* Tablet: Max 3 columns */
@media (min-width: 641px) and (max-width: 1024px) {
  .build-grid {
    --column-count: min(var(--user-column-count), 3);
  }
}

/* Desktop: Full control */
@media (min-width: 1025px) {
  .build-grid {
    --column-count: var(--user-column-count);
  }
}
```

**Alternative: Tailwind Approach**:

```tsx
// Dynamic column classes
const columnClasses = {
  1: 'grid-cols-1',
  2: 'grid-cols-2',
  3: 'grid-cols-3',
  4: 'grid-cols-4',
  5: 'grid-cols-5',
  6: 'grid-cols-6',
};

<div className={`grid ${columnClasses[columnCount]} gap-4`}>
  {/* Powers */}
</div>
```

**Note**: Tailwind approach requires JIT mode or safelist for dynamic classes.

### Layout Component Structure

```
app/
├── builder/
│   └── page.tsx          # Main builder page
│       └── <BuildLayout>
│           ├── <TopPanel>
│           │   ├── <CharacterInfoDisplay>
│           │   └── <ControlButtons>
│           ├── <SidePanel>
│           │   ├── <CharacterForm>
│           │   └── <PowerSelection>
│           └── <MainBuildGrid>
│               └── <PowerCard>[] (map)
├── build/
│   └── [id]/
│       └── page.tsx      # Shared build viewer
└── page.tsx              # Home page

components/
├── layout/
│   ├── BuildLayout.tsx      # Main layout wrapper
│   ├── TopPanel.tsx         # Top control bar
│   ├── SidePanel.tsx        # Left sidebar (optional collapse)
│   └── MainBuildGrid.tsx    # Power grid container
└── ui/
    └── ColumnLayoutSelector.tsx  # 2-6 column toggle
```

## Warnings & Edge Cases

1. **Very Wide Screens (4K+)**
   - At 6 columns on 3840px width, each column is ~640px
   - Power cards may look too large/spaced out
   - Solution: Max column width ~250px, center grid if screen is very wide

2. **Very Narrow Screens (Mobile)**
   - Sidebar takes too much horizontal space
   - Solution: Collapse sidebar to slide-out drawer on mobile
   - Use hamburger menu to toggle sidebar

3. **Empty State Layout**
   - Layout should look reasonable with 0 powers selected
   - Show empty level slots with numbers
   - Visual indication that slots are clickable (future epic)

4. **Overflow Handling**
   - Long power lists in sidebar should scroll vertically
   - Build grid should scroll vertically for long builds
   - Never scroll horizontally (bad UX)

5. **Panel Collapsing**
   - When sidebar collapses, ensure build grid expands smoothly
   - Use CSS transitions for smooth width changes
   - Maintain column count proportions

6. **Column Count Changes**
   - When reducing columns (e.g., 6 to 2), powers must reflow
   - Maintain level order (1, 2, 4, 6, ...)
   - Animate position changes smoothly

7. **Browser Zoom**
   - Layout should remain usable at 50%-200% zoom
   - Use relative units (rem, %) not fixed px for key dimensions
   - Test at different zoom levels

8. **Tab Order / Accessibility**
   - Keyboard navigation should flow logically: menu → top panel → sidebar → build grid
   - Power cards must be keyboard-accessible (future epic)
   - Screen reader support for all interactive elements

## API Integration Points

### No New Backend Endpoints Needed for Epic 1.3

Epic 1.3 is layout/UI structure only. It uses existing infrastructure from Epic 1.2:
- `characterStore` (Zustand) for build state (placeholder data for now)
- `uiStore` (Zustand) for layout preferences (NEW: extend with layout fields)
- No new API calls required for basic layout

### Mock Data for Development

For Epic 1.3, use mock data to populate the layout:

```typescript
// mockData.ts
export const mockBuild = {
  character: {
    name: "Magic Blaster",
    archetype: "Blaster",
    origin: "Magic",
    level: 50,
  },
  powers: [
    { level: 1, name: "Snap Shot", primary: true, slots: [] },
    { level: 2, name: "Aimed Shot", primary: true, slots: [] },
    // ... more powers
  ],
};
```

### Future API Integration (Later Epics)

These endpoints will be added in future epics:

- **Epic 2**: `GET /api/archetypes`, `GET /api/powersets`, `GET /api/origins`
- **Epic 3**: `GET /api/powers/:id`, `GET /api/enhancements`, `POST /api/calculate`
- **Epic 6**: `POST /api/builds` (save build), `GET /api/builds/:id` (load build)

---

## Analysis Complete

This analysis provides the foundation for planning Epic 1.3 implementation. 

**Key Findings Summary**:

1. **Layout Structure**: MidsReborn uses a three-region layout: top panel (menu + controls), left sidebar (character creation + power selection), and center-right build grid
2. **Column System**: User-configurable 2-6 column layout for power grid, default 3 columns, persisted in config
3. **Top Control Panel**: 53px height panel with icon buttons for various functions (totals, sets, modes, etc.)
4. **Build Grid**: FlowLayoutPanel containing custom-drawn PanelGfx, uses ClsDrawX for rendering power cards with 15px horizontal / 25px vertical padding
5. **Separate Windows**: Totals and Set Bonuses are floating windows, not embedded panels
6. **Web Enhancements**: Responsive design (mobile/tablet/desktop), smooth animations, keyboard shortcuts, dark mode support

**Next Steps**:

1. Use `/superpowers:write-plan` to create detailed implementation plan for Epic 1.3
2. Plan should reference this analysis for layout structure and requirements
3. Focus on:
   - Next.js routing setup (`/`, `/builder`, `/build/[id]`)
   - BuildLayout component with TopPanel, SidePanel, MainBuildGrid
   - ColumnLayoutSelector component (2-6 column toggle)
   - UIStore extension with layout preferences
   - Responsive breakpoints (mobile/tablet/desktop)
   - CSS Grid implementation with dynamic column count

**Epic 1.3 Scope**:
- ✅ Layout shell and structure (empty state, placeholders)
- ✅ Column count selector and layout reflow
- ✅ Routing and navigation
- ✅ Responsive design
- ❌ Actual power selection (Epic 3)
- ❌ Enhancement slotting (Epic 3)
- ❌ Totals calculation (Epic 4)
- ❌ Set bonuses (Epic 5)

This epic establishes the visual structure and navigation framework. Future epics will add interactive functionality.

---

**Document Version**: 1.0
**Last Updated**: 2025-11-16
**Analysis Complete**: ✅
