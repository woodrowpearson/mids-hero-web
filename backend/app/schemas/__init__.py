"""Schemas package for API request/response models."""

# ruff: noqa: E402
# Import all schemas from the original schemas.py file
import sys
from pathlib import Path

# Add parent directory to path to import schemas.py
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Import everything from schemas.py
from schemas import *  # noqa: F401, F403

# Remove the added path
sys.path.pop(0)

# Import new calculator schemas
from .build import (
    BuildEnhancementSlot,
    BuildPayload,
    BuildPowerData,
    GlobalBuffs,
)
from .response import (
    AggregateStats,
    CalcResponse,
    EnhancementValues,
    PerPowerStats,
    PowerStatBlock,
    SetBonusDetail,
    ValidationWarning,
)

# Note: __all__ is not defined to allow all imports from schemas.py to be available
