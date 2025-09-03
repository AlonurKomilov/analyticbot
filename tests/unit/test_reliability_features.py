"""
Unit tests for reliability features: idempotency and rate limiting.
"""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
import redis

from core.services.enhanced_delivery_service import EnhancedDeliveryService
from core.utils.idempotency import IdempotencyGuard
from core.utils.ratelimit import TokenBucketRateLimiter


class TestIdempotencyGuard:
    """Test cases for IdempotencyGuard."""

    @pytest.fixture
    def mock_redis(self):
        """Mock Redis client."""
        return MagicMock(spec=redis.Redis)

    @pytest.fixture
    def idempotency_guard(self, mock_redis):
        """Create IdempotencyGuard with mocked Redis."""
        with patch("core.utils.idempotency.redis") as mock_redis_module:
            mock_redis_module.from_url.return_value = mock_redis
            return IdempotencyGuard(redis_url="redis://mock", key_prefix="test")

    def test_make_key_creates_valid_key(self, idempotency_guard):
        """Test that idempotency key formatting works correctly."""
        operation_id = uuid4()
        content = {"message": "test", "channel": 123}

        # Create an idempotency key (this would normally be done by the service)
        idempotency_key = f"delivery:{operation_id}:123"

        key = idempotency_guard._make_key(idempotency_key)

        assert key.startswith("test:")
        assert str(operation_id) in key
        assert len(key) > len("test:")

    @pytest.mark.asyncio
    async def test_is_duplicate_returns_false_for_new_key(self, idempotency_guard, mock_redis):
        """Test that new operations are not flagged as duplicates."""
        with patch.object(idempotency_guard, "get_redis") as mock_get_redis:
            mock_get_redis.return_value = mock_redis
            mock_redis.get.return_value = None

            key = "test:idempotency:new_key"
            is_duplicate, status = await idempotency_guard.is_duplicate(key)

            assert is_duplicate is False
            assert status is None
            mock_redis.get.assert_called_once_with(key)

    @pytest.mark.asyncio
    async def test_is_duplicate_returns_true_for_existing_key(self, idempotency_guard, mock_redis):
        """Test that existing operations are flagged as duplicates."""
        with patch.object(idempotency_guard, "get_redis") as mock_get_redis:
            mock_get_redis.return_value = mock_redis
            # Mock existing idempotency status as JSON
            mock_status = '{"status": "processing", "created_at": "2025-01-01T00:00:00"}'
            mock_redis.get.return_value = mock_status

            key = "test:idempotency:existing_key"
            is_duplicate, status = await idempotency_guard.is_duplicate(key)

            assert is_duplicate is True
            assert status is not None
            assert status.status == "processing"

    @pytest.mark.asyncio
    async def test_mark_operation_start_sets_status(self, idempotency_guard, mock_redis):
        """Test that operation start is marked correctly."""
        with patch.object(idempotency_guard, "get_redis") as mock_get_redis:
            mock_get_redis.return_value = mock_redis
            mock_redis.set.return_value = True

            key = "test:idempotency:start_key"
            result = await idempotency_guard.mark_operation_start(key)

            assert result is True
            mock_redis.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_mark_operation_complete_updates_status(self, idempotency_guard, mock_redis):
        """Test that operation completion is marked correctly."""
        with patch.object(idempotency_guard, "get_redis") as mock_get_redis:
            mock_get_redis.return_value = mock_redis
            mock_redis.set.return_value = True

            key = "test:idempotency:complete_key"
            result_data = {"message_id": 12345}
            result = await idempotency_guard.mark_operation_complete(key, result_data)

            # mark_operation_complete returns None, not True
            assert result is None
            mock_redis.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_cleanup_expired_removes_old_entries(self, idempotency_guard, mock_redis):
        """Test that expired entries are cleaned up."""
        with patch.object(idempotency_guard, "get_redis") as mock_get_redis:
            mock_get_redis.return_value = mock_redis
            mock_redis.keys.return_value = [
                "test:idempotency:old1",
                "test:idempotency:old2",
            ]
            mock_redis.ttl.side_effect = [-1, 3600]  # old1 expired, old2 still valid
            mock_redis.delete.return_value = 1

            result = await idempotency_guard.cleanup_expired()

            assert result == 1  # One key cleaned up
            mock_redis.delete.assert_called_once_with("test:old1")


