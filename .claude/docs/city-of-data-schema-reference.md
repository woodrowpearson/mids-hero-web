# City of Data Schema Reference

> **Generated:** 2025-11-01
> **Purpose:** JSON schema documentation for filtering logic

## Overview

City of Data uses a hierarchical directory structure where each power category is a subdirectory containing powersets, which in turn contain individual powers.

**Total Power Categories:** 205

## Structure Hierarchy

```
powers/
├── {category}/               # Power category (e.g., "pool", "epic", "blaster_ranged")
│   ├── index.json           # Category metadata and powerset list
│   └── {powerset}/          # Individual powerset (e.g., "fighting", "fire_blast")
│       ├── index.json       # Powerset metadata and power list
│       └── {power}.json     # Individual power definition
```

## powers/{category}/index.json

**Purpose:** Defines a power category and lists all powersets within it

**Structure:**
```json
{
  "name": "Category_Name",
  "display_name": "Human Readable Name",
  "source_file": "DEFS/POWERS/...",
  "archetypes": ["archetype1", "archetype2"],
  "powerset_names": ["category.powerset1", "category.powerset2"],
  "powerset_display_names": ["Display 1", "Display 2"],
  "powersets_with_requirements": ["category.powerset_needing_prereq"],
  "display_help": "string or null",
  "display_short_help": "string or null"
}
```

**Key Fields:**
- `name`: Internal category identifier (e.g., "Pool", "Blaster_Ranged")
- `display_name`: User-facing category name
- `archetypes`: List of archetypes that can access this category
- `powerset_names`: Fully qualified powerset identifiers
- `powerset_display_names`: User-facing powerset names

**Player Relevance Indicators:**
- Categories with `archetypes` containing player archetypes → Player-relevant
- Categories named "Pool", "Epic", "Inherent", "Incarnate" → Always player-relevant
- Categories without archetype list → Likely NPC-only

**Example - Pool Powers:**
```json
{
  "name": "Pool",
  "display_name": "Pool",
  "source_file": "DEFS/POWERS/POOL.CATEGORIES",
  "archetypes": [
    "arachnos_soldier",
    "arachnos_widow",
    "blaster",
    "brute",
    "controller",
    "corruptor",
    "defender",
    "dominator",
    "mastermind",
    "peacebringer",
    "scrapper",
    "sentinel",
    "stalker",
    "tanker",
    "warshade"
  ],
  "powerset_names": [
    "pool.experimentation",
    "pool.fighting",
    "pool.fitness",
    "pool.flight",
    "pool.force_of_will",
    "pool.gadgetry",
    "pool.invisibility",
    "pool.leadership",
    "pool.leaping",
    "pool.manipulation",
    "pool.medicine",
    "pool.sorcery",
    "pool.speed",
    "pool.teleportation",
    "pool.utility_belt"
  ],
  "powerset_display_names": [
    "Experimentation",
    "Fighting",
    "Fitness",
    "Flight",
    "Force of Will",
    "Gadgetry",
    "Concealment",
    "Leadership",
    "Leaping",
    "Presence",
    "Medicine",
    "Sorcery",
    "Speed",
    "Teleportation",
    "Utility Belt"
  ],
  "powersets_with_requirements": [
    "pool.utility_belt"
  ]
}
```

## Layer 1: Explicit Player Categories

### Pool Powers
**Directory:** `powers/pool/`
**Powersets:** 15 pool powersets
**All Player Archetypes:** Yes
**Keep:** Entire directory

### Epic Powers
**Directory:** `powers/epic/`
**Purpose:** Patron/Epic power pools unlocked at high level
**Keep:** Entire directory

### Inherent Powers
**Directory:** `powers/inherent/`
**Purpose:** Built-in archetype abilities
**Keep:** Entire directory

### Incarnate Powers
**Directories:** `powers/incarnate/`, `powers/incarnate_alphastrike/`, `powers/incarnate_i20/`
**Purpose:** End-game incarnate abilities
**Keep:** All incarnate directories

