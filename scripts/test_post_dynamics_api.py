#!/usr/bin/env python3
"""
Test Post Dynamics API Endpoint
This script tests if the Post Dynamics API endpoint returns data correctly
"""

import asyncio
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import Mock

from fastapi import Request

from apps.api.routers.analytics_post_dynamics_router import get_post_dynamics


async def test_post_dynamics_endpoint():
    """Test the post dynamics endpoint directly"""

    print("=" * 60)
    print("🧪 Testing Post Dynamics API Endpoint")
    print("=" * 60)

    # Get container and dependencies
    from apps.api.di_analytics import get_analytics_fusion_service, get_cache

    service = await anext(get_analytics_fusion_service())
    cache = await anext(get_cache())

    # Mock request
    request = Mock(spec=Request)

    # Test for ABC LEGACY NEWS channel
    channel_id = "1002678877654"
    period = "24h"

    print(f"\n📊 Testing channel: {channel_id}")
    print(f"   Period: {period}")

    try:
        # Call the endpoint function directly
        result = await get_post_dynamics(
            channel_id=channel_id, request=request, period=period, service=service, cache=cache
        )

        print("\n✅ API Response:")
        print(f"   Data points returned: {len(result)}")

        if result:
            print("\n📈 Sample data (first 3 points):")
            for i, point in enumerate(result[:3]):
                print(f"   {i+1}. Time: {point['time']}")
                print(f"      Views: {point['views']}, Likes: {point['likes']}")
                print(f"      Shares: {point['shares']}, Comments: {point['comments']}")
        else:
            print("\n⚠️  No data points returned (but query succeeded)")

        print("\n🎉 SUCCESS: Post Dynamics API is working!")
        return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_post_dynamics_endpoint())
    sys.exit(0 if success else 1)
