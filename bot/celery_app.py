import logging
from celery import Celery
from celery.signals import task_prerun, task_postrun, task_failure, worker_ready

from bot.config import settings
from bot.utils.error_handler import ErrorHandler, ErrorContext
from bot.utils.monitoring import metrics

# Setup logging
logger = logging.getLogger(__name__)

# Celery app creation with enhanced configuration
celery_app = Celery(
    "analytic_bot_tasks",
    broker=settings.REDIS_URL.unicode_string(),
    backend=settings.REDIS_URL.unicode_string(),
    include=["bot.tasks"],
)

# Enhanced Celery configuration
celery_app.conf.update(
    # Task acknowledgment and delivery
    task_acks_late=True,  # Ensure redelivery on worker crash
    worker_prefetch_multiplier=1,  # Fair dispatch
    
    # Retry configuration
    task_default_retry_delay=settings.TASK_RETRY_DELAY,
    task_default_max_retries=settings.TASK_MAX_RETRIES,
    
    # Time limits
    task_time_limit=600,  # 10 minutes hard limit
    task_soft_time_limit=540,  # 9 minutes soft limit
    
    # Queue configuration
    task_default_queue="default",
    task_routes={
        'bot.tasks.send_scheduled_message': {'queue': 'messages'},
        'bot.tasks.update_post_views_task': {'queue': 'analytics'},
        'bot.tasks.health_check_task': {'queue': 'monitoring'},
    },
    
    # Serialization
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    
    # Worker configuration
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    
    # Timezone
    timezone='UTC',
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
        retry_backoff=True,          # Exponential backoff: 2^n seconds
        retry_backoff_max=300,       # Max 5 minutes between retries
        retry_jitter=True,           # Add randomness to prevent thundering herd
        max_retries=settings.TASK_MAX_RETRIES,
        default_retry_delay=settings.TASK_RETRY_DELAY,
    )
    base.update(opts)
    
    def decorator(func):
        task = celery_app.task(**base)(func)
        
        # Add monitoring wrapper
        original_apply_async = task.apply_async
        
        def monitored_apply_async(*args, **kwargs):
            task_name = task.name
            metrics.record_metric(f"celery_task_queued", 1.0, {"task": task_name})
            return original_apply_async(*args, **kwargs)
        
        task.apply_async = monitored_apply_async
        return task
    
    return decorator


# Celery Beat schedule with enhanced monitoring
celery_app.conf.beat_schedule = {
    "send-scheduled-messages": {
        "task": "bot.tasks.send_scheduled_message",
        "schedule": 60.0,  # Every 60 seconds
        "options": {"queue": "messages"},
    },
    "update-post-views": {
        "task": "bot.tasks.update_post_views_task",
        "schedule": float(settings.ANALYTICS_UPDATE_INTERVAL),  # Configurable interval
        "options": {"queue": "analytics"},
    },
    "health-check": {
        "task": "bot.tasks.health_check_task",
        "schedule": float(settings.HEALTH_CHECK_INTERVAL),  # Configurable health checks
        "options": {"queue": "monitoring"},
    },
    "cleanup-metrics": {
        "task": "bot.tasks.cleanup_metrics_task",
        "schedule": 3600.0,  # Every hour
        "options": {"queue": "maintenance"},
    },
    "maintenance-cleanup": {
        "task": "bot.tasks.maintenance_cleanup",
        "schedule": 3600.0,  # Every hour
        "options": {"queue": "maintenance"},
    },
    "update-prometheus-metrics": {
        "task": "bot.tasks.update_prometheus_metrics",
        "schedule": 300.0,  # Every 5 minutes
        "options": {"queue": "monitoring"},
    },
}


# Celery signals for monitoring and logging
@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **kwds):
    """Called before task execution"""
    logger.info(f"Starting task {task.name} (ID: {task_id})")
    metrics.record_metric("celery_task_started", 1.0, {"task": task.name})


@task_postrun.connect 
def task_postrun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, 
                        retval=None, state=None, **kwds):
    """Called after task execution"""
    logger.info(f"Completed task {task.name} (ID: {task_id}) with state: {state}")
    
    success = state == "SUCCESS"
    metrics.record_metric("celery_task_completed", 1.0, {
        "task": task.name,
        "state": state,
        "success": str(success).lower()
    })


@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, traceback=None, einfo=None, **kwds):
    """Called when task fails"""
    context = (ErrorContext()
              .add("task_name", sender.name)
              .add("task_id", task_id)
              .add("celery_task", True))
    
    ErrorHandler.log_error(exception, context)
    metrics.record_metric("celery_task_failed", 1.0, {"task": sender.name})


@worker_ready.connect
def worker_ready_handler(sender=None, **kwargs):
    """Called when worker is ready"""
    logger.info(f"Celery worker {sender.hostname} is ready")
    metrics.record_metric("celery_worker_ready", 1.0, {"hostname": sender.hostname})


# Health check function for Celery
def check_celery_health():
    """Check if Celery workers are responsive"""
    try:
        # Check if workers are available
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        
        if not stats:
            return {"status": "unhealthy", "reason": "No active workers"}
        
        # Check worker health
        active_workers = len(stats)
        ping_responses = inspect.ping()
        responsive_workers = len(ping_responses) if ping_responses else 0
        
        health_ratio = responsive_workers / active_workers if active_workers > 0 else 0
        
        if health_ratio >= 0.8:  # 80% of workers responsive
            return {
                "status": "healthy",
                "active_workers": active_workers,
                "responsive_workers": responsive_workers,
                "health_ratio": health_ratio
            }
        elif health_ratio >= 0.5:  # 50% of workers responsive
            return {
                "status": "degraded",
                "active_workers": active_workers, 
                "responsive_workers": responsive_workers,
                "health_ratio": health_ratio
            }
        else:
            return {
                "status": "unhealthy",
                "active_workers": active_workers,
                "responsive_workers": responsive_workers,
                "health_ratio": health_ratio,
                "reason": "Too many unresponsive workers"
            }
            
    except Exception as e:
        return {"status": "error", "error": str(e)}


# Register Celery health check with monitoring system
try:
    from bot.utils.monitoring import health_monitor
    health_monitor.register_check('celery', check_celery_health, timeout=10)
except ImportError:
    logger.warning("Could not register Celery health check (monitoring module not available)")


if __name__ == '__main__':
    # For development/testing
    celery_app.start()
