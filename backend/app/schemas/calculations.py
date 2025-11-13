"""
Pydantic schemas for Calculation API endpoints.

Defines request/response models for all calculation endpoints in Phase 5.
"""

from enum import Enum

from pydantic import BaseModel, Field

# ============================================================================
# Core Enums and Types
# ============================================================================

class ArchetypeEnum(str, Enum):
    """Character archetype types."""
    BLASTER = "Blaster"
    CONTROLLER = "Controller"
    DEFENDER = "Defender"
    SCRAPPER = "Scrapper"
    TANKER = "Tanker"
    PEACEBRINGER = "Peacebringer"
    WARSHADE = "Warshade"
    BRUTE = "Brute"
    STALKER = "Stalker"
    MASTERMIND = "Mastermind"
    DOMINATOR = "Dominator"
    CORRUPTOR = "Corruptor"
    ARACHNOS_SOLDIER = "Arachnos Soldier"
    ARACHNOS_WIDOW = "Arachnos Widow"


class DamageTypeEnum(str, Enum):
    """Damage types."""
    NONE = "none"
    SMASHING = "smashing"
    LETHAL = "lethal"
    FIRE = "fire"
    COLD = "cold"
    ENERGY = "energy"
    NEGATIVE = "negative"
    TOXIC = "toxic"
    PSIONIC = "psionic"
    SPECIAL = "special"


class PowerTypeEnum(str, Enum):
    """Power activation types."""
    CLICK = "click"
    TOGGLE = "toggle"
    AUTO = "auto"
    BOOST = "boost"


class DamageMathModeEnum(str, Enum):
    """How to handle probabilistic damage."""
    AVERAGE = "average"  # Include procs weighted by probability
    MINIMUM = "minimum"  # Exclude procs (guaranteed damage only)


class DamageReturnModeEnum(str, Enum):
    """What damage value to return."""
    NUMERIC = "numeric"  # Raw damage number
    DPS = "dps"  # Damage per second
    DPA = "dpa"  # Damage per activation


class DefenseTypeEnum(str, Enum):
    """Defense types (typed and positional)."""
    # Typed defenses
    SMASHING = "smashing"
    LETHAL = "lethal"
    FIRE = "fire"
    COLD = "cold"
    ENERGY = "energy"
    NEGATIVE = "negative"
    TOXIC = "toxic"
    PSIONIC = "psionic"
    # Positional defenses
    MELEE = "melee"
    RANGED = "ranged"
    AOE = "aoe"


class ResistanceTypeEnum(str, Enum):
    """Resistance types (typed only)."""
    SMASHING = "smashing"
    LETHAL = "lethal"
    FIRE = "fire"
    COLD = "cold"
    ENERGY = "energy"
    NEGATIVE = "negative"
    TOXIC = "toxic"
    PSIONIC = "psionic"


# ============================================================================
# Effect Models
# ============================================================================

class EffectRequest(BaseModel):
    """Single effect for calculation requests."""
    effect_type: str = Field(..., description="Effect type (e.g., 'damage', 'defense', 'resistance')")
    magnitude: float = Field(..., description="Base magnitude value")
    duration: float = Field(default=0.0, description="Duration in seconds (0 for instant)")
    probability: float = Field(default=1.0, ge=0.0, le=1.0, description="Probability of effect occurring")
    damage_type: DamageTypeEnum | None = Field(None, description="Damage type for damage effects")
    ticks: int = Field(default=1, ge=1, description="Number of ticks for DoT effects")
    to_who: str = Field(default="target", description="Target of effect (self/target/both)")

    class Config:
        json_schema_extra = {
            "example": {
                "effect_type": "damage",
                "magnitude": 50.0,
                "duration": 0.0,
                "probability": 1.0,
                "damage_type": "smashing",
                "ticks": 1,
                "to_who": "target"
            }
        }


# ============================================================================
# Power Damage Calculation
# ============================================================================

class DamageCalculationRequest(BaseModel):
    """Request for power damage calculation."""
    effects: list[EffectRequest] = Field(..., description="List of power effects")
    power_type: PowerTypeEnum = Field(..., description="Power activation type")
    recharge_time: float = Field(default=0.0, ge=0.0, description="Base recharge time in seconds")
    cast_time: float = Field(default=0.0, ge=0.0, description="Animation/cast time in seconds")
    interrupt_time: float = Field(default=0.0, ge=0.0, description="Interrupt time in seconds")
    activate_period: float = Field(default=0.0, ge=0.0, description="For toggles, time between ticks")
    damage_math_mode: DamageMathModeEnum = Field(
        default=DamageMathModeEnum.AVERAGE,
        description="How to handle probabilistic damage"
    )
    damage_return_mode: DamageReturnModeEnum = Field(
        default=DamageReturnModeEnum.NUMERIC,
        description="What value to return"
    )
    archetype_damage_cap: float = Field(default=4.0, ge=1.0, description="Archetype damage buff cap")

    class Config:
        json_schema_extra = {
            "example": {
                "effects": [
                    {
                        "effect_type": "damage",
                        "magnitude": 62.56,
                        "damage_type": "smashing",
                        "probability": 1.0
                    }
                ],
                "power_type": "click",
                "recharge_time": 4.0,
                "cast_time": 1.07,
                "damage_return_mode": "numeric"
            }
        }


