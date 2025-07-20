"""Build-related schemas for calculation API."""

from pydantic import BaseModel, Field, field_validator


class BuildInfo(BaseModel):
    """Basic build information."""

    name: str = Field(..., description="Build name")
    archetype: str = Field(..., description="Archetype name (e.g., 'Blaster', 'Tanker')")
    origin: str = Field(..., description="Origin (e.g., 'Science', 'Magic')")
    level: int = Field(..., ge=1, le=50, description="Character level (1-50)")
    alignment: str = Field(
        ..., description="Alignment (Hero, Villain, Praetorian)"
    )

    @field_validator("level")
    def validate_level(cls, v):
        if not 1 <= v <= 50:
            raise ValueError("Level must be between 1 and 50")
        return v


class BuildEnhancementSlot(BaseModel):
    """Enhancement slot configuration."""

    slot_index: int = Field(..., ge=0, le=5, description="Slot index (0-5)")
    enhancement_id: str | int = Field(..., description="Enhancement unique identifier")
    enhancement_level: int = Field(
        ..., ge=1, le=53, description="Enhancement level (1-53)"
    )
    boosted: bool = Field(default=False, description="Whether enhancement is boosted")
    catalyzed: bool = Field(
        default=False, description="Whether enhancement is catalyzed"
    )


class BuildPowerData(BaseModel):
    """Power configuration within a build."""

    id: str | int = Field(..., description="Power unique identifier")
    power_name: str = Field(..., description="Power display name")
    powerset: str = Field(..., description="Powerset name")
    level_taken: int = Field(..., ge=1, le=50, description="Level when power was taken")
    slots: list[BuildEnhancementSlot] = Field(
        default_factory=list, description="Enhancement slots (max 6)"
    )

    @field_validator("slots")
    def validate_slots(cls, v):
        if len(v) > 6:
            raise ValueError("Powers can have at most 6 enhancement slots")
        # Validate slot indices are unique
        indices = [slot.slot_index for slot in v]
        if len(indices) != len(set(indices)):
            raise ValueError("Slot indices must be unique")
        return v


class DefenseBuffs(BaseModel):
    """Defense buff values."""

    melee: float = Field(default=0.0, description="Melee defense buff %")
    ranged: float = Field(default=0.0, description="Ranged defense buff %")
    aoe: float = Field(default=0.0, description="AoE defense buff %")


class ResistanceBuffs(BaseModel):
    """Resistance buff values."""

    smashing: float = Field(default=0.0, description="Smashing resistance %")
    lethal: float = Field(default=0.0, description="Lethal resistance %")
    fire: float = Field(default=0.0, description="Fire resistance %")
    cold: float = Field(default=0.0, description="Cold resistance %")
    energy: float = Field(default=0.0, description="Energy resistance %")
    negative: float = Field(default=0.0, description="Negative energy resistance %")
    toxic: float = Field(default=0.0, description="Toxic resistance %")
    psionic: float = Field(default=0.0, description="Psionic resistance %")


class GlobalBuffs(BaseModel):
    """Global buffs affecting the entire character."""

    damage: float = Field(default=0.0, description="Global damage buff %")
    recharge: float = Field(default=0.0, description="Global recharge buff %")
    defense: DefenseBuffs = Field(
        default_factory=DefenseBuffs, description="Defense buffs"
    )
    resistance: ResistanceBuffs = Field(
        default_factory=ResistanceBuffs, description="Resistance buffs"
    )


class BuildPayload(BaseModel):
    """Complete build payload for calculation."""

    build: BuildInfo = Field(..., description="Basic build information")
    powers: list[BuildPowerData] = Field(..., description="List of powers in build")
    global_buffs: GlobalBuffs = Field(
        default_factory=GlobalBuffs, description="Global character buffs"
    )

    @field_validator("powers")
    def validate_powers(cls, v):
        # Validate power IDs are unique
        power_ids = [p.id for p in v]
        if len(power_ids) != len(set(power_ids)):
            raise ValueError("Power IDs must be unique within the build")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "build": {
                    "name": "Fire/Fire Blaster",
                    "archetype": "Blaster",
                    "origin": "Science",
                    "level": 50,
                    "alignment": "Hero",
                },
                "powers": [
                    {
                        "id": "blaster_ranged.fire_blast.fire_blast",
                        "power_name": "Fire Blast",
                        "powerset": "Fire Blast",
                        "level_taken": 1,
                        "slots": [
                            {
                                "slot_index": 0,
                                "enhancement_id": "devastation_damage",
                                "enhancement_level": 50,
                                "boosted": False,
                                "catalyzed": False,
                            }
                        ],
                    }
                ],
                "global_buffs": {
                    "damage": 10.0,
                    "recharge": 25.0,
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
                },
            }
        }
