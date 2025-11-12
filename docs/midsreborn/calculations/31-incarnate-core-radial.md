# Spec 31: Incarnate Core vs Radial Branches

**Status**: 🟡 Breadth Complete
**Priority**: Low
**Complexity**: Medium
**Last Updated**: 2025-11-10

---

## 1. Overview

### Purpose
Implements the branching choice system for Tier 3 (Rare) and Tier 4 (Very Rare) Incarnate abilities, where players choose between **Core** (focused, high magnitude) and **Radial** (broad, lower magnitude) paths. This choice fundamentally alters how the Incarnate ability functions and represents a permanent character-defining decision.

### Used By
- Incarnate slot calculation (Spec 30)
- Build comparison tools (comparing Core vs Radial choices)
- Power effect calculation (different effects based on branch)
- UI display (showing branching tree visualization)
- Character export/import (preserving branch choice)

### Complexity Rating: Medium
**Justification**: The branching logic itself is straightforward (enum-based selection), but the complexity comes from:
- Different effect magnitudes and types per branch
- Tier progression with multiple intermediate steps
- UI implications for displaying the branching tree
- Need to compare Core vs Radial for optimization

---

## 2. MidsReborn Implementation

### File Locations
- **Core/Enums.cs**: Lines 99-189 - Incarnate tier ordering enums
  - `eAlphaOrder`, `eJudgementOrder`, `eInterfaceOrder`, etc.
  - Each enum defines 9 tiers: T1 → T2 Core/Radial → T3 variants → T4 Core/Radial
- **Forms/frmIncarnate.cs**: Lines 63-246 - Incarnate UI and power parsing
  - `FillLists()`: Populates incarnate power lists by slot
  - `ParseIncarnate()`: Sorts powers by tier order

### Key Classes/Enums

#### Tier Order Pattern (All Incarnate Slots)
```csharp
// Example: eAlphaOrder (Enums.cs:99-110)
public enum eAlphaOrder
{
    Boost,                      // T1 (Common)
    Core_Boost,                 // T2 (Uncommon) - Core path
    Radial_Boost,               // T2 (Uncommon) - Radial path
    Total_Core_Revamp,          // T3 (Rare) - Core Total
    Partial_Core_Revamp,        // T3 (Rare) - Core Partial
    Total_Radial_Revamp,        // T3 (Rare) - Radial Total
    Partial_Radial_Revamp,      // T3 (Rare) - Radial Partial
    Core_Paragon,               // T4 (Very Rare) - Core endpoint
    Radial_Paragon              // T4 (Very Rare) - Radial endpoint
}

// Same pattern for all slots:
// - eJudgementOrder: Judgement → Final Judgement
// - eInterfaceOrder: Interface → Flawless Interface
// - eLoreOrder: Ally → Superior Ally
// - eDestinyOrder: Invocation → Epiphany
// - eHybridOrder: Genome → Embodiment
// - eGenesisOrder: Genesis → Flawless Genesis
```

### High-Level Algorithm

```
INCARNATE_TIER_PROGRESSION:
  Input: slot_type (Alpha, Judgement, etc.), ability_name (Musculature, etc.)

  Tier 1 (Common):
    - Single common power: "Musculature Boost"
    - No branching yet
    - Provides base effect

  Tier 2 (Uncommon):
    - Branch split occurs: "Core Boost" vs "Radial Boost"
    - Core: Maintains T1 effects, slightly enhanced
    - Radial: Maintains T1 effects, slightly enhanced
    - Names still generic (both called "Boost")

  Tier 3 (Rare):
    - Four options emerge:
      * Total Core Revamp
      * Partial Core Revamp
      * Total Radial Revamp
      * Partial Radial Revamp
    - "Total" variants: One effect at maximum strength
    - "Partial" variants: Two effects at moderate strength
    - Core vs Radial now have different effect types

  Tier 4 (Very Rare):
    - Two endpoints:
      * Core Paragon (from Core T3 path)
      * Radial Paragon (from Radial T3 path)
    - Unique ability names (e.g., "Core Paragon" vs "Radial Paragon")
    - Maximum power for chosen path
    - **Choice is permanent** - cannot switch without re-crafting

BRANCH_COMPARISON_LOGIC:
  For power in incarnate_slot:
    tier = determine_tier(power.DisplayName)
    branch = determine_branch(power.DisplayName)  // Core, Radial, or Common

    if tier >= 2:
      branch_effects[branch].add(power.Effects)

    if tier >= 3:
      specialization = determine_specialization(power.DisplayName)  // Total or Partial

  Return: {
    tier: tier,
    branch: branch,
    specialization: specialization,
    effects: power.Effects
  }
```

