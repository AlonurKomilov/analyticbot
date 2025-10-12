"""
Shared API Routers - Framework-Independent API Endpoints

Routers in this module provide API endpoints that can be used
by both main API and Bot API layers.

Moved from apps.bot.api as part of Phase 2 Option B
to enable shared access and break cross-layer dependencies.
"""

from apps.shared.api.content_protection_router import router as content_protection_router
from apps.shared.api.payment_router import router as payment_router

__all__ = [
    "content_protection_router",
    "payment_router",
]
