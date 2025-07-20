"""Set bonus calculation module.

Implements set bonus aggregation and stacking rules for enhancement sets.
"""

from collections import defaultdict
from typing import Dict, List, Set, Tuple

from app.config.constants import SET_BONUS_RULES


class SetBonusInfo:
    """Information about a set bonus."""
    
    def __init__(self, set_name: str, pieces_required: int, 
                 bonus_type: str, bonus_value: float, 
                 bonus_description: str = ""):
        self.set_name = set_name
        self.pieces_required = pieces_required
        self.bonus_type = bonus_type
        self.bonus_value = bonus_value
        self.bonus_description = bonus_description
    
    def __repr__(self):
        return f"SetBonus({self.set_name}@{self.pieces_required}: {self.bonus_type}={self.bonus_value})"


def gather_set_bonuses(
    enhancement_sets: List[Dict[str, any]],
) -> Tuple[List[SetBonusInfo], Dict[str, float]]:
    """Gather all set bonuses from slotted enhancement sets.

    Enforces stacking rules:
    - Maximum 5 of the same set across the build
    - Each unique bonus from a set counts only once

    Args:
        enhancement_sets: List of dicts with set_name, piece_count, bonuses

    Returns:
        Tuple of (list of active bonuses, dict of aggregated bonus values)
    """
    # Track how many times each set is used
    set_counts = defaultdict(int)
    
    # Track which unique bonuses we've already counted
    counted_bonuses: Set[Tuple[str, str, float]] = set()
    
    # Active bonuses
    active_bonuses = []
    
    # Process each set
    for set_data in enhancement_sets:
        set_name = set_data.get("set_name", "Unknown")
        piece_count = set_data.get("piece_count", 0)
        
        # Check if we've hit the max for this set
        if set_counts[set_name] >= SET_BONUS_RULES["max_same_set"]:
            continue
        
        set_counts[set_name] += 1
        
        # Get bonuses for this set at this piece count
        set_bonuses = _get_bonuses_for_set(set_name, piece_count)
        
        for bonus in set_bonuses:
            # Create unique key for this bonus
            bonus_key = (set_name, bonus.bonus_type, bonus.bonus_value)
            
            # Check if we've already counted this exact bonus
            if SET_BONUS_RULES["unique_bonus_per_set"] and bonus_key in counted_bonuses:
                continue
            
            counted_bonuses.add(bonus_key)
            active_bonuses.append(bonus)
    
    # Aggregate bonuses by type
    aggregated = aggregate_bonuses(active_bonuses)
    
    return active_bonuses, aggregated


def aggregate_bonuses(bonuses: List[SetBonusInfo]) -> Dict[str, float]:
    """Aggregate set bonuses by type.

    Most bonuses stack additively.

    Args:
        bonuses: List of active set bonuses

    Returns:
        Dict mapping bonus type to total value
    """
    totals = defaultdict(float)
    
    for bonus in bonuses:
        # Most bonuses are additive
        totals[bonus.bonus_type] += bonus.bonus_value
    
    return dict(totals)


def _get_bonuses_for_set(set_name: str, piece_count: int) -> List[SetBonusInfo]:
    """Get bonuses for a specific set at a given piece count.

    This is a stub implementation. In a real system, this would
    query the database or use cached set bonus data.

    Args:
        set_name: Name of the enhancement set
        piece_count: Number of pieces slotted

    Returns:
        List of bonuses provided at this piece count
    """
    # Example set bonus data (would come from database)
    example_sets = {
        "Devastation": {
            2: [SetBonusInfo("Devastation", 2, "hp", 12.0, "+1.13% HP")],
            3: [SetBonusInfo("Devastation", 3, "damage", 2.5, "+2.5% Damage")],
            4: [SetBonusInfo("Devastation", 4, "recharge", 5.0, "+5% Recharge")],
            5: [SetBonusInfo("Devastation", 5, "defense_ranged", 1.875, "+1.875% Ranged Defense")],
            6: [SetBonusInfo("Devastation", 6, "accuracy", 7.5, "+7.5% Accuracy")],
        },
        "Crushing Impact": {
            2: [SetBonusInfo("Crushing Impact", 2, "immobilize_resist", 2.2, "+2.2% Immobilize Resist")],
            3: [SetBonusInfo("Crushing Impact", 3, "hp", 1.88, "+1.88% HP")],
            4: [SetBonusInfo("Crushing Impact", 4, "accuracy", 7.0, "+7% Accuracy")],
            5: [SetBonusInfo("Crushing Impact", 5, "recharge", 5.0, "+5% Recharge")],
        },
        "Luck of the Gambler": {
            2: [SetBonusInfo("Luck of the Gambler", 2, "regeneration", 10.0, "+10% Regeneration")],
            3: [SetBonusInfo("Luck of the Gambler", 3, "hp", 1.5, "+1.5% HP")],
            4: [SetBonusInfo("Luck of the Gambler", 4, "accuracy", 9.0, "+9% Accuracy")],
            5: [SetBonusInfo("Luck of the Gambler", 5, "recharge", 7.5, "+7.5% Recharge")],
        },
    }
    
    # Get bonuses for this set
    set_data = example_sets.get(set_name, {})
    
    # Collect all bonuses up to piece_count
    all_bonuses = []
    for pieces in range(2, piece_count + 1):
        if pieces in set_data:
            all_bonuses.extend(set_data[pieces])
    
    return all_bonuses


