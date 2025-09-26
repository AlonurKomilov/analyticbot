"""
Bot Microhandlers Integration
=============================

Integrates focused bot microhandlers following clean architecture principles.
Replaces monolithic analytics_v2.py (714 lines) with 3 focused microhandlers.

Microhandlers included:
- bot_analytics_handler.py - Pure analytics domain (command, display, navigation)
- bot_export_handler.py - Pure export domain (formats, sharing)
- bot_alerts_handler.py - Pure alerts domain (subscriptions, management)

Architecture: Clean domain separation with focused responsibilities
"""

from aiogram import Router

# Import bot microhandlers (replaces monolithic analytics_v2.py)
from src.bot_service.handlers.bot_analytics_handler import router as bot_analytics_router
from src.bot_service.handlers.bot_export_handler import router as bot_export_router
from src.bot_service.handlers.bot_alerts_handler import router as bot_alerts_router

# Import legacy handlers for compatibility (to be consolidated later)
from src.bot_service.handlers.alerts import router as legacy_alerts_router
from src.bot_service.handlers.exports import router as legacy_exports_router

# Create unified bot microhandlers router
bot_microhandlers_router = Router()

# Include bot microhandlers (priority over legacy handlers)
bot_microhandlers_router.include_router(bot_analytics_router)  # Analytics domain microhandler
bot_microhandlers_router.include_router(bot_export_router)     # Export domain microhandler
bot_microhandlers_router.include_router(bot_alerts_router)     # Alerts domain microhandler

# Include legacy handlers for compatibility (lower priority)
bot_microhandlers_router.include_router(legacy_exports_router)  # Legacy export processing
bot_microhandlers_router.include_router(legacy_alerts_router)   # Legacy alert management

# Export for easy import in main bot
__all__ = ["bot_microhandlers_router"]
