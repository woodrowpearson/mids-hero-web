"""JSON Schema validators for City of Heroes data."""

import json
from pathlib import Path
from typing import Any, Dict

from pydantic import BaseModel, Field, ValidationError as PydanticValidationError

from .exceptions import ValidationError


class PowerSchema(BaseModel):
    """Schema for power data validation."""

    id: int
    name: str
    display_name: str | None = None
    description: str | None = None
    powerset_id: int | None = None
    power_type: str | None = None
    accuracy: float = Field(default=1.0, ge=0)
    damage: float = Field(default=0, ge=0)
    endurance_cost: float = Field(default=0, ge=0)
    recharge_time: float = Field(default=0, ge=0)
    activation_time: float = Field(default=0, ge=0)
    range: float = Field(default=0, ge=0)
    effect_area: str | None = None
    max_targets: int = Field(default=1, ge=1)
    attributes: Dict[str, Any] = Field(default_factory=dict)


class PowersetSchema(BaseModel):
    """Schema for powerset data validation."""

    id: int
    name: str
    display_name: str | None = None
    description: str | None = None
    archetype_id: int | None = None
    power_type: str  # Primary, Secondary, Pool, Epic, etc.
    powers: list[int] = Field(default_factory=list)


class ArchetypeSchema(BaseModel):
    """Schema for archetype data validation."""

    id: int
    name: str
    display_name: str
    description: str | None = None
    hit_points: float = Field(gt=0)
    max_hit_points: float = Field(gt=0)
    primary_powersets: list[int] = Field(default_factory=list)
    secondary_powersets: list[int] = Field(default_factory=list)
    epic_powersets: list[int] = Field(default_factory=list)
    inherent_powers: list[int] = Field(default_factory=list)


class EnhancementSchema(BaseModel):
    """Schema for enhancement data validation."""

    id: int
    name: str
    display_name: str
    description: str | None = None
    enhancement_type: str  # IO, SO, DO, TO, Set
    level_min: int = Field(ge=1, le=50)
    level_max: int = Field(ge=1, le=50)
    schedule: str | None = None
    effects: Dict[str, float] = Field(default_factory=dict)
    set_id: int | None = None


class JsonSchemaValidator:
    """Validates JSON data against defined schemas."""

    def __init__(self):
        self.schemas = {
            "power": PowerSchema,
            "powerset": PowersetSchema,
            "archetype": ArchetypeSchema,
            "enhancement": EnhancementSchema,
        }

    def validate(self, data: Dict[str, Any], schema_type: str) -> BaseModel:
        """Validate data against a specific schema.

        Args:
            data: The data to validate
            schema_type: The type of schema to validate against

        Returns:
            Validated pydantic model instance

        Raises:
            ValidationError: If validation fails
        """
        if schema_type not in self.schemas:
            raise ValidationError(f"Unknown schema type: {schema_type}")

        schema_class = self.schemas[schema_type]
        try:
            return schema_class(**data)
        except PydanticValidationError as e:
            errors = [
                {"field": err["loc"][0], "message": err["msg"]} for err in e.errors()
            ]
            raise ValidationError(
                f"Validation failed for {schema_type} data", errors=errors
            )

    def validate_file(self, file_path: Path, schema_type: str) -> list[BaseModel]:
        """Validate a JSON file containing multiple records.

        Args:
            file_path: Path to the JSON file
            schema_type: The type of schema to validate against

        Returns:
            List of validated model instances

        Raises:
            ValidationError: If validation fails for any record
        """
        if not file_path.exists():
            raise ValidationError(f"File not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON in {file_path}: {e}")

        # Handle both single object and array of objects
        if not isinstance(data, list):
            data = [data]

        validated_records = []
        for idx, record in enumerate(data):
            try:
                validated = self.validate(record, schema_type)
                validated_records.append(validated)
            except ValidationError as e:
                raise ValidationError(f"Record {idx} failed validation: {e}")

        return validated_records

    def validate_bulk(
        self, data: list[Dict[str, Any]], schema_type: str
    ) -> list[BaseModel]:
        """Validate multiple records at once.

        Args:
            data: List of records to validate
            schema_type: The type of schema to validate against

        Returns:
            List of validated model instances

        Raises:
            ValidationError: If any record fails validation
        """
        validated_records = []
        errors = []

        for idx, record in enumerate(data):
            try:
                validated = self.validate(record, schema_type)
                validated_records.append(validated)
            except ValidationError as e:
                errors.append({"index": idx, "error": str(e)})

        if errors:
            raise ValidationError(
                f"Validation failed for {len(errors)} records", errors=errors
            )

        return validated_records