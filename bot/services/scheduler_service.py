import logging
from datetime import datetime

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

from bot.database.repositories import (  # AnalyticsRepository'ni import qilamiz
    AnalyticsRepository,
    SchedulerRepository,
)

logger = logging.getLogger(__name__)


class SchedulerService:
    # __init__ metodini o'zgartiramiz
    def __init__(
        self,
        bot: Bot,
        scheduler_repo: SchedulerRepository,
        analytics_repo: AnalyticsRepository,
    ):
        self.bot = bot
        self.scheduler_repo = scheduler_repo
        self.analytics_repo = analytics_repo

    async def send_post_to_channel(self, post_data: dict):
        """Rejalashtirilgan postni kanalga yuboradi va natijani log qiladi."""
        try:
            # Postni yuborish logikasi (sizning postingiz media yoki matn bo'lishiga qarab)
            if post_data.get("media_id"):
                # Media bilan yuborish
                sent_message = await self.bot.send_photo(
                    chat_id=post_data["channel_id"],
                    photo=post_data["media_id"],
                    caption=post_data["post_text"],
                    reply_markup=post_data.get("inline_buttons"),
                )
            else:
                # Oddiy matn yuborish
                sent_message = await self.bot.send_message(
                    chat_id=post_data["channel_id"],
                    text=post_data["post_text"],
                    reply_markup=post_data.get("inline_buttons"),
                    disable_web_page_preview=True,
                )

            # Post yuborilganini bazaga yozamiz
            await self.analytics_repo.log_sent_post(
                scheduled_post_id=post_data["id"],
                channel_id=sent_message.chat.id,
                message_id=sent_message.message_id,
            )

            await self.scheduler_repo.update_post_status(post_data["id"], "sent")
            logger.info(
                f"Successfully sent post {post_data['id']} to channel {post_data['channel_id']}"
            )

        except TelegramAPIError as e:
            await self.scheduler_repo.update_post_status(post_data["id"], "error")
            logger.error(f"Failed to send post {post_data['id']}: {e}", exc_info=True)

    async def schedule_post(
        self,
        user_id: int,
        channel_id: int,
        post_text: str | None,
        schedule_time: datetime,
        media_id: str | None = None,
        media_type: str | None = None,
        inline_buttons: dict | None = None,
    ) -> int:
        """Create a scheduled post via the repository."""
        return await self.scheduler_repo.create_scheduled_post(
            user_id=user_id,
            channel_id=channel_id,
            post_text=post_text or "",
            schedule_time=schedule_time,
            media_id=media_id,
            media_type=media_type,
            inline_buttons=inline_buttons,
        )
