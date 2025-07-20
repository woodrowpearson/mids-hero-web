"""Buff and debuff calculation module.

This module handles all buff and debuff calculations including:
- Buff aggregation from multiple sources
- Debuff resistance application
- Cap enforcement
- Stacking rules
"""

import logging

from app.config.constants import (
    ARCHETYPE_CAPS,
    BUFF_CAPS,
    DEBUFF_RESISTANCE_CAPS,
)

logger = logging.getLogger(__name__)


class BuffCalculator:
    """Handles buff and debuff calculations for character builds."""

    def __init__(self, archetype: str):
        """Initialize with archetype-specific data.
        
        Args:
            archetype: Character archetype name
        """
        self.archetype = archetype
        self.archetype_data = ARCHETYPE_CAPS.get(archetype, {})

    def aggregate_buffs(
        self,
        buff_sources: list[dict[str, float]],
        buff_type: str,
        include_debuffs: bool = True
    ) -> float:
        """Aggregate buffs from multiple sources.
        
        Args:
            buff_sources: List of buff dictionaries from various sources
            buff_type: Type of buff to aggregate (e.g., "damage", "defense_melee")
            include_debuffs: Whether to include negative (debuff) values
            
        Returns:
            Total buff value after aggregation
        """
        total = 0.0

        for source in buff_sources:
            value = source.get(buff_type, 0.0)

            # Skip negative values if not including debuffs
            if not include_debuffs and value < 0:
                continue

            total += value

        logger.debug(f"Aggregated {buff_type}: {total}% from {len(buff_sources)} sources")
        return total

    def apply_debuff_resistance(
        self,
        debuff_value: float,
        resistance_type: str,
        resistance_sources: list[dict[str, float]]
    ) -> float:
        """Apply debuff resistance to reduce debuff effectiveness.
        
        Args:
            debuff_value: Original debuff value (negative)
            resistance_type: Type of debuff resistance
            resistance_sources: Sources of debuff resistance
            
        Returns:
            Modified debuff value after resistance
        """
        if debuff_value >= 0:
            return debuff_value

        # Calculate total resistance
        total_resistance = self.aggregate_buffs(
            resistance_sources,
            f"{resistance_type}_resistance",
            include_debuffs=False
        )

        # Cap resistance at 100%
        total_resistance = min(total_resistance, DEBUFF_RESISTANCE_CAPS.get(resistance_type, 100.0))

        # Apply resistance (reduces debuff by resistance percentage)
        # e.g., -50% debuff with 40% resistance = -30% debuff
        resistance_factor = 1.0 - (total_resistance / 100.0)
        modified_debuff = debuff_value * resistance_factor

        logger.debug(
            f"Applied {resistance_type} resistance: {debuff_value}% -> {modified_debuff}% "
            f"(resistance: {total_resistance}%)"
        )

        return modified_debuff

    def calculate_offensive_buffs(
        self,
        buff_sources: list[dict[str, float]],
        debuff_resistance_sources: list[dict[str, float]] | None = None
    ) -> dict[str, float]:
        """Calculate offensive buff totals.
        
        Args:
            buff_sources: All buff sources
            debuff_resistance_sources: Sources of debuff resistance
            
        Returns:
            Dictionary of offensive buff types to total values
        """
        if debuff_resistance_sources is None:
            debuff_resistance_sources = []

        results = {}

        # Damage buffs (separate by type)
        for damage_type in ["melee", "ranged", "aoe", "all"]:
            buff_key = f"damage_{damage_type}" if damage_type != "all" else "damage"

            # Aggregate positive buffs
            positive_buffs = self.aggregate_buffs(
                buff_sources, buff_key, include_debuffs=False
            )

            # Aggregate negative buffs (debuffs)
            all_buffs = self.aggregate_buffs(buff_sources, buff_key, include_debuffs=True)
            debuffs = all_buffs - positive_buffs

            # Apply damage debuff resistance if applicable
            if debuffs < 0 and debuff_resistance_sources:
                debuffs = self.apply_debuff_resistance(
                    debuffs, "damage", debuff_resistance_sources
                )

            # Apply archetype damage cap to positive portion only
            damage_cap = self.archetype_data.get("damage_cap", 4.0) * 100  # Convert to percentage
            capped_positive = min(positive_buffs, damage_cap)

            # Combine capped positive buffs with resisted debuffs
            results[buff_key] = capped_positive + debuffs

        # ToHit buffs (not affected by damage cap)
        tohit_buffs = self.aggregate_buffs(buff_sources, "tohit", include_debuffs=False)
        tohit_all = self.aggregate_buffs(buff_sources, "tohit", include_debuffs=True)
        tohit_debuffs = tohit_all - tohit_buffs

        if tohit_debuffs < 0 and debuff_resistance_sources:
            tohit_debuffs = self.apply_debuff_resistance(
                tohit_debuffs, "tohit", debuff_resistance_sources
            )

        # ToHit has its own caps
        tohit_buffs = min(tohit_buffs, BUFF_CAPS.get("tohit", 200.0))
        results["tohit"] = tohit_buffs + tohit_debuffs

        # Accuracy buffs (multiplicative, handled differently)
        accuracy_buffs = self.aggregate_buffs(buff_sources, "accuracy", include_debuffs=False)
        accuracy_all = self.aggregate_buffs(buff_sources, "accuracy", include_debuffs=True)
        accuracy_debuffs = accuracy_all - accuracy_buffs

        if accuracy_debuffs < 0 and debuff_resistance_sources:
            accuracy_debuffs = self.apply_debuff_resistance(
                accuracy_debuffs, "accuracy", debuff_resistance_sources
            )

        # Accuracy cap
        accuracy_buffs = min(accuracy_buffs, BUFF_CAPS.get("accuracy", 200.0))
        results["accuracy"] = accuracy_buffs + accuracy_debuffs

        return results

    def calculate_defensive_buffs(
        self,
        buff_sources: list[dict[str, float]],
        debuff_resistance_sources: list[dict[str, float]] | None = None
    ) -> dict[str, float]:
        """Calculate defensive buff totals.
        
        Args:
            buff_sources: All buff sources
            debuff_resistance_sources: Sources of debuff resistance
            
        Returns:
            Dictionary of defensive buff types to total values
        """
        if debuff_resistance_sources is None:
            debuff_resistance_sources = []

        results = {}

        # Max HP buffs
        hp_buffs = self.aggregate_buffs(buff_sources, "hp", include_debuffs=False)
        hp_all = self.aggregate_buffs(buff_sources, "hp", include_debuffs=True)
        hp_debuffs = hp_all - hp_buffs

        if hp_debuffs < 0 and debuff_resistance_sources:
            hp_debuffs = self.apply_debuff_resistance(
                hp_debuffs, "hp", debuff_resistance_sources
            )

        # HP buffs capped at archetype maximum
        hp_cap = BUFF_CAPS.get("hp", 200.0)  # Usually +100% to +200%
        hp_buffs = min(hp_buffs, hp_cap)
        results["hp"] = hp_buffs + hp_debuffs

        # Regeneration buffs
        regen_buffs = self.aggregate_buffs(buff_sources, "regeneration", include_debuffs=False)
        regen_all = self.aggregate_buffs(buff_sources, "regeneration", include_debuffs=True)
        regen_debuffs = regen_all - regen_buffs

        if regen_debuffs < 0 and debuff_resistance_sources:
            regen_debuffs = self.apply_debuff_resistance(
                regen_debuffs, "regeneration", debuff_resistance_sources
            )

        # Regen cap
        regen_cap = BUFF_CAPS.get("regeneration", 2000.0)  # Very high cap
        regen_buffs = min(regen_buffs, regen_cap)
        results["regeneration"] = regen_buffs + regen_debuffs

        # Recovery buffs
        recovery_buffs = self.aggregate_buffs(buff_sources, "recovery", include_debuffs=False)
        recovery_all = self.aggregate_buffs(buff_sources, "recovery", include_debuffs=True)
        recovery_debuffs = recovery_all - recovery_buffs

        if recovery_debuffs < 0 and debuff_resistance_sources:
            recovery_debuffs = self.apply_debuff_resistance(
                recovery_debuffs, "recovery", debuff_resistance_sources
            )

        # Recovery cap
        recovery_cap = BUFF_CAPS.get("recovery", 500.0)
        recovery_buffs = min(recovery_buffs, recovery_cap)
        results["recovery"] = recovery_buffs + recovery_debuffs

        # Defense buffs (handled per type)
        for def_type in ["melee", "ranged", "aoe", "smashing", "lethal", "fire", "cold",
                         "energy", "negative", "toxic", "psionic"]:
            buff_key = f"defense_{def_type}"

            def_buffs = self.aggregate_buffs(buff_sources, buff_key, include_debuffs=False)
            def_all = self.aggregate_buffs(buff_sources, buff_key, include_debuffs=True)
            def_debuffs = def_all - def_buffs

            if def_debuffs < 0 and debuff_resistance_sources:
                def_debuffs = self.apply_debuff_resistance(
                    def_debuffs, "defense", debuff_resistance_sources
                )

            # Defense doesn't have a buff cap, only final value cap (95%)
            results[buff_key] = def_buffs + def_debuffs

        return results

    def calculate_utility_buffs(
        self,
        buff_sources: list[dict[str, float]],
        debuff_resistance_sources: list[dict[str, float]] | None = None
    ) -> dict[str, float]:
        """Calculate utility buff totals.
        
        Args:
            buff_sources: All buff sources
            debuff_resistance_sources: Sources of debuff resistance
            
        Returns:
            Dictionary of utility buff types to total values
        """
        if debuff_resistance_sources is None:
            debuff_resistance_sources = []

        results = {}

        # Recharge buffs
        recharge_buffs = self.aggregate_buffs(buff_sources, "recharge", include_debuffs=False)
        recharge_all = self.aggregate_buffs(buff_sources, "recharge", include_debuffs=True)
        recharge_debuffs = recharge_all - recharge_buffs

        if recharge_debuffs < 0 and debuff_resistance_sources:
            recharge_debuffs = self.apply_debuff_resistance(
                recharge_debuffs, "recharge", debuff_resistance_sources
            )

        # Recharge cap (+500%)
        recharge_cap = BUFF_CAPS.get("recharge", 500.0)
        recharge_buffs = min(recharge_buffs, recharge_cap)
        results["recharge"] = recharge_buffs + recharge_debuffs

        # Movement buffs (run, fly, jump)
        for movement_type in ["run_speed", "fly_speed", "jump_height", "jump_speed"]:
            move_buffs = self.aggregate_buffs(buff_sources, movement_type, include_debuffs=False)
            move_all = self.aggregate_buffs(buff_sources, movement_type, include_debuffs=True)
            move_debuffs = move_all - move_buffs

            if move_debuffs < 0 and debuff_resistance_sources:
                move_debuffs = self.apply_debuff_resistance(
                    move_debuffs, "movement", debuff_resistance_sources
                )

            # Movement caps vary by type
            move_cap = BUFF_CAPS.get(movement_type, 300.0)
            move_buffs = min(move_buffs, move_cap)
            results[movement_type] = move_buffs + move_debuffs

        # Endurance modification (both cost reduction and recovery)
        end_cost_buffs = self.aggregate_buffs(
            buff_sources, "endurance_cost", include_debuffs=False
        )
        end_cost_all = self.aggregate_buffs(
            buff_sources, "endurance_cost", include_debuffs=True
        )
        end_cost_debuffs = end_cost_all - end_cost_buffs

        if end_cost_debuffs < 0 and debuff_resistance_sources:
            end_cost_debuffs = self.apply_debuff_resistance(
                end_cost_debuffs, "endurance", debuff_resistance_sources
            )

        # Endurance cost reduction cap
        end_cost_cap = BUFF_CAPS.get("endurance_cost", 90.0)  # Max 90% reduction
        end_cost_buffs = min(end_cost_buffs, end_cost_cap)
        results["endurance_cost"] = end_cost_buffs + end_cost_debuffs

        return results

    def calculate_all_buffs(
        self,
        global_buffs: dict[str, float],
        power_buffs: list[dict[str, float]],
        set_bonuses: list[dict[str, float]],
        debuff_resistance_sources: list[dict[str, float]] | None = None
    ) -> dict[str, dict[str, float]]:
        """Calculate all buff categories.
        
        Args:
            global_buffs: Global buffs from build
            power_buffs: Buffs from auto/toggle powers
            set_bonuses: Buffs from enhancement set bonuses
            debuff_resistance_sources: Sources of debuff resistance
            
        Returns:
            Dictionary with offensive, defensive, and utility buff totals
        """
        # Combine all buff sources
        all_sources = []

        # Add global buffs if provided
        if global_buffs:
            all_sources.append(global_buffs)

        # Add power buffs
        all_sources.extend(power_buffs)

        # Add set bonuses
        all_sources.extend(set_bonuses)

        # Calculate each category
        offensive = self.calculate_offensive_buffs(all_sources, debuff_resistance_sources)
        defensive = self.calculate_defensive_buffs(all_sources, debuff_resistance_sources)
        utility = self.calculate_utility_buffs(all_sources, debuff_resistance_sources)

        return {
            "offensive": offensive,
            "defensive": defensive,
            "utility": utility
        }

