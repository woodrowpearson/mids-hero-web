"""Importer for Recipe data."""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Type, Optional

from sqlalchemy.orm import Session

from app.models import Recipe, RecipeSalvage, Enhancement, Salvage
from .base_importer import BaseImporter

logger = logging.getLogger(__name__)


class RecipeImporter(BaseImporter):
    """Importer for recipe data from recipes.json."""

    def __init__(self, database_url: str, batch_size: int = 1000):
        super().__init__(database_url, batch_size)
        self._enhancement_cache: Dict[str, int] = {}
        self._salvage_cache: Dict[str, int] = {}
        self._recipe_salvage_mappings: List[Dict[str, Any]] = []

    def get_import_type(self) -> str:
        """Get the type of import for logging."""
        return "recipes"

    def get_model_class(self) -> Type[Recipe]:
        """Get the SQLAlchemy model class for this importer."""
        return Recipe

    def _load_enhancement_cache(self, session: Session) -> None:
        """Load enhancement name to ID mapping."""
        if not self._enhancement_cache:
            enhancements = session.query(Enhancement.id, Enhancement.name).all()
            self._enhancement_cache = {enh.name: enh.id for enh in enhancements}
            logger.info(f"Loaded {len(self._enhancement_cache)} enhancements into cache")

    def _load_salvage_cache(self, session: Session) -> None:
        """Load salvage internal name to ID mapping."""
        if not self._salvage_cache:
            salvages = session.query(Salvage.id, Salvage.internal_name).all()
            self._salvage_cache = {salv.internal_name: salv.id for salv in salvages}
            logger.info(f"Loaded {len(self._salvage_cache)} salvage items into cache")

    def _parse_recipe_entry(self, entry: Any) -> Dict[str, Any]:
        """Parse a recipe entry from the raw data.
        
        The recipe format appears to be complex with various structures.
        This method handles the parsing logic.
        """
        if isinstance(entry, dict):
            return entry
        
        # Handle string or list formats
        if isinstance(entry, (list, tuple)):
            # Convert list to dict based on expected structure
            result = {}
            if len(entry) > 0:
                result["internal_name"] = str(entry[0])
            if len(entry) > 1:
                result["display_name"] = str(entry[1])
            if len(entry) > 2:
                result["enhancement_name"] = str(entry[2])
            
            # Parse salvage requirements from remaining entries
            salvage_reqs = []
            i = 3
            while i < len(entry):
                if i + 1 < len(entry) and str(entry[i]).startswith("S_"):
                    salvage_reqs.append({
                        "salvage_name": str(entry[i]),
                        "quantity": 1  # Default quantity
                    })
                i += 1
            
            if salvage_reqs:
                result["salvage_requirements"] = salvage_reqs
            
            return result
        
        # Handle string format
        return {"internal_name": str(entry), "display_name": str(entry)}

    def _determine_recipe_type(self, name: str, enhancement_name: Optional[str]) -> str:
        """Determine recipe type based on name and associated enhancement."""
        name_lower = name.lower()
        
        if enhancement_name:
            enh_lower = enhancement_name.lower()
            if any(x in enh_lower for x in ["devastation", "apocalypse", "armageddon", "obliteration"]):
                return "very_rare"
            elif "invention:" in enh_lower:
                return "common"
        
        # Check name patterns
        if "very rare" in name_lower or "purple" in name_lower:
            return "very_rare"
        elif "rare" in name_lower or "orange" in name_lower:
            return "rare"
        elif "uncommon" in name_lower or "yellow" in name_lower:
            return "uncommon"
        else:
            return "common"

    def _parse_crafting_cost(self, recipe_data: Dict[str, Any]) -> tuple[int, int]:
        """Parse crafting costs from recipe data.
        
        Returns:
            Tuple of (normal_cost, premium_cost)
        """
        # Default costs based on recipe rarity
        recipe_type = recipe_data.get("recipe_type", "common")
        
        default_costs = {
            "common": (5000, 25000),
            "uncommon": (15000, 75000),
            "rare": (50000, 250000),
            "very_rare": (100000, 500000),
        }
        
        base_cost, premium_cost = default_costs.get(recipe_type, (5000, 25000))
        
        # Adjust by level if available
        level_min = recipe_data.get("level_min", 10)
        level_factor = level_min / 10  # Scale costs by level
        
        return int(base_cost * level_factor), int(premium_cost * level_factor)

    def transform_data(self, raw_data: Any) -> Dict[str, Any]:
        """Transform raw recipe data to model-compatible format.

        Args:
            raw_data: Raw recipe data

        Returns:
            Dictionary ready for Recipe model creation
        """
        # Parse the recipe entry
        recipe_data = self._parse_recipe_entry(raw_data)
        
        internal_name = recipe_data.get("internal_name", "")
        display_name = recipe_data.get("display_name", internal_name)
        enhancement_name = recipe_data.get("enhancement_name")
        
        # Get enhancement ID if available
        enhancement_id = None
        if enhancement_name:
            enhancement_id = self._enhancement_cache.get(enhancement_name)
        
        # Determine recipe properties
        recipe_type = self._determine_recipe_type(display_name, enhancement_name)
        crafting_cost, crafting_cost_premium = self._parse_crafting_cost(recipe_data)
        
        # Extract level range
        level_match = re.search(r"(?:level|lvl)\s*(\d+)(?:\s*-\s*(\d+))?", display_name.lower())
        if level_match:
            level_min = int(level_match.group(1))
            level_max = int(level_match.group(2)) if level_match.group(2) else level_min
        else:
            # Default level ranges by type
            level_ranges = {
                "common": (10, 50),
                "uncommon": (15, 50),
                "rare": (25, 50),
                "very_rare": (30, 50),
            }
            level_min, level_max = level_ranges.get(recipe_type, (10, 50))
        
        transformed = {
            "internal_name": internal_name,
            "display_name": display_name,
            "enhancement_id": enhancement_id,
            "recipe_type": recipe_type,
            "level_min": level_min,
            "level_max": level_max,
            "crafting_cost": crafting_cost,
            "crafting_cost_premium": crafting_cost_premium,
            "memorized": False,  # Default
        }
        
        # Store salvage requirements for later processing
        if "salvage_requirements" in recipe_data:
            for req in recipe_data["salvage_requirements"]:
                salvage_name = req["salvage_name"]
                if salvage_name.startswith("S_"):
                    salvage_name = salvage_name[2:]  # Remove S_ prefix
                
                salvage_id = self._salvage_cache.get(salvage_name)
                if salvage_id:
                    self._recipe_salvage_mappings.append({
                        "recipe_internal_name": internal_name,
                        "salvage_id": salvage_id,
                        "quantity": req.get("quantity", 1),
                    })
        
        return transformed

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate transformed recipe data."""
        # Check required fields
        if not data.get("internal_name"):
            logger.error("Missing required field: internal_name")
            return False
        
        if not data.get("display_name"):
            logger.error("Missing required field: display_name")
            return False
        
        # Validate recipe type
        valid_types = ["common", "uncommon", "rare", "very_rare"]
        if data.get("recipe_type") not in valid_types:
            logger.error(f"Invalid recipe_type: {data.get('recipe_type')}")
            return False
        
        # Validate level range
        if data.get("level_min", 0) < 1 or data.get("level_min", 0) > 50:
            logger.error(f"Invalid level_min: {data.get('level_min')}")
            return False
        
        if data.get("level_max", 0) < data.get("level_min", 0):
            logger.error("level_max must be >= level_min")
            return False
        
        # Validate costs
        if data.get("crafting_cost", 0) < 0:
            logger.error(f"Invalid crafting_cost: {data.get('crafting_cost')}")
            return False
        
        return True

    def import_data(self, file_path: Path, resume_from: int = 0) -> None:
        """Override to handle caches and salvage mappings."""
        session = self.SessionLocal()
        try:
            # Load caches
            self._load_enhancement_cache(session)
            self._load_salvage_cache(session)
        finally:
            session.close()
        
        # Import recipes
        result = super().import_data(file_path, resume_from)
        
        # Now import recipe-salvage mappings
        if self._recipe_salvage_mappings:
            logger.info(f"Importing {len(self._recipe_salvage_mappings)} recipe-salvage mappings")
            
            session = self.SessionLocal()
            try:
                # Get recipe internal_name to ID mapping
                recipes = session.query(Recipe.id, Recipe.internal_name).all()
                recipe_map = {r.internal_name: r.id for r in recipes}
                
                # Create RecipeSalvage entries
                batch = []
                for mapping in self._recipe_salvage_mappings:
                    recipe_id = recipe_map.get(mapping["recipe_internal_name"])
                    if recipe_id:
                        batch.append({
                            "recipe_id": recipe_id,
                            "salvage_id": mapping["salvage_id"],
                            "quantity": mapping["quantity"],
                        })
                    
                    if len(batch) >= self.batch_size:
                        session.bulk_insert_mappings(RecipeSalvage, batch)
                        session.commit()
                        batch = []
                
                # Insert remaining
                if batch:
                    session.bulk_insert_mappings(RecipeSalvage, batch)
                    session.commit()
                
                logger.info("Recipe-salvage mappings imported successfully")
                
            except Exception as e:
                logger.error(f"Failed to import recipe-salvage mappings: {e}")
                session.rollback()
                raise
            finally:
                session.close()
        
        return result