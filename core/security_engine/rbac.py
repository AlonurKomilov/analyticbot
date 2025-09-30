"""
🔒 Role-Based Access Control (RBAC) System

Enterprise-grade RBAC implementation with hierarchical roles,
granular permissions, and resource-level access control.
"""

import json
import logging
from dataclasses import dataclass
from datetime import timedelta
from enum import Enum

from core.ports.security_ports import CachePort, SecurityEventsPort
from .models import PermissionMatrix, User
# Import new role system with backwards compatibility  
from .roles import ApplicationRole, AdministrativeRole, UserRole as LegacyUserRole

logger = logging.getLogger(__name__)


class RBACError(Exception):
    """Custom exception for RBAC-related errors"""
    
    def __init__(self, message: str, error_code: str | None = None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)


@dataclass
class RBACConfig:
    """RBAC configuration settings"""

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None


class Permission(str, Enum):
    """System permissions enumeration"""

    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_LIST = "user:list"
    ANALYTICS_READ = "analytics:read"
    ANALYTICS_CREATE = "analytics:create"
    ANALYTICS_UPDATE = "analytics:update"
    ANALYTICS_DELETE = "analytics:delete"
    ANALYTICS_EXPORT = "analytics:export"
    REPORT_READ = "report:read"
    REPORT_CREATE = "report:create"
    REPORT_UPDATE = "report:update"
    REPORT_DELETE = "report:delete"
    REPORT_SHARE = "report:share"
    SETTINGS_READ = "settings:read"
    SETTINGS_UPDATE = "settings:update"
    SETTINGS_SYSTEM = "settings:system"
    API_READ = "api:read"
    API_WRITE = "api:write"
    API_ADMIN = "api:admin"
    BOT_MANAGE = "bot:manage"
    BOT_CONFIG = "bot:config"
    BOT_LOGS = "bot:logs"
    SYSTEM_ADMIN = "system:admin"
    SYSTEM_MONITOR = "system:monitor"
    SYSTEM_BACKUP = "system:backup"


class Resource(str, Enum):
    """System resources"""

    USER = "user"
    ANALYTICS = "analytics"
    REPORT = "report"
    SETTINGS = "settings"
    API = "api"
    BOT = "bot"
    SYSTEM = "system"


