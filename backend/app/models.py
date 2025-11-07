"""
Database models for Mids-Web backend - Updated for filtered_data import.

Redesigned schema to support the rich JSON data from filtered_data directory.
This represents a clean break from the old MHD-based schema.
"""

from datetime import datetime

from sqlalchemy import (
    ARRAY,
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

    # Basic identification
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(100))
    icon = Column(String(255))

    # Help text
    display_help = Column(Text)
    display_short_help = Column(Text)

    # Game mechanics
    default_rank = Column(String(50))
    class_requires = Column(String(200))
    restrictions = Column(JSON)  # Array of restrictions
    level_up_respecs = Column(JSON)  # Array of level-based respecs

    # Power categories
    primary_category = Column(String(100), index=True)
    secondary_category = Column(String(100), index=True)
    power_pool_category = Column(String(100))
    epic_pool_category = Column(String(100))

    # Stats and modifiers
    defiant_scale = Column(Numeric(5, 2))
    deep_sleep_resistance = Column(Numeric(5, 2))
    off_defiant_hit_points_attrib = Column(Integer)

    # Faction
    is_villain = Column(Boolean, default=False)

    # Localization
    class_key = Column(String(100))

    # Base attributes (stored as JSON for flexibility)
    attrib_base = Column(JSON)  # Complete attrib_base object from filtered_data

    # Legacy fields (can be computed from attrib_base if needed)
    hit_points_base = Column(Integer)
    hit_points_max = Column(Integer)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    powersets = relationship("Powerset", back_populates="archetype")
    builds = relationship("Build", back_populates="archetype")
    modifier_tables = relationship("ArchetypeModifierTable", back_populates="archetype")

    __table_args__ = (
        Index("idx_archetype_categories", "primary_category", "secondary_category"),
    )


class ArchetypeModifierTable(Base):
    """Archetype modifier tables for damage/effect calculations."""

    __tablename__ = "archetype_modifier_tables"

    id = Column(Integer, primary_key=True, index=True)
    archetype_id = Column(Integer, ForeignKey("archetypes.id"), nullable=False)

    # Table identification
    table_name = Column(
        String(100), nullable=False, index=True
    )  # e.g., "Melee_Damage", "Ranged_Damage"

    # The actual modifier values (array of floats for each level)
    values = Column(JSON, nullable=False)  # Array of numeric values

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    archetype = relationship("Archetype", back_populates="modifier_tables")

    __table_args__ = (
        UniqueConstraint("archetype_id", "table_name", name="uq_archetype_table"),
        Index("idx_archetype_table_name", "archetype_id", "table_name"),
    )


class Powerset(Base):
    """Powerset model representing groups of powers."""

    __tablename__ = "powersets"

    id = Column(Integer, primary_key=True, index=True)

    # Identification
    name = Column(String(100), nullable=False, index=True)  # Internal name
    display_name = Column(String(100))
    display_fullname = Column(String(200))

    # Help text
    display_help = Column(Text)
    display_short_help = Column(Text)

    # Archetype association
    archetype_id = Column(Integer, ForeignKey("archetypes.id"))

    # Powerset type
    powerset_type = Column(
        String(20), nullable=False, index=True
    )  # primary, secondary, pool, epic, incarnate

    # Source information
    source_file = Column(String(500))

    # UI
    icon = Column(String(255))

    # Requirements
    requires = Column(Text)  # Expression string for requirements

    # Powers in this set
    power_names = Column(JSON)  # Array of full power names
    power_display_names = Column(JSON)  # Array of display names
    power_short_helps = Column(JSON)  # Array of short help texts
    available_level = Column(JSON)  # Array of levels when powers become available

    # Metadata
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
        UniqueConstraint("name", "archetype_id", name="uq_powerset_archetype"),
        Index("idx_powerset_type", "powerset_type"),
    )


