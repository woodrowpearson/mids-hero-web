"""Add source_metadata field to Power model

Revision ID: 5b383233c28f
Revises: 0236d1f741c9
Create Date: 2025-11-06 19:07:00.576565

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5b383233c28f'
down_revision: Union[str, Sequence[str], None] = '0236d1f741c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add source_metadata JSON field to powers table."""
    op.add_column(
        "powers",
        sa.Column("source_metadata", sa.JSON(), nullable=True, comment="Raw JSON from source"),
    )


def downgrade() -> None:
    """Remove source_metadata field from powers table."""
    op.drop_column("powers", "source_metadata")
