"""
SuperAdmin Management Panel - Database Models
Enterprise-grade admin system with comprehensive user and system management
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Base class for all admin models"""
    pass


class AdminRole(str, Enum):
    """Admin role hierarchy"""
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
    """SuperAdmin users with elevated privileges"""
    __tablename__ = "admin_users"
    
    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[AdminRole] = mapped_column(String(20), nullable=False)
    
    # Security fields
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # IP Security
    allowed_ips: Mapped[Optional[list]] = mapped_column(JSON)  # List of allowed IP addresses
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by: Mapped[Optional[UUID]] = mapped_column(PostgresUUID(as_uuid=True), ForeignKey("admin_users.id"))
    
    # Relationships
    sessions: Mapped[list["AdminSession"]] = relationship("AdminSession", back_populates="admin_user", cascade="all, delete-orphan")
    audit_logs: Mapped[list["AdminAuditLog"]] = relationship("AdminAuditLog", back_populates="admin_user")


class AdminSession(Base):
    """Admin user sessions with enhanced security"""
    __tablename__ = "admin_sessions"
    
    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    admin_user_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), ForeignKey("admin_users.id"), nullable=False)
    session_token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    
    # Session metadata
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    user_agent: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_activity: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    admin_user: Mapped["AdminUser"] = relationship("AdminUser", back_populates="sessions")


class SystemUser(Base):
    """System users managed by SuperAdmin"""
    __tablename__ = "system_users"
    
    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(50))
    full_name: Mapped[Optional[str]] = mapped_column(String(100))
    email: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Status and subscription
    status: Mapped[UserStatus] = mapped_column(String(20), nullable=False, default=UserStatus.ACTIVE)
    subscription_tier: Mapped[Optional[str]] = mapped_column(String(20))  # free, basic, pro, enterprise
    
    # Usage statistics
    total_channels: Mapped[int] = mapped_column(Integer, default=0)
    total_posts: Mapped[int] = mapped_column(Integer, default=0)
    last_activity: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    suspended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    suspended_by: Mapped[Optional[UUID]] = mapped_column(PostgresUUID(as_uuid=True), ForeignKey("admin_users.id"))
    suspension_reason: Mapped[Optional[str]] = mapped_column(Text)


class AdminAuditLog(Base):
    """Comprehensive audit logging for admin actions"""
    __tablename__ = "admin_audit_logs"
    
    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    admin_user_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), ForeignKey("admin_users.id"), nullable=False)
    
    # Action details
    action: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., "user_suspended", "system_config_updated"
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., "user", "system", "subscription"
    resource_id: Mapped[Optional[str]] = mapped_column(String(100))  # ID of affected resource
    
    # Request details
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    request_method: Mapped[Optional[str]] = mapped_column(String(10))
    request_path: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Change tracking
    old_values: Mapped[Optional[dict]] = mapped_column(JSON)
    new_values: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # Metadata
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    additional_data: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    admin_user: Mapped["AdminUser"] = relationship("AdminUser", back_populates="audit_logs")


class SystemConfiguration(Base):
    """Runtime system configuration managed by SuperAdmin"""
    __tablename__ = "system_configurations"
    
    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    value_type: Mapped[str] = mapped_column(String(20), nullable=False)  # string, integer, boolean, json
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # system, security, features, etc.
    
    # Metadata
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_sensitive: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_restart: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    updated_by: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), ForeignKey("admin_users.id"), nullable=False)


class SystemMetrics(Base):
    """System-wide metrics and statistics"""
    __tablename__ = "system_metrics"
    
    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)
    metric_value: Mapped[float] = mapped_column(nullable=False)
    metric_type: Mapped[str] = mapped_column(String(20), nullable=False)  # counter, gauge, histogram
    
    # Dimensions/Labels
    labels: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # Timestamp
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
