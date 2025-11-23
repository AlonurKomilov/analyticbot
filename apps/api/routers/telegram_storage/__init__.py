"""
Storage Microservice

Telegram Storage Management - zero-cost file storage using user's own Telegram channels.

Structure:
- channels.py: Channel connection and validation
- files.py: File upload, list, download, delete, forward
- models.py: Pydantic request/response models
- deps.py: Shared dependencies
- router.py: Main router aggregator
"""

from .router import router

__all__ = ["router"]
