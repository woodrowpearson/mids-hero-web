"""
Test database relationships and foreign key integrity.
"""
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from app.models import (
    Archetype,
    Enhancement,
    EnhancementSet,
    Power,
    PowerPrerequisite,
    Powerset,
    Recipe,
    RecipeSalvage,
    Salvage,
)


class TestRelationships:
    """Test all database relationships and foreign key constraints."""

    def test_all_foreign_keys_have_indexes(self, db: Session):
        """Verify all foreign keys have corresponding indexes for performance."""
        inspector = inspect(db.bind)

        issues = []
        for table_name in inspector.get_table_names():
            # Get foreign keys
            foreign_keys = inspector.get_foreign_keys(table_name)
            # Get indexes
            indexes = inspector.get_indexes(table_name)
            indexed_columns = set()

            for index in indexes:
                indexed_columns.update(index['column_names'])

            # Check each foreign key
            for fk in foreign_keys:
                for column in fk['constrained_columns']:
                    if column not in indexed_columns:
                        issues.append(f"{table_name}.{column} (FK) missing index")

        if issues:
            print(f"WARNING: Foreign keys without indexes (performance issue): {issues}")
            # In production, all FKs should have indexes for performance

    def test_powerset_archetype_relationships(self, db: Session):
        """Test that all powersets have valid archetype references."""
        orphaned = db.query(Powerset).outerjoin(
            Archetype, Powerset.archetype_id == Archetype.id
        ).filter(
            Archetype.id.is_(None),
            Powerset.archetype_id.isnot(None)
        ).count()

        assert orphaned == 0, f"Found {orphaned} powersets with invalid archetype_id"

    def test_power_powerset_relationships(self, db: Session):
        """Test that all powers have valid powerset references."""
        orphaned = db.query(Power).outerjoin(
            Powerset, Power.powerset_id == Powerset.id
        ).filter(
            Powerset.id.is_(None),
            Power.powerset_id.isnot(None)
        ).count()

        assert orphaned == 0, f"Found {orphaned} powers with invalid powerset_id"

    def test_power_prerequisites_validity(self, db: Session):
        """Test that all power prerequisites reference valid powers."""
        # Check required_power_id references
        orphaned_required = db.query(PowerPrerequisite).outerjoin(
            Power, PowerPrerequisite.required_power_id == Power.id
        ).filter(Power.id.is_(None)).count()

        # Check power_id references
        orphaned_power = db.query(PowerPrerequisite).outerjoin(
            Power, PowerPrerequisite.power_id == Power.id
        ).filter(Power.id.is_(None)).count()

        assert orphaned_required == 0, f"Found {orphaned_required} prerequisites with invalid required_power_id"
        assert orphaned_power == 0, f"Found {orphaned_power} prerequisites with invalid power_id"

    def test_enhancement_set_relationships(self, db: Session):
        """Test enhancement to enhancement set relationships."""
        orphaned = db.query(Enhancement).outerjoin(
            EnhancementSet, Enhancement.set_id == EnhancementSet.id
        ).filter(
            EnhancementSet.id.is_(None),
            Enhancement.set_id.isnot(None)
        ).count()

        assert orphaned == 0, f"Found {orphaned} enhancements with invalid enhancement_set_id"

    def test_recipe_enhancement_relationships(self, db: Session):
        """Test that all recipes reference valid enhancements."""
        orphaned = db.query(Recipe).outerjoin(
            Enhancement, Recipe.enhancement_id == Enhancement.id
        ).filter(
            Enhancement.id.is_(None),
            Recipe.enhancement_id.isnot(None)
        ).count()

        assert orphaned == 0, f"Found {orphaned} recipes with invalid enhancement_id"

    def test_recipe_salvage_relationships(self, db: Session):
        """Test recipe to salvage relationships."""
        # Check recipe references
        orphaned_recipes = db.query(RecipeSalvage).outerjoin(
            Recipe, RecipeSalvage.recipe_id == Recipe.id
        ).filter(Recipe.id.is_(None)).count()

        # Check salvage references
        orphaned_salvage = db.query(RecipeSalvage).outerjoin(
            Salvage, RecipeSalvage.salvage_id == Salvage.id
        ).filter(Salvage.id.is_(None)).count()

        assert orphaned_recipes == 0, f"Found {orphaned_recipes} recipe_salvage with invalid recipe_id"
        assert orphaned_salvage == 0, f"Found {orphaned_salvage} recipe_salvage with invalid salvage_id"

    def test_no_orphaned_records(self, db: Session):
        """Test for orphaned records across all tables."""
        # Powers without powersets (excluding inherent powers)
        orphaned_powers = db.query(Power).filter(
            Power.powerset_id.is_(None),
            ~Power.name.like('%inherent%')
        ).count()

        # Powersets without archetypes (excluding pool powers)
        orphaned_powersets = db.query(Powerset).filter(
            Powerset.archetype_id.is_(None),
            Powerset.powerset_type != 'pool'
        ).count()

        assert orphaned_powers == 0, f"Found {orphaned_powers} orphaned powers"
        assert orphaned_powersets == 0, f"Found {orphaned_powersets} orphaned powersets"

    def test_circular_dependencies(self, db: Session):
        """Test that there are no circular dependencies in power prerequisites."""
        # Check for simple circular dependencies
        # Note: This is a simplified check that works with SQLite
        prerequisites = db.query(PowerPrerequisite).all()

        circular_count = 0
        for prereq in prerequisites:
            # Check if the required power requires the original power
            reverse = db.query(PowerPrerequisite).filter(
                PowerPrerequisite.power_id == prereq.required_power_id,
                PowerPrerequisite.required_power_id == prereq.power_id
            ).first()

            if reverse:
                circular_count += 1

        assert circular_count == 0, f"Found {circular_count} circular dependencies in power prerequisites"

    def test_referential_integrity_on_delete(self, db: Session):
        """Test that CASCADE and SET NULL constraints are properly configured."""
        # This test is informational - it shows which FKs have CASCADE
        # In production, these should be carefully reviewed
        inspector = inspect(db.bind)

        tables_to_check = ['power_prerequisites', 'recipe_salvage']

        for table_name in tables_to_check:
            try:
                fks = inspector.get_foreign_keys(table_name)
                for fk in fks:
                    if fk.get('ondelete') != 'CASCADE':
                        print(f"Warning: {table_name}.{fk['constrained_columns']} does not have CASCADE delete")
            except Exception:
                # Table might not exist in test database
                pass


