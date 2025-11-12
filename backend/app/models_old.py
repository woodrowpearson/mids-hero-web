"""
Database models for Mids-Web backend.

Based on the comprehensive database design for City of Heroes character build planner.
"""

from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .database import Base


class Archetype(Base):
    """Archetype model representing character classes."""

    __tablename__ = "archetypes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    display_name = Column(String(100))
    primary_group = Column(String(50))  # damage, control, defense, support
    secondary_group = Column(String(50))  # damage, control, defense, support
    hit_points_base = Column(Integer)
    hit_points_max = Column(Integer)
    inherent_power_id = Column(Integer, ForeignKey("powers.id"))
    icon_path = Column(String(255))  # Added for archetype icons
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    powersets = relationship("Powerset", back_populates="archetype")
    builds = relationship("Build", back_populates="archetype")
    inherent_power = relationship("Power", foreign_keys=[inherent_power_id])

    __table_args__ = (
        Index("idx_archetype_groups", "primary_group", "secondary_group"),
    )


class Powerset(Base):
    """Powerset model representing groups of powers."""

    __tablename__ = "powersets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    display_name = Column(String(100))
    description = Column(Text)
    archetype_id = Column(Integer, ForeignKey("archetypes.id"), nullable=False)
    powerset_type = Column(
        String(20), nullable=False
    )  # primary, secondary, pool, epic, incarnate
    icon_path = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    archetype = relationship("Archetype", back_populates="powersets")
    powers = relationship("Power", back_populates="powerset")
    primary_builds = relationship(
        "Build",
        foreign_keys="Build.primary_powerset_id",
        back_populates="primary_powerset",
    )
    secondary_builds = relationship(
        "Build",
        foreign_keys="Build.secondary_powerset_id",
        back_populates="secondary_powerset",
    )

    __table_args__ = (
        UniqueConstraint(
            "name", "archetype_id", "powerset_type", name="uq_powerset_archetype_type"
        ),
        Index("idx_powerset_type", "powerset_type"),
    )


class Power(Base):
    """Power model representing individual abilities."""

    __tablename__ = "powers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    display_name = Column(String(100))
    description = Column(Text)
    powerset_id = Column(Integer, ForeignKey("powersets.id"), nullable=False)
    level_available = Column(Integer, default=1)
    power_type = Column(String(50))  # attack, defense, control, support, travel
    target_type = Column(String(50))  # self, ally, enemy, location

    # Base stats
    accuracy = Column(Numeric(5, 2), default=1.0)
    damage_scale = Column(Numeric(5, 2))
    endurance_cost = Column(Numeric(5, 2))
    recharge_time = Column(Numeric(6, 2))
    activation_time = Column(Numeric(4, 2))
    range_feet = Column(Integer)
    radius_feet = Column(Integer)
    max_targets = Column(Integer)

    # Effects stored as JSONB for flexibility
    effects = Column(JSON)

    # Additional power data fields
    internal_name = Column(String(100))  # Internal power name from game data
    requires_line_of_sight = Column(Boolean, default=True)
    modes_required = Column(JSON)  # JSON array of required modes
    modes_disallowed = Column(JSON)  # JSON array of disallowed modes
    ai_report = Column(String(50))  # AI behavior type
    effect_groups = Column(JSON)  # Detailed effect group data

    # UI information
    icon_path = Column(String(255))
    display_order = Column(Integer)
    display_info = Column(JSON)  # Additional display information
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    powerset = relationship("Powerset", back_populates="powers")
    prerequisites = relationship(
        "PowerPrerequisite",
        foreign_keys="PowerPrerequisite.power_id",
        back_populates="power",
    )
    required_for = relationship(
        "PowerPrerequisite",
        foreign_keys="PowerPrerequisite.required_power_id",
        back_populates="required_power",
    )
    build_powers = relationship("BuildPower", back_populates="power")
    compatibilities = relationship(
        "PowerEnhancementCompatibility", back_populates="power"
    )

    __table_args__ = (
        Index("idx_power_level", "level_available"),
        Index("idx_power_type", "power_type"),
    )


class PowerPrerequisite(Base):
    """Power prerequisite model for power requirements."""

    __tablename__ = "power_prerequisites"

    id = Column(Integer, primary_key=True, index=True)
    power_id = Column(Integer, ForeignKey("powers.id"), nullable=False)
    required_power_id = Column(Integer, ForeignKey("powers.id"), nullable=False)
    required_level = Column(Integer)
    prerequisite_type = Column(String(20))  # one_of, all_of
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    power = relationship(
        "Power", foreign_keys=[power_id], back_populates="prerequisites"
    )
    required_power = relationship(
        "Power", foreign_keys=[required_power_id], back_populates="required_for"
    )

    __table_args__ = (
        Index("idx_prereq_power", "power_id"),
        Index("idx_prereq_required", "required_power_id"),
    )


class EnhancementSet(Base):
    """Enhancement set model representing named sets."""

    __tablename__ = "enhancement_sets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(100))
    description = Column(Text)
    min_level = Column(Integer, default=10)
    max_level = Column(Integer, default=50)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    enhancements = relationship("Enhancement", back_populates="enhancement_set")
    set_bonuses = relationship("SetBonus", back_populates="enhancement_set")


