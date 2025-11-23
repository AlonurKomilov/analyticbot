"""
Channels Microservice

Channel Management - Complete CRUD operations, lifecycle, and status endpoints.

Structure:
- admin_status.py: Bot/MTProto admin status checking
- validation.py: Channel validation
- crud.py: CRUD operations (list, create, read, update, delete)
- lifecycle.py: Activate/deactivate channels
- status.py: Channel status and statistics
- models.py: Pydantic request/response models
- deps.py: Shared dependencies
- router.py: Main router aggregator

Status: Complete refactoring - all 13 endpoints migrated from channels_router.py (906 lines).
"""

from .router import router

__all__ = ["router"]