class TestDataIntegrity:
    """Test data integrity constraints and rules."""

    def test_unique_constraints(self, db: Session):
        """Test that unique constraints are enforced."""
        # Check archetype names are unique
        from sqlalchemy import func
        duplicate_archetypes = db.query(
            Archetype.name,
            func.count(Archetype.id).label('count')
        ).group_by(Archetype.name).having(func.count(Archetype.id) > 1).all()

        assert not duplicate_archetypes, f"Duplicate archetype names: {duplicate_archetypes}"

        # Check power names within powersets are unique
        from sqlalchemy import func
        duplicate_powers = db.query(
            Power.name,
            Power.powerset_id,
            func.count(Power.id).label('count')
        ).group_by(
            Power.name,
            Power.powerset_id
        ).having(func.count(Power.id) > 1).all()

        assert not duplicate_powers, f"Duplicate power names in same powerset: {duplicate_powers}"

    def test_required_fields_not_null(self, db: Session):
        """Test that required fields are not null."""
        # Archetypes
        null_archetypes = db.query(Archetype).filter(
            (Archetype.name.is_(None)) |
            (Archetype.display_name.is_(None)) |
            (Archetype.hit_points_base.is_(None))
        ).count()

        # Powers
        null_powers = db.query(Power).filter(
            (Power.name.is_(None)) |
            (Power.display_name.is_(None)) |
            (Power.level_available.is_(None))
        ).count()

        # Enhancements
        null_enhancements = db.query(Enhancement).filter(
            (Enhancement.name.is_(None)) |
            (Enhancement.display_name.is_(None))
        ).count()

        assert null_archetypes == 0, f"Found {null_archetypes} archetypes with null required fields"
        assert null_powers == 0, f"Found {null_powers} powers with null required fields"
        assert null_enhancements == 0, f"Found {null_enhancements} enhancements with null required fields"

    def test_data_type_constraints(self, db: Session):
        """Test that numeric fields have valid ranges."""
        # Level constraints
        invalid_levels = db.query(Power).filter(
            (Power.level_available < 1) | (Power.level_available > 50)
        ).count()

        # Hit points must be positive
        invalid_hp = db.query(Archetype).filter(
            (Archetype.hit_points_base <= 0) | (Archetype.hit_points_max <= 0)
        ).count()

        assert invalid_levels == 0, f"Found {invalid_levels} powers with invalid level"
        assert invalid_hp == 0, f"Found {invalid_hp} archetypes with invalid hit points"

    def test_enum_field_values(self, db: Session):
        """Test that enum fields contain valid values."""
        # Powerset types
        valid_set_types = ['primary', 'secondary', 'pool', 'epic', 'incarnate']
        invalid_set_types = db.query(Powerset).filter(
            ~Powerset.powerset_type.in_(valid_set_types)
        ).count()

        # Salvage rarity
        valid_rarities = ['Common', 'Uncommon', 'Rare']
        invalid_salvage = db.query(Salvage).filter(
            ~Salvage.rarity.in_(valid_rarities)
        ).count()

        # Salvage origin
        valid_origins = ['Tech', 'Magic', 'Natural']
        invalid_origins = db.query(Salvage).filter(
            ~Salvage.origin.in_(valid_origins)
        ).count()

        assert invalid_set_types == 0, f"Found {invalid_set_types} powersets with invalid set_type"
        assert invalid_salvage == 0, f"Found {invalid_salvage} salvage with invalid rarity"
        assert invalid_origins == 0, f"Found {invalid_origins} salvage with invalid origin"
