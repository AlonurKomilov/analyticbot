"""
🔒 Role-Based Access Control (RBAC) System

Enterprise-grade RBAC implementation with hierarchical roles,
granular permissions, and resource-level access control.
"""

from typing import Dict, List, Set, Optional, Any
from enum import Enum
import json
import redis
from datetime import timedelta
import logging

from .config import SecurityConfig
from .models import UserRole, User, PermissionMatrix

logger = logging.getLogger(__name__)

class Permission(str, Enum):
    """System permissions enumeration"""
    # User management
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_LIST = "user:list"
    
    # Analytics permissions
    ANALYTICS_READ = "analytics:read"
    ANALYTICS_CREATE = "analytics:create"
    ANALYTICS_UPDATE = "analytics:update"
    ANALYTICS_DELETE = "analytics:delete"
    ANALYTICS_EXPORT = "analytics:export"
    
    # Reports permissions
    REPORT_READ = "report:read"
    REPORT_CREATE = "report:create"
    REPORT_UPDATE = "report:update"
    REPORT_DELETE = "report:delete"
    REPORT_SHARE = "report:share"
    
    # Settings permissions
    SETTINGS_READ = "settings:read"
    SETTINGS_UPDATE = "settings:update"
    SETTINGS_SYSTEM = "settings:system"
    
    # API permissions
    API_READ = "api:read"
    API_WRITE = "api:write"
    API_ADMIN = "api:admin"
    
    # Bot permissions
    BOT_MANAGE = "bot:manage"
    BOT_CONFIG = "bot:config"
    BOT_LOGS = "bot:logs"
    
    # System permissions
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
    
    def __init__(self):
        self.config = SecurityConfig()
        self.redis_client = redis.Redis(
            host=self.config.REDIS_HOST,
            port=self.config.REDIS_PORT,
            db=self.config.REDIS_DB,
            decode_responses=True
        )
        
        # Initialize role hierarchy and permissions
        self._setup_default_permissions()
    
    def _setup_default_permissions(self) -> None:
        """Setup default role permissions"""
        self.role_hierarchy = {
            UserRole.GUEST: 0,
            UserRole.READONLY: 1,
            UserRole.USER: 2,
            UserRole.ANALYST: 3,
            UserRole.MODERATOR: 4,
            UserRole.ADMIN: 5
        }
        
        # Define default permissions for each role
        self.default_permissions = {
            UserRole.GUEST: [
                Permission.ANALYTICS_READ,
                Permission.REPORT_READ
            ],
            
            UserRole.READONLY: [
                Permission.ANALYTICS_READ,
                Permission.REPORT_READ,
                Permission.USER_READ,
                Permission.SETTINGS_READ,
                Permission.API_READ
            ],
            
            UserRole.USER: [
                Permission.ANALYTICS_READ,
                Permission.ANALYTICS_CREATE,
                Permission.REPORT_READ,
                Permission.REPORT_CREATE,
                Permission.USER_READ,
                Permission.SETTINGS_READ,
                Permission.API_READ
            ],
            
            UserRole.ANALYST: [
                Permission.ANALYTICS_READ,
                Permission.ANALYTICS_CREATE,
                Permission.ANALYTICS_UPDATE,
                Permission.ANALYTICS_EXPORT,
                Permission.REPORT_READ,
                Permission.REPORT_CREATE,
                Permission.REPORT_UPDATE,
                Permission.REPORT_SHARE,
                Permission.USER_READ,
                Permission.SETTINGS_READ,
                Permission.API_READ,
                Permission.API_WRITE
            ],
            
            UserRole.MODERATOR: [
                Permission.ANALYTICS_READ,
                Permission.ANALYTICS_CREATE,
                Permission.ANALYTICS_UPDATE,
                Permission.ANALYTICS_DELETE,
                Permission.ANALYTICS_EXPORT,
                Permission.REPORT_READ,
                Permission.REPORT_CREATE,
                Permission.REPORT_UPDATE,
                Permission.REPORT_DELETE,
                Permission.REPORT_SHARE,
                Permission.USER_READ,
                Permission.USER_UPDATE,
                Permission.SETTINGS_READ,
                Permission.API_READ,
                Permission.API_WRITE,
                Permission.BOT_MANAGE,
                Permission.BOT_LOGS
            ],
            
            UserRole.ADMIN: [
                # Admins get all permissions
                *list(Permission)
            ]
        }
        
        # Cache default permissions in Redis
        self._cache_default_permissions()
    
    def _cache_default_permissions(self) -> None:
        """Cache default role permissions in Redis"""
        for role, permissions in self.default_permissions.items():
            permission_list = [perm.value for perm in permissions]
            self.redis_client.setex(
                f"role_permissions:{role.value}",
                int(timedelta(hours=24).total_seconds()),
                json.dumps(permission_list)
            )
    
    def has_permission(self, user: User, permission: Permission, resource_id: Optional[str] = None) -> bool:
        """
        Check if user has specific permission
        
        Args:
            user: User object
            permission: Permission to check
            resource_id: Optional resource ID for resource-level permissions
            
        Returns:
            True if user has permission, False otherwise
        """
        # Get user's effective permissions
        user_permissions = self.get_user_permissions(user)
        
        # Check basic permission
        if permission not in user_permissions:
            logger.debug(f"User {user.username} lacks permission {permission.value}")
            return False
        
        # Check resource-level permissions if specified
        if resource_id:
            return self._check_resource_permission(user, permission, resource_id)
        
        # Log successful permission check
        logger.debug(f"Permission {permission.value} granted to user {user.username}")
        return True
    
    def has_role(self, user: User, required_role: UserRole) -> bool:
        """
        Check if user has required role (or higher in hierarchy)
        
        Args:
            user: User object
            required_role: Required role
            
        Returns:
            True if user has required role or higher
        """
        user_role_level = self.role_hierarchy.get(user.role, 0)
        required_role_level = self.role_hierarchy.get(required_role, 0)
        
        has_role = user_role_level >= required_role_level
        
        if has_role:
            logger.debug(f"Role check passed: {user.username} has {user.role.value} (>= {required_role.value})")
        else:
            logger.debug(f"Role check failed: {user.username} has {user.role.value} (< {required_role.value})")
        
        return has_role
    
    def get_user_permissions(self, user: User) -> Set[Permission]:
        """
        Get all effective permissions for user
        
        Args:
            user: User object
            
        Returns:
            Set of permissions
        """
        # Check cache first
        cache_key = f"user_permissions:{user.id}"
        cached_permissions = self.redis_client.get(cache_key)
        
        if cached_permissions:
            try:
                permission_list = json.loads(cached_permissions)
                return {Permission(perm) for perm in permission_list}
            except (json.JSONDecodeError, ValueError):
                pass
        
        # Get role-based permissions
        role_permissions = set(self.default_permissions.get(user.role, []))
        
        # Get custom user permissions (if any)
        custom_permissions = self._get_custom_user_permissions(user.id)
        role_permissions.update(custom_permissions)
        
        # Cache permissions for performance
        permission_list = [perm.value for perm in role_permissions]
        self.redis_client.setex(
            cache_key,
            int(timedelta(hours=1).total_seconds()),
            json.dumps(permission_list)
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
        # Get current custom permissions
        custom_permissions = self._get_custom_user_permissions(user_id)
        custom_permissions.add(permission)
        
        # Store updated permissions
        permission_list = [perm.value for perm in custom_permissions]
        self.redis_client.setex(
            f"custom_permissions:{user_id}",
            int(timedelta(days=30).total_seconds()),
            json.dumps(permission_list)
        )
        
        # Clear user permission cache
        self.redis_client.delete(f"user_permissions:{user_id}")
        
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
        # Get current custom permissions
        custom_permissions = self._get_custom_user_permissions(user_id)
        custom_permissions.discard(permission)
        
        # Store updated permissions
        if custom_permissions:
            permission_list = [perm.value for perm in custom_permissions]
            self.redis_client.setex(
                f"custom_permissions:{user_id}",
                int(timedelta(days=30).total_seconds()),
                json.dumps(permission_list)
            )
        else:
            # Remove custom permissions if empty
            self.redis_client.delete(f"custom_permissions:{user_id}")
        
        # Clear user permission cache
        self.redis_client.delete(f"user_permissions:{user_id}")
        
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
        
        # Group permissions by resource
        matrix = {
            "analytics": [],
            "users": [],
            "settings": [],
            "reports": [],
            "api": [],
            "bot": [],
            "system": []
        }
        
        for permission in user_permissions:
            perm_str = permission.value
            
            # Categorize permissions
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
        
        return PermissionMatrix(
            role=user.role,
            permissions=matrix
        )
    
    def _get_custom_user_permissions(self, user_id: str) -> Set[Permission]:
        """Get custom permissions for user"""
        custom_permissions_str = self.redis_client.get(f"custom_permissions:{user_id}")
        if not custom_permissions_str:
            return set()
        
        try:
            permission_list = json.loads(custom_permissions_str)
            return {Permission(perm) for perm in permission_list}
        except (json.JSONDecodeError, ValueError):
            return set()
    
    def _check_resource_permission(self, user: User, permission: Permission, resource_id: str) -> bool:
        """Check resource-level permission"""
        # For now, implement basic resource ownership check
        # This can be extended for more complex resource-level permissions
        
        # Resource ownership key format: "resource_owner:{resource_type}:{resource_id}"
        resource_type = permission.value.split(":")[0]
        owner_key = f"resource_owner:{resource_type}:{resource_id}"
        
        resource_owner = self.redis_client.get(owner_key)
        
        # If no owner is set, allow based on role permissions
        if not resource_owner:
            return True
        
        # If user is the owner, allow
        if resource_owner == user.id:
            return True
        
        # If user is admin or moderator, allow
        if user.role in [UserRole.ADMIN, UserRole.MODERATOR]:
            return True
        
        logger.debug(f"Resource permission denied: User {user.username} not owner of {resource_type}:{resource_id}")
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
        self.redis_client.setex(
            owner_key,
            int(timedelta(days=365).total_seconds()),  # 1 year expiration
            owner_id
        )
        
        logger.info(f"Set resource owner: {resource_type}:{resource_id} -> {owner_id}")
        return True
    
    def clear_user_permissions_cache(self, user_id: str) -> None:
        """Clear cached permissions for user"""
        self.redis_client.delete(f"user_permissions:{user_id}")
        logger.debug(f"Cleared permission cache for user {user_id}")

# Global RBAC manager instance
rbac_manager = RBACManager()
