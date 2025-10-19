"""
⚠️ ⚠️ ⚠️ NOTICE - MIGRATION IN PROGRESS ⚠️ ⚠️ ⚠️

This file is being phased out in favor of the unified DI system: apps/di/

MIGRATION STATUS: All critical files have been migrated (12/12 complete)

MIGRATION GUIDE:
---------------

OLD (this file):
    from apps.shared.di import get_container, Container
    container = get_container()
    user_repo = await container.user_repo()

NEW (unified DI):
    from apps.di import get_container
    container = get_container()
    user_repo = await container.database.user_repo()

KEY CHANGES:
1. Import from apps.di instead of apps.shared.di
2. Use namespaced access: container.database.X() instead of container.X()
3. All providers are now properly organized by domain

DEPRECATION SCHEDULE:
- 2025-10-19: Migration complete (all files updated)
- 2025-10-26: Evaluate for removal or conversion to forwarding shim

See: DI_MIGRATION_COMPLETE.md for full migration report

---

Dependency Injection Container
Minimal, practical skeleton for Clean Architecture
"""

import warnings
from dataclasses import dataclass

# Emit migration notice
warnings.warn(
    "apps/shared/di is being phased out. Use apps/di/ instead. "
    "See DI_MIGRATION_COMPLETE.md for migration guide.",
    FutureWarning,
    stacklevel=2
)

import asyncpg
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from core.repositories.interfaces import AdminRepository, UserRepository
from infra.db.connection_manager import DatabaseManager, db_manager
from infra.db.repositories import (
    AsyncpgAdminRepository,
    AsyncpgAnalyticsRepository,
    AsyncpgChannelRepository,
    AsyncpgPaymentRepository,
    AsyncpgPlanRepository,
    AsyncpgUserRepository,
)


class OptimizedPoolAdapter:
    """Adapter to provide asyncpg pool interface using optimized database manager"""

    def __init__(self, db_manager: DatabaseManager):
        self._db_manager = db_manager

    @classmethod
    async def create(cls, db_manager: DatabaseManager):
        """Create adapter instance"""
        return cls(db_manager)

    async def fetchrow(self, query: str, *args, **kwargs):
        """Fetch single row"""
        return await self._db_manager.fetch_one(query, *args, **kwargs)

    async def fetch(self, query: str, *args, **kwargs):
        """Fetch multiple rows"""
        return await self._db_manager.fetch_query(query, *args, **kwargs)

    async def execute(self, query: str, *args, **kwargs):
        """Execute query"""
        return await self._db_manager.execute_query(query, *args, **kwargs)


@dataclass(frozen=True)
class Settings:
    """Application settings"""

    database_url: str
    database_pool_size: int = 10
    database_max_overflow: int = 20


class Container:
    """Dependency Injection Container"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None
        self._asyncpg_pool: asyncpg.Pool | None = None
        self._db_manager: DatabaseManager | None = None

    # Database connections - now using optimized database manager
    async def database_manager(self) -> DatabaseManager:
        """Get optimized database manager"""
        if not self._db_manager:
            self._db_manager = db_manager
            if not db_manager._pool:  # Initialize if not already done
                await db_manager.initialize()
        return self._db_manager

    async def engine(self) -> AsyncEngine:
        """Get SQLAlchemy async engine (for future SQLAlchemy implementations)"""
        if not self._engine:
            self._engine = create_async_engine(
                self.settings.database_url,
                pool_size=self.settings.database_pool_size,
                max_overflow=self.settings.database_max_overflow,
                pool_pre_ping=True,
            )
        return self._engine

    async def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Get SQLAlchemy session factory"""
        if not self._session_factory:
            engine = await self.engine()
            self._session_factory = async_sessionmaker(engine, expire_on_commit=False)
        return self._session_factory

    async def asyncpg_pool(self) -> asyncpg.Pool:
        """Get asyncpg connection pool (legacy - use database_manager instead)"""
        if not self._asyncpg_pool:
            # Convert SQLAlchemy URL to asyncpg format if needed
            db_url = self.settings.database_url
            if db_url.startswith("postgresql+asyncpg://"):
                db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")

            self._asyncpg_pool = await asyncpg.create_pool(
                db_url, min_size=1, max_size=self.settings.database_pool_size
            )
        assert self._asyncpg_pool is not None  # Type narrowing for mypy
        return self._asyncpg_pool

    # Repository implementations (infra layer) - now using optimized connection management
    async def user_repo(self) -> UserRepository:
        """Get User repository implementation"""
        pool = await self.asyncpg_pool()
        return AsyncpgUserRepository(pool)

    async def admin_repo(self) -> AdminRepository:
        """Get Admin repository implementation"""
        pool = await self.asyncpg_pool()
        return AsyncpgAdminRepository(pool)

    async def analytics_repo(self) -> AsyncpgAnalyticsRepository:
        """Get Analytics repository implementation"""
        pool = await self.asyncpg_pool()
        return AsyncpgAnalyticsRepository(pool)

    async def channel_repo(self) -> AsyncpgChannelRepository:
        """Get Channel repository implementation"""
        pool = await self.asyncpg_pool()
        return AsyncpgChannelRepository(pool)

    async def payment_repo(self) -> AsyncpgPaymentRepository:
        """Get Payment repository implementation"""
        pool = await self.asyncpg_pool()
        return AsyncpgPaymentRepository(pool)

    async def plan_repo(self) -> AsyncpgPlanRepository:
        """Get Plan repository implementation"""
        pool = await self.asyncpg_pool()
        return AsyncpgPlanRepository(pool)

    # Service layer (to be implemented)
    # async def user_service(self) -> UserService:
    #     """Get User service implementation"""
    #     user_repo = await self.user_repo()
    #     return UserService(user_repo)

    # Cleanup
    async def close(self):
        """Close all connections"""
        if self._db_manager:
            await self._db_manager.close()
        if self._asyncpg_pool:
            await self._asyncpg_pool.close()
        if self._engine:
            await self._engine.dispose()


# Global container instance (auto-initialized with default settings)
_container: Container | None = None


def get_container() -> Container:
    """
    Get global container instance

    NOTE: For new code, prefer using apps.shared.unified_di.get_container()
    This function is maintained for backward compatibility.
    """
    global _container
    if _container is None:
        # Auto-initialize with settings from config module
        from config import settings as app_settings

        # Get database URL from config settings
        database_url = app_settings.get_database_url()

        # Convert postgresql:// to postgresql+asyncpg:// if needed for SQLAlchemy
        if database_url.startswith("postgresql://") and "+asyncpg" not in database_url:
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")

        default_settings = Settings(
            database_url=database_url,
            database_pool_size=app_settings.DB_POOL_SIZE,
            database_max_overflow=app_settings.DB_MAX_OVERFLOW,
        )
        _container = Container(default_settings)
    return _container


def init_container(settings: Settings) -> Container:
    """Initialize global container with custom settings"""
    global _container
    _container = Container(settings)
    return _container


async def close_container():
    """Close global container"""
    global _container
    if _container:
        await _container.close()
        _container = None


# Create container alias for backward compatibility
container = get_container
