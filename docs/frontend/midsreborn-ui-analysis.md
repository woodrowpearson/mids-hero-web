# MidsReborn UI/UX Analysis Report

**Created**: 2025-11-13
**Purpose**: Document MidsReborn UI structure, features, and patterns for Mids Hero Web frontend
**Source**: Comprehensive exploration of `/Users/w/code/mids-hero-web/external/dev/MidsReborn`

---

## Executive Summary

MidsReborn is a sophisticated Windows Forms desktop application (294KB main form) with a complex character building workflow. The UI centers around power selection, enhancement slotting, and real-time stat calculation visualization.

**Key Findings**:
- 15+ major Form windows, 10+ custom controls
- 3 build sharing mechanisms (file, URL, API)
- Real-time stat calculation with observer pattern
- Information-dense UI with 100+ stat displays
- Highly customizable layout (2-6 columns)

**For Mids Hero Web**: We can achieve feature parity with a cleaner, modern web UX while skipping 7 advanced features (Incarnates, boosters, attuned IOs, etc.).

---

## 1. MidsReborn UI Structure

### Main Application Windows

**Primary**:
- `frmMain.cs` (294KB) - Main application window
- `UIv2/MainForm.cs` - Alternative main form

**Key Dialogs**:
- `frmTotals.cs` - Build statistics (floating window)
- `frmSetViewer.cs` - Enhancement set viewer with bonuses
- `frmRecipeViewer.cs` - Recipe and crafting display

**SKIP (Per User Requirements)**:
- `frmIncarnate.cs` - Incarnate powers
- `frmDPSCalc.cs` - DPS calculator
- `frmRotationHelper.cs` - Power rotation recommendations

### Custom Controls

**Core UI Components**:
- `EnhPicker.cs` / `I9Picker.cs` - Enhancement selection (sophisticated)
- `PowerSelector.cs` - Power selection dialog
- `ctlMultiGraph.cs` - Multi-bar graph for stats
- `PowerControl.cs` - Individual power display
- `SkList` - Custom power list control

---

## 2. Feature Inventory

### MUST-HAVE Features (Core Functionality)

#### Character Creation
- Archetype Selection (14+ archetypes)
- Origin Selection (5 origins)
- Alignment Selection (Hero, Vigilante, Villain, Rogue)
- Character Name
- Primary/Secondary Powerset selection
- Pool Powers (4 slots)
- Ancillary/Epic Pool (1 slot)

#### Power Selection
- Level-based power picking (levels 1-50)
- Power lists (vertical scrollable)
- Power level display
- Power prerequisites (visual locking)
- Power respec capability
- Inherent powers (auto-granted)

#### Enhancement Slotting
- **Slot Assignment**: Up to 6 slots per power
- **Enhancement Types**:
  - Training/Dual/Single Origin (TO/DO/SO)
  - Invention Origin (IO) - generic and set
  - Special IOs (LotG, ATOs, etc.)
- **Enhancement Picker (I9Picker)**: Complex popup with:
  - Tabs: Normal, Set, Special
  - Grade selection (TO/DO/SO, IO levels 10-50)
  - Relative level (+3 to -3)
  - Visual grid of enhancements
  - Set filtering
  - Search functionality
- **Visual Slot Display**: Shows slotted enhancements
- **Set Bonus Tracking**: Real-time active set bonuses

#### Build Statistics Display

**Categories** (from `frmTotals.cs`):

1. **Defense**: Smashing, Lethal, Fire, Cold, Energy, Negative, Psionic, Toxic, Melee, Ranged, AoE
2. **Resistance**: All damage types
3. **HP & Endurance**: Regen %, Max HP, Absorb, Recovery/s, Usage/s, Max End
4. **Movement**: Run/Jump/Fly Speed, Jump Height
5. **Stealth & Perception**: Stealth (PvE/PvP), Perception radius
6. **Misc**: Haste (recharge%), ToHit%, Accuracy%, Damage%, End Reduction%, Threat
7. **Status Protection**: Hold, Stun, Sleep, Immob, KB, Repel, Confused, etc. (magnitudes)
8. **Status Resistance**: Same categories as protection (percentages)
9. **Debuff Resistance**: Defense, End, Recovery, Perception, ToHit, Recharge, Speed, Regen
10. **Elusivity** (PvP): All damage types

