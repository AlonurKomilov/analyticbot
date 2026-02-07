"""
Application-layer metrics decorators with DI support.

These decorators provide actual metrics recording using DI,
while the core layer decorators remain framework-agnostic placeholders.
"""

import functools
import logging
import time
from collections.abc import Callable
from typing import Any, TypeVar

# ✅ FIXED: Lazy import to avoid circular dependency
# from apps.di import get_business_metrics_service, get_metrics_collector_service, get_system_metrics_service
from core.services.bot.metrics.models import (
    CeleryTaskMetric,
    DatabaseQueryMetric,
    HTTPRequestMetric,
    TelegramAPIMetric,
)

logger = logging.getLogger(__name__)


def _get_di_services():
    """Lazy import to avoid circular dependency during module initialization"""
    from apps.di import (
        get_business_metrics_service,
        get_metrics_collector_service,
        get_system_metrics_service,
    )

    return (
        get_business_metrics_service,
        get_metrics_collector_service,
        get_system_metrics_service,
    )


F = TypeVar("F", bound=Callable[..., Any])


def metrics_timer(
    metric_type: str = "function",
    metric_name: str | None = None,
    labels: dict[str, str] | None = None,
) -> Callable[[F], F]:
    """
    Decorator to time function execution and record metrics using DI.

    Args:
        metric_type: Type of metric (function, celery_task, http, telegram_api, database)
        metric_name: Custom metric name (default: function name)
        labels: Additional labels for the metric

    Usage:
        from apps.bot.metrics_decorators import metrics_timer

        @metrics_timer(metric_type="celery_task")
        async def my_task():
            ...
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            status = "success"

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception:
                status = "failed"
                raise
            finally:
                duration = time.time() - start_time
                await _record_metric(
                    metric_type=metric_type,
                    metric_name=metric_name or func.__name__,
                    duration=duration,
                    status=status,
                    labels=labels or {},
                )

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            status = "success"

            try:
                result = func(*args, **kwargs)
                return result
            except Exception:
                status = "failed"
                raise
            finally:
                duration = time.time() - start_time
                logger.debug(
                    f"Sync function '{func.__name__}' executed in {duration:.3f}s (status: {status})"
                )

        import inspect

        if inspect.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        else:
            return sync_wrapper  # type: ignore

    return decorator


async def _record_metric(
    metric_type: str,
    metric_name: str,
    duration: float,
    status: str,
    labels: dict[str, str],
) -> None:
    """
    Record a metric using DI services.

    Args:
        metric_type: Type of metric
        metric_name: Name of the metric
        duration: Execution duration in seconds
        status: Status (success, failed)
        labels: Additional labels
    """
    try:
        # Lazy import to avoid circular dependency
        _, get_metrics_collector_service, _ = _get_di_services()
        collector = get_metrics_collector_service()
        if not collector:
            return

        # Record based on metric type
        if metric_type == "celery_task":
            metric: (
                CeleryTaskMetric | DatabaseQueryMetric | HTTPRequestMetric | TelegramAPIMetric
            ) = CeleryTaskMetric(
                task_name=metric_name,
                status=status,
                duration=duration,
                labels=labels,
            )
            await collector.record_celery_task(metric)

        elif metric_type == "database":
            metric = DatabaseQueryMetric(
                operation=metric_name,
                status=status,
                duration=duration,
                labels=labels,
            )
            await collector.record_database_query(metric)

        elif metric_type == "http":
            metric = HTTPRequestMetric(
                method=labels.get("method", "UNKNOWN"),
                endpoint=labels.get("endpoint", metric_name),
                status_code=int(labels.get("status_code", 200 if status == "success" else 500)),
                duration=duration,
                labels=labels,
            )
            await collector.record_http_request(metric)

        elif metric_type == "telegram_api":
            metric = TelegramAPIMetric(
                method=metric_name,
                status=status,
                duration=duration,
                labels=labels,
            )
            await collector.record_telegram_api_request(metric)

        else:
            logger.debug(f"Function '{metric_name}' executed in {duration:.3f}s (status: {status})")

    except Exception as e:
        logger.error(f"Failed to record metric: {e}")


def collect_system_metrics_decorator(func: F) -> F:
    """
    Decorator to collect system metrics before function execution using DI.

    Usage:
        from apps.bot.metrics_decorators import collect_system_metrics_decorator

        @collect_system_metrics_decorator
        async def update_metrics_task():
            ...
    """

    @functools.wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            # Lazy import to avoid circular dependency
            _, _, get_system_metrics_service_func = _get_di_services()
            system_metrics_service = get_system_metrics_service_func()
            if system_metrics_service:
                await system_metrics_service.collect_and_update_system_metrics()
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")

        return await func(*args, **kwargs)

    @functools.wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        logger.warning(f"System metrics collection skipped for sync function '{func.__name__}'")
        return func(*args, **kwargs)

    import inspect

    if inspect.iscoroutinefunction(func):
        return async_wrapper  # type: ignore
    else:
        return sync_wrapper  # type: ignore
