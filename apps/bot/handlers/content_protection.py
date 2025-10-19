"""
Bot Handlers for Content Protection & Premium Features

Telegram bot handlers for content protection features including:
- Watermarking (text and video)
- Theft detection
- Content protection status management
- Premium emoji features

Architecture:
- Uses core services from core/services/bot/content/ (Clean Architecture)
- Provides aiogram handler implementations
- Integrates with DI container for service resolution

Migration Note:
- Phase 2.3 implementation (2024)
- Refactored to use clean architecture services (2025)
- See: docs/CONTENT_PROTECTION_LEGACY_ANALYSIS.md for historical context
"""

from pathlib import Path
from typing import cast

# Import Bot from aiogram main module (not from .types)
from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    User,
)

from apps.bot.models.content_protection import PremiumFeatureLimits, UserTier

# TODO Phase 3.5: PremiumEmojiService should be moved to dedicated premium features module
# Currently in apps/bot.services/premium_emoji_service.py as temporary location
from apps.bot.services.premium_emoji_service import PremiumEmojiService

router = Router()
premium_emoji_service = PremiumEmojiService()


# Type guard helpers for aiogram handlers
def validate_callback_state(callback: CallbackQuery) -> bool:
    """Validate callback has required attributes (message, bot, from_user)"""
    from aiogram.types import Message as MessageType

    return bool(
        callback.message
        and isinstance(callback.message, MessageType)
        and callback.bot
        and callback.from_user
    )


def validate_message_state(message: Message) -> bool:
    """Validate message has required attributes (bot, from_user)"""
    return bool(message.bot and message.from_user)


# FSM States for content protection workflows
class ContentProtectionStates(StatesGroup):
    waiting_for_watermark_image = State()
    waiting_for_watermark_text = State()
    waiting_for_watermark_config = State()
    waiting_for_custom_emoji_text = State()
    waiting_for_theft_check_content = State()


@router.message(Command("protect"))
async def cmd_protect_content(message: Message, state: FSMContext):
    """Main content protection command"""

    # Guard clause: Ensure user exists (required by Telegram API in message handlers)
    if not message.from_user:
        return

    user_tier = await _get_user_subscription_tier(message.from_user.id)
    limits = PremiumFeatureLimits.get_limits_for_tier(user_tier)

    # Create protection menu based on user tier
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    # Image watermarking (available for all tiers)
    keyboard.inline_keyboard.append(
        [
            InlineKeyboardButton(
                text="🖼️ Add Image Watermark", callback_data="protect_image_watermark"
            )
        ]
    )

    # Video watermarking (premium only)
    if user_tier != UserTier.FREE:
        keyboard.inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text="🎥 Add Video Watermark", callback_data="protect_video_watermark"
                )
            ]
        )

    # Custom emojis (premium only)
    if user_tier != UserTier.FREE:
        keyboard.inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text="🎭 Format with Custom Emojis", callback_data="protect_custom_emoji"
                )
            ]
        )

    # Content theft detection
    keyboard.inline_keyboard.append(
        [InlineKeyboardButton(text="🔍 Check Content Theft", callback_data="protect_theft_check")]
    )

    # Usage statistics
    keyboard.inline_keyboard.append(
        [InlineKeyboardButton(text="📊 Usage Statistics", callback_data="protect_usage_stats")]
    )

    # Upgrade option for free users
    if user_tier == UserTier.FREE:
        keyboard.inline_keyboard.append(
            [InlineKeyboardButton(text="⭐ Upgrade to Premium", callback_data="upgrade_premium")]
        )

    protection_text = f"""
🛡️ **Content Protection & Premium Features**

**Your Tier:** {user_tier.value.title()}
**Monthly Limits:**
• Image Watermarks: {limits.watermarks_per_month or '∞'}
• Video Watermarks: {'✅' if user_tier != UserTier.FREE else '❌ Premium Only'}
• Custom Emojis: {limits.custom_emojis_per_month or '∞'}
• Theft Scans: {limits.theft_scans_per_month or '∞'}
• Max File Size: {limits.max_file_size_mb}MB

Choose a protection feature below:
"""

    await message.answer(protection_text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data == "protect_image_watermark")
