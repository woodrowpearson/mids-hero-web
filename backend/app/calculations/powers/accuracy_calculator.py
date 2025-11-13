"""
Power Accuracy/ToHit Calculator

Calculates hit chance for attack powers, distinguishing between accuracy
(multiplicative) and tohit (additive) mechanics.

Based on MidsReborn clsToonX.cs GBPA_Pass4_ApplyAccuracy() and ConfigData.cs.
Implementation from Spec 08 (Power Accuracy/ToHit).
"""

from dataclasses import dataclass
from enum import Enum


class EntityType(Enum):
    """Entities that can be auto-hit"""

    NONE = "none"
    CASTER = "caster"
    PLAYER = "player"
    CRITTER = "critter"
    ANY = "any"


@dataclass
class AccuracyResult:
    """
    Result of accuracy/tohit calculation.

    Maps to MidsReborn's powerBuffed.Accuracy and AccuracyMult properties.

    Attributes:
        final_accuracy: Base * (1 + enh + buff) * (scalingToHit + tohitBuff)
        accuracy_mult: Base * (1 + enh + buff) - without tohit scaling
        base_accuracy: Power's base accuracy (typically 1.0)
        enhancement_bonus: Accuracy from enhancements (after ED)
        global_accuracy_buff: Global accuracy buffs (Kismet, set bonuses)
        global_tohit_buff: Global tohit buffs (Build Up, Aim, Tactics)
        scaling_tohit: Base tohit for enemy level (0.75 default)
        is_auto_hit: True if power auto-hits
    """

    final_accuracy: float
    accuracy_mult: float
    base_accuracy: float
    enhancement_bonus: float
    global_accuracy_buff: float
    global_tohit_buff: float
    scaling_tohit: float
    is_auto_hit: bool = False

    @property
    def hit_chance_vs_even_defense(self) -> float:
        """
        Hit chance vs enemy with no defense at same level.

        Applies 5%-95% floor/ceiling.

        Returns:
            Hit chance (0.05-0.95 or 1.0 for auto-hit)
        """
        if self.is_auto_hit:
            return 1.0
        chance = self.final_accuracy
        return max(0.05, min(0.95, chance))

    def hit_chance_vs_defense(self, enemy_defense: float) -> float:
        """
        Hit chance vs enemy with specific defense value.

        Args:
            enemy_defense: Enemy defense value (0.0-1.0+)

        Returns:
            Hit chance (0.05-0.95 or 1.0 for auto-hit)
        """
        if self.is_auto_hit:
            return 1.0
        chance = self.final_accuracy - enemy_defense
        return max(0.05, min(0.95, chance))

    def __str__(self) -> str:
        """Format like MidsReborn display"""
        if self.is_auto_hit:
            return "Auto"
        return f"{self.final_accuracy * 100:.2f}%"


