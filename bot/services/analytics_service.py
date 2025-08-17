import asyncio
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

from bot.database.repositories.analytics_repository import AnalyticsRepository

# Logger sozlamalari
logger = logging.getLogger(__name__)


class AnalyticsService:
    def __init__(self, bot: Bot, analytics_repository: AnalyticsRepository):
        self.analytics_repository = analytics_repository
        self.bot = bot

    async def update_all_post_views(self):
        """
        Barcha kanallardagi barcha postlarning ko'rishlar sonini Telegramdan so'rab oladi
        va ma'lumotlar bazasini yangilaydi. Bu metod endi argument talab qilmaydi.
        """
        # Yuqorida yaratilgan yangi metod orqali postlarni olamiz
        posts = await self.analytics_repository.get_all_posts_to_track_views()

        if not posts:
            logger.info("Yangilash uchun postlar topilmadi.")
            return

        logger.info(f"{len(posts)} ta postning ko'rishlarini yangilash boshlandi.")

        for post in posts:
            try:
                # get_messages xabarlar ro'yxatini qaytaradi, bizga faqat bittasi kerak
                messages = await self.bot.get_messages(
                    chat_id=post["channel_id"], message_ids=[post["message_id"]]
                )

                # Agar xabar mavjud bo'lsa va unda ko'rishlar soni bo'lsa
                if messages and messages[0] and messages[0].views is not None:
                    # Ma'lumotlar bazasidagi ko'rishlar sonini yangilaymiz
                    await self.analytics_repository.update_post_views(
                        scheduled_post_id=post["id"], views=messages[0].views
                    )
                    logger.debug(
                        f"Post ID {post['id']} ning ko'rishlari {messages[0].views} ga yangilandi."
                    )

                # Telegram API'ga bosimni kamaytirish uchun kichik pauza
                await asyncio.sleep(0.5)

            except TelegramBadRequest as e:
                # Xabar o'chirilgan yoki bot kanaldan chiqarilgan bo'lishi mumkin
                logger.warning(
                    f"Xabar {post['message_id']} ni kanal {post['channel_id']} dan olishda xatolik: {e}"
                )
                continue
            except Exception as e:
                logger.error(
                    f"Post ID {post['id']} ni yangilashda kutilmagan xatolik: {e}",
                    exc_info=True,
                )
                continue

        logger.info("Barcha postlarning ko'rishlarini yangilash yakunlandi.")

    async def get_posts_ordered_by_views(self, channel_id: int):
        """
        Kanalning postlarini ko'rishlar soni bo'yicha saralab qaytaradi.
        (Bu metod o'zgarishsiz qoladi)
        """
        return await self.analytics_repository.get_posts_ordered_by_views(channel_id)

    async def create_views_chart(self, channel_id: int, limit: int = 10) -> bytes:
        """Generate a simple bar chart of top N posts by views.

        Returns PNG bytes or empty bytes on failure / no data.
        """
        try:
            posts = await self.analytics_repository.get_posts_ordered_by_views(
                channel_id
            )
            if not posts:
                return b""
            top = posts[:limit]
            ids = [str(p["id"]) for p in top]
            views = [int(p.get("views") or 0) for p in top]
            # Lazy import matplotlib (heavy) only when needed
            import matplotlib.pyplot as plt
            from io import BytesIO

            fig, ax = plt.subplots(figsize=(min(12, 1.2 * len(ids)), 4))
            ax.bar(ids, views, color="#4C72B0")
            ax.set_title("Top post views")
            ax.set_xlabel("Post ID")
            ax.set_ylabel("Views")
            for i, v in enumerate(views):
                ax.text(i, v, str(v), ha="center", va="bottom", fontsize=8)
            fig.tight_layout()
            buf = BytesIO()
            fig.savefig(buf, format="png")
            plt.close(fig)
            buf.seek(0)
            return buf.read()
        except Exception:
            return b""

    async def get_post_views(self, scheduled_post_id: int, _unused_user_id: int) -> int | None:
        """Return stored view count for a scheduled post.

        Note: handler passes (post_id, user_id). User ID is not currently
        used for authorization; could be extended later to verify ownership.
        """
        try:
            return await self.analytics_repository.get_post_views(scheduled_post_id)
        except Exception:
            return None

    async def get_total_users_count(self) -> int:
        """
        Retrieves the total number of users from the repository.
        """
        return await self.analytics_repository.get_total_users_count()

    async def get_total_channels_count(self) -> int:
        """
        Retrieves the total number of channels from the repository.
        """
        return await self.analytics_repository.get_total_channels_count()

    async def get_total_posts_count(self) -> int:
        """
        Retrieves the total number of posts from the repository.
        """
        return await self.analytics_repository.get_total_posts_count()
