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
    EnduranceStatsResponse,
    ErrorResponse,
    GameConstantsResponse,
    HPStatsResponse,
    MiscStatsResponse,
    ProcCalculationRequest,
    ProcCalculationResponse,
    RechargeStatsResponse,
    ResistanceCalculationRequest,
    ResistanceCalculationResponse,
    ResistanceTypeEnum,
)

router = APIRouter()


# ============================================================================
# Helper Functions
# ============================================================================


def convert_effect_request_to_effect(effect_request, unique_id: int = 0) -> Effect:
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
        # Note: "both" is not currently supported in ToWho enum
        # Effects targeting both self and target should be modeled as separate effects
    }

    effect_type = effect_type_map.get(
        effect_request.effect_type.lower(), EffectType.DAMAGE
    )

    damage_type = None
    if effect_request.damage_type:
        damage_type = damage_type_map.get(effect_request.damage_type.value.lower())

    to_who = to_who_map.get(effect_request.to_who.lower(), ToWho.TARGET)

    return Effect(
        unique_id=unique_id,
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
        "negative": DefenseType.NEGATIVE_ENERGY,
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
        "negative": ResistanceType.NEGATIVE_ENERGY,
        "toxic": ResistanceType.TOXIC,
        "psionic": ResistanceType.PSIONIC,
    }
    return resistance_map.get(resistance_enum.value.lower(), ResistanceType.SMASHING)


def convert_defense_type_to_api(internal_dtype: DefenseType) -> DefenseTypeEnum:
    """Convert internal DefenseType to API DefenseTypeEnum."""
    reverse_map = {
        DefenseType.SMASHING: DefenseTypeEnum.SMASHING,
        DefenseType.LETHAL: DefenseTypeEnum.LETHAL,
        DefenseType.FIRE: DefenseTypeEnum.FIRE,
        DefenseType.COLD: DefenseTypeEnum.COLD,
        DefenseType.ENERGY: DefenseTypeEnum.ENERGY,
        DefenseType.NEGATIVE_ENERGY: DefenseTypeEnum.NEGATIVE,
        DefenseType.TOXIC: DefenseTypeEnum.TOXIC,
        DefenseType.PSIONIC: DefenseTypeEnum.PSIONIC,
        DefenseType.MELEE: DefenseTypeEnum.MELEE,
        DefenseType.RANGED: DefenseTypeEnum.RANGED,
        DefenseType.AOE: DefenseTypeEnum.AOE,
    }
    return reverse_map.get(internal_dtype, DefenseTypeEnum.SMASHING)


