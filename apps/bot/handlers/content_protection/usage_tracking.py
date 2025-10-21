"""
Usage Tracking Handlers for Content Protection

Handles feature usage statistics display.
"""

import logging
from typing import cast

from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from apps.bot.models.content_protection import PremiumFeatureLimits, UserTier

from .services.tier_service import (
    get_current_usage,
    get_user_subscription_tier,
)
from .validation import validate_callback_state

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "protect_usage_stats")
async def handle_usage_stats(callback: CallbackQuery):
    """Show user's feature usage statistics"""

    if not validate_callback_state(callback):
        await callback.answer("❌ Invalid callback state")
        return

    # Type narrowing
    msg = cast(Message, callback.message)

    user_tier = await get_user_subscription_tier(callback.from_user.id)
    limits = PremiumFeatureLimits.get_limits_for_tier(user_tier)
    current_usage = await get_current_usage(callback.from_user.id)

    # Calculate remaining usage
    def format_limit(used, limit):
        if limit is None:
            return f"{used}/∞"
        remaining = max(0, limit - used)
        return f"{used}/{limit} ({remaining} left)"

    usage_text = f"""
📊 **Usage Statistics - {user_tier.value.title()}**

**This Month:**
🖼️ **Image Watermarks:** {format_limit(
        current_usage.get('watermarks', 0), limits.watermarks_per_month
    )}
🎥 **Video Watermarks:** {format_limit(
        current_usage.get('video_watermarks', 0), limits.watermarks_per_month
    )}
🎭 **Custom Emojis:** {format_limit(
        current_usage.get('custom_emojis', 0), limits.custom_emojis_per_month
    )}
🔍 **Theft Scans:** {format_limit(
        current_usage.get('theft_scans', 0), limits.theft_scans_per_month
    )}

**File Size Limit:** {limits.max_file_size_mb}MB
"""

    # Add upgrade suggestion for free users
    if user_tier == UserTier.FREE:
        usage_text += "\n⭐ **Upgrade to Premium** for unlimited features!"

    upgrade_keyboard = None
    if user_tier == UserTier.FREE:
        upgrade_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="⭐ Upgrade Now", callback_data="upgrade_premium")]
            ]
        )

    await msg.edit_text(usage_text, reply_markup=upgrade_keyboard, parse_mode="Markdown")
    await callback.answer()
