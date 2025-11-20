# MidsReborn UI Analysis: Epic 4.2 - HP, Endurance, Recharge Displays

**Created**: 2025-11-20
**Epic**: 4.2 - HP, Endurance, Recharge Displays  
**MidsReborn Forms Analyzed**: frmTotals.cs, frmTotalsV2.cs, Statistics.cs

## Executive Summary

Epic 4.2 extends the Totals window (analyzed in Epic 4.1) to include health, endurance, and recharge statistics. MidsReborn displays these stats using the same CtlMultiGraph control introduced in Epic 4.1, with color-coded horizontal bars: green for health, blue for endurance, and purple/cyan for recharge. The implementation calculates complex derived values (net endurance recovery, time to full, HP/sec regen) and presents them with detailed tooltips. The web implementation will reuse the StatBar component from Epic 4.1 and extend the TotalsPanel container with four new panels: HPPanel, EndurancePanel, RechargePanel, and MiscStatsPanel.

## MidsReborn UI Components

### Component 1: frmTotals - Health Section

- **File**: `external/dev/MidsReborn/MidsReborn/Forms/WindowMenuItems/frmTotals.cs`
- **Lines**: 559-581
- **Purpose**: Display character health regeneration and maximum hit points
- **Layout**: Two horizontal bars stacked vertically in the Health section
  - Row 1: Regeneration (percentage with green bar)
  - Row 2: Max HP (numeric value with green bar)
- **Data Displayed**:
  - **Regeneration**: Percentage (base 100%, bonuses add to this)
    - Example: "140%" = base 100% + 40% from bonuses
    - Displays as: "Regeneration| 140%"
  - **Max HP**: Numeric hit points
    - Example: "1205" for a character at level 50
    - Displays as: "Max HP| 1205.72%"
    - Percentage is relative to archetype cap
- **Color Scheme**: Green gradient
  - ColorBase: `#60C060` (green)
  - Bar gradient: Green to darker green
- **User Interactions**:
  - Hover shows detailed tooltip
  - No click interactions

### Component 2: frmTotals - Endurance Section

- **File**: `external/dev/MidsReborn/MidsReborn/Forms/WindowMenuItems/frmTotals.cs`
- **Lines**: 513-557
- **Purpose**: Display endurance recovery, usage, and maximum endurance
- **Layout**: Three horizontal bars stacked vertically in the Endurance section
  - Row 1: End Recovery (percentage and numeric /s with blue bar)
  - Row 2: End Use (numeric /s with blue bar)
  - Row 3: Max End (numeric value with blue bar)
- **Data Displayed**:
  - **End Recovery**: Percentage AND numeric per second
    - Example: "EndRec| 100% (2.08/s)"
    - Base recovery: ~2.08/s for most archetypes at 100 max end
  - **End Use**: Numeric per second (sum of all toggle costs)
    - Example: "EndUse| 0.52/s"
    - Shows total endurance drain from active toggles
  - **Max End**: Numeric maximum endurance
    - Example: "Max End| 100%"
    - Base is 100, bonuses add to this
- **Color Scheme**: Blue gradient
  - ColorBase: `#4040C0` (blue)
  - Bar gradient: Blue to darker blue
- **Tooltips**:
  - **End Recovery**: Shows time to full, cap info
    - "Time to go from 0-100% end: 18.0s."
    - "Capped from a total of: X%" (if capped)
  - **End Use**: Shows net recovery (Recovery - Usage)
    - If positive: "Net Endurance Gain: +1.56/s"
    - If negative: "You will lose end at a rate of: -0.43/s. Time to zero: 232s."
  - **Max End**: Shows base and current
    - "Base Endurance: 100"
    - "Current Max End: 110"
    - "Increased by 10%"

### Component 3: frmTotals - Recharge Section

- **File**: `external/dev/MidsReborn/MidsReborn/Forms/WindowMenuItems/frmTotals.cs` (movement section), **frmTotalsV2.cs** lines 786-792
- **Purpose**: Display global recharge speed bonus (Haste)
- **Layout**: Single horizontal bar in Misc Buffs section
  - Row 1: Haste (percentage with purple/cyan bar)
- **Data Displayed**:
  - **Haste/Global Recharge**: Percentage (base 100%)
    - Example: "170%" = base 100% + 70% from Hasten
    - Displays as: "Haste| 170%"
    - Storage format: BuffHaste = 0.70 (factor), display = (0.70 + 1) × 100 = 170%
- **Color Scheme**: Purple/cyan gradient (similar to defense/resistance)
- **Tooltip**: Shows base, capped, and uncapped values
  - "170% Haste"
  - "Base: 100%"
  - If capped: "Capped at 400%"

### Component 4: frmTotalsV2 - Modern Health Section

- **File**: `external/dev/MidsReborn/MidsReborn/Forms/WindowMenuItems/frmTotalsV2.cs`
- **Lines**: 708-744
- **Purpose**: Improved health display with absorb shield visualization
- **Layout**: Two rows in HP section with cleaner API
  - Row 1: Regeneration (percentage with HP/s in tooltip)
  - Row 2: Max HP (numeric with absorb shield layer)
- **Improvements over frmTotals**:
  - Uses `AddItemPair()` for cleaner code
  - Shows absorb shield as separate bar layer
  - Better tooltip formatting with `GenericDataTooltip3()`
  - Displays HP/s regeneration rate in tooltip
- **Absorb Shield**:
  - Shown as translucent layer on HP bar
  - Limited to percentage of base HP
  - Example: "Absorb: 240 (20% of base HP)"
  - Uses `absorbValue` parameter in AddItemPair()

### Component 5: frmTotalsV2 - Modern Endurance Section

