"""Add role column to user_bot_credentials table.

Revision ID: 0046_add_bot_role
Revises: 0045_mtproto_interval
Create Date: 2025-12-12 00:30:00.000000

This migration adds a 'role' column to distinguish between:
- 'system': System-owned bots configured via environment (for admin operations)
- 'user': User-owned bots in multi-tenant system (default)
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0046_add_bot_role"
down_revision = "0045_mtproto_interval_config"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add role column to user_bot_credentials table."""
    
    # Add role column with default 'user' for existing records
    op.add_column(
        "user_bot_credentials",
        sa.Column(
            "role",
            sa.String(20),
            nullable=False,
            server_default="user",
            comment="Bot role: 'system' for system-owned, 'user' for user-owned bots"
        )
    )
    
    # Add index for efficient role-based filtering
    op.create_index(
        "idx_bot_credentials_role",
        "user_bot_credentials",
        ["role"]
    )
    
    # Add composite index for common query pattern (role + status)
    op.create_index(
        "idx_bot_credentials_role_status",
        "user_bot_credentials",
        ["role", "status"]
    )


def downgrade() -> None:
    """Remove role column from user_bot_credentials table."""
    
    # Drop indexes first
    op.drop_index("idx_bot_credentials_role_status", table_name="user_bot_credentials")
    op.drop_index("idx_bot_credentials_role", table_name="user_bot_credentials")
    
    # Drop column
    op.drop_column("user_bot_credentials", "role")
