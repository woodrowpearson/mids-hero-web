"""MidsReborn comparison schemas for validating calculation accuracy."""

from typing import Any

from pydantic import BaseModel, Field


class MidsTotalStatistics(BaseModel):
    """Schema matching MidsReborn's TotalStatistics structure."""

    # Defense arrays indexed by damage type
    defense_smashing: float = Field(default=0.0, description="Smashing defense %")
    defense_lethal: float = Field(default=0.0, description="Lethal defense %")
    defense_fire: float = Field(default=0.0, description="Fire defense %")
    defense_cold: float = Field(default=0.0, description="Cold defense %")
    defense_energy: float = Field(default=0.0, description="Energy defense %")
    defense_negative: float = Field(default=0.0, description="Negative energy defense %")
    defense_psionic: float = Field(default=0.0, description="Psionic defense %")
    defense_melee: float = Field(default=0.0, description="Melee defense %")
    defense_ranged: float = Field(default=0.0, description="Ranged defense %")
    defense_aoe: float = Field(default=0.0, description="AoE defense %")

    # Resistance arrays indexed by damage type
    resistance_smashing: float = Field(default=0.0, description="Smashing resistance %")
    resistance_lethal: float = Field(default=0.0, description="Lethal resistance %")
    resistance_fire: float = Field(default=0.0, description="Fire resistance %")
    resistance_cold: float = Field(default=0.0, description="Cold resistance %")
    resistance_energy: float = Field(default=0.0, description="Energy resistance %")
    resistance_negative: float = Field(default=0.0, description="Negative energy resistance %")
    resistance_toxic: float = Field(default=0.0, description="Toxic resistance %")
    resistance_psionic: float = Field(default=0.0, description="Psionic resistance %")

    # Core stats
    hp_max: float = Field(description="Maximum hit points")
    hp_regen: float = Field(description="Health regeneration per second")
    end_max: float = Field(default=100.0, description="Maximum endurance")
    end_rec: float = Field(description="Endurance recovery per second")
    end_use: float = Field(default=0.0, description="Endurance usage reduction %")

    # Movement
    run_speed: float = Field(description="Run speed (mph)")
    jump_speed: float = Field(description="Jump speed (mph)")
    fly_speed: float = Field(description="Fly speed (mph)")
    jump_height: float = Field(description="Jump height (feet)")

    # Combat modifiers
    damage_buff: float = Field(default=0.0, description="Global damage buff %")
    tohit_buff: float = Field(default=0.0, description="Global to-hit buff %")
    accuracy_buff: float = Field(default=0.0, description="Global accuracy buff %")
    recharge_buff: float = Field(default=0.0, description="Global recharge buff %")

    # Mez protection (magnitude)
    mez_protection_hold: float = Field(default=0.0)
    mez_protection_stun: float = Field(default=0.0)
    mez_protection_sleep: float = Field(default=0.0)
    mez_protection_immobilize: float = Field(default=0.0)
    mez_protection_confuse: float = Field(default=0.0)
    mez_protection_fear: float = Field(default=0.0)
    mez_protection_taunt: float = Field(default=0.0)
    mez_protection_placate: float = Field(default=0.0)

    # Debuff resistance
    debuff_resistance: float = Field(default=0.0, description="Generic debuff resistance %")

    # Perception and stealth
    perception_radius: float = Field(default=500.0, description="Perception radius (feet)")
    stealth_radius: float = Field(default=0.0, description="Stealth radius (feet)")

    # Special
    threat_level: float = Field(default=1.0, description="Threat multiplier")
    absorb: float = Field(default=0.0, description="Absorb shield amount")


class MidsComparisonResult(BaseModel):
    """Result of comparing our calculations to MidsReborn."""

    build_name: str
    our_stats: dict[str, Any]
    mids_stats: MidsTotalStatistics
    differences: dict[str, dict[str, float]]  # stat_name -> {ours, mids, diff}
    max_difference_pct: float
    passed: bool


