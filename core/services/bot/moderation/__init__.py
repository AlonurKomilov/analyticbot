"""
Bot Moderation - Pluggable marketplace services for user bots

This package contains modular bot moderation features that can be purchased
and activated through the marketplace services system.

Each feature integrates with:
- Feature gate service (access control)
- Usage logging (quota tracking)
- User bot moderation service (execution)

Services:
- BaseBotService: Base class for all bot services
- BotFeaturesManager: Manager for bot feature orchestration
- AntiSpamService: Anti-spam and flood protection
- AutoDeleteJoinsService: Auto-delete join/leave messages
"""

from core.services.bot.moderation.base_bot_service import BaseBotService
from core.services.bot.moderation.bot_features_manager import BotFeaturesManager
from core.services.bot.moderation.anti_spam_service import AntiSpamService
from core.services.bot.moderation.auto_delete_joins_service import AutoDeleteJoinsService

__all__ = [
    "BaseBotService",
    "BotFeaturesManager", 
    "AntiSpamService",
    "AutoDeleteJoinsService",
]

