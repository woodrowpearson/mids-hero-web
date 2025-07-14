"""
Archetype API endpoints for Mids-Web backend.
"""

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/archetypes")
async def get_archetypes():
    """Get all archetypes."""
    # Placeholder implementation
    return [
        {
            "id": 1,
            "name": "Blaster",
            "description": "Ranged damage dealer",
            "primary_powersets": ["Archery", "Assault Rifle", "Beam Rifle"],
            "secondary_powersets": ["Devices", "Energy Manipulation", "Martial Combat"],
            "origins": ["Natural", "Magic", "Science", "Technology", "Mutation"],
        },
        {
            "id": 2,
            "name": "Defender",
            "description": "Support and healing specialist",
            "primary_powersets": ["Empathy", "Force Field", "Kinetics"],
            "secondary_powersets": ["Archery", "Assault Rifle", "Beam Rifle"],
            "origins": ["Natural", "Magic", "Science", "Technology", "Mutation"],
        },
    ]


@router.get("/archetypes/{archetype_id}")
async def get_archetype(archetype_id: int):
    """Get a specific archetype by ID."""
    # Placeholder implementation
    if archetype_id == 1:
        return {
            "id": 1,
            "name": "Blaster",
            "description": "Ranged damage dealer with high offense but low defense",
            "primary_powersets": ["Archery", "Assault Rifle", "Beam Rifle"],
            "secondary_powersets": ["Devices", "Energy Manipulation", "Martial Combat"],
            "origins": ["Natural", "Magic", "Science", "Technology", "Mutation"],
        }
    else:
        raise HTTPException(status_code=404, detail="Archetype not found")


@router.get("/archetypes/{archetype_id}/powersets")
async def get_archetype_powersets(archetype_id: int):
    """Get all powersets for a specific archetype."""
    # Placeholder implementation
    if archetype_id == 1:
        return [
            {
                "id": 1,
                "name": "Archery",
                "description": "Ranged attacks using a bow",
                "type": "primary",
                "powers": ["Snap Shot", "Aimed Shot", "Fistful of Arrows"],
            },
            {
                "id": 2,
                "name": "Devices",
                "description": "Gadgets and traps",
                "type": "secondary",
                "powers": ["Web Grenade", "Caltrops", "Taser"],
            },
        ]
    else:
        raise HTTPException(status_code=404, detail="Archetype not found")
