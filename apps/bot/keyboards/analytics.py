"""
Inline keyboards for Analytics V2 Bot UI
Provides navigation and interaction elements for analytics features
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class AnalyticsKeyboards:
    """Factory class for analytics-related keyboards"""

    @staticmethod
    def periods_keyboard() -> InlineKeyboardMarkup:
        """Time period selection keyboard"""
        periods = [
            ("📊 7 Days", "period:7"),
            ("📈 30 Days", "period:30"),
            ("📉 90 Days", "period:90"),
        ]

        # Optimized list comprehension instead of append loop
        keyboard = [
            [InlineKeyboardButton(text=text, callback_data=callback_data)]
            for text, callback_data in periods
        ]

        # Add back button
        keyboard.append([InlineKeyboardButton(text="◀️ Back", callback_data="analytics:back")])

        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def channels_keyboard(
        channels: list[tuple[str, str]], page: int = 0, per_page: int = 5
    ) -> InlineKeyboardMarkup:
        """Channel selection keyboard with pagination"""
        keyboard = []

        # Calculate pagination
        start_idx = page * per_page
        end_idx = start_idx + per_page
        page_channels = channels[start_idx:end_idx]

        # Add channel buttons
        for channel_title, channel_id in page_channels:
            # Truncate long channel names
            display_name = channel_title[:25] + "..." if len(channel_title) > 25 else channel_title
            keyboard.append(
                [
                    InlineKeyboardButton(
                        text=f"📺 {display_name}", callback_data=f"channel:{channel_id}"
                    )
                ]
            )

        # Add pagination buttons
        pagination_row = []
        if page > 0:
            pagination_row.append(
                InlineKeyboardButton(text="◀️ Prev", callback_data=f"channels:page:{page-1}")
            )

        # Show page info
        total_pages = (len(channels) + per_page - 1) // per_page
        pagination_row.append(
            InlineKeyboardButton(
                text=f"{page+1}/{total_pages}", callback_data="analytics:page_info"
            )
        )

        if end_idx < len(channels):
            pagination_row.append(
                InlineKeyboardButton(text="Next ▶️", callback_data=f"channels:page:{page+1}")
            )

        if pagination_row:
            keyboard.append(pagination_row)

        # Add back button
        keyboard.append(
            [InlineKeyboardButton(text="◀️ Back to Menu", callback_data="analytics:main")]
        )

        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def analytics_tabs_keyboard(channel_id: str, period: int) -> InlineKeyboardMarkup:
        """Main analytics tabs keyboard"""
        tabs = [
            ("📊 Overview", f"analytics:overview:{channel_id}:{period}"),
            ("📈 Growth", f"analytics:growth:{channel_id}:{period}"),
            ("👁️ Reach", f"analytics:reach:{channel_id}:{period}"),
        ]

        keyboard = []

        # First row of tabs
        keyboard.append(
            [
                InlineKeyboardButton(text=text, callback_data=callback_data)
                for text, callback_data in tabs
            ]
        )

        # Second row of tabs
        second_row_tabs = [
            ("🔥 Top Posts", f"analytics:top_posts:{channel_id}:{period}"),
            ("🌊 Sources", f"analytics:sources:{channel_id}:{period}"),
            ("📊 Trending", f"analytics:trending:{channel_id}:{period}"),
        ]

        keyboard.append(
            [
                InlineKeyboardButton(text=text, callback_data=callback_data)
                for text, callback_data in second_row_tabs
            ]
        )

        # Action buttons
        action_buttons = [
            ("📤 Export", f"analytics:export:{channel_id}:{period}"),
            ("🔔 Alerts", f"analytics:alerts:{channel_id}"),
            ("🔗 Share", f"analytics:share:{channel_id}:{period}"),
        ]

        keyboard.append(
            [
                InlineKeyboardButton(text=text, callback_data=callback_data)
                for text, callback_data in action_buttons
            ]
        )

        # Navigation
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="🔄 Refresh",
                    callback_data=f"analytics:refresh:{channel_id}:{period}",
                ),
                InlineKeyboardButton(
                    text="⏰ Change Period",
                    callback_data=f"analytics:period:{channel_id}",
                ),
            ]
        )

        keyboard.append(
            [InlineKeyboardButton(text="◀️ Back to Channels", callback_data="analytics:channels")]
        )

        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def export_options_keyboard(channel_id: str, period: int) -> InlineKeyboardMarkup:
        """Export options keyboard"""
        options = [
            ("� JSON Data", f"export:json:{channel_id}:{period}"),
            ("�📄 CSV Report", f"export:csv:{channel_id}:{period}"),
            ("📈 PNG Chart", f"export:png:{channel_id}:{period}"),
            ("📦 Full Export", f"export:full:{channel_id}:{period}"),
        ]

        # Optimized list comprehension instead of append loop
        keyboard = [
            [InlineKeyboardButton(text=text, callback_data=callback_data)]
            for text, callback_data in options
        ]

        keyboard.append(
            [InlineKeyboardButton(text="◀️ Back", callback_data=f"analytics:channel:{channel_id}")]
        )

        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def alerts_main_keyboard(channel_id: str) -> InlineKeyboardMarkup:
        """Main alerts management keyboard"""
        options = [
            ("🔔 My Alerts", f"alerts:list:{channel_id}"),
            ("➕ Add Alert", f"alerts:add:{channel_id}"),
            ("⚙️ Alert Settings", f"alerts:settings:{channel_id}"),
        ]

        # Optimized list comprehension instead of append loop
        keyboard = [
            [InlineKeyboardButton(text=text, callback_data=callback_data)]
            for text, callback_data in options
        ]

        keyboard.append(
            [
                InlineKeyboardButton(
                    text="◀️ Back to Analytics",
                    callback_data=f"analytics:overview:{channel_id}:30",
                )
            ]
        )

        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def alert_types_keyboard(channel_id: str) -> InlineKeyboardMarkup:
        """Alert types selection keyboard"""
        alert_types = [
            ("🚀 Spike Alert", f"alert:type:spike:{channel_id}"),
            ("😴 Quiet Alert", f"alert:type:quiet:{channel_id}"),
            ("📈 Growth Alert", f"alert:type:growth:{channel_id}"),
        ]

        # Optimized list comprehension instead of append loop
        keyboard = [
            [InlineKeyboardButton(text=text, callback_data=callback_data)]
            for text, callback_data in alert_types
        ]

        keyboard.append(
            [
                InlineKeyboardButton(
                    text="◀️ Back to Alerts", callback_data=f"alerts:main:{channel_id}"
                )
            ]
        )

        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def alert_management_keyboard(alert_id: int, channel_id: str) -> InlineKeyboardMarkup:
        """Individual alert management keyboard"""
        options = [
            ("✏️ Edit", f"alert:edit:{alert_id}"),
            ("🔄 Toggle", f"alert:toggle:{alert_id}"),
            ("🗑️ Delete", f"alert:delete:{alert_id}"),
        ]

        keyboard = []
        keyboard.append(
            [
                InlineKeyboardButton(text=text, callback_data=callback_data)
                for text, callback_data in options
            ]
        )

        keyboard.append(
            [
                InlineKeyboardButton(
                    text="◀️ Back to Alerts", callback_data=f"alerts:list:{channel_id}"
                )
            ]
        )

        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def top_posts_keyboard(channel_id: str, period: int, page: int = 0) -> InlineKeyboardMarkup:
        """Top posts navigation keyboard"""
        keyboard = []

        # Pagination
        pagination_row = []
        if page > 0:
            pagination_row.append(
                InlineKeyboardButton(
                    text="◀️ Prev",
                    callback_data=f"top_posts:page:{channel_id}:{period}:{page-1}",
                )
            )

        pagination_row.append(
            InlineKeyboardButton(
                text="🔄 Refresh",
                callback_data=f"top_posts:refresh:{channel_id}:{period}",
            )
        )

        pagination_row.append(
            InlineKeyboardButton(
                text="Next ▶️",
                callback_data=f"top_posts:page:{channel_id}:{period}:{page+1}",
            )
        )

        keyboard.append(pagination_row)

        # Back button
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="◀️ Back to Analytics",
                    callback_data=f"analytics:overview:{channel_id}:{period}",
                )
            ]
        )

        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def confirmation_keyboard(
        action: str, confirm_data: str, cancel_data: str
    ) -> InlineKeyboardMarkup:
        """Confirmation dialog keyboard"""
        keyboard = [
            [
                InlineKeyboardButton(text="✅ Confirm", callback_data=confirm_data),
                InlineKeyboardButton(text="❌ Cancel", callback_data=cancel_data),
            ]
        ]

        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def share_options_keyboard(channel_id: str, period: int) -> InlineKeyboardMarkup:
        """Share options keyboard"""
        options = [
            ("🔗 1 Hour Link", f"share:create:{channel_id}:{period}:3600"),
            ("🔗 6 Hour Link", f"share:create:{channel_id}:{period}:21600"),
            ("🔗 24 Hour Link", f"share:create:{channel_id}:{period}:86400"),
        ]

        # Optimized list comprehension instead of append loop
        keyboard = [
            [InlineKeyboardButton(text=text, callback_data=callback_data)]
            for text, callback_data in options
        ]

        keyboard.append(
            [
                InlineKeyboardButton(
                    text="◀️ Back to Analytics",
                    callback_data=f"analytics:overview:{channel_id}:{period}",
                )
            ]
        )

        return InlineKeyboardMarkup(inline_keyboard=keyboard)


# Convenience functions for commonly used keyboards
def kb_periods() -> InlineKeyboardMarkup:
    """Get periods keyboard"""
    return AnalyticsKeyboards.periods_keyboard()


def kb_channels(channels: list[tuple[str, str]], page: int = 0) -> InlineKeyboardMarkup:
    """Get channels keyboard"""
    return AnalyticsKeyboards.channels_keyboard(channels, page)


def kb_tabs(channel_id: str, period: int) -> InlineKeyboardMarkup:
    """Get analytics tabs keyboard"""
    return AnalyticsKeyboards.analytics_tabs_keyboard(channel_id, period)


def kb_export(channel_id: str, period: int) -> InlineKeyboardMarkup:
    """Get export options keyboard"""
    return AnalyticsKeyboards.export_options_keyboard(channel_id, period)


def kb_alerts_main(channel_id: str) -> InlineKeyboardMarkup:
    """Get main alerts keyboard"""
    return AnalyticsKeyboards.alerts_main_keyboard(channel_id)


def kb_alert_types(channel_id: str) -> InlineKeyboardMarkup:
    """Get alert types keyboard"""
    return AnalyticsKeyboards.alert_types_keyboard(channel_id)


def kb_confirmation(action: str, confirm_data: str, cancel_data: str) -> InlineKeyboardMarkup:
    """Get confirmation keyboard"""
    return AnalyticsKeyboards.confirmation_keyboard(action, confirm_data, cancel_data)


def get_analytics_main_keyboard() -> InlineKeyboardMarkup:
    """Main analytics menu keyboard"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 Overview", callback_data="analytics_overview"),
                InlineKeyboardButton(text="📈 Growth", callback_data="analytics_growth"),
            ],
            [
                InlineKeyboardButton(text="👥 Reach", callback_data="analytics_reach"),
                InlineKeyboardButton(text="🔝 Top Posts", callback_data="analytics_top_posts"),
            ],
            [
                InlineKeyboardButton(text="🚀 Traffic Sources", callback_data="analytics_sources"),
                InlineKeyboardButton(text="📱 Trending", callback_data="analytics_trending"),
            ],
            [
                InlineKeyboardButton(text="📋 Export Data", callback_data="analytics_export"),
                InlineKeyboardButton(text="🔔 Alerts", callback_data="analytics_alerts"),
            ],
            [InlineKeyboardButton(text="⬅️ Back", callback_data="main_menu")],
        ]
    )


