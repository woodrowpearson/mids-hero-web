"""
Database models for Mids-Web backend.
"""

from sqlalchemy import JSON, Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


class Archetype(Base):
    """Archetype model representing character classes."""

    __tablename__ = "archetypes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    description = Column(Text)
    hit_point_multiplier = Column(Float)
    endurance_multiplier = Column(Float)

    # Relationships
    powersets = relationship("Powerset", back_populates="archetype")


class Powerset(Base):
    """Powerset model representing groups of powers."""

    __tablename__ = "powersets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    description = Column(Text)
    powerset_type = Column(String(50))  # primary, secondary, pool, epic
    archetype_id = Column(Integer, ForeignKey("archetypes.id"))

    # Relationships
    archetype = relationship("Archetype", back_populates="powersets")
    powers = relationship("Power", back_populates="powerset")


class Power(Base):
    """Power model representing individual abilities."""

    __tablename__ = "powers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    description = Column(Text)
    level_available = Column(Integer)
    powerset_id = Column(Integer, ForeignKey("powersets.id"))

    # Power attributes
    base_damage = Column(Float)
    base_accuracy = Column(Float)
    base_recharge = Column(Float)
    base_endurance_cost = Column(Float)

    # Enhancement categories (stored as JSON)
    enhancement_categories = Column(JSON)

    # Relationships
    powerset = relationship("Powerset", back_populates="powers")


class Enhancement(Base):
    """Enhancement model representing power modifications."""

    __tablename__ = "enhancements"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    description = Column(Text)
    category = Column(String(50))
    enhancement_type = Column(String(50))  # SO, IO, Set IO, etc.
    set_name = Column(String(100))
    level_required = Column(Integer)

    # Bonus values (stored as JSON)
    bonus_values = Column(JSON)


class SetBonus(Base):
    """Set bonus model representing enhancement set bonuses."""

    __tablename__ = "set_bonuses"

    id = Column(Integer, primary_key=True, index=True)
    set_name = Column(String(100), index=True)
    pieces_required = Column(Integer)
    bonus_description = Column(Text)

    # Bonus values (stored as JSON)
    bonus_values = Column(JSON)
