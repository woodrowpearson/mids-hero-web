# MidsReborn Reference Screenshots

**Purpose**: Store screenshots from the MidsReborn desktop application for visual reference during Mids Hero Web frontend development.

**Location**: `/Users/w/code/mids-hero-web/shared/user/midsreborn-screenshots/`

---

## Usage

These screenshots are used by the frontend development workflow to:

1. **Visual Reference**: Compare our web implementation with MidsReborn's desktop UI
2. **Feature Discovery**: Identify UI patterns and behaviors from the reference app
3. **UX Parity**: Ensure functional parity (not pixel-perfect match) with MidsReborn

---

## Screenshot Guidelines

### Recommended Screenshots

1. **Main Window - Full UI Layout**
   - Filename: `midsreborn-main-window.png`
   - Shows: Complete main window with all panels visible, character created with powers slotted

2. **Character Creation - Initial State**
   - Filename: `midsreborn-character-creation.png`
   - Shows: Empty build, archetype dropdown, origin/alignment selectors

3. **Power Selection Panel**
   - Filename: `midsreborn-power-selection.png`
   - Shows: Primary/Secondary power lists, available vs unavailable powers

4. **Enhancement Picker (I9Picker) - Set IOs Tab**
   - Filename: `midsreborn-i9picker-set-tab.png`
   - Shows: Enhancement picker popup with Set IOs tab, enhancement grid, selectors

5. **Enhancement Picker - Normal Tab**
   - Filename: `midsreborn-i9picker-normal-tab.png`
   - Shows: TO/DO/SO enhancements tab

6. **Power with Slotted Enhancements**
   - Filename: `midsreborn-power-slotted.png`
   - Shows: Close-up of power entry with 6 slots filled with IOs

7. **Totals Window (frmTotals)**
   - Filename: `midsreborn-totals-window.png`
   - Shows: Floating totals window with defense/resistance/HP bars

8. **Set Viewer Window**
   - Filename: `midsreborn-set-viewer.png`
   - Shows: Set viewer with slotted sets list and bonus breakdown

9. **Recipe Viewer Window**
   - Filename: `midsreborn-recipe-viewer.png`
   - Shows: Recipe viewer with salvage requirements

10. **Build Sharing - ShareMenu**
    - Filename: `midsreborn-share-menu.png`
    - Shows: ShareMenu dialog with multiple tabs (Data, Forum, Links, InfoGraphic)

11. **Pool Powers Panel**
    - Filename: `midsreborn-pool-powers.png`
    - Shows: Scrollable pool powers area with 4 pool selectors

12. **Menu Bar**
    - Filename: `midsreborn-menu-bar.png`
    - Shows: Top menu with File/Character/View/Window menus expanded

### Capture Tips

- **Theme**: Use default Hero theme (blue)
- **Example Character**: Create a simple build (e.g., "Brute - Super Strength / Willpower")
- **Enhancement Slotting**: Slot some common IO sets (Luck of the Gambler, Numina's)
- **Resolution**: 1920x1080 or higher
- **Format**: PNG
- **Naming**: Use descriptive filenames with `midsreborn-` prefix
- **Annotations**: Optional - add arrows/labels if helpful

---

## How Frontend Agents Use These Screenshots

The `frontend-development` skill workflow:

1. **Phase 1: Context Collection** - Lists available screenshots in this directory
2. **Phase 2: MidsReborn UI Analysis** - References screenshots for feature identification
3. **Phase 3: Planning** - Uses screenshots to inform component design
4. **Phase 5: Visual Verification** - Compares our implementation against screenshots

---

## Adding New Screenshots

When capturing new screenshots from MidsReborn:

1. Open MidsReborn desktop application
2. Navigate to the feature/screen you want to capture
3. Take screenshot (Windows: `Win+Shift+S`, Mac: `Cmd+Shift+4`)
4. Save to this directory: `/Users/w/code/mids-hero-web/shared/user/midsreborn-screenshots/`
5. Use descriptive filename: `midsreborn-[feature]-[state].png`
6. Screenshots will be automatically detected by frontend development workflow

---

**Note**: These screenshots are for reference only. Our web implementation aims for **functional UX parity** (same features, similar layout) with a **modern web aesthetic** (not pixel-perfect clone).
