"""
Power API endpoints for Mids-Web backend.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..database import get_db

router = APIRouter()


class PowerWithPrerequisites(schemas.Power):
    """Power schema with prerequisite information."""

    prerequisites: list[schemas.PowerPrerequisite] = []


@router.get("/powers/{power_id}", response_model=PowerWithPrerequisites)
async def get_power(
    power_id: int,
    include_prerequisites: bool = True,
    db: Session = Depends(get_db),
):
    """
    Get a specific power by ID.

    Returns detailed information about a power, optionally including prerequisites.
    """
    power = crud.get_power(db, power_id=power_id)
    if power is None:
        raise HTTPException(status_code=404, detail="Power not found")

    # Convert to dict to add prerequisites
    power_data = power.__dict__.copy()

    # Include prerequisites if requested
    if include_prerequisites:
        # Get prerequisites for this power
        prerequisites = (
            db.query(models.PowerPrerequisite)
            .filter(models.PowerPrerequisite.power_id == power_id)
            .all()
        )
        power_data["prerequisites"] = prerequisites
    else:
        power_data["prerequisites"] = []

    return PowerWithPrerequisites(**power_data)


@router.get("/powers", response_model=list[schemas.Power])
async def search_powers(
    name: str | None = Query(None, description="Search by power name"),
    power_type: str | None = Query(None, description="Filter by power type"),
    min_level: int | None = Query(
        None, ge=1, le=50, description="Minimum level available"
    ),
    max_level: int | None = Query(
        None, ge=1, le=50, description="Maximum level available"
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """
    Search and filter powers.

    Supports searching by name and filtering by various criteria.
    """
    query = db.query(models.Power)

    # Apply filters
    if name:
        query = query.filter(models.Power.name.ilike(f"%{name}%"))

    if power_type:
        query = query.filter(models.Power.power_type == power_type)

    if min_level is not None:
        query = query.filter(models.Power.level_available >= min_level)

    if max_level is not None:
        query = query.filter(models.Power.level_available <= max_level)

    # Apply pagination
    powers = query.offset(skip).limit(limit).all()
    return powers
