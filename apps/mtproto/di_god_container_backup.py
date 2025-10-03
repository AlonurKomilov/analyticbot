import logging
from typing import Any

from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject

from apps.mtproto.config import MTProtoSettings
from apps.mtproto.health_http import HealthCheckServer
from apps.mtproto.metrics import MTProtoMetrics, initialize_metrics
from core.ports.tg_client import TGClient
from infra.common.faults import FaultInjector, get_global_injector
from infra.common.ratelimit import RateLimitManager
from infra.db.repositories.channel_daily_repository import ChannelDailyRepository
from infra.db.repositories.channel_repository import ChannelRepository
from infra.db.repositories.post_metrics_repository import PostMetricsRepository
from infra.db.repositories.post_repository import PostRepository
from infra.db.repositories.stats_raw_repository import StatsRawRepository
from infra.obs.otel import MTProtoTracer, initialize_global_tracer

# Phase 4.6: Import scaling components
from infra.tg.account_pool import AccountPool
from infra.tg.dc_router import DCRouter
from infra.tg.parsers import normalize_message, normalize_update
from infra.tg.proxy_pool import ProxyPool
from infra.tg.telethon_client import TelethonTGClient

logger = logging.getLogger(__name__)


class ScalingContainer:
    """Container for Phase 4.6 scaling components."""

    def __init__(self, settings: MTProtoSettings):
        self.settings = settings

        # Initialize scaling components based on feature flags
        self.account_pool: AccountPool | None = None
        self.proxy_pool: ProxyPool | None = None
        self.rate_limiter: RateLimitManager | None = None
        self.dc_router: DCRouter = DCRouter()
        self.metrics: MTProtoMetrics = MTProtoMetrics(enabled=False)
        self.tracer: MTProtoTracer = MTProtoTracer(enabled=False)
        self.health_server: HealthCheckServer | None = None
        self.fault_injector: FaultInjector = get_global_injector()

        self._initialized = False

    async def initialize(self) -> None:
        """Initialize scaling components based on configuration."""
        if self._initialized:
            return

        try:
            # Initialize metrics if enabled
            if self.settings.OBS_PROMETHEUS_ENABLED:
                self.metrics = initialize_metrics(enabled=True, port=self.settings.PROMETHEUS_PORT)
                logger.info("Prometheus metrics initialized")

            # Initialize tracing if enabled
            if self.settings.OBS_OTEL_ENABLED and self.settings.OTEL_EXPORTER_OTLP_ENDPOINT:
                self.tracer = initialize_global_tracer(
                    endpoint=self.settings.OTEL_EXPORTER_OTLP_ENDPOINT,
                    sampling_ratio=self.settings.OTEL_SAMPLER_RATIO,
                    service_name="mtproto",
                )
                logger.info("OpenTelemetry tracing initialized")

            # Initialize rate limiting
            self.rate_limiter = RateLimitManager(
                global_rps=self.settings.MTPROTO_GLOBAL_RPS,
                account_rps=self.settings.MTPROTO_RPS_PER_ACCOUNT,
                max_concurrency_per_account=self.settings.MTPROTO_MAX_CONCURRENCY_PER_ACCOUNT,
            )
            logger.info("Rate limiting initialized")

            # Initialize proxy pool if enabled
            if self.settings.MTPROTO_PROXY_ENABLED and self.settings.MTPROTO_PROXIES:
                self.proxy_pool = ProxyPool(
                    proxy_urls=self.settings.MTPROTO_PROXIES,
                    rotation_interval=self.settings.MTPROTO_PROXY_ROTATION_SEC,
                    fail_score_limit=self.settings.MTPROTO_PROXY_FAIL_SCORE_LIMIT,
                )
                await self.proxy_pool.start()
                logger.info(
                    f"Proxy pool initialized with {len(self.settings.MTPROTO_PROXIES)} proxies"
                )

            # Initialize account pool if enabled
            if self.settings.MTPROTO_POOL_ENABLED and self.settings.MTPROTO_ACCOUNTS:
                # Create factory function for TGClient
                def tg_client_factory(session_name: str) -> TGClient:
                    client_settings = self.settings.copy()
                    client_settings.TELEGRAM_SESSION_NAME = session_name
                    return TelethonTGClient(client_settings)  # type: ignore[return-value]

                self.account_pool = AccountPool(
                    factory=tg_client_factory,
                    accounts=self.settings.MTPROTO_ACCOUNTS,
                    rps_per_account=self.settings.MTPROTO_RPS_PER_ACCOUNT,
                    max_concurrency_per_account=self.settings.MTPROTO_MAX_CONCURRENCY_PER_ACCOUNT,
                )
                await self.account_pool.start()
                logger.info(
                    f"Account pool initialized with {len(self.settings.MTPROTO_ACCOUNTS)} accounts"
                )

            # Initialize health check server
            self.health_server = HealthCheckServer(
                bind_address=self.settings.HEALTH_BIND,
                account_pool=self.account_pool,
                proxy_pool=self.proxy_pool,
                rate_limiter=self.rate_limiter,
            )
            await self.health_server.start()
            logger.info(f"Health check server started on {self.settings.HEALTH_BIND}")

            self._initialized = True
            logger.info("All scaling components initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize scaling components: {e}")
            raise

    async def shutdown(self) -> None:
        """Gracefully shutdown scaling components."""
        logger.info("Shutting down scaling components...")

        try:
            # Stop health server
            if self.health_server:
                await self.health_server.stop()

            # Stop proxy pool
            if self.proxy_pool:
                await self.proxy_pool.stop()

            # Stop account pool (wait for graceful shutdown)
            if self.account_pool:
                await self.account_pool.stop()

            logger.info("Scaling components shutdown complete")

        except Exception as e:
            logger.error(f"Error during scaling components shutdown: {e}")

    def get_client(self) -> TGClient:
        """Get a client instance (pooled if available, otherwise single)."""
        if self.account_pool and self.account_pool.is_ready:
            # Return a wrapper that uses the pool
            if self.rate_limiter is None:
                raise ValueError("RateLimitManager is required but not available")
            return PooledClientWrapper(
                self.account_pool, self.rate_limiter, self.metrics, self.dc_router
            )
        else:
            # Fallback to single client
            return TelethonTGClient(self.settings)  # type: ignore[return-value]

    def get_stats(self) -> dict:
        """Get stats from all scaling components."""
        stats = {
            "initialized": self._initialized,
            "feature_flags": {
                "pool_enabled": self.settings.MTPROTO_POOL_ENABLED,
                "proxy_enabled": self.settings.MTPROTO_PROXY_ENABLED,
                "prometheus_enabled": self.settings.OBS_PROMETHEUS_ENABLED,
                "otel_enabled": self.settings.OBS_OTEL_ENABLED,
            },
        }

        if self.account_pool:
            stats["account_pool"] = self.account_pool.get_stats()

        if self.proxy_pool:
            stats["proxy_pool"] = self.proxy_pool.get_stats()

        if self.rate_limiter:
            stats["rate_limiter"] = self.rate_limiter.get_all_stats()

        if self.dc_router:
            stats["dc_router"] = self.dc_router.get_cache_stats()

        if self.fault_injector:
            stats["fault_injection"] = self.fault_injector.get_stats()

        return stats


