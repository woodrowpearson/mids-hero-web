"""Tests for parsing Recipe records and database from MHD files."""

import io
import struct
from dataclasses import dataclass
from typing import List

import pytest

from app.mhd_parser.recipe_parser import (
    parse_recipe, parse_recipe_database,
    Recipe, RecipeDatabase, RecipeRarity
)


class TestRecipeParser:
    """Test cases for parsing Recipe records."""
    
    def test_parse_minimal_recipe(self):
        """Test parsing a minimal recipe record."""
        data = io.BytesIO()
        
        # Write recipe fields
        data.write(b'\x0CRecipe_Acc_1')  # RecipeID/UID (12 chars)
        data.write(b'\x0BAccuracy IO')  # Name (11 chars)
        data.write(struct.pack('<i', 10))  # Level requirement
        data.write(struct.pack('<i', 0))  # Rarity (Common)
        
        # Ingredients
        data.write(struct.pack('<i', 2))  # Ingredient count
        data.write(b'\x09Boresight')  # Salvage 1 (9 chars)
        data.write(b'\x08Luck Gem')  # Salvage 2 (8 chars)
        
        # Quantities (parallel array)
        data.write(struct.pack('<i', 1))  # Quantity 1
        data.write(struct.pack('<i', 2))  # Quantity 2
        
        # Cost and reward
        data.write(struct.pack('<i', 10000))  # Crafting cost
        data.write(b'\x0BAccuracy IO')  # Reward (11 chars)
        
        data.seek(0)
        
        recipe = parse_recipe(data)
        
        assert recipe.recipe_id == "Recipe_Acc_1"
        assert recipe.name == "Accuracy IO"
        assert recipe.level_requirement == 10
        assert recipe.rarity == RecipeRarity.COMMON
        assert len(recipe.ingredients) == 2
        assert recipe.ingredients[0] == "Boresight"
        assert recipe.ingredients[1] == "Luck Gem"
        assert recipe.quantities == [1, 2]
        assert recipe.crafting_cost == 10000
        assert recipe.reward == "Accuracy IO"
    
    def test_parse_recipe_with_many_ingredients(self):
        """Test parsing recipe with multiple ingredients."""
        data = io.BytesIO()
        
        # Basic fields
        data.write(b'\x0FRecipe_Hami_Dam')  # RecipeID (15 chars)
        data.write(b'\x0EHamidon Damage')  # Name (14 chars)
        data.write(struct.pack('<i', 50))  # Level 50
        data.write(struct.pack('<i', 3))  # Very Rare
        
        # 5 ingredients
        data.write(struct.pack('<i', 5))  # Ingredient count
        data.write(b'\x0BHamidon Goo')  # Salvage 1 (11 chars)
        data.write(b'\x0FSynthetic HamiO')  # Salvage 2 (15 chars)
        data.write(b'\x09Nucleolus')  # Salvage 3 (9 chars)
        data.write(b'\x08Ribosome')  # Salvage 4 (8 chars)
        data.write(b'\x0CMitochondria')  # Salvage 5 (12 chars)
        
        # Quantities
        for i in range(5):
            data.write(struct.pack('<i', i + 1))  # 1, 2, 3, 4, 5
        
        # Cost and reward
        data.write(struct.pack('<i', 1000000))  # 1 million inf
        data.write(b'\x0EHamidon Dam HO')  # Reward (14 chars)
        
        data.seek(0)
        
        recipe = parse_recipe(data)
        
        assert recipe.recipe_id == "Recipe_Hami_Dam"
        assert recipe.level_requirement == 50
        assert recipe.rarity == RecipeRarity.VERY_RARE
        assert len(recipe.ingredients) == 5
        assert recipe.quantities == [1, 2, 3, 4, 5]
        assert recipe.crafting_cost == 1000000
    
    def test_parse_recipe_all_rarities(self):
        """Test parsing recipes with different rarities."""
        test_cases = [
            (0, RecipeRarity.COMMON),
            (1, RecipeRarity.UNCOMMON),
            (2, RecipeRarity.RARE),
            (3, RecipeRarity.VERY_RARE),
        ]
        
        for rarity_int, expected_rarity in test_cases:
            data = io.BytesIO()
            
            data.write(b'\x04Test')  # RecipeID
            data.write(b'\x04Test')  # Name
            data.write(struct.pack('<i', 1))  # Level
            data.write(struct.pack('<i', rarity_int))  # Rarity
            data.write(struct.pack('<i', 0))  # No ingredients
            data.write(struct.pack('<i', 0))  # Cost
            data.write(b'\x04Test')  # Reward
            
            data.seek(0)
            
            recipe = parse_recipe(data)
            assert recipe.rarity == expected_rarity


