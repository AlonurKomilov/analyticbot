"""
Simple bot handlers using core services
Framework-agnostic business logic with DI
"""

import logging
from datetime import datetime, timedelta

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from apps.bot.deps import bot_container

logger = logging.getLogger(__name__)

# Create router for schedule-related handlers
schedule_router = Router()


@schedule_router.message(Command("schedule"))
async def handle_schedule_command(message: Message):
    """
    Handle /schedule command
    Uses ScheduleService via dependency injection
    """
    try:
        # Get service via DI
        schedule_service = await bot_container.get_schedule_service()

        # Validate required objects
        if schedule_service is None:
            await message.answer("❌ Schedule service is not available")
            return
        if message.from_user is None:
            await message.answer("❌ User information is not available")
            return
        if message.text is None:
            await message.answer("❌ Message text is required")
            return

        # Parse simple command format: /schedule <title> | <content> | <minutes_from_now>
        args = message.text.split(" ", 1)
        if len(args) < 2:
            await message.answer(
                "Usage: /schedule <title> | <content> | <minutes_from_now>\n"
                "Example: /schedule My Post | Hello world! | 30"
            )
            return

        try:
            parts = args[1].split(" | ")
            if len(parts) != 3:
                raise ValueError("Invalid format")

            title, content, minutes_str = parts
            minutes = int(minutes_str)

            if minutes <= 0:
                raise ValueError("Minutes must be positive")

        except (ValueError, IndexError):
            await message.answer("Invalid format. Use: title | content | minutes_from_now")
            return

        # Calculate scheduled time
        scheduled_at = datetime.utcnow() + timedelta(minutes=minutes)

        # Create scheduled post using business service
        post = await schedule_service.create_scheduled_post(
            title=title,
            content=content,
            channel_id=str(message.chat.id),
            user_id=str(message.from_user.id),
            scheduled_at=scheduled_at,
        )

        await message.answer(
            f"✅ Post scheduled!\n"
            f"📝 Title: {post.title}\n"
            f"⏰ Scheduled for: {scheduled_at.strftime('%Y-%m-%d %H:%M:%S')} UTC\n"
            f"🆔 ID: {post.id}"
        )

        logger.info(f"User {message.from_user.id} scheduled post {post.id}")

    except ValueError as e:
        await message.answer(f"❌ Error: {str(e)}")
        user_id = message.from_user.id if message.from_user else "unknown"
        logger.warning(f"Schedule error for user {user_id}: {e}")
    except Exception as e:
        await message.answer("❌ An error occurred while scheduling the post")
        logger.error(f"Unexpected error in schedule handler: {e}", exc_info=True)


@schedule_router.message(Command("myposts"))
async def handle_my_posts_command(message: Message):
    """
    Handle /myposts command
    Shows user's scheduled posts using ScheduleService
    """
    try:
        schedule_service = await bot_container.get_schedule_service()

        # Validate required objects
        if schedule_service is None:
            await message.answer("❌ Schedule service is not available")
            return
        if message.from_user is None:
            await message.answer("❌ User information is not available")
            return

        # Get user's posts
        posts = await schedule_service.get_user_posts(user_id=str(message.from_user.id), limit=10)

        if not posts:
            await message.answer("📝 You have no scheduled posts")
            return

        # Format posts list
        response = "📝 Your scheduled posts:\n\n"
        for i, post in enumerate(posts, 1):
            status_emoji = {
                "draft": "📝",
                "scheduled": "⏰",
                "published": "✅",
                "failed": "❌",
                "cancelled": "🚫",
            }.get(post.status.value, "❓")

            response += (
                f"{i}. {status_emoji} {post.title}\n"
                f"   ⏰ {post.scheduled_at.strftime('%Y-%m-%d %H:%M')} UTC\n"
                f"   🆔 {post.id}\n\n"
            )

        await message.answer(response)

    except Exception as e:
        await message.answer("❌ An error occurred while fetching your posts")
        logger.error(f"Error in myposts handler: {e}", exc_info=True)


@schedule_router.message(Command("cancel"))
async def handle_cancel_command(message: Message):
    """
    Handle /cancel command
    Cancel a scheduled post by ID
    """
    try:
        # Validate required objects
        if message.text is None:
            await message.answer("❌ Message text is required")
            return
        if message.from_user is None:
            await message.answer("❌ User information is not available")
            return

        args = message.text.split(" ", 1)
        if len(args) < 2:
            await message.answer("Usage: /cancel <post_id>")
            return

        post_id_str = args[1].strip()

        try:
            from uuid import UUID

            post_id = UUID(post_id_str)
        except ValueError:
            await message.answer("❌ Invalid post ID format")
            return

        schedule_service = await bot_container.get_schedule_service()

        if schedule_service is None:
            await message.answer("❌ Schedule service is not available")
            return

        # Check if post exists and belongs to user
        post = await schedule_service.get_post(post_id)
        if not post:
            await message.answer("❌ Post not found")
            return

        if post.user_id != str(message.from_user.id):
            await message.answer("❌ You can only cancel your own posts")
            return

        # Cancel the post
        success = await schedule_service.cancel_post(post_id)

        if success:
            await message.answer(f"✅ Post '{post.title}' has been cancelled")
            logger.info(f"User {message.from_user.id} cancelled post {post_id}")
        else:
            await message.answer("❌ Failed to cancel post")

    except ValueError as e:
        await message.answer(f"❌ Error: {str(e)}")
    except Exception as e:
        await message.answer("❌ An error occurred while cancelling the post")
        logger.error(f"Error in cancel handler: {e}", exc_info=True)


@schedule_router.message(Command("stats"))
async def handle_stats_command(message: Message):
    """
    Handle /stats command
    Show delivery statistics using DeliveryService
    """
    try:
        delivery_service = await bot_container.get_delivery_service()

        if delivery_service is None:
            await message.answer("❌ Delivery service is not available")
            return

        # Get stats for this chat
        stats = await delivery_service.get_delivery_stats(channel_id=str(message.chat.id))

        total = stats.get("total_attempts", 0)
        success_rate = stats.get("success_rate", 0)

        response = (
            f"📊 Delivery Statistics\n\n"
            f"📤 Total Attempts: {total}\n"
            f"✅ Delivered: {stats.get('delivered', 0)}\n"
            f"⏳ Pending: {stats.get('pending', 0)}\n"
            f"🔄 Processing: {stats.get('processing', 0)}\n"
            f"❌ Failed: {stats.get('failed', 0)}\n"
            f"🔄 Retrying: {stats.get('retrying', 0)}\n\n"
            f"📈 Success Rate: {success_rate:.1f}%"
        )

        await message.answer(response)

    except Exception as e:
        await message.answer("❌ An error occurred while fetching statistics")
        logger.error(f"Error in stats handler: {e}", exc_info=True)
