"""Importer for Salvage data."""

import logging
from pathlib import Path
from typing import Any, Dict, Type, List

from app.models import Salvage
from .base_importer import BaseImporter

logger = logging.getLogger(__name__)


class SalvageImporter(BaseImporter):
    """Importer for salvage data from salvage.json."""

    def get_import_type(self) -> str:
        """Get the type of import for logging."""
        return "salvage"

    def get_model_class(self) -> Type[Salvage]:
        """Get the SQLAlchemy model class for this importer."""
        return Salvage

    def _determine_salvage_type(self, name: str, internal_name: str) -> str:
        """Determine salvage type based on name patterns."""
        name_lower = name.lower()
        internal_lower = internal_name.lower()
        
        # Rare salvage patterns
        rare_keywords = [
            "diamond", "platinum", "enriched", "synthetic", "pangaean",
            "deific", "prophecy", "essence", "soulbound", "dimensional",
            "chronal", "photonic", "positronic", "rikti", "mu", "incarnate"
        ]
        
        # Uncommon salvage patterns
        uncommon_keywords = [
            "titanium", "steel", "alloy", "compound", "extract",
            "advanced", "complex", "refined", "modified", "enhanced",
            "mutant", "psychic", "magical", "technological"
        ]
        
        # Check for rare
        if any(keyword in name_lower for keyword in rare_keywords):
            return "rare"
        
        # Check for uncommon
        if any(keyword in name_lower for keyword in uncommon_keywords):
            return "uncommon"
        
        # Default to common
        return "common"

    def _determine_salvage_origin(self, name: str, internal_name: str) -> str:
        """Determine salvage origin based on name patterns."""
        name_lower = name.lower()
        internal_lower = internal_name.lower()
        
        # Tech salvage patterns
        tech_keywords = [
            "circuit", "computer", "cybernetic", "technological",
            "mechanical", "electronic", "hydraulic", "titanium",
            "steel", "alloy", "polymer", "ceramic", "carbon"
        ]
        
        # Magic salvage patterns
        magic_keywords = [
            "spell", "scroll", "mystic", "magical", "arcane",
            "rune", "essence", "soul", "spirit", "demon",
            "blood", "bone", "dust", "amulet", "charm"
        ]
        
        # Natural salvage patterns
        natural_keywords = [
            "blood", "tissue", "sample", "dna", "genetic",
            "protein", "enzyme", "chemical", "compound",
            "extract", "serum", "venom", "mutant"
        ]
        
        # Count keyword matches
        tech_count = sum(1 for k in tech_keywords if k in name_lower)
        magic_count = sum(1 for k in magic_keywords if k in name_lower)
        natural_count = sum(1 for k in natural_keywords if k in name_lower)
        
        # Return origin with most matches
        if magic_count > tech_count and magic_count > natural_count:
            return "magic"
        elif tech_count > natural_count:
            return "tech"
        else:
            return "natural"

    def _determine_level_range(self, salvage_type: str) -> str:
        """Determine level range based on salvage type.
        
        In City of Heroes, salvage is typically categorized by level ranges.
        """
        # This is a simplified mapping - actual game may have more complex rules
        if salvage_type == "common":
            return "1-50"  # Common salvage usable at all levels
        elif salvage_type == "uncommon":
            return "10-50"  # Uncommon typically starts at level 10
        else:  # rare
            return "25-50"  # Rare typically starts at level 25

    def transform_data(self, raw_data: Any) -> Dict[str, Any]:
        """Transform raw salvage data to model-compatible format.

        Args:
            raw_data: Raw salvage data (could be list of two strings)

        Returns:
            Dictionary ready for Salvage model creation
        """
        # Handle different input formats
        if isinstance(raw_data, list) and len(raw_data) >= 2:
            # Format: ["S_InternalName", "Display Name"]
            internal_name = raw_data[0]
            display_name = raw_data[1]
        elif isinstance(raw_data, dict):
            internal_name = raw_data.get("internal_name", raw_data.get("name", ""))
            display_name = raw_data.get("display_name", raw_data.get("name", ""))
        else:
            # Try to parse as string
            parts = str(raw_data).split(",")
            internal_name = parts[0].strip() if parts else ""
            display_name = parts[1].strip() if len(parts) > 1 else internal_name
        
        # Clean up internal name (remove S_ prefix if present)
        if internal_name.startswith("S_"):
            internal_name = internal_name[2:]
        
        # Determine salvage properties
        salvage_type = self._determine_salvage_type(display_name, internal_name)
        origin = self._determine_salvage_origin(display_name, internal_name)
        level_range = self._determine_level_range(salvage_type)
        
        transformed = {
            "internal_name": internal_name,
            "display_name": display_name,
            "salvage_type": salvage_type,
            "origin": origin,
            "level_range": level_range,
            "icon_path": f"salvage/{internal_name.lower()}.png",
        }
        
        return transformed

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate transformed salvage data."""
        # Check required fields
        if not data.get("internal_name"):
            logger.error("Missing required field: internal_name")
            return False
        
        if not data.get("display_name"):
            logger.error("Missing required field: display_name")
            return False
        
        # Validate salvage type
        valid_types = ["common", "uncommon", "rare"]
        if data.get("salvage_type") not in valid_types:
            logger.error(f"Invalid salvage_type: {data.get('salvage_type')}")
            return False
        
        # Validate origin
        valid_origins = ["tech", "magic", "natural"]
        if data.get("origin") not in valid_origins:
            logger.error(f"Invalid origin: {data.get('origin')}")
            return False
        
        return True

    def import_data(self, file_path: Path, resume_from: int = 0) -> None:
        """Override to handle salvage data format."""
        # Load the data
        raw_data = self.load_json_file(file_path)
        
        # Handle the specific format of salvage.json
        if isinstance(raw_data, dict) and "salvage" in raw_data:
            # The file contains a list of salvage pairs
            items = raw_data["salvage"]
            
            # Convert pairs to list format for processing
            salvage_items = []
            for i in range(0, len(items), 2):
                if i + 1 < len(items):
                    salvage_items.append([items[i], items[i + 1]])
            
            # Create a temporary file-like structure
            temp_data = salvage_items
            
            # Save original load method and replace temporarily
            original_load = self.load_json_file
            self.load_json_file = lambda x: temp_data
            
            try:
                result = super().import_data(file_path, resume_from)
            finally:
                # Restore original method
                self.load_json_file = original_load
            
            return result
        else:
            # Standard processing
            return super().import_data(file_path, resume_from)