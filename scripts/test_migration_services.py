#!/usr/bin/env python3
"""
Test migration validation - verify services can be instantiated after migration
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_di_container():
    """Test that DI container can be imported and basic services instantiated"""
    try:
        logger.info("🧪 Testing DI Container import...")
        from core.di_container import DIContainer

        logger.info("✅ DI Container imported successfully")

        # Test container initialization
        DIContainer()
        logger.info("✅ DI Container instantiated successfully")

        return True
    except Exception as e:
        logger.error(f"❌ DI Container failed: {e}")
        return False


async def test_core_services():
    """Test that core migrated services can be imported"""
    services_to_test = [
        # Domain entities (corrected paths)
        ("src.identity.domain.entities.user", "User"),
        ("src.analytics.domain.entities.analytics_report", "AnalyticsReport"),
        # Application services
        (
            "src.shared_kernel.application.services.analytics_service",
            "AnalyticsService",
        ),
        ("src.bot_service.application.services.payment_service", "PaymentService"),
        # Infrastructure
        (
            "src.shared_kernel.infrastructure.cache.async_redis_client",
            "create_redis_client",
        ),
        (
            "src.shared_kernel.infrastructure.email.smtp_email_service",
            "SMTPEmailService",
        ),
        # Security
        ("src.security.auth", "SecurityManager"),
    ]

    results = []

    for module_path, class_name in services_to_test:
        try:
            logger.info(f"🧪 Testing {module_path}.{class_name}...")
            module = __import__(module_path, fromlist=[class_name])
            getattr(module, class_name)
            logger.info(f"✅ {module_path}.{class_name} imported successfully")
            results.append(True)
        except Exception as e:
            logger.error(f"❌ {module_path}.{class_name} failed: {e}")
            results.append(False)

    return all(results)


async def test_mock_services():
    """Test that mock services can be imported (critical for testing)"""
    mock_services = [
        (
            "src.api_service.infrastructure.testing.services.mock_analytics_service",
            "MockAnalyticsService",
        ),
        (
            "src.api_service.infrastructure.testing.services.mock_payment_service",
            "MockPaymentService",
        ),
        (
            "src.api_service.infrastructure.testing.database.mock_database",
            "MockDatabase",
        ),
        (
            "src.api_service.infrastructure.testing.services.mock_ai_service",
            "MockAIService",
        ),
    ]

    results = []

    for module_path, class_name in mock_services:
        try:
            logger.info(f"🧪 Testing mock {module_path}.{class_name}...")
            module = __import__(module_path, fromlist=[class_name])
            getattr(module, class_name)
            logger.info(f"✅ Mock {module_path}.{class_name} imported successfully")
            results.append(True)
        except Exception as e:
            logger.error(f"❌ Mock {module_path}.{class_name} failed: {e}")
            results.append(False)

    return all(results)


async def main():
    """Run all service validation tests"""
    logger.info("🚀 Starting Migration Validation Tests...")

    # Test 1: DI Container
    di_test = await test_di_container()

    # Test 2: Core Services
    core_test = await test_core_services()

    # Test 3: Mock Services
    mock_test = await test_mock_services()

    # Results
    total_tests = 3
    passed_tests = sum([di_test, core_test, mock_test])

    logger.info("=" * 60)
    logger.info("📊 MIGRATION VALIDATION RESULTS:")
    logger.info(f"   DI Container: {'✅ PASS' if di_test else '❌ FAIL'}")
    logger.info(f"   Core Services: {'✅ PASS' if core_test else '❌ FAIL'}")
    logger.info(f"   Mock Services: {'✅ PASS' if mock_test else '❌ FAIL'}")
    logger.info(f"   Overall: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        logger.info("🎉 Migration validation SUCCESSFUL - all services working!")
        return True
    else:
        logger.error("💥 Migration validation FAILED - some services need fixing")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
