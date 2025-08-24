"""
Celery Application Configuration - Master Scheduler
Production-ready Celery setup with retry/backoff strategies
"""

import logging
from typing import Dict, Any

from celery import Celery
from celery.signals import task_failure, task_postrun, task_prerun, worker_ready

# Import from centralized configuration
from config.settings import Settings
settings = Settings()

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
    worker_prefetch_multiplier=1,
    
    # Default retry configuration (enhanced)
    task_default_retry_delay=30,  # 30 seconds base delay
    task_default_max_retries=5,   # Maximum 5 retries
    
    # Task time limits
    task_time_limit=600,      # 10 minutes hard limit
    task_soft_time_limit=540, # 9 minutes soft limit
    
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
    
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    result_expires=3600,  # 1 hour
    
    # Worker configuration
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    worker_send_task_events=True,
    
    # Timezone
    timezone="UTC",
    enable_utc=True,
    
    # Beat schedule database
    beat_scheduler="django_celery_beat.schedulers:DatabaseScheduler" if hasattr(settings, "DATABASE_URL") else "celery.beat:PersistentScheduler",
)


def enhanced_retry_task(**opts) -> callable:
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
        "retry_backoff": 2,          # Exponential backoff: 2^retry_num
        "retry_backoff_max": 300,    # Max 5 minutes between retries
        "retry_jitter": True,        # Add random jitter to prevent thundering herd
        "max_retries": 5,            # Maximum retry attempts
        "default_retry_delay": 30,   # Base delay in seconds
    }
    base_config.update(opts)
    
    def decorator(func):
        task = celery_app.task(**base_config)(func)
        
        # Enhance apply_async with monitoring
        original_apply_async = task.apply_async
        
        def monitored_apply_async(*args, **kwargs):
            task_name = task.name
            logger.debug(f"Queueing task: {task_name}")
            
            # Add monitoring hook if available
            try:
                from apps.bot.utils.monitoring import metrics
                metrics.record_metric("celery_task_queued", 1.0, {"task": task_name})
            except ImportError:
                pass
                
            return original_apply_async(*args, **kwargs)
        
        task.apply_async = monitored_apply_async
        return task
    
    return decorator


def critical_message_task(**opts) -> callable:
    """
    Special decorator for critical message tasks with aggressive retry strategy.
    
    Used for send_message_task and similar critical operations.
    """
    critical_config = {
        "autoretry_for": (Exception,),
        "retry_backoff": 2,          # Exponential backoff
        "retry_backoff_max": 600,    # Max 10 minutes for critical tasks
        "retry_jitter": True,        # Prevent thundering herd
        "max_retries": 5,            # 5 retries for critical tasks
        "default_retry_delay": 10,   # Start with 10 seconds for critical
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
    logger.info(f"Starting task {task.name} (ID: {task_id[:8]}...)")
    
    # Record metrics if available
    try:
        from apps.bot.utils.monitoring import metrics
        metrics.record_metric("celery_task_started", 1.0, {"task": task.name})
    except ImportError:
        pass


@task_postrun.connect
def task_postrun_handler(
    sender=None, task_id=None, task=None, args=None, kwargs=None, 
    retval=None, state=None, **kwds
):
    """Enhanced post-run handler with comprehensive metrics"""
    logger.info(f"Completed task {task.name} (ID: {task_id[:8]}...) with state: {state}")
    
    # Record detailed metrics
    try:
        from apps.bot.utils.monitoring import metrics
        success = state == "SUCCESS"
        metrics.record_metric(
            "celery_task_completed", 1.0,
            {"task": task.name, "state": state, "success": str(success).lower()}
        )
    except ImportError:
        pass


@task_failure.connect
def task_failure_handler(
    sender=None, task_id=None, exception=None, traceback=None, einfo=None, **kwds
):
    """Enhanced failure handler with error context"""
    logger.error(f"Task {sender.name} (ID: {task_id[:8]}...) failed: {exception}")
    
    # Create error context if available
    try:
        from apps.bot.utils.error_handler import ErrorContext, ErrorHandler
        context = (
            ErrorContext()
            .add("task_name", sender.name)
            .add("task_id", task_id)
            .add("celery_task", True)
        )
        ErrorHandler.log_error(exception, context)
    except ImportError:
        logger.error(f"Error handling task failure: {exception}", exc_info=True)
    
    # Record failure metrics
    try:
        from apps.bot.utils.monitoring import metrics
        metrics.record_metric("celery_task_failed", 1.0, {"task": sender.name})
    except ImportError:
        pass


@worker_ready.connect
def worker_ready_handler(sender=None, **kwargs):
    """Worker ready handler with hostname tracking"""
    hostname = getattr(sender, 'hostname', 'unknown')
    logger.info(f"Celery worker {hostname} is ready")
    
    # Record worker metrics
    try:
        from apps.bot.utils.monitoring import metrics
        metrics.record_metric("celery_worker_ready", 1.0, {"hostname": hostname})
    except ImportError:
        pass


def check_celery_health() -> Dict[str, Any]:
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
            "reserved_tasks": sum(len(tasks) for tasks in reserved_tasks.values()) if reserved_tasks else 0,
            "timestamp": str(__import__("datetime").datetime.utcnow()),
        }
        
    except Exception as e:
        logger.error(f"Celery health check failed: {e}")
        return {"status": "error", "error": str(e)}


# Register health check if monitoring is available
try:
    from apps.bot.utils.monitoring import health_monitor
    health_monitor.register_check("celery", check_celery_health, timeout=10)
    logger.info("Registered Celery health check")
except ImportError:
    logger.warning("Could not register Celery health check (monitoring module not available)")


if __name__ == "__main__":
    celery_app.start()
