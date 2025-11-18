# MidsReborn UI Analysis: Epic 2.2 - Powerset Selection

**Created**: 2025-11-18
**Epic**: 2.2 - Powerset Selection
**MidsReborn Forms Analyzed**: 
- `external/dev/MidsReborn/MidsReborn/Forms/frmMain.cs` (main form)
- `external/dev/MidsReborn/MidsReborn/UIv2/Controls/PowerList.cs` (new UI control)
- `external/dev/MidsReborn/MidsReborn/Forms/MainUILogic.cs` (business logic)

## Executive Summary

Epic 2.2 implements powerset selection for character builds. MidsReborn uses ComboBox dropdowns for primary, secondary, 4 pool powers, and ancillary/epic powersets. Powersets are filtered by archetype and validated to prevent duplicates. The key insight is that powerset selection is tightly coupled to archetype—changing the archetype resets all powersets. Pool powersets allow selection from a universal pool (all ATs), while primary/secondary/ancillary are archetype-specific.

## MidsReborn UI Components

### Component 1: Primary Powerset Selector

- **File**: `external/dev/MidsReborn/MidsReborn/Forms/frmMain.cs` (cbPrimary ComboBox)
- **Purpose**: Allows user to select their primary powerset from archetype-specific options
- **Layout**: Located in top-left character creation area, directly below archetype selector
- **Data Displayed**: 
  - Powerset display name
  - Powerset icon (16x16 sprite) drawn via OwnerDraw
  - Tooltip with powerset description on hover
- **User Interactions**:
  - Click to open dropdown with filtered primary powersets
  - Select a powerset from list
  - Hover for tooltip with description
- **Filtering Logic**: 
  ```csharp
  DatabaseAPI.GetPowersetIndexes(MidsContext.Character.Archetype, Enums.ePowerSetType.Primary)
  ```
  - Filters powersets where `powerset.ATClass == archetype.ClassName && powerset.SetType == Primary`
- **Event Handler**: `cbPrimary_SelectedIndexChanged()`
  - Calls `ChangeSets()` - Updates character powersets in MidsContext
  - Calls `UpdatePowerLists()` - Refreshes power list UI to show powers from new powerset
  - If powerset changes mid-build, all selected powers from old powerset are cleared

### Component 2: Secondary Powerset Selector

- **File**: `external/dev/MidsReborn/MidsReborn/Forms/frmMain.cs` (cbSecondary ComboBox)
- **Purpose**: Allows user to select their secondary powerset from archetype-specific options
- **Layout**: Positioned next to primary powerset selector
- **Data Displayed**: Same as primary (display name + icon)
- **User Interactions**: Same as primary
- **Filtering Logic**: 
  ```csharp
  DatabaseAPI.GetPowersetIndexes(MidsContext.Character.Archetype, Enums.ePowerSetType.Secondary)
  ```
- **Special Handling**:
  - Some powersets have `nIDLinkSecondary` - the secondary is linked to primary
  - Example: Epic ATs (Warshade, Peacebringer) have branching secondaries based on primary selection
  - When secondary is linked, it's auto-selected and cannot be changed independently
  - Tooltip shows: "This powerset is linked to your primary set and cannot be changed independently"
- **Event Handler**: `cbSecondary_SelectedIndexChanged()` - Same behavior as primary

### Component 3: Pool Power Selectors (4 slots)

- **File**: `external/dev/MidsReborn/MidsReborn/Forms/frmMain.cs` (cbPool0, cbPool1, cbPool2, cbPool3)
- **Purpose**: Allow user to select up to 4 pool powersets (universal powersets available to all ATs)
- **Layout**: 
  - Located in `poolsPanel` container
  - Vertically stacked in a dedicated "Pool Powers" section
  - Each labeled "Pool 1", "Pool 2", "Pool 3", "Pool 4"
- **Data Displayed**: 
  - Pool powerset display name + icon
  - Tooltip with pool description (see screenshot: pool-desc-mouse-over.png)
  - Tooltip includes special notes like "This pool is mutually exclusive with X"
- **User Interactions**:
  - Select from dropdown of all pool powersets
  - Can select up to 4 different pools
  - Cannot select same pool twice (validation required)
- **Filtering Logic**:
  ```csharp
  DatabaseAPI.Database.Powersets.Where(p => p?.SetType == Enums.ePowerSetType.Pool)
  ```
  - All pool powersets are universal (not filtered by archetype)
  - However, must exclude already-selected pools from other dropdowns
- **Validation**: 
  - **Client-side**: Dropdown options should exclude pools already selected in other slots
  - **No duplicate pools**: If user selects "Speed" in Pool 1, "Speed" should be disabled/hidden in Pool 2, 3, 4
- **Event Handlers**: 
  - `cbPool0_SelectedIndexChanged()`, `cbPool1_SelectedIndexChanged()`, etc.
  - All call same logic: `ChangeSets()` + `UpdatePowerLists()`

### Component 4: Ancillary/Epic Powerset Selector

- **File**: `external/dev/MidsReborn/MidsReborn/Forms/frmMain.cs` (cbAncillary ComboBox)
- **Purpose**: Allows selection of ancillary/epic powerset (endgame powersets unlocked at level 35+)
- **Layout**: 
  - Located in `poolsPanel` below the 4 pool selectors
  - Labeled "Ancillary/Epic Pool"
