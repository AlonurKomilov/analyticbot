"""
Compatibility Redirect: auth.py
========================================
This file provides backward compatibility by redirecting to the clean architecture implementation.
Original implementation moved to: src.api_service.presentation.middleware.auth
"""

# Import from clean architecture location
try:
    from src.api_service.presentation.middleware.auth import *
    print("✅ Using clean architecture implementation from src.api_service.presentation.middleware.auth")
except ImportError as e:
    print(f"⚠️  Could not import from src.api_service.presentation.middleware.auth: {e}")
    print("🔄 This may indicate the clean architecture module needs attention")
    raise ImportError(f"Clean architecture module not available: src.api_service.presentation.middleware.auth") from e

# Re-export for compatibility
# All exports available via import *

