"""
Rate Limit Repository (Phase 3)

Database operations for rate limit configurations with full audit trail.
Handles CRUD operations and audit logging.

Domain: API rate limiting - database persistence
"""

import logging
from datetime import datetime
from typing import Any

from sqlalchemy import and_, delete, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from infra.db.models.rate_limit_orm import (
    RateLimitAuditLog,
    RateLimitConfig,
    RateLimitStats,
)

logger = logging.getLogger(__name__)


class RateLimitRepository:
    """
    Repository for rate limit configuration management

    Handles all database operations for rate limit configs,
    audit logs, and statistics.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize repository

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    # === CONFIG OPERATIONS ===

    async def get_config(self, service_key: str) -> RateLimitConfig | None:
        """
        Get configuration for a specific service

        Args:
            service_key: Service identifier (e.g., "bot_operations")

        Returns:
            Configuration or None if not found
        """
        try:
            result = await self.session.execute(
                select(RateLimitConfig).where(RateLimitConfig.service_key == service_key)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting config for {service_key}: {e}")
            return None

    async def get_all_configs(self, enabled_only: bool = False) -> list[RateLimitConfig]:
        """
        Get all configurations

        Args:
            enabled_only: If True, return only enabled configs

        Returns:
            List of configurations
        """
        try:
            query = select(RateLimitConfig)
            if enabled_only:
                query = query.where(RateLimitConfig.enabled == True)

            query = query.order_by(RateLimitConfig.service_name)

            result = await self.session.execute(query)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting all configs: {e}")
            return []

    async def create_config(
        self,
        service_key: str,
        service_name: str,
        limit_value: int,
        period: str,
        enabled: bool = True,
        description: str | None = None,
        created_by: str | None = None,
    ) -> RateLimitConfig | None:
        """
        Create a new configuration

        Args:
            service_key: Unique service identifier
            service_name: Human-readable service name
            limit_value: Maximum requests in period
            period: Time period (minute, hour, day)
            enabled: Whether rate limiting is enabled
            description: Optional description
            created_by: Admin user ID who created this

        Returns:
            Created configuration or None on error
        """
        try:
            config = RateLimitConfig(
                service_key=service_key,
                service_name=service_name,
                limit_value=limit_value,
                period=period,
                enabled=enabled,
                description=description,
                created_by=created_by,
                updated_by=created_by,
            )

            self.session.add(config)
            await self.session.commit()
            await self.session.refresh(config)

            logger.info(f"Created rate limit config: {service_key} = {limit_value}/{period}")
            return config

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating config for {service_key}: {e}")
            return None

    async def update_config(
        self,
        service_key: str,
        limit_value: int | None = None,
        period: str | None = None,
        enabled: bool | None = None,
        description: str | None = None,
        updated_by: str | None = None,
    ) -> RateLimitConfig | None:
        """
        Update an existing configuration

        Args:
            service_key: Service to update
            limit_value: New limit (optional)
            period: New period (optional)
            enabled: New enabled state (optional)
            description: New description (optional)
            updated_by: Admin user ID who updated this

        Returns:
            Updated configuration or None on error
        """
        try:
            # Get existing config
            config = await self.get_config(service_key)
            if not config:
                logger.warning(f"Config not found for update: {service_key}")
                return None

            # Update fields
            if limit_value is not None:
                config.limit_value = limit_value
            if period is not None:
                config.period = period
            if enabled is not None:
                config.enabled = enabled
            if description is not None:
                config.description = description
            if updated_by is not None:
                config.updated_by = updated_by

            config.updated_at = datetime.utcnow()

            await self.session.commit()
            await self.session.refresh(config)

            logger.info(f"Updated rate limit config: {service_key}")
            return config

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating config for {service_key}: {e}")
            return None

    async def delete_config(self, service_key: str) -> bool:
        """
        Delete a configuration

        Args:
            service_key: Service to delete

        Returns:
            True if deleted, False otherwise
        """
        try:
            result = await self.session.execute(
                delete(RateLimitConfig).where(RateLimitConfig.service_key == service_key)
            )
            await self.session.commit()

            deleted = result.rowcount > 0
            if deleted:
                logger.info(f"Deleted rate limit config: {service_key}")
            else:
                logger.warning(f"Config not found for deletion: {service_key}")

            return deleted

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting config for {service_key}: {e}")
            return False

    # === AUDIT LOG OPERATIONS ===

    async def log_change(
        self,
        service_key: str,
        action: str,
        old_config: RateLimitConfig | None,
        new_config: RateLimitConfig | None,
        changed_by: str,
        changed_by_username: str | None = None,
        changed_by_ip: str | None = None,
        change_reason: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RateLimitAuditLog | None:
        """
        Log a configuration change to audit trail

        Args:
            service_key: Service that was changed
            action: Action performed (create, update, delete, enable, disable, reset)
            old_config: Configuration before change (None for create)
            new_config: Configuration after change (None for delete)
            changed_by: Admin user ID
            changed_by_username: Admin username
            changed_by_ip: Admin IP address
            change_reason: Optional explanation
            metadata: Additional context

        Returns:
            Created audit log entry or None on error
        """
        try:
            audit_entry = RateLimitAuditLog(
                service_key=service_key,
                action=action,
                old_limit=old_config.limit_value if old_config else None,
                new_limit=new_config.limit_value if new_config else None,
                old_period=old_config.period if old_config else None,
                new_period=new_config.period if new_config else None,
                old_enabled=old_config.enabled if old_config else None,
                new_enabled=new_config.enabled if new_config else None,
                changed_by=changed_by,
                changed_by_username=changed_by_username,
                changed_by_ip=changed_by_ip,
                change_reason=change_reason,
                metadata=metadata,
            )

            self.session.add(audit_entry)
            await self.session.commit()
            await self.session.refresh(audit_entry)

            logger.info(
                f"Logged rate limit change: {action} on {service_key} by {changed_by_username or changed_by}"
            )
            return audit_entry

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error logging audit entry for {service_key}: {e}")
            return None

    async def get_audit_trail(
        self,
        service_key: str | None = None,
        changed_by: str | None = None,
        action: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[RateLimitAuditLog]:
        """
        Get audit trail with optional filters

        Args:
            service_key: Filter by service (optional)
            changed_by: Filter by admin user (optional)
            action: Filter by action type (optional)
            limit: Maximum records to return
            offset: Number of records to skip

        Returns:
            List of audit log entries
        """
        try:
            query = select(RateLimitAuditLog)

            # Apply filters
            conditions = []
            if service_key:
                conditions.append(RateLimitAuditLog.service_key == service_key)
            if changed_by:
                conditions.append(RateLimitAuditLog.changed_by == changed_by)
            if action:
                conditions.append(RateLimitAuditLog.action == action)

            if conditions:
                query = query.where(and_(*conditions))

            # Order by newest first
            query = query.order_by(desc(RateLimitAuditLog.created_at))

            # Pagination
            query = query.limit(limit).offset(offset)

            result = await self.session.execute(query)
            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"Error getting audit trail: {e}")
            return []

    async def get_recent_changes(self, hours: int = 24, limit: int = 50) -> list[RateLimitAuditLog]:
        """
        Get recent configuration changes

        Args:
            hours: Number of hours to look back
            limit: Maximum records to return

        Returns:
            List of recent audit log entries
        """
        try:
            cutoff_time = datetime.utcnow().replace(hour=datetime.utcnow().hour - hours)

            query = (
                select(RateLimitAuditLog)
                .where(RateLimitAuditLog.created_at >= cutoff_time)
                .order_by(desc(RateLimitAuditLog.created_at))
                .limit(limit)
            )

            result = await self.session.execute(query)
            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"Error getting recent changes: {e}")
            return []

    # === STATS OPERATIONS ===

    async def record_request(
        self,
        service_key: str,
        ip_address: str,
        blocked: bool = False,
    ) -> bool:
        """
        Record a request in statistics

        Args:
            service_key: Service that handled the request
            ip_address: IP address that made the request
            blocked: Whether the request was blocked

        Returns:
            True if recorded successfully
        """
        try:
            # Get or create stats record for current hour window
            now = datetime.utcnow()
            window_start = now.replace(minute=0, second=0, microsecond=0)
            window_end = window_start.replace(hour=window_start.hour + 1)

            # Try to find existing record
            result = await self.session.execute(
                select(RateLimitStats).where(
                    and_(
                        RateLimitStats.service_key == service_key,
                        RateLimitStats.ip_address == ip_address,
                        RateLimitStats.window_start == window_start,
                    )
                )
            )
            stats = result.scalar_one_or_none()

            if stats:
                # Update existing
                stats.requests_made += 1
                if blocked:
                    stats.requests_blocked += 1
                    stats.last_blocked_at = now
                stats.last_request_at = now
                stats.updated_at = now
            else:
                # Create new
                stats = RateLimitStats(
                    service_key=service_key,
                    ip_address=ip_address,
                    requests_made=1,
                    requests_blocked=1 if blocked else 0,
                    last_request_at=now,
                    last_blocked_at=now if blocked else None,
                    window_start=window_start,
                    window_end=window_end,
                )
                self.session.add(stats)

            await self.session.commit()
            return True

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error recording request stats: {e}")
            return False

    async def get_stats(
        self,
        service_key: str | None = None,
        ip_address: str | None = None,
        hours: int = 24,
    ) -> list[RateLimitStats]:
        """
        Get usage statistics

        Args:
            service_key: Filter by service (optional)
            ip_address: Filter by IP (optional)
            hours: Number of hours to look back

        Returns:
            List of statistics records
        """
        try:
            cutoff_time = datetime.utcnow().replace(hour=datetime.utcnow().hour - hours)

            query = select(RateLimitStats).where(RateLimitStats.window_start >= cutoff_time)

            if service_key:
                query = query.where(RateLimitStats.service_key == service_key)
            if ip_address:
                query = query.where(RateLimitStats.ip_address == ip_address)

            query = query.order_by(desc(RateLimitStats.window_start))

            result = await self.session.execute(query)
            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return []


# === HELPER FUNCTIONS ===


async def get_rate_limit_repository(session: AsyncSession) -> RateLimitRepository:
    """
    Factory function to create repository instance

    Args:
        session: SQLAlchemy async session

    Returns:
        Repository instance
    """
    return RateLimitRepository(session)


# === EXPORTS ===

__all__ = [
    "RateLimitRepository",
    "get_rate_limit_repository",
]
