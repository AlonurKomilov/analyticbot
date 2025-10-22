"""
Bot Service Providers

Factory functions for bot-specific services.
Includes guard, subscription, payment, analytics, and channel management.
"""

import inspect
import logging
from typing import Any

logger = logging.getLogger(__name__)


def create_service_with_deps(ServiceCls: type, **provided_kwargs) -> Any:
    """Create service with flexible dependency injection based on constructor signature"""
    sig = inspect.signature(ServiceCls.__init__)  # type: ignore[misc]
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


def create_guard_service(user_repository=None, **kwargs):
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


def create_subscription_service(user_repository=None, plan_repository=None, **kwargs):
    """Create subscription service"""
    try:
        from apps.bot.services.subscription_service import SubscriptionService

        return create_service_with_deps(
            SubscriptionService,
            user_repository=user_repository,
            plan_repository=plan_repository,
            **kwargs,
        )
    except ImportError:
        return None


def create_payment_orchestrator(payment_repository=None, **kwargs):
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


def create_analytics_service(analytics_repository=None, channel_repository=None, **kwargs):
    """Create analytics service (core service)"""
    try:
        # ✅ Phase 3.5.2: Migrated to core analytics (2025-10-15)
        from core.services.bot.analytics import AnalyticsService

        return create_service_with_deps(
            AnalyticsService,
            analytics_repository=analytics_repository,
            channel_repository=channel_repository,
            **kwargs,
        )
    except ImportError:
        return None


def create_channel_management_service(channel_repository=None, bot=None, **kwargs):
    """Create channel management service"""
    try:
        # ✅ Phase 3.5.2: Migrated to core analytics (2025-10-15)
        from core.services.bot.analytics import AnalyticsService

        return create_service_with_deps(
            AnalyticsService,
            channel_repository=channel_repository,
            analytics_repository=channel_repository,
            bot=bot,
            **kwargs,
        )
    except ImportError:
        return None
