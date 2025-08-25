# Mids Hero Web Backend - Calculation Logic Analysis Report

## Executive Summary

This report provides a comprehensive analysis of the current state of calculation logic in the Mids Hero Web backend. The analysis focuses on which character attributes are supported, power type handling (auto/toggle/click), calculation flows, and what functionality is implemented versus missing.

## 1. Supported Character Attributes

### 1.1 Fully Implemented Attributes

#### **Defense** (Positional)
- **Types**: Melee, Ranged, AoE
- **Power Support**: 
  - ✅ Auto powers (passive bonuses)
  - ✅ Toggle powers (with enhancement support)
  - ✅ Set bonuses
  - ✅ Global buffs
- **Features**:
  - Enhancement Diversification (ED) applied using Schedule B
  - Hard cap at 95% for all archetypes
  - Soft cap warnings at 45% (PvE)
  - Combines typed defense (smashing/lethal/etc) with positional defense

#### **Resistance** (Damage Type)
- **Types**: Smashing, Lethal, Fire, Cold, Energy, Negative, Toxic, Psionic
- **Power Support**:
  - ✅ Auto powers (passive bonuses)
  - ✅ Toggle powers (with enhancement support)
  - ✅ Set bonuses
  - ✅ Global buffs
- **Features**:
  - Enhancement Diversification (ED) applied using Schedule B
  - Archetype-specific caps (75% for most, 90% for Tanker/Brute, 85% for Kheldians)
  - Supports negative resistance (vulnerability)

#### **Damage**
- **Types**: Melee, Ranged, AoE (buff categories)
- **Power Support**:
  - ✅ Click powers (attack powers)
  - ✅ Set bonuses
  - ✅ Global buffs
  - ❌ Damage auras (toggle powers)
- **Features**:
  - Enhancement Diversification (ED) applied using Schedule A
  - Archetype-specific damage caps (300%-600%)
  - Damage scale to damage conversion based on archetype modifiers
  - Critical hit calculations for Scrappers/Stalkers
  - Resistance-adjusted damage calculations

#### **Hit Points (HP)**
- **Attributes**: Base HP, Max HP, Regeneration Rate
- **Power Support**:
  - ✅ Set bonuses (HP buffs)
  - ❌ Auto/toggle powers with HP buffs
  - ❌ Accolades
- **Features**:
  - Archetype-specific base HP and caps
  - Regeneration rate fixed at 0.42% per second

#### **Endurance**
- **Attributes**: Max Endurance, Recovery Rate, Cost Reduction
- **Power Support**:
  - ✅ Click powers (endurance cost calculation)
  - ✅ Toggle powers (endurance per second)
  - ✅ Enhancement reduction (Schedule A)
  - ❌ Recovery buffs from powers
- **Features**:
  - Base recovery of 1.67/sec
  - Minimum cost floor at 10% of base
  - Toggle cost calculations

#### **Recharge**
- **Attributes**: Recharge Time Reduction
- **Power Support**:
  - ✅ All power types (recharge reduction)
  - ✅ Set bonuses
  - ✅ Global buffs
- **Features**:
  - Enhancement Diversification (ED) applied using Schedule A
  - Hard cap at +500% recharge
  - Minimum recharge time of 0.5 seconds
  - Perma-power calculations
  - Attack chain timing

#### **Accuracy**
- **Attributes**: Accuracy Multiplier
- **Power Support**:
  - ✅ All attack powers
  - ✅ Set bonuses
  - ✅ Enhancement values
- **Features**:
  - Enhancement Diversification (ED) applied using Schedule A
  - Cap at 95% final tohit
  - Floor at 5% final tohit

### 1.2 Partially Implemented Attributes

#### **Movement**
- **Types**: Run Speed, Fly Speed, Jump Height, Jump Speed
- **Implementation**: Base values only, no power/enhancement support
- **Missing**: Speed buffs from powers, travel power calculations

#### **Stealth/Perception**
- **Types**: PvE and PvP values
- **Implementation**: Base values only
- **Missing**: Stealth powers, perception buffs

### 1.3 Not Implemented Attributes

#### **Healing**
- No heal amount calculations
- No heal enhancement support
- No heal over time calculations

#### **Mez Protection/Duration**
- No hold/stun/sleep/immobilize protection
- No mez duration calculations
- No mez enhancement support

#### **ToHit Buffs/Debuffs**
- Basic accuracy implemented but no tohit buff/debuff calculations
- No defense debuff calculations

