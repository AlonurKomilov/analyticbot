"""
Role Hierarchy Management Service

This module provides services for managing the 4-role hierarchical system,
including role validation, permission management, and migration utilities.
"""

import logging
from dataclasses import dataclass
from typing import Any

from .permissions import (
    Permission,
    PermissionChecker,
    get_migration_permissions,
    get_permissions_for_role,
)
from .roles import (
    AdministrativeRole,
    ApplicationRole,
    get_role_level,
    has_role_or_higher,
    is_administrative_role,
    migrate_admin_role,
    migrate_user_role,
)

logger = logging.getLogger(__name__)


@dataclass
class UserRoleInfo:
    """Complete role and permission information for a user."""

    role: str
    permissions: set[Permission]
    is_administrative: bool
    role_level: int
    migration_profile: str | None = None


class RoleHierarchyService:
    """Service for managing role hierarchy and permissions."""

    def __init__(self):
        self.permission_checker = PermissionChecker()

    def get_user_role_info(
        self,
        role: str,
        additional_permissions: list[str] | None = None,
        migration_profile: str | None = None,
    ) -> UserRoleInfo:
        """
        Get complete role information for a user.

        Args:
            role: The user's primary role
            additional_permissions: Extra permissions (for migrated users)
            migration_profile: Migration profile for special permission sets

        Returns:
            Complete role information
        """
        # Get base permissions for role
        permissions = get_permissions_for_role(role)

        # Add migration profile permissions if specified
        if migration_profile:
            migration_perms = get_migration_permissions(migration_profile)
            permissions.update(migration_perms)

        # Add any additional permissions
        if additional_permissions:
            extra_permissions = self.permission_checker.get_role_permissions(
                role, additional_permissions
            )
            permissions.update(extra_permissions)

        return UserRoleInfo(
            role=role,
            permissions=permissions,
            is_administrative=is_administrative_role(role),
            role_level=get_role_level(role),
            migration_profile=migration_profile,
        )

    def can_user_access_resource(
        self,
        user_role_info: UserRoleInfo,
        required_role: str | None = None,
        required_permission: Permission | None = None,
        required_permissions: list[Permission] | None = None,
    ) -> bool:
        """
        Check if user can access a resource based on role or permissions.

        Args:
            user_role_info: User's role information
            required_role: Minimum required role level
            required_permission: Single required permission
            required_permissions: List of required permissions (user needs ALL)

        Returns:
            True if user can access the resource
        """
        # Check role-based access
        if required_role:
            if not has_role_or_higher(user_role_info.role, required_role):
                return False

        # Check single permission
        if required_permission:
            if not self.permission_checker.has_permission(
                user_role_info.permissions, required_permission
            ):
                return False

        # Check multiple permissions (ALL required)
        if required_permissions:
            if not self.permission_checker.has_all_permissions(
                user_role_info.permissions, required_permissions
            ):
                return False

        return True

    def migrate_legacy_role(
        self, old_role: str, role_type: str = "user"
    ) -> tuple[str, list[str], str | None]:
        """
        Migrate a legacy role to the new system.

        Args:
            old_role: The legacy role value
            role_type: "user" for UserRole migration, "admin" for AdminRole migration

        Returns:
            Tuple of (new_role, additional_permissions, migration_profile)
        """
        if role_type == "user":
            new_role, additional_perms = migrate_user_role(old_role)

            # Determine migration profile
            migration_profile = None
            if old_role == "readonly":
                migration_profile = "readonly_user"
            elif old_role == "analyst":
                migration_profile = "analyst_user"

            return new_role, additional_perms, migration_profile

        elif role_type == "admin":
            new_role, additional_perms = migrate_admin_role(old_role)

            # Determine migration profile
            migration_profile = None
            if old_role == "support":
                migration_profile = "support_moderator"

            return new_role, additional_perms, migration_profile

        else:
            logger.warning(f"Unknown role type: {role_type}")
            return ApplicationRole.USER.value, [], None

    def get_available_roles(self, include_deprecated: bool = False) -> dict[str, list[str]]:
        """
        Get all available roles in the system.

        Args:
            include_deprecated: Whether to include deprecated roles

        Returns:
            Dictionary with role categories and their values
        """
        roles = {
            "application": [role.value for role in ApplicationRole],
            "administrative": [role.value for role in AdministrativeRole],
        }

        if include_deprecated:
            from .roles import AdminRole, UserRole

            roles["deprecated_user"] = [role.value for role in UserRole]
            roles["deprecated_admin"] = [role.value for role in AdminRole]

        return roles

    def validate_role_assignment(self, assigner_role: str, target_role: str) -> bool:
        """
        Validate if a user can assign a specific role to another user.

        Rules:
        - SUPER_ADMIN can assign any role
        - MODERATOR can assign USER and GUEST roles
        - Users cannot assign roles

        Args:
            assigner_role: Role of the user making the assignment
            target_role: Role being assigned

        Returns:
            True if assignment is allowed
        """
        get_role_level(assigner_role)
        target_level = get_role_level(target_role)

        # SUPER_ADMIN can assign any role
        if assigner_role == AdministrativeRole.SUPER_ADMIN.value:
            return True

        # MODERATOR can assign roles below their level
        if assigner_role == AdministrativeRole.MODERATOR.value:
            return target_level < get_role_level(AdministrativeRole.MODERATOR.value)

        # Regular users cannot assign roles
        return False

    def get_role_hierarchy_display(self) -> dict[str, Any]:
        """
        Get role hierarchy for display purposes.

        Returns:
            Hierarchical structure of roles with metadata
        """
        return {
            "hierarchy": [
                {
                    "role": ApplicationRole.GUEST.value,
                    "level": get_role_level(ApplicationRole.GUEST.value),
                    "type": "application",
                    "description": "Unauthenticated or limited access",
                },
                {
                    "role": ApplicationRole.USER.value,
                    "level": get_role_level(ApplicationRole.USER.value),
                    "type": "application",
                    "description": "Authenticated application users",
                },
                {
                    "role": AdministrativeRole.MODERATOR.value,
                    "level": get_role_level(AdministrativeRole.MODERATOR.value),
                    "type": "administrative",
                    "description": "Content moderation and user management",
                },
                {
                    "role": AdministrativeRole.SUPER_ADMIN.value,
                    "level": get_role_level(AdministrativeRole.SUPER_ADMIN.value),
                    "type": "administrative",
                    "description": "System administration and configuration",
                },
            ],
            "total_roles": 4,
            "administrative_roles": 2,
            "application_roles": 2,
        }