### Branch Determination Logic
```csharp
// From Forms/frmIncarnate.cs:166-246
// Powers are named with branch indicators:
// - "Core" in name → Core branch
// - "Radial" in name → Radial branch
// - "Total" → Single focused effect
// - "Partial" → Multiple moderate effects

private void ParseIncarnate(string setName, string abilityName)
{
    // Example: "Alpha.Musculature Core Paragon"
    // Split by spaces, extract:
    // - setName: "Alpha"
    // - abilityName: "Musculature"
    // - tier: determined by enum position
    // - branch: "Core" or "Radial" in name

    // Sort by enum order (T1 → T4)
    var sortedPowers = powers.OrderBy(p => GetTierOrder(p));
}
```

---

## 3. Game Mechanics Context

### Why Core vs Radial Exists
**Design Philosophy** (City of Heroes Issue 19-20, 2010-2011):
- **Core Path**: "Do one thing extremely well"
  - Higher magnitude bonuses
  - Narrower application
  - Focused on primary archetype strength
  - Example: Pure damage increase

- **Radial Path**: "Do multiple things well"
  - Broader effect coverage
  - Lower magnitude per effect
  - More versatile across different builds
  - Example: Damage + endurance reduction

### Historical Context
1. **Initial Release (Issue 19)**: Only Alpha slot available
   - Core/Radial split introduced at T2 (Uncommon)
   - Community initially favored Core for min/maxing

2. **Issue 20 Expansion**: Added Judgement, Interface, Lore, Destiny
   - Each slot follows same branching pattern
   - Radial gained popularity for hybrid builds

3. **T3/T4 Naming Convention**:
   - Each ability gets unique T4 names
   - Example Alpha slot endings: "Paragon", "Revamp"
   - Example Judgement endings: "Final Judgement"
   - Example Interface endings: "Flawless Interface"

### Tier Progression Details

#### Tier Structure
```
T1 (Common):          One power, no branching
    ↓
T2 (Uncommon):        Split: Core Boost vs Radial Boost
    ↓                        ↓
T3 (Rare):            Total Core    Partial Core    Total Radial    Partial Radial
                          ↓                             ↓
T4 (Very Rare):       Core Paragon                 Radial Paragon
```

#### Rarity and Crafting
- **Common (T1)**: Easiest to craft, basic effects
- **Uncommon (T2)**: Branch choice begins, moderate cost
- **Rare (T3)**: Expensive, choose Total vs Partial specialization
- **Very Rare (T4)**: Most expensive, maximum power

### Known Quirks

1. **Naming Inconsistency**:
   - Alpha uses "Revamp" and "Paragon"
   - Judgement uses "Judgement" and "Final Judgement"
   - Interface uses "Conversion" and "Flawless Interface"
   - Lore uses "Improved Ally" and "Superior Ally"
   - Different thematic names per slot, but same structure

2. **Total vs Partial Confusion**:
   - "Total" has ONE effect at max strength (counterintuitive name)
   - "Partial" has TWO effects at moderate strength
   - Players often assume "Total" means "everything"

3. **Cannot Change Branch**:
   - Once T2 is slotted, branch choice locks in
   - Must craft new Incarnate ability to switch
   - Game allows crafting both but only one can be equipped

4. **Display Name Parsing**:
   - MidsReborn parses branch from power name string
   - No explicit "branch" field in power data
   - Relies on consistent naming: "Core" or "Radial" in DisplayName

---

## 4. Python Implementation Notes

### Proposed Architecture

