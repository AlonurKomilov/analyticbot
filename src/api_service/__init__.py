"""
API Service Domain
==================
Core API service functionality with clean architecture.

Layers:
- Domain: Core business logic and entities
- Application: Use cases and application services  
- Infrastructure: External integrations and persistence
- Presentation: HTTP endpoints and request handling
"""

# Safe imports with error handling
try:
    from .presentation.routers import *
    from .application.services import *
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Some API service imports not available: {e}")
    IMPORTS_AVAILABLE = False

__version__ = "1.0.0"
__domain__ = "api_service"
__all__ = ["IMPORTS_AVAILABLE"]