#### **Range/Radius**
- Base values stored but no enhancement calculations
- No cone angle calculations

#### **Buff/Debuff Powers**
- No buff duration calculations
- No debuff resistance calculations
- No buff/debuff enhancement support

## 2. Power Type Support Analysis

### 2.1 Auto Powers (Always On)
- **Supported Effects**:
  - ✅ Defense bonuses (all positional types)
  - ✅ Resistance bonuses (all damage types)
  - ❌ HP/Endurance/Recovery bonuses
  - ❌ Movement bonuses
  - ❌ Other passive effects

### 2.2 Toggle Powers
- **Supported Effects**:
  - ✅ Defense bonuses (with enhancement)
  - ✅ Resistance bonuses (with enhancement)
  - ✅ Endurance cost per second
  - ❌ Damage auras
  - ❌ Buff/debuff auras
  - ❌ Other toggle effects

### 2.3 Click Powers
- **Supported Effects**:
  - ✅ Damage calculations
  - ✅ Endurance cost
  - ✅ Recharge time
  - ✅ Accuracy
  - ❌ Healing
  - ❌ Buffs/Debuffs
  - ❌ Summons/Pets

## 3. Calculation Flow Architecture

### 3.1 Main Calculation Pipeline
```
1. run_calculations() [calculator.py]
   ├── Process each power
   │   └── _calculate_power_stats()
   │       ├── Get power data from DB
   │       ├── Calculate enhancement values
   │       ├── Apply ED
   │       └── Calculate enhanced stats
   └── Calculate aggregate stats
       └── _calculate_aggregate_stats()
           ├── Calculate set bonuses
           ├── Calculate auto/toggle effects
           ├── Apply caps
           └── Generate totals
```

### 3.2 Enhancement Calculation Flow
```
1. _calculate_enhancement_values()
   ├── Query enhancement data
   ├── Sum enhancement bonuses by type
   ├── Apply Enhancement Diversification
   └── Return pre-ED and post-ED values
```

### 3.3 Set Bonus Calculation Flow
```
1. _calculate_set_bonuses()
   ├── Group enhancements by set
   ├── Count pieces per power
   ├── Apply Rule of Five
   └── Aggregate bonus values
```

## 4. Key Implementation Details

### 4.1 Enhancement Diversification (ED)
- Three schedules implemented (A, B, C)
- Schedule A: Standard attributes (damage, accuracy, endurance, recharge, heal)
- Schedule B: Defense/resistance attributes
- Schedule C: Range/cone/AoE attributes
- Proper piecewise linear implementation

### 4.2 Archetype-Specific Mechanics
- Damage scale modifiers per archetype
- Resistance caps varying by archetype
- HP base and caps per archetype
- Critical hit mechanics for Scrappers/Stalkers

### 4.3 Database Integration
- Powers loaded from database with fallback defaults
- Enhancements loaded with effects field support
- Set bonuses queried from database
- Archetype data partially from database, partially hardcoded

## 5. Missing Functionality Analysis

### 5.1 High Priority Missing Features
1. **Heal Calculations**
   - No heal amount calculations
   - No heal enhancement support
   - Critical for Defenders/Controllers/Corruptors

2. **Buff/Debuff Calculations**
   - No buff power effects
   - No debuff calculations
   - No buff/debuff enhancements

3. **ToHit Buff/Debuff System**
   - Only basic accuracy implemented
   - No tohit buff calculations
   - No defense debuff support

### 5.2 Medium Priority Missing Features
1. **Movement Speed Calculations**
   - Only base values
   - No travel power support
   - No speed buff calculations

2. **Mez System**
   - No mez protection calculations
   - No mez duration support
   - No mez enhancement

3. **Range/Radius Enhancement**
   - Base values only
   - No enhancement support
   - No cone calculations

### 5.3 Low Priority Missing Features
1. **Pet/Summon Calculations**
2. **Proc Calculations**
3. **Incarnate Power Support**
4. **PvP-specific Calculations**

## 6. Recommendations

### 6.1 Immediate Actions
1. Implement heal calculations module (calc/heal.py)
2. Add buff/debuff calculation support
3. Extend auto/toggle power effects to support more attribute types

### 6.2 Short-term Improvements
1. Complete tohit buff/debuff system
2. Add movement speed calculations
3. Implement basic mez calculations

### 6.3 Long-term Goals
1. Full pet/summon support
2. Proc chance calculations
3. Incarnate system support
4. Complete PvP calculations

## 7. Reference Files Mapping

