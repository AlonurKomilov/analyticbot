"""
Watermarking Handlers for Content Protection

Handles image watermarking workflows including:
- Protection menu
- Image upload
- Default watermark application
- Custom watermark text
"""

import logging
from pathlib import Path
from typing import cast

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    User,
)

from apps.bot.models.content_protection import PremiumFeatureLimits, UserTier

from .states import ContentProtectionStates
from .validation import validate_callback_state, validate_message_state

logger = logging.getLogger(__name__)
router = Router()


# Import tier service functions (will be refactored in Phase 2.8)
from apps.bot.handlers.content_protection.services.tier_service import (
    check_feature_usage_limit,
    get_user_subscription_tier,
    increment_feature_usage,
)


@router.message(Command("protect"))
async def cmd_protect_content(message: Message, state: FSMContext):
    """Main content protection command - displays protection menu"""

    # Guard clause: Ensure user exists (required by Telegram API in message handlers)
    if not message.from_user:
        return

    user_tier = await get_user_subscription_tier(message.from_user.id)
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

    user_tier = await get_user_subscription_tier(callback.from_user.id)

    # Check usage limits
    if not await check_feature_usage_limit("watermarks", callback.from_user.id, user_tier):
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

    user_tier = await get_user_subscription_tier(message.from_user.id)
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
        await increment_feature_usage("watermarks", callback.from_user.id)

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
        await increment_feature_usage("watermarks", user.id)

        # Cleanup
        tmp_path.unlink(missing_ok=True)
        watermarked_path.unlink(missing_ok=True)

    except Exception as e:
        await message.answer(f"❌ **Watermarking failed:**\n{str(e)}")

    finally:
        await state.clear()


@router.callback_query(F.data.startswith("watermark_cancel"))
async def handle_cancel(callback: CallbackQuery, state: FSMContext):
    """Cancel watermarking operation"""

    if not validate_callback_state(callback):
        await callback.answer("❌ Invalid callback state")
        return

    # Type narrowing
    msg = cast(Message, callback.message)

    await state.clear()
    await msg.edit_text("❌ **Operation cancelled.**")
    await callback.answer()
