"""
Permission System for 4-Role Hierarchical Architecture

This module defines granular permissions that work with the simplified role system.
Instead of creating many roles, we use permissions to control feature access within roles.
"""

from dataclasses import dataclass
from enum import Enum


class Permission(Enum):
    """
    Granular permissions for feature control within simplified roles.

    Analytics Permissions:
    """

    # Analytics & Reporting
    VIEW_ANALYTICS = "view_analytics"
    EXPORT_ANALYTICS = "export_analytics"
    MANAGE_ANALYTICS = "manage_analytics"

    # User Management
    VIEW_USERS = "view_users"
    MANAGE_USERS = "manage_users"
    DELETE_USERS = "delete_users"

    # Content Management
    VIEW_CONTENT = "view_content"
    EDIT_CONTENT = "edit_content"
    DELETE_CONTENT = "delete_content"
    MODERATE_CONTENT = "moderate_content"

    # System Administration
    SYSTEM_CONFIG = "system_config"
    VIEW_LOGS = "view_logs"
    MANAGE_SETTINGS = "manage_settings"
    DATABASE_ACCESS = "database_access"

    # Bot Management
    BOT_CONFIG = "bot_config"
    BOT_COMMANDS = "bot_commands"
    BOT_ANALYTICS = "bot_analytics"

    # API Access
    API_READ = "api_read"
    API_WRITE = "api_write"
    API_ADMIN = "api_admin"

    # Special Access Modes
    READONLY_ACCESS = "readonly_access"  # For former READONLY role
    CUSTOMER_SUPPORT = "customer_support"  # For former SUPPORT role

    # Demo & Testing
    DEMO_ACCESS = "demo_access"
    TESTING_ACCESS = "testing_access"


@dataclass
class RolePermissions:
    """Permission set for a specific role."""

    role: str
    permissions: set[Permission]
    description: str


# Default permission sets for each role
DEFAULT_ROLE_PERMISSIONS: dict[str, RolePermissions] = {
    # Legacy role for backwards compatibility (maps to viewer)
    "guest": RolePermissions(
        role="guest",
        permissions={
            Permission.DEMO_ACCESS,
        },
        description="DEPRECATED: Use 'viewer' instead. Limited access for unauthenticated users",
    ),
    "user": RolePermissions(
        role="user",
        permissions={
            Permission.VIEW_CONTENT,
            Permission.API_READ,
            Permission.BOT_COMMANDS,
        },
        description="Standard authenticated user permissions",
    ),
    "moderator": RolePermissions(
        role="moderator",
        permissions={
            # Inherit user permissions
            Permission.VIEW_CONTENT,
            Permission.API_READ,
            Permission.BOT_COMMANDS,
            # Additional moderator permissions
            Permission.VIEW_USERS,
            Permission.MANAGE_USERS,
            Permission.EDIT_CONTENT,
            Permission.MODERATE_CONTENT,
            Permission.VIEW_ANALYTICS,
            Permission.BOT_ANALYTICS,
            Permission.API_WRITE,
        },
        description="Content moderation and user management",
    ),
    "admin": RolePermissions(
        role="admin",
        permissions={
            # Platform administration - most permissions except sensitive system config
            *Permission.__members__.values()
        },
        description="Platform administration access",
    ),
    "owner": RolePermissions(
        role="owner",
        permissions={
            # All permissions - system owner with full control
            *Permission.__members__.values()
        },
        description="Full system ownership and control",
    ),
    # Legacy role for backwards compatibility
    "super_admin": RolePermissions(
        role="super_admin",
        permissions={
            # Maps to owner - full system administration access
            *Permission.__members__.values()
        },
        description="DEPRECATED: Use 'owner' instead. Full system administration access",
    ),
}


