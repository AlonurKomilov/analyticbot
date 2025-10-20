import asyncio
import logging
from datetime import datetime
from typing import Any

# Metrics now via DI (Phase 3.4)
from apps.bot.metrics_decorators import metrics_timer
from apps.bot.utils.error_handler import ErrorContext, ErrorHandler
from apps.bot.utils.task_utils import enhanced_retry_task

logger = logging.getLogger(__name__)
from apps.di import get_container


async def cleanup_resources():
    """Clean up resources after task completion"""
    try:
        # Note: db_session method doesn't exist in clean container
        # This cleanup is handled by the DI container lifecycle
        pass
    except Exception as e:
        logger.warning("Resource cleanup warning", exc_info=e)


@enhanced_retry_task
def send_post_task(scheduler_id: int):
    async def _run():
        context = ErrorContext().add("task", "send_post_task").add("scheduler_id", scheduler_id)
        try:
            container = get_container()
            bot = await container.bot.bot_client()
            scheduler_repo_result = await container.database.schedule_repo()

            # Handle potential coroutines
            if asyncio.iscoroutine(scheduler_repo_result):
                scheduler_repository = await scheduler_repo_result
            else:
                scheduler_repository = scheduler_repo_result

            # Convert int to UUID if needed
            from uuid import UUID

            try:
                post_uuid = UUID(str(scheduler_id))
                if hasattr(scheduler_repository, "get_by_id"):
                    scheduler = await scheduler_repository.get_by_id(post_uuid)
                else:
                    logger.warning("scheduler_repository.get_by_id method not available")
                    return "method-not-available"
            except (ValueError, TypeError):
                logger.warning(f"Invalid scheduler_id format: {scheduler_id}")
                return "invalid-scheduler-id"
            if not scheduler:
                logger.warning(f"Scheduler {scheduler_id} not found")
                return "scheduler-not-found"
            logger.info(f"Processed scheduler task {scheduler_id}")
            return "completed"
        except Exception as e:
            logger.error(f"Error in send_post_task: {e}")
            raise

    # Run the async function
    import asyncio

    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(_run())
    except RuntimeError:
        # If no loop is running, create a new one
        return asyncio.run(_run())

    return asyncio.run(_run())


@enhanced_retry_task
def remove_expired_schedulers():
    async def _run():
        context = ErrorContext().add("task", "remove_expired_schedulers")
        try:
            bot = get_container().bot_client()
            repo = get_container().schedule_repo()
            # TODO: Implement remove_expired using clean architecture patterns
            # For now, using safe placeholder that logs the request
            logger.info("remove_expired_schedulers called - placeholder implementation")
            removed_count = 0  # Safe placeholder logic
            logger.info(f"Removed {removed_count} expired schedulers (placeholder)")
            return f"removed-{removed_count}"
        except Exception as e:
            ErrorHandler.log_error(e, context)
            raise
        finally:
            await cleanup_resources()

    return asyncio.run(_run())


@enhanced_retry_task
def send_scheduled_message():
    async def _run() -> str:
        context = ErrorContext().add("task", "send_scheduled_message")
        stats = {"processed": 0, "sent": 0, "errors": 0}
        try:
            # Get services from container with fallback handling
            bot = get_container().bot_client()
            scheduler_service = get_container().scheduler_service()
            scheduler_repo_result = get_container().schedule_repo()

            # Handle potential coroutines
            if asyncio.iscoroutine(scheduler_repo_result):
                scheduler_repo = await scheduler_repo_result
            else:
                scheduler_repo = scheduler_repo_result

            # Safety checks for services
            if not scheduler_service:
                logger.error("Scheduler service not available")
                return "scheduler-service-unavailable"

            if not scheduler_repo:
                logger.error("Scheduler repository not available")
                return "scheduler-repo-unavailable"

            # TODO: Implement claim_due_posts using clean architecture - PLACEHOLDER
            # Using safe fallback implementation that logs the request
            logger.info("claim_due_posts called - using safe placeholder implementation")
            due_posts: list[Any] = []  # Safe placeholder - no actual posts claimed

            if not due_posts:
                logger.info("No due posts to send (placeholder implementation)")
                return "no-due-posts"
            logger.info(f"Processing {len(due_posts)} due posts")
            stats["processed"] = len(due_posts)
            for post in due_posts:
                try:
                    if hasattr(scheduler_service, "send_post_to_channel"):
                        result = await scheduler_service.send_post_to_channel(post)
                    else:
                        logger.warning("send_post_to_channel method not available")
                        stats["errors"] += 1
                        continue
                    if result.get("success"):
                        stats["sent"] += 1
                        logger.debug(f"Successfully sent post {post.id}")
                    else:
                        stats["errors"] += 1
                        logger.warning(f"Failed to send post {post.id}: {result.get('error')}")
                except Exception as e:
                    stats["errors"] += 1
                    post_context = context.add("post_id", str(post.id))
                    ErrorHandler.log_error(e, post_context)
            logger.info(
                f"Scheduled message task completed. Processed: {stats['processed']}, Sent: {stats['sent']}, Errors: {stats['errors']}"
            )
            return f"processed-{stats['processed']}-sent-{stats['sent']}-errors-{stats['errors']}"
        except Exception as e:
            ErrorHandler.log_error(e, context)
            raise
        finally:
            await cleanup_resources()

    return asyncio.run(_run())