```python
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List

class IncarnateBranch(Enum):
    """Branch choice for T2+ Incarnate abilities."""
    COMMON = "common"           # T1 only
    CORE = "core"               # Focused, high magnitude
    RADIAL = "radial"           # Broad, lower magnitude

class IncarnateTier(Enum):
    """Incarnate ability tier/rarity."""
    T1_COMMON = 1               # Base ability
    T2_UNCOMMON = 2             # First branch split
    T3_RARE = 3                 # Total/Partial split
    T4_VERY_RARE = 4            # Maximum power

class IncarnateSpecialization(Enum):
    """T3 specialization within branch."""
    NONE = "none"               # T1/T2
    TOTAL_CORE = "total_core"   # One effect, max strength
    PARTIAL_CORE = "partial_core"   # Two effects, moderate
    TOTAL_RADIAL = "total_radial"
    PARTIAL_RADIAL = "partial_radial"

@dataclass
class IncarnateBranchInfo:
    """Information about an Incarnate ability's branch."""
    tier: IncarnateTier
    branch: IncarnateBranch
    specialization: IncarnateSpecialization
    display_name: str
    internal_name: str          # e.g., "Core_Paragon"
    slot_type: str              # Alpha, Judgement, etc.
    ability_family: str         # Musculature, Ion, etc.
```

### Key Functions

```python
def parse_incarnate_branch(power_name: str) -> IncarnateBranch:
    """
    Determine branch from power display name.

    Examples:
        "Musculature Core Paragon" → CORE
        "Musculature Radial Paragon" → RADIAL
        "Musculature Boost" → COMMON
    """
    name_lower = power_name.lower()
    if "core" in name_lower:
        return IncarnateBranch.CORE
    elif "radial" in name_lower:
        return IncarnateBranch.RADIAL
    else:
        return IncarnateBranch.COMMON

def parse_incarnate_tier(power_name: str) -> IncarnateTier:
    """
    Determine tier from power name patterns.

    Tier patterns:
        T1: "Boost", "Judgement", "Interface", etc. (no Core/Radial)
        T2: "Core Boost", "Radial Judgement", etc.
        T3: "Total Core Revamp", "Partial Radial Conversion", etc.
        T4: "Core Paragon", "Radial Final Judgement", etc.
    """
    name_lower = power_name.lower()

    if "paragon" in name_lower or "final" in name_lower or \
       "flawless" in name_lower or "superior" in name_lower or \
       "epiphany" in name_lower or "embodiment" in name_lower:
        return IncarnateTier.T4_VERY_RARE

    if "total" in name_lower or "partial" in name_lower:
        return IncarnateTier.T3_RARE

    if "core" in name_lower or "radial" in name_lower:
        return IncarnateTier.T2_UNCOMMON

    return IncarnateTier.T1_COMMON

def parse_incarnate_specialization(power_name: str) -> IncarnateSpecialization:
    """
    Determine T3 specialization (Total vs Partial).

    Total = One effect at maximum strength
    Partial = Multiple effects at moderate strength
    """
    name_lower = power_name.lower()

    if "total" in name_lower and "core" in name_lower:
        return IncarnateSpecialization.TOTAL_CORE
    elif "partial" in name_lower and "core" in name_lower:
        return IncarnateSpecialization.PARTIAL_CORE
    elif "total" in name_lower and "radial" in name_lower:
        return IncarnateSpecialization.TOTAL_RADIAL
    elif "partial" in name_lower and "radial" in name_lower:
        return IncarnateSpecialization.PARTIAL_RADIAL
    else:
        return IncarnateSpecialization.NONE

def get_incarnate_branch_info(power: Power) -> IncarnateBranchInfo:
    """
    Extract complete branch information from an Incarnate power.

    Returns:
        IncarnateBranchInfo with tier, branch, specialization details
    """
    return IncarnateBranchInfo(
        tier=parse_incarnate_tier(power.display_name),
        branch=parse_incarnate_branch(power.display_name),
        specialization=parse_incarnate_specialization(power.display_name),
        display_name=power.display_name,
        internal_name=power.name,
        slot_type=power.set_name,       # Alpha, Judgement, etc.
        ability_family=extract_ability_family(power.display_name)
    )

def extract_ability_family(display_name: str) -> str:
    """
    Extract ability family name (e.g., "Musculature" from "Musculature Core Paragon").

    Assumes format: "{Family} [{Branch}] {Tier}"
    """
    # Split and take first token before "Core" or "Radial" or tier name
    tokens = display_name.split()
    if tokens:
        return tokens[0]
    return ""

def compare_core_vs_radial(
    core_power: Power,
    radial_power: Power
) -> dict:
    """
    Compare Core and Radial versions of same-tier Incarnate ability.

    Returns:
        {
            "core": {
                "effects": [...],
                "magnitude_total": float,
                "effect_count": int
            },
            "radial": {
                "effects": [...],
                "magnitude_total": float,
                "effect_count": int
            },
            "recommendation": str  # Based on build optimization
        }
    """
    # Defer detailed comparison logic to Milestone 3
    # Key: Core usually has higher single-effect magnitude
    # Radial usually has more diverse effects
    pass
```