class TestRecipeDatabaseParser:
    """Test cases for parsing complete Recipe database files."""
    
    def test_parse_minimal_recipe_database(self):
        """Test parsing a minimal recipe database."""
        data = io.BytesIO()
        
        # Header
        header = "Mids Reborn Recipe Database"
        data.write(bytes([len(header)]))
        data.write(header.encode())
        
        # Version
        version = "1.0.0.0"
        data.write(bytes([len(version)]))
        data.write(version.encode())
        
        # Count
        data.write(struct.pack('<i', 0))  # No recipes
        
        data.seek(0)
        
        db = parse_recipe_database(data)
        
        assert db.header == "Mids Reborn Recipe Database"
        assert db.version == "1.0.0.0"
        assert len(db.recipes) == 0
    
    def test_parse_recipe_database_with_recipes(self):
        """Test parsing recipe database with multiple recipes."""
        data = io.BytesIO()
        
        # Header
        header = "Mids Reborn Recipe Database"
        data.write(bytes([len(header)]))
        data.write(header.encode())
        
        # Version
        version = "1.0.0.0"
        data.write(bytes([len(version)]))
        data.write(version.encode())
        
        # Count
        data.write(struct.pack('<i', 2))  # 2 recipes
        
        # Recipe 1: Simple common
        data.write(b'\x08Recipe_1')  # RecipeID (8 chars)
        data.write(b'\x08Training')  # Name (8 chars)
        data.write(struct.pack('<i', 1))  # Level 1
        data.write(struct.pack('<i', 0))  # Common
        data.write(struct.pack('<i', 1))  # 1 ingredient
        data.write(b'\x05Scrap')  # Salvage (5 chars)
        data.write(struct.pack('<i', 1))  # Quantity
        data.write(struct.pack('<i', 100))  # Cost
        data.write(b'\x0BTraining IO')  # Reward (11 chars)
        
        # Recipe 2: Complex rare
        data.write(b'\x08Recipe_2')  # RecipeID
        data.write(b'\x04Rare')  # Name (4 chars)
        data.write(struct.pack('<i', 30))  # Level 30
        data.write(struct.pack('<i', 2))  # Rare
        data.write(struct.pack('<i', 3))  # 3 ingredients
        data.write(b'\x06Silver')  # Salvage 1 (6 chars)
        data.write(b'\x04Gold')  # Salvage 2 (4 chars)
        data.write(b'\x08Platinum')  # Salvage 3 (8 chars)
        data.write(struct.pack('<i', 2))  # Quantity 1
        data.write(struct.pack('<i', 1))  # Quantity 2
        data.write(struct.pack('<i', 1))  # Quantity 3
        data.write(struct.pack('<i', 50000))  # Cost
        data.write(b'\x07Rare IO')  # Reward (7 chars)
        
        data.seek(0)
        
        db = parse_recipe_database(data)
        
        assert len(db.recipes) == 2
        assert db.recipes[0].name == "Training"
        assert db.recipes[0].level_requirement == 1
        assert len(db.recipes[0].ingredients) == 1
        assert db.recipes[1].name == "Rare"
        assert db.recipes[1].rarity == RecipeRarity.RARE
        assert len(db.recipes[1].ingredients) == 3
        assert db.recipes[1].quantities == [2, 1, 1]
    
    def test_parse_recipe_database_eof_handling(self):
        """Test handling of EOF during database parsing."""
        data = io.BytesIO()
        
        # Header only
        header = "Mids Reborn Recipe Database"
        data.write(bytes([len(header)]))
        data.write(header.encode())
        # Missing rest
        
        data.seek(0)
        
        with pytest.raises(EOFError):
            parse_recipe_database(data)