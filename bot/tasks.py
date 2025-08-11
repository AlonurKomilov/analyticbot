import asyncio
from datetime import datetime

from bot.celery_app import celery_app
from bot.container import container


@celery_app.task
async def send_post_task(scheduler_id: int):
    # Container'dan bot obyektini olamiz
    bot = container.bot()

    try:
        scheduler_repository = container.scheduler_repository()
        scheduler = await scheduler_repository.get_scheduler_by_id(scheduler_id)
        if not scheduler:
            return

        active_subscriptions = (
            await container.subscription_service().get_active_subscriptions()
        )
        await container.analytics_service().create_post(
            scheduler.post_id, len(active_subscriptions)
        )

        for channel in active_subscriptions:
            # Endi bu qator to'g'ri ishlaydi
            await bot.send_post(channel.channel_id, scheduler.post_id)

    except asyncio.CancelledError:
        pass
    finally:
        await container.db_session().close()


@celery_app.task
def remove_expired_schedulers():
    scheduler_repository = container.scheduler_repository()
    scheduler_repository.remove_expired(datetime.utcnow())