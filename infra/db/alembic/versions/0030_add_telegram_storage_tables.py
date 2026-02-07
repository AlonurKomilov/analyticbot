"""Add Telegram storage tables for user-owned channels

Revision ID: 0030
Revises: 0029
Create Date: 2025-11-14 12:00:00.000000

This migration adds support for using user's own Telegram channels as cloud storage.
Users can connect their private channels to store media files, eliminating server storage costs.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0030"
down_revision: str | Sequence[str] | None = "0029"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create user_storage_channels and telegram_media tables."""

    # Create user_storage_channels table
    op.create_table(
        "user_storage_channels",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("channel_id", sa.BigInteger(), nullable=False),
        sa.Column("channel_title", sa.String(length=255), nullable=True),
        sa.Column("channel_username", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "channel_id", name="uq_user_storage_channel"),
    )

    # Add indexes for user_storage_channels
    op.create_index(
        "idx_user_storage_channels_user_id",
        "user_storage_channels",
        ["user_id"],
    )
    op.create_index(
        "idx_user_storage_channels_channel_id",
        "user_storage_channels",
        ["channel_id"],
    )
    op.create_index(
        "idx_user_storage_channels_active",
        "user_storage_channels",
        ["is_active"],
    )

    # Create telegram_media table
    op.create_table(
        "telegram_media",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("storage_channel_id", sa.Integer(), nullable=False),
        sa.Column("telegram_file_id", sa.String(length=255), nullable=False),
        sa.Column("telegram_message_id", sa.Integer(), nullable=False),
        sa.Column("file_type", sa.String(length=50), nullable=True),  # 'photo', 'video', 'document'
        sa.Column("file_name", sa.String(length=255), nullable=True),
        sa.Column("file_size", sa.BigInteger(), nullable=True),
        sa.Column("mime_type", sa.String(length=100), nullable=True),
        sa.Column("thumbnail_file_id", sa.String(length=255), nullable=True),
        sa.Column("caption", sa.Text(), nullable=True),
        sa.Column("width", sa.Integer(), nullable=True),  # For images/videos
        sa.Column("height", sa.Integer(), nullable=True),  # For images/videos
        sa.Column("duration", sa.Integer(), nullable=True),  # For videos
        sa.Column(
            "uploaded_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column("metadata", sa.JSON(), nullable=True),  # Additional metadata as JSON
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["storage_channel_id"],
            ["user_storage_channels.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Add indexes for telegram_media
    op.create_index(
        "idx_telegram_media_user_id",
        "telegram_media",
        ["user_id"],
    )
    op.create_index(
        "idx_telegram_media_storage_channel_id",
        "telegram_media",
        ["storage_channel_id"],
    )
    op.create_index(
        "idx_telegram_media_file_id",
        "telegram_media",
        ["telegram_file_id"],
    )
    op.create_index(
        "idx_telegram_media_uploaded_at",
        "telegram_media",
        ["uploaded_at"],
    )
    op.create_index(
        "idx_telegram_media_file_type",
        "telegram_media",
        ["file_type"],
    )

    # Composite index for efficient queries
    op.create_index(
        "idx_telegram_media_user_channel",
        "telegram_media",
        ["user_id", "storage_channel_id"],
    )


def downgrade() -> None:
    """Drop telegram_media and user_storage_channels tables."""

    # Drop indexes first
    op.drop_index("idx_telegram_media_user_channel", table_name="telegram_media")
    op.drop_index("idx_telegram_media_file_type", table_name="telegram_media")
    op.drop_index("idx_telegram_media_uploaded_at", table_name="telegram_media")
    op.drop_index("idx_telegram_media_file_id", table_name="telegram_media")
    op.drop_index("idx_telegram_media_storage_channel_id", table_name="telegram_media")
    op.drop_index("idx_telegram_media_user_id", table_name="telegram_media")

    op.drop_index("idx_user_storage_channels_active", table_name="user_storage_channels")
    op.drop_index("idx_user_storage_channels_channel_id", table_name="user_storage_channels")
    op.drop_index("idx_user_storage_channels_user_id", table_name="user_storage_channels")

    # Drop tables
    op.drop_table("telegram_media")
    op.drop_table("user_storage_channels")
