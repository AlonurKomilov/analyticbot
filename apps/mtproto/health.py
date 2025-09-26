"""
Compatibility Redirect: health.py
========================================
This file provides backward compatibility by redirecting to the clean architecture implementation.
Original implementation moved to: src.mtproto_service.infrastructure.health
"""

# Import from clean architecture location
try:
    from src.mtproto_service.infrastructure.health import *
    print("✅ Using clean architecture implementation from src.mtproto_service.infrastructure.health")
except ImportError as e:
    print(f"⚠️  Could not import from src.mtproto_service.infrastructure.health: {e}")
    print("🔄 This may indicate the clean architecture module needs attention")
    raise ImportError(f"Clean architecture module not available: src.mtproto_service.infrastructure.health") from e

# Re-export for compatibility
# All exports available via import *

