import asyncio
from collections.abc import Awaitable, Callable
from types import SimpleNamespace
from typing import Any

# ✅ UNIFIED DI: Using dependency-injector for clean architecture
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from asyncpg.pool import Pool as AsyncPGPool
from sqlalchemy.ext.asyncio import async_sessionmaker

from apps.bot.config import settings as app_settings
from apps.bot.utils.safe_i18n_core import SafeFluentRuntimeCore

# ARCHIVED 2025-10-16: AnalyticsService moved to core.services.bot.analytics
# Use AnalyticsCoordinator or specific analytics services from core layer
# New scheduling services (Clean Architecture)

# Use repository factory instead of direct infra imports
# from infra.db.repositories import AsyncpgAnalyticsRepository as AnalyticsRepository
# from infra.db.repositories import AsyncpgChannelRepository as ChannelRepository
# from infra.db.repositories import AsyncpgPlanRepository as PlanRepository
# from infra.db.repositories import AsyncpgScheduleRepository as SchedulerRepository
# from infra.db.repositories import AsyncpgUserRepository as UserRepository


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
        return type("User", (), {"locale": None})()


class DependencyMiddleware(BaseMiddleware):
    """
    DI konteynerdan qaramliklarni `data` ga qo'shadi.
    DB yo'q bo'lsa Null obyektlar qo'yiladi.
    i18n middleware ishlamagan holatga fallback shim bor.
    """

    def __init__(self, container: Any = None):
        """Accept any container type for compatibility"""
        self.container: Any = container
        self._fallback_core = SafeFluentRuntimeCore(path="bot/locales/{locale}")
        self._fallback_locale: str = getattr(app_settings, "DEFAULT_LOCALE", None) or "en"

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        session_pool: Any | None = None
        try:
            if hasattr(self.container, "resolve"):
                session_pool = self.container.resolve(AsyncPGPool)
        except Exception:
            try:
                if hasattr(self.container, "resolve"):
                    session_pool = self.container.resolve(async_sessionmaker)
            except Exception:
                session_pool = None
        if asyncio.iscoroutine(session_pool):
            try:
                session_pool = await session_pool
            except Exception as e:
                import logging

                logger = logging.getLogger(__name__)
                logger.warning("DB pool resolve failed, using fallback repositories: %s", e)
                session_pool = None
        if session_pool is not None:
            data["session_pool"] = session_pool
        if session_pool is not None:
            # Repositories - temporarily simplified for clean architecture
            # TODO: Implement proper repository injection via factory
            # The loop is commented out as repositories are not injected via container
            # for key, dep in [
            #     ("user_repo", UserRepository),
            #     ("plan_repo", PlanRepository),
            #     ("channel_repo", ChannelRepository),
            #     ("scheduler_repo", SchedulerRepository),
            #     ("analytics_repo", AnalyticsRepository),
            # ]:
            #     try:
            #         if hasattr(self.container, "resolve"):
            #             data[key] = self.container.resolve(dep)
            #     except Exception:
            #         continue
            pass
        else:
            data["user_repo"] = _NullUserRepository()
            data["plan_repo"] = _Null()
            data["channel_repo"] = _Null()
            data["scheduler_repo"] = _Null()
            data["analytics_repo"] = _Null()
        # Inject services using modern container API
        if session_pool is not None and hasattr(self.container, "bot"):
            try:
                # Legacy services (will be deprecated)
                data["subscription_service"] = self.container.bot.subscription_service()
                data["guard_service"] = self.container.bot.guard_service()
                # REMOVED: scheduler_service (deprecated - use schedule_manager instead)
                data["analytics_service"] = self.container.bot.analytics_service()

                # New scheduling services (Clean Architecture)
                data["schedule_manager"] = self.container.bot.schedule_manager()
                data["post_delivery_service"] = self.container.bot.post_delivery_service()
                data["delivery_status_tracker"] = self.container.bot.delivery_status_tracker()

                # New alert services (Clean Architecture)
                data["alert_condition_evaluator"] = self.container.bot.alert_condition_evaluator()
                data["alert_rule_manager"] = self.container.bot.alert_rule_manager()
                data["alert_event_manager"] = self.container.bot.alert_event_manager()
                data["telegram_alert_notifier"] = self.container.bot.telegram_alert_notifier()

            except Exception as e:
                import logging

                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to inject services: {e}")
                # Fallback to nulls
                data["subscription_service"] = _Null()
                data["guard_service"] = _Null()
                data["scheduler_service"] = _Null()
                data["analytics_service"] = _Null()
                data["schedule_manager"] = _Null()
                data["post_delivery_service"] = _Null()
                data["delivery_status_tracker"] = _Null()
                data["alert_condition_evaluator"] = _Null()
                data["alert_rule_manager"] = _Null()
                data["alert_event_manager"] = _Null()
                data["telegram_alert_notifier"] = _Null()
        else:
            data["subscription_service"] = _Null()
            data["guard_service"] = _Null()
            data["scheduler_service"] = _Null()
            data["analytics_service"] = _Null()
            data["schedule_manager"] = _Null()
            data["post_delivery_service"] = _Null()
            data["delivery_status_tracker"] = _Null()
            data["alert_condition_evaluator"] = _Null()
            data["alert_rule_manager"] = _Null()
            data["alert_event_manager"] = _Null()
            data["telegram_alert_notifier"] = _Null()
        if not data.get("i18n"):
            core = self._fallback_core
            loc = self._fallback_locale

            def _safe_get(key: str, **kw: Any) -> str:
                try:
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
