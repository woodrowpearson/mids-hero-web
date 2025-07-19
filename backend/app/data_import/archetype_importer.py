"""Importer for Archetype data."""

import logging
from typing import Any

from app.models import Archetype

from .base_importer import BaseImporter

logger = logging.getLogger(__name__)


class ArchetypeImporter(BaseImporter):
    """Importer for archetype data from I9_structured.json."""

    def get_import_type(self) -> str:
        """Get the type of import for logging."""
        return "archetypes"

    def get_model_class(self) -> type[Archetype]:
        """Get the SQLAlchemy model class for this importer."""
        return Archetype

    def transform_data(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        """Transform raw archetype data to model-compatible format.

        Args:
            raw_data: Raw archetype data from JSON

        Returns:
            Dictionary ready for Archetype model creation
        """
        # Extract archetype name
        name = raw_data.get("name", "")

        # Map archetype names to primary/secondary groups
        # Based on City of Heroes archetype classifications
        archetype_groups = {
            "Blaster": ("damage", "support"),
            "Controller": ("control", "support"),
            "Defender": ("support", "defense"),
            "Scrapper": ("damage", "defense"),
            "Tanker": ("defense", "damage"),
            "Peacebringer": ("damage", "defense"),
            "Warshade": ("damage", "defense"),
            "Brute": ("damage", "defense"),
            "Corruptor": ("damage", "support"),
            "Dominator": ("control", "damage"),
            "Mastermind": ("support", "defense"),
            "Stalker": ("damage", "defense"),
            "Arachnos Soldier": ("defense", "damage"),
            "Arachnos Widow": ("damage", "defense"),
            "Sentinel": ("damage", "defense"),
        }

        primary_group, secondary_group = archetype_groups.get(
            name, ("damage", "support")  # Default values
        )

        # Map archetype names to hit point values
        # These are approximate base values from the game
        hp_values = {
            "Blaster": (1070, 1606),
            "Controller": (1017, 1606),
            "Defender": (1017, 1606),
            "Scrapper": (1339, 2088),
            "Tanker": (1874, 3534),
            "Peacebringer": (1070, 2409),
            "Warshade": (1070, 2409),
            "Brute": (1499, 3212),
            "Corruptor": (1070, 1606),
            "Dominator": (1017, 1606),
            "Mastermind": (803, 1606),
            "Stalker": (1204, 1606),
            "Arachnos Soldier": (1070, 2088),
            "Arachnos Widow": (1070, 2088),
            "Sentinel": (1184, 1807),
        }

        hit_points_base, hit_points_max = hp_values.get(name, (1000, 1500))

        # Build the transformed data
        transformed = {
            "name": name,
            "display_name": name,  # Can be customized later
            "description": f"{name} archetype",  # Placeholder description
            "primary_group": primary_group,
            "secondary_group": secondary_group,
            "hit_points_base": hit_points_base,
            "hit_points_max": hit_points_max,
            "icon_path": f"archetypes/{name.lower().replace(' ', '_')}.png",
        }

        return transformed

    def validate_data(self, data: dict[str, Any]) -> bool:
        """Validate transformed archetype data.

        Args:
            data: Transformed data dictionary

        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        required_fields = ["name", "primary_group", "secondary_group"]
        for field in required_fields:
            if not data.get(field):
                logger.error(f"Missing required field: {field}")
                return False

        # Validate group values
        valid_groups = ["damage", "control", "defense", "support"]
        if data["primary_group"] not in valid_groups:
            logger.error(f"Invalid primary_group: {data['primary_group']}")
            return False

        if data["secondary_group"] not in valid_groups:
            logger.error(f"Invalid secondary_group: {data['secondary_group']}")
            return False

        # Validate hit points
        if data.get("hit_points_base", 0) <= 0:
            logger.error(f"Invalid hit_points_base: {data.get('hit_points_base')}")
            return False

        if data.get("hit_points_max", 0) <= data.get("hit_points_base", 0):
            logger.error("hit_points_max must be greater than hit_points_base")
            return False

        return True
