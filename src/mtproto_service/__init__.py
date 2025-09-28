"""
MTProto Service
==============
Clean architecture implementation of MTProto/Telegram integration.

This service handles:
- Telegram client connection and management
- Message history synchronization
- Statistics collection and metrics
- Health checks and monitoring

Architecture:
- Domain: MTProto entities and value objects
- Application: Use cases and business logic
- Infrastructure: Telethon adapters, collectors, tasks
- Presentation: HTTP APIs and interfaces (if any)
"""

# Re-export main components for backward compatibility

__version__ = "1.0.0"
__all__ = [
    # Main exports will be defined as the service evolves
]
