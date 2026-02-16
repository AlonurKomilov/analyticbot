"""
Rate Limit Database Models (Phase 3)

SQLAlchemy ORM models for rate limit configuration persistence
with full audit trail support.

Domain: API rate limiting - database persistence
"""

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Text,
)
from sqlalchemy.sql import func

from infra.db.models.base import Base


class RateLimitConfig(Base):
    """
    Rate limit configuration stored in database

    Stores rate limit settings for different services with metadata
    about who created/modified the config.

    Table: rate_limit_configs
    """

    __tablename__ = "rate_limit_configs"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Service identification
    service_key = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Service identifier (e.g., 'bot_operations', 'auth_login')",
    )
    service_name = Column(
        String(200),
        nullable=False,
        comment="Human-readable service name (e.g., 'Bot Operations')",
    )

    # Rate limit settings
    limit_value = Column(Integer, nullable=False, comment="Maximum requests allowed in the period")
    period = Column(String(20), nullable=False, comment="Time period: 'minute', 'hour', 'day'")
    enabled = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether rate limiting is enabled for this service",
    )

    # Documentation
    description = Column(Text, comment="Detailed description of what this service does")

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    created_by = Column(String(100), comment="Admin user ID who created this config")
    updated_by = Column(String(100), comment="Admin user ID who last updated this config")

    def __repr__(self):
        return f"<RateLimitConfig(service={self.service_key}, limit={self.limit_value}/{self.period}, enabled={self.enabled})>"

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "service_key": self.service_key,
            "service_name": self.service_name,
            "limit": self.limit_value,
            "period": self.period,
            "enabled": self.enabled,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
        }


class RateLimitAuditLog(Base):
    """
    Audit trail for all rate limit configuration changes

    Tracks who changed what and when, with before/after values
    for full change history.

    Table: rate_limit_audit_log
    """

    __tablename__ = "rate_limit_audit_log"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # What was changed
    service_key = Column(
        String(100), nullable=False, index=True, comment="Service that was modified"
    )
    action = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Action performed: 'create', 'update', 'delete', 'reset', 'enable', 'disable'",
    )

    # Before/after values
    old_limit = Column(Integer, comment="Previous limit value")
    new_limit = Column(Integer, comment="New limit value")
    old_period = Column(String(20), comment="Previous period")
    new_period = Column(String(20), comment="New period")
    old_enabled = Column(Boolean, comment="Previous enabled state")
    new_enabled = Column(Boolean, comment="New enabled state")

    # Who made the change
    changed_by = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Admin user ID who made the change",
    )
    changed_by_username = Column(String(200), comment="Admin username")
    changed_by_ip = Column(String(50), comment="IP address of the admin")

    # Why it was changed
    change_reason = Column(Text, comment="Optional explanation for the change")

    # Additional context
    metadata = Column(JSON, comment="Additional metadata (request info, etc.)")

    # When it was changed
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    def __repr__(self):
        return f"<RateLimitAuditLog(service={self.service_key}, action={self.action}, by={self.changed_by_username}, at={self.created_at})>"

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "service_key": self.service_key,
            "action": self.action,
            "old_limit": self.old_limit,
            "new_limit": self.new_limit,
            "old_period": self.old_period,
            "new_period": self.new_period,
            "old_enabled": self.old_enabled,
            "new_enabled": self.new_enabled,
            "changed_by": self.changed_by,
            "changed_by_username": self.changed_by_username,
            "changed_by_ip": self.changed_by_ip,
            "change_reason": self.change_reason,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class RateLimitStats(Base):
    """
    Statistics about rate limit usage over time

    Aggregated statistics for monitoring and analysis.
    Helps identify patterns and potential issues.

    Table: rate_limit_stats
    """

    __tablename__ = "rate_limit_stats"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # What service and IP
    service_key = Column(String(100), nullable=False, index=True, comment="Service being tracked")
    ip_address = Column(
        String(50), nullable=False, index=True, comment="IP address making requests"
    )

    # Usage metrics
    requests_made = Column(
        Integer, default=0, nullable=False, comment="Total requests made in this window"
    )
    requests_blocked = Column(
        Integer, default=0, nullable=False, comment="Requests blocked due to rate limit"
    )

    # Timestamps
    last_request_at = Column(DateTime(timezone=True), comment="When the last request was made")
    last_blocked_at = Column(DateTime(timezone=True), comment="When the last request was blocked")

    # Time window
    window_start = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Start of the time window",
    )
    window_end = Column(DateTime(timezone=True), nullable=False, comment="End of the time window")

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self):
        return f"<RateLimitStats(service={self.service_key}, ip={self.ip_address}, requests={self.requests_made}, blocked={self.requests_blocked})>"

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "service_key": self.service_key,
            "ip_address": self.ip_address,
            "requests_made": self.requests_made,
            "requests_blocked": self.requests_blocked,
            "last_request_at": (self.last_request_at.isoformat() if self.last_request_at else None),
            "last_blocked_at": (self.last_blocked_at.isoformat() if self.last_blocked_at else None),
            "window_start": (self.window_start.isoformat() if self.window_start else None),
            "window_end": self.window_end.isoformat() if self.window_end else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# === INDEXES ===

# Additional indexes will be created in the Alembic migration:
# - idx_audit_log_created_at: For time-based queries
# - idx_stats_window: For efficient window queries (service_key, window_start, window_end)
# - idx_stats_ip_service: For per-IP, per-service lookups

# === EXPORTS ===

__all__ = [
    "RateLimitConfig",
    "RateLimitAuditLog",
    "RateLimitStats",
]