class DamageCalculationResponse(BaseModel):
    """Response for power damage calculation."""
    total: float = Field(..., description="Total damage value")
    by_type: dict[DamageTypeEnum, float] = Field(..., description="Damage by type")
    has_pvp_difference: bool = Field(default=False, description="True if PvE/PvP differ")
    has_toggle_enhancements: bool = Field(default=False, description="True if toggle has enhancement effects")
    activate_period: float | None = Field(None, description="For toggles, time between ticks")
    tooltip: str = Field(..., description="Formatted tooltip text")

    class Config:
        json_schema_extra = {
            "example": {
                "total": 62.56,
                "by_type": {"smashing": 62.56},
                "has_pvp_difference": False,
                "has_toggle_enhancements": False,
                "activate_period": None,
                "tooltip": "Total: 62.56 (Smashing: 62.56)"
            }
        }


# ============================================================================
# Build Totals Calculation
# ============================================================================

class DefenseBonusInput(BaseModel):
    """Defense bonus from a single source (power, enhancement set, etc.)."""
    bonuses: dict[DefenseTypeEnum, float] = Field(..., description="Defense bonuses by type")

    class Config:
        json_schema_extra = {
            "example": {
                "bonuses": {
                    "melee": 0.03,
                    "smashing": 0.02
                }
            }
        }


class ResistanceBonusInput(BaseModel):
    """Resistance bonus from a single source."""
    bonuses: dict[ResistanceTypeEnum, float] = Field(..., description="Resistance bonuses by type")

    class Config:
        json_schema_extra = {
            "example": {
                "bonuses": {
                    "smashing": 0.20,
                    "lethal": 0.15
                }
            }
        }


class DefenseCalculationRequest(BaseModel):
    """Request for build defense calculation."""
    archetype: ArchetypeEnum = Field(..., description="Character archetype")
    defense_bonuses: list[DefenseBonusInput] = Field(
        default_factory=list,
        description="List of defense bonuses from all sources"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "archetype": "Scrapper",
                "defense_bonuses": [
                    {"bonuses": {"melee": 0.30}},
                    {"bonuses": {"smashing": 0.15}}
                ]
            }
        }


class DefenseCalculationResponse(BaseModel):
    """Response for build defense calculation."""
    typed: dict[DefenseTypeEnum, float] = Field(..., description="Typed defense values")
    positional: dict[DefenseTypeEnum, float] = Field(..., description="Positional defense values")
    ddr: float = Field(default=0.0, description="Defense Debuff Resistance")
    elusivity: float = Field(default=0.0, description="Elusivity value")

    class Config:
        json_schema_extra = {
            "example": {
                "typed": {
                    "smashing": 0.15,
                    "lethal": 0.10
                },
                "positional": {
                    "melee": 0.30,
                    "ranged": 0.20,
                    "aoe": 0.15
                },
                "ddr": 0.0,
                "elusivity": 0.0
            }
        }


class ResistanceCalculationRequest(BaseModel):
    """Request for build resistance calculation."""
    archetype: ArchetypeEnum = Field(..., description="Character archetype")
    resistance_bonuses: list[ResistanceBonusInput] = Field(
        default_factory=list,
        description="List of resistance bonuses from all sources"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "archetype": "Tanker",
                "resistance_bonuses": [
                    {"bonuses": {"smashing": 0.30, "lethal": 0.30}},
                    {"bonuses": {"fire": 0.25}}
                ]
            }
        }


class ResistanceCalculationResponse(BaseModel):
    """Response for build resistance calculation."""
    values: dict[ResistanceTypeEnum, float] = Field(..., description="Resistance values by type")
    resistance_debuff_resistance: float = Field(default=0.0, description="Resistance to resistance debuffs")

    class Config:
        json_schema_extra = {
            "example": {
                "values": {
                    "smashing": 0.75,
                    "lethal": 0.75,
                    "fire": 0.60
                },
                "resistance_debuff_resistance": 0.0
            }
        }


class BuildTotalsRequest(BaseModel):
    """Request for complete build totals calculation."""
    archetype: ArchetypeEnum = Field(..., description="Character archetype")
    defense_bonuses: list[DefenseBonusInput] = Field(
        default_factory=list,
        description="Defense bonuses from all sources"
    )
    resistance_bonuses: list[ResistanceBonusInput] = Field(
        default_factory=list,
        description="Resistance bonuses from all sources"
    )
    # TODO: Add recharge, damage, accuracy, and other stats in future updates

    class Config:
        json_schema_extra = {
            "example": {
                "archetype": "Scrapper",
                "defense_bonuses": [
                    {"bonuses": {"melee": 0.30}}
                ],
                "resistance_bonuses": [
                    {"bonuses": {"smashing": 0.20}}
                ]
            }
        }


