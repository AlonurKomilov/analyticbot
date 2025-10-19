"""
Bot Export Handlers
Handles file exports (CSV/PNG) and sending to users in Telegram bot
"""

import logging
from io import StringIO

import aiohttp
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    Message,
)

from apps.bot.keyboards.analytics import (
    get_export_format_keyboard,
    get_export_type_keyboard,
)
from apps.bot.middlewares.throttle import rate_limit
from apps.shared.clients.analytics_client import (
    AnalyticsClient,
    GrowthResponse,
    OverviewResponse,
    ReachResponse,
    SourcesResponse,
    TopPostsResponse,
    TrendingResponse,
)

# ✅ PHASE 1 FIX: Import from apps.shared.exports (circular dependency fix)
from apps.shared.exports.csv_v2 import CSVExporter

# ✅ PHASE 3 FIX (Oct 19, 2025): Use DI container instead of factory
from apps.di import get_container
from config import settings

logger = logging.getLogger(__name__)
router = Router()


def get_analytics_client() -> AnalyticsClient:
    """Get analytics client with bot integration"""
    return AnalyticsClient(settings.ANALYTICS_V2_BASE_URL)


def get_csv_exporter() -> CSVExporter:
    """Get CSV exporter instance"""
    return CSVExporter()


logger = logging.getLogger(__name__)
router = Router()


def get_chart_service():
    """
    Get chart service instance via DI
    Phase 3 Fix (Oct 19, 2025): Removed factory usage
    """
    # Note: Chart service creation maintained for now
    # TODO: Move to proper DI provider when chart service is refactored
    from apps.shared.services.chart_service import create_chart_service

    return create_chart_service()


@router.callback_query(F.data == "analytics_export")
@rate_limit("export", per_minute=5)
async def handle_export_menu(callback: CallbackQuery, state: FSMContext):
    """Handle export menu selection"""

    if not settings.EXPORT_ENABLED:
        await callback.answer("📋 Export functionality is currently disabled", show_alert=True)
        return

    if not callback.message or not isinstance(callback.message, Message):
        await callback.answer("Message not available")
        return

    keyboard = get_export_type_keyboard()
    await callback.message.edit_text(
        "📋 <b>Export Analytics Data</b>\n\n" "Choose the type of data you want to export:",
        reply_markup=keyboard,
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("export_type:"))
@rate_limit("export", per_minute=10)
async def handle_export_type_selection(callback: CallbackQuery, state: FSMContext):
    """Handle export type selection"""
    if not callback.data:
        await callback.answer("Invalid selection")
        return

    export_type = callback.data.split(":")[-1]

    # Store export type in state
    await state.update_data(export_type=export_type)

    if not callback.message or not isinstance(callback.message, Message):
        await callback.answer("Message not available")
        return

    # Show format selection
    keyboard = get_export_format_keyboard(export_type)

    type_labels = {
        "overview": "Overview",
        "growth": "Growth Analysis",
        "reach": "Reach Analysis",
        "top_posts": "Top Posts",
        "sources": "Traffic Sources",
        "trending": "Trending Content",
    }

    type_label = type_labels.get(export_type, export_type.title())

    await callback.message.edit_text(
        f"📋 <b>Export {type_label}</b>\n\n" "Choose export format:",
        reply_markup=keyboard,
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("export_format:"))
@rate_limit("export", per_minute=10)
async def handle_export_format_selection(callback: CallbackQuery, state: FSMContext):
    """Handle export format selection and start export"""
    if not callback.data:
        await callback.answer("Invalid selection")
        return

    format_type = callback.data.split(":")[-1]

    if not callback.message or not isinstance(callback.message, Message):
        await callback.answer("Message not available")
        return

    # Get export type from state
    state_data = await state.get_data()
    export_type = state_data.get("export_type")

    if not export_type:
        await callback.answer("❌ Export session expired. Please start over.", show_alert=True)
        return

    # Clear state
    await state.clear()

    # Start export process
    await callback.message.edit_text(
        f"⏳ Preparing {format_type.upper()} export...\n" "This may take a few moments."
    )
    await callback.answer()

    try:
        # Get channel_id from callback context (you might need to adjust this)
        _user_id = callback.from_user.id  # Store for future use
        # For demo purposes, using a placeholder channel_id
        # In real implementation, you'd get this from user context/settings
        channel_id = "@demo_channel"  # TODO: Get from user settings
        period = 30  # TODO: Allow user to specify period

        if format_type == "csv":
            await export_csv_data(callback.message, export_type, channel_id, period)
        elif format_type == "png":
            await export_png_chart(callback.message, export_type, channel_id, period)

    except Exception as e:
        logger.error(f"Export failed for user {callback.from_user.id}: {e}")
        await callback.message.edit_text(
            "❌ <b>Export Failed</b>\n\n"
            "Sorry, we couldn't generate your export. Please try again later.",
            parse_mode="HTML",
        )


