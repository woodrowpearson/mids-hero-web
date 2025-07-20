"""Calculator orchestration service.

This module coordinates all calculation logic for character builds.
"""

import logging
from datetime import datetime
from typing import Dict, List

from app.config.constants import (
    ARCHETYPE_CAPS,
    BASE_ENDURANCE,
    BASE_MOVEMENT,
    BASE_STEALTH_PERCEPTION,
    get_archetype_cap,
)
from app.schemas.build import BuildPayload
from app.schemas.response import (
    AggregateStats,
    CalcResponse,
    CombatTotals,
    DefenseTotals,
    DamageBuffTotals,
    EnduranceStats,
    HitPointStats,
    MovementStats,
    PerPowerStats,
    PowerStatBlock,
    ResistanceTotals,
    SetBonusDetail,
    StealthPerceptionStats,
    ValidationWarning,
)

logger = logging.getLogger(__name__)


def run_calculations(build: BuildPayload) -> CalcResponse:
    """Run all calculations for a character build.

    This is the main orchestration function that coordinates:
    1. Power enhancement calculations
    2. Set bonus aggregation
    3. Global buff application
    4. Cap enforcement
    5. Final stat totaling

    Args:
        build: Complete build configuration

    Returns:
        Complete calculation results
    """
    logger.info(f"Starting calculations for build: {build.build.name}")

    # Initialize response data
    per_power_stats = []
    validation_warnings = []

    # Get archetype data
    archetype = build.build.archetype
    archetype_data = ARCHETYPE_CAPS.get(archetype)
    if not archetype_data:
        raise ValueError(f"Unknown archetype: {archetype}")

    # Process each power
    for power_data in build.powers:
        power_stats = _calculate_power_stats(power_data, build.global_buffs)
        per_power_stats.append(power_stats)

    # Calculate aggregate stats
    aggregate_stats = _calculate_aggregate_stats(
        build, archetype_data, validation_warnings
    )

    # Create response
    response = CalcResponse(
        timestamp=datetime.utcnow(),
        build_name=build.build.name,
        archetype=archetype,
        level=build.build.level,
        per_power_stats=per_power_stats,
        aggregate_stats=aggregate_stats,
        validation_warnings=validation_warnings,
    )

    logger.info(
        f"Calculations complete for {build.build.name}: "
        f"{len(per_power_stats)} powers processed, "
        f"{len(validation_warnings)} warnings"
    )

    return response


def _calculate_power_stats(power_data, global_buffs) -> PerPowerStats:
    """Calculate enhanced statistics for a single power.

    Uses the actual calculation modules for accurate results.
    """
    from app.calc.damage import calc_final_damage
    from app.calc.endurance import calc_end_cost
    from app.calc.recharge import calc_recharge
    
    # TODO: Get actual base stats from database
    # For now, use placeholder values
    base_stats = PowerStatBlock(
        damage=50.0,
        endurance_cost=10.0,
        recharge_time=10.0,
        accuracy=1.0,
        activation_time=1.5,
        range=80.0,
        radius=0.0,
    )
    
    # TODO: Calculate enhancement values from slot data
    # For now, use common values
    enhancement_values = {
        "damage": 0.95,  # 95% damage enhancement
        "accuracy": 0.95,  # 95% accuracy enhancement
        "endurance": 0.50,  # 50% endurance reduction
        "recharge": 0.50,  # 50% recharge reduction
        "range": 0.0,  # No range enhancement
    }
    
    # Calculate enhanced values using actual formulas
    enhanced_damage = calc_final_damage(
        base_stats.damage,
        enhancement_values["damage"],
        global_buffs.damage / 100.0,  # Convert percentage to decimal
        "Blaster",  # TODO: Get from build data
    )
    
    enhanced_end_cost = calc_end_cost(
        base_stats.endurance_cost,
        enhancement_values["endurance"],
        0.0,  # No global endurance reduction in this example
    )
    
    enhanced_recharge = calc_recharge(
        base_stats.recharge_time,
        enhancement_values["recharge"],
        global_buffs.recharge / 100.0,  # Convert percentage to decimal
    )
    
    # Calculate enhanced accuracy (simple formula for now)
    enhanced_accuracy = base_stats.accuracy * (1.0 + enhancement_values["accuracy"])
    
    enhanced_stats = PowerStatBlock(
        damage=enhanced_damage,
        endurance_cost=enhanced_end_cost,
        recharge_time=enhanced_recharge,
        accuracy=enhanced_accuracy,
        activation_time=base_stats.activation_time,  # No change
        range=base_stats.range,  # TODO: Implement range enhancement
        radius=base_stats.radius,  # TODO: Implement radius enhancement
    )

    return PerPowerStats(
        power_id=power_data.id,
        power_name=power_data.power_name,
        base_stats=base_stats,
        enhanced_stats=enhanced_stats,
        enhancement_values={
            k: v * 100 for k, v in enhancement_values.items()  # Convert to percentage
        },
    )


