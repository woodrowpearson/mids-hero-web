"""
Powerset API endpoints for Mids-Web backend.
"""


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter()


class PowersetWithPowers(schemas.Powerset):
    """Powerset schema with related powers."""
    powers: list[schemas.Power] = []


@router.get("/powersets/{powerset_id}", response_model=PowersetWithPowers)
async def get_powerset(
    powerset_id: int,
    include_powers: bool = True,
    db: Session = Depends(get_db),
):
    """
    Get a specific powerset by ID.

    Returns detailed information about a powerset, optionally including its powers.
    """
    powerset = crud.get_powerset(db, powerset_id=powerset_id)
    if powerset is None:
        raise HTTPException(status_code=404, detail="Powerset not found")

    # Convert to dict to add powers
    powerset_data = powerset.__dict__.copy()

    # Include powers if requested
    if include_powers:
        powers = crud.get_powers_by_powerset(db, powerset_id=powerset_id)
        powerset_data["powers"] = powers
    else:
        powerset_data["powers"] = []

    return PowersetWithPowers(**powerset_data)


@router.get("/powersets/{powerset_id}/powers", response_model=list[schemas.Power])
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
