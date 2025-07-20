"""Response schemas for calculation API."""

from datetime import datetime

from pydantic import BaseModel, Field


class PowerStatBlock(BaseModel):
    """Base statistics for a power."""

    damage: float = Field(..., description="Damage value")
    endurance_cost: float = Field(..., description="Endurance cost")
    recharge_time: float = Field(..., description="Recharge time in seconds")
    accuracy: float = Field(..., description="Accuracy multiplier")
    activation_time: float = Field(..., description="Activation time in seconds")
    range: float = Field(..., description="Range in feet")
    radius: float = Field(..., description="Radius in feet (0 for single target)")


class EnhancementValues(BaseModel):
    """Enhancement values after ED calculation."""

    damage: float = Field(default=0.0, description="Total damage enhancement % after ED")
    accuracy: float = Field(
        default=0.0, description="Total accuracy enhancement % after ED"
    )
    endurance: float = Field(
        default=0.0, description="Total endurance reduction % after ED"
    )
    recharge: float = Field(
        default=0.0, description="Total recharge reduction % after ED"
    )
    range: float = Field(default=0.0, description="Total range enhancement % after ED")


class PerPowerStats(BaseModel):
    """Per-power calculation results."""

    power_id: str = Field(..., description="Power unique identifier")
    power_name: str = Field(..., description="Power display name")
    base_stats: PowerStatBlock = Field(..., description="Base power statistics")
    enhanced_stats: PowerStatBlock = Field(
        ..., description="Enhanced power statistics"
    )
    enhancement_values: EnhancementValues = Field(
        ..., description="Total enhancement values after ED"
    )


class HitPointStats(BaseModel):
    """Hit point statistics."""

    base: float = Field(..., description="Base hit points")
    max: float = Field(..., description="Maximum hit points")
    regeneration_rate: float = Field(
        ..., description="HP regeneration per second"
    )


class EnduranceStats(BaseModel):
    """Endurance statistics."""

    max: float = Field(..., description="Maximum endurance")
    recovery_rate: float = Field(..., description="Endurance recovery per second")


class MovementStats(BaseModel):
    """Movement statistics."""

    run_speed: float = Field(..., description="Run speed in mph")
    fly_speed: float = Field(..., description="Fly speed in mph")
    jump_height: float = Field(..., description="Jump height in feet")
    jump_speed: float = Field(..., description="Jump speed in mph")


class StealthPerceptionStats(BaseModel):
    """Stealth and perception statistics."""

    pve: float = Field(..., description="PvE value")
    pvp: float = Field(..., description="PvP value")


class CombatTotals(BaseModel):
    """Combat-related totals."""

    hit_points: HitPointStats
    endurance: EnduranceStats
    movement: MovementStats
    stealth: StealthPerceptionStats = Field(..., alias="stealth")
    perception: StealthPerceptionStats


class DefenseTotals(BaseModel):
    """Defense totals after all calculations."""

    melee: float = Field(..., description="Total melee defense %")
    ranged: float = Field(..., description="Total ranged defense %")
    aoe: float = Field(..., description="Total AoE defense %")


class ResistanceTotals(BaseModel):
    """Resistance totals after all calculations."""

    smashing: float = Field(..., description="Total smashing resistance %")
    lethal: float = Field(..., description="Total lethal resistance %")
    fire: float = Field(..., description="Total fire resistance %")
    cold: float = Field(..., description="Total cold resistance %")
    energy: float = Field(..., description="Total energy resistance %")
    negative: float = Field(..., description="Total negative resistance %")
    toxic: float = Field(..., description="Total toxic resistance %")
    psionic: float = Field(..., description="Total psionic resistance %")


class DamageBuffTotals(BaseModel):
    """Damage buff totals."""

    melee: float = Field(..., description="Total melee damage buff %")
    ranged: float = Field(..., description="Total ranged damage buff %")
    aoe: float = Field(..., description="Total AoE damage buff %")