## Layer 2: Archetype-Linked Categories

Categories referenced in archetype primary/secondary sets. Examples:

### Archetype Naming Pattern
- `blaster_ranged` → Blaster primary sets
- `blaster_support` → Blaster secondary sets
- `brute_defense` → Brute primary sets
- `brute_melee` → Brute secondary sets
- `controller_buff` → Controller secondary sets
- `controller_control` → Controller primary sets
- `corruptor_buff` → Corruptor primary sets
- `corruptor_ranged` → Corruptor secondary sets

**Identification:** Categories containing archetype names (blaster, brute, controller, corruptor, defender, dominator, mastermind, scrapper, sentinel, stalker, tanker, peacebringer, warshade, arachnos_soldier, arachnos_widow)

## Exclusion Patterns

### NPC-Only Indicators
Categories named after enemy groups are NPC-only:
- `5thcolumn` → 5th Column enemy group
- `animusarcana` → Animus Arcana enemy group
- `apparitions` → Apparitions enemy group
- `banishedpantheon` → Banished Pantheon enemy group
- `blackknights` → Black Knights enemy group
- `carnival` → Carnival of Shadows enemy group
- `circleofthorns` → Circle of Thorns enemy group
- `clockwork` → Clockwork enemy group
- `council` → Council enemy group

**Pattern:** If category name matches known enemy group → EXCLUDE

### Base Powers
Categories for base building (not player character powers):
- `base_aux` → Base auxiliary systems
- `base_defenses` → Base defenses
- `base_fields` → Base force fields
- `base_traps` → Base traps

**Pattern:** Categories starting with `base_` → EXCLUDE

## Edge Cases

### Boosts
**Directory:** `powers/boosts/`
**Purpose:** Temporary buffs/debuffs
**Decision:** REVIEW - May include player temporary powers

### Arachnos Soldiers/Widows
**Directories:** `powers/arachnos_soldiers/`, `powers/arachnos_widow/`
**Purpose:** Player archetype powersets (Villain Epic Archetypes)
**Decision:** KEEP - Player archetypes

## archetypes/{name}.json

**Purpose:** Defines archetype characteristics, including primary/secondary power categories

**Structure:**
```json
{
  "name": "archetype_name",
  "display_name": "Archetype Display Name",
  "primary_category": "Category_Name",
  "secondary_category": "Category_Name",
  "epic_pool_category": null,
  "power_pool_category": null,
  "attrib_base": {...},
  "attrib_max": {...},
  // Many other attribute fields
}
```

**Key Fields for Filtering:**
- `name`: Archetype identifier (e.g., "blaster", "tanker")
- `primary_category`: Power category for primary powersets (e.g., "Blaster_RANGED")
- `secondary_category`: Power category for secondary powersets (e.g., "Blaster_SUPPORT")

**Player Archetypes:**
- blaster, controller, defender, scrapper, tanker
- brute, stalker, mastermind, dominator, corruptor
- peacebringer, warshade, arachnos_soldier, arachnos_widow, sentinel

**Total Player Archetypes:** 15
**Total Unique Categories from Archetypes:** 30

**Example - Blaster:**
```json
{
  "name": "Class_Blaster",
  "display_name": "Blaster",
  "primary_category": "Blaster_RANGED",
  "secondary_category": "Blaster_SUPPORT",
  "epic_pool_category": null,
  "power_pool_category": null
}
```

**Usage for Filtering:**
Load all player archetype files, extract primary_category and secondary_category values, create set of Layer 2 categories to keep.

**Mapping Output:** See `.claude/docs/archetype-category-mapping.json`

## Validation Strategy

For each power category:
1. Check if category name is "pool", "epic", "inherent", or contains "incarnate" → KEEP (Layer 1)
2. Check if category in archetype mapping (primary/secondary categories) → KEEP (Layer 2)
3. Check if category name matches exclusion patterns (enemy groups, base_*) → EXCLUDE
4. Otherwise → FLAG FOR REVIEW
