"""Importer for Attribute Modifier and Type Grade data."""

import logging
from pathlib import Path
from typing import Any, Dict, Type, Optional

from sqlalchemy.orm import Session

from app.models import AttributeModifier, TypeGrade, Power, Enhancement, Archetype
from .base_importer import BaseImporter

logger = logging.getLogger(__name__)


class AttributeModifierImporter(BaseImporter):
    """Importer for attribute modifier data from AttribMod.json."""

    def __init__(self, database_url: str, batch_size: int = 1000):
        super().__init__(database_url, batch_size)
        self._power_cache: Dict[str, int] = {}
        self._enhancement_cache: Dict[str, int] = {}

    def get_import_type(self) -> str:
        """Get the type of import for logging."""
        return "attribute_modifiers"

    def get_model_class(self) -> Type[AttributeModifier]:
        """Get the SQLAlchemy model class for this importer."""
        return AttributeModifier

    def _load_power_cache(self, session: Session) -> None:
        """Load power internal name to ID mapping."""
        if not self._power_cache:
            powers = session.query(Power.id, Power.internal_name).all()
            self._power_cache = {p.internal_name: p.id for p in powers}
            logger.info(f"Loaded {len(self._power_cache)} powers into cache")

    def _load_enhancement_cache(self, session: Session) -> None:
        """Load enhancement name to ID mapping."""
        if not self._enhancement_cache:
            enhancements = session.query(Enhancement.id, Enhancement.name).all()
            self._enhancement_cache = {e.name: e.id for e in enhancements}
            logger.info(f"Loaded {len(self._enhancement_cache)} enhancements into cache")

    def transform_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform raw attribute modifier data to model-compatible format.

        Args:
            raw_data: Raw attribute modifier data

        Returns:
            Dictionary ready for AttributeModifier model creation
        """
        # Extract power or enhancement reference
        power_name = raw_data.get("power_name") or raw_data.get("power_internal_name")
        enhancement_name = raw_data.get("enhancement_name")
        
        power_id = None
        enhancement_id = None
        
        if power_name:
            power_id = self._power_cache.get(power_name)
        
        if enhancement_name:
            enhancement_id = self._enhancement_cache.get(enhancement_name)
        
        # Skip if neither power nor enhancement found
        if not power_id and not enhancement_id:
            raise ValueError(f"No valid power or enhancement reference found")
        
        # Extract attribute data
        attribute_name = raw_data.get("attribute", raw_data.get("attribute_name", ""))
        
        # Parse modifier table reference
        modifier_table = raw_data.get("table", raw_data.get("modifier_table", ""))
        
        # Parse scale value
        scale = raw_data.get("scale", raw_data.get("modifier_scale", 0.0))
        if isinstance(scale, str):
            try:
                scale = float(scale)
            except ValueError:
                scale = 0.0
        
        transformed = {
            "power_id": power_id,
            "enhancement_id": enhancement_id,
            "attribute_name": attribute_name,
            "attribute_type": raw_data.get("type", raw_data.get("attribute_type", "magnitude")),
            "modifier_table": modifier_table,
            "scale": scale,
            "aspect": raw_data.get("aspect", "Current"),
            "application_type": raw_data.get("application", raw_data.get("application_type", "OnActivate")),
            "target_type": raw_data.get("target", raw_data.get("target_type", "Self")),
            "effect_area": raw_data.get("area", raw_data.get("effect_area", "SingleTarget")),
            "flags": raw_data.get("flags", {}),
        }
        
        return transformed

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate transformed attribute modifier data."""
        # Must have either power_id or enhancement_id
        if not data.get("power_id") and not data.get("enhancement_id"):
            logger.error("Must have either power_id or enhancement_id")
            return False
        
        # Check required fields
        if not data.get("attribute_name"):
            logger.error("Missing required field: attribute_name")
            return False
        
        # Validate scale
        if data.get("scale") is not None:
            try:
                float(data["scale"])
            except (TypeError, ValueError):
                logger.error(f"Invalid scale value: {data.get('scale')}")
                return False
        
        return True

    def import_data(self, file_path: Path, resume_from: int = 0) -> None:
        """Override to handle cache loading."""
        session = self.SessionLocal()
        try:
            self._load_power_cache(session)
            self._load_enhancement_cache(session)
        finally:
            session.close()
        
        return super().import_data(file_path, resume_from)


