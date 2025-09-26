"""
Compatibility Redirect: csv_v2.py
========================================
This file provides backward compatibility by redirecting to the clean architecture implementation.
Original implementation moved to: src.api_service.infrastructure.external.csv_v2
"""

# Import from clean architecture location
try:
    from src.api_service.infrastructure.external.csv_v2 import *
    print("✅ Using clean architecture implementation from src.api_service.infrastructure.external.csv_v2")
except ImportError as e:
    print(f"⚠️  Could not import from src.api_service.infrastructure.external.csv_v2: {e}")
    print("🔄 This may indicate the clean architecture module needs attention")
    raise ImportError(f"Clean architecture module not available: src.api_service.infrastructure.external.csv_v2") from e

# Re-export for compatibility
# All exports available via import *

