# MidsReborn UI Analysis: Epic 1.1 - Visual Style Baseline

**Created**: 2025-11-14
**Epic**: 1.1 - Next.js + Design System Setup
**Purpose**: Establish visual design baseline for web implementation

## Executive Summary

MidsReborn is a dense, information-rich desktop application with a dark theme featuring strong blue/cyan accents. The UI prioritizes functionality over aesthetics with a multi-panel layout, tabbed interfaces, and color-coded information systems. Our web implementation should preserve the functional, data-focused approach while modernizing the aesthetic with improved spacing, responsive design patterns, and web-native interactions.

## Screenshot Analysis

### Screenshot 1: mids-new-build.png (Main Build Editor)
- **Shows**: Primary build creation interface with power selection grid, enhancement slots, and detailed statistics
- **Key UI elements**: Tabbed power pools (rows/columns), dark panels for power descriptions, blue highlight selection, color-coded stat categories (green, cyan, purple bars)
- **Visual patterns**: Dense grid layout with floating information panels, heavy use of color for categorization, compact typography for data density

### Screenshot 2: pool-desc-mouse-over.png (Power Pool Hover)
- **Shows**: Detailed power pool description tooltip with orange highlight accent
- **Key UI elements**: Dark modal/tooltip with orange header, multi-line text description, color-coded power information
- **Visual patterns**: Orange accent color for highlights, white text on dark background, clear information hierarchy within tooltip

### Screenshot 3: power-desc-mouse-over.png (Power Detail Hover)
- **Shows**: Comprehensive power description with enhancement values, inherited powers, and set bonuses
- **Key UI elements**: Modal overlay with cyan/blue accents, green checkmarks for active powers, detailed stat breakdown in light green/cyan text
- **Visual patterns**: Layered information with color-coding: cyan for headers, green for positive stats, monospace for calculations

### Screenshot 4: power-enh-slot-pick.png (Enhancement Slot Picker)
- **Shows**: Grid of available enhancements with set icons and inventory icons
- **Key UI elements**: Hexagonal/circular set bonus icons, numbered level indicators, dark background grid
- **Visual patterns**: Icon-heavy UI, dark grid on darker background, small number badges for inventory counts

### Screenshot 5: power-enh.png (Enhancement Details)
- **Shows**: Full build view with enhancement details and derived stat calculations
- **Key UI elements**: Dark panels with stat calculations, orange power name highlight, color-coded damage breakdown (red), green beneficial effects
- **Visual patterns**: Heavy use of color for damage types, calculation displays in monospace, active/inactive states clearly differentiated

