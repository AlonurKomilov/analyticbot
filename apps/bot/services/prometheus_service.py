"""
Prometheus metrics integration service for comprehensive application monitoring.
"""

import asyncio
import logging
import time
from functools import wraps

from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

from apps.bot.utils.error_handler import ErrorContext, ErrorHandler

logger = logging.getLogger(__name__)


class PrometheusService:
    """Service for Prometheus metrics collection and exposition"""

    def __init__(self, registry: CollectorRegistry | None = None, db_manager=None):
        self.registry = registry or CollectorRegistry()
        self.db_manager = db_manager  # Inject database manager for metrics
        self._setup_metrics()

    def _setup_metrics(self):
        """Initialize Prometheus metrics"""
        self.app_info = Gauge(
            "app_info",
            "Application information",
            ["version", "environment"],
            registry=self.registry,
        )
        self.http_requests_total = Counter(
            "http_requests_total",
            "Total HTTP requests",
            ["method", "endpoint", "status_code"],
            registry=self.registry,
        )
        self.http_request_duration_seconds = Histogram(
            "http_request_duration_seconds",
            "HTTP request duration in seconds",
            ["method", "endpoint"],
            registry=self.registry,
        )
        self.telegram_api_requests_total = Counter(
            "telegram_api_requests_total",
            "Total Telegram API requests",
            ["method", "status"],
            registry=self.registry,
        )
        self.telegram_api_request_duration_seconds = Histogram(
            "telegram_api_request_duration_seconds",
            "Telegram API request duration in seconds",
            ["method"],
            registry=self.registry,
        )
        self.telegram_updates_processed_total = Counter(
            "telegram_updates_processed_total",
            "Total Telegram updates processed",
            ["handler_type"],
            registry=self.registry,
        )
        self.database_connections_active = Gauge(
            "database_connections_active",
            "Active database connections",
            registry=self.registry,
        )
        self.database_query_duration_seconds = Histogram(
            "database_query_duration_seconds",
            "Database query duration in seconds",
            ["operation"],
            registry=self.registry,
        )
        self.database_queries_total = Counter(
            "database_queries_total",
            "Total database queries",
            ["operation", "status"],
            registry=self.registry,
        )
        self.celery_tasks_total = Counter(
            "celery_tasks_total",
            "Total Celery tasks",
            ["task_name", "status"],
            registry=self.registry,
        )
        self.celery_task_duration_seconds = Histogram(
            "celery_task_duration_seconds",
            "Celery task duration in seconds",
            ["task_name"],
            registry=self.registry,
        )
        self.celery_workers_active = Gauge(
            "celery_workers_active", "Active Celery workers", registry=self.registry
        )
        self.channels_total = Gauge(
            "channels_total", "Total number of channels", registry=self.registry
        )
        self.users_total = Gauge("users_total", "Total number of users", registry=self.registry)
        self.posts_scheduled = Gauge(
            "posts_scheduled", "Number of scheduled posts", registry=self.registry
        )
        self.posts_sent_total = Counter(
            "posts_sent_total",
            "Total posts sent",
            ["channel_id"],
            registry=self.registry,
        )
        self.post_views_updated_total = Counter(
            "post_views_updated_total",
            "Total post views updated",
            registry=self.registry,
        )
        self.system_memory_usage = Gauge(
            "system_memory_usage_percent",
            "System memory usage percentage",
            registry=self.registry,
        )
        self.system_cpu_usage = Gauge(
            "system_cpu_usage_percent",
            "System CPU usage percentage",
            registry=self.registry,
        )
        self.health_check_status = Gauge(
            "health_check_status",
            "Health check status (1=healthy, 0=unhealthy)",
            ["check_name"],
            registry=self.registry,
        )
        logger.info("Prometheus metrics initialized")

    def record_http_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics"""
        self.http_requests_total.labels(
            method=method, endpoint=endpoint, status_code=status_code
        ).inc()
        self.http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(
            duration
        )

    def record_telegram_api_request(self, method: str, status: str, duration: float):
        """Record Telegram API request metrics"""
        self.telegram_api_requests_total.labels(method=method, status=status).inc()
        self.telegram_api_request_duration_seconds.labels(method=method).observe(duration)

    def record_telegram_update(self, handler_type: str):
        """Record Telegram update processing"""
        self.telegram_updates_processed_total.labels(handler_type=handler_type).inc()

    def record_database_query(self, operation: str, status: str, duration: float):
        """Record database query metrics"""
        self.database_queries_total.labels(operation=operation, status=status).inc()
        self.database_query_duration_seconds.labels(operation=operation).observe(duration)

    def update_database_connections(self, active_count: int):
        """Update active database connections count"""
        self.database_connections_active.set(active_count)

    def record_celery_task(self, task_name: str, status: str, duration: float):
        """Record Celery task execution"""
        self.celery_tasks_total.labels(task_name=task_name, status=status).inc()
        self.celery_task_duration_seconds.labels(task_name=task_name).observe(duration)

    def update_celery_workers(self, worker_count: int):
        """Update active Celery workers count"""
        self.celery_workers_active.set(worker_count)

    def update_business_metrics(self, channels: int, users: int, scheduled_posts: int):
        """Update business metrics"""
        self.channels_total.set(channels)
        self.users_total.set(users)
        self.posts_scheduled.set(scheduled_posts)

    def record_post_sent(self, channel_id: str):
        """Record post sent"""
        self.posts_sent_total.labels(channel_id=channel_id).inc()

    def record_post_views_update(self, count: int = 1):
        """Record post views update"""
        self.post_views_updated_total.inc(count)

    def update_system_metrics(self, memory_percent: float, cpu_percent: float):
        """Update system resource metrics"""
        self.system_memory_usage.set(memory_percent)
        self.system_cpu_usage.set(cpu_percent)

    async def get_database_metrics(self) -> dict:
        """Get database metrics via dependency injection"""
        try:
            # Get database manager through DI instead of direct import
            if hasattr(self, "db_manager") and self.db_manager:
                pool = getattr(self.db_manager, "pool", None)
                if pool:
                    pool_size = getattr(pool, "get_size", lambda: 0)()
                return {"pool_size": pool_size}
            return {"pool_size": 0}
        except Exception:
            return {"pool_size": 0}

    def update_health_check(self, check_name: str, is_healthy: bool):
        """Update health check status"""
        self.health_check_status.labels(check_name=check_name).set(1 if is_healthy else 0)

    def set_app_info(self, version: str, environment: str = "production"):
        """Set application information"""
        self.app_info.labels(version=version, environment=environment).set(1)

    def get_metrics(self) -> str:
        """Generate Prometheus metrics output"""
        return generate_latest(self.registry).decode("utf-8")

    def get_content_type(self) -> str:
        """Get Prometheus metrics content type"""
        return CONTENT_TYPE_LATEST


prometheus_service = PrometheusService()


def prometheus_timer(metric_name: str, labels: dict[str, str] | None = None):
    """Decorator to time function execution and record in Prometheus"""

    def decorator(func):
        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                status = "success"
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception:
                    status = "error"
                    raise
                finally:
                    duration = time.time() - start_time
                    if metric_name == "telegram_api":
                        prometheus_service.record_telegram_api_request(
                            func.__name__, status, duration
                        )
                    elif metric_name == "database":
                        prometheus_service.record_database_query(func.__name__, status, duration)
                    elif metric_name == "celery_task":
                        prometheus_service.record_celery_task(func.__name__, status, duration)

            return async_wrapper
        else:

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                status = "success"
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception:
                    status = "error"
                    raise
                finally:
                    duration = time.time() - start_time
                    if metric_name == "telegram_api":
                        prometheus_service.record_telegram_api_request(
                            func.__name__, status, duration
                        )
                    elif metric_name == "database":
                        prometheus_service.record_database_query(func.__name__, status, duration)
                    elif metric_name == "celery_task":
                        prometheus_service.record_celery_task(func.__name__, status, duration)

            return sync_wrapper

    return decorator


async def collect_system_metrics():
    """Collect system metrics for Prometheus"""
    try:
        try:
            import psutil

            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=1)
            prometheus_service.update_system_metrics(memory.percent, cpu)
        except ImportError:
            logger.warning("psutil not available, system metrics disabled")
        try:
            # Get database metrics through service instead of direct infra import
            db_metrics = await prometheus_service.get_database_metrics()
            if db_metrics:
                prometheus_service.update_database_connections(db_metrics.get("pool_size", 0))
        except Exception as e:
            context = ErrorContext().add("operation", "collect_database_metrics")
            ErrorHandler.log_error(e, context)
        try:
            # ✅ MIGRATED: Use new modular DI instead of legacy bot.di
            from apps.di import get_container

            container = get_container()
            await container.database.channel_repo()
            await container.database.user_repo()
            await container.database.schedule_repo()
            # TODO: Implement count methods using clean architecture
            # For now, use placeholder values
            channels_count = 0  # await channel_repo.count()
            users_count = 0  # await user_repo.count()
            scheduled_posts_count = 0  # await scheduler_repo.count()
            logger.info(
                "Business metrics collection - count methods not implemented in clean architecture"
            )
            prometheus_service.update_business_metrics(
                channels_count, users_count, scheduled_posts_count
            )
        except Exception as e:
            context = ErrorContext().add("operation", "collect_business_metrics")
            ErrorHandler.log_error(e, context)
    except Exception as e:
        context = ErrorContext().add("operation", "collect_system_metrics")
        ErrorHandler.log_error(e, context)


def setup_prometheus_middleware():
    """Setup Prometheus middleware for FastAPI"""
    import time

    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.requests import Request

    class PrometheusMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            start_time = time.time()
            response = await call_next(request)
            duration = time.time() - start_time
            prometheus_service.record_http_request(
                method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code,
                duration=duration,
            )
            return response

    return PrometheusMiddleware