**Visualization**:
- Multi-bar graphs (CtlMultiGraph)
- Color-coded bars (soft-cap yellow, hard-cap red)
- Value labels on bars
- Hover for detailed info

#### Build Save/Load
- **File Formats**:
  - `.mxd` (legacy compressed)
  - `.mbd` (modern binary)
- Save As, Open dialogs
- Auto-save option
- File modified indicator

#### Build Sharing

**Method 1: API Sharing (Modern - RECOMMENDED)**
- Submit build to API server
- Returns:
  - Unique Build ID
  - Download URL (permalink)
  - Image URL (infographic)
  - Schema URL
  - Expiration date
- Discord-formatted markdown export
- Update existing builds by ID
- Expiring builds collection tracking

**Method 2: Build Data Chunk**
- Base64-encoded build data
- Copy to clipboard
- Import via paste
- Validates format

**Method 3: Forum Export**
- Formats: HTML, BBCode, Markdown
- Customizable color themes
- Optional sections (stats, bonuses)
- Generated using TagGenerator

**Method 4: Infographic**
- PNG image of build stats
- Two graphic variants
- Copy to clipboard
- Auto-generated with API share

---

### SHOULD-HAVE Features (Important but Can Defer)

- Power detail view (floating popup)
- Enhancement set viewer (detailed bonus breakdown)
- Recipe viewer (crafting requirements)
- Build comparison (side-by-side)
- Accolade/Temp powers
- UI customization (column layouts, themes)
- Visual enhancements (power icons, enhancement icons)

---

### SKIP Features (Per User Requirements)

- Alternate IO slotting (flipped builds)
- Enhancement boosters (+5 system)
- Attuned IOs (level-scaling)
- Level scaling (variable level builds)
- Incarnate powers (Alpha-Hybrid)
- Power rotation recommendations
- DPS calculator

---

## 3. Build Sharing Mechanism Analysis

### Current MidsReborn Implementation

**File-Based**:
- `.mxd` / `.mbd` binary formats
- Magic number: "MxD\x0C"
- Stores: Archetype, Origin, Powersets, Powers, Slots, Enhancements
- Version-tracked (current: 3.20)

**URL/Link-Based**:
- Legacy DataLink: Base64 in URL params (max 2048 chars)
- Build Data Chunk: Pure base64, copy/paste

**API-Based** (from `ShareGenerator.cs`):
```csharp
// Build Submission
POST /api/builds
{
  Name, Archetype, Description,
  Primary, Secondary,
  BuildData (compressed),
  ImageData (PNG)
}

// Returns
{
  Id, DownloadUrl, ImageUrl, SchemaUrl,
  ExpirationDate
}

// Discord Format
"### [BuildName] a [Primary]/[Secondary] [Archetype]
📥 [Grab The Build Here](download-url) - *(Link expires date)*
👁️ [Stat Preview Below](image-url)"
```

**Recommended for Mids Hero Web**:
- **Primary**: API-based sharing (permalink URLs)
- **Secondary**: Data chunk copy/paste (fallback)
- **Export**: Markdown/BBCode for forums
- **Infographic**: Auto-generated PNG

---

## 4. UI Layout Patterns

### Main Window Layout

**Top Panel**:
- Character name input
- Archetype dropdown
- Origin dropdown
- Icon button bar:
  - PvE/PvP mode toggle
  - Alignment selector
  - Slot levels
  - Accolades, Team, Recipes, Sets, Totals
  - Prestige, Temp Powers

**Power Selection Area**:
- Primary powerset selector + power list
- Secondary powerset selector + power list

**Pool Powers Panel** (scrollable):
- 4 pool power selectors + lists
- 1 ancillary/epic selector + list

**Central Display** (FlowLayoutPanel):
- 2-6 columns configurable
- Shows selected/slotted powers
- Each power displays:
  - Icon
  - Name
  - Level taken
  - Slots (visual indicators)
  - Slotted enhancements (icons/names)

**Menu Bar**:
- **File**: New, Open, Save, Import, Export, Share
- **Character**: Set IO levels, grades, relative levels, slot operations
- **View**: Column layout, display options
- **Window**: Set Viewer, Totals, Recipe Viewer, etc.
- **Options**: Configuration, database management
- **Help**: Help, updates, about

### Enhancement Picker Popup (I9Picker)

**Tabbed Interface**:
- **Normal Tab**: TO/DO/SO
- **Set Tab**: IO sets
- **Special Tab**: Unique IOs, ATOs

