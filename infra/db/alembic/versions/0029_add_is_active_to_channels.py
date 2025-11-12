"""Add is_active column to channels table

Revision ID: 0029_add_is_active
Revises: 0028
Create Date: 2025-01-13 12:00:00.000000

This migration adds an is_active column to track whether a channel is active or suspended.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0029"
down_revision: str | Sequence[str] | None = "0028"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add is_active column to channels table."""

    # Add is_active column (default true, not null)
    op.add_column(
        "channels", sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true")
    )

    # Add index for efficient queries (filtering by active/inactive channels)
    op.create_index("idx_channels_is_active", "channels", ["is_active"])

    # Add comment for documentation
    op.execute("""
        COMMENT ON COLUMN channels.is_active IS
        'Whether the channel is active (true) or suspended (false). Used for filtering and status management.'
    """)


def downgrade() -> None:
    """Remove is_active column and index."""

    # Drop index
    op.drop_index("idx_channels_is_active", table_name="channels")

    # Drop column
    op.drop_column("channels", "is_active")
