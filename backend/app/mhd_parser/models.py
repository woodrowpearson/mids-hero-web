"""Data models for MHD file parsing."""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

from .binary_reader import BinaryReader


@dataclass
class MHDArchetype:
    """Archetype data from MHD file."""
    idx: int = 0
    display_name: str = ""
    hitpoints: int = 0
    hp_cap: float = 0.0
    desc_long: str = ""
    desc_short: str = ""
    res_cap: float = 0.0
    origins: List[str] = field(default_factory=list)
    class_name: str = ""
    class_type: int = 0  # Enum value
    column: int = 0
    primary_group: str = ""
    secondary_group: str = ""
    playable: bool = True
    recharge_cap: float = 0.0
    damage_cap: float = 0.0
    recovery_cap: float = 0.0
    regen_cap: float = 0.0
    base_recovery: float = 0.0
    base_regen: float = 0.0
    base_threat: float = 0.0
    perception_cap: float = 0.0
    
    @classmethod
    def from_reader(cls, reader: BinaryReader, idx: int) -> 'MHDArchetype':
        """Create an Archetype from a BinaryReader."""
        arch = cls()
        arch.idx = idx
        arch.display_name = reader.read_string()
        arch.hitpoints = reader.read_int32()
        arch.hp_cap = reader.read_float()
        arch.desc_long = reader.read_string()
        arch.res_cap = reader.read_float()
        
        origin_count = reader.read_int32()
        arch.origins = []
        for i in range(origin_count + 1):
            arch.origins.append(reader.read_string())
        
        arch.class_name = reader.read_string()
        arch.class_type = reader.read_int32()
        arch.column = reader.read_int32()
        arch.desc_short = reader.read_string()
        arch.primary_group = reader.read_string()
        arch.secondary_group = reader.read_string()
        arch.playable = reader.read_boolean()
        arch.recharge_cap = reader.read_float()
        arch.damage_cap = reader.read_float()
        arch.recovery_cap = reader.read_float()
        arch.regen_cap = reader.read_float()
        arch.base_recovery = reader.read_float()
        arch.base_regen = reader.read_float()
        arch.base_threat = reader.read_float()
        arch.perception_cap = reader.read_float()
        
        return arch


@dataclass
class MHDPowerset:
    """Powerset data from MHD file."""
    nid: int = 0
    display_name: str = ""
    archetype_id: int = 0
    set_type: int = 0  # Enum value
    image_name: str = ""
    full_name: str = ""
    set_name: str = ""
    description: str = ""
    sub_name: str = ""
    at_class: str = ""
    uid_trunk_set: str = ""
    uid_link_secondary: str = ""
    uid_mutex_sets: List[str] = field(default_factory=list)
    nid_mutex_sets: List[int] = field(default_factory=list)
    
    @classmethod
    def from_reader(cls, reader: BinaryReader, nid: int) -> 'MHDPowerset':
        """Create a Powerset from a BinaryReader."""
        ps = cls()
        ps.nid = nid
        ps.display_name = reader.read_string()
        ps.archetype_id = reader.read_int32()
        ps.set_type = reader.read_int32()
        ps.image_name = reader.read_string()
        ps.full_name = reader.read_string()
        
        if not ps.full_name:
            ps.full_name = f"Orphan.{ps.display_name.replace(' ', '_')}"
        
        ps.set_name = reader.read_string()
        ps.description = reader.read_string()
        ps.sub_name = reader.read_string()
        ps.at_class = reader.read_string()
        ps.uid_trunk_set = reader.read_string()
        ps.uid_link_secondary = reader.read_string()
        
        mutex_count = reader.read_int32()
        ps.uid_mutex_sets = []
        ps.nid_mutex_sets = []
        for i in range(mutex_count + 1):
            ps.uid_mutex_sets.append(reader.read_string())
            ps.nid_mutex_sets.append(reader.read_int32())
        
        return ps