def calculate_set_bonus_totals(
    build_slots: List[Dict[str, any]],
) -> Dict[str, any]:
    """Calculate total set bonuses for a build.

    Args:
        build_slots: List of all enhancement slots in the build

    Returns:
        Dict with bonus totals and details
    """
    # Group slots by set
    sets_in_build = defaultdict(list)
    
    for slot in build_slots:
        if slot.get("set_name"):
            sets_in_build[slot["set_name"]].append(slot)
    
    # Count pieces per set instance
    enhancement_sets = []
    for set_name, slots in sets_in_build.items():
        # Group by power (each power is a separate instance of the set)
        by_power = defaultdict(list)
        for slot in slots:
            by_power[slot.get("power_id", "unknown")].append(slot)
        
        # Create set entries for each power
        for power_id, power_slots in by_power.items():
            enhancement_sets.append({
                "set_name": set_name,
                "piece_count": len(power_slots),
                "power_id": power_id,
            })
    
    # Gather bonuses
    active_bonuses, totals = gather_set_bonuses(enhancement_sets)
    
    # Format for response
    bonus_details = []
    for bonus in active_bonuses:
        bonus_details.append({
            "set_name": bonus.set_name,
            "bonus_tier": bonus.pieces_required,
            "bonus_description": bonus.bonus_description,
            "bonus_values": {
                bonus.bonus_type: bonus.bonus_value
            }
        })
    
    return {
        "totals": totals,
        "details": bonus_details,
        "set_counts": dict(defaultdict(int)),  # Track for rule enforcement
    }


def apply_set_bonuses_to_stats(
    base_stats: Dict[str, float],
    set_bonus_totals: Dict[str, float],
) -> Dict[str, float]:
    """Apply set bonuses to character stats.

    Args:
        base_stats: Base character stats
        set_bonus_totals: Aggregated set bonus values

    Returns:
        Stats with set bonuses applied
    """
    enhanced_stats = base_stats.copy()
    
    # Map set bonus types to stat names
    bonus_mapping = {
        "hp": "max_hp",
        "damage": "damage_bonus",
        "recharge": "recharge_bonus",
        "accuracy": "accuracy_bonus",
        "defense_melee": "defense_melee",
        "defense_ranged": "defense_ranged",
        "defense_aoe": "defense_aoe",
        "resistance_smashing": "resistance_smashing",
        "resistance_lethal": "resistance_lethal",
        "resistance_fire": "resistance_fire",
        "resistance_cold": "resistance_cold",
        "resistance_energy": "resistance_energy",
        "resistance_negative": "resistance_negative",
        "resistance_toxic": "resistance_toxic",
        "resistance_psionic": "resistance_psionic",
        "regeneration": "regeneration_bonus",
        "recovery": "recovery_bonus",
    }
    
    # Apply bonuses
    for bonus_type, value in set_bonus_totals.items():
        stat_name = bonus_mapping.get(bonus_type, bonus_type)
        if stat_name in enhanced_stats:
            # Most bonuses are additive
            enhanced_stats[stat_name] += value
        else:
            # New stat from set bonus
            enhanced_stats[stat_name] = value
    
    return enhanced_stats