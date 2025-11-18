# MidsReborn UI Analysis: Epic 4.1 - Defense & Resistance Displays

**Created**: 2025-11-18
**Epic**: 4.1 - Defense & Resistance Displays
**MidsReborn Forms Analyzed**: frmTotals.cs, frmTotalsV2.cs, CtlMultiGraph.cs

## Executive Summary

The MidsReborn Totals window displays character defense and resistance statistics using custom horizontal bar graphs. Defense values are shown in purple/magenta, resistance in cyan/teal, with all 11 defense types (8 typed + 3 positional) and 8 resistance types displayed as percentage values with visual bars. The implementation uses a custom `CtlMultiGraph` control that renders bars using SkiaSharp, with tooltips providing detailed breakdowns and cap information.

## MidsReborn UI Components

### Component 1: frmTotals (Original Implementation)

- **File**: `external/dev/MidsReborn/MidsReborn/Forms/WindowMenuItems/frmTotals.cs`
- **Purpose**: Main totals window showing all character statistics including defense, resistance, health, and endurance
- **Layout**: Tabbed interface with three panels:
  - Tab 0: "Survival" - Defense, Resistance, Health & Endurance (pnlDRHE)
  - Tab 1: "Misc Buffs" - Movement, Stealth, ToHit, Accuracy, Damage, etc. (pnlMisc)
  - Tab 2: "Status" - Status Protection, Resistance, Debuff Resistance (pnlStatus)

- **Data Displayed**: 
  - **Defense**: 
    - 8 Typed: Smashing, Lethal, Fire, Cold, Energy, Negative, Toxic (conditional), Psionic
    - 3 Positional: Melee, Ranged, AoE
  - **Resistance**: 
    - 8 Typed: Smashing, Lethal, Fire, Cold, Energy, Negative, Toxic, Psionic
  - **Health**: Regeneration percentage, Max HP
  - **Endurance**: End Recovery, End Use, Max End

- **User Interactions**: 
  - Hover over bars to see detailed tooltips
  - Click tabs to switch between stat categories
  - Toggle "Keep On Top" to keep window above main UI
  - Close button to dismiss window

- **Bar Rendering**: Uses `CtlMultiGraph` custom control
  - Each stat is added via `AddItem(label, value, enhancedValue, tooltip)`
  - Defense bars: Purple gradient (`ColorBase = #C000C0`)
  - Resistance bars: Cyan gradient (`ColorBase = #00C0C0`)
  - Health bars: Green gradient (`ColorBase = #60C060`)
  - Endurance bars: Blue gradient (`ColorBase = #4040C0`)

- **Cap Indicators**: 
  - Resistance shows when values exceed archetype cap
  - Tooltip displays "capped at X%" message
  - Different tooltip text for capped vs uncapped values

### Component 2: frmTotalsV2 (Modern Implementation)

- **File**: `external/dev/MidsReborn/MidsReborn/Forms/WindowMenuItems/frmTotalsV2.cs`
- **Purpose**: Redesigned totals window with improved layout and visual design
- **Layout**: Four-tab interface using custom tab strip control:
  - Tab 1: "Core Stats" - Defense, Resistance, Health, Endurance
  - Tab 2: "Misc Buffs" - Movement, Perception, Haste, ToHit, Accuracy, Damage, etc.
  - Tab 3: "Status Protection" - Mez protection and resistance
  - Tab 4: "Debuff Resistances" - Debuff resistance and Elusivity

- **Key Improvements**:
  - Uses `AddItemPair()` for cleaner API
  - Better tooltip formatting with `GenericDataTooltip3()` helper
  - Displays base, capped, and uncapped values separately
  - Shows absorb shield as separate bar layer on HP
  - Dynamic panel sizing based on content height
  - Hero/Villain color scheme support

- **Bar Configuration**:
  - Defense: 11 items, Max: 100%, Border: BlueViolet, Bar: Magenta
  - Resistance: 8 items, Max: 100%, Border: LightSeaGreen, Bar: Cyan, Overcap color: Pink
  - HP: 2 items, Max: 4000, Border: PaleGreen, Bar: Green with absorb layer
  - Endurance: 3 items, Max: 100, Border: RoyalBlue, Bar: Blue

