# City of Data Pruning Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Prune City of Data raw dataset (~36,000 powers) to include only player-relevant powers, creating a filtered dataset ready for database import.

**Architecture:** Three-phase approach: (1) Sequential mapping agent documents structure comprehensively with incremental commits, (2) Parallel filtering agents process directories using 3-layer filter rules, (3) Sequential synthesis agent validates results and creates tracking manifest. Uses existing tools (just jq, fd, rg) with Python scripts for complex logic.

**Tech Stack:** Python 3.11+, jq for JSON processing, fd/rg for file operations, git for incremental commits, GitHub Issues for tracking

---

## Prerequisites

- [ ] Current branch: `fix/claude-review-comment-support` or create new feature branch
- [ ] `just jq` command available (already created)
- [ ] City of Data directory exists at `/Users/w/code/mids-hero-web/external/city_of_data/raw_data_homecoming-20250617_6916`
- [ ] GitHub issues created: #300 (Epic), #302-305 (Tasks)

---

## Task 2.5.2: Phase 1 - Map and Document City of Data Structure

**Files:**
- Create: `.claude/docs/city-of-data-structure-map.md`
- Create: `.claude/docs/city-of-data-schema-reference.md`
- Create: `.claude/docs/player-power-identification.md`
- Create: `.claude/docs/city-of-data-pruning-strategy.md`
- Modify: `.claude/state/progress.json` (update progress tracking)

**Context Management Strategy:** This task involves exploring ~36,000 files. To avoid context exhaustion:
- Commit findings every 15-20 minutes
- Update TodoWrite checklist after each directory
- Use `just ucp "docs: mapped {directory}"` frequently
- Keep sessions focused on one documentation file at a time

### Step 1: Initialize documentation structure

**Action:** Create directory and initialize first document with header

```bash
# Ensure docs directory exists
mkdir -p /Users/w/code/mids-hero-web/.claude/docs

# Create empty structure map document
touch /Users/w/code/mids-hero-web/.claude/docs/city-of-data-structure-map.md
```

**Expected:** Files created, ready for content

### Step 2: Map top-level directory structure

**Action:** List top-level directories and count files

```bash
cd /Users/w/code/mids-hero-web/external/city_of_data/raw_data_homecoming-20250617_6916

# List directories with details
ls -lh

# Count total files
fd -t f . | wc -l

# Count files per directory
for dir in */; do
  echo "$dir: $(fd -t f . "$dir" | wc -l) files"
done
```

**Document in city-of-data-structure-map.md:**

```markdown
# City of Data Structure Map

> **Generated:** 2025-11-01
> **Source:** raw_data_homecoming-20250617_6916
> **Purpose:** Complete directory mapping for player power filtering

## Overview

Total files: [INSERT COUNT]

## Top-Level Directory Structure

### archetypes/
**Purpose:** Player archetype definitions
**Files:** [COUNT]
**Player Relevant:** YES - Keep all

### boost_sets/
**Purpose:** Enhancement/IO set definitions
**Files:** [COUNT]
**Player Relevant:** YES - Keep all (all enhancements are player-relevant)

### entities/
**Purpose:** Character entities (NPCs and players)
**Files:** [COUNT]
**Player Relevant:** PARTIAL - Likely NPC-heavy, needs analysis

[Continue for each directory...]
```

**Expected:** First section of structure map documented

### Step 3: Commit initial structure mapping

**Action:** Commit progress to avoid losing work

```bash
git add .claude/docs/city-of-data-structure-map.md
git commit -m "docs: initial City of Data directory structure mapping

- Mapped top-level directories
- Counted files per directory
- Identified player-relevant directories

Part of #302 Task 2.5.2 Phase 1"
```

**Expected:** Clean commit, work saved

### Step 4: Analyze powers/index.json schema

**Action:** Examine master power category index

```bash
cd /Users/w/code/mids-hero-web/external/city_of_data/raw_data_homecoming-20250617_6916

# View structure
just jq '.' powers/index.json | head -100

# Get keys
just jq 'keys' powers/index.json

# List power categories
just jq '.power_categories | keys' powers/index.json

# Sample first category
just jq '.power_categories | .[0]' powers/index.json
```

**Document in city-of-data-schema-reference.md:**

