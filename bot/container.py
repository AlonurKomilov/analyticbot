from pathlib import Path

import punq
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_i18n.middleware import I18nManager
from aiogram_i18n.cores import FluentRuntimeCore
from fluent_compiler.bundle import FluentBundle
from fluent_compiler.resource import FluentResource
from punctuated import Singleton

from bot.config import Settings
from bot.database.db import create_pool
from bot.database.repositories.analytics_repository import AnalyticsRepository
from bot.database.repositories.channel_repository import ChannelRepository
from bot.database.repositories.plan_repository import PlanRepository
from bot.database.repositories.scheduler_repository import SchedulerRepository
from bot.database.repositories.user_repository import UserRepository
from bot.services.analytics_service import AnalyticsService
from bot.services.guard_service import GuardService
from bot.services.scheduler_service import SchedulerService
from bot.services.subscription_service import SubscriptionService


class Locales:
    def __init__(self, locales_path: Path) -> None:
        self.locales_map = {}
        for locale in locales_path.iterdir():
            if not locale.is_dir():
                continue

            self.locales_map[locale.name] = FluentBundle(
                locales=[locale.name],
                use_isolating=False,
            )

            for ftl_file in (locales_path / locale.name).iterdir():
                with open(ftl_file, "r", encoding="utf-8") as f:
                    self.locales_map[locale.name].add_resource(
                        FluentResource(f.read())
                    )

    def get_fluent_runtime_core(self) -> FluentRuntimeCore:
        return FluentRuntimeCore(
            path="locales/{locale}",
            locales_map=self.locales_map,
        )


class Container(punq.Container):
    locales = Singleton(Locales, locales_path=Path("bot/locales"))

    config = Singleton(Settings)

    bot = Singleton(
        Bot,
        token=config.provided.BOT_TOKEN,
        parse_mode=ParseMode.HTML,
    )

    dp = Singleton(
        Dispatcher,
        storage=MemoryStorage(),
    )

    db_session = Singleton(create_pool)

    i18n = Singleton(I18nManager, core=locales.provided.get_fluent_runtime_core())

    user_repository = Singleton(UserRepository, session=db_session)
    plan_repository = Singleton(PlanRepository, session=db_session)
    channel_repository = Singleton(ChannelRepository, session=db_session)
    scheduler_repository = Singleton(SchedulerRepository, session=db_session)
    analytics_repository = Singleton(AnalyticsRepository, session=db_session)

    guard_service = Singleton(GuardService, repository=channel_repository)
    subscription_service = Singleton(SubscriptionService, repository=channel_repository)
    scheduler_service = Singleton(
        SchedulerService,
        scheduler_repository=scheduler_repository,
        user_repository=user_repository,
    )
    analytics_service = Singleton(AnalyticsService, repository=analytics_repository)


container = Container()