- **File**: `external/dev/MidsReborn/MidsReborn/Forms/WindowMenuItems/frmTotalsV2.cs`
- **Lines**: 746-774
- **Purpose**: Improved endurance display with net recovery
- **Layout**: Three rows in Endurance section
  - Row 1: End Rec (/s with percentage in tooltip)
  - Row 2: End Use (/s with net gain in tooltip)
  - Row 3: Max End (numeric)
- **Display Format**:
  - End Rec: "2.08/s" (main display), tooltip shows percentage
  - End Use: "0.52/s" (main display), tooltip shows net: "Net gain: +1.56/s"
  - Max End: "100" (main display), tooltip shows base: "base: 100"

### Component 6: frmTotalsV2 - Misc Buffs Section

- **File**: `external/dev/MidsReborn/MidsReborn/Forms/WindowMenuItems/frmTotalsV2.cs`
- **Lines**: 786-819
- **Purpose**: Display accuracy, tohit, damage, and recharge bonuses
- **Layout**: Multiple rows for different buff types
  - Haste: Global recharge percentage (base 100%)
  - ToHit: ToHit bonus percentage (base 0%)
  - Accuracy: Accuracy bonus percentage (base 0%)
  - Damage: Damage bonus percentage (base 100%)
  - Range: Range bonus percentage (base 100%)
- **Color Scheme**: Various colors per stat type
- **Tooltip Format**: Uses `GenericDataTooltip3()` helper for consistency

## Feature Requirements

### MUST-HAVE Features

#### 1. HP Regeneration Display
- **Description**: Show character's health regeneration rate as percentage
- **MidsReborn Implementation**:
  - Displays percentage (base 100%, bonuses add to this)
  - Example: 140% = base 100% + 40% from bonuses
  - Green horizontal bar
  - Tooltip shows HP/s regeneration rate: "12.5 HP/s"
  - Tooltip shows time to full health: "Time to full: 96.4s"
- **Web Equivalent**:
  - StatBar component with green gradient
  - Label: "Regeneration"
  - Value: `{regenPercent}%`
  - Tooltip: `{regenPercent}% Regeneration ({hpPerSec} HP/s)\nBase: 100%`
  - Bar max: Dynamic based on max value (use `getMaxValue()` logic)

#### 2. Max HP Display
- **Description**: Show character's maximum hit points
- **MidsReborn Implementation**:
  - Displays numeric HP value
  - Example: "1205" for level 50 Scrapper
  - Green horizontal bar
  - Bar width represents percentage of archetype cap
  - Tooltip shows base HP and cap: "Base: 1017, Cap: 2409"
- **Web Equivalent**:
  - StatBar component with green gradient
  - Label: "Max HP"
  - Value: `{maxHp}` (numeric)
  - Tooltip: `{maxHp} HP ({archetype} HP cap: {hpCap})\nBase: {baseHp} HP`
  - Bar max: Archetype HP cap

#### 3. Absorb Shield Display
- **Description**: Show temporary absorb shield as layer on HP bar
- **MidsReborn Implementation**:
  - Shown as separate bar layer (translucent)
  - Limited to percentage of base HP
  - Example: "Absorb: 240 (20% of base HP)"
  - Only in frmTotalsV2 (modern version)
- **Web Equivalent**:
  - StatBar component with `absorbLayer` prop
  - Display absorb as overlay on HP bar (different color/opacity)
  - Tooltip: `Absorb: {absorbValue} ({absorbPercent}% of base HP)`
  - Skip if absorb value is 0

#### 4. Endurance Recovery Display
- **Description**: Show endurance recovered per second
- **MidsReborn Implementation**:
  - Displays as "/s" value: "2.08/s"
  - Tooltip shows percentage: "100% (2.08/s)"
  - Blue horizontal bar
  - Base recovery: ~2.08/s for most ATs at 100 max end
  - Tooltip shows time to full: "Time to full: 48.1s"
- **Web Equivalent**:
  - StatBar component with blue gradient
  - Label: "End Rec"
  - Value: `{recoveryNumeric}/s`
  - Tooltip: `{recoveryNumeric}/s End. ({recoveryPercent}%)\nBase: {baseRecovery}/s\nTime to full: {timeToFull}s`
  - Bar max: 400% (recovery cap for most ATs)

#### 5. Endurance Usage Display
- **Description**: Show endurance drained per second from toggles
- **MidsReborn Implementation**:
  - Displays as "/s" value: "0.52/s"
  - Blue horizontal bar
  - Sum of all active toggle costs
  - Tooltip shows net recovery: "Net gain: +1.56/s" or "Net loss: -0.43/s"
- **Web Equivalent**:
  - StatBar component with blue gradient (or red if net negative)
  - Label: "End Use"
  - Value: `{endUsage}/s`
  - Tooltip: `{endUsage}/s End.\nNet recovery: {netRecovery}/s`
  - If net negative: Add warning indicator
  - Bar max: 4 /s (typical max toggle drain)

#### 6. Max Endurance Display
- **Description**: Show maximum endurance pool
- **MidsReborn Implementation**:
  - Displays numeric value: "100" (base), "110" (with bonuses)
  - Blue horizontal bar
  - Base is 100, bonuses add to this
  - Tooltip shows base and increase: "Base: 100, Current: 110, Increased by 10"
- **Web Equivalent**:
  - StatBar component with blue gradient
  - Label: "Max End"
  - Value: `{maxEnd}` (numeric)
  - Tooltip: `{maxEnd} Maximum Endurance\nBase: 100`
  - Bar max: 150 (allows for bonuses up to +50%)

