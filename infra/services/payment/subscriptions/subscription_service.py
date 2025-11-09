"""
Subscription Management Microservice
====================================

Focused microservice for subscription lifecycle management.
Handles subscription creation, updates, cancellation, and plan management.

Single Responsibility: Subscription operations only.
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from apps.bot.models.payment import BillingCycle as AdapterBillingCycle
from apps.bot.services.adapters.payment_adapter_factory import PaymentAdapterFactory
from core.domain.payment import (
    BillingCycle,
    Money,
    Subscription,
    SubscriptionData,
    SubscriptionStatus,
)
from core.protocols.payment.payment_protocols import (
    SubscriptionProtocol,
    SubscriptionResult,
)

logger = logging.getLogger(__name__)


class SubscriptionService(SubscriptionProtocol):
    """
    Subscription management microservice.

    Responsibilities:
    - Create and configure subscriptions
    - Manage subscription lifecycle (pause, resume, cancel)
    - Handle plan changes and upgrades
    - Track subscription billing cycles
    - Coordinate with payment providers for recurring billing
    """

    def __init__(self, payment_repository, payment_method_service=None):
        self.repository = payment_repository
        self.payment_method_service = payment_method_service
        self.payment_adapter = PaymentAdapterFactory.get_current_adapter()
        logger.info("🔄 SubscriptionService initialized")

    def _create_subscription_entity(self, subscription_data: dict[str, Any]) -> Subscription:
        """Helper method to convert database record to Subscription domain entity"""
        return Subscription(
            id=subscription_data["id"],
            user_id=subscription_data["user_id"],
            plan_id=subscription_data["plan_id"],
            payment_method_id=subscription_data["payment_method_id"],
            status=subscription_data["status"],
            billing_cycle=subscription_data["billing_cycle"],
            amount=Money(
                amount=subscription_data["amount"],
                currency=subscription_data["currency"],
            ),
            current_period_start=subscription_data["current_period_start"],
            current_period_end=subscription_data["current_period_end"],
            trial_ends_at=subscription_data.get("trial_ends_at"),
            created_at=subscription_data["created_at"],
            canceled_at=subscription_data.get("canceled_at"),
            cancel_at_period_end=subscription_data.get("cancel_at_period_end", False),
            metadata=subscription_data.get("metadata", {}),
        )

    async def create_subscription(
        self, user_id: int, subscription_data: SubscriptionData
    ) -> SubscriptionResult:
        """
        Create a new subscription for a user.

        Args:
            user_id: User identifier
            subscription_data: Subscription configuration

        Returns:
            SubscriptionResult with subscription details
        """
        try:
            logger.info(
                f"🔄 Creating subscription for user {user_id}, plan: {subscription_data.plan_id}"
            )

            # Validate subscription data
            validation_result = await self._validate_subscription_data(subscription_data)
            if not validation_result["is_valid"]:
                return SubscriptionResult(
                    success=False,
                    error_message=f"Validation failed: {validation_result['errors']}",
                )

            # Get plan details
            plan = await self.repository.get_plan_with_pricing(str(subscription_data.plan_id))
            if not plan:
                return SubscriptionResult(
                    success=False, error_message="Subscription plan not found"
                )

            # Calculate subscription pricing and periods
            pricing_info = self._calculate_subscription_pricing(
                plan, subscription_data.billing_cycle
            )

            # Calculate subscription periods
            now = datetime.utcnow()
            trial_ends_at = None
            current_period_start = now

            if subscription_data.trial_days and subscription_data.trial_days > 0:
                trial_ends_at = now + timedelta(days=subscription_data.trial_days)
                current_period_start = trial_ends_at

            current_period_end = current_period_start + timedelta(days=pricing_info["period_days"])

            # Create subscription record
            subscription_id = await self.repository.create_subscription(
                user_id=user_id,
                plan_id=subscription_data.plan_id,
                payment_method_id=subscription_data.payment_method_id,
                provider_subscription_id=None,  # Will be set after provider creation
                billing_cycle=subscription_data.billing_cycle.value,
                amount=pricing_info["amount"],
                currency=pricing_info["currency"],
                current_period_start=current_period_start,
                current_period_end=current_period_end,
                trial_ends_at=trial_ends_at,
                metadata=subscription_data.metadata or {},
            )

            # Create subscription with payment provider
            provider_response = None
            if subscription_data.payment_method_id:
                provider_result = await self._create_provider_subscription(
                    user_id, subscription_data, subscription_id, plan
                )
                if provider_result["success"]:
                    provider_response = provider_result["response"]
                else:
                    logger.warning(
                        f"⚠️ Provider subscription creation failed: {provider_result['error']}"
                    )

            # Update subscription status
            await self.repository.update_subscription_status(
                subscription_id=subscription_id, status=SubscriptionStatus.ACTIVE
            )

            # Get final subscription record
            subscription = await self.repository.get_user_active_subscription(str(user_id))
            if not subscription:
                raise ValueError("Subscription not found after creation")

            subscription_entity = self._create_subscription_entity(subscription)

            logger.info(f"✅ Subscription created successfully: {subscription_id}")
            return SubscriptionResult(
                success=True,
                subscription=subscription_entity,
                provider_response=provider_response,
            )

        except Exception as e:
            logger.error(f"❌ Failed to create subscription for user {user_id}: {e}")
            return SubscriptionResult(success=False, error_message=str(e))

    async def get_user_subscription(self, user_id: int) -> Subscription | None:
        """
        Get user's active subscription.

        Args:
            user_id: User identifier

        Returns:
            Active subscription details or None
        """
        try:
            subscription = await self.repository.get_user_active_subscription(str(user_id))
            if not subscription:
                return None

            return self._create_subscription_entity(subscription)

        except Exception as e:
            logger.error(f"❌ Failed to get subscription for user {user_id}: {e}")
            return None

    async def update_subscription(
        self, subscription_id: str, updates: dict[str, Any]
    ) -> SubscriptionResult:
        """
        Update subscription details.

        Args:
            subscription_id: Subscription identifier
            updates: Dictionary of fields to update

        Returns:
            SubscriptionResult with updated subscription
        """
        try:
            logger.info(f"🔄 Updating subscription {subscription_id}")

            # Get existing subscription
            subscription = await self.repository.get_subscription(subscription_id)
            if not subscription:
                return SubscriptionResult(success=False, error_message="Subscription not found")

            # Apply updates (only allow certain fields)
            allowed_updates = ["metadata", "cancel_at_period_end"]
            filtered_updates = {k: v for k, v in updates.items() if k in allowed_updates}

            if not filtered_updates:
                return SubscriptionResult(success=False, error_message="No valid fields to update")

            # Update subscription
            updated_subscription = await self.repository.update_subscription(
                subscription_id, filtered_updates
            )
            if not updated_subscription:
                return SubscriptionResult(
                    success=False, error_message="Failed to update subscription"
                )

            subscription_entity = self._create_subscription_entity(updated_subscription)

            logger.info(f"✅ Subscription updated successfully: {subscription_id}")
            return SubscriptionResult(success=True, subscription=subscription_entity)

        except Exception as e:
            logger.error(f"❌ Failed to update subscription {subscription_id}: {e}")
            return SubscriptionResult(success=False, error_message=str(e))

    async def cancel_subscription(
        self, user_id: int, immediate: bool = False, reason: str | None = None
    ) -> dict[str, Any]:
        """
        Cancel a user's subscription.

        Args:
            user_id: User identifier
            immediate: Whether to cancel immediately or at period end
            reason: Optional cancellation reason

        Returns:
            Cancellation result details
        """
        try:
            logger.info(f"🔄 Canceling subscription for user {user_id}, immediate: {immediate}")

            subscription = await self.repository.get_user_active_subscription(str(user_id))
            if not subscription:
                return {"success": False, "error": "No active subscription found"}

            # Cancel with provider if exists
            if subscription["provider_subscription_id"]:
                try:
                    await self.payment_adapter.cancel_subscription(
                        subscription["provider_subscription_id"]
                    )
                except Exception as e:
                    logger.warning(f"⚠️ Provider cancellation failed (continuing): {e}")

            # Determine cancellation date
            canceled_at = datetime.utcnow() if immediate else subscription["current_period_end"]

            # Update subscription status
            await self.repository.update_subscription_status(
                subscription_id=subscription["id"],
                status=SubscriptionStatus.CANCELED,
                canceled_at=canceled_at,
                cancel_reason=reason,
            )

            logger.info(f"✅ Subscription canceled successfully: {subscription['id']}")
            return {
                "success": True,
                "subscription_id": subscription["id"],
                "canceled_at": canceled_at.isoformat(),
                "immediate": immediate,
                "reason": reason,
            }

        except Exception as e:
            logger.error(f"❌ Failed to cancel subscription for user {user_id}: {e}")
            return {"success": False, "error": str(e)}

    async def pause_subscription(
        self, subscription_id: str, duration_days: int
    ) -> SubscriptionResult:
        """
        Pause a subscription for a specific duration.

        Args:
            subscription_id: Subscription identifier
            duration_days: Number of days to pause

        Returns:
            SubscriptionResult with pause details
        """
        try:
            logger.info(f"🔄 Pausing subscription {subscription_id} for {duration_days} days")

            # Get subscription
            subscription = await self.repository.get_subscription(subscription_id)
            if not subscription:
                return SubscriptionResult(success=False, error_message="Subscription not found")

            if subscription["status"] != SubscriptionStatus.ACTIVE:
                return SubscriptionResult(
                    success=False, error_message="Can only pause active subscriptions"
                )

            # Calculate pause period
            pause_until = datetime.utcnow() + timedelta(days=duration_days)

            # Update subscription
            updates = {
                "status": "paused",  # Use string instead of enum since PAUSED doesn't exist
                "paused_until": pause_until,
                "metadata": {
                    **subscription.get("metadata", {}),
                    "pause_duration_days": duration_days,
                    "paused_at": datetime.utcnow().isoformat(),
                },
            }

            updated_subscription = await self.repository.update_subscription(
                subscription_id, updates
            )
            subscription_entity = self._create_subscription_entity(updated_subscription)

            logger.info(f"✅ Subscription paused successfully: {subscription_id}")
            return SubscriptionResult(success=True, subscription=subscription_entity)

        except Exception as e:
            logger.error(f"❌ Failed to pause subscription {subscription_id}: {e}")
            return SubscriptionResult(success=False, error_message=str(e))

    async def resume_subscription(self, subscription_id: str) -> SubscriptionResult:
        """
        Resume a paused subscription.

        Args:
            subscription_id: Subscription identifier

        Returns:
            SubscriptionResult with resume details
        """
        try:
            logger.info(f"🔄 Resuming subscription {subscription_id}")

            # Get subscription
            subscription = await self.repository.get_subscription(subscription_id)
            if not subscription:
                return SubscriptionResult(success=False, error_message="Subscription not found")

            if subscription["status"] != "paused":  # Use string instead of enum
                return SubscriptionResult(
                    success=False, error_message="Can only resume paused subscriptions"
                )

            # Update subscription
            updates = {
                "status": SubscriptionStatus.ACTIVE,
                "paused_until": None,
                "metadata": {
                    **subscription.get("metadata", {}),
                    "resumed_at": datetime.utcnow().isoformat(),
                },
            }

            updated_subscription = await self.repository.update_subscription(
                subscription_id, updates
            )
            subscription_entity = self._create_subscription_entity(updated_subscription)

            logger.info(f"✅ Subscription resumed successfully: {subscription_id}")
            return SubscriptionResult(success=True, subscription=subscription_entity)

        except Exception as e:
            logger.error(f"❌ Failed to resume subscription {subscription_id}: {e}")
            return SubscriptionResult(success=False, error_message=str(e))

    async def change_subscription_plan(
        self, subscription_id: str, new_plan_id: str
    ) -> SubscriptionResult:
        """
        Change subscription plan.

        Args:
            subscription_id: Subscription identifier
            new_plan_id: New plan identifier

        Returns:
            SubscriptionResult with plan change details
        """
        try:
            logger.info(f"🔄 Changing subscription {subscription_id} to plan {new_plan_id}")

            # Get current subscription
            subscription = await self.repository.get_subscription(subscription_id)
            if not subscription:
                return SubscriptionResult(success=False, error_message="Subscription not found")

            # Get new plan
            new_plan = await self.repository.get_plan_with_pricing(new_plan_id)
            if not new_plan:
                return SubscriptionResult(success=False, error_message="New plan not found")

            # Calculate new pricing
            billing_cycle = BillingCycle(subscription["billing_cycle"])
            pricing_info = self._calculate_subscription_pricing(new_plan, billing_cycle)

            # Update subscription
            updates = {
                "plan_id": new_plan_id,
                "amount": pricing_info["amount"],
                "metadata": {
                    **subscription.get("metadata", {}),
                    "plan_changed_at": datetime.utcnow().isoformat(),
                    "previous_plan_id": subscription["plan_id"],
                },
            }

            updated_subscription = await self.repository.update_subscription(
                subscription_id, updates
            )
            subscription_entity = self._create_subscription_entity(updated_subscription)

            logger.info(f"✅ Subscription plan changed successfully: {subscription_id}")
            return SubscriptionResult(success=True, subscription=subscription_entity)

        except Exception as e:
            logger.error(f"❌ Failed to change subscription plan {subscription_id}: {e}")
            return SubscriptionResult(success=False, error_message=str(e))

    async def get_available_plans(self) -> list[dict[str, Any]]:
        """
        Get all available subscription plans.

        Returns:
            List of available plans
        """
        try:
            plans = await self.repository.get_active_plans()
            return [
                {
                    "id": plan["id"],
                    "name": plan["name"],
                    "price_monthly": plan["price_monthly"],
                    "price_yearly": plan["price_yearly"],
                    "currency": plan["currency"],
                    "max_channels": plan["max_channels"],
                    "max_posts_per_month": plan["max_posts_per_month"],
                    "features": plan["features"] or [],
                    "is_active": plan["is_active"],
                    "stripe_price_id": plan.get("stripe_price_id"),
                    "stripe_yearly_price_id": plan.get("stripe_yearly_price_id"),
                    "trial_days": plan.get("trial_days"),
                }
                for plan in plans
            ]
        except Exception as e:
            logger.error(f"❌ Failed to get available plans: {e}")
            return []

    async def _validate_subscription_data(
        self, subscription_data: SubscriptionData
    ) -> dict[str, Any]:
        """Validate subscription data before creation."""
        errors = []

        if not subscription_data.plan_id:
            errors.append("Plan ID is required")

        if subscription_data.trial_days and subscription_data.trial_days < 0:
            errors.append("Trial days cannot be negative")

        if subscription_data.trial_days and subscription_data.trial_days > 365:
            errors.append("Trial days cannot exceed 365")

        return {"is_valid": len(errors) == 0, "errors": errors}

    def _calculate_subscription_pricing(
        self, plan: dict[str, Any], billing_cycle: BillingCycle
    ) -> dict[str, Any]:
        """Calculate subscription pricing based on plan and billing cycle."""
        if billing_cycle == BillingCycle.MONTHLY:
            return {
                "amount": plan["price_monthly"],
                "currency": plan["currency"],
                "period_days": 30,
            }
        else:
            return {
                "amount": plan["price_yearly"],
                "currency": plan["currency"],
                "period_days": 365,
            }

    async def _create_provider_subscription(
        self,
        user_id: int,
        subscription_data: SubscriptionData,
        subscription_id: str,
        plan: dict[str, Any],
    ) -> dict[str, Any]:
        """Create subscription with payment provider."""
        try:
            payment_method = await self.repository.get_payment_method(
                subscription_data.payment_method_id
            )
            if not payment_method:
                return {"success": False, "error": "Payment method not found"}

            provider_response = await self.payment_adapter.create_subscription(
                customer_id=str(user_id),
                payment_method_id=payment_method["provider_method_id"],
                price_id=str(subscription_data.plan_id),
                billing_cycle=AdapterBillingCycle(subscription_data.billing_cycle.value),
                metadata={},
            )

            return {"success": True, "response": provider_response}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def health_check(self) -> dict[str, Any]:
        """Health check for subscription service."""
        try:
            # Test repository connection
            test_plans = await self.repository.get_active_plans()

            # Test adapter connection
            adapter_health = (
                await self.payment_adapter.health_check()
                if hasattr(self.payment_adapter, "health_check")
                else {"status": "unknown"}
            )

            return {
                "service": "SubscriptionService",
                "status": "healthy",
                "repository_connected": True,
                "available_plans": len(test_plans),
                "adapter_status": adapter_health.get("status", "unknown"),
                "adapter_name": self.payment_adapter.get_adapter_name(),
            }
        except Exception as e:
            return {
                "service": "SubscriptionService",
                "status": "unhealthy",
                "error": str(e),
            }
