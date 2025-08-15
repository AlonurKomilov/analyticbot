import asyncio
import logging
from datetime import datetime

from bot.celery_app import celery_app
from bot.container import container

logger = logging.getLogger(__name__)


@celery_app.task(name="bot.tasks.send_post_task")
def send_post_task(scheduler_id: int):
    async def _run():
        container.bot()
        try:
            scheduler_repository = container.scheduler_repository()
            scheduler = await scheduler_repository.get_scheduler_by_id(scheduler_id)
            if not scheduler:
                return

            # TODO: real business logic (example structure)
            # if not scheduler.is_due:
            #     return
            # subscriptions = await container.subscription_repository().get_active_for_user(scheduler.user_id)
            # for channel in subscriptions:
            #     await bot.send_post(channel.channel_id, scheduler.post_id)
        except asyncio.CancelledError:
            pass
        finally:
            try:
                db = container.db_session()
                if hasattr(db, "close"):
                    res = db.close()
                    if asyncio.iscoroutine(res):
                        await res
            except Exception as e:
                # don't crash worker on cleanup issues
                logger.exception("cleanup error in send_post_task", exc_info=e)

    asyncio.run(_run())


@celery_app.task(name="bot.tasks.remove_expired_schedulers")
def remove_expired_schedulers():
    scheduler_repository = container.scheduler_repository()
    scheduler_repository.remove_expired(datetime.utcnow())


@celery_app.task(name="bot.tasks.send_scheduled_message")
def send_scheduled_message():
    # TODO: implement dispatcher of due schedulers
    return "ok"


@celery_app.task(name="bot.tasks.update_post_views_task")
def update_post_views_task():
    # TODO: implement view updates
    return "ok"
