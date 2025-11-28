# MidsReborn UI Analysis: Epic 2.3 - Character Sheet Display

**Created**: 2025-11-18
**Epic**: 2.3 - Character Sheet Display
**MidsReborn Forms Analyzed**: 
- `external/dev/MidsReborn/MidsReborn/Forms/frmMain.cs`
- `external/dev/MidsReborn/MidsReborn/Forms/frmMain.Designer.cs`
- `external/dev/MidsReborn/MidsReborn/Core/Base/Data_Classes/Character.cs`
- `external/dev/MidsReborn/MidsReborn/Core/Base/Data_Classes/Archetype.cs`
- `external/dev/MidsReborn/MidsReborn/Core/Base/Display/InherentDisplayItem.cs`
- `external/dev/MidsReborn/MidsReborn/Core/DatabaseAPI.cs`

## Executive Summary

MidsReborn displays character summary information in a top panel label (`lblCharacter`) that consolidates name, level, archetype, origin, and powersets into a single readable string (e.g., "Magic Blaster: Level 10 Magic Blaster (Archery / Tactical Arrow)"). The archetype data model includes comprehensive cap values (damage, resistance, defense, HP, recovery, regeneration, recharge) and base modifiers (HP, regen, recovery, threat) that define archetype balance. Inherent powers are retrieved from a special "Inherent" powerset and displayed via the InherentDisplayList on the Character object. For the web implementation, we'll create dedicated components (CharacterSheet, ATModifiersDisplay, CapsDisplay, InherentPowersDisplay) that fetch archetype data from the backend API and present it in modern card-based layouts with clear visual hierarchy.

## MidsReborn UI Components

### Component 1: Character Summary Display (lblCharacter)

- **File**: `external/dev/MidsReborn/MidsReborn/Forms/frmMain.cs` (line 1220-1254)
- **Purpose**: Display consolidated character summary in top panel
- **Layout**: Single label control in topPanel, dynamically updated
  - Location: Top of main window
  - Font: Default label font
  - Updates on character changes
