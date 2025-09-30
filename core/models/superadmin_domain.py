"""
🔧 Core Admin Domain Models - Pure Dataclasses

Framework-independent domain entities for admin management.
No ORM dependencies - pure Python dataclasses for clean domain logic.

Updated for 4-Role Hierarchical System with backwards compatibility.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
import warnings


class AdminRole(str, Enum):
    """
    DEPRECATED: Legacy admin role hierarchy - use AdministrativeRole instead.
    
    Migration mapping:
    - SUPPORT → AdministrativeRole.MODERATOR + customer_support permission
    - MODERATOR → AdministrativeRole.MODERATOR
    - ADMIN → AdministrativeRole.SUPER_ADMIN
    - SUPER_ADMIN → AdministrativeRole.SUPER_ADMIN
    """
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"
    SUPPORT = "support"


class UserStatus(str, Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
    DELETED = "deleted"


class SystemStatus(str, Enum):
    """System component status"""
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"


class AuditAction(str, Enum):
    """Audit trail action types"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    PERMISSION_CHANGE = "permission_change"
    SYSTEM_CONFIG = "system_config"


@dataclass
class AdminUser:
    """Admin user domain entity - Updated for 4-Role System"""
    id: UUID = field(default_factory=uuid4)
    username: str = ""
    email: str = ""
    password_hash: str = ""
    
    # Role System - New hierarchical approach
    role: str = "moderator"  # Default to AdministrativeRole.MODERATOR.value
    legacy_role: AdminRole | None = None  # For backwards compatibility
    additional_permissions: List[str] = field(default_factory=list)  # Extra permissions
    migration_profile: str | None = None  # Migration profile for special cases
    
    status: UserStatus = UserStatus.ACTIVE
    first_name: str = ""
    last_name: str = ""
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    timezone: str = "UTC"
    language: str = "en"
    last_login: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[UUID] = None
    
    # Security settings
    is_mfa_enabled: bool = False
    failed_login_attempts: int = 0
    account_locked_until: Optional[datetime] = None
    password_changed_at: Optional[datetime] = None
    
    # Preferences
    preferences: Dict[str, Any] = field(default_factory=dict)
    permissions: List[str] = field(default_factory=list)  # Legacy permissions field
    
    def __post_init__(self):
        """Post-initialization validation and migration"""
        if not self.email:
            raise ValueError("Email is required")
        if not self.username:
            raise ValueError("Username is required")
        self._migrate_legacy_role()
    
    def _migrate_legacy_role(self) -> None:
        """Migrate legacy AdminRole to new system if needed"""
        if self.legacy_role and not self._is_new_role_system():
            # Import here to avoid circular imports
            from core.security_engine.roles import migrate_admin_role
            
            new_role, additional_perms = migrate_admin_role(self.legacy_role.value)
            self.role = new_role
            self.additional_permissions.extend(additional_perms)
            
            # Set migration profile for special cases
            if self.legacy_role == AdminRole.SUPPORT:
                self.migration_profile = "support_moderator"

    def _is_new_role_system(self) -> bool:
        """Check if using new role system values"""
        # Import here to avoid circular imports
        try:
            from core.security_engine.roles import AdministrativeRole
            new_role_values = [
                AdministrativeRole.MODERATOR.value,
                AdministrativeRole.SUPER_ADMIN.value,
            ]
            return self.role in new_role_values
        except ImportError:
            return False

    def get_permissions(self):
        """Get all permissions for this admin user"""
        try:
            from core.security_engine.role_hierarchy import role_hierarchy_service
            
            user_info = role_hierarchy_service.get_user_role_info(
                role=self.role,
                additional_permissions=self.additional_permissions,
                migration_profile=self.migration_profile
            )
            return user_info.permissions
        except ImportError:
            # Fallback to legacy permissions if new system not available
            return set(self.permissions)

    def has_permission(self, permission: str) -> bool:
        """Check if admin user has specific permission"""
        try:
            from core.security_engine.permissions import Permission
            
            # Check new permission system
            user_permissions = self.get_permissions()
            if isinstance(permission, str):
                try:
                    permission_enum = Permission(permission)
                    return permission_enum in user_permissions
                except ValueError:
                    pass
            
            # Fallback to legacy permission check
            return permission in self.permissions
        except ImportError:
            # Legacy permission check only
            return permission in self.permissions
    
    @property
    def full_name(self) -> str:
        """Get full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    @property
    def is_active(self) -> bool:
        """Check if user is active"""
        return self.status == UserStatus.ACTIVE
    
    @property
    def is_locked(self) -> bool:
        """Check if account is locked"""
        if self.account_locked_until:
            return datetime.utcnow() < self.account_locked_until
        return False
    
    def has_role(self, required_role) -> bool:
        """Check if user has required role or higher"""
        try:
            from core.security_engine.roles import has_role_or_higher
            # Use new role hierarchy system
            if isinstance(required_role, str):
                return has_role_or_higher(self.role, required_role)
            elif hasattr(required_role, 'value'):
                return has_role_or_higher(self.role, required_role.value)
        except ImportError:
            pass
        
        # Fallback to legacy role hierarchy
        legacy_role_hierarchy = {
            "support": 1,
            "moderator": 2, 
            "admin": 3,
            "super_admin": 4,
        }
        
        current_role_str = self.role if isinstance(self.role, str) else self.role.value
        required_role_str = required_role if isinstance(required_role, str) else required_role.value
        
        current_level = legacy_role_hierarchy.get(current_role_str, 0)
        required_level = legacy_role_hierarchy.get(required_role_str, 0)
        
        return current_level >= required_level


@dataclass
class AdminSession:
    """Admin user session domain entity"""
    id: UUID = field(default_factory=uuid4)
    user_id: UUID = field(default_factory=uuid4)
    token: str = ""
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_info: Dict[str, Any] = field(default_factory=dict)
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow())
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    
    @property
    def is_expired(self) -> bool:
        """Check if session is expired"""
        return datetime.utcnow() > self.expires_at
    
    def extend_session(self, hours: int = 24) -> None:
        """Extend session expiration"""
        from datetime import timedelta
        self.expires_at = datetime.utcnow() + timedelta(hours=hours)
        self.last_activity = datetime.utcnow()


@dataclass
class SystemComponent:
    """System component domain entity"""
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    status: SystemStatus = SystemStatus.OFFLINE
    version: str = "1.0.0"
    health_check_url: Optional[str] = None
    last_health_check: Optional[datetime] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def is_healthy(self) -> bool:
        """Check if component is healthy"""
        return self.status == SystemStatus.ONLINE


@dataclass
class AuditEntry:
    """Audit trail domain entity"""
    id: UUID = field(default_factory=uuid4)
    user_id: Optional[UUID] = None
    action: AuditAction = AuditAction.READ
    resource_type: str = ""
    resource_id: Optional[str] = None
    description: str = ""
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Change tracking
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None


@dataclass
class SystemConfig:
    """System configuration domain entity"""
    id: UUID = field(default_factory=uuid4)
    key: str = ""
    value: Any = None
    category: str = "general"
    description: str = ""
    is_sensitive: bool = False
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    updated_by: Optional[UUID] = None
    
    def __post_init__(self):
        """Post-initialization validation"""
        if not self.key:
            raise ValueError("Configuration key is required")


@dataclass
class AdminNotification:
    """Admin notification domain entity"""
    id: UUID = field(default_factory=uuid4)
    user_id: Optional[UUID] = None  # None for system-wide notifications
    title: str = ""
    message: str = ""
    type: str = "info"  # info, warning, error, success
    priority: str = "normal"  # low, normal, high, urgent
    is_read: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    expires_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = None
    
    @property
    def is_expired(self) -> bool:
        """Check if notification is expired"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False


