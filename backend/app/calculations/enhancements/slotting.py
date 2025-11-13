"""
Enhancement Slotting System

Implements Spec 11: Enhancement Slotting from the calculation engine.
Maps to MidsReborn's I9Slot.cs, SlotEntry.cs, and PowerEntry.cs.

Key features:
- Maximum 6 slots per power
- Attuned IOs (scale with character level, cap at 50)
- Catalyzed enhancements (Superior sets with 1.25x multiplier)
- Enhancement boosters (+0 to +5, each adds ~5.2%)
- Relative level multipliers for TO/DO/SO
- Exemplaring and slot availability
"""

from dataclasses import dataclass, field
from enum import Enum

# Constants from MidsReborn
MAX_SLOTS_PER_POWER = 6
SUPERIOR_MULTIPLIER = 1.25
BOOSTER_VALUE_PER_LEVEL = 0.052  # ~5.2% per boost level
ATTUNED_IO_LEVEL_CAP = 50


class EnhancementGrade(Enum):
    """Enhancement quality grades (maps to eEnhGrade)."""

    NONE = "none"  # Empty slot
    TRAINING_O = "training"  # Training Origin
    DUAL_O = "dual"  # Dual Origin
    SINGLE_O = "single"  # Single Origin (standard SOs)


class EnhancementType(Enum):
    """Enhancement types (maps to eType)."""

    NORMAL = "normal"  # TO/DO/SO
    INVENT_O = "invention"  # Invention Origins (IOs)
    SPECIAL_O = "special"  # Hamidon Origins (HOs)
    SET_O = "set"  # Set IOs


class RelativeLevel(Enum):
    """Relative level to character (maps to eEnhRelative)."""

    MINUS_THREE = -3
    MINUS_TWO = -2
    MINUS_ONE = -1
    EVEN = 0
    PLUS_ONE = 1
    PLUS_TWO = 2
    PLUS_THREE = 3
    PLUS_FOUR = 4
    PLUS_FIVE = 5


@dataclass
class Slot:
    """
    Single enhancement slot with enhancement instance.

    Maps to MidsReborn I9Slot class. Represents a slotted enhancement
    with all its properties (level, grade, boosts, etc.).

    Attributes:
        enhancement_id: Enhancement database ID (-1 = empty)
        grade: Enhancement quality (TO/DO/SO or None for IOs)
        io_level: IO level (1-53)
        relative_level: Relative to character level (-3 to +5, TO/DO/SO only)
        obtained: Whether player has acquired it
        is_attuned: Scales with character level (caps at 50)
        is_catalyzed: Upgraded to Superior (1.25x multiplier)
        is_boosted: Has enhancement boosters applied
        boost_level: Number of booster levels (+0 to +5)
    """

    enhancement_id: int = -1  # -1 = empty
    grade: EnhancementGrade = EnhancementGrade.NONE
    io_level: int = 1  # 1-53 for IOs
    relative_level: RelativeLevel = RelativeLevel.EVEN
    obtained: bool = False
    is_attuned: bool = False
    is_catalyzed: bool = False
    is_boosted: bool = False
    boost_level: int = 0  # 0-5

    @property
    def is_empty(self) -> bool:
        """Check if slot is empty."""
        return self.enhancement_id < 0

    def clone(self) -> "Slot":
        """Create a deep copy of this slot."""
        return Slot(
            enhancement_id=self.enhancement_id,
            grade=self.grade,
            io_level=self.io_level,
            relative_level=self.relative_level,
            obtained=self.obtained,
            is_attuned=self.is_attuned,
            is_catalyzed=self.is_catalyzed,
            is_boosted=self.is_boosted,
            boost_level=self.boost_level,
        )


@dataclass
class SlotEntry:
    """
    Full slot information with level and inherent status.

    Maps to MidsReborn SlotEntry struct. Tracks when the slot was added
    and whether it's an inherent slot (like Health/Stamina extra slots).

    Attributes:
        level: Character level when slot was added
        is_inherent: True if automatic/inherent slot
        enhancement: Primary enhancement (build 1)
        flipped_enhancement: Alternate build 2
    """

    level: int  # Character level when slot added
    is_inherent: bool = False
    enhancement: Slot = field(default_factory=Slot)
    flipped_enhancement: Slot | None = None  # For dual builds

    def flip(self) -> None:
        """Swap primary and secondary build enhancements."""
        if self.flipped_enhancement is not None:
            self.enhancement, self.flipped_enhancement = (
                self.flipped_enhancement,
                self.enhancement,
            )


