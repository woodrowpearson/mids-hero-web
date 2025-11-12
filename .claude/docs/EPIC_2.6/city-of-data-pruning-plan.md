# City of Data Pruning Plan

> **Epic 2.5**: City of Data Import Preparation
> **Created**: 2025-11-01
> **Status**: Planning Complete - Ready for Execution

## Executive Summary

Prune the City of Data raw dataset (`raw_data_homecoming-20250617_6916`) to include only player-relevant powers, reducing ~36,000 total powers to player-focused subset. This enables efficient import into Mids Hero Web database.

## Background

City of Heroes power data includes both player and NPC powers. Most NPC powers are critter-specific and not relevant to player build planning. According to the City of Data creator:

- **~36,000 total powers** in the dataset
- Powers organized in 3-tier hierarchy: Category → Powerset → Power
- NPCs often have unique copies of similar powersets
- Player powers include: Primary/Secondary, Pool, Epic, Inherent, Incarnate, and Enhancements

## Player Power Categories

Based on Mids Hero Web requirements, we need to keep:

1. **Primary/Secondary Powersets** - Archetype-specific powers
2. **Pool Powers** - Shared by all player archetypes
3. **Epic Powers** - Epic power pools (not "Patron")
4. **Inherent Powers** - Built-in archetype abilities
5. **Boosts** - Enhancement powers (in `boost_sets/` directory)
6. **Incarnate Powers** - End-game progression powers

## Three-Phase Approach

### Phase 1: Mapping & Documentation

**Objective**: Create comprehensive reference documents for subsequent agents without hitting context limits.

**Strategy**: Sequential agent maps entire structure, commits findings incrementally to avoid context exhaustion.

#### Phase 1.1: Directory Structure Mapping

**Agent**: General-purpose exploration agent
**Output**: `.claude/docs/city-of-data-structure-map.md`

Document:
- Complete directory tree with file counts
- Top-level directory purposes:
  - `powers/` - Player and NPC power definitions
  - `boost_sets/` - Enhancement/IO sets (ALL player-relevant!)
  - `archetypes/` - Player archetype definitions
  - `entities/` - Character entities (likely NPC-heavy)
  - `entity_tags/` - Entity classification
  - `exclusion_groups/` - Power exclusion rules
  - `recharge_groups/` - Recharge mechanics
  - `tables/` - Lookup tables
  - `tags/` - Tag definitions
- File type inventory (JSON structure patterns)
- Size analysis (total files, player vs NPC ratio estimate)

**Context Management**:
- Commit findings every 15-20 minutes
- Update TodoWrite checklist after each directory
- Use `just ucp "progress: mapped {directory}"` frequently

#### Phase 1.2: Schema Documentation

**Agent**: Same agent continues
**Output**: `.claude/docs/city-of-data-schema-reference.md`

Document JSON schemas for:
- `powers/index.json` - Master power category index
- `powers/{category}/index.json` - Category-level index
- `powers/{category}/{powerset}/index.json` - Powerset definitions
- `archetypes/{name}/index.json` - Archetype powerset mappings
- `boost_sets/index.json` - Enhancement set index
- `boost_sets/{set}/index.json` - Individual enhancement sets

For each schema, capture:
- **Purpose**: What this file represents
- **Structure**: Field definitions and data types
- **Relationships**: How it links to other files
- **Player Relevance**: Indicators of player vs NPC data
- **Example**: Actual snippet from file

#### Phase 1.3: Player Power Identification

**Agent**: Same agent continues
**Output**: `.claude/docs/player-power-identification.md`

Document filtering rules across 3 layers:

**Layer 1 - Explicit Categories** (from `powers/index.json`):
- ✅ `Pool.*` - All pool powers
- ✅ `Epic.*` - Epic power pools
- ✅ `Inherent.*` - Inherent abilities
- ✅ `Incarnate.*` - Incarnate powers
- ❓ Other categories requiring review

**Layer 2 - Archetype-Linked Categories**:
- Analyze all `archetypes/*/index.json` files
- Build map: `archetype → primary_categories + secondary_categories`
- Mark categories referenced by player archetypes as "keep"

**Layer 3 - Special Directories**:
- `boost_sets/` - Keep ALL (all enhancement data is player-relevant)
- `archetypes/` - Keep ALL (defines player archetypes)
- Other directories as discovered

**Exclusion Patterns**:
- Categories matching: `Villain_*`, `NPC_*`, `Critter_*`
- Entity-linked powers without archetype association
- Temporary/event-specific powers (review case-by-case)

#### Phase 1.4: Pruning Strategy

