"""Add soft delete columns to posts table

Revision ID: 0026
Revises: 0025
Create Date: 2025-11-10 07:30:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0026"
down_revision = "0025"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add is_deleted and deleted_at columns to posts table for soft delete functionality."""

    # Add is_deleted boolean column (default FALSE)
    op.add_column(
        "posts",
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default="false"),
    )

    # Add deleted_at timestamp column (nullable, only set when deleted)
    op.add_column("posts", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))

    # Add index on is_deleted for faster queries filtering deleted posts
    op.create_index("idx_posts_is_deleted", "posts", ["is_deleted"])

    # Add composite index for channel_id + is_deleted for efficient channel queries
    op.create_index("idx_posts_channel_not_deleted", "posts", ["channel_id", "is_deleted"])


def downgrade() -> None:
    """Remove soft delete columns and indexes."""

    # Drop indexes
    op.drop_index("idx_posts_channel_not_deleted", table_name="posts")
    op.drop_index("idx_posts_is_deleted", table_name="posts")

    # Drop columns
    op.drop_column("posts", "deleted_at")
    op.drop_column("posts", "is_deleted")
