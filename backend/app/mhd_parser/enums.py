"""Enumerations used in MHD files.

These match the enums used in the MidsReborn C# codebase.
"""

from enum import IntEnum


class ClassType(IntEnum):
    """Character archetype class types."""
    
    NONE = 0
    BLASTER = 1
    CONTROLLER = 2
    DEFENDER = 3
    SCRAPPER = 4
    TANKER = 5
    BRUTE = 6
    STALKER = 7
    MASTERMIND = 8
    DOMINATOR = 9
    KHELDIAN = 10
    VEAT = 11
    CORRUPTOR = 12
    SENTINEL = 13


class PowerType(IntEnum):
    """Power activation types."""
    
    CLICK = 0
    AUTO = 1
    TOGGLE = 2
    BOOST = 3
    INSPIRATION = 4
    INHERENT = 5
    TEMPORARY = 6
    GLOBAL_BOOST = 7


class SetType(IntEnum):
    """Enhancement set types."""
    
    NONE = 0
    MELEE_DAMAGE = 1
    RANGED_DAMAGE = 2
    TARGETED_AOE_DAMAGE = 3
    PBAOE_DAMAGE = 4
    SNIPER_ATTACKS = 5
    PET_DAMAGE = 6
    DEFENSE = 7
    RESIST_DAMAGE = 8
    HEALING = 9
    HOLDS = 10
    STUNS = 11
    IMMOBILIZE = 12
    SLOW_MOVEMENT = 13
    SLEEP = 14
    FEAR = 15
    CONFUSE = 16
    FLIGHT = 17
    LEAP = 18
    RUN = 19
    TELEPORT = 20
    DEFENSE_DEBUFF = 21
    ENDURANCE_MODIFICATION = 22
    ENDURANCE_REDUCTION = 23
    TAUNT = 24
    TOHIT_BUFF = 25
    TOHIT_DEBUFF = 26
    KNOCKBACK = 27
    UNIVERSAL_DAMAGE = 28
    ARCHETYPE_ORIGIN = 29
    UNIVERSAL_TRAVEL = 30
    ACCURATE_DEFENSE_DEBUFF = 31
    ACCURATE_HEALING = 32
    ACCURATE_TOHIT_DEBUFF = 33
    RECHARGE_INTENSIVE_PETS = 34
    ENHANCEMENT_CONVERTERS = 35
    WINTER = 36
    SUPERIOR_ATO = 37


class EnhancementType(IntEnum):
    """Enhancement types."""
    
    NONE = 0
    NORMAL = 1
    INVENTION = 2
    SPECIAL_ORIGIN = 3
    SET_IO = 4
    HAMIDON = 5


class BuffDebuff(IntEnum):
    """Buff/Debuff mode."""
    
    BUFF = 0
    DEBUFF = 1
    ANY = 2


class Aspect(IntEnum):
    """Power aspect types."""
    
    STR = 0  # Strength/Accuracy
    RES = 1  # Resistance/Damage
    SCH = 2  # Schedule
    MAX = 3  # Maximum enhancement
    ACC = 4  # Accuracy
    DAM = 5  # Damage
    END_MOD = 6  # Endurance modification
    END_RDUX = 7  # Endurance reduction
    RCHG = 8  # Recharge
    HOLD = 9  # Hold duration
    INTRDX = 10  # Interrupt reduction
    RNG = 11  # Range
    DEFENSE = 12  # Defense
    HEAL = 13  # Healing
    STUN = 14  # Stun duration
    SLOW = 15  # Movement slow
    FLY = 16  # Flight speed
    JUMP = 17  # Jump height/speed
    SPD = 18  # Run speed
    IMMOB = 19  # Immobilize duration
    SLEEP = 20  # Sleep duration
    KNOCK = 21  # Knockback
    TOHIT_BUFF = 22  # To-hit buff
    TOHIT_DEBUFF = 23  # To-hit debuff
    FEAR = 24  # Fear duration
    CONFUSE = 25  # Confuse duration
    TAUNT = 26  # Taunt duration
    PLACATE = 27  # Placate duration
    THREAT = 28  # Threat level
    DEFENSE_DEBUFF = 29  # Defense debuff
    
    
class VectorType(IntEnum):
    """Power vector/targeting types."""
    
    NONE = 0
    SELF = 1
    MELEE = 2
    RANGED = 3
    RANGED_CONE = 4
    RANGED_AOE = 5
    AURA = 6
    MELEE_CONE = 7
    CHAIN = 8
    SUMMON = 9
    LOCATION = 10
    TELEPORT = 11