"""
Calculation API endpoints for Mids-Web backend.

Phase 5: API Integration - Exposes all calculation services via FastAPI.

Endpoints:
    Core Calculations:
        - POST /api/v1/calculations/power/damage
        - POST /api/v1/calculations/power/buffs (TODO)
        - POST /api/v1/calculations/power/control (TODO)
        - POST /api/v1/calculations/power/healing (TODO)
        - POST /api/v1/calculations/power/accuracy (TODO)

    Build Calculations:
        - POST /api/v1/calculations/build/totals
        - POST /api/v1/calculations/build/defense
        - POST /api/v1/calculations/build/resistance
        - GET /api/v1/calculations/constants

    Enhancement Calculations:
        - POST /api/v1/calculations/enhancements/procs
        - POST /api/v1/calculations/enhancements/slotting (TODO)
        - POST /api/v1/calculations/enhancements/set-bonuses (TODO)
"""

from fastapi import APIRouter, HTTPException

from app.calculations.build.defense_aggregator import (
    DefenseType,
    aggregate_defense_bonuses,
)
from app.calculations.build.resistance_aggregator import (
    ResistanceType,
    aggregate_resistance_bonuses,
)

# Import calculation modules
from app.calculations.core import constants
from app.calculations.core.archetype_caps import ArchetypeType
from app.calculations.core.effect import Effect
from app.calculations.core.effect_types import DamageType, EffectType
from app.calculations.core.enums import PvMode, ToWho

# Proc calculator not yet integrated - using simplified formula in endpoint
from app.calculations.powers.damage_calculator import (
    DamageCalculator,
    DamageMathMode,
    DamageReturnMode,
    PowerType,
)
from app.schemas.calculations import (  # Request/Response models; Enums
    BuildTotalsRequest,
    BuildTotalsResponse,
    DamageCalculationRequest,
    DamageCalculationResponse,
    DamageTypeEnum,
    DefenseCalculationRequest,
    DefenseCalculationResponse,
    DefenseTypeEnum,
    ErrorResponse,
    GameConstantsResponse,
    ProcCalculationRequest,
    ProcCalculationResponse,
    ResistanceCalculationRequest,
    ResistanceCalculationResponse,
    ResistanceTypeEnum,
)

router = APIRouter()


# ============================================================================
# Helper Functions
# ============================================================================


def convert_effect_request_to_effect(effect_request) -> Effect:
    """Convert API effect request to internal Effect object."""
    # Map effect type string to EffectType enum
    effect_type_map = {
        "damage": EffectType.DAMAGE,
        "defense": EffectType.DEFENSE,
        "resistance": EffectType.RESISTANCE,
        "heal": EffectType.HEAL,
        "endurance": EffectType.ENDURANCE,
        # Add more as needed
    }

    # Map damage type
    damage_type_map = {
        "smashing": DamageType.SMASHING,
        "lethal": DamageType.LETHAL,
        "fire": DamageType.FIRE,
        "cold": DamageType.COLD,
        "energy": DamageType.ENERGY,
        "negative": DamageType.NEGATIVE,
        "toxic": DamageType.TOXIC,
        "psionic": DamageType.PSIONIC,
    }

    # Map to_who
    to_who_map = {
        "self": ToWho.SELF,
        "target": ToWho.TARGET,
        "both": ToWho.BOTH,
    }

    effect_type = effect_type_map.get(
        effect_request.effect_type.lower(), EffectType.DAMAGE
    )

    damage_type = None
    if effect_request.damage_type:
        damage_type = damage_type_map.get(effect_request.damage_type.value.lower())

    to_who = to_who_map.get(effect_request.to_who.lower(), ToWho.TARGET)

    return Effect(
        effect_type=effect_type,
        magnitude=effect_request.magnitude,
        duration=effect_request.duration,
        probability=effect_request.probability,
        damage_type=damage_type,
        ticks=effect_request.ticks,
        to_who=to_who,
        pv_mode=PvMode.PVE,
    )


