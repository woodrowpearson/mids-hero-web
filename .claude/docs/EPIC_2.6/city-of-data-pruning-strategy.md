# City of Data Pruning Strategy

> **Generated:** 2025-11-01
> **Purpose:** Actionable filtering plan for creating player-only dataset

## Executive Summary

**Source:** `raw_data_homecoming-20250617_6916` (43,224 total files)
**Target:** `filtered_data/` (estimated 1,000-2,000 files, ~95% reduction)
**Approach:** 3-layer filtering with automated scripts and manual review checkpoints

## Filter Rules Summary

### Layer 1: Explicit Categories (4 directories)

Keep entire directories with specific names:

**Pattern Matching:**
```python
category_name in ["pool", "epic", "inherent"] or
"incarnate" in category_name.lower()
```

**Categories:**
1. `powers/pool/` - 15 powersets (Fighting, Speed, Leadership, etc.)
2. `powers/epic/` - 81 powersets (Epic/Patron pools)
3. `powers/inherent/` - 2 powersets (Inherent abilities)
4. `powers/incarnate*/` - 3 directories (Incarnate system)

**Implementation:** Directory-level copy

### Layer 2: Archetype-Linked (30 categories)

Keep categories referenced by player archetypes:

**Data Source:** `.claude/docs/archetype-category-mapping.json`

**Categories List:**
```
Arachnos_Soldiers, Blaster_RANGED, Blaster_SUPPORT,
Brute_DEFENSE, Brute_Melee, Controller_BUFF, Controller_CONTROL,
Corruptor_BUFF, Corruptor_Ranged, Defender_BUFF, Defender_RANGED,
Dominator_Assault, Dominator_CONTROL, Mastermind_Buff, Mastermind_Summon,
Peacebringer_Defensive, Peacebringer_Offensive, Scrapper_DEFENSE, Scrapper_MELEE,
Sentinel_Defense, Sentinel_Ranged, Stalker_Defense, Stalker_Melee,
Tanker_DEFENSE, Tanker_MELEE, Teamwork, Training_Gadgets,
Warshade_Defensive, Warshade_Offensive, Widow_Training
```

**Implementation:**
```python
def is_archetype_linked(category_name: str, mapping: Set[str]) -> bool:
    return category_name in mapping
```

### Layer 3: Special Directories (2 directories)

Always keep entire directories:

