"""
Dependency injection setup for Telegram Bot
Simple DI container for bot handlers
"""

import os

import aiosqlite
import asyncpg
from src.shared_kernel.domain.services import DeliveryService, ScheduleService

from config import settings
from src.shared_kernel.infrastructure.persistence import (
    AsyncpgDeliveryRepository,
    AsyncpgScheduleRepository,
)


class BotContainer:
    """
    Simple DI container for bot dependencies
    Manages database connections and service instances
    """

    def __init__(self):
        self._db_pool: asyncpg.Pool | None = None
        self._sqlite_conn: aiosqlite.Connection | None = None
        self._schedule_service: ScheduleService | None = None
        self._delivery_service: DeliveryService | None = None
        self._use_sqlite = not settings.DATABASE_URL or "sqlite" in settings.DATABASE_URL

    async def init_db_pool(self):
        """Initialize database connection pool"""
        if self._use_sqlite:
            # Use SQLite for local development
            db_path = "data/analytics.db"
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            self._sqlite_conn = await aiosqlite.connect(db_path)
            print(f"Bot: Connected to SQLite database at {db_path}")
        else:
            if not self._db_pool:
                # Convert SQLAlchemy URL to asyncpg-compatible URL
                db_url = settings.DATABASE_URL
                if db_url and db_url.startswith("postgresql+asyncpg://"):
                    db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")

                self._db_pool = await asyncpg.create_pool(
                    db_url,
                    min_size=settings.DB_POOL_SIZE,
                    max_size=settings.DB_MAX_OVERFLOW,
                    command_timeout=settings.DB_POOL_TIMEOUT,
                )
                print("Bot: Connected to PostgreSQL database")

    async def get_db_connection(self):
        """Get database connection"""
        if not self._db_pool and not self._sqlite_conn:
            await self.init_db_pool()

        if self._use_sqlite:
            return self._sqlite_conn
        else:
            return self._db_pool.acquire()

    async def get_schedule_service(self) -> ScheduleService:
        """Get schedule service with repository dependencies"""
        if not self._schedule_service:
            if self._use_sqlite:
                # For SQLite, we'll need to create a different repository implementation
                # For now, let's create a dummy service
                print("Warning: SQLite repositories not implemented yet")
                return None
            else:
                # For bot, we'll use a connection per service instance
                # In production, consider connection pooling per request
                connection = await self._db_pool.acquire()
                schedule_repo = AsyncpgScheduleRepository(connection)
                self._schedule_service = ScheduleService(schedule_repo)

        return self._schedule_service

    async def get_delivery_service(self) -> DeliveryService:
        """Get delivery service with repository dependencies"""
        if not self._delivery_service:
            if self._use_sqlite:
                # For SQLite, we'll need to create a different repository implementation
                # For now, let's create a dummy service
                print("Warning: SQLite repositories not implemented yet")
                return None
            else:
                connection = await self._db_pool.acquire()
                schedule_repo = AsyncpgScheduleRepository(connection)
                delivery_repo = AsyncpgDeliveryRepository(connection)
                self._delivery_service = DeliveryService(delivery_repo, schedule_repo)

        return self._delivery_service

    async def cleanup(self):
        """Cleanup resources"""
        if self._db_pool:
            await self._db_pool.close()
        if self._sqlite_conn:
            await self._sqlite_conn.close()


# Global container instance
bot_container = BotContainer()
