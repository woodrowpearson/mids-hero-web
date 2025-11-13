"""
Pet Calculations

Calculates power effects and attributes for summonable entities (pets) that inherit
some stats from caster and have their own enhancement slotting.

Based on:
    - MidsReborn Core/PetInfo.cs
    - MidsReborn Core/SummonedEntity.cs
    - MidsReborn Core/Base/Data_Classes/Power.cs (AbsorbPetEffects)
    - Specification: docs/midsreborn/calculations/32-pet-calculations.md
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EntityType(Enum):
    """Types of summonable entities."""

    PET = "pet"  # Standard summonable pets
    HENCHMAN = "henchman"  # Mastermind henchmen
    PSEUDOPET = "pseudopet"  # Invisible effect delivery entities
    ENTITY = "entity"  # Generic entity


@dataclass
class InheritedCasterBuffs:
    """
    Buffs that pets inherit from their caster.

    Pets inherit:
    - Global +Accuracy (multiplicative)
    - Global +ToHit (additive)
    - Global +Damage buffs (by damage type)
    - Global +Healing buffs

    Pets DO NOT inherit:
    - Defense, Resistance, HP, Endurance, Recharge, Range, Movement
    """

    accuracy_multiplier: float = 1.0  # e.g., 1.20 = +20% accuracy
    tohit_bonus: float = 0.0  # e.g., 0.10 = +10% tohit
    damage_buffs: dict[str, float] = field(
        default_factory=dict
    )  # By damage type, e.g., {'smashing': 0.50}
    healing_multiplier: float = 1.0  # e.g., 1.30 = +30% healing


@dataclass
class PetPowerData:
    """
    Base and buffed versions of a single pet power.

    Tracks:
    - base_power: Unbuffed pet power from database
    - buffed_power: After caster inheritance + pet slotting
    """

    base_damage: float = 0.0  # Base damage value
    enhanced_damage: float = 0.0  # After pet enhancements
    final_damage: float = 0.0  # After caster buffs

    base_accuracy: float = 1.0
    final_accuracy: float = 1.0

    pet_enhancement_bonus: float = 0.0  # From pet slotting (%)
    caster_buff_bonus: float = 0.0  # From caster inheritance (%)

    @property
    def total_increase_percent(self) -> float:
        """Calculate total percentage increase from base to final."""
        if self.base_damage == 0:
            return 0.0
        return ((self.final_damage - self.base_damage) / self.base_damage) * 100.0


class PetCalculator:
    """
    Calculate pet power effects with selective caster inheritance.

    Implements:
    - Selective inheritance (accuracy/damage only, NOT defense/recharge)
    - Pet-specific enhancement slotting
    - Entity class modifiers
    """

    def __init__(
        self, database: Any | None = None, character: Any | None = None
    ) -> None:
        """
        Initialize pet calculator.

        Args:
            database: Game database for entity/power lookups
            character: Character/build for caster buff calculations
        """
        self.database = database
        self.character = character

    def calculate_pet_power(
        self,
        base_damage: float,
        damage_type: str,
        base_accuracy: float = 1.0,
        pet_enhancements: dict[str, float] | None = None,
        caster_buffs: InheritedCasterBuffs | None = None,
        entity_class_modifier: float = 1.0,
    ) -> PetPowerData:
        """
        Calculate final pet power values with enhancements and caster buffs.

        Args:
            base_damage: Base pet damage value
            damage_type: Type of damage (smashing, lethal, etc.)
            base_accuracy: Base accuracy value
            pet_enhancements: Pet enhancement bonuses {'damage': 0.636, 'accuracy': 0.20}
            caster_buffs: Inherited buffs from caster
            entity_class_modifier: Entity class damage modifier (default 1.0)

        Returns:
            PetPowerData with base, enhanced, and final values
        """
        if pet_enhancements is None:
            pet_enhancements = {}
        if caster_buffs is None:
            caster_buffs = InheritedCasterBuffs()

        # Step 1: Apply pet enhancements
        pet_damage_bonus = pet_enhancements.get("damage", 0.0)
        enhanced_damage = base_damage * (1.0 + pet_damage_bonus)

        pet_accuracy_bonus = pet_enhancements.get("accuracy", 0.0)
        enhanced_accuracy = base_accuracy * (1.0 + pet_accuracy_bonus)

        # Step 2: Apply entity class modifier
        enhanced_damage *= entity_class_modifier

        # Step 3: Apply inherited caster buffs
        # Only damage and accuracy are inherited
        caster_damage_buff = caster_buffs.damage_buffs.get(damage_type, 0.0)
        final_damage = enhanced_damage * (1.0 + caster_damage_buff)

        final_accuracy = enhanced_accuracy * caster_buffs.accuracy_multiplier

        # Calculate increases
        pet_enhancement_increase = (
            ((enhanced_damage - base_damage) / base_damage * 100.0)
            if base_damage > 0
            else 0.0
        )
        caster_buff_increase = caster_damage_buff * 100.0

        return PetPowerData(
            base_damage=base_damage,
            enhanced_damage=enhanced_damage,
            final_damage=final_damage,
            base_accuracy=base_accuracy,
            final_accuracy=final_accuracy,
            pet_enhancement_bonus=pet_enhancement_increase,
            caster_buff_bonus=caster_buff_increase,
        )

    def apply_pet_enhancements(
        self, base_value: float, enhancement_bonus: float, apply_ed: bool = True
    ) -> float:
        """
        Apply pet enhancement bonuses to base value.

        Args:
            base_value: Base attribute value
            enhancement_bonus: Sum of enhancement bonuses (e.g., 0.636 = 63.6%)
            apply_ed: Whether to apply Enhancement Diversification

        Returns:
            Enhanced value
        """
        # TODO: Integrate with ED schedule calculator when available
        # For now, apply enhancement bonus directly
        return base_value * (1.0 + enhancement_bonus)

    def get_inherited_caster_buffs(
        self,
        caster_accuracy_mult: float = 1.0,
        caster_tohit_bonus: float = 0.0,
        caster_damage_buffs: dict[str, float] | None = None,
        caster_healing_mult: float = 1.0,
    ) -> InheritedCasterBuffs:
        """
        Build inherited caster buffs structure.

        Args:
            caster_accuracy_mult: Caster's total accuracy multiplier
            caster_tohit_bonus: Caster's total tohit bonus
            caster_damage_buffs: Caster's damage buffs by type
            caster_healing_mult: Caster's healing multiplier

        Returns:
            InheritedCasterBuffs object
        """
        if caster_damage_buffs is None:
            caster_damage_buffs = {}

        return InheritedCasterBuffs(
            accuracy_multiplier=caster_accuracy_mult,
            tohit_bonus=caster_tohit_bonus,
            damage_buffs=caster_damage_buffs.copy(),
            healing_multiplier=caster_healing_mult,
        )

    def calculate_absorbed_pet_effects(
        self,
        pet_damage_per_power: list[float],
        stacking: int = 1,
        entity_class_modifier: float = 1.0,
    ) -> float:
        """
        Calculate total absorbed pet damage for summon power display.

        When a summon power has AbsorbSummonEffects flag, it shows the total
        damage capability of the summoned pet.

        Args:
            pet_damage_per_power: List of damage values from all pet powers
            stacking: Number of pets summoned (for variable stacking)
            entity_class_modifier: Entity class damage modifier

        Returns:
            Total absorbed damage capability
        """
        total_damage = sum(pet_damage_per_power)
        total_damage *= entity_class_modifier
        total_damage *= stacking

        return total_damage
