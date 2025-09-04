"""
Celery Tasks - Master Task Collection
Production-ready tasks with enhanced retry/backoff strategies
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from infra.celery.celery_app import critical_message_task, enhanced_retry_task
from apps.bot.container import container
from config.settings import Settings
from pydantic import SecretStr

try:
    from aiogram.client.bot import Bot as _AioBot
except Exception:
    from aiogram import Bot as _AioBot

logger = logging.getLogger(__name__)


@critical_message_task(
    bind=True,
    name="infra.celery.tasks.send_message_task",
    autoretry_for=(Exception,),
    retry_backoff=2,
    retry_jitter=True,
    max_retries=5,
)
def send_message_task(
    self, chat_id: str, message: str, idempotency_key: str | None = None, **kwargs
) -> dict[str, Any]:
    """
    Enhanced message sending task with idempotency and rate limiting.

    Args:
        chat_id: Target chat ID
        message: Message text
        idempotency_key: Optional idempotency key for duplicate prevention
        **kwargs: Additional parameters for bot.send_message()
    """
    import asyncio

    async def _send_message_with_reliability():
        try:
            # Import inside task to avoid circular imports
            from apps.bot.container import container
            from apps.bot.utils.error_handler import ErrorContext, ErrorHandler
            from core.common_helpers.idempotency import IdempotencyGuard
            from core.common_helpers.ratelimit import TokenBucketRateLimiter

            context = (
                ErrorContext()
                .add("task", "send_message_task")
                .add("chat_id", chat_id)
                .add("idempotency_key", idempotency_key)
                .add("retry", self.request.retries if hasattr(self.request, "retries") else 0)
            )

            # Generate idempotency key if not provided
            effective_idempotency_key = idempotency_key or f"task:{self.request.id}"

            logger.info(
                f"Sending message to {chat_id} with reliability guards "
                f"(attempt {self.request.retries + 1}/6, key={effective_idempotency_key})"
            )

            # Initialize reliability components
            idempotency_guard = IdempotencyGuard()
            rate_limiter = TokenBucketRateLimiter()

            # Check for duplicate operation
            is_duplicate, existing_status = await idempotency_guard.is_duplicate(
                effective_idempotency_key
            )

            if is_duplicate and existing_status and existing_status.status == "completed":
                logger.info(
                    f"Duplicate task detected, returning cached result: {effective_idempotency_key}"
                )
                return {
                    "success": True,
                    "message_id": existing_status.result.get("message_id")
                    if existing_status.result
                    else None,
                    "chat_id": chat_id,
                    "duplicate": True,
                    "cached_result": existing_status.result,
                    "timestamp": datetime.utcnow().isoformat(),
                }

            # Mark operation as started
            operation_started = await idempotency_guard.mark_operation_start(
                effective_idempotency_key
            )
            if not operation_started:
                logger.warning(f"Could not acquire idempotency lock: {effective_idempotency_key}")
                raise Exception("Operation already in progress")

            try:
                # Apply rate limiting
                chat_allowed = await rate_limiter.acquire_with_delay(
                    bucket_id=str(chat_id),
                    tokens=1,
                    limit_type="chat",
                    max_wait=60.0,  # 1 minute max wait
                )

                if not chat_allowed:
                    raise Exception(f"Chat rate limit exceeded for {chat_id}")

                global_allowed = await rate_limiter.acquire_with_delay(
                    bucket_id="global_bot", tokens=1, limit_type="global", max_wait=60.0
                )

                if not global_allowed:
                    raise Exception("Global bot rate limit exceeded")

                # Get bot instance and send message
                bot = container.resolve(_AioBot)
                result = await bot.send_message(chat_id=chat_id, text=message, **kwargs)

                logger.info(f"Message sent successfully to {chat_id}: {result.message_id}")

                # Prepare result data
                result_data = {
                    "success": True,
                    "message_id": result.message_id,
                    "chat_id": chat_id,
                    "retry_count": self.request.retries,
                    "idempotency_key": effective_idempotency_key,
                    "rate_limited": False,
                    "duplicate": False,
                    "timestamp": datetime.utcnow().isoformat(),
                }

                # Mark operation as completed
                await idempotency_guard.mark_operation_complete(
                    effective_idempotency_key, result_data
                )

                # Record success metric
                try:
                    from apps.bot.utils.monitoring import metrics

                    metrics.record_metric(
                        "message_sent_success",
                        1.0,
                        {
                            "chat_id": str(chat_id),
                            "retry_count": str(self.request.retries),
                            "with_idempotency": str(bool(idempotency_key)).lower(),
                        },
                    )
                except ImportError:
                    pass

                return result_data

            except Exception as send_error:
                # Mark operation as failed
                await idempotency_guard.mark_operation_failed(
                    effective_idempotency_key, str(send_error)
                )
                raise send_error

        except Exception as e:
            context.add("error", str(e))
            ErrorHandler.log_error(e, context)

            # Record failure metric
            try:
                from apps.bot.utils.monitoring import metrics

                metrics.record_metric(
                    "message_sent_failure",
                    1.0,
                    {
                        "chat_id": str(chat_id),
                        "retry_count": str(self.request.retries),
                        "error_type": type(e).__name__,
                        "with_idempotency": str(bool(idempotency_key)).lower(),
                    },
                )
            except ImportError:
                pass

            # Calculate delay for next retry
            delay = min(10 * (2**self.request.retries), 300)  # Max 5 minutes

            # Check if this is a rate limit error and adjust delay
            if any(phrase in str(e).lower() for phrase in ["rate limit", "flood", "too many"]):
                delay = min(delay * 2, 600)  # Double delay for rate limit errors, max 10 minutes
                logger.warning(f"Rate limit detected, extending retry delay to {delay}s")

            logger.warning(f"Message send failed to {chat_id}, retrying in {delay}s: {e}")
            raise self.retry(countdown=delay, exc=e)

    return asyncio.run(_send_message_with_reliability())


@enhanced_retry_task(
    bind=True,
    name="infra.celery.tasks.process_analytics",
    autoretry_for=(Exception,),
    retry_backoff=2,
    retry_jitter=True,
    max_retries=3,
)
def process_analytics(self, channel_id: str, post_id: str | None = None) -> dict[str, Any]:
    """
    Process analytics data for a channel/post with retry capability.

    Args:
        channel_id: Telegram channel ID
        post_id: Specific post ID (optional)

    Returns:
        Dict with processing results
    """
    import asyncio

    async def _process():
        try:
            from apps.bot.container import container
            from apps.bot.utils.error_handler import ErrorContext, ErrorHandler

            context = (
                ErrorContext()
                .add("task", "process_analytics")
                .add("channel_id", channel_id)
                .add("post_id", post_id)
            )

            logger.info(f"Processing analytics for channel {channel_id}")

            # Get analytics service
            analytics_service = container.analytics_service()

            if post_id:
                result = await analytics_service.update_post_analytics(channel_id, post_id)
            else:
                result = await analytics_service.update_channel_analytics(channel_id)

            logger.info(
                f"Analytics processed for {channel_id}: {result.get('processed_count', 0)} items"
            )

            return {
                "success": True,
                "channel_id": channel_id,
                "post_id": post_id,
                "processed_count": result.get("processed_count", 0),
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            context.add("error", str(e))
            ErrorHandler.log_error(e, context)

            delay = min(30 * (2**self.request.retries), 300)
            logger.warning(
                f"Analytics processing failed for {channel_id}, retrying in {delay}s: {e}"
            )

            raise self.retry(countdown=delay, exc=e)

    return asyncio.run(_process())


@enhanced_retry_task(
    bind=True,
    name="infra.celery.tasks.cleanup_old_data",
    autoretry_for=(Exception,),
    retry_backoff=2,
    retry_jitter=True,
    max_retries=3,
)
def cleanup_old_data(self, days_old: int = 30) -> dict[str, Any]:
    """
    Clean up old data from database (logs, metrics, etc.).

    Args:
        days_old: Remove data older than this many days

    Returns:
        Dict with cleanup results
    """
    import asyncio

    async def _cleanup():
        try:
            from apps.bot.container import container

            logger.info(f"Starting cleanup of data older than {days_old} days")

            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            cleanup_results = {}

            # Clean up old metrics
            try:
                metrics_repo = container.metrics_repository()
                deleted_metrics = await metrics_repo.delete_old_metrics(cutoff_date)
                cleanup_results["metrics"] = deleted_metrics
                logger.info(f"Cleaned up {deleted_metrics} old metrics")
            except Exception as e:
                logger.warning(f"Failed to cleanup metrics: {e}")
                cleanup_results["metrics"] = 0

            # Clean up old logs
            try:
                logs_repo = container.logs_repository()
                deleted_logs = await logs_repo.delete_old_logs(cutoff_date)
                cleanup_results["logs"] = deleted_logs
                logger.info(f"Cleaned up {deleted_logs} old logs")
            except Exception as e:
                logger.warning(f"Failed to cleanup logs: {e}")
                cleanup_results["logs"] = 0

            total_cleaned = sum(cleanup_results.values())
            logger.info(f"Cleanup completed: {total_cleaned} total items removed")

            return {
                "success": True,
                "days_old": days_old,
                "cutoff_date": cutoff_date.isoformat(),
                "results": cleanup_results,
                "total_cleaned": total_cleaned,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Cleanup task failed: {e}")

            delay = min(60 * (2**self.request.retries), 600)
            raise self.retry(countdown=delay, exc=e)

    return asyncio.run(_cleanup())


@enhanced_retry_task(
    bind=True,
    name="infra.celery.tasks.health_check_task",
    autoretry_for=(Exception,),
    retry_backoff=2,
    retry_jitter=True,
    max_retries=2,
)
def health_check_task(self) -> dict[str, Any]:
    """
    Comprehensive system health check task.

    Returns:
        Dict with health status of all components
    """
    import asyncio

    async def _health_check():
        try:
            from apps.bot.container import container

            logger.debug("Running system health check")

            health_results = {"timestamp": datetime.utcnow().isoformat(), "components": {}}

            # Check database health
            try:
                db = container.db_session()
                # Simple query to check DB connectivity
                await db.execute("SELECT 1")
                health_results["components"]["database"] = {
                    "status": "healthy",
                    "response_time_ms": 0,  # Could measure actual response time
                }
            except Exception as e:
                logger.warning(f"Database health check failed: {e}")
                health_results["components"]["database"] = {"status": "unhealthy", "error": str(e)}

            # Check Redis health
            try:
                import redis

                from config.settings import Settings

                try:
                    settings = Settings()
                except Exception:
                    # For tests/development, create settings with minimal required values
                    import os
                    settings = Settings(
                        BOT_TOKEN=SecretStr(os.getenv("BOT_TOKEN", "test_token")),
                        STORAGE_CHANNEL_ID=int(os.getenv("STORAGE_CHANNEL_ID", "0")),
                        POSTGRES_USER=os.getenv("POSTGRES_USER", "test_user"),
                        POSTGRES_PASSWORD=SecretStr(os.getenv("POSTGRES_PASSWORD", "test_pass")),
                        POSTGRES_DB=os.getenv("POSTGRES_DB", "test_db"),
                        JWT_SECRET_KEY=SecretStr(os.getenv("JWT_SECRET_KEY", "test_jwt_key"))
                    )
                redis_client = redis.from_url(str(settings.REDIS_URL))
                redis_client.ping()
                health_results["components"]["redis"] = {"status": "healthy"}
            except Exception as e:
                logger.warning(f"Redis health check failed: {e}")
                health_results["components"]["redis"] = {"status": "unhealthy", "error": str(e)}

            # Check Telegram API health
            try:
                bot = container.resolve(_AioBot)
                me = await bot.get_me()
                health_results["components"]["telegram"] = {
                    "status": "healthy",
                    "bot_username": me.username,
                }
            except Exception as e:
                logger.warning(f"Telegram health check failed: {e}")
                health_results["components"]["telegram"] = {"status": "unhealthy", "error": str(e)}

            # Overall health status
            all_healthy = all(
                comp.get("status") == "healthy" for comp in health_results["components"].values()
            )
            health_results["overall_status"] = "healthy" if all_healthy else "degraded"

            logger.info(f"Health check completed: {health_results['overall_status']}")

            return health_results

        except Exception as e:
            logger.error(f"Health check task failed: {e}")
            raise self.retry(countdown=30, exc=e)

    return asyncio.run(_health_check())


@enhanced_retry_task(
    bind=True,
    name="infra.celery.tasks.scheduled_broadcast",
    autoretry_for=(Exception,),
    retry_backoff=2,
    retry_jitter=True,
    max_retries=3,
)
def scheduled_broadcast(
    self, message: str, target_channels: list, schedule_time: str
) -> dict[str, Any]:
    """
    Send scheduled broadcast message to multiple channels.

    Args:
        message: Message content to broadcast
        target_channels: List of channel IDs to send to
        schedule_time: ISO timestamp of when this was scheduled

    Returns:
        Dict with broadcast results
    """
    logger.info(f"Starting scheduled broadcast to {len(target_channels)} channels")

    results = {"success": 0, "failed": 0, "total": len(target_channels), "failures": []}

    for channel_id in target_channels:
        try:
            # Use the critical message task for individual sends
            result = send_message_task.delay(chat_id=channel_id, message=message)

            # Wait for result (with timeout)
            task_result = result.get(timeout=30)

            if task_result.get("success"):
                results["success"] += 1
            else:
                results["failed"] += 1
                results["failures"].append({"channel_id": channel_id, "error": "Task failed"})

        except Exception as e:
            logger.warning(f"Failed to send to channel {channel_id}: {e}")
            results["failed"] += 1
            results["failures"].append({"channel_id": channel_id, "error": str(e)})

    logger.info(f"Broadcast completed: {results['success']}/{results['total']} successful")

    return {
        "success": True,
        "broadcast_results": results,
        "scheduled_time": schedule_time,
        "completed_time": datetime.utcnow().isoformat(),
    }


# Task registry for easy discovery
AVAILABLE_TASKS = {
    "send_message_task": send_message_task,
    "process_analytics": process_analytics,
    "cleanup_old_data": cleanup_old_data,
    "health_check_task": health_check_task,
    "scheduled_broadcast": scheduled_broadcast,
}

logger.info(f"Registered {len(AVAILABLE_TASKS)} Celery tasks in infra.celery.tasks")