### Component 3: CtlMultiGraph (Custom Graph Control)

- **File**: `external/dev/MidsReborn/MidsReborn/Controls/ctlMultiGraph.cs`
- **Purpose**: Reusable horizontal bar graph control for displaying stats
- **Rendering**: Uses SkiaSharp for hardware-accelerated graphics
- **Key Properties**:
  - `ColorBase`: Main bar color
  - `ColorEnh`: Enhancement/secondary bar color
  - `ColorFadeStart/End`: Gradient colors for bar fill
  - `ColorHighlight`: Hover highlight color
  - `ColorOvercap`: Color for values exceeding cap
  - `ItemHeight`: Height of each bar row (default 10-13px)
  - `TextWidth`: Width reserved for labels (default 187px)
  - `Max`: Maximum value for scale (100 for percentages)
  - `MarkerValue`: Optional marker line (e.g., for 100% baseline)
  - `Border`: Draw outer border
  - `Lines`: Draw separator lines between items
  - `Dual`: Show two bars per item (base + enhancement)
  - `Overcap`: Highlight values exceeding cap
  - `Style`: GraphStyle enum (baseOnly, enhOnly, Stacked)

- **Bar Styles**:
  - `baseOnly`: Single bar showing total value
  - `enhOnly`: Single bar for enhancement values
  - `Stacked`: Multiple bars stacked (base + enhancements + overcap)

## Feature Requirements

### MUST-HAVE Features

1. **Typed Defense Display**
   - **Description**: Show defense percentages for all 8 damage types (Smashing, Lethal, Fire, Cold, Energy, Negative, Toxic, Psionic)
   - **MidsReborn Implementation**: Vertical list of horizontal bars, purple color, format "{type}| {value}%", max 100%, shows all values including 0%
   - **Web Equivalent**: StatBar component for each defense type using Tailwind width percentage, purple gradient background

2. **Positional Defense Display**
   - **Description**: Show defense for Melee, Ranged, AoE
   - **MidsReborn Implementation**: Same purple bars in same list as typed defense, no visual distinction
   - **Web Equivalent**: StatBar component for each position, same styling as typed defense

3. **Typed Resistance Display**
   - **Description**: Show resistance percentages for all 8 damage types
   - **MidsReborn Implementation**: Vertical list of horizontal bars, cyan/teal color, shows capped value with tooltip for overcap, max 100%
   - **Web Equivalent**: StatBar component for each resistance type, cyan gradient, show overcap indicator when value exceeds archetype cap

4. **Visual Bar Graphs**
   - **Description**: Horizontal bars showing stat magnitude as percentage of max
   - **MidsReborn Implementation**: Custom SkiaSharp rendering with gradient fills, borders, and optional markers
   - **Web Equivalent**: Custom StatBar component using Tailwind:
     ```tsx
     <div className="relative h-3 bg-black border border-purple-500 rounded-sm">
       <div 
         className="h-full bg-gradient-to-r from-purple-900 to-purple-500 transition-all"
         style={{ width: `${(value / max) * 100}%` }}
       />
     </div>
     ```

5. **Cap Indicators**
   - **Description**: Show when defense/resistance reaches or exceeds cap
   - **MidsReborn Implementation**: 
     - Resistance uses `ColorOvercap` (pink/red) when value exceeds archetype cap
     - Tooltip shows "capped at X%" message with original uncapped value
     - MarkerValue property can draw a line at cap threshold
   - **Web Equivalent**: 
     - Conditional bar color change when at cap
     - Border color change or glow effect
     - Tooltip shows "Capped at {archetype.resCap * 100}% (Original: {uncappedValue}%)"

6. **Percentage Labels**
   - **Description**: Display percentage values next to bars
   - **MidsReborn Implementation**: Text drawn at `TextWidth` pixels from left, format "{value}%" or "{value:##0.##}%"
   - **Web Equivalent**: Flex layout with label on left, value on right side of bar

7. **Tooltips**
   - **Description**: Detailed information on hover
   - **MidsReborn Implementation**: ToolTip control with formatted strings showing:
     - "{value}% {type} defense/resistance"
     - Archetype cap information for resistance
     - Base vs enhanced breakdown
     - Capped vs uncapped values
   - **Web Equivalent**: shadcn/ui Tooltip or Radix Tooltip component with formatted JSX content

