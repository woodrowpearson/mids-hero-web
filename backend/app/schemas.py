"""
Pydantic schemas for Mids-Web backend.

Comprehensive schema definitions matching the database models.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


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
    description: Optional[str] = None
    display_name: Optional[str] = None
    primary_group: Optional[str] = None
    secondary_group: Optional[str] = None
    hit_points_base: Optional[int] = None
    hit_points_max: Optional[int] = None


class ArchetypeCreate(ArchetypeBase):
    pass


class ArchetypeUpdate(ArchetypeBase):
    name: Optional[str] = None


class Archetype(ArchetypeBase, TimestampedBase, BaseEntitySchema):
    id: int
    inherent_power_id: Optional[int] = None


# Powerset Schemas
class PowersetBase(BaseModel):
    name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    powerset_type: str  # primary, secondary, pool, epic, incarnate
    icon_path: Optional[str] = None


class PowersetCreate(PowersetBase):
    archetype_id: int


class PowersetUpdate(PowersetBase):
    name: Optional[str] = None
    powerset_type: Optional[str] = None


class Powerset(PowersetBase, TimestampedBase, BaseEntitySchema):
    id: int
    archetype_id: int


# Power Schemas
class PowerBase(BaseModel):
    name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    level_available: int = 1
    power_type: Optional[str] = None  # attack, defense, control, support, travel
    target_type: Optional[str] = None  # self, ally, enemy, location
    accuracy: Optional[Decimal] = None
    damage_scale: Optional[Decimal] = None
    endurance_cost: Optional[Decimal] = None
    recharge_time: Optional[Decimal] = None
    activation_time: Optional[Decimal] = None
    range_feet: Optional[int] = None
    radius_feet: Optional[int] = None
    max_targets: Optional[int] = None
    effects: Optional[Dict[str, Any]] = None
    icon_path: Optional[str] = None
    display_order: Optional[int] = None


class PowerCreate(PowerBase):
    powerset_id: int


class PowerUpdate(PowerBase):
    name: Optional[str] = None
    level_available: Optional[int] = None


class Power(PowerBase, TimestampedBase, BaseEntitySchema):
    id: int
    powerset_id: int


# Power Prerequisite Schemas
class PowerPrerequisiteBase(BaseModel):
    required_level: Optional[int] = None
    prerequisite_type: Optional[str] = None  # one_of, all_of


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
    display_name: Optional[str] = None
    description: Optional[str] = None
    min_level: int = 10
    max_level: int = 50


class EnhancementSetCreate(EnhancementSetBase):
    pass


class EnhancementSetUpdate(EnhancementSetBase):
    name: Optional[str] = None


class EnhancementSet(EnhancementSetBase, TimestampedBase, BaseEntitySchema):
    id: int


# Enhancement Schemas
class EnhancementBase(BaseModel):
    name: str
    display_name: Optional[str] = None
    enhancement_type: Optional[str] = None  # IO, SO, DO, TO, HamiO, set_piece
    level_min: int = 1
    level_max: int = 50
    accuracy_bonus: Optional[Decimal] = None
    damage_bonus: Optional[Decimal] = None
    endurance_bonus: Optional[Decimal] = None
    recharge_bonus: Optional[Decimal] = None
    defense_bonus: Optional[Decimal] = None
    resistance_bonus: Optional[Decimal] = None
    other_bonuses: Optional[Dict[str, Any]] = None
    unique_enhancement: bool = False
    icon_path: Optional[str] = None


class EnhancementCreate(EnhancementBase):
    set_id: Optional[int] = None


class EnhancementUpdate(EnhancementBase):
    name: Optional[str] = None


class Enhancement(EnhancementBase, TimestampedBase, BaseEntitySchema):
    id: int
    set_id: Optional[int] = None


# Set Bonus Schemas
class SetBonusBase(BaseModel):
    pieces_required: int
    bonus_description: Optional[str] = None
    bonus_type: Optional[str] = None
    bonus_amount: Optional[Decimal] = None
    bonus_details: Optional[Dict[str, Any]] = None


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


class PowerEnhancementCompatibility(PowerEnhancementCompatibilityBase, BaseEntitySchema):
    id: int
    power_id: int
    created_at: datetime


# Build Schemas
class BuildBase(BaseModel):
    name: str
    level: int = 1
    build_data: Optional[Dict[str, Any]] = None
    is_public: bool = False


class BuildCreate(BuildBase):
    archetype_id: int
    primary_powerset_id: int
    secondary_powerset_id: int


class BuildUpdate(BuildBase):
    name: Optional[str] = None
    level: Optional[int] = None


class Build(BuildBase, TimestampedBase, BaseEntitySchema):
    id: int
    archetype_id: int
    primary_powerset_id: int
    secondary_powerset_id: int
    user_id: Optional[int] = None


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
    import_type: Optional[str] = None  # full, incremental, patch
    source_file: Optional[str] = None
    game_version: Optional[str] = None
    records_processed: Optional[int] = None
    records_imported: Optional[int] = None
    errors: Optional[int] = None
    import_data: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class ImportLogCreate(ImportLogBase):
    pass


class ImportLog(ImportLogBase, BaseEntitySchema):
    id: int
    created_at: datetime


# Complex Response Schemas
class ArchetypeWithPowersets(Archetype):
    """Archetype with associated powersets."""
    powersets: List[Powerset] = []


class PowersetWithPowers(Powerset):
    """Powerset with associated powers."""
    powers: List[Power] = []


class PowerWithDetails(Power):
    """Power with prerequisites and compatibility info."""
    prerequisites: List[PowerPrerequisite] = []
    compatibilities: List[PowerEnhancementCompatibility] = []


class EnhancementSetWithDetails(EnhancementSet):
    """Enhancement set with enhancements and bonuses."""
    enhancements: List[Enhancement] = []
    set_bonuses: List[SetBonus] = []


class BuildWithDetails(Build):
    """Complete build with all related data."""
    archetype: Archetype
    primary_powerset: Powerset
    secondary_powerset: Powerset
    build_powers: List[BuildPower] = []


class BuildStats(BaseModel):
    """Calculated build statistics."""
    damage_bonus: Decimal = Decimal("0.0")
    accuracy_bonus: Decimal = Decimal("0.0")
    defense_totals: Dict[str, Decimal] = {}
    resistance_totals: Dict[str, Decimal] = {}
    set_bonuses: List[str] = []
    total_endurance_cost: Decimal = Decimal("0.0")
    recharge_reduction: Decimal = Decimal("0.0")