class PooledClientWrapper(TGClient):
    """Wrapper that provides TGClient interface using AccountPool."""

    def __init__(
        self,
        pool: AccountPool,
        rate_limiter: RateLimitManager,
        metrics: MTProtoMetrics,
        dc_router: DCRouter,
    ):
        self.pool = pool
        self.rate_limiter = rate_limiter
        self.metrics = metrics
        self.dc_router = dc_router

    async def start(self) -> None:
        """Pool is already started."""

    async def stop(self) -> None:
        """Pool shutdown is handled by ScalingContainer."""

    async def is_connected(self) -> bool:
        """Check if pool has healthy accounts."""
        return self.pool.is_ready

    async def iter_history(
        self, peer: Any, *, offset_id: int = 0, limit: int = 200
    ) -> Any:
        """Iterate through message history using pooled client."""
        lease = await self.pool.lease()
        async with lease as client:
            async for message in client.iter_history(peer, offset_id=offset_id, limit=limit):
                yield message

    async def get_broadcast_stats(self, channel: Any) -> Any:
        """Get broadcast stats using pooled client."""
        lease = await self.pool.lease()
        async with lease as client:
            return await client.get_broadcast_stats(channel)

    async def get_megagroup_stats(self, chat: Any) -> Any:
        """Get megagroup stats using pooled client."""
        lease = await self.pool.lease()
        async with lease as client:
            return await client.get_megagroup_stats(chat)

    async def load_async_graph(self, token: str) -> Any:
        """Load async graph using pooled client."""
        lease = await self.pool.lease()
        async with lease as client:
            return await client.load_async_graph(token)

    async def get_full_channel(self, peer: Any) -> Any:
        """Get full channel using pooled client."""
        lease = await self.pool.lease()
        async with lease as client:
            return await client.get_full_channel(peer)

    async def iter_updates(self) -> Any:
        """Iterate updates using pooled client."""
        lease = await self.pool.lease()
        async with lease as client:
            async for update in client.iter_updates():
                yield update

    async def get_me(self) -> Any:
        """Get current user using pooled client."""
        lease = await self.pool.lease()
        async with lease as client:
            return await client.get_me()

    async def disconnect(self) -> None:
        """Disconnect pooled clients."""
        await self.stop()

    async def get_entity(self, entity):
        """Get entity using pooled client."""
        lease = await self.pool.lease()
        async with lease as client:
            return await client.get_entity(entity)

    async def iter_messages(self, entity, limit=None, offset_date=None, reverse=False):
        """Iterate messages using pooled client with DC routing."""
        lease = await self.pool.lease()
        async with lease as client:
            # Use DC router for better reliability
            return await self.dc_router.run_with_dc_retry(
                client,
                client.iter_messages,
                peer_id=str(entity),
                request_type="messages",
                entity=entity,
                limit=limit,
                offset_date=offset_date,
                reverse=reverse,
            )

    # Add other TGClient methods as needed...


