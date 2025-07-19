"""add_i12_power_data_optimizations

Revision ID: 0236d1f741c9
Revises: ebb093a41e89
Create Date: 2025-07-19 04:07:56.584362

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0236d1f741c9'
down_revision: Union[str, Sequence[str], None] = 'ebb093a41e89'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema with I12 power data optimizations."""
    
    # Add composite indexes for common query patterns
    op.create_index(
        'idx_power_powerset_level', 
        'powers', 
        ['powerset_id', 'level_available'], 
        unique=False
    )
    
    op.create_index(
        'idx_power_type_level', 
        'powers', 
        ['power_type', 'level_available'], 
        unique=False
    )
    
    op.create_index(
        'idx_power_name_powerset', 
        'powers', 
        ['name', 'powerset_id'], 
        unique=False
    )
    
    op.create_index(
        'idx_power_internal_name', 
        'powers', 
        ['internal_name'], 
        unique=False
    )
    
    # Add GIN indexes for JSON fields (PostgreSQL specific)
    # Note: These will be no-ops on SQLite
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_power_effects 
        ON powers USING GIN (effects)
    """)
    
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_power_effect_groups 
        ON powers USING GIN (effect_groups)
    """)
    
    # Add covering index for build queries (PostgreSQL specific)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_power_build_data 
        ON powers(id, name, level_available, power_type)
        INCLUDE (accuracy, damage_scale, endurance_cost, recharge_time)
    """)
    
    # Create materialized view for power build summary
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS power_build_summary AS
        SELECT 
            p.id,
            p.name,
            p.internal_name,
            p.display_name,
            p.powerset_id,
            ps.name as powerset_name,
            ps.archetype_id,
            a.name as archetype_name,
            p.level_available,
            p.power_type,
            p.target_type,
            p.accuracy,
            p.damage_scale,
            p.endurance_cost,
            p.recharge_time,
            p.activation_time,
            p.range_feet,
            p.max_targets,
            p.icon_path,
            p.display_order
        FROM powers p
        JOIN powersets ps ON p.powerset_id = ps.id
        JOIN archetypes a ON ps.archetype_id = a.id
    """)
    
    # Create index on materialized view
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_power_build_summary_archetype 
        ON power_build_summary(archetype_id, level_available)
    """)
    
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_power_build_summary_powerset 
        ON power_build_summary(powerset_id, level_available)
    """)
    
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_power_build_summary_type 
        ON power_build_summary(power_type, level_available)
    """)
    
    # Create import log table for tracking large imports
    op.create_table(
        'import_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('import_type', sa.String(length=50), nullable=True),
        sa.Column('source_file', sa.String(length=255), nullable=True),
        sa.Column('game_version', sa.String(length=50), nullable=True),
        sa.Column('records_processed', sa.Integer(), nullable=True),
        sa.Column('records_imported', sa.Integer(), nullable=True),
        sa.Column('errors', sa.Integer(), nullable=True),
        sa.Column('import_data', sa.JSON(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    
    op.create_index(
        'idx_import_logs_type', 
        'import_logs', 
        ['import_type'], 
        unique=False
    )
    
    op.create_index(
        'idx_import_logs_date', 
        'import_logs', 
        ['started_at'], 
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema by removing I12 optimizations."""
    
    # Drop import logs table
    op.drop_index('idx_import_logs_date', table_name='import_logs')
    op.drop_index('idx_import_logs_type', table_name='import_logs')
    op.drop_table('import_logs')
    
    # Drop materialized view and its indexes
    op.execute("DROP INDEX IF EXISTS idx_power_build_summary_type")
    op.execute("DROP INDEX IF EXISTS idx_power_build_summary_powerset")
    op.execute("DROP INDEX IF EXISTS idx_power_build_summary_archetype")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS power_build_summary")
    
    # Drop covering index
    op.execute("DROP INDEX IF EXISTS idx_power_build_data")
    
    # Drop GIN indexes
    op.execute("DROP INDEX IF EXISTS idx_power_effect_groups")
    op.execute("DROP INDEX IF EXISTS idx_power_effects")
    
    # Drop composite indexes
    op.drop_index('idx_power_internal_name', table_name='powers')
    op.drop_index('idx_power_name_powerset', table_name='powers')
    op.drop_index('idx_power_type_level', table_name='powers')
    op.drop_index('idx_power_powerset_level', table_name='powers')
