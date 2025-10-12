"""
Backward Compatibility Wrapper for Content Protection Router

DEPRECATED: This module is maintained for backward compatibility only.
New code should import from apps.shared.api instead.

Moved to apps.shared.api.content_protection_router as part of Phase 2 Option B
to enable shared access between API and Bot layers.
"""

# Import from shared location for backward compatibility
from apps.shared.api.content_protection_router import router

__all__ = ["router"]
