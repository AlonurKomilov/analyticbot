"""Add user suspension tracking fields

Revision ID: 0038_add_user_suspension_fields
Revises: 0037_remove_unused_indexes
Create Date: 2025-12-04

Adds fields to track suspension details:
- suspension_reason: Why the user was suspended
- suspended_at: When the suspension occurred
- suspended_by: Admin who suspended the user
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0039_add_user_suspension_fields"
down_revision = "0038"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add suspension tracking fields to users table
    op.add_column(
        "users",
        sa.Column("suspension_reason", sa.String(500), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("suspended_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("suspended_by", sa.BigInteger(), nullable=True),
    )

    # Add index for finding suspended users quickly
    op.create_index(
        "ix_users_status_suspended",
        "users",
        ["status"],
        postgresql_where=sa.text("status = 'suspended'"),
    )


def downgrade() -> None:
    op.drop_index("ix_users_status_suspended", table_name="users")
    op.drop_column("users", "suspended_by")
    op.drop_column("users", "suspended_at")
    op.drop_column("users", "suspension_reason")