class RBACManager:
    """
    🛡️ Role-Based Access Control Manager

    Provides comprehensive RBAC functionality:
    - Hierarchical role management
    - Granular permission control
    - Resource-level access control
    - Permission caching for performance
    - Audit logging for access control
    """

    def __init__(
        self, 
        cache: CachePort | None = None, 
        security_events: SecurityEventsPort | None = None, 
        config: RBACConfig | None = None
    ):
        """
        Initialize RBAC Manager with dependency injection support
        
        Args:
            cache: Cache port for permission caching (optional, falls back to Redis/memory)
            security_events: Security events port for audit logging (optional)
            config: RBAC configuration (optional)
        """
        self.cache = cache
        self.security_events = security_events
        self.config = config or RBACConfig()
        
        # Legacy Redis fallback if no cache port provided
        if not self.cache:
            self._setup_legacy_cache()
        
        self._setup_default_permissions()

    def _setup_legacy_cache(self) -> None:
        """Setup memory cache fallback when no cache port is provided"""
        logger.info("No cache port provided, using memory cache fallback")
        self._redis_available = False
        self.redis_client = None
        self._memory_cache = {}

    def _cache_get(self, key: str) -> str | None:
        """Get value from cache (abstracted)"""
        if self.cache:
            return self.cache.get(key)
        elif self._redis_available and self.redis_client:
            result = self.redis_client.get(key)
            return result if isinstance(result, str) else None
        else:
            return self._memory_cache.get(key)

    def _cache_set(self, key: str, value: str, expire: int | None = None) -> None:
        """Set value in cache (abstracted)"""
        if self.cache:
            self.cache.set(key, value, expire)
        elif self._redis_available and self.redis_client:
            if expire:
                self.redis_client.setex(key, expire, value)
            else:
                self.redis_client.set(key, value)
        else:
            self._memory_cache[key] = value

    def _cache_delete(self, key: str) -> None:
        """Delete value from cache (abstracted)"""
        if self.cache:
            self.cache.delete(key)
        elif self._redis_available and self.redis_client:
            self.redis_client.delete(key)
        else:
            self._memory_cache.pop(key, None)

    def _log_security_event(self, event: str, user_id: str | None = None, details: dict | None = None) -> None:
        """Log security event (abstracted)"""
        if self.security_events:
            self.security_events.log_security_event(user_id, event, details or {})
        else:
            logger.info(f"Security event: {event} - User: {user_id} - Details: {details}")

    def _setup_default_permissions(self) -> None:
        """Setup default role permissions"""
        # Legacy role hierarchy (DEPRECATED - use new role system instead)
        # self.role_hierarchy = {
        #     UserRole.GUEST: 0,
        #     UserRole.READONLY: 1,
        #     UserRole.USER: 2,
        #     UserRole.ANALYST: 3,
        #     UserRole.MODERATOR: 4,
        #     UserRole.ADMIN: 5,
        # }
        # Legacy default permissions (DEPRECATED - use new permission system instead)
        # Use role_hierarchy_service.get_permissions_for_role() instead
        self.default_permissions = {}
        self._cache_default_permissions()

    def _cache_default_permissions(self) -> None:
        """Cache default role permissions - Updated for new role system"""
        # New role system uses role_hierarchy_service for permission management
        # Legacy caching no longer needed
        logger.info("Role permissions now managed by role_hierarchy_service")

    def has_permission(
        self, user: User, permission: Permission, resource_id: str | None = None
    ) -> bool:
        """
        Check if user has specific permission

        Args:
            user: User object
            permission: Permission to check
            resource_id: Optional resource ID for resource-level permissions

        Returns:
            True if user has permission, False otherwise
        """
        user_permissions = self.get_user_permissions(user)
        if permission not in user_permissions:
            logger.debug(f"User {user.username} lacks permission {permission.value}")
            return False
        if resource_id:
            return self._check_resource_permission(user, permission, resource_id)
        logger.debug(f"Permission {permission.value} granted to user {user.username}")
        return True

    def has_role(self, user: User, required_role: str) -> bool:
        """
        Check if user has required role (or higher in hierarchy)

        Args:
            user: User object
            required_role: Required role (string value)
            
        Returns:
            True if user has required role or higher
        """
        # Use new role hierarchy system
        from .roles import has_role_or_higher
        return has_role_or_higher(user.role, required_role)
    
    def get_user_permissions(self, user: User) -> set[Permission]:
        """
        Get all effective permissions for user

        Args:
            user: User object

        Returns:
            Set of permissions
        """
        cache_key = f"user_permissions:{user.id}"
        cached_permissions = self._cache_get(cache_key)
        if cached_permissions:
            try:
                permission_list = json.loads(cached_permissions)
                return {Permission(perm) for perm in permission_list}
            except (json.JSONDecodeError, ValueError):
                pass
        role_permissions = set(self.default_permissions.get(user.role, []))
        custom_permissions = self._get_custom_user_permissions(user.id)
        role_permissions.update(custom_permissions)
        permission_list = [perm.value for perm in role_permissions]
        self._cache_set(
            cache_key, json.dumps(permission_list), int(timedelta(hours=1).total_seconds())
        )
        logger.debug(f"Retrieved {len(role_permissions)} permissions for user {user.username}")
        return role_permissions

    def grant_permission(self, user_id: str, permission: Permission) -> bool:
        """
        Grant specific permission to user

        Args:
            user_id: User ID
            permission: Permission to grant

        Returns:
            Success status
        """
        custom_permissions = self._get_custom_user_permissions(user_id)
        custom_permissions.add(permission)
        permission_list = [perm.value for perm in custom_permissions]
        self._cache_set(
            f"custom_permissions:{user_id}",
            json.dumps(permission_list),
            int(timedelta(days=30).total_seconds())
        )
        self._cache_delete(f"user_permissions:{user_id}")
        logger.info(f"Granted permission {permission.value} to user {user_id}")
        return True

    def revoke_permission(self, user_id: str, permission: Permission) -> bool:
        """
        Revoke specific permission from user

        Args:
            user_id: User ID
            permission: Permission to revoke

        Returns:
            Success status
        """
        custom_permissions = self._get_custom_user_permissions(user_id)
        custom_permissions.discard(permission)
        if custom_permissions:
            permission_list = [perm.value for perm in custom_permissions]
            self._cache_set(
                f"custom_permissions:{user_id}",
                json.dumps(permission_list),
                int(timedelta(days=30).total_seconds())
            )
        else:
            self._cache_delete(f"custom_permissions:{user_id}")
        self._cache_delete(f"user_permissions:{user_id}")
        logger.info(f"Revoked permission {permission.value} from user {user_id}")
        return True

    def get_permission_matrix(self, user: User) -> PermissionMatrix:
        """
        Get permission matrix for user

        Args:
            user: User object

        Returns:
            PermissionMatrix object
        """
        user_permissions = self.get_user_permissions(user)
        matrix = {
            "analytics": [],
            "users": [],
            "settings": [],
            "reports": [],
            "api": [],
            "bot": [],
            "system": [],
        }
        for permission in user_permissions:
            perm_str = permission.value
            if perm_str.startswith("analytics:"):
                action = perm_str.split(":")[1]
                matrix["analytics"].append(action)
            elif perm_str.startswith("user:"):
                action = perm_str.split(":")[1]
                matrix["users"].append(action)
            elif perm_str.startswith("settings:"):
                action = perm_str.split(":")[1]
                matrix["settings"].append(action)
            elif perm_str.startswith("report:"):
                action = perm_str.split(":")[1]
                matrix["reports"].append(action)
            elif perm_str.startswith("api:"):
                action = perm_str.split(":")[1]
                matrix["api"].append(action)
            elif perm_str.startswith("bot:"):
                action = perm_str.split(":")[1]
                matrix["bot"].append(action)
            elif perm_str.startswith("system:"):
                action = perm_str.split(":")[1]
                matrix["system"].append(action)
        return PermissionMatrix(role=user.role, permissions=matrix)

    def _get_custom_user_permissions(self, user_id: str) -> set[Permission]:
        """Get custom permissions for user"""
        custom_permissions_str = self._cache_get(f"custom_permissions:{user_id}")
        if not custom_permissions_str:
            return set()
        try:
            permission_list = json.loads(custom_permissions_str)
            return {Permission(perm) for perm in permission_list}
        except (json.JSONDecodeError, ValueError):
            return set()

    def _check_resource_permission(
        self, user: User, permission: Permission, resource_id: str
    ) -> bool:
        """Check resource-level permission"""
        resource_type = permission.value.split(":")[0]
        owner_key = f"resource_owner:{resource_type}:{resource_id}"
        resource_owner = self._cache_get(owner_key)
        if not resource_owner:
            return True
        if resource_owner == user.id:
            return True
        if user.role in ["admin", "moderator", "super_admin"]:  # Use string values for new system
            return True
        logger.debug(
            f"Resource permission denied: User {user.username} not owner of {resource_type}:{resource_id}"
        )
        return False

    def set_resource_owner(self, resource_type: str, resource_id: str, owner_id: str) -> bool:
        """
        Set resource owner

        Args:
            resource_type: Type of resource (analytics, report, etc.)
            resource_id: Resource ID
            owner_id: Owner user ID

        Returns:
            Success status
        """
        owner_key = f"resource_owner:{resource_type}:{resource_id}"
        self._cache_set(owner_key, owner_id, int(timedelta(days=365).total_seconds()))
        logger.info(f"Set resource owner: {resource_type}:{resource_id} -> {owner_id}")
        return True

    def clear_user_permissions_cache(self, user_id: str) -> None:
        """Clear cached permissions for user"""
        self._cache_delete(f"user_permissions:{user_id}")
        logger.debug(f"Cleared permission cache for user {user_id}")


# RBAC manager should be initialized with proper config in application layer
# rbac_manager = RBACManager()  # Removed - use DI instead
