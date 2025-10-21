"""
Theft Detection Handlers for Content Protection

Handles content theft analysis workflows.
"""

import logging
from typing import cast

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, User

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


@router.callback_query(F.data == "protect_theft_check")
async def handle_theft_check_start(callback: CallbackQuery, state: FSMContext):
    """Start content theft detection"""

    if not validate_callback_state(callback):
        await callback.answer("❌ Invalid callback state")
        return

    # Type narrowing
    msg = cast(Message, callback.message)

    user_tier = await get_user_subscription_tier(callback.from_user.id)

    if not await check_feature_usage_limit("theft_scans", callback.from_user.id, user_tier):
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
            RiskLevel.LOW: "🟢",
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
        await increment_feature_usage("theft_scans", user.id)

    except Exception as e:
        await message.answer(f"❌ **Analysis failed:**\n{str(e)}")

    finally:
        await state.clear()
