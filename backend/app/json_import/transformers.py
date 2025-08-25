"""Data transformers for converting JSON data to database models."""

from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Archetype, Enhancement, Power, Powerset
from .exceptions import TransformationError


class JsonDataTransformer:
    """Transforms validated JSON data into database models."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.archetype_map: Dict[int, int] = {}  # JSON ID -> DB ID
        self.powerset_map: Dict[int, int] = {}
        self.power_map: Dict[int, int] = {}
        self.enhancement_map: Dict[int, int] = {}

    async def transform_archetype(self, data: Dict[str, Any]) -> Archetype:
        """Transform archetype data into database model.

        Args:
            data: Validated archetype data

        Returns:
            Archetype model instance

        Raises:
            TransformationError: If transformation fails
        """
        try:
            archetype = Archetype(
                name=data["name"],
                display_name=data["display_name"],
                description=data.get("description"),
                hit_points=data["hit_points"],
                max_hp=data["max_hit_points"],
                # Store powerset references as JSON for now
                primary_powersets=data.get("primary_powersets", []),
                secondary_powersets=data.get("secondary_powersets", []),
                epic_powersets=data.get("epic_powersets", []),
                inherent_powers=data.get("inherent_powers", []),
            )
            return archetype
        except Exception as e:
            raise TransformationError(f"Failed to transform archetype: {e}")

    async def transform_powerset(self, data: Dict[str, Any]) -> Powerset:
        """Transform powerset data into database model.

        Args:
            data: Validated powerset data

        Returns:
            Powerset model instance

        Raises:
            TransformationError: If transformation fails
        """
        try:
            # Map archetype ID if it exists
            archetype_id = None
            if data.get("archetype_id") and data["archetype_id"] in self.archetype_map:
                archetype_id = self.archetype_map[data["archetype_id"]]

            powerset = Powerset(
                name=data["name"],
                display_name=data.get("display_name", data["name"]),
                description=data.get("description"),
                archetype_id=archetype_id,
                power_type=data["power_type"],
                # Store power references as JSON for now
                powers=data.get("powers", []),
            )
            return powerset
        except Exception as e:
            raise TransformationError(f"Failed to transform powerset: {e}")

    async def transform_power(self, data: Dict[str, Any]) -> Power:
        """Transform power data into database model.

        Args:
            data: Validated power data

        Returns:
            Power model instance

        Raises:
            TransformationError: If transformation fails
        """
        try:
            # Map powerset ID if it exists
            powerset_id = None
            if data.get("powerset_id") and data["powerset_id"] in self.powerset_map:
                powerset_id = self.powerset_map[data["powerset_id"]]

            power = Power(
                name=data["name"],
                display_name=data.get("display_name", data["name"]),
                description=data.get("description"),
                powerset_id=powerset_id,
                power_type=data.get("power_type"),
                accuracy=data.get("accuracy", 1.0),
                damage_scale=data.get("damage", 0),
                endurance_cost=data.get("endurance_cost", 0),
                recharge_time=data.get("recharge_time", 0),
                activation_time=data.get("activation_time", 0),
                range_feet=data.get("range", 0),
                effect_area=data.get("effect_area"),
                max_targets=data.get("max_targets", 1),
                # Store additional attributes as JSON
                attributes=data.get("attributes", {}),
            )
            return power
        except Exception as e:
            raise TransformationError(f"Failed to transform power: {e}")

    async def transform_enhancement(self, data: Dict[str, Any]) -> Enhancement:
        """Transform enhancement data into database model.

        Args:
            data: Validated enhancement data

        Returns:
            Enhancement model instance

        Raises:
            TransformationError: If transformation fails
        """
        try:
            enhancement = Enhancement(
                name=data["name"],
                display_name=data["display_name"],
                description=data.get("description"),
                enhancement_type=data["enhancement_type"],
                level_min=data["level_min"],
                level_max=data["level_max"],
                schedule=data.get("schedule"),
                effects=data.get("effects", {}),
                set_id=data.get("set_id"),
            )
            return enhancement
        except Exception as e:
            raise TransformationError(f"Failed to transform enhancement: {e}")

    async def update_references(self):
        """Update cross-references between entities after initial import.

        This method should be called after all entities are imported to
        properly link relationships using the ID mappings.
        """
        # This would update foreign key references using the mapping tables
        # Implementation depends on specific database schema requirements
        pass