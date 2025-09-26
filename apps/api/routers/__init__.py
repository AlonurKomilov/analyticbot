"""
Compatibility Redirect: __init__.py
========================================
This file provides backward compatibility by redirecting to the clean architecture implementation.
Original implementation moved to: src.bot_service.infrastructure.database.__init__
"""

# Import from clean architecture location
try:
    from src.bot_service.infrastructure.database.__init__ import *
    print("✅ Using clean architecture implementation from src.bot_service.infrastructure.database.__init__")
except ImportError as e:
    print(f"⚠️  Could not import from src.bot_service.infrastructure.database.__init__: {e}")
    print("🔄 This may indicate the clean architecture module needs attention")
    raise ImportError(f"Clean architecture module not available: src.bot_service.infrastructure.database.__init__") from e

# Re-export for compatibility
# All exports available via import *

