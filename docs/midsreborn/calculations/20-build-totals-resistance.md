# Build Totals - Resistance

## Overview
- **Purpose**: Aggregate typed resistance values from all sources and enforce archetype-specific resistance caps for final build totals display
- **Used By**: Build statistics, character sheet, survivability analysis, build comparison
- **Complexity**: Medium
- **Priority**: CRITICAL
- **Status**: ✅ Depth Complete (Milestone 3)

## MidsReborn Implementation

### Primary Location
- **File**: `Core/Base/Data_Classes/Character.cs` - `TotalStatistics` class with `Res[]` array
- **Related Files**:
  - `Core/Statistics.cs` - `DamageResistance()` method for capped/uncapped display
  - `Core/Base/Data_Classes/Archetype.cs` - `ResCap` property per archetype
  - `Core/Utils/Helpers.cs` - `GeneratedStatData()` for resistance display formatting
  - `Forms/WindowMenuItems/frmTotalsV2.cs` - UI display of resistance totals

[... keeping existing breadth content sections 1-5 ...]

---

## SECTION 1: Detailed Resistance Aggregation Algorithm

### Complete Resistance Calculation Process

```
BUILD_TOTALS_RESISTANCE_CALCULATION(character):
    """
    Aggregate all resistance sources and apply archetype-specific caps

    Process:
    1. Initialize resistance arrays (uncapped and capped)
    2. Aggregate from all active powers
    3. Aggregate from set bonuses
    4. Aggregate from global IOs
    5. Aggregate from incarnate powers
    6. Apply archetype resistance caps
    7. Store both uncapped and capped values for display

    Key Difference from Defense:
    - Defense uses "highest wins" for typed vs positional
    - Resistance uses SIMPLE ADDITION (all sources stack)
    - Resistance has HARD CAPS per archetype (75%, 85%, 90%)
    """

    # Step 1: Initialize resistance storage
    # MidsReborn uses float arrays indexed by damage type enum
    INITIALIZE_RESISTANCE_ARRAYS:
        Totals.Res = new float[Enums.eDamage.Length]  # Uncapped values
        TotalsCapped.Res = new float[Enums.eDamage.Length]  # Capped values

        # Initialize all 8 typed resistance values to 0.0
        FOR i = 0 TO 8:  # Smashing through Psionic
            Totals.Res[i] = 0.0
            TotalsCapped.Res[i] = 0.0

        # NOTE: Resistance does NOT use positional types
        # Only typed damage: Smashing, Lethal, Fire, Cold, Energy, Negative, Toxic, Psionic

    # Step 2: Aggregate resistance from active powers
    # Powers include toggles, auto powers, and active click buffs
    AGGREGATE_POWER_RESISTANCE:
        FOR each power_entry IN character.CurrentBuild.Powers:
            IF NOT power_entry.StatInclude:
                # Power is disabled/not active - skip it
                CONTINUE

            power = power_entry.Power

            # Process each effect in the power
            FOR each effect IN power.Effects:
                IF effect.EffectType == Enums.eEffectType.Resistance:
                    # Extract resistance value and damage type
                    damage_type_index = effect.DamageType  # 1-8 for typed damage
                    magnitude = effect.Magnitude  # Resistance value (e.g., 0.30 for 30%)

                    # Apply archetype modifier (AT scaling)
                    # Example: Tanker gets 1.0x, Scrapper gets 0.75x
                    at_modifier = character.Archetype.ResistanceMod
                    scaled_magnitude = magnitude * at_modifier

                    # Apply enhancement value from slotted enhancements
                    # This is already calculated in power enhancement processing
                    enhanced_magnitude = scaled_magnitude * power.EnhancementMultiplier

                    # Add to uncapped total (ADDITIVE stacking)
                    Totals.Res[damage_type_index] += enhanced_magnitude

        # Example Power: Invulnerability/Temp Invulnerability
        # Base: 30% S/L resistance
        # AT Mod (Tanker): 1.0
        # Enhancements: 3× Resistance IOs (+95% total)
        # Enhanced: 30% × 1.0 × (1 + 0.95) = 58.5% S/L
        # Adds to Totals.Res[Smashing] and Totals.Res[Lethal]

    # Step 3: Aggregate resistance from set bonuses
    # Set bonuses are ALWAYS active (no on/off toggle)
    AGGREGATE_SET_BONUS_RESISTANCE:
        set_bonuses = character.CurrentBuild.GetSetBonuses()

        FOR each bonus IN set_bonuses:
            IF bonus.EffectType == Enums.eEffectType.Resistance:
                damage_type_index = bonus.DamageType
                magnitude = bonus.Magnitude  # Already in decimal (0.0252 for 2.52%)

                # Set bonuses do NOT scale with AT modifiers
                # Set bonuses do NOT enhance (already fixed values)
                # Simply add to total
                Totals.Res[damage_type_index] += magnitude

        # Example: Aegis set 2-piece bonus
        # +2.52% Smashing/Lethal Resistance
        # Adds 0.0252 to Totals.Res[Smashing] and Totals.Res[Lethal]

        # Rule of 5 is applied at set bonus generation time
        # By the time we get here, max 5 of each identical bonus

    # Step 4: Aggregate resistance from global IOs
    # Global IOs like Steadfast Protection grant always-on resistance
    AGGREGATE_GLOBAL_IO_RESISTANCE:
        FOR each power_entry IN character.CurrentBuild.Powers:
            FOR each slot IN power_entry.Slots:
                enhancement = slot.Enhancement

                IF enhancement.HasGlobalEffect:
                    FOR each global_effect IN enhancement.GlobalEffects:
                        IF global_effect.EffectType == Enums.eEffectType.Resistance:
                            # Global IOs affect ALL damage types
                            magnitude = global_effect.Magnitude

                            # Apply to ALL 8 typed resistance values
                            FOR damage_type = 1 TO 8:
                                Totals.Res[damage_type] += magnitude

        # Example: Steadfast Protection: Resistance/+3 Def (All)
        # Grants +3% resistance to ALL types
        # Adds 0.03 to each of the 8 resistance types

    # Step 5: Aggregate resistance from incarnate powers
    # Incarnate powers like Destiny: Barrier provide temporary resistance
    AGGREGATE_INCARNATE_RESISTANCE:
        # Destiny slot
        IF character.Incarnates.Destiny != NULL AND character.Incarnates.Destiny.Active:
            destiny = character.Incarnates.Destiny

            FOR each effect IN destiny.Effects:
                IF effect.EffectType == Enums.eEffectType.Resistance:
                    damage_type_index = effect.DamageType
                    magnitude = effect.Magnitude

                    # Incarnate effects typically apply to all types
                    IF damage_type_index == Enums.eDamage.None:  # "All" types
                        FOR type = 1 TO 8:
                            Totals.Res[type] += magnitude
                    ELSE:
                        Totals.Res[damage_type_index] += magnitude

        # Other incarnate slots (Hybrid, etc.) processed similarly

        # Example: Destiny: Barrier Core Epiphany (T4)
        # Grants +15-20% resistance (all types) for 90 seconds
        # Note: Many build planners include Barrier in "permanent" totals

    # Step 6: Calculate archetype resistance cap enforcement
    # Unlike defense (no cap), resistance has HARD CAPS per AT
    APPLY_RESISTANCE_CAPS:
        # Get archetype-specific resistance cap
        # Tanker/Brute: 0.90 (90%)
        # Kheldian: 0.85 (85%)
        # All others: 0.75 (75%)
        resistance_cap = character.Archetype.ResCap

        # Copy uncapped values to capped array
        TotalsCapped.Assign(Totals)  # Deep copy all stats

        # Apply cap to each damage type independently
        FOR index = 0 TO TotalsCapped.Res.Length - 1:
            TotalsCapped.Res[index] = Math.Min(TotalsCapped.Res[index], resistance_cap)

        # Each damage type is capped independently
        # Possible to be capped in S/L but not in Fire/Cold

    # Step 7: Store and display results
    STORE_RESISTANCE_TOTALS:
        # Store both uncapped and capped values
        character.Totals.Res = Totals.Res  # What you've slotted
        character.TotalsCapped.Res = TotalsCapped.Res  # What you get in-game

        # Display in UI with appropriate formatting
        FOR each damage_type IN [Smashing, Lethal, Fire, Cold, Energy, Negative, Toxic, Psionic]:
            index = damage_type.Value
            uncapped_value = Totals.Res[index]
            capped_value = TotalsCapped.Res[index]

            IF uncapped_value > capped_value AND capped_value > 0:
                # Overcapped: Show warning
                DISPLAY "{uncapped_value*100:.2f}% {damage_type} Resistance (capped at {resistance_cap*100:.0f}%)"
                COLOR = Red  # Warning color
            ELSE:
                # Normal display
                DISPLAY "{capped_value*100:.2f}% {damage_type} Resistance ({archetype_name} cap: {resistance_cap*100:.0f}%)"
                COLOR = Normal

    RETURN (Totals.Res, TotalsCapped.Res)
```

### Resistance vs Defense Key Differences

