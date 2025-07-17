"""Parser for Enhancement records and their nested structures from MHD files."""

from dataclasses import dataclass
from enum import IntEnum
from typing import BinaryIO

from .binary_reader import BinaryReader

# We'll import parse_effect when we need to handle nested FX
# from .power_parser import parse_effect, Effect


class EffectMode(IntEnum):
    """Enhancement effect mode enumeration."""
    NONE = 0
    ENHANCE = 1
    EFFECT = 2
    POWER_ENH = 3
    POWER_EFFECT = 4


@dataclass
class SEffect:
    """Represents an sEffect structure within an Enhancement."""

    mode: int
    buff_mode: int
    enhance_id: int
    enhance_sub_id: int
    schedule: int
    multiplier: float
    fx: object | None = None  # Will be Effect when implemented


@dataclass
class Enhancement:
    """Represents an Enhancement record from MHD data."""

    # Basic info
    static_index: int
    name: str
    short_name: str
    description: str

    # Type info
    type_id: int
    sub_type_id: int
    class_ids: list[int]

    # Visual and reference
    image: str
    n_id_set: int
    uid_set: str

    # Stats
    effect_chance: float
    level_min: int
    level_max: int
    unique: bool
    mut_ex_id: int
    buff_mode: int

    # Effects
    effects: list[SEffect]

    # Additional info
    uid: str
    recipe_name: str
    superior: bool
    is_proc: bool
    is_scalable: bool


@dataclass
class EnhancementSet:
    """Represents an Enhancement Set record from MHD data."""

    # Basic info
    display_index: int
    display_name: str
    short_name: str
    description: str
    set_type: int

    # Enhancements in set
    enhancement_indices: list[int]

    # Set bonuses
    bonuses: list[int]  # Power indices
    bonus_min: list[int]  # Minimum pieces for each bonus
    bonus_max: list[int]  # Maximum pieces (rarely used)
    special_bonuses: list[int]  # PVP/exemplar bonuses

    # Reference info
    uid_set: str
    level_min: int
    level_max: int


def parse_s_effect(stream: BinaryIO) -> SEffect:
    """Parse an sEffect structure from a binary stream.

    Args:
        stream: Binary stream positioned at the start of an sEffect

    Returns:
        Parsed SEffect object

    Raises:
        EOFError: If stream ends while reading
        NotImplementedError: If nested Effect FX parsing is required
    """
    reader = BinaryReader(stream)

    try:
        # Basic fields
        mode = reader.read_int32()
        buff_mode = reader.read_int32()

        # Enhance sub-structure
        enhance_id = reader.read_int32()
        enhance_sub_id = reader.read_int32()

        # Schedule and multiplier
        schedule = reader.read_int32()
        multiplier = reader.read_float32()

        # Check for nested Effect FX
        has_fx = reader.read_bool()

        fx = None
        if has_fx:
            # TODO: Import and use parse_effect from power_parser
            # fx = parse_effect(stream)
            raise NotImplementedError("Nested Effect FX parsing not yet implemented")

        return SEffect(
            mode=mode,
            buff_mode=buff_mode,
            enhance_id=enhance_id,
            enhance_sub_id=enhance_sub_id,
            schedule=schedule,
            multiplier=multiplier,
            fx=fx
        )

    except EOFError as e:
        raise EOFError(f"Unexpected EOF while parsing sEffect: {str(e)}")


def parse_enhancement(stream: BinaryIO) -> Enhancement:
    """Parse an Enhancement record from a binary stream.

    Args:
        stream: Binary stream positioned at the start of an Enhancement

    Returns:
        Parsed Enhancement object

    Raises:
        EOFError: If stream ends while reading
    """
    reader = BinaryReader(stream)

    try:
        # Basic info
        static_index = reader.read_int32()
        name = reader.read_string()
        short_name = reader.read_string()
        description = reader.read_string()

        # Type info
        type_id = reader.read_int32()
        sub_type_id = reader.read_int32()

        # ClassID array (count+1 pattern)
        class_count = reader.read_int32()
        class_ids = []
        for _ in range(class_count):
            class_ids.append(reader.read_int32())
        # Read and discard the extra entry
        reader.read_int32()

        # Visual and reference
        image = reader.read_string()
        n_id_set = reader.read_int32()
        uid_set = reader.read_string()

        # Stats
        effect_chance = reader.read_float32()
        level_min = reader.read_int32()
        level_max = reader.read_int32()
        unique = reader.read_bool()
        mut_ex_id = reader.read_int32()
        buff_mode = reader.read_int32()

        # Effect array (sEffect structures)
        effect_count = reader.read_int32()
        effects = []
        for _ in range(effect_count):
            effects.append(parse_s_effect(stream))

        # Additional info
        uid = reader.read_string()
        recipe_name = reader.read_string()
        superior = reader.read_bool()
        is_proc = reader.read_bool()
        is_scalable = reader.read_bool()

        return Enhancement(
            static_index=static_index,
            name=name,
            short_name=short_name,
            description=description,
            type_id=type_id,
            sub_type_id=sub_type_id,
            class_ids=class_ids,
            image=image,
            n_id_set=n_id_set,
            uid_set=uid_set,
            effect_chance=effect_chance,
            level_min=level_min,
            level_max=level_max,
            unique=unique,
            mut_ex_id=mut_ex_id,
            buff_mode=buff_mode,
            effects=effects,
            uid=uid,
            recipe_name=recipe_name,
            superior=superior,
            is_proc=is_proc,
            is_scalable=is_scalable
        )

    except EOFError as e:
        raise EOFError(f"Unexpected EOF while parsing Enhancement: {str(e)}")


def parse_enhancement_set(stream: BinaryIO) -> EnhancementSet:
    """Parse an EnhancementSet record from a binary stream.

    Args:
        stream: Binary stream positioned at the start of an EnhancementSet

    Returns:
        Parsed EnhancementSet object

    Raises:
        EOFError: If stream ends while reading
    """
    reader = BinaryReader(stream)

    try:
        # Basic info
        display_index = reader.read_int32()
        display_name = reader.read_string()
        short_name = reader.read_string()
        description = reader.read_string()
        set_type = reader.read_int32()

        # Enhancement indices array
        enh_count = reader.read_int32()
        enhancement_indices = []
        for _ in range(enh_count):
            enhancement_indices.append(reader.read_int32())

        # Bonus arrays
        bonus_count = reader.read_int32()
        bonuses = []
        for _ in range(bonus_count):
            bonuses.append(reader.read_int32())

        bonus_min_count = reader.read_int32()
        bonus_min = []
        for _ in range(bonus_min_count):
            bonus_min.append(reader.read_int32())

        bonus_max_count = reader.read_int32()
        bonus_max = []
        for _ in range(bonus_max_count):
            bonus_max.append(reader.read_int32())

        # Special bonuses
        special_count = reader.read_int32()
        special_bonuses = []
        for _ in range(special_count):
            special_bonuses.append(reader.read_int32())

        # Final fields
        uid_set = reader.read_string()
        level_min = reader.read_int32()
        level_max = reader.read_int32()

        return EnhancementSet(
            display_index=display_index,
            display_name=display_name,
            short_name=short_name,
            description=description,
            set_type=set_type,
            enhancement_indices=enhancement_indices,
            bonuses=bonuses,
            bonus_min=bonus_min,
            bonus_max=bonus_max,
            special_bonuses=special_bonuses,
            uid_set=uid_set,
            level_min=level_min,
            level_max=level_max
        )

    except EOFError as e:
        raise EOFError(f"Unexpected EOF while parsing EnhancementSet: {str(e)}")
