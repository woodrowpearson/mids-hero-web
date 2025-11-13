"""
Enhancement Set Bonuses System

Implements Spec 13: Enhancement Set Bonuses from the calculation engine.
Maps to MidsReborn's EnhancementSet.cs, I9SetData.cs, and Build.cs.

Key features:
- Set bonus activation (2, 3, 4, 5, 6 piece bonuses)
- Rule of 5 (maximum 5 instances of any identical bonus)
- PvE/PvP mode filtering
- Special enhancement bonuses (per-enhancement bonuses)
"""

from dataclasses import dataclass, field
from enum import Enum

# Constants from MidsReborn
RULE_OF_FIVE_LIMIT = 5  # Maximum instances of same bonus
MAX_BONUS_TIERS = 5  # Regular sets: 2-6 piece (5 tiers)
MAX_PVP_BONUS_TIERS = 11  # PvP sets can have up to 11 bonus tiers


class PvMode(Enum):
    """PvE/PvP mode for bonus activation (maps to ePvX)."""

    PVE = 0  # PvE only
    PVP = 1  # PvP only
    ANY = 2  # Both modes


@dataclass
class BonusItem:
    """
    Represents a single set bonus tier (2-piece, 3-piece, etc.).

    Maps to MidsReborn BonusItem struct (lines 412-432 in EnhancementSet.cs).

    Attributes:
        slotted_required: Number of pieces needed (2-6)
        power_ids: Bonus power IDs granted
        pv_mode: PvE/PvP/Any mode
        special: Special flag (-1 = normal)
        alt_string: Alternative display string
        power_names: Bonus power names (for display)
    """

    slotted_required: int  # Number of pieces needed (2-6)
    power_ids: list[int]  # Bonus power IDs granted
    pv_mode: PvMode = PvMode.ANY  # PvE/PvP/Any
    special: int = -1  # Special flag (-1 = normal)
    alt_string: str = ""  # Alternative display
    power_names: list[str] = field(default_factory=list)  # Display names


@dataclass
class EnhancementSet:
    """
    Enhancement set definition with bonuses.

    Maps to MidsReborn EnhancementSet class (lines 12-40 in EnhancementSet.cs).

    Attributes:
        id: Set database ID
        uid: Unique identifier string
        name: Full set name
        short_name: Abbreviated name
        set_type: Set type (Melee, Ranged, Defense, etc.)
        level_min: Minimum level (usually 10-50)
        level_max: Maximum level (usually 50-53)
        enhancement_ids: Enhancement IDs in this set
        bonuses: Regular bonuses (2-6 piece) - Bonus[0-4]
        special_bonuses: Per-enhancement bonuses - SpecialBonus[0-5]
        description: Set description
        image: Image path
    """

    id: int
    uid: str
    name: str
    short_name: str
    set_type: str
    level_min: int
    level_max: int
    enhancement_ids: list[int]
    bonuses: list[BonusItem] = field(default_factory=list)  # Regular bonuses
    special_bonuses: list[BonusItem] = field(default_factory=list)  # Per-enhancement
    description: str = ""
    image: str = ""


@dataclass
class SlottedSet:
    """
    Tracks a set slotted in a specific power.

    Maps to MidsReborn I9SetData.sSetInfo struct (lines 130-136 in I9SetData.cs).

    Attributes:
        power_id: Power in build where set is slotted
        set_id: Enhancement set ID
        slotted_count: How many pieces from this set are slotted
        enhancement_ids: Specific enhancement IDs slotted
    """

    power_id: int
    set_id: int
    slotted_count: int
    enhancement_ids: list[int]  # Specific enhancements slotted