@dataclass
class MHDPower:
    """Simplified Power data from MHD file."""
    static_index: int = 0
    full_name: str = ""
    group_name: str = ""
    set_name: str = ""
    power_name: str = ""
    display_name: str = ""
    available: int = 0
    power_type: int = 0  # Enum value
    accuracy: float = 0.0
    end_cost: float = 0.0
    cast_time: float = 0.0
    recharge_time: float = 0.0
    range: float = 0.0
    desc_short: str = ""
    desc_long: str = ""
    # Many more fields exist but these are the essential ones
    
    @classmethod
    def from_reader(cls, reader: BinaryReader) -> 'MHDPower':
        """Create a simplified Power from a BinaryReader."""
        power = cls()
        power.static_index = reader.read_int32()
        power.full_name = reader.read_string()
        power.group_name = reader.read_string()
        power.set_name = reader.read_string()
        power.power_name = reader.read_string()
        power.display_name = reader.read_string()
        power.available = reader.read_int32()
        
        # Skip Requirement reading for now - it's complex
        # In real implementation, we'd read the Requirement object here
        skip_requirement(reader)
        
        # Read remaining fields
        reader.read_int32()  # modes_required
        reader.read_int32()  # modes_disallowed
        power.power_type = reader.read_int32()
        power.accuracy = reader.read_float()
        reader.read_int32()  # accuracy_mult (skip)
        reader.read_int32()  # attack_types
        
        # Skip group membership array
        group_count = reader.read_int32()
        for i in range(group_count + 1):
            reader.read_string()
        
        # Skip entity fields
        reader.read_int32()  # entities_affected
        reader.read_int32()  # entities_auto_hit
        reader.read_int32()  # target
        reader.read_boolean()  # target_los
        power.range = reader.read_float()
        reader.read_int32()  # target_secondary
        reader.read_float()  # range_secondary
        
        power.end_cost = reader.read_float()
        reader.read_float()  # interrupt_time
        power.cast_time = reader.read_float()
        power.recharge_time = reader.read_float()
        reader.read_float()  # base_recharge_time
        reader.read_float()  # activate_period
        reader.read_int32()  # effect_area
        reader.read_float()  # radius
        reader.read_int32()  # arc
        reader.read_int32()  # max_targets
        reader.read_string()  # max_boosts
        reader.read_int32()  # cast_flags
        reader.read_int32()  # ai_report
        reader.read_int32()  # num_charges
        reader.read_int32()  # usage_time
        reader.read_int32()  # life_time
        reader.read_int32()  # life_time_in_game
        reader.read_int32()  # num_allowed
        reader.read_boolean()  # do_not_save
        
        # Skip boosts allowed array
        boost_count = reader.read_int32()
        for i in range(boost_count + 1):
            reader.read_string()
        
        reader.read_boolean()  # cast_through_hold
        reader.read_boolean()  # ignore_strength
        power.desc_short = reader.read_string()
        power.desc_long = reader.read_string()
        
        # Skip the rest of the complex fields for now
        # In a real implementation, we'd continue reading all fields
        
        return power


def skip_requirement(reader: BinaryReader):
    """Skip reading a Requirement object."""
    # Requirements have complex nested structure
    # For now, we'll skip the bytes
    # In real implementation, this would parse the requirement
    class_count = reader.read_int32()
    for i in range(class_count + 1):
        reader.read_string()
    
    class_count2 = reader.read_int32()
    for i in range(class_count2 + 1):
        reader.read_string()
    
    powerset_count = reader.read_int32()
    for i in range(powerset_count + 1):
        reader.read_string()
    
    powerset_count2 = reader.read_int32()
    for i in range(powerset_count2 + 1):
        reader.read_string()
    
    power_count = reader.read_int32()
    for i in range(power_count + 1):
        power_count2 = reader.read_int32()
        for j in range(power_count2 + 1):
            reader.read_string()
    
    power_count3 = reader.read_int32()
    for i in range(power_count3 + 1):
        power_count4 = reader.read_int32()
        for j in range(power_count4 + 1):
            reader.read_string()


@dataclass
class MHDEnhancement:
    """Enhancement data from MHD file."""
    static_index: int = 0
    name: str = ""
    short_name: str = ""
    desc: str = ""
    type_id: int = 0
    sub_type_id: int = 0
    class_ids: List[int] = field(default_factory=list)
    image: str = ""
    set_id: int = 0
    uid_set: str = ""
    effect_chance: float = 0.0
    level_min: int = 0
    level_max: int = 0
    unique: bool = False
    uid: str = ""
    recipe_name: str = ""
    superior: bool = False
    
    @classmethod
    def from_reader(cls, reader: BinaryReader) -> 'MHDEnhancement':
        """Create an Enhancement from a BinaryReader."""
        enh = cls()
        enh.static_index = reader.read_int32()
        enh.name = reader.read_string()
        enh.short_name = reader.read_string()
        enh.desc = reader.read_string()
        enh.type_id = reader.read_int32()
        enh.sub_type_id = reader.read_int32()
        
        class_count = reader.read_int32()
        enh.class_ids = []
        for i in range(class_count + 1):
            enh.class_ids.append(reader.read_int32())
        
        enh.image = reader.read_string()
        enh.set_id = reader.read_int32()
        enh.uid_set = reader.read_string()
        enh.effect_chance = reader.read_float()
        enh.level_min = reader.read_int32()
        enh.level_max = reader.read_int32()
        enh.unique = reader.read_boolean()
        reader.read_int32()  # mutex_id
        reader.read_int32()  # buff_mode
        
        # Skip effect array for now
        effect_count = reader.read_int32()
        for i in range(effect_count + 1):
            reader.read_int32()  # mode
            reader.read_int32()  # buff_mode
            reader.read_int32()  # enhance_id
            reader.read_int32()  # enhance_sub_id
            reader.read_int32()  # schedule
            reader.read_float()  # multiplier
            has_fx = reader.read_boolean()
            if has_fx:
                # Skip reading the effect - it's complex
                pass
        
        enh.uid = reader.read_string()
        enh.recipe_name = reader.read_string()
        enh.superior = reader.read_boolean()
        reader.read_boolean()  # is_proc
        reader.read_boolean()  # is_scalable
        
        return enh


@dataclass
class MHDDatabase:
    """Complete MHD database structure."""
    version: str = ""
    date: Optional[datetime] = None
    issue: int = 0
    page_vol: int = 0
    page_vol_text: str = ""
    archetypes: List[MHDArchetype] = field(default_factory=list)
    powersets: List[MHDPowerset] = field(default_factory=list)
    powers: List[MHDPower] = field(default_factory=list)
    enhancements: List[MHDEnhancement] = field(default_factory=list)