"""
Celery Application Configuration - Master Scheduler
Production-ready Celery setup with retry/backoff strategies
"""

import logging

# Always use environment variables with fallbacks for consistent behavior
import os
from collections.abc import Callable
from typing import Any

from celery import Celery
from celery.signals import task_failure, task_postrun, task_prerun, worker_ready
from pydantic import SecretStr

# Import from centralized configuration
from config.settings import Settings

settings = Settings(
    BOT_TOKEN=SecretStr(os.getenv("BOT_TOKEN", "test_token")),
    STORAGE_CHANNEL_ID=int(os.getenv("STORAGE_CHANNEL_ID", "0")),
    POSTGRES_USER=os.getenv("POSTGRES_USER", "test_user"),
    POSTGRES_PASSWORD=SecretStr(os.getenv("POSTGRES_PASSWORD", "test_pass")),
    POSTGRES_DB=os.getenv("POSTGRES_DB", "test_db"),
    JWT_SECRET_KEY=SecretStr(os.getenv("JWT_SECRET_KEY", "test_jwt_key")),
)

logger = logging.getLogger(__name__)

# Primary Celery application instance
celery_app = Celery(
    "analyticbot_tasks",
    broker=str(settings.REDIS_URL),
    backend=str(settings.REDIS_URL),
    include=[
        "infra.celery.tasks",
        "apps.bot.tasks",
    ],
)

# Core Celery Configuration
celery_app.conf.update(
    # Task acknowledgment and prefetch
    task_acks_late=True,
    worker_prefetch_multiplier=2,  # UPDATED: Increase prefetch for better throughput
    # Default retry configuration (enhanced)
    task_default_retry_delay=30,  # 30 seconds base delay
    task_default_max_retries=5,  # Maximum 5 retries
    # Task time limits
    task_time_limit=600,  # 10 minutes hard limit
    task_soft_time_limit=540,  # 9 minutes soft limit
    # Queue management
    task_default_queue="default",
    task_routes={
        # Message tasks - high priority
        "infra.celery.tasks.send_message_task": {"queue": "messages"},
        "bot.tasks.send_scheduled_message": {"queue": "messages"},
        # Analytics tasks - medium priority
        "bot.tasks.update_post_views_task": {"queue": "analytics"},
        "infra.celery.tasks.process_analytics": {"queue": "analytics"},
        # Health and monitoring - low priority
        "bot.tasks.health_check_task": {"queue": "monitoring"},
        "infra.celery.tasks.cleanup_old_data": {"queue": "maintenance"},
        # Maintenance tasks
        "bot.tasks.cleanup_metrics_task": {"queue": "maintenance"},
        "bot.tasks.maintenance_cleanup": {"queue": "maintenance"},
    },
    # Serialization and compression (ENHANCED)
    task_serializer="msgpack",
    accept_content=["json", "msgpack"],
    result_serializer="msgpack",
    result_compression="gzip",  # NEW: Compress results to save memory
    task_compression="gzip",  # NEW: Compress task payloads
    result_expires=7200,  # UPDATED: Increase to 2 hours
    # Worker configuration (ENHANCED)
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    worker_send_task_events=True,
    worker_max_memory_per_child=200000,  # NEW: 200MB per worker child process
    # Broker connection pool settings (NEW)
    broker_pool_limit=10,  # NEW: Limit broker connections
    broker_connection_retry_on_startup=True,  # NEW: Retry broker connections
    broker_connection_max_retries=5,  # NEW: Max broker retry attempts
    # Result backend transport options (NEW)
    result_backend_transport_options={
        "retry_policy": {
            "timeout": 5.0,
            "max_retries": 3,
            "interval_start": 0.1,
            "interval_step": 0.2,
            "interval_max": 2.0,
        },
        "connection_pool_kwargs": {
            "max_connections": 20,
            "retry_on_timeout": True,
        },
    },
    # Broker transport options (NEW)
    broker_transport_options={
        "retry_policy": {
            "timeout": 5.0,
            "max_retries": 5,
            "interval_start": 0.1,
            "interval_step": 0.2,
            "interval_max": 2.0,
        },
        "connection_pool_kwargs": {
            "max_connections": 20,
            "retry_on_timeout": True,
        },
    },
    # Performance optimizations (NEW)
    task_always_eager=False,  # NEW: Ensure tasks run asynchronously
    task_eager_propagates=False,  # NEW: Don't propagate exceptions in eager mode
    result_persistent=True,  # NEW: Persist results to disk
    # Timezone
    timezone="UTC",
    enable_utc=True,
    # Beat schedule database
    beat_scheduler=(
        "django_celery_beat.schedulers:DatabaseScheduler"
        if hasattr(settings, "DATABASE_URL")
        else "celery.beat:PersistentScheduler"
    ),
)