#### 7. Global Recharge Display
- **Description**: Show global recharge speed bonus (Haste)
- **MidsReborn Implementation**:
  - Displays percentage (base 100%)
  - Example: "170%" = base 100% + 70% from Hasten
  - Storage: BuffHaste = 0.70 (factor), display = (0.70 + 1) × 100 = 170%
  - Purple/cyan horizontal bar
  - Tooltip shows base and cap: "Base: 100%, Cap: 400%"
- **Web Equivalent**:
  - StatBar component with purple/cyan gradient
  - Label: "Global Recharge"
  - Value: `{rechargePercent}%`
  - Tooltip: `{rechargePercent}% Global Recharge\nBase: 100%`
  - If >= 170% (perma-Hasten threshold): Add indicator icon
  - Bar max: 400% (recharge cap for most ATs)

#### 8. Accuracy Display
- **Description**: Show global accuracy bonus
- **MidsReborn Implementation**:
  - Displays percentage (base 0%)
  - Example: "+15%" from set bonuses
  - Tooltip shows value: "15% Accuracy"
- **Web Equivalent**:
  - StatBar component
  - Label: "Accuracy"
  - Value: `+{accuracyPercent}%`
  - Tooltip: `{accuracyPercent}% Accuracy bonus`
  - Bar max: 100% (typical max)

#### 9. ToHit Display
- **Description**: Show global tohit bonus
- **MidsReborn Implementation**:
  - Displays percentage (base 0%)
  - Example: "+10%" from buffs
  - Tooltip shows value: "10% ToHit"
- **Web Equivalent**:
  - StatBar component
  - Label: "ToHit"
  - Value: `+{tohitPercent}%`
  - Tooltip: `{tohitPercent}% ToHit bonus`
  - Bar max: 100% (typical max)

#### 10. Damage Display
- **Description**: Show global damage bonus
- **MidsReborn Implementation**:
  - Displays percentage (base 100%)
  - Example: "150%" = base 100% + 50% from bonuses
  - Tooltip shows base and cap
- **Web Equivalent**:
  - StatBar component
  - Label: "Damage"
  - Value: `{damagePercent}%`
  - Tooltip: `{damagePercent}% Damage\nBase: 100%`
  - Bar max: Archetype damage cap (varies by AT)

### SHOULD-HAVE Features

#### 1. Net Endurance Recovery Calculation
- **Description**: Show net endurance change (Recovery - Usage)
- **MidsReborn Implementation**:
  - Calculated as: `EnduranceRecoveryNet = EnduranceRecoveryNumeric - EnduranceUsage`
  - If positive: "Net gain: +1.56/s"
  - If negative: "Net loss: -0.43/s, Time to zero: 232s"
  - Displayed in End Use tooltip
- **Web Equivalent**:
  - Calculate `netRecovery = recoveryNumeric - endUsage`
  - Display in EndurancePanel summary
  - Color-code: green if positive, red if negative
  - If negative: Show time to zero endurance

#### 2. Time to Full Calculations
- **Description**: Show time to recover from 0 to max
- **MidsReborn Implementation**:
  - Health: `timeToFull = maxHp / hpPerSec`
  - Endurance: `timeToFull = maxEnd / recoveryNumeric`
  - Displayed in tooltips
- **Web Equivalent**:
  - Calculate and display in tooltips
  - Format: "Time to full: {time}s"
  - Consider showing in panel summary as well

#### 3. Perma-Hasten Indicator
- **Description**: Visual indicator when build achieves permanent Hasten
- **MidsReborn Implementation**:
  - Not explicitly shown in totals window
  - Players calculate manually: need ~170% total recharge with good slotting
- **Web Equivalent**:
  - Check if global recharge (excluding Hasten) + local recharge in Hasten allows permanent uptime
  - Threshold: ~70% global + 95% local = Hasten recharges in ~34s (under 120s duration)
  - Display green checkmark icon next to Haste bar if achieved
  - Tooltip: "Perma-Hasten achieved!"

#### 4. HP/s and End/s Display
- **Description**: Show numeric regeneration/recovery rates
- **MidsReborn Implementation**:
  - HP/s shown in tooltip: "12.5 HP/s"
  - End/s shown in main display: "2.08/s"
- **Web Equivalent**:
  - Display HP/s in regeneration tooltip
  - Display End/s as main value for recovery
  - Use consistent "/s" suffix

#### 5. Cap Indicators
- **Description**: Show when stats are capped
- **MidsReborn Implementation**:
  - Tooltip shows: "Capped from a total of: X%"
  - Example: Regen capped at 2500% shows uncapped value in tooltip
- **Web Equivalent**:
  - Check if capped value < uncapped value
  - If capped: Change bar color or add indicator
  - Tooltip: "Capped at {cap}% (Actual: {uncapped}%)"

### COULD-SKIP Features

#### 1. Separate Marker Lines
- **Description**: Vertical line at 100% baseline
- **MidsReborn Implementation**:
  - Uses `MarkerValue` property on CtlMultiGraph
  - Draws line at 100% for stats with base 100%
- **Rationale**: Nice visual aid but not critical for MVP
- **Web Equivalent**: Can add later with CSS absolute positioned divider

#### 2. Uncapped Display Toggle
- **Description**: Toggle between capped and uncapped values
- **MidsReborn Implementation**:
  - Most methods have `bool uncapped` parameter
  - Example: `HealthRegenPercent(bool uncapped)`
- **Rationale**: Advanced feature, defer to v2
- **Web Equivalent**: Add toggle button in panel header

#### 3. Export Stats to Clipboard
- **Description**: Copy stats as formatted text
- **Rationale**: Low priority for MVP

## State Management Analysis

### Server State (TanStack Query)

