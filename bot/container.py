from typing import cast
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
    # Settings (Singleton)
    config = Singleton(Settings)

    @Singleton
    def bot(self) -> Bot:
        cfg: Settings = cast(Settings, self.resolve(Settings))
        return Bot(
            token=cfg.BOT_TOKEN.get_secret_value(),
            parse_mode=ParseMode.HTML,
        )

    # Aiogram Dispatcher
    dp = Singleton(
        Dispatcher,
        storage=MemoryStorage(),
    )

    # DB session / pool
    db_session = Singleton(create_pool)

    # Repositories
    user_repository = Singleton(UserRepository, session=db_session)
    plan_repository = Singleton(PlanRepository, session=db_session)
    channel_repository = Singleton(ChannelRepository, session=db_session)
    scheduler_repository = Singleton(SchedulerRepository, session=db_session)
    analytics_repository = Singleton(AnalyticsRepository, session=db_session)

    # Services (string import yo‘li bilan lazy resolve)
    guard_service = Singleton(
        "bot.services.guard_service.GuardService",
        repository=channel_repository,
    )
    subscription_service = Singleton(
        "bot.services.subscription_service.SubscriptionService",
        repository=channel_repository,
    )
    scheduler_service = Singleton(
        "bot.services.scheduler_service.SchedulerService",
        scheduler_repository=scheduler_repository,
        user_repository=user_repository,
    )
    analytics_service = Singleton(
        "bot.services.analytics_service.AnalyticsService",
        repository=analytics_repository,
    )


# Global container instance
container = Container()

# ----------------------------------------------------------------------
# Type aliases: class-based resolve() (e.g. container.resolve(UserRepository))
# ishlashi uchun mavjud Singleton provayderlarni klasslarga map qilamiz.
# Bu punq uchun "implementation for <class '...'>" topilmasligi xatolarini tuzatadi.
# ----------------------------------------------------------------------

# Aiogram: Bot/Dispatcher aliaslari
try:
    # aiogram v3 class identity'ni aniq moslab olish uchun client.bot dan import qilamiz
    from aiogram.client.bot import Bot as _BotCls
except Exception:
    from aiogram import Bot as _BotCls  # fallback (odatda shart emas)

from aiogram import Dispatcher as _Dispatcher

try:
    container.register(_BotCls, instance=container.bot)         # Singleton(Bot)
except Exception:
    pass
try:
    container.register(_Dispatcher, instance=container.dp)      # Singleton(Dispatcher)
except Exception:
    pass

# Settings alias
from bot.config import Settings as _Settings
try:
    container.register(_Settings, instance=container.config)    # Singleton(Settings)
except Exception:
    pass

# Repository aliaslari
from bot.database.repositories.user_repository import UserRepository as _UserRepo
from bot.database.repositories.channel_repository import ChannelRepository as _ChannelRepo
from bot.database.repositories.analytics_repository import AnalyticsRepository as _AnalyticsRepo
from bot.database.repositories.plan_repository import PlanRepository as _PlanRepo
from bot.database.repositories.scheduler_repository import SchedulerRepository as _SchedulerRepo

try:
    container.register(_UserRepo, instance=container.user_repository)
    container.register(_ChannelRepo, instance=container.channel_repository)
    container.register(_AnalyticsRepo, instance=container.analytics_repository)
    container.register(_PlanRepo, instance=container.plan_repository)
    container.register(_SchedulerRepo, instance=container.scheduler_repository)
except Exception:
    pass

# Service aliaslari
from bot.services.guard_service import GuardService as _GuardService
from bot.services.subscription_service import SubscriptionService as _SubService
from bot.services.scheduler_service import SchedulerService as _SchedService
from bot.services.analytics_service import AnalyticsService as _AnalytService

try:
    container.register(_GuardService, instance=container.guard_service)
    container.register(_SubService, instance=container.subscription_service)
    container.register(_SchedService, instance=container.scheduler_service)
    container.register(_AnalytService, instance=container.analytics_service)
except Exception:
    pass