async def handle_image_watermark_start(callback: CallbackQuery, state: FSMContext):
    """Start image watermarking process"""

    # Guard clauses for type safety
    if not callback.from_user or not callback.message:
        await callback.answer("❌ Invalid callback state")
        return

    # Type narrowing: cast after validation for Pylance
    assert callback.message is not None
    assert callback.bot is not None
    assert callback.from_user is not None
    msg = cast(Message, callback.message)
    bot = cast(Bot, callback.bot)

    user_tier = await _get_user_subscription_tier(callback.from_user.id)

    # Check usage limits
    if not await _check_feature_usage_limit("watermarks", callback.from_user.id, user_tier):
        await callback.answer("Monthly watermark limit reached! Upgrade for more.", show_alert=True)
        return

    await msg.edit_text(
        "🖼️ **Image Watermarking**\n\n"
        "Please send me an image file that you want to watermark.\n"
        "Supported formats: JPG, PNG, WebP",
        parse_mode="Markdown",
    )

    await state.set_state(ContentProtectionStates.waiting_for_watermark_image)
    await callback.answer()


@router.message(ContentProtectionStates.waiting_for_watermark_image)
async def handle_watermark_image_upload(message: Message, state: FSMContext):
    """Process uploaded image for watermarking"""

    # Guard clauses for type safety
    if not message.from_user or not message.bot:
        await message.answer("❌ Invalid message state") if message else None
        return

    if not message.photo and not message.document:
        await message.answer("❌ Please send an image file.")
        return

    user_tier = await _get_user_subscription_tier(message.from_user.id)
    limits = PremiumFeatureLimits.get_limits_for_tier(user_tier)

    # Get file info
    file_size: int | None = None
    if message.photo:
        file_info = await message.bot.get_file(message.photo[-1].file_id)
        file_size = message.photo[-1].file_size
    else:
        # Type guard for document
        if not message.document or not message.document.mime_type:
            await message.answer("❌ Invalid document.")
            return
        if not message.document.mime_type.startswith("image/"):
            await message.answer("❌ Please send an image file.")
            return
        if not message.document.file_id or not message.document.file_size:
            await message.answer("❌ Invalid file data.")
            return
        file_info = await message.bot.get_file(message.document.file_id)
        file_size = message.document.file_size

    # Check file size limit (after guard, file_size is guaranteed to be int)
    if file_size and file_size > limits.max_file_size_mb * 1024 * 1024:
        await message.answer(
            f"❌ File too large! Maximum size for {user_tier.value} tier: {limits.max_file_size_mb}MB"
        )
        return

    # Store file info in state
    await state.update_data(
        file_id=file_info.file_id, file_path=file_info.file_path, file_size=file_size
    )

    # Ask for watermark text
    watermark_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💧 Use Default Watermark", callback_data="watermark_default"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✏️ Custom Watermark Text", callback_data="watermark_custom"
                )
            ],
            [InlineKeyboardButton(text="❌ Cancel", callback_data="watermark_cancel")],
        ]
    )

    await message.answer(
        "💧 **Watermark Configuration**\n\n" "Choose watermark option:",
        reply_markup=watermark_keyboard,
        parse_mode="Markdown",
    )

    await state.set_state(ContentProtectionStates.waiting_for_watermark_config)