- **Data Displayed**: Same as other powersets (display name + icon + tooltip)
- **User Interactions**:
  - Dropdown to select from archetype-specific ancillary powersets
  - **Disabled** until character reaches level 35+
  - **Completely hidden** for Epic ATs (Peacebringer, Warshade) - they don't have ancillary pools
- **Filtering Logic**:
  ```csharp
  // From PowerList.cs BindAncillary() method
  if (archetype.DisplayName != "Peacebringer" && archetype.DisplayName != "Warshade") {
      var setList = archetype.Ancillary.Select(t => DatabaseAPI.Database.Powersets
          .FirstOrDefault(p => p?.SetType == Enums.ePowerSetType.Ancillary && p.nID.Equals(t)))
          .ToList();
  } else {
      // Disable and clear for Epic ATs
      _typeDropDown.Enabled = false;
  }
  ```
  - Filters by archetype's `Ancillary` array (list of ancillary powerset IDs available to this AT)
- **Level Requirement**:
  - Ancillary powersets have `levelAvailable = 35`
  - Selector is disabled (`Enabled = false`) when `character.Level < 35`
  - Automatically enabled when level reaches 35
- **Epic AT Special Case**:
  - Peacebringer and Warshade archetypes do NOT have ancillary pools
  - For these ATs: hide the ancillary selector entirely or show disabled state
- **Event Handler**: Standard `cbAncillary_SelectedIndexChanged()` → `ChangeSets()` + `UpdatePowerLists()`

## Feature Requirements

### MUST-HAVE Features

#### 1. Primary Powerset Selection
- **Description**: Dropdown filtered by archetype's primary powersets
- **MidsReborn Implementation**: 
  - ComboBox with OwnerDraw for icons
  - Filtered list via `DatabaseAPI.GetPowersetIndexes(archetype, Primary)`
  - Shows powerset icon (16x16) + display name
- **Web Equivalent**: 
  - shadcn/ui Select component
  - Filter powersets client-side: `powersets.filter(ps => ps.powerset_type === 'primary' && ps.archetype_id === archetypeId)`
  - Display powerset icon using Next.js Image component in Select options

#### 2. Secondary Powerset Selection
- **Description**: Dropdown filtered by archetype's secondary powersets
- **MidsReborn Implementation**: Same as primary, with special handling for linked secondaries
- **Web Equivalent**: 
  - shadcn/ui Select component
  - Filter: `powersets.filter(ps => ps.powerset_type === 'secondary' && ps.archetype_id === archetypeId)`
  - **Linked Secondary Handling**:
    - If `primaryPowerset.nIDLinkSecondary !== -1`, auto-select linked secondary
    - Disable secondary selector when linked
    - Show info tooltip explaining the link

#### 3. Pool Power Selection (4 slots)
- **Description**: 4 dropdown slots for pool powers
- **MidsReborn Implementation**: 
  - 4 separate ComboBox controls (cbPool0-3)
  - All pull from same pool powerset list
  - Manual validation to prevent duplicates
- **Web Equivalent**: 
  - Reusable `PoolPowerSelector` component instantiated 4 times
  - Each instance passes `selectedPoolIds` to filter out already-selected pools
  - Component signature:
    ```typescript
    <PoolPowerSelector
      index={0}
      value={poolPowersets[0]}
      onChange={(ps) => setPoolPowerset(0, ps)}
      excludeIds={[poolPowersets[1]?.id, poolPowersets[2]?.id, poolPowersets[3]?.id]}
    />
    ```
- **Validation**: 
  - Filter dropdown options to exclude pools selected in other slots
  - Visual indicator if user somehow selects duplicate (edge case)

#### 4. Ancillary/Epic Selection
- **Description**: Unlocks at level 35+, archetype-specific
- **MidsReborn Implementation**: 
  - ComboBox enabled when `level >= 35`
  - Disabled/hidden for Epic ATs
  - Filtered by archetype's ancillary powerset list
- **Web Equivalent**: 
  - shadcn/ui Select with conditional `disabled={level < 35}`
  - Filter: `powersets.filter(ps => ps.powerset_type === 'epic' && ps.archetype_id === archetypeId)`
  - For Epic ATs: conditionally hide component entirely or show disabled with tooltip
  - Display level requirement in tooltip: "Unlocks at level 35"

#### 5. Powerset Change Handling
- **Description**: Changing archetype resets all powersets; changing powerset clears selected powers
- **MidsReborn Implementation**: 
  - `cbAT_SelectedIndexChanged()` → `NewToon(false)` - resets entire character
  - `ChangeSets()` clears powers when powerset changes
  - Shows confirmation dialog if powers already selected
- **Web Equivalent**: 
  - Zustand store actions:
    ```typescript
    setArchetype(archetype: Archetype) {
      // Show confirmation if powersets already selected
      if (this.hasPowersets()) {
        showConfirmDialog("Changing archetype will reset powersets. Continue?");
      }
      
      // Reset all powersets
      this.primaryPowerset = null;
      this.secondaryPowerset = null;
      this.poolPowersets = [null, null, null, null];
      this.ancillaryPowerset = null;
      this.archetype = archetype;
    }
    
    setPrimaryPowerset(powerset: Powerset) {
      // Show confirmation if powers already picked from old powerset
      if (this.primaryPowerset && this.hasSelectedPowers()) {
        showConfirmDialog("Changing powerset will clear selected powers. Continue?");
      }
      
      this.primaryPowerset = powerset;
      this.clearPowersFromPowerset(this.primaryPowerset.id);
    }
    ```

