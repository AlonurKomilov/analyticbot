"""
Compatibility Redirect: main.py
========================================
This file provides backward compatibility by redirecting to the clean architecture implementation.
Original implementation moved to: src.api_service.presentation.main
"""

# Import from clean architecture location
try:
    from src.api_service.presentation.routers.main import app

    print(
        "✅ Using clean architecture implementation from src.api_service.presentation.routers.main"
    )
except ImportError as e:
    print(f"⚠️  Could not import from src.api_service.presentation.routers.main: {e}")
    print("🔄 This may indicate the clean architecture module needs attention")
    raise ImportError(
        "Clean architecture module not available: src.api_service.presentation.routers.main"
    ) from e

# Re-export for compatibility
__all__ = ["app", "create_app"]
