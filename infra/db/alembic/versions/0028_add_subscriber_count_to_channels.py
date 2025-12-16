"""Add subscriber_count column to channels table

Revision ID: 0028_add_subscriber_count
Revises: 0027
Create Date: 2025-11-11 08:00:00.000000

This migration adds a subscriber_count column to track channel subscriber numbers.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0028"
down_revision: str | Sequence[str] | None = "0027"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add subscriber_count column to channels table."""

    # Add subscriber_count column (default 0, not null)
    op.add_column(
        "channels",
        sa.Column("subscriber_count", sa.Integer(), nullable=False, server_default="0"),
    )

    # Add index for efficient queries
    op.create_index("idx_channels_subscriber_count", "channels", ["subscriber_count"])

    # Add comment for documentation
    op.execute(
        """
        COMMENT ON COLUMN channels.subscriber_count IS
        'Number of subscribers/members in the channel (updated by MTProto worker)'
    """
    )


def downgrade() -> None:
    """Remove subscriber_count column and index."""

    # Drop index
    op.drop_index("idx_channels_subscriber_count", table_name="channels")

    # Drop column
    op.drop_column("channels", "subscriber_count")
