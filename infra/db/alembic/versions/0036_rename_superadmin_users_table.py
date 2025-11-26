"""Rename superadmin_users table to admin_users for clarity

Revision ID: 0036_rename_superadmin_users_table
Revises: 0035_add_comments_and_replies_count
Create Date: 2025-11-26 14:00:00.000000

This migration renames the superadmin_users table to admin_users for better clarity.
The table stores all internal team members (owner, admin, moderator roles), not just the owner.

SAFE: Only renames table and sequence, no data changes.
"""

from alembic import op

revision = "0036"
down_revision = "0035"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Rename superadmin_users table to admin_users"""

    print("\n" + "=" * 80)
    print("MIGRATION 0036: Rename superadmin_users → admin_users")
    print("=" * 80 + "\n")

    # Rename table
    print("📝 Renaming table: superadmin_users → admin_users...")
    op.rename_table("superadmin_users", "admin_users")

    # Rename sequence
    print("📝 Renaming sequence: superadmin_users_id_seq → admin_users_id_seq...")
    op.execute("ALTER SEQUENCE superadmin_users_id_seq RENAME TO admin_users_id_seq")

    # Note: Indexes and constraints are automatically renamed by PostgreSQL

    print("\n✅ Migration complete!")
    print("=" * 80)
    print("Table 'admin_users' now stores all internal team members:")
    print("  - owner (project owner)")
    print("  - admin (platform administrators)")
    print("  - moderator (support team)")
    print("=" * 80 + "\n")


def downgrade() -> None:
    """Revert table rename"""

    print("\n" + "=" * 80)
    print("ROLLBACK 0036: Rename admin_users → superadmin_users")
    print("=" * 80 + "\n")

    # Rename table back
    print("📝 Renaming table: admin_users → superadmin_users...")
    op.rename_table("admin_users", "superadmin_users")

    # Rename sequence back
    print("📝 Renaming sequence: admin_users_id_seq → superadmin_users_id_seq...")
    op.execute("ALTER SEQUENCE admin_users_id_seq RENAME TO superadmin_users_id_seq")

    print("\n✅ Rollback complete!")
    print("=" * 80 + "\n")