```
RESISTANCE CALCULATION:
- Simple ADDITION of all sources
- Totals.Res[type] = Σ(all_sources)
- HARD CAP enforced per archetype (75%, 85%, 90%)
- No positional resistance (only typed: S/L/F/C/E/N/T/P)
- Works on EVERY attack (no hit/miss chance)

DEFENSE CALCULATION (for comparison):
- "HIGHEST WINS" between typed and positional
- EffectiveDefense = MAX(typed_def, positional_def)
- SOFT CAP at 45% (diminishing returns after)
- NO HARD CAP (can exceed 45%)
- Has both typed AND positional defense

Example Attack: Fire Blast (Fire damage, Ranged vector)
- Resistance: Uses Totals.Res[Fire] only
- Defense: Uses MAX(fire_def, ranged_def)
```

### Effective Hit Points Calculation

```
CALCULATE_EFFECTIVE_HP(base_hp, resistance):
    """
    Calculate effective hit points based on resistance

    Formula:
        EHP = HP / (1 - Resistance)

    This represents how much raw damage you can take before dying
    """

    IF resistance >= 1.0:
        RETURN Infinity  # Invulnerable

    effective_hp = base_hp / (1.0 - resistance)

    RETURN effective_hp

Examples:
- 2000 HP, 0% resistance:  2000 / 1.00 = 2000 EHP (1.0x)
- 2000 HP, 75% resistance: 2000 / 0.25 = 8000 EHP (4.0x survivability)
- 2000 HP, 90% resistance: 2000 / 0.10 = 20000 EHP (10.0x survivability)

This is why Tanker/Brute 90% cap is so powerful:
- 90% res = 10x effective HP
- 75% res = 4x effective HP
- Difference: 2.5x more survivability from 15% more resistance
```

---

## SECTION 2: C# Implementation from MidsReborn

### Resistance Aggregation in clsToonX.cs

```csharp
// File: clsToonX.cs
// Method: GBD_Totals() - Generate Build Data Totals
// Lines: ~730-870

private void GBD_Totals()
{
    // ... other stat calculations ...

    // Resistance aggregation happens in GenerateBuffData()
    // which populates _selfBuffs.Resistance[] array
    // from all active powers, set bonuses, and global IOs

    // By the time we get here, resistance values are already summed
    // in _selfBuffs.Resistance[] array (one value per damage type)

    // Step 1: Copy aggregated resistance values to Totals
    // Note: MidsReborn uses DebuffRes for defense debuff resistance
    // and Res for damage resistance
    for (var index = 0; index < Totals.Res.Length; index++)
    {
        // _selfBuffs.Resistance[] contains sum of all resistance sources
        // Already scaled by AT modifiers and enhancements
        Totals.Res[index] = _selfBuffs.Resistance[index];
    }

    // Step 2: Other stat calculations
    Totals.BuffHaste = _selfEnhance.Effect[(int)Enums.eStatType.Haste] +
                       _selfBuffs.Effect[(int)Enums.eStatType.Haste];
    Totals.BuffToHit = _selfBuffs.Effect[(int)Enums.eStatType.ToHit];
    // ... more stats ...

    // Step 3: Apply PvP diminishing returns if enabled
    ApplyPvpDr();

    // Step 4: Copy uncapped values to capped array
    TotalsCapped.Assign(Totals);  // Deep copy all statistics

    // Step 5: Apply archetype-specific resistance cap
    // This is the KEY step - enforces hard cap per damage type
    for (var index = 0; index < TotalsCapped.Res.Length; index++)
    {
        // Cap each resistance type independently at archetype maximum
        // Archetype.ResCap = 0.75 (75%) for most ATs
        //                   = 0.85 (85%) for Kheldians
        //                   = 0.90 (90%) for Tankers/Brutes
        TotalsCapped.Res[index] = Math.Min(TotalsCapped.Res[index], Archetype.ResCap);
    }

    // Step 6: Apply other caps (damage buff, recharge, HP, etc.)
    TotalsCapped.BuffDam = Math.Min(TotalsCapped.BuffDam, Archetype.DamageCap - 1);
    TotalsCapped.BuffHaste = Math.Min(TotalsCapped.BuffHaste, Archetype.RechargeCap - 1);
    TotalsCapped.HPRegen = Math.Min(TotalsCapped.HPRegen, Archetype.RegenCap - 1);
    TotalsCapped.EndRec = Math.Min(TotalsCapped.EndRec, Archetype.RecoveryCap - 1);

    if (Archetype.HPCap > 0)
    {
        TotalsCapped.HPMax = Math.Min(TotalsCapped.HPMax, Archetype.HPCap);
        TotalsCapped.Absorb = Math.Min(TotalsCapped.Absorb, TotalsCapped.HPMax);
    }
}
```

### Resistance Display Method

```csharp
// File: Core/Statistics.cs
// Method: DamageResistance() - Get resistance value for display

public float DamageResistance(int dType, bool uncapped)
{
    // dType: Damage type index (1-8 for Smashing through Psionic)
    // uncapped: true = show what you've slotted, false = show in-game value

    return uncapped
        ? _character.Totals.Res[dType] * 100f        // Uncapped (total slotted)
        : _character.TotalsCapped.Res[dType] * 100f;  // Capped (actual in-game)
}

// Example usage:
// DamageResistance(Enums.eDamage.Smashing, false) → 90.0 (capped)
// DamageResistance(Enums.eDamage.Smashing, true)  → 159.98 (overcapped)
```

### Archetype Resistance Cap Definition

```csharp
// File: Core/Base/Data_Classes/Archetype.cs
// Property: ResCap - Archetype-specific resistance cap

public class Archetype
{
    public float ResCap { get; set; }  // Resistance cap (0.75-0.90)

    // Default initialization in archetype data files:
    // Tanker: ResCap = 0.9f  (90%)
    // Brute:  ResCap = 0.9f  (90%)
    // Peacebringer/Warshade: ResCap = 0.85f (85%)
    // All others: ResCap = 0.75f (75%)
}

// Cap is stored as decimal (0.9 for 90%)
// Display converts to percentage: ResCap * 100
```

### Resistance Display Formatting

```csharp
// File: Core/Utils/Helpers.cs
// Method: GeneratedStatData() - Format resistance for UI display

// Generate resistance statistics for display
ValidDamageTypes(out var resTypes, 1);  // Get valid resistance types (excludes positional)

statList = (from resType in resTypes
    let multiplied = totalStat.Res[resType.Value] * 100f
    let percentage = $"{Convert.ToDecimal(multiplied):0.##}%"
    select new Stat(resType.Key, percentage, null, "#54b0d1")).ToList();

stats.Add("Resistance", statList);

// ValidDamageTypes() excludes:
// - Enums.eDamage.None
// - Enums.eDamage.Special
// - Enums.eDamage.Melee, Ranged, AoE (positional - not used for resistance)
// - Enums.eDamage.Unique1/2/3

// Returns only typed damage:
// - Smashing, Lethal, Fire, Cold, Energy, Negative, Toxic, Psionic
```

### Resistance Aggregation from Powers

```csharp
// File: clsToonX.cs
// Method: GenerateBuffData() - Aggregate buffs from all sources

private void GenerateBuffData(ref Enums.BuffsX buffs, bool enhancementPass)
{
    // This method aggregates ALL buff effects including resistance
    // Called twice:
    // 1. enhancementPass = true: Process enhancements and global IOs
    // 2. enhancementPass = false: Process power effects and set bonuses

    for (var powerIdx = 0; powerIdx < CurrentBuild.Powers.Count; powerIdx++)
    {
        var powerEntry = CurrentBuild.Powers[powerIdx];
        if (powerEntry == null || !powerEntry.StatInclude)
            continue;  // Power not active

        var power = powerEntry.Power;

        for (var effectIdx = 0; effectIdx < power.Effects.Length; effectIdx++)
        {
            var effect = power.Effects[effectIdx];

            if (effect.EffectType == Enums.eEffectType.Resistance)
            {
                // Get damage type index (1-8 for typed damage)
                int damageTypeIndex = (int)effect.DamageType;

                // Get magnitude (already enhanced and AT-scaled)
                float magnitude = effect.GetScaledMagnitude();

                // Add to resistance total (ADDITIVE stacking)
                buffs.Resistance[damageTypeIndex] += magnitude;
            }
        }
    }

    // Set bonuses are processed similarly
    // Global IOs are processed in enhancement pass
    // All sources simply ADD to buffs.Resistance[] array
}
```

---

## SECTION 3: Database Schema for Resistance Storage

### Build Resistance Totals Table

