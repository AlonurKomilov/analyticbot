"""
Subscription Status Adapter

Implements SubscriptionPort for content protection.
Integrates with payment/subscription services from infra layer.
"""

import logging
from datetime import datetime

from core.domain.payment import SubscriptionStatus

logger = logging.getLogger(__name__)


class SubscriptionAdapter:
    """
    Real implementation of SubscriptionPort.

    Integrates with the payment domain subscription service to provide
    premium status checking and tier information for content protection features.
    """

    def __init__(self, subscription_service):
        """
        Initialize the subscription adapter.

        Args:
            subscription_service: SubscriptionService from infra layer
        """
        self.subscription_service = subscription_service
        logger.info("✅ SubscriptionAdapter initialized with real subscription service")

    async def check_premium_status(self, user_id: int) -> bool:
        """
        Check if a user has active premium subscription.

        Args:
            user_id: Telegram user ID

        Returns:
            True if user has active premium subscription, False otherwise
        """
        try:
            subscription = await self.subscription_service.get_user_subscription(user_id)

            if not subscription:
                logger.debug(f"No subscription found for user {user_id}")
                return False

            # Check if subscription is active
            is_active = subscription.status in [
                SubscriptionStatus.ACTIVE,
                SubscriptionStatus.TRIALING,
            ]

            # Also check if not expired
            now = datetime.utcnow()
            is_not_expired = subscription.current_period_end > now

            # If subscription is marked to cancel at period end, still consider it active
            # until the period actually ends
            premium_status = is_active and is_not_expired

            logger.debug(
                f"User {user_id} premium status: {premium_status} "
                f"(status={subscription.status}, expires={subscription.current_period_end})"
            )

            return premium_status

        except Exception as e:
            logger.error(f"Error checking premium status for user {user_id}: {e}", exc_info=True)
            # Return False on error to maintain security (don't grant premium on error)
            return False

    async def get_user_tier(self, user_id: int) -> str:
        """
        Get user's subscription tier.

        Args:
            user_id: Telegram user ID

        Returns:
            Tier name: "free", "pro", "premium", "enterprise"
            Defaults to "free" if no subscription found
        """
        try:
            subscription = await self.subscription_service.get_user_subscription(user_id)

            if not subscription:
                logger.debug(f"No subscription found for user {user_id}, defaulting to 'free'")
                return "free"

            # Check if subscription is currently active
            is_premium = await self.check_premium_status(user_id)

            if not is_premium:
                logger.debug(f"User {user_id} has inactive/expired subscription, returning 'free'")
                return "free"

            # Map plan_id to tier
            # This assumes plan_id follows naming convention like "plan_pro", "plan_premium", etc.
            plan_id = subscription.plan_id.lower()

            if "enterprise" in plan_id:
                tier = "enterprise"
            elif "premium" in plan_id or "ultimate" in plan_id:
                tier = "premium"
            elif "pro" in plan_id or "professional" in plan_id:
                tier = "pro"
            else:
                # Default to pro for any paid subscription
                tier = "pro"

            logger.debug(f"User {user_id} tier: {tier} (plan_id={subscription.plan_id})")
            return tier

        except Exception as e:
            logger.error(f"Error getting user tier for user {user_id}: {e}", exc_info=True)
            # Return free tier on error (safe default)
            return "free"


# Keep the stub for backward compatibility during transition
class StubSubscriptionService:
    """
    Stub implementation of SubscriptionPort.

    DEPRECATED: Use SubscriptionAdapter instead.
    This stub is kept temporarily for backward compatibility.
    """

    async def check_premium_status(self, user_id: int) -> bool:
        """
        Check if a user has active premium subscription.

        Args:
            user_id: Telegram user ID

        Returns:
            True (stub always returns premium for now)

        Note:
            DEPRECATED: This is a stub implementation.
            Use SubscriptionAdapter with real subscription service instead.
        """
        logger.warning(
            "⚠️ StubSubscriptionService.check_premium_status called - "
            "migrate to SubscriptionAdapter"
        )
        # For now, return True to allow testing watermark features
        return True

    async def get_user_tier(self, user_id: int) -> str:
        """
        Get user's subscription tier.

        Args:
            user_id: Telegram user ID

        Returns:
            Tier name (stub returns "pro")

        Note:
            DEPRECATED: This is a stub implementation.
            Use SubscriptionAdapter with real subscription service instead.
        """
        logger.warning(
            "⚠️ StubSubscriptionService.get_user_tier called - " "migrate to SubscriptionAdapter"
        )
        return "pro"
