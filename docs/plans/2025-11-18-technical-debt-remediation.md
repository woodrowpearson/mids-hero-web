# Technical Debt Remediation Plan

**Date**: 2025-11-18
**Status**: Planning
**Priority**: High
**Estimated Effort**: 8-12 hours

## Overview

This plan addresses pre-existing TypeScript errors and test failures discovered during Epic 2.2 troubleshooting. Issues are organized by the Epic that introduced them to provide context for code review and remediation.

**Total Issues**:
- 28 TypeScript type errors
- 11 component test failures

**Impact**: These issues prevent clean CI/CD pipeline execution and may hide new issues introduced by future changes.

---

## Epic 1.2: State Management (characterStore)

**Branch**: `claude/frontend-dev-epic-1-2-01EMK8gS3pPNGr2zstQeYc5D`
**Commit**: `58ef19e87` - "feat: implement Epic 1.2 state management infrastructure"
**Files Affected**:
- `stores/characterStore.ts`
- `__tests__/stores/characterStore.test.ts`

### Issues

#### 1.2.1: Unused Type Imports (3 errors)
**Location**: `stores/characterStore.ts:11,18,22`

```typescript
// ERROR: Type imports declared but never used
import type {
  Character,    // Line 11 - TS6196
  Slot,         // Line 18 - TS6196
  PowersetSlots // Line 22 - TS6196
} from "@/types/character.types";
```

**Root Cause**: Types imported for future use but not yet implemented in store interface.

**Fix**:
```typescript
// Option A: Remove unused imports
import type {
  Archetype,
  Origin,
  // Character, Slot, PowersetSlots - removed, will re-add when needed
  BuildData,
  CalculatedTotals,
} from "@/types/character.types";

// Option B: Use in type annotations
export interface CharacterState {
  // Add these fields if they're needed
  character?: Character;  // Make optional if not ready
  slots?: Slot[];
  powersetSlots?: PowersetSlots;
}
```

**Verification**:
```bash
npm run type-check | grep "characterStore.ts"
# Should show 0 errors for these lines
```

---

#### 1.2.2: Power Object Possibly Undefined (6 errors)
**Location**: `stores/characterStore.ts:153,161,163,173,179,188,189`

```typescript
// Line 153 - ERROR: power may be undefined
const newEntry = {
  level,
  power,  // Type 'Power | undefined' not assignable to 'Power'
  slots: power?.initialSlots?.map((slot) => ({
    enhancement: null,
    level: slot.level,
  })),
};

// Lines 161,163,173,179,188,189 - ERROR: power is possibly undefined
power.id           // Line 161
power.name         // Line 163
power.initialSlots // Line 173,179
```

**Root Cause**: `getPowerById()` returns `Power | undefined`, but code assumes it always exists.

**Fix**:
```typescript
// In addPower function
addPower: (powerId: number, level: number) => {
  const power = get().getPowerById(powerId);

  // Guard clause - handle undefined case
  if (!power) {
    console.error(`Power ${powerId} not found`);
    return;
  }

  const newEntry: PowerEntry = {
    level,
    power,  // Now guaranteed to be Power, not undefined
    slots: power.initialSlots?.map((slot) => ({
      enhancement: null,
      level: slot.level ?? level,  // Also fix slot.level undefined
    })) || [],
  };

  set((state) => ({
    powers: [...state.powers, newEntry],
  }));
}
```

**Verification**:
```bash
npm run type-check | grep "stores/characterStore.ts"
# Lines 153,161,163,173,179,188,189 should have 0 errors
```

---

#### 1.2.3: BuildData Type Mismatch (1 error)
**Location**: `stores/characterStore.ts:217`

```typescript
// ERROR: totals is CalculatedTotals | null, but BuildData expects | undefined
exportBuild: (): BuildData => ({
  character: { ... },
  powersets: { ... },
  powers: get().powers,
  totals: get().totals,  // Line 217 - Type 'null' not assignable
})
```

**Root Cause**: Store uses `null` for missing totals, but BuildData type expects `undefined`.