### SHOULD-HAVE Features

#### 1. Powerset Icons/Images
- **Description**: Display icons for visual identification
- **MidsReborn Implementation**: 
  - OwnerDraw ComboBox with 16x16 sprite sheet
  - Icons loaded from `I9Gfx.LoadPowerSets()` async
  - Icon drawn left of powerset name
- **Web Equivalent**: 
  - Next.js Image components in Select options
  - Icon URL from powerset.icon field (e.g., `/images/powersets/archery.png`)
  - Fallback to placeholder if icon missing
  - Example:
    ```tsx
    <SelectItem value={powerset.id}>
      <div className="flex items-center gap-2">
        <Image src={powerset.icon} width={16} height={16} alt="" />
        <span>{powerset.display_name}</span>
      </div>
    </SelectItem>
    ```

#### 2. Powerset Descriptions
- **Description**: Tooltip or popover with powerset info on hover
- **MidsReborn Implementation**: 
  - Tooltip appears on mouse hover over dropdown
  - Shows `display_help` field
  - For pools: includes mutual exclusivity warnings
- **Web Equivalent**: 
  - shadcn/ui Popover or Tooltip triggered on hover
  - Display `powerset.display_help` and `powerset.display_short_help`
  - For pools: highlight special rules (mutual exclusivity, requirements)
  - Example from screenshot: "This is a pool powerset. This powerset can be changed by removing all of the powers selected from it."

#### 3. Auto-Selection for Single Option
- **Description**: If archetype has only 1 primary/secondary option, auto-select it
- **MidsReborn Implementation**: 
  - Some Epic ATs have only one primary option → auto-selected
  - Secondary is auto-selected if linked to primary
- **Web Equivalent**: 
  ```typescript
  useEffect(() => {
    if (archetype && primaryPowersets.length === 1) {
      setPrimaryPowerset(primaryPowersets[0]);
    }
  }, [archetype]);
  ```

### COULD-SKIP Features (v1 scope)

1. **Power Customization** - Deferred to Epic 3+ (power selection first)
2. **Alternate Animations** - Not in scope for initial release
3. **Epic vs Ancillary Toggle** - Simplified to one selector (both types are "epic" in backend)
4. **Powerset Respec History** - Track powerset change history (nice-to-have)

## State Management Analysis

### Server State (TanStack Query)

#### Query 1: All Powersets (Cache Strategy)
- **Query Key**: `['powersets']`
- **Endpoint**: `GET /api/archetypes/{archetypeId}/powersets`
- **Cache Strategy**: `staleTime: Infinity` (static game data, never refetch)
- **Purpose**: Fetch all powersets for selected archetype
- **Filtering**: Filter client-side by `powerset_type`
- **Why not fetch all powersets globally?**: 
  - Powersets are archetype-specific (except pools)
  - More efficient to fetch per-archetype
  - Pool powersets can be fetched separately: `GET /api/archetypes/{id}/powersets?powerset_type=pool`

#### Query 2: Archetype Powersets (Recommended)
- **Query Key**: `['archetypes', archetypeId, 'powersets']`
- **Endpoint**: `GET /api/archetypes/{archetypeId}/powersets`
- **Response**: Array of Powerset objects filtered by archetype
- **Client-side filtering**:
  ```typescript
  const primaryPowersets = powersets.filter(ps => ps.powerset_type === 'primary');
  const secondaryPowersets = powersets.filter(ps => ps.powerset_type === 'secondary');
  const epicPowersets = powersets.filter(ps => ps.powerset_type === 'epic');
  ```
- **Cache**: Forever (`staleTime: Infinity`)

#### Query 3: Pool Powersets (Universal)
- **Query Key**: `['powersets', 'pool']`
- **Endpoint**: Option A: `GET /api/archetypes/{anyArchetypeId}/powersets?powerset_type=pool`
  - OR Option B: Create new endpoint `GET /api/powersets?type=pool` (better)
- **Purpose**: Fetch all pool powersets (universal, not archetype-specific)
- **Cache**: Forever

### Client State (Zustand characterStore)

#### State Shape (additions to Epic 2.1 store)
```typescript
interface CharacterState {
  // Existing from Epic 2.1
  name: string;
  archetype: Archetype | null;
  origin: Origin | null;
  alignment: Alignment;
  
  // NEW for Epic 2.2
  primaryPowerset: Powerset | null;
  secondaryPowerset: Powerset | null;
  poolPowersets: (Powerset | null)[]; // Array of 4, initialized as [null, null, null, null]
  ancillaryPowerset: Powerset | null;
  
  level: number; // Needed for ancillary unlock logic (level 35+)
}
```

#### Actions
```typescript
interface CharacterActions {
  // NEW for Epic 2.2
  setPrimaryPowerset: (powerset: Powerset | null) => void;
  setSecondaryPowerset: (powerset: Powerset | null) => void;
  setPoolPowerset: (index: 0 | 1 | 2 | 3, powerset: Powerset | null) => void;
  setAncillaryPowerset: (powerset: Powerset | null) => void;
  
  // ENHANCED from Epic 2.1
  setArchetype: (archetype: Archetype) => void; // Now also resets all powersets
  
  // Helpers
  resetPowersets: () => void; // Clear all powersets
  hasSelectedPowersets: () => boolean; // Check if any powersets selected
}
```

