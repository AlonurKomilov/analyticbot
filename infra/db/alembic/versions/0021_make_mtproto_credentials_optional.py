"""Make MTProto credentials optional in user_bot_credentials

Revision ID: 0021_make_mtproto_optional
Revises: 0020_add_channel_description
Create Date: 2025-11-02 11:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0021"
down_revision = "0020"
branch_labels = None
depends_on = None


def upgrade():
    """Make telegram_api_id and telegram_api_hash nullable"""
    # Make telegram_api_id nullable
    op.alter_column(
        "user_bot_credentials", "telegram_api_id", existing_type=sa.BigInteger(), nullable=True
    )

    # Make telegram_api_hash nullable
    op.alter_column(
        "user_bot_credentials", "telegram_api_hash", existing_type=sa.String(255), nullable=True
    )


def downgrade():
    """Revert telegram_api_id and telegram_api_hash to NOT NULL"""
    # Note: This will fail if there are NULL values in the database
    op.alter_column(
        "user_bot_credentials", "telegram_api_id", existing_type=sa.BigInteger(), nullable=False
    )

    op.alter_column(
        "user_bot_credentials", "telegram_api_hash", existing_type=sa.String(255), nullable=False
    )
