"""
Bot Services DI Container

Single Responsibility: Bot-specific services and adapters
Includes Telegram bot client, bot services, and adapters to core services
"""

import logging
import os
from typing import Any

from dependency_injector import containers, providers

from apps.bot.config import Settings as BotSettings

logger = logging.getLogger(__name__)


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================


def _create_bot_client(settings: BotSettings) -> Any | None:
    """Create bot client or return None for API-only deployments"""
    try:
        token = settings.BOT_TOKEN.get_secret_value() if hasattr(settings, "BOT_TOKEN") else None
    except Exception:
        token = os.getenv("BOT_TOKEN")

    if not token or token == "replace_me":
        return None

    try:
        from aiogram import Bot as _AioBot
        from aiogram.client.default import DefaultBotProperties
        from aiogram.enums import ParseMode

        return _AioBot(
            token=token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
    except ImportError:
        return None


def _create_dispatcher():
    """Create aiogram dispatcher"""
    try:
        from aiogram import Dispatcher as _AioDispatcher
        from aiogram.fsm.storage.memory import MemoryStorage

        return _AioDispatcher(storage=MemoryStorage())
    except ImportError:
        return None


# ============================================================================
# BOT ADAPTERS (Thin layers over core services)
# ============================================================================


async def _create_bot_analytics_adapter(
    core_analytics_service=None, bot=None, **kwargs
):
    """Create bot analytics adapter (thin layer over core service)"""
    try:
        from apps.bot.adapters.analytics_adapter import BotAnalyticsAdapter

        # Only create if core service is available
        if core_analytics_service is None:
            return None

        return BotAnalyticsAdapter(
            batch_processor=core_analytics_service, bot=bot
        )
    except ImportError as e:
        logger.warning(f"Bot analytics adapter not available: {e}")
        return None


async def _create_bot_reporting_adapter(core_reporting_service=None, **kwargs):
    """Create bot reporting adapter (thin layer over core service)"""
    try:
        from apps.bot.adapters.reporting_adapter import BotReportingAdapter

        # Only create if core service is available
        if core_reporting_service is None:
            return None

        return BotReportingAdapter(reporting_system=core_reporting_service)
    except ImportError as e:
        logger.warning(f"Bot reporting adapter not available: {e}")
        return None


async def _create_bot_dashboard_adapter(core_dashboard_service=None, **kwargs):
    """Create bot dashboard adapter (thin layer over core service)"""
    try:
        from apps.bot.adapters.dashboard_adapter import BotDashboardAdapter

        return BotDashboardAdapter(dashboard=core_dashboard_service)
    except ImportError as e:
        logger.warning(f"Bot dashboard adapter not available: {e}")
        return None


def _create_aiogram_message_sender(bot=None, **kwargs):
    """Create Aiogram message sender adapter"""
    try:
        from apps.bot.adapters.scheduling_adapters import AiogramMessageSender

        if bot is None:
            logger.warning("Cannot create message sender: bot is None")
            return None

        return AiogramMessageSender(bot=bot)
    except ImportError as e:
        logger.warning(f"Message sender adapter not available: {e}")
        return None


def _create_aiogram_markup_builder(**kwargs):
    """Create Aiogram markup builder adapter"""
    try:
        from apps.bot.adapters.scheduling_adapters import AiogramMarkupBuilder

        return AiogramMarkupBuilder()
    except ImportError as e:
        logger.warning(f"Markup builder adapter not available: {e}")
        return None


# ============================================================================
# BOT SERVICES
# ============================================================================


def _create_guard_service(user_repository=None, **kwargs):
    """Create guard service with cache adapter for content moderation"""
    try:
        from apps.bot.services.guard_service import GuardService
        from infra.cache.redis_cache_adapter import create_redis_cache_adapter

        # Use in-memory cache by default (Redis optional)
        cache = create_redis_cache_adapter(None)
        return GuardService(cache=cache)
    except ImportError as e:
        logger.warning(f"Failed to create guard service: {e}")
        return None


def _create_subscription_service(user_repository=None, plan_repository=None, **kwargs):
    """Create subscription service"""
    try:
        from apps.bot.services.subscription_service import SubscriptionService

        return _create_service_with_deps(
            SubscriptionService,
            user_repository=user_repository,
            plan_repository=plan_repository,
            **kwargs,
        )
    except ImportError:
        return None


def _create_payment_orchestrator(payment_repository=None, **kwargs):
    """Create payment microservices orchestrator"""
    try:
        from infra.services.payment import (
            PaymentAnalyticsService,
            PaymentGatewayManagerService,
            PaymentMethodService,
            PaymentOrchestratorService,
            PaymentProcessingService,
            WebhookService,
        )
        from infra.services.payment import (
            SubscriptionService as PaymentSubscriptionService,
        )

        if payment_repository is None:
            return None

        # Create microservices
        payment_method_service = PaymentMethodService(payment_repository)
        payment_processing_service = PaymentProcessingService(payment_repository)
        payment_subscription_service = PaymentSubscriptionService(payment_repository)
        webhook_service = WebhookService(payment_repository)
        analytics_service = PaymentAnalyticsService(payment_repository)
        gateway_manager_service = PaymentGatewayManagerService()

        # Create orchestrator
        return PaymentOrchestratorService(
            payment_method_service=payment_method_service,
            payment_processing_service=payment_processing_service,
            subscription_service=payment_subscription_service,
            webhook_service=webhook_service,
            analytics_service=analytics_service,
            gateway_manager_service=gateway_manager_service,
        )
    except ImportError as e:
        logger.warning(f"Payment orchestrator not available: {e}")
        return None


def _create_scheduler_service(schedule_repository=None, bot=None, **kwargs):
    """
    DEPRECATED: Legacy scheduler service (archived in Phase 3.1)

    Use instead:
    - schedule_manager() for core scheduling logic
    - post_delivery_service() for message delivery
    - delivery_status_tracker() for status management
    """
    logger.warning(
        "SchedulerService is deprecated. Use new scheduling services: "
        "schedule_manager, post_delivery_service, delivery_status_tracker"
    )
    return None


# ============================================================================
# NEW SCHEDULING SERVICES (Clean Architecture)
# ============================================================================


def _create_schedule_manager(schedule_repository=None, analytics_repository=None, **kwargs):
    """Create schedule manager (core scheduling logic)"""
    try:
        from core.services.bot.scheduling import ScheduleManager

        if schedule_repository is None:
            logger.warning("Cannot create schedule manager: missing schedule repository")
            return None

        return ScheduleManager(schedule_repository=schedule_repository)
    except ImportError as e:
        logger.warning(f"Schedule manager not available: {e}")
        return None


def _create_post_delivery_service(
    message_sender=None,
    markup_builder=None,
    schedule_repository=None,
    analytics_repository=None,
    **kwargs
):
    """Create post delivery service (orchestrates message delivery)"""
    try:
        from typing import cast

        from core.services.bot.scheduling import PostDeliveryService
        from core.services.bot.scheduling.protocols import (
            AnalyticsRepository,
            MarkupBuilderPort,
            MessageSenderPort,
            ScheduleRepository,
        )

        if not all([message_sender, markup_builder, schedule_repository, analytics_repository]):
            logger.warning("Cannot create post delivery service: missing dependencies")
            return None

        # Type cast to satisfy type checker (DI ensures correct types at runtime)
        return PostDeliveryService(
            message_sender=cast(MessageSenderPort, message_sender),
            markup_builder=cast(MarkupBuilderPort, markup_builder),
            schedule_repo=cast(ScheduleRepository, schedule_repository),
            analytics_repo=cast(AnalyticsRepository, analytics_repository),
        )
    except ImportError as e:
        logger.warning(f"Post delivery service not available: {e}")
        return None


def _create_delivery_status_tracker(
    schedule_repository=None,
    analytics_repository=None,
    **kwargs
):
    """Create delivery status tracker (manages post lifecycle)"""
    try:
        from core.services.bot.scheduling import DeliveryStatusTracker

        if schedule_repository is None or analytics_repository is None:
            logger.warning("Cannot create delivery status tracker: missing repositories")
            return None

        return DeliveryStatusTracker(
            schedule_repo=schedule_repository,
            analytics_repo=analytics_repository,
        )
    except ImportError as e:
        logger.warning(f"Delivery status tracker not available: {e}")
        return None


def _create_alert_condition_evaluator(alert_repository=None, **kwargs):
    """Create alert condition evaluator (core alert logic)"""
    try:
        from core.services.bot.alerts import AlertConditionEvaluator

        if alert_repository is None:
            logger.warning("Cannot create alert condition evaluator: missing alert repository")
            return None

        return AlertConditionEvaluator(alert_repository=alert_repository)
    except ImportError as e:
        logger.warning(f"Alert condition evaluator not available: {e}")
        return None


def _create_alert_rule_manager(alert_repository=None, **kwargs):
    """Create alert rule manager (CRUD for alert rules)"""
    try:
        from core.services.bot.alerts import AlertRuleManager

        if alert_repository is None:
            logger.warning("Cannot create alert rule manager: missing alert repository")
            return None

        return AlertRuleManager(alert_repository=alert_repository)
    except ImportError as e:
        logger.warning(f"Alert rule manager not available: {e}")
        return None


def _create_alert_event_manager(alert_repository=None, **kwargs):
    """Create alert event manager (manages alert events and history)"""
    try:
        from core.services.bot.alerts import AlertEventManager

        if alert_repository is None:
            logger.warning("Cannot create alert event manager: missing alert repository")
            return None

        return AlertEventManager(alert_repository=alert_repository)
    except ImportError as e:
        logger.warning(f"Alert event manager not available: {e}")
        return None


def _create_telegram_alert_notifier(bot=None, **kwargs):
    """Create Telegram alert notifier (sends alerts via Telegram)"""
    try:
        from apps.bot.adapters.alert_adapters import TelegramAlertNotifier

        if bot is None:
            logger.warning("Cannot create telegram alert notifier: missing bot")
            return None

        return TelegramAlertNotifier(bot=bot)
    except ImportError as e:
        logger.warning(f"Telegram alert notifier not available: {e}")
        return None


def _create_analytics_service(analytics_repository=None, channel_repository=None, **kwargs):
    """Create analytics service (legacy bot service)"""
    try:
        from apps.bot.services.analytics_service import AnalyticsService

        return _create_service_with_deps(
            AnalyticsService,
            analytics_repository=analytics_repository,
            channel_repository=channel_repository,
            **kwargs,
        )
    except ImportError:
        return None


def _create_alerting_service(bot=None, user_repository=None, **kwargs):
    """
    DEPRECATED: Legacy alerting service (archived in Phase 3.2)

    Use instead:
    - alert_condition_evaluator() for metric evaluation
    - alert_rule_manager() for rule management
    - alert_event_manager() for event lifecycle
    - telegram_alert_notifier() for notifications
    """
    logger.warning(
        "AlertingService is deprecated. Use new alert services: "
        "alert_condition_evaluator, alert_rule_manager, alert_event_manager"
    )
    return None


def _create_channel_management_service(channel_repository=None, bot=None, **kwargs):
    """Create channel management service"""
    try:
        from apps.bot.services.analytics_service import AnalyticsService

        return _create_service_with_deps(
            AnalyticsService,
            channel_repository=channel_repository,
            analytics_repository=channel_repository,
            bot=bot,
            **kwargs,
        )
    except ImportError:
        return None


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def _create_service_with_deps(ServiceCls: type, **provided_kwargs) -> Any:
    """Create service with flexible dependency injection based on constructor signature"""
    import inspect

    sig = inspect.signature(ServiceCls.__init__)
    accepted_params = set(sig.parameters.keys()) - {"self"}

    # Filter to only include parameters the service accepts and that are not None
    filtered_kwargs = {
        k: v for k, v in provided_kwargs.items() if k in accepted_params and v is not None
    }

    try:
        return ServiceCls(**filtered_kwargs)
    except Exception:
        # Fallback: try without any parameters
        try:
            return ServiceCls()
        except Exception:
            return None


# ============================================================================
# BOT CONTAINER
# ============================================================================


class BotContainer(containers.DeclarativeContainer):
    """
    Bot Services Container

    Single Responsibility: Telegram bot services and adapters
    Includes bot client, bot-specific services, and thin adapters to core services
    """

    config = providers.Configuration()
    bot_settings = providers.Singleton(BotSettings)

    # Dependencies from other containers
    database = providers.DependenciesContainer()
    core_services = providers.DependenciesContainer()

    # ============================================================================
    # BOT CLIENT & DISPATCHER
    # ============================================================================

    bot_client = providers.Factory(_create_bot_client, settings=bot_settings)
    dispatcher = providers.Factory(_create_dispatcher)

    # ============================================================================
    # BOT ADAPTERS (Thin adapters to core services)
    # ============================================================================

    bot_analytics_adapter = providers.Factory(
        _create_bot_analytics_adapter,
        core_analytics_service=core_services.analytics_batch_processor,
        bot=bot_client,
        analytics_repo=database.analytics_repo,
    )

    bot_reporting_adapter = providers.Factory(
        _create_bot_reporting_adapter,
        core_reporting_service=core_services.reporting_service,
        bot=bot_client,
    )

    bot_dashboard_adapter = providers.Factory(
        _create_bot_dashboard_adapter,
        core_dashboard_service=core_services.dashboard_service,
        bot=bot_client,
    )

    # Telegram adapters for scheduling
    aiogram_message_sender = providers.Factory(
        _create_aiogram_message_sender,
        bot=bot_client,
    )

    aiogram_markup_builder = providers.Factory(
        _create_aiogram_markup_builder,
    )

    # ============================================================================
    # BOT SERVICES
    # ============================================================================

    guard_service = providers.Factory(
        _create_guard_service,
        user_repository=database.user_repo
    )

    subscription_service = providers.Factory(
        _create_subscription_service,
        user_repository=database.user_repo,
        plan_repository=database.plan_repo,
    )

    payment_orchestrator = providers.Factory(
        _create_payment_orchestrator,
        payment_repository=database.payment_repo
    )

    scheduler_service = providers.Factory(
        _create_scheduler_service,
        schedule_repository=database.schedule_repo,
        bot=bot_client,
    )

    # New scheduling services (Clean Architecture)
    schedule_manager = providers.Factory(
        _create_schedule_manager,
        schedule_repository=database.schedule_repo,
        analytics_repository=database.analytics_repo,
    )

    post_delivery_service = providers.Factory(
        _create_post_delivery_service,
        message_sender=aiogram_message_sender,
        markup_builder=aiogram_markup_builder,
        schedule_repository=database.schedule_repo,
        analytics_repository=database.analytics_repo,
    )

    delivery_status_tracker = providers.Factory(
        _create_delivery_status_tracker,
        schedule_repository=database.schedule_repo,
        analytics_repository=database.analytics_repo,
    )

    # New alert services (Clean Architecture)
    alert_condition_evaluator = providers.Factory(
        _create_alert_condition_evaluator,
        alert_repository=database.alert_repo,
    )

    alert_rule_manager = providers.Factory(
        _create_alert_rule_manager,
        alert_repository=database.alert_repo,
    )

    alert_event_manager = providers.Factory(
        _create_alert_event_manager,
        alert_repository=database.alert_repo,
    )

    telegram_alert_notifier = providers.Factory(
        _create_telegram_alert_notifier,
        bot=bot_client,
    )

    analytics_service = providers.Factory(
        _create_analytics_service,
        analytics_repository=database.analytics_repo,
        channel_repository=database.channel_repo,
    )

    alerting_service = providers.Factory(
        _create_alerting_service,
        bot=bot_client,
        user_repository=database.user_repo
    )

    channel_management_service = providers.Factory(
        _create_channel_management_service,
        channel_repository=database.channel_repo,
        bot=bot_client,
    )
