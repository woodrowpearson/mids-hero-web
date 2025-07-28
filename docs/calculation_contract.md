# Calculation Contract API Specification

This document defines the JSON schema for the build calculation API endpoints, detailing input/output formats, constants, and calculation formulas.

## POST /api/calculate

Calculates power statistics, totals, and set bonuses for a character build.

### Request Schema

```json
{
  "build": {
    "name": "string",
    "archetype": "string",  // e.g., "Blaster", "Tanker"
    "origin": "string",     // e.g., "Science", "Magic"
    "level": "integer",     // 1-50
    "alignment": "string"   // "Hero", "Villain", "Praetorian"
  },
  "powers": [
    {
      "id": "string",       // Power unique identifier
      "power_name": "string",
      "powerset": "string",
      "level_taken": "integer",
      "slots": [
        {
          "slot_index": "integer",  // 0-5
          "enhancement_id": "string",
          "enhancement_level": "integer", // Enhancement level
          "boosted": "boolean",
          "catalyzed": "boolean"
        }
      ]
    }
  ],
  "global_buffs": {
    "damage": "float",      // Global damage buff %
    "recharge": "float",    // Global recharge buff %
    "defense": {
      "melee": "float",
      "ranged": "float",
      "aoe": "float"
    },
    "resistance": {
      "smashing": "float",
      "lethal": "float",
      "fire": "float",
      "cold": "float",
      "energy": "float",
      "negative": "float",
      "toxic": "float",
      "psionic": "float"
    }
  }
}
```

### Response Schema

```json
{
  "timestamp": "string",    // ISO 8601 timestamp
  "build_name": "string",
  "archetype": "string",
  "level": "integer",
  "per_power_stats": [
    {
      "power_id": "string",
      "power_name": "string",
      "base_stats": {
        "damage": "float",
        "endurance_cost": "float",
        "recharge_time": "float",
        "accuracy": "float",
        "activation_time": "float",
        "range": "float",
        "radius": "float"
      },
      "enhanced_stats": {
        "damage": "float",
        "endurance_cost": "float",
        "recharge_time": "float",
        "accuracy": "float",
        "range": "float",
        "radius": "float"
      },
      "enhancement_values": {
        "damage": "float",      // Total enhancement % after ED
        "accuracy": "float",
        "endurance": "float",
        "recharge": "float",
        "range": "float"
      }
    }
  ],
  "aggregate_stats": {
    "totals": {
      "hit_points": {
        "base": "float",
        "max": "float",
        "regeneration_rate": "float"
      },
      "endurance": {
        "max": "float",
        "recovery_rate": "float"
      },
      "movement": {
        "run_speed": "float",
        "fly_speed": "float",
        "jump_height": "float",
        "jump_speed": "float"
      },
      "stealth": {
        "pve": "float",
        "pvp": "float"
      },
      "perception": {
        "pve": "float",
        "pvp": "float"
      }
    },
    "defense": {
      "melee": "float",
      "ranged": "float",
      "aoe": "float"
    },
    "resistance": {
      "smashing": "float",
      "lethal": "float",
      "fire": "float",
      "cold": "float",
      "energy": "float",
      "negative": "float",
      "toxic": "float",
      "psionic": "float"
    },
    "damage_buff": {
      "melee": "float",
      "ranged": "float",
      "aoe": "float"
    },
    "set_bonuses": [
      {
        "set_name": "string",
        "bonus_tier": "integer",
        "bonus_description": "string",
        "bonus_values": {
          "attribute": "string",
          "value": "float"
        }
      }
    ]
  },
  "validation_warnings": [
    {
      "type": "string",     // "cap_exceeded", "invalid_slot", etc.
      "message": "string",
      "affected_stat": "string"
    }
  ]
}
```

## Constants and Caps

### Archetype-Specific Caps

