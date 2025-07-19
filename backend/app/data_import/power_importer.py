"""Importer for Power and Powerset data."""

import logging
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.models import Archetype, Power, Powerset

from .base_importer import BaseImporter

logger = logging.getLogger(__name__)


class PowersetImporter(BaseImporter):
    """Importer for powerset data from I9_structured.json."""

    def __init__(self, database_url: str, batch_size: int = 1000):
        super().__init__(database_url, batch_size)
        self._archetype_cache: dict[str, int] = {}

    def get_import_type(self) -> str:
        """Get the type of import for logging."""
        return "powersets"

    def get_model_class(self) -> type[Powerset]:
        """Get the SQLAlchemy model class for this importer."""
        return Powerset

    def _load_archetype_cache(self, session: Session) -> None:
        """Load archetype name to ID mapping."""
        if not self._archetype_cache:
            archetypes = session.query(Archetype.id, Archetype.name).all()
            self._archetype_cache = {arch.name: arch.id for arch in archetypes}
            logger.info(f"Loaded {len(self._archetype_cache)} archetypes into cache")

    def transform_data(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        """Transform raw powerset data to model-compatible format.

        Args:
            raw_data: Raw powerset data with archetype and powerset info

        Returns:
            Dictionary ready for Powerset model creation
        """
        # Extract archetype and powerset info
        archetype_name = raw_data.get("archetype", "")
        powerset_info = raw_data.get("powerset", {})

        # Get archetype ID from cache
        archetype_id = self._archetype_cache.get(archetype_name)
        if not archetype_id:
            raise ValueError(f"Unknown archetype: {archetype_name}")

        name = powerset_info.get("name", "")
        powerset_type = powerset_info.get("type", "primary")

        # Normalize powerset type
        if powerset_type not in ["primary", "secondary", "pool", "epic", "incarnate"]:
            powerset_type = "primary"  # Default

        transformed = {
            "name": name,
            "display_name": name,
            "description": f"{name} powerset for {archetype_name}",
            "archetype_id": archetype_id,
            "powerset_type": powerset_type,
            "icon_path": f"powersets/{name.lower().replace(' ', '_')}.png",
        }

        return transformed

    def import_data(self, file_path: Path, resume_from: int = 0) -> None:
        """Override to handle archetype cache loading."""
        session = self.SessionLocal()
        try:
            self._load_archetype_cache(session)
        finally:
            session.close()

        return super().import_data(file_path, resume_from)


class PowerImporter(BaseImporter):
    """Importer for power data from I9_structured.json or I12 data."""

    def __init__(self, database_url: str, batch_size: int = 1000):
        super().__init__(database_url, batch_size)
        self._powerset_cache: dict[str, int] = {}

    def get_import_type(self) -> str:
        """Get the type of import for logging."""
        return "powers"

    def get_model_class(self) -> type[Power]:
        """Get the SQLAlchemy model class for this importer."""
        return Power

    def _load_powerset_cache(self, session: Session) -> None:
        """Load powerset name to ID mapping."""
        if not self._powerset_cache:
            powersets = session.query(Powerset.id, Powerset.name).all()
            self._powerset_cache = {ps.name: ps.id for ps in powersets}
            logger.info(f"Loaded {len(self._powerset_cache)} powersets into cache")

    def transform_data(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        """Transform raw power data to model-compatible format.

        Args:
            raw_data: Raw power data

        Returns:
            Dictionary ready for Power model creation
        """
        # Handle different data formats (I9 vs I12)
        if "powerset" in raw_data:
            # I9 format
            powerset_name = raw_data.get("powerset", "")
            power_data = raw_data.get("power", {})
            name = power_data.get("name", "")
            level = power_data.get("level", 1)
        else:
            # I12 or other format
            powerset_name = raw_data.get("powerset_name", "")
            name = raw_data.get("name", "")
            level = raw_data.get("level_available", 1)
            power_data = raw_data

        # Get powerset ID from cache
        powerset_id = self._powerset_cache.get(powerset_name)
        if not powerset_id:
            # Skip powers without valid powerset
            raise ValueError(f"Unknown powerset: {powerset_name}")

        # Extract power attributes with defaults
        transformed = {
            "name": name,
            "display_name": name,
            "description": power_data.get("description", f"{name} power"),
            "powerset_id": powerset_id,
            "level_available": int(level) if level else 1,
            "power_type": self._determine_power_type(power_data),
            "target_type": power_data.get("target_type", "self"),
            "accuracy": float(power_data.get("accuracy", 1.0)),
            "damage_scale": (
                float(power_data.get("damage_scale", 0.0))
                if power_data.get("damage_scale")
                else None
            ),
            "endurance_cost": float(power_data.get("endurance_cost", 0.0)),
            "recharge_time": float(power_data.get("recharge_time", 0.0)),
            "activation_time": float(power_data.get("activation_time", 0.0)),
            "range_feet": (
                int(power_data.get("range", 0)) if power_data.get("range") else None
            ),
            "radius_feet": (
                int(power_data.get("radius", 0)) if power_data.get("radius") else None
            ),
            "max_targets": (
                int(power_data.get("max_targets", 1))
                if power_data.get("max_targets")
                else None
            ),
            "icon_path": f"powers/{name.lower().replace(' ', '_')}.png",
            "display_order": int(power_data.get("display_order", level)),
            "internal_name": power_data.get("internal_name", name),
            "requires_line_of_sight": power_data.get("requires_los", True),
            "modes_required": power_data.get("modes_required"),
            "modes_disallowed": power_data.get("modes_disallowed"),
            "ai_report": power_data.get("ai_report"),
            "effects": power_data.get("effects"),
            "effect_groups": power_data.get("effect_groups"),
            "display_info": power_data.get("display_info"),
        }

        return transformed

    def _determine_power_type(self, power_data: dict[str, Any]) -> str:
        """Determine the power type based on power data."""
        # Simple heuristic based on power attributes
        if power_data.get("damage_scale", 0) > 0:
            return "attack"
        elif "defense" in power_data.get("description", "").lower():
            return "defense"
        elif "control" in power_data.get("description", "").lower():
            return "control"
        elif "heal" in power_data.get("description", "").lower():
            return "support"
        elif "travel" in power_data.get("description", "").lower():
            return "travel"
        else:
            return "support"  # Default

    def import_data(self, file_path: Path, resume_from: int = 0) -> None:
        """Override to handle powerset cache loading."""
        session = self.SessionLocal()
        try:
            self._load_powerset_cache(session)
        finally:
            session.close()

        return super().import_data(file_path, resume_from)

    def validate_data(self, data: dict[str, Any]) -> bool:
        """Validate transformed power data."""
        # Check required fields
        if not data.get("name"):
            logger.error("Missing required field: name")
            return False

        if not data.get("powerset_id"):
            logger.error("Missing required field: powerset_id")
            return False

        # Validate numeric fields
        numeric_fields = [
            "level_available",
            "accuracy",
            "endurance_cost",
            "recharge_time",
            "activation_time",
        ]

        for field in numeric_fields:
            value = data.get(field)
            if value is not None and value < 0:
                logger.error(f"Invalid {field}: {value} (must be >= 0)")
                return False

        return True
