#!/usr/bin/env python3
"""
Test AI Status Endpoint
"""

import asyncio
import sys

sys.path.insert(0, "/home/abcdev/projects/analyticbot")

from apps.di import get_container


async def test_ai_status():
    """Test the AI status endpoint repositories."""
    print("Testing AI Status Endpoint Dependencies...")
    print("=" * 60)

    container = get_container()

    # Test user ID (your Telegram ID from logs)
    user_id = 844338517

    try:
        # Get repositories
        config_repo = await container.database.user_ai_config_repo()
        usage_repo = await container.database.user_ai_usage_repo()
        services_repo = await container.database.user_ai_services_repo()

        print(f"\n1. Testing config repository for user {user_id}...")
        config = await config_repo.get_or_create_default(user_id)
        print("   ✅ Config retrieved:")
        print(f"      - Tier: {config['tier']}")
        print(f"      - Enabled: {config['enabled']}")
        print(f"      - Settings: {config.get('settings')}")
        print(f"      - Features: {config.get('enabled_features')}")

        print(f"\n2. Testing usage repository for user {user_id}...")
        usage = await usage_repo.get_today(user_id)
        if usage:
            print("   ✅ Usage data:")
            print(f"      - Requests: {usage['requests_count']}")
            print(f"      - Tokens: {usage['tokens_used']}")
        else:
            print("   ℹ️  No usage data for today (expected for new user)")

        print(f"\n3. Testing services repository for user {user_id}...")
        services = await services_repo.get_active_services(user_id)
        print(f"   ✅ Active services: {len(services)}")
        for service in services:
            print(f"      - {service['service_type']}")

        print(f"\n{'=' * 60}")
        print("✅ All repository tests passed!")
        print("\nNow testing full status response...")

        # Build status response (simulating the endpoint)
        from apps.ai.user.config import AITier, UserAILimits

        tier = AITier(config["tier"])
        limits = UserAILimits.from_tier(tier)
        usage_today = usage["requests_count"] if usage else 0
        remaining = max(0, limits.requests_per_day - usage_today)
        service_names = [s["service_type"] for s in services]

        status_response = {
            "user_id": user_id,
            "tier": config["tier"],
            "enabled": config["enabled"],
            "usage_today": usage_today,
            "usage_limit": limits.requests_per_day,
            "remaining_requests": remaining,
            "features_enabled": config.get("enabled_features", []),
            "services_enabled": service_names,
        }

        print("\n📊 Status Response:")
        import json

        print(json.dumps(status_response, indent=2))

        print("\n✅ Test completed successfully!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    result = asyncio.run(test_ai_status())
    sys.exit(0 if result else 1)
