#!/usr/bin/env python3
"""
Test Retry Logic with Exponential Backoff

This script tests the retry logic implementation:
1. Exponential backoff calculation
2. Retry policy selection based on error type
3. Successful retry after transient failures
4. Non-retryable errors handled correctly
5. Rate limit errors with FloodWait
6. Retry statistics tracking
"""

import asyncio
import time
from typing import Any

from apps.bot.multi_tenant.retry_logic import (
    RetryPolicy,
    RetryStrategy,
    RetryErrorCategory,
    calculate_delay,
    categorize_error,
    get_retry_policy,
    retry_with_backoff,
    NonRetryableError,
    get_retry_statistics,
)


# Mock Telethon errors for testing
class FloodWaitError(Exception):
    def __init__(self, seconds: int):
        self.seconds = seconds
        super().__init__(f"FloodWait: {seconds} seconds")


class ServerError(Exception):
    pass


class UserDeactivatedError(Exception):
    pass


class TimedOutError(Exception):
    pass


async def test_exponential_backoff_calculation():
    """Test exponential backoff delay calculation."""
    print("\n🧪 Test 1: Exponential Backoff Calculation")
    print("=" * 70)

    policy = RetryPolicy(
        base_delay=1.0,
        exponential_base=2.0,
        strategy=RetryStrategy.EXPONENTIAL,
        jitter=False,
    )

    delays = []
    for attempt in range(5):
        delay = calculate_delay(attempt, policy)
        delays.append(delay)
        print(f"  Attempt {attempt}: {delay:.2f}s")

    # Verify exponential growth
    assert delays[0] == 1.0  # 1 * 2^0
    assert delays[1] == 2.0  # 1 * 2^1
    assert delays[2] == 4.0  # 1 * 2^2
    assert delays[3] == 8.0  # 1 * 2^3
    assert delays[4] == 16.0  # 1 * 2^4

    print("✅ Test 1 PASSED: Exponential backoff calculated correctly")


async def test_jitter_adds_randomness():
    """Test that jitter adds randomness to delays."""
    print("\n🧪 Test 2: Jitter Adds Randomness")
    print("=" * 70)

    policy = RetryPolicy(
        base_delay=10.0,
        strategy=RetryStrategy.EXPONENTIAL,
        jitter=True,
    )

    delays = []
    for _ in range(10):
        delay = calculate_delay(2, policy)  # Attempt 2
        delays.append(delay)

    # All delays should be different due to jitter
    unique_delays = len(set(delays))
    print(f"  Generated {unique_delays} unique delays out of 10")
    print(f"  Min delay: {min(delays):.2f}s, Max delay: {max(delays):.2f}s")
    print(f"  Average: {sum(delays)/len(delays):.2f}s")

    # With jitter, we should have mostly unique values
    assert unique_delays >= 7, "Jitter should produce varied delays"

    print("✅ Test 2 PASSED: Jitter adds randomness to delays")


async def test_linear_backoff():
    """Test linear backoff calculation."""
    print("\n🧪 Test 3: Linear Backoff")
    print("=" * 70)

    policy = RetryPolicy(
        base_delay=2.0,
        strategy=RetryStrategy.LINEAR,
        jitter=False,
    )

    delays = []
    for attempt in range(5):
        delay = calculate_delay(attempt, policy)
        delays.append(delay)
        print(f"  Attempt {attempt}: {delay:.2f}s")

    # Verify linear growth
    assert delays[0] == 2.0  # 2 * 1
    assert delays[1] == 4.0  # 2 * 2
    assert delays[2] == 6.0  # 2 * 3
    assert delays[3] == 8.0  # 2 * 4
    assert delays[4] == 10.0  # 2 * 5

    print("✅ Test 3 PASSED: Linear backoff calculated correctly")