def convert_archetype_enum(archetype_enum) -> ArchetypeType:
    """Convert API archetype enum to internal ArchetypeType."""
    archetype_map = {
        "Blaster": ArchetypeType.BLASTER,
        "Controller": ArchetypeType.CONTROLLER,
        "Defender": ArchetypeType.DEFENDER,
        "Scrapper": ArchetypeType.SCRAPPER,
        "Tanker": ArchetypeType.TANKER,
        "Peacebringer": ArchetypeType.PEACEBRINGER,
        "Warshade": ArchetypeType.WARSHADE,
        "Brute": ArchetypeType.BRUTE,
        "Stalker": ArchetypeType.STALKER,
        "Mastermind": ArchetypeType.MASTERMIND,
        "Dominator": ArchetypeType.DOMINATOR,
        "Corruptor": ArchetypeType.CORRUPTOR,
        "Arachnos Soldier": ArchetypeType.ARACHNOS_SOLDIER,
        "Arachnos Widow": ArchetypeType.ARACHNOS_WIDOW,
    }
    return archetype_map.get(archetype_enum.value, ArchetypeType.SCRAPPER)


def convert_defense_type_enum(defense_enum: DefenseTypeEnum) -> DefenseType:
    """Convert API defense type enum to internal DefenseType."""
    defense_map = {
        "smashing": DefenseType.SMASHING,
        "lethal": DefenseType.LETHAL,
        "fire": DefenseType.FIRE,
        "cold": DefenseType.COLD,
        "energy": DefenseType.ENERGY,
        "negative": DefenseType.NEGATIVE,
        "toxic": DefenseType.TOXIC,
        "psionic": DefenseType.PSIONIC,
        "melee": DefenseType.MELEE,
        "ranged": DefenseType.RANGED,
        "aoe": DefenseType.AOE,
    }
    return defense_map.get(defense_enum.value.lower(), DefenseType.SMASHING)


def convert_resistance_type_enum(resistance_enum: ResistanceTypeEnum) -> ResistanceType:
    """Convert API resistance type enum to internal ResistanceType."""
    resistance_map = {
        "smashing": ResistanceType.SMASHING,
        "lethal": ResistanceType.LETHAL,
        "fire": ResistanceType.FIRE,
        "cold": ResistanceType.COLD,
        "energy": ResistanceType.ENERGY,
        "negative": ResistanceType.NEGATIVE,
        "toxic": ResistanceType.TOXIC,
        "psionic": ResistanceType.PSIONIC,
    }
    return resistance_map.get(resistance_enum.value.lower(), ResistanceType.SMASHING)


# ============================================================================
# Core Calculation Endpoints
# ============================================================================


