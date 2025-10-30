"""
Database & Repository DI Container

Single Responsibility: Database connectivity and repository factory
Clean Architecture compliant - uses repository factory pattern
Phase 2 Fix (Oct 19, 2025): Updated to use protocols instead of concrete implementations
"""

import logging
import os
from typing import Any

import asyncpg
from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# ✅ PHASE 2 FIX: Import protocol instead of concrete implementation
from core.protocols import DatabaseManagerProtocol

# ✅ PHASE 3 FIX (Oct 19, 2025): Import repository protocols for type hints
from core.protocols import (
    AdminRepositoryProtocol,
    AnalyticsRepositoryProtocol,
    ChannelDailyRepositoryProtocol,
    ChannelRepositoryProtocol,
    PostMetricsRepositoryProtocol,
    StatsRawRepositoryProtocol,
    UserRepositoryProtocol,
)

# ✅ PHASE 3 FIX: Import concrete repository implementations
from infra.db.repositories.admin_repository import AsyncpgAdminRepository
from infra.db.repositories.analytics_repository import AsyncpgAnalyticsRepository
from infra.db.repositories.channel_daily_repository import ChannelDailyRepository
from infra.db.repositories.channel_repository import AsyncpgChannelRepository
from infra.db.repositories.post_metrics_repository import AsyncpgPostMetricsRepository
from infra.db.repositories.stats_raw_repository import AsyncpgStatsRawRepository
from infra.db.repositories.user_repository import AsyncpgUserRepository

# Import other repositories (no protocols yet)
from core.repositories.alert_repository import AlertSentRepository, AlertSubscriptionRepository
from core.repositories.shared_reports_repository import SharedReportsRepository
from infra.db.repositories.edges_repository import AsyncpgEdgesRepository
from infra.db.repositories.payment_repository import AsyncpgPaymentRepository
from infra.db.repositories.plan_repository import AsyncpgPlanRepository
from infra.db.repositories.post_repository import AsyncpgPostRepository
from infra.db.repositories.schedule_repository import AsyncpgScheduleRepository

# Still need concrete implementation for instantiation
from infra.db.connection_manager import DatabaseManager, db_manager

logger = logging.getLogger(__name__)


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================


async def _create_database_manager() -> DatabaseManagerProtocol:
    """Create or get optimized database manager (returns protocol interface)"""
    if not db_manager._pool:
        await db_manager.initialize()
    return db_manager  # Returns concrete type but typed as protocol


async def _create_asyncpg_pool(database_url: str, pool_size: int = 10) -> asyncpg.Pool:
    """Create asyncpg connection pool"""
    # Convert SQLAlchemy URL to asyncpg format if needed
    db_url = database_url
    if db_url.startswith("postgresql+asyncpg://"):
        db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")

    pool = await asyncpg.create_pool(db_url, min_size=1, max_size=pool_size)
    if pool is None:
        raise RuntimeError("Failed to create asyncpg pool")
    return pool


async def _create_sqlalchemy_engine(
    database_url: str, pool_size: int = 10, max_overflow: int = 20
) -> AsyncEngine:
    """Create SQLAlchemy async engine"""
    # Log the database URL for debugging (mask password)
    masked_url = database_url.replace(database_url.split('@')[0].split('://')[-1], '***')
    logger.info(f"🔧 Creating SQLAlchemy engine with URL: {masked_url}")
    
    # Ensure we're using asyncpg driver
    if not database_url.startswith("postgresql+asyncpg://"):
        logger.warning(f"⚠️  DATABASE_URL does not start with 'postgresql+asyncpg://'")
        logger.warning(f"⚠️  Converting '{database_url.split('://')[0]}' to 'postgresql+asyncpg'")
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
    
    return create_async_engine(
        database_url,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_pre_ping=True,
    )


