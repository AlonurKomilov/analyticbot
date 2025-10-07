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

from .auth import (  # Deprecated wrappers
    AuthenticationError,
    SecurityManager,
    create_access_token,
    verify_token,
)
from .container import get_rbac_manager, get_security_container, get_security_manager
from .decorators import (
    permission_check,
    require_admin,
    require_analytics_access,
    require_permission,
    require_role,
    require_system_config,
    require_user_management,
)
from .mfa import MFAError, MFAManager
from .models import AuthProvider, User, UserRole, UserSession, UserStatus
from .oauth import OAuthError, OAuthManager
from .permissions import Permission, PermissionChecker, get_permissions_for_role
from .rbac import RBACError, RBACManager
from .role_hierarchy import RoleHierarchyService, UserRoleInfo, role_hierarchy_service

# New 4-Role Hierarchical System
from .roles import AdministrativeRole, ApplicationRole
from .roles import AdminRole as LegacyAdminRole
from .roles import UserRole as LegacyUserRole

__all__ = [
    "SecurityManager",
    "AuthenticationError",
    "get_security_manager",
    "get_rbac_manager",
    "get_security_container",
    "create_access_token",  # Deprecated
    "verify_token",  # Deprecated
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
