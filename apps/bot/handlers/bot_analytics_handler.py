"""
Bot Analytics Microhandler - Minimal Working Version
=====================================================

Simplified microhandler containing core analytics functionality.
Part of Phase 2 microrouter implementation (analytics domain).

Domain Responsibilities:
- Main analytics command
- Basic analytics display
- Simple navigation

Extracted from: apps/bot/handlers/analytics_v2.py (714 lines → simplified analytics)
Architecture: Clean separation following Phase 1 microrouter pattern
"""

import logging
from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

logger = logging.getLogger(__name__)

# Create analytics microhandler router
router = Router()


# ================================
# ANALYTICS DOMAIN HELPER FUNCTIONS
# ================================

def _get_settings():
    """Get settings instance with proper error handling"""
    try:
        from config.settings import Settings
        return Settings
    except Exception:
        # Fallback mock settings
        class MockSettings:
            BOT_ANALYTICS_UI_ENABLED = True
            ANALYTICS_V2_BASE_URL = "http://localhost:8000"
            ANALYTICS_V2_TOKEN = None
        return MockSettings()


async def _safe_edit_message(callback: CallbackQuery, text: str, reply_markup=None) -> bool:
    """Safely edit callback message with type checking"""
    try:
        from aiogram.types import Message
        if (callback.message and 
            isinstance(callback.message, Message) and 
            hasattr(callback.message, 'edit_text')):
            await callback.message.edit_text(text, reply_markup=reply_markup)
            return True
        return False
    except Exception:
        return False


def _get_user_id(event) -> int | None:
    """Extract user ID from message or callback"""
    if hasattr(event, "from_user") and event.from_user:
        return event.from_user.id
    return None


def _create_back_keyboard() -> InlineKeyboardMarkup:
    """Create simple back navigation keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🔙 Back", callback_data="analytics_back")
    ]])


def _create_analytics_menu_keyboard() -> InlineKeyboardMarkup:
    """Create analytics menu keyboard"""
    buttons = [
        [InlineKeyboardButton(text="📊 Overview", callback_data="analytics_overview")],
        [InlineKeyboardButton(text="📈 Growth", callback_data="analytics_growth")],
        [InlineKeyboardButton(text="👁️ Reach", callback_data="analytics_reach")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="analytics_channels")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def _create_period_keyboard() -> InlineKeyboardMarkup:
    """Create period selection keyboard"""
    buttons = [
        [
            InlineKeyboardButton(text="7 days", callback_data="analytics_period:7"),
            InlineKeyboardButton(text="30 days", callback_data="analytics_period:30")
        ],
        [
            InlineKeyboardButton(text="90 days", callback_data="analytics_period:90"),
            InlineKeyboardButton(text="365 days", callback_data="analytics_period:365")
        ],
        [InlineKeyboardButton(text="🔙 Back", callback_data="analytics_channels")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def _create_channels_keyboard(channels: list) -> InlineKeyboardMarkup:
    """Create channel selection keyboard"""
    buttons = []
    for channel in channels[:10]:  # Limit to 10 channels
        channel_name = channel.get('name', f"Channel {channel.get('id', 'Unknown')}")
        channel_id = str(channel.get('id', ''))
        buttons.append([InlineKeyboardButton(
            text=f"📡 {channel_name}",
            callback_data=f"analytics_channel:{channel_id}"
        )])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# =======================================
# ANALYTICS DOMAIN COMMAND HANDLERS
# =======================================

@router.message(Command("analytics"))
async def analytics_command(message: Message, state: FSMContext) -> None:
    """Main analytics command - entry point to analytics domain"""
    try:
        settings = _get_settings()
        
        # Check if analytics UI is enabled
        if not getattr(settings, 'BOT_ANALYTICS_UI_ENABLED', True):
            await message.answer("📊 Analytics interface is currently disabled.")
            return

        user_id = _get_user_id(message)
        if not user_id:
            await message.answer("❌ Unable to identify user.")
            return

        # Mock channels for now (in production, would fetch from API)
        channels = [
            {"id": "demo_channel_1", "name": "Demo Channel 1"},
            {"id": "demo_channel_2", "name": "Demo Channel 2"},
        ]

        if not channels:
            await message.answer(
                "📊 **Analytics**\n\n"
                "❌ No channels found or analytics service unavailable.\n"
                "Please ensure you have connected channels and try again."
            )
            return

        # Store channels in state for later use
        await state.update_data(channels=channels)

        # Show channel selection
        keyboard = _create_channels_keyboard(channels)
        await message.answer(
            "📊 **Select Channel for Analytics**\n\n"
            "Choose a channel to view detailed analytics:",
            reply_markup=keyboard
        )

    except Exception as e:
        logger.error(f"Analytics command error: {e}")
        await message.answer("❌ An error occurred while loading analytics.")


@router.callback_query(lambda c: c.data and c.data.startswith("analytics_channel:"))
async def analytics_channel_callback(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle channel selection for analytics"""
    try:
        # Extract channel ID from callback data
        channel_id = callback.data.split(":", 1)[1] if ":" in callback.data else None
        if not channel_id:
            await callback.answer("❌ Invalid channel selection", show_alert=True)
            return

        # Store selected channel
        await state.update_data(selected_channel=channel_id)

        # Show period selection
        keyboard = _create_period_keyboard()
        text = (
            f"📊 **Analytics: Channel {channel_id}**\n\n"
            "📅 Select time period for analytics:"
        )
        
        success = await _safe_edit_message(callback, text, keyboard)
        if success:
            await callback.answer()
        else:
            await callback.message.answer(text, reply_markup=keyboard)
            await callback.answer()

    except Exception as e:
        logger.error(f"Channel selection error: {e}")
        await callback.answer("❌ Error selecting channel", show_alert=True)