class SetBonusCalculator:
    """
    Calculates active set bonuses with Rule of 5.

    Implementation based on MidsReborn:
    - I9SetData.BuildEffects() (lines 73-128)
    - Build.GetSetBonusPowers() (lines 1372-1405)

    The Rule of 5: Only 5 instances of any identical bonus power can be
    active at once. Additional instances are suppressed.
    """

    def __init__(self, pv_mode: PvMode = PvMode.PVE):
        """
        Initialize calculator.

        Args:
            pv_mode: PvE or PvP mode for bonus filtering
        """
        self.pv_mode = pv_mode
        self.bonus_power_counts: dict[int, int] = {}

    def calculate_set_bonuses(
        self,
        slotted_sets: list[SlottedSet],
        enhancement_sets: dict[int, EnhancementSet],
    ) -> list[int]:
        """
        Calculate all active set bonuses with Rule of 5 applied.

        Returns list of active bonus power IDs. May contain duplicates
        (up to 5 times each due to Rule of 5).

        Implementation from MidsReborn I9SetData.BuildEffects() and
        Build.GetSetBonusPowers().

        Args:
            slotted_sets: All sets slotted across all powers
            enhancement_sets: Set definitions by ID

        Returns:
            List of bonus power IDs (may contain duplicates up to 5)

        Examples:
            >>> # Three powers each with 2-piece Thunderstrike
            >>> # Each grants +2% Damage bonus (same power ID)
            >>> calculator.calculate_set_bonuses(sets, set_defs)
            [100, 100, 100]  # 3 instances of power ID 100

            >>> # Six powers each with 2-piece granting same bonus
            >>> # Only first 5 count due to Rule of 5
            >>> calculator.calculate_set_bonuses(sets, set_defs)
            [100, 100, 100, 100, 100]  # 6th instance suppressed
        """
        active_bonuses = []
        self.bonus_power_counts = {}

        for slotted in slotted_sets:
            set_def = enhancement_sets.get(slotted.set_id)
            if not set_def:
                continue

            # STEP 1: Check regular bonuses (2-6 piece)
            # From I9SetData.cs lines 75-98
            if slotted.slotted_count > 1:
                for bonus in set_def.bonuses:
                    # Check if we have enough pieces slotted
                    if slotted.slotted_count < bonus.slotted_required:
                        continue

                    # Check PvE/PvP mode
                    if not self._should_apply_bonus(bonus):
                        continue

                    # Add bonus powers with Rule of 5
                    added_powers = self._apply_rule_of_5(bonus.power_ids)
                    active_bonuses.extend(added_powers)

            # STEP 2: Check special bonuses (per-enhancement)
            # From I9SetData.cs lines 100-126
            if slotted.slotted_count > 0:
                for enh_index, enh_id in enumerate(set_def.enhancement_ids):
                    # Check if this specific enhancement is slotted
                    if enh_id not in slotted.enhancement_ids:
                        continue

                    # Get special bonus for this enhancement (parallel array)
                    if enh_index >= len(set_def.special_bonuses):
                        continue

                    special = set_def.special_bonuses[enh_index]
                    if not special or len(special.power_ids) == 0:
                        continue

                    # Check PvE/PvP mode
                    if not self._should_apply_bonus(special):
                        continue

                    # Add special bonus powers with Rule of 5
                    added_powers = self._apply_rule_of_5(special.power_ids)
                    active_bonuses.extend(added_powers)

        return active_bonuses

    def _should_apply_bonus(self, bonus: BonusItem) -> bool:
        """
        Check if bonus applies in current PvE/PvP mode.

        Implementation from I9SetData.cs lines 84-87.

        Args:
            bonus: Bonus item to check

        Returns:
            True if bonus should be applied
        """
        # ANY mode bonuses always apply
        if bonus.pv_mode == PvMode.ANY:
            return True

        # Mode-specific bonuses only apply in matching mode
        return bonus.pv_mode == self.pv_mode

    def _apply_rule_of_5(self, power_ids: list[int]) -> list[int]:
        """
        Apply Rule of 5: maximum 5 instances of any bonus power.

        Implementation from Build.cs lines 1389-1404.

        The check is `>= 6` to allow exactly 5 instances:
        - Instances 1-5: count 1-5, all added
        - Instance 6+: count 6+, suppressed

        Args:
            power_ids: Bonus power IDs to add

        Returns:
            Power IDs that should be added (may be empty if all suppressed)
        """
        added = []
        for power_id in power_ids:
            # Get current count for this power
            count = self.bonus_power_counts.get(power_id, 0)

            # Increment count
            count += 1
            self.bonus_power_counts[power_id] = count

            # Rule of 5: only add if count < 6 (allows 1-5)
            # Line 1398 in Build.cs: if (setCount[powerIndex] >= 6) continue;
            if count < 6:
                added.append(power_id)
            # else: suppressed by Rule of 5 (6th+ instance)

        return added

    def get_bonus_counts(self) -> dict[int, int]:
        """
        Get count of each bonus power after Rule of 5 applied.

        Returns:
            Dictionary mapping power_id -> count
        """
        return self.bonus_power_counts.copy()

    def get_suppressed_bonuses(self) -> list[int]:
        """
        Get bonus powers that exceed Rule of 5 limit.

        Returns:
            List of power IDs that have > 5 instances
        """
        suppressed = []
        for power_id, count in self.bonus_power_counts.items():
            if count > RULE_OF_FIVE_LIMIT:
                suppressed.append(power_id)
        return suppressed


