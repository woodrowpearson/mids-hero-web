"""
Enhancements API Router
Epic 2.5.5: JSON-native enhancement/boost data access
"""
from fastapi import APIRouter, HTTPException
from ..services.game_data_service import game_data_service

router = APIRouter(
    prefix="/api/v1/enhancements",
    tags=["enhancements"],
)

@router.get("/sets")
async def get_enhancement_sets():
    """
    Get all enhancement sets.
    
    Returns a list of all available enhancement sets (IOs, ATOs, etc.)
    with their bonuses and requirements.
    """
    try:
        return game_data_service.get_boost_sets()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sets/{set_name}")
async def get_enhancement_set(set_name: str):
    """
    Get detailed information for a specific enhancement set.
    
    Parameters:
    - set_name: The name of the enhancement set
    
    Returns complete set data including:
    - Individual enhancements in the set
    - Set bonuses at different thresholds
    - Level requirements and restrictions
    """
    try:
        return game_data_service.get_enhancement(set_name)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Enhancement set '{set_name}' not found"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{enhancement_name}")
async def get_enhancement(enhancement_name: str):
    """
    Get detailed information for a specific enhancement.
    
    Parameters:
    - enhancement_name: The name of the enhancement
    
    Returns enhancement data including:
    - Enhancement effects and values
    - Valid slot types
    - Level range
    - Special properties (unique, proc, etc.)
    """
    try:
        return game_data_service.get_enhancement(enhancement_name)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Enhancement '{enhancement_name}' not found"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))