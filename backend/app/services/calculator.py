"""Calculator orchestration service.

This module coordinates all calculation logic for character builds.
"""

import logging
from datetime import datetime

from sqlalchemy.orm import Session

from app import models
from app.calc.tohit import ToHitCalculator
from app.calc_schemas.build import BuildPayload
from app.calc_schemas.response import (
    AggregateStats,
    CalcResponse,
    CombatTotals,
    DamageBuffTotals,
    DefenseTotals,
    EnduranceStats,
    EnhancementValues,
    HitPointStats,
    MovementStats,
    PerPowerStats,
    PowerStatBlock,
    ResistanceTotals,
    SetBonusDetail,
    StealthPerceptionStats,
    ValidationWarning,
)
from app.config.constants import (
    ARCHETYPE_CAPS,
    BASE_ENDURANCE,
    BASE_MOVEMENT,
    BASE_STEALTH_PERCEPTION,
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

    # Get archetype data from database
    archetype_name = build.build.archetype
    archetype_record = db.query(models.Archetype).filter(
        models.Archetype.name == archetype_name
    ).first()

    if not archetype_record:
        # Fallback to hardcoded data if not in database
        archetype_data = ARCHETYPE_CAPS.get(archetype_name)
        if not archetype_data:
            raise ValueError(f"Unknown archetype: {archetype_name}")
    else:
        # Use database values for caps (TODO: Add cap columns to archetype table)
        # For now, still use hardcoded caps
        archetype_data = ARCHETYPE_CAPS.get(archetype_name, {
            "damage_cap": 4.0,
            "resistance_cap": 0.75,
            "defense_cap": 0.95,
            "hp_base": archetype_record.hit_points_base or 1000,
            "hp_max": archetype_record.hit_points_max or 1606,
        })

    # Process each power
    for power_data in build.powers:
        power_stats = _calculate_power_stats(
            power_data,
            build.global_buffs,
            db,
            archetype_name,
            build.build.level
        )
        per_power_stats.append(power_stats)

    # Calculate aggregate stats
    aggregate_stats = _calculate_aggregate_stats(
        build, archetype_data, validation_warnings, db
    )

    # Create response
    response = CalcResponse(
        timestamp=datetime.utcnow(),
        build_name=build.build.name,
        archetype=archetype_name,
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
    from app.calc.healing import calc_base_heal, calc_final_healing
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
            healing=0.0,
            endurance_cost=10.0,
            recharge_time=10.0,
            accuracy=1.0,
            activation_time=1.5,
            range=80.0,
            radius=0.0,
            hit_chance=0.0,  # Will be calculated later
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

        # Extract healing scale from power effects
        heal_scale = 0.0
        if power.effects and isinstance(power.effects, dict):
            heal_scale = float(power.effects.get("heal_scale", 0.0))

        healing_value = 0.0
        if heal_scale > 0:
            healing_value = calc_base_heal(
                heal_scale,
                archetype,
                level
            )

        base_stats = PowerStatBlock(
            damage=damage_value,
            healing=healing_value,
            endurance_cost=float(power.endurance_cost or 10.0),
            recharge_time=float(power.recharge_time or 10.0),
            accuracy=float(power.accuracy or 1.0),
            activation_time=float(power.activation_time or 1.5),
            range=float(power.range_feet or 80),
            radius=float(power.radius_feet or 0),
            hit_chance=0.0,  # Will be calculated later
        )

    # Calculate enhancement values from slot data
    enhancement_data = _calculate_enhancement_values(power_data.slots, db)
    pre_ed_values = enhancement_data["pre_ed"]
    post_ed_values = enhancement_data["post_ed"]

    # Calculate enhanced values using actual formulas
    # calc_final_damage expects pre-ED percentage as decimal
    enhanced_damage = calc_final_damage(
        base_stats.damage,
        pre_ed_values["damage"] / 100.0,  # Convert percentage to decimal
        global_buffs.damage / 100.0,  # Convert percentage to decimal
        archetype,
    )

    # Calculate enhanced healing
    enhanced_healing = 0.0
    if base_stats.healing > 0:
        enhanced_healing = calc_final_healing(
            base_stats.healing,
            pre_ed_values["heal"] / 100.0,  # Convert percentage to decimal
            global_buffs.healing / 100.0 if hasattr(global_buffs, 'healing') else 0.0,
            archetype
        )

    enhanced_end_cost = calc_end_cost(
        base_stats.endurance_cost,
        post_ed_values["endurance"],
        0.0,  # No global endurance reduction in this example
    )

    enhanced_recharge = calc_recharge(
        base_stats.recharge_time,
        post_ed_values["recharge"],
        global_buffs.recharge / 100.0,  # Convert percentage to decimal
    )

    # Calculate enhanced accuracy (simple formula for now)
    enhanced_accuracy = base_stats.accuracy * (1.0 + post_ed_values["accuracy"] / 100.0)

    # Calculate hit chance using ToHit system
    # For now, calculate against a standard target with no defense
    # TODO: Add support for calculating against specific defense values
    tohit_calc = ToHitCalculator()
    tohit_buffs_total = enhancement_data.get("tohit_buffs", 0.0) / 100.0  # ToHit buffs from enhancements/powers
    hit_chance = tohit_calc.calculate_power_hit_chance(
        power_accuracy=base_stats.accuracy,
        tohit_buffs=tohit_buffs_total,
        target_defense=0.0,  # Base calculation assumes no defense
        accuracy_enhancements=post_ed_values["accuracy"] / 100.0,
        global_accuracy_bonus=0.0,  # TODO: Add global accuracy from set bonuses
        attacker_level=level,
        target_level=level,  # Assume even-con for now
        is_pvp=False
    ) * 100.0  # Convert back to percentage

    enhanced_stats = PowerStatBlock(
        damage=enhanced_damage,
        healing=enhanced_healing,
        endurance_cost=enhanced_end_cost,
        recharge_time=enhanced_recharge,
        accuracy=enhanced_accuracy,
        activation_time=base_stats.activation_time,  # No change
        range=base_stats.range,  # TODO: Implement range enhancement
        radius=base_stats.radius,  # TODO: Implement radius enhancement
        hit_chance=hit_chance
    )

    return PerPowerStats(
        power_id=power_data.id,
        power_name=power_data.power_name,
        base_stats=base_stats,
        enhanced_stats=enhanced_stats,
        enhancement_values=EnhancementValues(
            damage=post_ed_values["damage"],
            healing=post_ed_values["heal"],
            accuracy=post_ed_values["accuracy"],
            endurance=post_ed_values["endurance"],
            recharge=post_ed_values["recharge"],
            range=post_ed_values["range"],
            tohit=enhancement_data.get("tohit_buffs", 0.0),
        ),
    )


def _calculate_aggregate_stats(
    build: BuildPayload,
    archetype_data: dict,
    validation_warnings: list[ValidationWarning],
    db: Session,
) -> AggregateStats:
    """Calculate aggregate statistics for the entire build."""
    # First, calculate set bonuses
    set_bonus_details = _calculate_set_bonuses(build, db)

    # Aggregate set bonuses by type
    set_bonus_totals = {}
    for bonus in set_bonus_details:
        for bonus_type, value in bonus.bonus_values.items():
            if bonus_type not in set_bonus_totals:
                set_bonus_totals[bonus_type] = 0.0
            set_bonus_totals[bonus_type] += value

    # Calculate passive/auto power effects
    auto_power_effects = _calculate_auto_power_effects(build, db)

    # Base HP calculation
    base_hp = archetype_data.get("base_hp", 1000.0)
    hp_cap = archetype_data.get("hp_cap", 1606)

    # Apply HP buffs from set bonuses
    hp_buff = 1.0 + set_bonus_totals.get("hp", 0.0) / 100.0
    max_hp = min(base_hp * hp_buff, hp_cap)

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

    # Apply global buffs AND set bonuses AND auto/toggle power effects to defense
    # Note: In City of Heroes, positional defense (melee/ranged/aoe) and typed defense (smashing/lethal/etc)
    # are separate. The game uses the higher of the two when calculating hit chances.
    # For simplicity, we'll add typed defense bonuses to the corresponding positional defense.
    defense_totals = DefenseTotals(
        melee=(build.global_buffs.defense.melee +
               set_bonus_totals.get("defense_melee", 0.0) +
               auto_power_effects.get("defense_melee", 0.0) +
               max(set_bonus_totals.get("defense_smashing", 0.0),
                   set_bonus_totals.get("defense_lethal", 0.0),
                   auto_power_effects.get("defense_smashing", 0.0),
                   auto_power_effects.get("defense_lethal", 0.0))),
        ranged=(build.global_buffs.defense.ranged +
                set_bonus_totals.get("defense_ranged", 0.0) +
                auto_power_effects.get("defense_ranged", 0.0) +
                max(set_bonus_totals.get("defense_energy", 0.0),
                    set_bonus_totals.get("defense_negative", 0.0),
                    auto_power_effects.get("defense_energy", 0.0),
                    auto_power_effects.get("defense_negative", 0.0))),
        aoe=(build.global_buffs.defense.aoe +
             set_bonus_totals.get("defense_aoe", 0.0) +
             auto_power_effects.get("defense_aoe", 0.0) +
             max(set_bonus_totals.get("defense_fire", 0.0),
                 set_bonus_totals.get("defense_cold", 0.0),
                 auto_power_effects.get("defense_fire", 0.0),
                 auto_power_effects.get("defense_cold", 0.0))),
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

    # Combine global buffs, auto power effects, and set bonuses for resistance
    resistance_dict = {
        "smashing": (build.global_buffs.resistance.smashing +
                    auto_power_effects.get("resistance_smashing", 0.0)),
        "lethal": (build.global_buffs.resistance.lethal +
                  auto_power_effects.get("resistance_lethal", 0.0)),
        "fire": (build.global_buffs.resistance.fire +
                auto_power_effects.get("resistance_fire", 0.0)),
        "cold": (build.global_buffs.resistance.cold +
                auto_power_effects.get("resistance_cold", 0.0)),
        "energy": (build.global_buffs.resistance.energy +
                  auto_power_effects.get("resistance_energy", 0.0)),
        "negative": (build.global_buffs.resistance.negative +
                    auto_power_effects.get("resistance_negative", 0.0)),
        "toxic": (build.global_buffs.resistance.toxic +
                 auto_power_effects.get("resistance_toxic", 0.0)),
        "psionic": (build.global_buffs.resistance.psionic +
                   auto_power_effects.get("resistance_psionic", 0.0)),
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

    # Apply global buffs AND set bonuses to damage
    damage_buff_totals = DamageBuffTotals(
        melee=build.global_buffs.damage + set_bonus_totals.get("damage", 0.0),
        ranged=build.global_buffs.damage + set_bonus_totals.get("damage", 0.0),
        aoe=build.global_buffs.damage + set_bonus_totals.get("damage", 0.0),
    )

    return AggregateStats(
        totals=combat_totals,
        defense=defense_totals,
        resistance=resistance_totals,
        damage_buff=damage_buff_totals,
        set_bonuses=set_bonus_details,  # Use the already calculated set bonuses
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
        Dictionary of enhancement type to total percentage value (post-ED)
    """
    from app.calc.ed import apply_ed, get_ed_schedule_for_type


    enhancement_totals = {
        "damage": 0.0,
        "accuracy": 0.0,
        "endurance": 0.0,
        "recharge": 0.0,
        "range": 0.0,
        "defense": 0.0,
        "resistance": 0.0,
        "heal": 0.0,
        "tohit": 0.0,  # ToHit buffs (not affected by ED)
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


        # Use the new effects field if available
        if hasattr(enhancement, 'effects') and enhancement.effects:
            # Effects field contains enhancement values as decimals
            for effect_type, effect_value in enhancement.effects.items():
                if effect_type in enhancement_totals:
                    enhancement_totals[effect_type] += effect_value
        # Check other_bonuses field for additional enhancements (like heal)
        elif hasattr(enhancement, 'other_bonuses') and enhancement.other_bonuses:
            for effect_type, effect_value in enhancement.other_bonuses.items():
                if effect_type in enhancement_totals:
                    enhancement_totals[effect_type] += effect_value
        else:
            # Fallback to individual bonus fields (stored as percentages)
            if hasattr(enhancement, 'damage_bonus') and enhancement.damage_bonus:
                enhancement_totals["damage"] += float(enhancement.damage_bonus)
            if hasattr(enhancement, 'accuracy_bonus') and enhancement.accuracy_bonus:
                enhancement_totals["accuracy"] += float(enhancement.accuracy_bonus)
            if hasattr(enhancement, 'endurance_bonus') and enhancement.endurance_bonus:
                enhancement_totals["endurance"] += float(enhancement.endurance_bonus)
            if hasattr(enhancement, 'recharge_bonus') and enhancement.recharge_bonus:
                enhancement_totals["recharge"] += float(enhancement.recharge_bonus)
            if hasattr(enhancement, 'defense_bonus') and enhancement.defense_bonus:
                enhancement_totals["defense"] += float(enhancement.defense_bonus)
            if hasattr(enhancement, 'resistance_bonus') and enhancement.resistance_bonus:
                enhancement_totals["resistance"] += float(enhancement.resistance_bonus)

        # TODO: Handle boosted (+5 levels) and catalyzed (attuned) enhancements
        # TODO: Handle level scaling for IOs vs SOs

    # Apply Enhancement Diversification to each enhancement type
    ed_totals = {}
    pre_ed_totals = {}
    for enh_type, total_value in enhancement_totals.items():
        pre_ed_totals[enh_type] = total_value
        if total_value > 0:
            schedule = get_ed_schedule_for_type(enh_type)
            # Convert percentage to decimal for ED calculation
            ed_value = apply_ed(schedule, total_value / 100.0)
            # Convert back to percentage
            ed_totals[enh_type] = ed_value * 100.0
            # Debug logging
            if enh_type == "damage" and total_value > 100:
                logger.debug(f"ED Debug - Type: {enh_type}, Pre-ED: {total_value}%, Schedule: {schedule}, Post-ED: {ed_value * 100.0}%")
        else:
            ed_totals[enh_type] = 0.0

    # Return both pre-ED (for damage calc) and post-ED (for display) values
    # Also include tohit_buffs separately since they're not affected by ED
    return {
        "pre_ed": pre_ed_totals,
        "post_ed": ed_totals,
        "tohit_buffs": enhancement_totals.get("tohit", 0.0)
    }


def _calculate_auto_power_effects(build: BuildPayload, db: Session) -> dict[str, float]:
    """Calculate passive effects from auto and toggle powers.
    
    Auto powers are always-on powers that provide passive bonuses.
    Toggle powers are powers that can be activated/deactivated and provide
    ongoing bonuses while active (with endurance cost).
    
    Args:
        build: Build configuration
        db: Database session
        
    Returns:
        Dictionary of effect type to total value
    """
    auto_effects = {}


    # Process each power to check for auto/passive/toggle effects
    for power_data in build.powers:
        # Get power from database
        power_id = power_data.id
        if isinstance(power_id, str) and power_id.isdigit():
            power_id = int(power_id)

        power = db.query(models.Power).filter(
            models.Power.id == power_id
        ).first()

        if not power:
            continue

        # Check if it's an auto or toggle power with effects
        if power.power_type in ("auto", "toggle") and power.effects:
            # Calculate enhancement values for this power if it's a toggle
            # Auto powers typically can't be enhanced for their effects
            enhancement_multiplier = 1.0

            if power.power_type == "toggle" and power_data.slots:
                # Get enhancement values for defense/resistance
                enhancement_data = _calculate_enhancement_values(power_data.slots, db)
                post_ed_values = enhancement_data["post_ed"]

                # Apply appropriate enhancement based on effect type
                # Note: We need to apply enhancements to each effect individually
                temp_effects = {}


                for effect_name, effect_value in power.effects.items():
                    if effect_name.startswith("defense_"):
                        # Apply defense enhancement
                        enhancement_bonus = post_ed_values.get("defense", 0.0) / 100.0
                        enhanced_value = effect_value * (1.0 + enhancement_bonus)
                        temp_effects[effect_name] = enhanced_value
                    elif effect_name.startswith("resistance_"):
                        # Apply resistance enhancement
                        enhancement_bonus = post_ed_values.get("resistance", 0.0) / 100.0
                        enhanced_value = effect_value * (1.0 + enhancement_bonus)
                        temp_effects[effect_name] = enhanced_value
                    else:
                        # No enhancement for other effects
                        temp_effects[effect_name] = effect_value

                # Add enhanced effects
                for effect_name, effect_value in temp_effects.items():
                    if effect_name not in auto_effects:
                        auto_effects[effect_name] = 0.0
                    # Convert to percentage for consistency
                    if effect_name.startswith(("resistance_", "defense_")):
                        auto_effects[effect_name] += effect_value * 100
                    else:
                        auto_effects[effect_name] += effect_value
            else:
                # Auto power or toggle without enhancements
                for effect_name, effect_value in power.effects.items():
                    if effect_name not in auto_effects:
                        auto_effects[effect_name] = 0.0
                    # Convert percentage to decimal if needed
                    if isinstance(effect_value, (int, float)):
                        # Resistance/defense values are stored as decimals (0.15 = 15%)
                        # Convert to percentage for consistency
                        if effect_name.startswith(("resistance_", "defense_")):
                            auto_effects[effect_name] += effect_value * 100
                        else:
                            auto_effects[effect_name] += effect_value

    return auto_effects


def _calculate_set_bonuses(build: BuildPayload, db: Session) -> list[SetBonusDetail]:
    """Calculate set bonuses from slotted enhancements.

    Args:
        build: Build configuration
        db: Database session

    Returns:
        List of active set bonuses
    """
    from app.calc.setbonus import calculate_set_bonus_totals

    # Collect all enhancement slots from all powers
    all_slots = []
    for power in build.powers:
        for slot in power.slots:
            # Get enhancement details to find set membership
            enh_id = slot.enhancement_id
            if isinstance(enh_id, str) and enh_id.isdigit():
                enh_id = int(enh_id)

            enhancement = None
            if isinstance(enh_id, int):
                enhancement = db.query(models.Enhancement).filter(
                    models.Enhancement.id == enh_id
                ).first()
            else:
                enhancement = db.query(models.Enhancement).filter(
                    models.Enhancement.name == enh_id
                ).first()

            if enhancement and enhancement.set_id:
                # Get the enhancement set
                enh_set = db.query(models.EnhancementSet).filter(
                    models.EnhancementSet.id == enhancement.set_id
                ).first()

                if enh_set:
                    all_slots.append({
                        "power_id": power.id,
                        "set_name": enh_set.name,
                        "enhancement_id": enhancement.id,
                    })

    # Calculate bonuses using the setbonus module
    result = calculate_set_bonus_totals(all_slots, db)

    # Convert to response format
    bonus_details = []
    for detail in result.get("details", []):
        bonus_details.append(SetBonusDetail(
            set_name=detail["set_name"],
            bonus_tier=detail["bonus_tier"],
            bonus_description=detail["bonus_description"],
            bonus_values=detail["bonus_values"]
        ))

    return bonus_details
