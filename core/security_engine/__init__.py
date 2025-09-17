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

from .auth import SecurityManager, get_security_manager, create_access_token, verify_token
from .mfa import MFAManager
from .models import User, UserRole, UserSession, UserStatus, AuthProvider
from .oauth import OAuthManager
from .rbac import RBACManager

__all__ = [
    "SecurityManager", 
    "get_security_manager",
    "create_access_token",
    "verify_token",
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
