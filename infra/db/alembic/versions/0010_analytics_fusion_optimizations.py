"""Add Analytics Fusion performance optimizations and indexes

Revision ID: 0010_analytics_fusion_optimizations
Revises: 0009_content_protection_system
Create Date: 2025-01-27 15:00:00.000000
"""

from alembic import op

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade():
    """Add performance optimizations for Analytics Fusion API v2"""
    
    from sqlalchemy import inspect
    
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_tables = inspector.get_table_names()

    # Add indexes for efficient querying in posts table (skip if table doesn't exist)
    if "posts" in existing_tables:
        op.create_index("idx_posts_channel_date", "posts", ["channel_id", "date"])
        op.create_index("idx_posts_channel_msg", "posts", ["channel_id", "msg_id"])
        op.create_index(
            "idx_posts_date_desc",
            "posts",
            ["date"],
            postgresql_using="btree",
            postgresql_ops={"date": "DESC"},
        )

    # Add indexes for post_metrics table for analytics queries (skip if table doesn't exist)
    if "post_metrics" in existing_tables:
        op.create_index(
            "idx_post_metrics_channel_time", "post_metrics", ["channel_id", "snapshot_time"]
        )
        op.create_index(
            "idx_post_metrics_channel_msg_time",
            "post_metrics",
            ["channel_id", "msg_id", "snapshot_time"],
        )
        op.create_index(
            "idx_post_metrics_views_desc",
            "post_metrics",
            ["views"],
            postgresql_using="btree",
            postgresql_ops={"views": "DESC"},
        )

    # Add indexes for channel_daily table for time series queries (skip if table doesn't exist)
    if "channel_daily" in existing_tables:
        op.create_index("idx_channel_daily_channel_metric", "channel_daily", ["channel_id", "metric"])
        op.create_index("idx_channel_daily_day", "channel_daily", ["day"])
        op.create_index("idx_channel_daily_metric_day", "channel_daily", ["metric", "day"])

    # Add indexes for stats_raw table for MTProto data (skip if table doesn't exist)
    if "stats_raw" in existing_tables:
        op.create_index("idx_stats_raw_channel_key", "stats_raw", ["channel_id", "key"])
        op.create_index(
            "idx_stats_raw_fetched_desc",
            "stats_raw",
            ["fetched_at"],
            postgresql_using="btree",
            postgresql_ops={"fetched_at": "DESC"},
        )

    # Create materialized views for better performance on recent data (skip if tables don't exist)
    if "channel_daily" in existing_tables:
        op.execute("""
            CREATE MATERIALIZED VIEW IF NOT EXISTS mv_channel_daily_recent AS
            SELECT channel_id, day, metric, value
            FROM channel_daily
            WHERE day >= CURRENT_DATE - INTERVAL '120 days'
            WITH DATA;
        """)

        # Index the materialized view
        op.create_index(
            "idx_mv_channel_daily_recent", "mv_channel_daily_recent", ["channel_id", "metric", "day"]
        )

    # Create materialized view for recent post metrics (skip if table doesn't exist)
    if "post_metrics" in existing_tables:
        op.execute("""
            CREATE MATERIALIZED VIEW IF NOT EXISTS mv_post_metrics_recent AS
            SELECT DISTINCT ON (channel_id, msg_id)
                channel_id, msg_id, views, forwards, replies_count,
                reactions, reactions_count, snapshot_time
            FROM post_metrics
            WHERE snapshot_time >= NOW() - INTERVAL '120 days'
            ORDER BY channel_id, msg_id, snapshot_time DESC
            WITH DATA;
        """)

        # Index the post metrics materialized view
        op.create_index("idx_mv_post_metrics_recent", "mv_post_metrics_recent", ["channel_id", "views"])
        op.create_index(
            "idx_mv_post_metrics_recent_views",
            "mv_post_metrics_recent",
        ["views"],
        postgresql_using="btree",
        postgresql_ops={"views": "DESC"},
    )


def downgrade():
    """Remove analytics fusion performance optimizations"""

    # Drop materialized views
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_post_metrics_recent;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_channel_daily_recent;")

    # Drop indexes for stats_raw
    op.drop_index("idx_stats_raw_fetched_desc", "stats_raw")
    op.drop_index("idx_stats_raw_channel_key", "stats_raw")

    # Drop indexes for channel_daily
    op.drop_index("idx_channel_daily_metric_day", "channel_daily")
    op.drop_index("idx_channel_daily_day", "channel_daily")
    op.drop_index("idx_channel_daily_channel_metric", "channel_daily")

    # Drop indexes for post_metrics
    op.drop_index("idx_post_metrics_views_desc", "post_metrics")
    op.drop_index("idx_post_metrics_channel_msg_time", "post_metrics")
    op.drop_index("idx_post_metrics_channel_time", "post_metrics")

    # Drop indexes for posts
    op.drop_index("idx_posts_date_desc", "posts")
    op.drop_index("idx_posts_channel_msg", "posts")
    op.drop_index("idx_posts_channel_date", "posts")
