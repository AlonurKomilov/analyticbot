"""
Phase 2 Bot Microhandlers Integration Bridge
============================================

Connects new focused bot microhandlers following Phase 1 microrouter pattern.
Replaces monolithic analytics_v2.py (714 lines) with 3 focused microhandlers.

Part of Phase 2 implementation:
- bot_analytics_handler.py (~500 lines) - Pure analytics domain
- bot_export_handler.py (~100 lines) - Pure export domain
- bot_alerts_handler.py (~100 lines) - Pure alerts domain

Architecture: Clean domain separation following successful Phase 1 microrouter implementation
"""

from aiogram import Router

# Import legacy Phase 4.5 handlers (to be consolidated later)
from apps.bot.handlers.alerts import router as legacy_alerts_router
from apps.bot.handlers.bot_alerts_handler import router as bot_alerts_router

# Import Phase 2 bot microhandlers (replaces monolithic analytics_v2.py)
from apps.bot.handlers.bot_analytics_handler import router as bot_analytics_router
from apps.bot.handlers.bot_export_handler import router as bot_export_router
from apps.bot.handlers.exports import router as legacy_exports_router

# Create unified microhandlers router
phase_45_router = Router()

# Include Phase 2 bot microhandlers (priority over legacy handlers)
phase_45_router.include_router(bot_analytics_router)  # Analytics domain microhandler
phase_45_router.include_router(bot_export_router)  # Export domain microhandler
phase_45_router.include_router(bot_alerts_router)  # Alerts domain microhandler

# Include legacy handlers for compatibility (lower priority)
phase_45_router.include_router(legacy_exports_router)  # Legacy export processing
phase_45_router.include_router(legacy_alerts_router)  # Legacy alert management

# Export for easy import in main bot
__all__ = ["phase_45_router"]
