"""
Payment Orchestrator Service
============================

Master orchestrator for all payment microservices.
Coordinates workflows across payment methods, processing, subscriptions, webhooks, and analytics.

Single Responsibility: Orchestration and workflow coordination only.
"""

import logging
from typing import Any

from core.domain.payment import PaymentData, SubscriptionData
from core.protocols.payment.payment_protocols import (
    PaymentOrchestratorProtocol,
    PaymentResult,
    SubscriptionResult,
)

logger = logging.getLogger(__name__)


class PaymentOrchestratorService(PaymentOrchestratorProtocol):
    """
    Payment system orchestrator.

    Responsibilities:
    - Coordinate complex payment workflows
    - Manage service dependencies and interactions
    - Handle cross-service error recovery
    - Provide unified interface for payment operations
    - Monitor payment system health
    """

    def __init__(
        self,
        payment_method_service,
        payment_processing_service,
        subscription_service,
        webhook_service,
        analytics_service,
        gateway_manager_service,
    ):
        self.payment_method_service = payment_method_service
        self.payment_processing_service = payment_processing_service
        self.subscription_service = subscription_service
        self.webhook_service = webhook_service
        self.analytics_service = analytics_service
        self.gateway_manager_service = gateway_manager_service

        logger.info("🎼 PaymentOrchestratorService initialized with all microservices")

    async def execute_payment_workflow(
        self,
        user_id: int,
        payment_data: PaymentData,
        workflow_options: dict[str, Any] | None = None,
    ) -> PaymentResult:
        """
        Execute complete payment workflow with validation and recovery.

        Args:
            user_id: User identifier
            payment_data: Payment details
            workflow_options: Optional workflow configuration

        Returns:
            PaymentResult with comprehensive status
        """
        workflow_id = f"payment_workflow_{user_id}_{int(__import__('time').time())}"

        try:
            logger.info(f"🎼 Executing payment workflow: {workflow_id}")

            # Step 1: Validate payment method exists and is valid
            if payment_data.payment_method_id:
                payment_method = await self.payment_method_service.get_payment_method(
                    payment_data.payment_method_id
                )
                if not payment_method:
                    return PaymentResult(success=False, error_message="Payment method not found")

                if payment_method.user_id != user_id:
                    return PaymentResult(
                        success=False,
                        error_message="Payment method does not belong to user",
                    )

            # Step 2: Pre-flight validation
            validation_result = await self.payment_processing_service.validate_payment_data(
                payment_data
            )
            if not validation_result["is_valid"]:
                return PaymentResult(
                    success=False,
                    error_message=f"Payment validation failed: {validation_result['errors']}",
                )

            # Step 3: Execute payment processing
            payment_result = await self.payment_processing_service.process_payment(
                user_id=user_id,
                payment_data=payment_data,
                idempotency_key=(
                    workflow_options.get("idempotency_key") if workflow_options else None
                ),
            )

            # Step 4: Handle post-payment actions
            if payment_result.success:
                await self._handle_successful_payment(user_id, payment_result, workflow_options)
            else:
                await self._handle_failed_payment(user_id, payment_result, workflow_options)

            logger.info(
                f"✅ Payment workflow completed: {workflow_id}, success: {payment_result.success}"
            )
            return payment_result

        except Exception as e:
            logger.error(f"❌ Payment workflow failed: {workflow_id}, error: {e}")
            return PaymentResult(
                success=False, error_message=f"Workflow execution failed: {str(e)}"
            )

    async def execute_subscription_workflow(
        self,
        user_id: int,
        subscription_data: SubscriptionData,
        workflow_options: dict[str, Any] | None = None,
    ) -> SubscriptionResult:
        """
        Execute complete subscription creation workflow.

        Args:
            user_id: User identifier
            subscription_data: Subscription configuration
            workflow_options: Optional workflow configuration

        Returns:
            SubscriptionResult with comprehensive status
        """
        workflow_id = f"subscription_workflow_{user_id}_{int(__import__('time').time())}"

        try:
            logger.info(f"🎼 Executing subscription workflow: {workflow_id}")

            # Step 1: Check for existing active subscription
            existing_subscription = await self.subscription_service.get_user_subscription(user_id)
            if existing_subscription and existing_subscription.status.value == "active":
                return SubscriptionResult(
                    success=False,
                    error_message="User already has an active subscription",
                )

            # Step 2: Validate payment method if provided
            if subscription_data.payment_method_id:
                payment_method = await self.payment_method_service.get_payment_method(
                    subscription_data.payment_method_id
                )
                if not payment_method:
                    return SubscriptionResult(
                        success=False, error_message="Payment method not found"
                    )

                if payment_method.user_id != user_id:
                    return SubscriptionResult(
                        success=False,
                        error_message="Payment method does not belong to user",
                    )

            # Step 3: Validate plan availability
            available_plans = await self.subscription_service.get_available_plans()
            plan_ids = [plan["id"] for plan in available_plans]
            if str(subscription_data.plan_id) not in plan_ids:
                return SubscriptionResult(
                    success=False, error_message="Selected plan is not available"
                )

            # Step 4: Execute subscription creation
            subscription_result = await self.subscription_service.create_subscription(
                user_id=user_id, subscription_data=subscription_data
            )

            # Step 5: Handle post-subscription actions
            if subscription_result.success:
                await self._handle_successful_subscription(
                    user_id, subscription_result, workflow_options
                )
            else:
                await self._handle_failed_subscription(
                    user_id, subscription_result, workflow_options
                )

            logger.info(
                f"✅ Subscription workflow completed: {workflow_id}, success: {subscription_result.success}"
            )
            return subscription_result

        except Exception as e:
            logger.error(f"❌ Subscription workflow failed: {workflow_id}, error: {e}")
            return SubscriptionResult(
                success=False, error_message=f"Workflow execution failed: {str(e)}"
            )

    async def handle_payment_failure_workflow(
        self, payment_id: str, failure_reason: str
    ) -> dict[str, Any]:
        """
        Handle payment failure recovery workflow.

        Args:
            payment_id: Failed payment identifier
            failure_reason: Reason for failure

        Returns:
            Recovery workflow result
        """
        workflow_id = f"failure_recovery_{payment_id}_{int(__import__('time').time())}"

        try:
            logger.info(f"🎼 Executing payment failure recovery: {workflow_id}")

            # Step 1: Analyze failure reason
            failure_analysis = await self._analyze_payment_failure(payment_id, failure_reason)

            # Step 2: Determine recovery strategy
            recovery_strategy = await self._determine_recovery_strategy(failure_analysis)

            # Step 3: Execute recovery actions
            recovery_result = await self._execute_recovery_actions(payment_id, recovery_strategy)

            logger.info(f"✅ Payment failure recovery completed: {workflow_id}")
            return {
                "workflow_id": workflow_id,
                "success": recovery_result.get("success", False),
                "failure_analysis": failure_analysis,
                "recovery_strategy": recovery_strategy,
                "recovery_result": recovery_result,
            }

        except Exception as e:
            logger.error(f"❌ Payment failure recovery failed: {workflow_id}, error: {e}")
            return {"workflow_id": workflow_id, "success": False, "error": str(e)}

    async def get_payment_system_health(self) -> dict[str, Any]:
        """
        Get comprehensive health status of payment system.

        Returns:
            Complete health status across all services
        """
        try:
            logger.info("🎼 Checking payment system health")

            # Check all service health
            health_checks = await __import__("asyncio").gather(
                self.payment_method_service.health_check(),
                self.payment_processing_service.health_check(),
                self.subscription_service.health_check(),
                self.webhook_service.health_check(),
                self.analytics_service.health_check(),
                self.gateway_manager_service.get_gateway_health(),
                return_exceptions=True,
            )

            # Process health check results
            services_health = {}
            overall_status = "healthy"

            service_names = [
                "payment_method_service",
                "payment_processing_service",
                "subscription_service",
                "webhook_service",
                "analytics_service",
                "gateway_manager_service",
            ]

            for i, health_result in enumerate(health_checks):
                service_name = service_names[i]

                if isinstance(health_result, Exception):
                    services_health[service_name] = {
                        "status": "unhealthy",
                        "error": str(health_result),
                    }
                    overall_status = "degraded"
                else:
                    services_health[service_name] = health_result
                    if health_result.get("status") != "healthy":
                        overall_status = "degraded"

            # Calculate system metrics
            healthy_services = sum(
                1 for health in services_health.values() if health.get("status") == "healthy"
            )
            total_services = len(services_health)

            return {
                "orchestrator": "PaymentOrchestratorService",
                "overall_status": overall_status,
                "healthy_services": healthy_services,
                "total_services": total_services,
                "service_health": services_health,
                "checked_at": __import__("datetime").datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Failed to check payment system health: {e}")
            return {
                "orchestrator": "PaymentOrchestratorService",
                "overall_status": "unhealthy",
                "error": str(e),
                "checked_at": __import__("datetime").datetime.utcnow().isoformat(),
            }

    async def _handle_successful_payment(
        self,
        user_id: int,
        payment_result: PaymentResult,
        workflow_options: dict[str, Any] | None,
    ):
        """Handle post-payment actions for successful payments."""
        try:
            # Update analytics
            if hasattr(self.analytics_service, "record_payment_success"):
                await self.analytics_service.record_payment_success(payment_result.payment)

            # Trigger any configured webhooks or notifications
            if workflow_options and workflow_options.get("notify_success"):
                logger.info(f"🎼 Payment success notification for user {user_id}")

        except Exception as e:
            logger.warning(f"⚠️ Post-payment success handling failed: {e}")

    async def _handle_failed_payment(
        self,
        user_id: int,
        payment_result: PaymentResult,
        workflow_options: dict[str, Any] | None,
    ):
        """Handle post-payment actions for failed payments."""
        try:
            # Update analytics
            if hasattr(self.analytics_service, "record_payment_failure"):
                await self.analytics_service.record_payment_failure(payment_result)

            # Trigger failure notifications
            if workflow_options and workflow_options.get("notify_failure"):
                logger.info(f"🎼 Payment failure notification for user {user_id}")

        except Exception as e:
            logger.warning(f"⚠️ Post-payment failure handling failed: {e}")

    async def _handle_successful_subscription(
        self,
        user_id: int,
        subscription_result: SubscriptionResult,
        workflow_options: dict[str, Any] | None,
    ):
        """Handle post-subscription actions for successful subscriptions."""
        try:
            # Update analytics
            if hasattr(self.analytics_service, "record_subscription_creation"):
                await self.analytics_service.record_subscription_creation(
                    subscription_result.subscription
                )

            # Trigger subscription welcome notifications
            logger.info(f"🎼 Subscription created successfully for user {user_id}")

        except Exception as e:
            logger.warning(f"⚠️ Post-subscription success handling failed: {e}")

    async def _handle_failed_subscription(
        self,
        user_id: int,
        subscription_result: SubscriptionResult,
        workflow_options: dict[str, Any] | None,
    ):
        """Handle post-subscription actions for failed subscriptions."""
        try:
            # Record failure analytics
            if hasattr(self.analytics_service, "record_subscription_failure"):
                await self.analytics_service.record_subscription_failure(subscription_result)

            logger.info(f"🎼 Subscription creation failed for user {user_id}")

        except Exception as e:
            logger.warning(f"⚠️ Post-subscription failure handling failed: {e}")

    async def _analyze_payment_failure(
        self, payment_id: str, failure_reason: str
    ) -> dict[str, Any]:
        """Analyze payment failure to determine root cause."""
        return {
            "payment_id": payment_id,
            "failure_reason": failure_reason,
            "failure_category": self._categorize_failure(failure_reason),
            "is_retryable": self._is_failure_retryable(failure_reason),
            "suggested_action": self._suggest_failure_action(failure_reason),
        }

    async def _determine_recovery_strategy(
        self, failure_analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Determine appropriate recovery strategy based on failure analysis."""
        if failure_analysis["is_retryable"]:
            return {
                "strategy": "retry",
                "max_retries": 3,
                "retry_delay": 300,  # 5 minutes
            }
        else:
            return {"strategy": "manual_review", "notify_admin": True}

    async def _execute_recovery_actions(
        self, payment_id: str, recovery_strategy: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute recovery actions based on strategy."""
        if recovery_strategy["strategy"] == "retry":
            retry_result = await self.payment_processing_service.retry_failed_payment(payment_id)
            return {
                "success": retry_result.success,
                "action": "retry_attempted",
                "result": retry_result,
            }
        else:
            return {
                "success": False,
                "action": "manual_review_required",
                "message": "Payment requires manual review",
            }

    def _categorize_failure(self, failure_reason: str) -> str:
        """Categorize payment failure reason."""
        failure_reason_lower = failure_reason.lower()

        if "insufficient" in failure_reason_lower or "declined" in failure_reason_lower:
            return "card_declined"
        elif "expired" in failure_reason_lower:
            return "card_expired"
        elif "network" in failure_reason_lower or "timeout" in failure_reason_lower:
            return "network_error"
        else:
            return "unknown"

    def _is_failure_retryable(self, failure_reason: str) -> bool:
        """Determine if payment failure is retryable."""
        non_retryable_keywords = ["insufficient", "declined", "expired", "invalid"]
        failure_reason_lower = failure_reason.lower()

        return not any(keyword in failure_reason_lower for keyword in non_retryable_keywords)

    def _suggest_failure_action(self, failure_reason: str) -> str:
        """Suggest action based on failure reason."""
        category = self._categorize_failure(failure_reason)

        suggestions = {
            "card_declined": "Update payment method or contact bank",
            "card_expired": "Update payment method with new expiration date",
            "network_error": "Retry payment after network issue resolves",
            "unknown": "Contact support for assistance",
        }

        return suggestions.get(category, "Contact support")
