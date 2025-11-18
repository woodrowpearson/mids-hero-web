# MidsReborn UI Analysis: Epic 2.1 - Archetype & Origin Selection

**Created**: 2025-11-16
**Epic**: 2.1 - Archetype & Origin Selection
**MidsReborn Forms Analyzed**: 
- `external/dev/MidsReborn/MidsReborn/Forms/frmMain.cs`
- `external/dev/MidsReborn/MidsReborn/Forms/frmMain.Designer.cs`
- `external/dev/MidsReborn/MidsReborn/Core/Base/Data_Classes/Character.cs`
- `external/dev/MidsReborn/MidsReborn/Core/Base/Data_Classes/Archetype.cs`
- `external/dev/MidsReborn/MidsReborn/Core/Base/Data_Classes/Origin.cs`

## Executive Summary

Character creation in MidsReborn is handled through a compact top panel in the main window (frmMain) with inline controls for Name (TextBox), Archetype (ComboBox), and Origin (ComboBox). Alignment is managed via a toggle button (ibAlignmentEx) that cycles between Hero/Villain/Rogue/Vigilante states. The UI emphasizes simplicity with dropdowns displaying icons alongside text, immediate state updates to the Character object, and validation to ensure archetype/origin compatibility. For web translation, we'll use shadcn/ui Select components with search capability, Input for name, and Radio/Toggle for alignment, fetching data from `/api/archetypes` endpoint.

## MidsReborn UI Components

### Component 1: Main Window Character Creation Panel (frmMain)

- **File**: `external/dev/MidsReborn/MidsReborn/Forms/frmMain.cs` + `.Designer.cs`
- **Purpose**: Primary character creation interface visible at top of main window
- **Layout**: Horizontal panel layout (top-left of window) with stacked controls:
  - Row 1: `lblName` label + `txtName` TextBox (Location: 94, 82; Size: 144x20)
  - Row 2: `lblAT` label + `cbAT` ComboBox (Location: 94, 108; Size: 144x23)
  - Row 3: `lblOrigin` label + `cbOrigin` ComboBox (Location: 94, 133; Size: 144x23)
  - Toolbar buttons: `ibAlignmentEx` (alignment toggle button), `ibModeEx`, etc.
