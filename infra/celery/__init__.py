"""
Celery Infrastructure Module
Master scheduler and task queue management

This module provides:
- Centralized Celery configuration with retry/backoff strategies
- Enhanced task decorators for different priority levels
- Production-ready task implementations
- Comprehensive health monitoring
"""

from .celery_app import (
    celery_app,
    check_celery_health,
    critical_message_task,
    enhanced_retry_task,
)
from .tasks import (
    AVAILABLE_TASKS,
    cleanup_old_data,
    health_check_task,
    process_analytics,
    scheduled_broadcast,
    send_message_task,
)

__all__ = [
    # Core Celery app and decorators
    "celery_app",
    "enhanced_retry_task",
    "critical_message_task",
    "check_celery_health",
    # Task functions
    "send_message_task",
    "process_analytics",
    "cleanup_old_data",
    "health_check_task",
    "scheduled_broadcast",
    "AVAILABLE_TASKS",
]