#### Implementation Example
```typescript
export const useCharacterStore = create<CharacterState & CharacterActions>()(
  persist(
    (set, get) => ({
      // State
      primaryPowerset: null,
      secondaryPowerset: null,
      poolPowersets: [null, null, null, null],
      ancillaryPowerset: null,
      level: 1,
      
      // Actions
      setPrimaryPowerset: (powerset) => {
        const state = get();
        
        // Confirmation if changing existing powerset with selected powers
        if (state.primaryPowerset && state.hasSelectedPowers?.()) {
          // Show confirmation modal (handled by UI component)
          // For now, just set
        }
        
        set({ primaryPowerset: powerset });
      },
      
      setPoolPowerset: (index, powerset) => {
        const poolPowersets = [...get().poolPowersets];
        poolPowersets[index] = powerset;
        set({ poolPowersets });
      },
      
      setArchetype: (archetype) => {
        const state = get();
        
        // Confirmation if changing archetype with existing powersets
        if (state.hasSelectedPowersets()) {
          // Show confirmation (handled by UI)
        }
        
        // Reset all powersets when archetype changes
        set({
          archetype,
          primaryPowerset: null,
          secondaryPowerset: null,
          poolPowersets: [null, null, null, null],
          ancillaryPowerset: null,
        });
      },
      
      resetPowersets: () => set({
        primaryPowerset: null,
        secondaryPowerset: null,
        poolPowersets: [null, null, null, null],
        ancillaryPowerset: null,
      }),
      
      hasSelectedPowersets: () => {
        const state = get();
        return !!(
          state.primaryPowerset ||
          state.secondaryPowerset ||
          state.poolPowersets.some(p => p !== null) ||
          state.ancillaryPowerset
        );
      },
    }),
    {
      name: 'character-storage', // localStorage key
    }
  )
);
```

#### Persistence
- All character state (including powersets) automatically saved to localStorage via Zustand persist middleware (Epic 1.2)
- No manual save/load logic needed

### Derived State

#### Available Primary Powersets
```typescript
const { archetype } = useCharacterStore();
const { data: powersets } = useQuery({
  queryKey: ['archetypes', archetype?.id, 'powersets'],
  queryFn: () => fetchArchetypePowersets(archetype.id),
  enabled: !!archetype,
  staleTime: Infinity,
});

const primaryPowersets = useMemo(
  () => powersets?.filter(ps => ps.powerset_type === 'primary') ?? [],
  [powersets]
);
```

#### Available Pool Powers (exclude selected)
```typescript
const { poolPowersets } = useCharacterStore();
const selectedPoolIds = poolPowersets.filter(p => p !== null).map(p => p.id);

const availablePoolsForSlot = (slotIndex: number) => {
  const currentSelection = poolPowersets[slotIndex];
  const otherSelections = poolPowersets
    .filter((_, i) => i !== slotIndex)
    .map(p => p?.id);
  
  return allPoolPowersets.filter(
    pool => !otherSelections.includes(pool.id)
  );
};
```

#### Ancillary Enabled
```typescript
const { level, archetype } = useCharacterStore();
const isEpicAT = ['Peacebringer', 'Warshade'].includes(archetype?.name ?? '');

const ancillaryEnabled = level >= 35 && !isEpicAT;
```

## Web Component Mapping

| MidsReborn Pattern | Web Equivalent | Library/Component | Notes |
|--------------------|----------------|-------------------|-------|
| ComboBox (Primary) | Select | shadcn/ui Select | Filtered by archetype |
| ComboBox (Secondary) | Select | shadcn/ui Select | May be auto-selected if linked |
| ComboBox (Pool) × 4 | Select × 4 | shadcn/ui Select (reusable) | Each filters out other selections |
| ComboBox (Ancillary) | Select (conditional) | shadcn/ui Select | Disabled until level 35, hidden for Epic ATs |
| OwnerDraw icons | Image in Select option | Next.js Image | 16x16 powerset icons |
| Tooltip (info) | Popover/Tooltip | shadcn/ui Popover | Show display_help on hover |
| Confirmation Dialog | AlertDialog | shadcn/ui AlertDialog | When changing AT/powerset |

## API Integration Points

### Backend Endpoints Needed

#### 1. GET /api/archetypes/{archetype_id}/powersets
- **Purpose**: Fetch all powersets for an archetype
- **Query Params**: 
  - `powerset_type` (optional): Filter by type (primary, secondary, pool, epic)
- **Response**: 
  ```typescript
  [
    {
      id: 1,
      name: "Archery",
      display_name: "Archery",
      display_help: "Archery provides ranged attacks...",
      powerset_type: "primary",
      archetype_id: 5, // Blaster
      icon: "/images/powersets/archery.png",
    },
    // ...
  ]
  ```
- **Status**: ✅ Already implemented in `backend/app/routers/archetypes.py`

#### 2. GET /api/powersets/{powerset_id}
- **Purpose**: Get single powerset details
- **Response**: Same as above (single object)
- **Status**: ✅ Already implemented in `backend/app/routers/powersets.py`

#### 3. GET /api/powersets/{powerset_id}/powers
- **Purpose**: Get all powers in a powerset (for next epic - power selection)
- **Response**: Array of Power objects
- **Status**: ✅ Already implemented

#### 4. (Optional) GET /api/powersets?powerset_type=pool
- **Purpose**: Get all pool powersets (universal across ATs)
- **Alternative**: Use `GET /api/archetypes/{any_id}/powersets?powerset_type=pool` (less clean)
- **Status**: ⚠️ Not implemented, but can use existing archetype endpoint