class Enhancement(Base):
    """Enhancement model representing power modifications."""

    __tablename__ = "enhancements"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    display_name = Column(String(200))  # Increased size based on data
    short_name = Column(String(50))  # Added for enhancement abbreviations
    description = Column(Text)  # Added for enhancement descriptions
    enhancement_type = Column(
        String(50), index=True
    )  # IO, SO, DO, TO, HamiO, set_piece
    set_id = Column(Integer, ForeignKey("enhancement_sets.id"))
    level_min = Column(Integer, default=1)
    level_max = Column(Integer, default=50)

    # Enhancement values as percentages
    accuracy_bonus = Column(Numeric(5, 2))
    damage_bonus = Column(Numeric(5, 2))
    endurance_bonus = Column(Numeric(5, 2))
    recharge_bonus = Column(Numeric(5, 2))
    defense_bonus = Column(Numeric(5, 2))
    resistance_bonus = Column(Numeric(5, 2))

    # Additional bonuses as JSONB
    other_bonuses = Column(JSON)
    unique_enhancement = Column(Boolean, default=False)
    icon_path = Column(String(255))
    recipe_name = Column(String(100))  # Added for recipe references
    salvage_name = Column(String(100))  # Added for salvage references
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    enhancement_set = relationship("EnhancementSet", back_populates="enhancements")
    build_enhancements = relationship("BuildEnhancement", back_populates="enhancement")

    __table_args__ = (Index("idx_enhancement_level", "level_min", "level_max"),)


class SetBonus(Base):
    """Set bonus model representing enhancement set bonuses."""

    __tablename__ = "set_bonuses"

    id = Column(Integer, primary_key=True, index=True)
    set_id = Column(Integer, ForeignKey("enhancement_sets.id"), nullable=False)
    pieces_required = Column(Integer, nullable=False, index=True)  # 2, 3, 4, 5, 6
    bonus_description = Column(Text)

    # Bonus values
    bonus_type = Column(String(50))  # defense, resistance, recharge, etc.
    bonus_amount = Column(Numeric(5, 2))
    bonus_details = Column(JSON)  # For complex bonuses
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    enhancement_set = relationship("EnhancementSet", back_populates="set_bonuses")

    __table_args__ = (Index("idx_set_bonus_set", "set_id"),)


class PowerEnhancementCompatibility(Base):
    """Power enhancement compatibility model."""

    __tablename__ = "power_enhancement_compatibility"

    id = Column(Integer, primary_key=True, index=True)
    power_id = Column(Integer, ForeignKey("powers.id"), nullable=False)
    enhancement_type = Column(
        String(50), nullable=False
    )  # accuracy, damage, endurance, etc.
    allowed = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    power = relationship("Power", back_populates="compatibilities")

    __table_args__ = (
        UniqueConstraint(
            "power_id", "enhancement_type", name="uq_power_enhancement_type"
        ),
        Index("idx_compat_power", "power_id"),
        Index("idx_compat_type", "enhancement_type"),
    )


# Character Build Models


class Build(Base):
    """Build model representing stored character builds."""

    __tablename__ = "builds"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    archetype_id = Column(Integer, ForeignKey("archetypes.id"), nullable=False)
    primary_powerset_id = Column(Integer, ForeignKey("powersets.id"), nullable=False)
    secondary_powerset_id = Column(Integer, ForeignKey("powersets.id"), nullable=False)
    user_id = Column(Integer)  # Future user system
    level = Column(Integer, default=1)
    build_data = Column(JSON)  # Complete build data
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    archetype = relationship("Archetype", back_populates="builds")
    primary_powerset = relationship(
        "Powerset", foreign_keys=[primary_powerset_id], back_populates="primary_builds"
    )
    secondary_powerset = relationship(
        "Powerset",
        foreign_keys=[secondary_powerset_id],
        back_populates="secondary_builds",
    )
    build_powers = relationship(
        "BuildPower", back_populates="build", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_build_user", "user_id"),
        Index("idx_build_public", "is_public"),
    )


class BuildPower(Base):
    """Build power model representing powers selected in a build."""

    __tablename__ = "build_powers"

    id = Column(Integer, primary_key=True, index=True)
    build_id = Column(
        Integer, ForeignKey("builds.id", ondelete="CASCADE"), nullable=False
    )
    power_id = Column(Integer, ForeignKey("powers.id"), nullable=False)
    level_taken = Column(Integer, nullable=False)
    slot_count = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    build = relationship("Build", back_populates="build_powers")
    power = relationship("Power", back_populates="build_powers")
    build_enhancements = relationship(
        "BuildEnhancement", back_populates="build_power", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_build_power_build", "build_id"),
        Index("idx_build_power_power", "power_id"),
    )


