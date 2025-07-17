"""Parser for Recipe records and database from MHD files."""

from dataclasses import dataclass
from enum import IntEnum
from typing import BinaryIO, List

from .binary_reader import BinaryReader


class RecipeRarity(IntEnum):
    """Recipe rarity enumeration."""
    COMMON = 0
    UNCOMMON = 1
    RARE = 2
    VERY_RARE = 3


@dataclass
class Recipe:
    """Represents a Recipe record from MHD data."""
    
    recipe_id: str  # UID/Internal identifier
    name: str
    level_requirement: int
    rarity: RecipeRarity
    ingredients: List[str]  # Salvage names
    quantities: List[int]  # Parallel array to ingredients
    crafting_cost: int
    reward: str  # Enhancement or item produced


@dataclass
class RecipeDatabase:
    """Represents a complete Recipe database file."""
    
    header: str
    version: str
    recipes: List[Recipe]


def parse_recipe(stream: BinaryIO) -> Recipe:
    """Parse a Recipe record from a binary stream.
    
    Args:
        stream: Binary stream positioned at the start of a Recipe record
        
    Returns:
        Parsed Recipe object
        
    Raises:
        EOFError: If stream ends while reading
    """
    reader = BinaryReader(stream)
    
    try:
        # Basic fields
        recipe_id = reader.read_string()
        name = reader.read_string()
        level_requirement = reader.read_int32()
        rarity = RecipeRarity(reader.read_int32())
        
        # Ingredients array
        ingredient_count = reader.read_int32()
        ingredients = []
        for _ in range(ingredient_count):
            ingredients.append(reader.read_string())
        
        # Quantities array (parallel to ingredients)
        quantities = []
        for _ in range(ingredient_count):
            quantities.append(reader.read_int32())
        
        # Cost and reward
        crafting_cost = reader.read_int32()
        reward = reader.read_string()
        
        return Recipe(
            recipe_id=recipe_id,
            name=name,
            level_requirement=level_requirement,
            rarity=rarity,
            ingredients=ingredients,
            quantities=quantities,
            crafting_cost=crafting_cost,
            reward=reward
        )
        
    except EOFError as e:
        raise EOFError(f"Unexpected EOF while parsing Recipe: {str(e)}")


def parse_recipe_database(stream: BinaryIO) -> RecipeDatabase:
    """Parse a complete Recipe database file.
    
    Args:
        stream: Binary stream positioned at the start of the database
        
    Returns:
        Parsed RecipeDatabase object with all recipes
        
    Raises:
        EOFError: If stream ends unexpectedly
        ValueError: If file format is invalid
    """
    reader = BinaryReader(stream)
    
    try:
        # Parse header
        header = reader.read_string()
        if "Recipe" not in header:
            raise ValueError(f"Invalid recipe database header: {header}")
        
        # Version
        version = reader.read_string()
        
        # Read recipe count
        recipe_count = reader.read_int32()
        recipes = []
        
        for _ in range(recipe_count):
            recipes.append(parse_recipe(stream))
        
        return RecipeDatabase(
            header=header,
            version=version,
            recipes=recipes
        )
        
    except EOFError as e:
        raise EOFError(f"Unexpected EOF while parsing recipe database: {str(e)}")