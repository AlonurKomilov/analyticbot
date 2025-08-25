#!/usr/bin/env python3
"""
PR-F2 Test: Docker Compose Explicit Commands Validation
Tests that docker-compose.yml has explicit commands for deterministic startup
"""

import sys
from pathlib import Path

import yaml


def test_compose_explicit_commands():
    """Test that docker-compose.yml has explicit command entries"""
    print("🚀 Testing PR-F2: Docker Compose Explicit Commands...")

    compose_file = Path("/workspaces/analyticbot/docker-compose.yml")

    if not compose_file.exists():
        print("❌ docker-compose.yml not found!")
        return False

    with open(compose_file) as f:
        compose_data = yaml.safe_load(f)

    services = compose_data.get("services", {})

    # Test API service
    api_service = services.get("api", {})
    api_command = api_service.get("command")
    expected_api_command = "uvicorn apps.api.main:app --host 0.0.0.0 --port 8000"

    if api_command != expected_api_command:
        print(f"❌ API command mismatch. Expected: {expected_api_command}, Got: {api_command}")
        return False
    print("✅ API service has explicit command")

    # Test Bot service
    bot_service = services.get("bot", {})
    bot_command = bot_service.get("command")
    expected_bot_command = "python -m apps.bot.run_bot"

    if bot_command != expected_bot_command:
        print(f"❌ Bot command mismatch. Expected: {expected_bot_command}, Got: {bot_command}")
        return False
    print("✅ Bot service has explicit command")

    # Test Worker service (optional)
    worker_service = services.get("worker", {})
    worker_command = worker_service.get("command")
    expected_worker_command = "celery -A infra.celery.celery_app worker -l info"

    if worker_command != expected_worker_command:
        print(
            f"❌ Worker command mismatch. Expected: {expected_worker_command}, Got: {worker_command}"
        )
        return False
    print("✅ Worker service has explicit command")

    # Test Beat service (optional)
    beat_service = services.get("beat", {})
    beat_command = beat_service.get("command")
    expected_beat_command = "celery -A infra.celery.celery_app beat -l info"

    if beat_command != expected_beat_command:
        print(f"❌ Beat command mismatch. Expected: {expected_beat_command}, Got: {beat_command}")
        return False
    print("✅ Beat service has explicit command")

    # Test API healthcheck settings
    api_healthcheck = api_service.get("healthcheck", {})
    expected_interval = "10s"
    expected_timeout = "3s"
    expected_retries = 10

    if api_healthcheck.get("interval") != expected_interval:
        print(f"❌ API healthcheck interval mismatch. Expected: {expected_interval}")
        return False

    if api_healthcheck.get("timeout") != expected_timeout:
        print(f"❌ API healthcheck timeout mismatch. Expected: {expected_timeout}")
        return False

    if api_healthcheck.get("retries") != expected_retries:
        print(f"❌ API healthcheck retries mismatch. Expected: {expected_retries}")
        return False

    print("✅ API healthcheck settings correct")

    return True


def test_app_module_imports():
    """Test that the apps can be imported without errors"""
    print("\n🔍 Testing module imports...")

    try:
        # Test bot module import
        import apps.bot.run_bot

        print("✅ apps.bot.run_bot imports successfully")
    except ImportError as e:
        print(f"❌ apps.bot.run_bot import failed: {e}")
        return False

    try:
        # Test celery app import
        from infra.celery.celery_app import celery_app

        print("✅ infra.celery.celery_app imports successfully")
    except ImportError as e:
        print(f"❌ infra.celery.celery_app import failed: {e}")
        return False

    try:
        # Test API main import
        from apps.api.main import app

        print("✅ apps.api.main imports successfully")
    except ImportError as e:
        print(f"❌ apps.api.main import failed: {e}")
        return False

    return True


def main():
    """Run all PR-F2 validation tests"""
    print("=" * 60)
    print("PR-F2: Docker Compose Explicit Commands Validation")
    print("=" * 60)

    tests_passed = 0
    total_tests = 2

    # Test 1: Compose explicit commands
    if test_compose_explicit_commands():
        tests_passed += 1

    # Test 2: Module imports
    if test_app_module_imports():
        tests_passed += 1

    print("\n" + "=" * 60)
    print("📊 PR-F2 TEST SUMMARY")
    print("=" * 60)
    print(
        f"Explicit commands in docker-compose.yml... {'✅ PASSED' if tests_passed >= 1 else '❌ FAILED'}"
    )
    print(
        f"Module imports without errors.......... {'✅ PASSED' if tests_passed >= 2 else '❌ FAILED'}"
    )
    print("-" * 60)

    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED! PR-F2 implementation is ready.")
        print("\n📋 ACCEPTANCE CRITERIA STATUS:")
        print("✅ docker-compose.yml has explicit commands for api/bot/worker/beat")
        print("✅ API healthcheck updated (10s interval, 3s timeout, 10 retries)")
        print("✅ Bot module imports without errors")
        print("✅ Ready for: docker compose up -d api bot")
        return True
    else:
        print(f"❌ {total_tests - tests_passed}/{total_tests} tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
