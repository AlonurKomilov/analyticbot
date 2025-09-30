"""
Permission-based Authentication Decorators

Provides decorators for role and permission-based access control
using the new 4-role hierarchical system. Framework-agnostic core with
FastAPI integration through exceptions.
"""

from functools import wraps
from typing import List, Optional, Union, Callable, Any
import logging

# Framework-agnostic exceptions - can be adapted to any framework
class AuthenticationError(Exception):
    """Authentication required error"""
    def __init__(self, message: str = "Authentication required", status_code: int = 401):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class PermissionError(Exception):
    """Permission denied error"""
    def __init__(self, message: str = "Permission denied", status_code: int = 403):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

from .permissions import Permission
from .roles import ApplicationRole, AdministrativeRole, has_role_or_higher
from .role_hierarchy import role_hierarchy_service, check_user_access

logger = logging.getLogger(__name__)


def require_permission(
    permission: Union[Permission, str, List[Union[Permission, str]]],
    allow_admin_override: bool = True
):
    """
    Decorator to require specific permission(s) for endpoint access.
    
    Args:
        permission: Single permission or list of permissions required
        allow_admin_override: Whether SUPER_ADMIN can bypass permission checks
        
    Usage:
        @require_permission(Permission.VIEW_ANALYTICS)
        @require_permission([Permission.VIEW_ANALYTICS, Permission.EXPORT_ANALYTICS])
        @require_permission("view_analytics")
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from dependency injection
            current_user = None
            for key, value in kwargs.items():
                if hasattr(value, 'get') and 'id' in str(value):
                    current_user = value
                    break
            
            if not current_user:
                raise AuthenticationError("Authentication required")
            
            # Get user role info
            user_info = role_hierarchy_service.get_user_role_info(
                role=current_user.get('role', 'user'),
                additional_permissions=current_user.get('additional_permissions', []),
                migration_profile=current_user.get('migration_profile')
            )
            
            # Admin override check
            if allow_admin_override and user_info.role == AdministrativeRole.SUPER_ADMIN.value:
                logger.debug(f"Admin override: {current_user.get('username')} accessing {func.__name__}")
                return await func(*args, **kwargs)
            
            # Permission checking
            permissions_to_check = permission if isinstance(permission, list) else [permission]
            
            for perm in permissions_to_check:
                if isinstance(perm, str):
                    try:
                        perm = Permission(perm)
                    except ValueError:
                        logger.warning(f"Unknown permission: {perm}")
                        raise PermissionError(f"Unknown permission: {perm}")
                
                if perm not in user_info.permissions:
                    logger.warning(
                        f"Permission denied: {current_user.get('username')} lacks {perm.value}"
                    )
                    raise PermissionError(f"Insufficient permissions. Required: {perm.value}")
            
            logger.debug(f"Permission granted: {current_user.get('username')} accessing {func.__name__}")
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_role(
    min_role: Union[str, ApplicationRole, AdministrativeRole],
    allow_equal: bool = True
):
    """
    Decorator to require minimum role level for endpoint access.
    
    Args:
        min_role: Minimum required role
        allow_equal: Whether equal role level is sufficient
        
    Usage:
        @require_role(AdministrativeRole.MODERATOR)
        @require_role("moderator")
        @require_role(ApplicationRole.USER)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from dependency injection
            current_user = None
            for key, value in kwargs.items():
                if hasattr(value, 'get') and 'id' in str(value):
                    current_user = value
                    break
            
            if not current_user:
                raise AuthenticationError("Authentication required")
            
            user_role = current_user.get('role', 'guest')
            required_role = str(min_role)  # Convert to string directly
            
            # Check role hierarchy
            if not has_role_or_higher(user_role, required_role):
                logger.warning(
                    f"Role access denied: {current_user.get('username')} "
                    f"has {user_role}, requires {required_role}"
                )
                raise PermissionError(f"Insufficient role. Required: {required_role}, Current: {user_role}")
            
            logger.debug(f"Role access granted: {current_user.get('username')} accessing {func.__name__}")
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_admin(allow_moderator: bool = True):
    """
    Decorator to require administrative access.
    
    Args:
        allow_moderator: Whether MODERATOR role is sufficient
        
    Usage:
        @require_admin()  # Allows MODERATOR and SUPER_ADMIN
        @require_admin(allow_moderator=False)  # Only SUPER_ADMIN
    """
    min_role = AdministrativeRole.MODERATOR if allow_moderator else AdministrativeRole.SUPER_ADMIN
    return require_role(min_role)


def permission_check(
    user_dict: dict,
    required_permission: Union[Permission, str],
    raise_on_fail: bool = True
) -> bool:
    """
    Utility function for manual permission checking.
    
    Args:
        user_dict: User dictionary with role and permissions
        required_permission: Permission to check
        raise_on_fail: Whether to raise exception on failure
        
    Returns:
        True if user has permission, False otherwise
    """
    try:
        user_info = role_hierarchy_service.get_user_role_info(
            role=user_dict.get('role', 'user'),
            additional_permissions=user_dict.get('additional_permissions', []),
            migration_profile=user_dict.get('migration_profile')
        )
        
        if isinstance(required_permission, str):
            required_permission = Permission(required_permission)
        
        has_permission = required_permission in user_info.permissions
        
        if not has_permission and raise_on_fail:
            raise PermissionError(f"Permission required: {required_permission.value}")
        
        return has_permission
        
    except ValueError as e:
        if raise_on_fail:
            raise PermissionError(f"Invalid permission: {required_permission}")
        return False


# Convenience decorators for common permissions
def require_analytics_access():
    """Require analytics viewing permission."""
    return require_permission(Permission.VIEW_ANALYTICS)


def require_user_management():
    """Require user management permission."""
    return require_permission(Permission.MANAGE_USERS)


def require_system_config():
    """Require system configuration permission."""
    return require_permission(Permission.SYSTEM_CONFIG)


def require_api_write():
    """Require API write permission."""
    return require_permission(Permission.API_WRITE)


# Framework-agnostic permission checking functions
def check_user_permission(user_dict: dict, permission: Permission) -> bool:
    """
    Check if user has required permission - framework agnostic.
    
    Args:
        user_dict: User dictionary with role and permissions
        permission: Required permission
        
    Returns:
        True if user has permission, False otherwise
    """
    return permission_check(user_dict, permission, raise_on_fail=False)


def check_user_role(user_dict: dict, min_role: Union[str, ApplicationRole, AdministrativeRole]) -> bool:
    """
    Check if user has required role level - framework agnostic.
    
    Args:
        user_dict: User dictionary with role
        min_role: Minimum required role
        
    Returns:
        True if user has sufficient role, False otherwise
    """
    user_role = user_dict.get('role', 'guest')
    required_role = str(min_role)  # Convert to string directly
    return has_role_or_higher(user_role, required_role)


def check_admin_access(user_dict: dict) -> bool:
    """
    Check if user has admin access - framework agnostic.
    
    Args:
        user_dict: User dictionary with role
        
    Returns:
        True if user has admin access, False otherwise
    """
    return check_user_role(user_dict, AdministrativeRole.MODERATOR)


# Export the permission decorators and utility functions
__all__ = [
    "require_permission",
    "require_role", 
    "require_admin",
    "permission_check",
    "check_user_permission",
    "check_user_role", 
    "check_admin_access",
    "require_analytics_access",
    "require_user_management",
    "require_system_config",
    "require_api_write",
    "AuthenticationError",
    "PermissionError",
]