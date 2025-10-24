"""Merge analytics and performance optimization branches

Revision ID: 0015_merge_analytics_and_performance
Revises: 0014_performance_critical_indexes
Create Date: 2025-09-17 07:27:16.572667

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision = "0015"
down_revision: str | Sequence[str] | None = "0014"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