class TypeGradeImporter(BaseImporter):
    """Importer for type grade data from TypeGrades.json."""

    def __init__(self, database_url: str, batch_size: int = 1000):
        super().__init__(database_url, batch_size)
        self._archetype_cache: Dict[str, int] = {}

    def get_import_type(self) -> str:
        """Get the type of import for logging."""
        return "type_grades"

    def get_model_class(self) -> Type[TypeGrade]:
        """Get the SQLAlchemy model class for this importer."""
        return TypeGrade

    def _load_archetype_cache(self, session: Session) -> None:
        """Load archetype name to ID mapping."""
        if not self._archetype_cache:
            archetypes = session.query(Archetype.id, Archetype.name).all()
            self._archetype_cache = {a.name: a.id for a in archetypes}
            logger.info(f"Loaded {len(self._archetype_cache)} archetypes into cache")

    def transform_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform raw type grade data to model-compatible format.

        Args:
            raw_data: Raw type grade data

        Returns:
            Dictionary ready for TypeGrade model creation
        """
        # Extract archetype reference
        archetype_name = raw_data.get("archetype", raw_data.get("archetype_name", ""))
        archetype_id = self._archetype_cache.get(archetype_name)
        
        if not archetype_id:
            raise ValueError(f"Unknown archetype: {archetype_name}")
        
        # Extract attribute and grade info
        attribute_name = raw_data.get("attribute", raw_data.get("attribute_name", ""))
        grade_type = raw_data.get("grade_type", raw_data.get("type", ""))
        
        # Parse modifier value
        modifier_value = raw_data.get("modifier", raw_data.get("modifier_value", 1.0))
        if isinstance(modifier_value, str):
            try:
                modifier_value = float(modifier_value)
            except ValueError:
                modifier_value = 1.0
        
        # Parse level scaling data
        level_scaling = raw_data.get("level_scaling", raw_data.get("scaling", {}))
        if isinstance(level_scaling, str):
            # Try to parse as JSON if it's a string
            try:
                import json
                level_scaling = json.loads(level_scaling)
            except:
                level_scaling = {}
        
        transformed = {
            "archetype_id": archetype_id,
            "attribute_name": attribute_name,
            "grade_type": grade_type,
            "modifier_value": modifier_value,
            "level_scaling": level_scaling,
        }
        
        return transformed

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate transformed type grade data."""
        # Check required fields
        if not data.get("archetype_id"):
            logger.error("Missing required field: archetype_id")
            return False
        
        if not data.get("attribute_name"):
            logger.error("Missing required field: attribute_name")
            return False
        
        if not data.get("grade_type"):
            logger.error("Missing required field: grade_type")
            return False
        
        # Validate modifier value
        if data.get("modifier_value") is not None:
            try:
                value = float(data["modifier_value"])
                if value < 0:
                    logger.error(f"Invalid modifier_value: {value} (must be >= 0)")
                    return False
            except (TypeError, ValueError):
                logger.error(f"Invalid modifier_value: {data.get('modifier_value')}")
                return False
        
        return True

    def import_data(self, file_path: Path, resume_from: int = 0) -> None:
        """Override to handle cache loading."""
        session = self.SessionLocal()
        try:
            self._load_archetype_cache(session)
        finally:
            session.close()
        
        return super().import_data(file_path, resume_from)


# Combined importer for convenience
class AttributeImporter:
    """Combined importer for both AttributeModifier and TypeGrade data."""
    
    def __init__(self, database_url: str, batch_size: int = 1000):
        self.attribute_modifier_importer = AttributeModifierImporter(database_url, batch_size)
        self.type_grade_importer = TypeGradeImporter(database_url, batch_size)
    
    def import_attribute_modifiers(self, file_path: Path, resume_from: int = 0):
        """Import attribute modifier data."""
        return self.attribute_modifier_importer.import_data(file_path, resume_from)
    
    def import_type_grades(self, file_path: Path, resume_from: int = 0):
        """Import type grade data."""
        return self.type_grade_importer.import_data(file_path, resume_from)