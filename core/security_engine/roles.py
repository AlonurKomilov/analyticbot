"""
Simplified 4-Role Hierarchical System

This module defines the new simplified role system with clear hierarchy:
- ApplicationRole: GUEST, USER (end-user roles)
- AdministrativeRole: MODERATOR, SUPER_ADMIN (staff roles)

The hierarchy is: GUEST < USER < MODERATOR < SUPER_ADMIN
"""

from enum import Enum
from typing import Dict, List, Set
import warnings


class ApplicationRole(Enum):
    """
    End-user application roles for general users.
    
    Hierarchy: GUEST < USER
    """
    GUEST = "guest"      # Unauthenticated or limited access users
    USER = "user"        # Authenticated application users


class AdministrativeRole(Enum):
    """
    Administrative roles for staff and system management.
    
    Hierarchy: MODERATOR < SUPER_ADMIN
    """
    MODERATOR = "moderator"      # Content moderation and user management
    SUPER_ADMIN = "super_admin"  # System administration and configuration


class RoleLevel(Enum):
    """Role level hierarchy for comparison operations."""
    GUEST = 1
    USER = 2
    MODERATOR = 3
    SUPER_ADMIN = 4


# Role hierarchy mapping
ROLE_HIERARCHY: Dict[str, int] = {
    ApplicationRole.GUEST.value: RoleLevel.GUEST.value,
    ApplicationRole.USER.value: RoleLevel.USER.value,
    AdministrativeRole.MODERATOR.value: RoleLevel.MODERATOR.value,
    AdministrativeRole.SUPER_ADMIN.value: RoleLevel.SUPER_ADMIN.value,
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
    """Check if a role is administrative (MODERATOR or SUPER_ADMIN)."""
    return role in [AdministrativeRole.MODERATOR.value, AdministrativeRole.SUPER_ADMIN.value]


def is_application_role(role: str) -> bool:
    """Check if a role is an application role (GUEST or USER)."""
    return role in [ApplicationRole.GUEST.value, ApplicationRole.USER.value]


# Backwards compatibility - DEPRECATED
# These will be removed in a future version
class UserRole(str, Enum):
    """
    DEPRECATED: Use ApplicationRole and AdministrativeRole instead.
    
    Legacy UserRole mapping:
    - GUEST → ApplicationRole.GUEST
    - USER → ApplicationRole.USER  
    - READONLY → ApplicationRole.USER + readonly_access permission
    - ANALYST → ApplicationRole.USER + view_analytics permission
    - MODERATOR → AdministrativeRole.MODERATOR
    - ADMIN → AdministrativeRole.SUPER_ADMIN
    """
    GUEST = "guest"
    USER = "user"
    READONLY = "readonly"
    ANALYST = "analyst"
    MODERATOR = "moderator"
    ADMIN = "admin"


class AdminRole(str, Enum):
    """
    DEPRECATED: Use AdministrativeRole instead.
    
    Legacy AdminRole mapping:
    - SUPPORT → AdministrativeRole.MODERATOR + customer_support permission
    - MODERATOR → AdministrativeRole.MODERATOR
    - ADMIN → AdministrativeRole.SUPER_ADMIN
    - SUPER_ADMIN → AdministrativeRole.SUPER_ADMIN
    """
    SUPPORT = "support"
    MODERATOR = "moderator"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


# Migration helper functions
def migrate_user_role(old_role: str) -> tuple[str, List[str]]:
    """
    Migrate old UserRole to new system.
    
    Returns:
        Tuple of (new_role, additional_permissions)
    """
    migration_map = {
        "guest": (ApplicationRole.GUEST.value, []),
        "user": (ApplicationRole.USER.value, []),
        "readonly": (ApplicationRole.USER.value, ["readonly_access"]),
        "analyst": (ApplicationRole.USER.value, ["view_analytics"]),
        "moderator": (AdministrativeRole.MODERATOR.value, []),
        "admin": (AdministrativeRole.SUPER_ADMIN.value, []),
    }
    return migration_map.get(old_role, (ApplicationRole.USER.value, []))


def migrate_admin_role(old_role: str) -> tuple[str, List[str]]:
    """
    Migrate old AdminRole to new system.
    
    Returns:
        Tuple of (new_role, additional_permissions)
    """
    migration_map = {
        "support": (AdministrativeRole.MODERATOR.value, ["customer_support"]),
        "moderator": (AdministrativeRole.MODERATOR.value, []),
        "admin": (AdministrativeRole.SUPER_ADMIN.value, []),
        "super_admin": (AdministrativeRole.SUPER_ADMIN.value, []),
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