```markdown
# City of Data Schema Reference

> **Generated:** 2025-11-01
> **Purpose:** JSON schema documentation for filtering logic

## powers/index.json

**Purpose:** Master index of all power categories in the game

**Structure:**
```json
{
  "revision": "string",
  "power_categories": [
    {
      "name": "Category_Name",
      "display_name": "Human Readable Name",
      // Additional fields discovered
    }
  ]
}
```

**Relationships:** Links to `powers/{category}/index.json` files

**Player Relevance Indicators:**
- Categories containing "Pool" → Player pool powers
- Categories containing "Epic" → Player epic pools
- Categories containing "Inherent" → Player inherent abilities
- Categories containing "Incarnate" → Player incarnate powers
- Categories referenced in `archetypes/*/index.json` → Player primary/secondary sets

**Example:**
```json
[INSERT ACTUAL SNIPPET FROM FILE]
```

**Total Categories:** [COUNT]
```

**Expected:** Schema documented with real examples

### Step 5: Commit schema documentation progress

**Action:** Save schema analysis work

```bash
git add .claude/docs/city-of-data-schema-reference.md
git commit -m "docs: document powers/index.json schema

- Analyzed master power category index
- Identified player relevance indicators
- Added real example snippets

Part of #302 Task 2.5.2 Phase 1"
```

**Expected:** Clean commit

### Step 6: Analyze archetype structure

**Action:** Examine archetype definitions to understand primary/secondary powerset mappings

```bash
cd /Users/w/code/mids-hero-web/external/city_of_data/raw_data_homecoming-20250617_6916

# List all archetypes
ls -1 archetypes/

# Sample Blaster archetype
just jq '.' archetypes/Blaster/index.json | head -100

# Extract primary sets structure
just jq '.primary_sets // .primaries // keys' archetypes/Blaster/index.json

# Extract secondary sets structure
just jq '.secondary_sets // .secondaries // keys' archetypes/Blaster/index.json

# Repeat for 2-3 more archetypes to identify pattern
just jq 'keys' archetypes/Controller/index.json
just jq 'keys' archetypes/Tanker/index.json
```

**Document in city-of-data-schema-reference.md:**

Add section:

```markdown
## archetypes/{name}/index.json

**Purpose:** Defines archetype's available primary and secondary powersets

**Structure:**
```json
{
  "archetype_name": "string",
  "primary_sets": ["Category_Name_1", "Category_Name_2"],
  "secondary_sets": ["Category_Name_3", "Category_Name_4"],
  // Additional fields
}
```

**Relationships:**
- `primary_sets` → Links to power categories in `powers/`
- `secondary_sets` → Links to power categories in `powers/`

**Player Relevance:** ALL archetype files are player-relevant (keep all)

**Usage for Filtering:** Build map of archetype → categories to identify Layer 2 player power categories

**Example - Blaster:**
```json
[INSERT ACTUAL BLASTER DATA]
```

**Known Archetypes:** [LIST ALL]
```

**Expected:** Archetype schema documented with mapping strategy

### Step 7: Build archetype-to-category mapping

**Action:** Create Python script to extract all archetype→category relationships

**Create file:** `scripts/map_archetype_categories.py`

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pathlib"]
# ///

"""
Extract archetype → power category mappings from City of Data.

Usage: uv run scripts/map_archetype_categories.py
Output: .claude/docs/archetype-category-mapping.json
"""

import json
from pathlib import Path
from typing import Dict, List, Set

def extract_archetype_categories(archetypes_dir: Path) -> Dict[str, Dict[str, List[str]]]:
    """Extract primary/secondary categories for each archetype."""
    mapping = {}

    for archetype_path in archetypes_dir.iterdir():
        if not archetype_path.is_dir():
            continue

        archetype_name = archetype_path.name
        index_file = archetype_path / "index.json"

        if not index_file.exists():
            print(f"Warning: No index.json for {archetype_name}")
            continue

        with open(index_file) as f:
            data = json.load(f)

        # Try different possible field names
        primary = (
            data.get("primary_sets") or
            data.get("primaries") or
            data.get("primary_powersets") or
            []
        )

        secondary = (
            data.get("secondary_sets") or
            data.get("secondaries") or
            data.get("secondary_powersets") or
            []
        )

        mapping[archetype_name] = {
            "primary": primary,
            "secondary": secondary
        }

        print(f"✓ {archetype_name}: {len(primary)} primary, {len(secondary)} secondary")

    return mapping

def get_all_archetype_categories(mapping: Dict) -> Set[str]:
    """Get unique set of all categories referenced by archetypes."""
    categories = set()
    for archetype, sets in mapping.items():
        categories.update(sets["primary"])
        categories.update(sets["secondary"])
    return categories

def main():
    base_dir = Path("/Users/w/code/mids-hero-web/external/city_of_data/raw_data_homecoming-20250617_6916")
    archetypes_dir = base_dir / "archetypes"
    output_file = Path("/Users/w/code/mids-hero-web/.claude/docs/archetype-category-mapping.json")

    print("Extracting archetype→category mappings...")
    mapping = extract_archetype_categories(archetypes_dir)

    print("\nAll archetype-linked categories:")
    all_categories = get_all_archetype_categories(mapping)
    for cat in sorted(all_categories):
        print(f"  - {cat}")

    # Save mapping
    output_data = {
        "archetypes": mapping,
        "all_categories": sorted(list(all_categories)),
        "total_archetypes": len(mapping),
        "total_categories": len(all_categories)
    }

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"\n✅ Mapping saved to {output_file}")
    print(f"Total archetypes: {len(mapping)}")
    print(f"Total unique categories: {len(all_categories)}")

if __name__ == "__main__":
    main()
```

**Run:**

```bash
cd /Users/w/code/mids-hero-web
uv run scripts/map_archetype_categories.py
```

**Expected:**
- Script outputs archetype analysis
- Creates `.claude/docs/archetype-category-mapping.json`
- Shows total archetypes and categories

### Step 8: Commit archetype mapping

**Action:** Save mapping script and output

```bash
git add scripts/map_archetype_categories.py
git add .claude/docs/archetype-category-mapping.json
git add .claude/docs/city-of-data-schema-reference.md
git commit -m "docs: extract archetype→category mappings

- Created Python script to analyze archetype definitions
- Generated mapping of all player archetype categories
- Updated schema documentation with archetype structure

Part of #302 Task 2.5.2 Phase 1"
```

**Expected:** Clean commit with mapping data

### Step 9: Identify explicit player categories

**Action:** Analyze power categories for explicit player patterns

```bash
cd /Users/w/code/mids-hero-web/external/city_of_data/raw_data_homecoming-20250617_6916

# List all power categories
just jq '.power_categories[] | .name' powers/index.json > /tmp/all_categories.txt

# Find Pool categories
rg -i "pool" /tmp/all_categories.txt

# Find Epic categories
rg -i "epic" /tmp/all_categories.txt

# Find Inherent categories
rg -i "inherent" /tmp/all_categories.txt

# Find Incarnate categories
rg -i "incarnate" /tmp/all_categories.txt

# Count each type
echo "Pool: $(rg -i 'pool' /tmp/all_categories.txt | wc -l)"
echo "Epic: $(rg -i 'epic' /tmp/all_categories.txt | wc -l)"
echo "Inherent: $(rg -i 'inherent' /tmp/all_categories.txt | wc -l)"
echo "Incarnate: $(rg -i 'incarnate' /tmp/all_categories.txt | wc -l)"
```

**Document in player-power-identification.md:**

```markdown
# Player Power Identification Guide

> **Generated:** 2025-11-01
> **Purpose:** Define filtering rules for player vs NPC power classification

## Overview

City of Heroes has ~36,000 total powers. Most are NPC-specific. This guide defines the 3-layer filtering approach to identify player-relevant powers.

## Layer 1: Explicit Player Categories

Categories with names matching these patterns are player-relevant:

### Pool Powers
**Pattern:** Category name contains "Pool"
**Count:** [INSERT COUNT]
**Examples:**
- Pool.Fighting
- Pool.Speed
- Pool.Leadership
[INSERT MORE FROM ACTUAL DATA]

### Epic Powers
**Pattern:** Category name contains "Epic"
**Count:** [INSERT COUNT]
**Examples:**
- [INSERT FROM ACTUAL DATA]

### Inherent Powers
**Pattern:** Category name contains "Inherent"
**Count:** [INSERT COUNT]
**Examples:**
- [INSERT FROM ACTUAL DATA]

### Incarnate Powers
**Pattern:** Category name contains "Incarnate"
**Count:** [INSERT COUNT]
**Examples:**
- [INSERT FROM ACTUAL DATA]

**Total Layer 1 Categories:** [SUM]

## Layer 2: Archetype-Linked Categories

Categories referenced in archetype primary/secondary sets.

**Source:** `.claude/docs/archetype-category-mapping.json`

**Total Layer 2 Categories:** [COUNT FROM MAPPING]

**Examples:**
- Tanker_Melee.* (Tanker primary sets)
- Blaster_Ranged.* (Blaster primary sets)
- Controller_Control.* (Controller primary sets)
[INSERT MORE FROM ACTUAL DATA]

## Layer 3: Special Directories

Entire directories that are player-relevant:

### boost_sets/
**Reason:** ALL enhancement/IO sets are player powers
**Action:** Keep entire directory

### archetypes/
**Reason:** Defines player archetypes
**Action:** Keep entire directory

## Exclusion Patterns

Clear NPC-only indicators:

### Pattern Matches
- `Villain_*` → NPC villain powers
- `NPC_*` → Explicit NPC designation
- `Critter_*` → NPC critter powers
- `Enemy_*` → NPC enemy powers

### Entity-Linked Without Archetype
Powers in `entities/` directory that are NOT referenced by any archetype are likely NPC-only.

## Edge Cases & Ambiguities

[TO BE FILLED DURING ANALYSIS]

**Temporary Powers:** Need classification (some player, some event-specific)
**Customization Data:** Likely player-relevant if linked to player powers
**Special Events:** Case-by-case review

## Filtering Decision Matrix

```
IF category name matches Layer 1 patterns → KEEP
ELSE IF category in archetype mapping (Layer 2) → KEEP
ELSE IF directory in Layer 3 special list → KEEP
ELSE IF category matches exclusion patterns → EXCLUDE
ELSE → FLAG FOR MANUAL REVIEW
```
```

**Expected:** Complete player identification guide with real data

### Step 10: Commit player identification guide

**Action:** Save filtering rules

```bash
git add .claude/docs/player-power-identification.md
git commit -m "docs: define 3-layer player power filtering rules

- Layer 1: Explicit categories (Pool, Epic, Inherent, Incarnate)
- Layer 2: Archetype-linked categories from mapping
- Layer 3: Special directories (boost_sets, archetypes)
- Exclusion patterns for NPC-only powers

Part of #302 Task 2.5.2 Phase 1"
```

**Expected:** Clean commit

### Step 11: Analyze boost_sets structure

**Action:** Understand enhancement data structure

```bash
cd /Users/w/code/mids-hero-web/external/city_of_data/raw_data_homecoming-20250617_6916

# Count boost set files
fd -t f . boost_sets/ | wc -l

# Check for index
just jq 'keys' boost_sets/index.json

# Sample a boost set
fd 'index.json' boost_sets/ | head -5
just jq '.' boost_sets/[FIRST_SET_FOUND]/index.json | head -50
```

**Add to city-of-data-schema-reference.md:**

```markdown
## boost_sets/index.json

**Purpose:** Master index of enhancement/IO sets

**Structure:**
```json
{
  "boost_sets": [
    {
      "name": "string",
      // Additional fields
    }
  ]
}
```

**Player Relevance:** ALL boost sets are player-relevant

## boost_sets/{set_name}/index.json

**Purpose:** Individual enhancement set definition

**Structure:**
[INSERT FROM ACTUAL DATA]

**Player Relevance:** YES - All enhancements are for player builds

**Filtering Action:** Keep entire `boost_sets/` directory
```

**Expected:** Boost sets schema documented

### Step 12: Create pruning strategy document

**Action:** Synthesize all findings into actionable filtering strategy

**Create:** `.claude/docs/city-of-data-pruning-strategy.md`

```markdown
# City of Data Pruning Strategy

> **Generated:** 2025-11-01
> **Purpose:** Actionable filtering plan for creating player-only dataset

## Filter Rules Summary

### Layer 1: Explicit Categories
Keep if category name matches:
- `*Pool*`
- `*Epic*`
- `*Inherent*`
- `*Incarnate*`

**Implementation:** String pattern matching on category names

### Layer 2: Archetype-Linked
Keep if category in archetype mapping:
- Load `.claude/docs/archetype-category-mapping.json`
- Check if category in `all_categories` list

**Implementation:** Set membership test

### Layer 3: Special Directories
Always keep entire directories:
- `boost_sets/` (all enhancements)
- `archetypes/` (player archetype definitions)

**Implementation:** Directory-level copy

### Exclusion Patterns
Exclude if category name matches:
- `Villain_*`
- `NPC_*`
- `Critter_*`
- `Enemy_*`

**Implementation:** String pattern matching (takes precedence over Layer 1/2)

## Directory Processing Plan

### 1. archetypes/
**Action:** Copy entire directory
**Reason:** All player archetype definitions
**Agent:** Archetypes Processor

### 2. boost_sets/
**Action:** Copy entire directory
**Reason:** All enhancement data is player-relevant
**Agent:** Boost Sets Processor

### 3. powers/
**Action:** Apply Layer 1 + Layer 2 filters
**Process:**
1. Load archetype category mapping
2. Read `powers/index.json`
3. For each category:
   - Check exclusion patterns → EXCLUDE
   - Check Layer 1 patterns → KEEP
   - Check Layer 2 mapping → KEEP
   - Else → FLAG for manual review
4. Copy matching category directories

**Agent:** Powers Processor (depends on Archetypes Processor for mapping)

### 4. entities/
**Action:** EXCLUDE (NPC-heavy, not needed for build planner)
**Reason:** Entity data not required for power calculations
**Agent:** None (skip directory)

### 5. tables/
**Action:** REVIEW case-by-case
**Process:** Check if tables contain player-relevant lookup data
**Agent:** Metadata Processor

### 6. tags/, entity_tags/, exclusion_groups/, recharge_groups/
**Action:** REVIEW case-by-case
**Process:** Determine if metadata needed for power mechanics
**Agent:** Metadata Processor

## Output Structure

```
filtered_data/
├── archetypes/           # Complete copy
├── boost_sets/           # Complete copy
├── powers/               # Filtered categories
│   ├── Pool.*/          # Layer 1
│   ├── Epic.*/          # Layer 1
│   ├── Inherent.*/      # Layer 1
│   ├── Incarnate.*/     # Layer 1
│   └── [Archetype_*]/   # Layer 2
├── tables/              # Selected tables (if any)
└── manifest.json        # Tracking manifest
```

## Agent Coordination

### Sequential Phase (Agent 1)
1. **Archetypes Processor** runs first
2. Generates archetype-category mapping
3. Outputs mapping for Powers Processor

### Parallel Phase (Agents 2, 3, 4)
Launch simultaneously:
- **Boost Sets Processor** (independent)
- **Powers Processor** (uses Agent 1 output)
- **Metadata Processor** (independent)

### Synthesis Phase (Agent 5)
1. Collect outputs from all agents
2. Validate completeness
3. Create manifest.json

## Manifest Format Specification

See `.claude/docs/city-of-data-pruning-plan.md` for complete manifest schema.

**Key sections:**
- `metadata`: Source, date, counts, strategy version
- `filter_rules`: Applied rules per layer
- `kept_files`: Full list with reasons
- `excluded_files`: Full list with reasons
- `statistics`: Counts by layer and directory
- `validation`: Completeness checks
```

