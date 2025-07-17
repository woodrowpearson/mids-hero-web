"""
Archetype API endpoints for Mids-Web backend.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter()


@router.get("/archetypes", response_model=list[schemas.Archetype])
async def get_archetypes(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of items to return"),
    db: Session = Depends(get_db),
):
    """
    Get all archetypes.

    Returns a list of all character archetypes (classes) with pagination support.
    """
    archetypes = crud.get_archetypes(db, skip=skip, limit=limit)
    return archetypes


@router.get("/archetypes/{archetype_id}", response_model=schemas.Archetype)
async def get_archetype(
    archetype_id: int,
    db: Session = Depends(get_db),
):
    """
    Get a specific archetype by ID.

    Returns detailed information about a single archetype.
    """
    archetype = crud.get_archetype(db, archetype_id=archetype_id)
    if archetype is None:
        raise HTTPException(status_code=404, detail="Archetype not found")
    return archetype


@router.get(
    "/archetypes/{archetype_id}/powersets", response_model=list[schemas.Powerset]
)
async def get_archetype_powersets(
    archetype_id: int,
    powerset_type: str | None = Query(
        None, description="Filter by powerset type (primary, secondary, pool, epic)"
    ),
    db: Session = Depends(get_db),
):
    """
    Get all powersets for a specific archetype.

    Returns a list of powersets available to the specified archetype.
    Optionally filter by powerset type.
    """
    # First check if archetype exists
    archetype = crud.get_archetype(db, archetype_id=archetype_id)
    if archetype is None:
        raise HTTPException(status_code=404, detail="Archetype not found")

    # Get powersets
    powersets = crud.get_powersets_by_archetype(db, archetype_id=archetype_id)

    # Filter by type if specified
    if powerset_type:
        powersets = [ps for ps in powersets if ps.powerset_type == powerset_type]

    return powersets
