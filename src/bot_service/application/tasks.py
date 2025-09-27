import asyncio
import logging
from datetime import datetime

from src.bot_service.container import container
from src.bot_service.services.prometheus_service import prometheus_timer
from src.bot_service.utils.error_handler import ErrorContext, ErrorHandler

from infra.celery import enhanced_retry_task

logger = logging.getLogger(__name__)


async def cleanup_resources():
    """Clean up resources after task completion"""
    try:
        db = container.db_session()
        if hasattr(db, "close"):
            res = db.close()
            if asyncio.iscoroutine(res):
                await res
    except Exception as e:
        logger.warning("Resource cleanup warning", exc_info=e)


@enhanced_retry_task(name="bot.tasks.send_post_task", bind=True)
def send_post_task(self, scheduler_id: int):
    async def _run():
        context = ErrorContext().add("task", "send_post_task").add("scheduler_id", scheduler_id)
        try:
            container.bot()
            scheduler_repository = container.scheduler_repository()
            scheduler = await scheduler_repository.get_scheduler_by_id(scheduler_id)
            if not scheduler:
                logger.warning(f"Scheduler {scheduler_id} not found")
                return "scheduler-not-found"
            logger.info(f"Processed scheduler task {scheduler_id}")
            return "completed"
        except asyncio.CancelledError:
            logger.info(f"Task {scheduler_id} was cancelled")
            raise
        except Exception as e:
            ErrorHandler.log_error(e, context)
            raise
        finally:
            await cleanup_resources()

    return asyncio.run(_run())


@enhanced_retry_task(name="bot.tasks.remove_expired_schedulers", bind=True)
def remove_expired_schedulers(self):
    async def _run():
        context = ErrorContext().add("task", "remove_expired_schedulers")
        try:
            container.bot()
            repo = container.scheduler_repository()
            removed_count = await repo.remove_expired(datetime.utcnow())
            logger.info(f"Removed {removed_count} expired schedulers")
            return f"removed-{removed_count}"
        except Exception as e:
            ErrorHandler.log_error(e, context)
            raise
        finally:
            await cleanup_resources()

    return asyncio.run(_run())


@enhanced_retry_task(name="bot.tasks.send_scheduled_message", bind=True)
def send_scheduled_message(self):
    async def _run() -> str:
        context = ErrorContext().add("task", "send_scheduled_message")
        stats = {"processed": 0, "sent": 0, "errors": 0}
        try:
            container.bot()
            scheduler_service = container.scheduler_service()
            scheduler_repo = container.scheduler_repository()
            due_posts = await scheduler_repo.claim_due_posts(limit=50)
            if not due_posts:
                logger.info("No due posts to send")
                return "no-due-posts"
            logger.info(f"Processing {len(due_posts)} due posts")
            stats["processed"] = len(due_posts)
            for post in due_posts:
                try:
                    result = await scheduler_service.send_post_to_channel(post)
                    if result.get("success"):
                        stats["sent"] += 1
                        logger.debug(f"Successfully sent post {post.get('id')}")
                    else:
                        stats["errors"] += 1
                        logger.warning(
                            f"Failed to send post {post.get('id')}: {result.get('error')}"
                        )
                except Exception as e:
                    stats["errors"] += 1
                    post_context = context.add("post_id", post.get("id"))
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


@enhanced_retry_task(name="bot.tasks.update_post_views_task", bind=True)
@prometheus_timer("celery_task")
def update_post_views_task(self):
    async def _run() -> str:
        context = ErrorContext().add("task", "update_post_views_task")
        try:
            container.bot()
            analytics_service = container.analytics_service()
            logger.info("Starting post views update task")
            stats = await analytics_service.update_all_post_views()
            result = f"processed-{stats.get('processed', 0)}-updated-{stats.get('updated', 0)}-errors-{stats.get('errors', 0)}-skipped-{stats.get('skipped', 0)}"
            logger.info(f"Post views update completed: {result}")
            return result
        except Exception as e:
            ErrorHandler.log_error(e, context)
            raise
        finally:
            await cleanup_resources()

    return asyncio.run(_run())


@enhanced_retry_task(name="bot.tasks.health_check_task", bind=True)
def health_check_task(self):
    """Periodic health check task for monitoring system status"""

    async def _run() -> str:
        context = ErrorContext().add("task", "health_check_task")
        try:
            from src.bot_service.database.db import is_db_healthy

            db_healthy = await is_db_healthy()
            try:
                bot = container.bot()
                bot_info = await bot.get_me()
                bot_healthy = bot_info is not None
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


@enhanced_retry_task(name="bot.tasks.cleanup_metrics_task", bind=True)
def cleanup_metrics_task(self):
    """Periodic cleanup task for metrics and monitoring data"""

    async def _run() -> str:
        context = ErrorContext().add("task", "cleanup_metrics_task")
        try:
            from src.bot_service.utils.monitoring import metrics

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


@enhanced_retry_task(name="bot.tasks.maintenance_cleanup", bind=True)
def maintenance_cleanup(self):
    """Periodic maintenance: requeue stuck 'sending' posts and cleanup old posts."""

    async def _run():
        container.bot()
        try:
            scheduler_repo = container.scheduler_repository()
            requeued = await scheduler_repo.requeue_stuck_sending_posts(max_age_minutes=15)
            if requeued > 0:
                logger.info("Requeued %d stuck sending posts", requeued)
            cleaned = await scheduler_repo.cleanup_old_posts(days_old=30)
            if cleaned > 0:
                logger.info("Cleaned up %d old posts", cleaned)
        except Exception as e:
            logger.exception("maintenance_cleanup failed", exc_info=e)
        finally:
            try:
                db = container.db_session()
                if hasattr(db, "close"):
                    res = db.close()
                    if asyncio.iscoroutine(res):
                        await res
            except Exception:
                pass

    asyncio.run(_run())
    return "ok"


@enhanced_retry_task(name="bot.tasks.update_prometheus_metrics", bind=True)
def update_prometheus_metrics(self):
    """Periodic task to update Prometheus metrics"""

    async def _run() -> str:
        context = ErrorContext().add("task", "update_prometheus_metrics")
        try:
            from src.bot_service.services.prometheus_service import (
                collect_system_metrics,
            )

            logger.info("Collecting Prometheus metrics")
            await collect_system_metrics()
            logger.info("Prometheus metrics collection completed")
            return "metrics-updated"
        except Exception as e:
            ErrorHandler.log_error(e, context)
            return "metrics-failed"
        finally:
            await cleanup_resources()

    return asyncio.run(_run())
