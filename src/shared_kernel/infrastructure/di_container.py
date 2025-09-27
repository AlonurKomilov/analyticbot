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
    AnalyticsFusionServiceProtocol,
    AnalyticsServiceProtocol,
    AuthServiceProtocol,
    DatabaseServiceProtocol,
    DemoDataServiceProtocol,
    EmailServiceProtocol,
    PaymentServiceProtocol,
    RedisClientProtocol,
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

    async def get_service(self, interface: type[T]) -> T:
        """
        Get service instance - FIXED: Now properly handles async factories

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

        # Create new instance - FIXED: Await async factories
        if registration.factory:
            instance = await registration.factory()
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

    # ✅ NEW: Register asyncpg Pool in DI container for proper lifecycle management
    async def get_asyncpg_pool_factory():
        """Factory for creating asyncpg pool"""
        from src.shared_kernel.infrastructure.di import get_container

        shared_container = get_container()
        return await shared_container.asyncpg_pool()

    # Register asyncpg Pool as a singleton service
    container.register_service(
        interface=type(None),  # Will be replaced with proper Pool protocol
        implementation=type(None),
        singleton=True,
        factory=get_asyncpg_pool_factory,
    )

    # ✅ NEW: Register Analytics Fusion Service
    # Always use real analytics fusion service - demo vs real is handled within the service
    async def get_analytics_fusion_service_factory():
        """Factory for creating analytics fusion service"""
        try:
            # Use migrated analytics fusion service
            from src.analytics.application.services.analytics_fusion_service import (
                AnalyticsFusionService,
            )

            return AnalyticsFusionService()
        except ImportError as e:
            logger.error(f"Failed to import AnalyticsFusionService: {e}")
            return None

    container.register_service(
        interface=AnalyticsFusionServiceProtocol,
        implementation=type(None),  # Factory-based creation
        singleton=True,
        factory=get_analytics_fusion_service_factory,
    )
    logger.info("Registered AnalyticsFusionService via DI factory")

    # ✅ NEW: Register Redis Client
    async def get_redis_client_factory():
        """Factory for creating Redis client"""
        try:
            from src.shared_kernel.infrastructure.cache.async_redis_client import (
                create_redis_client,
            )

            return create_redis_client()
        except ImportError as e:
            logger.error(f"Failed to import Redis client: {e}")
            return None

    container.register_service(
        interface=RedisClientProtocol,
        implementation=type(None),  # Factory-based creation
        singleton=True,
        factory=get_redis_client_factory,
    )
    logger.info("Registered RedisClient via DI factory")

    # Analytics Service
    if demo_config.should_use_mock_service("analytics"):
        try:
            from src.mock_services.services.mock_analytics_service import (
                MockAnalyticsService,
            )

            container.register_service(AnalyticsServiceProtocol, MockAnalyticsService)
            logger.info("Registered MockAnalyticsService")
        except ImportError as e:
            logger.error(f"Failed to import MockAnalyticsService: {e}")
    else:
        try:
            from src.bot_service.application.services.adapters.telegram_analytics_adapter import (
                TelegramAnalyticsAdapter,
            )

            container.register_service(AnalyticsServiceProtocol, TelegramAnalyticsAdapter)
            logger.info("Registered TelegramAnalyticsAdapter")
        except ImportError as e:
            logger.error(f"Failed to import TelegramAnalyticsAdapter: {e}")
            # Fallback to mock service
            try:
                from src.mock_services.services.mock_analytics_service import (
                    MockAnalyticsService,
                )

                container.register_service(AnalyticsServiceProtocol, MockAnalyticsService)
                logger.info("Fallback: Registered MockAnalyticsService")
            except ImportError:
                logger.error("No analytics service available")

    # Payment Service
    if demo_config.should_use_mock_service("payment"):
        try:
            from src.mock_services.services.mock_payment_service import (
                MockPaymentService,
            )

            container.register_service(PaymentServiceProtocol, MockPaymentService)
            logger.info("Registered MockPaymentService")
        except ImportError as e:
            logger.error(f"Failed to import MockPaymentService: {e}")
    else:
        # ✅ NEW: Register real payment service
        async def get_payment_service_factory():
            """Factory for creating real payment service"""
            from src.bot_service.application.services.payment_service import (
                PaymentService,
            )
            from src.shared_kernel.infrastructure.di import get_container

            shared_container = get_container()
            payment_repo = await shared_container.payment_repo()
            return PaymentService(payment_repo)

        container.register_service(
            interface=PaymentServiceProtocol,
            implementation=type(None),  # Factory-based creation
            singleton=True,
            factory=get_payment_service_factory,
        )
        logger.info("Registered real PaymentService")

    # Database Service
    if demo_config.should_use_mock_service("database"):
        from src.api_service.infrastructure.testing.database.mock_database import (
            MockDatabase,
        )

        container.register_service(DatabaseServiceProtocol, MockDatabase)
        logger.info("Registered MockDatabase")
    else:
        # ✅ NEW: Register real database repositories with proper pool injection
        async def get_user_repo_factory():
            from src.shared_kernel.infrastructure.di import get_container

            shared_container = get_container()
            return await shared_container.user_repo()

        async def get_channel_repo_factory():
            from src.shared_kernel.infrastructure.di import get_container

            shared_container = get_container()
            return await shared_container.channel_repo()

        # Register repository factories
        container.register_service(
            interface=type(None),  # UserRepositoryProtocol when created
            implementation=type(None),
            singleton=True,
            factory=get_user_repo_factory,
        )

        container.register_service(
            interface=type(None),  # ChannelRepositoryProtocol when created
            implementation=type(None),
            singleton=True,
            factory=get_channel_repo_factory,
        )

        logger.info("Registered real database repositories with pool injection")

    # AI Services
    if demo_config.should_use_mock_service("ai_services"):
        try:
            from src.mock_services.services import MockAIService

            container.register_service(AIServiceProtocol, MockAIService)
            logger.info("Registered MockAIService")
        except ImportError as e:
            logger.error(f"Failed to import MockAIService: {e}")
    else:
        # ✅ NEW: Register real AI service (AIInsightsGenerator)
        async def get_ai_service_factory():
            """Factory for creating real AI service"""
            from src.bot_service.application.services.ml.ai_insights import (
                AIInsightsGenerator,
            )

            return AIInsightsGenerator()

        container.register_service(
            interface=AIServiceProtocol,
            implementation=type(None),  # Factory-based creation
            singleton=True,
            factory=get_ai_service_factory,
        )
        logger.info("Registered real AIService (AIInsightsGenerator)")

    # Telegram API Service
    if demo_config.should_use_mock_service("telegram_api"):
        from src.mock_services.services import MockTelegramService

        container.register_service(TelegramAPIServiceProtocol, MockTelegramService)
        logger.info("Registered MockTelegramService")
    else:
        # ✅ FIXED: Register real Telegram service
        async def get_telegram_service_factory():
            """Factory for creating real Telegram service"""
            from config.settings import settings
            from infra.tg.telethon_client import TelethonClient

            return TelethonClient(
                api_id=settings.TELEGRAM_API_ID,
                api_hash=settings.TELEGRAM_API_HASH,
                session_name=settings.TELEGRAM_SESSION_NAME,
            )

        container.register_service(
            interface=TelegramAPIServiceProtocol,
            implementation=type(None),  # Factory-based creation
            singleton=True,
            factory=get_telegram_service_factory,
        )
        logger.info("Registered real TelegramService (TelegramClient)")

    # Email Service
    if demo_config.should_use_mock_service("email_delivery"):
        from src.mock_services.services.mock_email_service import MockEmailService

        container.register_service(EmailServiceProtocol, MockEmailService)
        logger.info("Registered MockEmailService")
    else:
        # ✅ FIXED: Register email service with proper fallback
        async def get_email_service_factory():
            """Factory for creating email service with fallback"""
            try:
                # Try to import real SMTP service if it exists
                from config.settings import settings
                from src.shared_kernel.infrastructure.email.smtp_email_service import (
                    SMTPEmailService,
                )

                return SMTPEmailService(
                    smtp_host=settings.SMTP_HOST,
                    smtp_port=settings.SMTP_PORT,
                    smtp_user=settings.SMTP_USER,
                    smtp_password=settings.SMTP_PASSWORD,
                    use_tls=settings.SMTP_USE_TLS,
                )
            except ImportError:
                # Fallback to mock service if SMTP service not available
                logger.warning("Real SMTP service not available, falling back to mock")
                from src.mock_services.services.mock_email_service import (
                    MockEmailService,
                )

                return MockEmailService()

        container.register_service(
            interface=EmailServiceProtocol,
            implementation=type(None),  # Factory-based creation
            singleton=True,
            factory=get_email_service_factory,
        )
        logger.info("Registered real EmailService (SMTPEmailService)")

    # Auth Service
    if demo_config.should_use_mock_service("auth"):
        try:
            from src.mock_services.services import MockAuthService

            container.register_service(AuthServiceProtocol, MockAuthService)
            logger.info("Registered MockAuthService")
        except ImportError as e:
            logger.error(f"Failed to import MockAuthService: {e}")
    else:
        # ✅ NEW: Register real auth service (SecurityManager)
        async def get_auth_service_factory():
            """Factory for creating real auth service"""
            from src.security.auth import SecurityManager

            return SecurityManager()

        container.register_service(
            interface=AuthServiceProtocol,
            implementation=type(None),  # Factory-based creation
            singleton=True,
            factory=get_auth_service_factory,
        )
        logger.info("Registered real AuthService (SecurityManager)")

    # Admin Service
    if demo_config.should_use_mock_service("admin"):
        try:
            from src.mock_services.services import MockAdminService

            container.register_service(AdminServiceProtocol, MockAdminService)
            logger.info("Registered MockAdminService")
        except ImportError as e:
            logger.error(f"Failed to import MockAdminService: {e}")
    else:
        # ✅ NEW: Register real admin service (SuperAdminService)
        async def get_admin_service_factory():
            """Factory for creating real admin service"""
            from src.identity.application.services.superadmin_service import (
                SuperAdminService,
            )
            from src.shared_kernel.infrastructure.di import get_container

            shared_container = get_container()
            db_session = (
                await shared_container.db_session()
            )  # Get SQLAlchemy session for admin service
            return SuperAdminService(db_session)

        container.register_service(
            interface=AdminServiceProtocol,
            implementation=type(None),  # Factory-based creation
            singleton=True,
            factory=get_admin_service_factory,
        )
        logger.info("Registered real AdminService (SuperAdminService)")

    # Demo Data Service
    if demo_config.should_use_mock_service("demo_data"):
        try:
            from src.mock_services.services import MockDemoDataService

            container.register_service(DemoDataServiceProtocol, MockDemoDataService)
            logger.info("Registered MockDemoDataService")
        except ImportError as e:
            logger.error(f"Failed to import MockDemoDataService: {e}")
    else:
        logger.info("Real demo data service not needed in production")

    # ✅ NEW: Identity Domain Services
    # Register Identity Domain Use Cases and Services
    async def get_user_repository_factory():
        """Factory for creating user repository"""
        from src.identity.infrastructure.repositories.asyncpg_user_repository import (
            AsyncpgUserRepository,
        )
        from src.shared_kernel.infrastructure.di import get_container

        shared_container = get_container()
        pool = await shared_container.asyncpg_pool()
        return AsyncpgUserRepository(pool)

    async def get_jwt_token_service_factory():
        """Factory for creating JWT token service"""
        from src.identity.infrastructure.external.jwt_token_service import (
            JWTTokenService,
        )

        return JWTTokenService()

    async def get_register_user_use_case_factory():
        """Factory for creating register user use case"""
        from src.identity.application.use_cases.register_user import RegisterUserUseCase

        user_repo = await container.get_service(type(None))  # UserRepository
        return RegisterUserUseCase(user_repo)

    async def get_authenticate_user_use_case_factory():
        """Factory for creating authenticate user use case"""
        from src.identity.application.use_cases.authenticate_user import (
            AuthenticateUserUseCase,
        )

        user_repo = await container.get_service(type(None))  # UserRepository
        return AuthenticateUserUseCase(user_repo)

    # Register identity services
    container.register_service(
        interface=type(None),  # UserRepositoryProtocol when created
        implementation=type(None),
        singleton=True,
        factory=get_user_repository_factory,
    )

    container.register_service(
        interface=type(None),  # JWTTokenServiceProtocol when created
        implementation=type(None),
        singleton=True,
        factory=get_jwt_token_service_factory,
    )

    container.register_service(
        interface=type(None),  # RegisterUserUseCaseProtocol when created
        implementation=type(None),
        singleton=True,
        factory=get_register_user_use_case_factory,
    )

    container.register_service(
        interface=type(None),  # AuthenticateUserUseCaseProtocol when created
        implementation=type(None),
        singleton=True,
        factory=get_authenticate_user_use_case_factory,
    )

    logger.info("Registered Identity Domain Services")

    # ✅ NEW: Inter-Domain Communication Setup
    # Set up event bus and register domain event handlers
    async def setup_inter_domain_communication():
        """Initialize inter-domain event communication"""
        from src.analytics.application.event_handlers import (
            register_analytics_event_handlers,
        )
        from src.identity.application.event_handlers import (
            register_identity_event_handlers,
        )
        from src.payments.application.event_handlers import (
            register_payments_event_handlers,
        )
        from src.shared_kernel.application.event_bus import get_event_bus

        event_bus = get_event_bus()

        # Register event handlers for each domain
        await register_identity_event_handlers(event_bus, user_repository=None)
        await register_analytics_event_handlers(event_bus, analytics_repository=None)
        await register_payments_event_handlers(event_bus, payment_repository=None)

        logger.info("Inter-domain communication configured")
        return event_bus

    # Register event bus as a service
    container.register_service(
        interface=type(None),  # EventBusProtocol when created
        implementation=type(None),
        singleton=True,
        factory=setup_inter_domain_communication,
    )

    container._initialized = True
    logger.info("Service configuration complete with inter-domain communication")


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


# ============================================================================
# MIGRATION PHASE SUPPORT
# ============================================================================
# During migration, we need to support both legacy apps/ and new src/ services


async def register_migration_services():
    """Register services with migration adapter support"""
    from src.migration_adapters import get_analytics_service, get_identity_service

    # Register services that can fall back to legacy implementations
    try:
        container.register_singleton(
            "identity_service", factory=lambda: get_identity_service("user_management")
        )
        logger.info("✅ Identity service registered with migration adapter")
    except Exception as e:
        logger.warning(f"Identity service registration failed: {e}")

    try:
        container.register_singleton(
            "analytics_service", factory=lambda: get_analytics_service("analytics")
        )
        logger.info("✅ Analytics service registered with migration adapter")
    except Exception as e:
        logger.warning(f"Analytics service registration failed: {e}")

    # Add other services as needed during migration
    logger.info("🔄 Migration-aware DI container ready")


# Auto-register migration services
import asyncio

try:
    asyncio.create_task(register_migration_services())
except RuntimeError:
    # Not in async context, will register when needed
    pass
