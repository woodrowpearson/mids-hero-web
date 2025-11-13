"""
Healing and Absorption Calculator

Calculates instant healing, regeneration rate, and temporary absorption HP from powers.

Based on MidsReborn's Statistics.cs and clsToonX.cs implementation.
"""

import math
from dataclasses import dataclass

# ============================================================================
# CONSTANTS (from MidsReborn)
# ============================================================================

BASE_MAGIC: float = 1.666667  # Statistics.cs line 22
DEFAULT_HP_CAP: float = 5000.0  # Archetype.cs line 44
DEFAULT_REGEN_CAP: float = 20.0  # 2000%
DEFAULT_BASE_REGEN: float = 1.0  # Most ATs


# ============================================================================
# DATA CLASSES
# ============================================================================


@dataclass
class ArchetypeHealthStats:
    """
    Archetype health properties.

    Maps to Archetype.cs properties:
    - Hitpoints (base HP at level 50)
    - HPCap (maximum HP limit)
    - BaseRegen (regeneration multiplier)
    - RegenCap (maximum regeneration percentage)
    """

    base_hitpoints: float
    hp_cap: float
    base_regen: float = DEFAULT_BASE_REGEN
    regen_cap: float = DEFAULT_REGEN_CAP

    def __post_init__(self):
        """Validate properties"""
        if self.base_hitpoints <= 0:
            raise ValueError(
                f"base_hitpoints must be positive, got {self.base_hitpoints}"
            )
        if self.hp_cap < self.base_hitpoints:
            raise ValueError(
                f"hp_cap ({self.hp_cap}) must be >= base_hitpoints ({self.base_hitpoints})"
            )
        if self.base_regen <= 0:
            raise ValueError(f"base_regen must be positive, got {self.base_regen}")
        if self.regen_cap <= 0:
            raise ValueError(f"regen_cap must be positive, got {self.regen_cap}")


@dataclass
class HealEffect:
    """
    Instant heal effect (eEffectType.Heal).

    Maps to MidsReborn Effect with EffectType = Heal (13).
    """

    magnitude: float  # Percentage of max HP
    buffed_magnitude: float | None = None  # After enhancements
    duration: float = 0.0  # 0 = instant
    tick_interval: float | None = None  # For HoT effects
    probability: float = 1.0  # 1.0 = always
    display_percentage: bool = True

    def get_effective_magnitude(self) -> float:
        """Return buffed magnitude if available, else base magnitude"""
        return (
            self.buffed_magnitude
            if self.buffed_magnitude is not None
            else self.magnitude
        )

    def __post_init__(self):
        """Validate properties"""
        if self.magnitude < 0:
            raise ValueError(f"magnitude cannot be negative, got {self.magnitude}")
        if not (0 <= self.probability <= 1):
            raise ValueError(f"probability must be 0-1, got {self.probability}")
        if self.duration < 0:
            raise ValueError(f"duration cannot be negative, got {self.duration}")


@dataclass
class HitPointsEffect:
    """
    Maximum HP modifier effect (eEffectType.HitPoints/HPMax).

    Maps to MidsReborn Effect with EffectType = HPMax (14).
    """

    magnitude: float  # Flat HP or percentage
    buffed_magnitude: float | None = None
    display_percentage: bool = False  # True if percentage-based
    duration: float = 0.0
    source_type: str | None = None  # 'power', 'accolade', 'set_bonus'

    def get_effective_magnitude(self) -> float:
        """Return buffed magnitude if available, else base magnitude"""
        return (
            self.buffed_magnitude
            if self.buffed_magnitude is not None
            else self.magnitude
        )


@dataclass
class RegenerationEffect:
    """
    Regeneration rate modifier effect (eEffectType.Regeneration).

    Maps to MidsReborn Effect with EffectType = Regeneration (27).
    Magnitude is percentage modifier (0.75 = +75% regen).
    """

    magnitude: float  # Percentage modifier
    buffed_magnitude: float | None = None
    duration: float = 0.0
    resistible: bool = True

    def get_effective_magnitude(self) -> float:
        """Return buffed magnitude if available, else base magnitude"""
        return (
            self.buffed_magnitude
            if self.buffed_magnitude is not None
            else self.magnitude
        )