**Fix Option A - Change Store**:
```typescript
// In CharacterState interface
export interface CharacterState {
  totals: CalculatedTotals | undefined;  // Change from | null
  // ...
  setTotals: (totals: CalculatedTotals | undefined) => void;
}

// Update all references from null to undefined
const useCharacterStore = create<CharacterState>()(
  devtools(
    persist(
      (set, get) => ({
        totals: undefined,  // Changed from null
        setTotals: (totals) => set({ totals }),
      })
    )
  )
);
```

**Fix Option B - Change BuildData Type**:
```typescript
// In types/character.types.ts
export interface BuildData {
  character: Character;
  powersets: PowersetSlots;
  powers: PowerEntry[];
  totals?: CalculatedTotals | null;  // Add | null
}
```

**Recommended**: Option A (use undefined consistently)

**Verification**:
```bash
npm run type-check | grep "stores/characterStore.ts:217"
# Should show 0 errors
```

---

#### 1.2.4: CharacterStore Test Failures (11 errors)
**Location**: `__tests__/stores/characterStore.test.ts:101,102,124,143,156,167,168,180`

```typescript
// ERROR: Object is possibly 'undefined'
expect(state.powers[0].power.id).toBe(1);      // Line 101
expect(state.powers[0].power.name).toBe(...);  // Line 102
// ... repeated pattern on lines 124,143,156,167,168,180
```

**Root Cause**: Tests don't guard against undefined power objects.

**Fix**:
```typescript
// Add type assertions or guards
it("adds power correctly", () => {
  const { result } = renderHook(() => useCharacterStore());

  result.current.addPower(1, 1);
  const state = result.current;

  // Option A: Type assertion (if we're confident power exists)
  expect(state.powers[0]!.power!.id).toBe(1);

  // Option B: Guard assertion (safer)
  expect(state.powers[0]?.power?.id).toBe(1);

  // Option C: Explicit check (best for tests)
  expect(state.powers).toHaveLength(1);
  const power = state.powers[0]?.power;
  expect(power).toBeDefined();
  expect(power?.id).toBe(1);
  expect(power?.name).toBe("Expected Name");
});
```

**Verification**:
```bash
npm run type-check | grep "characterStore.test.ts"
# Should show 0 errors
```

---

## Epic 1.3: Layout Shell + Navigation

**Branch**: Branch merged to main
**Commit**: `d30851a7c` - "feat: implement Epic 1.3 - Layout Shell + Navigation"
**Files Affected**:
- `components/layout/BuildLayout.tsx`
- `components/layout/SidePanel.tsx`
- `__tests__/components/layout/BuildLayout.test.tsx`
- `__tests__/components/layout/SidePanel.test.tsx`

### Issues

#### 1.3.1: Unused Variable isSidebarVisible (1 error)
**Location**: `components/layout/BuildLayout.tsx:39`

```typescript
export function BuildLayout({ ... }: BuildLayoutProps) {
  const { columnLayout, sidebarCollapsed } = useUIStore();
  const columns = columnCount ?? columnLayout;

  // Line 39 - ERROR: 'isSidebarVisible' is declared but never used
  const isSidebarVisible = showSidebar && !sidebarCollapsed;

  return (
    <div className="flex flex-col h-screen bg-background">
      <TopPanel />
      <div className="flex flex-1 overflow-hidden">
        {/* Uses showSidebar directly, not isSidebarVisible */}
        {showSidebar && <SidePanel collapsed={sidebarCollapsed} />}
        ...
      </div>
    </div>
  );
}
```

**Root Cause**: Variable calculated but never used - logic uses `showSidebar` prop directly.

**Fix Option A - Use the Variable**:
```typescript
// Use isSidebarVisible instead of showSidebar
const isSidebarVisible = showSidebar && !sidebarCollapsed;

return (
  <div className="flex flex-col h-screen bg-background">
    <TopPanel />
    <div className="flex flex-1 overflow-hidden">
      {isSidebarVisible && <SidePanel collapsed={false} />}
      ...
    </div>
  </div>
);
```

**Fix Option B - Remove Variable**:
```typescript
// Remove unused variable
export function BuildLayout({ ... }: BuildLayoutProps) {
  const { columnLayout, sidebarCollapsed } = useUIStore();
  const columns = columnCount ?? columnLayout;
  // Removed: const isSidebarVisible = showSidebar && !sidebarCollapsed;

  return (
    <div className="flex flex-col h-screen bg-background">
      <TopPanel />
      <div className="flex flex-1 overflow-hidden">
        {showSidebar && <SidePanel collapsed={sidebarCollapsed} />}
        ...
      </div>
    </div>
  );
}
```