def convert_our_stats_to_mids_format(calc_response: dict) -> dict[str, float]:
    """Convert our CalcResponse to MidsReborn stat format for comparison."""
    agg = calc_response["aggregate_stats"]

    # Extract defense values
    defense = agg["defense"]
    resistance = agg["resistance"]
    totals = agg["totals"]

    # Build flat dictionary matching MidsTotalStatistics fields
    stats = {
        # Positional defense
        "defense_melee": defense["melee"],
        "defense_ranged": defense["ranged"],
        "defense_aoe": defense["aoe"],

        # Typed defense (we don't calculate these separately yet)
        "defense_smashing": 0.0,
        "defense_lethal": 0.0,
        "defense_fire": 0.0,
        "defense_cold": 0.0,
        "defense_energy": 0.0,
        "defense_negative": 0.0,
        "defense_psionic": 0.0,

        # Resistance
        "resistance_smashing": resistance["smashing"],
        "resistance_lethal": resistance["lethal"],
        "resistance_fire": resistance["fire"],
        "resistance_cold": resistance["cold"],
        "resistance_energy": resistance["energy"],
        "resistance_negative": resistance["negative"],
        "resistance_toxic": resistance["toxic"],
        "resistance_psionic": resistance["psionic"],

        # HP/End
        "hp_max": totals["hit_points"]["max"],
        "hp_regen": totals["hit_points"]["regeneration_rate"],
        "end_max": totals["endurance"]["max"],
        "end_rec": totals["endurance"]["recovery_rate"],
        "end_use": 0.0,  # TODO: Calculate endurance reduction

        # Movement
        "run_speed": totals["movement"]["run_speed"],
        "jump_speed": totals["movement"]["jump_speed"],
        "fly_speed": totals["movement"]["fly_speed"],
        "jump_height": totals["movement"]["jump_height"],

        # Combat modifiers (from damage_buff)
        # Use the maximum of melee/ranged/aoe for comparison
        "damage_buff": max(
            agg["damage_buff"].get("melee", 0.0),
            agg["damage_buff"].get("ranged", 0.0),
            agg["damage_buff"].get("aoe", 0.0)
        ),
        "tohit_buff": 0.0,  # TODO: Track tohit separately
        "accuracy_buff": 0.0,  # TODO: Track accuracy buff from sets
        "recharge_buff": 0.0,  # TODO: Track global recharge

        # Perception/Stealth
        "perception_radius": totals["perception"]["pve"],
        "stealth_radius": totals["stealth"]["pve"],

        # Defaults for unimplemented
        "mez_protection_hold": 0.0,
        "mez_protection_stun": 0.0,
        "mez_protection_sleep": 0.0,
        "mez_protection_immobilize": 0.0,
        "mez_protection_confuse": 0.0,
        "mez_protection_fear": 0.0,
        "mez_protection_taunt": 0.0,
        "mez_protection_placate": 0.0,
        "debuff_resistance": 0.0,
        "threat_level": 1.0,
        "absorb": 0.0,
    }

    return stats


def compare_with_mids(
    our_response: dict,
    mids_stats: MidsTotalStatistics,
    tolerance_pct: float = 1.0
) -> MidsComparisonResult:
    """Compare our calculation results with MidsReborn output.
    
    Args:
        our_response: Our CalcResponse as dict
        mids_stats: MidsReborn TotalStatistics
        tolerance_pct: Acceptable difference percentage
        
    Returns:
        Comparison result with differences
    """
    our_stats = convert_our_stats_to_mids_format(our_response)
    mids_dict = mids_stats.model_dump()

    differences = {}
    max_diff_pct = 0.0

    # Compare each stat
    for stat_name, mids_value in mids_dict.items():
        our_value = our_stats.get(stat_name, 0.0)

        # Skip if both are zero
        if mids_value == 0.0 and our_value == 0.0:
            continue

        # Calculate difference
        diff = abs(our_value - mids_value)

        # Calculate percentage difference (avoid division by zero)
        if mids_value != 0:
            diff_pct = (diff / abs(mids_value)) * 100
        else:
            diff_pct = 100.0 if our_value != 0 else 0.0

        # Record if difference exceeds tolerance
        if diff_pct > tolerance_pct:
            differences[stat_name] = {
                "ours": our_value,
                "mids": mids_value,
                "diff": our_value - mids_value,
                "diff_pct": diff_pct
            }
            max_diff_pct = max(max_diff_pct, diff_pct)

    return MidsComparisonResult(
        build_name=our_response["build_name"],
        our_stats=our_stats,
        mids_stats=mids_stats,
        differences=differences,
        max_difference_pct=max_diff_pct,
        passed=max_diff_pct <= tolerance_pct
    )
