"""
DI Provider Functions Package

This package contains organized factory functions for dependency injection.
Each module contains related providers grouped by functionality.

Modules:
- bot_infrastructure: Bot client and dispatcher
- adapters: Bot adapters (analytics, reporting, dashboard, scheduling)
- bot_services: Bot-specific services (guard, subscription, payment, analytics)
- scheduling_providers: Scheduling services (schedule manager, delivery, tracking)
- alert_providers: Alert system services (evaluator, rules, events, notifier)
- content_protection_providers: Content protection services (watermarking, theft detection)
- metrics_providers: Metrics and monitoring services (Prometheus, health, charts)
"""

# Bot infrastructure
# Bot adapters
from .adapters import (
    create_aiogram_markup_builder,
    create_aiogram_message_sender,
    create_bot_analytics_adapter,
    create_bot_dashboard_adapter,
    create_bot_reporting_adapter,
)

# Alert services
from .alert_providers import (
    create_alert_condition_evaluator,
    create_alert_event_manager,
    create_alert_rule_manager,
    create_telegram_alert_notifier,
)
from .bot_infrastructure import create_bot_client, create_dispatcher

# Bot services
from .bot_services import (
    create_analytics_service,
    create_channel_management_service,
    create_guard_service,
    create_payment_orchestrator,
    create_service_with_deps,
    create_subscription_service,
)

# Content protection services
from .content_protection_providers import (
    create_content_protection_service,
    create_file_system_adapter,
    create_image_processor,
    create_subscription_adapter,
    create_theft_detector,
    create_video_processor,
    create_video_watermark_service,
    create_watermark_service,
)

# Metrics services
from .metrics_providers import (
    create_business_metrics_service,
    create_chart_service,
    create_health_check_service,
    create_metrics_collector_service,
    create_prometheus_metrics_adapter,
    create_system_metrics_adapter,
    create_system_metrics_service,
)

# Scheduling services
from .scheduling_providers import (
    create_delivery_status_tracker,
    create_post_delivery_service,
    create_schedule_manager,
)

__all__ = [
    # Infrastructure
    "create_bot_client",
    "create_dispatcher",
    # Adapters
    "create_bot_analytics_adapter",
    "create_bot_reporting_adapter",
    "create_bot_dashboard_adapter",
    "create_aiogram_message_sender",
    "create_aiogram_markup_builder",
    # Bot services
    "create_guard_service",
    "create_subscription_service",
    "create_payment_orchestrator",
    "create_analytics_service",
    "create_channel_management_service",
    "create_service_with_deps",
    # Scheduling
    "create_schedule_manager",
    "create_post_delivery_service",
    "create_delivery_status_tracker",
    # Alerts
    "create_alert_condition_evaluator",
    "create_alert_rule_manager",
    "create_alert_event_manager",
    "create_telegram_alert_notifier",
    # Content protection
    "create_image_processor",
    "create_video_processor",
    "create_file_system_adapter",
    "create_subscription_adapter",
    "create_theft_detector",
    "create_watermark_service",
    "create_video_watermark_service",
    "create_content_protection_service",
    # Metrics
    "create_prometheus_metrics_adapter",
    "create_system_metrics_adapter",
    "create_metrics_collector_service",
    "create_business_metrics_service",
    "create_health_check_service",
    "create_system_metrics_service",
    "create_chart_service",
]