**Expected:** Complete actionable strategy

### Step 13: Commit pruning strategy

**Action:** Save final strategy document

```bash
git add .claude/docs/city-of-data-pruning-strategy.md
git add .claude/docs/city-of-data-schema-reference.md
git commit -m "docs: complete Phase 1 pruning strategy

- Defined 3-layer filtering logic
- Created directory processing plan
- Specified agent coordination strategy
- Documented output structure and manifest format

Part of #302 Task 2.5.2 Phase 1"
```

**Expected:** Clean commit

### Step 14: Update progress tracking

**Action:** Mark Phase 1 complete in progress.json

**Modify:** `.claude/state/progress.json`

Change:
```json
"epic2_5": {
  "progress": 20,
  "tasks": [
    "✅ Task 2.5.1: Create comprehensive pruning plan and documentation",
    "🚧 Task 2.5.2: Phase 1 - Map and document City of Data structure",
```

To:
```json
"epic2_5": {
  "progress": 40,
  "tasks": [
    "✅ Task 2.5.1: Create comprehensive pruning plan and documentation",
    "✅ Task 2.5.2: Phase 1 - Map and document City of Data structure",
    "🚧 Task 2.5.3: Phase 2 - Execute multi-layered filtering",
```

**Commit:**

```bash
git add .claude/state/progress.json
git commit -m "progress: complete Task 2.5.2 Phase 1 mapping

- All 4 documentation files created
- Archetype-category mapping extracted
- Filtering strategy defined
- Ready for Phase 2 execution

Closes #302"
```

