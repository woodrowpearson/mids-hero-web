"""Parser for Power records and their nested structures from MHD files."""

from dataclasses import dataclass
from enum import IntEnum
from typing import BinaryIO

from .binary_reader import BinaryReader


class PowerType(IntEnum):
    """Power activation type enumeration."""
    NONE = 0
    CLICK = 1
    TOGGLE = 2
    AUTO_ = 3  # AUTO is reserved


class EffectType(IntEnum):
    """Effect type enumeration."""
    NONE = 0
    DAMAGE = 1
    HEAL = 2
    DEFENSE = 3
    ENDURANCE = 4
    MEZE = 5
    ENHANCEMENT = 6
    SUMMON = 7


@dataclass
class Requirement:
    """Represents a requirement for a power or effect."""

    class_name: str
    class_name_not: str
    classes_required: list[int]
    classes_disallowed: list[int]
    power_ids: list[int]
    power_ids_not: list[int]


@dataclass
class Effect:
    """Represents an Effect within a Power."""

    # Basic identifiers
    power_full_name: int
    effect_class: int
    effect_type: int
    damage_type: int
    mez_type: int
    et_modifies: int
    summon: str

    # Numeric values (15 floats in C# struct)
    scale: float
    duration: float
    magnitude: float
    ticks: float
    delay_time: float
    tick_chance: float
    percent_chance: float
    attrib_mod: float
    accuracy: float
    radius: float
    arc: float
    range: float
    range_secondary: float
    endurance_cost: float
    interval_time: float

    # Display and probability
    display_percentage: int
    probability: float
    delay: float
    stacking: int

    # Arrays
    suppression: list[bool]
    reward: list[str]
    effect_ids: list[str]
    ignore_ed: list[int]
    ignore_scale: list[int]

    # Nested requirement
    requirement: Requirement

    # Special fields
    special_case: str
    uid_class_name: int
    n_id_class_name: int
    cancel_events: list[int]

    # Additional fields
    attrib_type: int
    aspect: int
    modifier_table: str
    n_modifier_table: int
    power_full_name_enh: str
    buff_mode: int
    override: list[str]

    # Final fields
    procs_per_minute: int
    cancelable: bool
    ignore_toggle_drop: bool
    ignore_active_defense: bool
    chain_ids: list[int]
    chains_require_primary_target: bool
    ignore_strength: bool


@dataclass
class Power:
    """Represents a Power record from MHD data."""

    # Basic info
    full_name: str
    group_name: str
    set_name: str
    power_name: str
    display_name: str
    available: int

    # Requirements
    requirement: Requirement

    # Power characteristics
    power_type: PowerType
    accuracy: float
    attack_types: int
    group_membership: list[str]
    entities_affected: int
    entities_auto_hit: int
    target: int
    target_line_special_range: bool
    range: float
    range_secondary: float

    # Costs and timing
    end_cost: float
    interrupt_time: float
    cast_time: float
    recharge_time: float
    base_recharge_time: float
    activate_period: float

    # Area effect
    effect_area: int
    radius: float
    arc: int
    max_targets: int

    # Boosts
    max_boosts: str  # Actually stored as string
    boosts_allowed: list[int]

    # Flags and AI
    cast_flags: int
    ai_report: int
    num_effects: int

    # More numeric fields
    usage_time: float
    life_time: float
    life_time_in_game: float
    num_charges: float
    num_activated: int
    def_value: float
    def_override: float

    # Descriptions and strings
    desc_short: str
    desc_long: str

    # Arrays
    set_types: list[int]
    uid_sub_power: list[str]
    ignore_strength: list[bool]
    ignore_buff: list[str]

    # More flags
    click_buff: int
    always_toggle: bool
    level: int
    allow_front_loading: bool
    ignore_enh: bool
    ignore_set_bonus: bool
    boost_boostable: bool
    boost_always: bool
    skip_max: bool
    display_location: int
    mutex_auto: bool
    mutex_ignore: bool
    absorb_summon_effects: bool
    absorb_summon_attributes: bool
    show_summon_anyway: bool
    never_auto_update: bool
    never_auto_update_requirements: bool
    include_flag: bool
    forced_class: str
    sort_override: int
    boost_boost_special_allowed: bool

    # Effects
    effects: list[Effect]

    # Final flag
    hidden_power: bool


