"""
Bot Export Microhandler - Pure Export Domain
============================================

Focused microhandler containing only export-related functionality.
Part of Phase 2 microrouter implementation (export domain).

Domain Responsibilities:
- Export options display
- Export format selection
- Share functionality
- Share options management

Extracted from: apps/bot/handlers/analytics_v2.py (714 lines → ~100 lines export)
Architecture: Clean separation of export concerns following Phase 1 microrouter pattern
"""

import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)

# Create export microhandler router
router = Router()


# ==============================
# EXPORT DOMAIN HELPER FUNCTIONS
# ==============================


def _get_settings():
    """Get settings instance with proper error handling"""
    try:
        from config.settings import Settings

        return Settings
    except Exception:
        # Fallback mock settings
        class MockSettings:
            EXPORT_ENABLED = True
            SHARE_LINKS_ENABLED = True

        return MockSettings()


def _safe_callback_data_split(
    callback_data: str | None, separator: str = ":", index: int = 1
) -> str | None:
    """Safely split callback data and return the requested part"""
    if not callback_data:
        return None
    try:
        parts = callback_data.split(separator)
        if len(parts) > index:
            return parts[index]
        return None
    except (AttributeError, IndexError):
        return None


async def _safe_edit_message(callback: CallbackQuery, text: str, reply_markup=None) -> bool:
    """Safely edit callback message with type checking"""
    try:
        from aiogram.types import Message

        if (
            callback.message
            and isinstance(callback.message, Message)
            and hasattr(callback.message, "edit_text")
        ):
            await callback.message.edit_text(text, reply_markup=reply_markup)  # type: ignore
            return True
        return False
    except Exception:
        return False


# =====================================
# EXPORT DOMAIN COMMAND HANDLERS
# =====================================


@router.callback_query(F.data.startswith("analytics:export:"))
async def show_export_options(callback: CallbackQuery) -> None:
    """Show export options for analytics data"""
    try:
        settings = _get_settings()

        if not getattr(settings, "EXPORT_ENABLED", True):
            await callback.answer(
                "🚧 Export feature is currently disabled. Coming soon!", show_alert=True
            )
            return

        # Extract channel_id and period from callback data
        parts = callback.data.split(":")
        if len(parts) < 4:
            await callback.answer("❌ Invalid export request", show_alert=True)
            return

        channel_id, period = parts[2], int(parts[3])

        # Create simple export keyboard
        buttons = [
            [InlineKeyboardButton(text="📊 CSV", callback_data="export_format:csv")],
            [InlineKeyboardButton(text="📋 JSON", callback_data="export_format:json")],
            [InlineKeyboardButton(text="📄 PDF", callback_data="export_format:pdf")],
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

        text = (
            "📤 **Export Options**\n\n"
            f"Channel: {channel_id}\n"
            f"Period: {period} days\n\n"
            "Choose export format:"
        )

        success = await _safe_edit_message(callback, text, keyboard)
        if success:
            await callback.answer()
        else:
            await callback.message.answer(text, reply_markup=keyboard)
            await callback.answer()

    except Exception as e:
        logger.error(f"Export options failed: {e}")
        await callback.answer("❌ Failed to show export options", show_alert=True)


@router.callback_query(F.data.startswith("analytics:share:"))
async def show_share_options(callback: CallbackQuery) -> None:
    """Show share options for analytics data"""
    try:
        settings = _get_settings()

        if not getattr(settings, "SHARE_LINKS_ENABLED", True):
            await callback.answer(
                "🚧 Share links feature is currently disabled. Coming soon!", show_alert=True
            )
            return

        # Extract channel_id and period from callback data
        parts = callback.data.split(":")
        if len(parts) < 4:
            await callback.answer("❌ Invalid share request", show_alert=True)
            return

        channel_id, period = parts[2], int(parts[3])

        # For now, show coming soon message
        await callback.answer("🔗 Share links feature coming soon!", show_alert=True)

    except Exception as e:
        logger.error(f"Share options failed: {e}")
        await callback.answer("❌ Failed to show share options", show_alert=True)


# =====================================
# EXPORT DOMAIN FORMAT HANDLERS
# =====================================


@router.callback_query(F.data.startswith("export_format:"))
async def handle_export_format(callback: CallbackQuery) -> None:
    """Handle specific export format selection"""
    try:
        # Extract format from callback data
        export_format = _safe_callback_data_split(callback.data, ":", 1)
        if not export_format:
            await callback.answer("❌ Invalid export format", show_alert=True)
            return

        # Handle different export formats
        if export_format == "csv":
            await _handle_csv_export(callback)
        elif export_format == "json":
            await _handle_json_export(callback)
        elif export_format == "pdf":
            await _handle_pdf_export(callback)
        else:
            await callback.answer("❌ Unsupported export format", show_alert=True)

    except Exception as e:
        logger.error(f"Export format handler failed: {e}")
        await callback.answer("❌ Export failed", show_alert=True)


async def _handle_csv_export(callback: CallbackQuery) -> None:
    """Handle CSV export format"""
    # Implementation placeholder
    await callback.answer("📊 CSV export will be implemented soon!", show_alert=True)


async def _handle_json_export(callback: CallbackQuery) -> None:
    """Handle JSON export format"""
    # Implementation placeholder
    await callback.answer("📋 JSON export will be implemented soon!", show_alert=True)


async def _handle_pdf_export(callback: CallbackQuery) -> None:
    """Handle PDF export format"""
    # Implementation placeholder
    await callback.answer("📄 PDF export will be implemented soon!", show_alert=True)


# =====================================
# SHARE DOMAIN HANDLERS
# =====================================


@router.callback_query(F.data.startswith("share_type:"))
async def handle_share_type(callback: CallbackQuery) -> None:
    """Handle specific share type selection"""
    try:
        # Extract share type from callback data
        share_type = _safe_callback_data_split(callback.data, ":", 1)
        if not share_type:
            await callback.answer("❌ Invalid share type", show_alert=True)
            return

        # Handle different share types
        if share_type == "link":
            await _handle_share_link(callback)
        elif share_type == "image":
            await _handle_share_image(callback)
        elif share_type == "report":
            await _handle_share_report(callback)
        else:
            await callback.answer("❌ Unsupported share type", show_alert=True)

    except Exception as e:
        logger.error(f"Share type handler failed: {e}")
        await callback.answer("❌ Share failed", show_alert=True)


async def _handle_share_link(callback: CallbackQuery) -> None:
    """Handle share link generation"""
    # Implementation placeholder
    await callback.answer("🔗 Share link generation will be implemented soon!", show_alert=True)


async def _handle_share_image(callback: CallbackQuery) -> None:
    """Handle share image generation"""
    # Implementation placeholder
    await callback.answer("🖼️ Share image generation will be implemented soon!", show_alert=True)


async def _handle_share_report(callback: CallbackQuery) -> None:
    """Handle share report generation"""
    # Implementation placeholder
    await callback.answer("📊 Share report generation will be implemented soon!", show_alert=True)
