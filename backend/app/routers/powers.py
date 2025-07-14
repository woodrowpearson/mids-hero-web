"""
Power API endpoints for Mids-Web backend.
"""

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/powers/{power_id}")
async def get_power(power_id: int):
    """Get a specific power by ID."""
    # Placeholder implementation
    if power_id == 1:
        return {
            "id": 1,
            "name": "Snap Shot",
            "description": "A quick, light attack that has a small chance of knocking down foes.",
            "level_available": 1,
            "powerset_id": 1,
            "prerequisites": [],
            "enhancement_categories": ["Damage", "Accuracy", "Range"],
        }
    else:
        raise HTTPException(status_code=404, detail="Power not found")
