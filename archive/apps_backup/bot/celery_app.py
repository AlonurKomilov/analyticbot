# apps/bot/celery_app.py
"""
DEPRECATED: Legacy re-export of Celery app.
New code should import directly from infra.celery.celery_app
This module exists only for backward compatibility and will be removed in a future version.
"""

try:
    # Prefer re-export if resilient_task exists
    from infra.celery.celery_app import celery_app as app
    from infra.celery.celery_app import resilient_task
except ImportError:
    # Fallback: import only app and provide a thin decorator
    from infra.celery.celery_app import celery_app as app  # type: ignore

    def resilient_task(*dargs, **dkwargs):
        # Delegate to celery_app.task() to keep signature behavior
        return app.task(*dargs, **dkwargs)


__all__ = ["resilient_task", "app"]