### TypeScript Types

```typescript
// backend/app/schemas.py already defines these, need to create TS equivalents

interface Powerset {
  id: number;
  name: string; // Internal name (e.g., "Blaster_Ranged.Archery")
  display_name: string; // User-facing name (e.g., "Archery")
  display_fullname?: string;
  display_help?: string; // Long description
  display_short_help?: string; // Short description
  powerset_type: 'primary' | 'secondary' | 'pool' | 'epic' | 'incarnate';
  archetype_id: number | null; // null for universal pools
  icon?: string; // URL to icon image
  created_at: string;
  updated_at: string;
}

interface PowersetWithPowers extends Powerset {
  powers: Power[];
}
```

## Screenshot Analysis

### Available Screenshots

Location: `/home/user/mids-hero-web/shared/user/midsreborn-screenshots`

#### 1. mids-new-build.png
- **Shows**: Main build window with complete powerset selection UI
- **Relevant Elements**:
  - Top-left: Name input, Archetype dropdown (Blaster selected), Origin dropdown (Magic)
  - Below archetype: "Primary Power Set" dropdown showing "Archery"
  - Next to it: "Secondary Power Set" dropdown showing "Atomic Manipulation"
  - Left sidebar: Power lists for Primary and Secondary (Snap Shot, Aimed Shot, etc.)
  - Center area: Power level columns (1, 10, 22, 35) with slot rows
  - Not visible in this screenshot: Pool power selectors (likely scrolled down)
- **Key Insights**:
  - Powerset selectors are prominently placed near top
  - Icons displayed for each powerset (Archery has bow icon, Atomic has atom icon)
  - Clean dropdown UI with clear labels

#### 2. pool-desc-mouse-over.png
- **Shows**: Pool power selection interface with tooltip popup
- **Relevant Elements**:
  - Left sidebar showing "Pool 1", "Pool 2", "Pool 3", "Pool 4" dropdowns
  - Pool 2 has "Experimentation" selected
  - Tooltip popup displays:
    - Title: "Experimentation"
    - Subtitle: "Archetype: All" (indicates pool is universal)
    - "Set Type: Pool" (confirms powerset type)
    - Detailed description of pool powers
    - Special note: "Note: this pool is mutually exclusive with Force of Will and Sorcery."
    - Warning in blue: "This is a pool powerset. This powerset can be changed by removing all of the powers selected from it."
  - Below pools: "Ancillary/Epic Pool" dropdown showing "Arsenal Mastery"
  - Pool powers listed: Boxing, Kick, Tough, Weave, Cross Punch (from "Fighting" pool)
  - Flight pool: Hover, Air Superiority, Fly, Group Fly, Evasive Maneuvers
- **Key Insights**:
  - 4 pool slots clearly separated
  - Ancillary selector placed after pools
  - Tooltips are detailed and informative
  - Mutual exclusivity rules exist for some pools (must implement!)
  - Pools can be changed by removing selected powers (confirmation dialog)

### Additional Screenshots Recommended

These would be helpful but are not critical blockers:

#### 1. Primary Powerset Dropdown Open
- **Filename suggestion**: `midsreborn-primary-powerset-dropdown.png`
- **Should show**: Dropdown expanded with list of primary powersets for specific AT
- **Needed for**: Understanding dropdown item layout, icon positioning

#### 2. Archetype Change Confirmation Dialog
- **Filename suggestion**: `midsreborn-archetype-change-confirm.png`
- **Should show**: Dialog asking user to confirm archetype change when powersets selected
- **Needed for**: Understanding confirmation flow and messaging

#### 3. Ancillary Selector Disabled State
- **Filename suggestion**: `midsreborn-ancillary-disabled.png`
- **Should show**: Ancillary dropdown disabled (grayed out) when level < 35
- **Needed for**: Visual design of disabled state

## Implementation Notes

### Key Behaviors to Replicate

#### 1. Archetype Change Resets Powersets
- **MidsReborn Behavior**: 
  - Changing archetype calls `NewToon(false)` which creates fresh character
  - All powersets reset to null
  - Shows confirmation if powersets already selected
- **Web Implementation**:
  ```typescript
  const handleArchetypeChange = (newArchetype: Archetype) => {
    const hasExistingPowersets = hasSelectedPowersets();
    
    if (hasExistingPowersets) {
      showConfirmDialog({
        title: "Change Archetype?",
        description: "Changing your archetype will reset all selected powersets. This cannot be undone.",
        onConfirm: () => {
          setArchetype(newArchetype); // Triggers reset in store
        }
      });
    } else {
      setArchetype(newArchetype);
    }
  };
  ```

#### 2. Pool Power Validation (No Duplicates)
- **MidsReborn Behavior**: 
  - User can open any pool dropdown
  - However, selecting same pool in multiple slots would cause issues
  - Implicit validation (not enforced in UI but logically prevented)
- **Web Implementation**:
  ```typescript
  // In PoolPowerSelector component
  const availableOptions = useMemo(() => {
    const otherSelectedIds = excludeIds.filter(id => id !== undefined);
    return allPoolPowersets.filter(pool => !otherSelectedIds.includes(pool.id));
  }, [allPoolPowersets, excludeIds]);
  ```
  - Each pool dropdown only shows pools NOT selected in other slots
  - As user selects pools, available options in other dropdowns update reactively

#### 3. Ancillary Level Lock
- **MidsReborn Behavior**: 
  - Ancillary ComboBox has `Enabled = (level >= 35)`
  - Grayed out and non-clickable when disabled
  - Tooltip shows "Unlocks at level 35"
