"""
Enhancement API endpoints for Mids-Web backend.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..database import get_db

router = APIRouter()


@router.get("/enhancements", response_model=list[schemas.Enhancement])
async def get_enhancements(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of items to return"),
    enhancement_type: str | None = Query(
        None,
        description="Filter by enhancement type (IO, SO, DO, TO, HamiO, set_piece)",
    ),
    db: Session = Depends(get_db),
):
    """
    Get all enhancements.

    Returns a list of all enhancements with pagination support.
    Optionally filter by enhancement type.
    """
    enhancements = crud.get_enhancements(db, skip=skip, limit=limit)

    # Filter by type if specified
    if enhancement_type:
        enhancements = [
            e for e in enhancements if e.enhancement_type == enhancement_type
        ]

    return enhancements


@router.get("/enhancements/{enhancement_id}", response_model=schemas.Enhancement)
async def get_enhancement(
    enhancement_id: int,
    db: Session = Depends(get_db),
):
    """
    Get a specific enhancement by ID.

    Returns detailed information about a single enhancement.
    """
    enhancement = crud.get_enhancement(db, enhancement_id=enhancement_id)
    if enhancement is None:
        raise HTTPException(status_code=404, detail="Enhancement not found")
    return enhancement


@router.get("/enhancement-sets", response_model=list[schemas.EnhancementSet])
async def get_enhancement_sets(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of items to return"),
    db: Session = Depends(get_db),
):
    """
    Get all enhancement sets.

    Returns a list of all enhancement sets with pagination support.
    """
    sets = db.query(models.EnhancementSet).offset(skip).limit(limit).all()
    return sets


class EnhancementSetWithBonuses(schemas.EnhancementSet):
    """Enhancement set schema with bonuses and enhancements."""

    enhancements: list[schemas.Enhancement] = []


@router.get("/enhancement-sets/{set_id}", response_model=EnhancementSetWithBonuses)
async def get_enhancement_set(
    set_id: int,
    include_enhancements: bool = True,
    include_bonuses: bool = True,
    db: Session = Depends(get_db),
):
    """
    Get a specific enhancement set by ID.

    Returns detailed information about an enhancement set,
    optionally including its enhancements and set bonuses.

    Note: Set bonuses are stored in the 'bonuses' JSON field on the EnhancementSet model.
    """
    enhancement_set = (
        db.query(models.EnhancementSet)
        .filter(models.EnhancementSet.id == set_id)
        .first()
    )

    if enhancement_set is None:
        raise HTTPException(status_code=404, detail="Enhancement set not found")

    # Convert to dict to add related data
    set_data = enhancement_set.__dict__.copy()

    # Include enhancements if requested
    if include_enhancements:
        enhancements = (
            db.query(models.Enhancement)
            .filter(models.Enhancement.set_id == set_id)
            .all()
        )
        set_data["enhancements"] = enhancements
    else:
        set_data["enhancements"] = []

    # Bonuses are already in the model as a JSON field
    # If include_bonuses is False, set to None or empty array
    if not include_bonuses:
        set_data["bonuses"] = None

    return EnhancementSetWithBonuses(**set_data)
