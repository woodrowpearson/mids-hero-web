"""
Powerset API endpoints for Mids-Web backend.
"""

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/powersets/{powerset_id}")
async def get_powerset(powerset_id: int):
    """Get a specific powerset by ID."""
    # Placeholder implementation
    if powerset_id == 1:
        return {
            "id": 1,
            "name": "Archery",
            "description": "Ranged attacks using a bow",
            "archetype_id": 1,
            "powers": [
                {"id": 1, "name": "Snap Shot", "level_available": 1},
                {"id": 2, "name": "Aimed Shot", "level_available": 2},
                {"id": 3, "name": "Fistful of Arrows", "level_available": 4},
            ],
        }
    else:
        raise HTTPException(status_code=404, detail="Powerset not found")
