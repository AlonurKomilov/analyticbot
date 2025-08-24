"""add helpful indexes

Revision ID: 0003_add_indexes
Revises: 0002_seed_plans
Create Date: 2025-08-17
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0003_add_indexes"
down_revision: str | None = "0002_seed_plans"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Composite / targeted indexes to speed scheduling & lookups
    op.create_index(
        "ix_scheduled_posts_status_schedule_time",
        "scheduled_posts",
        ["status", "schedule_time"],
        postgresql_concurrently=False,
    )
    op.create_index(
        "ix_scheduled_posts_user_created_at",
        "scheduled_posts",
        ["user_id", "created_at"],
        postgresql_concurrently=False,
    )
    op.create_index(
        "ix_sent_posts_scheduled_post_id",
        "sent_posts",
        ["scheduled_post_id"],
        postgresql_concurrently=False,
    )


def downgrade() -> None:
    op.drop_index("ix_sent_posts_scheduled_post_id", table_name="sent_posts")
    op.drop_index("ix_scheduled_posts_user_created_at", table_name="scheduled_posts")
    op.drop_index("ix_scheduled_posts_status_schedule_time", table_name="scheduled_posts")
