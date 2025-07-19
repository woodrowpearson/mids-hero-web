"""Importer for Enhancement data."""

import logging
import re
from pathlib import Path
from typing import Any

from app.models import Enhancement, EnhancementSet

from .base_importer import BaseImporter

logger = logging.getLogger(__name__)


class EnhancementImporter(BaseImporter):
    """Importer for enhancement data from enhancements.json."""

    def __init__(self, database_url: str, batch_size: int = 1000):
        super().__init__(database_url, batch_size)
        self._set_cache: dict[str, int] = {}
        self._enhancement_sets: dict[str, EnhancementSet] = {}

    def get_import_type(self) -> str:
        """Get the type of import for logging."""
        return "enhancements"

    def get_model_class(self) -> type[Enhancement]:
        """Get the SQLAlchemy model class for this importer."""
        return Enhancement

    def _parse_enhancement_line(self, line: str) -> tuple[str, str, str, str, str | None, str | None]:
        """Parse an enhancement line from the raw data.

        The format appears to be:
        "Display Name", "Short;Description text", "icon.png", "Recipe_Name", "Salvage_Name"

        Returns:
            Tuple of (display_name, short_name, description, icon_path, recipe_name, salvage_name)
        """
        parts = line.split('","')
        parts = [p.strip('"') for p in parts]

        if len(parts) < 3:
            raise ValueError(f"Invalid enhancement line: {line}")

        display_name = parts[0]

        # Parse short name and description
        if ';' in parts[1]:
            short_name, description = parts[1].split(';', 1)
        else:
            short_name = parts[1][:10]  # Take first 10 chars as short name
            description = parts[1]

        icon_path = parts[2] if len(parts) > 2 else None
        recipe_name = parts[3] if len(parts) > 3 else None
        salvage_name = parts[4] if len(parts) > 4 else None

        return display_name, short_name, description, icon_path, recipe_name, salvage_name

    def _determine_enhancement_type(self, name: str) -> str:
        """Determine the enhancement type based on the name."""
        name_lower = name.lower()

        if "invention:" in name_lower:
            return "IO"
        elif any(x in name_lower for x in ["devastation:", "apocalypse:", "armageddon:", "obliteration:"]):
            return "set_piece"
        elif "hamidon" in name_lower or "hamio" in name_lower:
            return "HamiO"
        elif name_lower.endswith("_so"):
            return "SO"
        elif name_lower.endswith("_do"):
            return "DO"
        elif name_lower.endswith("_to"):
            return "TO"
        else:
            return "IO"  # Default

    def _extract_set_info(self, name: str) -> str | None:
        """Extract enhancement set name from enhancement name."""
        # Look for pattern "SetName: Enhancement"
        match = re.match(r"^([^:]+):\s*", name)
        if match:
            return match.group(1)
        return None

    def _parse_bonus_values(self, description: str) -> dict[str, float]:
        """Parse bonus values from description text."""
        bonuses = {}

        # Common patterns in descriptions
        patterns = {
            "accuracy": r"(?:accuracy|acc)\s*\+?(\d+(?:\.\d+)?)",
            "damage": r"(?:damage|dmg)\s*\+?(\d+(?:\.\d+)?)",
            "endurance": r"(?:endurance|end)\s*(?:reduction|redux)?\s*\+?(\d+(?:\.\d+)?)",
            "recharge": r"(?:recharge|rech)\s*\+?(\d+(?:\.\d+)?)",
            "defense": r"(?:defense|def)\s*\+?(\d+(?:\.\d+)?)",
            "resistance": r"(?:resistance|res)\s*\+?(\d+(?:\.\d+)?)",
        }

        desc_lower = description.lower()
        for bonus_type, pattern in patterns.items():
            match = re.search(pattern, desc_lower)
            if match:
                bonuses[bonus_type] = float(match.group(1))

        return bonuses

    def transform_data(self, raw_data: Any) -> dict[str, Any]:
        """Transform raw enhancement data to model-compatible format.

        Args:
            raw_data: Raw enhancement data (could be string or dict)

        Returns:
            Dictionary ready for Enhancement model creation
        """
        # Handle different input formats
        if isinstance(raw_data, str):
            # Parse the enhancement line
            display_name, short_name, description, icon_path, recipe_name, salvage_name = self._parse_enhancement_line(raw_data)
        else:
            # Assume dict format
            display_name = raw_data.get("display_name", raw_data.get("name", ""))
            short_name = raw_data.get("short_name", "")
            description = raw_data.get("description", "")
            icon_path = raw_data.get("icon_path", "")
            recipe_name = raw_data.get("recipe_name")
            salvage_name = raw_data.get("salvage_name")

        # Determine enhancement type
        enhancement_type = self._determine_enhancement_type(display_name)

        # Extract set information if applicable
        set_name = self._extract_set_info(display_name)
        set_id = None
        if set_name and enhancement_type == "set_piece":
            set_id = self._get_or_create_set(set_name)

        # Parse bonus values from description
        bonuses = self._parse_bonus_values(description)

        # Check if unique (typically set pieces with special names)
        is_unique = "unique" in description.lower() or "proc" in description.lower()

        transformed = {
            "name": display_name,
            "display_name": display_name,
            "short_name": short_name,
            "description": description,
            "enhancement_type": enhancement_type,
            "set_id": set_id,
            "level_min": 10 if enhancement_type in ["IO", "set_piece"] else 1,
            "level_max": 50,
            "accuracy_bonus": bonuses.get("accuracy"),
            "damage_bonus": bonuses.get("damage"),
            "endurance_bonus": bonuses.get("endurance"),
            "recharge_bonus": bonuses.get("recharge"),
            "defense_bonus": bonuses.get("defense"),
            "resistance_bonus": bonuses.get("resistance"),
            "other_bonuses": {k: v for k, v in bonuses.items()
                            if k not in ["accuracy", "damage", "endurance", "recharge", "defense", "resistance"]},
            "unique_enhancement": is_unique,
            "icon_path": f"enhancements/{icon_path}" if icon_path else None,
            "recipe_name": recipe_name,
            "salvage_name": salvage_name,
        }

        return transformed

    def _get_or_create_set(self, set_name: str) -> int:
        """Get or create an enhancement set."""
        if set_name in self._set_cache:
            return self._set_cache[set_name]

        # Create the set if it doesn't exist
        session = self.SessionLocal()
        try:
            enh_set = session.query(EnhancementSet).filter_by(name=set_name).first()
            if not enh_set:
                enh_set = EnhancementSet(
                    name=set_name,
                    display_name=set_name,
                    description=f"{set_name} enhancement set",
                    min_level=10,
                    max_level=50
                )
                session.add(enh_set)
                session.commit()
                logger.info(f"Created enhancement set: {set_name}")

            self._set_cache[set_name] = enh_set.id
            self._enhancement_sets[set_name] = enh_set
            return enh_set.id
        finally:
            session.close()

    def validate_data(self, data: dict[str, Any]) -> bool:
        """Validate transformed enhancement data."""
        # Check required fields
        if not data.get("name"):
            logger.error("Missing required field: name")
            return False

        if not data.get("enhancement_type"):
            logger.error("Missing required field: enhancement_type")
            return False

        # Validate enhancement type
        valid_types = ["IO", "SO", "DO", "TO", "HamiO", "set_piece"]
        if data["enhancement_type"] not in valid_types:
            logger.error(f"Invalid enhancement_type: {data['enhancement_type']}")
            return False

        # Validate bonus values (should be positive if present)
        bonus_fields = [
            "accuracy_bonus", "damage_bonus", "endurance_bonus",
            "recharge_bonus", "defense_bonus", "resistance_bonus"
        ]

        for field in bonus_fields:
            value = data.get(field)
            if value is not None and value < 0:
                logger.error(f"Invalid {field}: {value} (must be >= 0)")
                return False

        return True

    def import_data(self, file_path: Path, resume_from: int = 0) -> None:
        """Override to handle enhancement data format."""
        # First pass: create all enhancement sets
        raw_data = self.load_json_file(file_path)

        # Handle the specific format of enhancements.json
        if isinstance(raw_data, dict) and "enhancements" in raw_data:
            # The file contains a list of enhancement data
            items = raw_data["enhancements"]
        else:
            items = raw_data

        # Extract unique set names
        set_names = set()
        for item in items:
            if isinstance(item, str):
                display_name = item.split('","')[0].strip('"')
            else:
                display_name = item.get("display_name", item.get("name", ""))

            set_name = self._extract_set_info(display_name)
            if set_name:
                set_names.add(set_name)

        # Create all sets first
        for set_name in set_names:
            self._get_or_create_set(set_name)

        # Now import enhancements
        return super().import_data(file_path, resume_from)
