"""
FSM States for Content Protection Workflows

Defines all state machine states used across content protection handlers.
"""

from aiogram.fsm.state import State, StatesGroup


class ContentProtectionStates(StatesGroup):
    """FSM states for content protection features"""

    waiting_for_watermark_image = State()
    waiting_for_watermark_text = State()
    waiting_for_watermark_config = State()
    waiting_for_custom_emoji_text = State()
    waiting_for_theft_check_content = State()
