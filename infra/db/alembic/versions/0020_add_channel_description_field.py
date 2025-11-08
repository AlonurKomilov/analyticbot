"""Add description field to channels table

Revision ID: 0020_add_channel_description
Revises: 0019_add_user_bot_credentials
Create Date: 2025-10-28 00:00:00.000000

This migration adds a description field to the channels table to store
channel descriptions fetched from Telegram API or provided by users.
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0020_add_channel_description"
down_revision = "0019_add_user_bot_credentials"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add description column to channels table"""

    # Add description field
    op.add_column("channels", sa.Column("description", sa.Text(), nullable=True))

    # Add comment for documentation
    op.execute(
        """
        COMMENT ON COLUMN channels.description IS
        'Channel description from Telegram API or user-provided text'
    """
    )


def downgrade() -> None:
    """Remove description column from channels table"""

    op.drop_column("channels", "description")