def track_slotted_sets(build_powers: list[dict]) -> list[SlottedSet]:
    """
    Extract slotted set information from build data.

    Helper function to convert build data into SlottedSet objects for
    the calculator.

    Args:
        build_powers: List of power dictionaries with slot information

    Returns:
        List of SlottedSet objects, one per set per power

    Examples:
        >>> build_powers = [
        ...     {
        ...         'id': 1,
        ...         'slots': [
        ...             {'enhancement': {'id': 100, 'type': 'SetO', 'set_id': 10}},
        ...             {'enhancement': {'id': 101, 'type': 'SetO', 'set_id': 10}},
        ...         ]
        ...     }
        ... ]
        >>> track_slotted_sets(build_powers)
        [SlottedSet(power_id=1, set_id=10, slotted_count=2, ...)]
    """
    slotted_sets = []

    for power in build_powers:
        set_tracker: dict[int, list[int]] = {}  # set_id -> [enhancement_ids]

        # Scan slots for Set IOs
        for slot in power.get("slots", []):
            enh = slot.get("enhancement")
            if not enh:
                continue

            # Check if Set IO
            if enh.get("type") != "SetO":
                continue

            set_id = enh.get("set_id")
            if set_id is None:
                continue

            # Track this enhancement
            if set_id not in set_tracker:
                set_tracker[set_id] = []
            set_tracker[set_id].append(enh["id"])

        # Create SlottedSet for each set in this power
        for set_id, enh_ids in set_tracker.items():
            slotted_sets.append(
                SlottedSet(
                    power_id=power["id"],
                    set_id=set_id,
                    slotted_count=len(enh_ids),
                    enhancement_ids=enh_ids,
                )
            )

    return slotted_sets


