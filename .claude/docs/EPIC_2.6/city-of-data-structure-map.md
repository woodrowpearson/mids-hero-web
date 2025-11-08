# City of Data Structure Map

> **Generated:** 2025-11-01
> **Source:** raw_data_homecoming-20250617_6916
> **Purpose:** Complete directory mapping for player power filtering

## Overview

Total files: 43,224

## Top-Level Directory Structure

### archetypes/
**Purpose:** Player archetype definitions (Blaster, Tanker, Controller, etc.)
**Files:** 66
**Player Relevant:** YES - Keep all
**Rationale:** All archetype definitions are player-relevant

### boost_sets/
**Purpose:** Enhancement/IO set definitions
**Files:** 228
**Player Relevant:** YES - Keep all
**Rationale:** All enhancements are player-relevant

### entities/
**Purpose:** Character entities (NPCs and players)
**Files:** 8,707
**Player Relevant:** EXCLUDE - NPC-heavy
**Rationale:** Entity data not required for build planner calculations

### entity_tags/
**Purpose:** Tags for entities
**Files:** 28
**Player Relevant:** EXCLUDE - NPC-related metadata
**Rationale:** Linked to entity system which is NPC-heavy

### exclusion_groups/
**Purpose:** Power exclusion group definitions
**Files:** 25
**Player Relevant:** REVIEW - May affect power mechanics
**Rationale:** Could define mutual exclusion rules for player powers

### powers/
**Purpose:** All power category definitions
**Files:** 33,775
**Player Relevant:** PARTIAL - Requires filtering
**Rationale:** Mix of player and NPC powers, needs 3-layer filtering

### recharge_groups/
**Purpose:** Recharge time groupings
**Files:** 4
**Player Relevant:** REVIEW - May affect power mechanics
**Rationale:** Could be needed for power calculations

### tables/
**Purpose:** Lookup tables and reference data
**Files:** 65
**Player Relevant:** REVIEW - May contain player-relevant lookups
**Rationale:** Tables may be referenced by power calculations

### tags/
**Purpose:** Power tags and metadata
**Files:** 316
**Player Relevant:** REVIEW - May be referenced by player powers
**Rationale:** Tags may classify player powers

## Top-Level JSON Files

### all_power_search.json
**Size:** 2.8M
**Purpose:** Search index for all powers
**Player Relevant:** PARTIAL - Contains both player and NPC powers

### at_power_search.json
**Size:** 572K
**Purpose:** Archetype-specific power search index
**Player Relevant:** YES - Player-focused search index

### attribute_names.json
**Size:** 50K
**Purpose:** Power attribute name definitions
**Player Relevant:** YES - Required for power mechanics

### boostset_groups.json
**Size:** 77K
**Purpose:** Enhancement set grouping data
**Player Relevant:** YES - Enhancement-related

### display_names.json
**Size:** 8.6K
**Purpose:** Display name mappings
**Player Relevant:** YES - UI-related

### entity_names.json
**Size:** 604K
**Purpose:** Entity name mappings
**Player Relevant:** EXCLUDE - Entity-related

### powers_by_at.json
**Size:** 27K
**Purpose:** Powers organized by archetype
**Player Relevant:** YES - Player archetype power mapping

### set_bonuses.json
**Size:** 345K
**Purpose:** Enhancement set bonus definitions
**Player Relevant:** YES - Enhancement-related

### set_conversions.json
**Size:** 37K
**Purpose:** Enhancement set conversion rules
**Player Relevant:** YES - Enhancement-related

## Summary Statistics

**Total Directories:** 9
**Total Files:** 43,224

**High Priority (Keep All):**
- archetypes/ (66 files)
- boost_sets/ (228 files)

**Requires Filtering:**
- powers/ (33,775 files) - Largest directory, needs 3-layer filtering

**For Review:**
- tables/ (65 files)
- tags/ (316 files)
- exclusion_groups/ (25 files)
- recharge_groups/ (4 files)

**Exclude:**
- entities/ (8,707 files)
- entity_tags/ (28 files)

## Next Steps

1. Analyze powers/index.json schema
2. Map archetype structure to identify primary/secondary powersets
3. Define Layer 1/2/3 filtering rules
4. Create archetype-to-category mapping
