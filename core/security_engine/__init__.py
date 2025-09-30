"""
🔒 PHASE 3.5: SECURITY ENHANCEMENT
Authentication & Authorization Framework

This module provides comprehensive security services including:
- OAuth 2.0 integration (Google, GitHub)
- JWT token management with refresh tokens
- Multi-factor authentication (TOTP)
- Role-based access control (RBAC)
- Session management
- Password security
"""

from .auth import SecurityManager, create_access_token, verify_token, AuthenticationError  # Deprecated wrappers
from .container import get_security_manager, get_rbac_manager, get_security_container
from .mfa import MFAManager, MFAError
from .models import User, UserRole, UserSession, UserStatus, AuthProvider
from .oauth import OAuthManager, OAuthError
from .rbac import RBACManager, RBACError

# New 4-Role Hierarchical System
from .roles import ApplicationRole, AdministrativeRole, UserRole as LegacyUserRole, AdminRole as LegacyAdminRole
from .permissions import Permission, PermissionChecker, get_permissions_for_role
from .role_hierarchy import RoleHierarchyService, UserRoleInfo, role_hierarchy_service
from .decorators import (
    require_permission, require_role, require_admin,
    require_analytics_access, require_user_management, require_system_config,
    permission_check
)

__all__ = [
    "SecurityManager", 
    "AuthenticationError",
    "get_security_manager",
    "get_rbac_manager", 
    "get_security_container",
    "create_access_token",  # Deprecated
    "verify_token",         # Deprecated
    "User",
    "UserRole",
    "UserSession",
    "UserStatus",
    "AuthProvider",
    "OAuthManager",
    "OAuthError",
    "MFAManager",
    "MFAError",
    "RBACManager",
    "RBACError",
    # New 4-Role Hierarchical System
    "ApplicationRole",
    "AdministrativeRole",
    "Permission",
    "PermissionChecker",
    "RoleHierarchyService",
    "UserRoleInfo",
    "role_hierarchy_service",
    "get_permissions_for_role",
    # Permission decorators
    "require_permission",
    "require_role", 
    "require_admin",
    "require_analytics_access",
    "require_user_management",
    "require_system_config",
    "permission_check",
    # Legacy roles (deprecated)
    "LegacyUserRole",
    "LegacyAdminRole",
]

__version__ = "3.5.0"
__author__ = "AnalyticBot Security Team"
