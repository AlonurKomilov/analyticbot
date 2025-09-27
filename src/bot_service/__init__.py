"""
Bot Service Domain
==================
Telegram bot service with clean architecture.
"""

# Safe imports with error handling
try:
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Some bot service imports not available: {e}")
    IMPORTS_AVAILABLE = False

__version__ = "1.0.0"
__domain__ = "bot_service"
__all__ = ["IMPORTS_AVAILABLE"]
