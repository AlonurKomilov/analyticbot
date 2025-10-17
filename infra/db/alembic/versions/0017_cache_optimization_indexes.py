"""Add cache-optimized indexes for Phase 2 performance

Revision ID: 0017_cache_optimization_indexes
Revises: 0016_critical_fix_cascade_delete_constraints
Create Date: 2025-10-16 00:00:00.000000

This migration adds strategic indexes to support:
- Redis cache warming and invalidation
- Fast user lookups for cache keys
- Analytics query optimization
- Frequently accessed endpoint patterns

Expected Performance Gain: 2-5x for non-cached queries
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0017_cache_optimization_indexes"
down_revision: str | Sequence[str] | None = "51ba01a1cb0e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add cache-optimized indexes for Phase 2 performance improvements."""

    # 1. User ID lookup optimization (for cache key generation)
    # Speeds up: cache:auth:me:user_{id}
    op.execute("""
    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_id_active
    ON users (id)
    WHERE plan_id IS NOT NULL;
    """)

    # 2. Channel lookup by user (for cache:analytics:channels:user_{id})
    # Covering index includes all columns needed for response
    op.execute("""
    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_channels_user_analytics_cover
    ON channels (user_id, created_at DESC)
    INCLUDE (id, title, username)
    WHERE title IS NOT NULL;
    """)

    # 3. Fast channel count for dashboard (frequently cached)
    op.execute("""
    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_channels_user_count
    ON channels (user_id)
    WHERE title IS NOT NULL AND username IS NOT NULL;
    """)

    # 4. Analytics aggregation optimization (top posts, trending)
    op.execute("""
    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scheduled_posts_trending
    ON scheduled_posts (channel_id, views DESC NULLS LAST, created_at DESC)
    WHERE status = 'sent' AND views > 0;
    """)

    # 5. Recent activity tracking (for user dashboard)
    op.execute("""
    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scheduled_posts_recent_activity
    ON scheduled_posts (user_id, created_at DESC)
    INCLUDE (channel_id, status, views)
    WHERE created_at >= CURRENT_DATE - INTERVAL '7 days';
    """)

    # 6. Health check optimization (frequently accessed endpoint)
    # Fast query for system metrics
    op.execute("""
    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_active_count
    ON users (created_at DESC)
    WHERE plan_id IS NOT NULL
      AND created_at >= CURRENT_DATE - INTERVAL '30 days';
    """)

    # 7. Channel statistics for analytics (cached per user)
    op.execute("""
    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sent_posts_channel_stats
    ON sent_posts (channel_id, sent_at DESC)
    INCLUDE (scheduled_post_id, message_id)
    WHERE sent_at >= CURRENT_DATE - INTERVAL '30 days';
    """)

    # 8. User session lookup optimization (for auth middleware)
    op.execute("""
    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_username_lookup
    ON users (username)
    INCLUDE (id, plan_id, created_at)
    WHERE username IS NOT NULL;
    """)

    # 9. Analytics time-series optimization (common query pattern)
    op.execute("""
    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scheduled_posts_timeseries
    ON scheduled_posts (created_at DESC, channel_id, views DESC NULLS LAST)
    WHERE status = 'sent'
      AND created_at >= CURRENT_DATE - INTERVAL '90 days';
    """)

    # 10. Multi-channel user dashboard (frequently cached)
    op.execute("""
    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_channels_user_dashboard
    ON channels (user_id)
    INCLUDE (id, title, username, created_at)
    WHERE username IS NOT NULL AND title IS NOT NULL;
    """)


def downgrade() -> None:
    """Remove cache-optimized indexes."""
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_users_id_active;")
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_channels_user_analytics_cover;")
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_channels_user_count;")
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_scheduled_posts_trending;")
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_scheduled_posts_recent_activity;")
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_users_active_count;")
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_sent_posts_channel_stats;")
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_users_username_lookup;")
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_scheduled_posts_timeseries;")
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_channels_user_dashboard;")