def enhanced_retry_task(**opts) -> Callable:
    """
    Enhanced decorator for tasks with intelligent retry/backoff and monitoring.

    Features:
    - Exponential backoff with jitter
    - Comprehensive error handling
    - Task metrics and monitoring
    - Configurable retry strategies

    Usage:
        @enhanced_retry_task(bind=True, name="my_task")
        def my_task(self, param): ...
    """
    base_config = {
        "autoretry_for": (Exception,),
        "retry_backoff": 2,  # Exponential backoff: 2^retry_num
        "retry_backoff_max": 300,  # Max 5 minutes between retries
        "retry_jitter": True,  # Add random jitter to prevent thundering herd
        "max_retries": 5,  # Maximum retry attempts
        "default_retry_delay": 30,  # Base delay in seconds
    }
    base_config.update(opts)

    def decorator(func):
        task = celery_app.task(**base_config)(func)

        # Enhance apply_async with monitoring
        original_apply_async = task.apply_async

        def monitored_apply_async(*args, **kwargs):
            task_name = task.name
            logger.debug(f"Queueing task: {task_name}")

            # Add monitoring hook if available (optional for clean architecture)
            try:
                # Note: monitoring should be injected via DI in the future
                # For now, this is a soft dependency
                pass  # Monitoring disabled to maintain clean architecture
            except Exception:
                pass

            # Ensure original_apply_async is callable
            if callable(original_apply_async):
                return original_apply_async(*args, **kwargs)
            else:
                # Fallback if not callable
                return None

        task.apply_async = monitored_apply_async
        return task

    return decorator


def critical_message_task(**opts) -> Callable:
    """
    Special decorator for critical message tasks with aggressive retry strategy.

    Used for send_message_task and similar critical operations.
    """
    critical_config = {
        "autoretry_for": (Exception,),
        "retry_backoff": 2,  # Exponential backoff
        "retry_backoff_max": 600,  # Max 10 minutes for critical tasks
        "retry_jitter": True,  # Prevent thundering herd
        "max_retries": 5,  # 5 retries for critical tasks
        "default_retry_delay": 10,  # Start with 10 seconds for critical
    }
    critical_config.update(opts)

    return enhanced_retry_task(**critical_config)


# Celery Beat Schedule - Master Schedule Configuration
celery_app.conf.beat_schedule = {
    # High frequency tasks (every minute)
    "send-scheduled-messages": {
        "task": "bot.tasks.send_scheduled_message",
        "schedule": 60.0,  # Every minute
        "options": {"queue": "messages", "priority": 9},
    },
    # Medium frequency tasks (every 5 minutes)
    "update-post-views": {
        "task": "bot.tasks.update_post_views_task",
        "schedule": 300.0,  # Every 5 minutes
        "options": {"queue": "analytics", "priority": 5},
    },
    "health-check": {
        "task": "bot.tasks.health_check_task",
        "schedule": 300.0,  # Every 5 minutes
        "options": {"queue": "monitoring", "priority": 3},
    },
    # Low frequency tasks (hourly)
    "cleanup-metrics": {
        "task": "bot.tasks.cleanup_metrics_task",
        "schedule": 3600.0,  # Every hour
        "options": {"queue": "maintenance", "priority": 1},
    },
    "maintenance-cleanup": {
        "task": "bot.tasks.maintenance_cleanup",
        "schedule": 3600.0,  # Every hour
        "options": {"queue": "maintenance", "priority": 1},
    },
    "update-prometheus-metrics": {
        "task": "bot.tasks.update_prometheus_metrics",
        "schedule": 300.0,  # Every 5 minutes
        "options": {"queue": "monitoring", "priority": 3},
    },
    # Daily maintenance tasks
    "cleanup-old-data": {
        "task": "infra.celery.tasks.cleanup_old_data",
        "schedule": 86400.0,  # Daily
        "options": {"queue": "maintenance", "priority": 1},
    },
}


