"""add_i12_power_data_optimizations

Revision ID: 0236d1f741c9
Revises: ebb093a41e89
Create Date: 2025-07-19 04:07:56.584362

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0236d1f741c9"
down_revision: str | Sequence[str] | None = "ebb093a41e89"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema with I12 power data optimizations.

    NOTE: Most optimizations disabled due to schema changes in PR 309.
    Only keeping ImportLog table creation which is still needed.
    """

    # DISABLED: Composite indexes reference removed columns
    # (internal_name, power_type, level_available, etc. don't exist in new schema)

    # DISABLED: GIN indexes reference removed columns (effects, effect_groups)

    # DISABLED: Covering index references removed columns

    # DISABLED: Materialized view references removed columns and table structure

    # Create import log table for tracking large imports
    # This is the only part that still applies to the current schema
    # Check if table exists first (it may have been created manually)
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if "import_logs" not in tables:
        op.create_table(
            "import_logs",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("import_type", sa.String(length=50), nullable=True),
            sa.Column("source_file", sa.String(length=255), nullable=True),
            sa.Column("game_version", sa.String(length=50), nullable=True),
            sa.Column("records_processed", sa.Integer(), nullable=True),
            sa.Column("records_imported", sa.Integer(), nullable=True),
            sa.Column("errors", sa.Integer(), nullable=True),
            sa.Column("import_data", sa.JSON(), nullable=True),
            sa.Column("started_at", sa.DateTime(), nullable=True),
            sa.Column("completed_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )

        op.create_index(
            "idx_import_logs_type", "import_logs", ["import_type"], unique=False
        )

        op.create_index(
            "idx_import_logs_date", "import_logs", ["started_at"], unique=False
        )


def downgrade() -> None:
    """Downgrade schema by removing I12 optimizations."""

    # Drop import logs table (only part that was actually created)
    op.drop_index("idx_import_logs_date", table_name="import_logs")
    op.drop_index("idx_import_logs_type", table_name="import_logs")
    op.drop_table("import_logs")

    # DISABLED: All other drops reference indexes/views that were never created
