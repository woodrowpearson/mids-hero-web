"""
Power Defense/Resistance Calculator

Calculates defense and resistance values - the primary damage mitigation
mechanics in City of Heroes.

Based on MidsReborn Core/Stats.cs Defense and Resistance classes.
Implementation from Spec 09 (Power Defense/Resistance).
"""

from dataclasses import dataclass
from enum import Enum

from app.calculations.core.effect import Effect
from app.calculations.core.effect_types import EffectType


class DamageType(Enum):
    """Damage types for typed defense/resistance"""

    SMASHING = "smashing"
    LETHAL = "lethal"
    FIRE = "fire"
    COLD = "cold"
    ENERGY = "energy"
    NEGATIVE = "negative"
    PSIONIC = "psionic"
    TOXIC = "toxic"


class PositionType(Enum):
    """Position types for positional defense"""

    MELEE = "melee"
    RANGED = "ranged"
    AOE = "aoe"


@dataclass
class DefenseValues:
    """
    Character defense values.

    Maps to MidsReborn's Defense class in Core/Stats.cs.

    Defense has two systems:
    - Typed defense (vs damage type): smashing, lethal, fire, cold, energy, negative, psionic, toxic
    - Positional defense (vs attack vector): melee, ranged, aoe

    An attack checks BOTH typed and positional defense, using whichever is HIGHER.
    """

    # Typed defense (vs damage type)
    smashing: float = 0.0
    lethal: float = 0.0
    fire: float = 0.0
    cold: float = 0.0
    energy: float = 0.0
    negative: float = 0.0
    psionic: float = 0.0
    toxic: float = 0.0

    # Positional defense (vs attack vector)
    melee: float = 0.0
    ranged: float = 0.0
    aoe: float = 0.0

    def get_typed(self, damage_type: DamageType) -> float:
        """Get typed defense for a damage type"""
        return getattr(self, damage_type.value)

    def get_positional(self, position: PositionType) -> float:
        """Get positional defense for an attack vector"""
        return getattr(self, position.value)

    def get_effective(self, damage_type: DamageType, position: PositionType) -> float:
        """
        Get effective defense against an attack.

        City of Heroes uses the HIGHER of typed or positional defense.
        This is critical for build planning.

        Example:
            Ranged Fire attack checks both "Ranged" and "Fire" defense.
            If you have 35% Ranged and 20% Fire, effective defense is 35%.

        Args:
            damage_type: Damage type of the attack
            position: Position type of the attack

        Returns:
            Effective defense (the higher of typed or positional)
        """
        typed = self.get_typed(damage_type)
        positional = self.get_positional(position)
        return max(typed, positional)


@dataclass
class ResistanceValues:
    """
    Character resistance values.

    Maps to MidsReborn's Resistance class in Core/Stats.cs.

    Resistance only has typed resistance (no positional).
    """

    smashing: float = 0.0
    lethal: float = 0.0
    fire: float = 0.0
    cold: float = 0.0
    energy: float = 0.0
    negative: float = 0.0
    psionic: float = 0.0
    toxic: float = 0.0

    def get(self, damage_type: DamageType) -> float:
        """Get resistance for a damage type"""
        return getattr(self, damage_type.value)


@dataclass
class DebuffResistanceValues:
    """
    Defense debuff resistance (DDR) and other debuff resistances.

    Maps to MidsReborn's DebuffResistance class.

    DDR reduces the magnitude of defense debuffs, protecting defense-based
    characters from "defense cascade" failure.
    """

    defense: float = 0.0  # DDR - reduces defense debuffs
    endurance: float = 0.0  # Reduces endurance drain
    perception: float = 0.0  # Reduces perception debuffs
    recharge: float = 0.0  # Reduces recharge debuffs
    recovery: float = 0.0  # Reduces recovery debuffs
    regeneration: float = 0.0  # Reduces regeneration debuffs
    tohit: float = 0.0  # Reduces tohit debuffs


