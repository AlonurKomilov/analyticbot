"""Phase 4.5 Bot UI & Alerts Integration - Database Schema

Revision ID: 0011_bot_ui_alerts
Revises: 0010_analytics_fusion_optimizations
Create Date: 2025-08-31 12:00:00.000000

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create tables for Phase 4.5 Bot UI & Alerts Integration"""

    # Alert subscriptions table
    op.create_table(
        "alert_subscriptions",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("chat_id", sa.BigInteger(), nullable=False),
        sa.Column("channel_id", sa.BigInteger(), nullable=False),
        sa.Column("kind", sa.Text(), nullable=False),
        sa.Column("threshold", sa.Numeric(), nullable=True),
        sa.Column("window_hours", sa.Integer(), nullable=False, server_default="48"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("kind IN ('spike','quiet','growth')", name="ck_alert_subscription_kind"),
    )

    # Create indexes for alert subscriptions
    op.create_index(
        "ix_alert_subscriptions_chat_channel", "alert_subscriptions", ["chat_id", "channel_id"]
    )
    op.create_index("ix_alert_subscriptions_enabled", "alert_subscriptions", ["enabled"])
    op.create_index("ix_alert_subscriptions_kind", "alert_subscriptions", ["kind"])

    # Alert sent tracking for deduplication
    op.create_table(
        "alerts_sent",
        sa.Column("chat_id", sa.BigInteger(), nullable=False),
        sa.Column("channel_id", sa.BigInteger(), nullable=False),
        sa.Column("kind", sa.Text(), nullable=False),
        sa.Column("key", sa.Text(), nullable=False),
        sa.Column("sent_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("chat_id", "channel_id", "kind", "key"),
    )

    # Create index for cleanup queries
    op.create_index("ix_alerts_sent_sent_at", "alerts_sent", ["sent_at"])

    # Shared reports table for shareable links
    op.create_table(
        "shared_reports",
        sa.Column("token", sa.Text(), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")),
        sa.Column("created_by_chat_id", sa.BigInteger(), nullable=True),
        sa.Column("access_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_accessed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("token"),
    )

    # Create indexes for shared reports
    op.create_index("ix_shared_reports_expires_at", "shared_reports", ["expires_at"])
    op.create_index("ix_shared_reports_created_by", "shared_reports", ["created_by_chat_id"])
    op.create_index("ix_shared_reports_created_at", "shared_reports", ["created_at"])


def downgrade() -> None:
    """Drop tables for Phase 4.5 Bot UI & Alerts Integration"""

    # Drop shared reports table and indexes
    op.drop_index("ix_shared_reports_created_at", "shared_reports")
    op.drop_index("ix_shared_reports_created_by", "shared_reports")
    op.drop_index("ix_shared_reports_expires_at", "shared_reports")
    op.drop_table("shared_reports")

    # Drop alerts sent table and indexes
    op.drop_index("ix_alerts_sent_sent_at", "alerts_sent")
    op.drop_table("alerts_sent")

    # Drop alert subscriptions table and indexes
    op.drop_index("ix_alert_subscriptions_kind", "alert_subscriptions")
    op.drop_index("ix_alert_subscriptions_enabled", "alert_subscriptions")
    op.drop_index("ix_alert_subscriptions_chat_channel", "alert_subscriptions")
    op.drop_table("alert_subscriptions")