- **Endpoint**: `POST /api/calculations/totals` (already exists from Epic 4.1)
- **Request Data**: Same as Epic 4.1 (buildId, archetype, level, powers, enhancements)
- **Response Data** (extend existing response):
  ```typescript
  {
    // Existing from Epic 4.1
    defense: { ... },
    resistance: { ... },
    resistanceCapped: { ... },
    
    // NEW for Epic 4.2
    health: {
      regeneration_percent: number,      // 140.0 = 140%
      regeneration_hp_per_sec: number,   // 12.5 HP/s
      max_hp: number,                     // 1205
      max_hp_percent: number,             // 50.0 (% of cap)
      base_hp: number,                    // 1017
      hp_cap: number,                     // 2409
      absorb: number,                     // 240
      time_to_full: number                // 96.4 seconds
    },
    endurance: {
      recovery_percent: number,           // 100.0 = 100%
      recovery_numeric: number,           // 2.08 /s
      recovery_base: number,              // 2.08 /s (at 100%)
      usage: number,                      // 0.52 /s
      max_endurance: number,              // 100
      net_recovery: number,               // 1.56 /s (can be negative)
      time_to_full: number,               // 48.1 seconds
      time_to_zero: number                // Infinity or seconds if draining
    },
    recharge: {
      global_percent: number,             // 170.0 = +70% recharge
      global_factor: number,              // 0.70 (internal representation)
      cap_percent: number,                // 400.0 for most ATs
      is_capped: boolean,
      perma_hasten: boolean               // true if achieves perma-Hasten
    },
    buffs: {
      accuracy: number,                   // 15.0 = +15%
      tohit: number,                      // 10.0 = +10%
      damage_percent: number,             // 150.0 = +50% damage
      damage_cap: number                  // 400.0 or 500.0 depending on AT
    }
  }
  ```

- **Caching Strategy**: No caching (same as Epic 4.1)
  - Always recalculate on demand
  - Trigger on power/enhancement changes

### Client State (Zustand)

- **Store**: `characterStore` (extend existing from Epic 4.1)
- **State Shape**:
  ```typescript
  {
    totals: CalculatedTotals | null,  // Includes Epic 4.2 data
    isCalculating: boolean,
    lastCalculated: Date | null,
    // ... existing build state
  }
  ```

- **Actions**: Reuse from Epic 4.1
  ```typescript
  {
    setTotals: (totals: CalculatedTotals) => void,
    setCalculating: (isCalculating: boolean) => void,
    recalculate: async () => Promise<void>,
  }
  ```

### Derived State

- **Net Endurance Recovery**:
  ```typescript
  const netRecovery = totals.endurance.recovery_numeric - totals.endurance.usage;
  const isPositive = netRecovery > 0;
  ```

- **Perma-Hasten Check**:
  ```typescript
  // Simplified check: global recharge >= 170% with good slotting
  const permaHasten = totals.recharge.global_percent >= 170;
  ```

- **Bar Widths** (reuse from Epic 4.1):
  ```typescript
  const barWidth = Math.min((value / max) * 100, 100); // Cap at 100%
  ```

- **Color Classes**:
  ```typescript
  const healthBarClass = "bg-gradient-to-r from-green-900 to-green-500";
  const enduranceBarClass = "bg-gradient-to-r from-blue-900 to-blue-500";
  const rechargeBarClass = "bg-gradient-to-r from-purple-900 to-purple-500";
  const netNegativeClass = "bg-gradient-to-r from-red-900 to-red-500"; // When endurance draining
  ```

## Web Component Mapping

| MidsReborn Pattern | Web Equivalent | Library/Component |
| ------------------ | -------------- | ----------------- |
| graphRegen (regeneration bar) | StatBar (green) | Reuse from Epic 4.1 |
| graphHP (max HP bar) | StatBar (green) with absorb layer | Extend StatBar |
| graphRec (end recovery bar) | StatBar (blue) | Reuse from Epic 4.1 |
| graphDrain (end usage bar) | StatBar (blue/red) | Reuse from Epic 4.1 |
| graphMaxEnd (max endurance bar) | StatBar (blue) | Reuse from Epic 4.1 |
| graphHaste (recharge bar) | StatBar (purple) | Reuse from Epic 4.1 |
| graphAccuracy (accuracy bar) | StatBar | Reuse from Epic 4.1 |
| graphToHit (tohit bar) | StatBar | Reuse from Epic 4.1 |
| graphDamage (damage bar) | StatBar | Reuse from Epic 4.1 |
| AddItem() | <StatBar label={} value={} /> | React component |
| AddItemPair() (frmTotalsV2) | <StatBar label={} value={} baseValue={} absorbValue={} /> | Extended StatBar |
| Tooltip with HP/s, End/s | Tooltip with formatted JSX | shadcn/ui Tooltip |
| Net recovery calculation | Derived state in component | React useMemo |

## API Integration Points

### Backend Endpoints Needed

1. **POST /api/calculations/totals** - Calculate all build totals
   - **Status**: ✅ Already exists (Epic 4.1)
   - **Extend Response**: Add health, endurance, recharge, buffs sections (see State Management above)
   - **Backend Calculation**:
     - Health: Use specs from `docs/midsreborn/calculations/` (regeneration spec)
     - Endurance: Use `docs/midsreborn/calculations/06-power-endurance-recovery.md`
     - Recharge: Use `docs/midsreborn/calculations/21-build-totals-recharge.md`

### Data Flow

1. User modifies build (same as Epic 4.1)
2. Zustand store triggers recalculation
3. Backend calculates health/endurance/recharge stats
4. Response includes all Epic 4.2 data
5. React components (HPPanel, EndurancePanel, RechargePanel, MiscStatsPanel) render
6. StatBar components display with appropriate colors and tooltips

