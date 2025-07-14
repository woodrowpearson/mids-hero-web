"""
Enhancement API endpoints for Mids-Web backend.
"""

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/enhancements")
async def get_enhancements():
    """Get all enhancements."""
    # Placeholder implementation
    return [
        {
            "id": 1,
            "name": "Damage",
            "description": "Increases damage output",
            "category": "Damage",
            "bonus_values": {"damage": 33.0},
        },
        {
            "id": 2,
            "name": "Accuracy",
            "description": "Increases accuracy",
            "category": "Accuracy",
            "bonus_values": {"accuracy": 33.0},
        },
    ]


@router.get("/enhancements/{enhancement_id}")
async def get_enhancement(enhancement_id: int):
    """Get a specific enhancement by ID."""
    # Placeholder implementation
    if enhancement_id == 1:
        return {
            "id": 1,
            "name": "Damage",
            "description": "Increases damage output",
            "category": "Damage",
            "bonus_values": {"damage": 33.0},
        }
    else:
        raise HTTPException(status_code=404, detail="Enhancement not found")
