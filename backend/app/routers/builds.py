"""
Build API endpoints for Mids-Web backend.
"""

from fastapi import APIRouter, HTTPException

router = APIRouter()


# Removed /calculate endpoint - now handled by calc.py router


@router.post("/build/encode")
async def encode_build(build_data: dict):
    """Encode build data into a shareable format."""
    # Placeholder implementation
    return {"code": "MRB-ABC123-DEF456"}


@router.post("/build/decode")
async def decode_build(code_data: dict):
    """Decode build data from a shareable format."""
    # Placeholder implementation
    code = code_data.get("code", "")
    if code.startswith("MRB-"):
        return {
            "archetype_id": 1,
            "powers": [1, 2, 3],
            "enhancements": {"1": [1, 2], "2": [1], "3": [1, 2, 3]},
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid build code")