def create_bonus_summary(
    active_bonuses: list[int],
    bonus_power_counts: dict[int, int],
    power_names: dict[int, str],
) -> dict[str, any]:
    """
    Create human-readable summary of set bonuses.

    Args:
        active_bonuses: List of active bonus power IDs
        bonus_power_counts: Count of each power ID
        power_names: Mapping of power_id -> display name

    Returns:
        Dictionary with summary information

    Examples:
        >>> create_bonus_summary([100, 100, 101], {100: 2, 101: 1}, {100: "+2% Damage", 101: "+1.5% Defense"})
        {
            'total_bonuses': 3,
            'unique_bonuses': 2,
            'bonuses': [
                {'power_id': 100, 'name': '+2% Damage', 'count': 2, 'suppressed': False},
                {'power_id': 101, 'name': '+1.5% Defense', 'count': 1, 'suppressed': False}
            ],
            'rule_of_5_active': False
        }
    """
    bonus_list = []
    rule_of_5_triggered = False

    for power_id, count in bonus_power_counts.items():
        is_suppressed = count > RULE_OF_FIVE_LIMIT
        if is_suppressed:
            rule_of_5_triggered = True

        bonus_list.append(
            {
                "power_id": power_id,
                "name": power_names.get(power_id, f"Power {power_id}"),
                "count": count,
                "effective_count": min(count, RULE_OF_FIVE_LIMIT),
                "suppressed": is_suppressed,
                "suppressed_count": max(0, count - RULE_OF_FIVE_LIMIT),
            }
        )

    # Sort by count (most common first)
    bonus_list.sort(key=lambda x: x["count"], reverse=True)

    return {
        "total_bonuses": len(active_bonuses),
        "unique_bonuses": len(bonus_power_counts),
        "bonuses": bonus_list,
        "rule_of_5_active": rule_of_5_triggered,
        "max_possible_bonuses": sum(bonus_power_counts.values()),
        "suppressed_bonuses": sum(
            max(0, c - RULE_OF_FIVE_LIMIT) for c in bonus_power_counts.values()
        ),
    }


# Validation functions
class SetBonusError(Exception):
    """Base exception for set bonus errors."""

    pass


class InvalidSetError(SetBonusError):
    """Raised when set ID is invalid."""

    pass


class InvalidBonusTierError(SetBonusError):
    """Raised when bonus tier is invalid."""

    pass


def validate_enhancement_set(set_def: EnhancementSet) -> list[str]:
    """
    Validate enhancement set definition.

    Args:
        set_def: EnhancementSet to validate

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    # Validate level range
    if set_def.level_min < 1 or set_def.level_min > 53:
        errors.append(f"Invalid level_min: {set_def.level_min} (must be 1-53)")

    if set_def.level_max < 1 or set_def.level_max > 53:
        errors.append(f"Invalid level_max: {set_def.level_max} (must be 1-53)")

    if set_def.level_min > set_def.level_max:
        errors.append(
            f"level_min ({set_def.level_min}) > level_max ({set_def.level_max})"
        )

    # Validate enhancement count
    if len(set_def.enhancement_ids) < 2:
        errors.append(
            f"Set has only {len(set_def.enhancement_ids)} enhancements (need at least 2)"
        )

    if len(set_def.enhancement_ids) > 6:
        errors.append(f"Set has {len(set_def.enhancement_ids)} enhancements (max 6)")

    # Validate bonus tiers
    for i, bonus in enumerate(set_def.bonuses):
        if bonus.slotted_required < 2 or bonus.slotted_required > 6:
            errors.append(
                f"Bonus tier {i}: Invalid slotted_required {bonus.slotted_required} (must be 2-6)"
            )

        if len(bonus.power_ids) == 0:
            errors.append(f"Bonus tier {i}: No bonus powers defined")

    # Validate special bonuses array size
    if len(set_def.special_bonuses) > len(set_def.enhancement_ids):
        errors.append(
            f"Too many special bonuses ({len(set_def.special_bonuses)}) "
            f"for enhancements ({len(set_def.enhancement_ids)})"
        )

    return errors


def validate_slotted_set(slotted: SlottedSet) -> list[str]:
    """
    Validate slotted set instance.

    Args:
        slotted: SlottedSet to validate

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    # Validate slotted count
    if slotted.slotted_count < 0:
        errors.append(f"Negative slotted_count: {slotted.slotted_count}")

    if slotted.slotted_count > 6:
        errors.append(f"Slotted count {slotted.slotted_count} exceeds maximum (6)")

    # Validate enhancement IDs match count
    if len(slotted.enhancement_ids) != slotted.slotted_count:
        errors.append(
            f"Enhancement ID count ({len(slotted.enhancement_ids)}) "
            f"doesn't match slotted_count ({slotted.slotted_count})"
        )

    return errors