**Recommended**: Option A (use the variable - it has better semantics)

**Verification**:
```bash
npm run type-check | grep "BuildLayout.tsx:39"
# Should show 0 errors
```

---

#### 1.3.2: BuildLayout Test Failures (2 failures)
**Files**: `__tests__/components/layout/BuildLayout.test.tsx`

##### Test 1: "renders TopPanel component"
```typescript
it("renders TopPanel component", () => {
  render(<BuildLayout>Test Content</BuildLayout>);

  // FAILS: Cannot find TopPanel
  expect(screen.getByRole("banner")).toBeInTheDocument();
});
```

**Root Cause**: TopPanel may not render with default character store state.

**Fix**:
```typescript
it("renders TopPanel component", () => {
  // Set up required store state
  useCharacterStore.setState({
    name: "Test Hero",
    archetype: mockArchetype,
    level: 1,
  });

  render(<BuildLayout>Test Content</BuildLayout>);

  // TopPanel should now render properly
  const header = screen.getByRole("banner");
  expect(header).toBeInTheDocument();
  expect(screen.getByText("Test Hero")).toBeInTheDocument();
});
```

##### Test 2: "respects sidebar collapsed state from uiStore"
```typescript
it("respects sidebar collapsed state from uiStore", async () => {
  render(<BuildLayout>Test Content</BuildLayout>);

  // FAILS: Sidebar behavior not matching expectations
  expect(screen.queryByRole("complementary")).not.toBeInTheDocument();
});
```

**Root Cause**: Test expectations don't match actual component behavior with collapsing.

**Fix**:
```typescript
it("respects sidebar collapsed state from uiStore", async () => {
  // Set collapsed state BEFORE rendering
  useUIStore.setState({ sidebarCollapsed: true });

  render(<BuildLayout>Test Content</BuildLayout>);

  // Sidebar should still exist but be visually collapsed (width: 0)
  const sidebar = screen.getByRole("complementary");
  expect(sidebar).toHaveStyle({ width: "0px" });
  expect(sidebar).toHaveAttribute("aria-hidden", "true");
});
```

**Verification**:
```bash
npm test -- BuildLayout.test.tsx --run
# Should show 2/2 tests passing
```

---

#### 1.3.3: SidePanel Test Failures (2 failures)
**Files**: `__tests__/components/layout/SidePanel.test.tsx`

##### Test 1: "collapses to zero width when collapsed prop is true"
```typescript
it("collapses to zero width when collapsed prop is true", () => {
  render(<SidePanel collapsed={true} />);

  const panel = screen.getByRole("complementary");
  // FAILS: Expected width: 0px
  expect(panel).toHaveStyle({ width: "0px" });
});
```

**Root Cause**: Component uses CSS classes for collapse, not inline width style.

**Fix**:
```typescript
it("collapses to zero width when collapsed prop is true", () => {
  render(<SidePanel collapsed={true} />);

  const panel = screen.getByRole("complementary");

  // Check for collapsed class instead of inline style
  expect(panel).toHaveClass("w-0");  // Tailwind class
  // OR check computed style if needed
  const computedStyle = window.getComputedStyle(panel);
  expect(computedStyle.width).toBe("0px");
});
```

##### Test 2: "has aria-hidden attribute when collapsed"
```typescript
it("has aria-hidden attribute when collapsed", () => {
  render(<SidePanel collapsed={true} />);

  const panel = screen.getByRole("complementary");
  // FAILS: aria-hidden not set
  expect(panel).toHaveAttribute("aria-hidden", "true");
});
```

**Root Cause**: Component doesn't set aria-hidden when collapsed.

**Fix in Component**:
```typescript
// In SidePanel.tsx
export function SidePanel({ collapsed }: SidePanelProps) {
  return (
    <aside
      role="complementary"
      aria-hidden={collapsed}  // Add this
      className={cn(
        "border-r bg-background transition-all duration-300",
        collapsed ? "w-0" : "w-64"
      )}
    >
      {!collapsed && (
        <div className="p-4">
          {/* Content */}
        </div>
      )}
    </aside>
  );
}
```

