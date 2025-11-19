"""
Pydantic schemas for Mids-Web backend.

Comprehensive schema definitions matching the database models.
Updated for filtered_data schema structure.
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
    display_name: str | None = None
    icon: str | None = None
    display_help: str | None = None
    display_short_help: str | None = None
    default_rank: str | None = None
    class_requires: str | None = None
    restrictions: dict[str, Any] | None = None
    level_up_respecs: dict[str, Any] | None = None
    primary_category: str | None = None
    secondary_category: str | None = None
    power_pool_category: str | None = None
    epic_pool_category: str | None = None
    defiant_scale: Decimal | None = None
    deep_sleep_resistance: Decimal | None = None
    off_defiant_hit_points_attrib: int | None = None
    is_villain: bool | None = None
    class_key: str | None = None
    attrib_base: dict[str, Any] | None = None
    hit_points_base: int | None = None
    hit_points_max: int | None = None

    # Base modifiers (Epic 2.3)
    base_hp: Decimal | None = None
    base_regen: Decimal | None = None
    base_recovery: Decimal | None = None
    base_threat: Decimal | None = None

    # Archetype caps (Epic 2.3)
    damage_cap: Decimal | None = None
    resistance_cap: Decimal | None = None
    defense_cap: Decimal | None = None
    hp_cap: Decimal | None = None
    regeneration_cap: Decimal | None = None
    recovery_cap: Decimal | None = None
    recharge_cap: Decimal | None = None


class ArchetypeCreate(ArchetypeBase):
    pass


class ArchetypeUpdate(BaseModel):
    name: str | None = None
    display_name: str | None = None
    icon: str | None = None
    display_help: str | None = None
    display_short_help: str | None = None
    default_rank: str | None = None
    class_requires: str | None = None
    restrictions: dict[str, Any] | None = None
    level_up_respecs: dict[str, Any] | None = None
    primary_category: str | None = None
    secondary_category: str | None = None
    power_pool_category: str | None = None
    epic_pool_category: str | None = None
    defiant_scale: Decimal | None = None
    deep_sleep_resistance: Decimal | None = None
    off_defiant_hit_points_attrib: int | None = None
    is_villain: bool | None = None
    class_key: str | None = None
    attrib_base: dict[str, Any] | None = None
    hit_points_base: int | None = None
    hit_points_max: int | None = None

    # Base modifiers (Epic 2.3)
    base_hp: Decimal | None = None
    base_regen: Decimal | None = None
    base_recovery: Decimal | None = None
    base_threat: Decimal | None = None

    # Archetype caps (Epic 2.3)
    damage_cap: Decimal | None = None
    resistance_cap: Decimal | None = None
    defense_cap: Decimal | None = None
    hp_cap: Decimal | None = None
    regeneration_cap: Decimal | None = None
    recovery_cap: Decimal | None = None
    recharge_cap: Decimal | None = None


class Archetype(ArchetypeBase, TimestampedBase, BaseEntitySchema):
    id: int

    @field_serializer(
        "defiant_scale",
        "deep_sleep_resistance",
        "base_hp",
        "base_regen",
        "base_recovery",
        "base_threat",
        "damage_cap",
        "resistance_cap",
        "defense_cap",
        "hp_cap",
        "regeneration_cap",
        "recovery_cap",
        "recharge_cap",
        mode="wrap",
    )
    def serialize_decimal(self, value: Decimal | None, nxt) -> float | None:
        if value is None:
            return None
        if isinstance(value, Decimal):
            return float(value)
        return nxt(value)


# Powerset Schemas
class PowersetBase(BaseModel):
    name: str
    display_name: str | None = None
    display_fullname: str | None = None
    display_help: str | None = None
    display_short_help: str | None = None
    powerset_type: str  # primary, secondary, pool, epic, incarnate
    source_file: str | None = None
    icon: str | None = None
    requires: str | None = None
    power_names: dict[str, Any] | None = None
    power_display_names: dict[str, Any] | None = None
    power_short_helps: dict[str, Any] | None = None
    available_level: dict[str, Any] | None = None


class PowersetCreate(PowersetBase):
    archetype_id: int | None = None


class PowersetUpdate(BaseModel):
    name: str | None = None
    display_name: str | None = None
    display_fullname: str | None = None
    display_help: str | None = None
    display_short_help: str | None = None
    powerset_type: str | None = None
    source_file: str | None = None
    icon: str | None = None
    requires: str | None = None
    power_names: dict[str, Any] | None = None
    power_display_names: dict[str, Any] | None = None
    power_short_helps: dict[str, Any] | None = None
    available_level: dict[str, Any] | None = None


class Powerset(PowersetBase, TimestampedBase, BaseEntitySchema):
    id: int
    archetype_id: int | None = None


# Power Schemas
class PowerBase(BaseModel):
    name: str
    full_name: str
    display_name: str | None = None
    display_fullname: str | None = None
    short_name: str | None = None
    type: str | None = None  # Click, Toggle, Auto, etc.
    display_help: str | None = None
    display_short_help: str | None = None
    powerset_name: str | None = None
    available_level: int | None = None
    level_bought: int | None = None
    icon: str | None = None
    tray_placement: str | None = None
    tray_number: int | None = None
    tray_slot: int | None = None
    server_tray_priority: int | None = None
    accuracy: Decimal | None = None
    activation_time: Decimal | None = None
    recharge_time: Decimal | None = None
    endurance_cost: Decimal | None = None
    range: Decimal | None = None
    radius: Decimal | None = None
    arc: Decimal | None = None
    max_targets_hit: int | None = None
    target_type: str | None = None
    target_visibility: str | None = None
    effect_area: str | None = None
    requires: str | None = None
    activate_requires: str | None = None
    confirm_requires: str | None = None
    max_boosts: int | None = None
    boosts_allowed: dict[str, Any] | None = None
    allowed_boostset_cats: dict[str, Any] | None = None
    power_data: dict[str, Any] | None = None
    archetypes: dict[str, Any] | None = None
    tags: dict[str, Any] | None = None
    exclusion_groups: dict[str, Any] | None = None
    recharge_groups: dict[str, Any] | None = None


class PowerCreate(PowerBase):
    powerset_id: int


class PowerUpdate(BaseModel):
    name: str | None = None
    full_name: str | None = None
    display_name: str | None = None
    display_fullname: str | None = None
    short_name: str | None = None
    type: str | None = None
    display_help: str | None = None
    display_short_help: str | None = None
    powerset_name: str | None = None
    available_level: int | None = None
    level_bought: int | None = None
    icon: str | None = None
    tray_placement: str | None = None
    tray_number: int | None = None
    tray_slot: int | None = None
    server_tray_priority: int | None = None
    accuracy: Decimal | None = None
    activation_time: Decimal | None = None
    recharge_time: Decimal | None = None
    endurance_cost: Decimal | None = None
    range: Decimal | None = None
    radius: Decimal | None = None
    arc: Decimal | None = None
    max_targets_hit: int | None = None
    target_type: str | None = None
    target_visibility: str | None = None
    effect_area: str | None = None
    requires: str | None = None
    activate_requires: str | None = None
    confirm_requires: str | None = None
    max_boosts: int | None = None
    boosts_allowed: dict[str, Any] | None = None
    allowed_boostset_cats: dict[str, Any] | None = None
    power_data: dict[str, Any] | None = None
    archetypes: dict[str, Any] | None = None
    tags: dict[str, Any] | None = None
    exclusion_groups: dict[str, Any] | None = None
    recharge_groups: dict[str, Any] | None = None


class Power(PowerBase, TimestampedBase, BaseEntitySchema):
    id: int
    powerset_id: int

    @field_serializer(
        "accuracy",
        "activation_time",
        "recharge_time",
        "endurance_cost",
        "range",
        "radius",
        "arc",
        mode="wrap",
    )
    def serialize_decimal(self, value: Decimal | None, nxt) -> float | None:
        if value is None:
            return None
        if isinstance(value, Decimal):
            return float(value)
        return nxt(value)


# Enhancement Set Schemas
class EnhancementSetBase(BaseModel):
    name: str
    display_name: str | None = None
    group_name: str | None = None
    min_level: int = 10
    max_level: int = 50
    conversion_groups: dict[str, Any] | None = None
    boost_lists: dict[str, Any] | None = None
    bonuses: dict[str, Any] | None = None
    computed: dict[str, Any] | None = None


class EnhancementSetCreate(EnhancementSetBase):
    pass


class EnhancementSetUpdate(BaseModel):
    name: str | None = None
    display_name: str | None = None
    group_name: str | None = None
    min_level: int | None = None
    max_level: int | None = None
    conversion_groups: dict[str, Any] | None = None
    boost_lists: dict[str, Any] | None = None
    bonuses: dict[str, Any] | None = None
    computed: dict[str, Any] | None = None


class EnhancementSet(EnhancementSetBase, TimestampedBase, BaseEntitySchema):
    id: int


# Enhancement Schemas
class EnhancementBase(BaseModel):
    name: str
    display_name: str | None = None
    computed_name: str | None = None
    boostset_name: str | None = None
    boost_type: str | None = None
    level_min: int = 1
    level_max: int = 50
    min_slot_level: int | None = None
    min_bonus_level: int | None = None
    only_at_50: bool = False
    slot_requires: str | None = None
    ignores_level_differences: bool = False
    bonuses_ignore_exemplar: bool = False
    combinable: bool = False
    tradeable: bool = False
    account_bound: bool = False
    boostable: bool = False
    attuned: bool = False
    catalyzes_to: dict[str, Any] | None = None
    superior_scales: bool = False
    is_proc: bool = False
    is_unique: bool = False
    restricted_ats: dict[str, Any] | None = None
    unique_group: dict[str, Any] | None = None
    aspects: dict[str, Any] | None = None
    global_bonuses: dict[str, Any] | None = None
    icon: str | None = None


class EnhancementCreate(EnhancementBase):
    set_id: int | None = None


class EnhancementUpdate(BaseModel):
    name: str | None = None
    display_name: str | None = None
    computed_name: str | None = None
    boostset_name: str | None = None
    boost_type: str | None = None
    level_min: int | None = None
    level_max: int | None = None
    min_slot_level: int | None = None
    min_bonus_level: int | None = None
    only_at_50: bool | None = None
    slot_requires: str | None = None
    ignores_level_differences: bool | None = None
    bonuses_ignore_exemplar: bool | None = None
    combinable: bool | None = None
    tradeable: bool | None = None
    account_bound: bool | None = None
    boostable: bool | None = None
    attuned: bool | None = None
    catalyzes_to: dict[str, Any] | None = None
    superior_scales: bool | None = None
    is_proc: bool | None = None
    is_unique: bool | None = None
    restricted_ats: dict[str, Any] | None = None
    unique_group: dict[str, Any] | None = None
    aspects: dict[str, Any] | None = None
    global_bonuses: dict[str, Any] | None = None
    icon: str | None = None


class Enhancement(EnhancementBase, TimestampedBase, BaseEntitySchema):
    id: int
    set_id: int | None = None


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
    """Power with full details."""

    pass


class EnhancementSetWithDetails(EnhancementSet):
    """Enhancement set with enhancements."""

    enhancements: list[Enhancement] = []


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