@dataclass
class SlottedPower:
    """
    Power instance with slotting information.

    Maps to MidsReborn PowerEntry. Represents a power with all its
    enhancement slots and tracks inherent slot usage.

    Attributes:
        power_id: Power database ID
        slots: List of slot entries
        inherent_slots_used: Count of inherent slots
        is_slottable: Whether power accepts enhancements
    """

    power_id: int
    slots: list[SlotEntry] = field(default_factory=list)
    inherent_slots_used: int = 0
    is_slottable: bool = True

    @property
    def slot_count(self) -> int:
        """Get current number of slots."""
        return len(self.slots)

    def add_slot(self, slot_level: int, is_inherent: bool = False) -> bool:
        """
        Add enhancement slot to power.

        Enforces 6-slot maximum and slottable validation.

        Args:
            slot_level: Character level when slot is added
            is_inherent: Whether this is an inherent slot

        Returns:
            True if slot added successfully
        """
        # Validate slottable
        if not self.is_slottable:
            return False

        # Enforce max slots
        if self.slot_count >= MAX_SLOTS_PER_POWER:
            return False

        # Create new slot
        new_slot = SlotEntry(
            level=slot_level, is_inherent=is_inherent, enhancement=Slot()
        )

        self.slots.append(new_slot)

        if is_inherent:
            self.inherent_slots_used += 1

        return True

    def validate_slots(self) -> list[str]:
        """
        Validate all slots and enhancements.

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        # Non-slottable powers should have no slots
        if not self.is_slottable and self.slot_count > 0:
            errors.append("Power is not slottable but has slots")

        # Enforce max slots
        if self.slot_count > MAX_SLOTS_PER_POWER:
            errors.append(f"Too many slots: {self.slot_count} > {MAX_SLOTS_PER_POWER}")

        return errors

    def flip_build(self) -> None:
        """Flip all slots to secondary build."""
        for slot in self.slots:
            slot.flip()


class SlottingCalculator:
    """
    Calculate enhancement values from slotted enhancements.

    Implementation based on MidsReborn I9Slot.GetEnhancementEffect().
    Calculates enhancement bonuses from individual slots and combines
    them (additively) before ED is applied.

    Attributes:
        mult_tables: Enhancement multiplier tables (TO/DO/SO/IO schedules)
    """

    def __init__(self, mult_tables: dict[str, list[list[float]]]):
        """
        Initialize calculator with multiplier tables.

        Args:
            mult_tables: Enhancement multiplier tables
                - 'MultTO': Training Origin values [1][4]
                - 'MultDO': Dual Origin values [1][4]
                - 'MultSO': Single Origin values [1][4]
                - 'MultIO': Invention Origin values [53][4]
        """
        self.mult_tables = mult_tables

    def get_relative_level_multiplier(self, relative_level: RelativeLevel) -> float:
        """
        Get enhancement strength multiplier based on relative level.

        Implementation from Enhancement.cs GetRelativeLevelMultiplier().

        Below Even (0): multiplier = 1.0 + (level * 0.1)
          -3 = 70%, -2 = 80%, -1 = 90%, 0 = 100%

        At or Above Even: multiplier = 1.0 + (level * 0.05)
          0 = 100%, +1 = 105%, +3 = 115%, +5 = 125%

        Args:
            relative_level: Relative level enum

        Returns:
            Multiplier (0.70 to 1.25)
        """
        level = relative_level.value

        if level < 0:
            # Below character level: 10% penalty per level
            return 1.0 + (level * 0.1)
        else:
            # At or above: 5% bonus per level
            return 1.0 + (level * 0.05)

    def calculate_slot_value(
        self,
        slot: Slot,
        schedule_index: int,
        character_level: int = 50,
        set_min_level: int = 1,
        set_max_level: int = 53,
    ) -> float:
        """
        Calculate enhancement value from single slot.

        Maps to MidsReborn I9Slot.GetEnhancementEffect().

        Args:
            slot: Slot with enhancement
            schedule_index: ED schedule (0=A, 1=B, 2=C, 3=D)
            character_level: Current character level (for attuned IOs)
            set_min_level: Minimum level of set (for attuned IOs)
            set_max_level: Maximum level of set (for attuned IOs)

        Returns:
            Enhancement value (e.g., 0.424 for 42.4%)

        Examples:
            >>> slot = Slot(enhancement_id=100, io_level=50)
            >>> calculator.calculate_slot_value(slot, 0)  # Schedule A
            0.424  # 42.4% for Level 50 IO
        """
        # Empty slot returns 0
        if slot.is_empty:
            return 0.0

        # Get base multiplier by enhancement type
        base_mult = self._get_base_multiplier(
            slot, schedule_index, character_level, set_min_level, set_max_level
        )

        # Apply relative level multiplier (TO/DO/SO only)
        if slot.grade in (
            EnhancementGrade.TRAINING_O,
            EnhancementGrade.DUAL_O,
            EnhancementGrade.SINGLE_O,
        ):
            rel_mult = self.get_relative_level_multiplier(slot.relative_level)
            base_mult *= rel_mult

        # Apply superior multiplier (catalyzed sets)
        if slot.is_catalyzed:
            base_mult *= SUPERIOR_MULTIPLIER

        # Apply enhancement booster levels
        if slot.is_boosted and slot.boost_level > 0:
            boost_mult = 1.0 + (slot.boost_level * BOOSTER_VALUE_PER_LEVEL)
            base_mult *= boost_mult

        return base_mult

    def _get_base_multiplier(
        self,
        slot: Slot,
        schedule_index: int,
        character_level: int,
        set_min_level: int,
        set_max_level: int,
    ) -> float:
        """Get base multiplier from lookup tables."""
        if slot.grade == EnhancementGrade.TRAINING_O:
            return self.mult_tables["MultTO"][0][schedule_index]

        elif slot.grade == EnhancementGrade.DUAL_O:
            return self.mult_tables["MultDO"][0][schedule_index]

        elif slot.grade == EnhancementGrade.SINGLE_O:
            return self.mult_tables["MultSO"][0][schedule_index]

        elif slot.is_attuned:
            # Attuned IOs scale with character level
            effective_level = self._get_attuned_level(
                character_level, set_min_level, set_max_level
            )
            io_index = max(0, min(effective_level - 1, 52))  # 0-52 index
            return self.mult_tables["MultIO"][io_index][schedule_index]

        else:
            # Regular IO uses fixed level
            io_index = max(0, min(slot.io_level - 1, 52))  # 0-52 index
            return self.mult_tables["MultIO"][io_index][schedule_index]

    def _get_attuned_level(
        self, character_level: int, set_min_level: int, set_max_level: int
    ) -> int:
        """Calculate effective level for attuned IO."""
        # Attuned IOs cap at level 50
        effective_level = min(character_level, ATTUNED_IO_LEVEL_CAP)

        # Clamp to set's level range
        effective_level = max(effective_level, set_min_level)
        effective_level = min(effective_level, set_max_level)

        return effective_level

    def calculate_total_enhancement(
        self,
        slotted_power: SlottedPower,
        schedule_index: int,
        character_level: int = 50,
        set_min_level: int = 1,
        set_max_level: int = 53,
        exemplar_level: int | None = None,
    ) -> float:
        """
        Calculate total enhancement value from all slots (BEFORE ED).

        Enhancements are ADDITIVE before ED curve is applied.

        Maps to MidsReborn PowerEntry slot aggregation logic.

        Args:
            slotted_power: Power with slots
            schedule_index: ED schedule
            character_level: Current character level
            set_min_level: Minimum set level (for attuned)
            set_max_level: Maximum set level (for attuned)
            exemplar_level: If exemplared, level to exemplar to

        Returns:
            Total enhancement value before ED

        Examples:
            >>> # Three Level 50 Damage IOs
            >>> calculator.calculate_total_enhancement(power, 0)
            1.272  # 127.2% before ED
        """
        total = 0.0

        # Get active slots (considering exemplaring)
        active_indices = self._get_active_slot_indices(slotted_power, exemplar_level)

        for i in active_indices:
            slot_value = self.calculate_slot_value(
                slotted_power.slots[i].enhancement,
                schedule_index,
                character_level,
                set_min_level,
                set_max_level,
            )
            total += slot_value  # ADDITIVE

        return total

    def _get_active_slot_indices(
        self, slotted_power: SlottedPower, exemplar_level: int | None
    ) -> list[int]:
        """Get indices of active slots (considering exemplaring)."""
        if exemplar_level is None:
            # All slots active
            return list(range(slotted_power.slot_count))

        # When exemplared, only slots added at or below exemplar level active
        active_indices = []
        for i, slot_entry in enumerate(slotted_power.slots):
            if slot_entry.level <= exemplar_level:
                active_indices.append(i)

        return active_indices


# Validation functions
class SlottingError(Exception):
    """Base exception for slotting errors."""

    pass


class InvalidSlotCountError(SlottingError):
    """Raised when slot count exceeds maximum."""

    pass


class NonSlottablePowerError(SlottingError):
    """Raised when trying to slot non-slottable power."""

    pass


class InvalidEnhancementError(SlottingError):
    """Raised when enhancement is invalid for power."""

    pass


def validate_slotted_power(power: SlottedPower) -> list[str]:
    """
    Comprehensive validation of slotted power.

    Args:
        power: SlottedPower to validate

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    # Validate slot count
    if power.slot_count > MAX_SLOTS_PER_POWER:
        errors.append(
            f"Slot count {power.slot_count} exceeds maximum {MAX_SLOTS_PER_POWER}"
        )

    # Validate slottable
    if not power.is_slottable and power.slot_count > 0:
        errors.append("Non-slottable power has slots")

    # Validate each slot
    for i, slot_entry in enumerate(power.slots):
        # Validate slot level
        if not (1 <= slot_entry.level <= 50):
            errors.append(
                f"Slot {i}: Invalid slot level {slot_entry.level} (must be 1-50)"
            )

        # Validate enhancement (if not empty)
        if not slot_entry.enhancement.is_empty:
            enh_errors = validate_slot(slot_entry.enhancement, i)
            errors.extend(enh_errors)

    return errors