class RepositoryContainer:
    """Container for repository instances with shared database connection."""

    def __init__(self, db_pool: Any):
        """Initialize repositories with database connection pool.

        Args:
            db_pool: Database connection pool
        """
        self.channel_repo = ChannelRepository(db_pool)
        self.post_repo = PostRepository(db_pool)
        self.metrics_repo = PostMetricsRepository(db_pool)
        # Phase 4.3: Add stats repositories
        self.channel_daily_repo = ChannelDailyRepository(db_pool)
        self.stats_raw_repo = StatsRawRepository(db_pool)

        # Add parsers as utility functions
        self.parsers = type(
            "Parsers",
            (),
            {
                "normalize_message": staticmethod(normalize_message),
                "normalize_update": staticmethod(normalize_update),
            },
        )()


class MTProtoContainer(containers.DeclarativeContainer):
    """Dependency injection container for MTProto application.

    Provides centralized configuration and dependency management
    following Clean Architecture principles with repository integration.
    """

    # Configuration
    config = providers.Configuration()

    # Settings provider
    settings = providers.Singleton(MTProtoSettings)

    # TGClient implementation provider
    tg_client = providers.Factory(TelethonTGClient, settings=settings)

    # Phase 4.6: Scaling components container
    scaling_container = providers.Singleton(ScalingContainer, settings=settings)


# Container instance
container = MTProtoContainer()


def configure_container(settings: MTProtoSettings) -> None:
    """Configure the DI container with application settings."""
    container.config.from_dict(settings.dict())