**Agent**: Same agent finalizes
**Output**: `.claude/docs/city-of-data-pruning-strategy.md`

Create actionable plan:
- Directory processing order
- Filter rules per directory
- Output directory structure
- Manifest format specification

**Deliverables Checklist** (TodoWrite required):
- [ ] Complete `city-of-data-structure-map.md`
- [ ] Document schemas in `city-of-data-schema-reference.md`
- [ ] Analyze player categories in `player-power-identification.md`
- [ ] Create `city-of-data-pruning-strategy.md`
- [ ] Update `progress.json` with Epic 2.5 tasks

### Phase 2: Multi-Layered Filtering Execution

**Objective**: Execute pruning using documented strategy with parallel agents.

**Strategy**: Deploy specialized agents for each major directory, working in parallel.

#### Agent Assignments

**Agent 1: Archetypes Processor**
- Input: `archetypes/` directory
- Process: Copy entire directory (all player-relevant)
- Output: `filtered_data/archetypes/` + manifest entries
- Build archetype→category mapping for Layer 2 filtering

**Agent 2: Powers Processor**
- Input: `powers/` directory
- Process: Apply Layer 1 (explicit categories) + Layer 2 (archetype-linked)
- Output: `filtered_data/powers/` + manifest entries
- Use mapping from Agent 1 for Layer 2 decisions

**Agent 3: Boost Sets Processor**
- Input: `boost_sets/` directory
- Process: Copy entire directory (all player-relevant)
- Output: `filtered_data/boost_sets/` + manifest entries

**Agent 4: Tables & Metadata Processor**
- Input: `tables/`, `tags/`, `recharge_groups/`, `exclusion_groups/`
- Process: Analyze for player relevance (case-by-case)
- Output: Selected files to `filtered_data/` + manifest entries

**Coordination**:
- Agents 1, 3, 4 can run fully in parallel (independent)
- Agent 2 needs mapping from Agent 1 (sequential dependency)
- Launch sequence: Start 1, 3, 4 together → Wait for Agent 1 → Start Agent 2

#### Filtering Logic

**Layer 1 Filter** (Explicit Categories):
```python
def is_explicit_player_category(category_name: str) -> bool:
    patterns = ["Pool", "Epic", "Inherent", "Incarnate"]
    return any(pattern in category_name for pattern in patterns)
```

**Layer 2 Filter** (Archetype-Linked):
```python
def is_archetype_linked_category(category_name: str, archetype_map: dict) -> bool:
    # Check if category appears in any archetype's primary/secondary sets
    for archetype, data in archetype_map.items():
        if category_name in data['primary'] or category_name in data['secondary']:
            return True
    return False
```

**Layer 3 Filter** (Special Directories):
```python
def is_special_directory(directory: str) -> bool:
    keep_all = ["boost_sets", "archetypes"]
    return directory in keep_all
```

### Phase 3: Validation & Manifest Creation

**Objective**: Verify filtering results and create comprehensive tracking manifest.

**Strategy**: Single synthesis agent validates outputs and creates final manifest.

#### Validation Steps

1. **File Count Verification**:
   - Count total files in `filtered_data/`
   - Compare against expected player power count
   - Flag significant deviations for review

2. **Category Completeness**:
   - Verify all known player archetypes have primary/secondary sets
   - Verify Pool, Epic, Inherent, Incarnate categories present
   - Verify boost_sets directory complete

3. **Schema Integrity**:
   - Test that index.json files are valid
   - Verify cross-references resolve correctly
   - Check for broken links

4. **Manual Review Checklist**:
   - Sample random powersets for player/NPC classification accuracy
   - Review edge cases documented in Phase 1
   - Validate ambiguous categories

#### Manifest Format

**Output**: `filtered_data/manifest.json`

