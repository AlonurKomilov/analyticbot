"""
User Bot Management - Multi-tenant bot instances for users.

This module manages user-owned bots that are added via the frontend.
Credentials are stored encrypted in the database (user_bot_credentials table).

Components:
- bot_manager.py: Manages all user bot instances with LRU caching
- user_bot_instance.py: Individual user bot instance
- circuit_breaker.py: Fault tolerance for user bots
- global_rate_limiter.py: Rate limiting across user bots
- session_pool.py: Shared session pool for efficiency
- bot_health.py: Health monitoring for user bots
"""

from .bot_manager import MultiTenantBotManager, get_bot_manager, initialize_bot_manager
from .user_bot_instance import UserBotInstance

__all__ = [
    "UserBotInstance",
    "MultiTenantBotManager",
    "get_bot_manager",
    "initialize_bot_manager",
]
