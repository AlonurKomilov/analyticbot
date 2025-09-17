"""Merge analytics and performance optimization branches

Revision ID: 0015_merge_analytics_and_performance
Revises: 0014_performance_critical_indexes
Create Date: 2025-09-17 07:27:16.572667

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0015_merge_analytics_and_performance'
down_revision: Union[str, Sequence[str], None] = '0014_performance_critical_indexes'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
