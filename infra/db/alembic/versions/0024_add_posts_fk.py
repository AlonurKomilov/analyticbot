"""Add foreign key constraint to posts table

Revision ID: 0027_add_posts_fk
Revises: 0023_create_mtproto_posts_table
Create Date: 2025-11-06 10:00:00.000000

This migration adds referential integrity between posts and channels tables.
"""

from alembic import op

revision = "0027"
down_revision = "0023"  # Correctly references migration 0023
branch_labels = None
depends_on = None


def upgrade():
    """Add foreign key constraint to posts.channel_id

    This ensures:
    1. All posts belong to valid channels
    2. Posts are automatically deleted when channel is deleted (CASCADE)
    3. Database enforces referential integrity
    """

    # First, clean up any orphaned posts (posts without matching channels)
    # This should not happen in practice, but ensures migration won't fail
    op.execute(
        """
        DELETE FROM posts
        WHERE channel_id NOT IN (SELECT id FROM channels)
    """
    )

    # Add foreign key constraint with CASCADE delete
    # When a channel is deleted, all its posts are automatically deleted
    op.create_foreign_key(
        "fk_posts_channel_id",
        "posts",
        "channels",
        ["channel_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade():
    """Remove foreign key constraint"""
    op.drop_constraint("fk_posts_channel_id", "posts", type_="foreignkey")