## Screenshot Analysis

### Available Screenshots

Location: `/home/user/mids-hero-web/shared/user/midsreborn-screenshots`

#### 1. view-total-window.png
- **Shows**: Full "Totals for Self" window (frmTotals)
- **Relevant to**: HPPanel and EndurancePanel components
- **Key Observations**:
  - **Health Section**:
    - "Health:" section header (white text on black background)
    - Regeneration: "140%" with green horizontal bar (small bar since near base)
    - Max HP: "1205" with green horizontal bar
    - Green gradient bars on black background
  - **Endurance Section**:
    - "Endurance:" section header
    - End Rec: "2.08/s" with blue horizontal bar
    - End Use: "0/s" with blue horizontal bar (empty since no toggles)
    - Max End: "100" with blue horizontal bar (medium bar, base value)
    - Blue gradient bars on black background
  - **Visual Layout**:
    - Each section has header label
    - Stats listed vertically with label on left, value on right
    - Bars extend from left to right
    - Percentage width indicates magnitude relative to max

#### 2. total-screen-1.png
- **Shows**: Inline "Cumulative Totals (For Self)" panel (compact view)
- **Relevant to**: Compact stats summary (optional for MVP)
- **Key Observations**:
  - "Misc Effects:" section shows compact stat list
  - Recovery: "100% (1.7/s+ToHit: 0%"
  - Regen: "100%"
  - EndDrain: "0/s"
  - +EndRdx: "0%"
  - +Recharge: "0%"
  - Two-column compact layout
  - Less visual (no bars), text only

### Additional Screenshots NOT Needed

The existing screenshots provide sufficient coverage for:
- HP section layout (Regeneration + Max HP bars)
- Endurance section layout (End Rec + End Use + Max End bars)
- Color scheme (green for health, blue for endurance)
- Label formatting and bar visual design
- Compact vs expanded views

Epic 4.1 screenshots already cover the totals window structure and StatBar patterns.

## Implementation Notes

### Key Behaviors to Replicate

1. **Regeneration Display**:
   - Base is 100% (not 0%)
   - Bonuses add to base: 100% + 40% = 140%
   - Bar shows magnitude relative to max (dynamic max based on getMaxValue())
   - Green color scheme

2. **Max HP Display**:
   - Numeric value (not percentage)
   - Bar width represents percentage of archetype cap
   - Absorb shown as separate layer (frmTotalsV2 only)
   - Tooltip shows base HP and cap

3. **Endurance Recovery Display**:
   - Primary display: "/s" format (2.08/s)
   - Tooltip includes percentage (100%)
   - Base recovery varies by max endurance: `baseRecovery × (maxEnd/100 + 1)`
   - Blue color scheme

4. **Endurance Usage Display**:
   - Sum of all toggle costs
   - Display as "/s" format
   - Tooltip shows net recovery (can be negative)
   - If net negative: Red color scheme warning

5. **Net Recovery Calculation**:
   - Net = Recovery - Usage
   - If positive: "Net gain: +X/s"
   - If negative: "Net loss: -X/s, Time to zero: Xs"
   - Color-code based on sign

6. **Global Recharge Display**:
   - Base is 100% (not 0%)
   - Storage: factor (0.70 for +70%)
   - Display: percentage ((factor + 1) × 100 = 170%)
   - Cap at 400% for most ATs

7. **Perma-Hasten Threshold**:
   - Achieved when global recharge (excluding Hasten) + local recharge allows Hasten to recharge in < 120s
   - Simplified check: global >= 170% with 95% local slotting
   - Visual indicator (checkmark icon) when achieved

### UX Improvements for Web

1. **Net Recovery Summary**:
   - Add summary card showing net endurance recovery prominently
   - Color-code: green if positive, red if negative
   - Show time to full or time to zero

2. **Perma-Hasten Indicator**:
   - Visual checkmark or badge when achieved
   - Tooltip explains threshold and current values

3. **HP/s and End/s Prominence**:
   - Show numeric rates (/s) as primary display
   - Percentages in tooltips (less intuitive for most players)

4. **Absorb Shield Visualization**:
   - Translucent overlay on HP bar (different color)
   - Only show if absorb > 0
   - Tooltip shows percentage of base HP

5. **Responsive Layout**:
   - Desktop: 2×2 grid (HP + Endurance top row, Recharge + Misc bottom row)
   - Tablet: 2×2 or stacked
   - Mobile: Fully stacked (HP → Endurance → Recharge → Misc)

6. **Smooth Transitions**:
   - Animate bar width changes
   - Animate color changes (net recovery positive → negative)
   - Use Framer Motion for smooth transitions

## Warnings & Edge Cases

### Specific to HP

1. **Regeneration Cap**:
   - Most ATs: 2500% cap (can reach with stacked buffs)
   - Display uncapped value in tooltip if exceeds cap
   - Visual indicator when capped

2. **Absorb Shield**:
   - Limited to percentage of base HP (varies by power)
   - Temporary (not permanent like HP)
   - Show as separate layer, not added to max HP

3. **HP Cap**:
   - Varies by archetype (2409 for Scrapper, 3212 for Tanker, etc.)
   - Bar width relative to cap
   - Tooltip shows cap value

### Specific to Endurance

1. **Negative Net Recovery**:
   - Can occur if toggle costs exceed recovery
   - Display warning (red color)
   - Show time to zero: "Time to drain: 232s"
   - Common scenario: many toggles without Stamina

2. **Max Endurance Effect on Recovery**:
   - Higher max endurance increases recovery rate
   - Formula: `recovery × (maxEnd/100 + 1)`
   - Example: 110 max end = 2.1× multiplier (vs 2.0 at 100)
   - 5% more endurance recovered per tick

