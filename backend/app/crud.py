"""
CRUD operations for Mids-Web backend.
"""

from sqlalchemy.orm import Session

from . import models, schemas


def get_archetype(db: Session, archetype_id: int) -> models.Archetype | None:
    """Get an archetype by ID."""
    return (
        db.query(models.Archetype).filter(models.Archetype.id == archetype_id).first()
    )


def get_archetypes(
    db: Session, skip: int = 0, limit: int = 100
) -> list[models.Archetype]:
    """Get all archetypes."""
    return db.query(models.Archetype).offset(skip).limit(limit).all()


def create_archetype(
    db: Session, archetype: schemas.ArchetypeCreate
) -> models.Archetype:
    """Create a new archetype."""
    db_archetype = models.Archetype(**archetype.dict())
    db.add(db_archetype)
    db.commit()
    db.refresh(db_archetype)
    return db_archetype


def get_powerset(db: Session, powerset_id: int) -> models.Powerset | None:
    """Get a powerset by ID."""
    return db.query(models.Powerset).filter(models.Powerset.id == powerset_id).first()


def get_powersets_by_archetype(db: Session, archetype_id: int) -> list[models.Powerset]:
    """Get all powersets for an archetype."""
    return (
        db.query(models.Powerset)
        .filter(models.Powerset.archetype_id == archetype_id)
        .all()
    )


def get_power(db: Session, power_id: int) -> models.Power | None:
    """Get a power by ID."""
    return db.query(models.Power).filter(models.Power.id == power_id).first()


def get_powers_by_powerset(db: Session, powerset_id: int) -> list[models.Power]:
    """Get all powers for a powerset."""
    return db.query(models.Power).filter(models.Power.powerset_id == powerset_id).all()


def get_enhancements(
    db: Session, skip: int = 0, limit: int = 100
) -> list[models.Enhancement]:
    """Get all enhancements."""
    return db.query(models.Enhancement).offset(skip).limit(limit).all()


def get_enhancement(db: Session, enhancement_id: int) -> models.Enhancement | None:
    """Get an enhancement by ID."""
    return (
        db.query(models.Enhancement)
        .filter(models.Enhancement.id == enhancement_id)
        .first()
    )
