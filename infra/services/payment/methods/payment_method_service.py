"""
Payment Method Microservice
===========================

Focused microservice for payment method CRUD operations.
Handles creation, validation, and management of user payment methods.

Single Responsibility: Payment method lifecycle management only.
"""

import logging
from datetime import datetime
from typing import Any

from core.domain.payment import (
    PaymentMethod,
    PaymentMethodData,
    PaymentProvider,
)
from apps.bot.services.adapters.payment_adapter_factory import PaymentAdapterFactory

from core.protocols.payment.payment_protocols import (
    PaymentMethodProtocol,
    PaymentMethodResult,
)

logger = logging.getLogger(__name__)


class PaymentMethodService(PaymentMethodProtocol):
    """
    Payment method management microservice.

    Responsibilities:
    - Create and validate payment methods
    - Manage user payment method collections
    - Handle payment method updates and deletions
    - Coordinate with payment gateways for method storage
    """

    def __init__(self, payment_repository, payment_gateway_manager=None):
        self.repository = payment_repository
        self.gateway_manager = payment_gateway_manager
        self.payment_adapter = PaymentAdapterFactory.get_current_adapter()
        logger.info("💳 PaymentMethodService initialized")

    async def create_payment_method(
        self, user_id: int, payment_method_data: PaymentMethodData, provider: str | None = None
    ) -> PaymentMethodResult:
        """
        Create a new payment method for a user.

        Args:
            user_id: User identifier
            payment_method_data: Payment method details
            provider: Optional provider override

        Returns:
            PaymentMethodResult with success status and method details
        """
        try:
            logger.info(f"💳 Creating payment method for user {user_id}")

            # Use default provider if not specified
            provider = provider or PaymentProvider.STRIPE

            # Validate payment method data
            validation_result = await self._validate_payment_method_data(payment_method_data)
            if not validation_result["is_valid"]:
                return PaymentMethodResult(
                    success=False, error_message=f"Validation failed: {validation_result['errors']}"
                )

            # Create payment method with provider
            provider_response = await self.payment_adapter.create_payment_method(
                str(user_id), getattr(payment_method_data, "provider_data", {})
            )

            # Calculate expiration date for card-based methods
            expires_at = None
            if provider == PaymentProvider.STRIPE and "card" in provider_response:
                card = provider_response["card"]
                expires_at = datetime(
                    year=card.get("exp_year", 2025), month=card.get("exp_month", 12), day=1
                )

            # Store payment method in repository
            method_id = await self.repository.create_payment_method(
                user_id=user_id,
                provider=provider,
                provider_method_id=provider_response["id"],
                method_type=payment_method_data.method_type,
                last_four=payment_method_data.last_four,
                brand=payment_method_data.brand,
                expires_at=expires_at,
                is_default=payment_method_data.is_default,
                metadata={
                    "provider_response": provider_response,
                    **(getattr(payment_method_data, "metadata", {}) or {}),
                },
            )

            # Create domain entity
            payment_method = PaymentMethod(
                id=method_id,
                user_id=user_id,
                provider=PaymentProvider(provider) if isinstance(provider, str) else provider,
                method_type=payment_method_data.method_type,
                last_four=payment_method_data.last_four,
                brand=payment_method_data.brand,
                expires_at=expires_at,
                is_default=payment_method_data.is_default,
                is_active=True,
                created_at=datetime.utcnow(),
            )

            logger.info(f"✅ Payment method created successfully: {method_id}")
            return PaymentMethodResult(
                success=True, payment_method=payment_method, provider_response=provider_response
            )

        except Exception as e:
            logger.error(f"❌ Failed to create payment method for user {user_id}: {e}")
            return PaymentMethodResult(success=False, error_message=str(e))

    async def get_user_payment_methods(self, user_id: int) -> list[PaymentMethod]:
        """
        Retrieve all payment methods for a user.

        Args:
            user_id: User identifier

        Returns:
            List of user's payment methods
        """
        try:
            logger.info(f"💳 Retrieving payment methods for user {user_id}")

            methods = await self.repository.get_user_payment_methods(str(user_id))

            payment_methods = [
                PaymentMethod(
                    id=method["id"],
                    user_id=user_id,
                    provider=method["provider"],
                    method_type=method["method_type"],
                    last_four=method["last_four"],
                    brand=method["brand"],
                    expires_at=method["expires_at"],
                    is_default=method["is_default"],
                    is_active=method["is_active"],
                    created_at=method["created_at"],
                )
                for method in methods
            ]

            logger.info(f"📊 Found {len(payment_methods)} payment methods for user {user_id}")
            return payment_methods

        except Exception as e:
            logger.error(f"❌ Failed to get payment methods for user {user_id}: {e}")
            return []

    async def get_payment_method(self, method_id: str) -> PaymentMethod | None:
        """
        Get a specific payment method by ID.

        Args:
            method_id: Payment method identifier

        Returns:
            Payment method details or None if not found
        """
        try:
            method = await self.repository.get_payment_method(method_id)
            if not method:
                return None

            return PaymentMethod(
                id=method["id"],
                user_id=method["user_id"],
                provider=method["provider"],
                method_type=method["method_type"],
                last_four=method["last_four"],
                brand=method["brand"],
                expires_at=method["expires_at"],
                is_default=method["is_default"],
                is_active=method["is_active"],
                created_at=method["created_at"],
            )

        except Exception as e:
            logger.error(f"❌ Failed to get payment method {method_id}: {e}")
            return None

    async def update_payment_method(
        self, method_id: str, updates: dict[str, Any]
    ) -> PaymentMethodResult:
        """
        Update payment method details.

        Args:
            method_id: Payment method identifier
            updates: Dictionary of fields to update

        Returns:
            PaymentMethodResult with updated method details
        """
        try:
            logger.info(f"💳 Updating payment method {method_id}")

            # Get existing method
            existing_method = await self.get_payment_method(method_id)
            if not existing_method:
                return PaymentMethodResult(success=False, error_message="Payment method not found")

            # Apply updates (only allow certain fields to be updated)
            allowed_updates = ["is_default", "metadata"]
            filtered_updates = {k: v for k, v in updates.items() if k in allowed_updates}

            if not filtered_updates:
                return PaymentMethodResult(success=False, error_message="No valid fields to update")

            # Update in repository
            updated_method = await self.repository.update_payment_method(
                method_id, filtered_updates
            )
            if not updated_method:
                return PaymentMethodResult(
                    success=False, error_message="Failed to update payment method"
                )

            # Return updated method
            payment_method = PaymentMethod(**updated_method)

            logger.info(f"✅ Payment method updated successfully: {method_id}")
            return PaymentMethodResult(success=True, payment_method=payment_method)

        except Exception as e:
            logger.error(f"❌ Failed to update payment method {method_id}: {e}")
            return PaymentMethodResult(success=False, error_message=str(e))

    async def delete_payment_method(self, method_id: str, user_id: int) -> bool:
        """
        Delete a payment method.

        Args:
            method_id: Payment method identifier
            user_id: User identifier for authorization

        Returns:
            True if successfully deleted
        """
        try:
            logger.info(f"💳 Deleting payment method {method_id} for user {user_id}")

            # Verify ownership
            method = await self.get_payment_method(method_id)
            if not method or method.user_id != user_id:
                logger.warning(f"❌ Unauthorized deletion attempt for method {method_id}")
                return False

            # Delete from provider first (if supported)
            try:
                # Note: Not all providers support payment method deletion
                # This is handled gracefully as the local record is the source of truth
                logger.info("🔧 Payment method deletion from provider not implemented yet")
            except Exception as e:
                logger.warning(f"⚠️ Provider deletion failed (continuing): {e}")

            # Delete from repository
            success = await self.repository.delete_payment_method(method_id)

            if success:
                logger.info(f"✅ Payment method deleted successfully: {method_id}")
            else:
                logger.error(f"❌ Failed to delete payment method: {method_id}")

            return success

        except Exception as e:
            logger.error(f"❌ Error deleting payment method {method_id}: {e}")
            return False

    async def set_default_payment_method(self, method_id: str, user_id: int) -> bool:
        """
        Set a payment method as default for a user.

        Args:
            method_id: Payment method identifier
            user_id: User identifier

        Returns:
            True if successfully set as default
        """
        try:
            logger.info(f"💳 Setting default payment method {method_id} for user {user_id}")

            # Verify ownership
            method = await self.get_payment_method(method_id)
            if not method or method.user_id != user_id:
                logger.warning(f"❌ Unauthorized default setting for method {method_id}")
                return False

            # Remove default from all other methods for this user
            user_methods = await self.get_user_payment_methods(user_id)
            for user_method in user_methods:
                if user_method.is_default and user_method.id != method_id:
                    await self.update_payment_method(user_method.id, {"is_default": False})

            # Set this method as default
            result = await self.update_payment_method(method_id, {"is_default": True})

            success = result.success
            if success:
                logger.info(f"✅ Default payment method set: {method_id}")
            else:
                logger.error(f"❌ Failed to set default payment method: {method_id}")

            return success

        except Exception as e:
            logger.error(f"❌ Error setting default payment method {method_id}: {e}")
            return False

    async def _validate_payment_method_data(
        self, payment_method_data: PaymentMethodData
    ) -> dict[str, Any]:
        """
        Validate payment method data before creation.

        Args:
            payment_method_data: Payment method data to validate

        Returns:
            Validation result with errors if any
        """
        errors = []

        # Validate required fields
        if not payment_method_data.method_type:
            errors.append("Method type is required")

        if not payment_method_data.last_four:
            errors.append("Last four digits are required")

        # Validate last four format
        if payment_method_data.last_four and not payment_method_data.last_four.isdigit():
            errors.append("Last four must be numeric")

        if payment_method_data.last_four and len(payment_method_data.last_four) != 4:
            errors.append("Last four must be exactly 4 digits")

        # Validate brand for card types
        if payment_method_data.method_type == "card" and not payment_method_data.brand:
            errors.append("Brand is required for card payment methods")

        return {"is_valid": len(errors) == 0, "errors": errors}

    async def health_check(self) -> dict[str, Any]:
        """Health check for payment method service."""
        try:
            # Test repository connection
            test_methods = await self.repository.get_user_payment_methods("0")  # Test query

            # Test adapter connection
            adapter_health = (
                await self.payment_adapter.health_check()
                if hasattr(self.payment_adapter, "health_check")
                else {"status": "unknown"}
            )

            return {
                "service": "PaymentMethodService",
                "status": "healthy",
                "repository_connected": True,
                "adapter_status": adapter_health.get("status", "unknown"),
                "adapter_name": self.payment_adapter.get_adapter_name(),
            }
        except Exception as e:
            return {"service": "PaymentMethodService", "status": "unhealthy", "error": str(e)}
