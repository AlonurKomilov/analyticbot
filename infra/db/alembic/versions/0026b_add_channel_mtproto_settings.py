"""add_channel_mtproto_settings

Revision ID: 0026
Revises: 0025_add_mtproto_audit_log
Create Date: 2025-11-03 07:30:39.566753

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0026"
down_revision: str | Sequence[str] | None = "0025"  # add_mtproto_audit_log
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add per-channel MTProto settings table."""
    # Create table for granular per-channel MTProto control
    op.create_table(
        "channel_mtproto_settings",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False, index=True),
        sa.Column("channel_id", sa.BigInteger(), nullable=False, index=True),
        sa.Column("mtproto_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "channel_id", name="uq_user_channel_mtproto"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["channel_id"], ["channels.id"], ondelete="CASCADE"),
    )

    # Create index for common queries
    op.create_index(
        "ix_channel_mtproto_user_enabled",
        "channel_mtproto_settings",
        ["user_id", "mtproto_enabled"],
    )


def downgrade() -> None:
    """Remove per-channel MTProto settings table."""
    op.drop_index("ix_channel_mtproto_user_enabled", table_name="channel_mtproto_settings")
    op.drop_table("channel_mtproto_settings")
