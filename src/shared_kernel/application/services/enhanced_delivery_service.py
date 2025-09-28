"""
Enhanced DeliveryService with idempotency and rate limiting for reliable message delivery.

This service extends the core DeliveryService with:
- Redis-based idempotency to prevent duplicate message sending
- Token bucket rate limiting for Telegram API compliance
- Conservative rate limits per chat and globally
"""

import hashlib
import logging
from collections.abc import Callable
from datetime import datetime
from typing import Any
from uuid import UUID

from core.common_helpers.idempotency import IdempotencyGuard
from core.common_helpers.ratelimit import TokenBucketRateLimiter
from src.shared_kernel.application.services import (
    DeliveryService as BaseDeliveryService,
)

logger = logging.getLogger(__name__)


class EnhancedDeliveryService(BaseDeliveryService):
    """Enhanced delivery service with idempotency and rate limiting."""

    def __init__(self, delivery_repo, schedule_repo, redis_url: str | None = None):
        super().__init__(delivery_repo, schedule_repo)
        self.idempotency_guard = IdempotencyGuard(redis_url)
        self.rate_limiter = TokenBucketRateLimiter(redis_url)

    def _generate_idempotency_key(
        self, post_id: UUID, channel_id: str, content_hash: str | None = None
    ) -> str:
        """Generate idempotency key for a delivery operation."""
        base_key = f"delivery:{post_id}:{channel_id}"
        if content_hash:
            base_key += f":{content_hash}"
        return base_key

    def _hash_content(self, post_data: dict) -> str:
        """Generate hash of post content for idempotency."""
        content_parts = [
            str(post_data.get("post_text", "")),
            str(post_data.get("media_id", "")),
            str(post_data.get("media_type", "")),
        ]
        content_str = "|".join(content_parts)
        return hashlib.sha256(content_str.encode()).hexdigest()

    async def send_with_reliability_guards(
        self,
        delivery_id: UUID,
        post_data: dict,
        send_function: Callable[..., Any],
        idempotency_ttl: int = 1800,  # 30 minutes
        max_rate_limit_wait: float = 120.0,  # 2 minutes max wait
    ) -> dict[str, Any]:
        """
        Send message with idempotency and rate limiting guards.

        Args:
            delivery_id: Unique delivery ID
            post_data: Post data including channel_id, post_text, etc.
            send_function: Async function to actually send the message
            idempotency_ttl: TTL for idempotency key in seconds
            max_rate_limit_wait: Maximum time to wait for rate limiting

        Returns:
            Dict with result status, message_id, and metadata
        """
        channel_id = str(post_data.get("channel_id", ""))
        post_id = post_data.get("id") or delivery_id

        # Generate idempotency key
        content_hash = self._hash_content(post_data)
        idempotency_key = self._generate_idempotency_key(post_id, channel_id, content_hash)

        logger.info(
            f"Starting reliable delivery: delivery_id={delivery_id}, "
            f"channel_id={channel_id}, idempotency_key={idempotency_key}"
        )

        # Step 1: Check for duplicate operation
        is_duplicate, existing_status = await self.idempotency_guard.is_duplicate(idempotency_key)

        if is_duplicate and existing_status:
            if existing_status.status == "completed":
                logger.info(
                    f"Duplicate delivery detected, returning cached result: {idempotency_key}"
                )
                return {
                    "success": True,
                    "message_id": (
                        existing_status.result.get("message_id") if existing_status.result else None
                    ),
                    "duplicate": True,
                    "cached_result": existing_status.result,
                    "delivery_id": delivery_id,
                    "idempotency_key": idempotency_key,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            elif existing_status.status == "processing":
                logger.warning(f"Operation already in progress: {idempotency_key}")
                return {
                    "success": False,
                    "error": "Operation already in progress",
                    "duplicate": True,
                    "delivery_id": delivery_id,
                    "idempotency_key": idempotency_key,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            elif existing_status.status == "failed":
                logger.info(f"Previous operation failed, allowing retry: {idempotency_key}")
                # Allow retry of failed operations

        # Step 2: Mark operation as started (atomic check)
        operation_started = await self.idempotency_guard.mark_operation_start(
            idempotency_key, idempotency_ttl
        )

        if not operation_started:
            logger.warning(f"Failed to acquire idempotency lock: {idempotency_key}")
            return {
                "success": False,
                "error": "Could not acquire operation lock",
                "duplicate": True,
                "delivery_id": delivery_id,
                "idempotency_key": idempotency_key,
                "timestamp": datetime.utcnow().isoformat(),
            }

        try:
            # Step 3: Apply rate limiting
            logger.debug(f"Checking rate limits for channel: {channel_id}")

            # Check per-chat rate limit
            chat_allowed = await self.rate_limiter.acquire_with_delay(
                bucket_id=channel_id,
                tokens=1,
                limit_type="chat",
                max_wait=max_rate_limit_wait,
            )

            if not chat_allowed:
                raise Exception(
                    f"Per-chat rate limit exceeded for {channel_id}, max wait time reached"
                )

            # Check global bot rate limit
            global_allowed = await self.rate_limiter.acquire_with_delay(
                bucket_id="global_bot",
                tokens=1,
                limit_type="global",
                max_wait=max_rate_limit_wait,
            )

            if not global_allowed:
                raise Exception("Global bot rate limit exceeded, max wait time reached")

            logger.info(f"Rate limits passed for channel: {channel_id}")

            # Step 4: Execute the actual send operation
            logger.info(f"Executing send operation for delivery: {delivery_id}")
            send_result = await send_function(post_data)

            # Step 5: Mark operation as completed
            result_data = {
                "success": True,
                "message_id": send_result.get("message_id"),
                "telegram_result": send_result,
                "delivery_id": str(delivery_id),
                "channel_id": channel_id,
                "timestamp": datetime.utcnow().isoformat(),
            }

            await self.idempotency_guard.mark_operation_complete(
                idempotency_key, result_data, idempotency_ttl
            )

            logger.info(
                f"Reliable delivery completed successfully: delivery_id={delivery_id}, "
                f"message_id={result_data['message_id']}"
            )

            return {
                **result_data,
                "duplicate": False,
                "idempotency_key": idempotency_key,
                "rate_limited": False,
            }

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Reliable delivery failed: delivery_id={delivery_id}, error={error_msg}")

            # Mark operation as failed
            await self.idempotency_guard.mark_operation_failed(
                idempotency_key, error_msg, idempotency_ttl
            )

            # Determine if this was a rate limiting issue
            is_rate_limit_error = any(
                phrase in error_msg.lower()
                for phrase in ["rate limit", "too many requests", "flood", "slow down"]
            )

            return {
                "success": False,
                "error": error_msg,
                "duplicate": False,
                "delivery_id": delivery_id,
                "idempotency_key": idempotency_key,
                "rate_limited": is_rate_limit_error,
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def get_rate_limit_status(self) -> dict[str, Any]:
        """Get current rate limiting status across all buckets."""
        try:
            chat_stats = await self.rate_limiter.get_bucket_stats("chat")
            global_stats = await self.rate_limiter.get_bucket_stats("global")
            user_stats = await self.rate_limiter.get_bucket_stats("user")

            return {
                "rate_limits": {
                    "chat_buckets": chat_stats,
                    "global_buckets": global_stats,
                    "user_buckets": user_stats,
                },
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error getting rate limit status: {e}")
            return {"error": str(e)}

    async def get_idempotency_stats(self) -> dict[str, Any]:
        """Get idempotency guard statistics."""
        try:
            cleaned_count = await self.idempotency_guard.cleanup_expired()
            return {
                "idempotency": {
                    "cleaned_expired_keys": cleaned_count,
                    "last_cleanup": datetime.utcnow().isoformat(),
                }
            }
        except Exception as e:
            logger.error(f"Error getting idempotency stats: {e}")
            return {"error": str(e)}

    async def reset_rate_limits(
        self, bucket_type: str = "chat", bucket_id: str | None = None
    ) -> dict[str, Any]:
        """Reset rate limiting buckets (admin function)."""
        try:
            if bucket_id:
                await self.rate_limiter.reset_bucket(bucket_id, bucket_type)
                return {
                    "reset": True,
                    "bucket_type": bucket_type,
                    "bucket_id": bucket_id,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            else:
                # Reset all buckets of this type (dangerous!)
                logger.warning(f"Resetting ALL {bucket_type} rate limit buckets")
                cleaned = await self.rate_limiter.cleanup_expired()
                return {
                    "reset_all": True,
                    "bucket_type": bucket_type,
                    "cleaned_buckets": cleaned,
                    "timestamp": datetime.utcnow().isoformat(),
                }
        except Exception as e:
            logger.error(f"Error resetting rate limits: {e}")
            return {"error": str(e)}

    async def close(self):
        """Close all connections."""
        await self.idempotency_guard.close()
        await self.rate_limiter.close()
