from __future__ import annotations

from typing import TypeVar, Type, cast, Optional, Callable, Any
import inspect
import logging

import punq
from bot.utils.punctuated import Singleton

from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# Logging setup
logger = logging.getLogger(__name__)

# Aiogram identity (v3)
try:
    from aiogram.client.bot import Bot as _AioBot
except Exception:  # pragma: no cover
    from aiogram import Bot as _AioBot

from aiogram import Bot as _ClientBot
from aiogram import Dispatcher as _AioDispatcher

# DB turlari
from sqlalchemy.ext.asyncio import async_sessionmaker
from asyncpg.pool import Pool as AsyncPGPool

# Project config & DB
from bot.config import Settings
from bot.database.db import create_pool

# Repositories
from bot.database.repositories.analytics_repository import AnalyticsRepository
from bot.database.repositories.channel_repository import ChannelRepository
from bot.database.repositories.plan_repository import PlanRepository
from bot.database.repositories.scheduler_repository import SchedulerRepository
from bot.database.repositories.user_repository import UserRepository


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
    db_session = Singleton(create_pool)


# Global container
container = Container()


# ---------- Aiogram Bot/Dispatcher ----------
def _build_bot() -> _AioBot:
    cfg: Settings = cast(Settings, container.config)
    token: Optional[str]
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


def _pool_or_none() -> Optional[Any]:
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
        from bot.utils.error_handler import ErrorHandler, ErrorContext
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
container.register(
    async_sessionmaker, factory=lambda: cast(async_sessionmaker, _pool_or_none())
)

# ---------- Repository factory'lari (punq) ----------
container.register(
    UserRepository, factory=as_singleton(lambda: _make_repo(UserRepository))
)
container.register(
    PlanRepository, factory=as_singleton(lambda: _make_repo(PlanRepository))
)
container.register(
    ChannelRepository, factory=as_singleton(lambda: _make_repo(ChannelRepository))
)
container.register(
    SchedulerRepository, factory=as_singleton(lambda: _make_repo(SchedulerRepository))
)
container.register(
    AnalyticsRepository, factory=as_singleton(lambda: _make_repo(AnalyticsRepository))
)

# ---------- Service factory'lari (punq) ----------
try:
    from bot.services.guard_service import GuardService
    from bot.services.subscription_service import SubscriptionService
    from bot.services.scheduler_service import SchedulerService
    from bot.services.analytics_service import AnalyticsService

    container.register(
        GuardService, factory=as_singleton(lambda: _make_service(GuardService))
    )
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


def _resolve(key: Type[_T]) -> _T:
    return cast(_T, container.resolve(key))