@router.callback_query(lambda c: c.data and c.data.startswith("analytics_period:"))
async def analytics_period_callback(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle period selection for analytics"""
    try:
        # Extract period from callback data
        period = callback.data.split(":", 1)[1] if ":" in callback.data else "7"
        
        # Store selected period
        await state.update_data(selected_period=int(period))

        # Get state data
        state_data = await state.get_data()
        channel_id = state_data.get("selected_channel")
        
        if not channel_id:
            await callback.answer("❌ No channel selected", show_alert=True)
            return

        # Show analytics menu
        keyboard = _create_analytics_menu_keyboard()
        text = (
            f"📊 **Analytics Menu**\n\n"
            f"📡 Channel: {channel_id}\n"
            f"📅 Period: {period} days\n\n"
            "Select analytics type:"
        )
        
        success = await _safe_edit_message(callback, text, keyboard)
        if success:
            await callback.answer()
        else:
            await callback.message.answer(text, reply_markup=keyboard)
            await callback.answer()

    except Exception as e:
        logger.error(f"Period selection error: {e}")
        await callback.answer("❌ Error selecting period", show_alert=True)


@router.callback_query(lambda c: c.data == "analytics_overview")
async def analytics_overview_callback(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle overview analytics display"""
    try:
        # Get state data
        state_data = await state.get_data()
        channel_id = state_data.get("selected_channel")
        period = state_data.get("selected_period", 7)
        
        if not channel_id:
            await callback.answer("❌ Missing channel data", show_alert=True)
            return

        # Mock analytics data
        text = (
            "📊 **Channel Overview**\n\n"
            f"📡 Channel: {channel_id}\n"
            f"📅 Period: {period} days\n\n"
            "👥 **Subscribers:** 1.2K\n"
            "📈 **Growth:** +50 (+4.3%)\n\n"
            "📝 **Posts:** 15\n"
            "👁️ **Total Views:** 25.6K\n"
            "📊 **Avg Views/Post:** 1.7K\n"
            "💫 **Engagement Rate:** 8.5%\n\n"
            "🚧 *Demo data - Real analytics coming soon!*"
        )
        
        keyboard = _create_back_keyboard()
        
        success = await _safe_edit_message(callback, text, keyboard)
        if success:
            await callback.answer()
        else:
            await callback.message.answer(text, reply_markup=keyboard)
            await callback.answer()

    except Exception as e:
        logger.error(f"Overview analytics error: {e}")
        await callback.answer("❌ Error loading overview analytics", show_alert=True)


@router.callback_query(lambda c: c.data == "analytics_growth")
async def analytics_growth_callback(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle growth analytics display"""
    try:
        # Get state data
        state_data = await state.get_data()
        channel_id = state_data.get("selected_channel")
        period = state_data.get("selected_period", 7)
        
        if not channel_id:
            await callback.answer("❌ Missing channel data", show_alert=True)
            return

        # Mock growth data
        text = (
            "📈 **Growth Analytics**\n\n"
            f"📡 Channel: {channel_id}\n"
            f"📅 Period: {period} days\n\n"
            "📊 **Total Growth:** +50 subscribers\n"
            "📈 **Growth Rate:** +4.3%\n\n"
            "📅 **Recent Daily Growth:**\n"
            "• 01/15: 1.2K (+5)\n"
            "• 01/16: 1.2K (+3)\n"
            "• 01/17: 1.2K (+8)\n"
            "• 01/18: 1.2K (+2)\n\n"
            "🚧 *Demo data - Real analytics coming soon!*"
        )
        
        keyboard = _create_back_keyboard()
        
        success = await _safe_edit_message(callback, text, keyboard)
        if success:
            await callback.answer()
        else:
            await callback.message.answer(text, reply_markup=keyboard)
            await callback.answer()

    except Exception as e:
        logger.error(f"Growth analytics error: {e}")
        await callback.answer("❌ Error loading growth analytics", show_alert=True)


@router.callback_query(lambda c: c.data == "analytics_reach")
async def analytics_reach_callback(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle reach analytics display"""
    try:
        # Get state data
        state_data = await state.get_data()
        channel_id = state_data.get("selected_channel")
        period = state_data.get("selected_period", 7)
        
        if not channel_id:
            await callback.answer("❌ Missing channel data", show_alert=True)
            return

        # Mock reach data
        text = (
            "👁️ **Reach Analytics**\n\n"
            f"📡 Channel: {channel_id}\n"
            f"📅 Period: {period} days\n\n"
            "👀 **Total Views:** 25.6K\n"
            "👤 **Unique Viewers:** 18.2K\n"
            "📊 **View/Reach Ratio:** 1.4\n"
            "🔥 **Peak Concurrent:** 245\n\n"
            "⏰ **Top Active Hours:**\n"
            "• 20:00 - 3.2K views\n"
            "• 21:00 - 2.8K views\n"
            "• 19:00 - 2.1K views\n\n"
            "🚧 *Demo data - Real analytics coming soon!*"
        )
        
        keyboard = _create_back_keyboard()
        
        success = await _safe_edit_message(callback, text, keyboard)
        if success:
            await callback.answer()
        else:
            await callback.message.answer(text, reply_markup=keyboard)
            await callback.answer()

    except Exception as e:
        logger.error(f"Reach analytics error: {e}")
        await callback.answer("❌ Error loading reach analytics", show_alert=True)


# =======================================
# ANALYTICS DOMAIN NAVIGATION HANDLERS
# =======================================

@router.callback_query(lambda c: c.data == "analytics_back")
async def analytics_back_callback(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle back navigation within analytics"""
    try:
        # Get state data to show analytics menu
        state_data = await state.get_data()
        channel_id = state_data.get("selected_channel")
        period = state_data.get("selected_period", 7)
        
        if not channel_id:
            await callback.answer("❌ No channel selected", show_alert=True)
            return

        # Show analytics menu
        keyboard = _create_analytics_menu_keyboard()
        text = (
            f"📊 **Analytics Menu**\n\n"
            f"📡 Channel: {channel_id}\n"
            f"📅 Period: {period} days\n\n"
            "Select analytics type:"
        )
        
        success = await _safe_edit_message(callback, text, keyboard)
        if success:
            await callback.answer()
        else:
            await callback.message.answer(text, reply_markup=keyboard)
            await callback.answer()

    except Exception as e:
        logger.error(f"Analytics back navigation error: {e}")
        await callback.answer("❌ Navigation error", show_alert=True)


@router.callback_query(lambda c: c.data == "analytics_channels")
async def analytics_channels_callback(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle channel selection navigation"""
    try:
        # Get channels from state
        state_data = await state.get_data()
        channels = state_data.get("channels", [])
        
        if not channels:
            await callback.answer("❌ No channels available", show_alert=True)
            return

        # Show channel selection
        keyboard = _create_channels_keyboard(channels)
        text = (
            "📊 **Select Channel for Analytics**\n\n"
            "Choose a channel to view detailed analytics:"
        )
        
        success = await _safe_edit_message(callback, text, keyboard)
        if success:
            await callback.answer()
        else:
            await callback.message.answer(text, reply_markup=keyboard)
            await callback.answer()

    except Exception as e:
        logger.error(f"Channel navigation error: {e}")
        await callback.answer("❌ Navigation error", show_alert=True)