### Example Incarnate Branch Structures

```python
# Example 1: Alpha - Musculature
MUSCULATURE_PROGRESSION = {
    "T1": {
        "name": "Musculature Boost",
        "branch": IncarnateBranch.COMMON,
        "effects": [
            {"type": "Damage", "magnitude": 0.33}  # +33% damage
        ]
    },
    "T2_CORE": {
        "name": "Musculature Core Boost",
        "branch": IncarnateBranch.CORE,
        "effects": [
            {"type": "Damage", "magnitude": 0.45}  # +45% damage
        ]
    },
    "T2_RADIAL": {
        "name": "Musculature Radial Boost",
        "branch": IncarnateBranch.RADIAL,
        "effects": [
            {"type": "Damage", "magnitude": 0.33},      # +33% damage
            {"type": "EnduranceDiscount", "magnitude": 0.33}  # +33% end reduction
        ]
    },
    "T4_CORE": {
        "name": "Musculature Core Paragon",
        "branch": IncarnateBranch.CORE,
        "specialization": IncarnateSpecialization.TOTAL_CORE,
        "effects": [
            {"type": "Damage", "magnitude": 0.60}  # +60% damage (maximum)
        ]
    },
    "T4_RADIAL": {
        "name": "Musculature Radial Paragon",
        "branch": IncarnateBranch.RADIAL,
        "specialization": IncarnateSpecialization.TOTAL_RADIAL,
        "effects": [
            {"type": "Damage", "magnitude": 0.45},          # +45% damage
            {"type": "EnduranceDiscount", "magnitude": 0.45}  # +45% end reduction
        ]
    }
}

# Example 2: Judgement - Ion
ION_PROGRESSION = {
    "T1": {
        "name": "Ion Judgement",
        "branch": IncarnateBranch.COMMON,
        "effects": [
            {"type": "EnergyDamage", "magnitude": 300.0, "radius": 20}
        ]
    },
    "T4_CORE": {
        "name": "Ion Core Final Judgement",
        "branch": IncarnateBranch.CORE,
        "effects": [
            # Higher damage, smaller radius
            {"type": "EnergyDamage", "magnitude": 500.0, "radius": 15}
        ]
    },
    "T4_RADIAL": {
        "name": "Ion Radial Final Judgement",
        "branch": IncarnateBranch.RADIAL,
        "effects": [
            # Lower damage, larger radius, more chains
            {"type": "EnergyDamage", "magnitude": 400.0, "radius": 25},
            {"type": "ChainCount", "magnitude": 10}  # More chain targets
        ]
    }
}

# Example 3: Interface - Degenerative
DEGENERATIVE_PROGRESSION = {
    "T4_CORE": {
        "name": "Degenerative Core Flawless Interface",
        "branch": IncarnateBranch.CORE,
        "effects": [
            # High toxic DoT proc
            {"type": "ToxicDamageProc", "magnitude": 50.0, "chance": 0.75}
        ]
    },
    "T4_RADIAL": {
        "name": "Degenerative Radial Flawless Interface",
        "branch": IncarnateBranch.RADIAL,
        "effects": [
            # Moderate toxic DoT + heal debuff
            {"type": "ToxicDamageProc", "magnitude": 35.0, "chance": 0.75},
            {"type": "HealDebuffProc", "magnitude": -0.30, "chance": 0.75}
        ]
    }
}
```

### Integration Points

1. **Power Data Model** (Spec 02):
   - Add `incarnate_branch_info` field to Power dataclass
   - Parse branch info when loading Incarnate powers

2. **Effect Calculation** (Spec 06):
   - Branch affects effect magnitudes
   - Core: Higher single-effect magnitude
   - Radial: Multiple effects, lower individual magnitudes

3. **Incarnate Slot System** (Spec 30):
   - Track selected branch per character
   - Validate branch choices (cannot mix Core T3 with Radial T4)
   - Display branching tree in UI

4. **Build Optimization**:
   - Compare Core vs Radial for damage/survivability
   - Recommend branch based on archetype and power selections
   - Calculate opportunity cost of branch choice