3. **Time to Full vs Time to Full Net**:
   - Time to Full: Assumes no toggle usage
   - Time to Full Net: Considers net recovery
   - If net negative: Time to full is infinity

4. **Recovery Cap**:
   - Most ATs: 500% (5.0× multiplier)
   - Display uncapped value if exceeds cap
   - Rare to hit cap without extreme buffs

### Specific to Recharge

1. **Storage vs Display**:
   - Storage: BuffHaste = 0.70 (factor)
   - Display: (0.70 + 1) × 100 = 170%
   - Backend should return both for clarity

2. **Recharge Cap**:
   - Most ATs: 400% (5.0× speed including base)
   - Storage cap: 4.0 (BuffHaste factor)
   - Some ATs may have different caps

3. **Perma-Hasten Complexity**:
   - Depends on global recharge (excluding Hasten itself)
   - Depends on local recharge in Hasten power
   - Simplified check: ~170% total with 95% local
   - Advanced check: `120 / (1 + localRech) / (1 + globalRech) <= 118` (duration - animation)

4. **Global vs Local Confusion**:
   - Global recharge: Affects ALL powers
   - Local recharge: Affects single power
   - Players often confuse "recharge reduction" (local) with "recharge speed" (global)
   - Tooltip should clarify: "Global Recharge: Affects all powers"

### Specific to Misc Stats

1. **Accuracy vs ToHit**:
   - Accuracy: Multiplier on base tohit (100% = no change)
   - ToHit: Flat addition to hit chance
   - Both affect final hit chance differently
   - Tooltip should explain difference

2. **Damage Display**:
   - Base is 100% (not 0%)
   - Cap varies by AT (400% for most, 500% for Scrappers/Brutes)
   - Tooltip shows cap

3. **Buff vs Enhancement**:
   - These are global buffs (from powers, set bonuses)
   - Not local enhancements slotted in individual powers
   - Tooltip: "Global X bonus"

## MidsReborn Code References

### Primary Files

#### 1. frmTotals.cs (Original Implementation)

**File**: `external/dev/MidsReborn/MidsReborn/Forms/WindowMenuItems/frmTotals.cs`

**Health Section** (lines 559-581):
```csharp
// Regeneration bar
var iTip4 = $"Time to go from 0-100% health: {Utilities.FixDP(displayStats.HealthRegenTimeToFull)}s.\r\n" +
            $"Health regenerated per second: {Utilities.FixDP(displayStats.HealthRegenHealthPerSec)}%\r\n" +
            $"HitPoints regenerated per second at level 50: {Utilities.FixDP(displayStats.HealthRegenHPPerSec)} HP";
if (Math.Abs(displayStats.HealthRegenPercent(false) - displayStats.HealthRegenPercent(true)) > 0.01)
{
    iTip4 += $"\r\nCapped from a total of: {displayStats.HealthRegenPercent(true):###0}%.";
}

graphRegen.Clear();
graphRegen.AddItem($"Regeneration|{displayStats.HealthRegenPercent(false):###0}%", 
    Math.Max(0, displayStats.HealthRegenPercent(false)), 
    Math.Max(0, displayStats.HealthRegenPercent(true)), 
    iTip4);
graphRegen.Max = graphRegen.GetMaxValue();
graphRegen.MarkerValue = 100f;
graphRegen.Draw();

// Max HP bar
graphHP.Clear();
var iTip5 = $"Base HitPoints: {MidsContext.Character.Archetype.Hitpoints}\r\n" +
            $"Current HitPoints: {displayStats.HealthHitpointsNumeric(false)}";
if (Math.Abs(displayStats.HealthHitpointsNumeric(false) - displayStats.HealthHitpointsNumeric(true)) > 0.01)
{
    iTip5 += $"\r\n(Capped from a total of: {displayStats.HealthHitpointsNumeric(true):###0.##})";
}

graphHP.AddItem($"Max HP|{displayStats.HealthHitpointsPercentage:###0.##}%", 
    Math.Max(0, displayStats.HealthHitpointsPercentage), 
    Math.Max(0, displayStats.HealthHitpointsPercentage), 
    iTip5);
graphHP.Max = (float)(MidsContext.Character.Archetype.HPCap / (double)MidsContext.Character.Archetype.Hitpoints * 100);
graphHP.MarkerValue = 100f;
graphHP.Draw();
```

