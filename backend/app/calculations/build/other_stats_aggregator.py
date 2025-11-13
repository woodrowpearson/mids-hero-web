"""
Build Totals - Other Stats Calculator

Aggregates HP, endurance, movement, perception, stealth, and threat stats
for a character build with exact MidsReborn parity.

Maps to MidsReborn's clsToonX.cs lines 763-881 (GenerateBuildBuffs and CalcStatTotals).

File: backend/app/calculations/build/other_stats_aggregator.py
"""

from dataclasses import dataclass
from typing import Dict, Optional, Tuple
from enum import Enum


class StatType(Enum):
    """Stat types for effect aggregation"""
    HP_MAX = "hp_max"
    HP_REGEN = "hp_regen"
    ABSORB = "absorb"
    END_MAX = "end_max"
    END_RECOVERY = "end_recovery"
    RUN_SPEED = "run_speed"
    MAX_RUN_SPEED = "max_run_speed"
    JUMP_SPEED = "jump_speed"
    MAX_JUMP_SPEED = "max_jump_speed"
    JUMP_HEIGHT = "jump_height"
    FLY_SPEED = "fly_speed"
    MAX_FLY_SPEED = "max_fly_speed"
    PERCEPTION = "perception"
    STEALTH_PVE = "stealth_pve"
    STEALTH_PVP = "stealth_pvp"
    THREAT_LEVEL = "threat_level"
    RANGE = "range"
    TO_HIT = "to_hit"


@dataclass
class ArchetypeData:
    """Archetype base values and caps"""
    name: str
    hitpoints: int  # Base HP at level 50
    hp_cap: float  # Max HP cap
    base_regen: float  # Base regen multiplier (usually 1.0)
    regen_cap: float  # Max regen total (e.g., 20.0 = 2000%)
    base_recovery: float  # Base recovery multiplier (usually 1.67)
    recovery_cap: float  # Max recovery total (e.g., 5.0 = 500%)
    perception_cap: float  # Max perception distance (usually 1153 ft)
    base_threat: float  # Base threat multiplier (Tanker = 4.0, most = 1.0)


@dataclass
class ServerData:
    """Server constants for movement speeds"""
    base_run_speed: float = 21.0
    max_run_speed: float = 58.65
    max_max_run_speed: float = 166.257
    base_jump_speed: float = 22.275
    max_jump_speed: float = 114.4
    max_max_jump_speed: float = 176.358
    base_jump_height: float = 4.0
    max_jump_height: float = 200.0
    base_fly_speed: float = 31.5
    max_fly_speed: float = 58.65
    max_max_fly_speed: float = 257.985
    base_perception: float = 500.0
    magic_constant: float = 1.666667  # Regen/recovery conversion


@dataclass
class OtherStatsTotals:
    """Aggregated other stats for a build"""
    # HP
    hp_max: float
    hp_percent_of_base: float
    hp_regen_buff: float
    hp_regen_per_sec: float
    hp_regen_percent: float
    absorb: float

    # Endurance
    end_max: float
    end_recovery_buff: float
    end_recovery_per_sec: float
    end_recovery_percent: float

    # Movement
    run_speed: float
    run_speed_soft_cap: float
    jump_speed: float
    jump_speed_soft_cap: float
    jump_height: float
    fly_speed: float
    fly_speed_soft_cap: float
    can_fly: bool

    # Perception / Stealth / Threat
    perception: float
    stealth_pve: float
    stealth_pvp: float
    threat_level: float

    # Other buffs
    buff_range: float
    buff_tohit: float


