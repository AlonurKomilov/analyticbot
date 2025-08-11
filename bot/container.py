import punq
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from fluent_compiler.bundle import FluentBundle
from sqlalchemy.ext.asyncio import async_sessionmaker

from bot.config import Settings
from bot.database.db import create_session_pool
from bot.database.repositories.analytics_repository import AnalyticsRepository
from bot.database.repositories.channel_repository import ChannelRepository
from bot.database.repositories.plan_repository import PlanRepository
from bot.database.repositories.scheduler_repository import SchedulerRepository
from bot.database.repositories.user_repository import UserRepository
from bot.services.analytics_service import AnalyticsService
from bot.services.auth_service import AuthService
from bot.services.guard_service import GuardService
from bot.services.scheduler_service import SchedulerService
from bot.services.subscription_service import SubscriptionService
from bot.utils.language_manager import LanguageManager


def get_bot_instance(settings: Settings) -> Bot:
    return Bot(
        token=settings.bot_token.get_secret_value(),
        parse_mode="HTML",
    )


def get_container(settings: Settings) -> punq.Container:
    session_pool = create_session_pool(settings.db_config.dsn)
    container = punq.Container()

    # Settings
    container.register(Settings, instance=settings)

    # Database
    container.register(async_sessionmaker, instance=session_pool)

    # Repositories
    container.register(UserRepository)
    container.register(ChannelRepository)
    container.register(PlanRepository)
    container.register(SchedulerRepository)
    container.register(AnalyticsRepository)

    # Services
    container.register(SubscriptionService)
    container.register(GuardService)
    container.register(AuthService)
    container.register(AnalyticsService)
    container.register(SchedulerService)

    # Telegram Bot
    container.register(
        Bot,
        factory=get_bot_instance,
        scope=punq.Scope.singleton,
        settings=Settings,  # <--- ASOSIY O'ZGARISH SHU YERDA
    )
    container.register(Dispatcher, instance=Dispatcher(storage=MemoryStorage()))

    # Other
    container.register(LanguageManager)
    container.register(FluentBundle)

    return container


__all__ = [
    "get_container",
]