### 7.1 Enhancement Diversification (ED)
**mids-hero-web**: `/backend/app/calc/ed.py`
**MidsReborn source**: `/external/MidsReborn/MidsReborn/Core/Enhancement.cs`
- Key method: `ApplyED()` (line 456) in MidsReborn → `apply_ed()` in mids-hero-web
- Both implement the same piecewise linear function with ED schedules A, B, and C

### 7.2 Damage Calculations
**mids-hero-web**: `/backend/app/calc/damage.py`
**MidsReborn sources**:
- `/external/MidsReborn/MidsReborn/Core/Base/Data_Classes/Power.cs`
  - Methods: `FXGetDamageValue()` (line 775), `GetDamageTip()` (line 856)
- `/external/MidsReborn/MidsReborn/Core/Base/Data_Classes/Effect.cs`
  - Method: `GetDamage()` (line 2703)

### 7.3 Recharge Calculations
**mids-hero-web**: `/backend/app/calc/recharge.py`
**MidsReborn sources**:
- Distributed across multiple files:
  - `/external/MidsReborn/MidsReborn/Core/Build.cs`
  - `/external/MidsReborn/MidsReborn/Core/Base/Data_Classes/Power.cs`

### 7.4 Endurance Calculations
**mids-hero-web**: `/backend/app/calc/endurance.py`
**MidsReborn sources**:
- Integrated into power and effect calculations:
  - `/external/MidsReborn/MidsReborn/Core/Base/Data_Classes/Power.cs`
  - `/external/MidsReborn/MidsReborn/Core/Base/Data_Classes/Effect.cs`

### 7.5 Set Bonus Calculations
**mids-hero-web**: `/backend/app/calc/setbonus.py`
**MidsReborn sources**:
- `/external/MidsReborn/MidsReborn/Core/EnhancementSet.cs`
- `/external/MidsReborn/MidsReborn/Core/I9SetData.cs`
- `/external/MidsReborn/MidsReborn/Core/Build.cs`

### 7.6 Archetype Caps
**mids-hero-web**: `/backend/app/calc/caps.py`
**MidsReborn sources**:
- `/external/MidsReborn/MidsReborn/Core/Base/Data_Classes/Archetype.cs`
- Cap enforcement distributed throughout calculation logic

### 7.7 Defense/Resistance/Accuracy/ToHit
**mids-hero-web**: Implemented within calculator service and various calc modules
**MidsReborn sources**:
- `/external/MidsReborn/MidsReborn/Core/Build.cs`
- `/external/MidsReborn/MidsReborn/clsOutput.cs`
- Various form files: `frmTotals.cs`, `frmStats.cs`

### 7.8 Main Calculator Orchestration
**mids-hero-web**: `/backend/app/services/calculator.py`
**MidsReborn sources**:
- `/external/MidsReborn/MidsReborn/Core/Build.cs` - Main build calculation logic
- `/external/MidsReborn/MidsReborn/clsOutput.cs` - Output formatting and aggregation

### 7.9 Additional MidsReborn Reference Files
- **Constants and Enums**: `/external/MidsReborn/MidsReborn/Core/Enums.cs`
- **Database API**: `/external/MidsReborn/MidsReborn/Core/DatabaseAPI.cs`
- **Configuration**: `/external/MidsReborn/MidsReborn/Core/ConfigData.cs`

## 8. Code Quality Observations

### 8.1 Strengths
- Well-structured modular design
- Good separation of concerns
- Comprehensive ED implementation
- Proper type hints and documentation

### 8.2 Areas for Improvement
- Some hardcoded values that should be in database
- Missing comprehensive tests for all calculation paths
- Some calculation modules could be more generic/reusable

### 8.3 Implementation Differences
1. **Architecture**: MidsReborn uses C# with object-oriented design, while mids-hero-web uses Python with modular functions
2. **Data Access**: MidsReborn uses in-memory database objects, mids-hero-web uses SQLAlchemy ORM
3. **Calculation Flow**: MidsReborn integrates calculations throughout the object model, mids-hero-web separates them into discrete modules
4. **ED Implementation**: Both follow the same mathematical model but with different code structures

## Conclusion

The Mids Hero Web backend has a solid foundation for character build calculations, with comprehensive support for defense, resistance, damage, endurance, and recharge calculations. However, significant gaps exist in healing, buff/debuff, and various secondary systems. The architecture is well-designed to support adding these missing features incrementally. The reference mapping to MidsReborn source files provides a clear path for implementing missing features by studying the original C# implementation.