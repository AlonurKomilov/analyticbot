"""
Premium Features Handlers for Content Protection

Handles premium emoji formatting and upgrade prompts.
"""

import logging
from typing import cast

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    User,
)

from apps.bot.models.content_protection import UserTier
from apps.bot.services.premium_emoji_service import PremiumEmojiService

from .states import ContentProtectionStates
from .validation import validate_callback_state, validate_message_state

logger = logging.getLogger(__name__)
router = Router()
premium_emoji_service = PremiumEmojiService()


# Import tier service functions (will be refactored in Phase 2.8)
from apps.bot.handlers.content_protection.services.tier_service import (
    check_feature_usage_limit,
    get_user_subscription_tier,
    increment_feature_usage,
)


@router.callback_query(F.data == "protect_custom_emoji")
async def handle_custom_emoji_start(callback: CallbackQuery, state: FSMContext):
    """Start custom emoji formatting"""

    if not validate_callback_state(callback):
        await callback.answer("❌ Invalid callback state")
        return

    # Type narrowing
    msg = cast(Message, callback.message)

    user_tier = await get_user_subscription_tier(callback.from_user.id)

    if user_tier == UserTier.FREE:
        await callback.answer("Custom emojis require premium subscription!", show_alert=True)
        return

    if not await check_feature_usage_limit("custom_emojis", callback.from_user.id, user_tier):
        await callback.answer("Monthly custom emoji limit reached!", show_alert=True)
        return

    # Show available emoji packs
    available_emojis = await premium_emoji_service.get_premium_emoji_pack(user_tier.value)
    emoji_preview = " ".join(available_emojis[:10]) if available_emojis else "🎭✨🎨"

    await msg.edit_text(
        f"🎭 **Custom Emoji Formatting**\n\n"
        f"**Your Tier:** {user_tier.value.title()}\n"
        f"**Available Emojis:** {len(available_emojis)}\n"
        f"**Preview:** {emoji_preview}...\n\n"
        f"Send me your message and I'll format it with premium emojis!",
        parse_mode="Markdown",
    )

    await state.set_state(ContentProtectionStates.waiting_for_custom_emoji_text)
    await callback.answer()


@router.message(ContentProtectionStates.waiting_for_custom_emoji_text)
async def handle_custom_emoji_format(message: Message, state: FSMContext):
    """Format message with custom emojis"""

    if not validate_message_state(message):
        await message.answer("❌ Invalid message state") if message else None
        return

    # Type narrowing
    user = cast(User, message.from_user)

    if not message.text:
        await message.answer("❌ Please send a text message to format.")
        return

    user_tier = await get_user_subscription_tier(user.id)

    try:
        # Format message with premium emojis
        formatted_text, entities = await premium_emoji_service.format_premium_message(
            message.text, user_tier.value, include_signature=True
        )

        await message.answer(
            f"✨ **Premium Formatted Message:**\n\n{formatted_text}",
            parse_mode="Markdown",
        )

        # Update usage tracking
        await increment_feature_usage("custom_emojis", user.id)

    except Exception as e:
        await message.answer(f"❌ **Emoji formatting failed:**\n{str(e)}")

    finally:
        await state.clear()


@router.callback_query(F.data == "upgrade_premium")
async def handle_upgrade_premium(callback: CallbackQuery):
    """Handle premium upgrade request"""

    if not validate_callback_state(callback):
        await callback.answer("❌ Invalid callback state")
        return

    # Type narrowing
    msg = cast(Message, callback.message)

    # Integration with Phase 2.2 Payment System
    upgrade_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 View Premium Plans", callback_data="payment_plans")],
            [
                InlineKeyboardButton(
                    text="🔙 Back to Protection", callback_data="back_to_protection"
                )
            ],
        ]
    )

    await msg.edit_text(
        "⭐ **Upgrade to Premium**\n\n"
        "Unlock advanced content protection features:\n"
        "• Unlimited watermarking\n"
        "• Video watermark support\n"
        "• Premium custom emojis\n"
        "• Advanced theft detection\n"
        "• Larger file uploads (100MB)\n"
        "• Priority support\n\n"
        "Choose an option below:",
        reply_markup=upgrade_keyboard,
        parse_mode="Markdown",
    )
    await callback.answer()
