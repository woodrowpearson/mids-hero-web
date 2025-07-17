"""Tests for JSON export functionality."""

import json
import tempfile
from pathlib import Path

from app.mhd_parser.archetype_parser import Archetype
from app.mhd_parser.enhancement_database_parser import EnhancementDatabase
from app.mhd_parser.enhancement_parser import Enhancement, EnhancementSet, SEffect
from app.mhd_parser.json_exporter import MhdJsonExporter
from app.mhd_parser.main_database_parser import MainDatabase, SummonedEntity
from app.mhd_parser.power_parser import Power, PowerType, Requirement
from app.mhd_parser.powerset_parser import Powerset, PowersetType
from app.mhd_parser.recipe_parser import Recipe, RecipeDatabase, RecipeRarity
from app.mhd_parser.salvage_parser import (
    Salvage,
    SalvageDatabase,
    SalvageRarity,
    SalvageType,
)
from app.mhd_parser.text_mhd_parser import TextMhdFile


class TestJsonExporter:
    """Test cases for JSON export functionality."""

    def test_export_main_database(self):
        """Test exporting main database to JSON."""
        # Create sample database
        db = MainDatabase(
            header="Test Database",
            version="1.0.0",
            date=20231215,
            issue=27,
            page_vol=7,
            page_vol_text="Page 7",
            archetypes=[
                Archetype(
                    display_name="Blaster",
                    hitpoints=1000,
                    hp_cap=1606.0,
                    desc_long="Ranged damage dealer",
                    res_cap=75.0,
                    origins=["Science", "Technology", "Magic", "Mutation", "Natural"],
                    class_name="Class_Blaster",
                    class_type=0,
                    column=0,
                    desc_short="Blast",
                    primary_group="Ranged",
                    secondary_group="Support",
                    playable=True,
                    recharge_cap=500.0,
                    damage_cap=400.0,
                    recovery_cap=200.0,
                    regen_cap=175.0,
                    threat_cap=175.0,
                    resist_cap=95.0,
                    damage_resist_cap=300.0,
                    base_recovery=1.0,
                    base_regen=1.0,
                    base_threat=1.0,
                    perception_cap=1153.0
                )
            ],
            powersets=[
                Powerset(
                    display_name="Fire Blast",
                    archetype_index=0,
                    set_type=PowersetType.PRIMARY,
                    image_name="fireblast.png",
                    full_name="Blaster.Fire_Blast",
                    set_name="Fire_Blast",
                    description="Fire ranged attacks",
                    sub_name="",
                    at_class="Blaster_Ranged",
                    uid_trunk_set="Ranged_Damage",
                    uid_link_secondary="",
                    mutex_list=[]
                )
            ],
            powers=[
                Power(
                    full_name="Fire_Blast.Fire_Bolt",
                    group_name="Ranged",
                    set_name="Fire_Blast",
                    power_name="Fire_Bolt",
                    display_name="Fire Bolt",
                    available=1,
                    requirement=Requirement("", "", [], [], [], []),
                    power_type=PowerType.CLICK,
                    accuracy=1.0,
                    attack_types=1,
                    group_membership=[],
                    entities_affected=1,
                    entities_auto_hit=0,
                    target=1,
                    target_line_special_range=False,
                    range=80.0,
                    range_secondary=0.0,
                    end_cost=5.2,
                    interrupt_time=0.0,
                    cast_time=1.0,
                    recharge_time=4.0,
                    base_recharge_time=4.0,
                    activate_period=0.0,
                    effect_area=0,
                    radius=0.0,
                    arc=0,
                    max_targets=1,
                    max_boosts="",
                    boosts_allowed=[],
                    cast_flags=0,
                    ai_report=0,
                    num_effects=1,
                    usage_time=0.0,
                    life_time=0.0,
                    life_time_in_game=0.0,
                    num_charges=0.0,
                    num_activated=0,
                    def_value=0.0,
                    def_override=0.0,
                    desc_short="Quick fire attack",
                    desc_long="Launches a quick bolt of fire",
                    set_types=[],
                    uid_sub_power=[],
                    ignore_strength=[],
                    ignore_buff=[],
                    click_buff=0,
                    always_toggle=False,
                    level=0,
                    allow_front_loading=False,
                    ignore_enh=False,
                    ignore_set_bonus=False,
                    boost_boostable=False,
                    boost_always=False,
                    skip_max=False,
                    display_location=0,
                    mutex_auto=False,
                    mutex_ignore=False,
                    absorb_summon_effects=False,
                    absorb_summon_attributes=False,
                    show_summon_anyway=False,
                    never_auto_update=False,
                    never_auto_update_requirements=False,
                    include_flag=False,
                    forced_class="",
                    sort_override=0,
                    boost_boost_special_allowed=False,
                    effects=[],
                    hidden_power=False
                )
            ],
            summons=[
                SummonedEntity(
                    uid="Pet.FireImp",
                    display_name="Fire Imp",
                    entity_type=1,
                    class_name="Pet_FireImp",
                    powerset_full_names=[],
                    upgrade_power_full_names=[]
                )
            ]
        )

        # Export to JSON
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "main_db.json"
            exporter = MhdJsonExporter()
            exporter.export_main_database(db, output_path)

            # Verify file exists
            assert output_path.exists()

            # Load and verify JSON
            with open(output_path) as f:
                data = json.load(f)

            assert data["header"] == "Test Database"
            assert data["version"] == "1.0.0"
            assert data["date"] == 20231215
            assert data["statistics"]["archetype_count"] == 1
            assert data["statistics"]["powerset_count"] == 1
            assert data["statistics"]["power_count"] == 1
            assert data["statistics"]["summon_count"] == 1

            # Check specific data
            assert data["archetypes"][0]["display_name"] == "Blaster"
            assert data["powersets"][0]["display_name"] == "Fire Blast"
            assert data["powers"][0]["full_name"] == "Fire_Blast.Fire_Bolt"
            assert data["summons"][0]["uid"] == "Pet.FireImp"

    def test_export_enhancement_database(self):
        """Test exporting enhancement database to JSON."""
        db = EnhancementDatabase(
            header="Enhancement Database",
            version="1.0.0",
            date=20231215,
            enhancements=[
                Enhancement(
                    static_index=1001,
                    name="Accuracy IO",
                    short_name="Acc IO",
                    description="Increases accuracy",
                    type_id=1,
                    sub_type_id=0,
                    class_ids=[],
                    image="acc_io.png",
                    n_id_set=0,
                    uid_set="",
                    effect_chance=100.0,
                    level_min=10,
                    level_max=50,
                    unique=False,
                    mut_ex_id=0,
                    buff_mode=0,
                    effects=[
                        SEffect(
                            mode=1,
                            buff_mode=0,
                            enhance_id=1,
                            enhance_sub_id=0,
                            schedule=0,
                            multiplier=0.3333,
                            fx=None
                        )
                    ],
                    uid="IO.Acc",
                    recipe_name="",
                    superior=False,
                    is_proc=False,
                    is_scalable=True
                )
            ],
            enhancement_sets=[
                EnhancementSet(
                    display_index=100,
                    display_name="Thunderstrike",
                    short_name="TS",
                    description="Melee damage set",
                    set_type=1,
                    enhancement_indices=[0],
                    bonuses=[],
                    bonus_min=[],
                    bonus_max=[],
                    special_bonuses=[],
                    uid_set="Set.Thunderstrike",
                    level_min=10,
                    level_max=50
                )
            ]
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "enh_db.json"
            exporter = MhdJsonExporter()
            exporter.export_enhancement_database(db, output_path)

            with open(output_path) as f:
                data = json.load(f)

            assert data["statistics"]["enhancement_count"] == 1
            assert data["statistics"]["enhancement_set_count"] == 1
            assert data["enhancements"][0]["name"] == "Accuracy IO"
            assert data["enhancement_sets"][0]["display_name"] == "Thunderstrike"

    def test_export_salvage_database(self):
        """Test exporting salvage database to JSON."""
        db = SalvageDatabase(
            header="Salvage Database",
            version="1.0.0",
            salvage_items=[
                Salvage(
                    internal_name="Alchemical_Silver",
                    display_name="Alchemical Silver",
                    rarity=SalvageRarity.COMMON,
                    salvage_type=SalvageType.COMPONENT,
                    description="A rare metal"
                )
            ]
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "salvage_db.json"
            exporter = MhdJsonExporter()
            exporter.export_salvage_database(db, output_path)

            with open(output_path) as f:
                data = json.load(f)

            assert data["salvage_count"] == 1
            assert data["salvage_items"][0]["display_name"] == "Alchemical Silver"
            assert data["salvage_items"][0]["rarity"] == "COMMON"

    def test_export_recipe_database(self):
        """Test exporting recipe database to JSON."""
        db = RecipeDatabase(
            header="Recipe Database",
            version="1.0.0",
            recipes=[
                Recipe(
                    recipe_id="Recipe_Acc_1",
                    name="Accuracy IO",
                    level_requirement=10,
                    rarity=RecipeRarity.COMMON,
                    ingredients=["Boresight", "Luck Charm"],
                    quantities=[1, 2],
                    crafting_cost=10000,
                    reward="Accuracy IO"
                )
            ]
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "recipe_db.json"
            exporter = MhdJsonExporter()
            exporter.export_recipe_database(db, output_path)

            with open(output_path) as f:
                data = json.load(f)

            assert data["recipe_count"] == 1
            assert data["recipes"][0]["name"] == "Accuracy IO"
            assert data["recipes"][0]["ingredients"] == ["Boresight", "Luck Charm"]
            assert data["recipes"][0]["quantities"] == [1, 2]

    def test_export_text_mhd(self):
        """Test exporting text MHD file to JSON."""
        text_file = TextMhdFile(
            version="1.5.0",
            headers=["Level", "Experience"],
            data=[
                ["1", "0"],
                ["2", "106"],
                ["3", "337"]
            ]
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "text_mhd.json"
            exporter = MhdJsonExporter()
            exporter.export_text_mhd(text_file, output_path)

            with open(output_path) as f:
                data = json.load(f)

            assert data["version"] == "1.5.0"
            assert data["headers"] == ["Level", "Experience"]
            assert len(data["data"]) == 3
            assert data["data"][1] == ["2", "106"]