# Special permission profiles for migrated roles
MIGRATION_PERMISSION_PROFILES: dict[str, set[Permission]] = {
    # Former READONLY users get USER + readonly_access
    "readonly_user": {
        Permission.VIEW_CONTENT,
        Permission.API_READ,
        Permission.READONLY_ACCESS,
    },
    # Former ANALYST users get USER + analytics access
    "analyst_user": {
        Permission.VIEW_CONTENT,
        Permission.API_READ,
        Permission.BOT_COMMANDS,
        Permission.VIEW_ANALYTICS,
        Permission.EXPORT_ANALYTICS,
        Permission.BOT_ANALYTICS,
    },
    # Former SUPPORT admins get MODERATOR + customer support
    "support_moderator": {
        Permission.VIEW_CONTENT,
        Permission.API_READ,
        Permission.BOT_COMMANDS,
        Permission.VIEW_USERS,
        Permission.MANAGE_USERS,
        Permission.EDIT_CONTENT,
        Permission.MODERATE_CONTENT,
        Permission.CUSTOMER_SUPPORT,
        Permission.API_WRITE,
    },
}


class PermissionChecker:
    """Utility class for checking permissions."""

    @staticmethod
    def has_permission(user_permissions: set[Permission], required_permission: Permission) -> bool:
        """Check if user has a specific permission."""
        return required_permission in user_permissions

    @staticmethod
    def has_any_permission(
        user_permissions: set[Permission], required_permissions: list[Permission]
    ) -> bool:
        """Check if user has any of the required permissions."""
        return bool(user_permissions.intersection(required_permissions))

    @staticmethod
    def has_all_permissions(
        user_permissions: set[Permission], required_permissions: list[Permission]
    ) -> bool:
        """Check if user has all required permissions."""
        return set(required_permissions).issubset(user_permissions)

    @staticmethod
    def get_role_permissions(
        role: str, additional_permissions: list[str] | None = None
    ) -> set[Permission]:
        """
        Get permissions for a role, optionally adding extra permissions.

        Args:
            role: The user's role
            additional_permissions: Extra permissions to add (for migrated users)

        Returns:
            Set of permissions for the role
        """
        base_permissions = DEFAULT_ROLE_PERMISSIONS.get(
            role, DEFAULT_ROLE_PERMISSIONS["user"]
        ).permissions

        if additional_permissions:
            # Convert string permissions to Permission enums
            extra_perms = set()
            for perm_str in additional_permissions:
                try:
                    extra_perms.add(Permission(perm_str))
                except ValueError:
                    # Skip invalid permissions
                    pass
            return base_permissions.union(extra_perms)

        return base_permissions.copy()


def get_permissions_for_role(role: str) -> set[Permission]:
    """Get default permissions for a role."""
    return DEFAULT_ROLE_PERMISSIONS.get(role, DEFAULT_ROLE_PERMISSIONS["user"]).permissions


def get_migration_permissions(profile: str) -> set[Permission]:
    """Get permissions for a migration profile."""
    return MIGRATION_PERMISSION_PROFILES.get(profile, set())


# Convenience functions for common permission checks
def can_view_analytics(permissions: set[Permission]) -> bool:
    """Check if user can view analytics."""
    return Permission.VIEW_ANALYTICS in permissions


def can_manage_users(permissions: set[Permission]) -> bool:
    """Check if user can manage other users."""
    return Permission.MANAGE_USERS in permissions


def can_access_admin_features(permissions: set[Permission]) -> bool:
    """Check if user can access administrative features."""
    admin_permissions = {
        Permission.SYSTEM_CONFIG,
        Permission.MANAGE_SETTINGS,
        Permission.DATABASE_ACCESS,
        Permission.API_ADMIN,
    }
    return bool(permissions.intersection(admin_permissions))


def is_readonly_user(permissions: set[Permission]) -> bool:
    """Check if user is in readonly mode."""
    return Permission.READONLY_ACCESS in permissions


# Export the permission system
__all__ = [
    "Permission",
    "RolePermissions",
    "PermissionChecker",
    "DEFAULT_ROLE_PERMISSIONS",
    "MIGRATION_PERMISSION_PROFILES",
    "get_permissions_for_role",
    "get_migration_permissions",
    "can_view_analytics",
    "can_manage_users",
    "can_access_admin_features",
    "is_readonly_user",
]
