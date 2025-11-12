"""
Effect Types - All 85 effect types from MidsReborn

Maps to MidsReborn's eEffectType enumeration in Core/Enums.cs lines 1847-1933.
"""

from enum import Enum


class EffectType(Enum):
    """
    Complete enumeration of all 85 effect types.

    Maps to MidsReborn's Enums.eEffectType enum.
    Values match C# enum ordinals for compatibility.
    """
    NONE = 0
    ACCURACY = 1
    VIEW_ATTRIB = 2
    DAMAGE = 3
    DAMAGE_BUFF = 4
    DEFENSE = 5
    DROP_TOGGLES = 6
    ENDURANCE = 7
    ENDURANCE_DISCOUNT = 8
    ENHANCEMENT = 9
    FLY = 10
    SPEED_FLYING = 11
    GRANT_POWER = 12
    HEAL = 13
    HIT_POINTS = 14
    INTERRUPT_TIME = 15
    JUMP_HEIGHT = 16
    SPEED_JUMPING = 17
    METER = 18
    MEZ = 19
    MEZ_RESIST = 20
    MOVEMENT_CONTROL = 21
    MOVEMENT_FRICTION = 22
    PERCEPTION_RADIUS = 23
    RANGE = 24
    RECHARGE_TIME = 25
    RECOVERY = 26
    REGENERATION = 27
    RES_EFFECT = 28
    RESISTANCE = 29
    REVOKE_POWER = 30
    REWARD = 31
    SPEED_RUNNING = 32
    SET_COSTUME = 33
    SET_MODE = 34
    SLOW = 35
    STEALTH_RADIUS = 36
    STEALTH_RADIUS_PLAYER = 37
    ENT_CREATE = 38
    THREAT_LEVEL = 39
    TO_HIT = 40
    TRANSLUCENCY = 41
    XP_DEBT_PROTECTION = 42
    SILENT_KILL = 43
    ELUSIVITY = 44
    GLOBAL_CHANCE_MOD = 45
    LEVEL_SHIFT = 46
    UNSET_MODE = 47
    RAGE = 48
    MAX_RUN_SPEED = 49
    MAX_JUMP_SPEED = 50
    MAX_FLY_SPEED = 51
    DESIGNER_STATUS = 52
    POWER_REDIRECT = 53
    TOKEN_ADD = 54
    EXPERIENCE_GAIN = 55
    INFLUENCE_GAIN = 56
    PRESTIGE_GAIN = 57
    ADD_BEHAVIOR = 58
    RECHARGE_POWER = 59
    REWARD_SOURCE_TEAM = 60
    VISION_PHASE = 61
    COMBAT_PHASE = 62
    CLEAR_FOG = 63
    SET_SZE_VALUE = 64
    EXCLUSIVE_VISION_PHASE = 65
    ABSORB = 66
    X_AFRAID = 67
    X_AVOID = 68
    BEAST_RUN = 69
    CLEAR_DAMAGERS = 70
    ENT_CREATE_X = 71
    GLIDE = 72
    HOVERBOARD = 73
    JUMPPACK = 74
    MAGIC_CARPET = 75
    NINJA_RUN = 76
    NULL = 77
    NULL_BOOL = 78
    STEALTH = 79
    STEAM_JUMP = 80
    WALK = 81
    XP_DEBT = 82
    FORCE_MOVE = 83
    MODIFY_ATTRIB = 84
    EXECUTE_POWER = 85


class DamageType(Enum):
    """
    Damage type aspects.

    Maps to MidsReborn's Enums.eDamage enum.
    """
    NONE = 0
    SMASHING = 1
    LETHAL = 2
    FIRE = 3
    COLD = 4
    ENERGY = 5
    NEGATIVE = 6
    TOXIC = 7
    PSIONIC = 8


class MezType(Enum):
    """
    Mez/control type aspects.

    Maps to MidsReborn's Enums.eMez enum.
    """
    NONE = 0
    HOLD = 1
    STUN = 2
    SLEEP = 3
    IMMOBILIZE = 4
    CONFUSE = 5
    FEAR = 6
    TAUNT = 7
    PLACATE = 8
    KNOCKBACK = 9
    KNOCKUP = 10
    REPEL = 11
