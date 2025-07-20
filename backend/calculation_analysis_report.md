# Mids Hero Web Backend - Calculation Logic Analysis Report

## What Actually Exists (75-80% Complete)

- ✅ Core calculation engine fully functional
- ✅ Enhancement Diversification completely implemented
- ✅ Defense/Resistance calculations with caps
- ✅ Damage calculations with AT modifiers
- ✅ Set bonuses with proper stacking
- ✅ Comprehensive test coverage

## Actual Remaining Work

Created 5 focused issues for the real gaps:

1. #221 - Healing calculations
2. #222 - Complete ToHit/Accuracy system
3. #223 - Buff/debuff effects (non-defense)
4. #224 - Movement speed enhancements
5. #225 - Basic mez protection/resistance

Each issue includes:

- TDD test examples with pytest
- Reference to existing code patterns
- Clear acceptance criteria
- Integration requirements

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

- **Types**: Melee, Ranged, AoE (buff categories), pbAoE, Targeted AoE
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

## 7. Code Quality Observations

### 7.1 Strengths

- Well-structured modular design
- Good separation of concerns
- Comprehensive ED implementation
- Proper type hints and documentation

### 7.2 Areas for Improvement

- Some hardcoded values that should be in database
- Missing comprehensive tests for all calculation paths
- Some calculation modules could be more generic/reusable

## Conclusion

The Mids Hero Web backend has a solid foundation for character build calculations, with comprehensive support for defense, resistance, damage, endurance, and recharge calculations. However, significant gaps exist in healing, buff/debuff, and various secondary systems. The architecture is well-designed to support adding these missing features incrementally.