**Endurance Section** (lines 513-557):
```csharp
// Net recovery tooltip
var drainTip = "";
var str2 = $"Time to go from 0-100% end: {Utilities.FixDP(displayStats.EnduranceTimeToFull)}s.";
if (Math.Abs(displayStats.EnduranceRecoveryPercentage(false) - displayStats.EnduranceRecoveryPercentage(true)) > 0.01)
{
    str2 += $"\r\nCapped from a total of: {displayStats.EnduranceRecoveryPercentage(true):###0}%.";
}

var recTip = $"{str2}\r\nHover the mouse of the End Drain stats for more info.";
switch (displayStats.EnduranceRecoveryNet)
{
    case > 0:
        drainTip = $"Net Endurance Gain (Recovery - Drain): {Utilities.FixDP(displayStats.EnduranceRecoveryNet)}/s.";
        if (Math.Abs(displayStats.EnduranceRecoveryNet - displayStats.EnduranceRecoveryNumeric) > 0.01)
        {
            drainTip += $"\r\nTime to go from 0-100% end (using net gain): {Utilities.FixDP(displayStats.EnduranceTimeToFullNet)}s.";
        }
        break;
    case < 0:
        drainTip = $"With current end drain, you will lose end at a rate of: {Utilities.FixDP(displayStats.EnduranceRecoveryLossNet)}/s.\r\n" +
                   $"From 100% you would run out of end in: {Utilities.FixDP(displayStats.EnduranceTimeToZero)}s.";
        break;
}

// Max End bar
graphMaxEnd.Clear();
var iTip3 = $"Base Endurance: 100\r\nCurrent Max End: {Utilities.FixDP(displayStats.EnduranceMaxEnd)}";
if (MidsContext.Character.Totals.EndMax > 0)
{
    iTip3 += $"\r\nYour maximum endurance has been increased by {Utilities.FixDP(displayStats.EnduranceMaxEnd - 100f)}%";
}
graphMaxEnd.AddItem($"Max End|{Utilities.FixDP(displayStats.EnduranceMaxEnd)}%", 
    Math.Max(0, displayStats.EnduranceMaxEnd), 0, iTip3);
graphMaxEnd.Max = 150;
graphMaxEnd.MarkerValue = 100;
graphMaxEnd.Draw();

// End Use bar
graphDrain.Clear();
graphDrain.AddItem($"EndUse|{MidsContext.Character.Totals.EndUse:##0.##}/s", 
    MidsContext.Character.Totals.EndUse, 
    MidsContext.Character.Totals.EndUse, 
    drainTip);
graphDrain.Max = 4;
graphDrain.Draw();

// End Recovery bar
graphRec.Clear();
graphRec.AddItem($"EndRec|{displayStats.EnduranceRecoveryPercentage(false):###0}% ({displayStats.EnduranceRecoveryNumeric:##0.##}/s)", 
    Math.Max(0, displayStats.EnduranceRecoveryPercentage(false)), 
    Math.Max(0, displayStats.EnduranceRecoveryPercentage(true)), 
    recTip);
graphRec.Max = 400;
graphRec.MarkerValue = 100;
graphRec.Draw();
```

#### 2. frmTotalsV2.cs (Modern Implementation)

**File**: `external/dev/MidsReborn/MidsReborn/Forms/WindowMenuItems/frmTotalsV2.cs`

**Health Section** (lines 708-744):
```csharp
graphHP.Clear();
var regenValue = displayStats.HealthRegenPercent(false);
var regenValueUncapped = displayStats.HealthRegenPercent(true);
const float regenBase = 100;
graphHP.AddItemPair("Regeneration",
    $"{regenValue:###0.##}%",
    Math.Max(0, regenBase),
    Math.Max(0, regenValue),
    Math.Max(0, regenValueUncapped),
    (regenValueUncapped > regenValue & regenValue > 0
        ? $"{regenValueUncapped:##0.##}% Regeneration, capped at {regenValue:##0.##}%"
        : $"{regenValue:##0.##}% Regeneration"
    ) +
    $" ({MidsContext.Character.DisplayStats.HealthRegenHPPerSec:##0.##} HP/s)" +
    (regenBase > 0 ? $"\r\nBase: {regenBase:##0.##}%" : ""));

var hpValue = displayStats.HealthHitpointsNumeric(false);
var hpValueUncapped = displayStats.HealthHitpointsNumeric(true);
var hpBase = MidsContext.Character.Archetype.Hitpoints;
var absorbValue = Math.Min(displayStats.Absorb, hpBase);
graphHP.AddItemPair("Max HP", $"{hpValue:###0.##}",
    Math.Max(0, hpBase),
    Math.Max(0, hpValue),
    Math.Max(0, hpValueUncapped),
    Math.Max(0, absorbValue),
    (hpValueUncapped > hpValue & hpValue > 0
        ? $"{hpValueUncapped:##0.##} HP, capped at {MidsContext.Character.Archetype.HPCap} HP"
        : $"{hpValue:##0.##} HP ({atName} HP cap: {MidsContext.Character.Archetype.HPCap} HP)"
    ) +
    $"\r\nBase: {hpBase:##0.##} HP" +
    (absorbValue > 0
        ? $"\r\nAbsorb: {absorbValue:##0.##} ({absorbValue / hpBase * 100:##0.##}% of base HP)"
        : ""));
```

**Endurance Section** (lines 746-774):
```csharp
graphEnd.Clear();
var endRecValue = displayStats.EnduranceRecoveryNumeric;
var endRecValueUncapped = displayStats.EnduranceRecoveryNumericUncapped;
var endRecBase = MidsContext.Character.Archetype.BaseRecovery * displayStats.EnduranceMaxEnd / 60f;
graphEnd.AddItemPair("End Rec", $"{endRecValue:##0.##}/s",
    Math.Max(0, endRecBase),
    Math.Max(0, endRecValue),
    Math.Max(0, endRecValueUncapped),
    (endRecValueUncapped > endRecValue & endRecValue > 0
        ? $"{endRecValueUncapped:##0.##}/s End. ({displayStats.EnduranceRecoveryPercentage(true):##0.##}%), capped at {MidsContext.Character.Archetype.RecoveryCap * 100:##0.##}%"
        : $"{endRecValue:##0.##}/s End. ({displayStats.EnduranceRecoveryPercentage(false):##0.##}%) ({atName} End. recovery cap: {MidsContext.Character.Archetype.RecoveryCap * 100:##0.##}%)"
    ) +
    $"\r\nBase: {endRecBase:##0.##}/s");

graphEnd.AddItemPair("End Use",
    $"{displayStats.EnduranceUsage:##0.##}/s",
    0,
    displayStats.EnduranceUsage,
    $"{displayStats.EnduranceUsage:##0.##}/s End. (Net gain: {displayStats.EnduranceRecoveryNet:##0.##}/s)");

const float maxEndBase = 100;
graphEnd.AddItemPair("Max End",
    $"{displayStats.EnduranceMaxEnd:##0.##}",
    maxEndBase,
    displayStats.EnduranceMaxEnd,
    $"{displayStats.EnduranceMaxEnd:##0.##} Maximum Endurance (base: {maxEndBase:##0.##})");
```

