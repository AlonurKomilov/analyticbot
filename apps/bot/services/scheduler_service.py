import logging
from datetime import datetime
from typing import Any

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from pydantic import ValidationError

from apps.bot.domain.models import InlineButtonsPayload
from apps.bot.utils.error_handler import ErrorContext, ErrorHandler
from infra.db.repositories.analytics_repository import AsyncpgAnalyticsRepository
from infra.db.repositories.schedule_repository import AsyncpgScheduleRepository

logger = logging.getLogger(__name__)


class SchedulerService:
    """Enhanced scheduler service with improved error handling and monitoring"""

    def __init__(
        self,
        bot: Bot,
        scheduler_repo: AsyncpgScheduleRepository,
        analytics_repository: AsyncpgAnalyticsRepository,
    ):
        self.bot = bot
        self.scheduler_repo = scheduler_repo
        self.analytics_repo = analytics_repository

    def _build_reply_markup(self, raw: dict | None):
        """Build inline keyboard markup from raw button data with error handling"""
        if not raw:
            return None
        try:
            payload = InlineButtonsPayload(**raw)
        except ValidationError as e:
            context = ErrorContext().add("operation", "build_reply_markup").add("raw_data", raw)
            ErrorHandler.log_error(e, context, level=logging.WARNING)
            return None
        try:
            from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

            rows = []
            for row in payload.buttons:
                button_row = []
                for btn in row:
                    if btn.url and btn.callback_data:
                        logger.warning(
                            f"Button '{btn.text}' has both URL and callback_data, using URL only"
                        )
                    button = InlineKeyboardButton(
                        text=btn.text,
                        url=str(btn.url) if btn.url else None,
                        callback_data=(
                            btn.callback_data if btn.callback_data and (not btn.url) else None
                        ),
                    )
                    button_row.append(button)
                rows.append(button_row)
            return InlineKeyboardMarkup(inline_keyboard=rows) if rows else None
        except Exception as e:
            context = ErrorContext().add("operation", "create_keyboard_markup")
            ErrorHandler.log_error(e, context)
            return None

    async def send_post_to_channel(self, post_data: dict) -> dict[str, Any]:
        """
        Send scheduled post to channel with enhanced error handling, idempotency, and rate limiting.

        Returns:
            Dict with operation results and statistics
        """
        from uuid import uuid4

        from core.services.enhanced_delivery_service import EnhancedDeliveryService

        result = {
            "success": False,
            "message_id": None,
            "error": None,
            "post_id": post_data.get("id"),
        }

        context = (
            ErrorContext()
            .add("operation", "send_post_to_channel")
            .add("post_id", post_data.get("id"))
            .add("channel_id", post_data.get("channel_id"))
        )

        try:
            if not post_data.get("channel_id"):
                raise ValueError("Channel ID is required")
            if not post_data.get("post_text") and (not post_data.get("media_id")):
                raise ValueError("Either post text or media is required")

            # Create enhanced delivery service for reliability
            enhanced_delivery = EnhancedDeliveryService(
                delivery_repo=None,  # Not using the repo-based delivery tracking here
                schedule_repo=None,
            )

            # Create send function that encapsulates the actual sending logic
            async def _do_send(post_data: dict) -> dict:
                reply_markup = self._build_reply_markup(post_data.get("inline_buttons"))
                sent_message = None

                if post_data.get("media_id"):
                    media_type = post_data.get("media_type", "photo").lower()
                    if media_type == "photo":
                        sent_message = await self.bot.send_photo(
                            chat_id=post_data["channel_id"],
                            photo=post_data["media_id"],
                            caption=post_data.get("post_text", ""),
                            reply_markup=reply_markup,
                        )
                    elif media_type == "video":
                        sent_message = await self.bot.send_video(
                            chat_id=post_data["channel_id"],
                            video=post_data["media_id"],
                            caption=post_data.get("post_text", ""),
                            reply_markup=reply_markup,
                        )
                    elif media_type == "document":
                        sent_message = await self.bot.send_document(
                            chat_id=post_data["channel_id"],
                            document=post_data["media_id"],
                            caption=post_data.get("post_text", ""),
                            reply_markup=reply_markup,
                        )
                    else:
                        sent_message = await self.bot.send_photo(
                            chat_id=post_data["channel_id"],
                            photo=post_data["media_id"],
                            caption=post_data.get("post_text", ""),
                            reply_markup=reply_markup,
                        )
                else:
                    sent_message = await self.bot.send_message(
                        chat_id=post_data["channel_id"],
                        text=post_data["post_text"],
                        reply_markup=reply_markup,
                        disable_web_page_preview=True,
                    )

                if sent_message:
                    return {
                        "message_id": sent_message.message_id,
                        "chat_id": sent_message.chat.id,
                        "success": True,
                    }
                else:
                    raise Exception("No message returned from Telegram API")

            # Use enhanced delivery service with reliability guards
            delivery_result = await enhanced_delivery.send_with_reliability_guards(
                delivery_id=uuid4(),
                post_data=post_data,
                send_function=_do_send,
                idempotency_ttl=1800,  # 30 minutes
                max_rate_limit_wait=120.0,  # 2 minutes
            )

            # Process the delivery result
            if delivery_result.get("success"):
                sent_message_id = delivery_result.get("message_id")

                # Log analytics (with error handling)
                try:
                    await self.analytics_repo.log_sent_post(
                        scheduled_post_id=post_data["id"],
                        channel_id=post_data["channel_id"],
                        message_id=sent_message_id or 0,  # Provide default value
                    )
                except Exception as e:
                    analytics_context = context.add("sub_operation", "log_sent_post")
                    ErrorHandler.handle_database_error(e, analytics_context)

                # Update post status (with error handling)
                try:
                    await self.scheduler_repo.update_post_status(post_data["id"], "sent")
                except Exception as e:
                    status_context = context.add("sub_operation", "update_post_status")
                    ErrorHandler.handle_database_error(e, status_context)

                result.update(
                    {
                        "success": True,
                        "message_id": sent_message_id,
                        "duplicate": delivery_result.get("duplicate", False),
                        "rate_limited": delivery_result.get("rate_limited", False),
                        "idempotency_key": delivery_result.get("idempotency_key"),
                    }
                )

                logger.info(
                    f"Successfully sent post {post_data['id']} to channel {post_data['channel_id']} "
                    f"(message_id: {sent_message_id}, duplicate: {delivery_result.get('duplicate')}, "
                    f"rate_limited: {delivery_result.get('rate_limited')})"
                )
            else:
                error_msg = delivery_result.get("error", "Unknown delivery error")
                result["error"] = error_msg

                # Update post status to error
                try:
                    await self.scheduler_repo.update_post_status(post_data["id"], "error")
                except Exception as db_e:
                    status_context = context.add("sub_operation", "update_error_status")
                    ErrorHandler.handle_database_error(db_e, status_context)

                logger.error(f"Failed to send post {post_data['id']}: {error_msg}")

        except TelegramAPIError as e:
            error_id = ErrorHandler.handle_telegram_api_error(e, context)
            result["error"] = f"Telegram API error: {str(e)} (ID: {error_id})"
            try:
                await self.scheduler_repo.update_post_status(post_data["id"], "error")
            except Exception as db_e:
                status_context = context.add("sub_operation", "update_error_status")
                ErrorHandler.handle_database_error(db_e, status_context)
        except Exception as e:
            error_id = ErrorHandler.log_error(e, context)
            result["error"] = f"Unexpected error: {str(e)} (ID: {error_id})"
            try:
                await self.scheduler_repo.update_post_status(post_data["id"], "error")
            except Exception as db_e:
                status_context = context.add("sub_operation", "update_error_status")
                ErrorHandler.handle_database_error(db_e, status_context)

        return result

    async def schedule_post(
        self,
        user_id: int,
        channel_id: int,
        post_text: str | None,
        schedule_time: datetime,
        media_id: str | None = None,
        media_type: str | None = None,
        inline_buttons: dict | None = None,
    ) -> int | None:
        """
        Create a scheduled post with error handling.

        Returns:
            Post ID if successful, None if failed
        """
        context = (
            ErrorContext()
            .add("operation", "schedule_post")
            .add("user_id", user_id)
            .add("channel_id", channel_id)
        )
        try:
            if not post_text and (not media_id):
                raise ValueError("Either post_text or media_id must be provided")
            if schedule_time <= datetime.utcnow():
                raise ValueError("Schedule time must be in the future")
            if inline_buttons:
                try:
                    InlineButtonsPayload(**inline_buttons)
                except ValidationError as e:
                    raise ValueError(f"Invalid inline buttons format: {str(e)}")
            post_id = await self.scheduler_repo.create_scheduled_post(
                user_id=user_id,
                channel_id=channel_id,
                post_text=post_text or "",
                schedule_time=schedule_time,
                media_id=media_id,
                media_type=media_type,
                inline_buttons=inline_buttons,
            )
            logger.info(f"Successfully scheduled post {post_id} for {schedule_time}")
            return post_id
        except Exception as e:
            ErrorHandler.log_error(e, context)
            return None

    async def get_pending_posts(self, limit: int = 50) -> list:
        """Get pending posts that need to be sent"""
        try:
            return await self.scheduler_repo.get_pending_posts(limit=limit)
        except Exception as e:
            context = ErrorContext().add("operation", "get_pending_posts").add("limit", limit)
            ErrorHandler.handle_database_error(e, context)
            return []
