import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

from bot.celery_app import celery_app, resilient_task
from bot.container import container
from bot.services.analytics_service import AnalyticsService
from bot.services.scheduler_service import SchedulerService
from bot.services.prometheus_service import prometheus_service, prometheus_timer
from bot.utils.error_handler import ErrorHandler, ErrorContext
from bot.utils.monitoring import metrics

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


@resilient_task(name="bot.tasks.send_post_task", bind=True)
def send_post_task(self, scheduler_id: int):  # type: ignore[override]
    async def _run():
        context = ErrorContext().add("task", "send_post_task").add("scheduler_id", scheduler_id)
        
        try:
            # Initialize bot and repository
            container.bot()
            scheduler_repository = container.scheduler_repository()
            
            # Get scheduler data
            scheduler = await scheduler_repository.get_scheduler_by_id(scheduler_id)
            if not scheduler:
                logger.warning(f"Scheduler {scheduler_id} not found")
                return "scheduler-not-found"

            # TODO: Implement business logic based on scheduler data
            # Example structure:
            # if not scheduler.is_due:
            #     return "not-due"
            # 
            # subscription_repository = container.subscription_repository()
            # subscriptions = await subscription_repository.get_active_for_user(scheduler.user_id)
            # 
            # for channel in subscriptions:
            #     await bot.send_post(channel.channel_id, scheduler.post_id)
            
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


@resilient_task(name="bot.tasks.remove_expired_schedulers", bind=True)
def remove_expired_schedulers(self):  # type: ignore[override]
    async def _run():
        context = ErrorContext().add("task", "remove_expired_schedulers")
        
        try:
            container.bot()
            repo = container.scheduler_repository()
            
            # Remove expired schedulers
            removed_count = await repo.remove_expired(datetime.utcnow())
            logger.info(f"Removed {removed_count} expired schedulers")
            
            return f"removed-{removed_count}"
            
        except Exception as e:
            ErrorHandler.log_error(e, context)
            raise
        finally:
            await cleanup_resources()

    return asyncio.run(_run())


@resilient_task(name="bot.tasks.send_scheduled_message", bind=True)
def send_scheduled_message(self):  # type: ignore[override]
    async def _run() -> str:
        context = ErrorContext().add("task", "send_scheduled_message")
        stats = {"processed": 0, "sent": 0, "errors": 0}
        
        try:
            # Initialize services
            container.bot()
            scheduler_service = container.scheduler_service()
            scheduler_repo = container.scheduler_repository()

            # Atomically claim a batch of posts to avoid duplicate sends
            due_posts = await scheduler_repo.claim_due_posts(limit=50)
            if not due_posts:
                logger.info("No due posts to send")
                return "no-due-posts"

            logger.info(f"Processing {len(due_posts)} due posts")
            stats["processed"] = len(due_posts)

            # Process each post
            for post in due_posts:
                try:
                    result = await scheduler_service.send_post_to_channel(post)
                    
                    if result.get("success"):
                        stats["sent"] += 1
                        logger.debug(f"Successfully sent post {post.get('id')}")
                    else:
                        stats["errors"] += 1
                        logger.warning(f"Failed to send post {post.get('id')}: {result.get('error')}")
                        
                except Exception as e:
                    stats["errors"] += 1
                    post_context = context.add("post_id", post.get("id"))
                    ErrorHandler.log_error(e, post_context)

            logger.info(
                f"Scheduled message task completed. "
                f"Processed: {stats['processed']}, Sent: {stats['sent']}, Errors: {stats['errors']}"
            )
            
            return f"processed-{stats['processed']}-sent-{stats['sent']}-errors-{stats['errors']}"
            
        except Exception as e:
            ErrorHandler.log_error(e, context)
            raise
        finally:
            await cleanup_resources()

    return asyncio.run(_run())


@resilient_task(name="bot.tasks.update_post_views_task", bind=True)
@prometheus_timer("celery_task")
def update_post_views_task(self):  # type: ignore[override]
    async def _run() -> str:
        context = ErrorContext().add("task", "update_post_views_task")
        
        try:
            # Ensure bot + repos/services are initialized
            container.bot()
            analytics_service = container.analytics_service()
            
            logger.info("Starting post views update task")
            
            # Update all post views
            stats = await analytics_service.update_all_post_views()
            
            result = (
                f"processed-{stats.get('processed', 0)}-"
                f"updated-{stats.get('updated', 0)}-"
                f"errors-{stats.get('errors', 0)}-"
                f"skipped-{stats.get('skipped', 0)}"
            )
            
            logger.info(f"Post views update completed: {result}")
            return result
            
        except Exception as e:
            ErrorHandler.log_error(e, context)
            raise
        finally:
            await cleanup_resources()

    return asyncio.run(_run())


@resilient_task(name="bot.tasks.health_check_task", bind=True)
def health_check_task(self):  # type: ignore[override]
    """Periodic health check task for monitoring system status"""
    async def _run() -> str:
        context = ErrorContext().add("task", "health_check_task")
        
        try:
            from bot.database.db import is_db_healthy
            
            # Check database health
            db_healthy = await is_db_healthy()
            
            # Check bot health (basic check)
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


@resilient_task(name="bot.tasks.cleanup_metrics_task", bind=True)
def cleanup_metrics_task(self):  # type: ignore[override]
    """Periodic cleanup task for metrics and monitoring data"""
    async def _run() -> str:
        context = ErrorContext().add("task", "cleanup_metrics_task")
        
        try:
            from bot.utils.monitoring import metrics
            
            logger.info("Starting metrics cleanup task")
            
            # Cleanup old metrics
            metrics.cleanup_old_metrics()
            
            # Get current metrics summary
            summary = metrics.get_summary()
            
            logger.info(
                f"Metrics cleanup completed. "
                f"Total metrics: {summary.get('metrics_count', 0)}"
            )
            
            return "cleanup-completed"
            
        except Exception as e:
            ErrorHandler.log_error(e, context)
            return "cleanup-failed"
        finally:
            await cleanup_resources()

    return asyncio.run(_run())


@resilient_task(name="bot.tasks.maintenance_cleanup", bind=True)
def maintenance_cleanup(self):  # type: ignore[override]
    """Periodic maintenance: requeue stuck 'sending' posts and cleanup old posts."""
    async def _run():
        container.bot()
        try:
            scheduler_repo = container.scheduler_repository()
            
            # Requeue posts stuck in 'sending' status for >15 minutes
            requeued = await scheduler_repo.requeue_stuck_sending_posts(max_age_minutes=15)
            if requeued > 0:
                logger.info("Requeued %d stuck sending posts", requeued)
            
            # Cleanup posts older than 30 days
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
            except Exception:  # pragma: no cover
                pass

    asyncio.run(_run())
    return "ok"
# Prometheus metrics task - append to tasks.py

@resilient_task(name="bot.tasks.update_prometheus_metrics", bind=True)
def update_prometheus_metrics(self):  # type: ignore[override]
    """Periodic task to update Prometheus metrics"""
    async def _run() -> str:
        context = ErrorContext().add("task", "update_prometheus_metrics")
        
        try:
            from bot.services.prometheus_service import collect_system_metrics
            
            logger.info("Collecting Prometheus metrics")
            
            # Collect system and application metrics
            await collect_system_metrics()
            
            logger.info("Prometheus metrics collection completed")
            
            return "metrics-updated"
            
        except Exception as e:
            ErrorHandler.log_error(e, context)
            return "metrics-failed"
        finally:
            await cleanup_resources()

    return asyncio.run(_run())
