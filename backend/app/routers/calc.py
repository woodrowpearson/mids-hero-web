"""Calculator API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.calc_schemas.build import BuildPayload
from app.calc_schemas.response import CalcResponse
from app.services.calculator import run_calculations

router = APIRouter(prefix="/api", tags=["calculator"])


@router.post("/calculate", response_model=CalcResponse)
async def calculate(
    build: BuildPayload,
    db: Session = Depends(get_db)
) -> CalcResponse:
    """Calculate build statistics.

    This endpoint accepts a complete build configuration and returns
    calculated statistics including:
    - Per-power enhanced values
    - Total defense/resistance values
    - Set bonuses
    - Validation warnings for caps or invalid configurations

    Args:
        build: Complete build configuration
        db: Database session

    Returns:
        Calculated build statistics

    Raises:
        HTTPException: If calculation fails or invalid data provided
    """
    try:
        return run_calculations(build, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Calculation error: {str(e)}"
        )
