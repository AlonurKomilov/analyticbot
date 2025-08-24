import logging

from celery import Celery
from celery.signals import task_failure, task_postrun, task_prerun, worker_ready

from apps.bot.config import settings
from apps.bot.utils.error_handler import ErrorContext, ErrorHandler
from apps.bot.utils.monitoring import metrics

logger = logging.getLogger(__name__)
celery_app = Celery(
    "analytic_bot_tasks",
    broker=settings.REDIS_URL.unicode_string(),
    backend=settings.REDIS_URL.unicode_string(),
    include=["bot.tasks"],
)
celery_app.conf.update(
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_default_retry_delay=settings.TASK_RETRY_DELAY,
    task_default_max_retries=settings.TASK_MAX_RETRIES,
    task_time_limit=600,
    task_soft_time_limit=540,
    task_default_queue="default",
    task_routes={
        "bot.tasks.send_scheduled_message": {"queue": "messages"},
        "bot.tasks.update_post_views_task": {"queue": "analytics"},
        "bot.tasks.health_check_task": {"queue": "monitoring"},
    },
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    result_expires=3600,
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    timezone="UTC",
    enable_utc=True,
)


def resilient_task(**opts):
    """
    Enhanced decorator for tasks with intelligent retry/backoff defaults and monitoring.

    Usage:
        @resilient_task(bind=True, name="foo")
        def foo(self): ...
    """
    base = dict(
        autoretry_for=(Exception,),
        retry_backoff=True,
        retry_backoff_max=300,
        retry_jitter=True,
        max_retries=settings.TASK_MAX_RETRIES,
        default_retry_delay=settings.TASK_RETRY_DELAY,
    )
    base.update(opts)

    def decorator(func):
        task = celery_app.task(**base)(func)
        original_apply_async = task.apply_async

        def monitored_apply_async(*args, **kwargs):
            task_name = task.name
            metrics.record_metric("celery_task_queued", 1.0, {"task": task_name})
            return original_apply_async(*args, **kwargs)

        task.apply_async = monitored_apply_async
        return task

    return decorator


celery_app.conf.beat_schedule = {
    "send-scheduled-messages": {
        "task": "bot.tasks.send_scheduled_message",
        "schedule": 60.0,
        "options": {"queue": "messages"},
    },
    "update-post-views": {
        "task": "bot.tasks.update_post_views_task",
        "schedule": float(settings.ANALYTICS_UPDATE_INTERVAL),
        "options": {"queue": "analytics"},
    },
    "health-check": {
        "task": "bot.tasks.health_check_task",
        "schedule": float(settings.HEALTH_CHECK_INTERVAL),
        "options": {"queue": "monitoring"},
    },
    "cleanup-metrics": {
        "task": "bot.tasks.cleanup_metrics_task",
        "schedule": 3600.0,
        "options": {"queue": "maintenance"},
    },
    "maintenance-cleanup": {
        "task": "bot.tasks.maintenance_cleanup",
        "schedule": 3600.0,
        "options": {"queue": "maintenance"},
    },
    "update-prometheus-metrics": {
        "task": "bot.tasks.update_prometheus_metrics",
        "schedule": 300.0,
        "options": {"queue": "monitoring"},
    },
}


@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **kwds):
    """Called before task execution"""
    logger.info(f"Starting task {task.name} (ID: {task_id})")
    metrics.record_metric("celery_task_started", 1.0, {"task": task.name})


@task_postrun.connect
def task_postrun_handler(
    sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, state=None, **kwds
):
    """Called after task execution"""
    logger.info(f"Completed task {task.name} (ID: {task_id}) with state: {state}")
    success = state == "SUCCESS"
    metrics.record_metric(
        "celery_task_completed",
        1.0,
        {"task": task.name, "state": state, "success": str(success).lower()},
    )


@task_failure.connect
def task_failure_handler(
    sender=None, task_id=None, exception=None, traceback=None, einfo=None, **kwds
):
    """Called when task fails"""
    context = (
        ErrorContext()
        .add("task_name", sender.name)
        .add("task_id", task_id)
        .add("celery_task", True)
    )
    ErrorHandler.log_error(exception, context)
    metrics.record_metric("celery_task_failed", 1.0, {"task": sender.name})


@worker_ready.connect
def worker_ready_handler(sender=None, **kwargs):
    """Called when worker is ready"""
    logger.info(f"Celery worker {sender.hostname} is ready")
    metrics.record_metric("celery_worker_ready", 1.0, {"hostname": sender.hostname})


def check_celery_health():
    """Check if Celery workers are responsive"""
    try:
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        if not stats:
            return {"status": "unhealthy", "reason": "No active workers"}
        active_workers = len(stats)
        ping_responses = inspect.ping()
        responsive_workers = len(ping_responses) if ping_responses else 0
        health_ratio = responsive_workers / active_workers if active_workers > 0 else 0
        if health_ratio >= 0.8:
            return {
                "status": "healthy",
                "active_workers": active_workers,
                "responsive_workers": responsive_workers,
                "health_ratio": health_ratio,
            }
        elif health_ratio >= 0.5:
            return {
                "status": "degraded",
                "active_workers": active_workers,
                "responsive_workers": responsive_workers,
                "health_ratio": health_ratio,
            }
        else:
            return {
                "status": "unhealthy",
                "active_workers": active_workers,
                "responsive_workers": responsive_workers,
                "health_ratio": health_ratio,
                "reason": "Too many unresponsive workers",
            }
    except Exception as e:
        return {"status": "error", "error": str(e)}


try:
    from apps.bot.utils.monitoring import health_monitor

    health_monitor.register_check("celery", check_celery_health, timeout=10)
except ImportError:
    logger.warning("Could not register Celery health check (monitoring module not available)")
if __name__ == "__main__":
    celery_app.start()
