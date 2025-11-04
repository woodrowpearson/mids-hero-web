# City of Data Filtering Results

> **Completed:** 2025-11-01
> **Updated:** 2025-11-04 (Manual NPC cleanup - boss, lt, and minion archetypes)
> **Epic:** 2.5
> **GitHub Issue:** #300

## Summary

Successfully pruned City of Data raw dataset from 43,233 files to 6,363 player-relevant files (14.7% of source data).

**Manual Cleanup Applied:** Removed 115 NPC-related files through three cleanup passes:
- **Pass 1 (2025-11-01):** 79 files (27 boss_* archetypes, 27 boss_* tables, 9 exclusion_groups, 16 temporary/visual tags)
- **Pass 2 (2025-11-04):** 14 files (7 lt_* archetypes, 7 lt_* tables)
- **Pass 3 (2025-11-04):** 22 files (11 NPC minion_* archetypes, 11 NPC minion_* tables)

## Filtering Statistics

**Source:** `raw_data_homecoming-20250617_6916`
**Output:** `filtered_data/`

**Total files:**
- Source: 43,233 files
- Kept: 6,363 files (14.7%)
- Excluded: 167 power categories + 115 NPC/metadata files
- Reduction: 85.3% reduction in dataset size

**By Layer:**
- Layer 1 (Explicit categories): 2,058 files
  - Pool powers (fighting, leadership, speed, etc.)
  - Epic powers
  - Inherent powers
  - Incarnate powers (3 categories)
- Layer 2 (Archetype-linked): 3,717 files
  - Primary/secondary powersets for all player archetypes
- Layer 3 (Special directories): 589 files (reduced from 704 after three manual cleanup passes)
  - Archetypes directory (player archetypes + player pet archetypes only)
  - Complete boost_sets directory
  - Selected metadata directories

**By Directory:**
- archetypes/: 21 files (15 player + 5 player pet/summon archetypes)
  - Player archetypes: All 15 City of Heroes archetypes
  - Player pets: minion_controllerpets, minion_henchman, minion_henchman_small, minion_pets, minion_oilslicktarget
  - Removed: 27 boss_* + 7 lt_* + 11 NPC minion_* = 45 total NPC archetype files
- boost_sets/: 228 files (100% kept - all enhancement sets)
- powers/: 5,773 files (36 categories filtered from ~200+ categories)
- tables/: 20 files (selective metadata - player archetypes only)
  - Removed: 27 boss_* + 7 lt_* + 11 NPC minion_* = 45 total NPC table files
- tags/: 300 files (selective - removed 16 temporary/visual tags)
- exclusion_groups/: 16 files (selective - removed 9 NPC-related groups)
- recharge_groups/: 4 files (selective - power mechanics)

## Validation Results

**All validation checks passed:**

### Archetypes
✅ All 15 player archetypes present:
- Blaster, Controller, Defender, Scrapper, Tanker
- Brute, Stalker, Mastermind, Dominator, Corruptor
- Peacebringer, Warshade, Arachnos Soldier, Arachnos Widow, Sentinel

**Player Pet Archetypes:** 5 minion_* files retained for player-summoned pets:
- minion_controllerpets (Controller pets: Fire Imps, etc.)
- minion_henchman (Mastermind primary henchmen)
- minion_henchman_small (Mastermind small henchmen)
- minion_pets (Generic player summons)
- minion_oilslicktarget (Oil Slick Arrow from Trick Arrow power)

**Removed NPC Files:** 45 archetype files + 45 table files = 90 NPC files total:
- 27 boss_* files (Pass 1 - boss/elite boss/archvillain NPCs)
- 7 lt_* files (Pass 2 - lieutenant NPCs)
- 11 minion_* files (Pass 3 - enemy minions: grunt, practice, turret, swarm, monument, unkillable, praetorian, fire, small variants)

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
