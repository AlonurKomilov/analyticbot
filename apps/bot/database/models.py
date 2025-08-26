from dataclasses import dataclass

import sqlalchemy as sa

metadata = sa.MetaData()

# 1. 'plans' table (no dependencies)
plans = sa.Table(
    "plans",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("name", sa.String(50), unique=True, nullable=False),
    sa.Column("max_channels", sa.Integer, default=1),
    sa.Column("max_posts_per_month", sa.Integer, default=30),
)

# 2. 'users' table (depends on 'plans')
users = sa.Table(
    "users",
    metadata,
    sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=False),
    sa.Column("username", sa.String(255)),
    sa.Column(
        "plan_id",
        sa.Integer,
        sa.ForeignKey("plans.id", ondelete="SET NULL"),
        default=1,
    ),
    sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
)

# 3. 'channels' table (depends on 'users')
channels = sa.Table(
    "channels",
    metadata,
    sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=False),
    sa.Column(
        "user_id",
        sa.BigInteger,
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    sa.Column("title", sa.String(255)),
    sa.Column("username", sa.String(255), unique=True),
    sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
)

# 4. 'scheduled_posts' table (depends on 'users' and 'channels')
scheduled_posts = sa.Table(
    "scheduled_posts",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column(
        "user_id",
        sa.BigInteger,
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    ),
    sa.Column(
        "channel_id",
        sa.BigInteger,
        sa.ForeignKey("channels.id", ondelete="CASCADE"),
        index=True,
    ),
    sa.Column("post_text", sa.Text),
    sa.Column("media_id", sa.String(255)),
    sa.Column("media_type", sa.String(50)),
    sa.Column("inline_buttons", sa.JSON),
    sa.Column("status", sa.String(50), default="pending"),
    sa.Column("schedule_time", sa.DateTime(timezone=True)),
    sa.Column(
        "created_at",
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        index=True,
    ),
    sa.Column("views", sa.Integer, default=0),
)

# 5. 'sent_posts' table (depends on 'scheduled_posts' and 'channels')
sent_posts = sa.Table(
    "sent_posts",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column(
        "scheduled_post_id",
        sa.Integer,
        sa.ForeignKey("scheduled_posts.id", ondelete="CASCADE"),
        nullable=False,
    ),
    sa.Column(
        "channel_id",
        sa.BigInteger,
        sa.ForeignKey("channels.id", ondelete="CASCADE"),
        nullable=False,
    ),
    sa.Column("message_id", sa.BigInteger, nullable=False),
    sa.Column("sent_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
)

# NOTE: Alembic revision 0004 adds a composite unique constraint on (channel_id, message_id)
# to protect against duplicate log entries when retrying sends.
