"""
Payment Gateway Manager Microservice
====================================

Focused microservice for payment gateway management and switching.
Handles gateway configuration, health monitoring, and provider coordination.

Single Responsibility: Gateway management and coordination only.
"""

import logging
from typing import Any

from apps.bot.services.adapters.payment_adapter_factory import (
    PaymentAdapterFactory,
    PaymentGateway,
)

from ..protocols.payment_protocols import PaymentGatewayManagerProtocol

logger = logging.getLogger(__name__)


class PaymentGatewayManagerService(PaymentGatewayManagerProtocol):
    """
    Payment gateway management microservice.

    Responsibilities:
    - Manage payment gateway configurations
    - Switch between payment providers
    - Monitor gateway health and availability
    - Test gateway connections
    - Provide gateway status information
    """

    def __init__(self):
        self.supported_gateways = [PaymentGateway.STRIPE, PaymentGateway.MOCK]
        self.current_gateway = PaymentAdapterFactory.get_current_adapter()
        logger.info("🔧 PaymentGatewayManagerService initialized")

    async def get_current_gateway(self) -> str:
        """
        Get currently active payment gateway.

        Returns:
            Name of current gateway
        """
        try:
            return self.current_gateway.get_adapter_name()
        except Exception as e:
            logger.error(f"❌ Failed to get current gateway: {e}")
            return "unknown"

    async def switch_gateway(self, gateway_name: str) -> bool:
        """
        Switch to a different payment gateway.

        Args:
            gateway_name: Name of gateway to switch to

        Returns:
            True if successfully switched
        """
        try:
            logger.info(f"🔧 Switching to gateway: {gateway_name}")

            # Map gateway name to enum
            gateway_mapping = {
                "stripe": PaymentGateway.STRIPE,
                "mock": PaymentGateway.MOCK,
                "test": PaymentGateway.MOCK,
            }

            gateway_enum = gateway_mapping.get(gateway_name.lower())
            if not gateway_enum:
                logger.error(f"❌ Unsupported gateway: {gateway_name}")
                return False

            # Test gateway connection before switching
            test_result = await self.test_gateway_connection(gateway_name)
            if not test_result.get("connected", False):
                logger.error(f"❌ Gateway connection test failed: {gateway_name}")
                return False

            # Switch to new gateway
            PaymentAdapterFactory.set_current_adapter(gateway_enum)
            self.current_gateway = PaymentAdapterFactory.get_current_adapter()

            logger.info(f"✅ Successfully switched to gateway: {gateway_name}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to switch gateway to {gateway_name}: {e}")
            return False

    async def get_supported_gateways(self) -> list[str]:
        """
        Get list of supported payment gateways.

        Returns:
            List of supported gateway names
        """
        try:
            gateway_names = []
            for gateway in self.supported_gateways:
                if gateway == PaymentGateway.STRIPE:
                    gateway_names.append("stripe")
                elif gateway == PaymentGateway.MOCK:
                    gateway_names.append("mock")

            logger.info(f"🔧 Supported gateways: {gateway_names}")
            return gateway_names

        except Exception as e:
            logger.error(f"❌ Failed to get supported gateways: {e}")
            return []

    async def test_gateway_connection(self, gateway_name: str) -> dict[str, Any]:
        """
        Test connection to a payment gateway.

        Args:
            gateway_name: Name of gateway to test

        Returns:
            Connection test result
        """
        try:
            logger.info(f"🔧 Testing gateway connection: {gateway_name}")

            # Get current gateway for comparison
            current_gateway_name = await self.get_current_gateway()

            # If testing current gateway, use existing adapter
            if gateway_name.lower() == current_gateway_name.lower():
                adapter = self.current_gateway
            else:
                # Temporarily create adapter for testing
                gateway_mapping = {
                    "stripe": PaymentGateway.STRIPE,
                    "mock": PaymentGateway.MOCK,
                    "test": PaymentGateway.MOCK,
                }

                gateway_enum = gateway_mapping.get(gateway_name.lower())
                if not gateway_enum:
                    return {
                        "gateway": gateway_name,
                        "connected": False,
                        "error": f"Unsupported gateway: {gateway_name}",
                    }

                # Create temporary adapter for testing
                PaymentAdapterFactory.get_current_adapter()
                PaymentAdapterFactory.set_current_adapter(gateway_enum)
                adapter = PaymentAdapterFactory.get_current_adapter()

                # Restore original adapter after test
                if gateway_name.lower() != current_gateway_name.lower():
                    # We'll restore it after the test
                    pass

            # Test adapter functionality
            test_result = await self._test_adapter_health(adapter, gateway_name)

            # Restore original adapter if we switched for testing
            if gateway_name.lower() != current_gateway_name.lower():
                # Find original gateway enum and restore
                for gateway_enum in self.supported_gateways:
                    test_adapter = PaymentAdapterFactory.set_current_adapter(gateway_enum)
                    if test_adapter.get_adapter_name().lower() == current_gateway_name.lower():
                        self.current_gateway = test_adapter
                        break

            return test_result

        except Exception as e:
            logger.error(f"❌ Gateway connection test failed for {gateway_name}: {e}")
            return {"gateway": gateway_name, "connected": False, "error": str(e)}

    async def get_gateway_health(self) -> dict[str, Any]:
        """
        Get health status of all configured gateways.

        Returns:
            Health status for all gateways
        """
        try:
            logger.info("🔧 Checking health of all gateways")

            gateway_health = {}
            supported_names = await self.get_supported_gateways()

            # Test each supported gateway
            for gateway_name in supported_names:
                health_result = await self.test_gateway_connection(gateway_name)
                gateway_health[gateway_name] = {
                    "status": ("healthy" if health_result.get("connected", False) else "unhealthy"),
                    "connected": health_result.get("connected", False),
                    "response_time": health_result.get("response_time", 0),
                    "error": health_result.get("error"),
                    "last_checked": health_result.get("checked_at"),
                }

            # Calculate overall health
            healthy_gateways = sum(
                1 for health in gateway_health.values() if health["status"] == "healthy"
            )
            total_gateways = len(gateway_health)

            overall_status = "healthy" if healthy_gateways == total_gateways else "degraded"
            if healthy_gateways == 0:
                overall_status = "unhealthy"

            return {
                "overall_status": overall_status,
                "healthy_gateways": healthy_gateways,
                "total_gateways": total_gateways,
                "current_gateway": await self.get_current_gateway(),
                "gateway_health": gateway_health,
                "checked_at": __import__("datetime").datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Failed to check gateway health: {e}")
            return {
                "overall_status": "unhealthy",
                "error": str(e),
                "gateway_health": {},
                "checked_at": __import__("datetime").datetime.utcnow().isoformat(),
            }

    async def _test_adapter_health(self, adapter, gateway_name: str) -> dict[str, Any]:
        """
        Test specific adapter health and functionality.

        Args:
            adapter: Payment adapter to test
            gateway_name: Name of the gateway

        Returns:
            Health test result
        """
        import time

        start_time = time.time()

        try:
            # Test basic adapter functionality
            adapter_name = adapter.get_adapter_name()

            # Test if adapter has required methods
            required_methods = [
                "create_payment_intent",
                "create_payment_method",
                "create_subscription",
                "cancel_subscription",
            ]

            missing_methods = []
            for method in required_methods:
                if not hasattr(adapter, method):
                    missing_methods.append(method)

            if missing_methods:
                return {
                    "gateway": gateway_name,
                    "connected": False,
                    "error": f"Missing required methods: {missing_methods}",
                    "response_time": round((time.time() - start_time) * 1000, 2),
                    "checked_at": __import__("datetime").datetime.utcnow().isoformat(),
                }

            # Test adapter health check if available
            if hasattr(adapter, "health_check"):
                health_result = await adapter.health_check()
                if not health_result.get("status") == "healthy":
                    return {
                        "gateway": gateway_name,
                        "connected": False,
                        "error": f"Adapter health check failed: {health_result}",
                        "response_time": round((time.time() - start_time) * 1000, 2),
                        "checked_at": __import__("datetime").datetime.utcnow().isoformat(),
                    }

            # Basic connection test passed
            return {
                "gateway": gateway_name,
                "connected": True,
                "adapter_name": adapter_name,
                "response_time": round((time.time() - start_time) * 1000, 2),
                "checked_at": __import__("datetime").datetime.utcnow().isoformat(),
            }

        except Exception as e:
            return {
                "gateway": gateway_name,
                "connected": False,
                "error": str(e),
                "response_time": round((time.time() - start_time) * 1000, 2),
                "checked_at": __import__("datetime").datetime.utcnow().isoformat(),
            }

    async def configure_gateway(self, gateway_name: str, config: dict[str, Any]) -> bool:
        """
        Configure a payment gateway with new settings.

        Args:
            gateway_name: Name of gateway to configure
            config: Configuration parameters

        Returns:
            True if successfully configured
        """
        try:
            logger.info(f"🔧 Configuring gateway: {gateway_name}")

            # Validate configuration parameters
            if not self._validate_gateway_config(gateway_name, config):
                logger.error(f"❌ Invalid configuration for {gateway_name}")
                return False

            # Apply configuration (in real implementation, this would update
            # environment variables, database settings, etc.)
            success = await self._apply_gateway_config(gateway_name, config)

            if success:
                logger.info(f"✅ Gateway configured successfully: {gateway_name}")

                # Test the new configuration
                test_result = await self.test_gateway_connection(gateway_name)
                if not test_result.get("connected", False):
                    logger.warning(f"⚠️ Gateway configuration test failed: {gateway_name}")
                    return False

            return success

        except Exception as e:
            logger.error(f"❌ Failed to configure gateway {gateway_name}: {e}")
            return False

    def _validate_gateway_config(self, gateway_name: str, config: dict[str, Any]) -> bool:
        """Validate gateway configuration parameters."""
        if gateway_name.lower() == "stripe":
            required_keys = ["api_key", "webhook_secret"]
            return all(key in config for key in required_keys)
        elif gateway_name.lower() == "mock":
            # Mock gateway doesn't require specific configuration
            return True
        else:
            # Unknown gateway
            return False

    async def _apply_gateway_config(self, gateway_name: str, config: dict[str, Any]) -> bool:
        """Apply configuration to gateway."""
        # In real implementation, this would:
        # 1. Update environment variables
        # 2. Update database configuration
        # 3. Restart services if needed
        # 4. Validate new configuration

        # For now, just simulate successful configuration
        logger.info(f"🔧 Applied configuration for {gateway_name}: {list(config.keys())}")
        return True

    async def get_gateway_metrics(
        self, gateway_name: str, period_hours: int = 24
    ) -> dict[str, Any]:
        """
        Get performance metrics for a specific gateway.

        Args:
            gateway_name: Name of gateway
            period_hours: Period for metrics in hours

        Returns:
            Gateway performance metrics
        """
        try:
            logger.info(f"🔧 Getting metrics for gateway: {gateway_name}")

            # In real implementation, this would query metrics database
            # For now, return simulated metrics
            metrics = {
                "gateway": gateway_name,
                "period_hours": period_hours,
                "total_transactions": 1000,
                "successful_transactions": 950,
                "failed_transactions": 50,
                "success_rate": 95.0,
                "average_response_time": 1.2,
                "uptime_percentage": 99.5,
                "error_rate": 5.0,
            }

            return metrics

        except Exception as e:
            logger.error(f"❌ Failed to get metrics for {gateway_name}: {e}")
            return {"gateway": gateway_name, "error": str(e)}

    async def health_check(self) -> dict[str, Any]:
        """Health check for gateway manager service."""
        try:
            current_gateway = await self.get_current_gateway()
            supported_gateways = await self.get_supported_gateways()

            return {
                "service": "PaymentGatewayManagerService",
                "status": "healthy",
                "current_gateway": current_gateway,
                "supported_gateways": supported_gateways,
                "gateway_count": len(supported_gateways),
            }
        except Exception as e:
            return {
                "service": "PaymentGatewayManagerService",
                "status": "unhealthy",
                "error": str(e),
            }