# Global service instance
role_hierarchy_service = RoleHierarchyService()


# Convenience functions using the service
def check_user_access(
    user_role: str,
    user_permissions: list[str] | None = None,
    required_role: str | None = None,
    required_permission: str | None = None,
    migration_profile: str | None = None,
) -> bool:
    """
    Convenience function to check user access.

    Args:
        user_role: User's role
        user_permissions: Additional user permissions
        required_role: Required minimum role
        required_permission: Required permission
        migration_profile: Migration profile for special cases

    Returns:
        True if user has access
    """
    user_info = role_hierarchy_service.get_user_role_info(
        role=user_role,
        additional_permissions=user_permissions,
        migration_profile=migration_profile,
    )

    req_perm = Permission(required_permission) if required_permission else None

    return role_hierarchy_service.can_user_access_resource(
        user_role_info=user_info,
        required_role=required_role,
        required_permission=req_perm,
    )


def migrate_user_to_new_system(old_role: str, role_type: str = "user") -> dict:
    """
    Migrate a user from old role system to new system.

    Returns:
        Migration information dictionary
    """
    new_role, additional_perms, migration_profile = role_hierarchy_service.migrate_legacy_role(
        old_role, role_type
    )

    return {
        "old_role": old_role,
        "new_role": new_role,
        "additional_permissions": additional_perms,
        "migration_profile": migration_profile,
        "role_type": role_type,
    }


# Export the role hierarchy system
__all__ = [
    "RoleHierarchyService",
    "UserRoleInfo",
    "role_hierarchy_service",
    "check_user_access",
    "migrate_user_to_new_system",
]