- **Data Displayed**:
  - **Character Name**: Plain text input, stored as `MidsContext.Character.Name`
  - **Archetype**: ComboBox showing archetype display names with icons (OwnerDrawn)
    - DisplayMember: "DisplayName"
    - ValueMember: "Idx"
    - MaxDropDownItems: 15
    - Data source: `DatabaseAPI.Database.Archetypes` (filtered for playable ATs)
  - **Origin**: ComboBox showing origin names with icons (OwnerDrawn)
    - Items: Array from selected archetype's `Origin[]` property
    - Data source: `cbAT.SelectedItem.Origin` (archetype's allowed origins)
    - Default origins: Magic, Mutation, Natural, Science, Technology
  - **Alignment**: Toggle button (not dropdown) cycling through states
    - States: Hero, Villain, Rogue, Vigilante
    - Visual indicator changes with alignment (hero blue, villain red colors throughout UI)
- **User Interactions**:
  - **Name Input**: 
    - `txtName.TextChanged` event → `MidsContext.Character.Name = txtName.Text`
    - Real-time update, no validation (any string accepted)
  - **Archetype Selection**:
    - `cbAT.SelectionChangeCommitted` event → `cbAT_SelectedIndexChanged()`
    - Updates `MidsContext.Character.Archetype`
    - Triggers `Reset()` if archetype changes (clears incompatible powersets)
    - Updates origin dropdown to show only compatible origins
    - Shows/hides locked indicator `lblATLocked` when build is locked
  - **Origin Selection**:
    - `cbOrigin.SelectionChangeCommitted` event → `cbOrigin_SelectedIndexChanged()`
    - Updates `MidsContext.Character.Origin` (integer index)
    - Updates I9 graphics engine: `I9Gfx.SetOrigin(cbOrigin.SelectedItem)`
  - **Alignment Toggle**:
    - `ibAlignmentEx.OnClick` event → cycles through alignment states
    - Updates `MidsContext.Character.Alignment` enum
    - Triggers `AlignmentChanged` event → UI theme updates (colors, icons)
  - **Validation**:
    - Archetype required before powerset selection
    - Origin limited to archetype's allowed origins
    - Changing archetype resets build if powersets were selected (with confirmation)

### Component 2: Data Models

#### Character.cs
- **File**: `external/dev/MidsReborn/MidsReborn/Core/Base/Data_Classes/Character.cs`
- **Properties**:
  - `Name: string` - Character name (no max length enforced)
  - `Archetype: Archetype?` - Selected archetype object
  - `Origin: int` - Index into archetype's Origin[] array (0-4 typically)
  - `Alignment: Enums.Alignment` - Enum with values: Hero, Villain, Rogue, Vigilante
- **Events**:
  - `AlignmentChanged: EventHandler<Enums.Alignment>` - Fired when alignment changes
- **Behavior**:
  - Setting Archetype auto-sets Alignment based on `archetype.Hero` property
  - Origin stored as integer index, not object reference

#### Archetype.cs
- **File**: `external/dev/MidsReborn/MidsReborn/Core/Base/Data_Classes/Archetype.cs`
- **Key Properties**:
  - `Idx: int` - Unique archetype ID
  - `DisplayName: string` - "Tanker", "Blaster", etc.
  - `ClassName: string` - Internal class name
  - `DescLong: string` - Full description
  - `DescShort: string` - Brief description
  - `Origin: string[]` - Array of allowed origin names (default: 5 origins)
  - `Primary: int[]` - Array of allowed primary powerset IDs
  - `Secondary: int[]` - Array of allowed secondary powerset IDs
  - `Ancillary: int[]` - Array of allowed ancillary powerset IDs
  - `ClassType: Enums.eClassType` - Hero, HeroEpic, Villain, VillainEpic
  - **Modifiers/Caps**:
    - `Hitpoints: int` - Base HP
    - `HPCap: float` - Max HP multiplier
    - `DamageCap: float` - Max damage buff cap (4.0 = 400%)
    - `ResCap: float` - Max resistance cap (0.9 = 90%)
    - `RechargeCap: float` - Max recharge speed cap
    - `RegenCap: float` - Max regeneration cap
    - `RecoveryCap: float` - Max recovery cap
    - `BaseRegen: float` - Base regeneration rate
    - `BaseRecovery: float` - Base endurance recovery
    - `BaseThreat: float` - Threat multiplier
    - `PerceptionCap: float` - Perception radius cap
  - `Playable: bool` - Whether archetype is selectable

#### Origin.cs
- **File**: `external/dev/MidsReborn/MidsReborn/Core/Base/Data_Classes/Origin.cs`
- **Properties**:
  - `Name: string` - Origin name (Magic, Natural, etc.)
  - `Grades: string[]` - Enhancement grade names per origin
    - Index 0: "Training"
    - Index 1: Dual-Origin name (e.g., "Science", "Magic")
    - Index 2: Single-Origin name
    - Index 3-6: "HO", "IO", "IO", "IO"
- **Global List**: `DatabaseAPI.Database.Origins: List<Origin>` (5 origins globally)
- **Usage**: Origin selection affects enhancement visuals/names but not core stats in modern CoH

### Component 3: Archetype ComboBox Behavior

- **File**: `frmMain.cs` lines 6993-7067
- **Initialization** (`UpdateControls()` method):
  ```csharp
  cbAT.BeginUpdate();
  cbAT.Clear();
  cbAT.AddRange(all); // All archetypes from database
  cbAT.EndUpdate();
  
  if (cbAT.SelectedItem == null)
      cbAT.SelectedItem = MidsContext.Character.Archetype;
  ```
- **Custom Drawing** (`cbAT_DrawItem` event):
  - Draws archetype icon (16x16) next to display name
  - Uses custom rendering for visual appeal
- **Locked State**:
  - When `MainModule.MidsController.Toon.Locked == true`:
    - `cbAT.Enabled = false`
    - `lblATLocked` overlay shows archetype name (prevents editing)
- **Data Flow**:
  1. User selects archetype from dropdown
  2. `cbAT_SelectedIndexChanged()` fires
  3. If archetype changed: `MidsContext.Character.Reset(archetype, origin)`
  4. Origin dropdown updates to show only compatible origins
  5. Powerset dropdowns update/clear based on new archetype

### Component 4: Origin ComboBox Behavior

- **File**: `frmMain.cs` lines 7023-7034
- **Initialization** (`UpdateControls()` method):
  ```csharp
  cbOrigin.BeginUpdate();
  cbOrigin.Clear();
  cbOrigin.AddRange(cbAT.SelectedItem.Origin); // Origins from selected archetype
  cbOrigin.EndUpdate();
  
  if (cbOrigin.SelectedIndex != MidsContext.Character.Origin)
      cbOrigin.SelectedIndex = MidsContext.Character.Origin < cbOrigin.Items.Count
          ? MidsContext.Character.Origin : 0;
  ```
- **Custom Drawing** (`cbOrigin_DrawItem` event):
  - Draws origin icon (16x16) next to origin name
  - Icon source: `I9Gfx.Origins` sprite sheet
- **Data Flow**:
  1. User selects origin from dropdown
  2. `cbOrigin_SelectedIndexChanged()` fires
  3. `MidsContext.Character.Origin = cbOrigin.SelectedIndex` (stores index)
  4. `I9Gfx.SetOrigin(cbOrigin.SelectedItem)` updates graphics
- **Dependency**: Origin dropdown contents depend on selected archetype's `Origin[]` array

### Component 5: Alignment Toggle Button

- **File**: `frmMain.cs` line 2545
- **Control**: `ibAlignmentEx` - ImageButtonEx (custom toggle button)
- **Behavior**:
  ```csharp
  ibAlignmentEx.OnClick(sender, e) {
      MidsContext.Character.Alignment = ibAlignmentEx.ToggleState switch
      {
          0 => Enums.Alignment.Hero,
          1 => Enums.Alignment.Villain,
          2 => Enums.Alignment.Vigilante,
          _ => Enums.Alignment.Rogue
      };
  }
  ```
- **Visual State**:
  - Line 7134: `ibAlignmentEx.ToggleState = MidsContext.Character.IsHero() ? 0 : 1`
  - Button icon changes based on alignment
  - UI theme changes (hero blue vs villain red) throughout application
- **Impact**: Alignment affects available powersets (hero vs villain archetypes/pools)

### Component 6: Inherent Powers Display

- **Location**: Not in character creation panel, displayed in separate area
- **Data Source**: `MidsContext.Character.Archetype.Inherent` powers
- **Display**: List of inherent powers (auto-granted at level 1)
- **Examples**: 
  - Tanker: "Gauntlet", "Bruising"
  - Scrapper: "Critical Hit"
  - Defender: "Vigilance"
  - Controller: "Containment"
  - Blaster: "Defiance"
- **Web Requirement**: Display inherent powers after archetype selection

## Feature Requirements

### MUST-HAVE Features

1. **Character Name Input**
   - **Description**: Text field for character name (no max length, any string accepted)
   - **MidsReborn Implementation**: `txtName` TextBox control, real-time updates to `MidsContext.Character.Name`
   - **Web Equivalent**: shadcn/ui Input component with label
   - **Validation**: None required (optional: max 50 characters for UX)
   - **API**: No API call needed (client-side only)

2. **Archetype Selector**
   - **Description**: Dropdown with all playable archetypes (Tanker, Scrapper, Defender, Controller, Blaster, Peacebringer, Warshade, Brute, Stalker, Mastermind, Dominator, Corruptor, Arachnos Soldier, Arachnos Widow, Sentinel)
   - **MidsReborn Implementation**: 
     - ComboBox with OwnerDraw for icons
     - Data from `DatabaseAPI.Database.Archetypes.Where(at => at.Playable)`
     - MaxDropDownItems: 15
   - **Web Equivalent**: 
     - shadcn/ui Select component with search capability
     - Display: Archetype icon + display name
     - Sorted by ClassType (Hero, Villain, HeroEpic, VillainEpic)
   - **API Endpoint**: `GET /api/archetypes?playable=true`
   - **Response Shape**:
     ```typescript
     {
       id: number;
       name: string;
       displayName: string;
       icon: string;
       descShort: string;
       descLong: string;
       classType: "Hero" | "Villain" | "HeroEpic" | "VillainEpic";
       hitPoints: number;
       hpCap: number;
       damageCap: number;
       resCap: number;
       // ... other caps/modifiers
     }[]
     ```
   - **Behavior**: 
     - Selection updates characterStore.archetype
     - Triggers origin dropdown update (filter to archetype's allowed origins)
     - Displays archetype description in tooltip or info panel
     - Warning if changing archetype after powersets selected

3. **Origin Selector**
   - **Description**: Dropdown with 5 origins (Magic, Natural, Science, Mutation, Technology)
   - **MidsReborn Implementation**: 
     - ComboBox with OwnerDraw for icons
     - Items from selected archetype's `Origin[]` array
     - Typically all 5 origins, but some archetypes may restrict (Kheldians, etc.)
   - **Web Equivalent**: 
     - shadcn/ui Select component
     - Display: Origin icon + name
     - Derived from selected archetype or global list
   - **API Endpoint**: Option A: Derived from archetype data (archetype.allowedOrigins)
   - **API Endpoint**: Option B: `GET /api/origins` (global list)
   - **Response Shape**:
     ```typescript
     {
       id: number;
       name: string;
       displayName: string;
       description: string;
       icon: string;
     }[]
     ```
   - **Behavior**:
     - Enabled only after archetype selected
     - Selection updates characterStore.origin
     - No cascading effects (origin is cosmetic in modern CoH)

4. **Alignment Selector**
   - **Description**: Toggle/Radio for Hero/Villain/Vigilante/Rogue alignment
   - **MidsReborn Implementation**: 
     - `ibAlignmentEx` toggle button (ImageButtonEx)
     - Cycles through states on click
     - Default based on archetype.ClassType (Hero vs Villain)
   - **Web Equivalent**: 
     - Radio group or segmented control (shadcn/ui)
     - Options: Hero, Villain, Vigilante, Rogue
     - Visual distinction (hero blue, villain red theme)
   - **API**: No API call (client-side only, may affect powerset filtering)
   - **Behavior**:
     - Default to Hero for hero archetypes, Villain for villain archetypes
     - Going Rogue alignments (Vigilante/Rogue) allow cross-faction pool powers
     - Alignment changes trigger UI theme updates
     - Store as: `characterStore.alignment`

5. **Archetype Info Display**
   - **Description**: Show archetype description, inherent powers, AT modifiers when archetype selected
   - **MidsReborn Implementation**: 
     - Popup tooltip on hover (ShowPopup() method)
     - Separate inherent powers list in main UI
     - Archetype stats visible in totals panel
   - **Web Equivalent**: 
     - Collapsible Card or Accordion component
     - Sections: Description, Inherent Powers, AT Modifiers, Caps
   - **Display Data**:
     - **Description**: `archetype.descShort` or `archetype.descLong`
     - **Inherent Powers**: List of powers granted automatically (from archetype.inherentPowers)
     - **AT Modifiers**: Damage scale, HP base, caps (damage, resistance, defense, recharge, etc.)
     - **Caps Display**:
       - HP Cap: `archetype.hpCap` (e.g., "2409 HP")
       - Damage Cap: `archetype.damageCap` (e.g., "400%" or "500%")
       - Resistance Cap: `archetype.resCap` (e.g., "75%" or "90%")
       - Defense Soft Cap: 45% (universal)
       - Recharge Cap: `archetype.rechargeCap` (e.g., "500%")
   - **API**: Data from `GET /api/archetypes/{id}` (includes inherent powers)

### SHOULD-HAVE Features

1. **Archetype Icons/Visuals**
   - Use Next.js Image component with archetype icons
   - Fallback to archetype initial if icon missing
   - Icon size: 24x24 or 32x32 for selectors

2. **Origin Icons/Visuals**
   - Origin icon in dropdown (magic wand, DNA, beaker, atom, gear)
   - Icon size: 20x20 for inline display

3. **Tooltips with Details**
   - shadcn/ui Tooltip on hover showing:
     - Archetype: Full description, inherent powers preview
     - Origin: Lore description (cosmetic flavor)
   - Keyboard accessible (focus triggers tooltip)

4. **Validation Feedback**
   - Inline validation messages:
     - "Please select an archetype" (if trying to proceed without AT)
     - "Origin required" (if archetype selected but no origin)
   - Visual indicators (red border, error icon)
   - Toast notifications for critical errors

5. **Search/Filter in Archetype Selector**
   - Type to search archetype names
   - Filter by faction (Hero/Villain/Epic)
   - Keyboard navigation (arrow keys, enter to select)

6. **Alignment Visual Feedback**
   - Background color/gradient based on alignment:
     - Hero: Blue gradient
     - Villain: Red gradient
     - Vigilante: Purple/blue gradient
     - Rogue: Orange/red gradient
   - Icon changes (hero badge, villain symbol, etc.)

### COULD-SKIP Features (Defer to Later Epics)

1. **Advanced Archetype Info Displays**
   - Full archetype comparison table (compare multiple ATs side-by-side)
   - Detailed modifier tables (all 50 levels of damage scales)
   - Advanced caps breakdown (per power type)
   - **Reason**: Epic 4 (Build Totals) will show detailed stats

2. **Origin Power Details**
   - Origin-specific powers (no longer exist in modern CoH)
   - Origin enhancement bonuses (cosmetic only)
   - **Reason**: Origins are cosmetic in current game

3. **Archetype Recommendations**
   - AI/algorithm suggesting archetype based on playstyle quiz
   - "Popular" or "Recommended" badges
   - **Reason**: Nice-to-have, not core functionality

4. **Character Name Validation**
   - Check against profanity filter
   - Check name availability (requires server-side build storage)
   - **Reason**: Build storage is Epic 6

5. **Alignment Morality System**
   - Tip missions tracking (Hero → Vigilante → Villain path)
   - Alignment merits display
   - **Reason**: Beyond build planning scope

## State Management Analysis

### Server State (TanStack Query)

#### Query 1: Fetch All Archetypes

**Endpoint**: `GET /api/archetypes`

**Query Key**: `['archetypes']` or `['archetypes', { playable: true }]`

**Response Data**:
```typescript
Archetype[] = [
  {
    id: number;
    name: string;
    displayName: string;
    icon: string;
    displayHelp: string; // Long description
    displayShortHelp: string; // Short description
    classType: "Hero" | "Villain" | "HeroEpic" | "VillainEpic";
    isVillain: boolean;
    hitPointsBase: number;
    hitPointsMax: number;
    attribBase: {
      damageType: { [key: string]: number[] }; // Damage scales per level
      defenseType: { [key: string]: number[] }; // Defense caps
      // ... other modifier arrays
    };
    primaryCategory: string; // e.g., "Tanker_Primary"
    secondaryCategory: string;
    epicPoolCategory: string;
    // Calculated/derived fields for web:
    allowedOrigins?: string[]; // Derived from archetype logic or separate table
  }
]
```

**Caching Strategy**: 
- `staleTime: Infinity` (archetypes never change during session)
- `cacheTime: 1000 * 60 * 60 * 24` (cache for 24 hours)
- Prefetch on app load

**Hook**:
```typescript
// hooks/useArchetypes.ts
export function useArchetypes() {
  return useQuery({
    queryKey: ['archetypes'],
    queryFn: () => api.getArchetypes(),
    staleTime: Infinity,
    select: (data) => data.filter(at => at.playable), // Filter playable
  });
}
```

#### Query 2: Fetch Archetype Details (with inherent powers)

**Endpoint**: `GET /api/archetypes/{id}`

**Query Key**: `['archetype', archetypeId]`

**Response Data**:
```typescript
{
  ...Archetype,
  inherentPowers: Power[]; // Auto-granted powers
  modifierTables: {
    [tableName: string]: number[]; // e.g., "Melee_Damage": [0.5, 0.55, ...]
  };
}
```

**Caching Strategy**: Same as archetypes list

**Hook**:
```typescript
export function useArchetype(archetypeId: number | null) {
  return useQuery({
    queryKey: ['archetype', archetypeId],
    queryFn: () => api.getArchetype(archetypeId!),
    enabled: !!archetypeId, // Only fetch if archetype selected
    staleTime: Infinity,
  });
}
```

#### Query 3: Fetch Origins

**Endpoint**: `GET /api/origins` (if implementing separate origins endpoint)

**Query Key**: `['origins']`

**Response Data**:
```typescript
Origin[] = [
  {
    id: number;
    name: string;
    displayName: string;
    description: string;
    icon: string;
  }
]
// Expected: Magic, Mutation, Natural, Science, Technology
```

**Caching Strategy**: 
- `staleTime: Infinity`
- `cacheTime: 1000 * 60 * 60 * 24`

**Alternative Approach**: 
- Hardcode 5 origins in frontend (they're static game data)
- Or derive from archetype data (if archetypes have `allowedOrigins` field)

**Hook**:
```typescript
export function useOrigins() {
  // Option A: Fetch from API
  return useQuery({
    queryKey: ['origins'],
    queryFn: () => api.getOrigins(),
    staleTime: Infinity,
  });
  
  // Option B: Hardcoded constant
  return {
    data: ORIGINS_CONSTANT,
    isLoading: false,
    isError: false,
  };
}
```

### Client State (Zustand characterStore)

**Store**: `characterStore.ts` (already exists, see frontend/stores/characterStore.ts)

**State Shape** (Epic 2.1 subset):
```typescript
interface CharacterState {
  // Character identity
  name: string; // Character name
  archetype: Archetype | null; // Selected archetype object
  origin: Origin | null; // Selected origin object
  alignment: Alignment | null; // Selected alignment
  
  // Actions (already defined in existing store)
  setName: (name: string) => void;
  setArchetype: (archetype: Archetype | null) => void;
  setOrigin: (origin: Origin | null) => void;
  setAlignment: (alignment: Alignment | null) => void;
}
```

**Alignment Type** (update `types/character.types.ts`):
```typescript
// Currently defined as:
export type AlignmentType = "Hero" | "Villain" | "Vigilante" | "Rogue";

export interface Alignment {
  id: number;
  name: AlignmentType;
  displayName: string;
}
```

**Actions**:
- `setName(name)`: Update character name (simple string assignment)
- `setArchetype(archetype)`:
  - Update archetype
  - Clear incompatible powersets (primary/secondary if they don't match new archetype)
  - Reset origin to null (force re-selection from new archetype's allowed origins)
- `setOrigin(origin)`: Update origin (no cascading effects)
- `setAlignment(alignment)`: Update alignment (may affect available pool powers in Epic 2.2)

**Persistence**:
- Already configured with `zustand/middleware/persist`
- Persists to localStorage under `"character-build-storage"` key
- Survives page refreshes

**Store Usage in Components**:
```typescript
// In ArchetypeSelector component
const { archetype, setArchetype } = useCharacterStore();

function handleArchetypeChange(newArchetype: Archetype) {
  // Warn if powersets already selected
  if (hasPowersets && archetype !== newArchetype) {
    confirmDialog("Changing archetype will reset powersets. Continue?", () => {
      setArchetype(newArchetype);
    });
  } else {
    setArchetype(newArchetype);
  }
}
```

### Derived State

1. **Inherent Powers**
   - Source: `archetype.inherentPowers` (from API query)
   - Computed: Filter/map inherent powers for display
   - Hook: `useArchetype(archetypeId)` → `data.inherentPowers`

2. **AT Modifiers Display**
   - Source: `archetype.attribBase` and cap fields
   - Computed: Format for display (e.g., damageCap: 4.0 → "400%")
   - Component: `<ATModifiersDisplay archetype={archetype} />`

3. **Allowed Origins**
   - Source: `archetype.allowedOrigins` (if in API) or hardcoded list
   - Computed: Filter global origins list by archetype's allowed origins
   - Most archetypes allow all 5, but Kheldians may restrict

4. **Is Archetype Selected**
   - Computed: `!!characterStore.archetype`
   - Used to enable/disable origin selector

5. **Theme Color (based on alignment)**
   - Source: `characterStore.alignment.name`
   - Computed: Map to CSS class or Tailwind variant
   - Example: `Hero → "theme-hero"`, `Villain → "theme-villain"`

## Web Component Mapping

| MidsReborn Pattern | Web Equivalent | Library/Component | Props/Config |
| ------------------ | -------------- | ----------------- | ------------ |
| TextBox (`txtName`) | Input | shadcn/ui Input | `placeholder="Enter character name"` |
| ComboBox (`cbAT`) - Archetype | Select with Search | shadcn/ui Select + Command | `searchable`, `items={archetypes}` |
| ComboBox (`cbOrigin`) - Origin | Select | shadcn/ui Select | `items={origins}`, `disabled={!archetype}` |
| ImageButtonEx (`ibAlignmentEx`) - Alignment | Radio Group or Toggle | shadcn/ui RadioGroup or ToggleGroup | `options={alignments}`, `value={alignment}` |
| Label (Archetype info) | Typography + Card | shadcn/ui Card | `title`, `description`, `children` |
| PictureBox (Archetype icon) | Image | Next.js Image | `src={archetype.icon}`, `width={32}`, `height={32}` |
| ToolTip (AT description) | Tooltip | shadcn/ui Tooltip | `content={archetype.descLong}` |
| Popup (AT hover info) | Popover or Drawer | shadcn/ui Popover | `trigger={<InfoIcon />}`, `content={<ATDetails />}` |
| OwnerDraw ComboBox items | Custom Select Option | shadcn/ui Select with custom render | `renderOption={(item) => <Icon /> {item.name}` |

## API Integration Points

### Backend Endpoints Needed

1. **GET /api/archetypes**
   - **Purpose**: Fetch all playable archetypes
   - **Query Params**: 
     - `playable=true` (filter for player archetypes)
     - `faction=hero|villain|all` (optional filter)
   - **Response**: `Archetype[]` (see schema above)
   - **Status**: ✅ Already implemented (backend/app/routers/archetypes.py)
   - **Notes**: May need to add `allowedOrigins` field to schema if not present

2. **GET /api/archetypes/{archetype_id}**
   - **Purpose**: Fetch single archetype with full details (inherent powers, modifiers)
   - **Path Params**: `archetype_id: int`
   - **Response**: `ArchetypeWithDetails` (includes inherent powers)
   - **Status**: ✅ Already implemented
   - **Notes**: Verify response includes inherent powers or add separate join

3. **GET /api/origins** (Optional)
   - **Purpose**: Fetch all origins (if not hardcoded)
   - **Response**: `Origin[]` (5 origins)
   - **Status**: ❓ NOT YET IMPLEMENTED
   - **Decision**: 
     - **Option A**: Implement endpoint (recommended for consistency)
     - **Option B**: Hardcode in frontend constants (origins never change)
     - **Option C**: Derive from archetype data (archetype.allowedOrigins field)

4. **GET /api/archetypes/{archetype_id}/inherent-powers** (Alternative)
   - **Purpose**: Fetch inherent powers separately if not in main archetype endpoint
   - **Response**: `Power[]` (inherent powers for archetype)
   - **Status**: Not needed if archetype endpoint includes inherents

### Backend Schema Enhancements

**Check if these fields exist in backend Archetype schema** (backend/app/schemas/base.py):

```python
class Archetype(ArchetypeBase, TimestampedBase, BaseEntitySchema):
    id: int
    # ... existing fields ...
    
    # NEEDED FOR EPIC 2.1:
    inherent_powers: list[Power] | None = None  # Add if missing
    allowed_origins: list[str] | None = None    # Add if missing (or derive from game data)
    
    # Ensure these exist:
    display_help: str | None  # Long description (maps to DescLong)
    display_short_help: str | None  # Short description (maps to DescShort)
    hit_points_base: int | None
    hit_points_max: int | None
    # Caps (check if these are in attrib_base JSON or separate fields):
    damage_cap: float | None
    res_cap: float | None
    recharge_cap: float | None
    regen_cap: float | None
    recovery_cap: float | None
```

**Add Origins endpoint** (if not hardcoding):

```python
# backend/app/routers/origins.py
@router.get("/origins", response_model=list[schemas.Origin])
async def get_origins(db: Session = Depends(get_db)):
    """Get all character origins (Magic, Natural, Science, Mutation, Technology)."""
    origins = crud.get_origins(db)
    return origins
```

**Origin schema**:
```python
# backend/app/schemas/base.py
class OriginBase(BaseModel):
    name: str
    display_name: str | None = None
    description: str | None = None
    icon: str | None = None

class Origin(OriginBase, BaseEntitySchema):
    id: int
```

## Screenshot Analysis

### Available Screenshots

**Location**: `/home/user/mids-hero-web/shared/user/midsreborn-screenshots/`

1. **mids-new-build.png** ✅
   - **Shows**: 
     - Character name field: "Magic Blaster" (top-left)
     - Archetype dropdown: "Blaster" selected (below name)
     - Origin dropdown: "Magic" selected (below archetype)
     - Primary powerset: "Archery" (below origin)
     - Secondary powerset: "Atomic Manipulation" (below primary)
   - **Relevant to**: ALL Epic 2.1 components
   - **Position**: Top-left panel of main window, stacked vertically
   - **Layout**: Compact inline layout with labels on left, controls on right
   - **Notes**: 
     - Shows complete character creation flow in single screenshot
     - Labels: "Name:", "Archetype:", "Origin:" (simple text labels)
     - Dropdowns: ~144px width, 20-23px height
     - Spacing: ~5-8px between rows

2. **total-screen-1.png** ✅
   - **Shows**: Full Mids window with character panel visible
   - **Relevant to**: Overall layout context
   - **Notes**: Shows character creation panel in context of full UI

3. **view-total-window.png** ✅
   - **Shows**: Another full window view
   - **Relevant to**: Layout context

**Visual Insights from mids-new-build.png**:
- Character creation controls are VERY compact (fits in ~150px vertical space)
- Labels are right-aligned, controls left-aligned (forms a clean column)
- No visible alignment selector in this screenshot (alignment button is in toolbar)
- Dropdowns show icons inline (small 16x16 icons next to text)
- Simple, functional design - no fancy styling
- Clear visual hierarchy: Name → AT → Origin → Powersets

### Additional Screenshots Recommended

**Not critical for Epic 2.1 (can proceed without these)**:

1. **Archetype Dropdown Open**
   - Filename suggestion: `midsreborn-archetype-dropdown-open.png`
   - Should show: Full list of playable archetypes in dropdown
   - Needed for: Understanding dropdown UX, seeing all archetype names, icon placement
   - Priority: LOW (we understand the structure from code)

2. **Origin Dropdown Open**
   - Filename suggestion: `midsreborn-origin-dropdown-open.png`
   - Should show: All 5 origins listed with icons
   - Needed for: Origin selector UX, icon design
   - Priority: LOW (only 5 origins, structure is simple)

3. **Alignment Button States**
   - Filename suggestion: `midsreborn-alignment-toggle.png`
   - Should show: Alignment button in different states (Hero, Villain, etc.)
   - Needed for: Alignment selector visual design
   - Priority: MEDIUM (would help with icon/color choices, but we can design from scratch)

4. **Inherent Powers Display**
   - Filename suggestion: `midsreborn-inherent-powers.png`
   - Should show: Where inherent powers are displayed in UI
   - Needed for: Inherent powers layout
   - Priority: MEDIUM (helpful for Epic 2.1 info display)

**Conclusion**: Existing screenshot (mids-new-build.png) provides sufficient visual reference for Epic 2.1 implementation. Additional screenshots would be nice-to-have but not blockers.

## Implementation Notes

### Key Behaviors to Replicate

1. **Character Name Updates**
   - Real-time update to store on every keystroke
   - No debouncing needed (simple string assignment)
   - Auto-save to localStorage via Zustand persist middleware

2. **Archetype Selection**
   - Populates origin dropdown with archetype's allowed origins
   - Clears incompatible powersets if archetype changes (Epic 2.2 concern)
   - Shows warning/confirmation before clearing powersets
   - Updates inherent powers display
   - Updates AT modifiers/caps display

3. **Origin Selection**
   - Independent selection (no cascading effects to powersets)
   - Purely cosmetic in modern CoH (no stat changes)
   - Updates immediately in store

4. **Alignment Selection**
   - Default alignment based on archetype faction (Hero/Villain)
   - Toggle or radio group interface (not dropdown)
   - May affect pool power availability (Going Rogue feature)
   - Updates UI theme colors throughout app

5. **Data Flow**
   - Fetch archetypes on component mount (TanStack Query)
   - Store selected archetype/origin/alignment in Zustand
   - Persist to localStorage automatically
   - Sync between store and UI bidirectionally

6. **Validation**
   - Archetype required before proceeding to power selection
   - Origin required before proceeding
   - Name optional (can have empty string)
   - Show validation errors inline (red border, error message)

### UX Improvements for Web

1. **Search/Filter in Archetype Selector**
   - Add search input in Select dropdown (shadcn/ui Command component)
   - Filter archetypes by name as user types
   - Keyboard navigation (arrow keys, enter to select)
   - Group archetypes by faction (Hero, Villain, Epic)

2. **Archetype Icons with Fallback**
   - Use Next.js Image component with `onError` fallback
   - Fallback: Display archetype initial in colored circle
   - Lazy load icons for performance

3. **Tooltips on Hover**
   - Archetype: Show short description + inherent powers preview
   - Origin: Show lore description
   - Alignment: Show explanation of alignment system
   - Keyboard accessible (focus triggers tooltip)

4. **Smooth Transitions**
   - Fade in/out when changing archetype info display
   - Slide animation for origin dropdown appearing after AT selection
   - Framer Motion or Tailwind transitions

5. **Auto-save Indicators**
   - Subtle "Saved" indicator after selections (toast or inline text)
   - Loading states during API calls (skeleton loaders)
   - Error states with retry buttons

6. **Responsive Layout**
   - Desktop: Horizontal layout (labels left, controls right)
   - Mobile: Vertical stacking (labels above controls)
   - Tablet: Adaptive spacing

7. **Accessibility**
   - ARIA labels for all form controls
   - Keyboard navigation support (Tab, Enter, Escape)
   - Focus indicators (visible focus rings)
   - Screen reader announcements for state changes

8. **Visual Feedback**
   - Highlight selected archetype in dropdown (checkmark icon)
   - Disable origin selector until archetype selected (greyed out)
   - Required field indicators (asterisk or "Required" label)
   - Success states (green checkmark when valid)

### Component Structure Proposal

```
components/character/
├── CharacterCreationPanel.tsx      # Main container for Epic 2.1
│   ├── CharacterNameInput.tsx       # Name input field
│   ├── ArchetypeSelector.tsx        # Archetype dropdown with search
│   ├── OriginSelector.tsx           # Origin dropdown
│   ├── AlignmentSelector.tsx        # Alignment radio/toggle
│   └── ArchetypeInfoDisplay.tsx     # Info panel for selected AT
│       ├── InherentPowersList.tsx   # List of inherent powers
│       └── ATModifiersCard.tsx      # Caps and modifiers display
└── __tests__/
    ├── CharacterNameInput.test.tsx
    ├── ArchetypeSelector.test.tsx
    ├── OriginSelector.test.tsx
    └── AlignmentSelector.test.tsx
```

### Component Interaction Flow

```
User Action: Select Archetype
  ↓
ArchetypeSelector.onChange()
  ↓
characterStore.setArchetype(archetype)
  ↓
Store Updates:
  - archetype = newArchetype
  - origin = null (reset to force re-selection)
  - primaryPowerset = null (if incompatible)
  - secondaryPowerset = null (if incompatible)
  ↓
UI Updates (React re-renders):
  - OriginSelector enabled, shows archetype.allowedOrigins
  - ArchetypeInfoDisplay shows archetype details
  - InherentPowersList shows archetype inherent powers
  - ATModifiersCard shows caps/modifiers
  ↓
TanStack Query fetches:
  - useArchetype(archetypeId) → inherent powers, modifiers
  ↓
localStorage persists:
  - characterStore state auto-saved
```

## Warnings & Edge Cases

### Critical Edge Cases

1. **Changing Archetype After Powersets Selected**
   - **Issue**: User has already selected primary/secondary powersets, then changes archetype
   - **MidsReborn Behavior**: Calls `Character.Reset(newArchetype, origin)`, clears incompatible powersets
   - **Web Behavior**: 
     - Detect if `powers.length > 0` or powersets selected
     - Show confirmation dialog: "Changing archetype will reset your powersets. Continue?"
     - If confirmed: Clear powersets, reset to new archetype
     - If cancelled: Revert archetype selection
   - **Implementation**: Add `hasIncompatiblePowersets` computed in store

2. **Archetype Not Selected**
   - **Issue**: User tries to select origin without selecting archetype first
   - **MidsReborn Behavior**: Origin dropdown is empty/disabled
   - **Web Behavior**: 
     - Disable origin selector until archetype selected (`disabled={!archetype}`)
     - Show placeholder: "Select archetype first"
     - Inline hint text: "Choose an archetype above to select origin"

3. **Origin Dropdown Empty**
   - **Issue**: Selected archetype has no allowed origins (edge case, shouldn't happen)
   - **Web Behavior**: 
     - Show error message: "This archetype has no available origins"
     - Log error to console for debugging
     - Fallback: Show all 5 origins anyway (data corruption failsafe)

4. **API Fetch Failures**
   - **Issue**: GET /api/archetypes fails (network error, server down)
   - **Web Behavior**:
     - Show error message: "Failed to load archetypes. Please try again."
     - Retry button triggers `queryClient.refetch(['archetypes'])`
     - Skeleton loader during loading state
     - Fallback: Cache archetypes in localStorage? (optional)

5. **Long Archetype Names**
   - **Issue**: Archetype name overflows dropdown/display (e.g., "Arachnos Widow")
   - **Web Behavior**: 
     - Truncate with ellipsis: `text-overflow: ellipsis; white-space: nowrap;`
     - Show full name in tooltip on hover
     - Responsive width: Min 200px, max 400px

6. **Empty Character Name**
   - **Issue**: User leaves name field empty
   - **MidsReborn Behavior**: Allows empty name (no validation)
   - **Web Behavior**: 
     - Allow empty name (MidsReborn parity)
     - Optional: Placeholder "Unnamed Hero" in build list (Epic 6 concern)
     - No client-side validation required

7. **Alignment Auto-set**
   - **Issue**: User selects archetype, alignment auto-sets to Hero/Villain
   - **MidsReborn Behavior**: Sets alignment based on `archetype.ClassType` (Hero vs Villain)
   - **Web Behavior**: 
     - Auto-set alignment on archetype selection: 
       - Hero archetypes → "Hero"
       - Villain archetypes → "Villain"
     - User can override (change to Vigilante/Rogue)
     - Changing archetype resets alignment to default

8. **Kheldian/VEAT Special Cases**
   - **Issue**: Peacebringer/Warshade (Kheldians) and Soldier/Widow (VEATs) may have special origin rules
   - **MidsReborn Behavior**: Kheldians typically lock to "Natural" origin (lore reason)
   - **Web Behavior**: 
     - Respect archetype.allowedOrigins array
     - If only 1 origin allowed, auto-select and disable dropdown
     - Show info message: "This archetype is limited to [Origin] origin"

### Validation Rules

1. **Required Fields** (for completing Epic 2.1):
   - ✅ Archetype: REQUIRED (cannot proceed without)
   - ✅ Origin: REQUIRED (cannot proceed without)
   - ⚠️ Name: OPTIONAL (can be empty string)
   - ⚠️ Alignment: OPTIONAL (has default based on archetype)

2. **Field Dependencies**:
   - Origin depends on Archetype (must select AT first)
   - Alignment defaults from Archetype (but user can override)
   - Name is independent (can be set anytime)

3. **Data Validation**:
   - Archetype ID must exist in database (validated by API)
   - Origin must be in archetype's allowed origins list
   - Alignment must be one of 4 valid values
   - Name: No validation (any string, including empty)

### Performance Considerations

1. **Archetype List Size**
   - ~15-20 playable archetypes (manageable size)
   - No pagination needed for dropdown
   - Render all items, use virtual scrolling if list grows (unlikely)

2. **API Caching**
   - Cache archetypes indefinitely (static data)
   - Prefetch on app mount for instant availability
   - Consider service worker caching for offline support (future)

3. **Image Loading**
   - Lazy load archetype icons (Next.js Image handles this)
   - Optimize icons: WebP format, 32x32 or 64x64 max
   - CDN hosting for icons (future optimization)

4. **Store Updates**
   - Avoid unnecessary re-renders: Use Zustand selectors
   - Example: `const archetype = useCharacterStore(state => state.archetype)` (only re-renders when archetype changes)

### Testing Edge Cases

**Unit Tests**:
- CharacterNameInput: Empty string, very long name (>100 chars), special characters
- ArchetypeSelector: No archetypes (API returns []), API error, search filtering
- OriginSelector: Archetype not selected (disabled state), archetype with 1 allowed origin
- AlignmentSelector: Default alignment, user override, archetype change resets alignment

**Integration Tests**:
- Select archetype → origin dropdown populates
- Change archetype → powersets cleared (if any), origin reset
- Select all fields → verify store state correct
- Refresh page → verify localStorage persistence

**E2E Tests** (Playwright/Cypress):
- Complete character creation flow: Name → AT → Origin → Alignment
- Change archetype mid-build → confirmation dialog → reset
- API failure scenarios → error messages → retry

---

## Analysis Complete

**Status**: ✅ Ready for planning phase

**Components Identified**: 6 core components (CharacterCreationPanel, CharacterNameInput, ArchetypeSelector, OriginSelector, AlignmentSelector, ArchetypeInfoDisplay)

**API Endpoints Required**: 
- ✅ `GET /api/archetypes` (exists)
- ✅ `GET /api/archetypes/{id}` (exists)
- ❓ `GET /api/origins` (needs implementation decision)

**Web Components Needed**: 
- Input (name)
- Select (archetype, origin)
- RadioGroup or ToggleGroup (alignment)
- Card (archetype info)
- Tooltip (descriptions)
- Image (icons)

**State Management**:
- Server State: TanStack Query (archetypes, origins)
- Client State: Zustand characterStore (name, archetype, origin, alignment)
- Persistence: localStorage via Zustand persist middleware

**Next Steps**:
1. Review API backend to confirm archetype schema includes needed fields (inherent powers, allowed origins)
2. Decide on origins approach (API endpoint vs hardcoded vs archetype-derived)
3. Create implementation plan using `/superpowers:write-plan` workflow
4. Begin component development starting with CharacterNameInput (simplest)
5. Progressive enhancement: Name → AT → Origin → Alignment → Info Display

**Estimated Effort**: 2-3 days for Epic 2.1 (assuming API endpoints ready)