- **Web Implementation**:
  ```typescript
  <Select 
    disabled={level < 35 || isEpicAT}
    value={ancillaryPowerset?.id}
    onValueChange={handleAncillaryChange}
  >
    <SelectTrigger>
      <SelectValue placeholder={
        isEpicAT 
          ? "Not available for Epic archetypes" 
          : level < 35 
            ? "Unlocks at level 35" 
            : "Select ancillary powerset"
      } />
    </SelectTrigger>
    {/* ... */}
  </Select>
  ```

#### 4. Powerset Change Clears Powers
- **MidsReborn Behavior**: 
  - When user changes primary/secondary powerset, all powers from old powerset are cleared
  - Shows confirmation dialog: "Changing powerset will clear all selected powers. Continue?"
  - If user confirms, powerset changes and power list updates
- **Web Implementation**:
  ```typescript
  const setPrimaryPowerset = (newPowerset: Powerset) => {
    const hasSelectedPowers = /* check if powers selected from current primary */;
    
    if (currentPrimaryPowerset && hasSelectedPowers) {
      showConfirmDialog({
        title: "Change Primary Powerset?",
        description: "This will clear all powers you've selected from the current powerset.",
        onConfirm: () => {
          // Clear powers from old powerset
          clearPowersFromPowerset(currentPrimaryPowerset.id);
          // Set new powerset
          store.primaryPowerset = newPowerset;
        }
      });
    } else {
      store.primaryPowerset = newPowerset;
    }
  };
  ```
  - Note: Power selection is Epic 2.3+, so this logic will be implemented then

### UX Improvements for Web

#### 1. Search/Filter in Dropdowns
- **MidsReborn**: Standard ComboBox (no search)
- **Web Enhancement**: Use shadcn/ui Combobox (with Command) for searchable powersets
- **Benefit**: Easier to find powersets, especially pools (20+ options)
- **Example**:
  ```tsx
  <Combobox>
    <ComboboxInput placeholder="Search powersets..." />
    <ComboboxList>
      {filteredPowersets.map(ps => (
        <ComboboxItem key={ps.id} value={ps.id}>
          {ps.display_name}
        </ComboboxItem>
      ))}
    </ComboboxList>
  </Combobox>
  ```

#### 2. Visual Feedback for Selection
- **MidsReborn**: Selected powerset shown in ComboBox (closed state)
- **Web Enhancement**: 
  - Highlight selected powerset selector (border color change)
  - Show checkmark icon next to selected option in dropdown
  - Animate powerset change (subtle fade transition)

#### 3. Responsive Design
- **MidsReborn**: Fixed desktop layout
- **Web Design**:
  - **Desktop (>768px)**: Horizontal layout
    - Primary and Secondary side-by-side
    - Pools in 2x2 grid or vertical list
  - **Mobile (<768px)**: Vertical stack
    - Primary → Secondary → Pools (stacked) → Ancillary
  - Use CSS Grid for flexible layout

#### 4. Loading States
- **Show skeleton loaders** while fetching powersets from API
- **Disable selectors** until archetype is selected
- **Empty state message**: "Select an archetype to choose powersets"

## Warnings & Edge Cases

### Edge Case 1: Archetype with Limited Powersets

- **Scenario**: Some Epic ATs have only 1 primary and 1 secondary powerset
- **Example**: Warshade has "Umbral Blast" (only primary), "Umbral Aura" (only secondary)
- **MidsReborn Behavior**: 
  - Dropdowns still shown but with single option
  - Auto-selected by default (SelectedIndex = 0)
- **Web Behavior**: 
  - **Option A**: Auto-select and hide dropdown (cleaner UX)
  - **Option B**: Show disabled dropdown with only option (preserves consistency)
  - **Recommended**: Option A with informational text: "Primary: Umbral Blast (only option)"
- **Implementation**:
  ```typescript
  useEffect(() => {
    if (primaryPowersets.length === 1) {
      setPrimaryPowerset(primaryPowersets[0]);
    }
  }, [primaryPowersets]);
  
  if (primaryPowersets.length === 1) {
    return (
      <div className="flex items-center gap-2">
        <Label>Primary Powerset</Label>
        <div className="flex items-center gap-2">
          <Image src={primaryPowersets[0].icon} width={16} height={16} />
          <span>{primaryPowersets[0].display_name}</span>
          <span className="text-muted-foreground text-sm">(only option)</span>
        </div>
      </div>
    );
  }
  ```

### Edge Case 2: Changing Powerset Mid-Build

- **Scenario**: User has selected 10 powers from "Archery" primary, then switches to "Assault Rifle"
- **MidsReborn Behavior**: 
  - Shows confirmation: "Changing powerset will remove all selected powers from Archery. Continue?"
  - If user confirms: All 10 powers cleared, powerset changed, power list refreshed
  - If user cancels: Powerset stays as "Archery"
- **Web Behavior**: Same - confirmation dialog before destructive action
- **Implementation**: See "Powerset Change Clears Powers" above
- **Note**: This is for Epic 2.3+ when power selection is implemented

### Edge Case 3: Pool Power Order

- **Scenario**: User selects pools in order: Speed, Leaping, Fighting, Flight
- **MidsReborn Behavior**: 
  - Order doesn't matter functionally
  - Powers can be picked from any pool in any order
  - Pool order is just visual organization
