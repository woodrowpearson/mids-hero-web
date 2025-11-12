"""
Game Constants - Critical values from MidsReborn

All constants extracted from MidsReborn C# source with exact values.
These are THE fundamental values that all calculations depend on.
"""

# BASE_MAGIC - The most important constant in regeneration/recovery calculations
# From MidsReborn Enhancement.cs and various calculation files
# Converts percentage-based regen/recovery to per-second rates
# Represents the 4-second game tick system (1 / 0.6 ≈ 1.666667)
BASE_MAGIC: float = 1.666667

# Enhancement Diversification (ED) Thresholds
# From Maths.mhd - "ED Reduction Thresholds" section
# Each schedule has 3 thresholds where diminishing returns apply

# Schedule A - "Standard" (Most offensive attributes)
# Used by: Damage, Accuracy, Recharge, Heal, Endurance Mod, Recovery, Regen, etc.
ED_SCHEDULE_A_THRESH_1: float = 0.70  # 70% - No ED below this
ED_SCHEDULE_A_THRESH_2: float = 0.90  # 90% - 90% efficiency region
ED_SCHEDULE_A_THRESH_3: float = 1.00  # 100% - 70% efficiency region, 15% above

# Schedule B - "Defensive" (Defense/Resistance/ToHit/Range)
# Most aggressive schedule - ED hits early and hard
ED_SCHEDULE_B_THRESH_1: float = 0.40  # 40% - ED starts VERY early
ED_SCHEDULE_B_THRESH_2: float = 0.50  # 50%
ED_SCHEDULE_B_THRESH_3: float = 0.60  # 60%

# Schedule C - "Interrupt" (Interrupt time reduction only)
# Least aggressive schedule - ED hits late
ED_SCHEDULE_C_THRESH_1: float = 0.80  # 80%
ED_SCHEDULE_C_THRESH_2: float = 1.00  # 100%
ED_SCHEDULE_C_THRESH_3: float = 1.20  # 120%

# Schedule D - "Special Mez" (Afraid and Confused mez types only)
# Very lenient - allows high enhancement before ED
ED_SCHEDULE_D_THRESH_1: float = 1.20  # 120% - No ED until here!
ED_SCHEDULE_D_THRESH_2: float = 1.50  # 150%
ED_SCHEDULE_D_THRESH_3: float = 1.80  # 180%

# ED Efficiency Multipliers
# These are the scaling factors applied in each ED region
ED_EFFICIENCY_REGION_1: float = 1.00  # 100% efficiency (no ED)
ED_EFFICIENCY_REGION_2: float = 0.90  # 90% efficiency (light ED)
ED_EFFICIENCY_REGION_3: float = 0.70  # 70% efficiency (medium ED)
ED_EFFICIENCY_REGION_4: float = 0.15  # 15% efficiency (heavy ED)

# Purple Patch - Combat level difference modifiers
# TODO: Extract from MidsReborn when implementing combat calculations

# Archetype Caps - Maximum attribute values
# TODO: Will be loaded from .mhd files in Spec 17 implementation

# Proc Rates
# TODO: Will be defined in Spec 34 implementation

# Game Tick Rate
GAME_TICK_SECONDS: float = 4.0  # City of Heroes uses 4-second ticks
GAME_TICK_RATE: float = 1.0 / GAME_TICK_SECONDS  # 0.25 ticks per second

# Standard Enhancement Values
# From MidsReborn's enhancement tables
TRAINING_ORIGIN_VALUE: float = 0.0833  # 8.33% per TO
DUAL_ORIGIN_VALUE: float = 0.1667  # 16.67% per DO
SINGLE_ORIGIN_VALUE: float = 0.3333  # 33.33% per SO
INVENTION_ORIGIN_L50_VALUE: float = 0.424  # 42.4% for L50 IO

# Set Bonus Rule of 5
# Maximum number of identical set bonuses that count
RULE_OF_FIVE_LIMIT: int = 5