**Verification**:
```bash
npm test -- SidePanel.test.tsx --run
# Should show 2/2 tests passing for these
```

---

## Epic 1.4: API Client Integration

**Branch**: Branch merged to main
**Commit**: `0f80bd207` - "feat: implement Epic 1.4 - API Client Integration"
**Files Affected**:
- `hooks/useCalculations.ts`
- `hooks/useArchetypes.ts`
- `hooks/useKeyboardShortcuts.ts`
- `hooks/useAutoCalculate.ts`
- `__tests__/hooks/useCalculations.test.tsx`
- `__tests__/hooks/usePowersets.test.tsx`
- `__tests__/app/builder/page.test.tsx`

### Issues

#### 1.4.1: Unused Import in useArchetypes (1 error)
**Location**: `hooks/useArchetypes.ts:7`

```typescript
// Line 7 - ERROR: 'Archetype' is declared but never used
import { Archetype } from "@/types/character.types";
import { archetypeApi } from "@/services";
```

**Root Cause**: Type import not used (useQuery handles typing automatically).

**Fix**:
```typescript
// Remove unused import
import { archetypeApi } from "@/services";
// Archetype type is inferred from API response
```

**Verification**:
```bash
npm run type-check | grep "useArchetypes.ts:7"
# Should show 0 errors
```

---

#### 1.4.2: Unused Parameter in useKeyboardShortcuts (1 error)
**Location**: `hooks/useKeyboardShortcuts.ts:11`

```typescript
// Line 11 - ERROR: 'e' is declared but never used
const handleKeyPress = (e: KeyboardEvent) => {
  // Function body doesn't use 'e' parameter
};
```

**Root Cause**: Parameter declared but not accessed in function body.

**Fix Option A - Use Parameter**:
```typescript
const handleKeyPress = (e: KeyboardEvent) => {
  // Prevent default behavior
  if (e.ctrlKey && e.key === "s") {
    e.preventDefault();
    // Save logic
  }
};
```

**Fix Option B - Remove/Underscore**:
```typescript
// Prefix with underscore to indicate intentionally unused
const handleKeyPress = (_e: KeyboardEvent) => {
  // Logic doesn't need event object
};
```

**Recommended**: Option A (use the parameter for preventDefault, etc.)

**Verification**:
```bash
npm run type-check | grep "useKeyboardShortcuts.ts:11"
# Should show 0 errors
```

---

#### 1.4.3: useAutoCalculate Incorrect Arguments (1 error)
**Location**: `hooks/useAutoCalculate.ts:74`

```typescript
// Line 74 - ERROR: Expected 1 arguments, but got 2
calculateTotals(buildData, {
  onSuccess: (data) => setTotals(data),
  onError: () => setIsCalculating(false),
});
```

**Root Cause**: TanStack Query mutation signature changed, expects single request object.

**Fix**:
```typescript
// Correct mutation call signature
calculateTotals(
  { buildData },  // Single argument: CalculateTotalsRequest
  {
    onSuccess: (data) => setTotals(data),
    onError: () => setIsCalculating(false),
  }
);
```

**Verification**:
```bash
npm run type-check | grep "useAutoCalculate.ts:74"
# Should show 0 errors
```

---

#### 1.4.4: Test Failures - BuildData Type Mismatch (3 failures)

##### useCalculations.test.tsx
**Location**: `__tests__/hooks/useCalculations.test.tsx:93`

```typescript
// Line 93 - ERROR: pools is null[], but BuildData expects tuple
const mockBuildData = {
  character: { ... },
  powersets: {
    primary: null,
    secondary: null,
    pools: null[],  // Should be [null, null, null, null]
    ancillary: null,
  },
  powers: [],
};
```

**Fix**:
```typescript
const mockBuildData: BuildData = {
  character: {
    name: "Test Hero",
    archetype: null,
    origin: null,
    alignment: null,
    level: 1,
  },
  powersets: {
    primary: null,
    secondary: null,
    pools: [null, null, null, null],  // Fixed: 4-element tuple
    ancillary: null,
  },
  powers: [],
};
```

