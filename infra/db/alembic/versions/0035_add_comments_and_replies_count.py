"""Add comments_count and replies_count columns to post_metrics

Revision ID: 0035_add_comments_and_replies_count
Revises: 0034_create_user_alert_preferences
Create Date: 2025-11-25 12:00:00.000000

This migration properly names the two types of engagement:
- comments_count: Discussion group comments (linked discussion groups on channels)
- replies_count: Direct threaded replies (reply to specific messages)

The old 'replies_count' field will be renamed to 'comments_count' for clarity.
"""

import sqlalchemy as sa
from alembic import op

revision = "0035"
down_revision = "0034"
branch_labels = None
depends_on = None


def upgrade():
    """Rename replies_count to comments_count and add new replies_count column"""

    # Step 1: Rename existing replies_count to comments_count
    op.alter_column(
        "post_metrics",
        "replies_count",
        new_column_name="comments_count",
        comment="Number of discussion group comments",
    )

    # Step 2: Add new replies_count column for threaded replies
    op.add_column(
        "post_metrics",
        sa.Column(
            "replies_count",
            sa.BigInteger(),
            nullable=True,
            server_default="0",
            comment="Number of direct threaded replies",
        ),
    )

    # Step 3: Create indexes for analytics queries
    op.create_index(
        "idx_post_metrics_comments",
        "post_metrics",
        ["channel_id", "comments_count"],
        postgresql_where=sa.text("comments_count > 0"),
    )

    op.create_index(
        "idx_post_metrics_replies",
        "post_metrics",
        ["channel_id", "replies_count"],
        postgresql_where=sa.text("replies_count > 0"),
    )

    # Step 4: Backfill new replies_count with 0
    op.execute("UPDATE post_metrics SET replies_count = 0 WHERE replies_count IS NULL")

    # Step 5: Make column NOT NULL after backfill
    op.alter_column("post_metrics", "replies_count", nullable=False)


def downgrade():
    """Revert changes - rename back and drop replies_count"""

    # Drop indexes first
    op.drop_index("idx_post_metrics_replies", "post_metrics")
    op.drop_index("idx_post_metrics_comments", "post_metrics")

    # Drop new replies_count column
    op.drop_column("post_metrics", "replies_count")

    # Rename comments_count back to replies_count
    op.alter_column(
        "post_metrics",
        "comments_count",
        new_column_name="replies_count",
        comment="Number of replies",
    )