def convert_resistance_type_to_api(
    internal_rtype: ResistanceType,
) -> ResistanceTypeEnum:
    """Convert internal ResistanceType to API ResistanceTypeEnum."""
    reverse_map = {
        ResistanceType.SMASHING: ResistanceTypeEnum.SMASHING,
        ResistanceType.LETHAL: ResistanceTypeEnum.LETHAL,
        ResistanceType.FIRE: ResistanceTypeEnum.FIRE,
        ResistanceType.COLD: ResistanceTypeEnum.COLD,
        ResistanceType.ENERGY: ResistanceTypeEnum.ENERGY,
        ResistanceType.NEGATIVE_ENERGY: ResistanceTypeEnum.NEGATIVE,
        ResistanceType.TOXIC: ResistanceTypeEnum.TOXIC,
        ResistanceType.PSIONIC: ResistanceTypeEnum.PSIONIC,
    }
    return reverse_map.get(internal_rtype, ResistanceTypeEnum.SMASHING)


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
        effects = [
            convert_effect_request_to_effect(e, idx)
            for idx, e in enumerate(request.effects)
        ]

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
            api_dtype = convert_defense_type_to_api(dtype)
            typed_api[api_dtype] = value

        positional_api = {}
        for dtype, value in defense_values.positional.items():
            api_dtype = convert_defense_type_to_api(dtype)
            positional_api[api_dtype] = value

        return DefenseCalculationResponse(
            typed=typed_api,
            positional=positional_api,
            ddr=0.0,  # TODO: Add DDR tracking to DefenseValues
            elusivity=0.0,  # TODO: Add elusivity tracking to DefenseValues
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
            api_rtype = convert_resistance_type_to_api(rtype)
            values_api[api_rtype] = value

        return ResistanceCalculationResponse(
            values=values_api,
            resistance_debuff_resistance=0.0,  # TODO: Add RDR tracking to ResistanceValues
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
    - HP stats (max HP, regeneration, absorb)
    - Endurance stats (max end, recovery, usage)
    - Recharge stats (global recharge bonus)
    - Misc stats (accuracy, tohit, damage bonuses)

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

        # Get archetype base stats for HP/endurance calculations
        archetype_hp_base = _get_archetype_hp_base(request.archetype.value)
        archetype_hp_cap = _get_archetype_hp_cap(request.archetype.value)

        # Calculate HP stats
        hp_bonus_total = sum(request.hp_bonuses) if request.hp_bonuses else 0.0
        regen_bonus_total = sum(request.regen_bonuses) if request.regen_bonuses else 0.0

        # HP max = base * (1 + bonus), capped
        hp_max_raw = archetype_hp_base * (1 + hp_bonus_total)
        hp_max = min(int(hp_max_raw), archetype_hp_cap)

        # Regen percent = 100% base + bonuses (as percentage)
        regen_percent = 100.0 + (regen_bonus_total * 100.0)

        # Regen per second = (base HP * regen%) / (60 * magic constant)
        # magic constant = 1.666667 (game tick conversion)
        magic_constant = 1.666667
        regen_per_second = (archetype_hp_base * (regen_percent / 100.0)) / (60.0 * magic_constant)

        hp_stats = HPStatsResponse(
            max=hp_max,
            regen_percent=round(regen_percent, 1),
            regen_per_second=round(regen_per_second, 2),
            absorb=request.absorb_value,
        )

        # Calculate endurance stats
        recovery_bonus_total = sum(request.recovery_bonuses) if request.recovery_bonuses else 0.0

        # Base recovery = 1.67 end/sec at 100%
        base_recovery = 1.67
        recovery_percent = 1.0 + recovery_bonus_total
        recovery_per_second = base_recovery * recovery_percent

        endurance_stats = EnduranceStatsResponse(
            max=100,  # Standard max endurance
            recovery_per_second=round(recovery_per_second, 2),
            usage_per_second=0.0,  # Would need toggle data to calculate
        )

        # Calculate recharge stats
        recharge_bonus_total = sum(request.recharge_bonuses) if request.recharge_bonuses else 0.0
        recharge_percent = recharge_bonus_total * 100.0  # Convert to percentage

        recharge_stats = RechargeStatsResponse(
            global_percent=round(recharge_percent, 1),
        )

        # Calculate misc stats
        accuracy_bonus = sum(request.accuracy_bonuses) if request.accuracy_bonuses else 0.0
        tohit_bonus = sum(request.tohit_bonuses) if request.tohit_bonuses else 0.0
        damage_bonus = sum(request.damage_bonuses) if request.damage_bonuses else 0.0

        misc_stats = MiscStatsResponse(
            accuracy=round(accuracy_bonus * 100.0, 1),
            tohit=round(tohit_bonus * 100.0, 1),
            damage=round(damage_bonus * 100.0, 1),
        )

        return BuildTotalsResponse(
            defense=defense_resp,
            resistance=resistance_resp,
            hp=hp_stats,
            endurance=endurance_stats,
            recharge=recharge_stats,
            misc=misc_stats,
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def _get_archetype_hp_base(archetype: str) -> int:
    """Get base HP for archetype at level 50."""
    hp_bases = {
        "Tanker": 1874,
        "Brute": 1499,
        "Scrapper": 1338,
        "Stalker": 1204,
        "Blaster": 1071,
        "Defender": 1071,
        "Corruptor": 1071,
        "Controller": 1071,
        "Dominator": 1071,
        "Mastermind": 803,
        "Peacebringer": 1606,
        "Warshade": 1606,
        "Arachnos Soldier": 1338,
        "Arachnos Widow": 1338,
    }
    return hp_bases.get(archetype, 1338)


def _get_archetype_hp_cap(archetype: str) -> int:
    """Get HP cap for archetype."""
    hp_caps = {
        "Tanker": 3212,
        "Brute": 2409,
        "Scrapper": 2409,
        "Stalker": 2409,
        "Blaster": 1606,
        "Defender": 1606,
        "Corruptor": 1606,
        "Controller": 1606,
        "Dominator": 1606,
        "Mastermind": 1606,
        "Peacebringer": 2409,
        "Warshade": 2409,
        "Arachnos Soldier": 2409,
        "Arachnos Widow": 2409,
    }
    return hp_caps.get(archetype, 2409)


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