async def _create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create SQLAlchemy session factory"""
    return async_sessionmaker(engine, expire_on_commit=False)


async def _create_repository(factory, repo_type: str) -> Any:
    """Create repository using factory pattern - no direct infra imports"""
    try:
        if repo_type == "user":
            return await factory.get_user_repository()
        elif repo_type == "channel":
            return await factory.get_channel_repository()
        elif repo_type == "analytics":
            return await factory.get_analytics_repository()
        elif repo_type == "admin":
            return await factory.get_admin_repository()
        elif repo_type == "plan":
            return await factory.get_plan_repository()
        elif repo_type == "schedule":
            return await factory.get_schedule_repository()
        elif repo_type == "payment":
            return await factory.get_payment_repository()
        elif repo_type == "post":
            return await factory.get_post_repository()
        elif repo_type == "metrics":
            return await factory.get_metrics_repository()
        elif repo_type == "channel_daily":
            return await factory.get_channel_daily_repository()
        elif repo_type == "edges":
            return await factory.get_edges_repository()
        elif repo_type == "stats_raw":
            return await factory.get_stats_raw_repository()
        elif repo_type == "alert":
            return await factory.get_alert_repository()
        else:
            logger.warning(f"Unknown repository type: {repo_type}")
            return None
    except Exception as e:
        logger.warning(f"Failed to create {repo_type} repository: {e}")
        return None


# ============================================================================
# DATABASE CONTAINER
# ============================================================================


class DatabaseContainer(containers.DeclarativeContainer):
    """
    Database & Repository Container

    Single Responsibility: Manages database connections and repository access
    Follows Clean Architecture - uses factory pattern for repositories
    """

    # Configuration
    config = providers.Configuration()

    # Database URL from environment or configuration
    database_url = providers.Callable(
        lambda: os.getenv(
            "DATABASE_URL", "postgresql+asyncpg://analytic:change_me@localhost:5432/analytic_bot"
        )
    )

    # ============================================================================
    # DATABASE CONNECTIONS
    # ============================================================================

    database_manager = providers.Resource(_create_database_manager)

    asyncpg_pool = providers.Resource(_create_asyncpg_pool, database_url=database_url, pool_size=10)

    sqlalchemy_engine = providers.Resource(
        _create_sqlalchemy_engine, database_url=database_url, pool_size=10, max_overflow=20
    )

    session_factory = providers.Resource(_create_session_factory, engine=sqlalchemy_engine)

    # Backwards-compatibility alias: some parts of the codebase expect
    # `async_session_maker` on the database container. Provide an alias
    # to the new `session_factory` provider to avoid AttributeError at
    # startup while keeping the clearer name.
    async_session_maker = session_factory

    # ============================================================================
    # REPOSITORIES - Direct DI without Factory Anti-Pattern ✅
    # Phase 3 Fix (Oct 19, 2025): Eliminated factory.py, using direct providers
    # ============================================================================

    # User Repository (Protocol: UserRepositoryProtocol)
    user_repo = providers.Factory(
        AsyncpgUserRepository,
        pool=asyncpg_pool,
    )

    # Channel Repository (Protocol: ChannelRepositoryProtocol)
    channel_repo = providers.Factory(
        AsyncpgChannelRepository,
        pool=asyncpg_pool,
    )

    # Analytics Repository (Protocol: AnalyticsRepositoryProtocol)
    analytics_repo = providers.Factory(
        AsyncpgAnalyticsRepository,
        pool=asyncpg_pool,
    )

    # Admin Repository (Protocol: AdminRepositoryProtocol)
    admin_repo = providers.Factory(
        AsyncpgAdminRepository,
        pool=asyncpg_pool,
    )

    # Channel Daily Repository (Protocol: ChannelDailyRepositoryProtocol)
    channel_daily_repo = providers.Factory(
        ChannelDailyRepository,
        pool=asyncpg_pool,
    )

    # Post Metrics Repository (Protocol: PostMetricsRepositoryProtocol)
    metrics_repo = providers.Factory(
        AsyncpgPostMetricsRepository,
        pool=asyncpg_pool,
    )

    # Stats Raw Repository (Protocol: StatsRawRepositoryProtocol)
    stats_raw_repo = providers.Factory(
        AsyncpgStatsRawRepository,
        pool=asyncpg_pool,
    )

    # Other Repositories (no protocols yet)
    plan_repo = providers.Factory(
        AsyncpgPlanRepository,
        pool=asyncpg_pool,
    )

    schedule_repo = providers.Factory(
        AsyncpgScheduleRepository,
        pool=asyncpg_pool,
    )

    payment_repo = providers.Factory(
        AsyncpgPaymentRepository,
        pool=asyncpg_pool,
    )

    post_repo = providers.Factory(
        AsyncpgPostRepository,
        pool=asyncpg_pool,
    )

    edges_repo = providers.Factory(
        AsyncpgEdgesRepository,
        pool=asyncpg_pool,
    )

    # Alert repositories (from core)
    alert_subscription_repo = providers.Factory(
        AlertSubscriptionRepository,
        pool=asyncpg_pool,
    )

    alert_sent_repo = providers.Factory(
        AlertSentRepository,
        pool=asyncpg_pool,
    )

    # Shared reports repository
    shared_reports_repo = providers.Factory(
        SharedReportsRepository,
        pool=asyncpg_pool,
    )


# ============================================================================
# CLEANUP
# ============================================================================


async def cleanup_database_pool():
    """Cleanup database connections"""
    logger.info("Cleaning up database connections")
    # Cleanup will be handled by container lifecycle
