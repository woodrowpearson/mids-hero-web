"""
ToHit and Accuracy calculation module.

Implements the complete ToHit system including:
- Base ToHit calculations
- ToHit buffs/debuffs
- Defense integration
- Accuracy multipliers
- Hit chance floor/ceiling enforcement
"""



class ToHitCalculator:
    """Handles ToHit and accuracy calculations for combat."""

    # Base ToHit constants
    BASE_TOHIT_EVEN = 0.75  # 75% base chance vs even-level
    BASE_TOHIT_PVP = 0.50   # 50% base in PvP

    # Level difference modifiers (per level)
    TOHIT_LEVEL_MODIFIER = 0.05  # ±5% per level difference

    # Hit chance bounds
    HIT_CHANCE_FLOOR = 0.05   # 5% minimum
    HIT_CHANCE_CEILING = 0.95  # 95% maximum

    def __init__(self):
        """Initialize the ToHit calculator."""
        pass

    def calculate_base_tohit(
        self,
        attacker_level: int,
        target_level: int,
        is_pvp: bool = False
    ) -> float:
        """
        Calculate base ToHit chance based on level difference.
        
        Args:
            attacker_level: Level of the attacking entity
            target_level: Level of the target
            is_pvp: Whether this is a PvP calculation
            
        Returns:
            Base ToHit chance (0.0-1.0)
        """
        if is_pvp:
            return self.BASE_TOHIT_PVP

        level_diff = attacker_level - target_level
        base_tohit = self.BASE_TOHIT_EVEN + (level_diff * self.TOHIT_LEVEL_MODIFIER)

        # Don't clamp here - only clamp final result
        return base_tohit

    def calculate_hit_chance(self, combat_data: dict[str, float]) -> float:
        """
        Calculate final hit chance using the complete formula:
        HitChance = clamp((BaseToHit + ToHitBuffs - Defense) * Accuracy, 0.05, 0.95)
        
        Args:
            combat_data: Dictionary containing:
                - base_tohit: Base ToHit chance
                - tohit_buffs: Sum of ToHit buffs/debuffs
                - target_defense: Target's relevant defense value
                - accuracy: Accuracy multiplier (1.0 = 100%)
                
        Returns:
            Final hit chance clamped between floor and ceiling
        """
        base_tohit = combat_data.get('base_tohit', self.BASE_TOHIT_EVEN)
        tohit_buffs = combat_data.get('tohit_buffs', 0.0)
        target_defense = combat_data.get('target_defense', 0.0)
        accuracy = combat_data.get('accuracy', 1.0)

        # Apply the formula: (BaseToHit + ToHitBuffs - Defense) * Accuracy
        tohit_after_defense = base_tohit + tohit_buffs - target_defense
        final_chance = tohit_after_defense * accuracy

        # Clamp to floor and ceiling
        return max(self.HIT_CHANCE_FLOOR, min(self.HIT_CHANCE_CEILING, final_chance))

    def calculate_power_hit_chance(
        self,
        power_accuracy: float,
        tohit_buffs: float,
        target_defense: float,
        accuracy_enhancements: float,
        global_accuracy_bonus: float,
        attacker_level: int = 50,
        target_level: int = 50,
        is_pvp: bool = False
    ) -> float:
        """
        Calculate hit chance for a specific power.
        
        Args:
            power_accuracy: Base accuracy of the power (usually 1.0)
            tohit_buffs: Total ToHit buffs affecting attacker
            target_defense: Target's relevant defense
            accuracy_enhancements: Accuracy enhancement value (post-ED)
            global_accuracy_bonus: Global accuracy bonuses (set bonuses, etc)
            attacker_level: Attacker's level
            target_level: Target's level
            is_pvp: Whether this is PvP combat
            
        Returns:
            Final hit chance as percentage (0.0-1.0)
        """
        # Calculate base ToHit
        base_tohit = self.calculate_base_tohit(attacker_level, target_level, is_pvp)

        # Calculate total accuracy multiplier
        total_accuracy = power_accuracy * (1.0 + accuracy_enhancements + global_accuracy_bonus)

        # Build combat data
        combat_data = {
            'base_tohit': base_tohit,
            'tohit_buffs': tohit_buffs,
            'target_defense': target_defense,
            'accuracy': total_accuracy
        }

        return self.calculate_hit_chance(combat_data)

    def get_defense_cascade_tohit(
        self,
        defense_values: dict[str, float],
        attack_type: str
    ) -> float:
        """
        Get the appropriate defense value for ToHit calculations.
        Uses defense cascade: typed -> positional -> lowest.
        
        Args:
            defense_values: Dictionary of defense values by type
            attack_type: Type of attack (e.g., 'smashing_melee', 'energy_ranged')
            
        Returns:
            Relevant defense value to use
        """
        # Parse attack type
        if '_' in attack_type:
            damage_type, position_type = attack_type.split('_')
        else:
            # Fallback for simple types
            damage_type = attack_type
            position_type = 'melee'

        # Check typed defense first
        typed_defense = defense_values.get(damage_type, 0.0)

        # Check positional defense
        positional_defense = defense_values.get(position_type, 0.0)

        # Use the higher of the two
        return max(typed_defense, positional_defense)

    def calculate_streak_breaker(
        self,
        consecutive_misses: int,
        hit_chance: float
    ) -> bool:
        """
        Determine if streak breaker should force a hit.
        
        Streak breaker rules:
        - 90%+ hit chance: Force hit after 1 miss
        - 80-89%: Force hit after 2 misses
        - 60-79%: Force hit after 3 misses
        - 30-59%: Force hit after 4 misses
        - 20-29%: Force hit after 6 misses
        - 10-19%: Force hit after 8 misses
        - <10%: Force hit after 100 misses
        
        Args:
            consecutive_misses: Number of consecutive misses
            hit_chance: Current hit chance (0.0-1.0)
            
        Returns:
            True if streak breaker should force a hit
        """
        if hit_chance >= 0.90 and consecutive_misses >= 1:
            return True
        elif hit_chance >= 0.80 and consecutive_misses >= 2:
            return True
        elif hit_chance >= 0.60 and consecutive_misses >= 3:
            return True
        elif hit_chance >= 0.30 and consecutive_misses >= 4:
            return True
        elif hit_chance >= 0.20 and consecutive_misses >= 6:
            return True
        elif hit_chance >= 0.10 and consecutive_misses >= 8:
            return True
        elif consecutive_misses >= 100:
            return True

        return False
