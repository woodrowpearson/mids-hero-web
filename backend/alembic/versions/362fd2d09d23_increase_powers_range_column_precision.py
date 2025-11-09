"""increase_powers_range_column_precision

Revision ID: 362fd2d09d23
Revises: 61efac8da504
Create Date: 2025-11-09 08:53:25.637964

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '362fd2d09d23'
down_revision: str | Sequence[str] | None = '61efac8da504'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema - increase range column precision to handle 10000.0 values."""
    # Increase powers.range from NUMERIC(6,2) to NUMERIC(8,2)
    # This allows values up to 999,999.99 instead of 9,999.99
    op.alter_column(
        'powers',
        'range',
        type_=sa.Numeric(8, 2),
        existing_type=sa.Numeric(6, 2),
        existing_nullable=True
    )


def downgrade() -> None:
    """Downgrade schema - restore original column precision."""
    # NOTE: This will fail if any values > 9999.99 exist in the database
    op.alter_column(
        'powers',
        'range',
        type_=sa.Numeric(6, 2),
        existing_type=sa.Numeric(8, 2),
        existing_nullable=True
    )