@router.callback_query(
    F.data == "watermark_default", ContentProtectionStates.waiting_for_watermark_config
)
async def handle_default_watermark(callback: CallbackQuery, state: FSMContext):
    """Apply default watermark"""

    # Guard clauses for type safety
    if not callback.message or not callback.bot:
        await callback.answer("❌ Invalid callback state")
        return

    # Type narrowing: cast after validation
    assert callback.message is not None
    assert callback.bot is not None
    assert callback.from_user is not None
    msg = cast(Message, callback.message)
    bot = cast(Bot, callback.bot)

    await msg.edit_text("🔄 **Processing watermark...**\nThis may take a moment.")

    try:
        state_data = await state.get_data()

        # Download file
        file = await bot.download_file(state_data["file_path"])
        assert file is not None

        # Create temporary file
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
            tmp_file.write(file.read())
            tmp_path = Path(tmp_file.name)

        # Get watermark service from DI
        from apps.di import get_container
        from core.services.bot.content.models import (
            WatermarkConfig,
            WatermarkPosition,
        )

        container = get_container()
        watermark_service = container.bot.watermark_service()

        # Create default watermark config
        bot_info = await bot.get_me()
        watermark_config = WatermarkConfig(
            text=f"@{bot_info.username or 'AnalyticBot'}",
            position=WatermarkPosition.BOTTOM_RIGHT,
            opacity=0.7,
            font_size=24,
            color="white",
            shadow=True,
        )

        # Apply watermark
        result = await watermark_service.add_watermark(str(tmp_path), watermark_config)

        if not result.success:
            await msg.edit_text(f"❌ **Watermarking failed:**\n{result.error}")
            return

        watermarked_path = Path(result.output_path)

        # Send watermarked image back
        with open(watermarked_path, "rb") as watermarked_file:
            watermarked_input = BufferedInputFile(
                watermarked_file.read(), filename=f"watermarked_{tmp_path.stem}.jpg"
            )

            await callback.message.answer_photo(
                watermarked_input,
                caption="✅ **Watermark Applied Successfully!**\n\n"
                "Your image is now protected with a watermark.",
                parse_mode="Markdown",
            )

        # Update usage tracking
        await _increment_feature_usage("watermarks", callback.from_user.id)

        # Cleanup
        tmp_path.unlink(missing_ok=True)
        watermarked_path.unlink(missing_ok=True)

    except Exception as e:
        await msg.edit_text(f"❌ **Watermarking failed:**\n{str(e)}")

    finally:
        await state.clear()
        await callback.answer()


@router.callback_query(
    F.data == "watermark_custom", ContentProtectionStates.waiting_for_watermark_config
)
async def handle_custom_watermark_text(callback: CallbackQuery, state: FSMContext):
    """Request custom watermark text"""

    if not validate_callback_state(callback):
        await callback.answer("❌ Invalid callback state")
        return

    # Type narrowing
    msg = cast(Message, callback.message)

    await msg.edit_text(
        "✏️ **Custom Watermark**\n\n"
        "Enter your custom watermark text:\n"
        "(Keep it short for best results)"
    )

    await state.set_state(ContentProtectionStates.waiting_for_watermark_text)
    await callback.answer()


@router.message(ContentProtectionStates.waiting_for_watermark_text)
async def handle_custom_watermark_apply(message: Message, state: FSMContext):
    """Apply custom watermark text"""

    if not validate_message_state(message):
        await message.answer("❌ Invalid message state") if message else None
        return

    # Type narrowing
    bot = cast(Bot, message.bot)
    user = cast(User, message.from_user)

    if not message.text:
        await message.answer("❌ Please send text for watermark")
        return

    watermark_text = message.text.strip()
    if len(watermark_text) > 50:
        await message.answer("❌ Watermark text too long! Please keep it under 50 characters.")
        return

    await message.answer("🔄 **Processing custom watermark...**\nThis may take a moment.")

    try:
        state_data = await state.get_data()

        # Download file
        file = await bot.download_file(state_data["file_path"])
        assert file is not None, "Failed to download file"

        # Create temporary file
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
            tmp_file.write(file.read())
            tmp_path = Path(tmp_file.name)

        # Get watermark service from DI
        from apps.di import get_container
        from core.services.bot.content.models import (
            WatermarkConfig,
            WatermarkPosition,
        )

        container = get_container()
        watermark_service = container.bot.watermark_service()

        # Create custom watermark config
        watermark_config = WatermarkConfig(
            text=watermark_text,
            position=WatermarkPosition.BOTTOM_RIGHT,
            opacity=0.8,
            font_size=20,
            color="white",
            shadow=True,
        )

        # Apply watermark
        result = await watermark_service.add_watermark(str(tmp_path), watermark_config)

        if not result.success:
            await message.answer(f"❌ **Watermarking failed:**\n{result.error}")
            return

        watermarked_path = Path(result.output_path)

        # Send watermarked image back
        with open(watermarked_path, "rb") as watermarked_file:
            watermarked_input = BufferedInputFile(
                watermarked_file.read(), filename=f"watermarked_{tmp_path.stem}.jpg"
            )

            await message.answer_photo(
                watermarked_input,
                caption=f"✅ **Custom Watermark Applied!**\n\n"
                f"Watermark: `{watermark_text}`\n"
                f"Your image is now protected.",
                parse_mode="Markdown",
            )

        # Update usage tracking
        await _increment_feature_usage("watermarks", user.id)

        # Cleanup
        tmp_path.unlink(missing_ok=True)
        watermarked_path.unlink(missing_ok=True)

    except Exception as e:
        await message.answer(f"❌ **Watermarking failed:**\n{str(e)}")

    finally:
        await state.clear()