async def export_csv_data(message: Message, export_type: str, channel_id: str, period: int):
    """Export data as CSV file"""
    try:
        # Initialize clients
        analytics_client = get_analytics_client()
        csv_exporter = get_csv_exporter()

        # Fetch analytics data
        # Note: AnalyticsClient manages session internally
        data: (
            OverviewResponse
            | GrowthResponse
            | ReachResponse
            | TopPostsResponse
            | SourcesResponse
            | TrendingResponse
        )
        csv_content: StringIO

        if export_type == "overview":
            data = await analytics_client.overview(channel_id, period)
            csv_content = csv_exporter.overview_to_csv(data)
        elif export_type == "growth":
            data = await analytics_client.growth(channel_id, period)
            csv_content = csv_exporter.growth_to_csv(data)
        elif export_type == "reach":
            data = await analytics_client.reach(channel_id, period)
            csv_content = csv_exporter.reach_to_csv(data)
        elif export_type == "top_posts":
            data = await analytics_client.top_posts(channel_id, period)
            csv_content = csv_exporter.top_posts_to_csv(data)
        elif export_type == "sources":
            data = await analytics_client.sources(channel_id, period)
            csv_content = csv_exporter.sources_to_csv(data)
        elif export_type == "trending":
            data = await analytics_client.trending(channel_id, period)
            csv_content = csv_exporter.trending_to_csv(data)
        else:
            raise ValueError(f"Unsupported export type: {export_type}")

        if not data:
            await message.edit_text(
                "📋 <b>No Data Available</b>\n\n"
                "No analytics data available for the selected period.",
                parse_mode="HTML",
            )
            return

        # Prepare file
        filename = csv_exporter.generate_filename(export_type, channel_id, period)
        file_buffer = BufferedInputFile(csv_content.getvalue().encode("utf-8"), filename=filename)

        # Send file
        await message.answer_document(
            document=file_buffer,
            caption=f"📊 <b>{export_type.title()} Export</b>\n"
            f"📅 Period: {period} days\n"
            f"📈 Channel: {channel_id}",
            parse_mode="HTML",
        )

        # Update status message
        await message.edit_text(
            "✅ <b>Export Complete</b>\n\n" f"Your {export_type} data has been exported as CSV."
        )

        logger.info(f"CSV export completed for user {message.chat.id}, type {export_type}")

    except aiohttp.ClientError as e:
        logger.error(f"Analytics API error during CSV export: {e}")
        await message.edit_text(
            "❌ <b>Export Failed</b>\n\n"
            "Analytics service is currently unavailable. Please try again later.",
            parse_mode="HTML",
        )
    except Exception as e:
        logger.error(f"CSV export error: {e}")
        await message.edit_text(
            "❌ <b>Export Failed</b>\n\n" "An error occurred during export. Please try again.",
            parse_mode="HTML",
        )


