# MidsReborn Calculation Engine - Navigation Map

**Purpose**: Quick reference for finding any calculation in the MidsReborn C# codebase
**Last Updated**: 2025-11-10
**MidsReborn Path**: `/Users/w/code/mids-hero-web/external/dev/MidsReborn/MidsReborn`

---

## Quick Start

**New to the codebase?** Start here:
1. Read this navigation map (you are here)
2. Read `01-architecture-overview.md` for system-wide understanding
3. Check `02-calculation-index.md` to find specific calculations
4. Dive into individual calculation specs in `calculations/` directory

**Looking for a specific calculation?** Use the [Quick Lookup Table](#quick-lookup-table) below.

---

## Directory Structure

```
MidsReborn/MidsReborn/
├── Core/                           # All calculation logic lives here
│   ├── Build.cs                    # 104 KB - Master build orchestrator
│   ├── clsToonX.cs                 # 165 KB - Character/build state (root level)
│   ├── PowerEntry.cs               # 17 KB  - Individual power calculations
│   ├── Enhancement.cs              # 16 KB  - Enhancement logic & ED curves
│   ├── EnhancementSet.cs           # 17 KB  - Set bonuses
│   ├── I9Slot.cs                   # 26 KB  - Slotting mechanics
│   ├── GroupedFx.cs                # 105 KB - Effect grouping & aggregation
│   ├── Stats.cs                    # 24 KB  - Build totals aggregation
│   ├── DatabaseAPI.cs              # 136 KB - Data access layer
│   ├── Powerset.cs                 # Powerset data structure
│   ├── PowersetGroup.cs            # Powerset grouping
│   ├── Enums.cs                    # All enumerations
│   ├── Base/
│   │   ├── Data_Classes/
│   │   │   ├── Archetype.cs        # Archetype modifiers & caps
│   │   │   ├── Power.cs            # Power data structure
│   │   │   ├── Effect.cs           # IEffect interface & implementations
│   │   │   ├── Character.cs        # Character base data
│   │   │   ├── Database.cs         # Database wrapper
│   │   │   └── Origin.cs           # Origin data
│   │   ├── Master_Classes/
│   │   │   ├── MidsContext.cs      # Global application context
│   │   │   └── Utilities.cs        # Helper/utility functions
│   │   ├── Extensions/             # C# extension methods
│   │   └── Display/                # UI-related (not calc-relevant)
│   ├── BuildFile/                  # Build save/load (not calc-relevant)
│   └── Utils/                      # Utility classes
├── Forms/                          # UI code (ignore for calculations)
└── Data/                           # JSON data files (we use City of Data instead)
```

---

## Key Files by Function

### Build Orchestration

| File | Size | Purpose | Key Classes/Methods |
|------|------|---------|-------------------|
| **Core/Build.cs** | 104 KB | Master build orchestrator - coordinates all calculations | `Build` class with methods for recalculating powers, totals, set bonuses |
| **clsToonX.cs** | 165 KB | Character/build state management - triggers recalculation when build changes | `clsToonX` class - maintains current build state |
| **Core/Stats.cs** | 24 KB | Aggregates individual power calculations into build-wide totals | `Stats` class - methods for summing defense, resistance, damage, etc. |

### Power Calculations

| File | Size | Purpose | Key Classes/Methods |
|------|------|---------|---------------------|
| **Core/PowerEntry.cs** | 17 KB | Individual power stat calculation with enhancements applied | `PowerEntry` class - calculates final power stats |
| **Core/Base/Data_Classes/Power.cs** | ? | Power data structure and base calculations | `Power` class - stores power data from database |
| **Core/Base/Data_Classes/Effect.cs** | ? | Effect system foundation (IEffect interface) | `IEffect`, effect type implementations |
| **Core/GroupedFx.cs** | 105 KB | Groups and aggregates effects from multiple sources | `GroupedFx` class - effect combination logic |

### Enhancement System

| File | Size | Purpose | Key Classes/Methods |
|------|------|---------|---------------------|
| **Core/Enhancement.cs** | 16 KB | Enhancement calculations including ED (Enhancement Diminishing Returns) | `Enhancement` class - `ApplyED()`, schedule curves |
| **Core/EnhancementSet.cs** | 17 KB | Set bonus mechanics and Rule of 5 suppression | `EnhancementSet` class - set bonus activation logic |
| **Core/I9Slot.cs** | 26 KB | Slotting mechanics - how enhancements fit into power slots | `I9Slot` class - slot management |

### Archetype System

| File | Size | Purpose | Key Classes/Methods |
|------|------|---------|---------------------|
| **Core/Base/Data_Classes/Archetype.cs** | ? | Archetype modifiers, caps, and inherent powers | `Archetype` class - AT-specific scaling |

### Data Access

| File | Size | Purpose | Key Classes/Methods |
|------|------|---------|---------------------|
| **Core/DatabaseAPI.cs** | 136 KB | Database access layer for powers, archetypes, etc. | `DatabaseAPI` class - data loading methods |
| **Core/Base/Data_Classes/Database.cs** | ? | Database wrapper and initialization | `Database` class |

### Utilities

| File | Size | Purpose | Key Classes/Methods |
|------|------|---------|---------------------|
| **Core/Enums.cs** | ? | All enumerations used throughout codebase | Effect types, damage types, AT enums, etc. |
| **Core/Base/Master_Classes/Utilities.cs** | ? | General utility/helper functions | Static helper methods |

---

## Quick Lookup Table

**Use this table to find calculations in <2 minutes**

### Power System Calculations

| What You're Looking For | Primary File(s) | Secondary Files | Notes |
|------------------------|----------------|-----------------|-------|
| **Power damage calculation** | `PowerEntry.cs`, `Build.cs` | `Archetype.cs`, `Enhancement.cs` | AT scaling + enhancements |
| **Power effect system (buffs/debuffs)** | `Effect.cs`, `GroupedFx.cs` | `PowerEntry.cs` | IEffect interface |
| **Power accuracy/tohit** | `PowerEntry.cs`, `Build.cs` | `Enhancement.cs` | Accuracy vs ToHit |
| **Power recharge time** | `PowerEntry.cs`, `Build.cs` | `Enhancement.cs`, `Stats.cs` | Local + global recharge |
| **Power endurance cost** | `PowerEntry.cs`, `Build.cs` | `Enhancement.cs` | Base cost + modifiers |
| **Power range/radius/arc** | `PowerEntry.cs`, `Power.cs` | `Enhancement.cs` | Spatial attributes |
| **Control effects (mez)** | `Effect.cs`, `PowerEntry.cs` | `GroupedFx.cs` | Hold, stun, sleep, etc. |
| **Healing/absorption** | `Effect.cs`, `PowerEntry.cs` | `GroupedFx.cs` | HP restoration |

### Enhancement System Calculations

| What You're Looking For | Primary File(s) | Secondary Files | Notes |
|------------------------|----------------|-----------------|-------|
| **Enhancement Diminishing Returns (ED)** | `Enhancement.cs` | - | Schedule A/B/C/D curves - CRITICAL |
| **Enhancement slotting** | `I9Slot.cs`, `PowerEntry.cs` | `Enhancement.cs` | How enhancements combine |
| **Set bonuses** | `EnhancementSet.cs`, `Build.cs` | `Stats.cs` | Set activation + Rule of 5 |
| **IO procs (damage/heal/etc)** | `Enhancement.cs`, `PowerEntry.cs` | `Effect.cs` | Proc chance formulas |
| **Special IOs (LotG, etc)** | `Enhancement.cs`, `EnhancementSet.cs` | - | Global recharge, uniques |
| **Attuned IOs** | `Enhancement.cs` | - | Level scaling |
| **Enhancement boosters (+5)** | `Enhancement.cs` | - | Catalyst mechanics |

### Archetype System Calculations

| What You're Looking For | Primary File(s) | Secondary Files | Notes |
|------------------------|----------------|-----------------|-------|
| **Archetype modifiers** | `Archetype.cs`, `Build.cs` | `PowerEntry.cs` | Damage/buff scale by AT |
| **Archetype caps** | `Archetype.cs`, `Stats.cs` | `Build.cs` | Defense/resistance/damage caps |
| **Inherent powers** | `Archetype.cs`, `Power.cs` | `PowerEntry.cs` | Fury, Defiance, etc. |

### Build Aggregation Calculations

| What You're Looking For | Primary File(s) | Secondary Files | Notes |
|------------------------|----------------|-----------------|-------|
| **Build defense totals** | `Stats.cs`, `Build.cs` | `GroupedFx.cs` | Typed + positional |
| **Build resistance totals** | `Stats.cs`, `Build.cs` | `GroupedFx.cs` | By damage type |
| **Build recharge (global)** | `Stats.cs`, `Build.cs` | `EnhancementSet.cs` | Set bonuses + IOs |
| **Build damage bonuses** | `Stats.cs`, `Build.cs` | `EnhancementSet.cs` | Global + type-specific |
| **Build accuracy/tohit** | `Stats.cs`, `Build.cs` | `PowerEntry.cs` | Global bonuses |
| **HP, endurance, recovery** | `Stats.cs`, `Build.cs` | `GroupedFx.cs`, `Archetype.cs` | Base + bonuses |

### Special Systems Calculations

| What You're Looking For | Primary File(s) | Secondary Files | Notes |
|------------------------|----------------|-----------------|-------|
| **Pet calculations** | `SummonedEntity.cs`, `PowerEntry.cs` | `Archetype.cs` | Pet scaling |
| **Pseudopet mechanics** | `Power.cs`, `Effect.cs` | `GroupedFx.cs` | Invisible summons |
| **Incarnate abilities** | Search for "Incarnate" | Various | Alpha, Judgement, etc. |
| **Level scaling** | `PowerEntry.cs`, `Power.cs` | `Archetype.cs` | Level 1-50 scaling |
| **Exemplar mechanics** | `Build.cs`, `PowerEntry.cs` | `Enhancement.cs` | Level reduction effects |

---

## Search Strategies

### Using ripgrep (rg)

```bash
# From MidsReborn/MidsReborn directory

# Find where damage is calculated
rg "damage.*scale" Core/ -i

# Find Enhancement Diminishing Returns
rg "ApplyED|Schedule[ABC]" Core/ -i

# Find set bonus logic
rg "set.*bonus|Rule.*Five" Core/ -i

# Find archetype modifiers
rg "archetype.*modifier|at.*scale" Core/ -i

# Find effect grouping
rg "GroupedFx|IEffect" Core/ -i

# Find a specific power by name (e.g., "Hasten")
rg "Hasten" Core/ -i

# Find proc calculations
rg "proc.*chance|PPM" Core/ -i
```

### Using Visual Studio Code

1. Open `/Users/w/code/mids-hero-web/external/dev/MidsReborn/MidsReborn` in VS Code
2. Use **Ctrl+P** (Cmd+P on Mac) to quickly open files by name
3. Use **Ctrl+Shift+F** (Cmd+Shift+F) for full-text search across codebase
4. Use **F12** (Go to Definition) to trace method calls

### Reading Strategy for Complex Files

For large files like `Build.cs` (104 KB) or `GroupedFx.cs` (105 KB):

1. **Start with class-level documentation** - Read class summary comments
2. **Find public methods** - These are the entry points
3. **Trace a specific calculation** - Use F12 to follow method calls
4. **Look for key sections** - Search for comments like "// Enhancement calculation"
5. **Don't read linearly** - Jump between related methods as needed

---

## Calculation Flow Entry Points

### How Calculations Are Triggered

```
User Action (e.g., slot an enhancement)
    ↓
clsToonX.cs - Build state updated
    ↓
Build.cs - Recalculation triggered
    ↓
PowerEntry.cs - Individual power recalculated
    ↓
Enhancement.cs - ED applied to enhancements
    ↓
GroupedFx.cs - Effects grouped and combined
    ↓
Stats.cs - Build totals aggregated
    ↓
UI Updated with new values
```

**Key Entry Points to Start Investigation:**
- **Build.cs** - `Recalculate()`, `CalculatePower()`, `CalculateSetBonuses()`
- **PowerEntry.cs** - `Calculate()`, `GetEnhancedEffect()`
- **Stats.cs** - `UpdateDefense()`, `UpdateResistance()`, `UpdateDamage()`
- **Enhancement.cs** - `ApplyED()`, `GetSchedule()`

---

## Common Calculation Patterns

### Pattern 1: Power Stat Calculation
```
Base Value (from Power.cs data)
    → Apply Archetype Modifier (from Archetype.cs)
    → Apply Enhancements with ED (from Enhancement.cs)
    → Apply Set Bonuses (from EnhancementSet.cs)
    → Apply Global Buffs (from Stats.cs)
    → Final Value
```

### Pattern 2: Build Total Aggregation
```
For each power in build:
    Calculate power's contribution (PowerEntry.cs)
    Add to running total (Stats.cs)
Apply archetype caps (Archetype.cs)
Return capped total
```

### Pattern 3: Effect Combination
```
Collect all effects from all sources (powers, sets, globals)
Group by effect type (GroupedFx.cs)
Apply stacking rules (additive vs multiplicative)
Return combined effect value
```

---

## Cross-Reference with Mids Hero Web

### Our Python Architecture

```
backend/app/
├── models.py                    # SQLAlchemy models (Power, Powerset, Archetype, etc.)
├── calculations/                # Future Python calculation engine (to be implemented)
│   ├── power_damage.py         # PowerEntry.cs → power_damage.py
│   ├── enhancement_schedules.py # Enhancement.cs → enhancement_schedules.py
│   ├── set_bonuses.py          # EnhancementSet.cs → set_bonuses.py
│   ├── build_totals.py         # Stats.cs → build_totals.py
│   └── effects.py              # Effect.cs, GroupedFx.cs → effects.py
```

### Mapping MidsReborn → Mids Hero Web

| MidsReborn File | Future Python Module | Status |
|----------------|---------------------|--------|
| `Build.cs` | `backend/app/calculations/build_orchestrator.py` | Not implemented |
| `PowerEntry.cs` | `backend/app/calculations/power_calculations.py` | Not implemented |
| `Enhancement.cs` | `backend/app/calculations/enhancement_schedules.py` | Not implemented |
| `EnhancementSet.cs` | `backend/app/calculations/set_bonuses.py` | Not implemented |
| `Stats.cs` | `backend/app/calculations/build_totals.py` | Not implemented |
| `GroupedFx.cs` | `backend/app/calculations/effects.py` | Not implemented |
| `Archetype.cs` | `backend/app/models.py:Archetype` | Model exists, calculations not implemented |
| `Power.cs` | `backend/app/models.py:Power` | Model exists, calculations not implemented |

**Note**: Models exist in database but calculation logic is completely missing. That's what this documentation project will enable us to implement.

---

## Tips for Effective Navigation

1. **Use the Quick Lookup Table first** - Don't browse files randomly
2. **Start with high-level overview** - Read `01-architecture-overview.md` before diving into code
3. **Follow the data flow** - Trace from Build.cs downward
4. **Check calculation specs** - Individual specs in `calculations/` directory have detailed guides
5. **Use ripgrep liberally** - Searching is faster than reading
6. **Don't get lost in UI code** - Focus on `Core/` directory only
7. **Line numbers may shift** - Use method/class names as primary references
8. **C# vs Python gotchas** - Watch for 0-based vs 1-based indexing, integer division, etc.

---

## Next Steps

After using this navigation map:

1. **Read Architecture Overview**: `01-architecture-overview.md` explains how all these files fit together
2. **Check Calculation Index**: `02-calculation-index.md` lists all 43 calculation specifications
3. **Dive into Specific Calculations**: Browse `calculations/` directory for detailed specs
4. **Start Implementation**: Use specs to implement Python calculations in Mids Hero Web

---

## Maintenance Notes

**When to Update This Document**:
- MidsReborn codebase structure changes significantly
- New major calculation systems are discovered
- File paths or names change
- Key classes are refactored

**Current Version**: Based on MidsReborn codebase as of 2025-07-26 (file modification dates)

**Verification**: To verify file paths are still correct:
```bash
cd /Users/w/code/mids-hero-web/external/dev/MidsReborn/MidsReborn
ls -lh Core/{Build.cs,PowerEntry.cs,Enhancement.cs,EnhancementSet.cs,I9Slot.cs,GroupedFx.cs,Stats.cs,DatabaseAPI.cs}
ls -lh clsToonX.cs
```

---

**Document Status**: ✅ Complete - Foundation document ready for use
**Related Documents**: `01-architecture-overview.md`, `02-calculation-index.md`