@dataclass
class AbsorbEffect:
    """
    Absorption shield effect (eEffectType.Absorb).

    Maps to MidsReborn Effect with EffectType = Absorb (66).
    Creates temporary HP buffer that takes damage before real HP.
    """

    magnitude: float  # Flat HP or percentage
    display_percentage: bool = False
    duration: float = 0.0  # 0 = permanent until depleted
    stacks_with_self: bool = False  # Usually false
    priority: int = 0

    def __post_init__(self):
        """Validate properties"""
        if self.magnitude < 0:
            raise ValueError(f"magnitude cannot be negative, got {self.magnitude}")
        if self.duration < 0:
            raise ValueError(f"duration cannot be negative, got {self.duration}")


# ============================================================================
# HEALING CALCULATOR
# ============================================================================


class HealingCalculator:
    """
    Calculate healing, regeneration, and absorption effects.

    Maps to MidsReborn's healing calculation logic from:
    - Statistics.cs (regen formulas)
    - clsToonX.cs (HP and absorption totals)
    - Effect.cs (effect handling)
    """

    def calculate_instant_heal(
        self,
        heal_effects: list[HealEffect],
        max_hp: float,
        current_hp: float,
    ) -> dict[str, float]:
        """
        Calculate instant HP restoration from Heal effects.

        Formula from MidsReborn:
            HealAmount = (Sum(HealMagnitude) / 100.0) * MaxHP

        Args:
            heal_effects: List of Heal effects from power
            max_hp: Character's current maximum HP (after +MaxHP buffs)
            current_hp: Current HP before heal

        Returns:
            Dictionary with heal_magnitude_pct, heal_amount, new_hp, overheal

        Raises:
            ValueError: If max_hp or current_hp are invalid
        """
        if max_hp <= 0:
            raise ValueError(f"max_hp must be positive, got {max_hp}")
        if current_hp < 0:
            raise ValueError(f"current_hp cannot be negative, got {current_hp}")
        if current_hp > max_hp:
            raise ValueError(
                f"current_hp ({current_hp}) cannot exceed max_hp ({max_hp})"
            )

        # Sum all heal magnitudes
        total_heal_pct = 0.0
        for effect in heal_effects:
            mag = effect.get_effective_magnitude()

            # Apply probability for proc heals
            if effect.probability < 1.0:
                mag *= effect.probability

            total_heal_pct += mag

        # Convert percentage to HP value
        heal_amount = (total_heal_pct / 100.0) * max_hp

        # Apply to current HP
        new_hp = current_hp + heal_amount

        # Cap at max HP
        if new_hp > max_hp:
            overheal = new_hp - max_hp
            new_hp = max_hp
        else:
            overheal = 0.0

        return {
            "heal_magnitude_pct": total_heal_pct,
            "heal_amount": heal_amount,
            "new_hp": new_hp,
            "overheal": overheal,
        }

    def calculate_max_hp(
        self,
        at_stats: ArchetypeHealthStats,
        hp_effects: list[HitPointsEffect],
    ) -> dict[str, float]:
        """
        Calculate maximum HP from HitPoints effects.

        Formula from clsToonX.cs line 817:
            Totals.HPMax = _selfBuffs.Effect[HPMax] + Archetype.Hitpoints

        Cap from clsToonX.cs line 873:
            TotalsCapped.HPMax = Math.Min(TotalsCapped.HPMax, Archetype.HPCap)

        Args:
            at_stats: Archetype health statistics
            hp_effects: List of HitPoints effects

        Returns:
            Dictionary with base_hp, hp_bonus, uncapped_hp, capped_hp, over_cap
        """
        # Start with archetype base HP
        base_hp = at_stats.base_hitpoints

        # Sum all HP bonuses
        hp_bonus = 0.0
        for effect in hp_effects:
            mag = effect.get_effective_magnitude()

            # Convert percentage to flat value if needed
            if effect.display_percentage:
                mag = (mag / 100.0) * base_hp

            hp_bonus += mag

        # Calculate uncapped total
        uncapped_hp = base_hp + hp_bonus

        # Apply archetype cap
        if at_stats.hp_cap > 0:
            capped_hp = min(uncapped_hp, at_stats.hp_cap)
            over_cap = uncapped_hp - capped_hp if uncapped_hp > capped_hp else 0.0
        else:
            capped_hp = uncapped_hp
            over_cap = 0.0

        return {
            "base_hp": base_hp,
            "hp_bonus": hp_bonus,
            "uncapped_hp": uncapped_hp,
            "capped_hp": capped_hp,
            "over_cap": over_cap,
        }

    def calculate_regeneration(
        self,
        at_stats: ArchetypeHealthStats,
        regen_effects: list[RegenerationEffect],
        max_hp: float,
    ) -> dict[str, float]:
        """
        Calculate regeneration rate.

        Formulas from Statistics.cs lines 53-57:
            HealthRegenHealthPerSec = HealthRegen * BaseRegen * 1.66666662693024
            HealthRegenHPPerSec = HealthRegenHealthPerSec * HealthHitpointsNumeric / 100.0
            HealthRegenTimeToFull = HealthHitpointsNumeric / HealthRegenHPPerSec

        BASE_MAGIC constant (1.666667) converts regen to %/sec.

        Args:
            at_stats: Archetype health statistics (includes BaseRegen)
            regen_effects: List of Regeneration effects
            max_hp: Character's current maximum HP

        Returns:
            Dictionary with regen_total, regen_percent_per_sec, hp_per_sec,
            time_to_full, hp_per_tick

        Raises:
            ValueError: If max_hp is invalid
        """
        if max_hp <= 0:
            raise ValueError(f"max_hp must be positive, got {max_hp}")

        # Start at 100% base regeneration
        regen_total = 1.0

        # Add all regeneration modifiers
        for effect in regen_effects:
            mag = effect.get_effective_magnitude()
            regen_total += mag

        # Calculate % per second
        regen_percent_per_sec = regen_total * at_stats.base_regen * BASE_MAGIC

        # Calculate HP per second
        hp_per_sec = (regen_percent_per_sec * max_hp) / 100.0

        # Calculate time to full HP
        if hp_per_sec > 0:
            time_to_full = max_hp / hp_per_sec
        else:
            time_to_full = float("inf")

        # Calculate HP per 4-second tick
        hp_per_tick = hp_per_sec * 4.0

        return {
            "regen_total": regen_total,
            "regen_percent_per_sec": regen_percent_per_sec,
            "hp_per_sec": hp_per_sec,
            "time_to_full": time_to_full,
            "hp_per_tick": hp_per_tick,
        }

    def calculate_absorption(
        self,
        absorb_effects: list[AbsorbEffect],
        max_hp: float,
        base_hp: float,
    ) -> dict[str, float]:
        """
        Calculate absorption (temporary HP).

        From clsToonX.cs lines 688-691:
            if (effect.DisplayPercentage)
                shortFx.Value *= MidsContext.Character.Totals.HPMax

        From clsToonX.cs line 874:
            TotalsCapped.Absorb = Math.Min(TotalsCapped.Absorb, TotalsCapped.HPMax)

        Absorption rules:
        1. Typically does NOT stack - highest value wins
        2. Capped at current max HP
        3. Takes damage before real HP

        Args:
            absorb_effects: List of Absorb effects
            max_hp: Character's current maximum HP (capped)
            base_hp: Archetype base HP (for percentage display)

        Returns:
            Dictionary with absorb_amount, absorb_percent_base,
            absorb_percent_max, capped

        Raises:
            ValueError: If max_hp or base_hp are invalid
        """
        if max_hp <= 0:
            raise ValueError(f"max_hp must be positive, got {max_hp}")
        if base_hp <= 0:
            raise ValueError(f"base_hp must be positive, got {base_hp}")

        # Process all absorption effects
        absorb_values = []
        for effect in absorb_effects:
            mag = effect.magnitude

            # Convert percentage to flat value if needed
            # Uses current max HP, not base HP (clsToonX.cs line 690)
            if effect.display_percentage:
                mag = (mag / 100.0) * max_hp

            absorb_values.append(mag)

        # Apply stacking rule - take highest value
        if len(absorb_values) > 0:
            absorb_amount = max(absorb_values)
        else:
            absorb_amount = 0.0

        # Cap at max HP (clsToonX.cs line 874)
        capped = False
        if absorb_amount > max_hp:
            absorb_amount = max_hp
            capped = True

        # Calculate percentages for display
        absorb_percent_base = (absorb_amount / base_hp * 100.0) if base_hp > 0 else 0.0
        absorb_percent_max = (absorb_amount / max_hp * 100.0) if max_hp > 0 else 0.0

        return {
            "absorb_amount": absorb_amount,
            "absorb_percent_base": absorb_percent_base,
            "absorb_percent_max": absorb_percent_max,
            "capped": capped,
        }

    def calculate_heal_over_time(
        self,
        heal_effect: HealEffect,
        max_hp: float,
    ) -> dict[str, float]:
        """
        Calculate Heal over Time (HoT) effects.

        Some powers deliver heals via ticks over duration.

        Args:
            heal_effect: Heal effect with duration and tick_interval
            max_hp: Maximum HP

        Returns:
            Dictionary with heal_per_tick, num_ticks, total_heal, heal_per_sec

        Raises:
            ValueError: If heal_effect.duration is 0 or tick_interval is None
        """
        if heal_effect.duration == 0:
            raise ValueError("Heal effect must have duration > 0 for HoT calculation")
        if heal_effect.tick_interval is None or heal_effect.tick_interval <= 0:
            raise ValueError(
                "Heal effect must have valid tick_interval for HoT calculation"
            )

        # Calculate number of ticks
        num_ticks = int(heal_effect.duration / heal_effect.tick_interval)

        # Total heal magnitude over all ticks
        total_heal_pct = heal_effect.get_effective_magnitude()
        total_heal = (total_heal_pct / 100.0) * max_hp

        # Divide by number of ticks
        heal_per_tick = total_heal / num_ticks if num_ticks > 0 else total_heal

        # Calculate heal per second
        heal_per_sec = total_heal / heal_effect.duration

        return {
            "heal_per_tick": heal_per_tick,
            "num_ticks": num_ticks,
            "total_heal": total_heal,
            "heal_per_sec": heal_per_sec,
        }

    def apply_regen_debuff(
        self,
        current_regen: float,
        debuff_magnitude: float,
        debuff_resistance: float = 0.0,
    ) -> dict[str, float]:
        """
        Apply regeneration debuff with resistance.

        Args:
            current_regen: Current regen multiplier
            debuff_magnitude: Debuff strength (negative value)
            debuff_resistance: Resistance to regen debuffs (0.0 to 1.0)

        Returns:
            Dictionary with resisted_debuff, new_regen, is_negative
        """
        # Validate debuff_resistance
        if not (0 <= debuff_resistance <= 1):
            raise ValueError(f"debuff_resistance must be 0-1, got {debuff_resistance}")

        # Apply debuff resistance
        resisted_debuff = debuff_magnitude * (1.0 - debuff_resistance)

        # Apply to current regen
        new_regen = current_regen + resisted_debuff  # Debuff is negative

        # Check if negative
        is_negative = new_regen < 0

        return {
            "resisted_debuff": resisted_debuff,
            "new_regen": new_regen,
            "is_negative": is_negative,
        }

    def format_heal_display(self, heal_amount: float, base_hp: float) -> str:
        """
        Format heal for display matching MidsReborn style.

        Format: "{HP} HP ({%} of base HP)"

        Args:
            heal_amount: HP healed
            base_hp: Archetype base HP

        Returns:
            Formatted string
        """
        percent_of_base = (heal_amount / base_hp * 100.0) if base_hp > 0 else 0.0
        return f"{heal_amount:.2f} HP ({percent_of_base:.2f}% of base HP)"

    def format_regen_display(self, hp_per_sec: float, time_to_full: float) -> str:
        """
        Format regeneration for display.

        Format: "{HP/sec} HP/sec (Full in {time}s)"

        Args:
            hp_per_sec: HP regenerated per second
            time_to_full: Seconds to full HP

        Returns:
            Formatted string
        """
        if math.isinf(time_to_full):
            return f"{hp_per_sec:.2f} HP/sec (No regeneration)"
        else:
            return f"{hp_per_sec:.2f} HP/sec (Full in {time_to_full:.1f}s)"

    def format_absorption_display(self, absorb_amount: float, base_hp: float) -> str:
        """
        Format absorption for display matching MidsReborn style.

        Format: "{HP} HP ({%} of base HP)"

        Args:
            absorb_amount: Absorption HP
            base_hp: Archetype base HP

        Returns:
            Formatted string
        """
        percent_of_base = (absorb_amount / base_hp * 100.0) if base_hp > 0 else 0.0
        return f"{absorb_amount:.2f} HP ({percent_of_base:.2f}% of base HP)"