@router.callback_query(F.data == "protect_custom_emoji")
async def handle_custom_emoji_start(callback: CallbackQuery, state: FSMContext):
    """Start custom emoji formatting"""

    if not validate_callback_state(callback):
        await callback.answer("❌ Invalid callback state")
        return

    # Type narrowing
    msg = cast(Message, callback.message)

    user_tier = await _get_user_subscription_tier(callback.from_user.id)

    if user_tier == UserTier.FREE:
        await callback.answer("Custom emojis require premium subscription!", show_alert=True)
        return

    if not await _check_feature_usage_limit("custom_emojis", callback.from_user.id, user_tier):
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

    user_tier = await _get_user_subscription_tier(user.id)

    try:
        # Format message with premium emojis
        formatted_text, entities = await premium_emoji_service.format_premium_message(
            message.text, user_tier.value, include_signature=True
        )

        await message.answer(
            f"✨ **Premium Formatted Message:**\n\n{formatted_text}", parse_mode="Markdown"
        )

        # Update usage tracking
        await _increment_feature_usage("custom_emojis", user.id)

    except Exception as e:
        await message.answer(f"❌ **Emoji formatting failed:**\n{str(e)}")

    finally:
        await state.clear()


@router.callback_query(F.data == "protect_theft_check")
async def handle_theft_check_start(callback: CallbackQuery, state: FSMContext):
    """Start content theft detection"""

    if not validate_callback_state(callback):
        await callback.answer("❌ Invalid callback state")
        return

    # Type narrowing
    msg = cast(Message, callback.message)

    user_tier = await _get_user_subscription_tier(callback.from_user.id)

    if not await _check_feature_usage_limit("theft_scans", callback.from_user.id, user_tier):
        await callback.answer("Monthly theft scan limit reached!", show_alert=True)
        return

    await msg.edit_text(
        "🔍 **Content Theft Detection**\n\n"
        "Send me the content you want to analyze for potential theft indicators.\n"
        "This can be text from posts, comments, or messages.",
        parse_mode="Markdown",
    )

    await state.set_state(ContentProtectionStates.waiting_for_theft_check_content)
    await callback.answer()