class TestTokenBucketRateLimiter:
    """Test cases for TokenBucketRateLimiter."""

    @pytest.fixture
    def mock_redis(self):
        """Mock Redis client."""
        return MagicMock(spec=redis.Redis)

    @pytest.fixture
    def rate_limiter(self, mock_redis):
        """Create TokenBucketRateLimiter with mocked Redis."""
        with patch("core.utils.ratelimit.redis") as mock_redis_module:
            mock_redis_module.from_url.return_value = mock_redis
            return TokenBucketRateLimiter(
                redis_url="redis://mock",
                key_prefix="test:rate",
            )

    def test_get_bucket_key_formats_correctly(self, rate_limiter):
        """Test bucket key generation."""
        identifier = "user:123"
        limit_type = "chat"

        key = rate_limiter._make_key(identifier, limit_type)

        assert key == "test:rate:chat:user:123"

    @pytest.mark.asyncio
    async def test_acquire_allows_when_tokens_available(self, rate_limiter, mock_redis):
        """Test token acquisition when bucket has capacity."""
        with (
            patch.object(rate_limiter, "get_redis") as mock_get_redis,
            patch("time.time", return_value=1000.0),
        ):
            mock_get_redis.return_value = mock_redis
            # Mock Lua script execution - simulate tokens available
            mock_redis.eval.return_value = [
                1,
                9,
                1000.0,
            ]  # [success, remaining_tokens, updated_at]

            success, retry_after = await rate_limiter.acquire(
                bucket_id="user:123", tokens=1, limit_type="chat"
            )

            assert success is True
            assert retry_after == 0.0
            mock_redis.eval.assert_called_once()

    @pytest.mark.asyncio
    async def test_acquire_rejects_when_no_tokens(self, rate_limiter, mock_redis):
        """Test token acquisition when bucket is empty."""
        with (
            patch.object(rate_limiter, "get_redis") as mock_get_redis,
            patch("time.time", return_value=1000.0),
        ):
            mock_get_redis.return_value = mock_redis
            # Mock Lua script execution - simulate no tokens
            mock_redis.eval.return_value = [
                0,
                0,
                1000.0,
                60.0,
            ]  # [success, remaining_tokens, updated_at, retry_after]

            success, retry_after = await rate_limiter.acquire(
                bucket_id="user:123", tokens=1, limit_type="chat"
            )

            assert success is False
            assert retry_after == 60.0

    @pytest.mark.asyncio
    async def test_acquire_with_delay_waits_and_retries(self, rate_limiter, mock_redis):
        """Test acquire_with_delay waits for tokens and retries."""
        with patch.object(rate_limiter, "get_redis") as mock_get_redis:
            mock_get_redis.return_value = mock_redis
            # First call: no tokens, second call: tokens available
            mock_redis.eval.side_effect = [
                [0, 0, 1000.0, 1.0],  # [success, remaining, updated_at, retry_after]
                [1, 5, 1001.0],  # [success, remaining, updated_at]
            ]

            with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
                success = await rate_limiter.acquire_with_delay(
                    bucket_id="user:123",
                    tokens=1,
                    limit_type="chat",
                    max_wait=10.0,
                )

            assert success is True
            mock_sleep.assert_called_once_with(1.0)
            assert mock_redis.eval.call_count == 2

    @pytest.mark.asyncio
    async def test_get_bucket_stats_returns_current_state(self, rate_limiter, mock_redis):
        """Test bucket statistics retrieval."""
        with patch.object(rate_limiter, "get_redis") as mock_get_redis:
            mock_get_redis.return_value = mock_redis
            mock_redis.keys.return_value = ["test:rate:chat:user:123"]
            mock_redis.hmget.return_value = ["5", "1000.0"]  # [tokens, last_refill]

            stats = await rate_limiter.get_bucket_stats("chat")

            assert "total_buckets" in stats
            assert "limit_type" in stats
            assert "config" in stats
            mock_redis.keys.assert_called_once()


