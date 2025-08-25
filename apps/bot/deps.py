"""
Dependency injection setup for Telegram Bot
Simple DI container for bot handlers
"""

import asyncpg

from config import settings
from core.repositories.postgres import PgDeliveryRepository, PgScheduleRepository
from core.services import DeliveryService, ScheduleService


class BotContainer:
    """
    Simple DI container for bot dependencies
    Manages database connections and service instances
    """

    def __init__(self):
        self._db_pool: asyncpg.Pool | None = None
        self._schedule_service: ScheduleService | None = None
        self._delivery_service: DeliveryService | None = None

    async def init_db_pool(self):
        """Initialize database connection pool"""
        if not self._db_pool:
            self._db_pool = await asyncpg.create_pool(
                settings.DATABASE_URL,
                min_size=settings.DB_POOL_SIZE,
                max_size=settings.DB_MAX_OVERFLOW,
                command_timeout=settings.DB_POOL_TIMEOUT,
            )

    async def get_db_connection(self):
        """Get database connection"""
        if not self._db_pool:
            await self.init_db_pool()
        return self._db_pool.acquire()

    async def get_schedule_service(self) -> ScheduleService:
        """Get schedule service with repository dependencies"""
        if not self._schedule_service:
            # For bot, we'll use a connection per service instance
            # In production, consider connection pooling per request
            connection = await self._db_pool.acquire()
            schedule_repo = PgScheduleRepository(connection)
            self._schedule_service = ScheduleService(schedule_repo)

        return self._schedule_service

    async def get_delivery_service(self) -> DeliveryService:
        """Get delivery service with repository dependencies"""
        if not self._delivery_service:
            connection = await self._db_pool.acquire()
            schedule_repo = PgScheduleRepository(connection)
            delivery_repo = PgDeliveryRepository(connection)
            self._delivery_service = DeliveryService(delivery_repo, schedule_repo)

        return self._delivery_service

    async def cleanup(self):
        """Cleanup resources"""
        if self._db_pool:
            await self._db_pool.close()


# Global container instance
bot_container = BotContainer()
