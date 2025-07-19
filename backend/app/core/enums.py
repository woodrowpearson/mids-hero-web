"""Core enumerations for City of Heroes game mechanics.

This module contains Python equivalents of the C# enums from MidsReborn,
focusing on those needed for build calculations.
"""

from enum import Enum, IntEnum, auto


class Alignment(Enum):
    """Character alignment."""
    HERO = "Hero"
    ROGUE = "Rogue"
    VIGILANTE = "Vigilante"
    VILLAIN = "Villain"
    LOYALIST = "Loyalist"
    RESISTANCE = "Resistance"


class Archetype(Enum):
    """Character archetypes."""
    BLASTER = "Blaster"
    CONTROLLER = "Controller"
    DEFENDER = "Defender"
    SCRAPPER = "Scrapper"
    TANKER = "Tanker"
    BRUTE = "Brute"
    STALKER = "Stalker"
    MASTERMIND = "Mastermind"
    DOMINATOR = "Dominator"
    CORRUPTOR = "Corruptor"
    ARACHNOS_SOLDIER = "Arachnos Soldier"
    ARACHNOS_WIDOW = "Arachnos Widow"
    PEACEBRINGER = "Peacebringer"
    WARSHADE = "Warshade"
    SENTINEL = "Sentinel"


class DamageType(IntEnum):
    """Damage types in the game."""
    SMASHING = 0
    LETHAL = 1
    FIRE = 2
    COLD = 3
    ENERGY = 4
    NEGATIVE_ENERGY = 5
    TOXIC = 6
    PSIONIC = 7
    SPECIAL = 8
    UNIQUE = 9
    
    @classmethod
    def from_string(cls, value: str) -> "DamageType":
        """Convert string to DamageType."""
        mapping = {
            "smashing": cls.SMASHING,
            "lethal": cls.LETHAL,
            "fire": cls.FIRE,
            "cold": cls.COLD,
            "energy": cls.ENERGY,
            "negative": cls.NEGATIVE_ENERGY,
            "negative_energy": cls.NEGATIVE_ENERGY,
            "toxic": cls.TOXIC,
            "psionic": cls.PSIONIC,
            "special": cls.SPECIAL,
            "unique": cls.UNIQUE,
        }
        return mapping.get(value.lower(), cls.SPECIAL)


class DefenseType(IntEnum):
    """Defense types."""
    MELEE = 0
    RANGED = 1
    AOE = 2
    SMASHING = 3
    LETHAL = 4
    FIRE = 5
    COLD = 6
    ENERGY = 7
    NEGATIVE_ENERGY = 8
    PSIONIC = 9


class BuffMode(IntEnum):
    """Buff/debuff mode."""
    NORMAL = 0
    BUFF = 1
    DEBUFF = 2


