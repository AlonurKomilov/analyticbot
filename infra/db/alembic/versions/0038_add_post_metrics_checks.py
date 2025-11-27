"""Add post_metrics_checks table for change detection

Revision ID: 0038_add_post_metrics_checks
Revises: 0037
Create Date: 2025-11-27 12:00:00.000000

This migration creates a lightweight tracking table to record when posts
were last checked and when metrics last changed, enabling smart collection
that only saves snapshots when data actually changes.
"""

import sqlalchemy as sa
from alembic import op

revision = "0038"
down_revision = "0037"
branch_labels = None
depends_on = None


def upgrade():
    """Create post_metrics_checks table for smart collection tracking"""

    # Create the checks tracking table
    op.create_table(
        "post_metrics_checks",
        sa.Column(
            "channel_id",
            sa.BigInteger(),
            nullable=False,
            comment="Telegram channel ID",
        ),
        sa.Column(
            "msg_id",
            sa.BigInteger(),
            nullable=False,
            comment="Telegram message ID",
        ),
        sa.Column(
            "last_checked_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
            comment="When we last checked this post (even if metrics didn't change)",
        ),
        sa.Column(
            "last_changed_at",
            sa.TIMESTAMP(timezone=True),
            nullable=True,
            comment="When metrics last changed significantly",
        ),
        sa.Column(
            "check_count",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
            comment="Total number of times we checked this post",
        ),
        sa.Column(
            "save_count",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
            comment="Total number of times we saved a snapshot (changes detected)",
        ),
        sa.Column(
            "stable_since",
            sa.TIMESTAMP(timezone=True),
            nullable=True,
            comment="When did metrics become stable (stop changing)",
        ),
        sa.Column(
            "post_age_hours",
            sa.Numeric(precision=10, scale=2),
            nullable=True,
            comment="Cached post age in hours for query optimization",
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("channel_id", "msg_id"),
        sa.ForeignKeyConstraint(
            ["channel_id", "msg_id"],
            ["posts.channel_id", "posts.msg_id"],
            ondelete="CASCADE",
        ),
        comment="Tracks post metric collection history for smart change detection",
    )

    # Indexes for efficient queries
    op.create_index(
        "idx_checks_last_checked",
        "post_metrics_checks",
        ["last_checked_at"],
        comment="Find posts that need checking based on last check time",
    )

    op.create_index(
        "idx_checks_stable_since",
        "post_metrics_checks",
        ["stable_since"],
        postgresql_where=sa.text("stable_since IS NOT NULL"),
        comment="Find stable posts (metrics not changing)",
    )

    op.create_index(
        "idx_checks_post_age",
        "post_metrics_checks",
        ["post_age_hours"],
        comment="Age-based collection frequency optimization",
    )

    op.create_index(
        "idx_checks_efficiency",
        "post_metrics_checks",
        ["check_count", "save_count"],
        comment="Collection efficiency monitoring (save_count / check_count ratio)",
    )


def downgrade():
    """Drop post_metrics_checks table"""
    op.drop_index("idx_checks_efficiency", "post_metrics_checks")
    op.drop_index("idx_checks_post_age", "post_metrics_checks")
    op.drop_index("idx_checks_stable_since", "post_metrics_checks")
    op.drop_index("idx_checks_last_checked", "post_metrics_checks")
    op.drop_table("post_metrics_checks")
