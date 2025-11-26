"""
Celery Tasks Module

All Celery task definitions organized by domain.
Uses Clean Architecture with protocol dependency injection.
"""

from . import bot_tasks, maintenance_tasks, ml_tasks

__all__ = ["bot_tasks", "ml_tasks", "maintenance_tasks"]
