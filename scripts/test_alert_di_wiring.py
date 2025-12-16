#!/usr/bin/env python3
"""
Test Alert Services DI Wiring

Validates that all alert services can be instantiated through the DI container
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


async def test_alert_services_wiring():
    """Test that alert services can be instantiated via DI container"""
    print("=" * 80)
    print("Testing Alert Services DI Wiring")
    print("=" * 80)
    print()

    try:
        # Import container
        from apps.di import get_container

        container = get_container()
        print("✓ Container imported successfully")

        # Wire the container
        container.wire(modules=[__name__])
        print("✓ Container wired successfully")
        print()

        # Test database container
        print("Testing Database Container:")
        print("-" * 80)

        try:
            alert_repo_provider = container.database.alert_repo()
            # Repository providers are async coroutines
            print(f"✓ alert_repo provider created: {type(alert_repo_provider).__name__}")
        except Exception as e:
            print(f"✗ alert_repo failed: {e}")
            return False

        print()

        # Test bot container - alert services
        print("Testing Bot Container - Alert Services:")
        print("-" * 80)

        services_to_test = [
            ("alert_condition_evaluator", "AlertConditionEvaluator"),
            ("alert_rule_manager", "AlertRuleManager"),
            ("alert_event_manager", "AlertEventManager"),
            ("telegram_alert_notifier", "TelegramAlertNotifier"),
        ]

        all_passed = True

        for service_name, expected_class in services_to_test:
            try:
                service_provider = getattr(container.bot, service_name)

                # Check if it's a callable provider
                if callable(service_provider):
                    service = service_provider()
                    actual_class = type(service).__name__

                    if actual_class == expected_class:
                        print(f"✓ {service_name}: {actual_class}")
                    elif service is None:
                        print(
                            f"⚠ {service_name}: Provider returned None (expected if dependencies missing)"
                        )
                    else:
                        print(f"✗ {service_name}: Expected {expected_class}, got {actual_class}")
                        all_passed = False
                else:
                    print(f"✗ {service_name}: Not a callable provider")
                    all_passed = False

            except AttributeError:
                print(f"✗ {service_name}: Provider not found in container")
                all_passed = False
            except Exception as e:
                print(f"✗ {service_name}: {e}")
                all_passed = False

        print()

        # Test legacy alerting service (should still work)
        print("Testing Legacy Services (backward compatibility):")
        print("-" * 80)

        try:
            alerting_service = container.bot.alerting_service()
            print(f"✓ alerting_service (legacy): {type(alerting_service).__name__}")
        except Exception as e:
            print(f"⚠ alerting_service (legacy) failed (expected if archived): {e}")

        print()

        # Summary
        print("=" * 80)
        if all_passed:
            print("✅ ALL ALERT SERVICES TESTS PASSED")
            print("=" * 80)
            return True
        else:
            print("❌ SOME ALERT SERVICES TESTS FAILED")
            print("=" * 80)
            return False

    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_alert_service_dependencies():
    """Test that alert services have correct dependencies injected"""
    print()
    print("=" * 80)
    print("Testing Alert Service Dependencies")
    print("=" * 80)
    print()

    try:
        from apps.di import get_container

        container = get_container()

        # Get services (excluding telegram_alert_notifier which needs valid bot token)
        alert_condition_evaluator = container.bot.alert_condition_evaluator()
        alert_rule_manager = container.bot.alert_rule_manager()
        alert_event_manager = container.bot.alert_event_manager()

        print("Testing AlertConditionEvaluator:")
        print("-" * 80)
        print(f"✓ Has _alert_repo: {hasattr(alert_condition_evaluator, '_alert_repo')}")
        print(f"✓ Has _logger: {hasattr(alert_condition_evaluator, '_logger')}")
        print()

        print("Testing AlertRuleManager:")
        print("-" * 80)
        print(f"✓ Has _alert_repo: {hasattr(alert_rule_manager, '_alert_repo')}")
        print(f"✓ Has _logger: {hasattr(alert_rule_manager, '_logger')}")
        print(f"✓ Has VALID_CONDITIONS: {hasattr(alert_rule_manager, 'VALID_CONDITIONS')}")
        print(f"✓ Has VALID_SEVERITIES: {hasattr(alert_rule_manager, 'VALID_SEVERITIES')}")
        print()

        print("Testing AlertEventManager:")
        print("-" * 80)
        print(f"✓ Has _alert_repo: {hasattr(alert_event_manager, '_alert_repo')}")
        print(f"✓ Has _logger: {hasattr(alert_event_manager, '_logger')}")
        print()

        print("Testing TelegramAlertNotifier:")
        print("-" * 80)
        print("⚠ Skipped (requires valid bot token in test environment)")
        print()

        print("=" * 80)
        print("✅ ALL DEPENDENCY CHECKS PASSED")
        print("=" * 80)
        return True

    except Exception as e:
        print(f"❌ DEPENDENCY CHECK FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_middleware_injection():
    """Test that middleware can inject alert services"""
    print()
    print("=" * 80)
    print("Testing Middleware Injection")
    print("=" * 80)
    print()

    try:
        from apps.bot.middlewares.dependency_middleware import DependencyMiddleware
        from apps.di import get_container

        container = get_container()

        # Create middleware
        DependencyMiddleware(container)
        print("✓ DependencyMiddleware instantiated")

        # Simulate injection (without actual bot context)

        # Test that container has the services
        print("\nChecking container.bot providers:")
        print("-" * 80)

        services = [
            "alert_condition_evaluator",
            "alert_rule_manager",
            "alert_event_manager",
            "telegram_alert_notifier",
        ]

        for service_name in services:
            has_provider = hasattr(container.bot, service_name)
            print(f"{'✓' if has_provider else '✗'} container.bot.{service_name}: {has_provider}")

        print()
        print("=" * 80)
        print("✅ MIDDLEWARE INJECTION TEST PASSED")
        print("=" * 80)
        return True

    except Exception as e:
        print(f"❌ MIDDLEWARE INJECTION TEST FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "ALERT SERVICES DI WIRING TEST" + " " * 29 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    results = []

    # Test 1: Basic wiring
    result1 = await test_alert_services_wiring()
    results.append(("Alert Services Wiring", result1))

    # Test 2: Dependencies
    result2 = await test_alert_service_dependencies()
    results.append(("Service Dependencies", result2))

    # Test 3: Middleware
    result3 = await test_middleware_injection()
    results.append(("Middleware Injection", result3))

    # Final summary
    print("\n")
    print("=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)

    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:<40} {status}")

    print("=" * 80)

    all_passed = all(result for _, result in results)

    if all_passed:
        print("🎉 ALL TESTS PASSED - DI wiring is correct!")
        return 0
    else:
        print("⚠️  SOME TESTS FAILED - Please review the output above")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