# Task Signal Handlers
@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **kwds):
    """Enhanced pre-run handler with detailed logging"""
    task_name = getattr(task, "name", "unknown") if task else "unknown"
    task_id_short = task_id[:8] if task_id else "unknown"
    logger.info(f"Starting task {task_name} (ID: {task_id_short}...)")

    # Record metrics if available
    try:
        # Monitoring disabled for clean architecture
        metrics.record_metric("celery_task_started", 1.0, {"task": str(task_name)})
    except ImportError:
        pass


@task_postrun.connect
def task_postrun_handler(
    sender=None,
    task_id=None,
    task=None,
    args=None,
    kwargs=None,
    retval=None,
    state=None,
    **kwds,
):
    """Enhanced post-run handler with comprehensive metrics"""
    task_name = getattr(task, "name", "unknown") if task else "unknown"
    task_id_short = task_id[:8] if task_id else "unknown"
    logger.info(f"Completed task {task_name} (ID: {task_id_short}...) with state: {state}")

    # Record detailed metrics
    try:
        # Monitoring disabled for clean architecture

        success = state == "SUCCESS"
        metrics.record_metric(
            "celery_task_completed",
            1.0,
            {
                "task": str(getattr(task, "name", "unknown")),
                "state": str(state),
                "success": str(success).lower(),
            },
        )
    except ImportError:
        pass


@task_failure.connect
def task_failure_handler(
    sender=None, task_id=None, exception=None, traceback=None, einfo=None, **kwds
):
    """Enhanced failure handler with error context"""
    sender_name = getattr(sender, "name", "unknown") if sender else "unknown"
    task_id_short = task_id[:8] if task_id else "unknown"
    logger.error(f"Task {sender_name} (ID: {task_id_short}...) failed: {exception}")

    # Simple error logging without complex error context
    if exception and isinstance(exception, Exception):
        logger.error(f"Task failure details: {str(exception)}")

    # Record failure metrics
    try:
        # Monitoring disabled for clean architecture
        metrics.record_metric("celery_task_failed", 1.0, {"task": str(sender_name)})
    except ImportError:
        pass


@worker_ready.connect
def worker_ready_handler(sender=None, **kwargs):
    """Worker ready handler with hostname tracking"""
    hostname = getattr(sender, "hostname", "unknown")
    logger.info(f"Celery worker {hostname} is ready")

    # Record worker metrics
    try:
        # Monitoring disabled for clean architecture

        metrics.record_metric("celery_worker_ready", 1.0, {"hostname": str(hostname or "unknown")})
    except ImportError:
        pass


def check_celery_health() -> dict[str, Any]:
    """
    Comprehensive Celery health check
    Returns detailed status about workers, queues, and overall health
    """
    try:
        inspect = celery_app.control.inspect()

        # Check worker stats
        stats = inspect.stats()
        if not stats:
            return {"status": "unhealthy", "reason": "No active workers"}

        active_workers = len(stats)

        # Check worker responsiveness
        ping_responses = inspect.ping()
        responsive_workers = len(ping_responses) if ping_responses else 0

        # Check queue lengths
        try:
            active_queues = inspect.active_queues()
            reserved_tasks = inspect.reserved()
        except Exception as e:
            logger.warning(f"Could not fetch queue information: {e}")
            active_queues = {}
            reserved_tasks = {}

        # Calculate health ratio
        health_ratio = responsive_workers / active_workers if active_workers > 0 else 0

        # Determine overall status
        if health_ratio >= 0.8:
            status = "healthy"
        elif health_ratio >= 0.5:
            status = "degraded"
        else:
            status = "unhealthy"

        return {
            "status": status,
            "active_workers": active_workers,
            "responsive_workers": responsive_workers,
            "health_ratio": health_ratio,
            "queues": len(active_queues) if active_queues else 0,
            "reserved_tasks": (
                sum(len(tasks) for tasks in reserved_tasks.values()) if reserved_tasks else 0
            ),
            "timestamp": str(__import__("datetime").datetime.utcnow()),
        }

    except Exception as e:
        logger.error(f"Celery health check failed: {e}")
        return {"status": "error", "error": str(e)}


# Register health check if monitoring is available
try:
    # Health monitoring disabled for clean architecture

    health_monitor.register_check("celery", check_celery_health, timeout=10)
    logger.info("Registered Celery health check")
except ImportError:
    logger.warning("Could not register Celery health check (monitoring module not available)")


if __name__ == "__main__":
    celery_app.start()
