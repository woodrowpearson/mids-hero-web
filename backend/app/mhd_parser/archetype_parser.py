"""Parser for Archetype records from MHD files."""

from dataclasses import dataclass
from typing import BinaryIO

from .binary_reader import BinaryReader


@dataclass
class Archetype:
    """Represents an Archetype record from MHD data."""

    # Basic info
    display_name: str
    hitpoints: int
    hp_cap: float
    desc_long: str
    res_cap: float

    # Origins
    origins: list[str]

    # Class info
    class_name: str
    class_type: int
    column: int
    desc_short: str
    primary_group: str
    secondary_group: str
    playable: bool

    # Caps
    recharge_cap: float
    damage_cap: float
    recovery_cap: float
    regen_cap: float
    threat_cap: float
    resist_cap: float
    damage_resist_cap: float

    # Base stats
    base_recovery: float
    base_regen: float
    base_threat: float
    perception_cap: float


def parse_archetype(stream: BinaryIO) -> Archetype:
    """Parse an Archetype record from a binary stream.

    Args:
        stream: Binary stream positioned at the start of an Archetype record

    Returns:
        Parsed Archetype object

    Raises:
        EOFError: If stream ends while reading
    """
    reader = BinaryReader(stream)

    try:
        # 1. DisplayName (string)
        display_name = reader.read_string()

        # 2. Hitpoints (Int32)
        hitpoints = reader.read_int32()

        # 3. HPCap (Single/float)
        hp_cap = reader.read_float32()

        # 4. DescLong (string)
        desc_long = reader.read_string()

        # 5. ResCap (Single)
        res_cap = reader.read_float32()

        # 6. numOrigins (Int32) + Origin array (count+1 strings)
        num_origins = reader.read_int32()
        origins = []
        for _i in range(num_origins):
            origins.append(reader.read_string())
        # Read the extra string (count+1 pattern)
        reader.read_string()

        # 7. ClassName (string)
        class_name = reader.read_string()

        # 8. ClassType (Int32)
        class_type = reader.read_int32()

        # 9. Column (Int32)
        column = reader.read_int32()

        # 10. DescShort (string)
        desc_short = reader.read_string()

        # 11. PrimaryGroup (string)
        primary_group = reader.read_string()

        # 12. SecondaryGroup (string)
        secondary_group = reader.read_string()

        # 13. Playable (Boolean)
        playable = reader.read_bool()

        # 14. Various caps (7 floats in order)
        recharge_cap = reader.read_float32()
        damage_cap = reader.read_float32()
        recovery_cap = reader.read_float32()
        regen_cap = reader.read_float32()
        threat_cap = reader.read_float32()
        resist_cap = reader.read_float32()
        damage_resist_cap = reader.read_float32()

        # 15. Base stats (3 floats)
        base_recovery = reader.read_float32()
        base_regen = reader.read_float32()
        base_threat = reader.read_float32()

        # 16. PerceptionCap (Single)
        perception_cap = reader.read_float32()

        return Archetype(
            display_name=display_name,
            hitpoints=hitpoints,
            hp_cap=hp_cap,
            desc_long=desc_long,
            res_cap=res_cap,
            origins=origins,
            class_name=class_name,
            class_type=class_type,
            column=column,
            desc_short=desc_short,
            primary_group=primary_group,
            secondary_group=secondary_group,
            playable=playable,
            recharge_cap=recharge_cap,
            damage_cap=damage_cap,
            recovery_cap=recovery_cap,
            regen_cap=regen_cap,
            threat_cap=threat_cap,
            resist_cap=resist_cap,
            damage_resist_cap=damage_resist_cap,
            base_recovery=base_recovery,
            base_regen=base_regen,
            base_threat=base_threat,
            perception_cap=perception_cap,
        )

    except EOFError as e:
        # Re-raise with more context
        raise EOFError(f"Unexpected EOF while parsing Archetype: {str(e)}")