class Power(Base):
    """Power model representing individual abilities - stores complete JSON for complex data."""

    __tablename__ = "powers"

    id = Column(Integer, primary_key=True, index=True)

    # Identification
    name = Column(String(100), nullable=False, index=True)  # Short name
    full_name = Column(
        String(200), unique=True, nullable=False, index=True
    )  # Full qualified name
    display_name = Column(String(100))
    display_fullname = Column(String(200))
    short_name = Column(String(50))

    # Power type
    type = Column(String(50), index=True)  # Click, Toggle, Auto, etc.

    # Help text
    display_help = Column(Text)
    display_short_help = Column(Text)

    # Powerset association
    powerset_id = Column(Integer, ForeignKey("powersets.id"))
    powerset_name = Column(String(200), index=True)  # Denormalized for queries

    # Level availability
    available_level = Column(Integer, index=True)
    level_bought = Column(Integer, default=-1)

    # UI information
    icon = Column(String(255))
    tray_placement = Column(String(50))
    tray_number = Column(Integer)
    tray_slot = Column(Integer)
    server_tray_priority = Column(Integer)

    # Basic stats (commonly queried fields extracted for performance)
    accuracy = Column(Numeric(5, 2), default=1.0)
    activation_time = Column(Numeric(6, 2))
    recharge_time = Column(Numeric(6, 2))
    endurance_cost = Column(Numeric(6, 2))
    range = Column(Numeric(6, 2))
    radius = Column(Numeric(6, 2))
    arc = Column(Numeric(6, 4))
    max_targets_hit = Column(Integer)

    # Target information
    target_type = Column(String(50))
    target_visibility = Column(String(50))
    effect_area = Column(String(50))  # Cone, Sphere, etc.

    # Requirements
    requires = Column(Text)
    activate_requires = Column(Text)
    confirm_requires = Column(Text)

    # Enhancement information
    max_boosts = Column(Integer, default=6)
    boosts_allowed = Column(JSON)  # Array of allowed boost types
    allowed_boostset_cats = Column(JSON)  # Array of allowed boost set categories

    # Complete power data stored as JSON (for complex nested structures)
    # This includes: effects, templates, messages, flags, expressions, etc.
    power_data = Column(JSON)  # Complete power JSON from filtered_data

    # Source metadata from original JSON
    source_metadata = Column(JSON, nullable=True, comment="Raw JSON from source")

    # Archetypes that can use this power
    archetypes = Column(JSON)  # Array of archetype names

    # Tags for power interactions
    tags = Column(JSON)  # Array of tag names this power has

    # Groups
    exclusion_groups = Column(JSON)  # Array of exclusion group names
    recharge_groups = Column(JSON)  # Array of recharge group names

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    powerset = relationship("Powerset", back_populates="powers")
    build_powers = relationship("BuildPower", back_populates="power")

    __table_args__ = (
        Index("idx_power_level", "available_level"),
        Index("idx_power_type", "type"),
        Index("idx_power_powerset", "powerset_name"),
    )


class EnhancementSet(Base):
    """Enhancement set model representing named sets with bonuses."""

    __tablename__ = "enhancement_sets"

    id = Column(Integer, primary_key=True, index=True)

    # Identification
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(100))

    # Grouping
    group_name = Column(String(100), index=True)  # e.g., "Stuns", "Melee Damage"

    # Level range
    min_level = Column(Integer, default=10)
    max_level = Column(Integer, default=50)

    # Conversion groups (for converters)
    conversion_groups = Column(JSON)  # Array of rarity levels

    # Boost lists (all enhancement variants in this set)
    boost_lists = Column(JSON)  # Array of arrays of boost full names

    # Set bonuses
    bonuses = Column(JSON)  # Array of bonus objects with min/max requirements

    # Computed metadata (processed enhancement data)
    computed = Column(JSON)  # Complete computed object from filtered_data

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    enhancements = relationship("Enhancement", back_populates="enhancement_set")

    __table_args__ = (
        Index("idx_enhset_group", "group_name"),
        Index("idx_enhset_level", "min_level", "max_level"),
    )


