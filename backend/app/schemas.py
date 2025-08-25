"""
Pydantic schemas for Mids-Web backend.

Comprehensive schema definitions matching the database models.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, field_serializer


# Base classes for common patterns
class TimestampedBase(BaseModel):
    """Base class for models with timestamps."""

    created_at: datetime
    updated_at: datetime


class BaseEntitySchema(BaseModel):
    """Base schema with common model configuration."""

    model_config = ConfigDict(from_attributes=True)


# Archetype Schemas
class ArchetypeBase(BaseModel):
    name: str
    description: str | None = None
    display_name: str | None = None
    primary_group: str | None = None
    secondary_group: str | None = None
    hit_points_base: int | None = None
    hit_points_max: int | None = None


class ArchetypeCreate(ArchetypeBase):
    pass


class ArchetypeUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    display_name: str | None = None
    primary_group: str | None = None
    secondary_group: str | None = None
    hit_points_base: int | None = None
    hit_points_max: int | None = None


class Archetype(ArchetypeBase, TimestampedBase, BaseEntitySchema):
    id: int
    inherent_power_id: int | None = None


# Powerset Schemas
class PowersetBase(BaseModel):
    name: str
    display_name: str | None = None
    description: str | None = None
    powerset_type: str  # primary, secondary, pool, epic, incarnate
    icon_path: str | None = None


class PowersetCreate(PowersetBase):
    archetype_id: int


class PowersetUpdate(BaseModel):
    name: str | None = None
    display_name: str | None = None
    description: str | None = None
    powerset_type: str | None = None
    icon_path: str | None = None


class Powerset(PowersetBase, TimestampedBase, BaseEntitySchema):
    id: int
    archetype_id: int


# Power Schemas
class PowerBase(BaseModel):
    name: str
    display_name: str | None = None
    description: str | None = None
    level_available: int = 1
    power_type: str | None = None  # attack, defense, control, support, travel
    target_type: str | None = None  # self, ally, enemy, location
    accuracy: Decimal | None = None
    damage_scale: Decimal | None = None
    endurance_cost: Decimal | None = None
    recharge_time: Decimal | None = None
    activation_time: Decimal | None = None
    range_feet: int | None = None
    radius_feet: int | None = None
    max_targets: int | None = None
    effects: dict[str, Any] | None = None
    icon_path: str | None = None
    display_order: int | None = None
    internal_name: str | None = None
    requires_line_of_sight: bool = True
    modes_required: str | None = None
    modes_disallowed: str | None = None
    ai_report: str | None = None
    effect_groups: dict[str, Any] | None = None
    display_info: dict[str, Any] | None = None


class PowerCreate(PowerBase):
    powerset_id: int


class PowerUpdate(BaseModel):
    name: str | None = None
    display_name: str | None = None
    description: str | None = None
    level_available: int | None = None
    power_type: str | None = None
    target_type: str | None = None
    accuracy: Decimal | None = None
    damage_scale: Decimal | None = None
    endurance_cost: Decimal | None = None
    recharge_time: Decimal | None = None
    activation_time: Decimal | None = None
    range_feet: int | None = None
    radius_feet: int | None = None
    max_targets: int | None = None
    effects: dict[str, Any] | None = None
    icon_path: str | None = None
    display_order: int | None = None
    internal_name: str | None = None
    requires_line_of_sight: bool | None = None
    modes_required: str | None = None
    modes_disallowed: str | None = None
    ai_report: str | None = None
    effect_groups: dict[str, Any] | None = None
    display_info: dict[str, Any] | None = None


class Power(PowerBase, TimestampedBase, BaseEntitySchema):
    id: int
    powerset_id: int

    @field_serializer(
        "accuracy",
        "damage_scale",
        "endurance_cost",
        "recharge_time",
        "activation_time",
        mode="wrap",
    )
    def serialize_decimal(self, value: Decimal | None, nxt) -> float | None:
        if value is None:
            return None
        if isinstance(value, Decimal):
            return float(value)
        return nxt(value)


# Power Prerequisite Schemas
class PowerPrerequisiteBase(BaseModel):
    required_level: int | None = None
    prerequisite_type: str | None = None  # one_of, all_of


class PowerPrerequisiteCreate(PowerPrerequisiteBase):
    power_id: int
    required_power_id: int


class PowerPrerequisite(PowerPrerequisiteBase, BaseEntitySchema):
    id: int
    power_id: int
    required_power_id: int
    created_at: datetime


# Enhancement Set Schemas
class EnhancementSetBase(BaseModel):
    name: str
    display_name: str | None = None
    description: str | None = None
    min_level: int = 10
    max_level: int = 50


class EnhancementSetCreate(EnhancementSetBase):
    pass


class EnhancementSetUpdate(BaseModel):
    name: str | None = None
    display_name: str | None = None
    description: str | None = None
    min_level: int | None = None
    max_level: int | None = None


class EnhancementSet(EnhancementSetBase, TimestampedBase, BaseEntitySchema):
    id: int


# Enhancement Schemas
class EnhancementBase(BaseModel):
    name: str
    display_name: str | None = None
    enhancement_type: str | None = None  # IO, SO, DO, TO, HamiO, set_piece
    level_min: int = 1
    level_max: int = 50
    accuracy_bonus: Decimal | None = None
    damage_bonus: Decimal | None = None
    endurance_bonus: Decimal | None = None
    recharge_bonus: Decimal | None = None
    defense_bonus: Decimal | None = None
    resistance_bonus: Decimal | None = None
    other_bonuses: dict[str, Any] | None = None
    unique_enhancement: bool = False
    icon_path: str | None = None


class EnhancementCreate(EnhancementBase):
    set_id: int | None = None


class EnhancementUpdate(BaseModel):
    name: str | None = None
    display_name: str | None = None
    enhancement_type: str | None = None
    level_min: int | None = None
    level_max: int | None = None
    accuracy_bonus: Decimal | None = None
    damage_bonus: Decimal | None = None
    endurance_bonus: Decimal | None = None
    recharge_bonus: Decimal | None = None
    defense_bonus: Decimal | None = None
    resistance_bonus: Decimal | None = None
    other_bonuses: dict[str, Any] | None = None
    unique_enhancement: bool | None = None
    icon_path: str | None = None


class Enhancement(EnhancementBase, TimestampedBase, BaseEntitySchema):
    id: int
    set_id: int | None = None


# Set Bonus Schemas
class SetBonusBase(BaseModel):
    pieces_required: int
    bonus_description: str | None = None
    bonus_type: str | None = None
    bonus_amount: Decimal | None = None
    bonus_details: dict[str, Any] | None = None


class SetBonusCreate(SetBonusBase):
    set_id: int


class SetBonus(SetBonusBase, BaseEntitySchema):
    id: int
    set_id: int
    created_at: datetime


# Power Enhancement Compatibility Schemas
class PowerEnhancementCompatibilityBase(BaseModel):
    enhancement_type: str
    allowed: bool = True


class PowerEnhancementCompatibilityCreate(PowerEnhancementCompatibilityBase):
    power_id: int


class PowerEnhancementCompatibility(
    PowerEnhancementCompatibilityBase, BaseEntitySchema
):
    id: int
    power_id: int
    created_at: datetime


# Salvage Schemas
class SalvageBase(BaseModel):
    internal_name: str
    display_name: str
    salvage_type: str | None = None  # common, uncommon, rare
    origin: str | None = None  # tech, magic, natural
    level_range: str | None = None  # 10-25, 26-40, 41-50
    icon_path: str | None = None


class SalvageCreate(SalvageBase):
    pass


class Salvage(SalvageBase, TimestampedBase, BaseEntitySchema):
    id: int


# Recipe Schemas
class RecipeBase(BaseModel):
    internal_name: str
    display_name: str
    enhancement_id: int | None = None
    recipe_type: str | None = None  # common, uncommon, rare, very_rare
    level_min: int = 10
    level_max: int = 50
    crafting_cost: int | None = None
    crafting_cost_premium: int | None = None
    memorized: bool = False


class RecipeCreate(RecipeBase):
    pass


class Recipe(RecipeBase, TimestampedBase, BaseEntitySchema):
    id: int


# Recipe Salvage Schemas
class RecipeSalvageBase(BaseModel):
    recipe_id: int
    salvage_id: int
    quantity: int = 1


class RecipeSalvageCreate(RecipeSalvageBase):
    pass


class RecipeSalvage(RecipeSalvageBase, BaseEntitySchema):
    id: int
    created_at: datetime


# Build Schemas
class BuildBase(BaseModel):
    name: str
    level: int = 1
    build_data: dict[str, Any] | None = None
    is_public: bool = False


class BuildCreate(BuildBase):
    archetype_id: int
    primary_powerset_id: int
    secondary_powerset_id: int


class BuildUpdate(BaseModel):
    name: str | None = None
    level: int | None = None
    build_data: dict[str, Any] | None = None
    is_public: bool | None = None


class Build(BuildBase, TimestampedBase, BaseEntitySchema):
    id: int
    archetype_id: int
    primary_powerset_id: int
    secondary_powerset_id: int
    user_id: int | None = None


# Build Power Schemas
class BuildPowerBase(BaseModel):
    level_taken: int
    slot_count: int = 1


class BuildPowerCreate(BuildPowerBase):
    build_id: int
    power_id: int


class BuildPower(BuildPowerBase, BaseEntitySchema):
    id: int
    build_id: int
    power_id: int
    created_at: datetime


# Build Enhancement Schemas
class BuildEnhancementBase(BaseModel):
    slot_number: int
    enhancement_level: int = 50


class BuildEnhancementCreate(BuildEnhancementBase):
    build_power_id: int
    enhancement_id: int


class BuildEnhancement(BuildEnhancementBase, BaseEntitySchema):
    id: int
    build_power_id: int
    enhancement_id: int
    created_at: datetime


# Import Log Schemas
class ImportLogBase(BaseModel):
    import_type: str | None = None  # full, incremental, patch
    source_file: str | None = None
    game_version: str | None = None
    records_processed: int | None = None
    records_imported: int | None = None
    errors: int | None = None
    import_data: dict[str, Any] | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


class ImportLogCreate(ImportLogBase):
    pass


class ImportLog(ImportLogBase, BaseEntitySchema):
    id: int
    created_at: datetime


# Complex Response Schemas
class ArchetypeWithPowersets(Archetype):
    """Archetype with associated powersets."""

    powersets: list[Powerset] = []


class PowersetWithPowers(Powerset):
    """Powerset with associated powers."""

    powers: list[Power] = []


class PowerWithDetails(Power):
    """Power with prerequisites and compatibility info."""

    prerequisites: list[PowerPrerequisite] = []
    compatibilities: list[PowerEnhancementCompatibility] = []


class EnhancementSetWithDetails(EnhancementSet):
    """Enhancement set with enhancements and bonuses."""

    enhancements: list[Enhancement] = []
    set_bonuses: list[SetBonus] = []


class BuildWithDetails(Build):
    """Complete build with all related data."""

    archetype: Archetype
    primary_powerset: Powerset
    secondary_powerset: Powerset
    build_powers: list[BuildPower] = []


class BuildStats(BaseModel):
    """Calculated build statistics."""

    damage_bonus: Decimal = Decimal("0.0")
    accuracy_bonus: Decimal = Decimal("0.0")
    defense_totals: dict[str, Decimal] = {}
    resistance_totals: dict[str, Decimal] = {}
    set_bonuses: list[str] = []
    total_endurance_cost: Decimal = Decimal("0.0")
    recharge_reduction: Decimal = Decimal("0.0")
