"""add unique constraint to sent_posts

Revision ID: 0004_unique_sent_posts
Revises: 0003_add_indexes
Create Date: 2025-08-17
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0004_unique_sent_posts"
down_revision: Union[str, None] = "0003_add_indexes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add a composite unique constraint to prevent duplicate log entries
    op.create_unique_constraint(
        "uq_sent_posts_channel_message",
        "sent_posts",
        ["channel_id", "message_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_sent_posts_channel_message", "sent_posts", type_="unique"
    )