@dataclass
class Permission:
    """Permission domain entity"""
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    code: str = ""
    description: str = ""
    category: str = "general"
    is_system: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Post-initialization validation"""
        if not self.name or not self.code:
            raise ValueError("Permission name and code are required")


@dataclass
class RolePermission:
    """Role-Permission mapping domain entity"""
    role: AdminRole
    permission_code: str
    granted_by: Optional[UUID] = None
    granted_at: datetime = field(default_factory=datetime.utcnow)


# Domain value objects
@dataclass(frozen=True)
class UserPreferences:
    """User preferences value object"""
    theme: str = "light"
    notifications_enabled: bool = True
    email_notifications: bool = True
    timezone: str = "UTC"
    language: str = "en"
    dashboard_layout: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "theme": self.theme,
            "notifications_enabled": self.notifications_enabled,
            "email_notifications": self.email_notifications,
            "timezone": self.timezone,
            "language": self.language,
            "dashboard_layout": self.dashboard_layout,
        }


@dataclass(frozen=True)
class SecuritySettings:
    """Security settings value object"""
    password_min_length: int = 12
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numbers: bool = True
    password_require_special: bool = True
    password_history_count: int = 5
    session_timeout_hours: int = 24
    max_failed_login_attempts: int = 5
    account_lockout_duration_minutes: int = 30
    mfa_required_for_admin: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "password_min_length": self.password_min_length,
            "password_require_uppercase": self.password_require_uppercase,
            "password_require_lowercase": self.password_require_lowercase,
            "password_require_numbers": self.password_require_numbers,
            "password_require_special": self.password_require_special,
            "password_history_count": self.password_history_count,
            "session_timeout_hours": self.session_timeout_hours,
            "max_failed_login_attempts": self.max_failed_login_attempts,
            "account_lockout_duration_minutes": self.account_lockout_duration_minutes,
            "mfa_required_for_admin": self.mfa_required_for_admin,
        }