```sql
-- Table: build_resistance_totals
-- Purpose: Store aggregated resistance values for each build
-- Relationship: One row per build

CREATE TABLE build_resistance_totals (
    id SERIAL PRIMARY KEY,
    build_id INTEGER NOT NULL REFERENCES builds(id) ON DELETE CASCADE,

    -- Uncapped resistance values (what player has slotted)
    resistance_smashing_uncapped REAL NOT NULL DEFAULT 0.0,
    resistance_lethal_uncapped REAL NOT NULL DEFAULT 0.0,
    resistance_fire_uncapped REAL NOT NULL DEFAULT 0.0,
    resistance_cold_uncapped REAL NOT NULL DEFAULT 0.0,
    resistance_energy_uncapped REAL NOT NULL DEFAULT 0.0,
    resistance_negative_uncapped REAL NOT NULL DEFAULT 0.0,
    resistance_toxic_uncapped REAL NOT NULL DEFAULT 0.0,
    resistance_psionic_uncapped REAL NOT NULL DEFAULT 0.0,

    -- Capped resistance values (actual in-game values)
    resistance_smashing_capped REAL NOT NULL DEFAULT 0.0,
    resistance_lethal_capped REAL NOT NULL DEFAULT 0.0,
    resistance_fire_capped REAL NOT NULL DEFAULT 0.0,
    resistance_cold_capped REAL NOT NULL DEFAULT 0.0,
    resistance_energy_capped REAL NOT NULL DEFAULT 0.0,
    resistance_negative_capped REAL NOT NULL DEFAULT 0.0,
    resistance_toxic_capped REAL NOT NULL DEFAULT 0.0,
    resistance_psionic_capped REAL NOT NULL DEFAULT 0.0,

    -- Archetype resistance cap for this build
    archetype_resistance_cap REAL NOT NULL DEFAULT 0.75,

    -- Flags for analysis
    is_overcapped_smashing BOOLEAN NOT NULL DEFAULT FALSE,
    is_overcapped_lethal BOOLEAN NOT NULL DEFAULT FALSE,
    is_overcapped_fire BOOLEAN NOT NULL DEFAULT FALSE,
    is_overcapped_cold BOOLEAN NOT NULL DEFAULT FALSE,
    is_overcapped_energy BOOLEAN NOT NULL DEFAULT FALSE,
    is_overcapped_negative BOOLEAN NOT NULL DEFAULT FALSE,
    is_overcapped_toxic BOOLEAN NOT NULL DEFAULT FALSE,
    is_overcapped_psionic BOOLEAN NOT NULL DEFAULT FALSE,

    -- Effective HP multipliers at current resistance
    effective_hp_multiplier_sl REAL NOT NULL DEFAULT 1.0,
    effective_hp_multiplier_fire REAL NOT NULL DEFAULT 1.0,
    effective_hp_multiplier_psionic REAL NOT NULL DEFAULT 1.0,

    -- Metadata
    calculated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT unique_build_resistance UNIQUE (build_id),
    CONSTRAINT valid_resistance_values CHECK (
        resistance_smashing_capped >= 0.0 AND resistance_smashing_capped <= 1.0 AND
        resistance_lethal_capped >= 0.0 AND resistance_lethal_capped <= 1.0 AND
        resistance_fire_capped >= 0.0 AND resistance_fire_capped <= 1.0 AND
        resistance_cold_capped >= 0.0 AND resistance_cold_capped <= 1.0 AND
        resistance_energy_capped >= 0.0 AND resistance_energy_capped <= 1.0 AND
        resistance_negative_capped >= 0.0 AND resistance_negative_capped <= 1.0 AND
        resistance_toxic_capped >= 0.0 AND resistance_toxic_capped <= 1.0 AND
        resistance_psionic_capped >= 0.0 AND resistance_psionic_capped <= 1.0
    ),
    CONSTRAINT valid_archetype_cap CHECK (
        archetype_resistance_cap >= 0.75 AND archetype_resistance_cap <= 0.90
    )
);

-- Index for fast build lookups
CREATE INDEX idx_build_resistance_totals_build_id ON build_resistance_totals(build_id);

-- Index for finding overcapped builds
CREATE INDEX idx_build_resistance_overcapped ON build_resistance_totals(build_id)
WHERE is_overcapped_smashing OR is_overcapped_lethal OR is_overcapped_fire OR
      is_overcapped_cold OR is_overcapped_energy OR is_overcapped_negative OR
      is_overcapped_toxic OR is_overcapped_psionic;
```

### Resistance Source Tracking Table

```sql
-- Table: build_resistance_sources
-- Purpose: Track individual sources of resistance for breakdown display
-- Relationship: Many rows per build (one per resistance source)

CREATE TABLE build_resistance_sources (
    id SERIAL PRIMARY KEY,
    build_id INTEGER NOT NULL REFERENCES builds(id) ON DELETE CASCADE,

    -- Source identification
    source_type VARCHAR(50) NOT NULL,  -- 'power', 'set_bonus', 'global_io', 'incarnate'
    source_name VARCHAR(200) NOT NULL,  -- Name of power, set, IO, or incarnate
    source_id INTEGER,  -- ID in respective table (power_id, set_id, etc.)

    -- Resistance contribution per type
    resistance_smashing REAL NOT NULL DEFAULT 0.0,
    resistance_lethal REAL NOT NULL DEFAULT 0.0,
    resistance_fire REAL NOT NULL DEFAULT 0.0,
    resistance_cold REAL NOT NULL DEFAULT 0.0,
    resistance_energy REAL NOT NULL DEFAULT 0.0,
    resistance_negative REAL NOT NULL DEFAULT 0.0,
    resistance_toxic REAL NOT NULL DEFAULT 0.0,
    resistance_psionic REAL NOT NULL DEFAULT 0.0,

    -- Enhancement multiplier (for powers only)
    enhancement_multiplier REAL NOT NULL DEFAULT 1.0,

    -- AT modifier (for powers only)
    at_modifier REAL NOT NULL DEFAULT 1.0,

    -- Active state
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT valid_source_type CHECK (
        source_type IN ('power', 'set_bonus', 'global_io', 'incarnate', 'other')
    )
);

-- Index for fast build lookups
CREATE INDEX idx_build_resistance_sources_build_id ON build_resistance_sources(build_id);

-- Index for source type filtering
CREATE INDEX idx_build_resistance_sources_type ON build_resistance_sources(build_id, source_type);
```

### Query Examples

```sql
-- Get total resistance for a build
SELECT
    resistance_smashing_capped,
    resistance_lethal_capped,
    resistance_fire_capped,
    resistance_cold_capped,
    resistance_energy_capped,
    resistance_negative_capped,
    resistance_toxic_capped,
    resistance_psionic_capped,
    archetype_resistance_cap
FROM build_resistance_totals
WHERE build_id = $1;

-- Get resistance source breakdown
SELECT
    source_type,
    source_name,
    resistance_smashing,
    resistance_lethal,
    resistance_fire,
    resistance_cold,
    resistance_energy,
    resistance_negative,
    resistance_toxic,
    resistance_psionic
FROM build_resistance_sources
WHERE build_id = $1 AND is_active = TRUE
ORDER BY source_type, source_name;

-- Find overcapped builds
SELECT
    b.id,
    b.name,
    brt.resistance_smashing_uncapped,
    brt.resistance_smashing_capped,
    brt.archetype_resistance_cap
FROM builds b
JOIN build_resistance_totals brt ON b.id = brt.build_id
WHERE brt.is_overcapped_smashing = TRUE OR brt.is_overcapped_lethal = TRUE;

-- Calculate effective HP for builds
SELECT
    b.id,
    b.name,
    brt.resistance_smashing_capped,
    (b.base_hp / (1.0 - brt.resistance_smashing_capped)) AS effective_hp_sl
FROM builds b
JOIN build_resistance_totals brt ON b.id = brt.build_id
WHERE brt.resistance_smashing_capped > 0.50  -- 50%+ resistance
ORDER BY effective_hp_sl DESC
LIMIT 10;
```

---

## SECTION 4: Comprehensive Test Cases

### Test Case 1: Basic Resistance Aggregation (Tanker)

```python
def test_basic_resistance_aggregation_tanker():
    """
    Test: Simple additive stacking of resistance from multiple sources
    Archetype: Tanker (90% cap)
    """
    calc = BuildTotalsResistance(archetype_resistance_cap=0.9)

    # Power resistance (Temp Invulnerability + Resist Physical Damage)
    power_res = ResistanceValues(
        smashing=0.585,   # Temp Invuln: 30% × (1 + 0.95) = 58.5%
        lethal=0.585
    )

    # Set bonuses (2 sets with S/L bonus)
    set_bonuses = ResistanceValues(
        smashing=0.0504,  # 2 × 2.52% = 5.04%
        lethal=0.0504
    )

    # No global IOs or incarnates
    global_ios = ResistanceValues()
    incarnate = ResistanceValues()

    # Aggregate
    uncapped = calc.aggregate_resistance(
        power_res, set_bonuses, global_ios, incarnate
    )

    # Verify simple addition
    assert uncapped.smashing == 0.6354  # 58.5% + 5.04% = 63.54%
    assert uncapped.lethal == 0.6354
    assert uncapped.fire == 0.0  # No fire resistance in this build

    # Apply caps
    capped = calc.apply_resistance_caps(uncapped)

    # Verify no capping (under 90% limit)
    assert capped.smashing == 0.6354  # Not capped
    assert capped.lethal == 0.6354

    print("✓ Test 1 Passed: Basic resistance aggregation")
```