### Database Schema Additions

```sql
-- Add to powers table
ALTER TABLE powers ADD COLUMN incarnate_branch VARCHAR(10);  -- 'common', 'core', 'radial'
ALTER TABLE powers ADD COLUMN incarnate_tier INTEGER;        -- 1, 2, 3, 4
ALTER TABLE powers ADD COLUMN incarnate_specialization VARCHAR(20);  -- 'total_core', etc.

-- Track character Incarnate choices
CREATE TABLE character_incarnate_branches (
    character_id INTEGER REFERENCES characters(id),
    slot_type VARCHAR(20),           -- 'Alpha', 'Judgement', etc.
    ability_family VARCHAR(50),      -- 'Musculature', 'Ion', etc.
    branch VARCHAR(10),              -- 'core', 'radial'
    tier INTEGER,                    -- Current tier (1-4)
    power_id INTEGER REFERENCES powers(id),
    PRIMARY KEY (character_id, slot_type)
);
```

---

## Appendix: Complete Branch Enum Reference

### All Incarnate Slot Tier Orders

```python
# Tier progression for all Incarnate slots (from Enums.cs:99-189)

ALPHA_TIERS = [
    "Boost",                    # T1
    "Core_Boost",               # T2 Core
    "Radial_Boost",             # T2 Radial
    "Total_Core_Revamp",        # T3
    "Partial_Core_Revamp",      # T3
    "Total_Radial_Revamp",      # T3
    "Partial_Radial_Revamp",    # T3
    "Core_Paragon",             # T4 Core
    "Radial_Paragon"            # T4 Radial
]

JUDGEMENT_TIERS = [
    "Judgement",
    "Core_Judgement",
    "Radial_Judgement",
    "Total_Core_Judgement",
    "Partial_Core_Judgement",
    "Total_Radial_Judgement",
    "Partial_Radial_Judgement",
    "Core_Final_Judgement",
    "Radial_Final_Judgement"
]

INTERFACE_TIERS = [
    "Interface",
    "Core_Interface",
    "Radial_Interface",
    "Total_Core_Conversion",
    "Partial_Core_Conversion",
    "Total_Radial_Conversion",
    "Partial_Radial_Conversion",
    "Core_Flawless_Interface",
    "Radial_Flawless_Interface"
]

LORE_TIERS = [
    "Ally",
    "Core_Ally",
    "Radial_Ally",
    "Total_Core_Improved_Ally",
    "Partial_Core_Improved_Ally",
    "Total_Radial_Improved_Ally",
    "Partial_Radial_Improved_Ally",
    "Core_Superior_Ally",
    "Radial_Superior_Ally"
]

DESTINY_TIERS = [
    "Invocation",
    "Core_Invocation",
    "Radial_Invocation",
    "Total_Core_Invocation",
    "Partial_Core_Invocation",
    "Total_Radial_Invocation",
    "Partial_Radial_Invocation",
    "Core_Epiphany",
    "Radial_Epiphany"
]

HYBRID_TIERS = [
    "Genome",
    "Core_Genome",
    "Radial_Genome",
    "Total_Core_Graft",
    "Partial_Core_Graft",
    "Total_Radial_Graft",
    "Partial_Radial_Graft",
    "Core_Embodiment",
    "Radial_Embodiment"
]

GENESIS_TIERS = [
    "Genesis",
    "Core_Genesis",
    "Radial_Genesis",
    "Total_Core_Genesis",
    "Partial_Core_Genesis",
    "Total_Radial_Genesis",
    "Partial_Radial_Genesis",
    "Core_Flawless_Genesis",
    "Radial_Flawless_Genesis"
]
```

---

## References
- MidsReborn: `Core/Enums.cs` (Lines 99-189)
- MidsReborn: `Forms/frmIncarnate.cs` (Incarnate UI implementation)
- City of Heroes Wiki: Incarnate System (branching design philosophy)
- Issue 19/20 Patch Notes: Incarnate ability introduction

---

**Next Steps** (Milestone 3 - Depth):
1. Implement exact effect magnitude differences between Core/Radial
2. Create comparison tool for Core vs Radial optimization
3. Build branching tree visualization UI
4. Validate branch progression (cannot skip tiers)
5. Add unit tests for branch parsing logic
