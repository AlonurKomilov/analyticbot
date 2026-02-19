"""
AI User Module
==============

User-facing AI for:
- Per-user AI assistants
- Analytics insights and recommendations
- Content creation and optimization
- Marketplace service integration
- Configured via database/frontend
- User customizable

Usage:
    from apps.ai.user import UserAIAgent, UserAIConfig

    config = await UserAIConfig.from_database(user_id)
    agent = UserAIAgent(config)
    result = await agent.analyze_channel(channel_id)
"""

from apps.ai.user.agent import UserAIAgent
from apps.ai.user.config import UserAIConfig, UserAISettings

__all__ = [
    "UserAIAgent",
    "UserAIConfig",
    "UserAISettings",
]