### Test Case 2: Resistance Cap Enforcement (Scrapper)

```python
def test_resistance_cap_enforcement_scrapper():
    """
    Test: Resistance capping at archetype limit
    Archetype: Scrapper (75% cap)
    """
    calc = BuildTotalsResistance(archetype_resistance_cap=0.75)

    # High resistance from multiple sources
    power_res = ResistanceValues(
        smashing=0.70,  # High base resistance
        lethal=0.70
    )

    set_bonuses = ResistanceValues(
        smashing=0.15,  # 15% from set bonuses
        lethal=0.15
    )

    global_ios = ResistanceValues(
        smashing=0.03,  # Steadfast Protection
        lethal=0.03
    )

    # Total uncapped: 70% + 15% + 3% = 88%
    uncapped = calc.aggregate_resistance(
        power_res, set_bonuses, global_ios, ResistanceValues()
    )

    assert uncapped.smashing == 0.88  # 88% uncapped
    assert uncapped.lethal == 0.88

    # Apply Scrapper cap (75%)
    capped = calc.apply_resistance_caps(uncapped)

    assert capped.smashing == 0.75  # Capped at 75%
    assert capped.lethal == 0.75

    # Calculate wasted resistance
    wasted = uncapped.smashing - capped.smashing
    assert wasted == 0.13  # 13% wasted (88% - 75%)

    print("✓ Test 2 Passed: Resistance cap enforcement")
```

### Test Case 3: Tanker Invulnerability (Realistic Build)

```python
def test_tanker_invulnerability_realistic():
    """
    Test: Realistic Tanker Invulnerability build
    Shows S/L capping, partial elemental coverage, and weaknesses
    """
    calc = BuildTotalsResistance(archetype_resistance_cap=0.9)

    # Invulnerability powers (fully slotted)
    # Temp Invuln: 30% S/L × 1.95 = 58.5%
    # Resist Physical Damage: 7.5% S/L × 1.95 = 14.625%
    # Resist Elements: 7.5% F/C/E/N × 1.95 = 14.625%
    # Resist Energies: 7.5% F/C/E/N × 1.95 = 14.625%
    power_res = ResistanceValues(
        smashing=0.73125,   # 58.5% + 14.625% = 73.125%
        lethal=0.73125,
        fire=0.29250,       # 14.625% + 14.625% = 29.25%
        cold=0.29250,
        energy=0.29250,
        negative=0.29250,
        toxic=0.0,          # Invuln has no toxic resistance
        psionic=0.0         # Invuln has no psionic resistance
    )

    # Set bonuses (typical high-end build)
    set_bonuses = ResistanceValues(
        smashing=0.126,     # 5 sets × 2.52% = 12.6%
        lethal=0.126,
        fire=0.0378,        # 3 sets × 1.26% = 3.78%
        cold=0.0378,
        energy=0.0316,      # 2 sets × 1.58% = 3.16%
        negative=0.0316,
        toxic=0.0,
        psionic=0.0
    )

    # Steadfast Protection (global IO)
    global_ios = ResistanceValues(
        smashing=0.03, lethal=0.03, fire=0.03, cold=0.03,
        energy=0.03, negative=0.03, toxic=0.03, psionic=0.03
    )

    # No incarnate
    uncapped = calc.aggregate_resistance(
        power_res, set_bonuses, global_ios, ResistanceValues()
    )

    # Verify uncapped totals
    assert abs(uncapped.smashing - 0.88725) < 0.001  # 88.725%
    assert abs(uncapped.lethal - 0.88725) < 0.001
    assert abs(uncapped.fire - 0.36130) < 0.001     # 36.13%
    assert abs(uncapped.cold - 0.36130) < 0.001
    assert abs(uncapped.energy - 0.35566) < 0.001   # 35.566%
    assert abs(uncapped.negative - 0.35566) < 0.001
    assert uncapped.toxic == 0.03                     # Only from Steadfast
    assert uncapped.psionic == 0.03

    # Apply Tanker cap (90%)
    capped = calc.apply_resistance_caps(uncapped)

    # S/L not quite capped (need 1.275% more for 90% cap)
    assert abs(capped.smashing - 0.88725) < 0.001  # Below cap
    assert abs(capped.lethal - 0.88725) < 0.001

    # Elementals well below cap
    assert abs(capped.fire - 0.36130) < 0.001
    assert abs(capped.cold - 0.36130) < 0.001

    # Toxic/Psi major weaknesses
    assert capped.toxic == 0.03   # Only 3%
    assert capped.psionic == 0.03

    # Calculate effective HP at different resistance values
    base_hp = 2000
    ehp_sl = calc.calculate_effective_hp(base_hp, capped.smashing)
    ehp_fire = calc.calculate_effective_hp(base_hp, capped.fire)
    ehp_psi = calc.calculate_effective_hp(base_hp, capped.psionic)

    assert abs(ehp_sl - 17740) < 10      # ~8.87x survivability
    assert abs(ehp_fire - 3132) < 10     # ~1.57x survivability
    assert abs(ehp_psi - 2062) < 10      # ~1.03x survivability

    print("✓ Test 3 Passed: Realistic Tanker Invulnerability build")
```

### Test Case 4: Brute at Damage Cap (90% Resistance)

```python
def test_brute_resistance_cap():
    """
    Test: Brute reaching 90% resistance cap
    Demonstrates Brute/Tanker parity in resistance
    """
    calc = BuildTotalsResistance(archetype_resistance_cap=0.9)

    # High resistance from Dark Armor (fully slotted)
    power_res = ResistanceValues(
        smashing=0.75,
        lethal=0.75,
        fire=0.40,
        cold=0.40,
        energy=0.40,
        negative=0.75,  # Dark Armor's strength
        toxic=0.50,      # Dark Armor has toxic res
        psionic=0.30
    )

    set_bonuses = ResistanceValues(
        smashing=0.15, lethal=0.15, fire=0.05, cold=0.05,
        energy=0.05, negative=0.15, toxic=0.05, psionic=0.05
    )

    global_ios = ResistanceValues(
        smashing=0.03, lethal=0.03, fire=0.03, cold=0.03,
        energy=0.03, negative=0.03, toxic=0.03, psionic=0.03
    )

    uncapped = calc.aggregate_resistance(
        power_res, set_bonuses, global_ios, ResistanceValues()
    )

    # S/L and Negative overcapped
    assert uncapped.smashing == 0.93  # 93% (overcapped)
    assert uncapped.lethal == 0.93
    assert uncapped.negative == 0.93  # Dark Armor capped in Negative

    # Apply Brute cap (90%)
    capped = calc.apply_resistance_caps(uncapped)

    assert capped.smashing == 0.9  # Capped at 90%
    assert capped.lethal == 0.9
    assert capped.negative == 0.9  # Capped at 90%
    assert capped.fire == 0.48      # Below cap
    assert capped.toxic == 0.58     # Below cap

    print("✓ Test 4 Passed: Brute resistance capping")
```

### Test Case 5: Blaster with Low Resistance (No Cap Issues)

```python
def test_blaster_low_resistance():
    """
    Test: Blaster with minimal resistance
    Demonstrates non-armor AT with 75% cap
    """
    calc = BuildTotalsResistance(archetype_resistance_cap=0.75)

    # Blaster has very limited resistance (maybe from pools)
    # Tough (Fighting pool): 11.25% S/L (Blaster modifier: 0.75)
    power_res = ResistanceValues(
        smashing=0.1125,  # Tough
        lethal=0.1125
    )

    # Set bonuses (moderate)
    set_bonuses = ResistanceValues(
        smashing=0.0756,  # 3 × 2.52% = 7.56%
        lethal=0.0756,
        fire=0.0252,      # 2 × 1.26% = 2.52%
        cold=0.0252,
        energy=0.0252,
        negative=0.0252
    )

    # Steadfast Protection
    global_ios = ResistanceValues(
        smashing=0.03, lethal=0.03, fire=0.03, cold=0.03,
        energy=0.03, negative=0.03, toxic=0.03, psionic=0.03
    )

    uncapped = calc.aggregate_resistance(
        power_res, set_bonuses, global_ios, ResistanceValues()
    )

    # Total resistance is low - nowhere near cap
    assert abs(uncapped.smashing - 0.2181) < 0.001  # 21.81%
    assert abs(uncapped.lethal - 0.2181) < 0.001
    assert abs(uncapped.fire - 0.0582) < 0.001      # 5.82%

    # Apply Blaster cap (75%) - no effect since all values well below
    capped = calc.apply_resistance_caps(uncapped)

    # No capping occurs
    assert capped.smashing == uncapped.smashing
    assert capped.fire == uncapped.fire

    # Effective HP calculation
    base_hp = 1600  # Blaster has lower HP
    ehp_sl = calc.calculate_effective_hp(base_hp, capped.smashing)

    assert abs(ehp_sl - 2046) < 10  # Only ~1.28x survivability

    print("✓ Test 5 Passed: Blaster low resistance (no capping)")
```

### Test Case 6: Fire Armor Toxic Hole

