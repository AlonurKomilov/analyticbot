import asyncio
from collections.abc import Awaitable, Callable
from types import SimpleNamespace
from typing import Any

import punq
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

# DB pool turlari
from asyncpg.pool import Pool as AsyncPGPool
from punq import MissingDependencyError
from sqlalchemy.ext.asyncio import async_sessionmaker

from bot.config import settings as app_settings

# Repozitoriy va Servislar (type hint/resolve uchun)
from bot.database.repositories import (
    AnalyticsRepository,
    ChannelRepository,
    PlanRepository,
    SchedulerRepository,
    UserRepository,
)
from bot.services import (
    AnalyticsService,
    GuardService,
    SchedulerService,
    SubscriptionService,
)

# i18n fallback
from bot.utils.safe_i18n_core import SafeFluentRuntimeCore


# ---------- Null (no-op) obyektlar ----------
async def _noop(*args: Any, **kwargs: Any) -> None:
    return None


class _Null:
    """Har qanday atributga async no-op qaytaradi."""

    def __getattr__(self, name: str):
        return _noop


class _NullUserRepository(_Null):
    async def create_user(self, *args: Any, **kwargs: Any) -> None:
        return None

    async def get_locale(self, *args: Any, **kwargs: Any) -> str | None:
        return None

    async def get_user(self, *args: Any, **kwargs: Any):
        # .locale attr'i bo'lishi uchun oddiy obyekt
        return type("User", (), {"locale": None})()


class DependencyMiddleware(BaseMiddleware):
    """
    DI konteynerdan qaramliklarni `data` ga qo'shadi.
    DB yo'q bo'lsa Null obyektlar qo'yiladi.
    i18n middleware ishlamagan holatga fallback shim bor.
    """

    def __init__(self, container: punq.Container):
        self.container = container
        self._fallback_core = SafeFluentRuntimeCore(path="bot/locales/{locale}")
        # *har doim* non-empty bo'lsin
        self._fallback_locale: str = (
            getattr(app_settings, "DEFAULT_LOCALE", None) or "en"
        )

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        # --- DB session pool ---
        session_pool: Any | None = None
        try:
            session_pool = self.container.resolve(AsyncPGPool)
        except Exception:
            try:
                session_pool = self.container.resolve(async_sessionmaker)
            except Exception:
                session_pool = None

        # Agar coroutine bo'lsa (warmup o'tmagan) – await qilib olamiz
        if asyncio.iscoroutine(session_pool):
            try:
                session_pool = await session_pool  # type: ignore[func-returns-value]
            except Exception as e:
                import logging

                logger = logging.getLogger(__name__)
                logger.warning(
                    "DB pool resolve failed, using fallback repositories: %s", e
                )
                session_pool = None

        if session_pool is not None:
            data["session_pool"] = session_pool

        # --- Repozitoriylar ---
        if session_pool is not None:
            # Real repolarni resolve qilamiz
            for key, dep in [
                ("user_repo", UserRepository),
                ("plan_repo", PlanRepository),
                ("channel_repo", ChannelRepository),
                ("scheduler_repo", SchedulerRepository),
                ("analytics_repo", AnalyticsRepository),
            ]:
                try:
                    data[key] = self.container.resolve(dep)
                except MissingDependencyError:
                    continue
                except Exception:
                    continue
        else:
            # DB yo'q — Null repolar
            data["user_repo"] = _NullUserRepository()
            data["plan_repo"] = _Null()
            data["channel_repo"] = _Null()
            data["scheduler_repo"] = _Null()
            data["analytics_repo"] = _Null()

        # --- Servislar ---
        if session_pool is not None:
            for key, dep in [
                ("subscription_service", SubscriptionService),
                ("guard_service", GuardService),
                ("scheduler_service", SchedulerService),
                ("analytics_service", AnalyticsService),
            ]:
                try:
                    data[key] = self.container.resolve(dep)
                except MissingDependencyError:
                    continue
                except Exception:
                    continue
        else:
            data["subscription_service"] = _Null()
            data["guard_service"] = _Null()
            data["scheduler_service"] = _Null()
            data["analytics_service"] = _Null()

        # --- i18n fallback: agar i18n middleware context bermagan bo'lsa ---
        if not data.get("i18n"):
            core = self._fallback_core
            loc = self._fallback_locale  # hech qachon None emas

            def _safe_get(key: str, **kw: Any) -> str:
                try:
                    # lazy load locales (startup bo'lmagan holat uchun)
                    if not getattr(core, "locales", {}):
                        try:
                            core.locales.update(core.find_locales())
                        except Exception:
                            pass
                    return core.get(key, loc, **kw)
                except Exception:
                    return key

            data["i18n"] = SimpleNamespace(get=_safe_get, gettext=_safe_get)

        return await handler(event, data)
