"""
Workers Module - Celery Task Queue Application

This module contains the Celery application and task definitions.
Celery has been moved from infra/ to apps/ layer because:
- Celery is application orchestration (like FastAPI, Aiogram)
- It coordinates business workflows and tasks
- It needs to import from monitoring, services, and repositories
- Infrastructure layer should only provide base services

Migration: Moved from infra/celery/celery_app.py (Oct 2025)
"""

from .celery_app import celery_app

__version__ = "1.0.0"

__all__ = ["celery_app"]
