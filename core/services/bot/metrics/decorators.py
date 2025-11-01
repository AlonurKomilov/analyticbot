"""
Metrics timing decorators.

These decorators provide a clean way to time function execution
and record metrics, using DI for metrics services.
"""

import functools
import logging
import time
from collections.abc import Callable
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def metrics_timer(
    metric_type: str = "function",
    metric_name: str | None = None,
    labels: dict[str, str] | None = None,
) -> Callable[[F], F]:
    """
    Decorator to time function execution and record metrics.

    This decorator uses DI to get the metrics collector service
    and records execution duration as a histogram metric.

    Args:
        metric_type: Type of metric (function, celery_task, http, telegram_api, database)
        metric_name: Custom metric name (default: function name)
        labels: Additional labels for the metric

    Usage:
        @metrics_timer(metric_type="celery_task")
        async def my_task():
            ...

        @metrics_timer(metric_type="function", metric_name="custom_func")
        def my_function():
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
                # For sync functions, we can't easily record async metrics
                # Log a warning if metrics recording is critical
                logger.debug(
                    f"Sync function '{func.__name__}' executed in {duration:.3f}s (status: {status})"
                )

        # Return appropriate wrapper based on function type
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
    Record a metric.

    NOTE: This is a placeholder that logs metrics.
    Actual recording happens in the apps layer where DI is available.
    This keeps the core layer free of DI dependencies.

    Args:
        metric_type: Type of metric
        metric_name: Name of the metric
        duration: Execution duration in seconds
        status: Status (success, failed)
        labels: Additional labels
    """
    try:
        # Log the metric (core layer cannot access DI)
        logger.debug(
            f"Metric recorded: type={metric_type}, name={metric_name}, "
            f"duration={duration:.3f}s, status={status}, labels={labels}"
        )
    except Exception as e:
        logger.error(f"Failed to log metric: {e}")


def collect_system_metrics_decorator(func: F) -> F:
    """
    Decorator to collect system metrics before function execution.

    NOTE: This is a placeholder decorator.
    Actual system metrics collection should be done in the apps layer
    where DI is available. This keeps the core layer free of DI dependencies.

    Usage:
        @collect_system_metrics_decorator
        async def update_metrics_task():
            ...
    """

    @functools.wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        logger.debug(f"System metrics collection point: {func.__name__}")
        return await func(*args, **kwargs)

    @functools.wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        logger.debug(f"System metrics collection point: {func.__name__}")
        return func(*args, **kwargs)

    import inspect

    if inspect.iscoroutinefunction(func):
        return async_wrapper  # type: ignore
    else:
        return sync_wrapper  # type: ignore
