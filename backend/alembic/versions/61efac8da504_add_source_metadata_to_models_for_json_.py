"""add source_metadata to models for json import

Revision ID: 61efac8da504
Revises: 5b383233c28f
Create Date: 2025-11-08 16:57:19.135764

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '61efac8da504'
down_revision: str | Sequence[str] | None = '5b383233c28f'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add source_metadata JSON column to archetypes
    op.add_column('archetypes', sa.Column('source_metadata', sa.JSON(), nullable=True, comment='Raw JSON from filtered_data'))

    # Add source_metadata JSON column to enhancement_sets
    op.add_column('enhancement_sets', sa.Column('source_metadata', sa.JSON(), nullable=True, comment='Raw JSON from filtered_data'))

    # Add source_metadata JSON column to enhancements
    op.add_column('enhancements', sa.Column('source_metadata', sa.JSON(), nullable=True, comment='Raw JSON from filtered_data'))

    # Add source_metadata JSON column to powersets
    op.add_column('powersets', sa.Column('source_metadata', sa.JSON(), nullable=True, comment='Raw JSON from filtered_data'))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove source_metadata columns in reverse order
    op.drop_column('powersets', 'source_metadata')
    op.drop_column('enhancements', 'source_metadata')
    op.drop_column('enhancement_sets', 'source_metadata')
    op.drop_column('archetypes', 'source_metadata')
