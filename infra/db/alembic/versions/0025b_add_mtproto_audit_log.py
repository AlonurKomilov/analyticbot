"""add_mtproto_audit_log

Revision ID: 0025
Revises: 0022_add_mtproto_enabled_flag
Create Date: 2025-11-03 07:27:39.652075

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0025"
down_revision: str | Sequence[str] | None = "0022_add_mtproto_enabled_flag"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add MTProto audit log table."""
    # Create audit log table for MTProto events
    op.create_table(
        "mtproto_audit_log",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False, index=True),
        sa.Column(
            "channel_id", sa.BigInteger(), nullable=True, index=True
        ),  # NULL = global setting
        sa.Column(
            "action", sa.String(50), nullable=False
        ),  # 'enabled', 'disabled', 'setup', 'removed', etc.
        sa.Column("previous_state", sa.Boolean(), nullable=True),
        sa.Column("new_state", sa.Boolean(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),  # IPv4 or IPv6
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),  # Additional context
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
            index=True,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )

    # Create index for common queries
    op.create_index(
        "ix_mtproto_audit_user_timestamp", "mtproto_audit_log", ["user_id", "timestamp"]
    )


def downgrade() -> None:
    """Remove MTProto audit log table."""
    op.drop_index("ix_mtproto_audit_user_timestamp", table_name="mtproto_audit_log")
    op.drop_table("mtproto_audit_log")
