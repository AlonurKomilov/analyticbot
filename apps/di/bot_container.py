"""
Bot Services DI Container

Single Responsibility: Bot-specific services and adapters
Includes Telegram bot client, bot services, and adapters to core services

✅ Issue #4 Phase 1 (Oct 21, 2025): Split 910-line god object into modular provider packages.
Factory functions now organized in apps/di/providers/ by functionality.
"""

from dependency_injector import containers, providers

from apps.bot.config import Settings as BotSettings

# Import all provider factories from modular packages
from apps.di.providers import (  # Adapters; Alert services; Bot services; Infrastructure; Metrics; Content protection; Scheduling
    create_aiogram_markup_builder,
    create_aiogram_message_sender,
    create_alert_condition_evaluator,
    create_alert_event_manager,
    create_alert_rule_manager,
    create_analytics_service,
    create_bot_analytics_adapter,
    create_bot_client,
    create_bot_dashboard_adapter,
    create_bot_reporting_adapter,
    create_business_metrics_service,
    create_channel_management_service,
    create_chart_service,
    create_content_protection_service,
    create_delivery_status_tracker,
    create_dispatcher,
    create_file_system_adapter,
    create_guard_service,
    create_health_check_service,
    create_image_processor,
    create_metrics_collector_service,
    create_payment_orchestrator,
    create_post_delivery_service,
    create_prometheus_metrics_adapter,
    create_schedule_manager,
    create_subscription_adapter,
    create_subscription_service,
    create_system_metrics_adapter,
    create_system_metrics_service,
    create_telegram_alert_notifier,
    create_theft_detector,
    create_video_processor,
    create_video_watermark_service,
    create_watermark_service,
)


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

    bot_client = providers.Factory(create_bot_client, settings=bot_settings)
    dispatcher = providers.Factory(create_dispatcher)

    # ============================================================================
    # BOT ADAPTERS (Thin adapters to core services)
    # ============================================================================

    bot_analytics_adapter = providers.Factory(
        create_bot_analytics_adapter,
        core_analytics_service=core_services.analytics_batch_processor,
        bot=bot_client,
        analytics_repo=database.analytics_repo,
    )

    bot_reporting_adapter = providers.Factory(
        create_bot_reporting_adapter,
        core_reporting_service=core_services.reporting_service,
        bot=bot_client,
    )

    bot_dashboard_adapter = providers.Factory(
        create_bot_dashboard_adapter,
        core_dashboard_service=core_services.dashboard_service,
        bot=bot_client,
    )

    # Telegram adapters for scheduling
    aiogram_message_sender = providers.Factory(
        create_aiogram_message_sender,
        bot=bot_client,
    )

    aiogram_markup_builder = providers.Factory(
        create_aiogram_markup_builder,
    )

    # ============================================================================
    # BOT SERVICES
    # ============================================================================

    guard_service = providers.Factory(create_guard_service, user_repository=database.user_repo)

    subscription_service = providers.Factory(
        create_subscription_service,
        user_repository=database.user_repo,
        plan_repository=database.plan_repo,
    )

    payment_orchestrator = providers.Factory(
        create_payment_orchestrator, payment_repository=database.payment_repo
    )

    # New scheduling services (Clean Architecture)
    schedule_manager = providers.Factory(
        create_schedule_manager,
        schedule_repository=database.schedule_repo,
        analytics_repository=database.analytics_repo,
    )

    post_delivery_service = providers.Factory(
        create_post_delivery_service,
        message_sender=aiogram_message_sender,
        markup_builder=aiogram_markup_builder,
        schedule_repository=database.schedule_repo,
        analytics_repository=database.analytics_repo,
    )

    delivery_status_tracker = providers.Factory(
        create_delivery_status_tracker,
        schedule_repository=database.schedule_repo,
        analytics_repository=database.analytics_repo,
    )

    # New alert services (Clean Architecture)
    alert_condition_evaluator = providers.Factory(
        create_alert_condition_evaluator,
        alert_repository=database.alert_repo,
    )

    alert_rule_manager = providers.Factory(
        create_alert_rule_manager,
        alert_repository=database.alert_repo,
    )

    alert_event_manager = providers.Factory(
        create_alert_event_manager,
        alert_repository=database.alert_repo,
    )

    telegram_alert_notifier = providers.Factory(
        create_telegram_alert_notifier,
        bot=bot_client,
    )

    # Content protection adapters (Phase 3.3)
    image_processor = providers.Factory(create_image_processor)
    video_processor = providers.Factory(create_video_processor)
    file_system_adapter = providers.Factory(create_file_system_adapter)
    subscription_adapter = providers.Factory(create_subscription_adapter)

    # Content protection core services (Phase 3.3)
    theft_detector = providers.Factory(create_theft_detector)

    watermark_service = providers.Factory(
        create_watermark_service,
        image_processor=image_processor,
        file_system=file_system_adapter,
    )

    video_watermark_service = providers.Factory(
        create_video_watermark_service,
        video_processor=video_processor,
        file_system=file_system_adapter,
    )

    content_protection_service = providers.Factory(
        create_content_protection_service,
        watermark_service=watermark_service,
        video_watermark_service=video_watermark_service,
        theft_detector=theft_detector,
        subscription_adapter=subscription_adapter,
        file_system=file_system_adapter,
    )

    # Metrics adapters (Phase 3.4)
    prometheus_metrics_adapter = providers.Factory(create_prometheus_metrics_adapter)
    system_metrics_adapter = providers.Factory(create_system_metrics_adapter)

    # Metrics services (Phase 3.4)
    metrics_collector_service = providers.Factory(
        create_metrics_collector_service,
        metrics_backend=prometheus_metrics_adapter,
    )

    business_metrics_service = providers.Factory(
        create_business_metrics_service,
        metrics_backend=prometheus_metrics_adapter,
    )

    health_check_service = providers.Factory(
        create_health_check_service,
        metrics_backend=prometheus_metrics_adapter,
    )

    system_metrics_service = providers.Factory(
        create_system_metrics_service,
        metrics_backend=prometheus_metrics_adapter,
        system_monitor=system_metrics_adapter,
    )

    analytics_service = providers.Factory(
        create_analytics_service,
        analytics_repository=database.analytics_repo,
        channel_repository=database.channel_repo,
    )

    # Chart rendering service (Issue #10 - Oct 21, 2025)
    chart_service = providers.Factory(create_chart_service)

    channel_management_service = providers.Factory(
        create_channel_management_service,
        channel_repository=database.channel_repo,
        bot=bot_client,
    )
