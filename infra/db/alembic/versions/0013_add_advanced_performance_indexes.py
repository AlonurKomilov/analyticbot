"""Add advanced performance indexes

Revision ID: 0013_add_advanced_performance_indexes
Revises: 0012_add_performance_indexes_for_key_tables
Create Date: 2025-09-03 10:33:09.505177

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision = "0013"
down_revision: str | Sequence[str] | None = "0012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Advanced performance indexes for core analytics queries

    # Multi-column composite indexes for complex analytics queries
    op.execute(
        """
    CREATE INDEX IF NOT EXISTS idx_scheduled_posts_channel_status_time
    ON scheduled_posts (channel_id, status, created_at DESC)
    WHERE status = 'sent';
    """
    )

    op.execute(
        """
    CREATE INDEX IF NOT EXISTS idx_sent_posts_channel_message_time
    ON sent_posts (channel_id, message_id, sent_at DESC);
    """
    )

    # Optimized indexes for view tracking queries
    op.execute(
        """
    CREATE INDEX IF NOT EXISTS idx_scheduled_posts_views_desc
    ON scheduled_posts (channel_id, views DESC NULLS LAST)
    WHERE views IS NOT NULL AND status = 'sent';
    """
    )

    # Partial indexes for active data only
    # Skip idx_users_telegram_id_active - telegram_id column does not exist
    # op.execute("""
    # CREATE INDEX IF NOT EXISTS idx_users_telegram_id_active
    # ON users (telegram_id)
    # WHERE plan_id IS NOT NULL;
    # """)

    op.execute(
        """
    CREATE INDEX IF NOT EXISTS idx_channels_user_active
    ON channels (user_id, title)
    WHERE username IS NOT NULL;
    """
    )

    # Performance indexes for analytics aggregations
    op.execute(
        """
    CREATE INDEX IF NOT EXISTS idx_scheduled_posts_user_created_views
    ON scheduled_posts (user_id, created_at DESC, views DESC NULLS LAST)
    WHERE status = 'sent';
    """
    )

    # Time-based partitioning support indexes
    op.execute(
        """
    CREATE INDEX IF NOT EXISTS idx_sent_posts_sent_at_range
    ON sent_posts (sent_at DESC, channel_id)
    """
    )

    # Covering indexes to avoid table lookups
    op.execute(
        """
    CREATE INDEX IF NOT EXISTS idx_scheduled_posts_tracking_cover
    ON scheduled_posts (id, channel_id, views)
    WHERE status = 'sent' AND views IS NOT NULL;
    """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP INDEX IF EXISTS idx_scheduled_posts_channel_status_time;")
    op.execute("DROP INDEX IF EXISTS idx_sent_posts_channel_message_time;")
    op.execute("DROP INDEX IF EXISTS idx_scheduled_posts_views_desc;")
    # op.execute("DROP INDEX IF EXISTS idx_users_telegram_id_active;")  # Never created
    op.execute("DROP INDEX IF EXISTS idx_channels_user_active;")
    op.execute("DROP INDEX IF EXISTS idx_scheduled_posts_user_created_views;")
    op.execute("DROP INDEX IF EXISTS idx_sent_posts_sent_at_range;")
    op.execute("DROP INDEX IF EXISTS idx_scheduled_posts_tracking_cover;")