class EffectType(IntEnum):
    """Types of effects."""
    NONE = -1
    DAMAGE = 0
    DEFENSE = 1
    RESISTANCE = 2
    ENDURANCE_DISCOUNT = 3
    RECHARGE = 4
    RECOVERY = 5
    REGENERATION = 6
    DAMAGE_BUFF = 7
    TOHIT = 8
    ACCURACY = 9
    HEAL = 10
    HITPOINTS = 11
    ABSORB = 12
    ENDURANCE_MAX = 13
    MEZDURATION = 14
    MEZRESIST = 15
    RANGE = 16
    RADIUS = 17
    KBDISTANCE = 18
    KBMAGNITUDE = 19
    FLY = 20
    RUN = 21
    JUMP = 22
    STEALTH = 23
    PERCEPTION = 24
    THREAT = 25
    TAUNT = 26
    PLACATE = 27
    CONFUSE = 28
    AFRAID = 29
    TERRORIZE = 30
    HOLD = 31
    IMMOBILIZE = 32
    KNOCKBACK = 33
    KNOCKUP = 34
    DISORIENT = 35
    SLEEP = 36
    SLOW_MOVEMENT = 37
    SLOW_RECHARGE = 38
    SLOW_FLYFLYSPEED = 39
    SLOW_JUMPSPEED = 40
    SLOW_RUNSPEED = 41
    GLOBAL_CHANCE_MOD = 42
    DEBT_PROTECTION = 43
    EXPERIENCE_GAIN = 44
    INFLUENCE_GAIN = 45
    PRESTIGE_GAIN = 46
    EVADE = 47
    KNOCKBACK_PROTECT = 48
    REPEL = 49
    TELEPORT = 50
    UNTOUCHABLE = 51
    ONLY_AFFECTS_SELF = 52
    XP_DEBT = 53
    POWER_REDIRECT = 54
    FUSION = 55
    NULL = 56
    NPC = 57
    GLOBAL_DAMAGE = 58
    DESIGN_MODE = 59
    CRITICAL_HIT = 60
    METER = 61
    ELUSIVITY = 62
    ELUSIVITY_BASE = 63
    ABSORB_DAMAGE = 64
    REWARD_SOURCE_TEAM_SIZE = 65
    REWARD_LEVEL = 66
    REWARD_INFLUENCE = 67
    REWARD_PRESTIGE = 68
    REWARD_ITEM = 69
    REWARD_SALVAGE = 70
    REWARD_RECIPE = 71
    REWARD_TEMP_POWER = 72
    REWARD_COSTUME_PART = 73
    REWARD_BEHAVIOR = 74
    REWARD_INSPIRATON = 75
    REWARD_XP = 76
    REWARD_DEBT_PROTECTION = 77
    REWARD_CURRENCY = 78
    REWARD_SKILL_POINT = 79
    REWARD_AUCTION_WIN = 80
    REWARD_RAID_POINTS = 81
    REWARD_REM_AUCTION_LOSE = 82
    REWARD_POP_HELP = 83
    REWARD_MERIT_POINT = 84
    REWARD_RANDOM_RECIPE_ROLL = 85
    REWARD_SET_TITLE = 86
    REWARD_PARAGON_REP = 87
    EXECUTE_POWER = 88
    SET_MODE = 89
    UNSET_MODE = 90
    GRANT_POWER = 91
    REVOKE_POWER = 92
    CLEAR_FOG = 93
    SET_COSTUME = 94
    SET_RAID_TARGET = 95
    EXPRESSION_TOK = 96
    TOKEN_ADD = 97
    EXPRESSION_EVAL = 98
    TOKEN_SET = 99
    TOKEN_CLEAR = 100
    TOKEN_CLEAR_ALL = 101
    DESIGNATE_CONTACT = 102
    CONTACT_INTRODUCE = 103
    CONTACT_COMPLETE = 104
    CONTACT_CALL = 105
    CONTACT_FLASH = 106
    CONTACT_UPDATE = 107
    CONTACT_CAPTURE = 108
    ADD_BEHAVIOR = 109
    SPAWN_NPC = 110
    DESTROY_NPC = 111
    NPC_SET_ATTITUDE = 112
    GLOWIE = 113
    IN_GAME_CUTSCENE = 114
    SET_SUPERGROUP_MODE = 115
    CLEAR_SUPERGROUP_MODE = 116
    COMBAT_PHASE = 117
    COMBAT_MOD_SHIFT = 118
    REWARD_VOUCHER = 119
    REWARD_ACCOUNT_PRODUCT = 120
    REWARD_TEMP_BEHAVIOR = 121
    REWARD_BADGE = 122
    REWARD_GLADIATOR = 123
    COSTUME_CHANGE = 124
    PLAYER_CREATE_PET = 125
    VISIONPHASE = 126
    OVERHEALTH = 127
    FXSCALE = 128
    SET_PLAYER_LOYALTY = 129
    FORCE_ALIGNMENT = 130
    FORCE_TEAM_ALIGNMENT = 131
    LOCKOUT = 132
    REDUCTION = 133
    DAMAGE_RESIST = 134
    POWER_CHANCE_MOD = 135
    MODIFIER_DURATION = 136
    POWER_DELAY = 137
    LIFESPAN = 138
    ADD_LEAGUE = 139
    CUE_INTERNAL_MUSIC = 140
    RAGE = 141
    MAXRUN = 142
    MAXJUMP = 143
    MAXFLY = 144
    MODB = 145
    UNKNOWN_146 = 146
    EFFECT_CHANCE_MOD = 147
    DEBT_PROTECTION_RESIST = 148
    TOKEN_INCREMENT = 149
    REWARD_PACK = 150
    GRANT_POWER_TEMP = 151
    COMBAT_LEVEL_BOUGHT = 152
    COMBAT_LEVEL_FORCE = 153
    COMBAT_SET_LEVEL = 154
    COMBAT_EFFECTIVE_LEVEL = 155
    PRAETORIAN_PROGRESS = 156
    REWARD_PROGRESS_TOKEN = 157
    REFRESH_POWER_TRAY = 158
    LOCK_COSTUME = 159
    UNLOCK_COSTUME = 160
    DISABLE_TEMP_COSTUME = 161
    CHAIN = 162
    SILENT_KILL = 163
    XP_GAIN_DISABLE = 164
    SOU_LINK = 165
    EXEMPLAR_INF_DEBT = 166
    STEALTH_RADIUS_PLAYER = 167
    REWARD_ACCOUNT_INVENTORY = 168
    REWARD_BOOST = 169
    REWARD_TOKEN_QUEST = 170
    UNKNOWN_171 = 171
    HEAL_RESIST = 172
    SPECIAL_173 = 173  # Special damage?
    VIEWATTRIB = 174
    REWARD_POWER_CREDIT = 175
    REWARD_MORALITY_MISSION = 176
    TELEPORT_CAPTURE = 177
    FLY_PROTECTION = 178
    DAMAGE_TAKEN_PENALTY = 179
    ONLYATSOURCE = 180
    REWARD_TITLE = 181
    TAUNT_RESIST = 182
    PLACATE_RESIST = 183
    XP_NERF = 184
    KILL_TARGET = 185
    METERLOCK = 186
    VMETER = 187
    VANISH = 188
    FORWARD_POWER = 189
    AFTERBURNER = 190
    BOOST_UP = 191
    BOOST_MAX = 192
    POWER_RADIUS = 193
    STEALTH_RADIUS = 194
    STEALTH_RADIUS_PVE = 195
    PERCEPTION_RADIUS = 196
    PERCEPTION_RADIUS_PVE = 197
    PERCEPTION_RADIUS_PLAYER = 198
    REGENERATION_RESIST = 199
    RECOVERY_RESIST = 200
    PETCOMMANDKILL = 201
    REWARD_INCARNATE_SLOT = 202
    NPC_CREATE_PET = 203
    NPC_CLEARTARGET = 204
    REFRESH_TOHIT = 205
    
    @classmethod
    def get_name(cls, value: int) -> str:
        """Get the name of an effect type by its value."""
        try:
            return cls(value).name
        except ValueError:
            return f"UNKNOWN_{value}"


