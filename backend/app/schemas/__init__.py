"""Pydantic schemas for API requests and responses."""

from .calculations import (
    # Enums
    ArchetypeEnum,
    DamageTypeEnum,
    DefenseTypeEnum,
    ResistanceTypeEnum,
    PowerTypeEnum,
    DamageMathModeEnum,
    DamageReturnModeEnum,
    # Effect models
    EffectRequest,
    # Damage calculation
    DamageCalculationRequest,
    DamageCalculationResponse,
    # Defense calculation
    DefenseBonusInput,
    DefenseCalculationRequest,
    DefenseCalculationResponse,
    # Resistance calculation
    ResistanceBonusInput,
    ResistanceCalculationRequest,
    ResistanceCalculationResponse,
    # Build totals
    BuildTotalsRequest,
    BuildTotalsResponse,
    # Constants
    GameConstantsResponse,
    # Enhancement calculation
    EnhancementSlotRequest,
    ProcCalculationRequest,
    ProcCalculationResponse,
    # Error handling
    ErrorResponse,
)

__all__ = [
    # Enums
    "ArchetypeEnum",
    "DamageTypeEnum",
    "DefenseTypeEnum",
    "ResistanceTypeEnum",
    "PowerTypeEnum",
    "DamageMathModeEnum",
    "DamageReturnModeEnum",
    # Effect models
    "EffectRequest",
    # Damage calculation
    "DamageCalculationRequest",
    "DamageCalculationResponse",
    # Defense calculation
    "DefenseBonusInput",
    "DefenseCalculationRequest",
    "DefenseCalculationResponse",
    # Resistance calculation
    "ResistanceBonusInput",
    "ResistanceCalculationRequest",
    "ResistanceCalculationResponse",
    # Build totals
    "BuildTotalsRequest",
    "BuildTotalsResponse",
    # Constants
    "GameConstantsResponse",
    # Enhancement calculation
    "EnhancementSlotRequest",
    "ProcCalculationRequest",
    "ProcCalculationResponse",
    # Error handling
    "ErrorResponse",
]
