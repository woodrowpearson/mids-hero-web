"""
Powers API Router
Epic 2.5.5: JSON-native power data access
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from ..services.game_data_service import game_data_service

router = APIRouter(
    prefix="/api/v1/powers",
    tags=["powers"],
)

@router.get("/")
async def get_all_powers():
    """
    Get the comprehensive power database.
    
    Returns the complete power search index containing all powers
    in City of Heroes with their detailed attributes.
    """
    try:
        return game_data_service.get_all_powers()
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail="Power database not available"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_powers(
    q: str = Query(..., description="Search query"),
    archetype: Optional[str] = Query(None, description="Filter by archetype")
):
    """
    Search powers by name or description.
    
    Parameters:
    - q: Search query for power names or descriptions
    - archetype: Optional archetype filter
    
    Returns matching powers with relevance ranking.
    """
    try:
        results = game_data_service.search_powers(q, archetype)
        return {
            "query": q,
            "filters": {"archetype": archetype} if archetype else {},
            "count": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_power_stats():
    """
    Get statistics about available power data.
    
    Returns counts and metadata about the power database.
    """
    try:
        return game_data_service.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))