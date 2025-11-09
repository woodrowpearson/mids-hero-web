"""Power and Powerset JSON importer"""

import json
import logging
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.models import Archetype, Power, Powerset

logger = logging.getLogger(__name__)


class PowerImporter:
    """Import powers and powersets from City of Data JSON files"""

    def __init__(self, db_session: Session):
        self.db = db_session
        # Cache archetypes for performance
        self._archetype_cache = None

    def _get_archetype_id(self, archetype_name: str) -> int | None:
        """Get archetype ID by name, using cache"""
        if self._archetype_cache is None:
            archetypes = self.db.query(Archetype).all()
            self._archetype_cache = {at.name: at.id for at in archetypes}

        return self._archetype_cache.get(archetype_name)

    def _extract_archetype_from_display_fullname(self, display_fullname: str) -> int | None:
        """Extract archetype ID from display_fullname like 'Brute Defense.Invulnerability'

        Returns:
            Archetype ID if found, None for special powersets (Pool, Epic, Incarnate, etc.)
        """
        if not display_fullname:
            return None

        # Split on first dot
        parts = display_fullname.split(".", 1)
        if len(parts) < 2:
            return None

        category_part = parts[0].strip()

        # Map category prefixes to archetypes
        category_to_archetype = {
            "blaster ranged": "blaster",
            "blaster support": "blaster",
            "brute melee": "brute",
            "brute defense": "brute",
            "controller control": "controller",
            "controller buff": "controller",
            "corruptor ranged": "corruptor",
            "corruptor buff": "corruptor",
            "defender ranged": "defender",
            "defender buff": "defender",
            "dominator control": "dominator",
            "dominator assault": "dominator",
            "mastermind buff": "mastermind",
            "mastermind summon": "mastermind",
            "scrapper melee": "scrapper",
            "scrapper defense": "scrapper",
            "stalker melee": "stalker",
            "stalker defense": "stalker",
            "tanker melee": "tanker",
            "tanker defense": "tanker",
            "peacebringer defensive": "peacebringer",
            "peacebringer offensive": "peacebringer",
            "warshade defensive": "warshade",
            "warshade offensive": "warshade",
            "sentinel ranged": "sentinel",
            "sentinel defense": "sentinel",
            "arachnos soldiers": "arachnos_soldier",
            "arachnos widow": "arachnos_widow",
        }

        # Check for exact match
        category_lower = category_part.lower()
        if category_lower in category_to_archetype:
            archetype_name = category_to_archetype[category_lower]
            return self._get_archetype_id(archetype_name)

        # Special handling for Arachnos Training/Teamwork powersets
        powerset_name = parts[1].strip() if len(parts) > 1 else ""
        if "training" in category_lower or "teamwork" in category_lower:
            if "widow" in category_lower or "widow" in powerset_name.lower() or "fortunata" in powerset_name.lower():
                return self._get_archetype_id("arachnos_widow")
            elif "bane" in category_lower or "crab" in category_lower or "gadgets" in category_lower:
                return self._get_archetype_id("arachnos_soldier")
            elif "teamwork" in category_lower:
                return self._get_archetype_id("arachnos_soldier")

        # For special powersets (Pool, Epic, Incarnate, Inherent), return None
        special_categories = ["pool", "epic", "incarnate", "inherent", "temporary"]
        if any(cat in category_lower for cat in special_categories):
            return None

        # Try extracting first word
        first_word = category_part.split()[0].lower()
        if first_word in ["blaster", "brute", "controller", "corruptor", "defender",
                          "dominator", "mastermind", "scrapper", "stalker", "tanker",
                          "peacebringer", "warshade", "sentinel"]:
            return self._get_archetype_id(first_word)

        # Could not determine - log warning and return None
        logger.warning(f"Could not extract archetype from display_fullname: {display_fullname}")
        return None

    async def import_powerset(
        self, powerset_dir: Path, archetype_id: int
    ) -> dict[str, Any]:
        """Import a powerset from its directory

        Args:
            powerset_dir: Directory containing powerset index.json
            archetype_id: ID of the archetype this powerset belongs to

        Returns:
            Import results
        """
        result = {
            "success": False,
            "powersets_imported": 0,
            "powers_imported": 0,
            "skipped": 0,
            "errors": [],
        }

        try:
            index_file = powerset_dir / "index.json"
            if not index_file.exists():
                result["errors"].append(f"No index.json in {powerset_dir}")
                return result

            with open(index_file) as f:
                data = json.load(f)

            # Check if powerset already exists
            existing = self.db.query(Powerset).filter_by(name=data["name"]).first()

            if existing:
                logger.info(f"Powerset {data['name']} already exists")
                result["skipped"] = 1
                result["success"] = True
                return result

            # If archetype_id not provided, try to extract from display_fullname
            if archetype_id is None:
                display_fullname = data.get("display_fullname", "")
                archetype_id = self._extract_archetype_from_display_fullname(display_fullname)
                if archetype_id:
                    logger.info(f"Extracted archetype_id={archetype_id} from '{display_fullname}'")

            # Create powerset
            powerset = Powerset(
                name=data["name"],
                display_name=data.get("display_name", data["name"]),
                display_fullname=data.get("display_fullname", ""),
                display_help=data.get("display_help", ""),
                display_short_help=data.get("display_short_help", ""),
                archetype_id=archetype_id,
                powerset_type="primary",  # Will need to determine this properly
                icon=data.get("icon", ""),
                requires=data.get("requires", ""),
                power_names=data.get("power_names", []),
                power_display_names=data.get("power_display_names", []),
                power_short_helps=data.get("power_short_helps", []),
                available_level=data.get("available_level", []),
                source_metadata=data,
            )

            self.db.add(powerset)
            self.db.commit()

            result["powersets_imported"] = 1
            result["success"] = True
            logger.info(f"Imported powerset: {data['name']}")

        except Exception as e:
            self.db.rollback()
            error_msg = f"Error importing powerset {powerset_dir}: {str(e)}"
            logger.error(error_msg)
            result["errors"].append(error_msg)

        return result

    async def import_power(self, power_file: Path, powerset_id: int) -> dict[str, Any]:
        """Import an individual power from JSON file

        Args:
            power_file: Path to power JSON file
            powerset_id: ID of parent powerset

        Returns:
            Import results
        """
        result = {"success": False, "imported": 0, "skipped": 0, "errors": []}

        try:
            with open(power_file) as f:
                data = json.load(f)

            # Check if power already exists (using name as unique identifier)
            existing = self.db.query(Power).filter_by(name=data["name"]).first()
            if existing:
                logger.debug(f"Power {data['name']} already exists")
                result["skipped"] = 1
                result["success"] = True
                return result

            # Create power with basic fields
            power = Power(
                name=data["name"],
                full_name=data.get("full_name", data["name"]),
                display_name=data.get("display_name", data["name"]),
                display_help=data.get("display_help", ""),
                display_short_help=data.get("display_short_help", ""),
                powerset_id=powerset_id,
                type=data.get("type", ""),
                available_level=data.get("available_level", 1),
                icon=data.get("icon", ""),
                accuracy=data.get("accuracy", 1.0),
                activation_time=data.get("activation_time"),
                recharge_time=data.get("recharge_time"),
                endurance_cost=data.get("endurance_cost"),
                range=data.get("range"),
                radius=data.get("radius"),
                arc=data.get("arc"),
                max_targets_hit=data.get("max_targets_hit"),
                target_type=data.get("target_type", ""),
                requires=data.get("requires", ""),
                max_boosts=data.get("max_boosts", 6),
                boosts_allowed=data.get("boosts_allowed", []),
                allowed_boostset_cats=data.get("allowed_boostset_cats", []),
                power_data=data,  # Store complete JSON
                source_metadata=data,  # Also store in source_metadata
            )

            self.db.add(power)
            self.db.commit()

            result["imported"] = 1
            result["success"] = True
            logger.debug(f"Imported power: {data['name']}")

        except Exception as e:
            self.db.rollback()
            error_msg = f"Error importing power {power_file}: {str(e)}"
            logger.error(error_msg)
            result["errors"].append(error_msg)

        return result

    async def import_powerset_with_powers(
        self, powerset_dir: Path, archetype_id: int
    ) -> dict[str, Any]:
        """Import a powerset and all its powers

        Args:
            powerset_dir: Directory containing powerset index.json and power files
            archetype_id: ID of parent archetype

        Returns:
            Import results with progress tracking
        """
        result = {
            "success": True,
            "powersets_imported": 0,
            "powers_imported": 0,
            "skipped": 0,
            "errors": [],
        }

        # Import powerset first
        logger.info(f"Importing powerset from {powerset_dir.name}...")
        ps_result = await self.import_powerset(powerset_dir, archetype_id)
        result["powersets_imported"] = ps_result["powersets_imported"]
        result["skipped"] += ps_result["skipped"]
        result["errors"].extend(ps_result["errors"])

        if not ps_result["success"]:
            result["success"] = False
            return result

        # Get the powerset ID
        index_file = powerset_dir / "index.json"
        with open(index_file) as f:
            ps_data = json.load(f)

        powerset = self.db.query(Powerset).filter_by(name=ps_data["name"]).first()
        if not powerset:
            result["errors"].append(f"Failed to retrieve powerset {ps_data['name']}")
            result["success"] = False
            return result

        # Import all power JSON files
        power_files = list(powerset_dir.glob("*.json"))
        power_files = [f for f in power_files if f.name != "index.json"]

        total_powers = len(power_files)
        logger.info(f"Importing {total_powers} powers from {ps_data['name']}...")

        for idx, power_file in enumerate(power_files, 1):
            if idx % 10 == 0:  # Progress every 10 powers
                logger.info(f"  Progress: {idx}/{total_powers} powers")

            power_result = await self.import_power(power_file, powerset.id)
            result["powers_imported"] += power_result["imported"]
            result["skipped"] += power_result["skipped"]
            result["errors"].extend(power_result["errors"])

            if not power_result["success"]:
                result["success"] = False

        logger.info(
            f"Completed {ps_data['name']}: {result['powers_imported']} powers imported"
        )
        return result

    async def import_all_powersets(self, powers_root: Path) -> dict[str, Any]:
        """Import all powersets from root powers directory

        Args:
            powers_root: Root directory containing power category folders

        Returns:
            Aggregate import results
        """
        result = {
            "success": True,
            "powersets_imported": 0,
            "powers_imported": 0,
            "skipped": 0,
            "errors": [],
        }

        # Find all powerset directories (they contain index.json)
        powerset_dirs = []
        for category_dir in powers_root.iterdir():
            if category_dir.is_dir() and not category_dir.name.startswith("."):
                for powerset_dir in category_dir.iterdir():
                    if powerset_dir.is_dir() and (powerset_dir / "index.json").exists():
                        powerset_dirs.append(powerset_dir)

        logger.info(f"Found {len(powerset_dirs)} powersets")

        # For now, import without archetype association (will fix later)
        for powerset_dir in powerset_dirs:
            ps_result = await self.import_powerset(powerset_dir, None)
            result["powersets_imported"] += ps_result["powersets_imported"]
            result["powers_imported"] += ps_result["powers_imported"]
            result["skipped"] += ps_result["skipped"]
            result["errors"].extend(ps_result["errors"])

            if not ps_result["success"]:
                result["success"] = False

        return result
