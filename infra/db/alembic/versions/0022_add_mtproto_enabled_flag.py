"""add_mtproto_enabled_flag

Revision ID: 0022_add_mtproto_enabled_flag
Revises: 0021_make_mtproto_optional
Create Date: 2025-11-03 06:30:22.366895

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0022_add_mtproto_enabled_flag'
down_revision: Union[str, Sequence[str], None] = '0021_make_mtproto_optional'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add mtproto_enabled flag to user_bot_credentials table."""
    # Add mtproto_enabled column (default True to keep existing functionality)
    op.add_column(
        'user_bot_credentials',
        sa.Column('mtproto_enabled', sa.Boolean(), nullable=False, server_default=sa.true())
    )


def downgrade() -> None:
    """Remove mtproto_enabled flag from user_bot_credentials table."""
    op.drop_column('user_bot_credentials', 'mtproto_enabled')