##### usePowersets.test.tsx
**Test**: "fetches powersets when archetype ID is provided"

```typescript
it("fetches powersets when archetype ID is provided", async () => {
  const { result } = renderHook(() => usePowersetsByArchetype(1), {
    wrapper: createWrapper(),
  });

  // FAILS: Query not executing
  await waitFor(() => expect(result.current.isSuccess).toBe(true));
});
```

**Root Cause**: Mock API not set up correctly or query key mismatch.

**Fix**:
```typescript
it("fetches powersets when archetype ID is provided", async () => {
  // Mock the API response
  vi.mocked(powerApi.getPowersets).mockResolvedValue(mockPowersets);

  const { result } = renderHook(() => usePowersetsByArchetype(1), {
    wrapper: createWrapper(),
  });

  // Wait for query to succeed
  await waitFor(() => {
    expect(result.current.isSuccess).toBe(true);
  });

  expect(result.current.data).toEqual(mockPowersets);
  expect(powerApi.getPowersets).toHaveBeenCalledWith({ archetypeId: 1 });
});
```

##### builder/page.test.tsx
**Test**: "hides sidebar when collapsed in store"

```typescript
it("hides sidebar when collapsed in store", () => {
  useUIStore.setState({ sidebarCollapsed: true });

  render(<BuilderPage />);

  // FAILS: Sidebar still visible
  expect(screen.queryByRole("complementary")).not.toBeInTheDocument();
});
```

**Root Cause**: Same as BuildLayout test - sidebar exists but is visually collapsed.

**Fix**:
```typescript
it("hides sidebar when collapsed in store", () => {
  useUIStore.setState({ sidebarCollapsed: true });

  render(<BuilderPage />);

  // Sidebar exists but is collapsed (width: 0)
  const sidebar = screen.getByRole("complementary");
  expect(sidebar).toHaveStyle({ width: "0px" });
  // OR check for collapsed class
  expect(sidebar).toHaveClass("w-0");
});
```

**Verification**:
```bash
npm test -- useCalculations.test.tsx --run
npm test -- usePowersets.test.tsx --run
npm test -- page.test.tsx --run
# All should pass
```

---

## Epic 4.1: Defense & Resistance Displays

**Branch**: `claude/implement-epic-4.1-01H84VDQ3vY4fJttBr8rH4HU`
**Commit**: `37b9bb32b` - "feat: implement Epic 4.1 - Defense & Resistance Displays"
**Files Affected**:
- `components/stats/DefensePanel.tsx`
- `components/stats/StatBar.tsx`
- `components/stats/TotalsPanel.tsx`
- Tests for all above

### Issues

#### 4.1.1: DefensePanel Test - Multiple Elements Found
**Location**: `components/stats/__tests__/DefensePanel.test.tsx`

**Test**: "displays correct percentage values"

```typescript
it("displays correct percentage values", () => {
  render(<DefensePanel defense={mockDefense} defenseCap={45} />);

  // FAILS: Found multiple elements with text "45.0%"
  expect(screen.getByText("45.0%")).toBeInTheDocument();
});
```

**Root Cause**: TotalsPanel renders BOTH DefensePanel AND ResistancePanel, so labels appear twice.

**Fix Option A - Use getAllByText**:
```typescript
it("displays correct percentage values", () => {
  render(<DefensePanel defense={mockDefense} defenseCap={45} />);

  // Get all matching elements
  const percentageElements = screen.getAllByText("45.0%");
  expect(percentageElements).toHaveLength(2);  // Smashing and Lethal both at cap
});
```

**Fix Option B - Query within Panel**:
```typescript
it("displays correct percentage values", () => {
  const { container } = render(
    <DefensePanel defense={mockDefense} defenseCap={45} />
  );

  // Query within the defense section only
  const defenseSection = container.querySelector('[aria-label="Defense Stats"]');
  expect(within(defenseSection!).getByText("45.0%")).toBeInTheDocument();
});
```