def parse_requirement(stream: BinaryIO) -> Requirement:
    """Parse a Requirement structure from a binary stream.

    Args:
        stream: Binary stream positioned at the start of a Requirement

    Returns:
        Parsed Requirement object

    Raises:
        EOFError: If stream ends while reading
    """
    reader = BinaryReader(stream)

    try:
        # String fields
        class_name = reader.read_string()
        class_name_not = reader.read_string()

        # Classes arrays
        classes_required_count = reader.read_int32()
        classes_required = []
        for _ in range(classes_required_count):
            classes_required.append(reader.read_int32())

        classes_disallowed_count = reader.read_int32()
        classes_disallowed = []
        for _ in range(classes_disallowed_count):
            classes_disallowed.append(reader.read_int32())

        # Power ID arrays
        power_ids_count = reader.read_int32()
        power_ids = []
        for _ in range(power_ids_count):
            power_ids.append(reader.read_int32())

        power_ids_not_count = reader.read_int32()
        power_ids_not = []
        for _ in range(power_ids_not_count):
            power_ids_not.append(reader.read_int32())

        return Requirement(
            class_name=class_name,
            class_name_not=class_name_not,
            classes_required=classes_required,
            classes_disallowed=classes_disallowed,
            power_ids=power_ids,
            power_ids_not=power_ids_not
        )

    except EOFError as e:
        raise EOFError(f"Unexpected EOF while parsing Requirement: {str(e)}")


def parse_effect(stream: BinaryIO) -> Effect:
    """Parse an Effect structure from a binary stream.

    Args:
        stream: Binary stream positioned at the start of an Effect

    Returns:
        Parsed Effect object

    Raises:
        EOFError: If stream ends while reading
    """
    reader = BinaryReader(stream)

    try:
        # Basic fields
        power_full_name = reader.read_int32()
        effect_class = reader.read_int32()
        effect_type = reader.read_int32()
        damage_type = reader.read_int32()
        mez_type = reader.read_int32()
        et_modifies = reader.read_int32()
        summon = reader.read_string()

        # 15 float values
        scale = reader.read_float32()
        duration = reader.read_float32()
        magnitude = reader.read_float32()
        ticks = reader.read_float32()
        delay_time = reader.read_float32()
        tick_chance = reader.read_float32()
        percent_chance = reader.read_float32()
        attrib_mod = reader.read_float32()
        accuracy = reader.read_float32()
        radius = reader.read_float32()
        arc = reader.read_float32()
        range_val = reader.read_float32()
        range_secondary = reader.read_float32()
        endurance_cost = reader.read_float32()
        interval_time = reader.read_float32()

        # More fields
        display_percentage = reader.read_int32()
        probability = reader.read_float32()
        delay = reader.read_float32()
        stacking = reader.read_int32()

        # Suppression array
        suppression_count = reader.read_int32()
        suppression = []
        for _ in range(suppression_count):
            suppression.append(reader.read_bool())

        # Reward array
        reward_count = reader.read_int32()
        reward = []
        for _ in range(reward_count):
            reward.append(reader.read_string())

        # EffectId array
        effect_id_count = reader.read_int32()
        effect_ids = []
        for _ in range(effect_id_count):
            effect_ids.append(reader.read_string())

        # IgnoreED array
        ignore_ed_count = reader.read_int32()
        ignore_ed = []
        for _ in range(ignore_ed_count):
            ignore_ed.append(reader.read_int32())

        # IgnoreScale array
        ignore_scale_count = reader.read_int32()
        ignore_scale = []
        for _ in range(ignore_scale_count):
            ignore_scale.append(reader.read_int32())

        # Nested Requirement
        requirement = parse_requirement(stream)

        # Special fields
        special_case = reader.read_string()
        uid_class_name = reader.read_int32()
        n_id_class_name = reader.read_int32()

        # CancelEvents array
        cancel_events_count = reader.read_int32()
        cancel_events = []
        for _ in range(cancel_events_count):
            cancel_events.append(reader.read_int32())

        # More fields
        attrib_type = reader.read_int32()
        aspect = reader.read_int32()
        modifier_table = reader.read_string()
        n_modifier_table = reader.read_int32()
        power_full_name_enh = reader.read_string()
        buff_mode = reader.read_int32()

        # Override array
        override_count = reader.read_int32()
        override = []
        for _ in range(override_count):
            override.append(reader.read_string())

        # Final fields
        procs_per_minute = reader.read_int32()
        cancelable = reader.read_bool()
        ignore_toggle_drop = reader.read_bool()
        ignore_active_defense = reader.read_bool()

        # ChainID array
        chain_id_count = reader.read_int32()
        chain_ids = []
        for _ in range(chain_id_count):
            chain_ids.append(reader.read_int32())

        chains_require_primary_target = reader.read_bool()
        ignore_strength = reader.read_bool()

        return Effect(
            power_full_name=power_full_name,
            effect_class=effect_class,
            effect_type=effect_type,
            damage_type=damage_type,
            mez_type=mez_type,
            et_modifies=et_modifies,
            summon=summon,
            scale=scale,
            duration=duration,
            magnitude=magnitude,
            ticks=ticks,
            delay_time=delay_time,
            tick_chance=tick_chance,
            percent_chance=percent_chance,
            attrib_mod=attrib_mod,
            accuracy=accuracy,
            radius=radius,
            arc=arc,
            range=range_val,
            range_secondary=range_secondary,
            endurance_cost=endurance_cost,
            interval_time=interval_time,
            display_percentage=display_percentage,
            probability=probability,
            delay=delay,
            stacking=stacking,
            suppression=suppression,
            reward=reward,
            effect_ids=effect_ids,
            ignore_ed=ignore_ed,
            ignore_scale=ignore_scale,
            requirement=requirement,
            special_case=special_case,
            uid_class_name=uid_class_name,
            n_id_class_name=n_id_class_name,
            cancel_events=cancel_events,
            attrib_type=attrib_type,
            aspect=aspect,
            modifier_table=modifier_table,
            n_modifier_table=n_modifier_table,
            power_full_name_enh=power_full_name_enh,
            buff_mode=buff_mode,
            override=override,
            procs_per_minute=procs_per_minute,
            cancelable=cancelable,
            ignore_toggle_drop=ignore_toggle_drop,
            ignore_active_defense=ignore_active_defense,
            chain_ids=chain_ids,
            chains_require_primary_target=chains_require_primary_target,
            ignore_strength=ignore_strength
        )

    except EOFError as e:
        raise EOFError(f"Unexpected EOF while parsing Effect: {str(e)}")


