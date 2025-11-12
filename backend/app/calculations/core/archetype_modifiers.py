"""
Archetype Modifiers - AT-specific scaling for power effects

Implements archetype modifier system that scales power effects differently for each archetype.
Maps to MidsReborn's Modifiers.cs and DatabaseAPI.GetModifier() functions.

The same power does different amounts of damage/buff/debuff/control for different archetypes.
This is the core mechanic that differentiates archetypes beyond just HP/caps.
"""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ModifierTable:
    """
    Single modifier table (e.g., Melee_Damage).

    Maps to MidsReborn's ModifierTable class.
    Each table has 55 levels × 60 archetype columns of float modifiers.

    Attributes:
        id: Table name (e.g., "Melee_Damage", "Ranged_Buff_Def")
        base_index: Base index from MidsReborn (legacy field)
        table: 2D array [level][archetype_column] of float modifiers
    """

    id: str
    base_index: int
    table: list[list[float]]

    def get_modifier(self, level: int, archetype_column: int) -> float:
        """
        Get modifier for specific level and archetype.

        Args:
            level: Character level (1-55)
            archetype_column: Archetype column index (0-59)

        Returns:
            Modifier value, or 0.0 if out of bounds

        Examples:
            >>> table.get_modifier(50, 1)  # Scrapper at level 50
            -30.5856
        """
        # Validate bounds - matches C# behavior of returning 0 for invalid inputs
        if level < 1 or level > 55:
            return 0.0

        level_idx = level - 1  # Convert to 0-based index

        if level_idx >= len(self.table):
            return 0.0

        if archetype_column < 0 or archetype_column >= len(self.table[level_idx]):
            return 0.0

        return self.table[level_idx][archetype_column]

    def get_all_at_level(self, level: int) -> list[float]:
        """
        Get all archetype modifiers at a specific level.

        Args:
            level: Character level (1-55)

        Returns:
            List of modifiers for all archetypes, or empty list if invalid
        """
        if level < 1 or level > 55:
            return []

        level_idx = level - 1
        if level_idx >= len(self.table):
            return []

        return self.table[level_idx].copy()

    def __repr__(self) -> str:
        return f"ModifierTable(id='{self.id}', levels={len(self.table)})"


