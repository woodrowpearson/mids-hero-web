"""Initial database schema for City of Heroes data model

Revision ID: 4b9678b90f10
Revises: 
Create Date: 2025-07-13 22:30:02.969018

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4b9678b90f10'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create archetypes table
    op.create_table(
        'archetypes',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True, index=True),
        sa.Column('description', sa.Text()),
        sa.Column('display_name', sa.String(100)),
        sa.Column('primary_group', sa.String(50)),
        sa.Column('secondary_group', sa.String(50)),
        sa.Column('hit_points_base', sa.Integer()),
        sa.Column('hit_points_max', sa.Integer()),
        sa.Column('inherent_power_id', sa.Integer()),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('idx_archetype_groups', 'archetypes', ['primary_group', 'secondary_group'])

    # Create powersets table
    op.create_table(
        'powersets',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String(100), nullable=False, index=True),
        sa.Column('display_name', sa.String(100)),
        sa.Column('description', sa.Text()),
        sa.Column('archetype_id', sa.Integer(), sa.ForeignKey('archetypes.id'), nullable=False),
        sa.Column('powerset_type', sa.String(20), nullable=False),
        sa.Column('icon_path', sa.String(255)),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('idx_powerset_type', 'powersets', ['powerset_type'])
    op.create_unique_constraint('uq_powerset_archetype_type', 'powersets', ['name', 'archetype_id', 'powerset_type'])

    # Create powers table
    op.create_table(
        'powers',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String(100), nullable=False, index=True),
        sa.Column('display_name', sa.String(100)),
        sa.Column('description', sa.Text()),
        sa.Column('powerset_id', sa.Integer(), sa.ForeignKey('powersets.id'), nullable=False),
        sa.Column('level_available', sa.Integer(), default=1),
        sa.Column('power_type', sa.String(50)),
        sa.Column('target_type', sa.String(50)),
        sa.Column('accuracy', sa.Numeric(5, 2), default=1.0),
        sa.Column('damage_scale', sa.Numeric(5, 2)),
        sa.Column('endurance_cost', sa.Numeric(5, 2)),
        sa.Column('recharge_time', sa.Numeric(6, 2)),
        sa.Column('activation_time', sa.Numeric(4, 2)),
        sa.Column('range_feet', sa.Integer()),
        sa.Column('radius_feet', sa.Integer()),
        sa.Column('max_targets', sa.Integer()),
        sa.Column('effects', sa.JSON()),
        sa.Column('icon_path', sa.String(255)),
        sa.Column('display_order', sa.Integer()),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('idx_power_level', 'powers', ['level_available'])
    op.create_index('idx_power_type', 'powers', ['power_type'])

    # Create power_prerequisites table
    op.create_table(
        'power_prerequisites',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('power_id', sa.Integer(), sa.ForeignKey('powers.id'), nullable=False),
        sa.Column('required_power_id', sa.Integer(), sa.ForeignKey('powers.id'), nullable=False),
        sa.Column('required_level', sa.Integer()),
        sa.Column('prerequisite_type', sa.String(20)),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
    )
    op.create_index('idx_prereq_power', 'power_prerequisites', ['power_id'])
    op.create_index('idx_prereq_required', 'power_prerequisites', ['required_power_id'])

    # Create enhancement_sets table
    op.create_table(
        'enhancement_sets',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('display_name', sa.String(100)),
        sa.Column('description', sa.Text()),
        sa.Column('min_level', sa.Integer(), default=10),
        sa.Column('max_level', sa.Integer(), default=50),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Create enhancements table
    op.create_table(
        'enhancements',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String(100), nullable=False, index=True),
        sa.Column('display_name', sa.String(100)),
        sa.Column('enhancement_type', sa.String(50), index=True),
        sa.Column('set_id', sa.Integer(), sa.ForeignKey('enhancement_sets.id')),
        sa.Column('level_min', sa.Integer(), default=1),
        sa.Column('level_max', sa.Integer(), default=50),
        sa.Column('accuracy_bonus', sa.Numeric(5, 2)),
        sa.Column('damage_bonus', sa.Numeric(5, 2)),
        sa.Column('endurance_bonus', sa.Numeric(5, 2)),
        sa.Column('recharge_bonus', sa.Numeric(5, 2)),
        sa.Column('defense_bonus', sa.Numeric(5, 2)),
        sa.Column('resistance_bonus', sa.Numeric(5, 2)),
        sa.Column('other_bonuses', sa.JSON()),
        sa.Column('unique_enhancement', sa.Boolean(), default=False),
        sa.Column('icon_path', sa.String(255)),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('idx_enhancement_level', 'enhancements', ['level_min', 'level_max'])

    # Create set_bonuses table
    op.create_table(
        'set_bonuses',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('set_id', sa.Integer(), sa.ForeignKey('enhancement_sets.id'), nullable=False),
        sa.Column('pieces_required', sa.Integer(), nullable=False, index=True),
        sa.Column('bonus_description', sa.Text()),
        sa.Column('bonus_type', sa.String(50)),
        sa.Column('bonus_amount', sa.Numeric(5, 2)),
        sa.Column('bonus_details', sa.JSON()),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
    )
    op.create_index('idx_set_bonus_set', 'set_bonuses', ['set_id'])

    # Create power_enhancement_compatibility table
    op.create_table(
        'power_enhancement_compatibility',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('power_id', sa.Integer(), sa.ForeignKey('powers.id'), nullable=False),
        sa.Column('enhancement_type', sa.String(50), nullable=False),
        sa.Column('allowed', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
    )
    op.create_index('idx_compat_power', 'power_enhancement_compatibility', ['power_id'])
    op.create_index('idx_compat_type', 'power_enhancement_compatibility', ['enhancement_type'])
    op.create_unique_constraint('uq_power_enhancement_type', 'power_enhancement_compatibility', ['power_id', 'enhancement_type'])

    # Create builds table
    op.create_table(
        'builds',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('archetype_id', sa.Integer(), sa.ForeignKey('archetypes.id'), nullable=False),
        sa.Column('primary_powerset_id', sa.Integer(), sa.ForeignKey('powersets.id'), nullable=False),
        sa.Column('secondary_powerset_id', sa.Integer(), sa.ForeignKey('powersets.id'), nullable=False),
        sa.Column('user_id', sa.Integer()),
        sa.Column('level', sa.Integer(), default=1),
        sa.Column('build_data', sa.JSON()),
        sa.Column('is_public', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('idx_build_user', 'builds', ['user_id'])
    op.create_index('idx_build_public', 'builds', ['is_public'])

    # Create build_powers table
    op.create_table(
        'build_powers',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('build_id', sa.Integer(), sa.ForeignKey('builds.id', ondelete='CASCADE'), nullable=False),
        sa.Column('power_id', sa.Integer(), sa.ForeignKey('powers.id'), nullable=False),
        sa.Column('level_taken', sa.Integer(), nullable=False),
        sa.Column('slot_count', sa.Integer(), default=1),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
    )
    op.create_index('idx_build_power_build', 'build_powers', ['build_id'])
    op.create_index('idx_build_power_power', 'build_powers', ['power_id'])

    # Create build_enhancements table
    op.create_table(
        'build_enhancements',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('build_power_id', sa.Integer(), sa.ForeignKey('build_powers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('enhancement_id', sa.Integer(), sa.ForeignKey('enhancements.id'), nullable=False),
        sa.Column('slot_number', sa.Integer(), nullable=False),
        sa.Column('enhancement_level', sa.Integer(), default=50),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
    )
    op.create_index('idx_build_enh_power', 'build_enhancements', ['build_power_id'])
    op.create_index('idx_build_enh_enhancement', 'build_enhancements', ['enhancement_id'])

    # Create import_logs table
    op.create_table(
        'import_logs',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('import_type', sa.String(50)),
        sa.Column('source_file', sa.String(255)),
        sa.Column('game_version', sa.String(50)),
        sa.Column('records_processed', sa.Integer()),
        sa.Column('records_imported', sa.Integer()),
        sa.Column('errors', sa.Integer()),
        sa.Column('import_data', sa.JSON()),
        sa.Column('started_at', sa.DateTime()),
        sa.Column('completed_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
    )

    # Add foreign key constraints that reference powers table after it's created
    op.create_foreign_key('fk_archetype_inherent_power', 'archetypes', 'powers', ['inherent_power_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop tables in reverse order to avoid foreign key constraints
    op.drop_table('import_logs')
    op.drop_table('build_enhancements')
    op.drop_table('build_powers')
    op.drop_table('builds')
    op.drop_table('power_enhancement_compatibility')
    op.drop_table('set_bonuses')
    op.drop_table('enhancements')
    op.drop_table('enhancement_sets')
    op.drop_table('power_prerequisites')
    op.drop_table('powers')
    op.drop_table('powersets')
    op.drop_table('archetypes')
