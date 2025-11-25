"""Create user_alert_preferences table

Revision ID: 0034
Revises: 0033
Create Date: 2025-11-21 00:00:00.000000

USER ALERT PREFERENCES MIGRATION:
This migration creates the user_alert_preferences table to store
user-specific alert settings and preferences.

Features:
- Alert frequency control (immediate, daily, weekly)
- Severity filtering (all, high, critical)
- Quiet hours configuration
- Channel-specific muting
- Notification channel preferences (telegram, email, web_push)

Schema:
- user_id: User who owns these preferences
- alert_frequency: How often to send alerts
- min_severity: Minimum severity level to notify
- quiet_hours_start: Start of quiet period (hour 0-23)
- quiet_hours_end: End of quiet period (hour 0-23)
- timezone: User's timezone for quiet hours
- enabled: Master on/off switch
- telegram_enabled: Send via Telegram
- email_enabled: Send via email
- web_push_enabled: Send via web push
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0034"
down_revision = "0033"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create user_alert_preferences table"""
    op.create_table(
        "user_alert_preferences",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False, unique=True),
        sa.Column(
            "alert_frequency",
            sa.String(20),
            nullable=False,
            server_default="immediate",
            comment="immediate, daily, weekly",
        ),
        sa.Column(
            "min_severity",
            sa.String(20),
            nullable=False,
            server_default="medium",
            comment="low, medium, high, critical",
        ),
        sa.Column("quiet_hours_start", sa.Integer(), nullable=True, comment="Hour 0-23"),
        sa.Column("quiet_hours_end", sa.Integer(), nullable=True, comment="Hour 0-23"),
        sa.Column("timezone", sa.String(50), nullable=False, server_default="UTC"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "telegram_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "email_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "web_push_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
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
        sa.PrimaryKeyConstraint("id"),
    )

    # Index for quick user lookup
    op.create_index(
        "ix_user_alert_preferences_user_id",
        "user_alert_preferences",
        ["user_id"],
        unique=True,
    )

    # Create muted_channels table for channel-specific muting
    op.create_table(
        "muted_channels",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("channel_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "muted_until",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="NULL = permanently muted",
        ),
        sa.Column("reason", sa.String(100), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "channel_id", name="uq_user_channel_mute"),
    )

    # Index for checking if channel is muted
    op.create_index(
        "ix_muted_channels_user_channel",
        "muted_channels",
        ["user_id", "channel_id"],
    )

    # Index for cleanup of expired mutes
    op.create_index(
        "ix_muted_channels_muted_until",
        "muted_channels",
        ["muted_until"],
    )


def downgrade() -> None:
    """Drop user alert preferences tables"""
    op.drop_index("ix_muted_channels_muted_until", table_name="muted_channels")
    op.drop_index("ix_muted_channels_user_channel", table_name="muted_channels")
    op.drop_table("muted_channels")

    op.drop_index("ix_user_alert_preferences_user_id", table_name="user_alert_preferences")
    op.drop_table("user_alert_preferences")
