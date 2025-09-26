"""
Compatibility Redirect: auth_router.py
========================================
This file provides backward compatibility by redirecting to the clean architecture implementation.
Original implementation moved to: src.api_service.presentation.routers.auth_router
"""

# Import from clean architecture location
try:
    from src.api_service.presentation.routers.auth_router import *
    print("✅ Using clean architecture implementation from src.api_service.presentation.routers.auth_router")
except ImportError as e:
    print(f"⚠️  Could not import from src.api_service.presentation.routers.auth_router: {e}")
    print("🔄 This may indicate the clean architecture module needs attention")
    raise ImportError(f"Clean architecture module not available: src.api_service.presentation.routers.auth_router") from e

# Re-export for compatibility
# All exports available via import *