| Archetype        | Damage Cap | Resistance Cap | HP Cap | Defense Hard Cap |
|------------------|------------|----------------|--------|------------------|
| Blaster          | 400%       | 75%            | 1606   | 95%              |
| Controller       | 300%       | 75%            | 1606   | 95%              |
| Defender         | 300%       | 75%            | 1606   | 95%              |
| Scrapper         | 400%       | 75%            | 2088   | 95%              |
| Tanker           | 300%       | 90%            | 3534   | 95%              |
| Brute            | 600%       | 90%            | 3212   | 95%              |
| Stalker          | 400%       | 75%            | 1606   | 95%              |
| Mastermind       | 300%       | 75%            | 1606   | 95%              |
| Dominator        | 300%       | 75%            | 1606   | 95%              |
| Corruptor        | 400%       | 75%            | 1606   | 95%              |
| Arachnos Soldier | 400%       | 75%            | 1606   | 95%              |
| Arachnos Widow   | 400%       | 75%            | 1606   | 95%              |
| Peacebringer     | 300%       | 85%            | 2088   | 95%              |
| Warshade         | 300%       | 85%            | 2088   | 95%              |
| Sentinel         | 400%       | 75%            | 1606   | 95%              |

### Global Constants

```python
# Enhancement Diversification (ED) Thresholds
ED_SCHEDULE_A = {
    "thresholds": [0, 0.95, 1.70, 2.60],
    "multipliers": [1.0, 0.9, 0.7, 0.15]
}

ED_SCHEDULE_B = {
    "thresholds": [0, 0.40, 0.80, 1.20],
    "multipliers": [1.0, 0.9, 0.7, 0.15]
}

ED_SCHEDULE_C = {
    "thresholds": [0, 0.25, 0.50, 0.75],
    "multipliers": [1.0, 0.9, 0.7, 0.15]
}

# Global Caps
RECHARGE_CAP = 5.0          # +500% max global recharge
DEFENSE_HARD_CAP = 0.95     # 95% hard cap all ATs
DEFENSE_SOFT_CAP_PVE = 0.45 # 45% soft cap PvE
DEFENSE_SOFT_CAP_PVP = 0.45 # 45% soft cap PvP
ENDURANCE_MIN_COST = 0.1    # Minimum 10% of base cost

# PvP Modifiers
PVP_DAMAGE_MODIFIER = 0.5   # Damage halved in PvP
```

## Calculation Formulas

### Damage Calculation
```
Final Damage = Base Damage × (1 + ED(Damage Enhancement %) + Global Damage Buff %)
Cap at: Archetype Damage Cap
```

### Endurance Cost
```
Final Cost = Base Cost / (1 + ED(Endurance Reduction %) + Global End Redux %)
Floor at: 0.10 × Base Cost
```

### Recharge Time
```
Final Recharge = Base Recharge / (1 + ED(Recharge Enhancement %) + Global Recharge %)
Cap at: +500% (6x speed)
Minimum: 0.5 seconds per power
```

### Defense Totals
```
Total Defense = Sum(All Defense Buffs) - Sum(All Defense Debuffs)
Hard Cap: 95%
```

### Resistance Totals
```
Total Resistance = Sum(All Resistance Buffs) - Sum(All Resistance Debuffs)
Cap at: Archetype Resistance Cap
```

### Max HP
```
Final Max HP = min(Base HP × (1 + Max HP Buff %), Archetype HP Cap)
```

### Enhancement Diversification (ED)
```python
def apply_ed(schedule: str, enhancement_value: float) -> float:
    """Apply ED based on schedule type (A, B, or C)"""
    thresholds = ED_SCHEDULE[schedule]["thresholds"]
    multipliers = ED_SCHEDULE[schedule]["multipliers"]
    
    total = 0.0
    remaining = enhancement_value
    
    for i in range(len(thresholds) - 1):
        segment = min(remaining, thresholds[i + 1] - thresholds[i])
        total += segment * multipliers[i]
        remaining -= segment
        if remaining <= 0:
            break
    
    if remaining > 0:
        total += remaining * multipliers[-1]
    
    return total
```

### Set Bonus Stacking
- Each unique set bonus can only be counted once
- Maximum 5 of the same set across build
- Bonuses are additive with global buffs

## Error Codes

| Code | Type                | Description                                     |
|------|---------------------|-------------------------------------------------|
| 400  | Invalid Request     | Unknown power ID, invalid slot configuration   |
| 422  | Validation Error    | Schema validation failed                        |
| 500  | Calculation Error   | Internal calculation error                      |

## Performance Requirements

- Target response time: ≤ 30ms for 100-power payload
- Concurrent request handling: 100 req/s minimum
- Memory usage: < 50MB per request