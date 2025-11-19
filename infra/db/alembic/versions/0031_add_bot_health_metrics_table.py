"""Add bot health metrics table

Revision ID: 0031
Revises: 0030
Create Date: 2025-11-19 10:00:00.000000

This migration adds the bot_health_metrics table for persistent storage of
bot health monitoring data, enabling trend analysis and historical reporting.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0031"
down_revision: str | Sequence[str] | None = "0030"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create bot_health_metrics table with indexes."""

    # Create bot_health_metrics table
    op.create_table(
        "bot_health_metrics",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("total_requests", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("successful_requests", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failed_requests", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("consecutive_failures", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_rate", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("avg_response_time_ms", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("last_success", sa.DateTime(), nullable=True),
        sa.Column("last_failure", sa.DateTime(), nullable=True),
        sa.Column("last_check", sa.DateTime(), nullable=False),
        sa.Column("is_rate_limited", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("last_error_type", sa.String(length=255), nullable=True),
        sa.Column("circuit_breaker_state", sa.String(length=20), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for efficient queries
    op.create_index(
        "idx_bot_health_user_id",
        "bot_health_metrics",
        ["user_id"],
    )

    op.create_index(
        "idx_bot_health_timestamp",
        "bot_health_metrics",
        ["timestamp"],
    )

    # Composite index for user + timestamp queries (most common pattern)
    op.create_index(
        "idx_bot_health_user_timestamp",
        "bot_health_metrics",
        ["user_id", sa.text("timestamp DESC")],
    )

    # Composite index for status + timestamp queries (admin monitoring)
    op.create_index(
        "idx_bot_health_status_timestamp",
        "bot_health_metrics",
        ["status", sa.text("timestamp DESC")],
    )


def downgrade() -> None:
    """Drop bot_health_metrics table and indexes."""

    # Drop indexes first
    op.drop_index("idx_bot_health_status_timestamp", table_name="bot_health_metrics")
    op.drop_index("idx_bot_health_user_timestamp", table_name="bot_health_metrics")
    op.drop_index("idx_bot_health_timestamp", table_name="bot_health_metrics")
    op.drop_index("idx_bot_health_user_id", table_name="bot_health_metrics")

    # Drop table
    op.drop_table("bot_health_metrics")