**Controls**:
- Enhancement type dropdown/list
- Grade selector (levels 10-50 for IOs)
- Relative level selector (Even, +1, +2, +3, -1, -2, -3)
- Grid of enhancement icons
- Selected enhancement highlight
- Close button

### Floating Totals Window

**Layout**:
- Tabbed or single-panel scrollable
- Multi-graph controls for each stat category
- Radio buttons for unit selection (speed)
- "Keep On Top" toggle
- Close button

**Stats Organized By**:
- Defense (typed + positional)
- Resistance (typed)
- HP & Endurance (regen, recovery, max)
- Movement (run, jump, fly)
- Stealth & Perception
- Misc (haste, tohit, accuracy, damage, etc.)
- Status Protection (mez magnitudes)
- Status Resistance (mez percentages)
- Debuff Resistance (capped percentages)
- Elusivity (PvP only)

---

## 5. Common UI Patterns

### WinForms → Web Mapping

| MidsReborn Control | Web Equivalent | Notes |
|-------------------|----------------|-------|
| ListView | TanStack Table | Sortable, filterable, column support |
| ListBox | Listbox (shadcn/ui) | Simple selectable lists |
| ComboBox | Select/Combobox (shadcn/ui) | Searchable dropdowns |
| SkList | Custom scrollable list | Vertical power lists |
| TabControl | Tabs (shadcn/ui) | Multi-tab interfaces |
| TreeView | Accordion or custom tree | Hierarchical data |
| RichTextBox | div with Tailwind typography | Formatted text |
| Panel | div with Tailwind | Layout containers |
| FlowLayoutPanel | div with flex flex-wrap | Auto-flowing cards |
| ImageButtonEx | Button with icon | Lucide React icons |
| ToolTip | Tooltip (shadcn/ui) | Hover info |
| MessageBox | Dialog/Alert Dialog | Modal confirmations |
| CtlMultiGraph | Custom SVG bars / Recharts | Stat visualizations |
| I9Picker | Custom Popover + Tabs + Grid | Enhancement picker |
| ctlPopUp | Popover (shadcn/ui) | Floating info |
| CheckBox | Checkbox (shadcn/ui) | Boolean toggles |
| RadioButton | Radio Group (shadcn/ui) | Exclusive choices |
| TextBox | Input (shadcn/ui) | Text entry |
| ProgressBar | Progress (shadcn/ui) | Loading states |

---

## 6. Data Flow Analysis

### How MidsReborn UI Gets Data

**Database Layer** (Static):
- `DatabaseAPI` class provides access to:
  - `Database.Power[]`
  - `Database.Powersets[]`
  - `Database.Enhancements[]`
  - `Database.EnhancementSets[]`
  - `Database.Recipes[]`
  - `Database.Archetype[]`
- Data loaded on startup from files
- Static access throughout app

**Character State** (Singleton):
- `MidsContext.Character` holds current character:
  - `Archetype`, `Origin`, `Alignment`, `Name`
  - `Powersets[]` (8 slots: Primary, Secondary, Inherent, 4 Pools, Ancillary)
  - `CurrentBuild.Powers` (List of PowerEntry)
  - `CurrentBuild.SetBonuses`
  - `Totals` (calculated aggregates)

**Update Flow Example**:
1. User selects archetype
2. Event fires → Updates `MidsContext.Character.Archetype`
3. Clears incompatible powersets
4. Rebuilds powerset dropdowns
5. Clears incompatible powers
6. **Recalculates stats**
7. **Refreshes all UI displays**

**Calculation Cascade**:
- Triggered by any build change
- Walks all PowerEntries
- Applies enhancement boosts
- Sums into character totals
- Applies set bonuses
- Calculates derived stats
- Updates `Character.Totals`
- Fires UI update events
- All open windows refresh

**Observer Pattern**:
- UI controls subscribe to character change events
- When character changes, all subscribed controls refresh
- No manual refresh calls needed

---

## 7. Web Architecture Recommendations

### State Management Strategy

**TanStack Query** (Server State):
```typescript
// Fetch database (powers, archetypes, enhancements)
const { data: database } = useQuery({
  queryKey: ['database'],
  queryFn: fetchDatabase,
  staleTime: Infinity, // Cache forever
});

// Fetch shared build
const { data: sharedBuild } = useQuery({
  queryKey: ['build', buildId],
  queryFn: () => fetchSharedBuild(buildId),
});

// Submit build share
const shareMutation = useMutation({
  mutationFn: submitBuild,
  onSuccess: (data) => {
    // data.downloadUrl, data.imageUrl, data.id
  },
});
```

