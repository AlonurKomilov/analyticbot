"""Add deliveries table and enhanced indexes for observability

Revision ID: 0006_deliveries_observability
Revises: 0005_payment_system
Create Date: 2025-08-24 15:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0006_deliveries_observability"
down_revision: str | Sequence[str] | None = "0005_payment_system"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add deliveries table and enhanced indexes for observability."""
    
    # Create deliveries table for tracking message delivery attempts
    op.create_table(
        "deliveries",
        sa.Column("id", sa.String(36), primary_key=True),  # UUID
        sa.Column("scheduled_post_id", sa.Integer(), nullable=False),
        sa.Column("delivery_channel_id", sa.String(100), nullable=False),  # Telegram channel ID
        sa.Column("status", sa.String(50), nullable=False, default="pending"),  # pending, processing, delivered, failed, retrying
        sa.Column("message_id", sa.String(100), nullable=True),  # Telegram message ID after successful delivery
        sa.Column("attempted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False, default=0),
        sa.Column("max_retries", sa.Integer(), nullable=False, default=3),
        sa.Column("delivery_metadata", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["scheduled_post_id"], ["scheduled_posts.id"], ondelete="CASCADE"),
        sa.CheckConstraint("status IN ('pending', 'processing', 'delivered', 'failed', 'retrying')"),
        sa.CheckConstraint("retry_count >= 0"),
        sa.CheckConstraint("max_retries >= 0"),
    )
    
    # Create indexes for deliveries table for efficient querying
    op.create_index("ix_deliveries_post_id", "deliveries", ["scheduled_post_id"])
    op.create_index("ix_deliveries_status", "deliveries", ["status"])
    op.create_index("ix_deliveries_channel_id", "deliveries", ["delivery_channel_id"])
    op.create_index("ix_deliveries_created_at", "deliveries", ["created_at"])
    op.create_index("ix_deliveries_attempted_at", "deliveries", ["attempted_at"])
    op.create_index("ix_deliveries_delivered_at", "deliveries", ["delivered_at"])
    
    # Composite index for failed deliveries that can be retried
    op.create_index(
        "ix_deliveries_retryable", 
        "deliveries", 
        ["status", "retry_count", "max_retries"],
        postgresql_where=sa.text("status IN ('failed', 'retrying') AND retry_count < max_retries")
    )
    
    # Composite index for pending deliveries ready for processing
    op.create_index(
        "ix_deliveries_pending", 
        "deliveries", 
        ["status", "created_at"],
        postgresql_where=sa.text("status = 'pending'")
    )
    
    # Add enhanced indexes for scheduled_posts if they don't exist
    # Check for existing indexes first by trying to create them with IF NOT EXISTS pattern
    
    try:
        # Enhanced index for scheduled posts by status and schedule time (for efficient querying)
        op.create_index(
            "ix_scheduled_posts_status_enhanced", 
            "scheduled_posts", 
            ["status", "schedule_time", "created_at"]
        )
    except Exception:
        # Index might already exist, ignore
        pass
    
    try:
        # Index for users by creation date (for analytics)
        op.create_index("ix_users_created_at", "users", ["created_at"])
    except Exception:
        pass
    
    try:
        # Index for channels by creation date (for analytics) 
        op.create_index("ix_channels_created_at", "channels", ["created_at"])
    except Exception:
        pass


def downgrade() -> None:
    """Remove deliveries table and enhanced indexes."""
    
    # Drop deliveries table and its indexes
    op.drop_index("ix_deliveries_pending", table_name="deliveries")
    op.drop_index("ix_deliveries_retryable", table_name="deliveries") 
    op.drop_index("ix_deliveries_delivered_at", table_name="deliveries")
    op.drop_index("ix_deliveries_attempted_at", table_name="deliveries")
    op.drop_index("ix_deliveries_created_at", table_name="deliveries")
    op.drop_index("ix_deliveries_channel_id", table_name="deliveries")
    op.drop_index("ix_deliveries_status", table_name="deliveries")
    op.drop_index("ix_deliveries_post_id", table_name="deliveries")
    op.drop_table("deliveries")
    
    # Drop enhanced indexes if they exist
    try:
        op.drop_index("ix_channels_created_at", table_name="channels")
    except Exception:
        pass
    
    try:
        op.drop_index("ix_users_created_at", table_name="users")
    except Exception:
        pass
    
    try:
        op.drop_index("ix_scheduled_posts_status_enhanced", table_name="scheduled_posts")
    except Exception:
        pass