**Expected:** Progress updated, Phase 1 complete

---

## Task 2.5.3: Phase 2 - Execute Multi-Layered Filtering

**Files:**
- Create: `scripts/filter_archetypes.py`
- Create: `scripts/filter_powers.py`
- Create: `scripts/filter_boost_sets.py`
- Create: `scripts/filter_metadata.py`
- Create: `filtered_data/` directory structure
- Modify: `.claude/state/progress.json`

**Agent Strategy:** Launch 3 agents in parallel (Archetypes, Boost Sets, Metadata), then launch Powers agent after Archetypes completes.

### Step 1: Create output directory structure

**Action:** Initialize filtered_data directory

```bash
cd /Users/w/code/mids-hero-web

mkdir -p filtered_data/{archetypes,boost_sets,powers,tables}
```

**Expected:** Directory structure ready

### Step 2: Create Archetypes Processor script

**Create file:** `scripts/filter_archetypes.py`

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pathlib"]
# ///

"""
Filter archetypes directory (copy all - all player-relevant).

Usage: uv run scripts/filter_archetypes.py
"""

import json
import shutil
from pathlib import Path
from typing import List, Dict

SOURCE_DIR = Path("/Users/w/code/mids-hero-web/external/city_of_data/raw_data_homecoming-20250617_6916/archetypes")
OUTPUT_DIR = Path("/Users/w/code/mids-hero-web/filtered_data/archetypes")
MANIFEST_ENTRIES: List[Dict] = []

def copy_archetype_directory():
    """Copy entire archetypes directory."""
    print(f"Copying archetypes from {SOURCE_DIR} to {OUTPUT_DIR}...")

    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)

    shutil.copytree(SOURCE_DIR, OUTPUT_DIR)

    # Count files
    total_files = len(list(OUTPUT_DIR.rglob("*")))
    print(f"✓ Copied {total_files} archetype files")

    # Generate manifest entries
    for file_path in OUTPUT_DIR.rglob("*"):
        if file_path.is_file():
            relative_source = file_path.relative_to(Path("/Users/w/code/mids-hero-web/filtered_data"))
            MANIFEST_ENTRIES.append({
                "source": f"archetypes/{file_path.relative_to(OUTPUT_DIR)}",
                "reason": "layer_3_special_directory:archetypes",
                "layer": 3,
                "copied_to": str(relative_source),
                "size_bytes": file_path.stat().st_size
            })

    return total_files

def save_manifest_fragment():
    """Save manifest entries for synthesis agent."""
    manifest_file = Path("/Users/w/code/mids-hero-web/filtered_data/archetypes_manifest.json")

    with open(manifest_file, "w") as f:
        json.dump({
            "directory": "archetypes",
            "total_files": len(MANIFEST_ENTRIES),
            "entries": MANIFEST_ENTRIES
        }, f, indent=2)

    print(f"✓ Saved manifest fragment to {manifest_file}")

