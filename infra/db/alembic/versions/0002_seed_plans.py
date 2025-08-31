"""Seed plans

Revision ID: 0002
Revises: 0001
Create Date: 2025-08-16 22:37:55.770145

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002_seed_plans"
down_revision: str | Sequence[str] | None = "0001_initial_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.bulk_insert(
        sa.table(
            "plans",
            sa.column("name", sa.String),
            sa.column("max_channels", sa.Integer),
            sa.column("max_posts_per_month", sa.Integer),
        ),
        [
            {"name": "free", "max_channels": 1, "max_posts_per_month": 30},
            {"name": "pro", "max_channels": 3, "max_posts_per_month": 200},
            {"name": "business", "max_channels": 10, "max_posts_per_month": 2000},
        ],
    )


def downgrade() -> None:
    op.execute("DELETE FROM plans WHERE name IN ('free', 'pro', 'business')")