class AccuracyCalculator:
    """
    Calculates power accuracy and hit chance.

    Maps to MidsReborn's GBPA_Pass4_ApplyAccuracy and related methods.

    From Spec 08, Section 1 (Algorithm).
    """

    # Scaling tohit values for different enemy level differences
    # From ConfigData.cs lines 258-269
    SCALING_TOHIT_BY_LEVEL_DIFF = {
        -4: 0.95,  # Gray con (very easy)
        -3: 0.90,
        -2: 0.85,
        -1: 0.80,
        0: 0.75,  # Even level (base)
        1: 0.65,  # Orange con
        2: 0.56,  # Red con
        3: 0.48,  # Purple con
        4: 0.39,  # Purple +1
        5: 0.30,  # Purple +2
        6: 0.20,  # Purple +3
        7: 0.08,  # Purple +4 (nearly impossible)
    }

    def __init__(self, base_tohit: float = 0.75, enemy_level_diff: int = 0):
        """
        Initialize accuracy calculator.

        Args:
            base_tohit: Base tohit from ServerData (default 0.75 = 75%)
            enemy_level_diff: Enemy level - player level (0 = even, +4 = +4 level)
        """
        self.base_tohit = base_tohit
        self.scaling_tohit = self.SCALING_TOHIT_BY_LEVEL_DIFF.get(
            enemy_level_diff, base_tohit
        )

    def calculate_accuracy(
        self,
        power_base_accuracy: float,
        enhancement_accuracy: float,
        global_accuracy_buffs: float = 0.0,
        global_tohit_buffs: float = 0.0,
        ignores_accuracy_buffs: bool = False,
        ignores_tohit_buffs: bool = False,
        auto_hit_entities: EntityType = EntityType.NONE,
    ) -> AccuracyResult:
        """
        Calculate final accuracy and hit chance.

        Implementation from clsToonX.cs GBPA_Pass4_ApplyAccuracy lines 1990-2000.

        This implements Pass 4 only - ED is assumed to have been applied in Pass 2.

        Args:
            power_base_accuracy: Power's base accuracy (typically 1.0)
            enhancement_accuracy: Accuracy from slotted enhancements (post-ED)
            global_accuracy_buffs: Sum of global accuracy bonuses (Kismet, sets, etc.)
            global_tohit_buffs: Sum of global tohit bonuses (Build Up, Aim, etc.)
            ignores_accuracy_buffs: If True, power ignores global accuracy buffs
            ignores_tohit_buffs: If True, power ignores global tohit buffs
            auto_hit_entities: If not NONE, power auto-hits specified entities

        Returns:
            AccuracyResult with final values
        """
        # STEP 1: Check for auto-hit powers
        is_auto_hit = auto_hit_entities != EntityType.NONE
        if is_auto_hit:
            return AccuracyResult(
                final_accuracy=1.0,
                accuracy_mult=1.0,
                base_accuracy=power_base_accuracy,
                enhancement_bonus=0.0,
                global_accuracy_buff=0.0,
                global_tohit_buff=0.0,
                scaling_tohit=self.scaling_tohit,
                is_auto_hit=True,
            )

        # STEP 2: Enhancement accuracy is already post-ED (from Pass 2)
        # No need to apply ED here
        enhancement_after_ed = enhancement_accuracy

        # STEP 3: Apply global buff filters
        # Note: Logic is inverted in C# - "!" means "if NOT ignoring"
        # If ignores_accuracy_buffs is True, set nAcc to 0
        # If ignores_accuracy_buffs is False, use global_accuracy_buffs
        n_acc = 0.0 if ignores_accuracy_buffs else global_accuracy_buffs
        n_tohit = 0.0 if ignores_tohit_buffs else global_tohit_buffs

        # STEP 4: Calculate accuracy multiplier (without tohit scaling)
        # This is the "Real Numbers style" accuracy multiplier
        accuracy_mult = power_base_accuracy * (1.0 + enhancement_after_ed + n_acc)

        # STEP 5: Calculate final accuracy (with tohit scaling)
        # This is the displayed accuracy value in MidsReborn
        final_accuracy = accuracy_mult * (self.scaling_tohit + n_tohit)

        return AccuracyResult(
            final_accuracy=final_accuracy,
            accuracy_mult=accuracy_mult,
            base_accuracy=power_base_accuracy,
            enhancement_bonus=enhancement_after_ed,
            global_accuracy_buff=n_acc,
            global_tohit_buff=n_tohit,
            scaling_tohit=self.scaling_tohit,
            is_auto_hit=False,
        )

    def calculate_required_accuracy_for_hit_chance(
        self,
        target_hit_chance: float,
        enemy_defense: float = 0.0,
        global_accuracy_buffs: float = 0.0,
        global_tohit_buffs: float = 0.0,
        power_base_accuracy: float = 1.0,
    ) -> float:
        """
        Reverse calculation: determine required enhancement bonus to hit target hit chance.

        Useful for build optimization tools.

        Args:
            target_hit_chance: Desired hit chance (0.05-0.95)
            enemy_defense: Enemy defense value
            global_accuracy_buffs: Global accuracy bonuses from build
            global_tohit_buffs: Global tohit bonuses from build
            power_base_accuracy: Power's base accuracy (default 1.0)

        Returns:
            Required enhancement_accuracy (post-ED) to achieve target
        """
        # Clamp target to valid range
        target = max(0.05, min(0.95, target_hit_chance))

        # Work backwards from formula:
        # hit_chance = [base * (1 + enh + globalAcc) * (scalingToHit + globalToHit)] - defense
        # Solve for enh:
        # base * (1 + enh + globalAcc) = (target + defense) / (scalingToHit + globalToHit)
        # 1 + enh + globalAcc = (target + defense) / (scalingToHit + globalToHit) / base
        # enh = [(target + defense) / (scalingToHit + globalToHit) / base] - 1 - globalAcc

        tohit_total = self.scaling_tohit + global_tohit_buffs
        if tohit_total <= 0:
            return float("inf")  # Impossible to hit

        required_mult = (target + enemy_defense) / tohit_total
        required_enh = (
            (required_mult / power_base_accuracy) - 1.0 - global_accuracy_buffs
        )

        return max(0.0, required_enh)
