"""
Archetype API Router - Clean, simple, fast
Epic 2.5.5: Demonstrates JSON-native simplicity
"""
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from ..services.game_data_service import game_data_service

router = APIRouter(
    prefix="/api/v1/archetypes",
    tags=["archetypes"],
)

@router.get("/", response_model=List[Dict[str, Any]])
async def list_archetypes():
    """
    Get all available archetypes.
    
    Returns a list of all City of Heroes archetypes with their complete data.
    This directly serves JSON files - no database queries, no ORM overhead.
    """
    try:
        return game_data_service.get_all_archetypes()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{archetype_name}")
async def get_archetype(archetype_name: str):
    """
    Get detailed information for a specific archetype.
    
    Parameters:
    - archetype_name: The name of the archetype (e.g., "blaster", "tanker")
    
    Returns complete archetype data including:
    - Display name and description
    - Primary/Secondary powerset options
    - Inherent powers
    - Base stats and modifiers
    """
    try:
        return game_data_service.get_archetype(archetype_name)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, 
            detail=f"Archetype '{archetype_name}' not found"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{archetype_name}/powersets")
async def get_archetype_powersets(archetype_name: str):
    """
    Get all available powersets for an archetype.
    
    Returns a list of powerset names that are available for the specified archetype.
    This includes both primary and secondary powersets.
    """
    try:
        powersets = game_data_service.get_archetype_powersets(archetype_name)
        if not powersets:
            raise HTTPException(
                status_code=404,
                detail=f"No powersets found for archetype '{archetype_name}'"
            )
        return {"archetype": archetype_name, "powersets": powersets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{archetype_name}/powersets/{powerset_name}")
async def get_powerset(archetype_name: str, powerset_name: str):
    """
    Get detailed powerset information for an archetype.
    
    Parameters:
    - archetype_name: The archetype (e.g., "blaster")
    - powerset_name: The powerset name (e.g., "fire_blast")
    
    Returns complete powerset data including:
    - All powers in the set
    - Power availability by level
    - Power effects and attributes
    - Enhancement categories
    """
    try:
        return game_data_service.get_powerset(archetype_name, powerset_name)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Powerset '{powerset_name}' not found for archetype '{archetype_name}'"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/powers")
async def search_powers(
    q: str = Query(..., description="Search query for power names or descriptions"),
    archetype: str = Query(None, description="Filter results by archetype")
):
    """
    Search for powers across all archetypes.
    
    Parameters:
    - q: Search query (searches power names and descriptions)
    - archetype: Optional filter by archetype
    
    Returns a list of powers matching the search criteria.
    """
    try:
        results = game_data_service.search_powers(q, archetype)
        return {
            "query": q,
            "archetype_filter": archetype,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))