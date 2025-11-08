#!/usr/bin/env python3
"""
Send Scheduled Posts Worker
Checks for pending scheduled posts and sends them via Telegram Bot API
"""

import asyncio
import logging
import os
import sys

import asyncpg
import httpx

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://analytic:change_me@localhost:10100/analytic_bot"
)
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7603888301:AAHsmvb846iBbiGPzTda7wA1_RCimuowo3o")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"


async def get_pending_posts(conn):
    """Get all pending scheduled posts that are ready to be sent"""
    query = """
    SELECT id, user_id, channel_id, post_text, schedule_time
    FROM scheduled_posts
    WHERE status = 'pending'
      AND schedule_time <= NOW()
    ORDER BY schedule_time ASC
    LIMIT 10
    """
    return await conn.fetch(query)


async def send_message_to_telegram(channel_id: int, text: str) -> dict:
    """Send message to Telegram channel"""
    # Channel IDs in DB are stored as positive: 1002678877654
    # Telegram API needs them as negative: -1002678877654
    telegram_chat_id = -channel_id

    logger.info(f"Sending to Telegram chat_id: {telegram_chat_id}")

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            TELEGRAM_API_URL, json={"chat_id": telegram_chat_id, "text": text}
        )
        return response.json()


async def mark_post_as_sent(conn, post_id: int):
    """Mark post as sent in database"""
    query = """
    UPDATE scheduled_posts
    SET status = 'sent'
    WHERE id = $1
    """
    await conn.execute(query, post_id)


async def mark_post_as_error(conn, post_id: int, error_msg: str):
    """Mark post as error in database"""
    query = """
    UPDATE scheduled_posts
    SET status = 'error'
    WHERE id = $1
    """
    await conn.execute(query, post_id)
    logger.error(f"Post {post_id} failed: {error_msg}")


async def process_scheduled_posts():
    """Main worker function"""
    # Convert PostgreSQL URL format
    db_url = DATABASE_URL.replace("postgresql://", "").replace("postgresql+asyncpg://", "")

    try:
        # Connect to database
        conn = await asyncpg.connect(
            host="localhost",
            port=10100,
            user="analytic",
            password="change_me",
            database="analytic_bot",
        )

        logger.info("✅ Connected to database")

        # Get pending posts
        posts = await get_pending_posts(conn)

        if not posts:
            logger.info("📭 No pending posts to send")
            await conn.close()
            return

        logger.info(f"📬 Found {len(posts)} pending posts to send")

        # Process each post
        for post in posts:
            post_id = post["id"]
            channel_id = post["channel_id"]
            text = post["post_text"]
            post["schedule_time"]

            try:
                logger.info(f"📤 Sending post {post_id} to channel {channel_id}")

                # Send to Telegram
                result = await send_message_to_telegram(channel_id, text)

                if result.get("ok"):
                    message_id = result["result"]["message_id"]
                    logger.info(f"✅ Post {post_id} sent successfully! Message ID: {message_id}")
                    await mark_post_as_sent(conn, post_id)
                else:
                    error_desc = result.get("description", "Unknown error")
                    logger.error(f"❌ Telegram API error for post {post_id}: {error_desc}")
                    await mark_post_as_error(conn, post_id, error_desc)

            except Exception as e:
                logger.error(f"❌ Failed to send post {post_id}: {e}", exc_info=True)
                await mark_post_as_error(conn, post_id, str(e))

        await conn.close()
        logger.info("✅ Processing complete")

    except Exception as e:
        logger.error(f"❌ Worker error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    logger.info("🚀 Starting scheduled posts worker...")
    asyncio.run(process_scheduled_posts())