def main():
    print("=== Archetypes Processor ===\n")

    total = copy_archetype_directory()
    save_manifest_fragment()

    print(f"\n✅ Archetypes processing complete")
    print(f"Total files: {total}")
    print(f"Location: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
```

**Run:**

```bash
cd /Users/w/code/mids-hero-web
uv run scripts/filter_archetypes.py
```

**Expected:**
- `filtered_data/archetypes/` populated
- `filtered_data/archetypes_manifest.json` created
- Output shows file count

### Step 3: Commit Archetypes filtering

**Action:** Save filtered archetypes

```bash
git add scripts/filter_archetypes.py
git add filtered_data/archetypes/
git add filtered_data/archetypes_manifest.json
git commit -m "feat: filter archetypes (Layer 3 - copy all)

- Created Archetypes Processor script
- Copied all archetype definitions (all player-relevant)
- Generated manifest fragment

Part of #303 Task 2.5.3 Phase 2"
```

**Expected:** Clean commit

### Step 4: Create Boost Sets Processor script

**Create file:** `scripts/filter_boost_sets.py`

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pathlib"]
# ///

"""
Filter boost_sets directory (copy all - all enhancements player-relevant).

Usage: uv run scripts/filter_boost_sets.py
"""

import json
import shutil
from pathlib import Path
from typing import List, Dict

SOURCE_DIR = Path("/Users/w/code/mids-hero-web/external/city_of_data/raw_data_homecoming-20250617_6916/boost_sets")
OUTPUT_DIR = Path("/Users/w/code/mids-hero-web/filtered_data/boost_sets")
MANIFEST_ENTRIES: List[Dict] = []

def copy_boost_sets_directory():
    """Copy entire boost_sets directory."""
    print(f"Copying boost_sets from {SOURCE_DIR} to {OUTPUT_DIR}...")

    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)

    shutil.copytree(SOURCE_DIR, OUTPUT_DIR)

    # Count files
    total_files = len(list(OUTPUT_DIR.rglob("*")))
    print(f"✓ Copied {total_files} boost set files")

    # Generate manifest entries
    for file_path in OUTPUT_DIR.rglob("*"):
        if file_path.is_file():
            relative_source = file_path.relative_to(Path("/Users/w/code/mids-hero-web/filtered_data"))
            MANIFEST_ENTRIES.append({
                "source": f"boost_sets/{file_path.relative_to(OUTPUT_DIR)}",
                "reason": "layer_3_special_directory:boost_sets",
                "layer": 3,
                "copied_to": str(relative_source),
                "size_bytes": file_path.stat().st_size
            })

    return total_files

def save_manifest_fragment():
    """Save manifest entries for synthesis agent."""
    manifest_file = Path("/Users/w/code/mids-hero-web/filtered_data/boost_sets_manifest.json")

    with open(manifest_file, "w") as f:
        json.dump({
            "directory": "boost_sets",
            "total_files": len(MANIFEST_ENTRIES),
            "entries": MANIFEST_ENTRIES
        }, f, indent=2)

    print(f"✓ Saved manifest fragment to {manifest_file}")

def main():
    print("=== Boost Sets Processor ===\n")

    total = copy_boost_sets_directory()
    save_manifest_fragment()

    print(f"\n✅ Boost sets processing complete")
    print(f"Total files: {total}")
    print(f"Location: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
```

**Run:**

```bash
cd /Users/w/code/mids-hero-web
uv run scripts/filter_boost_sets.py
```

**Expected:**
- `filtered_data/boost_sets/` populated
- `filtered_data/boost_sets_manifest.json` created

### Step 5: Commit Boost Sets filtering

**Action:** Save filtered boost sets

```bash
git add scripts/filter_boost_sets.py
git add filtered_data/boost_sets/
git add filtered_data/boost_sets_manifest.json
git commit -m "feat: filter boost_sets (Layer 3 - copy all)

- Created Boost Sets Processor script
- Copied all enhancement sets (all player-relevant)
- Generated manifest fragment

Part of #303 Task 2.5.3 Phase 2"
```

**Expected:** Clean commit

### Step 6: Create Powers Processor script

**Create file:** `scripts/filter_powers.py`

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pathlib"]
# ///

"""
Filter powers directory using Layer 1 + Layer 2 rules.

Usage: uv run scripts/filter_powers.py
"""

import json
import shutil
from pathlib import Path
from typing import List, Dict, Set

SOURCE_DIR = Path("/Users/w/code/mids-hero-web/external/city_of_data/raw_data_homecoming-20250617_6916/powers")
OUTPUT_DIR = Path("/Users/w/code/mids-hero-web/filtered_data/powers")
MAPPING_FILE = Path("/Users/w/code/mids-hero-web/.claude/docs/archetype-category-mapping.json")
MANIFEST_ENTRIES: List[Dict] = []
EXCLUDED_ENTRIES: List[Dict] = []

# Layer 1 patterns
LAYER_1_PATTERNS = ["Pool", "Epic", "Inherent", "Incarnate"]

# Exclusion patterns
EXCLUSION_PATTERNS = ["Villain_", "NPC_", "Critter_", "Enemy_"]

def load_archetype_categories() -> Set[str]:
    """Load Layer 2 archetype-linked categories."""
    with open(MAPPING_FILE) as f:
        data = json.load(f)
    return set(data["all_categories"])

def matches_layer_1(category_name: str) -> bool:
    """Check if category matches Layer 1 explicit patterns."""
    return any(pattern in category_name for pattern in LAYER_1_PATTERNS)

def matches_exclusion(category_name: str) -> bool:
    """Check if category matches exclusion patterns."""
    return any(pattern in category_name for pattern in EXCLUSION_PATTERNS)

def filter_powers(archetype_categories: Set[str]):
    """Filter power categories using 3-layer rules."""

    # Read powers index
    with open(SOURCE_DIR / "index.json") as f:
        powers_index = json.load(f)

    kept_categories = []
    excluded_categories = []

    # Get all category directories
    for category_dir in SOURCE_DIR.iterdir():
        if not category_dir.is_dir() or category_dir.name.startswith("."):
            continue

        category_name = category_dir.name

        # Check exclusion first
        if matches_exclusion(category_name):
            excluded_categories.append({
                "category": category_name,
                "reason": "exclusion_pattern"
            })
            print(f"✗ EXCLUDE: {category_name} (exclusion pattern)")
            continue

        # Check Layer 1
        if matches_layer_1(category_name):
            kept_categories.append({
                "category": category_name,
                "reason": "layer_1_explicit",
                "layer": 1
            })
            print(f"✓ KEEP: {category_name} (Layer 1 - explicit)")
            copy_category(category_dir, category_name, "layer_1_explicit", 1)
            continue

        # Check Layer 2
        if category_name in archetype_categories:
            kept_categories.append({
                "category": category_name,
                "reason": "layer_2_archetype_linked",
                "layer": 2
            })
            print(f"✓ KEEP: {category_name} (Layer 2 - archetype-linked)")
            copy_category(category_dir, category_name, "layer_2_archetype_linked", 2)
            continue

        # Flag for review
        excluded_categories.append({
            "category": category_name,
            "reason": "no_match_review_needed"
        })
        print(f"? REVIEW: {category_name} (no matching rule)")

    print(f"\n✅ Filtering complete")
    print(f"Kept: {len(kept_categories)} categories")
    print(f"Excluded: {len(excluded_categories)} categories")

    return kept_categories, excluded_categories

def copy_category(category_dir: Path, category_name: str, reason: str, layer: int):
    """Copy a power category directory."""
    dest_dir = OUTPUT_DIR / category_name

    if dest_dir.exists():
        shutil.rmtree(dest_dir)

    shutil.copytree(category_dir, dest_dir)

    # Track files
    for file_path in dest_dir.rglob("*"):
        if file_path.is_file():
            relative_source = file_path.relative_to(Path("/Users/w/code/mids-hero-web/filtered_data"))
            MANIFEST_ENTRIES.append({
                "source": f"powers/{category_name}/{file_path.relative_to(dest_dir)}",
                "reason": reason,
                "layer": layer,
                "copied_to": str(relative_source),
                "size_bytes": file_path.stat().st_size
            })

def save_manifest_fragment(kept_categories, excluded_categories):
    """Save manifest entries for synthesis agent."""
    manifest_file = Path("/Users/w/code/mids-hero-web/filtered_data/powers_manifest.json")

    with open(manifest_file, "w") as f:
        json.dump({
            "directory": "powers",
            "total_files": len(MANIFEST_ENTRIES),
            "kept_categories": kept_categories,
            "excluded_categories": excluded_categories,
            "entries": MANIFEST_ENTRIES
        }, f, indent=2)

    print(f"✓ Saved manifest fragment to {manifest_file}")

def main():
    print("=== Powers Processor ===\n")

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load archetype categories
    print("Loading archetype-category mapping...")
    archetype_categories = load_archetype_categories()
    print(f"✓ Loaded {len(archetype_categories)} archetype-linked categories\n")

    # Filter powers
    kept, excluded = filter_powers(archetype_categories)

    # Save manifest
    save_manifest_fragment(kept, excluded)

    print(f"\n✅ Powers processing complete")
    print(f"Location: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
```

**Run:**

```bash
cd /Users/w/code/mids-hero-web
uv run scripts/filter_powers.py
```

**Expected:**
- `filtered_data/powers/` populated with filtered categories
- `filtered_data/powers_manifest.json` created
- Output shows kept/excluded breakdown

### Step 7: Commit Powers filtering

**Action:** Save filtered powers

```bash
git add scripts/filter_powers.py
git add filtered_data/powers/
git add filtered_data/powers_manifest.json
git commit -m "feat: filter powers (Layer 1 + Layer 2)

- Created Powers Processor script
- Applied explicit category patterns (Layer 1)
- Applied archetype-linked filtering (Layer 2)
- Generated manifest fragment with kept/excluded tracking

Part of #303 Task 2.5.3 Phase 2"
```

**Expected:** Clean commit

### Step 8: Create Metadata Processor script

**Create file:** `scripts/filter_metadata.py`

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pathlib"]
# ///

"""
Review and selectively copy metadata directories.

Usage: uv run scripts/filter_metadata.py
"""

import json
import shutil
from pathlib import Path
from typing import List, Dict

SOURCE_BASE = Path("/Users/w/code/mids-hero-web/external/city_of_data/raw_data_homecoming-20250617_6916")
OUTPUT_BASE = Path("/Users/w/code/mids-hero-web/filtered_data")
MANIFEST_ENTRIES: List[Dict] = []

# Directories to review
METADATA_DIRS = [
    "tables",
    "tags",
    "entity_tags",
    "exclusion_groups",
    "recharge_groups"
]

def analyze_directory(dir_name: str):
    """Analyze metadata directory to determine relevance."""
    source_dir = SOURCE_BASE / dir_name

    if not source_dir.exists():
        print(f"⚠️  {dir_name} not found, skipping")
        return None

    file_count = len(list(source_dir.rglob("*")))
    print(f"\n📂 {dir_name}/")
    print(f"   Files: {file_count}")

    # Check for index.json
    index_file = source_dir / "index.json"
    if index_file.exists():
        with open(index_file) as f:
            data = json.load(f)
        print(f"   Index keys: {list(data.keys())}")

    # For now, include tables (likely needed for lookups)
    # Skip entity_tags (NPC-related)
    # Include exclusion_groups, recharge_groups (power mechanics)
    # Include tags (may be referenced)

    if dir_name in ["tables", "exclusion_groups", "recharge_groups", "tags"]:
        return True  # Keep
    else:
        return False  # Exclude

def copy_metadata_directory(dir_name: str):
    """Copy metadata directory to filtered_data."""
    source_dir = SOURCE_BASE / dir_name
    dest_dir = OUTPUT_BASE / dir_name

    print(f"✓ Copying {dir_name}...")

    if dest_dir.exists():
        shutil.rmtree(dest_dir)

    shutil.copytree(source_dir, dest_dir)

    # Track files
    for file_path in dest_dir.rglob("*"):
        if file_path.is_file():
            relative_source = file_path.relative_to(OUTPUT_BASE)
            MANIFEST_ENTRIES.append({
                "source": f"{dir_name}/{file_path.relative_to(dest_dir)}",
                "reason": f"metadata:{dir_name}",
                "layer": 3,
                "copied_to": str(relative_source),
                "size_bytes": file_path.stat().st_size
            })

def save_manifest_fragment():
    """Save manifest entries for synthesis agent."""
    manifest_file = OUTPUT_BASE / "metadata_manifest.json"

    with open(manifest_file, "w") as f:
        json.dump({
            "directory": "metadata",
            "total_files": len(MANIFEST_ENTRIES),
            "entries": MANIFEST_ENTRIES
        }, f, indent=2)

    print(f"\n✓ Saved manifest fragment to {manifest_file}")

def main():
    print("=== Metadata Processor ===\n")

    kept_dirs = []
    excluded_dirs = []

    for dir_name in METADATA_DIRS:
        should_keep = analyze_directory(dir_name)

        if should_keep is None:
            continue
        elif should_keep:
            copy_metadata_directory(dir_name)
            kept_dirs.append(dir_name)
        else:
            excluded_dirs.append(dir_name)
            print(f"✗ Excluding {dir_name}")

    save_manifest_fragment()

    print(f"\n✅ Metadata processing complete")
    print(f"Kept: {kept_dirs}")
    print(f"Excluded: {excluded_dirs}")

if __name__ == "__main__":
    main()
```

**Run:**

```bash
cd /Users/w/code/mids-hero-web
uv run scripts/filter_metadata.py
```

**Expected:**
- Selected metadata directories copied
- `filtered_data/metadata_manifest.json` created

### Step 9: Commit Metadata filtering

**Action:** Save filtered metadata

```bash
git add scripts/filter_metadata.py
git add filtered_data/tables/ || true
git add filtered_data/tags/ || true
git add filtered_data/exclusion_groups/ || true
git add filtered_data/recharge_groups/ || true
git add filtered_data/metadata_manifest.json
git commit -m "feat: filter metadata directories

- Created Metadata Processor script
- Kept: tables, exclusion_groups, recharge_groups, tags
- Excluded: entity_tags (NPC-related)
- Generated manifest fragment

Part of #303 Task 2.5.3 Phase 2"
```

**Expected:** Clean commit

### Step 10: Update progress tracking

**Action:** Mark Phase 2 complete

**Modify:** `.claude/state/progress.json`

Change:
```json
"progress": 40,
"tasks": [
  "✅ Task 2.5.2: Phase 1 - Map and document City of Data structure",
  "🚧 Task 2.5.3: Phase 2 - Execute multi-layered filtering",
```

To:
```json
"progress": 70,
"tasks": [
  "✅ Task 2.5.2: Phase 1 - Map and document City of Data structure",
  "✅ Task 2.5.3: Phase 2 - Execute multi-layered filtering",
  "🚧 Task 2.5.4: Phase 3 - Validate and create manifest",
```

**Commit:**

```bash
git add .claude/state/progress.json
git commit -m "progress: complete Task 2.5.3 Phase 2 filtering

- Filtered archetypes (all kept)
- Filtered boost_sets (all kept)
- Filtered powers (Layer 1 + Layer 2)
- Filtered metadata directories
- Generated manifest fragments
- Ready for Phase 3 validation

Closes #303"
```

**Expected:** Progress updated, Phase 2 complete

---

## Task 2.5.4: Phase 3 - Validate and Create Manifest

**Files:**
- Create: `scripts/validate_filtered_data.py`
- Create: `filtered_data/manifest.json`
- Modify: `.claude/state/progress.json`

### Step 1: Create validation script

**Create file:** `scripts/validate_filtered_data.py`

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pathlib"]
# ///

"""
Validate filtered City of Data and create comprehensive manifest.

Usage: uv run scripts/validate_filtered_data.py
"""

import json
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime

FILTERED_DIR = Path("/Users/w/code/mids-hero-web/filtered_data")
SOURCE_DIR = Path("/Users/w/code/mids-hero-web/external/city_of_data/raw_data_homecoming-20250617_6916")
OUTPUT_MANIFEST = FILTERED_DIR / "manifest.json"

def load_manifest_fragments() -> Dict:
    """Load all manifest fragments from filtering agents."""
    fragments = {}

    for fragment_file in FILTERED_DIR.glob("*_manifest.json"):
        with open(fragment_file) as f:
            data = json.load(f)
        fragments[data["directory"]] = data

    return fragments

def count_files_by_directory() -> Dict[str, int]:
    """Count files in each filtered directory."""
    counts = {}

    for directory in FILTERED_DIR.iterdir():
        if directory.is_dir() and not directory.name.startswith("."):
            file_count = len([f for f in directory.rglob("*") if f.is_file()])
            counts[directory.name] = file_count

    return counts

def validate_archetypes() -> Dict:
    """Validate archetype completeness."""
    archetypes_dir = FILTERED_DIR / "archetypes"

    # Known player archetypes (City of Heroes)
    expected_archetypes = {
        "Blaster", "Controller", "Defender", "Scrapper", "Tanker",
        "Brute", "Stalker", "Mastermind", "Dominator", "Corruptor",
        "Peacebringer", "Warshade", "Arachnos_Soldier", "Arachnos_Widow",
        # Add more as discovered
    }

    found_archetypes = {d.name for d in archetypes_dir.iterdir() if d.is_dir()}

    return {
        "expected": list(expected_archetypes),
        "found": list(found_archetypes),
        "all_present": expected_archetypes.issubset(found_archetypes),
        "extra": list(found_archetypes - expected_archetypes)
    }

def validate_power_categories() -> Dict:
    """Validate power category completeness."""
    powers_dir = FILTERED_DIR / "powers"

    if not powers_dir.exists():
        return {"error": "powers directory not found"}

    categories = [d.name for d in powers_dir.iterdir() if d.is_dir()]

    # Check for required patterns
    has_pool = any("Pool" in cat for cat in categories)
    has_epic = any("Epic" in cat for cat in categories)
    has_inherent = any("Inherent" in cat for cat in categories)
    has_incarnate = any("Incarnate" in cat for cat in categories)

    return {
        "total_categories": len(categories),
        "has_pool": has_pool,
        "has_epic": has_epic,
        "has_inherent": has_inherent,
        "has_incarnate": has_incarnate,
        "all_required_present": all([has_pool, has_epic, has_inherent, has_incarnate]),
        "sample_categories": categories[:10]
    }

def validate_boost_sets() -> Dict:
    """Validate boost sets completeness."""
    boost_dir = FILTERED_DIR / "boost_sets"

    if not boost_dir.exists():
        return {"error": "boost_sets directory not found"}

    file_count = len([f for f in boost_dir.rglob("*") if f.is_file()])

    return {
        "present": True,
        "total_files": file_count
    }

def validate_schema_integrity() -> Dict:
    """Validate that index.json files are valid JSON."""
    errors = []
    checked = 0

    for index_file in FILTERED_DIR.rglob("index.json"):
        checked += 1
        try:
            with open(index_file) as f:
                json.load(f)
        except json.JSONDecodeError as e:
            errors.append({
                "file": str(index_file.relative_to(FILTERED_DIR)),
                "error": str(e)
            })

    return {
        "files_checked": checked,
        "errors": errors,
        "valid": len(errors) == 0
    }

def compile_manifest(fragments: Dict, validation: Dict) -> Dict:
    """Compile comprehensive manifest from all data."""

    # Collect all entries
    all_kept = []
    all_excluded = []

    for directory, fragment in fragments.items():
        all_kept.extend(fragment.get("entries", []))

        # Powers has excluded entries
        if "excluded_categories" in fragment:
            for exc in fragment["excluded_categories"]:
                all_excluded.append({
                    "source": f"powers/{exc['category']}/",
                    "reason": exc["reason"]
                })

    # Count by layer
    layer_counts = {1: 0, 2: 0, 3: 0}
    for entry in all_kept:
        layer = entry.get("layer", 3)
        layer_counts[layer] = layer_counts.get(layer, 0) + 1

    # Count by directory
    dir_counts = {}
    for entry in all_kept:
        dir_name = entry["copied_to"].split("/")[0]
        dir_counts[dir_name] = dir_counts.get(dir_name, 0) + 1

    # Load filter rules
    with open(Path("/Users/w/code/mids-hero-web/.claude/docs/archetype-category-mapping.json")) as f:
        mapping = json.load(f)

    manifest = {
        "metadata": {
            "source_dir": "raw_data_homecoming-20250617_6916",
            "filtered_date": datetime.now().isoformat(),
            "total_source_files": len([f for f in SOURCE_DIR.rglob("*") if f.is_file()]),
            "kept_files": len(all_kept),
            "excluded_files": len(all_excluded),
            "strategy_version": "v1.0",
            "epic": "2.5",
            "github_issue": "#300"
        },
        "filter_rules": {
            "explicit_categories": ["Pool", "Epic", "Inherent", "Incarnate"],
            "archetype_linked": mapping["all_categories"],
            "special_directories": ["boost_sets", "archetypes"],
            "exclusion_patterns": ["Villain_*", "NPC_*", "Critter_*", "Enemy_*"]
        },
        "kept_files": all_kept,
        "excluded_files": all_excluded,
        "statistics": {
            "by_layer": layer_counts,
            "by_directory": dir_counts
        },
        "validation": validation
    }

    return manifest

def main():
    print("=== Validation & Manifest Creation ===\n")

    # Load fragments
    print("Loading manifest fragments...")
    fragments = load_manifest_fragments()
    print(f"✓ Loaded {len(fragments)} fragments\n")

    # Validate
    print("Validating filtered data...\n")

    validation = {}

    print("1. Checking archetypes...")
    validation["archetypes"] = validate_archetypes()
    print(f"   ✓ Found {len(validation['archetypes']['found'])} archetypes")

    print("2. Checking power categories...")
    validation["power_categories"] = validate_power_categories()
    print(f"   ✓ Found {validation['power_categories']['total_categories']} categories")

    print("3. Checking boost sets...")
    validation["boost_sets"] = validate_boost_sets()
    print(f"   ✓ Boost sets present: {validation['boost_sets']['total_files']} files")

    print("4. Checking schema integrity...")
    validation["schema"] = validate_schema_integrity()
    print(f"   ✓ Checked {validation['schema']['files_checked']} index files")

    # Compile manifest
    print("\nCompiling manifest...")
    manifest = compile_manifest(fragments, validation)

    # Save manifest
    with open(OUTPUT_MANIFEST, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"✓ Saved manifest to {OUTPUT_MANIFEST}")

    # Summary
    print("\n" + "="*50)
    print("VALIDATION SUMMARY")
    print("="*50)
    print(f"Total source files: {manifest['metadata']['total_source_files']:,}")
    print(f"Kept files: {manifest['metadata']['kept_files']:,}")
    print(f"Excluded files: {manifest['metadata']['excluded_files']:,}")
    print(f"\nBy Layer:")
    print(f"  Layer 1 (Explicit): {manifest['statistics']['by_layer'][1]:,}")
    print(f"  Layer 2 (Archetype-linked): {manifest['statistics']['by_layer'][2]:,}")
    print(f"  Layer 3 (Special dirs): {manifest['statistics']['by_layer'][3]:,}")
    print(f"\nValidation:")
    print(f"  Archetypes: {'✅ PASS' if validation['archetypes']['all_present'] else '⚠️  REVIEW'}")
    print(f"  Power categories: {'✅ PASS' if validation['power_categories']['all_required_present'] else '⚠️  REVIEW'}")
    print(f"  Boost sets: {'✅ PASS' if validation['boost_sets']['present'] else '❌ FAIL'}")
    print(f"  Schema integrity: {'✅ PASS' if validation['schema']['valid'] else '❌ FAIL'}")

    if validation['schema']['errors']:
        print(f"\n⚠️  Schema errors found:")
        for err in validation['schema']['errors']:
            print(f"    - {err['file']}: {err['error']}")

    print("\n✅ Validation complete")
    print(f"Manifest saved to: {OUTPUT_MANIFEST}")

if __name__ == "__main__":
    main()
```

**Run:**

```bash
cd /Users/w/code/mids-hero-web
uv run scripts/validate_filtered_data.py
```

**Expected:**
- Validation checks run
- `filtered_data/manifest.json` created
- Summary output shows pass/fail for each check

### Step 2: Review validation results

**Action:** Check validation output for any failures

If validation shows errors:
- Fix schema issues
- Review missing archetypes
- Check power category completeness
- Re-run validation

**Expected:** All validation checks pass

### Step 3: Manual review of edge cases

**Action:** Sample filtered data to verify accuracy

```bash
cd /Users/w/code/mids-hero-web/filtered_data

# Check that Pool powers are present
ls powers/ | rg -i pool

# Check that Epic powers are present
ls powers/ | rg -i epic

# Sample a filtered power category
just jq '.' powers/Pool.Fighting/index.json | head -50

# Verify archetype primary/secondary sets exist
just jq '.primary_sets' archetypes/Blaster/index.json

# Check manifest statistics
just jq '.statistics' manifest.json
just jq '.validation' manifest.json
```

**Expected:** Spot checks confirm filtering worked correctly

### Step 4: Commit validation and manifest

**Action:** Save final manifest

```bash
git add scripts/validate_filtered_data.py
git add filtered_data/manifest.json
git commit -m "feat: validate filtered data and create manifest

- Created comprehensive validation script
- Validated archetypes, power categories, boost sets
- Checked schema integrity across all index.json files
- Generated complete tracking manifest
- All validation checks pass

Part of #304 Task 2.5.4 Phase 3"
```

**Expected:** Clean commit

### Step 5: Update progress tracking

**Action:** Mark Phase 3 complete

**Modify:** `.claude/state/progress.json`

Change:
```json
"progress": 70,
"tasks": [
  "✅ Task 2.5.3: Phase 2 - Execute multi-layered filtering",
  "🚧 Task 2.5.4: Phase 3 - Validate and create manifest",
```

To:
```json
"progress": 90,
"tasks": [
  "✅ Task 2.5.3: Phase 2 - Execute multi-layered filtering",
  "✅ Task 2.5.4: Phase 3 - Validate and create manifest",
  "📋 Task 2.5.5: Integrate filtered data into import pipeline",
```

**Commit:**

```bash
git add .claude/state/progress.json
git commit -m "progress: complete Task 2.5.4 Phase 3 validation

- All filtered data validated
- Comprehensive manifest created
- Schema integrity confirmed
- Ready for import pipeline integration

Closes #304"
```

**Expected:** Progress updated, Phase 3 complete

### Step 6: Create summary document

**Action:** Document filtering results for future reference

**Create:** `.claude/docs/city-of-data-filtering-results.md`

```markdown
# City of Data Filtering Results

> **Completed:** [DATE]
> **Epic:** 2.5
> **GitHub Issue:** #300

## Summary

Successfully pruned City of Data raw dataset from ~36,000 powers to player-only subset.

## Filtering Statistics

**Source:** `raw_data_homecoming-20250617_6916`
**Output:** `filtered_data/`

**Total files:**
- Source: [FROM MANIFEST]
- Kept: [FROM MANIFEST]
- Excluded: [FROM MANIFEST]
- Reduction: [PERCENTAGE]

**By Layer:**
- Layer 1 (Explicit categories): [COUNT] files
- Layer 2 (Archetype-linked): [COUNT] files
- Layer 3 (Special directories): [COUNT] files

**By Directory:**
- archetypes/: [COUNT] files (100% kept)
- boost_sets/: [COUNT] files (100% kept)
- powers/: [COUNT] files (filtered)
- metadata/: [COUNT] files (selective)

## Validation Results

✅ All archetypes present
✅ All required power categories present (Pool, Epic, Inherent, Incarnate)
✅ Boost sets complete
✅ Schema integrity confirmed

## Next Steps

See Task 2.5.5 (#305) for import pipeline integration.

## Files

- **Manifest:** `filtered_data/manifest.json`
- **Filtered Data:** `filtered_data/`
- **Scripts:**
  - `scripts/filter_archetypes.py`
  - `scripts/filter_powers.py`
  - `scripts/filter_boost_sets.py`
  - `scripts/filter_metadata.py`
  - `scripts/validate_filtered_data.py`
```

**Commit:**

```bash
git add .claude/docs/city-of-data-filtering-results.md
git commit -m "docs: document City of Data filtering results

- Summary of filtering statistics
- Validation results
- Next steps for import integration

Part of Epic 2.5"
```

**Expected:** Results documented

---

## Final Step: Plan Complete

**Action:** Update progress to show Epic 2.5 mostly complete

**Modify:** `.claude/state/progress.json`

Change epic2_5 status to show readiness for Task 2.5.5

**Commit:**

```bash
git add .claude/state/progress.json
git commit -m "progress: Epic 2.5 Phase 1-3 complete

City of Data pruning complete:
✅ Task 2.5.1: Planning and documentation
✅ Task 2.5.2: Mapping and schema analysis
✅ Task 2.5.3: Multi-layered filtering execution
✅ Task 2.5.4: Validation and manifest creation
📋 Task 2.5.5: Import pipeline integration (next)

Ready for database import implementation.

Part of #300 Epic 2.5"
```

**Expected:** Epic 2.5 90% complete, ready for import

---

## Execution Notes

### Context Management
- Each phase commits frequently (every 15-20 minutes)
- Documentation files keep sessions under token limits
- TodoWrite tracks progress within each task

### Testing Strategy
- Validation script serves as "test" for filtering accuracy
- Manual spot checks verify filtering logic
- Manifest provides complete audit trail

### Agent Coordination
- Phase 1: Single sequential agent (avoid context exhaustion)
- Phase 2: Parallel agents (maximize efficiency)
- Phase 3: Single synthesis agent (validate consistency)

### Dependencies
- Task 2.5.3 Powers Processor depends on Task 2.5.2 archetype mapping
- Task 2.5.4 Validation depends on Task 2.5.3 filtering complete
- All tasks require `just jq` command (already created)

---

**Plan Status:** ✅ Complete - Ready for Execution
**Total Tasks:** 3 major tasks (2.5.2, 2.5.3, 2.5.4)
**Estimated Time:** 4-6 hours across all phases
**Next:** Choose execution approach (subagent-driven or parallel session)