def parse_power(stream: BinaryIO) -> Power:
    """Parse a Power record from a binary stream.

    Args:
        stream: Binary stream positioned at the start of a Power record

    Returns:
        Parsed Power object

    Raises:
        EOFError: If stream ends while reading
    """
    reader = BinaryReader(stream)

    try:
        # Basic info
        full_name = reader.read_string()
        group_name = reader.read_string()
        set_name = reader.read_string()
        power_name = reader.read_string()
        display_name = reader.read_string()
        available = reader.read_int32()

        # Requirements
        requirement = parse_requirement(stream)

        # Power characteristics
        power_type = PowerType(reader.read_int32())
        accuracy = reader.read_float32()
        attack_types = reader.read_int32()

        # GroupMembership array
        group_membership_count = reader.read_int32()
        group_membership = []
        for _ in range(group_membership_count):
            group_membership.append(reader.read_string())

        # Entity fields
        entities_affected = reader.read_int32()
        entities_auto_hit = reader.read_int32()
        target = reader.read_int32()
        target_line_special_range = reader.read_bool()
        range_val = reader.read_float32()
        range_secondary = reader.read_float32()

        # Costs and timing
        end_cost = reader.read_float32()
        interrupt_time = reader.read_float32()
        cast_time = reader.read_float32()
        recharge_time = reader.read_float32()
        base_recharge_time = reader.read_float32()
        activate_period = reader.read_float32()

        # Area effect
        effect_area = reader.read_int32()
        radius = reader.read_float32()
        arc = reader.read_int32()
        max_targets = reader.read_int32()

        # Boosts
        max_boosts = reader.read_string()
        cast_flags = reader.read_int32()
        ai_report = reader.read_int32()
        num_effects = reader.read_int32()

        # BoostsAllowed array
        boosts_allowed_count = reader.read_int32()
        boosts_allowed = []
        for _ in range(boosts_allowed_count):
            boosts_allowed.append(reader.read_int32())

        # More numeric fields
        usage_time = reader.read_float32()
        life_time = reader.read_float32()
        life_time_in_game = reader.read_float32()
        num_charges = reader.read_float32()
        num_activated = reader.read_int32()
        def_value = reader.read_float32()
        def_override = reader.read_float32()

        # Descriptions
        desc_short = reader.read_string()
        desc_long = reader.read_string()

        # SetTypes array
        set_types_count = reader.read_int32()
        set_types = []
        for _ in range(set_types_count):
            set_types.append(reader.read_int32())

        # More flags
        click_buff = reader.read_int32()
        always_toggle = reader.read_bool()
        level = reader.read_int32()
        allow_front_loading = reader.read_bool()
        ignore_enh = reader.read_bool()
        ignore_set_bonus = reader.read_bool()
        boost_boostable = reader.read_bool()
        boost_always = reader.read_bool()

        # UIDSubPower array
        uid_sub_power_count = reader.read_int32()
        uid_sub_power = []
        for _ in range(uid_sub_power_count):
            uid_sub_power.append(reader.read_string())

        # IgnoreStrength array
        ignore_strength_count = reader.read_int32()
        ignore_strength = []
        for _ in range(ignore_strength_count):
            ignore_strength.append(reader.read_bool())

        # IgnoreBuff array
        ignore_buff_count = reader.read_int32()
        ignore_buff = []
        for _ in range(ignore_buff_count):
            ignore_buff.append(reader.read_string())

        # Final flags
        skip_max = reader.read_bool()
        display_location = reader.read_int32()
        mutex_auto = reader.read_bool()
        mutex_ignore = reader.read_bool()
        absorb_summon_effects = reader.read_bool()
        absorb_summon_attributes = reader.read_bool()
        show_summon_anyway = reader.read_bool()
        never_auto_update = reader.read_bool()
        never_auto_update_requirements = reader.read_bool()
        include_flag = reader.read_bool()
        forced_class = reader.read_string()
        sort_override = reader.read_int32()
        boost_boost_special_allowed = reader.read_bool()

        # Effects array
        effects_count = reader.read_int32()
        effects = []
        for _ in range(effects_count):
            effects.append(parse_effect(stream))

        # Final field
        hidden_power = reader.read_bool()

        return Power(
            full_name=full_name,
            group_name=group_name,
            set_name=set_name,
            power_name=power_name,
            display_name=display_name,
            available=available,
            requirement=requirement,
            power_type=power_type,
            accuracy=accuracy,
            attack_types=attack_types,
            group_membership=group_membership,
            entities_affected=entities_affected,
            entities_auto_hit=entities_auto_hit,
            target=target,
            target_line_special_range=target_line_special_range,
            range=range_val,
            range_secondary=range_secondary,
            end_cost=end_cost,
            interrupt_time=interrupt_time,
            cast_time=cast_time,
            recharge_time=recharge_time,
            base_recharge_time=base_recharge_time,
            activate_period=activate_period,
            effect_area=effect_area,
            radius=radius,
            arc=arc,
            max_targets=max_targets,
            max_boosts=max_boosts,
            boosts_allowed=boosts_allowed,
            cast_flags=cast_flags,
            ai_report=ai_report,
            num_effects=num_effects,
            usage_time=usage_time,
            life_time=life_time,
            life_time_in_game=life_time_in_game,
            num_charges=num_charges,
            num_activated=num_activated,
            def_value=def_value,
            def_override=def_override,
            desc_short=desc_short,
            desc_long=desc_long,
            set_types=set_types,
            uid_sub_power=uid_sub_power,
            ignore_strength=ignore_strength,
            ignore_buff=ignore_buff,
            click_buff=click_buff,
            always_toggle=always_toggle,
            level=level,
            allow_front_loading=allow_front_loading,
            ignore_enh=ignore_enh,
            ignore_set_bonus=ignore_set_bonus,
            boost_boostable=boost_boostable,
            boost_always=boost_always,
            skip_max=skip_max,
            display_location=display_location,
            mutex_auto=mutex_auto,
            mutex_ignore=mutex_ignore,
            absorb_summon_effects=absorb_summon_effects,
            absorb_summon_attributes=absorb_summon_attributes,
            show_summon_anyway=show_summon_anyway,
            never_auto_update=never_auto_update,
            never_auto_update_requirements=never_auto_update_requirements,
            include_flag=include_flag,
            forced_class=forced_class,
            sort_override=sort_override,
            boost_boost_special_allowed=boost_boost_special_allowed,
            effects=effects,
            hidden_power=hidden_power
        )

    except EOFError as e:
        raise EOFError(f"Unexpected EOF while parsing Power: {str(e)}")