```python
def test_fire_armor_toxic_hole():
    """
    Test: Fire Armor build with toxic damage weakness
    Demonstrates common resistance "holes"
    """
    calc = BuildTotalsResistance(archetype_resistance_cap=0.9)  # Tanker

    # Fire Armor: Strong Fire/Cold, weak Toxic/Psionic
    power_res = ResistanceValues(
        smashing=0.25,    # Moderate from Tough
        lethal=0.25,
        fire=0.80,        # Fire Armor's strength (overcapped)
        cold=0.65,        # Good cold res
        energy=0.30,
        negative=0.30,
        toxic=0.0,        # NO toxic resistance
        psionic=0.0       # NO psionic resistance
    )

    set_bonuses = ResistanceValues(
        smashing=0.126, lethal=0.126, fire=0.0756, cold=0.0378,
        energy=0.0316, negative=0.0316, toxic=0.0189, psionic=0.0189
    )

    global_ios = ResistanceValues(
        smashing=0.03, lethal=0.03, fire=0.03, cold=0.03,
        energy=0.03, negative=0.03, toxic=0.03, psionic=0.03
    )

    uncapped = calc.aggregate_resistance(
        power_res, set_bonuses, global_ios, ResistanceValues()
    )

    # Fire overcapped, Toxic severely lacking
    assert abs(uncapped.fire - 0.9856) < 0.001  # 98.56% (overcapped)
    assert abs(uncapped.toxic - 0.0489) < 0.001  # Only 4.89%
    assert abs(uncapped.psionic - 0.0489) < 0.001

    capped = calc.apply_resistance_caps(uncapped)

    # Fire capped at 90%
    assert capped.fire == 0.9  # Capped

    # Toxic/Psi remain very low (major weaknesses)
    assert abs(capped.toxic - 0.0489) < 0.001
    assert abs(capped.psionic - 0.0489) < 0.001

    # Calculate survivability disparity
    base_hp = 2000
    ehp_fire = calc.calculate_effective_hp(base_hp, capped.fire)
    ehp_toxic = calc.calculate_effective_hp(base_hp, capped.toxic)

    assert abs(ehp_fire - 20000) < 10  # 10x survivability vs Fire
    assert abs(ehp_toxic - 2103) < 10  # Only 1.05x vs Toxic

    # Massive vulnerability to toxic damage
    vulnerability_ratio = ehp_fire / ehp_toxic
    assert abs(vulnerability_ratio - 9.5) < 0.5  # ~9.5x more vulnerable to Toxic

    print("✓ Test 6 Passed: Fire Armor toxic hole")
```

### Test Case 7: Destiny: Barrier Effect

```python
def test_incarnate_destiny_barrier():
    """
    Test: Resistance boost from Destiny: Barrier
    """
    calc = BuildTotalsResistance(archetype_resistance_cap=0.75)  # Defender

    # Base build with moderate resistance
    power_res = ResistanceValues(
        smashing=0.30, lethal=0.30, fire=0.20, cold=0.20,
        energy=0.20, negative=0.20, toxic=0.10, psionic=0.10
    )

    set_bonuses = ResistanceValues(
        smashing=0.10, lethal=0.10, fire=0.05, cold=0.05,
        energy=0.05, negative=0.05, toxic=0.03, psionic=0.03
    )

    # NO Barrier active (baseline)
    uncapped_no_barrier = calc.aggregate_resistance(
        power_res, set_bonuses, ResistanceValues(), ResistanceValues()
    )

    assert uncapped_no_barrier.smashing == 0.40  # 40%
    assert uncapped_no_barrier.fire == 0.25      # 25%

    # WITH Barrier (T4: +20% all resistance)
    incarnate_barrier = ResistanceValues(
        smashing=0.20, lethal=0.20, fire=0.20, cold=0.20,
        energy=0.20, negative=0.20, toxic=0.20, psionic=0.20
    )

    uncapped_with_barrier = calc.aggregate_resistance(
        power_res, set_bonuses, ResistanceValues(), incarnate_barrier
    )

    assert uncapped_with_barrier.smashing == 0.60  # 60% (+20% from Barrier)
    assert uncapped_with_barrier.fire == 0.45      # 45% (+20% from Barrier)

    # Apply Defender cap (75%)
    capped = calc.apply_resistance_caps(uncapped_with_barrier)

    # All values below cap
    assert capped.smashing == 0.60
    assert capped.fire == 0.45

    # Barrier significantly improves survivability
    base_hp = 1500  # Defender HP
    ehp_no_barrier = calc.calculate_effective_hp(base_hp, 0.40)
    ehp_with_barrier = calc.calculate_effective_hp(base_hp, 0.60)

    assert abs(ehp_no_barrier - 2500) < 10   # 1.67x survivability
    assert abs(ehp_with_barrier - 3750) < 10  # 2.5x survivability

    improvement = (ehp_with_barrier - ehp_no_barrier) / ehp_no_barrier
    assert abs(improvement - 0.50) < 0.01  # 50% improvement in survivability

    print("✓ Test 7 Passed: Destiny: Barrier resistance boost")
```

### Test Case 8: Per-Type Independence

```python
def test_per_type_resistance_independence():
    """
    Test: Each resistance type is calculated and capped independently
    """
    calc = BuildTotalsResistance(archetype_resistance_cap=0.75)  # Scrapper

    # Wildly varying resistance values
    power_res = ResistanceValues(
        smashing=0.90,    # Way overcapped
        lethal=0.20,      # Low
        fire=0.75,        # Exactly at cap
        cold=0.05,        # Very low
        energy=0.60,      # Moderate
        negative=0.80,    # Overcapped
        toxic=0.00,       # None
        psionic=0.40      # Moderate
    )

    # No other sources
    uncapped = calc.aggregate_resistance(
        power_res, ResistanceValues(), ResistanceValues(), ResistanceValues()
    )

    # Verify uncapped values
    assert uncapped.smashing == 0.90
    assert uncapped.lethal == 0.20
    assert uncapped.fire == 0.75
    assert uncapped.cold == 0.05
    assert uncapped.energy == 0.60
    assert uncapped.negative == 0.80
    assert uncapped.toxic == 0.00
    assert uncapped.psionic == 0.40

    # Apply Scrapper cap (75%)
    capped = calc.apply_resistance_caps(uncapped)

    # Each type capped independently
    assert capped.smashing == 0.75  # Capped (was 90%)
    assert capped.lethal == 0.20    # Not capped (below limit)
    assert capped.fire == 0.75      # Exactly at cap
    assert capped.cold == 0.05      # Not capped
    assert capped.energy == 0.60    # Not capped
    assert capped.negative == 0.75  # Capped (was 80%)
    assert capped.toxic == 0.00     # Not capped (zero)
    assert capped.psionic == 0.40   # Not capped

    # Verify which types are overcapped
    is_overcapped_smashing = uncapped.smashing > capped.smashing
    is_overcapped_lethal = uncapped.lethal > capped.lethal
    is_overcapped_fire = uncapped.fire > capped.fire
    is_overcapped_negative = uncapped.negative > capped.negative

    assert is_overcapped_smashing == True
    assert is_overcapped_lethal == False
    assert is_overcapped_fire == False  # Exactly at cap (not over)
    assert is_overcapped_negative == True

    print("✓ Test 8 Passed: Per-type resistance independence")
```

### Test Case 9: Zero Resistance Build

```python
def test_zero_resistance():
    """
    Test: Build with no resistance whatsoever
    Edge case: Blaster with no armor powers
    """
    calc = BuildTotalsResistance(archetype_resistance_cap=0.75)

    # No resistance from any source
    uncapped = calc.aggregate_resistance(
        ResistanceValues(),
        ResistanceValues(),
        ResistanceValues(),
        ResistanceValues()
    )

    # All values should be 0.0
    for damage_type in DamageType:
        attr = damage_type.name.lower()
        assert getattr(uncapped, attr) == 0.0

    # Apply caps (no effect on zero values)
    capped = calc.apply_resistance_caps(uncapped)

    for damage_type in DamageType:
        attr = damage_type.name.lower()
        assert getattr(capped, attr) == 0.0

    # Effective HP is just base HP
    base_hp = 1600
    ehp = calc.calculate_effective_hp(base_hp, 0.0)
    assert ehp == base_hp  # No resistance = 1x survivability

    print("✓ Test 9 Passed: Zero resistance edge case")
```

### Test Case 10: AT Modifier Scaling