- **Data Displayed**:
  - Character name: `MidsContext.Character.Name`
  - Level: `MidsContext.Character.Level` (with level-up indicator if placing powers)
  - Origin: `archetype.Origin[character.Origin]` (string from archetype's origin array)
  - Archetype: `archetype.DisplayName`
  - Powersets (when locked): `powerset[0].DisplayName / powerset[1].DisplayName`
  - Exemp info (if active): Exemp range
  - **Format**: `"{Name}: Level {level} {Origin} {Archetype} ({Primary} / {Secondary})"`
  - **Example**: "Magic Blaster: Level 10 Magic Blaster (Archery / Tactical Arrow)"
- **User Interactions**:
  - Read-only display (no direct interaction)
  - Updates automatically when character properties change
  - Name editing happens via txtName TextBox (separate control)

### Component 2: Top Panel Character Controls

- **File**: `external/dev/MidsReborn/MidsReborn/Forms/frmMain.Designer.cs` (line 192-500)
- **Purpose**: Editable character creation controls
- **Layout**: Panel with stacked controls:
  ```
  topPanel (Panel)
    ├─ lblName + txtName (TextBox) - Location: (94, 82), Size: (144x20)
    ├─ lblAT + cbAT (ComboBox) - Location: (94, 108), Size: (144x23)
    ├─ lblOrigin + cbOrigin (ComboBox) - Location: (94, 133), Size: (144x23)
    ├─ ibAlignmentEx (ImageButton Toggle) - Hero/Villain toggle
    ├─ lblCharacter (Label) - Summary display
    └─ Various image buttons (Team, Temp Powers, Accolades, etc.)
  ```
- **Data Displayed**:
  - **Name**: Editable text field (any string)
  - **Archetype**: Dropdown with OwnerDrawn items showing icons
  - **Origin**: Dropdown filtered by selected archetype's allowed origins
  - **Alignment**: Toggle button (Hero/Villain with distinct visuals)
- **User Interactions**:
  - See Epic 2.1 analysis for detailed archetype/origin selection behavior
  - Character sheet displays derived from these selections

### Component 3: Archetype Data Model

- **File**: `external/dev/MidsReborn/MidsReborn/Core/Base/Data_Classes/Archetype.cs`
- **Purpose**: Store archetype caps and modifiers
- **Caps Properties**:
  - `HPCap: float` - Max HP cap (e.g., 3534.0 for Tanker, 1874.0 for Blaster)
  - `DamageCap: float` - Damage buff cap as multiplier (e.g., 7.75 for Brute = 775%, 4.0 for Blaster = 400%)
  - `ResCap: float` - Resistance cap as decimal (e.g., 0.90 for Tanker = 90%, 0.75 for Blaster = 75%)
  - `RegenCap: float` - Regeneration cap as multiplier (e.g., 25.0 for Tanker = 2500%, 20.0 for Blaster = 2000%)
  - `RecoveryCap: float` - Endurance recovery cap (e.g., 8.0 = 800%)
  - `RechargeCap: float` - Recharge speed cap (e.g., 5.0 = 500%)
  - `PerceptionCap: float` - Perception range cap in feet (e.g., 1153.0)
  - **Note**: Defense cap is not in Archetype.cs (it's a game-wide soft cap at 45%, hard display cap varies by AT)
- **Base Modifiers**:
  - `Hitpoints: int` - Base HP at level 1 (varies by AT)
  - `BaseRegen: float` - Base regeneration multiplier (typically 1.0)
  - `BaseRecovery: float` - Base endurance recovery (typically 1.67)
  - `BaseThreat: float` - Threat/aggro multiplier (e.g., higher for Tanker)
- **Display Properties**:
  - `DisplayName: string` - "Tanker", "Blaster", etc.
  - `ClassName: string` - Internal class name
  - `DescShort: string` - Brief archetype description
  - `DescLong: string` - Full archetype description
- **Usage in Code**:
  - Caps enforced in `clsToonX.cs` lines 862-873:
    ```csharp
    TotalsCapped.BuffDam = Math.Min(TotalsCapped.BuffDam, Archetype.DamageCap - 1);
    TotalsCapped.HPRegen = Math.Min(TotalsCapped.HPRegen, Archetype.RegenCap - 1);
    TotalsCapped.EndRec = Math.Min(TotalsCapped.EndRec, Archetype.RecoveryCap - 1);
    TotalsCapped.Res[index] = Math.Min(TotalsCapped.Res[index], Archetype.ResCap);
    TotalsCapped.HPMax = Math.Min(TotalsCapped.HPMax, Archetype.HPCap);
    ```

### Component 4: Inherent Powers System

- **File**: `external/dev/MidsReborn/MidsReborn/Core/DatabaseAPI.cs` (line 542)
- **Purpose**: Retrieve inherent powers for display
- **Data Structure**:
  - **InherentDisplayItem** (from `Core/Base/Display/InherentDisplayItem.cs`):
    ```csharp
    class InherentDisplayItem {
        int Priority { get; set; }
        IPower Power { get; set; }
    }
    ```
  - **Character.InherentDisplayList**: `List<InherentDisplayItem>?` - Ordered list of inherent powers
- **How Inherent Powers Work**:
  - Inherent powerset retrieved via `DatabaseAPI.GetInherentPowerset()`
  - Returns first powerset with `SetType == Enums.ePowerSetType.Inherent`
  - Examples of inherent powers by AT:
    - **Blaster**: Defiance (damage buff when low HP)
    - **Brute**: Fury (damage buff from attacks/taking damage)
    - **Scrapper**: Critical Hit (chance for double damage)
    - **Tanker**: Gauntlet (taunt on attacks)
    - **Defender**: Vigilance (endurance discount when team low HP)
    - **Controller**: Containment (double damage on controlled targets)
    - **Corruptor**: Scourge (increased damage on low-HP targets)
    - **Dominator**: Domination (mez protection + damage when bar full)
    - **Mastermind**: Supremacy (pet buff aura)
    - **Stalker**: Assassination/Hide (critical from hide, placate)
- **Display Location**: Not clearly visible in main window screenshots, but inherent powers are part of build data
- **Note**: Inherent powers are automatically granted and cannot be unslotted

## Feature Requirements

### MUST-HAVE Features

1. **Character Summary Display**
   - **Description**: Show character name, level, archetype, origin, alignment in readable format
   - **MidsReborn Implementation**: Single label (`lblCharacter.Text`) with formatted string
   - **Web Equivalent**: 
     - Card or panel component with typography hierarchy
     - Separate fields for each attribute (not single concatenated string)
     - Layout: Horizontal or grid with labels + values
     - **Components**:
       - Character name (large, prominent)
       - Level (badge or pill)
       - Archetype (with icon if available)
       - Origin (with icon if available)
       - Alignment indicator (Hero blue / Villain red)

2. **Archetype Caps Display**
   - **Description**: Show archetype-specific maximum values for stats
   - **MidsReborn Implementation**: Caps accessed via `Archetype.{CapName}`, enforced in calculations
   - **Web Equivalent**:
     - Table or grid showing cap values
     - **Caps to Display**:
       - HP Cap: `archetype.HPCap` (e.g., "3,534 HP" for Tanker)
       - Damage Cap: `archetype.DamageCap` (e.g., "400%" for Blaster, "775%" for Brute)
       - Resistance Cap: `archetype.ResCap` (e.g., "90%" for Tanker, "75%" for Blaster)
       - Defense Cap: From backend `ArchetypeCaps.defense_cap` (e.g., "225%" for Tanker, "175%" for Blaster)
       - Regeneration Cap: `archetype.RegenCap` (e.g., "2500%" for Tanker)
       - Recovery Cap: `archetype.RecoveryCap` (e.g., "800%" for Tanker, "1200%" for Controller)
       - Recharge Cap: `archetype.RechargeCap` (typically "500%" for all)
     - **Display Format**: Name + Value with units
     - **Visual Indicator**: Consider color-coding (green = high cap, yellow = medium, red = low)

3. **Archetype Base Modifiers Display**
   - **Description**: Show archetype base values (not caps)
   - **MidsReborn Implementation**: `Archetype.Hitpoints`, `BaseRegen`, `BaseRecovery`, `BaseThreat`
   - **Web Equivalent**:
     - Separate section or table for base stats
     - **Modifiers to Display**:
       - Base HP: `archetype.Hitpoints` (e.g., "1338" for Blaster at level 1)
       - Base Regen: `archetype.BaseRegen` (typically 1.0, display as percentage)
       - Base Recovery: `archetype.BaseRecovery` (typically 1.67 endurance/second)
       - Base Threat: `archetype.BaseThreat` (e.g., higher for Tanker)
     - **Note**: These are starting values, not caps

4. **Inherent Powers List**
   - **Description**: Display archetype's inherent powers with icons and descriptions
   - **MidsReborn Implementation**: `Character.InherentDisplayList` populated from inherent powerset
   - **Web Equivalent**:
     - List of cards or list items showing inherent powers
     - **Data per Power**:
       - Power name (from `power.DisplayName`)
       - Power icon (from `power.Icon` or backend)
       - Power description (from `power.DescShort`)
       - Priority (for ordering, from `InherentDisplayItem.Priority`)
     - **Display Format**: 
       - Horizontal cards with icon + name + description
       - Or vertical list with tooltips for descriptions
     - **Interaction**: Hover for full description tooltip

### SHOULD-HAVE Features

1. **Inline Character Name/Level Editing**
   - **Description**: Edit character name and level directly in character sheet
   - **MidsReborn Implementation**: Separate txtName TextBox, level derived from build
   - **Web Equivalent**: 
     - Click-to-edit name field (contentEditable or Input on focus)
     - Level selector (dropdown or number input)
     - **Consideration**: Level is typically auto-derived from build in MidsReborn, so inline editing may not be needed

2. **Archetype Description Tooltip**
   - **Description**: Show archetype description on hover
   - **MidsReborn Implementation**: Tooltip on cbAT ComboBox items
   - **Web Equivalent**: Tooltip component on archetype name showing `DescLong`

3. **Visual Cap Indicators**
   - **Description**: Show visual representation of caps (progress bars, gauges)
   - **MidsReborn Implementation**: Text-only display
   - **Web Equivalent**:
     - Progress bars showing current value vs cap (requires build totals - Epic 4)
     - For Epic 2.3, just display cap values; visual indicators come in Epic 4

### COULD-SKIP Features

1. **Exemp Info Display**
   - **Description**: Show exemp level range if character is exemped down
   - **MidsReborn Implementation**: Appended to lblCharacter text
   - **Web Equivalent**: Not priority for v1, can defer to later epic

2. **Archetype Comparison Feature**
   - **Description**: Compare caps between different archetypes
   - **MidsReborn Implementation**: Not present
   - **Web Equivalent**: Nice-to-have, not in scope for Epic 2.3

3. **Advanced Inherent Power Details**
   - **Description**: Show enhancement slots or detailed mechanics for inherent powers
   - **MidsReborn Implementation**: Inherents are not directly slottable in standard way
   - **Web Equivalent**: Defer to later epic if needed

## State Management Analysis

### Server State (TanStack Query)

**Endpoints:**
- `GET /api/archetypes/{id}` - Fetch archetype with full details
  - **Returns**: Archetype object with:
    - Basic info: `id`, `name`, `display_name`, `icon`, `display_help`, `display_short_help`
    - Powersets: Via `archetype.primary_category`, `secondary_category`, `power_pool_category`, `epic_pool_category`
    - Base stats: `hit_points_base`, `hit_points_max`, `attrib_base` (JSON with all base attributes)
    - **Note**: Caps may be in `attrib_base` JSON or need to be fetched from calculations module
- `GET /api/archetypes/{id}/powersets?powerset_type=inherent` - Fetch inherent powerset
  - **Returns**: List of powersets (should contain 1 inherent powerset)
  - Inherent powerset contains inherent powers
- **Backend Caps Data**: `backend/app/calculations/core/archetype_caps.py`
  - Contains `ARCHETYPE_CAPS_DATA` dictionary with all cap values
  - Caps by archetype: Tanker, Brute, Scrapper, Stalker, Blaster, Defender, Controller, Corruptor, Dominator, Mastermind, Sentinel, Peacebringer, Warshade, Arachnos Soldier, Arachnos Widow
  - **Note**: May need to expose caps via API endpoint or include in archetype response

**Caching Strategy:**
- **Archetype data**: Cache forever (static game data, invalidate only on database update)
- **Query keys**: 
  - `['archetypes', archetypeId]` for specific archetype
  - `['archetypes', archetypeId, 'inherentPowers']` for inherent powers

### Client State (Zustand characterStore)

**Store**: `characterStore` (from Epic 1.2)

**State Shape**:
```typescript
interface CharacterState {
  // From Epic 2.1
  name: string;
  level: number;
  archetype: Archetype | null;
  origin: Origin | null;
  alignment: Alignment | null;
  
  // Actions
  setName: (name: string) => void;
  setLevel: (level: number) => void;
  setArchetype: (archetype: Archetype | null) => void;
  setOrigin: (origin: Origin | null) => void;
  setAlignment: (alignment: Alignment) => void;
}
```

**Usage in Epic 2.3**:
- Character sheet components read from store: `name`, `level`, `archetype`, `origin`, `alignment`
- No new state needed for Epic 2.3 (display only)

### Derived State

**Computed Values** (derived from archetype):

1. **Inherent Powers List**
   - **Source**: `archetype.id` → fetch via `useQuery(['archetypes', archetypeId, 'inherentPowers'])`
   - **Derivation**: Filter powersets where `powerset_type === 'inherent'`, then get powers
   - **Component**: `InherentPowersDisplay`

2. **Archetype Caps**
   - **Source**: `archetype.id` → fetch via archetype endpoint or separate caps endpoint
   - **Derivation**: Extract caps from archetype `attrib_base` or backend calculations
   - **Component**: `CapsDisplay`

3. **Archetype Modifiers**
   - **Source**: `archetype.hit_points_base`, `archetype.attrib_base`
   - **Derivation**: Parse `attrib_base` JSON for base regen, recovery, threat
   - **Component**: `ATModifiersDisplay`

4. **Character Summary String**
   - **Source**: `characterStore` (name, level, archetype, origin, alignment)
   - **Derivation**: Format: `"{name}: Level {level} {origin.name} {archetype.display_name}"`
   - **Component**: `CharacterSheet`

## Web Component Mapping

| MidsReborn Pattern | Web Equivalent | Library/Component |
|--------------------|----------------|-------------------|
| `lblCharacter` (Label) | Typography + Card | shadcn/ui Card + custom layout |
| Archetype caps (data properties) | Table or Grid | shadcn/ui Table or custom Grid |
| Base modifiers (data properties) | Table or Key-Value pairs | Custom component |
| Inherent powers list | Card List | shadcn/ui Card in flex layout |
| `txtName` (TextBox) | Input | shadcn/ui Input |
| Level display | Badge or Label | shadcn/ui Badge |
| Alignment indicator | Badge with color | Custom Badge (blue/red) |
| Icons | Image or SVG | Next.js Image or SVG icons |
| Tooltips | Tooltip | shadcn/ui Tooltip |

## API Integration Points

### Backend Endpoints Needed

1. **GET /api/archetypes/{id}**
   - **Status**: ✅ Already implemented (`backend/app/routers/archetypes.py`)
   - **Returns**: Archetype with basic info, categories, HP, attrib_base
   - **Usage**: Fetch archetype data for caps and modifiers

2. **GET /api/archetypes/{id}/powersets?powerset_type=inherent**
   - **Status**: ✅ Already implemented (can filter by type)
   - **Returns**: List of powersets (inherent powerset for AT)
   - **Usage**: Fetch inherent powers for display

3. **Potential New Endpoint**: `GET /api/archetypes/{id}/caps`
   - **Status**: ❓ May need to create
   - **Returns**: Archetype caps from `backend/app/calculations/core/archetype_caps.py`
   - **Data**:
     ```json
     {
       "archetype": "Tanker",
       "damage_cap": 4.0,
       "resistance_cap": 0.90,
       "defense_cap": 2.25,
       "hp_cap": 3534.0,
       "recovery_cap": 8.0,
       "regeneration_cap": 25.0,
       "recharge_cap": 5.0,
       "perception_cap": 1153.0
     }
     ```
   - **Alternative**: Include caps in `GET /api/archetypes/{id}` response (add to schema)

4. **Potential New Endpoint**: `GET /api/archetypes/{id}/modifiers`
   - **Status**: ❓ May need to create or parse from attrib_base
   - **Returns**: Base modifiers (HP, regen, recovery, threat scales)
   - **Alternative**: Parse from `archetype.attrib_base` JSON field

### Backend API Enhancement Recommendations

**Option A: Extend Archetype Schema** (Recommended)
- Add cap fields to `ArchetypeBase` schema in `backend/app/schemas/base.py`:
  ```python
  class ArchetypeBase(BaseModel):
      # ... existing fields ...
      damage_cap: float | None = None
      resistance_cap: float | None = None
      defense_cap: float | None = None
      hp_cap: float | None = None
      recovery_cap: float | None = None
      regeneration_cap: float | None = None
      recharge_cap: float | None = None
      perception_cap: float | None = None
  ```
- Populate from `archetype_caps.py` when returning archetype
- **Pros**: Single endpoint, no extra requests
- **Cons**: Adds fields to archetype response

**Option B: Separate Caps Endpoint**
- Create `GET /api/archetypes/{id}/caps`
- Return caps from `get_archetype_caps()` in `archetype_caps.py`
- **Pros**: Clean separation, caps are optional fetch
- **Cons**: Extra request, more complex caching

**Recommendation**: Use Option A for simplicity.

## Screenshot Analysis

### Available Screenshots

Location: `/home/user/mids-hero-web/shared/user/midsreborn-screenshots`

#### 1. `mids-new-build.png`
   - **Shows**: Main window with character creation controls at top
   - **Relevant to**: Character info panel layout
   - **Observations**:
     - Top-left shows character name "Magic Blaster"
     - Archetype dropdown visible: "Blaster"
     - Origin dropdown visible: "Magic"
     - Power lists visible (Primary: Archery, Secondary: Manipulation, Pools, Epic)
   - **Key Insight**: Character info is compact at top, doesn't show inherent powers prominently in this view

#### 2. `total-screen-1.png`
   - **Shows**: Totals window (frmTotals) with defense/resistance/misc stats
   - **Relevant to**: Caps are enforced here but not displayed
   - **Observations**:
     - Shows "Cumulative Totals (For Self)" tab
     - Defense section with typed/positional defense (all at 0%)
     - Resistance section (all at 0%)
     - Misc Effects: Recovery, Regen, EndDrain, EndRdx, Recharge percentages
   - **Key Insight**: Totals window shows current values, not caps. Caps display is implicit (values can't exceed cap).

#### 3. `view-total-window.png`
   - **Shows**: Similar to total-screen-1.png, different tab or state
   - **Relevant to**: Stats display (Epic 4), not character sheet

### Additional Screenshots Recommended

For Epic 2.3 implementation, these screenshots would be helpful:

1. **Character Info Panel - Close-up**
   - **Filename suggestion**: `midsreborn-character-info-panel.png`
   - **Should show**: Top-left area with Name, Archetype, Origin, Alignment controls
   - **Needed for**: CharacterSheet component layout
   - **Status**: Partially visible in `mids-new-build.png`, but closer shot would help

2. **Archetype Caps - Documentation or UI**
   - **Filename suggestion**: `midsreborn-archetype-caps-reference.png`
   - **Should show**: Any UI that displays archetype caps explicitly
   - **Needed for**: CapsDisplay component
   - **Status**: ❌ Not found - MidsReborn may not display caps explicitly in UI
   - **Alternative**: Use backend `archetype_caps.py` as reference (already found)

3. **Inherent Powers Display**
   - **Filename suggestion**: `midsreborn-inherent-powers.png`
   - **Should show**: How/where inherent powers are shown in MidsReborn
   - **Needed for**: InherentPowersDisplay component
   - **Status**: ❌ Not found in current screenshots
   - **Note**: May need to inspect MidsReborn UI more carefully or rely on data structure

## Implementation Notes

### Key Behaviors to Replicate

1. **Character Summary Format**
   - MidsReborn uses single-line format: `"{Name}: Level {level} {Origin} {Archetype}"`
   - Web version should break this into separate fields for better responsiveness and scannability
   - Consider card-based layout with sections

2. **Level Display Logic**
   - In MidsReborn, level is derived from build (last power placed)
   - Level also shows "Placing {level+1}" indicator when building
   - For Epic 2.3 (character creation), level defaults to 1 or is user-selected
   - **Deferred**: Full level logic comes in Epic 3 (power selection)

3. **Caps vs Current Values**
   - Epic 2.3 displays **caps only** (archetype maximums)
   - Epic 4 will display **current values** from build totals
   - Epic 4 will show progress toward caps (e.g., "Defense: 35% / 45%" with progress bar)

4. **Inherent Powers Ordering**
   - InherentDisplayItem includes `Priority` field for ordering
   - Display inherent powers sorted by priority (ascending)
   - Some inherents may be conditional (e.g., Stalker has multiple)

### UX Improvements for Web

1. **Modern Card Layout**
   - Replace Windows Forms panels with shadcn/ui Card components
   - Use consistent spacing and typography hierarchy
   - Group related information (Summary, Caps, Modifiers, Inherents)

2. **Visual Hierarchy**
   - Character name: Large, bold typography
   - Archetype/Origin/Level: Secondary emphasis with icons
   - Caps: Table or grid with clear labels and units
   - Inherent powers: Horizontal scrollable card list or vertical list

3. **Responsive Design**
   - Stack cards vertically on mobile
   - Horizontal layout on desktop (sidebar or grid)
   - Collapsible sections for Caps and Modifiers (optional)

4. **Interactive Elements**
   - Tooltips on caps explaining what each means
   - Tooltips on inherent powers showing full descriptions
   - Click archetype name to see full description modal

5. **Color Coding**
   - Use alignment colors (blue for Hero, red for Villain) in UI accents
   - Consider color-coding caps (high caps = green, low caps = amber)

6. **Icons and Visual Aids**
   - Use archetype icons if available from backend
   - Use origin icons if available
   - Use power icons for inherent powers
   - Fallback to text-only if icons missing

## Warnings & Edge Cases

1. **Defense Cap Special Case**
   - Defense has no hard cap in City of Heroes (only soft cap at 45% for most content)
   - `ArchetypeCaps.defense_cap` is for **display purposes only**
   - Different ATs have different display caps: 225% (Tanker/Brute), 200% (Scrapper/Stalker), 175% (Blaster/Defender/etc.)
   - Do NOT enforce this as a hard cap in calculations
   - Note in UI that defense soft-cap is 45% (separately from AT cap)

2. **Inherent Powers May Not Be in Inherent Powerset**
   - Some inherent abilities are implemented as powers (Fury, Defiance)
   - Others are implemented as passive flags on Character (Scourge, Critical Hits)
   - Character class has boolean flags: `Defiance`, `Scourge`, `Domination`, `Containment`, `CriticalHits`, `Assassination`, etc.
   - May need to display these flags in addition to inherent powerset powers
   - **Solution**: Fetch inherent powerset AND check character inherent flags

3. **Epic Archetypes (Kheldians, Arachnos)**
   - Have unique inherent powers (shape-shifting, pet buffs)
   - May have multiple inherent powers with priorities
   - Ensure InherentDisplayList handles multiple powers correctly

4. **Caps Not in Database**
   - Archetype caps are in backend calculations (`archetype_caps.py`), not necessarily in DB
   - Need to expose caps via API or include in archetype schema
   - Ensure caps match between backend calculations and frontend display

5. **Attrib_Base JSON Parsing**
   - Backend archetype schema has `attrib_base` as `dict[str, Any]`
   - May contain base modifiers (regen, recovery, threat scales)
   - Need to parse JSON and extract relevant fields for ATModifiersDisplay
   - Handle missing or malformed data gracefully

6. **Level-Dependent Data**
   - Base HP and some modifiers scale with level
   - For Epic 2.3 (character creation), show level 1 or level 50 base values
   - Full level-scaling comes in Epic 3-4 with build calculations

7. **Missing Icons**
   - Archetype icons may not be in backend yet
   - Origin icons may not be in backend yet
   - Inherent power icons should be in powers table
   - Provide text-only fallbacks for missing icons

8. **Alignment vs Archetype Hero/Villain**
   - Archetype has `is_villain` boolean (determines default alignment)
   - Character alignment can change (Rogue, Vigilante in Going Rogue)
   - Don't assume alignment from archetype, use character's alignment field

---

## Next Steps for Implementation

1. **Backend API Enhancement**:
   - Decide: Extend Archetype schema with caps OR create separate caps endpoint
   - Ensure inherent powers accessible via `/api/archetypes/{id}/powersets?powerset_type=inherent`
   - Test archetype endpoint returns necessary data

2. **Component Development**:
   - `CharacterSheet.tsx` - Main container, shows summary
   - `ATModifiersDisplay.tsx` - Base modifiers table
   - `CapsDisplay.tsx` - Archetype caps table
   - `InherentPowersDisplay.tsx` - Inherent powers list with icons

3. **State Integration**:
   - Connect to characterStore for name, level, archetype, origin, alignment
   - Create TanStack Query hooks: `useArchetypeCaps`, `useInherentPowers`
   - Derive character summary string from store

4. **Visual Design**:
   - Design card layouts in Figma or directly in code
   - Choose typography scale for hierarchy
   - Define color scheme (hero blue, villain red accents)
   - Select icons (archetype, origin, powers)

5. **Testing**:
   - Test with different archetypes (Tanker, Blaster, Brute, etc.)
   - Verify caps match backend calculations
   - Test inherent powers display for all ATs
   - Test responsive layout (mobile, tablet, desktop)

---

**Document Status**: ✅ Complete
**Last Updated**: 2025-11-18
**Ready for**: Epic 2.3 Implementation Planning