1. **boost_sets/** (227 sets)
   - Reason: ALL enhancements are player powers
   - Action: Copy entire directory

2. **archetypes/** (66 files, 15 player archetypes)
   - Reason: Defines player archetypes
   - Action: Copy all files (including NPC archetypes for completeness)

**Implementation:** Directory-level copy

### Exclusion Patterns

Exclude categories matching known NPC patterns:

**Enemy Groups (partial list):**
```python
ENEMY_GROUPS = [
    "5thcolumn", "animusarcana", "apparitions", "banishedpantheon",
    "carnival", "circleofthorns", "clockwork", "council",
    "devouring_earth", "freakshow", "malta", "nemesis",
    "outcasts", "rikti", "skulls", "trolls", "vahzilok",
    # ... many more
]
```

**Base Powers:**
```python
category_name.startswith("base_")  # base_aux, base_defenses, etc.
```

**Implementation:** String pattern matching (takes precedence over Layer 1/2)

## Directory Processing Plan

### Phase 1: Layer 3 Special Directories (Parallel)

**Agent 1: Archetypes Processor**
```bash
Input: external/city_of_data/.../archetypes/
Output: filtered_data/archetypes/
Action: Copy all files
Reason: Archetype definitions needed for Layer 2
```

**Agent 2: Boost Sets Processor**
```bash
Input: external/city_of_data/.../boost_sets/
Output: filtered_data/boost_sets/
Action: Copy all files
Reason: All enhancements player-relevant
```

**Dependencies:** None (run in parallel)

### Phase 2: Layer 1 + Layer 2 Powers Filtering (Sequential)

**Agent 3: Powers Processor**
```bash
Input: external/city_of_data/.../powers/
Output: filtered_data/powers/
Dependencies: Archetype mapping from Agent 1
Action: Apply 3-layer filtering logic
```

**Filtering Logic:**
```python
def should_keep_category(category_name: str, archetype_categories: Set[str]) -> bool:
    # Check exclusions first
    if matches_exclusion(category_name):
        return False

    # Layer 1: Explicit categories
    if category_name.lower() in ["pool", "epic", "inherent"]:
        return True
    if "incarnate" in category_name.lower():
        return True

    # Layer 2: Archetype-linked
    if category_name in archetype_categories:
        return True

    # Unknown - flag for review
    return False

def matches_exclusion(category_name: str) -> bool:
    # Base powers
    if category_name.startswith("base_"):
        return True

    # Enemy groups (check against known list)
    if category_name.lower() in ENEMY_GROUPS:
        return True

    return False
```

### Phase 3: Metadata Directories (Selective)

**Agent 4: Metadata Processor**

**Review and decide:**

1. **tables/** (65 files)
   - Decision: KEEP - May contain power lookup tables
   - Action: Copy all

2. **tags/** (316 files)
   - Decision: KEEP - May be referenced by player powers
   - Action: Copy all

3. **exclusion_groups/** (25 files)
   - Decision: KEEP - Defines mutual exclusion for player powers
   - Action: Copy all

4. **recharge_groups/** (4 files)
   - Decision: KEEP - Needed for power mechanics
   - Action: Copy all

5. **entities/** (8,707 files)
   - Decision: EXCLUDE - NPC-heavy, not needed
   - Action: Skip

6. **entity_tags/** (28 files)
   - Decision: EXCLUDE - Linked to entity system
   - Action: Skip

## Output Structure

```
filtered_data/
├── archetypes/                # 66 files (Layer 3)
├── boost_sets/                # 227 files (Layer 3)
├── powers/                    # Filtered categories
│   ├── pool/                 # Layer 1 explicit
│   ├── epic/                 # Layer 1 explicit
│   ├── inherent/             # Layer 1 explicit
│   ├── incarnate/            # Layer 1 explicit
│   ├── incarnate_alphastrike/  # Layer 1 explicit
│   ├── incarnate_i20/        # Layer 1 explicit
│   ├── Blaster_RANGED/       # Layer 2 archetype-linked
│   ├── Blaster_SUPPORT/      # Layer 2 archetype-linked
│   ├── Controller_BUFF/      # Layer 2 archetype-linked
│   └── [26 more archetype categories...]
├── tables/                    # Metadata (selective)
├── tags/                      # Metadata (selective)
├── exclusion_groups/          # Metadata (selective)
├── recharge_groups/           # Metadata (selective)
├── manifest.json              # Tracking manifest
├── archetypes_manifest.json   # Agent 1 output
├── boost_sets_manifest.json   # Agent 2 output
├── powers_manifest.json       # Agent 3 output
└── metadata_manifest.json     # Agent 4 output
```

## Agent Coordination

### Sequential: Archetype Mapping First
```
[Agent 1: Archetypes] → Generates archetype-category-mapping.json
                      ↓
[Agent 2: Boost Sets] (parallel)
[Agent 3: Powers] (uses mapping)
[Agent 4: Metadata] (parallel)
```

### Parallel After Mapping
```
Agent 2, 3, 4 can run simultaneously after Agent 1 completes
```

### Synthesis: Validation Agent
```
[Agents 1-4 complete] → [Agent 5: Validation]
                       ↓
                   manifest.json created
                   completeness checks
                   schema validation
```

## Manifest Format Specification

### Per-Agent Fragment Format

Each filtering agent produces a manifest fragment:

```json
{
  "directory": "powers",
  "total_files": 1234,
  "kept_categories": [
    {"category": "pool", "reason": "layer_1_explicit", "layer": 1},
    {"category": "Blaster_RANGED", "reason": "layer_2_archetype_linked", "layer": 2}
  ],
  "excluded_categories": [
    {"category": "5thcolumn", "reason": "exclusion_pattern_enemy_group"}
  ],
  "entries": [
    {
      "source": "powers/pool/fighting/index.json",
      "reason": "layer_1_explicit:pool",
      "layer": 1,
      "copied_to": "filtered_data/powers/pool/fighting/index.json",
      "size_bytes": 1234
    }
  ]
}
```

### Final Manifest Format

Synthesis agent combines all fragments:

```json
{
  "metadata": {
    "source_dir": "raw_data_homecoming-20250617_6916",
    "filtered_date": "2025-11-01T12:00:00Z",
    "total_source_files": 43224,
    "kept_files": 1500,
    "excluded_files": 41724,
    "strategy_version": "v1.0",
    "epic": "2.5",
    "github_issue": "#300"
  },
  "filter_rules": {
    "layer_1_patterns": ["pool", "epic", "inherent", "incarnate"],
    "layer_2_categories": [...],  // from archetype mapping
    "layer_3_directories": ["boost_sets", "archetypes"],
    "exclusion_patterns": ["base_*", "5thcolumn", ...]
  },
  "kept_files": [...],  // all files kept with reasons
  "excluded_files": [...],  // all files excluded with reasons
  "statistics": {
    "by_layer": {
      "1": 500,
      "2": 800,
      "3": 200
    },
    "by_directory": {
      "powers": 1000,
      "boost_sets": 227,
      "archetypes": 66,
      "tables": 65,
      "tags": 316
    }
  },
  "validation": {
    "archetypes": {
      "all_present": true,
      "found": ["blaster", "controller", ...]
    },
    "power_categories": {
      "has_pool": true,
      "has_epic": true,
      "has_inherent": true,
      "has_incarnate": true
    },
    "boost_sets": {
      "present": true,
      "total_files": 227
    },
    "schema": {
      "files_checked": 150,
      "errors": [],
      "valid": true
    }
  }
}
```

## Implementation Scripts

### Script Locations
```
scripts/
├── map_archetype_categories.py  # Phase 1: Generate mapping
├── filter_archetypes.py        # Agent 1: Copy archetypes
├── filter_boost_sets.py        # Agent 2: Copy boost sets
├── filter_powers.py            # Agent 3: Filter powers
├── filter_metadata.py          # Agent 4: Filter metadata
└── validate_filtered_data.py  # Agent 5: Validate and create manifest
```

### Execution Order
```bash
# Phase 1: Generate mapping (already done in Task 2.5.2)
uv run scripts/map_archetype_categories.py

# Phase 2: Run filtering agents
uv run scripts/filter_archetypes.py    # Sequential first
uv run scripts/filter_boost_sets.py &  # Parallel
uv run scripts/filter_powers.py &      # Parallel (uses mapping)
uv run scripts/filter_metadata.py &    # Parallel
wait

# Phase 3: Validate and create manifest
uv run scripts/validate_filtered_data.py
```

## Validation Checks

### Completeness Checks
- [ ] All 15 player archetypes present
- [ ] Pool powers present (15 powersets)
- [ ] Epic powers present (81 powersets)
- [ ] Inherent powers present
- [ ] Incarnate powers present (3 directories)
- [ ] All 227 boost sets present
- [ ] All 30 archetype categories present

### Schema Integrity Checks
- [ ] All index.json files are valid JSON
- [ ] No broken references between files
- [ ] Required fields present in all files

### Size Checks
- [ ] Filtered data is 1,000-2,000 files (~5% of original)
- [ ] No empty directories
- [ ] File sizes reasonable (not corrupted)

## Success Criteria

1. **File Reduction:** 95%+ reduction from source
2. **Player Completeness:** All player powers included
3. **No False Negatives:** No player powers excluded
4. **Validation:** All checks pass
5. **Documentation:** Complete manifest with audit trail
6. **Ready for Import:** Filtered data ready for database import pipeline

## Next Steps After Filtering

See Task 2.5.5 (#305) for:
- Integrating filtered data into import pipeline
- Updating I12 parser to use filtered data
- Testing import with filtered dataset
- Database migration with player-only data