class BuildOtherStatsCalculator:
    """
    Calculates build totals for HP, endurance, movement, and other stats.

    Implements exact MidsReborn calculation logic from clsToonX.cs lines 763-881.
    """

    # Movement speed floor (can't reduce below 10% of base)
    SPEED_FLOOR: float = -0.9

    def __init__(
        self,
        archetype: ArchetypeData,
        server_data: ServerData = None
    ):
        """
        Initialize calculator with archetype and server data.

        Args:
            archetype: Archetype base values and caps
            server_data: Server constants (uses defaults if not provided)
        """
        self.archetype = archetype
        self.server_data = server_data or ServerData()

        # Internal totals (uncapped and capped)
        self.totals: Dict[str, float] = {}
        self.totals_capped: Dict[str, float] = {}

    def calculate_all(
        self,
        effects: Dict[StatType, float],
        can_fly: bool = False
    ) -> Tuple[OtherStatsTotals, OtherStatsTotals]:
        """
        Calculate all other stats from aggregated effects.

        Args:
            effects: Aggregated effect values by stat type
            can_fly: Whether character has an active fly power

        Returns:
            Tuple of (uncapped totals, capped totals)
        """
        # Calculate in dependency order
        self._calculate_hp(effects)
        self._calculate_endurance(effects)
        self._calculate_movement(effects, can_fly)
        self._calculate_perception_stealth_threat(effects)
        self._calculate_other_buffs(effects)

        # Apply caps
        self._apply_caps()

        # Build result objects
        uncapped = self._build_totals_object(capped=False)
        capped = self._build_totals_object(capped=True)

        return uncapped, capped

    def _calculate_hp(self, effects: Dict[StatType, float]) -> None:
        """
        Calculate HP max, regen, and absorb.

        From clsToonX.cs line 817:
        Totals.HPMax = _selfBuffs.Effect[(int)Enums.eStatType.HPMax] + Archetype.Hitpoints
        """
        # HP Max
        hp_bonuses = effects.get(StatType.HP_MAX, 0.0)
        self.totals['hp_max'] = self.archetype.hitpoints + hp_bonuses

        # HP Regen (stored as multiplier, not including base)
        # From line 772: Totals.HPRegen = _selfBuffs.Effect[(int)Enums.eStatType.HPRegen]
        self.totals['hp_regen'] = effects.get(StatType.HP_REGEN, 0.0)

        # Absorb
        # From line 774: Totals.Absorb = _selfBuffs.Effect[(int)Enums.eStatType.Absorb]
        # Note: Percentage-based absorb is handled in effect aggregation
        self.totals['absorb'] = effects.get(StatType.ABSORB, 0.0)

    def _calculate_endurance(self, effects: Dict[StatType, float]) -> None:
        """
        Calculate endurance max and recovery.

        From clsToonX.cs line 763:
        Totals.EndMax = _selfBuffs.MaxEnd
        """
        # End Max (bonuses only, base 100 added in display)
        # From line 763: Totals.EndMax = _selfBuffs.MaxEnd
        self.totals['end_max'] = effects.get(StatType.END_MAX, 0.0)

        # End Recovery (stored as multiplier, not including base)
        # From line 773: Totals.EndRec = _selfBuffs.Effect[(int)Enums.eStatType.EndRec]
        self.totals['end_recovery'] = effects.get(StatType.END_RECOVERY, 0.0)

    def _calculate_movement(
        self,
        effects: Dict[StatType, float],
        can_fly: bool
    ) -> None:
        """
        Calculate movement speeds with soft/hard cap system.

        From clsToonX.cs lines 777-791:
        Implements three-tier cap system (base → soft → hard)
        """
        # Run Speed
        self._calculate_speed(
            effects,
            StatType.RUN_SPEED,
            StatType.MAX_RUN_SPEED,
            self.server_data.base_run_speed,
            self.server_data.max_run_speed,
            self.server_data.max_max_run_speed,
            'run'
        )

        # Jump Speed
        self._calculate_speed(
            effects,
            StatType.JUMP_SPEED,
            StatType.MAX_JUMP_SPEED,
            self.server_data.base_jump_speed,
            self.server_data.max_jump_speed,
            self.server_data.max_max_jump_speed,
            'jump'
        )

        # Jump Height (simpler system, no soft cap)
        # From line 780: Totals.JumpHeight = (1 + Math.Max(_selfBuffs..., -0.9f)) * Statistics.BaseJumpHeight
        jump_height_buff = max(effects.get(StatType.JUMP_HEIGHT, 0.0), self.SPEED_FLOOR)
        self.totals['jump_height'] = (1.0 + jump_height_buff) * self.server_data.base_jump_height

        # Fly Speed (can be disabled)
        if can_fly:
            self._calculate_speed(
                effects,
                StatType.FLY_SPEED,
                StatType.MAX_FLY_SPEED,
                self.server_data.base_fly_speed,
                self.server_data.max_fly_speed,
                self.server_data.max_max_fly_speed,
                'fly'
            )
        else:
            # From line 819-820: if (!canFly) Totals.FlySpd = 0
            self.totals['fly_speed'] = 0.0
            self.totals['max_fly_speed'] = 0.0

    def _calculate_speed(
        self,
        effects: Dict[StatType, float],
        speed_stat: StatType,
        max_speed_stat: StatType,
        base_speed: float,
        default_soft_cap: float,
        hard_cap: float,
        prefix: str
    ) -> None:
        """
        Generic speed calculation with soft/hard caps.

        From clsToonX.cs lines 777-790:
        1. Calculate buffed speed with floor
        2. Calculate soft cap (can be increased by buffs)
        3. Apply hard cap to both speed and soft cap

        Args:
            effects: Aggregated effects
            speed_stat: Speed buff stat type
            max_speed_stat: Max speed (soft cap increase) stat type
            base_speed: Base speed constant
            default_soft_cap: Default soft cap value
            hard_cap: Absolute maximum (MaxMax)
            prefix: Stat name prefix for storage
        """
        # From line 777-779: Buffed speed with floor
        # Totals.RunSpd = (1 + Math.Max(_selfBuffs.Effect[...], -0.9f)) * Statistics.BaseRunSpeed
        speed_buff = max(effects.get(speed_stat, 0.0), self.SPEED_FLOOR)
        speed = (1.0 + speed_buff) * base_speed

        # From line 782-784: Soft cap calculation
        # Totals.MaxRunSpd = Statistics.MaxRunSpeed + _selfBuffs.Effect[...] * Statistics.BaseRunSpeed
        max_speed_buff = effects.get(max_speed_stat, 0.0)
        soft_cap = default_soft_cap + (max_speed_buff * base_speed)

        # From line 787-790: Apply hard cap (MaxMax)
        # Totals.FlySpd = Math.Min(Totals.FlySpd, DatabaseAPI.ServerData.MaxMaxFlySpeed)
        speed = min(speed, hard_cap)
        soft_cap = min(soft_cap, hard_cap)

        # Store results
        self.totals[f'{prefix}_speed'] = speed
        self.totals[f'max_{prefix}_speed'] = soft_cap

    def _calculate_perception_stealth_threat(
        self,
        effects: Dict[StatType, float]
    ) -> None:
        """
        Calculate perception, stealth, and threat level.

        From clsToonX.cs lines 768-771:
        Perception is multiplicative, stealth/threat are additive
        """
        # Perception (multiplicative)
        # From line 768: Totals.Perception = Statistics.BasePerception * (1 + _selfBuffs.Effect[...])
        perception_buff = effects.get(StatType.PERCEPTION, 0.0)
        self.totals['perception'] = self.server_data.base_perception * (1.0 + perception_buff)

        # Stealth (additive, separate PvE/PvP)
        # From lines 769-770: Totals.StealthPvE = _selfBuffs.Effect[...]
        self.totals['stealth_pve'] = effects.get(StatType.STEALTH_PVE, 0.0)
        self.totals['stealth_pvp'] = effects.get(StatType.STEALTH_PVP, 0.0)

        # Threat Level (additive)
        # From line 771: Totals.ThreatLevel = _selfBuffs.Effect[...]
        self.totals['threat'] = effects.get(StatType.THREAT_LEVEL, 0.0)

    def _calculate_other_buffs(self, effects: Dict[StatType, float]) -> None:
        """
        Calculate range and tohit buffs.

        From clsToonX.cs lines 775, 767
        """
        # From line 775: Totals.BuffRange = _selfBuffs.Effect[(int)Enums.eStatType.Range]
        self.totals['buff_range'] = effects.get(StatType.RANGE, 0.0)

        # From line 767: Totals.BuffToHit = _selfBuffs.Effect[(int)Enums.eStatType.ToHit]
        self.totals['buff_tohit'] = effects.get(StatType.TO_HIT, 0.0)

    def _apply_caps(self) -> None:
        """
        Apply archetype-specific caps to stats.

        From clsToonX.cs lines 861-881:
        Copy uncapped to capped, then apply caps selectively
        """
        # From line 861: TotalsCapped.Assign(Totals) - Copy all uncapped values
        self.totals_capped = self.totals.copy()

        # From line 864: TotalsCapped.HPRegen = Math.Min(TotalsCapped.HPRegen, Archetype.RegenCap - 1)
        # Subtract 1 because cap includes base 100%
        self.totals_capped['hp_regen'] = min(
            self.totals_capped['hp_regen'],
            self.archetype.regen_cap - 1.0
        )

        # From line 865: TotalsCapped.EndRec = Math.Min(TotalsCapped.EndRec, Archetype.RecoveryCap - 1)
        self.totals_capped['end_recovery'] = min(
            self.totals_capped['end_recovery'],
            self.archetype.recovery_cap - 1.0
        )

        # From line 871-875: HP cap and absorb cap
        if self.archetype.hp_cap > 0:
            self.totals_capped['hp_max'] = min(
                self.totals_capped['hp_max'],
                self.archetype.hp_cap
            )
            # Absorb is capped at capped max HP
            self.totals_capped['absorb'] = min(
                self.totals_capped['absorb'],
                self.totals_capped['hp_max']
            )

        # From line 877-879: Movement speed soft caps
        # TotalsCapped.RunSpd = Math.Min(TotalsCapped.RunSpd, Totals.MaxRunSpd)
        self.totals_capped['run_speed'] = min(
            self.totals_capped['run_speed'],
            self.totals['max_run_speed']
        )
        self.totals_capped['jump_speed'] = min(
            self.totals_capped['jump_speed'],
            self.totals['max_jump_speed']
        )

        if 'fly_speed' in self.totals:
            self.totals_capped['fly_speed'] = min(
                self.totals_capped['fly_speed'],
                self.totals['max_fly_speed']
            )

        # From line 880: TotalsCapped.JumpHeight = Math.Min(..., DatabaseAPI.ServerData.MaxJumpHeight)
        self.totals_capped['jump_height'] = min(
            self.totals_capped['jump_height'],
            self.server_data.max_jump_height
        )

        # From line 881: TotalsCapped.Perception = Math.Min(..., Archetype.PerceptionCap)
        self.totals_capped['perception'] = min(
            self.totals_capped['perception'],
            self.archetype.perception_cap
        )

    def _build_totals_object(self, capped: bool) -> OtherStatsTotals:
        """
        Build OtherStatsTotals object from internal totals.

        Args:
            capped: Whether to use capped or uncapped values

        Returns:
            OtherStatsTotals dataclass with formatted values
        """
        source = self.totals_capped if capped else self.totals

        # Calculate derived values
        hp_max = source['hp_max']
        hp_percent = (hp_max / self.archetype.hitpoints) * 100.0

        # HP Regen per sec
        # From Statistics.cs line 53:
        # HealthRegenHealthPerSec => HealthRegen(false) * Archetype.BaseRegen * 1.666667
        hp_regen_mult = source['hp_regen'] + 1.0
        hp_regen_per_sec = (
            hp_regen_mult *
            self.archetype.base_regen *
            self.server_data.magic_constant
        )
        hp_regen_percent = hp_regen_mult * 100.0

        # End Recovery per sec
        # From Statistics.cs line 37:
        # EnduranceRecoveryNumeric => EnduranceRecovery(false) * (Archetype.BaseRecovery * BaseMagic) * (TotalsCapped.EndMax / 100 + 1)
        end_recovery_mult = source['end_recovery'] + 1.0
        end_max_mult = (source['end_max'] / 100.0) + 1.0
        end_recovery_per_sec = (
            end_recovery_mult *
            self.archetype.base_recovery *
            self.server_data.magic_constant *
            end_max_mult
        )
        end_recovery_percent = end_recovery_mult * 100.0

        # End Max display (includes base 100)
        # From Statistics.cs line 35: EnduranceMaxEnd => _character.Totals.EndMax + 100f
        end_max_display = source['end_max'] + 100.0

        return OtherStatsTotals(
            # HP
            hp_max=hp_max,
            hp_percent_of_base=hp_percent,
            hp_regen_buff=source['hp_regen'],
            hp_regen_per_sec=hp_regen_per_sec,
            hp_regen_percent=hp_regen_percent,
            absorb=source['absorb'],

            # Endurance
            end_max=end_max_display,
            end_recovery_buff=source['end_recovery'],
            end_recovery_per_sec=end_recovery_per_sec,
            end_recovery_percent=end_recovery_percent,

            # Movement
            run_speed=source['run_speed'],
            run_speed_soft_cap=source['max_run_speed'],
            jump_speed=source['jump_speed'],
            jump_speed_soft_cap=source['max_jump_speed'],
            jump_height=source['jump_height'],
            fly_speed=source.get('fly_speed', 0.0),
            fly_speed_soft_cap=source.get('max_fly_speed', 0.0),
            can_fly=source.get('fly_speed', 0.0) > 0,

            # Perception / Stealth / Threat
            perception=source['perception'],
            stealth_pve=source['stealth_pve'],
            stealth_pvp=source['stealth_pvp'],
            threat_level=source['threat'],

            # Other buffs
            buff_range=source['buff_range'],
            buff_tohit=source['buff_tohit']
        )

    def format_for_display(
        self,
        uncapped: OtherStatsTotals,
        capped: OtherStatsTotals
    ) -> Dict[str, any]:
        """
        Format totals for UI display with user-friendly strings.

        Args:
            uncapped: Uncapped totals
            capped: Capped totals

        Returns:
            Dict with formatted display values
        """
        return {
            'hp': {
                'max': round(capped.hp_max, 0),
                'max_uncapped': round(uncapped.hp_max, 0),
                'percent': f"{round(capped.hp_percent_of_base, 1)}%",
                'regen_per_sec': round(capped.hp_regen_per_sec, 2),
                'regen_per_sec_uncapped': round(uncapped.hp_regen_per_sec, 2),
                'regen_percent': f"{round(capped.hp_regen_percent, 1)}%",
                'absorb': round(capped.absorb, 0),
                'is_capped': capped.hp_max < uncapped.hp_max,
                'regen_is_capped': capped.hp_regen_buff < uncapped.hp_regen_buff
            },
            'endurance': {
                'max': round(capped.end_max, 1),
                'recovery_per_sec': round(capped.end_recovery_per_sec, 2),
                'recovery_per_sec_uncapped': round(uncapped.end_recovery_per_sec, 2),
                'recovery_percent': f"{round(capped.end_recovery_percent, 1)}%",
                'is_capped': capped.end_recovery_buff < uncapped.end_recovery_buff
            },
            'movement': {
                'run_speed': f"{round(capped.run_speed, 2)} ft/sec",
                'run_speed_cap': f"{round(capped.run_speed_soft_cap, 2)} ft/sec",
                'run_at_cap': capped.run_speed >= capped.run_speed_soft_cap,
                'jump_speed': f"{round(capped.jump_speed, 2)} ft/sec",
                'jump_speed_cap': f"{round(capped.jump_speed_soft_cap, 2)} ft/sec",
                'jump_at_cap': capped.jump_speed >= capped.jump_speed_soft_cap,
                'jump_height': f"{round(capped.jump_height, 2)} ft",
                'fly_speed': f"{round(capped.fly_speed, 2)} ft/sec" if capped.can_fly else "No Fly Power",
                'fly_speed_cap': f"{round(capped.fly_speed_soft_cap, 2)} ft/sec" if capped.can_fly else "N/A",
                'fly_at_cap': capped.fly_speed >= capped.fly_speed_soft_cap if capped.can_fly else False
            },
            'perception': {
                'value': f"{round(capped.perception, 0)} ft",
                'value_uncapped': f"{round(uncapped.perception, 0)} ft",
                'is_capped': capped.perception < uncapped.perception
            },
            'stealth': {
                'pve': f"{round(capped.stealth_pve, 1)} ft",
                'pvp': f"{round(capped.stealth_pvp, 1)} ft"
            },
            'threat': {
                'level': f"{round(capped.threat_level, 2)}x"
            },
            'other': {
                'range_increase': f"{round(capped.buff_range * 100, 2)}%",
                'tohit_buff': f"{round(capped.buff_tohit * 100, 2)}%"
            }
        }
