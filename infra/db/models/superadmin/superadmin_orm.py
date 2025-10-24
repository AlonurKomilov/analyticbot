"""
SuperAdmin Management Panel - Database Models
Enterprise-grade admin system with comprehensive user and system management

Updated for 5-Role Hierarchical System: viewer < user < moderator < admin < owner
"""

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Base class for all admin models"""


class AdminRole(str, Enum):
    """
    DEPRECATED: Admin role hierarchy - use new 5-role system instead

    Migration to new system:
    - SUPPORT → moderator (with customer_support permission)
    - MODERATOR → moderator
    - ADMIN → admin
    - SUPER_ADMIN → owner
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
    DELETED = "deleted"
    PENDING = "pending"


class AdminUser(Base):
    """
    SuperAdmin users with elevated privileges - Aligned with 5-role domain model

    Role system: viewer < user < moderator < admin < owner
    Default role: moderator (support team level)
    """

    __tablename__ = "admin_users"

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        String(20), nullable=False, default="moderator"
    )  # New 5-role system

    # Profile fields
    status: Mapped[str] = mapped_column(String(20), default="active")
    first_name: Mapped[str] = mapped_column(String(50), default="")
    last_name: Mapped[str] = mapped_column(String(50), default="")
    phone: Mapped[str | None] = mapped_column(String(20))
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")
    language: Mapped[str] = mapped_column(String(10), default="en")

    # Security fields
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_activity: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    is_mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    account_locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    password_changed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Preferences and permissions
    preferences: Mapped[dict | None] = mapped_column(JSON)  # User preferences
    permissions: Mapped[list | None] = mapped_column(JSON)  # User-specific permissions

    # Audit fields
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    created_by: Mapped[UUID | None] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("admin_users.id")
    )

    # Relationships
    sessions: Mapped[list["AdminSession"]] = relationship(
        "AdminSession", back_populates="admin_user", cascade="all, delete-orphan"
    )
    audit_logs: Mapped[list["AdminAuditLog"]] = relationship(
        "AdminAuditLog", back_populates="admin_user"
    )


class AdminSession(Base):
    """Admin user sessions with enhanced security - Aligned with domain model"""

    __tablename__ = "admin_sessions"

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("admin_users.id"), nullable=False
    )
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    # Session metadata
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    user_agent: Mapped[str] = mapped_column(Text)
    device_info: Mapped[dict | None] = mapped_column(JSON)  # Device information
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_activity: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    admin_user: Mapped["AdminUser"] = relationship("AdminUser", back_populates="sessions")


class SystemUser(Base):
    """System components/services tracked by SuperAdmin - Aligned with SystemComponent domain"""

    __tablename__ = "system_components"

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default="offline")
    version: Mapped[str] = mapped_column(String(20), default="1.0.0")
    health_check_url: Mapped[str | None] = mapped_column(String(500))
    last_health_check: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Configuration and metrics
    metrics: Mapped[dict | None] = mapped_column(JSON)  # Performance metrics
    config: Mapped[dict | None] = mapped_column(JSON)  # Component configuration
    dependencies: Mapped[list | None] = mapped_column(JSON)  # List of dependency names

    # Audit fields
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class AdminAuditLog(Base):
    """Comprehensive audit logging for admin actions - Aligned with AuditEntry domain"""

    __tablename__ = "admin_audit_logs"

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID | None] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("admin_users.id")
    )

    # Action details
    action: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # e.g., "user_suspended", "system_config_updated"
    resource_type: Mapped[str] = mapped_column(
        String(50), default=""
    )  # e.g., "user", "system", "subscription"
    resource_id: Mapped[str | None] = mapped_column(String(100))  # ID of affected resource
    description: Mapped[str] = mapped_column(Text, default="")

    # Request details
    ip_address: Mapped[str | None] = mapped_column(String(45))
    user_agent: Mapped[str | None] = mapped_column(Text)

    # Change tracking
    old_values: Mapped[dict | None] = mapped_column(JSON)
    new_values: Mapped[dict | None] = mapped_column(JSON)

    # Additional metadata
    audit_metadata: Mapped[dict | None] = mapped_column(
        JSON, name="metadata"
    )  # Additional metadata

    # Timestamp
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    admin_user: Mapped["AdminUser"] = relationship("AdminUser", back_populates="audit_logs")


class SystemConfiguration(Base):
    """Runtime system configuration managed by SuperAdmin - Aligned with SystemConfig domain"""

    __tablename__ = "system_configurations"

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(
        String(50), default="general"
    )  # system, security, features, etc.

    # Metadata
    description: Mapped[str] = mapped_column(Text, default="")
    is_sensitive: Mapped[bool] = mapped_column(Boolean, default=False)
    validation_rules: Mapped[dict | None] = mapped_column(JSON)  # Validation rules

    # Audit fields
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    updated_by: Mapped[UUID | None] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("admin_users.id")
    )


class SystemMetrics(Base):
    """Admin notifications - Aligned with AdminNotification domain model"""

    __tablename__ = "admin_notifications"

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID | None] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("admin_users.id")
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, default="")
    type: Mapped[str] = mapped_column(String(20), default="info")  # info, warning, error, success
    # Priority: low, normal, high, urgent
    priority: Mapped[str] = mapped_column(String(20), default="normal")
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    notification_metadata: Mapped[dict | None] = mapped_column(
        JSON, name="metadata"
    )  # Additional metadata
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
