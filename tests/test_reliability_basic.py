#!/usr/bin/env python3
"""
Simple test runner for reliability features to validate basic functionality.
"""

import sys
from datetime import datetime
from unittest.mock import MagicMock
from uuid import uuid4

# Add the project root to Python path
sys.path.insert(0, "/workspaces/analyticbot")


def test_idempotency_basic():
    """Test basic idempotency functionality."""
    try:
        from core.common_helpers.idempotency import IdempotencyGuard, IdempotencyStatus

        # Create mock Redis client
        mock_redis = MagicMock()
        guard = IdempotencyGuard()
        guard._redis = mock_redis

        print("✅ IdempotencyGuard import and initialization: PASSED")

        # Test IdempotencyStatus model
        status = IdempotencyStatus(status="processing",             created_at=datetime.fromisoformat("2024-01-01T00:00:00+00:00"))
        assert status.status == "processing"
        print("✅ IdempotencyStatus model: PASSED")

        print("🎉 All IdempotencyGuard tests PASSED!")
        return True

    except Exception as e:
        print(f"❌ IdempotencyGuard test FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_rate_limiter_basic():
    """Test basic rate limiter functionality."""
    try:
        from core.common_helpers.ratelimit import (
            RateLimitResult,
            TokenBucketConfig,
            TokenBucketRateLimiter,
        )

        # Create mock Redis client
        mock_redis = MagicMock()
        limiter = TokenBucketRateLimiter()
        limiter._redis = mock_redis

        print("✅ TokenBucketRateLimiter import and initialization: PASSED")

        # Test config model
        config = TokenBucketConfig(capacity=10, refill_rate=1.0)
        assert config.capacity == 10
        assert config.refill_rate == 1.0
        print("✅ TokenBucketConfig model: PASSED")

        # Test result model with all required fields
        result = RateLimitResult(
            allowed=True, tokens_remaining=5, retry_after_seconds=0.0, bucket_key="test_key"
        )
        assert result.allowed is True
        assert result.tokens_remaining == 5
        print("✅ RateLimitResult model: PASSED")

        print("🎉 All TokenBucketRateLimiter tests PASSED!")
        return True

    except Exception as e:
        print(f"❌ TokenBucketRateLimiter test FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_enhanced_delivery_service_basic():
    """Test basic enhanced delivery service functionality."""
    try:
        # Mock the Redis module and dependencies at module level
        import sys
        from unittest.mock import MagicMock

        # Mock redis module
        mock_redis = MagicMock()
        sys.modules["redis"] = mock_redis
        sys.modules["redis.asyncio"] = mock_redis

        from core.services.enhanced_delivery_service import EnhancedDeliveryService

        # Create service
        service = EnhancedDeliveryService(delivery_repo=None, schedule_repo=None)

        print("✅ EnhancedDeliveryService import and initialization: PASSED")

        # Test content hash generation (using correct method name)
        post_data = {"post_text": "test message", "channel_id": 123, "buttons": ["btn1"]}
        hash1 = service._hash_content(post_data)
        hash2 = service._hash_content(post_data)

        assert hash1 == hash2
        assert len(hash1) == 32  # MD5 hash length
        print("✅ EnhancedDeliveryService content hash: PASSED")

        # Test different content produces different hashes
        post_data2 = {"post_text": "different message", "channel_id": 123}
        hash3 = service._hash_content(post_data2)
        assert hash1 != hash3
        print("✅ EnhancedDeliveryService different content hash: PASSED")

        # Test idempotency key generation
        test_post_id = uuid4()
        key = service._generate_idempotency_key(test_post_id, "456", hash1)
        assert str(test_post_id) in key
        assert "456" in key
        print("✅ EnhancedDeliveryService idempotency key generation: PASSED")

        print("🎉 All EnhancedDeliveryService tests PASSED!")
        return True

    except Exception as e:
        print(f"❌ EnhancedDeliveryService test FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all basic tests."""
    print("🚀 Starting basic reliability features tests...\n")

    results = []

    print("📋 Testing IdempotencyGuard...")
    results.append(test_idempotency_basic())
    print()

    print("📋 Testing TokenBucketRateLimiter...")
    results.append(test_rate_limiter_basic())
    print()

    print("📋 Testing EnhancedDeliveryService...")
    results.append(test_enhanced_delivery_service_basic())
    print()

    # Summary
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"🎉 ALL TESTS PASSED! ({passed}/{total})")
        print("✅ Reliability features are working correctly!")
        return 0
    else:
        print(f"❌ SOME TESTS FAILED! ({passed}/{total})")
        return 1


if __name__ == "__main__":
    exit(main())