- **Web Behavior**: Same - order is cosmetic only
- **Optional Enhancement**: Allow drag-and-drop reordering of pool slots (nice-to-have)
- **Implementation**:
  ```typescript
  // Slot order doesn't affect game mechanics, just display
  const reorderPoolSlot = (fromIndex: number, toIndex: number) => {
    const newPools = [...poolPowersets];
    const [moved] = newPools.splice(fromIndex, 1);
    newPools.splice(toIndex, 0, moved);
    setPoolPowersets(newPools);
  };
  ```

### Edge Case 4: Epic AT vs Normal AT

- **Scenario**: User selects Peacebringer or Warshade (Epic ATs)
- **MidsReborn Behavior**: 
  - Pool selectors hidden or disabled (Epic ATs don't have pool powers)
  - Ancillary selector hidden (Epic ATs don't have ancillary pools)
  - Only Primary and Secondary powersets available
- **Web Behavior**: 
  - Conditionally hide pool and ancillary sections for Epic ATs
  - Show informational message: "Epic Archetypes do not have access to Pool or Ancillary powers"
- **Implementation**:
  ```typescript
  const isEpicAT = ['Peacebringer', 'Warshade', 'Arachnos Soldier', 'Arachnos Widow'].includes(archetype?.name ?? '');
  
  return (
    <>
      <PrimaryPowersetSelector />
      <SecondaryPowersetSelector />
      
      {!isEpicAT && (
        <>
          <PoolPowerSelectors />
          <AncillarySelector />
        </>
      )}
      
      {isEpicAT && (
        <InfoBox>
          Epic Archetypes have unique power structures and do not have access to Pool or Ancillary power pools.
        </InfoBox>
      )}
    </>
  );
  ```

### Edge Case 5: Linked Secondary Powersets

- **Scenario**: Some ATs have secondaries linked to primary (e.g., Dominator branching)
- **MidsReborn Behavior**: 
  - If `powerset.nIDLinkSecondary > -1`, secondary is auto-selected when primary changes
  - Secondary dropdown disabled (grayed out)
  - Tooltip: "This secondary is linked to your primary powerset"
- **Web Behavior**: Same
- **Implementation**:
  ```typescript
  useEffect(() => {
    if (primaryPowerset?.linked_secondary_id) {
      const linkedSecondary = secondaryPowersets.find(
        ps => ps.id === primaryPowerset.linked_secondary_id
      );
      if (linkedSecondary) {
        setSecondaryPowerset(linkedSecondary);
      }
    }
  }, [primaryPowerset]);
  
  const isSecondaryLinked = !!primaryPowerset?.linked_secondary_id;
  
  <Select 
    disabled={isSecondaryLinked}
    value={secondaryPowerset?.id}
  >
    {/* ... */}
  </Select>
  
  {isSecondaryLinked && (
    <InfoText>Secondary powerset is linked to your primary selection</InfoText>
  )}
  ```

### Warning: Pool Mutual Exclusivity

- **Discovery from Screenshot**: Some pools are mutually exclusive
- **Example**: "Experimentation" is exclusive with "Force of Will" and "Sorcery"
- **MidsReborn Behavior**: Likely prevented at power selection time (not dropdown level)
- **Web Behavior**: 
  - **Option A**: Filter out mutually exclusive pools from dropdown (proactive)
  - **Option B**: Show warning when user selects conflicting pool (reactive)
  - **Recommended**: Option B for v1 (simpler), Option A for v2 (better UX)
- **Implementation**: 
  ```typescript
  // Add to Powerset type
  interface Powerset {
    // ... existing fields
    mutually_exclusive_with?: number[]; // IDs of exclusive powersets
  }
  
  // In pool selector
  const isMutuallyExclusive = (pool: Powerset) => {
    const selectedPoolIds = poolPowersets.map(p => p?.id).filter(Boolean);
    return pool.mutually_exclusive_with?.some(id => selectedPoolIds.includes(id));
  };
  
  const filteredPools = allPoolPowersets.filter(pool => {
    const alreadySelected = selectedPoolIds.includes(pool.id);
    const mutuallyExclusive = isMutuallyExclusive(pool);
    return !alreadySelected && !mutuallyExclusive;
  });
  ```
- **Note**: Need to confirm if mutual exclusivity data exists in database. If not, may need to hardcode rules or defer to Epic 2.3.

---

## Recommended Component Breakdown

Based on MidsReborn analysis, suggested component hierarchy:

### 1. PowersetSelector.tsx (Reusable Base)
```typescript
interface PowersetSelectorProps {
  label: string;
  powersets: Powerset[];
  value: Powerset | null;
  onChange: (powerset: Powerset | null) => void;
  disabled?: boolean;
  placeholder?: string;
  showIcons?: boolean;
}

export function PowersetSelector({ ... }: PowersetSelectorProps) {
  return (
    <div className="space-y-2">
      <Label>{label}</Label>
      <Select value={value?.id} onValueChange={(id) => {
        const ps = powersets.find(p => p.id === Number(id));
        onChange(ps ?? null);
      }}>
        <SelectTrigger disabled={disabled}>
          <SelectValue placeholder={placeholder} />
        </SelectTrigger>
        <SelectContent>
          {powersets.map(ps => (
            <SelectItem key={ps.id} value={ps.id.toString()}>
              <div className="flex items-center gap-2">
                {showIcons && ps.icon && (
                  <Image src={ps.icon} width={16} height={16} alt="" />
                )}
                <span>{ps.display_name}</span>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
```

### 2. PrimaryPowersetSelector.tsx
```typescript
export function PrimaryPowersetSelector() {
  const { archetype, primaryPowerset, setPrimaryPowerset } = useCharacterStore();
  const { data: powersets } = useArchetypePowersets(archetype?.id);
  
  const primaryOptions = useMemo(
    () => powersets?.filter(ps => ps.powerset_type === 'primary') ?? [],
    [powersets]
  );
  
  // Auto-select if only one option
  useEffect(() => {
    if (primaryOptions.length === 1 && !primaryPowerset) {
      setPrimaryPowerset(primaryOptions[0]);
    }
  }, [primaryOptions]);
  
  return (
    <PowersetSelector
      label="Primary Powerset"
      powersets={primaryOptions}
      value={primaryPowerset}
      onChange={setPrimaryPowerset}
      disabled={!archetype}
      placeholder="Select primary powerset"
      showIcons
    />
  );
}
```

### 3. SecondaryPowersetSelector.tsx
Similar to Primary, with linked secondary logic

### 4. PoolPowerSelector.tsx
```typescript
interface PoolPowerSelectorProps {
  index: 0 | 1 | 2 | 3;
  label: string;
}

export function PoolPowerSelector({ index, label }: PoolPowerSelectorProps) {
  const { poolPowersets, setPoolPowerset } = useCharacterStore();
  const { data: allPools } = usePoolPowersets();
  
  const selectedValue = poolPowersets[index];
  const otherSelections = poolPowersets
    .filter((_, i) => i !== index)
    .map(p => p?.id)
    .filter(Boolean);
  
  const availableOptions = useMemo(
    () => allPools?.filter(pool => !otherSelections.includes(pool.id)) ?? [],
    [allPools, otherSelections]
  );
  
  return (
    <PowersetSelector
      label={label}
      powersets={availableOptions}
      value={selectedValue}
      onChange={(ps) => setPoolPowerset(index, ps)}
      placeholder="Select pool power"
      showIcons
    />
  );
}
```

### 5. PoolPowerSelectors.tsx (Container for 4 slots)
```typescript
export function PoolPowerSelectors() {
  const { archetype } = useCharacterStore();
  const isEpicAT = ['Peacebringer', 'Warshade'].includes(archetype?.name ?? '');
  
  if (isEpicAT) {
    return null; // Hide for Epic ATs
  }
  
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Pool Powers</h3>
      <div className="grid gap-3">
        <PoolPowerSelector index={0} label="Pool Power 1" />
        <PoolPowerSelector index={1} label="Pool Power 2" />
        <PoolPowerSelector index={2} label="Pool Power 3" />
        <PoolPowerSelector index={3} label="Pool Power 4" />
      </div>
    </div>
  );
}
```

### 6. AncillarySelector.tsx
```typescript
export function AncillarySelector() {
  const { archetype, level, ancillaryPowerset, setAncillaryPowerset } = useCharacterStore();
  const { data: powersets } = useArchetypePowersets(archetype?.id);
  
  const isEpicAT = ['Peacebringer', 'Warshade'].includes(archetype?.name ?? '');
  const isDisabled = level < 35 || isEpicAT;
  
  const ancillaryOptions = useMemo(
    () => powersets?.filter(ps => ps.powerset_type === 'epic') ?? [],
    [powersets]
  );
  
  if (isEpicAT) {
    return null; // Hide for Epic ATs
  }
  
  return (
    <div className="space-y-2">
      <PowersetSelector
        label="Ancillary / Epic Pool"
        powersets={ancillaryOptions}
        value={ancillaryPowerset}
        onChange={setAncillaryPowerset}
        disabled={isDisabled}
        placeholder={level < 35 ? "Unlocks at level 35" : "Select ancillary powerset"}
        showIcons
      />
      {level < 35 && (
        <p className="text-sm text-muted-foreground">
          Ancillary pools unlock at level 35
        </p>
      )}
    </div>
  );
}
```

### 7. PowersetSelectionPanel.tsx (Main Container)
```typescript
export function PowersetSelectionPanel() {
  const { archetype } = useCharacterStore();
  
  if (!archetype) {
    return (
      <div className="text-center text-muted-foreground py-8">
        Select an archetype to choose powersets
      </div>
    );
  }
  
  return (
    <div className="space-y-6">
      <div className="grid md:grid-cols-2 gap-4">
        <PrimaryPowersetSelector />
        <SecondaryPowersetSelector />
      </div>
      
      <Separator />
      
      <PoolPowerSelectors />
      
      <Separator />
      
      <AncillarySelector />
    </div>
  );
}
```

---

## Next Steps

1. ✅ **Analysis Complete** - This document
2. **Create TypeScript Interfaces** - Define Powerset types matching backend schemas
3. **Implement Zustand Store Extensions** - Add powerset state + actions to characterStore
4. **Create TanStack Query Hooks** - `useArchetypePowersets()`, `usePoolPowersets()`
5. **Build Base Components** - PowersetSelector, then specialized variants
6. **Integrate with Character Creation Panel** - Add PowersetSelectionPanel to Epic 2.1 UI
7. **Add Confirmation Dialogs** - For archetype/powerset changes
8. **Testing** - Validate filtering, validation, state persistence
9. **Visual Polish** - Icons, tooltips, loading states

---

**Analysis Completed**: 2025-11-18
**Ready for**: Implementation Planning (Epic 2.2)