class Enhancement(Base):
    """Enhancement model representing individual enhancements/IOs."""

    __tablename__ = "enhancements"

    id = Column(Integer, primary_key=True, index=True)

    # Identification
    name = Column(String(200), nullable=False, index=True)  # Internal name
    display_name = Column(String(200))
    computed_name = Column(String(200))  # Computed display name

    # Set association
    set_id = Column(Integer, ForeignKey("enhancement_sets.id"))
    boostset_name = Column(String(100), index=True)  # Denormalized for queries

    # Type
    boost_type = Column(String(100), index=True)  # e.g., "Enhance Disorient"

    # Level information
    level_min = Column(Integer, default=1)
    level_max = Column(Integer, default=50)
    min_slot_level = Column(Integer)
    min_bonus_level = Column(Integer)
    only_at_50 = Column(Boolean, default=False)

    # Slotting requirements
    slot_requires = Column(Text)  # Expression for slotting requirements
    ignores_level_differences = Column(Boolean, default=False)
    bonuses_ignore_exemplar = Column(Boolean, default=False)

    # Trading/combining
    combinable = Column(Boolean, default=False)
    tradeable = Column(Boolean, default=False)
    account_bound = Column(Boolean, default=False)

    # Attuned/catalyst system
    boostable = Column(Boolean, default=False)  # Can be boosted
    attuned = Column(Boolean, default=False)  # Is attuned
    catalyzes_to = Column(JSON)  # [internal_name, display_name] if can catalyst
    superior_scales = Column(Boolean, default=False)

    # Special flags
    is_proc = Column(Boolean, default=False)
    is_unique = Column(Boolean, default=False)

    # Restrictions
    restricted_ats = Column(JSON)  # Array of restricted archetype names
    unique_group = Column(JSON)  # Array of enhancement names in unique group

    # What this enhancement affects
    aspects = Column(JSON)  # Array of aspect names (e.g., ["Accuracy", "Damage"])

    # Global bonuses (for procs/globals)
    global_bonuses = Column(JSON)

    # UI
    icon = Column(String(255))

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    enhancement_set = relationship("EnhancementSet", back_populates="enhancements")
    build_enhancements = relationship("BuildEnhancement", back_populates="enhancement")

    __table_args__ = (
        Index("idx_enhancement_set", "set_id"),
        Index("idx_enhancement_type", "boost_type"),
        Index("idx_enhancement_level", "level_min", "level_max"),
    )


class Tag(Base):
    """Tag model for power interaction system."""

    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)

    # Tag identification
    tag = Column(String(200), unique=True, nullable=False, index=True)

    # Powers that have this tag (bears)
    bears = Column(JSON)  # Array of [display_name, internal_name] pairs

    # Powers affected by this tag
    affects = Column(JSON)  # Array of [display_name, internal_name] pairs

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index("idx_tag_name", "tag"),)


class ExclusionGroup(Base):
    """Exclusion group model for mutually exclusive powers."""

    __tablename__ = "exclusion_groups"

    id = Column(Integer, primary_key=True, index=True)

    # Group identification
    group = Column(String(200), unique=True, nullable=False, index=True)

    # Powers in this group (only one can be slotted)
    powers = Column(JSON)  # Array of [display_name, internal_name] pairs

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index("idx_exclusion_group_name", "group"),)


class RechargeGroup(Base):
    """Recharge group model for powers that share recharge timers."""

    __tablename__ = "recharge_groups"

    id = Column(Integer, primary_key=True, index=True)

    # Group identification
    group = Column(String(200), unique=True, nullable=False, index=True)

    # Powers in this group (share recharge timer)
    powers = Column(JSON)  # Array of [display_name, internal_name] pairs

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index("idx_recharge_group_name", "group"),)


# Character Build Models (unchanged from original)


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


# Import tracking model


class ImportLog(Base):
    """Import log model for tracking data imports."""

    __tablename__ = "import_logs"

    id = Column(Integer, primary_key=True, index=True)
    import_type = Column(String(50), nullable=False, index=True)
    source_file = Column(String(500))
    records_processed = Column(Integer, default=0)
    records_imported = Column(Integer, default=0)
    errors = Column(Integer, default=0)
    import_data = Column(JSON)  # Error details, etc.
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)

    __table_args__ = (
        Index("idx_import_type", "import_type"),
        Index("idx_import_started", "started_at"),
    )
