"""
Unified 5-Role Hierarchical System

This module defines the new unified role system with clear hierarchy:
- ApplicationRole: VIEWER, USER (end-user roles)
- AdministrativeRole: MODERATOR, ADMIN, OWNER (staff roles)

The hierarchy is: VIEWER < USER < MODERATOR < ADMIN < OWNER

Role Definitions:
- VIEWER: Public read-only access (unauthenticated or demo users)
- USER: Authenticated application users (trial/paid customers)
- MODERATOR: Support team and content moderation
- ADMIN: Platform administrators with system configuration access
- OWNER: System owner with full control (highest privilege)
"""

from enum import Enum


class ApplicationRole(Enum):
    """
    End-user application roles for general users.

    Hierarchy: VIEWER < USER
    """

    VIEWER = "viewer"  # Public read-only access, unauthenticated users
    USER = "user"  # Authenticated application users


class AdministrativeRole(Enum):
    """
    Administrative roles for staff and system management.

    Hierarchy: MODERATOR < ADMIN < OWNER
    """

    MODERATOR = "moderator"  # Content moderation and user management
    ADMIN = "admin"  # Platform administration and configuration
    OWNER = "owner"  # System owner with full control


class RoleLevel(Enum):
    """Role level hierarchy for comparison operations."""

    VIEWER = 0
    USER = 1
    MODERATOR = 2
    ADMIN = 3
    OWNER = 4


# Role hierarchy mapping
ROLE_HIERARCHY: dict[str, int] = {
    ApplicationRole.VIEWER.value: RoleLevel.VIEWER.value,
    ApplicationRole.USER.value: RoleLevel.USER.value,
    AdministrativeRole.MODERATOR.value: RoleLevel.MODERATOR.value,
    AdministrativeRole.ADMIN.value: RoleLevel.ADMIN.value,
    AdministrativeRole.OWNER.value: RoleLevel.OWNER.value,
}


def get_role_level(role: str) -> int:
    """Get the hierarchical level of a role."""
    return ROLE_HIERARCHY.get(role, 0)


def has_role_or_higher(user_role: str, required_role: str) -> bool:
    """
    Check if user role meets or exceeds the required role level.

    Args:
        user_role: The user's current role
        required_role: The minimum required role

    Returns:
        True if user role is equal or higher than required role
    """
    user_level = get_role_level(user_role)
    required_level = get_role_level(required_role)
    return user_level >= required_level


def is_administrative_role(role: str) -> bool:
    """Check if a role is administrative (MODERATOR, ADMIN, or OWNER)."""
    return role in [
        AdministrativeRole.MODERATOR.value,
        AdministrativeRole.ADMIN.value,
        AdministrativeRole.OWNER.value,
    ]


def is_application_role(role: str) -> bool:
    """Check if a role is an application role (VIEWER or USER)."""
    return role in [ApplicationRole.VIEWER.value, ApplicationRole.USER.value]


# Backwards compatibility - DEPRECATED
# These will be removed in a future version
class UserRole(str, Enum):
    """
    DEPRECATED: Use ApplicationRole and AdministrativeRole instead.

    Legacy UserRole mapping:
    - GUEST → ApplicationRole.VIEWER
    - USER → ApplicationRole.USER
    - READONLY → ApplicationRole.VIEWER (with optional readonly_access permission)
    - ANALYST → ApplicationRole.USER + view_analytics permission
    - MODERATOR → AdministrativeRole.MODERATOR
    - ADMIN → AdministrativeRole.ADMIN or OWNER (context-dependent)
    """

    # New 5-role system
    VIEWER = "viewer"
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"
    OWNER = "owner"
    # Legacy deprecated roles
    GUEST = "guest"
    READONLY = "readonly"
    ANALYST = "analyst"


class AdminRole(str, Enum):
    """
    DEPRECATED: Use AdministrativeRole instead.

    Legacy AdminRole mapping:
    - SUPPORT → AdministrativeRole.MODERATOR + customer_support permission
    - MODERATOR → AdministrativeRole.MODERATOR
    - ADMIN → AdministrativeRole.ADMIN
    - SUPER_ADMIN → AdministrativeRole.OWNER
    """

    SUPPORT = "support"
    MODERATOR = "moderator"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


# Migration helper functions
def migrate_user_role(old_role: str) -> tuple[str, list[str]]:
    """
    Migrate old UserRole to new 5-role system.

    Returns:
        Tuple of (new_role, additional_permissions)
    """
    migration_map = {
        "guest": (ApplicationRole.VIEWER.value, []),
        "user": (ApplicationRole.USER.value, []),
        "readonly": (ApplicationRole.VIEWER.value, ["readonly_access"]),
        "analyst": (ApplicationRole.USER.value, ["view_analytics"]),
        "moderator": (AdministrativeRole.MODERATOR.value, []),
        "admin": (AdministrativeRole.ADMIN.value, []),  # Legacy admin → new admin
        "superadmin": (AdministrativeRole.OWNER.value, []),  # superadmin → owner
    }
    return migration_map.get(old_role, (ApplicationRole.USER.value, []))


def migrate_admin_role(old_role: str) -> tuple[str, list[str]]:
    """
    Migrate old AdminRole to new 5-role system.

    Returns:
        Tuple of (new_role, additional_permissions)
    """
    migration_map = {
        "support": (AdministrativeRole.MODERATOR.value, ["customer_support"]),
        "moderator": (AdministrativeRole.MODERATOR.value, []),
        "admin": (AdministrativeRole.ADMIN.value, []),  # Legacy admin → new admin
        "super_admin": (AdministrativeRole.OWNER.value, []),  # super_admin → owner
    }
    return migration_map.get(old_role, (AdministrativeRole.MODERATOR.value, []))


# Export the new role system
__all__ = [
    "ApplicationRole",
    "AdministrativeRole",
    "RoleLevel",
    "get_role_level",
    "has_role_or_higher",
    "is_administrative_role",
    "is_application_role",
    "migrate_user_role",
    "migrate_admin_role",
    # Deprecated but kept for backwards compatibility
    "UserRole",
    "AdminRole",
]