8. **Zero Value Display**
   - **Description**: Show 0% for stats with no bonuses (don't hide rows)
   - **MidsReborn Implementation**: All defense/resistance types always shown, even at 0%
   - **Web Equivalent**: Always render all stat rows, show "0%" text and empty bar

### SHOULD-HAVE Features

1. **Detailed Breakdown Tooltips**
   - Show which powers contribute to each stat
   - Show base value, enhancement bonuses, set bonuses separately
   - **Defer to**: Later epic focusing on power contribution breakdowns

2. **Real-time Updates**
   - Totals update immediately when build changes
   - Smooth animation when bars change
   - **Implementation**: React state updates trigger re-render, use Framer Motion for bar width transitions

3. **Separate Sections for Defense vs Resistance**
   - Visual grouping with section headers
   - Different background colors for sections
   - **Implementation**: Separate components `DefensePanel` and `ResistancePanel`, section header labels

4. **Responsive Layout**
   - Stack sections vertically on mobile
   - Horizontal layout on desktop if space permits
   - **Implementation**: Tailwind responsive classes

### COULD-SKIP Features

1. **Export totals to clipboard**
   - Copy stats as formatted text
   - **Rationale**: Low priority for MVP

2. **Per-power contribution graph**
   - Show which powers contribute how much to each stat
   - **Rationale**: Complex feature, defer to later epic

3. **Historical comparison**
   - Compare current build to previous versions
   - **Rationale**: Requires build versioning system

## State Management Analysis

### Server State (TanStack Query)

- **Endpoint**: `POST /api/calculations/totals`
- **Request Data**: 
  ```typescript
  {
    buildId: string,
    archetype: string,
    level: number,
    powers: SelectedPower[],  // Array of { powerId, level, slots: EnhancementSlot[] }
    // ... other build data
  }
  ```
- **Response Data**: 
  ```typescript
  {
    defense: {
      smashing: number,      // 0-100+
      lethal: number,
      fire: number,
      cold: number,
      energy: number,
      negative: number,
      toxic: number,
      psionic: number,
      melee: number,         // Positional
      ranged: number,
      aoe: number
    },
    resistance: {
      smashing: number,      // 0-100+
      lethal: number,
      fire: number,
      cold: number,
      energy: number,
      negative: number,
      toxic: number,
      psionic: number
    },
    resistanceCapped: {      // Values capped at archetype limit
      smashing: number,
      lethal: number,
      fire: number,
      cold: number,
      energy: number,
      negative: number,
      toxic: number,
      psionic: number
    },
    health: {
      regeneration: number,   // Percentage
      maxHp: number,         // Numeric
      absorb: number         // Absorb shield amount
    },
    endurance: {
      recovery: number,       // Per second
      usage: number,         // Per second
      maxEnd: number         // Numeric
    },
    // ... other stats
  }
  ```

- **Caching Strategy**: 
  - **NO caching** - Always recalculate on demand
  - **Rationale**: Build changes frequently during character creation, stale data causes confusion
  - **Implementation**: 
    ```typescript
    const { data: totals, mutate: calculateTotals } = useMutation({
      mutationKey: ['calculations', 'totals'],
      mutationFn: (buildData: BuildData) => api.post('/calculations/totals', buildData),
      gcTime: 0, // Don't cache
    });
    ```

- **Trigger**: 
  - Manual trigger via "Calculate Totals" button
  - Auto-trigger on power selection change (debounced 500ms)
  - Auto-trigger on enhancement slotting (debounced 500ms)

### Client State (Zustand)

- **Store**: `characterStore` (existing from Epic 1.2)
- **State Shape**:
  ```typescript
  {
    totals: CalculatedTotals | null,
    isCalculating: boolean,
    lastCalculated: Date | null,
    // ... existing build state
  }
  ```

- **Actions**: 
  ```typescript
  {
    setTotals: (totals: CalculatedTotals) => void,
    setCalculating: (isCalculating: boolean) => void,
    recalculate: async () => Promise<void>,
    // Triggers calculation mutation and updates store
  }
  ```

- **Automatic Triggers**:
  - Watch `powers` array changes → auto-recalculate
  - Watch `enhancements` array changes → auto-recalculate
  - Watch `level` changes → auto-recalculate
  - Use Zustand middleware to observe changes and trigger mutation

### Derived State

- **Cap Indicators**: 
  ```typescript
  const isAtCap = (value: number, cap: number) => value >= cap * 100;
  const defenseCap = 45; // Soft-cap, or 50 for Tanker/Brute
  const resistanceCap = archetype.resCap * 100; // 75 or 90
  ```

- **Bar Widths**: 
  ```typescript
  const barWidth = Math.min((value / 100) * 100, 100); // Cap at 100% width
  ```

- **Color Classes**: 
  ```typescript
  const defenseBarClass = "bg-gradient-to-r from-purple-900 to-purple-500";
  const resistanceBarClass = "bg-gradient-to-r from-cyan-900 to-cyan-500";
  const overcapClass = "bg-gradient-to-r from-red-900 to-red-500"; // When exceeds cap
  ```

- **Tooltip Content**:
  ```typescript
  const getDefenseTooltip = (type: string, value: number) => 
    `${value.toFixed(2)}% ${type} defense`;
  
  const getResistanceTooltip = (type: string, value: number, capped: number, cap: number) => 
    value > capped 
      ? `${value.toFixed(2)}% ${type} resistance, capped at ${cap}%`
      : `${capped.toFixed(2)}% ${type} resistance (${archetype} cap: ${cap}%)`;
  ```

## Web Component Mapping

| MidsReborn Pattern | Web Equivalent | Library/Component |
| ------------------ | -------------- | ----------------- |
| frmTotals window | TotalsPanel component | Custom React component |
| Tab control (pnlDRHE, pnlMisc, pnlStatus) | Tabs component | shadcn/ui Tabs |
| CtlMultiGraph (Defense) | DefenseStats component | Custom with multiple StatBar |
| CtlMultiGraph (Resistance) | ResistanceStats component | Custom with multiple StatBar |
| Single bar item | StatBar component | Custom div with Tailwind |
| AddItem(label, value, enhValue, tooltip) | <StatBar label={} value={} tooltip={} /> | React props |
| Gradient bar fill | bg-gradient-to-r from-{color}-900 to-{color}-500 | Tailwind gradient |
| Border | border border-{color}-500 | Tailwind border |
| Tooltip | Tooltip component | shadcn/ui Tooltip |
| Purple defense color | Purple/magenta Tailwind classes | purple-500, purple-900 |
| Cyan resistance color | Cyan/teal Tailwind classes | cyan-500, cyan-900 |
| Cap indicator | Conditional border/glow | ring-2 ring-yellow-400 |
| MarkerValue line | Vertical divider at percentage | Absolute positioned div |
| Percentage label | Text span | Plain React text |
| Section headers | Label component | Custom Label or h3 |

## API Integration Points

### Backend Endpoints Needed

1. **POST /api/calculations/totals** - Calculate all build totals
   - **Status**: ✅ Already exists (verified in Epic 1.4 backend implementation)
   - **Request**: 
     ```typescript
     {
       buildId?: string,
       archetype: string,
       level: number,
       powers: Array<{
         powerId: string,
         level: number,
         slots: Array<{
           enhancementId: string,
           level: number,
           boostLevel?: number
         }>
       }>
     }
     ```
   - **Response**: 
     ```typescript
     {
       defense: Record<DamageType, number>,     // 11 types
       resistance: Record<DamageType, number>,   // 8 types  
       resistanceCapped: Record<DamageType, number>,
       health: { regeneration, maxHp, absorb },
       endurance: { recovery, usage, maxEnd },
       movement: { runSpeed, jumpSpeed, flySpeed },
       // ... all other calculated stats
     }
     ```

2. **GET /api/archetypes/:archetypeId** - Get archetype caps
   - **Status**: ✅ Already exists
   - **Response includes**: 
     ```typescript
     {
       defenseCap: number,    // Usually 0.45 (45%)
       resistanceCap: number, // 0.75 or 0.90
       damageCap: number,
       // ... other caps
     }
     ```

### Data Flow

1. User modifies build (adds power, slots enhancement)
2. Zustand store updates build state
3. Debounced watcher triggers `recalculate()` action
4. Action calls TanStack Query mutation
5. Mutation POSTs to `/api/calculations/totals`
6. Backend calculates all stats using character calculation engine
7. Response updates Zustand store `totals` state
8. React components re-render with new totals
9. StatBar components animate to new widths
10. Tooltips show updated values

## Screenshot Analysis

### Available Screenshots

Location: `/home/user/mids-hero-web/shared/user/midsreborn-screenshots`

1. **view-total-window.png**
   - **Shows**: Full "Totals for Self" window (frmTotals)
   - **Relevant to**: Main defense/resistance display component
   - **Key observations**:
     - Defense section at top with purple/magenta bars
     - 11 defense types listed vertically: Smashing, Lethal, Fire, Cold, Energy, Negative, Toxic, Psionic, Melee, Ranged, AoE
     - All showing 0% (empty build)
     - Resistance section below with cyan/teal bars
     - 8 resistance types listed: Smashing, Lethal, Fire, Cold, Energy, Negative, Toxic, Psionic
     - All showing 0%
     - Health section with green bars: Regeneration (140%), Max HP (1205)
     - Endurance section with blue bars: End Rec (2.08/s), End Use (0/s), Max End (100)
     - Black background, white text labels
     - Section headers: "Defense:", "Resistance:", "Health:", "Endurance:"
     - "Keep on Top" and "Close" buttons at bottom

2. **total-screen-1.png**
   - **Shows**: Inline "Cumulative Totals (For Self)" panel
   - **Relevant to**: Compact stats display for main window
   - **Key observations**:
     - Two-column layout for Defense and Resistance
     - Defense left column: Smashing, Lethal, Energy, Cold, Toxic, Psionic (all 0%)
     - Defense right column: Fire, Cold, Melee, Ranged, AoE (all 0%)
     - Resistance in same two-column format below
     - "Misc Effects:" section showing: Recovery, Regen, EndDrain, ToHit, EndRdx, Recharge
     - Green section header for "Cumulative Totals (For Self)"
     - Note at bottom: "Click the 'View Totals' button for more."
     - More compact than full window view

### Additional Screenshots NOT Needed

The existing screenshots provide excellent coverage of:
- Full defense/resistance display layout
- Color scheme (purple defense, cyan resistance)
- Label formatting
- Bar visual design
- Section organization
- Compact vs expanded views

## Implementation Notes

### Key Behaviors to Replicate

1. **Real-time Updates**: 
   - Totals update when build changes
   - Use React state and TanStack Query to trigger recalculation
   - Debounce rapid changes (500ms)

2. **Color Coding**: 
   - Purple/magenta for defense bars (#C000C0 → #800080 gradient)
   - Cyan/teal for resistance bars (#00C0C0 → #008080 gradient)
   - Green for health bars (#40FF40 → #00C000 gradient)
   - Blue for endurance bars (#4040C0 → #0000C0 gradient)

3. **Percentage Display**: 
   - Always show as percentage: `{value.toFixed(2)}%`
   - Format: "Smashing| 25.5%" or "Smashing 25.5%" (pipe optional)

4. **Zero Values**: 
   - Show 0% for stats with no bonuses
   - Don't hide empty rows
   - All defense/resistance types always visible

5. **Cap Visualization**: 
   - Resistance: Show overcap indicator when value exceeds archetype cap
   - Defense: Soft-cap at 45%, hard cap at 50% (archetype-dependent)
   - Visual indicators: Color change, border glow, or tooltip message

6. **Tooltip Formatting**:
   ```
   Defense: "{value}% {type} defense"
   
   Resistance (uncapped): "{capped}% {type} resistance ({archetype} resistance cap: {cap}%)"
   
   Resistance (overcapped): "{uncapped}% {type} resistance, capped at {capped}%"
   ```

### UX Improvements for Web

1. **Responsive Design**: 
   - Desktop: Two-column layout (Defense left, Resistance right)
   - Tablet: Single column, stacked sections
   - Mobile: Compact view with collapsible sections

2. **Tooltips**: 
   - Show on hover (desktop) or tap (mobile)
   - Include power contribution breakdown (future enhancement)
   - Show base vs enhanced vs set bonus breakdown

3. **Smooth Animations**: 
   - Animate bar width changes using Framer Motion
   - Transition duration: 300ms
   - Easing: ease-in-out
   ```tsx
   <motion.div
     className="h-full bg-gradient-to-r from-purple-900 to-purple-500"
     initial={false}
     animate={{ width: `${barWidth}%` }}
     transition={{ duration: 0.3, ease: "easeInOut" }}
   />
   ```

4. **Collapsible Sections**: 
   - Use shadcn/ui Accordion or Collapsible
   - Allow hiding Defense or Resistance sections
   - Save preference in localStorage

5. **Highlight Changes**: 
   - Briefly highlight (yellow glow) stats that changed
   - Duration: 1 second flash
   - Implementation: Add/remove CSS class on value change

6. **Accessibility**:
   - ARIA labels for screen readers
   - Keyboard navigation for tooltips
   - High contrast mode support

### Defense/Resistance Cap Logic

- **Defense Soft-Cap**: 45% (most archetypes)
- **Defense Hard-Cap**: 50% (Tanker, Brute) or 45% (others)
- **Resistance Cap**: 75% (most archetypes), 90% (Tanker, Brute)
- **Visual Indicator**: 
  - At soft-cap: Yellow border
  - At hard-cap: Orange border
  - Over cap: Red bar color showing excess amount
- **Source**: Archetype data from `GET /api/archetypes/:archetypeId`

**Cap Calculation**:
```typescript
interface ArchetypeCaps {
  defenseCap: number;      // 0.45 or 0.50
  resistanceCap: number;   // 0.75 or 0.90
}

const getCapIndicator = (value: number, cap: number): 'normal' | 'at-cap' | 'over-cap' => {
  const capPercent = cap * 100;
  if (value >= capPercent) return 'at-cap';
  if (value >= capPercent * 0.9) return 'near-cap'; // 90% of cap
  return 'normal';
};
```

## Warnings & Edge Cases

1. **Negative Defense**: 
   - Possible if debuffed by enemy powers
   - Display in red color
   - Bar should not display (or show as empty)
   - Tooltip: "−15.5% Smashing defense (debuffed)"

2. **Over-cap Resistance**: 
   - Can exceed cap with temporary buffs (Inspirations, ally buffs)
   - Only capped value applies in game
   - Show both uncapped and capped in tooltip
   - Visual: Different bar color for overcap portion

3. **Missing Archetype**: 
   - Can't determine caps without archetype selected
   - Show default caps (45% defense, 75% resistance)
   - Warning message in UI: "Select archetype for accurate caps"

4. **Calculation Errors**: 
   - Handle API errors gracefully
   - Show previous totals with error indicator
   - Error message: "Failed to calculate totals. Retry?"
   - Don't clear existing data on error

5. **Empty Build**: 
   - Show all 0% if no powers selected
   - Base regeneration should show 100% (base rate)
   - Base HP should show archetype base HP
   - Base endurance recovery should show archetype base recovery

6. **Toxic Defense Edge Case**:
   - Some game realms don't use Toxic defense
   - Check `DatabaseAPI.RealmUsesToxicDef()` equivalent
   - Hide Toxic defense row if not applicable
   - Always show Toxic resistance (exists in all realms)

7. **Positional vs Typed Defense**:
   - Game uses HIGHER of (positional, typed) defense
   - Example: 30% Smashing, 25% Melee → actual defense vs Smashing Melee attack is 30%
   - Tooltip should explain: "Actual defense uses higher of positional or typed"

8. **Absorb Shield**:
   - Shows as separate bar layer on HP bar
   - Limited to % of base HP
   - Tooltip: "Absorb: {value} ({percent}% of base HP)"

## MidsReborn Code References

### Primary Files

1. **frmTotals.cs** (Original Implementation)
   - **File**: `external/dev/MidsReborn/MidsReborn/Forms/WindowMenuItems/frmTotals.cs`
   - **Key Method**: `UpdateData()` (lines 461-797)
     - Updates all stat displays
     - Calculates defense values via `displayStats.Defense(typeIndex)`
     - Calculates resistance via `displayStats.DamageResistance(typeIndex, capped)`
     - Formats tooltips with cap information
   - **Defense Display** (lines 469-492):
     - Loops through `Enums.eDamage` enum
     - Skips None, Special, Unique1-3
     - Conditionally skips Toxic based on realm
     - Adds bars via `graphDef.AddItem(label, value, enhValue, tooltip)`
   - **Resistance Display** (lines 494-511):
     - Loops through types 1-8 (skips type 9)
     - Compares capped vs uncapped values
     - Tooltip shows archetype cap: `"{archetype.DisplayName} resistance cap: {archetype.ResCap * 100}%"`

2. **frmTotalsV2.cs** (Modern Implementation)
   - **File**: `external/dev/MidsReborn/MidsReborn/Forms/WindowMenuItems/frmTotalsV2.cs`
   - **Key Method**: `UpdateData()` (lines 623-920)
     - Cleaner implementation using `AddItemPair()`
     - Better tooltip formatting with helper methods
   - **Defense Display** (lines 668-684):
     - Uses `FormatVectorType()` to format damage type names
     - Adds pairs via `graphDef.AddItemPair(name, formattedValue, value, value, tooltip)`
   - **Resistance Display** (lines 686-706):
     - Shows capped value as main bar
     - Uncapped value in tooltip and as overcap bar
     - Archetype cap in tooltip
   - **Helper Method**: `GenericDataTooltip3()` (lines 609-621)
     - Formats tooltips consistently
     - Shows base, value, uncapped, with cap message
     - Handles percentage sign and movement units

3. **CtlMultiGraph.cs** (Custom Graph Control)
   - **File**: `external/dev/MidsReborn/MidsReborn/Controls/ctlMultiGraph.cs`
   - **Purpose**: Reusable horizontal bar graph control
   - **Rendering**: Uses SkiaSharp (hardware-accelerated)
   - **Key Methods**:
     - `AddItem(label, value, enhValue, tooltip)` - Add single bar
     - `AddItemPair(name, displayValue, baseValue, value, uncappedValue, absorbValue, tooltip)` - Add bar with all value types
     - `Draw()` - Trigger redraw
     - `Clear()` - Remove all items
   - **Properties**: 
     - Colors: Base, Enh, FadeStart, FadeEnd, Highlight, Overcap, MarkerInner, MarkerOuter
     - Layout: ItemHeight, TextWidth, PaddingX, PaddingY
     - Behavior: Border, Lines, ShowScale, Dual, Overcap, Clickable
     - Scale: Max, MarkerValue, ForcedMax

4. **DisplayStats.cs** (Calculation Methods)
   - **File**: `external/dev/MidsReborn/MidsReborn/Core/Base/Display/Statistics.cs` (inferred)
   - **Key Methods**:
     - `Defense(int damageTypeIndex)` - Get defense percentage for damage type
     - `DamageResistance(int damageTypeIndex, bool uncapped)` - Get resistance percentage
     - `HealthRegenPercent(bool uncapped)` - Get regeneration percentage
     - `HealthHitpointsNumeric(bool uncapped)` - Get max HP
     - `EnduranceRecoveryNumeric` / `EnduranceRecoveryPercentage()` - Get recovery
   - **Data Source**: `MidsContext.Character.Totals` and `MidsContext.Character.TotalsCapped`

---

**Implementation Checklist**:
- [ ] Create `StatBar` component with gradient, border, label, value
- [ ] Create `DefenseStats` component rendering 11 defense bars
- [ ] Create `ResistanceStats` component rendering 8 resistance bars
- [ ] Create `TotalsPanel` container with tabs/sections
- [ ] Integrate TanStack Query mutation for `/api/calculations/totals`
- [ ] Add Zustand store actions for totals state
- [ ] Implement auto-recalculation on build changes
- [ ] Add tooltips with detailed breakdowns
- [ ] Add cap indicators (color/border changes)
- [ ] Add smooth animations for bar width changes
- [ ] Add responsive layout (mobile/tablet/desktop)
- [ ] Test with empty build (all 0%)
- [ ] Test with capped resistance values
- [ ] Test with negative defense (debuffed)
- [ ] Test archetype cap variations (Tanker vs Defender)
