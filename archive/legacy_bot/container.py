from __future__ import annotations

import inspect
import logging
from collections.abc import Callable
from typing import Any, TypeVar, cast

import punq
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from bot.utils.punctuated import Singleton

# Logging setup
logger = logging.getLogger(__name__)

# Aiogram identity (v3)
try:
    from aiogram.client.bot import Bot as _AioBot
except Exception:  # pragma: no cover
    from aiogram import Bot as _AioBot

from aiogram import Bot as _ClientBot
from aiogram import Dispatcher as _AioDispatcher
from asyncpg.pool import Pool as AsyncPGPool

# Project config & DB
from bot.config import Settings

# Repositories
from bot.database.repositories.analytics_repository import AnalyticsRepository
from bot.database.repositories.channel_repository import ChannelRepository
from bot.database.repositories.plan_repository import PlanRepository
from bot.database.repositories.scheduler_repository import SchedulerRepository
from bot.database.repositories.user_repository import UserRepository
from bot.database.sqlite_engine import init_db

# DB turlari
from sqlalchemy.ext.asyncio import async_sessionmaker


# ---------- helper: lazy singleton factory ----------
def as_singleton(factory: Callable[[], object]) -> Callable[[], object]:
    _cache: dict[str, object] = {}

    def _wrapper() -> object:
        if "v" not in _cache:
            _cache["v"] = factory()
        return _cache["v"]

    return _wrapper


class Container(punq.Container):
    # Settings (punctuated)
    config = Singleton(Settings)

    # DB pool (punctuated) – create_pool async bo‘lishi mumkin
    db_session = Singleton(init_db)


# Global container
container = Container()


# ---------- Aiogram Bot/Dispatcher ----------
def _build_bot() -> _AioBot:
    cfg: Settings = cast(Settings, container.config)
    token: str | None
    try:
        token = cfg.BOT_TOKEN.get_secret_value()
    except Exception:
        import os

        token = os.getenv("BOT_TOKEN")
    if not token or token == "replace_me":
        raise RuntimeError("BOT_TOKEN is missing or placeholder")
    return _AioBot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


def _build_dispatcher() -> _AioDispatcher:
    from aiogram.fsm.storage.memory import MemoryStorage

    return _AioDispatcher(storage=MemoryStorage())


_bot_singleton = as_singleton(_build_bot)
_dp_singleton = as_singleton(_build_dispatcher)

container.register(_AioBot, factory=_bot_singleton)
container.register(_ClientBot, factory=_bot_singleton)
container.register(_AioDispatcher, factory=_dp_singleton)


# ---------- Helperlar ----------
def _val(x: Any) -> Any:
    """punctuated.Singleton bo'lsa, instansiyani qaytaradi (cache bilan)."""
    return x() if callable(x) else x


def _pool_or_none() -> Any | None:
    """
    Get database pool with improved error handling.
    Returns DB (asyncpg Pool or async_sessionmaker) or None if not available.
    """
    try:
        pool_value = _val(container.db_session)

        # If it's a coroutine and warmup hasn't happened, return None
        if hasattr(pool_value, "__await__"):
            logger.warning("Database pool not initialized (warmup required)")
            return None

        return pool_value
    except Exception as e:
        from bot.utils.error_handler import ErrorContext, ErrorHandler

        context = ErrorContext().add("operation", "get_database_pool")
        ErrorHandler.handle_database_error(e, context)
        return None


def _make_repo(RepoCls: type) -> object:
    """
    Moslashuvchan repo yaratuvchi: pool/redis positional yoki turli keywordlar.
    """
    pool = _pool_or_none()
    # Agar warmup bo'lmagan bo'lsa va coroutine kelsa – None uzatamiz
    if hasattr(pool, "__await__"):
        pool = None

    # 1) Pozitsion (Repository(pool))
    try:
        return RepoCls(pool)
    except TypeError:
        pass

    # 2) Muqobil keyword nomlar
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

    # 3) Umuman argsiz
    return RepoCls()


