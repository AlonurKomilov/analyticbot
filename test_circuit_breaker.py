#!/usr/bin/env python3
"""
Test Circuit Breaker Functionality

This script tests the circuit breaker implementation:
1. Normal operation (CLOSED state)
2. Failure accumulation (CLOSED → OPEN)
3. Timeout and recovery testing (OPEN → HALF_OPEN)
4. Successful recovery (HALF_OPEN → CLOSED)
5. Recovery failure (HALF_OPEN → OPEN again)
"""

import asyncio
import time
from apps.bot.multi_tenant.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerRegistry,
    CircuitBreakerOpenError,
    CircuitState,
)


async def test_circuit_breaker_closed_state():
    """Test normal operation in CLOSED state."""
    print("\n🧪 Test 1: Circuit Breaker CLOSED State (Normal Operation)")
    print("=" * 70)

    breaker = CircuitBreaker(
        failure_threshold=5,
        timeout_seconds=2.0,  # Short timeout for testing
        success_threshold=2,
    )

    async def successful_operation():
        await asyncio.sleep(0.1)
        return "success"

    # Execute successful operations
    for i in range(3):
        result = await breaker.call(successful_operation)
        state = breaker.get_state()
        print(f"  Call {i+1}: {result}, State: {state['state']}, Failures: {state['failure_count']}")

    assert breaker.state == CircuitState.CLOSED
    print("✅ Test 1 PASSED: Circuit breaker stays CLOSED with successful operations")


async def test_circuit_breaker_opening():
    """Test circuit breaker opening after failures."""
    print("\n🧪 Test 2: Circuit Breaker Opening (CLOSED → OPEN)")
    print("=" * 70)

    breaker = CircuitBreaker(
        failure_threshold=5,
        timeout_seconds=2.0,
        success_threshold=2,
    )

    async def failing_operation():
        await asyncio.sleep(0.1)
        raise Exception("Simulated failure")

    # Execute failing operations
    for i in range(5):
        try:
            await breaker.call(failing_operation)
        except Exception as e:
            state = breaker.get_state()
            print(f"  Call {i+1}: Failed ({e}), State: {state['state']}, Failures: {state['failure_count']}")

    # Circuit should now be OPEN
    state = breaker.get_state()
    assert breaker.state == CircuitState.OPEN
    print(f"✅ Test 2 PASSED: Circuit breaker opened after {state['failure_count']} failures")


async def test_circuit_breaker_open_rejection():
    """Test that OPEN circuit breaker rejects calls immediately."""
    print("\n🧪 Test 3: Circuit Breaker Rejection (OPEN State)")
    print("=" * 70)

    breaker = CircuitBreaker(
        failure_threshold=5,
        timeout_seconds=2.0,
        success_threshold=2,
    )

    async def failing_operation():
        raise Exception("Simulated failure")

    # Open the circuit
    for _ in range(5):
        try:
            await breaker.call(failing_operation)
        except:
            pass

    assert breaker.state == CircuitState.OPEN

    # Try to call while circuit is open
    async def successful_operation():
        return "success"

    try:
        await breaker.call(successful_operation)
        assert False, "Should have raised CircuitBreakerOpenError"
    except CircuitBreakerOpenError as e:
        print(f"  ✅ Circuit breaker correctly rejected call: {e}")
        state = breaker.get_state()
        print(f"  State: {state['state']}, Timeout Remaining: {state['timeout_remaining']:.1f}s")

    print("✅ Test 3 PASSED: OPEN circuit breaker rejects calls immediately")


async def test_circuit_breaker_half_open():
    """Test circuit breaker recovery (OPEN → HALF_OPEN)."""
    print("\n🧪 Test 4: Circuit Breaker Recovery (OPEN → HALF_OPEN)")
    print("=" * 70)

    breaker = CircuitBreaker(
        failure_threshold=5,
        timeout_seconds=1.0,  # 1 second timeout
        success_threshold=2,
    )

    async def failing_operation():
        raise Exception("Simulated failure")

    # Open the circuit
    for _ in range(5):
        try:
            await breaker.call(failing_operation)
        except:
            pass

    assert breaker.state == CircuitState.OPEN
    print(f"  Circuit opened at {time.time():.2f}")

    # Wait for timeout
    print("  Waiting for timeout (1 second)...")
    await asyncio.sleep(1.5)

    # Next call should transition to HALF_OPEN
    async def successful_operation():
        return "success"

    result = await breaker.call(successful_operation)
    state = breaker.get_state()
    print(f"  After timeout - Call result: {result}, State: {state['state']}, Successes: {state['success_count']}")

    assert breaker.state == CircuitState.HALF_OPEN
    print("✅ Test 4 PASSED: Circuit breaker transitioned to HALF_OPEN after timeout")