async def test_max_delay_cap():
    """Test that delays are capped at max_delay."""
    print("\n🧪 Test 4: Max Delay Cap")
    print("=" * 70)

    policy = RetryPolicy(
        base_delay=10.0,
        max_delay=30.0,
        strategy=RetryStrategy.EXPONENTIAL,
        jitter=False,
    )

    delays = []
    for attempt in range(6):
        delay = calculate_delay(attempt, policy)
        delays.append(delay)
        print(f"  Attempt {attempt}: {delay:.2f}s (capped at {policy.max_delay}s)")

    # Verify all delays are <= max_delay
    assert all(delay <= policy.max_delay for delay in delays)
    print(f"  All delays capped at {policy.max_delay}s")

    print("✅ Test 4 PASSED: Max delay cap enforced")


async def test_error_categorization():
    """Test error categorization."""
    print("\n🧪 Test 5: Error Categorization")
    print("=" * 70)

    test_cases = [
        (FloodWaitError(60), RetryErrorCategory.RATE_LIMIT),
        (ServerError("Server error"), RetryErrorCategory.TRANSIENT_NETWORK),
        (TimedOutError("Timeout"), RetryErrorCategory.TRANSIENT_NETWORK),
        (UserDeactivatedError("Deactivated"), RetryErrorCategory.PERMANENT),
        (ValueError("Unknown error"), RetryErrorCategory.UNKNOWN),
    ]

    for error, expected_category in test_cases:
        category = categorize_error(error)
        status = "✅" if category == expected_category else "❌"
        print(f"  {status} {type(error).__name__}: {category.value}")
        assert category == expected_category

    print("✅ Test 5 PASSED: Errors categorized correctly")


async def test_retry_policy_selection():
    """Test retry policy selection based on error type."""
    print("\n🧪 Test 6: Retry Policy Selection")
    print("=" * 70)

        # Rate limit error - FloodWaitError gets special handling
    flood_error = FloodWaitError(30)
    policy = get_retry_policy(flood_error)
    print(f"  FloodWaitError: max_retries={policy.max_retries}, base_delay={policy.base_delay}s")
    # FloodWaitError uses base_delay from error.seconds and has max 3 retries for rate_limit category
    assert policy.max_retries == 3  # Rate limit category default

    # Transient error - should have max 2 retries
    server_error = ServerError("Server error")
    policy = get_retry_policy(server_error)
    print(f"  ServerError: max_retries={policy.max_retries}, base_delay={policy.base_delay}s")
    assert policy.max_retries == 2

    # Permanent error - should have 0 retries
    deactivated_error = UserDeactivatedError("Deactivated")
    policy = get_retry_policy(deactivated_error)
    print(f"  UserDeactivatedError: max_retries={policy.max_retries}")
    assert policy.max_retries == 0

    print("✅ Test 6 PASSED: Retry policies selected correctly")


async def test_successful_retry_after_failures():
    """Test successful retry after transient failures."""
    print("\n🧪 Test 7: Successful Retry After Failures")
    print("=" * 70)

    call_count = 0

    async def flaky_function():
        nonlocal call_count
        call_count += 1
        print(f"  Call #{call_count}")

        if call_count < 3:
            # Fail first 2 times
            raise ServerError("Server temporarily unavailable")
        return "success"

    start_time = time.time()
    result = await retry_with_backoff(flaky_function)
    elapsed = time.time() - start_time

    print(f"  Result: {result}")
    print(f"  Total calls: {call_count}")
    print(f"  Elapsed time: {elapsed:.2f}s")

    assert result == "success"
    assert call_count == 3
    print("✅ Test 7 PASSED: Successfully retried after transient failures")


async def test_retry_exhaustion():
    """Test that retries are exhausted after max attempts."""
    print("\n🧪 Test 8: Retry Exhaustion")
    print("=" * 70)

    call_count = 0

    async def always_failing():
        nonlocal call_count
        call_count += 1
        print(f"  Call #{call_count}")
        raise ServerError("Persistent server error")

    try:
        await retry_with_backoff(always_failing)
        assert False, "Should have raised exception"
    except ServerError:
        print(f"  Exception raised after {call_count} attempts (1 initial + 2 retries)")
        assert call_count == 3  # 1 initial + 2 retries
        print("✅ Test 8 PASSED: Retries exhausted correctly")


