"""Calculator orchestration service.

This module coordinates all calculation logic for character builds.
"""

import logging
from datetime import datetime

from sqlalchemy.orm import Session

from app import models
from app.config.constants import (
    ARCHETYPE_CAPS,
    BASE_ENDURANCE,
    BASE_MOVEMENT,
    BASE_STEALTH_PERCEPTION,
)
from app.calc_schemas.build import BuildPayload
from app.calc_schemas.response import (
    AggregateStats,
    CalcResponse,
    CombatTotals,
    DamageBuffTotals,
    DefenseTotals,
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


def run_calculations(build: BuildPayload, db: Session) -> CalcResponse:
    """Run all calculations for a character build.

    This is the main orchestration function that coordinates:
    1. Power enhancement calculations
    2. Set bonus aggregation
    3. Global buff application
    4. Cap enforcement
    5. Final stat totaling

    Args:
        build: Complete build configuration
        db: Database session for querying power/enhancement data

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
        power_stats = _calculate_power_stats(
            power_data, 
            build.global_buffs, 
            db,
            archetype,
            build.build.level
        )
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


def _calculate_power_stats(
    power_data, 
    global_buffs, 
    db: Session,
    archetype: str,
    level: int
) -> PerPowerStats:
    """Calculate enhanced statistics for a single power.

    Uses the actual calculation modules for accurate results.
    """
    from app.calc.damage import calc_damage_scale_to_damage, calc_final_damage
    from app.calc.endurance import calc_end_cost
    from app.calc.recharge import calc_recharge

    # Get actual power data from database
    # Handle both string and integer IDs
    power_id = power_data.id
    if isinstance(power_id, str) and power_id.isdigit():
        power_id = int(power_id)
    
    power = db.query(models.Power).filter(
        models.Power.id == power_id
    ).first()
    
    if not power:
        # Fallback to placeholder values if power not found
        logger.warning(f"Power {power_data.id} not found in database, using defaults")
        base_stats = PowerStatBlock(
            damage=50.0,
            endurance_cost=10.0,
            recharge_time=10.0,
            accuracy=1.0,
            activation_time=1.5,
            range=80.0,
            radius=0.0,
        )
    else:
        # Use actual power data from database
        # Convert damage scale to actual damage using archetype modifiers
        damage_value = 0.0
        if power.damage_scale:
            # Determine power type from power data (simplified)
            power_type = "ranged" if power.range_feet and power.range_feet > 7 else "melee"
            damage_value = calc_damage_scale_to_damage(
                float(power.damage_scale),
                archetype,
                level,
                power_type
            )
        
        base_stats = PowerStatBlock(
            damage=damage_value,
            endurance_cost=float(power.endurance_cost or 10.0),
            recharge_time=float(power.recharge_time or 10.0),
            accuracy=float(power.accuracy or 1.0),
            activation_time=float(power.activation_time or 1.5),
            range=float(power.range_feet or 80),
            radius=float(power.radius_feet or 0),
        )

    # Calculate enhancement values from slot data
    enhancement_values = _calculate_enhancement_values(power_data.slots, db)

    # Calculate enhanced values using actual formulas
    enhanced_damage = calc_final_damage(
        base_stats.damage,
        enhancement_values["damage"],
        global_buffs.damage / 100.0,  # Convert percentage to decimal
        archetype,
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
    archetype_data: dict,
    validation_warnings: list[ValidationWarning],
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


def _calculate_enhancement_values(
    slots: list,
    db: Session
) -> dict[str, float]:
    """Calculate total enhancement values from slotted enhancements.
    
    Args:
        slots: List of enhancement slots for the power
        db: Database session
        
    Returns:
        Dictionary of enhancement type to total percentage value
    """
    enhancement_totals = {
        "damage": 0.0,
        "accuracy": 0.0,
        "endurance": 0.0,
        "recharge": 0.0,
        "range": 0.0,
        "defense": 0.0,
        "resistance": 0.0,
    }
    
    for slot in slots:
        # Handle both string and integer enhancement IDs
        enh_id = slot.enhancement_id
        if isinstance(enh_id, int) or (isinstance(enh_id, str) and enh_id.isdigit()):
            # Query enhancement by numeric ID
            if isinstance(enh_id, str):
                enh_id = int(enh_id)
            enhancement = db.query(models.Enhancement).filter(
                models.Enhancement.id == enh_id
            ).first()
        else:
            # Query enhancement by name/internal name
            enhancement = db.query(models.Enhancement).filter(
                models.Enhancement.name == enh_id
            ).first()
        
        if not enhancement:
            logger.warning(f"Enhancement {slot.enhancement_id} not found in database")
            continue
            
        # Calculate enhancement value based on level
        # For SOs: They give their full value at their level
        # For IOs: They scale with level
        if enhancement.enhancement_type == "SO":
            # SOs give full value at their level
            level_modifier = 1.0
        else:
            # IOs scale: base_value * level / 50
            level_modifier = slot.enhancement_level / 50.0
        
        # Add bonuses from the enhancement
        if enhancement.damage_bonus:
            base_value = float(enhancement.damage_bonus) / 100.0  # Convert percentage
            enhancement_totals["damage"] += base_value * level_modifier
            
        if enhancement.accuracy_bonus:
            base_value = float(enhancement.accuracy_bonus) / 100.0
            enhancement_totals["accuracy"] += base_value * level_modifier
            
        if enhancement.endurance_bonus:
            base_value = float(enhancement.endurance_bonus) / 100.0
            enhancement_totals["endurance"] += base_value * level_modifier
            
        if enhancement.recharge_bonus:
            base_value = float(enhancement.recharge_bonus) / 100.0
            enhancement_totals["recharge"] += base_value * level_modifier
            
        # TODO: Handle boosted (+5 levels) and catalyzed (attuned) enhancements
        if slot.boosted:
            # Boosted adds 5 levels worth of enhancement
            pass
            
        if slot.catalyzed:
            # Catalyzed scales with character level
            pass
    
    return enhancement_totals


def _calculate_set_bonuses(build: BuildPayload) -> list[SetBonusDetail]:  # noqa: ARG001
    """Calculate set bonuses from slotted enhancements."""
    # TODO: This is a stub implementation
    # In a real system, we would:
    # 1. Extract enhancement sets from power slots
    # 2. Apply stacking rules
    # 3. Return active bonuses

    # For now, return empty list
    return []
