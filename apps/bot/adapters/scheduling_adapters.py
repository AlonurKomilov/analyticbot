"""
Telegram Scheduling Adapters

Framework Integration: Telegram-specific implementations of scheduling ports
These adapters connect core scheduling services to the Telegram/Aiogram framework
"""

import logging
from typing import Any

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)


class AiogramMessageSender:
    """
    Aiogram implementation of MessageSenderPort

    Adapts Aiogram Bot API to the framework-agnostic MessageSenderPort interface
    """

    def __init__(self, bot: Bot):
        """
        Initialize with Aiogram bot instance

        Args:
            bot: Aiogram Bot instance for sending messages
        """
        self._bot = bot

    async def send_text_message(
        self,
        channel_id: int,
        text: str,
        reply_markup: Any | None = None,
    ) -> int:
        """
        Send a text message to a channel

        Args:
            channel_id: Telegram channel ID
            text: Message text
            reply_markup: Optional inline keyboard markup

        Returns:
            Sent message ID

        Raises:
            Exception: If sending fails
        """
        try:
            message = await self._bot.send_message(
                chat_id=channel_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode="HTML",
            )
            return message.message_id
        except Exception as e:
            logger.error(
                f"Failed to send text message to channel {channel_id}: {e}",
                exc_info=True,
            )
            raise

    async def send_media_message(
        self,
        channel_id: int,
        media_id: str,
        media_type: str,
        caption: str | None = None,
        reply_markup: Any | None = None,
    ) -> int:
        """
        Send a media message (photo, video, document) to a channel

        Args:
            channel_id: Telegram channel ID
            media_id: Telegram file ID for the media
            media_type: Type of media (photo, video, document)
            caption: Optional caption text
            reply_markup: Optional inline keyboard markup

        Returns:
            Sent message ID

        Raises:
            ValueError: If media_type is not supported
            Exception: If sending fails
        """
        try:
            # Dispatch to appropriate send method based on media type
            if media_type == "photo":
                message = await self._bot.send_photo(
                    chat_id=channel_id,
                    photo=media_id,
                    caption=caption,
                    reply_markup=reply_markup,
                    parse_mode="HTML",
                )
            elif media_type == "video":
                message = await self._bot.send_video(
                    chat_id=channel_id,
                    video=media_id,
                    caption=caption,
                    reply_markup=reply_markup,
                    parse_mode="HTML",
                )
            elif media_type == "document":
                message = await self._bot.send_document(
                    chat_id=channel_id,
                    document=media_id,
                    caption=caption,
                    reply_markup=reply_markup,
                    parse_mode="HTML",
                )
            elif media_type == "audio":
                message = await self._bot.send_audio(
                    chat_id=channel_id,
                    audio=media_id,
                    caption=caption,
                    reply_markup=reply_markup,
                    parse_mode="HTML",
                )
            elif media_type == "animation":
                message = await self._bot.send_animation(
                    chat_id=channel_id,
                    animation=media_id,
                    caption=caption,
                    reply_markup=reply_markup,
                    parse_mode="HTML",
                )
            else:
                raise ValueError(f"Unsupported media type: {media_type}")

            return message.message_id

        except Exception as e:
            logger.error(
                f"Failed to send {media_type} to channel {channel_id}: {e}",
                exc_info=True,
            )
            raise


class AiogramMarkupBuilder:
    """
    Aiogram implementation of MarkupBuilderPort

    Builds Aiogram InlineKeyboardMarkup from generic button definitions
    """

    def build_inline_keyboard(self, buttons_data: dict) -> InlineKeyboardMarkup:
        """
        Build inline keyboard markup from button data

        Expected format:
        {
            "inline_keyboard": [
                [{"text": "Button 1", "url": "https://example.com"}],
                [{"text": "Button 2", "callback_data": "action"}]
            ]
        }

        Args:
            buttons_data: Dictionary with inline_keyboard structure

        Returns:
            InlineKeyboardMarkup for Aiogram

        Raises:
            ValueError: If buttons_data format is invalid
        """
        if not buttons_data or "inline_keyboard" not in buttons_data:
            raise ValueError("buttons_data must contain 'inline_keyboard' key")

        try:
            keyboard = []
            for row in buttons_data["inline_keyboard"]:
                button_row = []
                for btn_data in row:
                    button = self._build_button(btn_data)
                    button_row.append(button)
                keyboard.append(button_row)

            return InlineKeyboardMarkup(inline_keyboard=keyboard)

        except Exception as e:
            logger.error(f"Failed to build inline keyboard: {e}", exc_info=True)
            raise ValueError(f"Invalid button data: {e}") from e

    def _build_button(self, btn_data: dict) -> InlineKeyboardButton:
        """
        Build a single inline keyboard button

        Args:
            btn_data: Button data with 'text' and action key (url/callback_data)

        Returns:
            InlineKeyboardButton

        Raises:
            ValueError: If button data is invalid
        """
        if "text" not in btn_data:
            raise ValueError("Button must have 'text' field")

        text = btn_data["text"]

        # Support different button types
        if "url" in btn_data:
            return InlineKeyboardButton(text=text, url=btn_data["url"])
        elif "callback_data" in btn_data:
            return InlineKeyboardButton(text=text, callback_data=btn_data["callback_data"])
        elif "switch_inline_query" in btn_data:
            return InlineKeyboardButton(
                text=text, switch_inline_query=btn_data["switch_inline_query"]
            )
        else:
            raise ValueError("Button must have one of: url, callback_data, switch_inline_query")
