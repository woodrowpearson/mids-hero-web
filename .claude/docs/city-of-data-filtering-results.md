# City of Data Filtering Results

> **Completed:** 2025-11-01
> **Epic:** 2.5
> **GitHub Issue:** #300

## Summary

Successfully pruned City of Data raw dataset from 43,233 files to 6,479 player-relevant files (15% of source data).

## Filtering Statistics

**Source:** `raw_data_homecoming-20250617_6916`
**Output:** `filtered_data/`

**Total files:**
- Source: 43,233 files
- Kept: 6,479 files (15%)
- Excluded: 167 categories
- Reduction: 85% reduction in dataset size

**By Layer:**
- Layer 1 (Explicit categories): 2,058 files
  - Pool powers (fighting, leadership, speed, etc.)
  - Epic powers
  - Inherent powers
  - Incarnate powers (3 categories)
- Layer 2 (Archetype-linked): 3,717 files
  - Primary/secondary powersets for all player archetypes
- Layer 3 (Special directories): 704 files
  - Complete archetypes directory
  - Complete boost_sets directory
  - Selected metadata directories

**By Directory:**
- archetypes/: 66 files (15 player + 50 NPC archetypes - all kept)
- boost_sets/: 228 files (100% kept - all enhancement sets)
- powers/: 5,775 files (36 categories filtered from ~200+ categories)
- tables/: 65 files (selective - lookup tables)
- tags/: 316 files (selective - tag metadata)
- exclusion_groups/: 25 files (selective - power mechanics)
- recharge_groups/: 4 files (selective - power mechanics)

## Validation Results

**All validation checks passed:**

### Archetypes
✅ All 15 player archetypes present:
- Blaster, Controller, Defender, Scrapper, Tanker
- Brute, Stalker, Mastermind, Dominator, Corruptor
- Peacebringer, Warshade, Arachnos Soldier, Arachnos Widow, Sentinel

Note: 50 additional NPC archetypes were also kept (boss_*, lt_*, minion_* prefixes). These may be relevant for future features or can be filtered in a subsequent pass if needed.

### Power Categories
✅ All required power category patterns present:
- Pool powers: ✅ (fighting, leadership, speed, teleportation, etc.)
- Epic powers: ✅
- Inherent powers: ✅
- Incarnate powers: ✅ (incarnate, incarnate_alphastrike, incarnate_i20)

36 power categories kept from original dataset.

### Boost Sets
✅ Complete: 228 enhancement/IO set files

### Schema Integrity
✅ All 635 index.json files are valid JSON (no parse errors)

## Filter Rules Applied

### Layer 1: Explicit Categories
Categories with names matching:
- `*Pool*` → Player pool powers
- `*Epic*` → Player epic power pools
- `*Inherent*` → Player inherent abilities
- `*Incarnate*` → Player incarnate system powers

### Layer 2: Archetype-Linked
Categories referenced in archetype primary/secondary sets.

Source: `.claude/docs/archetype-category-mapping.json`

### Layer 3: Special Directories
Complete directory copies:
- `boost_sets/` → All enhancement sets (player-relevant)
- `archetypes/` → All archetype definitions
- Selected metadata directories (tables, tags, exclusion_groups, recharge_groups)

### Exclusion Patterns
Categories excluded if matching:
- `Villain_*` → NPC villain powers
- `NPC_*` → Explicit NPC designation
- `Critter_*` → NPC critter powers
- `Enemy_*` → NPC enemy powers

## Next Steps

See Task 2.5.5 (#305) for import pipeline integration.

The filtered dataset is ready to be integrated into the database import workflow.

## Files

- **Manifest:** `filtered_data/manifest.json`
- **Filtered Data:** `filtered_data/`
- **Validation Script:** `scripts/validate_filtered_data.py`
- **Filtering Scripts:**
  - `scripts/filter_archetypes.py` (Phase 2)
  - `scripts/filter_powers.py` (Phase 2)
  - `scripts/filter_boost_sets.py` (Phase 2)
  - `scripts/filter_metadata.py` (Phase 2)

## Manifest Contents

The `filtered_data/manifest.json` file contains:
- Complete metadata (source, date, counts, strategy version)
- Applied filter rules for all 3 layers
- Full list of kept files with reasons and layer assignments
- Full list of excluded files with reasons
- Statistics by layer and directory
- Validation results for all checks

This manifest provides a complete audit trail for the filtering process and can be used to verify data integrity during import.
