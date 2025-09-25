"""
Dependency Injection Container
Clean Architecture DI implementation for service management
"""

import logging
from collections.abc import Callable
from contextlib import asynccontextmanager
from typing import Any, TypeVar

from config.demo_mode_config import DemoModeConfig
from core.protocols import (
    AdminServiceProtocol,
    AIServiceProtocol,
    AnalyticsServiceProtocol,
    AuthServiceProtocol,
    DatabaseServiceProtocol,
    DemoDataServiceProtocol,
    EmailServiceProtocol,
    PaymentServiceProtocol,
    ServiceProtocol,
    TelegramAPIServiceProtocol,
)

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=ServiceProtocol)


class ServiceRegistration:
    """Service registration metadata"""

    def __init__(
        self,
        interface: type[ServiceProtocol],
        implementation: type[ServiceProtocol],
        singleton: bool = True,
        factory: Callable | None = None,
    ):
        self.interface = interface
        self.implementation = implementation
        self.singleton = singleton
        self.factory = factory


class DIContainer:
    """
    Dependency Injection Container
    Manages service lifecycle and dependencies
    """

    def __init__(self):
        self._registrations: dict[str, ServiceRegistration] = {}
        self._singletons: dict[str, ServiceProtocol] = {}
        self._initialized = False

    def register_service(
        self,
        interface: type[T],
        implementation: type[T],
        singleton: bool = True,
        factory: Callable | None = None,
    ) -> None:
        """
        Register a service implementation

        Args:
            interface: Service interface/protocol
            implementation: Concrete implementation class
            singleton: Whether to use singleton pattern
            factory: Optional factory function for complex initialization
        """
        key = self._get_service_key(interface)
        registration = ServiceRegistration(interface, implementation, singleton, factory)
        self._registrations[key] = registration

        logger.debug(f"Registered service: {key} -> {implementation.__name__}")

    def get_service(self, interface: type[T]) -> T:
        """
        Get service instance

        Args:
            interface: Service interface to retrieve

        Returns:
            Service instance

        Raises:
            ValueError: If service not registered
        """
        key = self._get_service_key(interface)

        if key not in self._registrations:
            raise ValueError(f"Service {key} not registered")

        registration = self._registrations[key]

        # Return singleton if already created
        if registration.singleton and key in self._singletons:
            return self._singletons[key]

        # Create new instance
        if registration.factory:
            instance = registration.factory()
        else:
            instance = registration.implementation()

        # Cache singleton
        if registration.singleton:
            self._singletons[key] = instance

        logger.debug(f"Created service instance: {key}")
        return instance

    def is_registered(self, interface: type[ServiceProtocol]) -> bool:
        """Check if service is registered"""
        key = self._get_service_key(interface)
        return key in self._registrations

    def clear_cache(self) -> None:
        """Clear singleton cache"""
        self._singletons.clear()
        logger.info("Cleared service cache")

    def get_registered_services(self) -> dict[str, str]:
        """Get list of registered services"""
        return {key: reg.implementation.__name__ for key, reg in self._registrations.items()}

    async def health_check_all(self) -> dict[str, Any]:
        """Run health check on all services"""
        results = {}

        for key, registration in self._registrations.items():
            try:
                service = self.get_service(registration.interface)
                health = await service.health_check()
                results[key] = health
            except Exception as e:
                logger.error(f"Health check failed for {key}: {e}")
                results[key] = {"status": "error", "error": str(e)}

        return results

    @staticmethod
    def _get_service_key(interface: type[ServiceProtocol]) -> str:
        """Get service key from interface"""
        return interface.__name__


