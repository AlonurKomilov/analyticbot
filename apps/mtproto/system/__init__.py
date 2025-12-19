"""
System MTProto - ENV-configured MTProto services.

This module contains the system-level MTProto functionality that uses
ENV-configured credentials (TELEGRAM_API_ID, TELEGRAM_API_HASH).

Components:
- __main__.py: Entry point for MTProto application
- config.py: MTProtoSettings from environment
- health.py: Health check endpoints
- collectors/: History and updates collectors
- tasks/: Celery background tasks
- services/: Data collection orchestration
- di/: Dependency injection container
"""

from apps.mtproto.system.config import MTProtoSettings

__all__ = [
    "MTProtoSettings",
]
