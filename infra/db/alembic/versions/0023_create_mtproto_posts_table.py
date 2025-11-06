"""Create posts and post_metrics tables for MTProto message storage

Revision ID: 0023_create_mtproto_posts_table
Revises: 0022_add_mtproto_enabled_flag
Create Date: 2025-11-05 10:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

revision = "0023"
down_revision = "0022"
branch_labels = None
depends_on = None


def upgrade():
    """Create posts and post_metrics tables for MTProto data collection"""
    
    # Create posts table for storing telegram messages
    op.create_table(
        "posts",
        sa.Column("channel_id", sa.BigInteger(), nullable=False, comment="Telegram channel ID"),
        sa.Column("msg_id", sa.BigInteger(), nullable=False, comment="Telegram message ID"),
        sa.Column("date", sa.TIMESTAMP(timezone=True), nullable=False, comment="Message date"),
        sa.Column("text", sa.Text(), nullable=True, comment="Message text content"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("channel_id", "msg_id"),
        comment="Stores Telegram messages collected via MTProto",
    )
    
    # Create indexes for posts table
    op.create_index("idx_posts_channel_date", "posts", ["channel_id", "date"])
    op.create_index("idx_posts_date", "posts", ["date"])
    
    # Create post_metrics table for storing message metrics over time
    op.create_table(
        "post_metrics",
        sa.Column("channel_id", sa.BigInteger(), nullable=False, comment="Telegram channel ID"),
        sa.Column("msg_id", sa.BigInteger(), nullable=False, comment="Telegram message ID"),
        sa.Column("snapshot_time", sa.TIMESTAMP(timezone=True), nullable=False, comment="When metrics were captured"),
        sa.Column("views", sa.BigInteger(), nullable=True, comment="Number of views"),
        sa.Column("forwards", sa.BigInteger(), nullable=True, comment="Number of forwards"),
        sa.Column("replies_count", sa.BigInteger(), nullable=True, comment="Number of replies"),
        sa.Column("reactions", sa.JSON(), nullable=True, comment="Reactions data (JSON)"),
        sa.Column("reactions_count", sa.BigInteger(), nullable=True, comment="Total reactions count"),
        sa.PrimaryKeyConstraint("channel_id", "msg_id", "snapshot_time"),
        sa.ForeignKeyConstraint(
            ["channel_id", "msg_id"],
            ["posts.channel_id", "posts.msg_id"],
            ondelete="CASCADE",
        ),
        comment="Stores time-series metrics for telegram messages",
    )
    
    # Create indexes for post_metrics table
    op.create_index("idx_post_metrics_channel_msg", "post_metrics", ["channel_id", "msg_id"])
    op.create_index("idx_post_metrics_snapshot_time", "post_metrics", ["snapshot_time"])


def downgrade():
    """Drop posts and post_metrics tables"""
    op.drop_index("idx_post_metrics_snapshot_time", "post_metrics")
    op.drop_index("idx_post_metrics_channel_msg", "post_metrics")
    op.drop_table("post_metrics")
    
    op.drop_index("idx_posts_date", "posts")
    op.drop_index("idx_posts_channel_date", "posts")
    op.drop_table("posts")