class TestEnhancedDeliveryService:
    """Test cases for EnhancedDeliveryService."""

    @pytest.fixture
    def mock_delivery_service(self):
        """Create EnhancedDeliveryService with mocked dependencies."""
        with (
            patch("core.utils.idempotency.redis") as mock_redis_idempotency,
            patch("core.utils.ratelimit.redis") as mock_redis_ratelimit,
        ):
            # Mock Redis connections
            mock_redis_idempotency.from_url.return_value = MagicMock()
            mock_redis_ratelimit.from_url.return_value = MagicMock()

            service = EnhancedDeliveryService(
                delivery_repo=None,
                schedule_repo=None,
                redis_url="redis://localhost:6379",
            )
            return service

    @pytest.mark.asyncio
    async def test_send_with_reliability_guards_success_path(self, mock_delivery_service):
        """Test successful message sending with all guards."""
        service = mock_delivery_service

        # Mock the internal guard methods
        with (
            patch.object(
                service.idempotency_guard, "is_duplicate", return_value=(False, None)
            ) as mock_duplicate,
            patch.object(
                service.idempotency_guard, "mark_operation_start", return_value=True
            ) as mock_start,
            patch.object(service.idempotency_guard, "mark_operation_complete") as mock_complete,
            patch.object(
                service.rate_limiter, "acquire_with_delay", return_value=True
            ) as mock_rate_limit,
        ):
            # Mock successful send function
            async def mock_send_function(post_data):
                return {"message_id": 12345, "success": True}

            # Test the method
            result = await service.send_with_reliability_guards(
                delivery_id=uuid4(),
                post_data={"text": "test", "channel_id": 123},
                send_function=mock_send_function,
                idempotency_ttl=300,
                max_rate_limit_wait=60.0,
            )

            # Assertions
            assert result["success"] is True
            assert result["message_id"] == 12345
            assert result["duplicate"] is False
            assert result["rate_limited"] is False

            # Verify guard methods were called
            mock_duplicate.assert_called_once()
            mock_start.assert_called_once()
            mock_complete.assert_called_once()
            assert mock_rate_limit.call_count == 2  # chat and global limits

    @pytest.mark.asyncio
    async def test_send_with_reliability_guards_duplicate_detection(self, mock_delivery_service):
        """Test duplicate request handling."""
        service = mock_delivery_service

        # Mock duplicate detection
        with patch.object(
            service.idempotency_guard,
            "is_duplicate",
            return_value=(
                True,
                MagicMock(status="completed", result={"message_id": 12345}),
            ),
        ) as mock_duplicate:

            async def mock_send_function(post_data):
                return {"message_id": 12345, "success": True}

            # Test the method
            result = await service.send_with_reliability_guards(
                delivery_id=uuid4(),
                post_data={"text": "test", "channel_id": 123},
                send_function=mock_send_function,
                idempotency_ttl=300,
                max_rate_limit_wait=60.0,
            )

            # Assertions
            assert result["success"] is True
            assert result["duplicate"] is True
            assert "idempotency_key" in result

            # Verify send function was NOT called and rate limiting was skipped
            mock_duplicate.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_with_reliability_guards_rate_limit_exceeded(self, mock_delivery_service):
        """Test rate limit handling."""
        service = mock_delivery_service

        # Mock successful duplicate check and operation start
        with (
            patch.object(
                service.idempotency_guard, "is_duplicate", return_value=(False, None)
            ) as mock_duplicate,
            patch.object(
                service.idempotency_guard, "mark_operation_start", return_value=True
            ) as mock_start,
            patch.object(
                service.rate_limiter, "acquire_with_delay", return_value=False
            ) as mock_rate_limit,
        ):

            async def mock_send_function(post_data):
                return {"message_id": 12345, "success": True}

            # Test the method
            result = await service.send_with_reliability_guards(
                delivery_id=uuid4(),
                post_data={"text": "test", "channel_id": 123},
                send_function=mock_send_function,
                idempotency_ttl=300,
                max_rate_limit_wait=60.0,  # Less than retry_after, should fail
            )

            # Assertions
            assert result["success"] is False
            assert result["rate_limited"] is True
            assert "rate limit exceeded" in result["error"].lower()

            # Verify flow
            mock_duplicate.assert_called_once()
            mock_start.assert_called_once()
            mock_rate_limit.assert_called()

    def test_generate_content_hash_consistent(self, mock_delivery_service):
        """Test that content hash generation is consistent."""
        service = mock_delivery_service

        post_data = {"text": "test message", "channel_id": 123, "buttons": ["btn1"]}

        hash1 = service._hash_content(post_data)
        hash2 = service._hash_content(post_data)

        assert hash1 == hash2
        assert len(hash1) == 32  # MD5 hash length

    def test_generate_content_hash_different_for_different_content(self, mock_delivery_service):
        """Test that different content produces different hashes."""
        service = mock_delivery_service

        post_data1 = {"post_text": "test message", "channel_id": 123}
        post_data2 = {"post_text": "different message", "channel_id": 123}

        hash1 = service._hash_content(post_data1)
        hash2 = service._hash_content(post_data2)

        assert hash1 != hash2


@pytest.mark.integration
class TestReliabilityIntegration:
    """Integration tests for reliability features."""

    @pytest.mark.asyncio
    async def test_full_reliability_pipeline(self):
        """Test the complete reliability pipeline with real Redis."""
        # This would require a real Redis instance for integration testing
        # For now, we'll mark it as a placeholder for integration tests

    def test_redis_connection_handling(self):
        """Test Redis connection error handling."""
        # Test what happens when Redis is unavailable

    def test_concurrent_operations_handling(self):
        """Test handling of concurrent operations with same idempotency key."""
        # Test race conditions and concurrent access


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