def _calculate_aggregate_stats(
    build: BuildPayload,
    archetype_data: Dict,
    validation_warnings: List[ValidationWarning],
) -> AggregateStats:
    """Calculate aggregate statistics for the entire build."""
    # Base HP calculation
    base_hp = archetype_data.get("base_hp", 1000.0)
    hp_cap = archetype_data.get("hp_cap", 1606)

    # Apply HP buffs (stub for now)
    max_hp = min(base_hp * 1.0, hp_cap)  # No HP buffs in stub

    # Create combat totals
    combat_totals = CombatTotals(
        hit_points=HitPointStats(
            base=base_hp,
            max=max_hp,
            regeneration_rate=base_hp * 0.0042,  # 0.42% per second
        ),
        endurance=EnduranceStats(
            max=BASE_ENDURANCE["max"],
            recovery_rate=BASE_ENDURANCE["recovery_rate"],
        ),
        movement=MovementStats(
            run_speed=BASE_MOVEMENT["run_speed"],
            fly_speed=BASE_MOVEMENT["fly_speed"],
            jump_height=BASE_MOVEMENT["jump_height"],
            jump_speed=BASE_MOVEMENT["jump_speed"],
        ),
        stealth=StealthPerceptionStats(
            pve=BASE_STEALTH_PERCEPTION["stealth_pve"],
            pvp=BASE_STEALTH_PERCEPTION["stealth_pvp"],
        ),
        perception=StealthPerceptionStats(
            pve=BASE_STEALTH_PERCEPTION["perception_pve"],
            pvp=BASE_STEALTH_PERCEPTION["perception_pvp"],
        ),
    )

    # Apply global buffs to defense/resistance
    defense_totals = DefenseTotals(
        melee=build.global_buffs.defense.melee,
        ranged=build.global_buffs.defense.ranged,
        aoe=build.global_buffs.defense.aoe,
    )

    # Check defense caps using caps module
    from app.calc.caps import check_defense_caps
    
    defense_dict = {
        "melee": defense_totals.melee,
        "ranged": defense_totals.ranged,
        "aoe": defense_totals.aoe,
    }
    
    cap_warnings = []
    capped_defense = check_defense_caps(defense_dict, cap_warnings)
    
    # Update defense totals with capped values
    defense_totals = DefenseTotals(**capped_defense)
    
    # Add any warnings
    for warning in cap_warnings:
        validation_warnings.append(
            ValidationWarning(
                type=warning["type"],
                message=warning["message"],
                affected_stat=f"defense.{warning.get('def_type', 'unknown')}",
            )
        )

    # Check resistance caps using caps module
    from app.calc.caps import check_resistance_caps
    
    resistance_dict = {
        "smashing": build.global_buffs.resistance.smashing,
        "lethal": build.global_buffs.resistance.lethal,
        "fire": build.global_buffs.resistance.fire,
        "cold": build.global_buffs.resistance.cold,
        "energy": build.global_buffs.resistance.energy,
        "negative": build.global_buffs.resistance.negative,
        "toxic": build.global_buffs.resistance.toxic,
        "psionic": build.global_buffs.resistance.psionic,
    }
    
    res_warnings = []
    capped_resistance = check_resistance_caps(
        resistance_dict, 
        build.build.archetype, 
        res_warnings
    )
    
    resistance_totals = ResistanceTotals(**capped_resistance)
    
    # Add any warnings
    for warning in res_warnings:
        validation_warnings.append(
            ValidationWarning(
                type=warning["type"],
                message=warning["message"],
                affected_stat=f"resistance.{warning.get('dmg_type', 'unknown')}",
            )
        )

    damage_buff_totals = DamageBuffTotals(
        melee=build.global_buffs.damage,
        ranged=build.global_buffs.damage,
        aoe=build.global_buffs.damage,
    )

    return AggregateStats(
        totals=combat_totals,
        defense=defense_totals,
        resistance=resistance_totals,
        damage_buff=damage_buff_totals,
        set_bonuses=_calculate_set_bonuses(build),
    )


def _calculate_set_bonuses(build: BuildPayload) -> List[SetBonusDetail]:
    """Calculate set bonuses from slotted enhancements."""
    # TODO: This is a stub implementation
    # In a real system, we would:
    # 1. Extract enhancement sets from power slots
    # 2. Apply stacking rules
    # 3. Return active bonuses
    
    # For now, return empty list
    return []