@router.message(ContentProtectionStates.waiting_for_theft_check_content)
async def handle_theft_check_analyze(message: Message, state: FSMContext):
    """Analyze content for theft indicators"""

    if not validate_message_state(message):
        await message.answer("❌ Invalid message state") if message else None
        return

    # Type narrowing
    user = cast(User, message.from_user)

    if not message.text:
        await message.answer("❌ Please send text content to analyze.")
        return

    await message.answer("🔄 **Analyzing content...**\nChecking for theft indicators.")

    try:
        # Get theft detector service from DI
        from apps.di import get_container
        from core.services.bot.content.models import RiskLevel

        container = get_container()
        theft_detector = container.bot.theft_detector_service()

        # Analyze content
        theft_analysis = await theft_detector.analyze_content(message.text)

        # Format results
        risk_emoji = {
            RiskLevel.HIGH: "🔴",
            RiskLevel.MEDIUM: "🟡",
            RiskLevel.LOW: "�",
        }[theft_analysis.risk_level]

        result_text = f"""
🔍 **Theft Detection Results**

{risk_emoji} **Risk Level:** {theft_analysis.risk_level.value.upper()}
📊 **Spam Score:** {theft_analysis.spam_score:.2f}/1.00
🔗 **Links Found:** {theft_analysis.link_count}

**Suspicious Patterns:**
"""

        if theft_analysis.suspicious_patterns:
            for pattern in theft_analysis.suspicious_patterns[:10]:  # Limit to 10
                result_text += f"• {pattern}\n"
        else:
            result_text += "• None detected\n"

        if theft_analysis.recommendations:
            result_text += "\n**Recommendations:**\n"
            for rec in theft_analysis.recommendations:
                result_text += f"• {rec}\n"

        await message.answer(result_text, parse_mode="Markdown")

        # Update usage tracking
        await _increment_feature_usage("theft_scans", user.id)

    except Exception as e:
        await message.answer(f"❌ **Analysis failed:**\n{str(e)}")

    finally:
        await state.clear()


@router.callback_query(F.data == "protect_usage_stats")
async def handle_usage_stats(callback: CallbackQuery):
    """Show user's feature usage statistics"""

    if not validate_callback_state(callback):
        await callback.answer("❌ Invalid callback state")
        return

    # Type narrowing
    msg = cast(Message, callback.message)

    user_tier = await _get_user_subscription_tier(callback.from_user.id)
    limits = PremiumFeatureLimits.get_limits_for_tier(user_tier)
    current_usage = await _get_current_usage(callback.from_user.id)

    # Calculate remaining usage
    def format_limit(used, limit):
        if limit is None:
            return f"{used}/∞"
        remaining = max(0, limit - used)
        return f"{used}/{limit} ({remaining} left)"

    usage_text = f"""
📊 **Usage Statistics - {user_tier.value.title()}**

**This Month:**
🖼️ **Image Watermarks:** {format_limit(current_usage['watermarks'], limits.watermarks_per_month)}
🎥 **Video Watermarks:** {format_limit(current_usage.get('video_watermarks', 0), limits.watermarks_per_month)}
🎭 **Custom Emojis:** {format_limit(current_usage['custom_emojis'], limits.custom_emojis_per_month)}
🔍 **Theft Scans:** {format_limit(current_usage['theft_scans'], limits.theft_scans_per_month)}

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


@router.callback_query(F.data.startswith("watermark_cancel"))
async def handle_cancel(callback: CallbackQuery, state: FSMContext):
    """Cancel current operation"""

    if not validate_callback_state(callback):
        await callback.answer("❌ Invalid callback state")
        return

    # Type narrowing
    msg = cast(Message, callback.message)

    await state.clear()
    await msg.edit_text("❌ **Operation cancelled.**")
    await callback.answer()


# Helper functions
async def _get_user_subscription_tier(user_id: int) -> UserTier:
    """Get user's subscription tier from payment system"""
    # TODO: Integrate with Phase 2.2 payment system
    # For now, return PRO for demo
    return UserTier.PRO


async def _check_feature_usage_limit(feature: str, user_id: int, user_tier: UserTier) -> bool:
    """Check if user has remaining feature usage"""
    limits = PremiumFeatureLimits.get_limits_for_tier(user_tier)
    current_usage = await _get_current_usage(user_id)

    feature_limit = getattr(limits, f"{feature}_per_month", None)
    if feature_limit is None:
        return True  # Unlimited

    return current_usage.get(feature, 0) < feature_limit


async def _increment_feature_usage(feature: str, user_id: int, count: int = 1):
    """Increment feature usage counter"""
    # TODO: Implement database update


async def _get_current_usage(user_id: int) -> dict[str, int]:
    """Get current month's feature usage"""
    # TODO: Implement database query
    return {"watermarks": 3, "custom_emojis": 8, "theft_scans": 1}  # Placeholder
