"""
Pydantic schemas for Mids-Web backend.
"""

from pydantic import BaseModel


class ArchetypeBase(BaseModel):
    name: str
    description: str


class ArchetypeCreate(ArchetypeBase):
    pass


class Archetype(ArchetypeBase):
    id: int
    primary_powersets: list[str]
    secondary_powersets: list[str]
    origins: list[str]

    class Config:
        from_attributes = True


class PowerBase(BaseModel):
    name: str
    description: str
    level_available: int


class Power(PowerBase):
    id: int
    powerset_id: int
    prerequisites: list[int]
    enhancement_categories: list[str]

    class Config:
        from_attributes = True


class EnhancementBase(BaseModel):
    name: str
    description: str
    category: str


class Enhancement(EnhancementBase):
    id: int
    set_name: str | None = None
    bonus_values: dict[str, float]

    class Config:
        from_attributes = True


class BuildStats(BaseModel):
    damage_bonus: float
    accuracy_bonus: float
    defense_totals: dict[str, float]
    resistance_totals: dict[str, float]
    set_bonuses: list[str]
