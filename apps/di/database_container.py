"""
Database & Repository DI Container

Single Responsibility: Database connectivity and repository factory
Clean Architecture compliant - uses repository factory pattern
Phase 2 Fix (Oct 19, 2025): Updated to use protocols instead of concrete implementations
Phase 3 Fix (Dec 19, 2025): Added scaling infrastructure (PgBouncer, ReadReplicas, QueryCache)
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
# ✅ PHASE 3 FIX (Oct 19, 2025): Import repository protocols for type hints
from core.protocols import (
    DatabaseManagerProtocol,
)

# Import other repositories (no protocols yet)
from core.repositories.alert_repository import (
    AlertSentRepository,
    AlertSubscriptionRepository,
)
from core.repositories.shared_reports_repository import SharedReportsRepository

# AI Repositories
from core.repositories.user_ai_config_repository import UserAIConfigRepository
from core.repositories.user_ai_providers_repository import UserAIProvidersRepository
from core.repositories.user_ai_services_repository import UserAIServicesRepository
from core.repositories.user_ai_usage_repository import UserAIUsageRepository

# Still need concrete implementation for instantiation
from infra.db.connection_manager import db_manager

# ✅ PHASE 3 FIX: Import concrete repository implementations
from infra.db.repositories.admin_repository import AsyncpgAdminRepository
from infra.db.repositories.analytics_repository import AsyncpgAnalyticsRepository
from infra.db.repositories.channel_daily_repository import ChannelDailyRepository
from infra.db.repositories.channel_repository import AsyncpgChannelRepository
from infra.db.repositories.credit_repository import CreditRepository
from infra.db.repositories.edges_repository import AsyncpgEdgesRepository
from infra.db.repositories.marketplace_service_repository import (
    MarketplaceServiceRepository,
)
from infra.db.repositories.payment_repository import AsyncpgPaymentRepository
from infra.db.repositories.plan_repository import AsyncpgPlanRepository
from infra.db.repositories.post_metrics_repository import AsyncpgPostMetricsRepository
from infra.db.repositories.post_repository import AsyncpgPostRepository
from infra.db.repositories.schedule_repository import AsyncpgScheduleRepository
from infra.db.repositories.stats_raw_repository import AsyncpgStatsRawRepository
from infra.db.repositories.user_bot_repository_factory import UserBotRepositoryFactory
from infra.db.repositories.user_bot_service_repository_factory import (
    UserBotServiceRepositoryFactory,
)
from infra.db.repositories.user_repository import AsyncpgUserRepository

# ✅ PHASE 3 SCALING (Dec 19, 2025): Import scaling infrastructure
from infra.db.scaling import (
    SCALE_CONFIGS,
    CacheTier,
    PgBouncerConfig,
    PgBouncerPool,
    QueryCacheManager,
    ReadReplicaRouter,
    ReadReplicaRouterConfig,
)

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
    """Create asyncpg connection pool with environment-based configuration"""
    # Read pool configuration from environment
    pool_size = int(os.getenv("DB_POOL_SIZE", "10"))
    max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "20"))

    # Calculate min/max sizes for asyncpg
    min_size = max(1, pool_size // 2)  # Minimum 1, typically half of pool_size
    max_size = pool_size + max_overflow

    # Convert SQLAlchemy URL to asyncpg format if needed
    db_url = database_url
    if db_url.startswith("postgresql+asyncpg://"):
        db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")

    logger.info(f"📊 Creating asyncpg pool: min_size={min_size}, max_size={max_size}")

    pool = await asyncpg.create_pool(
        db_url,
        min_size=min_size,
        max_size=max_size,
        max_queries=50000,  # Recycle connections after 50k queries
        max_inactive_connection_lifetime=300,  # Close idle connections after 5 minutes
        command_timeout=60,  # Command timeout 60 seconds
    )
    if pool is None:
        raise RuntimeError("Failed to create asyncpg pool")
    return pool


async def _create_sqlalchemy_engine(
    database_url: str, pool_size: int = 10, max_overflow: int = 20
) -> AsyncEngine:
    """Create SQLAlchemy async engine with environment-based configuration"""
    # Read pool configuration from environment
    pool_size = int(os.getenv("DB_POOL_SIZE", "10"))
    max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    pool_timeout = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    pool_recycle = int(os.getenv("DB_POOL_RECYCLE", "3600"))
    pool_pre_ping = os.getenv("DB_POOL_PRE_PING", "true").lower() == "true"

    # Log the database URL for debugging (mask password)
    masked_url = database_url.replace(database_url.split("@")[0].split("://")[-1], "***")
    logger.info(f"🔧 Creating SQLAlchemy engine with URL: {masked_url}")
    logger.info(
        f"📊 Pool config: size={pool_size}, overflow={max_overflow}, timeout={pool_timeout}s, recycle={pool_recycle}s, pre_ping={pool_pre_ping}"
    )

    # Ensure we're using asyncpg driver
    if not database_url.startswith("postgresql+asyncpg://"):
        logger.warning("⚠️  DATABASE_URL does not start with 'postgresql+asyncpg://'")
        logger.warning(f"⚠️  Converting '{database_url.split('://')[0]}' to 'postgresql+asyncpg'")
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")

    return create_async_engine(
        database_url,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_timeout=pool_timeout,
        pool_recycle=pool_recycle,
        pool_pre_ping=pool_pre_ping,
        echo=False,  # Disable SQL echo in production
    )


async def _create_session_factory(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
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
# PHASE 3 SCALING INFRASTRUCTURE FACTORY FUNCTIONS
# ============================================================================


async def _create_pgbouncer_pool() -> PgBouncerPool | None:
    """
    Create PgBouncer connection pool for 100K+ user scalability.

    Enables connection multiplexing: 10,000+ client connections → 50-500 DB connections.
    Only activates if PGBOUNCER_ENABLED=true in environment.
    """
    pgbouncer_enabled = os.getenv("PGBOUNCER_ENABLED", "false").lower() == "true"

    if not pgbouncer_enabled:
        logger.info("⚙️  PgBouncer disabled (PGBOUNCER_ENABLED != 'true')")
        return None

    # Determine scale from environment or default to 'medium'
    scale = os.getenv("PGBOUNCER_SCALE", "medium")
    if scale not in SCALE_CONFIGS:
        logger.warning(f"⚠️  Unknown PGBOUNCER_SCALE '{scale}', using 'medium'")
        scale = "medium"

    # Get base config for scale
    base_config = SCALE_CONFIGS[scale]

    # Allow environment overrides
    config = PgBouncerConfig(
        primary_host=os.getenv("PGBOUNCER_HOST", base_config.primary_host),
        primary_port=int(os.getenv("PGBOUNCER_PORT", str(base_config.primary_port))),
        min_connections=int(os.getenv("PGBOUNCER_MIN_CONN", str(base_config.min_connections))),
        max_connections=int(os.getenv("PGBOUNCER_MAX_CONN", str(base_config.max_connections))),
        pool_mode=os.getenv("PGBOUNCER_POOL_MODE", base_config.pool_mode),
        connection_timeout=base_config.connection_timeout,
        command_timeout=base_config.command_timeout,
        user=os.getenv("POSTGRES_USER", ""),
        password=os.getenv("POSTGRES_PASSWORD", ""),
        database=os.getenv("POSTGRES_DB", ""),
    )

    pool = PgBouncerPool(config)
    await pool.initialize()

    logger.info(
        f"✅ PgBouncer pool initialized (scale={scale}, min={config.min_connections}, max={config.max_connections})"
    )
    return pool


async def _create_read_replica_router(
    primary_pool: asyncpg.Pool,
) -> ReadReplicaRouter | None:
    """
    Create read replica router for read/write splitting.

    Routes read queries to replicas (load distribution), writes to primary.
    Only activates if READ_REPLICA_HOSTS is set in environment.
    """
    from infra.db.scaling.read_replica_router import ReplicaConfig

    replica_hosts = os.getenv("READ_REPLICA_HOSTS", "")

    if not replica_hosts:
        logger.info("⚙️  Read replicas disabled (READ_REPLICA_HOSTS not set)")
        return None

    # Parse replica hosts (comma-separated: "replica1:5432,replica2:5432")
    replicas = []
    for host_port in replica_hosts.split(","):
        host_port = host_port.strip()
        if ":" in host_port:
            host, port = host_port.rsplit(":", 1)
            replicas.append(ReplicaConfig(host=host, port=int(port)))
        elif host_port:
            replicas.append(ReplicaConfig(host=host_port, port=5432))

    if not replicas:
        logger.warning("⚠️  READ_REPLICA_HOSTS set but no valid hosts found")
        return None

    # Build config using correct structure
    config = ReadReplicaRouterConfig(
        primary_host=os.getenv("POSTGRES_HOST", "localhost"),
        primary_port=int(os.getenv("POSTGRES_PORT", "5432")),
        replicas=replicas,
        user=os.getenv("POSTGRES_USER", ""),
        password=os.getenv("POSTGRES_PASSWORD", ""),
        database=os.getenv("POSTGRES_DB", ""),
        pool_size_per_replica=int(os.getenv("REPLICA_POOL_SIZE", "20")),
        health_check_interval=int(os.getenv("REPLICA_HEALTH_CHECK_INTERVAL", "30")),
    )

    router = ReadReplicaRouter(config, primary_pool)
    await router.initialize()

    logger.info(f"✅ Read replica router initialized ({len(replicas)} replicas)")
    return router


async def _create_query_cache_manager(redis_client) -> QueryCacheManager | None:
    """
    Create multi-tier query cache manager for 70-90% cache hit rates.

    Uses tiered TTLs: HOT (30s), WARM (2min), STANDARD (5min), COLD (15min), STATIC (1hr).
    Requires Redis client injection.
    """
    cache_enabled = os.getenv("QUERY_CACHE_ENABLED", "true").lower() == "true"

    if not cache_enabled:
        logger.info("⚙️  Query cache disabled (QUERY_CACHE_ENABLED != 'true')")
        return None

    if redis_client is None:
        logger.warning("⚠️  Query cache disabled - no Redis client available")
        return None

    # Parse tier TTL overrides from environment
    tier_ttls = {}
    for tier in CacheTier:
        env_key = f"CACHE_TTL_{tier.name}"
        if env_value := os.getenv(env_key):
            tier_ttls[tier] = int(env_value)

    cache_manager = QueryCacheManager(
        redis_client=redis_client,
        default_tier=CacheTier.STANDARD,
        tier_ttls=tier_ttls if tier_ttls else None,
        key_prefix=os.getenv("CACHE_KEY_PREFIX", "qcache"),
    )

    logger.info(f"✅ Query cache manager initialized (prefix={cache_manager.key_prefix})")
    return cache_manager


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
            "DATABASE_URL",
            "postgresql+asyncpg://analytic:change_me@localhost:5432/analytic_bot",
        )
    )

    # ============================================================================
    # DATABASE CONNECTIONS
    # ============================================================================

    database_manager = providers.Resource(_create_database_manager)

    asyncpg_pool = providers.Resource(_create_asyncpg_pool, database_url=database_url, pool_size=10)

    sqlalchemy_engine = providers.Resource(
        _create_sqlalchemy_engine,
        database_url=database_url,
        pool_size=10,
        max_overflow=20,
    )

    session_factory = providers.Resource(_create_session_factory, engine=sqlalchemy_engine)

    # Backwards-compatibility alias: some parts of the codebase expect
    # `async_session_maker` on the database container. Provide an alias
    # to the new `session_factory` provider to avoid AttributeError at
    # startup while keeping the clearer name.
    async_session_maker = session_factory

    # ============================================================================
    # PHASE 3 SCALING INFRASTRUCTURE (100K+ Users)
    # ============================================================================

    # PgBouncer Connection Pool - connection multiplexing for 10K+ concurrent connections
    pgbouncer_pool = providers.Resource(_create_pgbouncer_pool)

    # Read Replica Router - distributes reads across replicas, writes to primary
    read_replica_router = providers.Resource(
        _create_read_replica_router,
        primary_pool=asyncpg_pool,
    )

    # Query Cache Manager - multi-tier caching with 70-90% hit rates
    # Note: Requires Redis client from CacheContainer, wire via application startup
    # query_cache = providers.Resource(_create_query_cache_manager, redis_client=...)

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

    # User Bot Credentials Repository (for MTProto) - uses factory pattern with session maker
    user_bot_repo = providers.Singleton(
        UserBotRepositoryFactory,
        session_factory=async_session_maker,
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

    # User Bot Service Repository (for chat settings, banned words, etc.)
    user_bot_service_repo = providers.Singleton(
        UserBotServiceRepositoryFactory,
        session_factory=async_session_maker,
    )

    # Credit System Repository
    credit_repo = providers.Factory(
        CreditRepository,
        pool=asyncpg_pool,
    )

    # Marketplace Services Repository (for service subscriptions)
    marketplace_service_repo = providers.Factory(
        MarketplaceServiceRepository,
        pool=asyncpg_pool,
    )

    # ========================================================================
    # AI REPOSITORIES (for User AI system)
    # ========================================================================

    # User AI Config Repository (for AI tier, settings, preferences)
    user_ai_config_repo = providers.Factory(
        UserAIConfigRepository,
        pool=asyncpg_pool,
    )

    # User AI Usage Repository (for usage tracking and rate limiting)
    user_ai_usage_repo = providers.Factory(
        UserAIUsageRepository,
        pool=asyncpg_pool,
    )

    # User AI Services Repository (for marketplace AI services)
    user_ai_services_repo = providers.Factory(
        UserAIServicesRepository,
        pool=asyncpg_pool,
    )

    # User AI Providers Repository (for multi-provider API key management)
    user_ai_providers_repo = providers.Factory(
        UserAIProvidersRepository,
        pool=asyncpg_pool,
    )


# ============================================================================
# CLEANUP
# ============================================================================


async def cleanup_database_pool():
    """Cleanup database connections"""
    logger.info("Cleaning up database connections")
    # Cleanup will be handled by container lifecycle
