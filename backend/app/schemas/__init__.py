"""Pydantic schemas for API requests and responses."""

from .base import (
    # Archetype schemas
    Archetype,
    ArchetypeBase,
    ArchetypeCreate,
    ArchetypeUpdate,
    ArchetypeWithPowersets,
    # Build schemas
    Build,
    BuildBase,
    BuildCreate,
    BuildEnhancement,
    BuildEnhancementBase,
    BuildEnhancementCreate,
    BuildPower,
    BuildPowerBase,
    BuildPowerCreate,
    BuildStats,
    BuildUpdate,
    BuildWithDetails,
    # Enhancement schemas
    Enhancement,
    EnhancementBase,
    EnhancementCreate,
    EnhancementSet,
    EnhancementSetBase,
    EnhancementSetCreate,
    EnhancementSetUpdate,
    EnhancementSetWithDetails,
    EnhancementUpdate,
    # Import log schemas
    ImportLog,
    ImportLogBase,
    ImportLogCreate,
    # Power schemas
    Power,
    PowerBase,
    PowerCreate,
    # Powerset schemas
    Powerset,
    PowersetBase,
    PowersetCreate,
    PowersetUpdate,
    PowersetWithPowers,
    PowerUpdate,
    PowerWithDetails,
)
from .calculations import (
    # Enums
    ArchetypeEnum,
    # Build totals
    BuildTotalsRequest,
    BuildTotalsResponse,
    # Damage calculation
    DamageCalculationRequest,
    DamageCalculationResponse,
    DamageMathModeEnum,
    DamageReturnModeEnum,
    DamageTypeEnum,
    # Defense calculation
    DefenseBonusInput,
    DefenseCalculationRequest,
    DefenseCalculationResponse,
    DefenseTypeEnum,
    # Effect models
    EffectRequest,
    # Enhancement calculation
    EnhancementSlotRequest,
    # Error handling
    ErrorResponse,
    # Constants
    GameConstantsResponse,
    PowerTypeEnum,
    ProcCalculationRequest,
    ProcCalculationResponse,
    # Resistance calculation
    ResistanceBonusInput,
    ResistanceCalculationRequest,
    ResistanceCalculationResponse,
    ResistanceTypeEnum,
)

__all__ = [
    # Base schemas - Archetypes
    "Archetype",
    "ArchetypeBase",
    "ArchetypeCreate",
    "ArchetypeUpdate",
    "ArchetypeWithPowersets",
    # Base schemas - Builds
    "Build",
    "BuildBase",
    "BuildCreate",
    "BuildEnhancement",
    "BuildEnhancementBase",
    "BuildEnhancementCreate",
    "BuildPower",
    "BuildPowerBase",
    "BuildPowerCreate",
    "BuildStats",
    "BuildUpdate",
    "BuildWithDetails",
    # Base schemas - Enhancements
    "Enhancement",
    "EnhancementBase",
    "EnhancementCreate",
    "EnhancementSet",
    "EnhancementSetBase",
    "EnhancementSetCreate",
    "EnhancementSetUpdate",
    "EnhancementSetWithDetails",
    "EnhancementUpdate",
    # Base schemas - Import logs
    "ImportLog",
    "ImportLogBase",
    "ImportLogCreate",
    # Base schemas - Powers
    "Power",
    "PowerBase",
    "PowerCreate",
    "PowerUpdate",
    "PowerWithDetails",
    # Base schemas - Powersets
    "Powerset",
    "PowersetBase",
    "PowersetCreate",
    "PowersetUpdate",
    "PowersetWithPowers",
    # Calculation schemas - Enums
    "ArchetypeEnum",
    "DamageTypeEnum",
    "DefenseTypeEnum",
    "ResistanceTypeEnum",
    "PowerTypeEnum",
    "DamageMathModeEnum",
    "DamageReturnModeEnum",
    # Calculation schemas - Effect models
    "EffectRequest",
    # Calculation schemas - Damage calculation
    "DamageCalculationRequest",
    "DamageCalculationResponse",
    # Calculation schemas - Defense calculation
    "DefenseBonusInput",
    "DefenseCalculationRequest",
    "DefenseCalculationResponse",
    # Calculation schemas - Resistance calculation
    "ResistanceBonusInput",
    "ResistanceCalculationRequest",
    "ResistanceCalculationResponse",
    # Calculation schemas - Build totals
    "BuildTotalsRequest",
    "BuildTotalsResponse",
    # Calculation schemas - Constants
    "GameConstantsResponse",
    # Calculation schemas - Enhancement calculation
    "EnhancementSlotRequest",
    "ProcCalculationRequest",
    "ProcCalculationResponse",
    # Calculation schemas - Error handling
    "ErrorResponse",
]