class BuildTotalsResponse(BaseModel):
    """Response for complete build totals calculation."""
    defense: DefenseCalculationResponse = Field(..., description="Defense totals")
    resistance: ResistanceCalculationResponse = Field(..., description="Resistance totals")
    # TODO: Add recharge, damage, accuracy, and other stats in future updates

    class Config:
        json_schema_extra = {
            "example": {
                "defense": {
                    "typed": {"smashing": 0.15},
                    "positional": {"melee": 0.30},
                    "ddr": 0.0,
                    "elusivity": 0.0
                },
                "resistance": {
                    "values": {"smashing": 0.20},
                    "resistance_debuff_resistance": 0.0
                }
            }
        }


# ============================================================================
# Constants Response
# ============================================================================

class GameConstantsResponse(BaseModel):
    """Response for game constants."""
    base_magic: float = Field(..., description="BASE_MAGIC constant (1.666667)")
    ed_schedule_a_thresholds: list[float] = Field(..., description="Schedule A ED thresholds")
    ed_schedule_b_thresholds: list[float] = Field(..., description="Schedule B ED thresholds")
    ed_schedule_c_thresholds: list[float] = Field(..., description="Schedule C ED thresholds")
    ed_schedule_d_thresholds: list[float] = Field(..., description="Schedule D ED thresholds")
    ed_efficiencies: list[float] = Field(..., description="ED efficiency multipliers")
    game_tick_seconds: float = Field(..., description="Game tick rate in seconds (4.0)")
    rule_of_five_limit: int = Field(..., description="Rule of 5 set bonus limit (5)")
    training_origin_value: float = Field(..., description="TO enhancement value")
    dual_origin_value: float = Field(..., description="DO enhancement value")
    single_origin_value: float = Field(..., description="SO enhancement value")
    invention_origin_l50_value: float = Field(..., description="L50 IO enhancement value")

    class Config:
        json_schema_extra = {
            "example": {
                "base_magic": 1.666667,
                "ed_schedule_a_thresholds": [0.70, 0.90, 1.00],
                "ed_schedule_b_thresholds": [0.40, 0.50, 0.60],
                "ed_schedule_c_thresholds": [0.80, 1.00, 1.20],
                "ed_schedule_d_thresholds": [1.20, 1.50, 1.80],
                "ed_efficiencies": [1.00, 0.90, 0.70, 0.15],
                "game_tick_seconds": 4.0,
                "rule_of_five_limit": 5,
                "training_origin_value": 0.0833,
                "dual_origin_value": 0.1667,
                "single_origin_value": 0.3333,
                "invention_origin_l50_value": 0.424
            }
        }


# ============================================================================
# Enhancement Calculation
# ============================================================================

class EnhancementSlotRequest(BaseModel):
    """Single enhancement slot."""
    enhancement_id: int = Field(default=-1, description="Enhancement database ID (-1 = empty)")
    io_level: int = Field(default=1, ge=1, le=53, description="IO level (1-53)")
    is_attuned: bool = Field(default=False, description="Scales with character level")
    is_catalyzed: bool = Field(default=False, description="Superior set (1.25x multiplier)")
    is_boosted: bool = Field(default=False, description="Has enhancement boosters")
    boost_level: int = Field(default=0, ge=0, le=5, description="Booster level (+0 to +5)")

    class Config:
        json_schema_extra = {
            "example": {
                "enhancement_id": 123,
                "io_level": 50,
                "is_attuned": False,
                "is_catalyzed": False,
                "is_boosted": True,
                "boost_level": 5
            }
        }


class ProcCalculationRequest(BaseModel):
    """Request for proc chance calculation."""
    ppm: float = Field(..., ge=0.0, description="Procs Per Minute rate")
    recharge_time: float = Field(..., ge=0.0, description="Power recharge time in seconds")
    cast_time: float = Field(default=0.0, ge=0.0, description="Power cast time in seconds")
    area_factor: float = Field(default=1.0, ge=1.0, description="Area modifier (1.0 for single target)")

    class Config:
        json_schema_extra = {
            "example": {
                "ppm": 3.5,
                "recharge_time": 8.0,
                "cast_time": 1.67,
                "area_factor": 1.0
            }
        }


class ProcCalculationResponse(BaseModel):
    """Response for proc chance calculation."""
    chance: float = Field(..., ge=0.0, le=1.0, description="Proc chance (0.0 to 1.0)")
    chance_percent: float = Field(..., ge=0.0, le=100.0, description="Proc chance as percentage")
    capped: bool = Field(default=False, description="True if capped at 90%")

    class Config:
        json_schema_extra = {
            "example": {
                "chance": 0.5625,
                "chance_percent": 56.25,
                "capped": False
            }
        }


# ============================================================================
# Error Response
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str = Field(..., description="Error message")
    detail: str | None = Field(None, description="Detailed error information")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Invalid archetype",
                "detail": "Archetype 'InvalidAT' is not recognized"
            }
        }
