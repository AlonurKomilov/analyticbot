"""
Marketplace Service

Business logic for marketplace services system:
- Service catalog browsing
- Service purchases (using credits)
- Subscription management
- Renewal processing

This module handles the core marketplace business logic, using repository
interfaces from infra/marketplace/ for data access.
"""

import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class MarketplaceService:
    """Service for marketplace operations"""

    def __init__(
        self,
        marketplace_repo,  # MarketplaceServiceRepository
        credit_repo,  # CreditRepository
    ):
        self.marketplace_repo = marketplace_repo
        self.credit_repo = credit_repo

    # ============================================
    # SERVICE CATALOG
    # ============================================

    async def get_service_catalog(
        self, category: str | None = None, user_id: int | None = None
    ) -> list[dict]:
        """
        Get marketplace service catalog.
        Optionally filter by category and mark user's active subscriptions.

        Args:
            category: Filter by category
            user_id: If provided, mark services user is subscribed to

        Returns:
            List of service records with subscription status
        """
        services = await self.marketplace_repo.get_all_services(
            include_inactive=False, category=category
        )

        # If user_id provided, add subscription status
        if user_id:
            active_services = await self.marketplace_repo.get_user_active_services(user_id)
            for service in services:
                service["user_subscribed"] = service["service_key"] in active_services

        return services

    async def get_service_details(
        self, service_key: str, user_id: int | None = None
    ) -> dict | None:
        """
        Get detailed information about a service.

        Args:
            service_key: Service key
            user_id: If provided, include user's subscription status

        Returns:
            Service details or None if not found
        """
        service = await self.marketplace_repo.get_service_by_key(service_key)
        if not service:
            return None

        # Add subscription status if user_id provided
        if user_id:
            subscription = await self.marketplace_repo.check_user_has_service(user_id, service_key)
            service["user_subscribed"] = subscription is not None
            service["user_subscription"] = subscription

        # Add statistics
        stats = await self.marketplace_repo.get_service_statistics(service["id"])
        service["statistics"] = stats

        return service

    async def get_featured_services(self, limit: int = 5) -> list[dict]:
        """Get featured services"""
        return await self.marketplace_repo.get_featured_services(limit)

    # ============================================
    # SERVICE PURCHASE
    # ============================================

    async def purchase_service(
        self,
        user_id: int,
        service_key: str,
        billing_cycle: str = "monthly",
    ) -> dict:
        """
        Purchase a marketplace service subscription.

        Args:
            user_id: User ID
            service_key: Service key to purchase
            billing_cycle: 'monthly' or 'yearly'

        Returns:
            Created subscription record

        Raises:
            ValueError: If service not found, user already subscribed,
                       insufficient credits, or invalid billing cycle
        """
        # Validate billing cycle
        if billing_cycle not in ["monthly", "yearly"]:
            raise ValueError(f"Invalid billing cycle: {billing_cycle}")

        # Get service
        service = await self.marketplace_repo.get_service_by_key(service_key)
        if not service:
            raise ValueError(f"Service not found: {service_key}")

        if not service["is_active"]:
            raise ValueError(f"Service is not active: {service_key}")

        # Check if user already has active subscription
        existing = await self.marketplace_repo.check_user_has_service(user_id, service_key)
        if existing:
            raise ValueError(f"User already has active subscription to {service_key}")

        # Determine price
        if billing_cycle == "monthly":
            price = service["price_credits_monthly"]
        else:
            price = service.get("price_credits_yearly")
            if price is None:
                raise ValueError(f"Yearly billing not available for {service_key}")

        # Check user has enough credits
        balance_data = await self.credit_repo.get_balance(user_id)
        balance = balance_data.get("balance", 0)
        if balance < price:
            raise ValueError(f"Insufficient credits. Required: {price}, Available: {balance}")

        # Calculate expiration
        if billing_cycle == "monthly":
            expires_at = datetime.now() + timedelta(days=30)
        else:
            expires_at = datetime.now() + timedelta(days=365)

        # Deduct credits
        await self.credit_repo.spend_credits(
            user_id=user_id,
            amount=price,
            service_key=service_key,
            description=f"Purchased {service['name']} ({billing_cycle})",
            reference_id=str(service["id"]),
        )

        # Create subscription
        subscription = await self.marketplace_repo.create_subscription(
            user_id=user_id,
            service_id=service["id"],
            billing_cycle=billing_cycle,
            price_paid=price,
            expires_at=expires_at,
            auto_renew=True,
        )

        logger.info(f"User {user_id} purchased {service_key} ({billing_cycle}) for {price} credits")

        return subscription

    # ============================================
    # SUBSCRIPTION MANAGEMENT
    # ============================================

    async def get_user_subscriptions(
        self, user_id: int, include_expired: bool = False
    ) -> list[dict]:
        """Get user's subscriptions"""
        return await self.marketplace_repo.get_user_subscriptions(
            user_id=user_id,
            status=None,
            include_expired=include_expired,
        )

    async def cancel_subscription(
        self, user_id: int, subscription_id: int, reason: str | None = None
    ) -> dict:
        """
        Cancel a subscription.

        Args:
            user_id: User ID (for verification)
            subscription_id: Subscription ID to cancel
            reason: Cancellation reason

        Returns:
            Updated subscription record

        Raises:
            ValueError: If subscription not found or doesn't belong to user
        """
        # Get current subscriptions
        subscriptions = await self.marketplace_repo.get_user_subscriptions(
            user_id=user_id, status=None, include_expired=False
        )

        # Find the subscription
        subscription = next((s for s in subscriptions if s["id"] == subscription_id), None)
        if not subscription:
            raise ValueError("Subscription not found or doesn't belong to user")

        # Cancel it
        result = await self.marketplace_repo.cancel_subscription(
            subscription_id=subscription_id, reason=reason
        )

        logger.info(f"User {user_id} cancelled subscription {subscription_id}")
        return result

    async def toggle_auto_renew(self, user_id: int, subscription_id: int, auto_renew: bool) -> dict:
        """
        Toggle auto-renewal for a subscription.

        Args:
            user_id: User ID (for verification)
            subscription_id: Subscription ID
            auto_renew: New auto-renew setting

        Returns:
            Updated subscription record
        """
        # Verify ownership
        subscriptions = await self.marketplace_repo.get_user_subscriptions(user_id=user_id)
        subscription = next((s for s in subscriptions if s["id"] == subscription_id), None)
        if not subscription:
            raise ValueError("Subscription not found")

        logger.info(
            f"User {user_id} toggled auto-renew for subscription {subscription_id} to {auto_renew}"
        )
        return subscription

    # ============================================
    # RENEWAL PROCESSING (Background Job)
    # ============================================

    async def process_renewals(self, days_ahead: int = 1) -> dict:
        """
        Process subscription renewals for subscriptions expiring soon.
        Should be called daily by a background job.

        Args:
            days_ahead: Process subscriptions expiring within N days

        Returns:
            Dict with renewal statistics
        """
        expiring = await self.marketplace_repo.get_expiring_subscriptions(days_ahead=days_ahead)

        stats = {
            "checked": len(expiring),
            "renewed": 0,
            "failed_insufficient_credits": 0,
            "failed_service_inactive": 0,
            "failed_other": 0,
        }

        for subscription in expiring:
            try:
                # Determine price
                if subscription["billing_cycle"] == "monthly":
                    price = subscription["price_credits_monthly"]
                else:
                    price = subscription["price_credits_yearly"]

                # Check user has enough credits
                if subscription["credit_balance"] < price:
                    stats["failed_insufficient_credits"] += 1
                    logger.warning(
                        f"Renewal failed: insufficient credits for "
                        f"subscription {subscription['id']}"
                    )
                    continue

                # Deduct credits
                await self.credit_repo.deduct_credits(
                    user_id=subscription["user_id"],
                    amount=price,
                    transaction_type="subscription_renewal",
                    category="marketplace",
                    description=f"Renewed subscription to service "
                    f"(ID: {subscription['service_id']})",
                    reference_id=str(subscription["id"]),
                )

                # Calculate new expiration
                if subscription["billing_cycle"] == "monthly":
                    new_expires = subscription["expires_at"] + timedelta(days=30)
                else:
                    new_expires = subscription["expires_at"] + timedelta(days=365)

                # Renew subscription
                await self.marketplace_repo.renew_subscription(
                    subscription_id=subscription["id"],
                    new_expires_at=new_expires,
                    price_paid=price,
                )

                stats["renewed"] += 1
                logger.info(
                    f"Renewed subscription {subscription['id']} for user {subscription['user_id']}"
                )

            except Exception as e:
                stats["failed_other"] += 1
                logger.error(f"Renewal failed for subscription {subscription['id']}: {e}")

        logger.info(f"Renewal processing complete: {stats}")
        return stats

    # ============================================
    # USAGE TRACKING
    # ============================================

    async def log_service_usage(
        self,
        user_id: int,
        service_key: str,
        action: str,
        resource_id: str | None = None,
        success: bool = True,
        error_message: str | None = None,
        response_time_ms: int | None = None,
        metadata: dict | None = None,
    ) -> None:
        """
        Log a service usage event.

        Args:
            user_id: User ID
            service_key: Service key
            action: Action performed (e.g., 'check_spam', 'delete_join')
            resource_id: Resource identifier (e.g., chat_id, message_id)
            success: Whether action succeeded
            error_message: Error message if failed
            response_time_ms: Response time in milliseconds
            metadata: Additional metadata
        """
        # Get user's subscription
        subscription = await self.marketplace_repo.check_user_has_service(user_id, service_key)
        if not subscription:
            logger.warning(
                f"Attempted to log usage for service {service_key} "
                f"but user {user_id} has no active subscription"
            )
            return

        # Get service
        service = await self.marketplace_repo.get_service_by_key(service_key)
        if not service:
            logger.error(f"Service not found: {service_key}")
            return

        # Log usage
        await self.marketplace_repo.log_service_usage(
            subscription_id=subscription["id"],
            user_id=user_id,
            service_id=service["id"],
            action=action,
            resource_id=resource_id,
            success=success,
            error_message=error_message,
            response_time_ms=response_time_ms,
            metadata=metadata,
        )

        # Increment usage counters
        await self.marketplace_repo.increment_subscription_usage(
            subscription_id=subscription["id"], count=1
        )

    async def get_subscription_usage_stats(self, subscription_id: int, days: int = 30) -> dict:
        """Get usage statistics for a subscription"""
        return await self.marketplace_repo.get_subscription_usage(
            subscription_id=subscription_id, days=days
        )