**Recharge Section** (lines 786-792):
```csharp
graphHaste.Clear();
graphHaste.AddItemPair("Haste",
    $"{displayStats.BuffHaste(false):##0.##}%",
    100,
    Math.Max(0, displayStats.BuffHaste(false)),
    Math.Max(0, displayStats.BuffHaste(true)),
    GenericDataTooltip3(displayStats.BuffHaste(false), 100, displayStats.BuffHaste(true), "Haste"));
```

#### 3. Statistics.cs (Calculation Methods)

**File**: `external/dev/MidsReborn/MidsReborn/Core/Statistics.cs`

**Constants** (line 22):
```csharp
internal const float BaseMagic = 1.666667f;
```

**Endurance Properties** (lines 35-51):
```csharp
public float EnduranceMaxEnd => _character.Totals.EndMax + 100f;

public float EnduranceRecoveryNumeric => 
    EnduranceRecovery(false) * (_character.Archetype.BaseRecovery * BaseMagic) * 
    (_character.TotalsCapped.EndMax / 100 + 1);

public float EnduranceRecoveryNumericUncapped => 
    EnduranceRecovery(true) * (_character.Archetype.BaseRecovery * BaseMagic) * 
    (_character.Totals.EndMax / 100 + 1);

public float EnduranceTimeToFull => EnduranceMaxEnd / EnduranceRecoveryNumeric;

public float EnduranceRecoveryNet => EnduranceRecoveryNumeric - EnduranceUsage;

public float EnduranceRecoveryLossNet => (float)-(EnduranceRecoveryNumeric - (double)EnduranceUsage);

public float EnduranceTimeToZero => 
    EnduranceMaxEnd / (float)-(EnduranceRecoveryNumeric - (double)EnduranceUsage);

public float EnduranceTimeToFullNet => EnduranceMaxEnd / (EnduranceRecoveryNumeric - EnduranceUsage);

public float EnduranceUsage => _character.Totals.EndUse;
```

**Health Properties** (lines 55-57):
```csharp
public float HealthRegenHPPerSec => 
    (float)(HealthRegen(false) * (double)_character.Archetype.BaseRegen * 
    1.66666662693024 * HealthHitpointsNumeric(false) / 100.0);

public float HealthRegenTimeToFull => HealthHitpointsNumeric(false) / HealthRegenHPPerSec;
```

**Recharge Property** (lines 231-236):
```csharp
public const float MaxHaste = 400f;  // Hard cap for display

public float BuffHaste(bool uncapped)
{
    return !uncapped
        ? Math.Min(MaxHaste, (_character.TotalsCapped.BuffHaste + 1) * 100)
        : (_character.Totals.BuffHaste + 1) * 100;
}
```

**Health Methods** (lines 84-89):
```csharp
public float HealthRegenPercent(bool uncapped)
{
    return HealthRegen(uncapped) * 100f;
}

public float HealthHitpointsNumeric(bool uncapped)
{
    // Implementation extracts HP value
}
```

**Endurance Methods** (lines 69-76):
```csharp
private float EnduranceRecovery(bool uncapped)
{
    return uncapped
        ? _character.Totals.EndRec + 1f
        : _character.TotalsCapped.EndRec + 1f;
}

public float EnduranceRecoveryPercentage(bool uncapped)
{
    return EnduranceRecovery(uncapped) * 100f;
}
```

#### 4. clsToonX.cs (Global Recharge Aggregation)

**File**: `external/dev/MidsReborn/MidsReborn/clsToonX.cs`

**Recharge Aggregation** (line 766):
```csharp
Totals.BuffHaste = _selfEnhance.Effect[(int)Enums.eStatType.Haste] + 
                   _selfBuffs.Effect[(int)Enums.eStatType.Haste];
```

**Recharge Capping** (line 863):
```csharp
TotalsCapped.BuffHaste = Math.Min(TotalsCapped.BuffHaste, Archetype.RechargeCap - 1);
```

---

**Implementation Checklist**:

Epic 4.2 Components:
- [ ] Extend `POST /api/calculations/totals` response with health, endurance, recharge, buffs data
- [ ] Create `HPPanel.tsx` component
  - [ ] Regeneration StatBar (green, base 100%)
  - [ ] Max HP StatBar (green, numeric)
  - [ ] Absorb layer visualization (if absorb > 0)
  - [ ] Tooltips with HP/s and time to full
- [ ] Create `EndurancePanel.tsx` component
  - [ ] End Recovery StatBar (blue, /s format)
  - [ ] End Usage StatBar (blue/red, /s format)
  - [ ] Max End StatBar (blue, numeric)
  - [ ] Net recovery calculation and display
  - [ ] Tooltips with net recovery, time to full/zero
- [ ] Create `RechargePanel.tsx` component
  - [ ] Global Recharge StatBar (purple, base 100%)
  - [ ] Perma-Hasten indicator (if >= 170%)
  - [ ] Tooltip with cap info
- [ ] Create `MiscStatsPanel.tsx` component
  - [ ] Accuracy StatBar (base 0%)
  - [ ] ToHit StatBar (base 0%)
  - [ ] Damage StatBar (base 100%)
  - [ ] Tooltips with explanations
- [ ] Extend `TotalsPanel.tsx` to include new panels
- [ ] Add color schemes (green, blue, purple)
- [ ] Add animations for value changes
- [ ] Test with various builds (low/high regen, net positive/negative end, perma-Hasten)
- [ ] Verify calculations match MidsReborn exactly
