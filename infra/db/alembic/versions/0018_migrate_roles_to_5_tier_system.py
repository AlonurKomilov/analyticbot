"""Migrate role system from 4-tier to 5-tier (viewer|user|moderator|admin|owner)

Revision ID: 0018_migrate_roles_to_5_tier_system
Revises: 0017_cache_optimization_indexes
Create Date: 2025-10-23 09:22:52.000000

CRITICAL MIGRATION: This updates user role values in the database.
- Changes: guest → viewer, super_admin → owner
- Adds: New 'admin' and 'owner' roles to system
- Safe: Includes rollback capability and validation checks

REQUIREMENTS:
1. Database backup created before running
2. Test on staging environment first
3. Verify all services stopped during migration
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy import text

revision = "0018"
down_revision = "0017"
branch_labels = None
depends_on = None


def upgrade():
    """
    Migrate role values from 4-tier to 5-tier system.

    Changes:
    - guest → viewer (public read-only access)
    - super_admin → owner (system owner with full control)
    - Adds 'admin' as new platform administrator role

    Tables affected:
    - admin_users (or superadmin_users if using old schema)
    """

    print("\n" + "=" * 80)
    print("🔄 PHASE 3: ROLE MIGRATION TO 5-TIER SYSTEM")
    print("=" * 80)

    # Detect which table name is being used
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()

    # Determine the correct table name and check for role column
    admin_table = None
    has_role_column = False

    if "admin_users" in tables:
        admin_table = "admin_users"
        columns = [c["name"] for c in inspector.get_columns(admin_table)]
        has_role_column = "role" in columns
        print(f"✅ Found table: {admin_table} (has role column: {has_role_column})")
    elif "superadmin_users" in tables:
        admin_table = "superadmin_users"
        columns = [c["name"] for c in inspector.get_columns(admin_table)]
        has_role_column = "role" in columns
        print(f"✅ Found table: {admin_table} (has role column: {has_role_column})")
    else:
        print("⚠️  No admin users table found - skipping migration")
        return

    if not has_role_column:
        print(f"⚠️  Table {admin_table} does not have a 'role' column - skipping migration")
        print("   (Table uses role_id foreign key instead of direct role column)")
        return

    # Step 1: Check current role distribution
    print("\n📊 Step 1: Analyzing current role distribution...")
    result = connection.execute(
        text(f"""
            SELECT role, COUNT(*) as count
            FROM {admin_table}
            GROUP BY role
            ORDER BY count DESC
        """)
    )

    role_counts = {row[0]: row[1] for row in result}
    total_users = sum(role_counts.values())

    print(f"   Total users: {total_users}")
    for role, count in role_counts.items():
        print(f"   - {role}: {count} users")

    # Step 2: Validate migration prerequisites
    print("\n🔍 Step 2: Validating migration prerequisites...")

    # Check for unexpected roles
    expected_old_roles = {
        "guest",
        "user",
        "moderator",
        "admin",
        "super_admin",
        "support",
        "readonly",
        "analyst",
    }
    unexpected_roles = set(role_counts.keys()) - expected_old_roles

    if unexpected_roles:
        print(f"⚠️  WARNING: Found unexpected roles: {unexpected_roles}")
        print("   These will NOT be migrated. Manual intervention may be required.")
    else:
        print("✅ All roles are recognized")

    # Step 3: Perform role migrations
    print("\n🔄 Step 3: Migrating role values...")

    migrations = [
        ("guest", "viewer", "Public read-only access"),
        ("super_admin", "owner", "System owner with full control"),
    ]

    for old_role, new_role, description in migrations:
        if old_role in role_counts:
            count = role_counts[old_role]
            print(f"   Migrating '{old_role}' → '{new_role}' ({count} users)")
            print(f"   Description: {description}")

            connection.execute(
                text(f"""
                    UPDATE {admin_table}
                    SET role = :new_role
                    WHERE role = :old_role
                """),
                {"new_role": new_role, "old_role": old_role},
            )

            # Verify migration
            verify_result = connection.execute(
                text(f"""
                    SELECT COUNT(*)
                    FROM {admin_table}
                    WHERE role = :old_role
                """),
                {"old_role": old_role},
            )
            remaining = verify_result.scalar()

            if remaining == 0:
                print(f"   ✅ Successfully migrated all {count} users")
            else:
                raise Exception(
                    f"❌ Migration failed! {remaining} users still have role '{old_role}'"
                )
        else:
            print(f"   ⏭️  No users with role '{old_role}' - skipping")

    # Step 4: Validate final state
    print("\n✅ Step 4: Validating migration results...")

    result = connection.execute(
        text(f"""
            SELECT role, COUNT(*) as count
            FROM {admin_table}
            GROUP BY role
            ORDER BY count DESC
        """)
    )

    new_role_counts = {row[0]: row[1] for row in result}

    print("   New role distribution:")
    for role, count in new_role_counts.items():
        print(f"   - {role}: {count} users")

    # Verify no old roles remain
    old_roles_found = {"guest", "super_admin"} & set(new_role_counts.keys())
    if old_roles_found:
        raise Exception(f"❌ Migration incomplete! Old roles still exist: {old_roles_found}")

    # Verify all roles are valid
    valid_new_roles = {"viewer", "user", "moderator", "admin", "owner"}
    invalid_roles = set(new_role_counts.keys()) - valid_new_roles

    if invalid_roles:
        print(f"   ⚠️  WARNING: Found non-standard roles: {invalid_roles}")
        print("   These may need manual migration or could be legacy test data")

    print("\n" + "=" * 80)
    print("✅ MIGRATION COMPLETE")
    print("=" * 80)
    print(f"✅ Migrated roles for {total_users} users")
    print("✅ Old roles removed: guest, super_admin")
    print("✅ New 5-tier system: viewer < user < moderator < admin < owner")
    print("=" * 80 + "\n")


def downgrade():
    """
    Rollback role migration from 5-tier to 4-tier system.

    This reverses the upgrade changes:
    - viewer → guest
    - owner → super_admin

    WARNING: This should only be used in emergency rollback scenarios.
    """

    print("\n" + "=" * 80)
    print("⚠️  PHASE 3 ROLLBACK: REVERTING TO 4-TIER SYSTEM")
    print("=" * 80)

    # Detect which table name is being used
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()

    admin_table = None
    if "admin_users" in tables:
        admin_table = "admin_users"
    elif "superadmin_users" in tables:
        admin_table = "superadmin_users"
    else:
        print("⚠️  No admin users table found - skipping rollback")
        return

    print(f"✅ Rolling back table: {admin_table}")

    # Check current state
    print("\n📊 Current role distribution:")
    result = connection.execute(
        text(f"""
            SELECT role, COUNT(*) as count
            FROM {admin_table}
            GROUP BY role
            ORDER BY count DESC
        """)
    )

    for row in result:
        print(f"   - {row[0]}: {row[1]} users")

    # Perform rollback
    print("\n🔄 Rolling back role values...")

    rollbacks = [
        ("viewer", "guest", "Public read-only access"),
        ("owner", "super_admin", "System administrator"),
    ]

    for new_role, old_role, description in rollbacks:
        result = connection.execute(
            text(f"""
                SELECT COUNT(*)
                FROM {admin_table}
                WHERE role = :new_role
            """),
            {"new_role": new_role},
        )
        count = result.scalar()

        if count is not None and count > 0:
            print(f"   Rolling back '{new_role}' → '{old_role}' ({count} users)")

            connection.execute(
                text(f"""
                    UPDATE {admin_table}
                    SET role = :old_role
                    WHERE role = :new_role
                """),
                {"old_role": old_role, "new_role": new_role},
            )

            print(f"   ✅ Rolled back {count} users")
        else:
            print(f"   ⏭️  No users with role '{new_role}' - skipping")

    # Validate rollback
    print("\n✅ Rollback validation:")
    result = connection.execute(
        text(f"""
            SELECT role, COUNT(*) as count
            FROM {admin_table}
            GROUP BY role
            ORDER BY count DESC
        """)
    )

    print("   Role distribution after rollback:")
    for row in result:
        print(f"   - {row[0]}: {row[1]} users")

    print("\n" + "=" * 80)
    print("✅ ROLLBACK COMPLETE")
    print("=" * 80)
    print("⚠️  System reverted to 4-tier role system")
    print("⚠️  Remember to also rollback code changes!")
    print("=" * 80 + "\n")
