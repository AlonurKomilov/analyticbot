"""
User AI Services Repository
============================

Repository for managing user's active AI marketplace services.
"""

import logging
from datetime import datetime

import asyncpg

logger = logging.getLogger(__name__)


class UserAIServicesRepository:
    """Repository for user AI services management."""

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def get_active_services(self, user_id: int) -> list[dict]:
        """Get all active AI services for a user."""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT 
                    id, user_id, service_key, enabled, activated_at, expires_at,
                    config, usage_count, last_used_at, subscription_id,
                    created_at, updated_at
                FROM user_ai_services
                WHERE user_id = $1 
                AND enabled = true
                AND (expires_at IS NULL OR expires_at > NOW())
                ORDER BY activated_at DESC
                """,
                user_id,
            )
            return [dict(row) for row in rows]

    async def activate_service(
        self,
        user_id: int,
        service_key: str,
        expires_at: datetime | None = None,
        subscription_id: int | None = None,
        config: dict | None = None,
    ) -> dict:
        """Activate an AI service for a user."""
        async with self.pool.acquire() as conn:
            # Check if service already exists
            existing = await conn.fetchrow(
                """
                SELECT id FROM user_ai_services
                WHERE user_id = $1 AND service_key = $2
                """,
                user_id,
                service_key,
            )

            if existing:
                # Update existing service
                row = await conn.fetchrow(
                    """
                    UPDATE user_ai_services
                    SET 
                        enabled = true,
                        expires_at = $3,
                        subscription_id = $4,
                        config = $5,
                        updated_at = NOW()
                    WHERE user_id = $1 AND service_key = $2
                    RETURNING 
                        id, user_id, service_key, enabled, activated_at, expires_at,
                        config, usage_count, last_used_at, subscription_id,
                        created_at, updated_at
                    """,
                    user_id,
                    service_key,
                    expires_at,
                    subscription_id,
                    config or {},
                )
                logger.info(f"✅ Re-activated AI service {service_key} for user {user_id}")
            else:
                # Create new service
                row = await conn.fetchrow(
                    """
                    INSERT INTO user_ai_services (
                        user_id, service_key, enabled, expires_at, 
                        subscription_id, config
                    )
                    VALUES ($1, $2, true, $3, $4, $5)
                    RETURNING 
                        id, user_id, service_key, enabled, activated_at, expires_at,
                        config, usage_count, last_used_at, subscription_id,
                        created_at, updated_at
                    """,
                    user_id,
                    service_key,
                    expires_at,
                    subscription_id,
                    config or {},
                )
                logger.info(f"✅ Activated AI service {service_key} for user {user_id}")

            return dict(row)

    async def deactivate_service(self, user_id: int, service_key: str) -> bool:
        """Deactivate an AI service."""
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE user_ai_services
                SET enabled = false, updated_at = NOW()
                WHERE user_id = $1 AND service_key = $2
                """,
                user_id,
                service_key,
            )
            success = result.split()[-1] == "1"
            if success:
                logger.info(f"❌ Deactivated AI service {service_key} for user {user_id}")
            return success

    async def is_service_active(self, user_id: int, service_key: str) -> bool:
        """Check if a service is active for a user."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT id FROM user_ai_services
                WHERE user_id = $1 
                AND service_key = $2
                AND enabled = true
                AND (expires_at IS NULL OR expires_at > NOW())
                """,
                user_id,
                service_key,
            )
            return row is not None

    async def update_usage(self, user_id: int, service_key: str) -> dict | None:
        """Increment usage counter for a service."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                UPDATE user_ai_services
                SET 
                    usage_count = usage_count + 1,
                    last_used_at = NOW(),
                    updated_at = NOW()
                WHERE user_id = $1 AND service_key = $2
                RETURNING 
                    id, user_id, service_key, enabled, activated_at, expires_at,
                    config, usage_count, last_used_at, subscription_id,
                    created_at, updated_at
                """,
                user_id,
                service_key,
            )
            return dict(row) if row else None

    async def get_service(self, user_id: int, service_key: str) -> dict | None:
        """Get specific service details."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT 
                    id, user_id, service_key, enabled, activated_at, expires_at,
                    config, usage_count, last_used_at, subscription_id,
                    created_at, updated_at
                FROM user_ai_services
                WHERE user_id = $1 AND service_key = $2
                """,
                user_id,
                service_key,
            )
            return dict(row) if row else None

    async def cleanup_expired_services(self) -> int:
        """Disable services that have expired."""
        async with self.pool.acquire() as conn:
            result = await conn.execute("""
                UPDATE user_ai_services
                SET enabled = false, updated_at = NOW()
                WHERE enabled = true
                AND expires_at IS NOT NULL
                AND expires_at <= NOW()
                """)
            disabled_count = int(result.split()[-1])
            if disabled_count > 0:
                logger.info(f"🧹 Disabled {disabled_count} expired AI services")
            return disabled_count
