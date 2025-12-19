"""
0048_marketplace_services_system

Creates tables for marketplace services system where users can purchase
recurring bot/MTProto service subscriptions using credits.

This is SEPARATE from:
- credit_services (per-use AI features, exports)
- marketplace_items (one-time theme/template purchases)

Revision ID: 0048_marketplace_services
Revises: 0047_user_bot_moderation_features
Create Date: 2025-12-14
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision = "0048_marketplace_services"
down_revision = "0047_bot_moderation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create marketplace services system tables"""

    # ============================================
    # Marketplace Services Table
    # Recurring subscription services (anti-spam, auto-delete, etc.)
    # ============================================
    op.create_table(
        "marketplace_services",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("service_key", sa.String(100), nullable=False, unique=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("short_description", sa.String(255), nullable=True),
        # Pricing
        sa.Column("price_credits_monthly", sa.Integer(), nullable=False),
        sa.Column("price_credits_yearly", sa.Integer(), nullable=True),  # NULL = not available
        # Categorization
        sa.Column(
            "category",
            sa.String(50),
            nullable=False,
        ),  # bot_service, bot_automation, mtproto_services, bot_analytics
        sa.Column("subcategory", sa.String(50), nullable=True),
        # Features & Limits
        sa.Column("features", postgresql.JSONB(), nullable=True),  # List of feature descriptions
        sa.Column("usage_quota_daily", sa.Integer(), nullable=True),  # NULL = unlimited
        sa.Column("usage_quota_monthly", sa.Integer(), nullable=True),  # NULL = unlimited
        sa.Column("rate_limit_per_minute", sa.Integer(), nullable=True),  # Service-level rate limit
        # Requirements
        sa.Column(
            "requires_bot", sa.Boolean(), server_default="false", nullable=False
        ),  # Needs bot connected
        sa.Column(
            "requires_mtproto", sa.Boolean(), server_default="false", nullable=False
        ),  # Needs MTProto session
        sa.Column("min_tier", sa.String(20), nullable=True),  # Minimum user tier required
        # Display & Marketing
        sa.Column("icon", sa.String(50), nullable=True),  # Material icon name
        sa.Column("color", sa.String(20), nullable=True),  # Hex color code
        sa.Column("is_featured", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("is_popular", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("is_new", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        # Status
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("is_beta", sa.Boolean(), server_default="false", nullable=False),
        # Metadata
        sa.Column("documentation_url", sa.String(500), nullable=True),
        sa.Column("demo_video_url", sa.String(500), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
        # Stats
        sa.Column("active_subscriptions", sa.Integer(), server_default="0", nullable=False),
        sa.Column("total_subscriptions", sa.Integer(), server_default="0", nullable=False),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_marketplace_services_key",
        "marketplace_services",
        ["service_key"],
        unique=True,
    )
    op.create_index(
        "ix_marketplace_services_category",
        "marketplace_services",
        ["category"],
    )
    op.create_index(
        "ix_marketplace_services_active",
        "marketplace_services",
        ["is_active"],
    )
    op.create_index(
        "ix_marketplace_services_featured",
        "marketplace_services",
        ["is_featured"],
    )

    # ============================================
    # User Service Subscriptions Table
    # Tracks which services each user has subscribed to
    # ============================================
    op.create_table(
        "user_service_subscriptions",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("service_id", sa.Integer(), nullable=False),
        # Subscription details
        sa.Column(
            "billing_cycle",
            sa.String(20),
            nullable=False,
        ),  # monthly, yearly
        sa.Column("price_paid", sa.Integer(), nullable=False),  # Credits paid
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="active",
        ),  # active, paused, cancelled, expired
        # Dates
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_renewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancellation_reason", sa.Text(), nullable=True),
        # Auto-renewal
        sa.Column(
            "auto_renew", sa.Boolean(), server_default="true", nullable=False
        ),  # Auto-renew on expiry
        sa.Column("renewal_attempts", sa.Integer(), server_default="0", nullable=False),
        sa.Column("last_renewal_attempt", sa.DateTime(timezone=True), nullable=True),
        # Usage tracking
        sa.Column("usage_count_daily", sa.Integer(), server_default="0", nullable=False),
        sa.Column("usage_count_monthly", sa.Integer(), server_default="0", nullable=False),
        sa.Column("usage_reset_daily", sa.DateTime(timezone=True), nullable=True),
        sa.Column("usage_reset_monthly", sa.DateTime(timezone=True), nullable=True),
        # Metadata
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_user_service_subscriptions_user",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["service_id"],
            ["marketplace_services.id"],
            name="fk_user_service_subscriptions_service",
            ondelete="RESTRICT",
        ),
    )

    op.create_index(
        "ix_user_service_subscriptions_user",
        "user_service_subscriptions",
        ["user_id"],
    )
    op.create_index(
        "ix_user_service_subscriptions_service",
        "user_service_subscriptions",
        ["service_id"],
    )
    op.create_index(
        "ix_user_service_subscriptions_status",
        "user_service_subscriptions",
        ["status"],
    )
    op.create_index(
        "ix_user_service_subscriptions_expires",
        "user_service_subscriptions",
        ["expires_at"],
    )
    # Compound index for active user subscriptions lookup
    op.create_index(
        "ix_user_service_subscriptions_active",
        "user_service_subscriptions",
        ["user_id", "status"],
    )

    # ============================================
    # Service Usage Log Table
    # Tracks every service usage for quota enforcement and billing
    # ============================================
    op.create_table(
        "service_usage_log",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("subscription_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("service_id", sa.Integer(), nullable=False),
        # Usage details
        sa.Column("action", sa.String(100), nullable=False),  # check_spam, delete_join, etc.
        sa.Column("resource_id", sa.String(255), nullable=True),  # chat_id, message_id, etc.
        sa.Column("usage_count", sa.Integer(), server_default="1", nullable=False),  # Usually 1
        # Result
        sa.Column("success", sa.Boolean(), nullable=False),  # Whether action succeeded
        sa.Column("error_message", sa.Text(), nullable=True),
        # Performance metrics
        sa.Column("response_time_ms", sa.Integer(), nullable=True),
        # Metadata
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
        # Timestamp
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["subscription_id"],
            ["user_service_subscriptions.id"],
            name="fk_service_usage_log_subscription",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_service_usage_log_user",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["service_id"],
            ["marketplace_services.id"],
            name="fk_service_usage_log_service",
            ondelete="RESTRICT",
        ),
    )

    op.create_index(
        "ix_service_usage_log_subscription",
        "service_usage_log",
        ["subscription_id"],
    )
    op.create_index(
        "ix_service_usage_log_user",
        "service_usage_log",
        ["user_id"],
    )
    op.create_index(
        "ix_service_usage_log_service",
        "service_usage_log",
        ["service_id"],
    )
    op.create_index(
        "ix_service_usage_log_created",
        "service_usage_log",
        ["created_at"],
    )
    # Compound index for user quota checks
    op.create_index(
        "ix_service_usage_log_quota_check",
        "service_usage_log",
        ["user_id", "service_id", "created_at"],
    )


def downgrade() -> None:
    """Drop marketplace services system tables"""
    op.drop_table("service_usage_log")
    op.drop_table("user_service_subscriptions")
    op.drop_table("marketplace_services")
