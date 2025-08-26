"""
FastAPI Routers Package

This package contains all the modular routers for the analyticbot API.
Each router handles a specific domain (analytics, security, AI/ML, etc.)
and can be easily included in the main FastAPI application.
"""

from .analytics_router import router as analytics_router
from .media_router import router as media_router
from .admin_router import router as admin_router

__all__ = ["analytics_router", "media_router", "admin_router"]