```json
{
  "metadata": {
    "source_dir": "raw_data_homecoming-20250617_6916",
    "filtered_date": "2025-11-01",
    "total_source_files": 12345,
    "kept_files": 4567,
    "excluded_files": 7778,
    "strategy_version": "v1.0",
    "epic": "2.5",
    "github_issue": "#XXX"
  },
  "filter_rules": {
    "explicit_categories": ["Pool", "Epic", "Inherent", "Incarnate"],
    "archetype_linked": ["Tanker_Melee", "Blaster_Ranged", ...],
    "special_directories": ["boost_sets", "archetypes"],
    "exclusion_patterns": ["Villain_*", "NPC_*", "Critter_*"]
  },
  "kept_files": [
    {
      "source": "powers/Pool.Fighting/index.json",
      "reason": "explicit_category:Pool",
      "layer": 1,
      "copied_to": "filtered_data/powers/Pool.Fighting/index.json",
      "size_bytes": 12345
    },
    {
      "source": "powers/Tanker_Melee.Super_Strength/index.json",
      "reason": "archetype_linked:Tanker",
      "layer": 2,
      "copied_to": "filtered_data/powers/Tanker_Melee.Super_Strength/index.json",
      "size_bytes": 8765
    }
  ],
  "excluded_files": [
    {
      "source": "powers/Villain_NPC.Hellion_Gunner/index.json",
      "reason": "npc_only",
      "pattern_match": "Villain_*"
    }
  ],
  "statistics": {
    "by_layer": {
      "layer_1_explicit": 250,
      "layer_2_archetype": 450,
      "layer_3_special": 3867
    },
    "by_directory": {
      "powers": 700,
      "boost_sets": 3500,
      "archetypes": 350,
      "tables": 17
    }
  },
  "validation": {
    "all_archetypes_present": true,
    "pool_powers_present": true,
    "epic_powers_present": true,
    "boost_sets_complete": true,
    "schema_valid": true,
    "manual_review_required": [
      "Category: Temporary_Powers - needs player/NPC classification"
    ]
  }
}
```

## Tools & Configuration

### Just Commands

**New Command**: `just jq`
```bash
# JSON processing with jq
jq *args:
    @command -v jq >/dev/null 2>&1 || (echo "❌ jq not installed. Install with: brew install jq" && exit 1)
    @jq {{args}}
```

**Usage Examples**:
```bash
# List power categories
just jq '.power_categories | keys' powers/index.json

# Extract archetype primary sets
just jq '.primary_sets' archetypes/Blaster/index.json

# Count files in directory
fd -t f . boost_sets | wc -l
```

### Required Tools Verification

Before starting execution, verify:
- ✅ `jq` - JSON processing (via `just jq`)
- ✅ `fd` - Fast file finding (existing in project)
- ✅ `rg` - Ripgrep for pattern matching (existing in project)
- ✅ `python3` - For complex processing logic (existing in project)
- ✅ `just` - Command runner (existing in project)

## Progress Tracking

### Epic Definition

**Epic 2.5**: City of Data Import Preparation

Tasks:
1. **Task 2.5.1**: Create City of Data pruning plan ✅ (this document)
2. **Task 2.5.2**: Phase 1 - Map and document City of Data structure
3. **Task 2.5.3**: Phase 2 - Execute multi-layered filtering
4. **Task 2.5.4**: Phase 3 - Validate and create manifest
5. **Task 2.5.5**: Integrate filtered data into import pipeline

### GitHub Issues

To be created:
- Epic issue: "Epic 2.5: City of Data Import Preparation"
- Task issues for each phase
- Link to existing Epic 2 parent

### Progress.json Updates

```json
"epic2_5": {
  "name": "City of Data Import Preparation",
  "status": "in_progress",
  "progress": 10,
  "tasks": [
    "✅ Task 2.5.1: Create comprehensive pruning plan",
    "📋 Task 2.5.2: Phase 1 - Map and document structure",
    "📋 Task 2.5.3: Phase 2 - Execute filtering",
    "📋 Task 2.5.4: Phase 3 - Validate and create manifest",
    "📋 Task 2.5.5: Integrate filtered data"
  ],
  "github_issues": [
    "#XXX Epic 2.5: City of Data Import Preparation"
  ]
}
```

## Agent Prompt Template

**Location**: `.claude/prompts/city-of-data-mapping-agent.md`

