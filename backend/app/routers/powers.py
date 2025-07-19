"""
Power API endpoints for Mids-Web backend.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..database import get_db

router = APIRouter()


@router.get("/powers/test/{power_id}")
async def test_power(
    power_id: int,
    db: Session = Depends(get_db),
):
    """Test endpoint to debug power retrieval."""
    try:
        power = crud.get_power(db, power_id=power_id)
        if power is None:
            return {"error": "Power not found"}

        # Return basic info without schema validation
        # Get all attributes
        attrs = {}
        for col in power.__table__.columns:
            val = getattr(power, col.name)
            if val is not None and hasattr(val, '__class__') and 'Decimal' in str(val.__class__):
                attrs[col.name] = float(val)
            else:
                attrs[col.name] = val
        return attrs
    except Exception as e:
        return {"error": str(e)}


@router.get("/powers/{power_id}")
async def get_power(
    power_id: int,
    db: Session = Depends(get_db),
):
    """
    Get a specific power by ID.

    Returns detailed information about a power.
    """
    power = crud.get_power(db, power_id=power_id)
    if power is None:
        raise HTTPException(status_code=404, detail="Power not found")

    # Convert decimals to floats manually
    result = {}
    for col in power.__table__.columns:
        val = getattr(power, col.name)
        if val is not None and hasattr(val, '__class__') and 'Decimal' in str(val.__class__):
            result[col.name] = float(val)
        else:
            result[col.name] = val

    return result


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
