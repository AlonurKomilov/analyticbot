"""
Subscription Status Adapter (Stub)

Implements SubscriptionPort for content protection.
This is a temporary stub until payment/subscription services are integrated.
"""


class StubSubscriptionService:
    """
    Stub implementation of SubscriptionPort.

    TODO: Replace with actual subscription service integration
    when payment domain is migrated in Phase 3.5.
    """

    async def check_premium_status(self, user_id: int) -> bool:
        """
        Check if a user has active premium subscription.

        Args:
            user_id: Telegram user ID

        Returns:
            True (stub always returns premium for now)

        Note:
            This is a stub implementation. In production, this should
            query the subscription/payment service.
        """
        # TODO: Integrate with actual payment/subscription service
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
            This is a stub implementation. Should query actual subscription data.
        """
        # TODO: Integrate with actual payment/subscription service
        return "pro"