```markdown
# City of Data Mapping Agent - Phase 1

## Mission
Map and document the structure of City of Data `raw_data_homecoming-20250617_6916`
to prepare for player power filtering.

## Critical: Context Limits Management

**You MUST avoid context exhaustion**:
1. Commit findings to documentation files every 15-20 minutes
2. Update TodoWrite checklist after completing each directory
3. Use `just ucp "progress: mapped {directory}"` after each commit
4. Reference CLAUDE.md for project patterns
5. Keep sessions focused - use `/clear` between major milestones

## Available Tools

- `just jq <args>` - JSON processing (REQUIRED for JSON analysis)
- `fd <pattern>` - Fast file finding
- `rg <pattern>` - Pattern matching in files
- `python3` - Complex analysis scripts

## Deliverables

Create these documentation files in `.claude/docs/`:

### 1. city-of-data-structure-map.md
- Complete directory tree with file counts
- Top-level directory purposes
- File type inventory
- Size analysis

### 2. city-of-data-schema-reference.md
For each key JSON file type:
- Purpose
- Structure (fields, types)
- Relationships to other files
- Player relevance indicators
- Example snippet

### 3. player-power-identification.md
- Layer 1: Explicit player categories
- Layer 2: Archetype-linked categories
- Layer 3: Special directories
- Exclusion patterns for NPC-only data

### 4. city-of-data-pruning-strategy.md
- Directory processing order
- Filter rules per directory
- Output structure specification
- Manifest format

## TodoWrite Checklist (REQUIRED)

You MUST create and maintain TodoWrite todos for:
- [ ] Map directory structure
- [ ] Document JSON schemas
- [ ] Identify player power categories
- [ ] Create pruning strategy
- [ ] Update progress.json

Mark each item in_progress when starting, completed when done.

## Approach

1. **Start**: `ls -lh` on top-level directory
2. **Iterate**: For each subdirectory:
   - List contents with file counts
   - Sample 2-3 representative JSON files with `just jq`
   - Document structure and purpose
   - **COMMIT** findings to documentation file
   - Update TodoWrite checklist
3. **Analyze**: Identify player vs NPC patterns
4. **Finalize**: Create pruning strategy document
5. **Update**: Update `.claude/state/progress.json` with Epic 2.5

## Example Commands

```bash
# List top-level directories
ls -lh raw_data_homecoming-20250617_6916/

# Count files in powers directory
fd -t f . raw_data_homecoming-20250617_6916/powers | wc -l

# Examine power categories index
just jq '.power_categories | keys' raw_data_homecoming-20250617_6916/powers/index.json

# Sample archetype structure
just jq '.' raw_data_homecoming-20250617_6916/archetypes/Blaster/index.json | head -50

# Find all index.json files
fd -t f 'index.json' raw_data_homecoming-20250617_6916/
```

## Reporting

After completing each deliverable:
1. Commit with `just ucp "docs: completed {deliverable}"`
2. Update TodoWrite marking task completed
3. Report completion to user with summary

Final report should include:
- Total directories mapped
- Total files analyzed
- Key findings (player vs NPC ratio estimate)
- Recommended next steps for Phase 2
```

## Execution Plan

### Phase 1 Execution (Sequential)

1. **Start mapping agent** (use Task tool with subagent_type=Explore)
2. Agent follows template prompt above
3. Agent commits findings incrementally
4. Human reviews Phase 1 documentation
5. Approve/adjust strategy before Phase 2

### Phase 2 Execution (Parallel)

1. Launch Agents 1, 3, 4 in parallel (use single message with multiple Task calls)
2. Wait for Agent 1 completion (provides archetype mapping)
3. Launch Agent 2 (Powers processor, uses Agent 1 output)
4. Monitor all agents, resolve blockers
5. Collect outputs in `filtered_data/`

### Phase 3 Execution (Sequential)

1. Launch synthesis agent
2. Validate filtering results
3. Create manifest.json
4. Report summary with statistics
5. Request human review of edge cases

## Success Criteria

- [ ] All 4 Phase 1 documentation files created and committed
- [ ] `filtered_data/` directory contains only player-relevant powers
- [ ] Manifest.json provides complete tracking of kept/excluded files
- [ ] All known player archetypes have powersets present
- [ ] Pool, Epic, Inherent, Incarnate categories complete
- [ ] Boost_sets directory fully copied
- [ ] Validation passes all automated checks
- [ ] Manual review of ambiguous cases completed
- [ ] Progress.json updated with Epic 2.5 completion
- [ ] GitHub issues created and linked

## Risk Mitigation

**Risk**: Agent hits context limits during mapping
**Mitigation**: Require commits every 15-20 minutes, TodoWrite tracking

**Risk**: Over-aggressive filtering removes player powers
**Mitigation**: Iterative approach, Layer 2 catches archetype-linked categories

**Risk**: Under-aggressive filtering includes NPC powers
**Mitigation**: Layer 1 explicit categories + exclusion patterns, manual review

**Risk**: Broken cross-references after filtering
**Mitigation**: Phase 3 validation checks schema integrity

**Risk**: Missing edge case categories
**Mitigation**: Phase 1 comprehensive mapping, manual review checklist

## Next Steps After Completion

1. Review manifest.json for accuracy
2. Run sample queries on filtered data to verify completeness
3. Update import pipeline to use `filtered_data/` directory
4. Create Epic 2.6: Import filtered City of Data into database
5. Implement import scripts for each data type
6. Validate imported data matches game mechanics

---

**Plan Status**: ✅ Complete - Ready for `/superpowers:write-plan`
**Epic**: 2.5
**Created By**: Claude Code (Brainstorming Skill)
**Date**: 2025-11-01
**Estimated Effort**: 3-5 agent sessions across all phases