class ArchetypeModifiers:
    """
    Manager for all archetype modifier tables.

    Maps to MidsReborn's Modifiers class and DatabaseAPI.GetModifier() methods.
    Loads from AttribMod.json and provides fast lookups.
    """

    def __init__(self):
        self.tables: dict[str, ModifierTable] = {}
        self.table_index: dict[str, int] = {}

    @classmethod
    def load_from_json(cls, filepath: Path) -> "ArchetypeModifiers":
        """
        Load modifier tables from AttribMod.json.

        Args:
            filepath: Path to AttribMod.json

        Returns:
            ArchetypeModifiers instance

        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If JSON is invalid

        Examples:
            >>> modifiers = ArchetypeModifiers.load_from_json(
            ...     Path("data/homecoming/AttribMod.json")
            ... )
            >>> len(modifiers.tables)
            102
        """
        with open(filepath) as f:
            data = json.load(f)

        instance = cls()

        for idx, table_data in enumerate(data["Modifier"]):
            table = ModifierTable(
                id=table_data["ID"],
                base_index=table_data["BaseIndex"],
                table=table_data["Table"],
            )
            instance.tables[table.id] = table
            instance.table_index[table.id] = idx

        return instance

    @classmethod
    def create_test_instance(cls) -> "ArchetypeModifiers":
        """
        Create instance with test data for unit tests.

        Creates minimal modifier tables with known values from Spec 16:
        - Melee_Damage: Level 50 Scrapper = -30.5856
        - Melee_Buff_Def: Level 50 Defender = 0.1
        - Melee_Ones: All values = 1.0

        Returns:
            ArchetypeModifiers with test data
        """
        instance = cls()

        # Create Melee_Damage table with test values from Spec 16
        # Level 50 values: Tanker=-55.6102, Scrapper=-30.5856, Defender=-30.5856,
        #                  Controller=-62.5615, Blaster=-52.8297
        melee_damage_level_50 = [
            -55.6102,  # Tanker (column 0)
            -30.5856,  # Scrapper (column 1)
            -30.5856,  # Defender (column 2)
            -62.5615,  # Controller (column 3)
            -52.8297,  # Blaster (column 4)
        ] + [
            0.0
        ] * 55  # Pad to 60 columns

        # Create minimal 55-level table (only need level 50 for tests)
        melee_damage_table = [[0.0] * 60 for _ in range(55)]
        melee_damage_table[49] = melee_damage_level_50  # Level 50 = index 49

        instance.tables["Melee_Damage"] = ModifierTable(
            id="Melee_Damage", base_index=0, table=melee_damage_table
        )

        # Create Melee_Buff_Def table with test values
        melee_buff_def_level_50 = [
            0.07,  # Tanker
            0.09,  # Scrapper
            0.1,  # Defender (highest)
            0.075,  # Controller
            0.1,  # Blaster
        ] + [0.0] * 55

        melee_buff_def_table = [[0.0] * 60 for _ in range(55)]
        melee_buff_def_table[49] = melee_buff_def_level_50

        instance.tables["Melee_Buff_Def"] = ModifierTable(
            id="Melee_Buff_Def", base_index=1, table=melee_buff_def_table
        )

        # Create Melee_Ones table (all 1.0)
        melee_ones_table = [[1.0] * 60 for _ in range(55)]

        instance.tables["Melee_Ones"] = ModifierTable(
            id="Melee_Ones", base_index=2, table=melee_ones_table
        )

        # Update index
        for idx, table_id in enumerate(instance.tables.keys()):
            instance.table_index[table_id] = idx

        return instance

    def get_modifier(self, table_id: str, level: int, archetype_column: int) -> float:
        """
        Main lookup function for modifiers.

        Maps to MidsReborn's DatabaseAPI.GetModifier(int iClass, int iTable, int iLevel).

        Args:
            table_id: Modifier table name (e.g., "Melee_Damage")
            level: Character level (1-55)
            archetype_column: Archetype column index (0-59)

        Returns:
            Modifier value, or 0.0 if table not found or out of bounds

        Examples:
            >>> modifiers = ArchetypeModifiers.create_test_instance()
            >>> modifiers.get_modifier("Melee_Damage", 50, 1)
            -30.5856
            >>> modifiers.get_modifier("NonExistent", 50, 1)
            0.0
        """
        if table_id not in self.tables:
            return 0.0

        return self.tables[table_id].get_modifier(level, archetype_column)

    def get_table(self, table_id: str) -> ModifierTable | None:
        """
        Get full modifier table by ID.

        Args:
            table_id: Modifier table name

        Returns:
            ModifierTable or None if not found
        """
        return self.tables.get(table_id)

    def table_exists(self, table_id: str) -> bool:
        """
        Check if a modifier table exists.

        Args:
            table_id: Modifier table name

        Returns:
            True if table exists
        """
        return table_id in self.tables

    def list_tables(self) -> list[str]:
        """
        Get list of all table IDs.

        Returns:
            List of table names (e.g., ["Melee_Damage", "Ranged_Heal", ...])
        """
        return list(self.tables.keys())

    def validate_structure(self) -> list[str]:
        """
        Validate modifier table structure.

        Checks:
        - Each table has 55 levels
        - All levels have consistent column count

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        for table_id, table in self.tables.items():
            # Check level count
            if len(table.table) != 55:
                errors.append(
                    f"Table '{table_id}' has {len(table.table)} levels, expected 55"
                )

            # Check column consistency
            if len(table.table) > 0:
                expected_columns = len(table.table[0])
                for level_idx, level_data in enumerate(table.table):
                    if len(level_data) != expected_columns:
                        errors.append(
                            f"Table '{table_id}' level {level_idx + 1} has "
                            f"{len(level_data)} columns, expected {expected_columns}"
                        )

        return errors

    def __repr__(self) -> str:
        return f"ArchetypeModifiers(tables={len(self.tables)})"


def calculate_effect_magnitude(
    base_magnitude: float, scale: float, modifier: float
) -> float:
    """
    Calculate final effect magnitude with archetype modifier.

    Maps to MidsReborn's Effect magnitude calculation:
    Scale * nMagnitude * DatabaseAPI.GetModifier(this)

    Args:
        base_magnitude: Base effect magnitude from power definition
        scale: Scale multiplier (default 1.0)
        modifier: Archetype modifier from modifier table

    Returns:
        Final scaled magnitude

    Examples:
        >>> # Scrapper melee attack at level 50
        >>> calculate_effect_magnitude(10.0, 1.0, -30.5856)
        -305.856
        >>> # Defender defense buff at level 50
        >>> calculate_effect_magnitude(5.0, 1.0, 0.1)
        0.5
    """
    return scale * base_magnitude * modifier
