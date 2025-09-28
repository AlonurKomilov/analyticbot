from __future__ import annotations

import inspect
import logging
from collections.abc import Callable
from typing import Any, TypeVar, cast

import punq
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from apps.bot.utils.punctuated import Singleton

logger = logging.getLogger(__name__)
try:
    from aiogram.client.bot import Bot as _AioBot
except Exception:
    from aiogram import Bot as _AioBot

from aiogram import Bot as _ClientBot
from aiogram import Dispatcher as _AioDispatcher
from apps.bot.config import Settings
from asyncpg.pool import Pool as AsyncPGPool
from infra.db.repositories.channel_repository import AsyncpgChannelRepository
from infra.db.repositories.user_repository import AsyncpgUserRepository
from sqlalchemy.ext.asyncio import async_sessionmaker

from infra.db.repositories.analytics_repository import AsyncpgAnalyticsRepository
from infra.db.repositories.plan_repository import AsyncpgPlanRepository
from infra.db.repositories.schedule_repository import AsyncpgScheduleRepository


def as_singleton(factory: Callable[[], object]) -> Callable[[], object]:
    _cache: dict[str, object] = {}

    def _wrapper() -> object:
        if "v" not in _cache:
            _cache["v"] = factory()
        return _cache["v"]

    return _wrapper


async def _get_asyncpg_pool():
    """Get asyncpg pool for repositories"""
    from apps.shared.di import container as shared_container

    try:
        container_instance = shared_container()
        return await container_instance.asyncpg_pool()
    except Exception as e:
        logger.warning(f"Failed to get asyncpg pool: {e}")
        return None


class Container(punq.Container):
    config = Singleton(Settings)
    # Remove the broken db_session that uses async init_db incorrectly

    # performance_analytics_service removed - functionality consolidated into AnalyticsFusionService

    def alerting_service(self):
        """Get alerting service instance"""
        from apps.bot.services.alerting_service import AlertingService

        return _resolve(AlertingService)

    def channel_management_service(self):
        """Get channel management service instance"""
        from apps.bot.services.channel_management_service import (
            ChannelManagementService,
        )

        return _resolve(ChannelManagementService)


container = Container()


def _build_bot() -> _AioBot | None:
    """Build bot instance, return None if BOT_TOKEN is missing (for API-only deployments)"""
    cfg: Settings = cast(Settings, container.config)
    token: str | None
    try:
        token = cfg.BOT_TOKEN.get_secret_value()
    except Exception:
        import os

        token = os.getenv("BOT_TOKEN")
    if not token or token == "replace_me":
        # For API-only deployments, return None instead of raising error
        return None
    return _AioBot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


def _build_dispatcher() -> _AioDispatcher:
    from aiogram.fsm.storage.memory import MemoryStorage

    return _AioDispatcher(storage=MemoryStorage())


_bot_singleton = as_singleton(_build_bot)
_dp_singleton = as_singleton(_build_dispatcher)
container.register(_AioBot, factory=_bot_singleton)
container.register(_ClientBot, factory=_bot_singleton)
container.register(_AioDispatcher, factory=_dp_singleton)


def _val(x: Any) -> Any:
    """punctuated.Singleton bo'lsa, instansiyani qaytaradi (cache bilan)."""
    return x() if callable(x) else x


def _pool_or_none() -> Any | None:
    """
    Get database pool using shared container.
    Returns asyncpg Pool or None if not available.
    """
    try:
        # Import here to avoid circular imports
        import asyncio

        # Try to get the pool synchronously if we're in an async context
        try:
            asyncio.get_running_loop()
            # If we're in an async context, we need to handle this differently
            # For now, return None and let the repository handle it gracefully
            logger.info("Async context detected - repositories should use proper async DI")
            return None
        except RuntimeError:
            # No running loop, we're in sync context
            return None
    except Exception as e:
        from apps.bot.utils.error_handler import ErrorContext, ErrorHandler

        context = ErrorContext().add("operation", "get_database_pool")
        ErrorHandler.handle_database_error(e, context)
        return None


def _make_repo(RepoCls: type) -> object:
    """
    Moslashuvchan repo yaratuvchi: pool/redis positional yoki turli keywordlar.
    """
    pool = _pool_or_none()
    if hasattr(pool, "__await__"):
        pool = None
    try:
        return RepoCls(pool)
    except TypeError:
        pass
    for kw in (
        "session_pool",
        "session",
        "pool",
        "db",
        "database",
        "redis",
        "redis_client",
    ):
        try:
            return RepoCls(**{kw: pool})
        except TypeError:
            continue
    return RepoCls()