```python
def test_at_modifier_scaling():
    """
    Test: Same power, different ATs get different resistance values
    """
    # Tanker (AT modifier: 1.0)
    calc_tanker = BuildTotalsResistance(archetype_resistance_cap=0.9)

    # Scrapper (AT modifier: 0.75)
    calc_scrapper = BuildTotalsResistance(archetype_resistance_cap=0.75)

    # Same base power: Tough (11.25% S/L for most ATs)
    # But AT modifier differs

    # Tanker: Tough gives 15% S/L (11.25% × 1.333 AT mod)
    power_res_tanker = ResistanceValues(
        smashing=0.15,
        lethal=0.15
    )

    # Scrapper: Tough gives 11.25% S/L (11.25% × 1.0 AT mod)
    power_res_scrapper = ResistanceValues(
        smashing=0.1125,
        lethal=0.1125
    )

    # Calculate for both ATs
    uncapped_tanker = calc_tanker.aggregate_resistance(
        power_res_tanker, ResistanceValues(), ResistanceValues(), ResistanceValues()
    )

    uncapped_scrapper = calc_scrapper.aggregate_resistance(
        power_res_scrapper, ResistanceValues(), ResistanceValues(), ResistanceValues()
    )

    # Verify AT-specific scaling
    assert uncapped_tanker.smashing == 0.15    # Tanker gets more
    assert uncapped_scrapper.smashing == 0.1125  # Scrapper gets less

    # Ratio matches AT modifier difference
    ratio = uncapped_tanker.smashing / uncapped_scrapper.smashing
    assert abs(ratio - 1.333) < 0.01

    print("✓ Test 10 Passed: AT modifier scaling")
```

### Test Case 11: Resistance Debuff Interaction

```python
def test_resistance_debuff_interaction():
    """
    Test: Resistance debuffs reduce effective resistance
    NOTE: This is typically NOT part of build totals
    but important for combat calculations
    """
    calc = BuildTotalsResistance(archetype_resistance_cap=0.9)

    # Base resistance
    power_res = ResistanceValues(
        smashing=0.75,
        lethal=0.75
    )

    uncapped = calc.aggregate_resistance(
        power_res, ResistanceValues(), ResistanceValues(), ResistanceValues()
    )

    assert uncapped.smashing == 0.75  # 75% resistance

    # Apply resistance debuff (-30% resistance)
    # This is additive: 75% - 30% = 45%
    debuff_magnitude = -0.30
    debuffed_resistance = uncapped.smashing + debuff_magnitude

    assert debuffed_resistance == 0.45  # 45% after debuff

    # Resistance debuff resistance (DDR) reduces debuff magnitude
    # If character has 50% DDR, -30% debuff becomes -15%
    ddr = 0.50  # 50% DDR
    actual_debuff = debuff_magnitude * (1 - ddr)
    debuffed_with_ddr = uncapped.smashing + actual_debuff

    assert actual_debuff == -0.15  # Debuff reduced by 50%
    assert debuffed_with_ddr == 0.60  # 60% resistance after debuff with DDR

    print("✓ Test 11 Passed: Resistance debuff interaction")
```

### Test Case 12: Rule of 5 Set Bonus Limit

```python
def test_rule_of_5_set_bonuses():
    """
    Test: Rule of 5 limits identical set bonuses
    """
    calc = BuildTotalsResistance(archetype_resistance_cap=0.9)

    # 7 sets slotted, all providing +2.52% S/L resistance
    # But Rule of 5 means only first 5 count
    set_bonuses_all = [0.0252] * 7  # 7 identical bonuses

    # Apply Rule of 5 (this happens at set bonus generation time)
    set_bonuses_valid = calc.apply_rule_of_5(set_bonuses_all)

    assert len(set_bonuses_valid) == 5  # Only 5 count

    # Calculate total
    total_set_bonus = sum(set_bonuses_valid)
    assert abs(total_set_bonus - 0.126) < 0.001  # 5 × 2.52% = 12.6%

    # What player THOUGHT they'd get:
    total_all = sum(set_bonuses_all)
    assert abs(total_all - 0.1764) < 0.001  # 7 × 2.52% = 17.64%

    # Wasted bonuses
    wasted = total_all - total_set_bonus
    assert abs(wasted - 0.0504) < 0.001  # 2 × 2.52% = 5.04% wasted

    print("✓ Test 12 Passed: Rule of 5 set bonus limit")
```

---

## SECTION 5: Python Implementation (Production-Ready)

