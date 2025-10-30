#!/usr/bin/env python3
"""
Simple script to send pending scheduled posts
Professional solution: Run this via cron every minute
"""

import asyncio
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def send_pending_posts():
    """Send all pending scheduled posts that are due"""
    try:
        # Import here to ensure environment is loaded
        import os

        from dotenv import load_dotenv

        load_dotenv()

        # Get database connection
        import asyncpg

        db_url = os.getenv(
            "DATABASE_URL", "postgresql://analytic:change_me@localhost:10100/analytic_bot"
        )
        if db_url.startswith("postgresql+asyncpg://"):
            db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")

        pool = await asyncpg.create_pool(db_url, min_size=1, max_size=2)

        # Get pending posts that are due
        now = datetime.now(UTC)
        query = """
            SELECT id, user_id, channel_id, post_text, schedule_time
            FROM scheduled_posts
            WHERE status = 'pending'
            AND schedule_time <= $1
            ORDER BY schedule_time ASC
            LIMIT 10
        """

        posts = await pool.fetch(query, now)

        if not posts:
            logger.info("✅ No pending posts to send")
            await pool.close()
            return

        logger.info(f"📬 Found {len(posts)} pending posts to send")

        # Get bot token
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not bot_token:
            logger.error("❌ TELEGRAM_BOT_TOKEN not found in environment")
            await pool.close()
            return

        # Send each post
        import aiohttp

        async with aiohttp.ClientSession() as session:
            for post in posts:
                try:
                    # Send to Telegram
                    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                    data = {"chat_id": f"-{post['channel_id']}", "text": post["post_text"]}

                    async with session.post(url, json=data) as resp:
                        if resp.status == 200:
                            result = await resp.json()
                            if result.get("ok"):
                                # Update status to sent
                                await pool.execute(
                                    "UPDATE scheduled_posts SET status = 'sent' WHERE id = $1",
                                    post["id"],
                                )
                                logger.info(
                                    f"✅ Sent post {post['id']} to channel {post['channel_id']}"
                                )
                            else:
                                logger.error(
                                    f"❌ Telegram API error for post {post['id']}: {result}"
                                )
                                await pool.execute(
                                    "UPDATE scheduled_posts SET status = 'error' WHERE id = $1",
                                    post["id"],
                                )
                        else:
                            error_text = await resp.text()
                            logger.error(
                                f"❌ HTTP {resp.status} for post {post['id']}: {error_text}"
                            )
                            await pool.execute(
                                "UPDATE scheduled_posts SET status = 'error' WHERE id = $1",
                                post["id"],
                            )

                except Exception as e:
                    logger.error(f"❌ Error sending post {post['id']}: {e}")
                    await pool.execute(
                        "UPDATE scheduled_posts SET status = 'error' WHERE id = $1", post["id"]
                    )

        await pool.close()
        logger.info("🎉 Delivery run complete")

    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(send_pending_posts())