**Zustand** (Client State):
```typescript
interface CharacterStore {
  character: Character;
  totals: CalculatedTotals;

  // Actions
  setArchetype: (archetype: Archetype) => void;
  setPowerset: (slot: number, powerset: Powerset) => void;
  addPower: (power: Power, level: number) => void;
  removePower: (index: number) => void;
  slotEnhancement: (powerIdx: number, slotIdx: number, enh: Enhancement) => void;

  // Derived
  recalculate: () => void; // Triggers calculation API call
}

// With undo/redo support
import { temporal } from 'zus tand/middleware';
const useCharacterStore = create(
  temporal<CharacterStore>((set) => ({ ... }))
);
// Access via: useCharacterStore.temporal.undo(), .redo()
```

**Calculation Flow**:
```typescript
// When user makes change:
1. Update Zustand store (optimistic)
2. Debounce recalculation (200ms)
3. Call FastAPI backend: POST /api/calculations/totals
4. Update totals in store
5. All components re-render automatically (React reactivity)
```

---

## 8. Screenshot Recommendations

To fully capture MidsReborn UI for visual reference, capture these screenshots:

1. **Main Window - Full UI Layout** - Complete window with character created, powers slotted
2. **Character Creation - Initial State** - Empty build, archetype dropdown open
3. **Power Selection Panel** - Primary/Secondary lists showing available/locked powers
4. **Enhancement Picker (I9Picker) - Set IOs Tab** - Popup with IO grid, selectors visible
5. **Enhancement Picker - Normal Tab** - TO/DO/SO tab
6. **Power with Slotted Enhancements** - Close-up of power showing 6 slotted IOs
7. **Totals Window (frmTotals)** - Floating window with Defense/Resistance/HP bars
8. **Set Viewer Window** - List of slotted sets with bonus breakdown
9. **Recipe Viewer Window** - Salvage requirements, shopping list
10. **Build Sharing - ShareMenu** - Dialog with tabs (Data Chunk, Forum, API, InfoGraphic)
11. **Menu Bar - File Menu** - Import/Export/Share submenu
12. **Pool Powers Panel** - Scrollable panel with 4 pools + ancillary
13. **Build with Sets Slotted** - Main display showing many powers with full IO sets
14. **Visual Indicators** - Power levels, slot levels, set membership indicators
15. **Stats Graphs** - Multi-bar graphs with cap indicators, color coding

**Capture Tips**:
- Use default Hero theme (blue)
- Example character: "Brute - Super Strength / Willpower"
- Slot common sets (Luck of the Gambler, Numina's, etc.)
- 1920x1080+ resolution
- Save as PNG
- Annotate key areas (optional)
- **Save to**: `/Users/w/code/mids-hero-web/shared/user/midsreborn-screenshots/`
- Use descriptive filenames: `midsreborn-main-window.png`, `midsreborn-i9picker-set-tab.png`, etc.

---

## Summary

### Key Takeaways

**MidsReborn Strengths**:
- Comprehensive feature set (30+ years of CoH knowledge)
- Real-time calculation engine (instant feedback)
- Rich data visualization (100+ stats displayed)
- Robust sharing system (files, URLs, API, images)
- Highly customizable UI

**For Mids Hero Web**:
- **Maintain**: Core workflow, stat displays, sharing system
- **Modernize**: UX/UI, responsive design, fast performance
- **Simplify**: Skip 7 advanced features (Incarnates, boosters, etc.)
- **Enhance**: Better visual aids, improved build sharing (permalinks)
- **Optimize**: API-first architecture, progressive disclosure

**Technical Alignment**:
- React components replace WinForms controls
- shadcn/ui provides modern primitives
- Tailwind for styling
- TanStack Query for data fetching
- Zustand for client state
- FastAPI backend handles all calculations (100% complete!)

**Next Steps**:
1. Create architecture document (tech stack, folder structure)
2. Create epic breakdown (stage-by-stage plan)
3. Start Epic 1.1 (Next.js setup + design system)

---

**Document Status**: ✅ Complete
**Source Analysis Date**: 2025-11-13
**MidsReborn Version**: Based on codebase snapshot (3.20)