class BuildEnhancement(Base):
    """Build enhancement model representing enhancements slotted in build powers."""

    __tablename__ = "build_enhancements"

    id = Column(Integer, primary_key=True, index=True)
    build_power_id = Column(
        Integer, ForeignKey("build_powers.id", ondelete="CASCADE"), nullable=False
    )
    enhancement_id = Column(Integer, ForeignKey("enhancements.id"), nullable=False)
    slot_number = Column(Integer, nullable=False)
    enhancement_level = Column(Integer, default=50)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    build_power = relationship("BuildPower", back_populates="build_enhancements")
    enhancement = relationship("Enhancement", back_populates="build_enhancements")

    __table_args__ = (
        Index("idx_build_enh_power", "build_power_id"),
        Index("idx_build_enh_enhancement", "enhancement_id"),
    )


# Game Data Models


class Salvage(Base):
    """Salvage model representing crafting materials."""

    __tablename__ = "salvage"

    id = Column(Integer, primary_key=True, index=True)
    internal_name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(200), nullable=False)
    salvage_type = Column(String(50))  # common, uncommon, rare
    origin = Column(String(50))  # tech, magic, natural
    level_range = Column(String(20))  # 10-25, 26-40, 41-50
    icon_path = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    recipes = relationship("RecipeSalvage", back_populates="salvage")

    __table_args__ = (Index("idx_salvage_type", "salvage_type", "origin"),)


class Recipe(Base):
    """Recipe model representing enhancement crafting recipes."""

    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    internal_name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(200), nullable=False)
    enhancement_id = Column(Integer, ForeignKey("enhancements.id"))
    recipe_type = Column(String(50))  # common, uncommon, rare, very_rare
    level_min = Column(Integer, default=10)
    level_max = Column(Integer, default=50)
    crafting_cost = Column(Integer)  # Influence/Infamy cost
    crafting_cost_premium = Column(Integer)  # Premium recipe cost
    memorized = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    enhancement = relationship("Enhancement")
    salvage_requirements = relationship("RecipeSalvage", back_populates="recipe")

    __table_args__ = (Index("idx_recipe_level", "level_min", "level_max"),)


class RecipeSalvage(Base):
    """Recipe salvage requirements junction table."""

    __tablename__ = "recipe_salvage"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    salvage_id = Column(Integer, ForeignKey("salvage.id"), nullable=False)
    quantity = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    recipe = relationship("Recipe", back_populates="salvage_requirements")
    salvage = relationship("Salvage", back_populates="recipes")

    __table_args__ = (
        UniqueConstraint("recipe_id", "salvage_id", name="uq_recipe_salvage"),
        Index("idx_recipe_salvage_recipe", "recipe_id"),
        Index("idx_recipe_salvage_salvage", "salvage_id"),
    )


class AttributeModifier(Base):
    """Attribute modifier model for detailed power effects."""

    __tablename__ = "attribute_modifiers"

    id = Column(Integer, primary_key=True, index=True)
    power_id = Column(Integer, ForeignKey("powers.id"))
    enhancement_id = Column(Integer, ForeignKey("enhancements.id"))
    attribute_name = Column(String(100), nullable=False, index=True)
    attribute_type = Column(String(50))  # magnitude, duration, etc.
    modifier_table = Column(String(100))  # Reference to modifier table
    scale = Column(Numeric(10, 4))
    aspect = Column(String(50))  # Current, Max, Strength, etc.
    application_type = Column(String(50))  # OnTick, OnActivate, etc.
    target_type = Column(String(50))  # Self, Enemy, Ally, etc.
    effect_area = Column(String(50))  # SingleTarget, Cone, Sphere, etc.
    flags = Column(JSON)  # Various flags as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    power = relationship("Power")
    enhancement = relationship("Enhancement")

    __table_args__ = (
        Index("idx_attribmod_power", "power_id"),
        Index("idx_attribmod_enhancement", "enhancement_id"),
        Index("idx_attribmod_attribute", "attribute_name"),
    )


class TypeGrade(Base):
    """Type grade model for archetype-specific modifiers."""

    __tablename__ = "type_grades"

    id = Column(Integer, primary_key=True, index=True)
    archetype_id = Column(Integer, ForeignKey("archetypes.id"))
    attribute_name = Column(String(100), nullable=False)
    grade_type = Column(String(50))  # melee_damage, ranged_damage, etc.
    modifier_value = Column(Numeric(10, 4))
    level_scaling = Column(JSON)  # Level-based scaling data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    archetype = relationship("Archetype")

    __table_args__ = (
        UniqueConstraint(
            "archetype_id", "attribute_name", "grade_type", name="uq_type_grade"
        ),
        Index("idx_type_grade_archetype", "archetype_id"),
        Index("idx_type_grade_attribute", "attribute_name"),
    )


# Data Import Models


class ImportLog(Base):
    """Import log model for tracking data imports from game files."""

    __tablename__ = "import_logs"

    id = Column(Integer, primary_key=True, index=True)
    import_type = Column(String(50))  # full, incremental, patch
    source_file = Column(String(255))
    game_version = Column(String(50))
    records_processed = Column(Integer)
    records_imported = Column(Integer)
    errors = Column(Integer)
    import_data = Column(JSON)  # Detailed import statistics
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
