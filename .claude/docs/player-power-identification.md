# Player Power Identification Guide

> **Generated:** 2025-11-01
> **Purpose:** Define filtering rules for player vs NPC power classification

## Overview

City of Heroes has ~43,000 total files (including ~33,775 power files across 205 categories). Most are NPC-specific. This guide defines the 3-layer filtering approach to identify player-relevant powers.

## Layer 1: Explicit Player Categories

Categories with specific directory names are always player-relevant.

### Pool Powers
**Directory:** `powers/pool/`
**Powersets:** 15
**Archetype Access:** All player archetypes
**Powersets:**
- experimentation
- fighting
- fitness
- flight
- force_of_will
- gadgetry
- invisibility
- leadership
- leaping
- manipulation
- medicine
- sorcery
- speed
- teleportation
- utility_belt

**Decision:** KEEP entire directory

### Epic Powers
**Directory:** `powers/epic/`
**Powersets:** 81
**Archetype Access:** Various (unlocked at level 35+)
**Examples:**
- arctic_mastery
- blaster_dark_mastery
- controller_mace_mastery
- defender_fire_mastery
- dominator_soul_mastery
- mastermind_leviathan_mastery
- sentinel_psionic_mastery
- tank_psionic_mastery

**Decision:** KEEP entire directory

### Inherent Powers
**Directory:** `powers/inherent/`
**Powersets:** 2
**Archetype Access:** All
**Powersets:**
- fitness (inherent fitness pool)
- inherent (core inherent abilities)

**Decision:** KEEP entire directory

### Incarnate Powers
**Directories:**
- `powers/incarnate/`
- `powers/incarnate_alphastrike/`
- `powers/incarnate_i20/`

**Archetype Access:** Level 50+ end-game content
**Purpose:** Incarnate system abilities (Alpha, Judgement, Interface, etc.)

**Decision:** KEEP all incarnate directories

**Total Layer 1 Categories:** 4 directories (pool, epic, inherent, incarnate*)

## Layer 2: Archetype-Linked Categories

Categories referenced in player archetype primary/secondary power selections.

**Source:** `.claude/docs/archetype-category-mapping.json`

**Total Layer 2 Categories:** 30 unique categories

**Categories List:**
- Arachnos_Soldiers
- Blaster_RANGED
- Blaster_SUPPORT
- Brute_DEFENSE
- Brute_Melee
- Controller_BUFF
- Controller_CONTROL
- Corruptor_BUFF
- Corruptor_Ranged
- Defender_BUFF
- Defender_RANGED
- Dominator_Assault
- Dominator_CONTROL
- Mastermind_Buff
- Mastermind_Summon
- Peacebringer_Defensive
- Peacebringer_Offensive
- Scrapper_DEFENSE
- Scrapper_MELEE
- Sentinel_Defense
- Sentinel_Ranged
- Stalker_Defense
- Stalker_Melee
- Tanker_DEFENSE
- Tanker_MELEE
- Teamwork
- Training_Gadgets
- Warshade_Defensive
- Warshade_Offensive
- Widow_Training

**Naming Pattern:** `{Archetype}_{Type}` where Type is RANGED, MELEE, DEFENSE, BUFF, CONTROL, SUPPORT, etc.

**Decision:** KEEP all categories in the archetype mapping

## Layer 3: Special Directories

Entire directories that are always player-relevant regardless of filtering rules.

### boost_sets/
**Files:** 228
**Purpose:** All enhancement/IO set definitions
**Reason:** ALL enhancements are player powers
**Decision:** KEEP entire directory

### archetypes/
**Files:** 66
**Purpose:** Player archetype definitions
**Reason:** Defines all player archetypes
**Decision:** KEEP entire directory

**Total Layer 3 Special Directories:** 2

## Exclusion Patterns

Clear NPC-only indicators for automatic exclusion.

### Enemy Group Patterns
Categories named after known enemy groups are NPC-only:

**Examples:**
- `5thcolumn` → 5th Column enemy group
- `animusarcana` → Animus Arcana enemy group
- `apparitions` → Apparitions enemy group
- `banishedpantheon` → Banished Pantheon enemy group
- `blackknights` → Black Knights enemy group
- `blackwingindustries` → Black Wing Industries
- `carnival` → Carnival of Shadows enemy group
- `circleofthorns` → Circle of Thorns enemy group
- `clockwork` → Clockwork enemy group
- `council` → Council enemy group
- `coralax` → Coralax enemy group
- `devouring_earth` → Devouring Earth enemy group
- `freakshow` → Freakshow enemy group
- `goldbrickers` → Gold Brickers
- `knives_of_artemis` → Knives of Artemis
- `lost` → The Lost enemy group
- `malta` → Malta Group
- `nemesis` → Nemesis Army
- `outcasts` → Outcasts enemy group
- `praetorians` → Praetorian enemy groups
- `rikti` → Rikti enemy group
- `skulls` → Skulls gang
- `trolls` → Trolls gang
- `tsoo` → Tsoo enemy group
- `vahzilok` → Vahzilok enemy group
- `warriors` → Warriors gang

**Pattern:** If category matches known enemy group name → EXCLUDE

### Base Powers
Categories for base building (not player character powers):

- `base_aux` → Base auxiliary systems
- `base_defenses` → Base defenses
- `base_fields` → Base force fields
- `base_traps` → Base traps

**Pattern:** Categories starting with `base_` → EXCLUDE

### Boss/Lieutenant/Minion Archetypes
NPC archetype definitions in archetypes directory:

- `boss_*` → Boss-rank NPCs
- `lt_*` → Lieutenant-rank NPCs
- `minion_*` → Minion-rank NPCs

**Pattern:** Archetype files matching these patterns → EXCLUDE

## Edge Cases & Ambiguities

### Temporary Powers
**Directory:** `powers/temporary_powers/` (if exists)
**Decision:** REVIEW - Some may be player-accessible event powers

### Boosts
**Directory:** `powers/boosts/`
**Purpose:** Temporary buffs/debuffs
**Decision:** REVIEW - May include player temporary powers vs NPC-only buffs

### Challenge Powers
**Directory:** `powers/challenge_*`
**Purpose:** Challenge mode or special event powers
**Decision:** REVIEW - Depends on player accessibility

## Filtering Decision Matrix

```
FOR each power category:
  IF category name IN ["pool", "epic", "inherent"] → KEEP (Layer 1)
  ELSE IF category name CONTAINS "incarnate" → KEEP (Layer 1)
  ELSE IF category IN archetype_mapping.all_categories → KEEP (Layer 2)
  ELSE IF category matches exclusion patterns → EXCLUDE
  ELSE → FLAG FOR MANUAL REVIEW
END FOR

FOR each special directory:
  IF directory IN ["boost_sets", "archetypes"] → KEEP ALL (Layer 3)
END FOR
```

## Expected Results

**Layer 1 (Explicit):** ~100 categories
- pool: 1 category with 15 powersets
- epic: 1 category with 81 powersets
- inherent: 1 category with 2 powersets
- incarnate*: 3 categories

**Layer 2 (Archetype-linked):** 30 categories
- All primary/secondary categories from 15 player archetypes

**Layer 3 (Special):** 2 directories
- boost_sets/: 228 files
- archetypes/: 66 files (15 player, 51 NPC)

**Excluded:** ~170+ categories (enemy groups, base powers, etc.)

**Total Player-Relevant Categories:** ~34 power categories + 2 special directories

**File Reduction:** From 43,224 total files to approximately 1,000-2,000 player-relevant files (estimated 95%+ reduction)