@enhanced_retry_task
@metrics_timer(metric_type="celery_task", metric_name="update_post_views_task")
def update_post_views_task():
    async def _run() -> str:
        context = ErrorContext().add("task", "update_post_views_task")
        try:
            bot = get_container().bot_client()
            analytics_service = get_container().analytics_service()

            # Safety check
            if not analytics_service:
                logger.error("Analytics service not available")
                return "analytics-service-unavailable"

            logger.info("Starting post views update task")

            if hasattr(analytics_service, "update_all_post_views"):
                stats = await analytics_service.update_all_post_views()
            else:
                logger.warning("update_all_post_views method not available")
                return "method-not-available"

            result = f"processed-{stats.get('processed', 0)}-updated-{stats.get('updated', 0)}-errors-{stats.get('errors', 0)}-skipped-{stats.get('skipped', 0)}"
            logger.info(f"Post views update completed: {result}")
            return result
        except Exception as e:
            ErrorHandler.log_error(e, context)
            raise
        finally:
            await cleanup_resources()

    return asyncio.run(_run())


@enhanced_retry_task
def health_check_task():
    """Periodic health check task for monitoring system status"""

    async def _run() -> str:
        context = ErrorContext().add("task", "health_check_task")
        try:
            # Use apps layer health service instead of direct infra import
            from apps.api.services.health_service import health_service

            system_health = await health_service.get_system_health()
            db_healthy = system_health.status == "healthy"
            try:
                bot = get_container().bot_client()
                if bot and hasattr(bot, "get_me"):
                    bot_info = await bot.get_me()
                    bot_healthy = bot_info is not None
                else:
                    bot_healthy = False
            except Exception:
                bot_healthy = False
            status = {
                "database": "healthy" if db_healthy else "unhealthy",
                "bot": "healthy" if bot_healthy else "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
            }
            if db_healthy and bot_healthy:
                logger.info("Health check passed: all systems healthy")
                return "healthy"
            else:
                logger.warning(f"Health check issues detected: {status}")
                return f"issues-db-{status['database']}-bot-{status['bot']}"
        except Exception as e:
            ErrorHandler.log_error(e, context)
            return "health-check-failed"
        finally:
            await cleanup_resources()

    return asyncio.run(_run())


@enhanced_retry_task
def cleanup_metrics_task():
    """Periodic cleanup task for metrics and monitoring data"""

    async def _run() -> str:
        context = ErrorContext().add("task", "cleanup_metrics_task")
        try:
            from apps.shared.monitoring import metrics

            logger.info("Starting metrics cleanup task")
            metrics.cleanup_old_metrics()
            summary = metrics.get_summary()
            logger.info(
                f"Metrics cleanup completed. Total metrics: {summary.get('metrics_count', 0)}"
            )
            return "cleanup-completed"
        except Exception as e:
            ErrorHandler.log_error(e, context)
            return "cleanup-failed"
        finally:
            await cleanup_resources()

    return asyncio.run(_run())


@enhanced_retry_task
def maintenance_cleanup():
    """Periodic maintenance: requeue stuck 'sending' posts and cleanup old posts."""

    async def _run():
        bot = get_container().bot_client()
        try:
            scheduler_repo = get_container().schedule_repo()
            # TODO: Implement requeue_stuck_sending_posts and cleanup_old_posts using clean architecture - PLACEHOLDER
            # Using safe placeholder implementation that logs the maintenance request
            logger.info("maintenance_cleanup called - using safe placeholder implementation")
            requeued = 0  # Safe placeholder - no actual requeueing performed
            cleaned = 0  # Safe placeholder - no actual cleanup performed

            logger.info(
                f"Maintenance cleanup completed (placeholder): {requeued} requeued, {cleaned} cleaned"
            )
        except Exception as e:
            logger.exception("maintenance_cleanup failed", exc_info=e)
        finally:
            # Cleanup is handled by DI container lifecycle
            await cleanup_resources()

    asyncio.run(_run())
    return "ok"


@enhanced_retry_task
def update_prometheus_metrics():
    """Periodic task to update system metrics"""

    async def _run() -> str:
        context = ErrorContext().add("task", "update_prometheus_metrics")
        try:
            from apps.di import get_system_metrics_service

            logger.info("Collecting system metrics")
            system_metrics_service = get_system_metrics_service()
            if system_metrics_service:
                await system_metrics_service.collect_and_update_system_metrics()
            logger.info("System metrics collection completed")
            return "metrics-updated"
        except Exception as e:
            ErrorHandler.log_error(e, context)
            return "metrics-failed"
        finally:
            await cleanup_resources()

    return asyncio.run(_run())
