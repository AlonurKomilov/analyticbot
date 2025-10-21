"""
Content Protection Router Aggregation

Combines all content protection sub-routers into a single unified router.

Structure:
- watermarking.py: Image watermarking workflows (6 handlers)
- premium_features.py: Premium emoji and upgrades (3 handlers)
- theft_detection.py: Content theft analysis (2 handlers)
- usage_tracking.py: Feature usage statistics (1 handler)
"""

import logging

from aiogram import Router

from . import premium_features, theft_detection, usage_tracking, watermarking

logger = logging.getLogger(__name__)

# Create main router
router = Router()

# Include all sub-routers
router.include_router(watermarking.router)
router.include_router(premium_features.router)
router.include_router(theft_detection.router)
router.include_router(usage_tracking.router)

logger.info("Content protection router initialized with 4 sub-modules (12+ handlers)")
