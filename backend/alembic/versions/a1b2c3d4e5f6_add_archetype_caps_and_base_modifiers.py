"""add archetype caps and base modifiers for epic 2.3

Revision ID: a1b2c3d4e5f6
Revises: 0236d1f741c9
Create Date: 2025-11-18 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: str | Sequence[str] | None = "0236d1f741c9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema - add caps and base modifiers to archetypes table."""

    # Base modifiers
    op.add_column(
        "archetypes",
        sa.Column(
            "base_hp",
            sa.Numeric(precision=10, scale=2),
            nullable=True,
            comment="Base HP at level 50",
        ),
    )
    op.add_column(
        "archetypes",
        sa.Column(
            "base_regen",
            sa.Numeric(precision=10, scale=6),
            nullable=True,
            comment="Base regeneration rate",
        ),
    )
    op.add_column(
        "archetypes",
        sa.Column(
            "base_recovery",
            sa.Numeric(precision=10, scale=6),
            nullable=True,
            comment="Base recovery rate",
        ),
    )
    op.add_column(
        "archetypes",
        sa.Column(
            "base_threat",
            sa.Numeric(precision=5, scale=2),
            nullable=True,
            comment="Base threat/aggro modifier",
        ),
    )

    # Archetype caps
    op.add_column(
        "archetypes",
        sa.Column(
            "damage_cap",
            sa.Numeric(precision=5, scale=2),
            nullable=True,
            comment="Damage buff cap",
        ),
    )
    op.add_column(
        "archetypes",
        sa.Column(
            "resistance_cap",
            sa.Numeric(precision=4, scale=2),
            nullable=True,
            comment="Resistance cap",
        ),
    )
    op.add_column(
        "archetypes",
        sa.Column(
            "defense_cap",
            sa.Numeric(precision=4, scale=2),
            nullable=True,
            comment="Defense display cap",
        ),
    )
    op.add_column(
        "archetypes",
        sa.Column(
            "hp_cap",
            sa.Numeric(precision=10, scale=2),
            nullable=True,
            comment="Max HP cap",
        ),
    )
    op.add_column(
        "archetypes",
        sa.Column(
            "regeneration_cap",
            sa.Numeric(precision=5, scale=2),
            nullable=True,
            comment="Regeneration cap",
        ),
    )
    op.add_column(
        "archetypes",
        sa.Column(
            "recovery_cap",
            sa.Numeric(precision=5, scale=2),
            nullable=True,
            comment="Recovery cap",
        ),
    )
    op.add_column(
        "archetypes",
        sa.Column(
            "recharge_cap",
            sa.Numeric(precision=5, scale=2),
            nullable=True,
            comment="Recharge speed cap",
        ),
    )


def downgrade() -> None:
    """Downgrade schema - remove caps and base modifiers from archetypes table."""

    # Remove caps in reverse order
    op.drop_column("archetypes", "recharge_cap")
    op.drop_column("archetypes", "recovery_cap")
    op.drop_column("archetypes", "regeneration_cap")
    op.drop_column("archetypes", "hp_cap")
    op.drop_column("archetypes", "defense_cap")
    op.drop_column("archetypes", "resistance_cap")
    op.drop_column("archetypes", "damage_cap")

    # Remove base modifiers
    op.drop_column("archetypes", "base_threat")
    op.drop_column("archetypes", "base_recovery")
    op.drop_column("archetypes", "base_regen")
    op.drop_column("archetypes", "base_hp")