class DefenseCalculator:
    """
    Calculates defense and resistance values including debuffs and caps.

    Maps to logic in clsToonX.cs and Statistics.cs.

    From Spec 09, Section 1 (Algorithm).
    """

    # Defense soft cap (45% vs even-level enemies)
    DEFENSE_SOFT_CAP = 0.45

    def __init__(self, archetype_resistance_cap: float = 0.9):
        """
        Initialize with archetype-specific caps.

        Args:
            archetype_resistance_cap: Resistance cap (0.75-0.9 depending on AT)
                - Tankers/Brutes: 0.90 (90%)
                - Most other ATs: 0.75 (75%)
        """
        self.resistance_cap = archetype_resistance_cap

    def extract_defense_from_power(self, effects: list[Effect]) -> DefenseValues:
        """
        Extract defense values from a power's effects.

        This extracts defense from a SINGLE POWER.
        Build-level aggregation is handled by build totals calculators.

        Args:
            effects: List of Effect objects from a single power

        Returns:
            DefenseValues with defense from this power
        """
        defense = DefenseValues()

        for effect in effects:
            # Filter: Only include defense effects
            if effect.effect_type != EffectType.DEFENSE:
                continue

            # Filter: Exclude effects with probability <= 0
            if effect.probability <= 0:
                continue

            # Get enhanced magnitude (includes enhancements and AT scaling)
            value = effect.buffed_magnitude

            # Check if this is typed or positional defense
            if hasattr(effect, "position") and effect.position is not None:
                # Positional defense
                position_attr = effect.position.value
                if hasattr(defense, position_attr):
                    current = getattr(defense, position_attr)
                    setattr(defense, position_attr, current + value)
            elif effect.damage_type is not None:
                # Typed defense
                damage_type_attr = effect.damage_type.name.lower()
                if hasattr(defense, damage_type_attr):
                    current = getattr(defense, damage_type_attr)
                    setattr(defense, damage_type_attr, current + value)

        return defense

    def extract_resistance_from_power(self, effects: list[Effect]) -> ResistanceValues:
        """
        Extract resistance values from a power's effects.

        This extracts resistance from a SINGLE POWER.
        Build-level aggregation is handled by build totals calculators.

        Args:
            effects: List of Effect objects from a single power

        Returns:
            ResistanceValues with resistance from this power
        """
        resistance = ResistanceValues()

        for effect in effects:
            # Filter: Only include resistance effects
            if effect.effect_type != EffectType.RESISTANCE:
                continue

            # Filter: Exclude effects with probability <= 0
            if effect.probability <= 0:
                continue

            # Get enhanced magnitude
            value = effect.buffed_magnitude

            # Map damage type to resistance attribute
            if effect.damage_type is not None:
                damage_type_attr = effect.damage_type.name.lower()
                if hasattr(resistance, damage_type_attr):
                    current = getattr(resistance, damage_type_attr)
                    setattr(resistance, damage_type_attr, current + value)

        return resistance

    def extract_debuff_resistance_from_power(
        self, effects: list[Effect]
    ) -> DebuffResistanceValues:
        """
        Extract debuff resistance values from a power's effects.

        Args:
            effects: List of Effect objects from a single power

        Returns:
            DebuffResistanceValues with DDR and other debuff resistances
        """
        ddr = DebuffResistanceValues()

        for effect in effects:
            # Filter: Exclude effects with probability <= 0
            if effect.probability <= 0:
                continue

            # Get enhanced magnitude
            value = effect.buffed_magnitude

            # Extract DDR (Defense Debuff Resistance)
            if effect.effect_type == EffectType.DEFENSE_DEBUFF_RESISTANCE:
                ddr.defense += value
            elif effect.effect_type == EffectType.ENDURANCE_DEBUFF_RESISTANCE:
                ddr.endurance += value
            elif effect.effect_type == EffectType.PERCEPTION_DEBUFF_RESISTANCE:
                ddr.perception += value
            elif effect.effect_type == EffectType.RECHARGE_DEBUFF_RESISTANCE:
                ddr.recharge += value
            elif effect.effect_type == EffectType.RECOVERY_DEBUFF_RESISTANCE:
                ddr.recovery += value
            elif effect.effect_type == EffectType.REGENERATION_DEBUFF_RESISTANCE:
                ddr.regeneration += value
            elif effect.effect_type == EffectType.TOHIT_DEBUFF_RESISTANCE:
                ddr.tohit += value

        return ddr

    def apply_defense_debuff(
        self, base_defense: float, defense_debuff: float, ddr: float
    ) -> float:
        """
        Apply defense debuff reduced by Defense Debuff Resistance (DDR).

        Formula: net_defense = base_defense - (defense_debuff * (1 - DDR))

        Args:
            base_defense: Base defense value (0.0 to 1.0+)
            defense_debuff: Defense debuff magnitude (positive value, e.g., 0.20 for -20%)
            ddr: Defense Debuff Resistance (0.0 to 1.0+, can exceed 1.0 for immunity)

        Returns:
            Net defense after debuff application

        Examples:
            # No DDR
            apply_defense_debuff(0.45, 0.20, 0.0) = 0.25

            # 50% DDR
            apply_defense_debuff(0.45, 0.20, 0.5) = 0.35

            # 100% DDR (immune)
            apply_defense_debuff(0.45, 0.20, 1.0) = 0.45
        """
        # DDR reduces the debuff magnitude
        actual_debuff = defense_debuff * (1.0 - ddr)

        # Apply reduced debuff
        net_defense = base_defense - actual_debuff

        return net_defense

    def apply_defense_debuff_to_values(
        self,
        base_defense: DefenseValues,
        defense_debuffs: DefenseValues,
        ddr: float,
    ) -> DefenseValues:
        """
        Apply defense debuffs to all defense values.

        Args:
            base_defense: Base defense values
            defense_debuffs: Defense debuff magnitudes (positive values)
            ddr: Defense debuff resistance (0.0 to 1.0+)

        Returns:
            Net defense after debuffs
        """
        net_defense = DefenseValues()

        # Apply DDR to typed defenses
        for damage_type in DamageType:
            attr = damage_type.value
            base = getattr(base_defense, attr)
            debuff = getattr(defense_debuffs, attr)
            setattr(net_defense, attr, self.apply_defense_debuff(base, debuff, ddr))

        # Apply DDR to positional defenses
        for position in PositionType:
            attr = position.value
            base = getattr(base_defense, attr)
            debuff = getattr(defense_debuffs, attr)
            setattr(net_defense, attr, self.apply_defense_debuff(base, debuff, ddr))

        return net_defense

    def apply_resistance_cap(self, resistance_value: float) -> float:
        """
        Apply archetype-specific resistance cap to a single value.

        Args:
            resistance_value: Uncapped resistance value (0.0 to any)

        Returns:
            Capped resistance value

        Note:
            Defense has NO hard cap (soft cap at 45% for even-level enemies).
            Resistance HAS hard caps per archetype.
        """
        return min(resistance_value, self.resistance_cap)

    def apply_resistance_cap_to_values(
        self, resistance: ResistanceValues
    ) -> ResistanceValues:
        """
        Apply archetype-specific resistance cap to all values.

        Args:
            resistance: Uncapped resistance values

        Returns:
            Capped resistance values
        """
        capped = ResistanceValues()

        for damage_type in DamageType:
            attr = damage_type.value
            value = getattr(resistance, attr)
            setattr(capped, attr, self.apply_resistance_cap(value))

        return capped

    def calculate_effective_hp(
        self,
        base_hp: float,
        defense: float,
        resistance: float,
        enemy_base_tohit: float = 0.50,
    ) -> float:
        """
        Calculate Effective Hit Points (EHP) with defense and resistance.

        Defense reduces chance to be hit.
        Resistance reduces damage taken when hit.
        Together they multiply survival time.

        Args:
            base_hp: Base hit points
            defense: Defense value (0.0 to 1.0+)
            resistance: Resistance value (0.0 to cap)
            enemy_base_tohit: Base tohit for enemies (default 0.50 = 50%)

        Returns:
            Effective hit points

        Formula:
            chance_to_hit = max(0.05, enemy_base_tohit - defense)  # 5% floor
            damage_multiplier = 1 - resistance
            EHP = base_hp / damage_multiplier / chance_to_hit

        Examples:
            # 45% defense, 75% resistance
            calculate_effective_hp(2000, 0.45, 0.75, 0.50)
            = 2000 / 0.25 / 0.05 = 160,000 EHP

            # 45% defense, 0% resistance
            calculate_effective_hp(2000, 0.45, 0.0, 0.50)
            = 2000 / 1.0 / 0.05 = 40,000 EHP

            # 0% defense, 75% resistance
            calculate_effective_hp(2000, 0.0, 0.75, 0.50)
            = 2000 / 0.25 / 0.50 = 16,000 EHP
        """
        # Calculate chance to hit (5% minimum floor)
        chance_to_hit = max(0.05, enemy_base_tohit - defense)

        # Calculate damage multiplier from resistance
        damage_multiplier = 1.0 - resistance

        # Handle edge case: immune to damage
        if damage_multiplier <= 0:
            return float("inf")

        # Calculate effective HP
        ehp = base_hp / damage_multiplier / chance_to_hit

        return ehp
