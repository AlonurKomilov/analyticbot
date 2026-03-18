"""Telegram bot handlers — simple: receive channel link → run analysis → send PDF"""

from __future__ import annotations

import logging
import os

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile, Message

from src.analyzer.fetcher import parse_channel_identifier
from src.analyzer.pipeline import run_analysis
from src.db.session import async_session

logger = logging.getLogger(__name__)
router = Router()


class AnalyzeState(StatesGroup):
    waiting_for_channel = State()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "<b>Welcome to Analyticbot!</b>\n\n"
        "I analyze Telegram channels and groups.\n\n"
        "Send /analyze and then paste a channel link or @username — "
        "I'll fetch the data and send you a detailed PDF report.\n\n"
        "Commands:\n"
        "/analyze — Start a new analysis\n"
        "/help — Show this message",
        parse_mode="HTML",
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "<b>How to use:</b>\n\n"
        "1. Send /analyze\n"
        "2. Paste a channel link (e.g. https://t.me/channel) or @username\n"
        "3. Wait while I fetch and analyze the data\n"
        "4. Receive a PDF report\n\n"
        "<i>Analysis usually takes 30-60 seconds depending on channel size.</i>",
        parse_mode="HTML",
    )


@router.message(Command("analyze"))
async def cmd_analyze(message: Message, state: FSMContext) -> None:
    await state.set_state(AnalyzeState.waiting_for_channel)
    await message.answer(
        "Send me a channel link or @username to analyze.\n\n"
        "Examples:\n"
        "• <code>https://t.me/durov</code>\n"
        "• <code>@durov</code>\n"
        "• <code>durov</code>",
        parse_mode="HTML",
    )


@router.message(AnalyzeState.waiting_for_channel)
async def handle_channel_input(message: Message, state: FSMContext) -> None:
    raw = (message.text or "").strip()
    if not raw:
        await message.answer("Please send a channel link or @username.")
        return

    # Validate input
    try:
        username = parse_channel_identifier(raw)
    except ValueError:
        await message.answer(
            "I couldn't recognize that as a channel link.\n"
            "Try formats like <code>@channel</code> or <code>https://t.me/channel</code>",
            parse_mode="HTML",
        )
        return

    await state.clear()

    progress = await message.answer(f"Analyzing <b>@{username}</b>… This may take a minute.", parse_mode="HTML")

    try:
        async with async_session() as session:
            metrics, pdf_path = await run_analysis(
                raw,
                session=session,
                requested_by=message.from_user.id if message.from_user else None,
                source="bot",
            )

        # Send summary
        summary = (
            f"<b>Analysis Complete: {metrics.channel_title}</b>\n\n"
            f"Members: {metrics.member_count:,}\n"
            f"Posts analyzed: {metrics.total_posts:,}\n"
            f"Avg views/post: {metrics.avg_views:,.0f}\n"
            f"Engagement rate: {metrics.avg_engagement_rate:.1f}%\n"
            f"Posts/day: {metrics.posting_pattern.avg_posts_per_day:.1f}\n\n"
            f"Full report attached below."
        )
        await message.answer(summary, parse_mode="HTML")

        # Send PDF
        if os.path.exists(pdf_path):
            doc = FSInputFile(pdf_path, filename=f"analytics_{username}.pdf")
            await message.answer_document(doc)
        else:
            await message.answer("Report generated but PDF file not found. Please try again.")

    except ValueError as e:
        await message.answer(f"Error: {e}")
    except Exception as e:
        logger.error(f"Analysis failed for {raw}: {e}", exc_info=True)
        await message.answer(
            "Something went wrong during analysis. "
            "Make sure the channel exists and is public, then try again."
        )

    # Clean up progress message
    try:
        await progress.delete()
    except Exception:
        pass
