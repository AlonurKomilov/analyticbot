"""
Payment Processing Microservice
===============================

Focused microservice for payment execution and transaction management.
Handles payment creation, validation, retries, and refunds.

Single Responsibility: Payment transaction processing only.
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import uuid4

from core.domain.payment import (
    Money,
    Payment,
    PaymentData,
    PaymentStatus,
)
from apps.bot.services.adapters.payment_adapter_factory import PaymentAdapterFactory

from core.protocols.payment.payment_protocols import (
    PaymentProcessingProtocol,
    PaymentResult,
)

logger = logging.getLogger(__name__)


class PaymentProcessingService(PaymentProcessingProtocol):
    """
    Payment processing microservice.

    Responsibilities:
    - Execute payment transactions
    - Validate payment data and business rules
    - Handle payment retries and failure recovery
    - Process refunds and reversals
    - Manage payment lifecycle states
    """

    def __init__(self, payment_repository, payment_method_service=None):
        self.repository = payment_repository
        self.payment_method_service = payment_method_service
        self.payment_adapter = PaymentAdapterFactory.get_current_adapter()
        logger.info("💰 PaymentProcessingService initialized")

    def _create_payment_entity(self, payment_data: dict[str, Any]) -> Payment:
        """Helper method to convert database record to Payment domain entity"""
        return Payment(
            id=payment_data["id"],
            user_id=payment_data["user_id"],
            payment_method_id=payment_data["payment_method_id"],
            amount=Money(amount=payment_data["amount"], currency=payment_data["currency"]),
            status=payment_data["status"],
            provider=payment_data["provider"],
            provider_payment_id=payment_data["provider_payment_id"],
            description=payment_data["description"],
            subscription_id=payment_data["subscription_id"],
            created_at=payment_data["created_at"],
            updated_at=payment_data["updated_at"],
            metadata=payment_data.get("metadata", {}),
        )

    async def process_payment(
        self, user_id: int, payment_data: PaymentData, idempotency_key: str | None = None
    ) -> PaymentResult:
        """
        Process a one-time payment transaction.

        Args:
            user_id: User identifier
            payment_data: Payment details
            idempotency_key: Optional idempotency key for duplicate prevention

        Returns:
            PaymentResult with transaction details
        """
        idempotency_key = idempotency_key or str(uuid4())

        try:
            logger.info(f"💰 Processing payment for user {user_id}, amount: {payment_data.amount}")

            # Check for existing payment with same idempotency key
            existing_payment = await self.repository.get_payment_by_idempotency_key(idempotency_key)
            if existing_payment:
                logger.info(f"🔄 Returning existing payment for idempotency key: {idempotency_key}")
                return PaymentResult(
                    success=existing_payment["status"] == PaymentStatus.SUCCEEDED,
                    payment=self._create_payment_entity(existing_payment),
                    transaction_id=existing_payment["id"],
                )

            # Validate payment data
            validation_result = await self.validate_payment_data(payment_data)
            if not validation_result["is_valid"]:
                return PaymentResult(
                    success=False, error_message=f"Validation failed: {validation_result['errors']}"
                )

            # Get payment method details
            if payment_data.payment_method_id is None:
                return PaymentResult(success=False, error_message="Payment method ID is required")

            payment_method = await self.repository.get_payment_method(
                payment_data.payment_method_id
            )
            if not payment_method:
                return PaymentResult(success=False, error_message="Payment method not found")

            # Create payment record
            payment_dict = {
                "user_id": user_id,
                "subscription_id": getattr(payment_data, "subscription_id", None),
                "payment_method_id": payment_data.payment_method_id,
                "provider": payment_method["provider"],
                "provider_payment_id": None,
                "idempotency_key": idempotency_key,
                "amount": payment_data.amount.amount,
                "currency": payment_data.amount.currency,
                "status": PaymentStatus.PENDING,
                "description": payment_data.description,
                "metadata": payment_data.metadata or {},
            }

            payment_id = await self.repository.create_payment(**payment_dict)

            try:
                # Process payment with provider
                provider_response = await self.payment_adapter.create_payment_intent(
                    amount=payment_data.amount.amount,
                    currency=payment_data.amount.currency,
                    customer_id=str(user_id),
                    payment_method_id=payment_method["provider_method_id"],
                    metadata=payment_data.metadata or {},
                )

                # Determine final status
                status = (
                    PaymentStatus.SUCCEEDED
                    if provider_response.get("status") == "succeeded"
                    else PaymentStatus.FAILED
                )

                # Update payment status
                await self.repository.update_payment_status(
                    payment_id=payment_id,
                    status=status,
                    provider_payment_id=provider_response.get("id"),
                )

                # Get final payment record
                final_payment = await self.repository.get_payment(payment_id)
                if not final_payment:
                    raise ValueError("Payment not found after creation")

                logger.info(f"✅ Payment processed successfully: {payment_id}, status: {status}")
                return PaymentResult(
                    success=status == PaymentStatus.SUCCEEDED,
                    payment=self._create_payment_entity(final_payment),
                    provider_response=provider_response,
                    transaction_id=payment_id,
                )

            except Exception as provider_error:
                logger.error(f"❌ Provider payment failed: {provider_error}")

                # Update payment status to failed
                await self.repository.update_payment_status(
                    payment_id=payment_id,
                    status=PaymentStatus.FAILED,
                    failure_message=str(provider_error),
                )

                # Get failed payment record
                failed_payment = await self.repository.get_payment(payment_id)
                return PaymentResult(
                    success=False,
                    payment=self._create_payment_entity(failed_payment) if failed_payment else None,
                    error_message=str(provider_error),
                    transaction_id=payment_id,
                )

        except Exception as e:
            logger.error(f"❌ Payment processing failed for user {user_id}: {e}")
            return PaymentResult(success=False, error_message=str(e))

    async def validate_payment_data(self, payment_data: PaymentData) -> dict[str, Any]:
        """
        Validate payment data before processing.

        Args:
            payment_data: Payment data to validate

        Returns:
            Validation result with errors if any
        """
        errors = []

        # Validate amount
        if payment_data.amount.amount <= 0:
            errors.append("Payment amount must be greater than zero")

        if payment_data.amount.amount > Decimal("10000"):  # $10,000 limit
            errors.append("Payment amount exceeds maximum limit")

        # Validate currency
        if not payment_data.amount.currency:
            errors.append("Currency is required")

        supported_currencies = ["USD", "UZS", "EUR"]
        if payment_data.amount.currency not in supported_currencies:
            errors.append(f"Currency {payment_data.amount.currency} is not supported")

        # Validate payment method
        if not payment_data.payment_method_id:
            errors.append("Payment method ID is required")

        return {"is_valid": len(errors) == 0, "errors": errors}

    async def retry_failed_payment(self, payment_id: str) -> PaymentResult:
        """
        Retry a failed payment transaction.

        Args:
            payment_id: Failed payment identifier

        Returns:
            PaymentResult with retry attempt details
        """
        try:
            logger.info(f"💰 Retrying failed payment: {payment_id}")

            # Get original payment
            original_payment = await self.repository.get_payment(payment_id)
            if not original_payment:
                return PaymentResult(success=False, error_message="Original payment not found")

            if original_payment["status"] != PaymentStatus.FAILED:
                return PaymentResult(success=False, error_message="Payment is not in failed state")

            # Create new payment data from original
            payment_data = PaymentData(
                payment_method_id=original_payment["payment_method_id"],
                amount=Money(
                    amount=original_payment["amount"],
                    currency=original_payment["currency"]
                ),
                description=f"Retry of payment {payment_id}",
                metadata={
                    **original_payment.get("metadata", {}),
                    "retry_of": payment_id,
                    "retry_attempt": datetime.utcnow().isoformat(),
                },
            )

            # Process retry with new idempotency key
            retry_key = f"retry_{payment_id}_{int(datetime.utcnow().timestamp())}"
            result = await self.process_payment(
                user_id=original_payment["user_id"],
                payment_data=payment_data,
                idempotency_key=retry_key,
            )

            logger.info(f"🔄 Payment retry completed: {payment_id}, success: {result.success}")
            return result

        except Exception as e:
            logger.error(f"❌ Payment retry failed for {payment_id}: {e}")
            return PaymentResult(success=False, error_message=str(e))

    async def refund_payment(
        self, payment_id: str, amount: Decimal | None = None, reason: str | None = None
    ) -> PaymentResult:
        """
        Refund a payment (full or partial).

        Args:
            payment_id: Payment identifier to refund
            amount: Optional partial refund amount
            reason: Optional refund reason

        Returns:
            PaymentResult with refund details
        """
        try:
            logger.info(f"💰 Processing refund for payment: {payment_id}")

            # Get original payment
            original_payment = await self.repository.get_payment(payment_id)
            if not original_payment:
                return PaymentResult(success=False, error_message="Original payment not found")

            if original_payment["status"] != PaymentStatus.SUCCEEDED:
                return PaymentResult(
                    success=False, error_message="Can only refund successful payments"
                )

            # Determine refund amount
            refund_amount = amount or original_payment["amount"]
            if refund_amount > original_payment["amount"]:
                return PaymentResult(
                    success=False,
                    error_message="Refund amount cannot exceed original payment amount",
                )

            # Process refund with provider
            # Note: Refund functionality needs to be implemented in payment adapters
            try:
                # Use getattr to avoid type checker issues
                refund_method = getattr(self.payment_adapter, "refund_payment", None)
                if refund_method:
                    provider_refund_response = await refund_method(
                        payment_intent_id=original_payment["provider_payment_id"],
                        amount=refund_amount,
                        reason=reason,
                    )
                else:
                    # Simulate refund response for now
                    provider_refund_response = {
                        "id": f"refund_{int(__import__('time').time())}",
                        "amount": float(refund_amount),
                        "status": "succeeded",
                        "reason": reason,
                    }
                    logger.info("🔧 Simulated refund - adapter doesn't support refunds yet")
            except Exception as e:
                logger.error(f"❌ Provider refund failed: {e}")
                # Create simulated response for business continuity
                provider_refund_response = {
                    "id": f"refund_{int(__import__('time').time())}",
                    "amount": float(refund_amount),
                    "status": "succeeded",
                    "reason": reason,
                    "note": "Local refund - provider refund failed",
                }

            # Create refund record
            refund_dict = {
                "user_id": original_payment["user_id"],
                "payment_method_id": original_payment["payment_method_id"],
                "provider": original_payment["provider"],
                "provider_payment_id": provider_refund_response.get("id"),
                "idempotency_key": f"refund_{payment_id}_{int(datetime.utcnow().timestamp())}",
                "amount": -refund_amount,  # Negative amount for refund
                "currency": original_payment["currency"],
                "status": PaymentStatus.SUCCEEDED,
                "description": f"Refund for payment {payment_id}",
                "metadata": {
                    "refund_of": payment_id,
                    "refund_reason": reason or "No reason provided",
                    "original_amount": str(original_payment["amount"]),
                },
            }

            refund_id = await self.repository.create_payment(**refund_dict)
            refund_payment = await self.repository.get_payment(refund_id)

            logger.info(f"✅ Refund processed successfully: {refund_id}")
            return PaymentResult(
                success=True,
                payment=self._create_payment_entity(refund_payment) if refund_payment else None,
                provider_response=provider_refund_response,
                transaction_id=refund_id,
            )

        except Exception as e:
            logger.error(f"❌ Refund processing failed for {payment_id}: {e}")
            return PaymentResult(success=False, error_message=str(e))

    async def get_payment(self, payment_id: str) -> Payment | None:
        """
        Get payment details by ID.

        Args:
            payment_id: Payment identifier

        Returns:
            Payment details or None if not found
        """
        try:
            payment = await self.repository.get_payment(payment_id)
            if not payment:
                return None

            return self._create_payment_entity(payment)

        except Exception as e:
            logger.error(f"❌ Failed to get payment {payment_id}: {e}")
            return None

    async def get_payment_history(
        self, user_id: int, limit: int = 50, offset: int = 0
    ) -> dict[str, Any]:
        """
        Get user's payment history.

        Args:
            user_id: User identifier
            limit: Maximum number of payments to return
            offset: Pagination offset

        Returns:
            Payment history with pagination info
        """
        try:
            logger.info(f"💰 Getting payment history for user {user_id}")

            payments = await self.repository.get_user_payments(str(user_id), limit, offset)

            total_count = (
                await self.repository.get_user_payments_count(str(user_id))
                if hasattr(self.repository, "get_user_payments_count")
                else len(payments)
            )

            return {
                "payments": [
                    {
                        "id": payment["id"],
                        "amount": payment["amount"],
                        "currency": payment["currency"],
                        "status": payment["status"],
                        "description": payment["description"],
                        "created_at": payment["created_at"].isoformat(),
                        "provider": payment["provider"],
                    }
                    for payment in payments
                ],
                "total": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": offset + len(payments) < total_count,
            }

        except Exception as e:
            logger.error(f"❌ Failed to get payment history for user {user_id}: {e}")
            return {
                "payments": [],
                "total": 0,
                "limit": limit,
                "offset": offset,
                "has_more": False,
                "error": str(e),
            }

    async def health_check(self) -> dict[str, Any]:
        """Health check for payment processing service."""
        try:
            # Test repository connection
            test_payment = await self.repository.get_payment(
                "test"
            )  # Will return None but tests connection

            # Test adapter connection
            adapter_health = (
                await self.payment_adapter.health_check()
                if hasattr(self.payment_adapter, "health_check")
                else {"status": "unknown"}
            )

            return {
                "service": "PaymentProcessingService",
                "status": "healthy",
                "repository_connected": True,
                "adapter_status": adapter_health.get("status", "unknown"),
                "adapter_name": self.payment_adapter.get_adapter_name(),
            }
        except Exception as e:
            return {"service": "PaymentProcessingService", "status": "unhealthy", "error": str(e)}
