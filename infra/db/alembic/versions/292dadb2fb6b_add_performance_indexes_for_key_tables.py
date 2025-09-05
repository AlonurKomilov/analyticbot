"""Add performance indexes for key tables

Revision ID: 292dadb2fb6b
Revises: 115f08938a98
Create Date: 2025-09-03 09:40:11.749080

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "292dadb2fb6b"
down_revision: str | Sequence[str] | None = "0010_phase_4_5_bot_ui_alerts"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
    CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users (telegram_id);
    """)
    op.execute("""
    CREATE INDEX IF NOT EXISTS idx_users_username ON users (username);
    """)
    op.execute("""
    CREATE INDEX IF NOT EXISTS idx_channels_user_id ON channels (user_id);
    """)
    op.execute("""
    CREATE INDEX IF NOT EXISTS idx_post_metrics_post_id_ts ON post_metrics (post_id, ts DESC);
    """)
    op.execute("""
    CREATE INDEX IF NOT EXISTS idx_post_metrics_channel_id_ts ON post_metrics (channel_id, ts DESC);
    """)
    op.execute("""
    CREATE INDEX IF NOT EXISTS idx_scheduled_posts_user_id_status 
    ON scheduled_posts (user_id, status);
    """)
    op.execute("""
    CREATE INDEX IF NOT EXISTS idx_scheduled_posts_scheduled_time_status 
    ON scheduled_posts (scheduled_time, status) 
    WHERE status = 'pending';
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP INDEX IF EXISTS idx_users_telegram_id;")
    op.execute("DROP INDEX IF EXISTS idx_users_username;")
    op.execute("DROP INDEX IF EXISTS idx_channels_user_id;")
    op.execute("DROP INDEX IF EXISTS idx_post_metrics_post_id_ts;")
    op.execute("DROP INDEX IF EXISTS idx_post_metrics_channel_id_ts;")
    op.execute("DROP INDEX IF EXISTS idx_scheduled_posts_user_id_status;")
    op.execute("DROP INDEX IF EXISTS idx_scheduled_posts_scheduled_time_status;")