def get_export_type_keyboard() -> InlineKeyboardMarkup:
    """Export type selection keyboard"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 Overview", callback_data="export_type:overview"),
                InlineKeyboardButton(text="📈 Growth", callback_data="export_type:growth"),
            ],
            [
                InlineKeyboardButton(text="👥 Reach", callback_data="export_type:reach"),
                InlineKeyboardButton(text="🔝 Top Posts", callback_data="export_type:top_posts"),
            ],
            [
                InlineKeyboardButton(text="🚀 Sources", callback_data="export_type:sources"),
                InlineKeyboardButton(text="📱 Trending", callback_data="export_type:trending"),
            ],
            [InlineKeyboardButton(text="⬅️ Back", callback_data="analytics_menu")],
        ]
    )


def get_export_format_keyboard(export_type: str) -> InlineKeyboardMarkup:
    """Export format selection keyboard"""
    # PNG charts are only available for certain data types
    chart_types = ["growth", "reach", "sources"]

    buttons = []

    # CSV is always available
    buttons.append([InlineKeyboardButton(text="📄 CSV File", callback_data="export_format:csv")])

    # PNG charts only for supported types
    if export_type in chart_types:
        buttons.append(
            [InlineKeyboardButton(text="📊 PNG Chart", callback_data="export_format:png")]
        )

    # Back button
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="analytics_export")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