async def test_circuit_breaker_recovery_success():
    """Test successful recovery (HALF_OPEN → CLOSED)."""
    print("\n🧪 Test 5: Successful Recovery (HALF_OPEN → CLOSED)")
    print("=" * 70)

    breaker = CircuitBreaker(
        failure_threshold=5,
        timeout_seconds=0.5,
        success_threshold=2,
    )

    async def failing_operation():
        raise Exception("Simulated failure")

    async def successful_operation():
        return "success"

    # Open the circuit
    for _ in range(5):
        try:
            await breaker.call(failing_operation)
        except:
            pass

    assert breaker.state == CircuitState.OPEN
    print("  Circuit opened")

    # Wait for timeout
    await asyncio.sleep(0.6)

    # First success (OPEN → HALF_OPEN)
    result1 = await breaker.call(successful_operation)
    state1 = breaker.get_state()
    print(f"  Success 1: {result1}, State: {state1['state']}, Successes: {state1['success_count']}")

    # Second success (HALF_OPEN → CLOSED)
    result2 = await breaker.call(successful_operation)
    state2 = breaker.get_state()
    print(f"  Success 2: {result2}, State: {state2['state']}, Successes: {state2['success_count']}")

    assert breaker.state == CircuitState.CLOSED
    print("✅ Test 5 PASSED: Circuit breaker closed after 2 successful recoveries")


async def test_circuit_breaker_recovery_failure():
    """Test failed recovery (HALF_OPEN → OPEN again)."""
    print("\n🧪 Test 6: Failed Recovery (HALF_OPEN → OPEN)")
    print("=" * 70)

    breaker = CircuitBreaker(
        failure_threshold=5,
        timeout_seconds=0.5,
        success_threshold=2,
    )

    async def failing_operation():
        raise Exception("Simulated failure")

    async def successful_operation():
        return "success"

    # Open the circuit
    for _ in range(5):
        try:
            await breaker.call(failing_operation)
        except:
            pass

    assert breaker.state == CircuitState.OPEN
    print("  Circuit opened")

    # Wait for timeout
    await asyncio.sleep(0.6)

    # First success (OPEN → HALF_OPEN)
    result = await breaker.call(successful_operation)
    state1 = breaker.get_state()
    print(f"  Success: {result}, State: {state1['state']}, Successes: {state1['success_count']}")
    assert breaker.state == CircuitState.HALF_OPEN

    # Now fail - should go back to OPEN
    try:
        await breaker.call(failing_operation)
    except Exception as e:
        state2 = breaker.get_state()
        print(f"  Failure: {e}, State: {state2['state']}")

    assert breaker.state == CircuitState.OPEN
    print("✅ Test 6 PASSED: Circuit breaker reopened after failure in HALF_OPEN")


async def test_circuit_breaker_registry():
    """Test CircuitBreakerRegistry."""
    print("\n🧪 Test 7: Circuit Breaker Registry")
    print("=" * 70)

    registry = CircuitBreakerRegistry()

    # Get breakers for different users
    breaker1 = registry.get_breaker(101)
    breaker2 = registry.get_breaker(102)
    breaker3 = registry.get_breaker(101)  # Should return same instance

    assert breaker1 is breaker3, "Should return same breaker instance for same user"
    assert breaker1 is not breaker2, "Should return different breaker instances for different users"
    print("  ✅ Registry returns correct breaker instances")

    # Open a circuit
    async def failing_operation():
        raise Exception("Simulated failure")

    for _ in range(5):
        try:
            await breaker1.call(failing_operation)
        except:
            pass

    # Check open breakers
    open_breakers = registry.get_open_breakers()
    assert 101 in open_breakers
    print(f"  ✅ Open breakers: {open_breakers}")

    # Reset breaker
    registry.reset_breaker(101)
    assert breaker1.state == CircuitState.CLOSED
    print("  ✅ Breaker reset successfully")

    # Get all states
    all_states = registry.get_all_states()
    print(f"  ✅ All states: {len(all_states)} breakers tracked")

    print("✅ Test 7 PASSED: Circuit breaker registry works correctly")


async def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("🔌 CIRCUIT BREAKER FUNCTIONALITY TEST SUITE")
    print("=" * 70)

    tests = [
        test_circuit_breaker_closed_state,
        test_circuit_breaker_opening,
        test_circuit_breaker_open_rejection,
        test_circuit_breaker_half_open,
        test_circuit_breaker_recovery_success,
        test_circuit_breaker_recovery_failure,
        test_circuit_breaker_registry,
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
        print("\n🎉 ALL TESTS PASSED! Circuit breaker is working correctly.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the output above.")

    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
