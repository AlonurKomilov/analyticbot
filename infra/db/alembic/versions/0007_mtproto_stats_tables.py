"""Add stats_raw and channel_daily tables for MTProto stats loader (Phase 4.3)

Revision ID: 0007_mtproto_stats_tables
Revises: 0006_deliveries_observability
Create Date: 2025-08-31 12:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade():
    """Add stats_raw and channel_daily tables."""
    op.create_table(
        "stats_raw",
        sa.Column("channel_id", sa.BigInteger(), nullable=False),
        sa.Column("key", sa.Text(), nullable=False),
        sa.Column("json", sa.JSON(), nullable=False),
        sa.Column(
            "fetched_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("channel_id", "key", "fetched_at"),
    )

    op.create_table(
        "channel_daily",
        sa.Column("channel_id", sa.BigInteger(), nullable=False),
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("metric", sa.Text(), nullable=False),
        sa.Column("value", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("channel_id", "day", "metric"),
    )


def downgrade():
    """Drop stats_raw and channel_daily tables."""
    op.drop_table("channel_daily")
    op.drop_table("stats_raw")
