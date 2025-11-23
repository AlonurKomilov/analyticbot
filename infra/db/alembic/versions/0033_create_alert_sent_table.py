"""Create alert_sent table for alert deduplication

Revision ID: 0033
Revises: 0032
Create Date: 2025-11-21 00:00:00.000000

ALERT TRACKING MIGRATION:
This migration creates the alert_sent table to track alert deliveries
and prevent duplicate alerts from being sent to users.

Table: alert_sent
- Tracks which alerts have been sent to which users
- Prevents duplicate notifications
- Stores delivery status and timestamps
- Enables alert delivery history and analytics

Schema:
- id: Primary key
- user_id: User who received the alert
- channel_id: Channel the alert was about
- alert_type: Type of alert (SPIKE, QUIET, GROWTH, etc.)
- rule_name: Alert rule that triggered
- severity: Alert severity level
- sent_at: When the alert was sent
- status: Delivery status (sent, failed, pending)
- message_id: Telegram message ID (for tracking)
- error_message: Error details if delivery failed
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0033"
down_revision = "0032"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create alert_sent table"""
    op.create_table(
        "alert_sent",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("channel_id", sa.BigInteger(), nullable=False),
        sa.Column("alert_type", sa.String(50), nullable=False),
        sa.Column("rule_name", sa.String(100), nullable=True),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column(
            "sent_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
        ),
        sa.Column("status", sa.String(20), nullable=False, server_default="sent"),
        sa.Column("message_id", sa.BigInteger(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # Index for checking recent alerts (deduplication)
    op.create_index(
        "ix_alert_sent_user_channel_type_time",
        "alert_sent",
        ["user_id", "channel_id", "alert_type", "sent_at"],
    )

    # Index for user alert history
    op.create_index(
        "ix_alert_sent_user_time",
        "alert_sent",
        ["user_id", "sent_at"],
    )

    # Index for delivery status tracking
    op.create_index(
        "ix_alert_sent_status",
        "alert_sent",
        ["status", "sent_at"],
    )


def downgrade() -> None:
    """Drop alert_sent table"""
    op.drop_index("ix_alert_sent_status", table_name="alert_sent")
    op.drop_index("ix_alert_sent_user_time", table_name="alert_sent")
    op.drop_index("ix_alert_sent_user_channel_type_time", table_name="alert_sent")
    op.drop_table("alert_sent")
