"""
Powerset API endpoints for Mids-Web backend.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud
from .. import schemas as app_schemas
from ..database import get_db

router = APIRouter()


@router.get("/powersets/{powerset_id}", response_model=app_schemas.Powerset)
async def get_powerset(
    powerset_id: int,
    db: Session = Depends(get_db),
):
    """
    Get a specific powerset by ID.

    Returns detailed information about a powerset.
    """
    powerset = crud.get_powerset(db, powerset_id=powerset_id)
    if powerset is None:
        raise HTTPException(status_code=404, detail="Powerset not found")

    return powerset


@router.get(
    "/powersets/{powerset_id}/detailed", response_model=app_schemas.PowersetWithPowers
)
async def get_powerset_detailed(
    powerset_id: int,
    db: Session = Depends(get_db),
):
    """
    Get a specific powerset by ID with all its powers.

    Returns detailed information about a powerset including all associated powers.
    """
    powerset = crud.get_powerset(db, powerset_id=powerset_id)
    if powerset is None:
        raise HTTPException(status_code=404, detail="Powerset not found")

    # Get powers for this powerset
    powers = crud.get_powers_by_powerset(db, powerset_id=powerset_id)

    # Create response with powers
    powerset_dict = {
        "id": powerset.id,
        "name": powerset.name,
        "display_name": powerset.display_name,
        "description": powerset.description,
        "powerset_type": powerset.powerset_type,
        "icon_path": powerset.icon_path,
        "archetype_id": powerset.archetype_id,
        "created_at": powerset.created_at,
        "updated_at": powerset.updated_at,
        "powers": powers,
    }

    return powerset_dict


@router.get("/powersets/{powerset_id}/powers", response_model=list[app_schemas.Power])
async def get_powerset_powers(
    powerset_id: int,
    db: Session = Depends(get_db),
):
    """
    Get all powers in a specific powerset.

    Returns a list of powers that belong to the specified powerset.
    """
    # First check if powerset exists
    powerset = crud.get_powerset(db, powerset_id=powerset_id)
    if powerset is None:
        raise HTTPException(status_code=404, detail="Powerset not found")

    powers = crud.get_powers_by_powerset(db, powerset_id=powerset_id)
    return powers
