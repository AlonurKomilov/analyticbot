"""
API Module Compatibility Layer
==============================
Redirects to the new clean architecture location in src/api_service/

This module provides backward compatibility for existing imports while
the system transitions to clean architecture.
"""

# Import from new clean architecture location
try:
    # Import all main API functionality from clean architecture
    from src.api_service.presentation.routers import *
    from src.api_service.application.services import *
    from src.api_service.domain.models import *
    from src.api_service.application.dtos import *
    
    print("✅ Using migrated API from src/api_service (clean architecture)")
    
    # Provide legacy-compatible access patterns
    import src.api_service.presentation.routers as routers
    import src.api_service.application.services as services  
    import src.api_service.domain.models as models
    import src.api_service.application.dtos as schemas
    
    # Legacy aliases for backward compatibility
    routes = routers
    handlers = services
    
except ImportError as e:
    print(f"⚠️  Could not import from new location: {e}")
    print("🔄 Falling back to local API implementation")
    
    # Fallback to local implementation if needed
    try:
        # Import whatever is available locally
        from . import *
    except ImportError:
        print("❌ No API implementation available")

# Export common API functionality
__all__ = [
    'routers',
    'services', 
    'models',
    'schemas',
    'routes',  # Legacy alias
    'handlers',  # Legacy alias
]