@router.post(
    "/v1/calculations/power/damage",
    response_model=DamageCalculationResponse,
    summary="Calculate power damage",
    description="""
    Calculate damage output for a power including all effects.

    Supports:
    - Multiple damage types (smashing, lethal, fire, etc.)
    - DoT effects with ticking
    - Probabilistic damage (procs)
    - Toggle powers
    - DPS and DPA calculations

    Based on MidsReborn's Power.cs FXGetDamageValue() implementation.
    """,
    responses={
        200: {"description": "Damage calculation successful"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
    },
)
async def calculate_power_damage(
    request: DamageCalculationRequest,
) -> DamageCalculationResponse:
    """Calculate damage from a power's effects."""
    try:
        # Convert request effects to internal Effect objects
        effects = [convert_effect_request_to_effect(e) for e in request.effects]

        # Convert enums
        power_type = PowerType(request.power_type.value)
        damage_math_mode = DamageMathMode(request.damage_math_mode.value)
        damage_return_mode = DamageReturnMode(request.damage_return_mode.value)

        # Create calculator
        calculator = DamageCalculator(
            archetype_damage_cap=request.archetype_damage_cap,
            damage_math_mode=damage_math_mode,
        )

        # Calculate damage
        result = calculator.calculate_power_damage(
            power_effects=effects,
            power_type=power_type,
            power_recharge_time=request.recharge_time,
            power_cast_time=request.cast_time,
            power_interrupt_time=request.interrupt_time,
            power_activate_period=request.activate_period,
            damage_return_mode=damage_return_mode,
        )

        # Convert internal DamageType to API DamageTypeEnum
        by_type_api = {}
        for dtype, value in result.by_type.items():
            # Map internal DamageType to API enum
            api_dtype = DamageTypeEnum(dtype.value)
            by_type_api[api_dtype] = value

        return DamageCalculationResponse(
            total=result.total,
            by_type=by_type_api,
            has_pvp_difference=result.has_pvp_difference,
            has_toggle_enhancements=result.has_toggle_enhancements,
            activate_period=result.activate_period,
            tooltip=result.format_tooltip(),
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Build Calculation Endpoints
# ============================================================================


@router.post(
    "/v1/calculations/build/defense",
    response_model=DefenseCalculationResponse,
    summary="Calculate build defense totals",
    description="""
    Calculate defense totals from all sources using "highest wins" logic.

    Implements:
    - Typed defenses (smashing, lethal, fire, etc.)
    - Positional defenses (melee, ranged, AoE)
    - "Highest wins" between typed and positional
    - Defense debuff resistance (DDR)
    - Archetype caps

    Based on Spec 19: Build Totals - Defense.
    """,
    responses={
        200: {"description": "Defense calculation successful"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
    },
)
async def calculate_build_defense(
    request: DefenseCalculationRequest,
) -> DefenseCalculationResponse:
    """Calculate build defense totals."""
    try:
        # Convert archetype
        archetype = convert_archetype_enum(request.archetype)

        # Convert defense bonuses
        bonuses_list = []
        for bonus_input in request.defense_bonuses:
            bonus_dict = {}
            for dtype_enum, value in bonus_input.bonuses.items():
                internal_dtype = convert_defense_type_enum(dtype_enum)
                bonus_dict[internal_dtype] = value
            bonuses_list.append(bonus_dict)

        # Aggregate bonuses
        defense_values = aggregate_defense_bonuses(bonuses_list, archetype)

        # Convert back to API enums
        typed_api = {}
        for dtype, value in defense_values.typed.items():
            api_dtype = DefenseTypeEnum(dtype.value)
            typed_api[api_dtype] = value

        positional_api = {}
        for dtype, value in defense_values.positional.items():
            api_dtype = DefenseTypeEnum(dtype.value)
            positional_api[api_dtype] = value

        return DefenseCalculationResponse(
            typed=typed_api,
            positional=positional_api,
            ddr=defense_values.ddr,
            elusivity=defense_values.elusivity,
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/v1/calculations/build/resistance",
    response_model=ResistanceCalculationResponse,
    summary="Calculate build resistance totals",
    description="""
    Calculate resistance totals from all sources using additive stacking.

    Implements:
    - Typed resistances (smashing, lethal, fire, etc.)
    - Additive stacking with archetype caps
    - Resistance debuff resistance

    Based on Spec 20: Build Totals - Resistance.
    """,
    responses={
        200: {"description": "Resistance calculation successful"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
    },
)
async def calculate_build_resistance(
    request: ResistanceCalculationRequest,
) -> ResistanceCalculationResponse:
    """Calculate build resistance totals."""
    try:
        # Convert archetype
        archetype = convert_archetype_enum(request.archetype)

        # Convert resistance bonuses
        bonuses_list = []
        for bonus_input in request.resistance_bonuses:
            bonus_dict = {}
            for rtype_enum, value in bonus_input.bonuses.items():
                internal_rtype = convert_resistance_type_enum(rtype_enum)
                bonus_dict[internal_rtype] = value
            bonuses_list.append(bonus_dict)

        # Aggregate bonuses
        resistance_values = aggregate_resistance_bonuses(bonuses_list, archetype)

        # Convert back to API enums
        values_api = {}
        for rtype, value in resistance_values.values.items():
            api_rtype = ResistanceTypeEnum(rtype.value)
            values_api[api_rtype] = value

        return ResistanceCalculationResponse(
            values=values_api,
            resistance_debuff_resistance=resistance_values.resistance_debuff_resistance,
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/v1/calculations/build/totals",
    response_model=BuildTotalsResponse,
    summary="Calculate complete build totals",
    description="""
    Calculate all build statistics in one call.

    Combines:
    - Defense calculations
    - Resistance calculations
    - (Future) Recharge, damage, accuracy, and other stats

    More efficient than calling individual endpoints separately.
    """,
    responses={
        200: {"description": "Build totals calculation successful"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
    },
)
async def calculate_build_totals(
    request: BuildTotalsRequest,
) -> BuildTotalsResponse:
    """Calculate complete build totals."""
    try:
        # Calculate defense
        defense_req = DefenseCalculationRequest(
            archetype=request.archetype,
            defense_bonuses=request.defense_bonuses,
        )
        defense_resp = await calculate_build_defense(defense_req)

        # Calculate resistance
        resistance_req = ResistanceCalculationRequest(
            archetype=request.archetype,
            resistance_bonuses=request.resistance_bonuses,
        )
        resistance_resp = await calculate_build_resistance(resistance_req)

        return BuildTotalsResponse(
            defense=defense_resp,
            resistance=resistance_resp,
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/v1/calculations/constants",
    response_model=GameConstantsResponse,
    summary="Get game constants",
    description="""
    Retrieve all fundamental game constants used in calculations.

    Includes:
    - BASE_MAGIC (1.666667) - Regeneration/recovery constant
    - Enhancement Diversification (ED) thresholds for all schedules
    - ED efficiency multipliers
    - Game tick rate
    - Enhancement values (TO/DO/SO/IO)
    - Rule of 5 limit

    These constants are from MidsReborn's Maths.mhd file.
    """,
    responses={
        200: {"description": "Constants retrieved successfully"},
    },
)
async def get_game_constants() -> GameConstantsResponse:
    """Get all game constants."""
    return GameConstantsResponse(
        base_magic=constants.BASE_MAGIC,
        ed_schedule_a_thresholds=[
            constants.ED_SCHEDULE_A_THRESH_1,
            constants.ED_SCHEDULE_A_THRESH_2,
            constants.ED_SCHEDULE_A_THRESH_3,
        ],
        ed_schedule_b_thresholds=[
            constants.ED_SCHEDULE_B_THRESH_1,
            constants.ED_SCHEDULE_B_THRESH_2,
            constants.ED_SCHEDULE_B_THRESH_3,
        ],
        ed_schedule_c_thresholds=[
            constants.ED_SCHEDULE_C_THRESH_1,
            constants.ED_SCHEDULE_C_THRESH_2,
            constants.ED_SCHEDULE_C_THRESH_3,
        ],
        ed_schedule_d_thresholds=[
            constants.ED_SCHEDULE_D_THRESH_1,
            constants.ED_SCHEDULE_D_THRESH_2,
            constants.ED_SCHEDULE_D_THRESH_3,
        ],
        ed_efficiencies=[
            constants.ED_EFFICIENCY_REGION_1,
            constants.ED_EFFICIENCY_REGION_2,
            constants.ED_EFFICIENCY_REGION_3,
            constants.ED_EFFICIENCY_REGION_4,
        ],
        game_tick_seconds=constants.GAME_TICK_SECONDS,
        rule_of_five_limit=constants.RULE_OF_FIVE_LIMIT,
        training_origin_value=constants.TRAINING_ORIGIN_VALUE,
        dual_origin_value=constants.DUAL_ORIGIN_VALUE,
        single_origin_value=constants.SINGLE_ORIGIN_VALUE,
        invention_origin_l50_value=constants.INVENTION_ORIGIN_L50_VALUE,
    )


# ============================================================================
# Enhancement Calculation Endpoints
# ============================================================================


@router.post(
    "/v1/calculations/enhancements/procs",
    response_model=ProcCalculationResponse,
    summary="Calculate proc chance",
    description="""
    Calculate proc chance using PPM (Procs Per Minute) formula.

    Formula: chance = PPM × (recharge + cast) / (60 × area_factor)

    Based on Spec 34: Proc Chances.
    """,
    responses={
        200: {"description": "Proc calculation successful"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
    },
)
async def calculate_proc_chance(
    request: ProcCalculationRequest,
) -> ProcCalculationResponse:
    """Calculate proc chance for a power."""
    try:
        # Simple PPM formula: chance = PPM × (recharge + cast) / (60 × area_factor)
        chance = (
            request.ppm
            * (request.recharge_time + request.cast_time)
            / (60 * request.area_factor)
        )

        # Apply minimum cap: PPM × 0.015 + 0.05
        min_cap = request.ppm * 0.015 + 0.05
        if chance < min_cap:
            chance = min_cap

        # Apply maximum cap: 90%
        MAX_PROC_CHANCE = 0.90
        if chance > MAX_PROC_CHANCE:
            chance = MAX_PROC_CHANCE

        # Check if capped at 90%
        capped = chance >= MAX_PROC_CHANCE

        return ProcCalculationResponse(
            chance=chance,
            chance_percent=chance * 100.0,
            capped=capped,
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
