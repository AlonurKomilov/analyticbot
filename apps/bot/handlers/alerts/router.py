"""
Alert Handlers Router
Aggregates all alert-related handlers
"""

from aiogram import Router

from apps.bot.handlers.alerts import creation, display, management, presets

# Create main router
router = Router()

# Include all sub-routers
router.include_router(display.router)
router.include_router(creation.router)
router.include_router(management.router)
router.include_router(presets.router)
