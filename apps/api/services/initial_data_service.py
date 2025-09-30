"""
Real Initial Data Service
Production service for fetching initial application data
"""

import logging
from typing import Optional, Dict, Any, List

from apps.bot.models.twa import InitialDataResponse
from apps.shared.factory import get_repository_factory

# TODO: Use proper repository protocols
# from infra.db.repositories.user_repository import AsyncpgUserRepository
# from infra.db.repositories.channel_repository import AsyncpgChannelRepository

logger = logging.getLogger(__name__)


async def get_real_initial_data(user_id: int) -> InitialDataResponse:
    """
    Get real initial data from production repositories
    This replaces demo/mock data with actual database queries
    """
    try:
        # ✅ FIXED: Use proper DI container for repository instantiation
        from apps.shared.di import get_container
        container = get_container()
        
        # Get repositories with proper pool injection
        user_repo = await container.user_repo()
        channel_repo = await container.channel_repo()
        
        # Get user data
        user = await user_repo.get_user_by_id(user_id)
        if not user:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user channels  
        channels = await channel_repo.get_user_channels(user_id)
        
        # Get user plan info - this would come from a proper plan service
        plan = await _get_user_plan(user_id)
        
        # Get scheduled posts - this would come from a proper schedule service
        scheduled_posts = await _get_user_scheduled_posts(user_id)
        
        # Get feature flags based on user plan and configuration
        features = await _get_user_features(user_id, plan)
        
        return InitialDataResponse(
            user={
                "id": user["id"],
                "telegram_id": user["telegram_id"],
                "username": user.get("username"),
                "full_name": user.get("full_name"),
                "email": user.get("email")
            },
            plan=plan,
            channels=[{
                "id": ch["id"],
                "name": ch["name"],
                "username": ch.get("username"),
                "subscriber_count": ch.get("subscriber_count", 0),
                "is_active": ch.get("is_active", True)
            } for ch in channels],
            scheduled_posts=scheduled_posts,
            features=features
        )
        
    except Exception as e:
        # ✅ FIXED: Proper error handling without inappropriate demo fallback
        logger.error(f"Failed to get real initial data for user {user_id}: {e}")
        
        # For real data service, we should never fallback to demo
        # Always propagate the error to be handled by the caller
        raise


async def _get_user_plan(user_id: int) -> Dict[str, Any]:
    """Get user subscription plan information"""
    # This would integrate with a proper subscription service
    # For now, return basic plan info
    return {
        "name": "Free",
        "channels_limit": 5,
        "posts_limit": 100,
        "analytics_enabled": True,
        "ai_insights_enabled": False,
        "export_enabled": True
    }


async def _get_user_scheduled_posts(user_id: int) -> List[Dict[str, Any]]:
    """Get user's scheduled posts"""
    # This would integrate with the schedule service
    # For now, return empty list
    return []


async def _get_user_features(user_id: int, plan: Dict[str, Any]) -> Dict[str, bool]:
    """Get feature flags based on user plan and configuration"""
    from config import settings
    
    return {
        "analytics_enabled": plan.get("analytics_enabled", True),
        "export_enabled": settings.EXPORT_ENABLED and plan.get("export_enabled", True),
        "ai_insights_enabled": plan.get("ai_insights_enabled", False),
        "advanced_features_enabled": plan.get("name") != "Free",
        "alerts_enabled": settings.ALERTS_ENABLED,
        "share_links_enabled": settings.SHARE_LINKS_ENABLED
    }