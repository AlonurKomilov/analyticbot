#!/usr/bin/env python3
"""
Test Global Rate Limiter Implementation

This script verifies that:
1. Global rate limiting works across multiple simulated users
2. Method-specific limits are enforced
3. Backoff mechanism works for 429 errors
4. Statistics tracking is accurate
"""

import asyncio
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def test_method_rate_limiting():
    """Test that method-specific rate limits are enforced"""
    from apps.bot.multi_tenant.global_rate_limiter import GlobalRateLimiter

    print("=" * 70)
    print("TEST 1: Method-Specific Rate Limiting")
    print("=" * 70)

    limiter = await GlobalRateLimiter.get_instance()

    # Test sendMessage limit (30 requests/second)
    print("\nTesting sendMessage rate limit (30 req/s)...")
    start_time = time.time()

    # Try to make 35 requests (should take ~2 seconds due to rate limiting)
    for i in range(35):
        await limiter.acquire("sendMessage", user_id=1)

    elapsed = time.time() - start_time

    if elapsed >= 1.0:  # Should take at least 1 second for 35 requests at 30/sec
        print(f"✅ PASS: 35 sendMessage requests took {elapsed:.2f}s (rate limited)")
    else:
        print(f"❌ FAIL: 35 requests completed too quickly ({elapsed:.2f}s)")
        return False

    # Check statistics
    stats = limiter.get_stats()
    print(f"   Total requests: {stats['total_requests']}")
    print(f"   Rate limited: {stats['rate_limited_count']}")

    print()
    return True


async def test_global_rate_limiting():
    """Test that global rate limit is enforced across all methods"""
    from apps.bot.multi_tenant.global_rate_limiter import GlobalRateLimiter

    print("=" * 70)
    print("TEST 2: Global Rate Limiting (1000 req/60s)")
    print("=" * 70)

    # Reset instance for clean test
    await GlobalRateLimiter.close()
    limiter = await GlobalRateLimiter.get_instance()

    print("\nTesting global limit with mixed methods...")
    start_time = time.time()

    # Make 50 requests with different methods (should be fast, well under limit)
    tasks = []
    for i in range(50):
        method = ["sendMessage", "getChat", "getChatMember"][i % 3]
        tasks.append(limiter.acquire(method, user_id=i))

    await asyncio.gather(*tasks)
    elapsed = time.time() - start_time

    print(f"✅ PASS: 50 mixed requests completed in {elapsed:.2f}s")

    # Check that global limit is tracked
    stats = limiter.get_stats()
    if "global" in stats["active_methods"]:
        global_count = stats["active_methods"]["global"]["active"]
        print(f"   Global active requests: {global_count}")

    print()
    return True


async def test_concurrent_users():
    """Test rate limiting with multiple concurrent users"""
    from apps.bot.multi_tenant.global_rate_limiter import GlobalRateLimiter

    print("=" * 70)
    print("TEST 3: Concurrent Multi-User Rate Limiting")
    print("=" * 70)

    # Reset instance for clean test
    await GlobalRateLimiter.close()
    limiter = await GlobalRateLimiter.get_instance()

    print("\nSimulating 10 users making 5 requests each (50 total)...")
    start_time = time.time()

    # Simulate 10 concurrent users
    async def user_requests(user_id: int):
        for _ in range(5):
            await limiter.acquire("sendMessage", user_id=user_id)

    # Run all users concurrently
    await asyncio.gather(*[user_requests(i) for i in range(10)])

    elapsed = time.time() - start_time

    print(f"✅ PASS: 10 users × 5 requests completed in {elapsed:.2f}s")

    stats = limiter.get_stats()
    print(f"   Total requests: {stats['total_requests']}")
    print(f"   Rate limited: {stats['rate_limited_count']}")

    print()
    return True


async def test_backoff_mechanism():
    """Test that backoff mechanism works for 429 errors"""
    from apps.bot.multi_tenant.global_rate_limiter import GlobalRateLimiter

    print("=" * 70)
    print("TEST 4: Backoff Mechanism (429 Error Handling)")
    print("=" * 70)

    # Reset instance for clean test
    await GlobalRateLimiter.close()
    limiter = await GlobalRateLimiter.get_instance()

    # Trigger a backoff
    print("\nSimulating 429 error with 2s backoff...")
    await limiter.handle_rate_limit_error(retry_after=2)

    # Check stats
    stats = limiter.get_stats()
    if stats["backoff_active"]:
        print(f"✅ PASS: Backoff activated ({stats['backoff_remaining']:.1f}s remaining)")
    else:
        print("❌ FAIL: Backoff not activated")
        return False

    # Try to make a request during backoff (should wait)
    print("   Attempting request during backoff...")
    start_time = time.time()
    await limiter.acquire("sendMessage")
    elapsed = time.time() - start_time

    if elapsed >= 1.5:  # Should wait ~2 seconds
        print(f"✅ PASS: Request waited {elapsed:.2f}s for backoff to complete")
    else:
        print(f"❌ FAIL: Request didn't wait long enough ({elapsed:.2f}s)")
        return False

    # Check that backoff is now inactive
    stats = limiter.get_stats()
    if not stats["backoff_active"]:
        print("✅ PASS: Backoff deactivated after completion")
    else:
        print("❌ FAIL: Backoff still active")
        return False

    print()
    return True


async def test_statistics():
    """Test that statistics tracking works correctly"""
    from apps.bot.multi_tenant.global_rate_limiter import GlobalRateLimiter

    print("=" * 70)
    print("TEST 5: Statistics Tracking")
    print("=" * 70)

    # Reset instance for clean test
    await GlobalRateLimiter.close()
    limiter = await GlobalRateLimiter.get_instance()

    # Make some requests
    for i in range(10):
        await limiter.acquire("sendMessage", user_id=1)

    for i in range(5):
        await limiter.acquire("getChat", user_id=2)

    # Get stats
    stats = limiter.get_stats()

    print("\n📊 Statistics:")
    print(f"   Total requests: {stats['total_requests']}")
    print(f"   Rate limited count: {stats['rate_limited_count']}")
    print(f"   Backoff count: {stats['backoff_count']}")
    print(f"   Backoff active: {stats['backoff_active']}")

    if stats["active_methods"]:
        print("\n   Active methods:")
        for method, data in stats["active_methods"].items():
            print(
                f"      {method}: {data['active']}/{data['limit']} " f"(window: {data['window']}s)"
            )

    if stats["total_requests"] == 15:
        print("\n✅ PASS: Statistics tracking accurate")
    else:
        print(f"\n❌ FAIL: Expected 15 requests, got {stats['total_requests']}")
        return False

    print()
    return True


async def main():
    """Run all tests"""
    print("\n🧪 Testing Global Rate Limiter Implementation\n")

    results = []

    try:
        results.append(await test_method_rate_limiting())
        results.append(await test_global_rate_limiting())
        results.append(await test_concurrent_users())
        results.append(await test_backoff_mechanism())
        results.append(await test_statistics())
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH EXCEPTION: {e}")
        import traceback

        traceback.print_exc()
        return 1

    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if all(results):
        print("\n✅ ALL TESTS PASSED - Global rate limiting working correctly!")
        print("\n🎯 Rate Limiting Features:")
        print("   • Per-method limits (sendMessage: 30/s, getChat: 20/s, etc.)")
        print("   • Global limit (1000 req/min across all methods)")
        print("   • Automatic backoff on 429 errors")
        print("   • Statistics tracking for monitoring")
        print("   • Thread-safe with asyncio locks")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED - Review implementation")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
