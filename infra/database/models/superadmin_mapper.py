"""
🗄️ Admin Domain-ORM Mapping

Converts between pure domain entities and SQLAlchemy ORM models.
Keeps domain models clean while enabling database persistence.
"""

from core.models.superadmin_domain import (
    AdminNotification,
    AdminRole,
    AdminSession,
    AdminUser,
    AuditEntry,
    Permission,
    SystemComponent,
    SystemConfig,
    UserStatus,
)

# Import ORM models
from infra.database.models.superadmin_orm import AdminAuditLog as AuditEntryORM
from infra.database.models.superadmin_orm import AdminSession as AdminSessionORM
from infra.database.models.superadmin_orm import AdminUser as AdminUserORM
from infra.database.models.superadmin_orm import SystemConfiguration as SystemConfigORM
from infra.database.models.superadmin_orm import SystemMetrics as AdminNotificationORM
from infra.database.models.superadmin_orm import SystemUser as SystemComponentORM


# For Permission, we'll create a simple class until proper ORM is available
class PermissionORM:
    def __init__(
        self,
        name: str,
        description: str = "",
        resource: str = "",
        actions: list[str] = None,
    ):
        self.name = name
        self.description = description
        self.resource = resource
        self.actions = actions or []


from .superadmin_orm import (
    AdminSession,
    AdminUser,
)