def validate_slot(slot: Slot, slot_index: int) -> list[str]:
    """Validate single enhancement slot."""
    errors = []

    # Validate IO level
    if not slot.is_empty:
        if not (1 <= slot.io_level <= 53):
            errors.append(
                f"Slot {slot_index}: Invalid IO level {slot.io_level} (must be 1-53)"
            )

    # Validate boost level
    if slot.boost_level < 0 or slot.boost_level > 5:
        errors.append(
            f"Slot {slot_index}: Invalid boost level {slot.boost_level} (must be 0-5)"
        )

    # Validate boost consistency
    if slot.is_boosted and slot.boost_level == 0:
        errors.append(f"Slot {slot_index}: Marked as boosted but boost_level is 0")

    return errors


def safe_add_slot(
    power: SlottedPower, slot_level: int, is_inherent: bool = False
) -> None:
    """
    Add slot with validation and error handling.

    Args:
        power: Power to add slot to
        slot_level: Character level when slot added
        is_inherent: Whether this is inherent slot

    Raises:
        InvalidSlotCountError: If would exceed max slots
        NonSlottablePowerError: If power is not slottable
        ValueError: If slot level is invalid
    """
    if not power.is_slottable:
        raise NonSlottablePowerError(f"Power {power.power_id} is not slottable")

    if power.slot_count >= MAX_SLOTS_PER_POWER:
        raise InvalidSlotCountError(
            f"Power already has maximum slots ({MAX_SLOTS_PER_POWER})"
        )

    if not (1 <= slot_level <= 50):
        raise ValueError(f"Invalid slot level {slot_level} (must be 1-50)")

    success = power.add_slot(slot_level, is_inherent)
    if not success:
        raise SlottingError("Failed to add slot")
