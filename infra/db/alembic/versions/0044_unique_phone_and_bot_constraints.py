"""Add unique constraints for telegram_phone and bot_id

Ensures one MTProto account and one bot per user system-wide.
Each Telegram phone number can only be linked to one AnalyticBot user.
Each bot can only be linked to one AnalyticBot user.

Revision ID: 0044
Revises: 0043
Create Date: 2025-12-09

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "0044"
down_revision = "0043"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add unique constraints for telegram_phone and bot_id."""
    # Add unique constraint for telegram_phone (allows NULL but unique when set)
    op.create_unique_constraint("unique_telegram_phone", "user_bot_credentials", ["telegram_phone"])

    # Add unique constraint for bot_id (allows NULL but unique when set)
    op.create_unique_constraint("unique_bot_id", "user_bot_credentials", ["bot_id"])


def downgrade() -> None:
    """Remove unique constraints."""
    op.drop_constraint("unique_telegram_phone", "user_bot_credentials", type_="unique")
    op.drop_constraint("unique_bot_id", "user_bot_credentials", type_="unique")