**Fix Option C - Add Data Attributes**:
```typescript
// In DefensePanel.tsx - add data-testid
<div data-testid="defense-panel" className="space-y-4">
  {/* Panel content */}
</div>

// In test
it("displays correct percentage values", () => {
  render(<DefensePanel defense={mockDefense} defenseCap={45} />);

  const panel = screen.getByTestId("defense-panel");
  expect(within(panel).getByText("45.0%")).toBeInTheDocument();
});
```

**Recommended**: Option C (most explicit and maintainable)

**Verification**:
```bash
npm test -- DefensePanel.test.tsx --run
# "displays correct percentage values" should pass
```

---

#### 4.1.2: StatBar Test - Negative Values
**Location**: `components/stats/__tests__/StatBar.test.tsx`

**Test**: "handles negative values (debuffs)"

```typescript
it("handles negative values (debuffs)", () => {
  render(<StatBar label="Defense" value={-10} cap={45} colorTheme="defense" />);

  const bar = screen.getByRole("presentation");
  // FAILS: Expected width: 0%, got something else
  expect(bar).toHaveStyle({ width: "0%" });
});
```

**Root Cause**: Component may not handle negative values correctly.

**Fix in StatBar.tsx**:
```typescript
export function StatBar({ value, cap, ... }: StatBarProps) {
  // Clamp negative values to 0
  const clampedValue = Math.max(0, value);
  const percentage = Math.min((clampedValue / cap) * 100, 100);

  return (
    <div ...>
      <div
        role="presentation"
        style={{ width: `${percentage}%` }}  // Will be 0% for negative values
        className={...}
      />
    </div>
  );
}
```

**Verification**:
```bash
npm test -- StatBar.test.tsx --run
# "handles negative values" should pass
```

---

#### 4.1.3: TotalsPanel Test Failures (2 failures)

##### Test 1: "displays all defense types"
```typescript
it("displays all defense types", () => {
  useCharacterStore.setState({
    archetype: mockArchetype,
    totals: mockTotals,
    isCalculating: false,
  });

  render(<TotalsPanel />, { wrapper: createWrapper() });

  // FAILS: Found multiple elements with "Smashing"
  expect(screen.getByText("Smashing")).toBeInTheDocument();
});
```

**Root Cause**: Same as DefensePanel - labels appear in both defense AND resistance sections.

**Fix**:
```typescript
it("displays all defense types", () => {
  useCharacterStore.setState({
    archetype: mockArchetype,
    totals: mockTotals,
    isCalculating: false,
  });

  const { container } = render(<TotalsPanel />, { wrapper: createWrapper() });

  // Use getAllByText or query within specific section
  const labels = screen.getAllByText("Smashing");
  expect(labels.length).toBeGreaterThanOrEqual(1);

  // Or test for ALL defense types being present
  expect(screen.getAllByText("Smashing")).toHaveLength(2); // Defense + Resistance
  expect(screen.getAllByText("Fire")).toHaveLength(2);
  expect(screen.getByText("Melee")).toBeInTheDocument(); // Only in Defense
});
```

##### Test 2: "handles missing totals gracefully"
```typescript
it("handles missing totals gracefully", () => {
  useCharacterStore.setState({
    archetype: mockArchetype,
    totals: null,
    isCalculating: false,
  });

  const { container } = render(<TotalsPanel />, { wrapper: createWrapper() });

  // FAILS: Renders loading state instead of null
  expect(container.firstChild).toBeNull();
});
```

**Root Cause**: Component has useEffect that triggers calculation when totals is null but archetype exists.

**Fix**:
```typescript
it("handles missing totals gracefully", () => {
  useCharacterStore.setState({
    archetype: null,  // No archetype prevents auto-calculation
    totals: null,
    isCalculating: false,
  });

  const { container } = render(<TotalsPanel />, { wrapper: createWrapper() });

  // Should render nothing when no archetype
  expect(container.firstChild).toBeNull();
});
```

**Verification**:
```bash
npm test -- TotalsPanel.test.tsx --run
# Both tests should pass
```

---

## Implementation Strategy

### Phase 1: TypeScript Errors (Priority: Critical)
**Estimated Time**: 3-4 hours

**Task Breakdown**:
1. **Epic 1.2 - characterStore.ts** (90 min)
   - Remove unused type imports (3 errors) - 10 min
   - Add power undefined guards (6 errors) - 40 min
   - Fix BuildData totals type (1 error) - 20 min
   - Update characterStore tests (11 errors) - 20 min