def _make_service(ServiceCls: type) -> object:
    """
    Servislarni __init__ signaturasiga moslab yig'ish.
    Bot va repos nomlarini introspeksiya qilamiz.
    """
    sig = inspect.signature(ServiceCls.__init__)
    names = set(sig.parameters.keys())

    kwargs: dict[str, Any] = {}

    # Bot
    if "bot" in names:
        kwargs["bot"] = container.resolve(_AioBot)

    # Repos
    if {"channel_repository", "channel_repo", "repository"} & names:
        repo = container.resolve(ChannelRepository)
        for cand in ("channel_repository", "channel_repo", "repository"):
            if cand in names:
                kwargs[cand] = repo
                break

    if {"scheduler_repository", "scheduler_repo"} & names:
        repo = container.resolve(SchedulerRepository)
        for cand in ("scheduler_repository", "scheduler_repo"):
            if cand in names:
                kwargs[cand] = repo
                break

    if {"user_repository", "user_repo"} & names:
        repo = container.resolve(UserRepository)
        for cand in ("user_repository", "user_repo"):
            if cand in names:
                kwargs[cand] = repo
                break

    if "analytics_repository" in names:
        kwargs["analytics_repository"] = container.resolve(AnalyticsRepository)

    # Qo'shimcha ehtimoliy paramlar (agar bo'lsa)
    if "plan_repository" in names:
        kwargs["plan_repository"] = container.resolve(PlanRepository)

    # Chaqaramiz
    try:
        return ServiceCls(**kwargs)
    except TypeError:
        # Agar baribir nomi boshqa bo'lsa, argumentsiz urinamiz
        return ServiceCls()


# ---------- DB aliaslar (DependencyMiddleware uchun) ----------
container.register(AsyncPGPool, factory=lambda: cast(AsyncPGPool, _pool_or_none()))
container.register(async_sessionmaker, factory=lambda: cast(async_sessionmaker, _pool_or_none()))

# ---------- Repository factory'lari (punq) ----------
container.register(UserRepository, factory=as_singleton(lambda: _make_repo(UserRepository)))
container.register(PlanRepository, factory=as_singleton(lambda: _make_repo(PlanRepository)))
container.register(ChannelRepository, factory=as_singleton(lambda: _make_repo(ChannelRepository)))
container.register(
    SchedulerRepository, factory=as_singleton(lambda: _make_repo(SchedulerRepository))
)
container.register(
    AnalyticsRepository, factory=as_singleton(lambda: _make_repo(AnalyticsRepository))
)

# ---------- Service factory'lari (punq) ----------
try:
    from bot.services.analytics_service import AnalyticsService
    from bot.services.guard_service import GuardService
    from bot.services.scheduler_service import SchedulerService
    from bot.services.subscription_service import SubscriptionService

    container.register(GuardService, factory=as_singleton(lambda: _make_service(GuardService)))
    container.register(
        SubscriptionService,
        factory=as_singleton(lambda: _make_service(SubscriptionService)),
    )
    container.register(
        SchedulerService, factory=as_singleton(lambda: _make_service(SchedulerService))
    )
    container.register(
        AnalyticsService, factory=as_singleton(lambda: _make_service(AnalyticsService))
    )
except Exception:
    # optional import failures allowed
    pass


# -------- Typed helper (Pylance uchun) --------
_T = TypeVar("_T")


def _resolve(key: type[_T]) -> _T:
    return cast(_T, container.resolve(key))


# ========================================================================
# COMPATIBILITY LAYER
# ========================================================================

# Backward compatibility alias for tests that expect OptimizedContainer
OptimizedContainer = Container


# For tests that expect ML service providers
class MLCompatibilityLayer:
    """Compatibility layer for ML service tests"""

    @property
    def prediction_service(self):
        """ML service compatibility - returns None if not available"""
        try:
            from bot.services.ml.prediction_service import PredictionService

            return container.resolve(PredictionService)
        except (ImportError, Exception):
            return None

    @property
    def content_optimizer(self):
        """ML service compatibility - returns None if not available"""
        try:
            from bot.services.ml.content_optimizer import ContentOptimizer

            return container.resolve(ContentOptimizer)
        except (ImportError, Exception):
            return None

    @property
    def churn_predictor(self):
        """ML service compatibility - returns None if not available"""
        try:
            from bot.services.ml.churn_predictor import ChurnPredictor

            return container.resolve(ChurnPredictor)
        except (ImportError, Exception):
            return None

    @property
    def engagement_analyzer(self):
        """ML service compatibility - returns None if not available"""
        try:
            from bot.services.ml.engagement_analyzer import EngagementAnalyzer

            return container.resolve(EngagementAnalyzer)
        except (ImportError, Exception):
            return None


# Create a mixed container that has both legacy functionality and ML compatibility
class OptimizedContainerCompat(Container):
    """Optimized container compatibility layer"""

    def __init__(self):
        super().__init__()
        self._ml_compat = MLCompatibilityLayer()

    def __getattr__(self, name):
        # Check for ML service compatibility
        if hasattr(self._ml_compat, name):
            return getattr(self._ml_compat, name)

        # Fall back to parent container
        return super().__getattribute__(name)


# Replace the OptimizedContainer alias with the compatibility version
OptimizedContainer = OptimizedContainerCompat