class SetBonusDetail(BaseModel):
    """Set bonus information."""

    set_name: str = Field(..., description="Enhancement set name")
    bonus_tier: int = Field(..., description="Number of pieces providing this bonus")
    bonus_description: str = Field(..., description="Human-readable bonus description")
    bonus_values: dict[str, float] = Field(
        ..., description="Attribute name to bonus value mapping"
    )


class AggregateStats(BaseModel):
    """Aggregate statistics for the entire build."""

    totals: CombatTotals = Field(..., description="Combat-related totals")
    defense: DefenseTotals = Field(..., description="Defense totals")
    resistance: ResistanceTotals = Field(..., description="Resistance totals")
    damage_buff: DamageBuffTotals = Field(..., description="Damage buff totals")
    set_bonuses: list[SetBonusDetail] = Field(
        default_factory=list, description="Active set bonuses"
    )


class ValidationWarning(BaseModel):
    """Validation warning information."""

    type: str = Field(
        ...,
        description="Warning type (cap_exceeded, invalid_slot, etc.)",
    )
    message: str = Field(..., description="Human-readable warning message")
    affected_stat: str = Field(..., description="Affected stat or power")


class CalcResponse(BaseModel):
    """Complete calculation response."""

    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Calculation timestamp"
    )
    build_name: str = Field(..., description="Build name")
    archetype: str = Field(..., description="Archetype name")
    level: int = Field(..., description="Character level")
    per_power_stats: list[PerPowerStats] = Field(
        ..., description="Statistics for each power"
    )
    aggregate_stats: AggregateStats = Field(
        ..., description="Aggregate build statistics"
    )
    validation_warnings: list[ValidationWarning] = Field(
        default_factory=list, description="Validation warnings"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2024-01-15T12:00:00Z",
                "build_name": "Fire/Fire Blaster",
                "archetype": "Blaster",
                "level": 50,
                "per_power_stats": [
                    {
                        "power_id": "blaster_ranged.fire_blast.fire_blast",
                        "power_name": "Fire Blast",
                        "base_stats": {
                            "damage": 62.56,
                            "endurance_cost": 5.2,
                            "recharge_time": 4.0,
                            "accuracy": 1.0,
                            "activation_time": 1.188,
                            "range": 80.0,
                            "radius": 0.0,
                        },
                        "enhanced_stats": {
                            "damage": 121.99,
                            "endurance_cost": 2.6,
                            "recharge_time": 2.0,
                            "accuracy": 1.95,
                            "activation_time": 1.188,
                            "range": 80.0,
                            "radius": 0.0,
                        },
                        "enhancement_values": {
                            "damage": 95.0,
                            "accuracy": 95.0,
                            "endurance": 50.0,
                            "recharge": 50.0,
                            "range": 0.0,
                        },
                    }
                ],
                "aggregate_stats": {
                    "totals": {
                        "hit_points": {
                            "base": 1204.8,
                            "max": 1606.4,
                            "regeneration_rate": 2.5,
                        },
                        "endurance": {"max": 100.0, "recovery_rate": 1.67},
                        "movement": {
                            "run_speed": 21.0,
                            "fly_speed": 0.0,
                            "jump_height": 14.0,
                            "jump_speed": 14.0,
                        },
                        "stealth": {"pve": 0.0, "pvp": 0.0},
                        "perception": {"pve": 500.0, "pvp": 1153.0},
                    },
                    "defense": {"melee": 5.0, "ranged": 5.0, "aoe": 5.0},
                    "resistance": {
                        "smashing": 10.0,
                        "lethal": 10.0,
                        "fire": 20.0,
                        "cold": 15.0,
                        "energy": 15.0,
                        "negative": 10.0,
                        "toxic": 0.0,
                        "psionic": 5.0,
                    },
                    "damage_buff": {"melee": 0.0, "ranged": 105.0, "aoe": 0.0},
                    "set_bonuses": [
                        {
                            "set_name": "Devastation",
                            "bonus_tier": 3,
                            "bonus_description": "+2.5% Damage",
                            "bonus_values": {"damage": 2.5},
                        }
                    ],
                },
                "validation_warnings": [],
            }
        }
