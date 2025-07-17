"""SQLAlchemy integration tests for MHD parser."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Archetype as ArchetypeModel
from app.mhd_parser.archetype_parser import Archetype
from app.mhd_parser.main_database_parser import MainDatabase
from app.mhd_parser.powerset_parser import Powerset, PowersetType


class TestSQLAlchemyIntegration:
    """Test integration between MHD parser and SQLAlchemy models."""
    
    @pytest.fixture
    def db_session(self):
        """Create a test database session."""
        # Use in-memory SQLite for tests
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        
        yield session
        
        session.close()
    
    def test_archetype_to_model_conversion(self, db_session):
        """Test converting parsed Archetype to SQLAlchemy model."""
        # Create parsed archetype
        parsed = Archetype(
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
        
        # Convert to SQLAlchemy model
        model = ArchetypeModel(
            name=parsed.class_name,
            display_name=parsed.display_name,
            description=parsed.desc_long,
            hit_points_base=parsed.hitpoints,
            hit_points_max=int(parsed.hp_cap),  # Convert float to int
            primary_group=parsed.primary_group,
            secondary_group=parsed.secondary_group
            # Note: playable field doesn't exist in SQLAlchemy model
        )
        
        # Save to database
        db_session.add(model)
        db_session.commit()
        
        # Verify it was saved
        saved = db_session.query(ArchetypeModel).filter_by(
            name="Class_Blaster"
        ).first()
        
        assert saved is not None
        assert saved.display_name == "Blaster"
        assert saved.hit_points_base == 1000
        assert saved.hit_points_max == 1606
    
    def test_database_import_order(self, db_session):
        """Test that entities can be imported in dependency order."""
        # Create a minimal database
        db = MainDatabase(
            header="Test",
            version="1.0",
            date=20231215,
            issue=27,
            page_vol=7,
            page_vol_text="Page 7",
            archetypes=[
                Archetype(
                    display_name="Blaster",
                    hitpoints=1000,
                    hp_cap=1606.0,
                    desc_long="",
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
                    threat_level=1.0,
                    taunt_effectiveness=1.0,
                    taunt_effectiveness_players=1.0,
                    debuff_resistance=0.0,
                    base_recovery=1.0,
                    base_regen=1.0,
                    base_threat=1.0,
                    perception_cap=1153.0
                )
            ],
            powersets=[],
            powers=[],
            summons=[]
        )
        
        # Import archetypes first (no dependencies)
        for arch in db.archetypes:
            model = ArchetypeModel(
                name=arch.class_name,
                display_name=arch.display_name,
                description=arch.desc_long,
                hit_points=arch.hitpoints,
                max_hp=arch.hp_cap,
                primary_category=arch.primary_group,
                secondary_category=arch.secondary_group,
                playable=arch.playable
            )
            db_session.add(model)
        
        db_session.commit()
        
        # Verify import worked
        arch_count = db_session.query(ArchetypeModel).count()
        assert arch_count == 1
    
    def test_index_reference_mapping(self):
        """Test mapping index-based references to database IDs."""
        # Create sample data with index references
        powersets = [
            Powerset(
                display_name="Fire Blast",
                archetype_index=0,  # References first archetype
                set_type=PowersetType.PRIMARY,
                image_name="fireblast.png",
                full_name="Blaster.Fire_Blast",
                set_name="Fire_Blast",
                description="Fire attacks",
                sub_name="",
                at_class="Blaster_Ranged",
                uid_trunk_set="Ranged",
                uid_link_secondary="",
                mutex_list=[]
            ),
            Powerset(
                display_name="Energy Blast",
                archetype_index=0,  # Also references first archetype
                set_type=PowersetType.PRIMARY,
                image_name="energy.png",
                full_name="Blaster.Energy_Blast",
                set_name="Energy_Blast",
                description="Energy attacks",
                sub_name="",
                at_class="Blaster_Ranged",
                uid_trunk_set="Ranged",
                uid_link_secondary="",
                mutex_list=[]
            )
        ]
        
        # Create index mapping
        archetype_id_map = {0: 1}  # Index 0 maps to database ID 1
        
        # Map powersets to archetype IDs
        for ps in powersets:
            if ps.archetype_index >= 0:
                db_arch_id = archetype_id_map.get(ps.archetype_index)
                assert db_arch_id is not None
                assert db_arch_id == 1
    
    def test_data_validation(self):
        """Test validation of parsed data integrity."""
        # Test known relationships
        db = MainDatabase(
            header="Test",
            version="1.0",
            date=20231215,
            issue=27,
            page_vol=7,
            page_vol_text="Page 7",
            archetypes=[
                Archetype(
                    display_name="Blaster",
                    hitpoints=1000,
                    hp_cap=1606.0,
                    desc_long="",
                    res_cap=75.0,
                    origins=["Science", "Technology", "Magic", "Mutation", "Natural"],
                    class_name="Class_Blaster",
                    class_type=0,
                    column=0,
                    desc_short="Blast",
                    primary_group="Ranged_Damage",
                    secondary_group="Ranged_Support",
                    playable=True,
                    recharge_cap=500.0,
                    damage_cap=400.0,
                    recovery_cap=200.0,
                    regen_cap=175.0,
                    threat_level=1.0,
                    taunt_effectiveness=1.0,
                    taunt_effectiveness_players=1.0,
                    debuff_resistance=0.0,
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
                    description="Fire attacks",
                    sub_name="",
                    at_class="Blaster_Ranged",
                    uid_trunk_set="Ranged_Damage",
                    uid_link_secondary="",
                    mutex_list=[]
                )
            ],
            powers=[],
            summons=[]
        )
        
        # Validate Blaster has appropriate powersets
        blaster = next(a for a in db.archetypes if a.display_name == "Blaster")
        blaster_idx = db.archetypes.index(blaster)
        
        # Find primary powersets for Blaster
        blaster_primaries = [
            ps for ps in db.powersets 
            if ps.archetype_index == blaster_idx 
            and ps.set_type == PowersetType.PRIMARY
        ]
        
        assert len(blaster_primaries) >= 1
        assert any("Fire" in ps.display_name for ps in blaster_primaries)
        
        # Validate powerset groups match archetype groups
        for ps in blaster_primaries:
            assert ps.uid_trunk_set == blaster.primary_group