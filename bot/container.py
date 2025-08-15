from pathlib import Path

import punq
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from bot.config import Settings
from bot.database.db import create_pool
from bot.database.repositories.analytics_repository import AnalyticsRepository
from bot.database.repositories.channel_repository import ChannelRepository
from bot.database.repositories.plan_repository import PlanRepository
from bot.database.repositories.scheduler_repository import SchedulerRepository
from bot.database.repositories.user_repository import UserRepository
from punctuated import Singleton


class Container(punq.Container):
    config = Singleton(Settings)

    @Singleton
    def bot(self) -> Bot:
        config = self.resolve(Settings)
        return Bot(
            token=config.BOT_TOKEN.get_secret_value(),
            parse_mode=ParseMode.HTML,
        )

    dp = Singleton(
        Dispatcher,
        storage=MemoryStorage(),
    )

    db_session = Singleton(create_pool)

    user_repository = Singleton(UserRepository, session=db_session)
    plan_repository = Singleton(PlanRepository, session=db_session)
    channel_repository = Singleton(ChannelRepository, session=db_session)
    scheduler_repository = Singleton(SchedulerRepository, session=db_session)
    analytics_repository = Singleton(AnalyticsRepository, session=db_session)

    guard_service = Singleton("bot.services.guard_service.GuardService", repository=channel_repository)
    subscription_service = Singleton("bot.services.subscription_service.SubscriptionService", repository=channel_repository)
    scheduler_service = Singleton(
        "bot.services.scheduler_service.SchedulerService",
        scheduler_repository=scheduler_repository,
        user_repository=user_repository,
    )
    analytics_service = Singleton("bot.services.analytics_service.AnalyticsService", repository=analytics_repository)


container = Container()
