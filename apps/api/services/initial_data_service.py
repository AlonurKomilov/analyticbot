"""
Real Initial Data Service
Production service for fetching initial application data
"""

import logging
from typing import Any

from apps.shared.models.twa import InitialDataResponse

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
        # ✅ MIGRATED: Use unified DI container from apps/di
        from apps.di import get_container

        container = get_container()

        # Get repositories with proper pool injection
        user_repo = await container.database.user_repo()
        channel_repo = await container.database.channel_repo()

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

        # Convert dicts to Pydantic models
        from apps.shared.models.twa import User, Plan, Channel, ScheduledPost

        return InitialDataResponse(
            user=User(
                id=user["id"],
                username=user.get("username"),
            ),
            plan=Plan(
                name=plan.get("name", "Free"),
                max_channels=plan.get("channels_limit", 5),
                max_posts_per_month=plan.get("posts_limit", 100),
            ) if plan else None,
            channels=[
                Channel(
                    id=ch["id"],
                    title=ch.get("name", ch.get("title", "Unknown")),
                    username=ch.get("username"),
                )
                for ch in channels
            ],
            scheduled_posts=[
                ScheduledPost(
                    id=post["id"],
                    channel_id=post["channel_id"],
                    scheduled_at=post["scheduled_at"],
                    text=post.get("text"),
                    media_id=post.get("media_id"),
                    media_type=post.get("media_type"),
                    buttons=post.get("buttons"),
                ) for post in scheduled_posts
            ],
            features=features,
        )

    except Exception as e:
        # ✅ FIXED: Proper error handling without inappropriate demo fallback
        logger.error(f"Failed to get real initial data for user {user_id}: {e}")

        # For real data service, we should never fallback to demo
        # Always propagate the error to be handled by the caller
        raise


async def _get_user_plan(user_id: int) -> dict[str, Any]:
    """Get user subscription plan information"""
    # This would integrate with a proper subscription service
    # For now, return basic plan info
    return {
        "name": "Free",
        "channels_limit": 5,
        "posts_limit": 100,
        "analytics_enabled": True,
        "ai_insights_enabled": False,
        "export_enabled": True,
    }


async def _get_user_scheduled_posts(user_id: int) -> list[dict[str, Any]]:
    """Get user's scheduled posts"""
    # This would integrate with the schedule service
    # For now, return empty list
    return []


async def _get_user_features(user_id: int, plan: dict[str, Any]) -> dict[str, bool]:
    """Get feature flags based on user plan and configuration"""
    from config import settings

    return {
        "analytics_enabled": plan.get("analytics_enabled", True),
        "export_enabled": settings.EXPORT_ENABLED and plan.get("export_enabled", True),
        "ai_insights_enabled": plan.get("ai_insights_enabled", False),
        "advanced_features_enabled": plan.get("name") != "Free",
        "alerts_enabled": settings.ALERTS_ENABLED,
        "share_links_enabled": settings.SHARE_LINKS_ENABLED,
    }