def configure_services(container: DIContainer, demo_config: DemoModeConfig) -> None:
    """
    Configure all services based on demo mode settings

    Args:
        container: DI container to configure
        demo_config: Demo mode configuration
    """
    logger.info("Configuring services with demo mode settings")

    # Analytics Service
    if demo_config.should_use_mock_service("analytics"):
        try:
            from apps.api.__mocks__.services.mock_analytics_service import (
                MockAnalyticsService,
            )

            container.register_service(AnalyticsServiceProtocol, MockAnalyticsService)
            logger.info("Registered MockAnalyticsService")
        except ImportError as e:
            logger.error(f"Failed to import MockAnalyticsService: {e}")
    else:
        try:
            from apps.bot.services.adapters.telegram_analytics_adapter import (
                TelegramAnalyticsAdapter,
            )

            container.register_service(AnalyticsServiceProtocol, TelegramAnalyticsAdapter)
            logger.info("Registered TelegramAnalyticsAdapter")
        except ImportError as e:
            logger.error(f"Failed to import TelegramAnalyticsAdapter: {e}")
            # Fallback to mock service
            try:
                from apps.api.__mocks__.services.mock_analytics_service import (
                    MockAnalyticsService,
                )

                container.register_service(AnalyticsServiceProtocol, MockAnalyticsService)
                logger.info("Fallback: Registered MockAnalyticsService")
            except ImportError:
                logger.error("No analytics service available")

    # Payment Service
    if demo_config.should_use_mock_service("payment"):
        try:
            from apps.api.__mocks__.services.mock_payment_service import (
                MockPaymentService,
            )

            container.register_service(PaymentServiceProtocol, MockPaymentService)
            logger.info("Registered MockPaymentService")
        except ImportError as e:
            logger.error(f"Failed to import MockPaymentService: {e}")
    else:
        logger.info("Real payment service not yet implemented")

    # Database Service
    if demo_config.should_use_mock_service("database"):
        from apps.api.__mocks__.database.mock_database import MockDatabase

        container.register_service(DatabaseServiceProtocol, MockDatabase)
        logger.info("Registered MockDatabase")
    else:
        # Real database service would be registered here
        # For now, we'll use a placeholder
        logger.info("Real database service not yet implemented")

    # AI Services
    if demo_config.should_use_mock_service("ai_services"):
        try:
            from apps.api.__mocks__.services.mock_ai_service import MockAIService

            container.register_service(AIServiceProtocol, MockAIService)
            logger.info("Registered MockAIService")
        except ImportError as e:
            logger.error(f"Failed to import MockAIService: {e}")
    else:
        # Real AI service would be registered here
        logger.info("Real AI service not yet implemented")

    # Telegram API Service
    if demo_config.should_use_mock_service("telegram_api"):
        from apps.api.__mocks__.services.mock_telegram_service import (
            MockTelegramService,
        )

        container.register_service(TelegramAPIServiceProtocol, MockTelegramService)
        logger.info("Registered MockTelegramService")
    else:
        # Real Telegram service would be registered here
        logger.info("Real Telegram service not yet implemented")

    # Email Service
    if demo_config.should_use_mock_service("email_delivery"):
        from apps.api.__mocks__.services.mock_email_service import MockEmailService

        container.register_service(EmailServiceProtocol, MockEmailService)
        logger.info("Registered MockEmailService")
    else:
        # Real email service would be registered here
        logger.info("Real email service not yet implemented")

    # Auth Service
    if demo_config.should_use_mock_service("auth"):
        try:
            from apps.api.__mocks__.services.mock_auth_service import MockAuthService

            container.register_service(AuthServiceProtocol, MockAuthService)
            logger.info("Registered MockAuthService")
        except ImportError as e:
            logger.error(f"Failed to import MockAuthService: {e}")
    else:
        logger.info("Real auth service not yet implemented")

    # Admin Service
    if demo_config.should_use_mock_service("admin"):
        try:
            from apps.api.__mocks__.services.mock_admin_service import MockAdminService

            container.register_service(AdminServiceProtocol, MockAdminService)
            logger.info("Registered MockAdminService")
        except ImportError as e:
            logger.error(f"Failed to import MockAdminService: {e}")
    else:
        logger.info("Real admin service not yet implemented")

    # Demo Data Service
    if demo_config.should_use_mock_service("demo_data"):
        try:
            from apps.api.__mocks__.services.mock_demo_data_service import (
                MockDemoDataService,
            )

            container.register_service(DemoDataServiceProtocol, MockDemoDataService)
            logger.info("Registered MockDemoDataService")
        except ImportError as e:
            logger.error(f"Failed to import MockDemoDataService: {e}")
    else:
        logger.info("Real demo data service not needed in production")

    container._initialized = True
    logger.info("Service configuration complete")


# Global DI container instance
container = DIContainer()


@asynccontextmanager
async def get_service_context(demo_config: DemoModeConfig):
    """Context manager for service lifecycle"""
    if not container._initialized:
        configure_services(container, demo_config)

    try:
        yield container
    finally:
        # Cleanup if needed
        pass