class EnhancementType(Enum):
    """Enhancement types."""
    TO = "Training Origin"
    DO = "Dual Origin"
    SO = "Single Origin"
    IO = "Invention Origin"
    SET_IO = "Set IO"
    HAMIO = "Hamidon Origin"
    SPECIAL = "Special"
    
    @property
    def grade_modifier(self) -> float:
        """Get the base effectiveness modifier for this enhancement type."""
        modifiers = {
            self.TO: 0.08333,  # 8.33%
            self.DO: 0.16666,  # 16.66%
            self.SO: 0.33333,  # 33.33%
            self.IO: 0.0,  # Variable based on level
            self.SET_IO: 0.0,  # Variable based on specific enhancement
            self.HAMIO: 0.50,  # 50%
            self.SPECIAL: 0.0,  # Variable
        }
        return modifiers.get(self, 0.0)


class PowerType(IntEnum):
    """Power types."""
    CLICK = 0
    AUTO = 1
    TOGGLE = 2
    BOOST = 3
    INSPIRATION = 4
    
    
class TargetType(IntEnum):
    """Target types for powers."""
    NONE = 0
    SELF = 1
    PLAYER = 2
    TEAMMATE = 3
    FOE = 4
    LOCATION = 5
    ANY = 6
    TELEPORT = 7
    DEAD_ALLY = 8
    DEAD_FOE = 9
    DEAD_PLAYER = 10
    DEAD_OR_ALIVE_FOE = 11
    DEAD_TEAMMATE = 12
    ITEM = 13
    NONTALK_NPC = 14
    TALK_NPC = 15
    BOSS = 16
    MISSION_OBJECTIVE = 17
    ANY_ANGLE = 18
    OWNED = 19
    DEAD_VILLAIN = 20
    DEAD_OR_ALIVE_VILLAIN = 21
    LEAGUEMATE = 22
    DEAD_OR_ALIVE_LEAGUEMATE = 23
    DEAD_LEAGUEMATE = 24
    PET = 25
    DEAD_OR_ALIVE_PET = 26
    DEAD_PET = 27
    TEAMMATE_NOT_SELF = 28
    DEAD_OR_ALIVE_TEAMMATE = 29
    DEAD_CRITTER = 30
    DEAD_OR_ALIVE_CRITTER = 31


class SlotPlacement(IntEnum):
    """Enhancement slot numbers."""
    SLOT_1 = 0
    SLOT_2 = 1
    SLOT_3 = 2
    SLOT_4 = 3
    SLOT_5 = 4
    SLOT_6 = 5


class Origin(Enum):
    """Character origins."""
    SCIENCE = "Science"
    MUTATION = "Mutation"
    MAGIC = "Magic"
    TECHNOLOGY = "Technology"
    NATURAL = "Natural"