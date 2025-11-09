"""Add user_bot_credentials and admin_bot_actions tables for multi-tenant bot system

Revision ID: 0019_add_user_bot_credentials
Revises: 0018_migrate_roles_to_5_tier_system
Create Date: 2025-10-27 00:00:00.000000

MULTI-TENANT BOT SYSTEM MIGRATION:
This migration adds support for isolated bot instances per user.
Each user can have their own dedicated Telegram bot and MTProto client.

Features:
- user_bot_credentials: Store encrypted bot tokens and MTProto credentials per user
- admin_bot_actions: Audit log for admin actions on user bots
- One bot per user constraint
- Rate limiting per bot
- Admin control and monitoring

REQUIREMENTS:
1. ENCRYPTION_KEY must be set in environment before using this feature
2. Users will need to provide their own bot tokens from @BotFather
3. Users will need API credentials from https://my.telegram.org
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0019_add_user_bot_credentials"
down_revision = "0018"  # Fixed: matches actual revision ID
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create user_bot_credentials and admin_bot_actions tables"""

    # Create user_bot_credentials table
    op.create_table(
        "user_bot_credentials",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        # Telegram Bot credentials (encrypted)
        sa.Column("bot_token", sa.String(255), nullable=False),
        sa.Column("bot_username", sa.String(255), nullable=True),
        sa.Column("bot_id", sa.BigInteger(), nullable=True),
        # MTProto credentials (api_hash is encrypted)
        sa.Column("telegram_api_id", sa.Integer(), nullable=False),
        sa.Column("telegram_api_hash", sa.String(255), nullable=False),
        sa.Column("telegram_phone", sa.String(20), nullable=True),
        sa.Column("session_string", sa.Text(), nullable=True),
        # Status & Control
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default="false"),
        # Ownership
        sa.Column("created_by_user_id", sa.BigInteger(), nullable=True),
        sa.Column("managed_by_admin_id", sa.BigInteger(), nullable=True),
        # Rate limiting
        sa.Column("rate_limit_rps", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("max_concurrent_requests", sa.Integer(), nullable=False, server_default="3"),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        # Primary key
        sa.PrimaryKeyConstraint("id"),
        # Foreign keys
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        # Unique constraints
        sa.UniqueConstraint("user_id", name="one_bot_per_user"),
        sa.UniqueConstraint("bot_token", name="unique_bot_token"),
        sa.UniqueConstraint("bot_username", name="unique_bot_username"),
    )

    # Create indexes for user_bot_credentials
    op.create_index("idx_bot_credentials_user_id", "user_bot_credentials", ["user_id"])
    op.create_index("idx_bot_credentials_status", "user_bot_credentials", ["status"])
    op.create_index("idx_bot_credentials_admin", "user_bot_credentials", ["managed_by_admin_id"])
    op.create_index("idx_bot_credentials_created_at", "user_bot_credentials", ["created_at"])

    # Create admin_bot_actions table for audit logging
    op.create_table(
        "admin_bot_actions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("admin_id", sa.BigInteger(), nullable=False),
        sa.Column("target_user_id", sa.BigInteger(), nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("details", postgresql.JSONB(), nullable=True),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        # Primary key
        sa.PrimaryKeyConstraint("id"),
        # Foreign keys
        sa.ForeignKeyConstraint(["target_user_id"], ["users.id"], ondelete="CASCADE"),
    )

    # Create indexes for admin_bot_actions
    op.create_index("idx_admin_actions_admin_id", "admin_bot_actions", ["admin_id"])
    op.create_index("idx_admin_actions_target_user_id", "admin_bot_actions", ["target_user_id"])
    op.create_index("idx_admin_actions_timestamp", "admin_bot_actions", ["timestamp"])
    op.create_index("idx_admin_actions_action", "admin_bot_actions", ["action"])


def downgrade() -> None:
    """Drop user_bot_credentials and admin_bot_actions tables"""

    # Drop admin_bot_actions indexes
    op.drop_index("idx_admin_actions_action", table_name="admin_bot_actions")
    op.drop_index("idx_admin_actions_timestamp", table_name="admin_bot_actions")
    op.drop_index("idx_admin_actions_target_user_id", table_name="admin_bot_actions")
    op.drop_index("idx_admin_actions_admin_id", table_name="admin_bot_actions")

    # Drop admin_bot_actions table
    op.drop_table("admin_bot_actions")

    # Drop user_bot_credentials indexes
    op.drop_index("idx_bot_credentials_created_at", table_name="user_bot_credentials")
    op.drop_index("idx_bot_credentials_admin", table_name="user_bot_credentials")
    op.drop_index("idx_bot_credentials_status", table_name="user_bot_credentials")
    op.drop_index("idx_bot_credentials_user_id", table_name="user_bot_credentials")

    # Drop user_bot_credentials table
    op.drop_table("user_bot_credentials")