def _make_service(ServiceCls: type) -> object:
    """
    Servislarni __init__ signaturasiga moslab yig'ish.
    Bot va repos nomlarini introspeksiya qilamiz.
    """
    sig = inspect.signature(ServiceCls.__init__)
    names = set(sig.parameters.keys())
    kwargs: dict[str, Any] = {}
    if "bot" in names:
        bot = container.resolve(_AioBot)
        if bot is not None:
            kwargs["bot"] = bot
        # If bot is None (API-only deployment), skip adding it - service should handle this
    if {"channel_repository", "channel_repo", "repository"} & names:
        repo = container.resolve(AsyncpgChannelRepository)
        for cand in ("channel_repository", "channel_repo", "repository"):
            if cand in names:
                kwargs[cand] = repo
                break
    if {"scheduler_repository", "scheduler_repo"} & names:
        repo = container.resolve(AsyncpgScheduleRepository)
        for cand in ("scheduler_repository", "scheduler_repo"):
            if cand in names:
                kwargs[cand] = repo
                break
    if {"user_repository", "user_repo"} & names:
        repo = container.resolve(AsyncpgUserRepository)
        for cand in ("user_repository", "user_repo"):
            if cand in names:
                kwargs[cand] = repo
                break
    if "analytics_repository" in names:
        kwargs["analytics_repository"] = container.resolve(AsyncpgAnalyticsRepository)
    if "plan_repository" in names:
        kwargs["plan_repository"] = container.resolve(AsyncpgPlanRepository)
    try:
        return ServiceCls(**kwargs)
    except TypeError:
        return ServiceCls()


container.register(AsyncPGPool, factory=lambda: cast(AsyncPGPool, _pool_or_none()))
container.register(async_sessionmaker, factory=lambda: cast(async_sessionmaker, _pool_or_none()))
container.register(
    AsyncpgUserRepository,
    factory=as_singleton(lambda: _make_repo(AsyncpgUserRepository)),
)
container.register(
    AsyncpgPlanRepository,
    factory=as_singleton(lambda: _make_repo(AsyncpgPlanRepository)),
)
container.register(
    AsyncpgChannelRepository,
    factory=as_singleton(lambda: _make_repo(AsyncpgChannelRepository)),
)
container.register(
    AsyncpgScheduleRepository,
    factory=as_singleton(lambda: _make_repo(AsyncpgScheduleRepository)),
)
container.register(
    AsyncpgAnalyticsRepository,
    factory=as_singleton(lambda: _make_repo(AsyncpgAnalyticsRepository)),
)


def _register_services():
    """Register services with local imports to avoid circular dependencies"""
    try:
        # Import each service individually to better handle any import issues
        from apps.bot.services.guard_service import GuardService

        container.register(GuardService, factory=as_singleton(lambda: _make_service(GuardService)))

        from apps.bot.services.subscription_service import SubscriptionService

        container.register(
            SubscriptionService,
            factory=as_singleton(lambda: _make_service(SubscriptionService)),
        )

        from apps.bot.services.scheduler_service import SchedulerService

        container.register(
            SchedulerService,
            factory=as_singleton(lambda: _make_service(SchedulerService)),
        )

        from apps.bot.services.analytics_service import AnalyticsService

        container.register(
            AnalyticsService,
            factory=as_singleton(lambda: _make_service(AnalyticsService)),
        )

        # PerformanceAnalyticsService removed - functionality consolidated into AnalyticsFusionService

        from apps.bot.services.alerting_service import AlertingService

        container.register(
            AlertingService,
            factory=as_singleton(lambda: _make_service(AlertingService)),
        )

        from apps.bot.services.channel_management_service import (
            ChannelManagementService,
        )

        container.register(
            ChannelManagementService,
            factory=as_singleton(lambda: _make_service(ChannelManagementService)),
        )
    except Exception as e:
        logger.warning(f"Could not register some services: {e}")


# Register services with local imports
_register_services()
_T = TypeVar("_T")


def _resolve(key: type[_T]) -> _T:
    return cast(_T, container.resolve(key))


OptimizedContainer = Container


class MLCompatibilityLayer:
    """Compatibility layer for ML service tests"""

    @property
    def prediction_service(self):
        """ML service compatibility - returns None if not available"""
        try:
            from apps.bot.services.ml.predictive_engine import PredictiveAnalyticsEngine

            return container.resolve(PredictiveAnalyticsEngine)
        except (ImportError, Exception):
            return None

    @property
    def content_optimizer(self):
        """ML service compatibility - returns None if not available"""
        try:
            from apps.bot.services.ml.content_optimizer import ContentOptimizer

            return container.resolve(ContentOptimizer)
        except (ImportError, Exception):
            return None

    @property
    def churn_predictor(self):
        """ML service compatibility - returns None if not available"""
        try:
            from apps.bot.services.ml.churn_predictor import ChurnPredictor

            return container.resolve(ChurnPredictor)
        except (ImportError, Exception):
            return None

    @property
    def engagement_analyzer(self):
        """ML service compatibility - returns None if not available"""
        try:
            from apps.bot.services.ml.engagement_analyzer import EngagementAnalyzer

            return container.resolve(EngagementAnalyzer)
        except (ImportError, Exception):
            return None


class OptimizedContainerCompat(Container):
    """Optimized container compatibility layer"""

    def __init__(self):
        super().__init__()
        self._ml_compat = MLCompatibilityLayer()

    def __getattr__(self, name):
        if hasattr(self._ml_compat, name):
            return getattr(self._ml_compat, name)
        return super().__getattribute__(name)


OptimizedContainer = OptimizedContainerCompat