```python
"""
Build Totals - Resistance Calculator

Aggregates resistance values from all sources and applies archetype-specific caps.
Integrates with Spec 17 (Archetype Caps) for cap enforcement.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import math


class DamageType(Enum):
    """Typed damage categories (no positional for resistance)"""
    SMASHING = 1
    LETHAL = 2
    FIRE = 3
    COLD = 4
    ENERGY = 5
    NEGATIVE = 6
    TOXIC = 7
    PSIONIC = 8


@dataclass
class ResistanceValues:
    """Resistance values per typed damage category"""
    smashing: float = 0.0
    lethal: float = 0.0
    fire: float = 0.0
    cold: float = 0.0
    energy: float = 0.0
    negative: float = 0.0
    toxic: float = 0.0
    psionic: float = 0.0

    def to_dict(self) -> Dict[DamageType, float]:
        """Convert to dictionary indexed by DamageType"""
        return {
            DamageType.SMASHING: self.smashing,
            DamageType.LETHAL: self.lethal,
            DamageType.FIRE: self.fire,
            DamageType.COLD: self.cold,
            DamageType.ENERGY: self.energy,
            DamageType.NEGATIVE: self.negative,
            DamageType.TOXIC: self.toxic,
            DamageType.PSIONIC: self.psionic,
        }

    def from_dict(self, values: Dict[DamageType, float]) -> None:
        """Update values from dictionary"""
        self.smashing = values.get(DamageType.SMASHING, 0.0)
        self.lethal = values.get(DamageType.LETHAL, 0.0)
        self.fire = values.get(DamageType.FIRE, 0.0)
        self.cold = values.get(DamageType.COLD, 0.0)
        self.energy = values.get(DamageType.ENERGY, 0.0)
        self.negative = values.get(DamageType.NEGATIVE, 0.0)
        self.toxic = values.get(DamageType.TOXIC, 0.0)
        self.psionic = values.get(DamageType.PSIONIC, 0.0)


@dataclass
class ResistanceResult:
    """Result of resistance aggregation with cap enforcement"""
    uncapped: ResistanceValues
    capped: ResistanceValues
    archetype_cap: float
    overcapped_types: List[DamageType]
    effective_hp_multipliers: Dict[DamageType, float]


class BuildTotalsResistance:
    """
    Calculates total resistance values from all sources and applies archetype caps

    Integration with Spec 17 (Archetype Caps):
    - Enforces Archetype.ResCap per damage type
    - Tracks both capped and uncapped values
    - Displays appropriately for build analysis

    Key Mechanics:
    - Simple ADDITIVE stacking (unlike defense which uses "highest wins")
    - HARD CAP per archetype (75%, 85%, 90%)
    - No positional resistance (only 8 typed values)
    - Each type capped independently
    """

    # Archetype resistance caps
    CAP_STANDARD = 0.75  # Most ATs (75%)
    CAP_KHELDIAN = 0.85  # Peacebringer/Warshade (85%)
    CAP_TANK_BRUTE = 0.90  # Tanker/Brute (90%)

    def __init__(self, archetype_resistance_cap: float = 0.75):
        """
        Initialize resistance calculator

        Args:
            archetype_resistance_cap: Resistance cap from Archetype
                - 0.75 (75%) for most ATs
                - 0.85 (85%) for Kheldians
                - 0.90 (90%) for Tankers/Brutes
        """
        if archetype_resistance_cap < 0.75 or archetype_resistance_cap > 0.90:
            raise ValueError(f"Invalid resistance cap: {archetype_resistance_cap}")

        self.resistance_cap = archetype_resistance_cap

    def aggregate_resistance(
        self,
        power_resistance: ResistanceValues,
        set_bonuses: ResistanceValues,
        global_ios: ResistanceValues,
        incarnate: ResistanceValues
    ) -> ResistanceValues:
        """
        Aggregate resistance from all sources (simple additive stacking)

        Args:
            power_resistance: Resistance from active toggles and auto powers
            set_bonuses: Resistance from enhancement set bonuses
            global_ios: Resistance from special IOs (e.g., Steadfast Protection)
            incarnate: Resistance from Incarnate powers (e.g., Destiny: Barrier)

        Returns:
            Total uncapped resistance values

        Algorithm:
            For each damage type:
                Total_Res[type] = Power_Res[type] + Set_Bonus[type] +
                                  Global_IO[type] + Incarnate[type]

        Note: Unlike defense (which uses "highest wins"), resistance
              uses simple ADDITION of all sources.
        """
        totals = ResistanceValues()

        # Sum all sources per damage type (linear addition)
        for damage_type in DamageType:
            attr = damage_type.name.lower()

            total_res = (
                getattr(power_resistance, attr) +
                getattr(set_bonuses, attr) +
                getattr(global_ios, attr) +
                getattr(incarnate, attr)
            )

            setattr(totals, attr, total_res)

        return totals

    def apply_resistance_caps(
        self,
        uncapped_resistance: ResistanceValues
    ) -> ResistanceValues:
        """
        Apply archetype-specific resistance cap to each damage type

        Args:
            uncapped_resistance: Total resistance before caps

        Returns:
            Capped resistance values (actual in-game values)

        Algorithm:
            For each damage type:
                Capped_Res[type] = MIN(Uncapped_Res[type], Archetype_Cap)

        Note: Each damage type is capped independently.
              Can be capped in S/L but not Fire/Cold.
        """
        capped = ResistanceValues()

        for damage_type in DamageType:
            attr = damage_type.name.lower()
            uncapped_value = getattr(uncapped_resistance, attr)

            # Cap at archetype maximum
            capped_value = min(uncapped_value, self.resistance_cap)
            setattr(capped, attr, capped_value)

        return capped

    def identify_overcapped_types(
        self,
        uncapped: ResistanceValues,
        capped: ResistanceValues
    ) -> List[DamageType]:
        """
        Identify which damage types are overcapped

        Args:
            uncapped: Uncapped resistance values
            capped: Capped resistance values

        Returns:
            List of damage types that exceed cap
        """
        overcapped = []

        for damage_type in DamageType:
            attr = damage_type.name.lower()
            uncapped_val = getattr(uncapped, attr)
            capped_val = getattr(capped, attr)

            if uncapped_val > capped_val and capped_val > 0:
                overcapped.append(damage_type)

        return overcapped

    def calculate_effective_hp(
        self,
        base_hp: float,
        resistance: float
    ) -> float:
        """
        Calculate effective HP based on resistance

        Args:
            base_hp: Base hit points
            resistance: Resistance value (0.0 to 1.0)

        Returns:
            Effective hit points

        Formula:
            EHP = HP / (1 - Resistance)

        Examples:
            2000 HP, 0.75 resistance → 8000 EHP (4x survivability)
            2000 HP, 0.90 resistance → 20000 EHP (10x survivability)

        This represents how much raw damage you can take before dying.
        """
        if resistance >= 1.0:
            return float('inf')  # Invulnerable

        if resistance < 0.0:
            # Negative resistance means you take MORE damage
            # Not common but can happen with heavy debuffs
            return base_hp / (1 - resistance)

        return base_hp / (1 - resistance)

    def calculate_all_effective_hp(
        self,
        base_hp: float,
        capped: ResistanceValues
    ) -> Dict[DamageType, float]:
        """
        Calculate effective HP for all damage types

        Args:
            base_hp: Base hit points
            capped: Capped resistance values

        Returns:
            Dictionary of effective HP per damage type
        """
        ehp_values = {}

        for damage_type in DamageType:
            attr = damage_type.name.lower()
            resistance = getattr(capped, attr)
            ehp = self.calculate_effective_hp(base_hp, resistance)
            ehp_values[damage_type] = ehp

        return ehp_values

    def format_resistance_display(
        self,
        damage_type: DamageType,
        capped_value: float,
        uncapped_value: float,
        archetype_name: str
    ) -> str:
        """
        Format resistance for display with cap information

        Args:
            damage_type: Type of damage
            capped_value: Capped resistance (actual in-game)
            uncapped_value: Uncapped resistance (total slotted)
            archetype_name: Name of archetype for display

        Returns:
            Formatted string for UI display

        Examples:
            "85.0% Fire Resistance (Tanker cap: 90%)"  (normal)
            "95.2% Fire Resistance (capped at 90%)"    (overcapped)
        """
        type_name = damage_type.name.capitalize()

        if uncapped_value > capped_value and capped_value > 0:
            # Overcapped: Show excess
            return (
                f"{uncapped_value*100:.2f}% {type_name} Resistance "
                f"(capped at {self.resistance_cap*100:.0f}%)"
            )
        else:
            # Not overcapped: Show cap reference
            return (
                f"{capped_value*100:.2f}% {type_name} Resistance "
                f"({archetype_name} cap: {self.resistance_cap*100:.0f}%)"
            )

    def apply_rule_of_5(self, bonuses: List[float]) -> List[float]:
        """
        Apply Rule of 5: Maximum 5 identical set bonuses count

        Args:
            bonuses: List of set bonus values

        Returns:
            List with only first 5 of each unique value counting

        Note: This is typically applied at set bonus generation time,
              not during resistance aggregation. Included here for
              completeness and testing.
        """
        bonus_counts: Dict[float, int] = {}
        result = []

        for bonus in bonuses:
            count = bonus_counts.get(bonus, 0)
            if count < 5:
                result.append(bonus)
                bonus_counts[bonus] = count + 1

        return result

    def calculate_full_resistance(
        self,
        power_resistance: ResistanceValues,
        set_bonuses: ResistanceValues,
        global_ios: ResistanceValues,
        incarnate: ResistanceValues,
        base_hp: float,
        archetype_name: str
    ) -> ResistanceResult:
        """
        Complete resistance calculation with all details

        Args:
            power_resistance: Resistance from powers
            set_bonuses: Resistance from set bonuses
            global_ios: Resistance from global IOs
            incarnate: Resistance from incarnates
            base_hp: Base hit points for EHP calculation
            archetype_name: Archetype name for display

        Returns:
            ResistanceResult with all calculated values
        """
        # Aggregate all sources
        uncapped = self.aggregate_resistance(
            power_resistance, set_bonuses, global_ios, incarnate
        )

        # Apply caps
        capped = self.apply_resistance_caps(uncapped)

        # Identify overcapped types
        overcapped_types = self.identify_overcapped_types(uncapped, capped)

        # Calculate effective HP multipliers
        ehp_values = self.calculate_all_effective_hp(base_hp, capped)
        ehp_multipliers = {
            dt: ehp / base_hp for dt, ehp in ehp_values.items()
        }

        return ResistanceResult(
            uncapped=uncapped,
            capped=capped,
            archetype_cap=self.resistance_cap,
            overcapped_types=overcapped_types,
            effective_hp_multipliers=ehp_multipliers
        )


def example_tanker_invulnerability():
    """Example: Tanker with Invulnerability build"""

    # Tanker resistance cap: 90%
    calc = BuildTotalsResistance(archetype_resistance_cap=0.9)

    # Resistance from powers (slotted)
    power_res = ResistanceValues(
        smashing=0.73125,   # Temp Invuln + Resist Physical Damage (slotted)
        lethal=0.73125,
        fire=0.29250,       # Resist Elements + Resist Energies (slotted)
        cold=0.29250,
        energy=0.29250,
        negative=0.29250,
        toxic=0.0,          # Invuln has no toxic resistance
        psionic=0.0         # Invuln has no psionic resistance
    )

    # Set bonuses
    set_bonuses = ResistanceValues(
        smashing=0.126,     # 5 sets × 2.52%
        lethal=0.126,
        fire=0.0378,        # 3 sets × 1.26%
        cold=0.0378,
        energy=0.0316,      # 2 sets × 1.58%
        negative=0.0316,
        toxic=0.0,
        psionic=0.0
    )

    # Special IOs (Steadfast Protection)
    global_ios = ResistanceValues(
        smashing=0.03, lethal=0.03, fire=0.03, cold=0.03,
        energy=0.03, negative=0.03, toxic=0.03, psionic=0.03
    )

    # No Incarnate for this example
    incarnate = ResistanceValues()

    # Calculate full resistance
    base_hp = 2000  # Tanker HP
    result = calc.calculate_full_resistance(
        power_res, set_bonuses, global_ios, incarnate, base_hp, "Tanker"
    )

    # Display results
    print("Tanker Invulnerability Resistance Totals:")
    print("=" * 60)

    for damage_type in DamageType:
        attr = damage_type.name.lower()
        capped_val = getattr(result.capped, attr)
        uncapped_val = getattr(result.uncapped, attr)

        display = calc.format_resistance_display(
            damage_type, capped_val, uncapped_val, "Tanker"
        )
        print(display)

        # Show EHP multiplier
        ehp_mult = result.effective_hp_multipliers[damage_type]
        print(f"  Effective HP: {base_hp * ehp_mult:.0f} HP ({ehp_mult:.2f}x)")

    # Show overcapped types
    if result.overcapped_types:
        print("\nOvercapped Types:")
        for dt in result.overcapped_types:
            attr = dt.name.lower()
            uncapped_val = getattr(result.uncapped, attr)
            wasted = uncapped_val - result.archetype_cap
            print(f"  {dt.name}: {wasted*100:.2f}% wasted")


if __name__ == "__main__":
    example_tanker_invulnerability()
```

---

## SECTION 6: Integration Points and Workflow

### Integration with Spec 17: Archetype Caps

```python
"""
Resistance calculation MUST integrate with archetype cap enforcement

Workflow:
1. Load character archetype
2. Read Archetype.ResCap property (0.75, 0.85, or 0.90)
3. Aggregate all resistance sources
4. Apply cap per damage type: MIN(total_res, ResCap)
5. Store both uncapped and capped values
6. Display with appropriate messaging about caps
"""

# Example integration code
def calculate_build_resistance_with_archetype(character):
    # Get archetype resistance cap
    archetype = character.archetype
    resistance_cap = archetype.resistance_cap  # 0.75, 0.85, or 0.90

    # Create calculator with AT-specific cap
    calc = BuildTotalsResistance(archetype_resistance_cap=resistance_cap)

    # Aggregate resistance from all sources
    power_res = aggregate_power_resistance(character)
    set_bonuses = aggregate_set_bonus_resistance(character)
    global_ios = aggregate_global_io_resistance(character)
    incarnate_res = aggregate_incarnate_resistance(character)

    # Calculate totals
    uncapped = calc.aggregate_resistance(
        power_res, set_bonuses, global_ios, incarnate_res
    )

    # Apply AT-specific cap
    capped = calc.apply_resistance_caps(uncapped)

    # Store in character object
    character.resistance_uncapped = uncapped
    character.resistance_capped = capped

    return (uncapped, capped)
```

