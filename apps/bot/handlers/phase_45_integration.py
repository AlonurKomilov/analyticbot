"""
Phase 4.5 Integration Bridge
Connects new export/alert/share handlers with existing analytics handlers
"""

from aiogram import Router

# Import existing analytics v2 handlers
from apps.bot.handlers.analytics_v2 import router as analytics_router

# Import new Phase 4.5 handlers
from apps.bot.handlers.exports import router as exports_router
from apps.bot.handlers.alerts import router as alerts_router

# Create unified router
phase_45_router = Router()

# Include all routers
phase_45_router.include_router(analytics_router)  # Existing analytics UI
phase_45_router.include_router(exports_router)    # New export processing  
phase_45_router.include_router(alerts_router)     # New alert management

# Export for easy import in main bot
__all__ = ['phase_45_router']
