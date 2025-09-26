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
    SecurityManager,
    create_access_token,
    verify_token,
)
from .auth_utils import AuthError, AuthUtils, auth_utils
from .container import get_rbac_manager, get_security_container, get_security_manager
from .mfa import MFAManager
from .models import AuthProvider, User, UserRole, UserSession, UserStatus
from .oauth import OAuthManager
from .rbac import RBACManager

__all__ = [
    "SecurityManager",
    "get_security_manager",
    "get_rbac_manager",
    "get_security_container",
    "AuthUtils",
    "auth_utils",
    "AuthError",
    "create_access_token",  # Deprecated
    "verify_token",  # Deprecated
    "User",
    "UserRole",
    "UserSession",
    "UserStatus",
    "AuthProvider",
    "OAuthManager",
    "MFAManager",
    "RBACManager",
]

__version__ = "3.5.0"
__author__ = "AnalyticBot Security Team"