### Screenshot 6: build-active-sets-bonuses.png (Set Bonuses View)
- **Shows**: Two-column layout comparing applied bonus effects and effect breakdown
- **Key UI elements**: White text on black panels, blue highlight selection for active set, scrollable content areas
- **Visual patterns**: Simple column layout, blue selection highlight (#0066FF or similar), white borders separating sections

### Screenshot 7: total-screen-1.png (Stats Summary - Compact)
- **Shows**: Compact cumulative stats display with color-coded categories
- **Key UI elements**: Green background for defense stats, cyan for resistance, purple for other effects, tabbed interface (INFO/EFFECTS/TOTALS/ENHANCE)
- **Visual patterns**: Solid color backgrounds for stat categories, high contrast white text, compact vertical layout

### Screenshot 8: view-total-window.png (Stats Summary - Expanded)
- **Shows**: Expanded totals window with detailed stat breakdowns and progress bars
- **Key UI elements**: Large color-coded sections (purple for defense/damage calculations, cyan for resistance, green for health/endurance), progress bars with color fills, bottom action buttons
- **Visual patterns**: Clear section separation with solid color backgrounds, large progress bars, action buttons at bottom (Keep/Close pattern)

## Visual Design Patterns

### Color Scheme

- **Background**: Solid black (#000000) - dominant UI background throughout application
- **Panel backgrounds**: Very dark gray/charcoal (#1a1a1a or #222222) - slightly raised from main background
- **Primary accent**: Bright cyan (#00CCFF or #00FFFF) - used for selected items, headers, important information
- **Secondary accent**: Bright blue (#0066FF or #0080FF) - selection highlights, button focus states
- **Orange accent**: Bright orange (#FF9900 or #FFAA00) - power names, special highlights, secondary importance
- **Text - Primary**: White (#FFFFFF) - main text, labels
- **Text - Secondary**: Light gray (#CCCCCC) - secondary information
- **Status colors**:
  - **Green (#00CC00 or #00FF00)**: Positive effects, beneficial stats, active selections, health
  - **Red (#FF3333 or #CC0000)**: Negative effects, damage calculations, resistance reductions
  - **Purple/Magenta (#9933FF or #CC66FF)**: Defense calculations, damage type mitigation, category header
  - **Cyan (#00CCFF)**: Resistance metrics, healing, recovery, information panels

### Layout Patterns

- **Overall layout**: Multi-panel dashboard with fixed left sidebar (power lists), main central grid (enhancement slots), right panels (descriptions/details)
- **Information density**: Very high - maximizes viewport usage, minimal whitespace, compact component sizing
- **Panel organization**: Vertical stacking of collapsible panels, tabbed interfaces for related content, floating modals for details
- **Scrolling**: Vertical scroll for long lists (power pools), horizontal scroll for enhancement grids, contained scrolling within panels
- **Grid system**: Enhancement slots displayed in 4-column grid at 35px spacing, power panels in 3-4 column layout

### Typography

- **Font style**: Sans-serif system fonts (appears to be Windows system font family)
- **Size hierarchy**:
  - Headers: 14-16px bold (power names, section titles)
  - Body: 11-12px regular (stats, descriptions)
  - Small: 9-10px (secondary labels, inventory counts)
- **Readability**: High contrast white on black, maintained even at small sizes, monospace for calculations and code-like data

### Component Patterns

1. **Buttons**: Blue/cyan solid backgrounds with white text, rectangular with slight rounded corners, clear hover states with lighter shade
2. **Dropdowns**: Styled as buttons with downward arrow, dropdown menu has dark background matching panels
3. **Tooltips**: Dark modal overlays with colored header bars (orange, cyan), white body text, border separation between header and content
4. **Panels/Cards**: Dark backgrounds with white borders (1-2px), contain related information, support scrolling and minimize/maximize states
5. **Tables/Grids**: Light text on dark background, column headers use color to denote type, alternating row emphasis subtle or absent
6. **Progress bars**: Color-coded by stat type (green for health, blue for endurance, etc.), with percentage text overlay, gradient fills
7. **Icons**: 24-32px hexagonal set icons, small inventory count badges, colored by damage type or set category
8. **Selection indicators**: Blue highlight overlay, bright borders, or background color change

## Design System Requirements for Epic 1.1

### Tailwind Configuration

Recommended custom colors to add:

```js
colors: {
  'mids-black': '#000000',
  'mids-dark': '#1a1a1a',
  'mids-panel': '#222222',
  'mids-accent-cyan': '#00CCFF',
  'mids-accent-blue': '#0066FF',
  'mids-accent-orange': '#FF9900',
  'mids-text-primary': '#FFFFFF',
  'mids-text-secondary': '#CCCCCC',
  'mids-status-green': '#00CC00',
  'mids-status-red': '#FF3333',
  'mids-status-purple': '#9933FF',
}
```

### shadcn/ui Components Needed (Initial Set for Epic 1.1)

For Epic 1.1 base setup, install:
- **Button** - Primary UI action, multiple variants (primary/secondary), blue/cyan styling
- **Dialog** - Modal overlays for tooltips, descriptions, detailed information
- **Select** - Dropdowns for power pool selection, sorting options
- **Tabs** - Tabbed interface for INFO/EFFECTS/TOTALS/ENHANCE views
- **Tooltip** - Hover information display with dark background and colored headers

Additional components for later epics (defer to 1.2+):
- **Table** - Power lists, stat breakdowns, set bonus lists
- **Slider** - Enhancement allocation controls
- **Checkbox** - Enhancement slot selection, enhancement options
- **Progress** - Stat progress bars, resource bars
- **Scroll Area** - Managed scrolling for dense content areas
- **Popover** - Enhancement detail popups

### Layout Approach

- **Desktop-first**: MidsReborn is desktop-only (primary target 1920x1080+), web version should prioritize desktop experience
- **Responsive breakpoints**: 
  - Desktop: 1920px+ (full multi-panel layout)
  - Tablet: 1024-1919px (collapsible left sidebar, main content focus)
  - Mobile: <1024px (single-column stack, tab-based navigation)
- **Grid system**: 
  - Enhancement slots: CSS Grid with 4 columns at base, responsive to 2-3 columns on smaller screens
  - Panels: Flexbox vertical stack with fixed sidebar width (280px), main content area flexible
  - Information density: Maintain compact spacing for desktop (8-12px), expand slightly for tablet (12-16px)

## Adaptation Strategy for Web

### Keep from MidsReborn

- Dark theme with cyan/blue accents (strong brand recognition for CoH community)
- Color-coded stat categories (green=health/beneficial, red=negative, purple=defense)
- Dense information display with high data visibility
- Multi-panel dashboard approach for power building workflow
- Tabbed interfaces for related content grouping

### Improve for Web

- Modernize spacing and padding (reduce information density slightly for readability)
- Add smooth transitions and animations for state changes
- Improve mobile responsiveness with collapsible panels
- Use modern CSS Grid instead of absolute positioning
- Add visual feedback (loading states, hover animations)
- Implement keyboard navigation and accessibility features
- Use web-native font stack (system fonts) for better performance
- Add responsive typography (larger text on mobile)

## Next Steps for Epic 1.1

Based on this analysis:

1. Initialize Next.js 14 project with TypeScript
2. Configure Tailwind CSS with custom MidsReborn color palette
3. Install initial shadcn/ui component set (Button, Dialog, Select, Tabs, Tooltip)
4. Create base layout component with header, sidebar placeholder, main content area
5. Set up typography system matching MidsReborn (11-12px body, 14-16px headers)
6. Create theme provider with dark mode enabled by default
7. Implement basic dashboard grid layout (sidebar + main + right panels)
8. Add storybook or component library setup for design system documentation

---

**Visual Baseline**: MidsReborn presents a functional, data-dense interface that rewards expert users with quick information access. Our web implementation should respect this expertise while adding modern web UX patterns and accessibility improvements.