@inject
def get_tg_client(tg_client: TGClient = Provide[MTProtoContainer.tg_client]) -> TGClient:
    """Get configured TGClient instance."""
    return tg_client


@inject
def get_scaling_container(
    scaling_container: ScalingContainer = Provide[MTProtoContainer.scaling_container],
) -> ScalingContainer:
    """Get scaling container instance."""
    return scaling_container


def create_tg_client(settings: MTProtoSettings) -> TGClient:
    """Create TGClient instance directly (for tasks)."""
    return TelethonTGClient(settings)  # type: ignore[return-value]


def create_scalable_client(settings: MTProtoSettings) -> TGClient:
    """Create scalable TGClient using pools if enabled."""
    scaling_container = ScalingContainer(settings)
    return scaling_container.get_client()


@inject
def get_settings(settings: MTProtoSettings = Provide[MTProtoContainer.settings]) -> MTProtoSettings:
    """Get application settings."""
    return settings


async def get_repositories() -> RepositoryContainer:
    """Get repository container with database connection.

    This function establishes database connectivity and creates
    repository instances for use in collectors and tasks.

    Returns:
        RepositoryContainer with initialized repositories
    """
    # Use environment variables directly to avoid settings conflicts
    import os

    import asyncpg

    # Load from environment
    database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://analytic:change_me@localhost:5433/analytic_bot")
    
    # Convert database URL for asyncpg
    if database_url.startswith("postgresql+asyncpg://"):
        db_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    else:
        db_url = database_url

    try:
        db_pool = await asyncpg.create_pool(
            db_url,
            min_size=int(os.getenv("DB_POOL_SIZE", "10")),
            max_size=int(os.getenv("DB_MAX_OVERFLOW", "20")),
            command_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
        )
        return RepositoryContainer(db_pool)
    except Exception as e:
        # Fallback for development/testing
        import logging

        logging.warning(f"Could not create database pool: {e}, using mock repositories")

        # Create mock pool
        mock_pool = type("MockPool", (), {})()
        return RepositoryContainer(mock_pool)


def create_stats_loader(tg_client: TGClient, repos: RepositoryContainer, settings: MTProtoSettings):
    """Create stats loader instance with dependencies."""
    from apps.mtproto.tasks.stats_loader import StatsLoaderTask

    return StatsLoaderTask()


async def initialize_application(settings: MTProtoSettings) -> ScalingContainer:
    """
    Initialize complete MTProto application with scaling components.

    This is the main initialization function for Phase 4.6 applications.
    """
    # Configure DI container
    configure_container(settings)

    # Create and initialize scaling container
    scaling_container = ScalingContainer(settings)
    await scaling_container.initialize()

    logger.info("MTProto application initialized successfully")
    return scaling_container


async def shutdown_application(scaling_container: ScalingContainer) -> None:
    """Gracefully shutdown MTProto application."""
    await scaling_container.shutdown()
    logger.info("MTProto application shutdown complete")


# Context manager for application lifecycle
class MTProtoApplication:
    """Context manager for MTProto application lifecycle."""

    def __init__(self, settings: MTProtoSettings):
        self.settings = settings
        self.scaling_container: ScalingContainer | None = None

    async def __aenter__(self) -> ScalingContainer:
        self.scaling_container = await initialize_application(self.settings)
        return self.scaling_container

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.scaling_container:
            await shutdown_application(self.scaling_container)


# Convenience function for task scripts
async def get_scalable_components(
    settings: MTProtoSettings,
) -> tuple[TGClient, RepositoryContainer, ScalingContainer]:
    """
    Get scalable components for use in task scripts.

    Returns:
        Tuple of (tg_client, repositories, scaling_container)
    """
    repos = await get_repositories()
    scaling_container = ScalingContainer(settings)
    await scaling_container.initialize()

    # Get scalable client (pooled if available)
    tg_client = scaling_container.get_client()

    return tg_client, repos, scaling_container
