"""Create SuperAdmin system tables and indexes

Revision ID: 0008_create_superadmin_system
Revises: 0007_mtproto_stats_tables
Create Date: 2025-01-27 10:30:00.000000
"""

import sqlalchemy as sa
from alembic import op

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade():
    """Create comprehensive SuperAdmin system tables and indexes."""
    # Create admin_roles table
    op.create_table(
        "admin_roles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("permissions", sa.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create superadmin_users table
    op.create_table(
        "superadmin_users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(255), nullable=True),
        sa.Column("first_name", sa.String(255), nullable=True),
        sa.Column("last_name", sa.String(255), nullable=True),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.Column("added_by", sa.BigInteger(), nullable=False),
        sa.Column(
            "added_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("last_activity", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["admin_roles.id"],
        ),
        sa.UniqueConstraint("user_id"),
    )

    # Create admin_audit_log table
    op.create_table(
        "admin_audit_log",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("admin_user_id", sa.BigInteger(), nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(50), nullable=True),
        sa.Column("resource_id", sa.String(100), nullable=True),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column(
            "timestamp",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("success", sa.Boolean(), nullable=False, default=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create admin_sessions table
    op.create_table(
        "admin_sessions",
        sa.Column("id", sa.String(255), nullable=False),
        sa.Column("admin_user_id", sa.BigInteger(), nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "last_activity",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create system_settings table
    op.create_table(
        "system_settings",
        sa.Column("key", sa.String(100), nullable=False),
        sa.Column("value", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("data_type", sa.String(20), nullable=False, default="string"),
        sa.Column("is_system", sa.Boolean(), nullable=False, default=False),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("key"),
    )

    # Create admin_api_keys table
    op.create_table(
        "admin_api_keys",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("admin_user_id", sa.BigInteger(), nullable=False),
        sa.Column("key_hash", sa.String(255), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("permissions", sa.JSON(), nullable=False),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("last_used", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key_hash"),
    )

    # Create indexes for performance
    op.create_index("ix_superadmin_users_user_id", "superadmin_users", ["user_id"])
    op.create_index("ix_superadmin_users_role_id", "superadmin_users", ["role_id"])
    op.create_index("ix_superadmin_users_is_active", "superadmin_users", ["is_active"])

    op.create_index("ix_admin_audit_log_admin_user_id", "admin_audit_log", ["admin_user_id"])
    op.create_index("ix_admin_audit_log_action", "admin_audit_log", ["action"])
    op.create_index("ix_admin_audit_log_timestamp", "admin_audit_log", ["timestamp"])
    op.create_index(
        "ix_admin_audit_log_resource",
        "admin_audit_log",
        ["resource_type", "resource_id"],
    )

    op.create_index("ix_admin_sessions_admin_user_id", "admin_sessions", ["admin_user_id"])
    op.create_index("ix_admin_sessions_expires_at", "admin_sessions", ["expires_at"])
    op.create_index("ix_admin_sessions_is_active", "admin_sessions", ["is_active"])

    op.create_index("ix_system_settings_is_system", "system_settings", ["is_system"])
    op.create_index("ix_system_settings_updated_at", "system_settings", ["updated_at"])

    op.create_index("ix_admin_api_keys_admin_user_id", "admin_api_keys", ["admin_user_id"])
    op.create_index("ix_admin_api_keys_is_active", "admin_api_keys", ["is_active"])
    op.create_index("ix_admin_api_keys_expires_at", "admin_api_keys", ["expires_at"])


def downgrade():
    """Drop SuperAdmin system tables and indexes."""
    # Drop indexes
    op.drop_index("ix_admin_api_keys_expires_at", table_name="admin_api_keys")
    op.drop_index("ix_admin_api_keys_is_active", table_name="admin_api_keys")
    op.drop_index("ix_admin_api_keys_admin_user_id", table_name="admin_api_keys")

    op.drop_index("ix_system_settings_updated_at", table_name="system_settings")
    op.drop_index("ix_system_settings_is_system", table_name="system_settings")

    op.drop_index("ix_admin_sessions_is_active", table_name="admin_sessions")
    op.drop_index("ix_admin_sessions_expires_at", table_name="admin_sessions")
    op.drop_index("ix_admin_sessions_admin_user_id", table_name="admin_sessions")

    op.drop_index("ix_admin_audit_log_resource", table_name="admin_audit_log")
    op.drop_index("ix_admin_audit_log_timestamp", table_name="admin_audit_log")
    op.drop_index("ix_admin_audit_log_action", table_name="admin_audit_log")
    op.drop_index("ix_admin_audit_log_admin_user_id", table_name="admin_audit_log")

    op.drop_index("ix_superadmin_users_is_active", table_name="superadmin_users")
    op.drop_index("ix_superadmin_users_role_id", table_name="superadmin_users")
    op.drop_index("ix_superadmin_users_user_id", table_name="superadmin_users")

    # Drop tables
    op.drop_table("admin_api_keys")
    op.drop_table("system_settings")
    op.drop_table("admin_sessions")
    op.drop_table("admin_audit_log")
    op.drop_table("superadmin_users")
    op.drop_table("admin_roles")
