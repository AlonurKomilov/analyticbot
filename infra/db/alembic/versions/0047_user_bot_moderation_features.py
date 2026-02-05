"""Add user bot moderation feature tables.

Revision ID: 0047_user_bot_moderation
Revises: 0046_add_bot_role
Create Date: 2025-12-12 10:00:00.000000

This migration adds tables for user bot moderation features:
- user_bot_settings: Per-user bot feature settings
- user_bot_banned_words: Custom banned word lists
- user_bot_invite_tracking: Track who invited whom
- user_bot_warnings: User warning history
- user_bot_moderation_log: Audit log for moderation actions
- user_bot_welcome_messages: Custom welcome templates
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = "0047_bot_moderation"
down_revision = "0046_add_bot_role"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create user bot moderation feature tables."""

    # ===========================================
    # 1. User Bot Settings Table
    # ===========================================
    op.create_table(
        "user_bot_settings",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("user_id", sa.BigInteger, nullable=False, index=True),
        sa.Column("chat_id", sa.BigInteger, nullable=False, comment="Telegram chat/channel ID"),
        sa.Column(
            "chat_type",
            sa.String(20),
            nullable=False,
            default="group",
            comment="Type: group, supergroup, channel",
        ),
        sa.Column("chat_title", sa.String(255), nullable=True),
        # Feature toggles
        sa.Column(
            "clean_join_messages",
            sa.Boolean,
            nullable=False,
            server_default="false",
            comment="Auto-delete join/leave service messages",
        ),
        sa.Column(
            "clean_leave_messages",
            sa.Boolean,
            nullable=False,
            server_default="false",
            comment="Auto-delete leave service messages",
        ),
        sa.Column(
            "banned_words_enabled",
            sa.Boolean,
            nullable=False,
            server_default="false",
            comment="Enable banned words filter",
        ),
        sa.Column(
            "anti_spam_enabled",
            sa.Boolean,
            nullable=False,
            server_default="false",
            comment="Enable anti-spam protection",
        ),
        sa.Column(
            "anti_link_enabled",
            sa.Boolean,
            nullable=False,
            server_default="false",
            comment="Block external links",
        ),
        sa.Column(
            "anti_forward_enabled",
            sa.Boolean,
            nullable=False,
            server_default="false",
            comment="Block forwarded messages",
        ),
        sa.Column(
            "welcome_enabled",
            sa.Boolean,
            nullable=False,
            server_default="false",
            comment="Send welcome message to new members",
        ),
        sa.Column(
            "invite_tracking_enabled",
            sa.Boolean,
            nullable=False,
            server_default="false",
            comment="Track who invited whom",
        ),
        sa.Column(
            "captcha_enabled",
            sa.Boolean,
            nullable=False,
            server_default="false",
            comment="Require captcha for new members",
        ),
        sa.Column(
            "slow_mode_enabled",
            sa.Boolean,
            nullable=False,
            server_default="false",
            comment="Dynamic slow mode based on activity",
        ),
        sa.Column(
            "night_mode_enabled",
            sa.Boolean,
            nullable=False,
            server_default="false",
            comment="Mute chat during specified hours",
        ),
        # Anti-spam settings
        sa.Column(
            "spam_action",
            sa.String(20),
            nullable=False,
            server_default="warn",
            comment="Action on spam: warn, mute, kick, ban",
        ),
        sa.Column(
            "max_warnings",
            sa.Integer,
            nullable=False,
            server_default="3",
            comment="Max warnings before action",
        ),
        sa.Column(
            "warning_action",
            sa.String(20),
            nullable=False,
            server_default="mute",
            comment="Action after max warnings: mute, kick, ban",
        ),
        sa.Column(
            "mute_duration_minutes",
            sa.Integer,
            nullable=False,
            server_default="60",
            comment="Mute duration in minutes",
        ),
        # Anti-flood settings
        sa.Column(
            "flood_limit",
            sa.Integer,
            nullable=False,
            server_default="5",
            comment="Max messages per flood_interval",
        ),
        sa.Column(
            "flood_interval_seconds",
            sa.Integer,
            nullable=False,
            server_default="10",
            comment="Time window for flood detection",
        ),
        # Night mode settings
        sa.Column(
            "night_mode_start_hour",
            sa.Integer,
            nullable=True,
            comment="Night mode start hour (0-23)",
        ),
        sa.Column(
            "night_mode_end_hour",
            sa.Integer,
            nullable=True,
            comment="Night mode end hour (0-23)",
        ),
        sa.Column(
            "night_mode_timezone",
            sa.String(50),
            nullable=True,
            server_default="'UTC'",
            comment="Timezone for night mode",
        ),
        # Allowed users/admins (JSON arrays of user IDs)
        sa.Column(
            "whitelisted_users",
            JSONB,
            nullable=True,
            comment="User IDs exempt from moderation",
        ),
        sa.Column(
            "admin_users",
            JSONB,
            nullable=True,
            comment="User IDs with admin permissions",
        ),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        # Constraints
        sa.UniqueConstraint("user_id", "chat_id", name="unique_user_chat_settings"),
    )

    # ===========================================
    # 2. Banned Words Table
    # ===========================================
    op.create_table(
        "user_bot_banned_words",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("user_id", sa.BigInteger, nullable=False, index=True),
        sa.Column(
            "chat_id",
            sa.BigInteger,
            nullable=True,
            comment="NULL means applies to all user's chats",
        ),
        sa.Column("word", sa.String(100), nullable=False, comment="Banned word or phrase"),
        sa.Column(
            "is_regex",
            sa.Boolean,
            nullable=False,
            server_default="false",
            comment="Treat word as regex pattern",
        ),
        sa.Column(
            "action",
            sa.String(20),
            nullable=False,
            server_default="delete",
            comment="Action: delete, warn, mute, kick, ban",
        ),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Index("idx_banned_words_user_chat", "user_id", "chat_id"),
        sa.Index("idx_banned_words_active", "user_id", "is_active"),
    )

    # ===========================================
    # 3. Invite Tracking Table
    # ===========================================
    op.create_table(
        "user_bot_invite_tracking",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column(
            "user_id",
            sa.BigInteger,
            nullable=False,
            index=True,
            comment="Bot owner user ID",
        ),
        sa.Column("chat_id", sa.BigInteger, nullable=False, index=True),
        sa.Column(
            "inviter_tg_id",
            sa.BigInteger,
            nullable=False,
            comment="Telegram ID of user who invited",
        ),
        sa.Column("inviter_username", sa.String(255), nullable=True),
        sa.Column("inviter_name", sa.String(255), nullable=True),
        sa.Column(
            "invited_tg_id",
            sa.BigInteger,
            nullable=False,
            comment="Telegram ID of invited user",
        ),
        sa.Column("invited_username", sa.String(255), nullable=True),
        sa.Column("invited_name", sa.String(255), nullable=True),
        sa.Column(
            "invite_link",
            sa.String(255),
            nullable=True,
            comment="Invite link used if any",
        ),
        sa.Column(
            "joined_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "left_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="When user left the chat",
        ),
        sa.Column("is_still_member", sa.Boolean, nullable=False, server_default="true"),
        sa.Index("idx_invite_tracking_inviter", "user_id", "chat_id", "inviter_tg_id"),
        sa.Index("idx_invite_tracking_invited", "user_id", "chat_id", "invited_tg_id"),
    )

    # ===========================================
    # 4. Warnings Table
    # ===========================================
    op.create_table(
        "user_bot_warnings",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column(
            "user_id",
            sa.BigInteger,
            nullable=False,
            index=True,
            comment="Bot owner user ID",
        ),
        sa.Column("chat_id", sa.BigInteger, nullable=False),
        sa.Column(
            "warned_tg_id",
            sa.BigInteger,
            nullable=False,
            comment="Telegram ID of warned user",
        ),
        sa.Column("warned_username", sa.String(255), nullable=True),
        sa.Column("warned_name", sa.String(255), nullable=True),
        sa.Column("reason", sa.String(500), nullable=False),
        sa.Column(
            "warning_type",
            sa.String(50),
            nullable=False,
            comment="Type: spam, banned_word, flood, manual",
        ),
        sa.Column(
            "message_id",
            sa.BigInteger,
            nullable=True,
            comment="Original message ID if applicable",
        ),
        sa.Column(
            "message_text",
            sa.Text,
            nullable=True,
            comment="Snippet of problematic content",
        ),
        sa.Column(
            "action_taken",
            sa.String(50),
            nullable=True,
            comment="Action taken: none, deleted, muted, kicked, banned",
        ),
        sa.Column(
            "is_active",
            sa.Boolean,
            nullable=False,
            server_default="true",
            comment="Can be reset/removed by admin",
        ),
        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="When warning expires",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "created_by_tg_id",
            sa.BigInteger,
            nullable=True,
            comment="Admin who issued manual warning",
        ),
        sa.Index("idx_warnings_chat_user", "user_id", "chat_id", "warned_tg_id"),
        sa.Index("idx_warnings_active", "user_id", "chat_id", "is_active"),
    )

    # ===========================================
    # 5. Moderation Log Table
    # ===========================================
    op.create_table(
        "user_bot_moderation_log",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column(
            "user_id",
            sa.BigInteger,
            nullable=False,
            index=True,
            comment="Bot owner user ID",
        ),
        sa.Column("chat_id", sa.BigInteger, nullable=False, index=True),
        sa.Column(
            "action",
            sa.String(50),
            nullable=False,
            comment="Action: message_deleted, user_warned, user_muted, user_kicked, user_banned, settings_changed",
        ),
        sa.Column(
            "target_tg_id",
            sa.BigInteger,
            nullable=True,
            comment="Telegram ID of affected user",
        ),
        sa.Column("target_username", sa.String(255), nullable=True),
        sa.Column(
            "performed_by",
            sa.String(50),
            nullable=False,
            comment="bot_auto, admin_manual, system",
        ),
        sa.Column(
            "performed_by_tg_id",
            sa.BigInteger,
            nullable=True,
            comment="Admin Telegram ID if manual",
        ),
        sa.Column("reason", sa.String(500), nullable=True),
        sa.Column(
            "details",
            JSONB,
            nullable=True,
            comment="Additional context: message content, rule triggered, etc.",
        ),
        sa.Column("message_id", sa.BigInteger, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            index=True,
        ),
    )

    # ===========================================
    # 6. Welcome Messages Table
    # ===========================================
    op.create_table(
        "user_bot_welcome_messages",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("user_id", sa.BigInteger, nullable=False, index=True),
        sa.Column("chat_id", sa.BigInteger, nullable=False),
        sa.Column(
            "message_type",
            sa.String(20),
            nullable=False,
            server_default="'welcome'",
            comment="Type: welcome, goodbye, rules",
        ),
        sa.Column(
            "message_text",
            sa.Text,
            nullable=False,
            comment="Message template with placeholders",
        ),
        sa.Column(
            "parse_mode",
            sa.String(20),
            nullable=False,
            server_default="'HTML'",
            comment="HTML, Markdown, MarkdownV2",
        ),
        sa.Column("buttons", JSONB, nullable=True, comment="Inline keyboard buttons"),
        sa.Column(
            "media_type",
            sa.String(20),
            nullable=True,
            comment="photo, video, animation, sticker",
        ),
        sa.Column("media_file_id", sa.String(255), nullable=True),
        sa.Column(
            "delete_after_seconds",
            sa.Integer,
            nullable=True,
            comment="Auto-delete welcome message after N seconds",
        ),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        sa.UniqueConstraint(
            "user_id", "chat_id", "message_type", name="unique_user_chat_message_type"
        ),
    )

    # ===========================================
    # Indexes for performance
    # ===========================================
    op.create_index(
        "idx_moderation_log_date_range",
        "user_bot_moderation_log",
        ["user_id", "chat_id", "created_at"],
    )

    op.create_index(
        "idx_invite_stats",
        "user_bot_invite_tracking",
        ["user_id", "chat_id", "inviter_tg_id", "is_still_member"],
    )


def downgrade() -> None:
    """Drop user bot moderation feature tables."""
    op.drop_table("user_bot_welcome_messages")
    op.drop_table("user_bot_moderation_log")
    op.drop_table("user_bot_warnings")
    op.drop_table("user_bot_invite_tracking")
    op.drop_table("user_bot_banned_words")
    op.drop_table("user_bot_settings")