2. **Epic 1.3 - BuildLayout** (30 min)
   - Fix isSidebarVisible usage (1 error) - 30 min

3. **Epic 1.4 - Hooks** (60 min)
   - Remove unused imports (2 errors) - 10 min
   - Fix useAutoCalculate args (1 error) - 20 min
   - Fix BuildData in tests (1 error) - 30 min

**Verification After Phase 1**:
```bash
npm run type-check
# Expected: 0 TypeScript errors
```

---

### Phase 2: Component Tests (Priority: High)
**Estimated Time**: 4-5 hours

**Task Breakdown**:
1. **Epic 1.3 - Layout Tests** (2 hours)
   - BuildLayout: TopPanel rendering (30 min)
   - BuildLayout: Sidebar collapse (30 min)
   - SidePanel: Width collapse (30 min)
   - SidePanel: aria-hidden (30 min)

2. **Epic 1.4 - Hook Tests** (1 hour)
   - usePowersets test (30 min)
   - builder/page test (30 min)

3. **Epic 4.1 - Stats Tests** (2 hours)
   - DefensePanel: Multiple elements (45 min)
   - StatBar: Negative values (30 min)
   - TotalsPanel: Multiple elements (45 min)

**Verification After Phase 2**:
```bash
npm test -- --run
# Expected: 0 test failures
```

---

### Phase 3: Final Validation (Priority: Medium)
**Estimated Time**: 1 hour

1. **Full CI/CD Pipeline Test** (30 min)
   ```bash
   just quality  # Run all checks locally
   git push      # Trigger GitHub Actions
   ```

2. **Documentation Update** (30 min)
   - Update this plan with "COMPLETED" status
   - Create checkpoint document
   - Update PROJECT_STATUS.md

---

## Success Criteria

### Must Have
- [ ] 0 TypeScript errors in `npm run type-check`
- [ ] 0 test failures in `npm test`
- [ ] All GitHub Actions checks passing (green)

### Should Have
- [ ] Code review completed by superpowers:code-reviewer agent
- [ ] Checkpoint document created
- [ ] Technical debt removed from PROJECT_STATUS.md

### Nice to Have
- [ ] ESLint warnings reduced (currently 7 warnings)
- [ ] Test coverage maintained or improved
- [ ] Performance regressions checked

---

## Rollback Plan

If issues arise during remediation:

1. **Create feature branch**: `fix/technical-debt-remediation`
2. **Commit changes in small batches** (one Epic at a time)
3. **Run tests after each Epic** to isolate failures
4. **If tests fail**:
   - Revert last commit
   - Create isolated fix in separate branch
   - Review and re-attempt

---

## Dependencies

**Before Starting**:
- [ ] Ensure main branch is stable
- [ ] No other PRs in progress that touch same files
- [ ] Full test suite passing baseline established

**External Dependencies**:
- None - all issues are internal to codebase

---

## Notes for Code Reviewer

When reviewing this remediation:

1. **Check Epic Context**: Each fix references the original Epic/commit for context
2. **Verify Tests**: All fixes should have corresponding test updates
3. **Type Safety**: Ensure fixes don't bypass type checking (avoid excessive `any` or `@ts-ignore`)
4. **Backwards Compatibility**: Changes should not break existing functionality

**Areas of Special Attention**:
- characterStore.ts power undefined handling (critical path)
- BuildData totals type (affects API contract)
- Test expectations vs actual component behavior (may reveal UX issues)

---

## References

- **Epic 1.2 PR**: #345 - State Management
- **Epic 1.3 PR**: Merged to main (find commit: `d30851a7c`)
- **Epic 1.4 PR**: Merged to main (find commit: `0f80bd207`)
- **Epic 4.1 PR**: #350 - Defense & Resistance Displays
- **Troubleshooting Summary**: `/tmp/epic-2.2-troubleshooting-summary.md`
- **Original Issue**: PR #351 GitHub Actions failures

---

**Created By**: Claude Code (systematic-debugging + write-plan workflow)
**Date**: 2025-11-18
**Estimated Total Time**: 8-12 hours
**Priority**: High (blocking clean CI/CD)