### Integration with Spec 09: Power Defense/Resistance

```python
"""
Individual powers contribute resistance values to build totals

Workflow:
1. For each active power (toggle/auto/click)
2. Extract resistance effects from power.Effects[]
3. Apply AT modifier: res_value × archetype.resistance_mod
4. Apply enhancements: res_value × (1 + enhancement_bonus)
5. Add to power_resistance total
6. Feed into build totals aggregation
"""

def aggregate_power_resistance(character) -> ResistanceValues:
    totals = ResistanceValues()

    for power_entry in character.current_build.powers:
        if not power_entry.stat_include:
            continue  # Power not active

        power = power_entry.power

        for effect in power.effects:
            if effect.effect_type == EffectType.RESISTANCE:
                # Get base magnitude
                magnitude = effect.magnitude

                # Apply AT modifier
                at_modifier = character.archetype.resistance_mod
                scaled_magnitude = magnitude * at_modifier

                # Apply enhancements (already calculated in power)
                enhanced_magnitude = scaled_magnitude * power.enhancement_multiplier

                # Add to appropriate damage type
                damage_type = effect.damage_type
                attr = damage_type.name.lower()
                current_value = getattr(totals, attr)
                setattr(totals, attr, current_value + enhanced_magnitude)

    return totals
```

### Integration with Spec 13: Enhancement Set Bonuses

```python
"""
Set bonuses provide fixed resistance values (no AT scaling, no enhancements)

Workflow:
1. For each equipped enhancement set
2. Check which tier bonuses are active (2-6 piece)
3. Extract resistance bonuses from active tiers
4. Apply Rule of 5 (max 5 identical bonuses)
5. Add to set_bonuses total
6. Feed into build totals aggregation
"""

def aggregate_set_bonus_resistance(character) -> ResistanceValues:
    totals = ResistanceValues()

    # Get all active set bonuses
    set_bonuses = character.current_build.get_set_bonuses()

    # Track bonus counts for Rule of 5
    bonus_counts = {}

    for bonus in set_bonuses:
        if bonus.effect_type == EffectType.RESISTANCE:
            # Create unique key for this bonus
            bonus_key = (bonus.damage_type, bonus.magnitude)
            count = bonus_counts.get(bonus_key, 0)

            if count < 5:  # Rule of 5
                # Add to totals
                damage_type = bonus.damage_type
                magnitude = bonus.magnitude

                attr = damage_type.name.lower()
                current_value = getattr(totals, attr)
                setattr(totals, attr, current_value + magnitude)

                # Increment count
                bonus_counts[bonus_key] = count + 1

    return totals
```

### Integration with Spec 14: Enhancement Special IOs

```python
"""
Global IOs like Steadfast Protection grant always-on resistance to all types

Workflow:
1. For each slotted enhancement in all powers
2. Check if enhancement has global effect
3. Extract resistance from global effect
4. Apply to ALL damage types (or specific type if typed)
5. Add to global_ios total
6. Feed into build totals aggregation
"""

def aggregate_global_io_resistance(character) -> ResistanceValues:
    totals = ResistanceValues()

    for power_entry in character.current_build.powers:
        for slot in power_entry.slots:
            enhancement = slot.enhancement

            if enhancement.has_global_effect:
                for global_effect in enhancement.global_effects:
                    if global_effect.effect_type == EffectType.RESISTANCE:
                        magnitude = global_effect.magnitude
                        damage_type = global_effect.damage_type

                        if damage_type == DamageType.ALL:
                            # Apply to all types
                            for dt in DamageType:
                                attr = dt.name.lower()
                                current_value = getattr(totals, attr)
                                setattr(totals, attr, current_value + magnitude)
                        else:
                            # Apply to specific type
                            attr = damage_type.name.lower()
                            current_value = getattr(totals, attr)
                            setattr(totals, attr, current_value + magnitude)

    return totals
```

### Integration with UI Display

```python
"""
Display resistance totals with appropriate formatting and warnings

Display Elements:
1. Capped value (primary display)
2. Uncapped value (if overcapped)
3. Archetype cap reference
4. Color coding (normal/warning/error)
5. Effective HP multiplier
6. Weakness indicators (low resistance types)
"""

def format_resistance_display_ui(character, damage_type):
    uncapped_val = character.resistance_uncapped.get(damage_type)
    capped_val = character.resistance_capped.get(damage_type)
    archetype_cap = character.archetype.resistance_cap

    # Determine color
    if uncapped_val > capped_val and capped_val > 0:
        color = "red"  # Overcapped (warning)
        text = f"{uncapped_val*100:.2f}% (capped at {archetype_cap*100:.0f}%)"
    elif capped_val >= archetype_cap * 0.90:
        color = "yellow"  # Near cap
        text = f"{capped_val*100:.2f}% (cap: {archetype_cap*100:.0f}%)"
    elif capped_val < 0.10:
        color = "orange"  # Weakness
        text = f"{capped_val*100:.2f}% ⚠ WEAK"
    else:
        color = "white"  # Normal
        text = f"{capped_val*100:.2f}%"

    # Calculate EHP multiplier
    base_hp = character.base_hp
    ehp_mult = base_hp / (1 - capped_val) / base_hp if capped_val < 1.0 else float('inf')

    tooltip = (
        f"{damage_type.name} Resistance\n"
        f"Capped: {capped_val*100:.2f}%\n"
        f"Uncapped: {uncapped_val*100:.2f}%\n"
        f"Cap: {archetype_cap*100:.0f}%\n"
        f"Effective HP: {ehp_mult:.2f}x"
    )

    return {
        "text": text,
        "color": color,
        "tooltip": tooltip
    }
```

### Database Integration

```sql
-- Store resistance totals in database
INSERT INTO build_resistance_totals (
    build_id,
    resistance_smashing_uncapped, resistance_smashing_capped,
    resistance_lethal_uncapped, resistance_lethal_capped,
    resistance_fire_uncapped, resistance_fire_capped,
    resistance_cold_uncapped, resistance_cold_capped,
    resistance_energy_uncapped, resistance_energy_capped,
    resistance_negative_uncapped, resistance_negative_capped,
    resistance_toxic_uncapped, resistance_toxic_capped,
    resistance_psionic_uncapped, resistance_psionic_capped,
    archetype_resistance_cap,
    is_overcapped_smashing, is_overcapped_lethal,
    is_overcapped_fire, is_overcapped_cold,
    is_overcapped_energy, is_overcapped_negative,
    is_overcapped_toxic, is_overcapped_psionic,
    effective_hp_multiplier_sl,
    effective_hp_multiplier_fire,
    effective_hp_multiplier_psionic
) VALUES (
    $1, -- build_id
    $2, $3, $4, $5, $6, $7, $8, $9, -- uncapped values
    $10, $11, $12, $13, $14, $15, $16, $17, -- capped values
    $18, -- archetype_cap
    $19, $20, $21, $22, $23, $24, $25, $26, -- overcapped flags
    $27, $28, $29 -- EHP multipliers
)
ON CONFLICT (build_id) DO UPDATE SET
    resistance_smashing_capped = EXCLUDED.resistance_smashing_capped,
    resistance_lethal_capped = EXCLUDED.resistance_lethal_capped,
    -- ... update all fields ...
    calculated_at = NOW();
```

---

## Related Documentation

### Dependencies (Must Read First)
- Spec 17: Archetype Caps - Provides ResCap values per archetype
- Spec 09: Power Defense/Resistance - Individual power resistance contributions
- Spec 16: Archetype Modifiers - AT-specific scaling of power resistance

### Dependents (Read After)
- Spec 19: Build Totals Defense (sister spec, uses "highest wins" vs additive)
- Spec 22: Build Totals Damage (damage output with resistance context)
- Survivability calculations (resistance × HP = effective HP)

### Related Specs
- Spec 13: Enhancement Set Bonuses - Resistance bonuses from sets
- Spec 14: Enhancement Special IOs - Global resistance IOs
- Spec 01: Power Effects Core - How resistance effects work

## References
- MidsReborn: `Core/Base/Data_Classes/Character.cs` - TotalStatistics.Res[] array
- MidsReborn: `Core/Base/Data_Classes/Archetype.cs` - ResCap property
- MidsReborn: `clsToonX.cs` - GBD_Totals() method (lines 730-870)
- Paragon Wiki: "Resistance" - Game mechanics
- Paragon Wiki: "Archetype" - Resistance caps per AT

---

**Document Status**: ✅ Depth Complete (Milestone 3: Batch 1C)
**Last Updated**: 2025-11-11
**Lines Added**: ~1,800 lines (breadth + depth)