class AdminDomainMapper:
    """Maps between domain entities and ORM models"""

    @staticmethod
    def admin_user_to_orm(domain: AdminUser) -> AdminUserORM:
        """Convert domain AdminUser to ORM model"""
        return AdminUserORM(
            id=domain.id,
            username=domain.username,
            email=domain.email,
            password_hash=domain.password_hash,
            role=domain.role.value,
            status=domain.status.value,
            first_name=domain.first_name,
            last_name=domain.last_name,
            phone=domain.phone,
            avatar_url=domain.avatar_url,
            timezone=domain.timezone,
            language=domain.language,
            last_login=domain.last_login,
            last_activity=domain.last_activity,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
            created_by=domain.created_by,
            is_mfa_enabled=domain.is_mfa_enabled,
            failed_login_attempts=domain.failed_login_attempts,
            account_locked_until=domain.account_locked_until,
            password_changed_at=domain.password_changed_at,
            preferences=domain.preferences,
            permissions=domain.permissions,
        )

    @staticmethod
    def orm_to_admin_user(orm: AdminUserORM) -> AdminUser:
        """Convert ORM model to domain AdminUser"""
        return AdminUser(
            id=orm.id,
            username=orm.username,
            email=orm.email,
            password_hash=orm.password_hash,
            role=AdminRole(orm.role),
            status=UserStatus(orm.status),
            first_name=orm.first_name,
            last_name=orm.last_name,
            phone=orm.phone,
            avatar_url=orm.avatar_url,
            timezone=orm.timezone,
            language=orm.language,
            last_login=orm.last_login,
            last_activity=orm.last_activity,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            created_by=orm.created_by,
            is_mfa_enabled=orm.is_mfa_enabled,
            failed_login_attempts=orm.failed_login_attempts,
            account_locked_until=orm.account_locked_until,
            password_changed_at=orm.password_changed_at,
            preferences=orm.preferences or {},
            permissions=orm.permissions or [],
        )

    @staticmethod
    def admin_session_to_orm(domain: AdminSession) -> AdminSessionORM:
        """Convert domain AdminSession to ORM model"""
        return AdminSessionORM(
            id=domain.id,
            user_id=domain.user_id,
            token=domain.token,
            ip_address=domain.ip_address,
            user_agent=domain.user_agent,
            device_info=domain.device_info,
            expires_at=domain.expires_at,
            created_at=domain.created_at,
            last_activity=domain.last_activity,
            is_active=domain.is_active,
        )

    @staticmethod
    def orm_to_admin_session(orm: AdminSessionORM) -> AdminSession:
        """Convert ORM model to domain AdminSession"""
        return AdminSession(
            id=orm.id,
            user_id=orm.user_id,
            token=orm.token,
            ip_address=orm.ip_address,
            user_agent=orm.user_agent,
            device_info=orm.device_info or {},
            expires_at=orm.expires_at,
            created_at=orm.created_at,
            last_activity=orm.last_activity,
            is_active=orm.is_active,
        )

    @staticmethod
    def system_component_to_orm(domain: SystemComponent) -> SystemComponentORM:
        """Convert domain SystemComponent to ORM model"""
        return SystemComponentORM(
            id=domain.id,
            name=domain.name,
            description=domain.description,
            status=domain.status.value,
            version=domain.version,
            health_check_url=domain.health_check_url,
            last_health_check=domain.last_health_check,
            metrics=domain.metrics,
            config=domain.config,
            dependencies=domain.dependencies,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
        )

    @staticmethod
    def orm_to_system_component(orm: SystemComponentORM) -> SystemComponent:
        """Convert ORM model to domain SystemComponent"""
        return SystemComponent(
            id=orm.id,
            name=orm.name,
            description=orm.description,
            status=SystemStatus(orm.status),
            version=orm.version,
            health_check_url=orm.health_check_url,
            last_health_check=orm.last_health_check,
            metrics=orm.metrics or {},
            config=orm.config or {},
            dependencies=orm.dependencies or [],
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    @staticmethod
    def audit_entry_to_orm(domain: AuditEntry) -> AuditEntryORM:
        """Convert domain AuditEntry to ORM model"""
        return AuditEntryORM(
            id=domain.id,
            user_id=domain.user_id,
            action=domain.action.value,
            resource_type=domain.resource_type,
            resource_id=domain.resource_id,
            description=domain.description,
            ip_address=domain.ip_address,
            user_agent=domain.user_agent,
            metadata=domain.metadata,
            timestamp=domain.timestamp,
            old_values=domain.old_values,
            new_values=domain.new_values,
        )

    @staticmethod
    def orm_to_audit_entry(orm: AuditEntryORM) -> AuditEntry:
        """Convert ORM model to domain AuditEntry"""
        return AuditEntry(
            id=orm.id,
            user_id=orm.user_id,
            action=AuditAction(orm.action),
            resource_type=orm.resource_type,
            resource_id=orm.resource_id,
            description=orm.description,
            ip_address=orm.ip_address,
            user_agent=orm.user_agent,
            metadata=orm.metadata or {},
            timestamp=orm.timestamp,
            old_values=orm.old_values,
            new_values=orm.new_values,
        )

    @staticmethod
    def system_config_to_orm(domain: SystemConfig) -> SystemConfigORM:
        """Convert domain SystemConfig to ORM model"""
        return SystemConfigORM(
            id=domain.id,
            key=domain.key,
            value=domain.value,
            category=domain.category,
            description=domain.description,
            is_sensitive=domain.is_sensitive,
            validation_rules=domain.validation_rules,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
            updated_by=domain.updated_by,
        )

    @staticmethod
    def orm_to_system_config(orm: SystemConfigORM) -> SystemConfig:
        """Convert ORM model to domain SystemConfig"""
        return SystemConfig(
            id=orm.id,
            key=orm.key,
            value=orm.value,
            category=orm.category,
            description=orm.description,
            is_sensitive=orm.is_sensitive,
            validation_rules=orm.validation_rules or {},
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            updated_by=orm.updated_by,
        )

    @staticmethod
    def admin_notification_to_orm(domain: AdminNotification) -> AdminNotificationORM:
        """Convert domain AdminNotification to ORM model"""
        return AdminNotificationORM(
            id=domain.id,
            user_id=domain.user_id,
            title=domain.title,
            message=domain.message,
            type=domain.type,
            priority=domain.priority,
            is_read=domain.is_read,
            metadata=domain.metadata,
            expires_at=domain.expires_at,
            created_at=domain.created_at,
            read_at=domain.read_at,
        )

    @staticmethod
    def orm_to_admin_notification(orm: AdminNotificationORM) -> AdminNotification:
        """Convert ORM model to domain AdminNotification"""
        return AdminNotification(
            id=orm.id,
            user_id=orm.user_id,
            title=orm.title,
            message=orm.message,
            type=orm.type,
            priority=orm.priority,
            is_read=orm.is_read,
            metadata=orm.metadata or {},
            expires_at=orm.expires_at,
            created_at=orm.created_at,
            read_at=orm.read_at,
        )

    @staticmethod
    def permission_to_orm(domain: Permission) -> PermissionORM:
        """Convert domain Permission to ORM model"""
        return PermissionORM(
            id=domain.id,
            name=domain.name,
            code=domain.code,
            description=domain.description,
            category=domain.category,
            is_system=domain.is_system,
            created_at=domain.created_at,
        )

    @staticmethod
    def orm_to_permission(orm: PermissionORM) -> Permission:
        """Convert ORM model to domain Permission"""
        return Permission(
            id=orm.id,
            name=orm.name,
            code=orm.code,
            description=orm.description,
            category=orm.category,
            is_system=orm.is_system,
            created_at=orm.created_at,
        )
