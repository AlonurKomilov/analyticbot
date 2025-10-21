"""
Tier Service for Content Protection

Handles user subscription tier management and feature usage tracking.

✅ CLEAN ARCHITECTURE FIX (Issue #4 Phase 2.8):
- Removed direct imports from infra.db.connection_manager
- Removed direct imports from infra.db.repositories.user_repository
- Now uses DI container to inject repositories
- Follows clean architecture principles (apps -> core -> infra)

Previous violations:
- from infra.db.connection_manager import db_manager (lines 796, 823)
- from infra.db.repositories.user_repository import AsyncpgUserRepository (lines 804, 831)

Current approach:
- Get repositories from DI container
- Use abstract interfaces (UserRepository protocol)
- No direct infrastructure dependencies
"""

import logging

from apps.bot.models.content_protection import PremiumFeatureLimits, UserTier

logger = logging.getLogger(__name__)


async def get_user_subscription_tier(user_id: int) -> UserTier:
    """
    Get user's subscription tier from payment system.

    ✅ Issue #3 Phase 2 (Oct 21, 2025): Integrated with SubscriptionAdapter
    ✅ Issue #4 Phase 2.8 (Oct 21, 2025): Uses DI container (clean architecture)

    Args:
        user_id: Telegram user ID

    Returns:
        UserTier: User's subscription tier (FREE, STARTER, PRO, ENTERPRISE)
    """
    try:
        from apps.di import get_container

        container = get_container()
        subscription_service = container.bot.subscription_service()

        if subscription_service:
            tier_name = await subscription_service.get_user_tier(user_id)
            # Map tier name to UserTier enum
            tier_map = {
                "free": UserTier.FREE,
                "starter": UserTier.STARTER,
                "pro": UserTier.PRO,
                "premium": UserTier.PRO,  # Map premium to PRO
                "enterprise": UserTier.ENTERPRISE,
            }
            return tier_map.get(tier_name.lower(), UserTier.FREE)
    except Exception as e:
        logger.error(f"Error getting user tier: {e}", exc_info=True)

    # Default to FREE on error
    return UserTier.FREE


async def check_feature_usage_limit(feature: str, user_id: int, user_tier: UserTier) -> bool:
    """
    Check if user has remaining feature usage for the month.

    ✅ Issue #4 Phase 2.8: Clean architecture - uses service layer

    Args:
        feature: Feature name (watermarks, custom_emojis, theft_scans)
        user_id: Telegram user ID
        user_tier: User's subscription tier

    Returns:
        bool: True if user can use feature, False if limit reached
    """
    limits = PremiumFeatureLimits.get_limits_for_tier(user_tier)
    current_usage = await get_current_usage(user_id)

    feature_limit = getattr(limits, f"{feature}_per_month", None)
    if feature_limit is None:
        return True  # Unlimited

    return current_usage.get(feature, 0) < feature_limit


async def increment_feature_usage(feature: str, user_id: int, count: int = 1):
    """
    Increment feature usage counter for current month.

    ✅ Issue #3 Phase 2 (Oct 21, 2025): Implemented real database update
    ✅ Issue #4 Phase 2.8 (Oct 21, 2025): Uses DI container (clean architecture)

    Args:
        feature: Feature name (watermarks, custom_emojis, theft_scans)
        user_id: Telegram user ID
        count: Number of uses to increment (default: 1)
    """
    try:
        # Get user repository from DI container (clean architecture)
        from apps.di import get_container

        container = get_container()
        user_repo = container.user_repository()

        if not user_repo:
            logger.warning("User repository not available, skipping usage tracking")
            return

        # Use repository to increment usage
        new_count = await user_repo.increment_feature_usage(user_id, feature, count)
        logger.debug(f"Incremented {feature} usage for user {user_id}: new count = {new_count}")

    except Exception as e:
        logger.error(f"Error incrementing feature usage: {e}", exc_info=True)
        # Don't fail the request if usage tracking fails


async def get_current_usage(user_id: int) -> dict[str, int]:
    """
    Get current month's feature usage for user.

    ✅ Issue #3 Phase 2 (Oct 21, 2025): Implemented real database query
    ✅ Issue #4 Phase 2.8 (Oct 21, 2025): Uses DI container (clean architecture)

    Args:
        user_id: Telegram user ID

    Returns:
        dict: Feature usage counts (e.g., {'watermarks': 5, 'theft_scans': 2})
    """
    try:
        # Get user repository from DI container (clean architecture)
        from apps.di import get_container

        container = get_container()
        user_repo = container.user_repository()

        if not user_repo:
            logger.warning("User repository not available, returning empty usage")
            return {}

        # Use repository to get usage
        usage = await user_repo.get_current_month_usage(user_id)
        logger.debug(f"Current usage for user {user_id}: {usage}")
        return usage

    except Exception as e:
        logger.error(f"Error getting current usage: {e}", exc_info=True)
        # Return empty dict on error (safe default - allows features to work)
        return {}
