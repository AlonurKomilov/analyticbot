"""
Metrics Service Providers

Factory functions for metrics and monitoring services.
Includes Prometheus metrics, system metrics, health checks, and chart rendering.
"""

import logging

logger = logging.getLogger(__name__)


def create_prometheus_metrics_adapter(**kwargs):
    """Create Prometheus metrics adapter"""
    try:
        from apps.bot.adapters.metrics import PrometheusMetricsAdapter

        return PrometheusMetricsAdapter()
    except ImportError as e:
        logger.warning(f"Prometheus metrics adapter not available: {e}")
        return None


def create_system_metrics_adapter(**kwargs):
    """Create system metrics adapter (PSUtil)"""
    try:
        from apps.bot.adapters.metrics import PSUtilSystemMetricsAdapter

        return PSUtilSystemMetricsAdapter()
    except ImportError as e:
        logger.warning(f"System metrics adapter not available: {e}")
        return None


def create_metrics_collector_service(metrics_backend=None, **kwargs):
    """Create metrics collector service"""
    try:
        from typing import cast

        from core.services.bot.metrics import MetricsCollectorService
        from core.services.bot.metrics.protocols import MetricsBackendPort

        if not metrics_backend:
            logger.warning("Cannot create metrics collector service: missing backend")
            return None

        service = MetricsCollectorService(metrics_backend=cast(MetricsBackendPort, metrics_backend))
        service.initialize_metrics()
        return service
    except ImportError as e:
        logger.warning(f"Metrics collector service not available: {e}")
        return None


def create_business_metrics_service(metrics_backend=None, **kwargs):
    """Create business metrics service"""
    try:
        from typing import cast

        from core.services.bot.metrics import BusinessMetricsService
        from core.services.bot.metrics.protocols import MetricsBackendPort

        if not metrics_backend:
            logger.warning("Cannot create business metrics service: missing backend")
            return None

        service = BusinessMetricsService(metrics_backend=cast(MetricsBackendPort, metrics_backend))
        service.initialize_metrics()
        return service
    except ImportError as e:
        logger.warning(f"Business metrics service not available: {e}")
        return None


def create_health_check_service(metrics_backend=None, **kwargs):
    """Create health check service"""
    try:
        from typing import cast

        from core.services.bot.metrics import HealthCheckService
        from core.services.bot.metrics.protocols import MetricsBackendPort

        if not metrics_backend:
            logger.warning("Cannot create health check service: missing backend")
            return None

        service = HealthCheckService(metrics_backend=cast(MetricsBackendPort, metrics_backend))
        service.initialize_metrics()
        return service
    except ImportError as e:
        logger.warning(f"Health check service not available: {e}")
        return None


def create_system_metrics_service(metrics_backend=None, system_monitor=None, **kwargs):
    """Create system metrics service"""
    try:
        from typing import cast

        from core.services.bot.metrics import SystemMetricsService
        from core.services.bot.metrics.protocols import MetricsBackendPort, SystemMetricsPort

        if not metrics_backend or not system_monitor:
            logger.warning("Cannot create system metrics service: missing dependencies")
            return None

        service = SystemMetricsService(
            metrics_backend=cast(MetricsBackendPort, metrics_backend),
            system_monitor=cast(SystemMetricsPort, system_monitor),
        )
        service.initialize_metrics()
        return service
    except ImportError as e:
        logger.warning(f"System metrics service not available: {e}")
        return None


def create_chart_service(**kwargs):
    """Create chart service for rendering analytics charts"""
    try:
        from apps.shared.services.chart_service import ChartService
        from infra.rendering.charts import MATPLOTLIB_AVAILABLE, ChartRenderer

        if not MATPLOTLIB_AVAILABLE:
            logger.warning(
                "Matplotlib not available - chart service will have limited functionality"
            )
            return ChartService(chart_renderer=None)

        # Create chart renderer from infrastructure layer
        chart_renderer = ChartRenderer()
        return ChartService(chart_renderer=chart_renderer)
    except ImportError as e:
        logger.warning(f"Chart service not available: {e}")
        return None
