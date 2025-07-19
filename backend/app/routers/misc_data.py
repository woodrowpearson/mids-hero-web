"""
Miscellaneous data API endpoints for Mids-Web backend.
Includes salvage, recipes, and incarnate-related endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter()


@router.get("/salvage", response_model=list[schemas.Salvage])
async def get_salvage(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of items to return"),
    rarity: str | None = Query(None, description="Filter by rarity (common, uncommon, rare)"),
    db: Session = Depends(get_db),
):
    """
    Get all salvage items.

    Returns a list of all salvage items with pagination support.
    Optionally filter by rarity.
    """
    query = db.query(models.Salvage)

    if rarity:
        query = query.filter(models.Salvage.rarity == rarity)

    salvage_items = query.offset(skip).limit(limit).all()
    return salvage_items


@router.get("/salvage/{salvage_id}", response_model=schemas.Salvage)
async def get_salvage_item(
    salvage_id: int,
    db: Session = Depends(get_db),
):
    """
    Get a specific salvage item by ID.

    Returns detailed information about a single salvage item.
    """
    salvage = db.query(models.Salvage).filter(models.Salvage.id == salvage_id).first()
    if salvage is None:
        raise HTTPException(status_code=404, detail="Salvage item not found")
    return salvage


@router.get("/recipes", response_model=list[schemas.Recipe])
async def get_recipes(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of items to return"),
    recipe_type: str | None = Query(None, description="Filter by recipe type"),
    db: Session = Depends(get_db),
):
    """
    Get all recipes.

    Returns a list of all recipes with pagination support.
    Optionally filter by recipe type.
    """
    query = db.query(models.Recipe)

    if recipe_type:
        query = query.filter(models.Recipe.recipe_type == recipe_type)

    recipes = query.offset(skip).limit(limit).all()
    return recipes


@router.get("/recipes/{recipe_id}", response_model=schemas.Recipe)
async def get_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
):
    """
    Get a specific recipe by ID.

    Returns detailed information about a recipe.
    """
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.get("/recipes/{recipe_id}/salvage", response_model=list[schemas.RecipeSalvage])
async def get_recipe_salvage(
    recipe_id: int,
    db: Session = Depends(get_db),
):
    """
    Get salvage requirements for a specific recipe.

    Returns a list of salvage items required to craft the recipe.
    """
    # First check if recipe exists
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # Get salvage requirements
    salvage_requirements = (
        db.query(models.RecipeSalvage)
        .filter(models.RecipeSalvage.recipe_id == recipe_id)
        .all()
    )
    return salvage_requirements

