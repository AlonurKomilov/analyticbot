"""Add critical performance indexes for analytics operations

Revision ID: 0014_performance_critical_indexes
Revises: 0013_add_advanced_performance_indexes
Create Date: 2025-09-04 15:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0014_performance_critical_indexes"
down_revision: str | Sequence[str] | None = "0013_add_advanced_performance_indexes"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add critical performance indexes based on audit analysis."""

    # High-Priority Analytics Queries - Missing from previous migrations
    op.execute("""
    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sent_posts_sent_at_interval
    ON sent_posts (sent_at DESC)
    WHERE sent_at >= CURRENT_DATE - INTERVAL '30 days';
    """)

    # User lookup optimizations with covering indexes
    op.execute("""
    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_telegram_id_plan_cover
    ON users (id)
    INCLUDE (username, plan_id)
    WHERE plan_id IS NOT NULL;
    """)

    # Channel repository optimization with covering index
    op.execute("""
    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_channels_user_lookup_cover
    ON channels (user_id)
    INCLUDE (id, title, username, created_at);
    """)

    # View tracking optimizations for analytics
    op.execute("""
    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scheduled_posts_view_tracking_cover
    ON scheduled_posts (status, views DESC NULLS LAST)
    INCLUDE (id, channel_id, created_at)
    WHERE status = 'sent' AND views IS NOT NULL;
    """)

    # Join optimization for analytics queries
    op.execute("""
    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sent_posts_join_optimization
    ON sent_posts (scheduled_post_id, channel_id, message_id, sent_at DESC);
    """)

    # Analytics aggregation optimization
    op.execute("""
    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scheduled_posts_analytics_agg
    ON scheduled_posts (channel_id, created_at DESC, views DESC NULLS LAST)
    WHERE status = 'sent' AND created_at >= CURRENT_DATE - INTERVAL '90 days';
    """)

    # User activity tracking
    op.execute("""
    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scheduled_posts_user_activity
    ON scheduled_posts (user_id, status, schedule_time DESC)
    WHERE status IN ('sent', 'pending');
    """)

    # Channel performance tracking
    op.execute("""
    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_channels_performance_lookup
    ON channels (user_id, created_at DESC)
    WHERE username IS NOT NULL;
    """)

    # Composite index for complex analytics queries
    op.execute("""
    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sent_posts_analytics_composite
    ON sent_posts (channel_id, sent_at DESC)
    INCLUDE (scheduled_post_id, message_id);
    """)

    # Optimize user subscription queries
    op.execute("""
    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_subscription_lookup
    ON users (plan_id, created_at DESC)
    WHERE plan_id IS NOT NULL;
    """)


def downgrade() -> None:
    """Remove critical performance indexes."""
    op.execute("DROP INDEX IF EXISTS idx_sent_posts_sent_at_interval;")
    op.execute("DROP INDEX IF EXISTS idx_users_telegram_id_plan_cover;")
    op.execute("DROP INDEX IF EXISTS idx_channels_user_lookup_cover;")
    op.execute("DROP INDEX IF EXISTS idx_scheduled_posts_view_tracking_cover;")
    op.execute("DROP INDEX IF EXISTS idx_sent_posts_join_optimization;")
    op.execute("DROP INDEX IF EXISTS idx_scheduled_posts_analytics_agg;")
    op.execute("DROP INDEX IF EXISTS idx_scheduled_posts_user_activity;")
    op.execute("DROP INDEX IF EXISTS idx_channels_performance_lookup;")
    op.execute("DROP INDEX IF EXISTS idx_sent_posts_analytics_composite;")
    op.execute("DROP INDEX IF EXISTS idx_users_subscription_lookup;")