async def export_png_chart(message: Message, export_type: str, channel_id: str, period: int):
    """Export data as PNG chart"""
    try:
        chart_service = get_chart_service()

        if not chart_service.is_available():
            await message.edit_text(
                "❌ <b>PNG Export Unavailable</b>\n\n"
                "Chart rendering is not available on this server.",
                parse_mode="HTML",
            )
            return

        # Initialize analytics client
        analytics_client = get_analytics_client()

        # Fetch analytics data
        # Note: AnalyticsClient manages session internally
        data: GrowthResponse | ReachResponse | SourcesResponse
        png_bytes: bytes

        if export_type == "growth":
            data = await analytics_client.growth(channel_id, period)
            png_bytes = chart_service.render_growth_chart(
                data.model_dump() if hasattr(data, "model_dump") else data.__dict__
            )
        elif export_type == "reach":
            data = await analytics_client.reach(channel_id, period)
            png_bytes = chart_service.render_reach_chart(
                data.model_dump() if hasattr(data, "model_dump") else data.__dict__
            )
        elif export_type == "sources":
            data = await analytics_client.sources(channel_id, period)
            png_bytes = chart_service.render_sources_chart(
                data.model_dump() if hasattr(data, "model_dump") else data.__dict__
            )
        else:
            await message.edit_text(
                f"❌ <b>PNG Export Not Supported</b>\n\n"
                f"PNG charts are not available for {export_type} data.\n"
                "Try CSV export instead.",
                parse_mode="HTML",
            )
            return

        if not data:
            await message.edit_text(
                "📋 <b>No Data Available</b>\n\n"
                "No analytics data available for the selected period.",
                parse_mode="HTML",
            )
            return

        # Prepare file
        filename = f"{export_type}_{channel_id}_{period}d.png"
        file_buffer = BufferedInputFile(png_bytes, filename=filename)

        # Send file
        await message.answer_photo(
            photo=file_buffer,
            caption=f"📊 <b>{export_type.title()} Chart</b>\n"
            f"📅 Period: {period} days\n"
            f"📈 Channel: {channel_id}",
            parse_mode="HTML",
        )

        # Update status message
        await message.edit_text(
            "✅ <b>Export Complete</b>\n\n" f"Your {export_type} chart has been generated."
        )

        logger.info(f"PNG export completed for user {message.chat.id}, type {export_type}")

    except aiohttp.ClientError as e:
        logger.error(f"Analytics API error during PNG export: {e}")
        await message.edit_text(
            "❌ <b>Export Failed</b>\n\n"
            "Analytics service is currently unavailable. Please try again later.",
            parse_mode="HTML",
        )
    except Exception as e:
        logger.error(f"Chart rendering error: {e}")
        await message.edit_text(
            "❌ <b>Chart Generation Failed</b>\n\n"
            "Unable to generate chart from the data. Please try again.",
            parse_mode="HTML",
        )


# Command for direct CSV export (advanced users)
@router.message(Command("export_csv"))
@rate_limit("export", per_minute=3)
async def cmd_export_csv(message: Message):
    """Direct CSV export command"""

    if not settings.EXPORT_ENABLED:
        await message.answer("📋 Export functionality is currently disabled.")
        return

    # Parse command arguments
    if not message.text:
        await message.answer("Invalid command: no text found")
        return

    args = message.text.split()[1:]  # Skip /export_csv

    if len(args) < 2:
        await message.answer(
            "📋 <b>CSV Export Command</b>\n\n"
            "Usage: <code>/export_csv {type} {channel_id} [period]</code>\n\n"
            "Types: overview, growth, reach, top_posts, sources, trending\n"
            "Period: days (default: 30)\n\n"
            "Example: <code>/export_csv growth @mychannel 7</code>",
            parse_mode="HTML",
        )
        return

    export_type = args[0]
    channel_id = args[1]
    period = int(args[2]) if len(args) > 2 else 30

    # Validate parameters
    valid_types = ["overview", "growth", "reach", "top_posts", "sources", "trending"]
    if export_type not in valid_types:
        await message.answer(f"❌ Invalid type. Must be one of: {', '.join(valid_types)}")
        return

    if period < 1 or period > 365:
        await message.answer("❌ Period must be between 1 and 365 days.")
        return

    # Start export
    status_message = await message.answer(f"⏳ Exporting {export_type} data...")
    await export_csv_data(status_message, export_type, channel_id, period)