async def test_non_retryable_error():
    """Test that non-retryable errors don't retry."""
    print("\n🧪 Test 9: Non-Retryable Errors")
    print("=" * 70)

    call_count = 0

    async def permanent_failure():
        nonlocal call_count
        call_count += 1
        print(f"  Call #{call_count}")
        raise UserDeactivatedError("User permanently deactivated")

    try:
        await retry_with_backoff(permanent_failure)
        assert False, "Should have raised NonRetryableError"
    except NonRetryableError as e:
        print(f"  NonRetryableError raised: {e}")
        assert call_count == 1  # Should not retry
        print("✅ Test 9 PASSED: Non-retryable errors handled correctly")


async def test_flood_wait_handling():
    """Test FloodWait error handling with server-specified delay."""
    print("\n🧪 Test 10: FloodWait Handling")
    print("=" * 70)

    call_count = 0

    async def flood_then_success():
        nonlocal call_count
        call_count += 1
        print(f"  Call #{call_count}")

        if call_count == 1:
            # First call triggers flood wait
            raise FloodWaitError(2)  # 2 second wait
        return "success"

    start_time = time.time()
    result = await retry_with_backoff(flood_then_success)
    elapsed = time.time() - start_time

    print(f"  Result: {result}")
    print(f"  Total calls: {call_count}")
    print(f"  Elapsed time: {elapsed:.2f}s")

    assert result == "success"
    assert call_count == 2
    assert elapsed >= 2.0  # Should wait at least 2 seconds
    print("✅ Test 10 PASSED: FloodWait handled with correct delay")


async def test_retry_statistics():
    """Test retry statistics tracking."""
    print("\n🧪 Test 11: Retry Statistics Tracking")
    print("=" * 70)

    stats = get_retry_statistics()
    stats.reset()

    # Record some attempts
    stats.record_attempt(attempt=0, success=True, error_category=None)
    stats.record_attempt(attempt=1, success=True, error_category="transient_network")
    stats.record_attempt(attempt=2, success=False, error_category="rate_limit")

    statistics = stats.get_statistics()
    print(f"  Total attempts: {statistics['total_attempts']}")
    print(f"  Total retries: {statistics['total_retries']}")
    print(f"  Successful retries: {statistics['successful_retries']}")
    print(f"  Failed retries: {statistics['failed_retries']}")
    print(f"  Success rate: {statistics['success_rate']:.1%}")

    assert statistics["total_attempts"] == 3
    assert statistics["total_retries"] == 2  # Attempts 1 and 2 are retries
    assert statistics["successful_retries"] == 1
    assert statistics["failed_retries"] == 1

    print("✅ Test 11 PASSED: Statistics tracked correctly")


async def test_immediate_success():
    """Test function that succeeds immediately (no retries needed)."""
    print("\n🧪 Test 12: Immediate Success (No Retries)")
    print("=" * 70)

    call_count = 0

    async def immediate_success():
        nonlocal call_count
        call_count += 1
        return "immediate_success"

    result = await retry_with_backoff(immediate_success)

    print(f"  Result: {result}")
    print(f"  Total calls: {call_count}")

    assert result == "immediate_success"
    assert call_count == 1
    print("✅ Test 12 PASSED: Immediate success handled correctly")


async def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("🔄 RETRY LOGIC TEST SUITE")
    print("=" * 70)

    tests = [
        test_exponential_backoff_calculation,
        test_jitter_adds_randomness,
        test_linear_backoff,
        test_max_delay_cap,
        test_error_categorization,
        test_retry_policy_selection,
        test_successful_retry_after_failures,
        test_retry_exhaustion,
        test_non_retryable_error,
        test_flood_wait_handling,
        test_retry_statistics,
        test_immediate_success,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            await test()
            passed += 1
        except AssertionError as e:
            print(f"❌ Test FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ Test ERROR: {e}")
            import traceback

            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 70)
    print("📊 TEST RESULTS")
    print("=" * 70)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Retry logic is working correctly.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the output above.")

    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
