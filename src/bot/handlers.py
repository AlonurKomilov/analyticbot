"""Telegram bot handlers — receive channel link → run analysis → send PDF"""

from __future__ import annotations

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from src.analyzer.fetcher import parse_channel_identifier
from src.analyzer.metrics import AnalysisMetrics
from src.analyzer.pipeline import run_analysis
from src.bot.i18n import format_date, get_lang, set_lang, t
from src.config import settings
from src.db.repository import AnalysisRepository
from src.db.session import async_session

logger = logging.getLogger(__name__)
router = Router()

_WEEKDAY_KEYS = [f"weekday_{i}" for i in range(7)]


# ── Helpers ────────────────────────────────────────────────────────────────

def _uid(msg_or_cb: Message | CallbackQuery) -> int | None:
    u = msg_or_cb.from_user
    return u.id if u else None


def _lang(msg_or_cb: Message | CallbackQuery) -> str:
    return get_lang(_uid(msg_or_cb))


# ── Inline keyboards ──────────────────────────────────────────────────────

def _main_menu_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("btn_analyze", lang), callback_data="action:analyze")],
        [
            InlineKeyboardButton(text=t("btn_history", lang), callback_data="action:history"),
            InlineKeyboardButton(text=t("btn_help", lang), callback_data="action:help"),
        ],
        [InlineKeyboardButton(text=t("btn_language", lang), callback_data="action:lang")],
    ])


def _after_report_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("btn_analyze_another", lang), callback_data="action:analyze")],
        [InlineKeyboardButton(text=t("btn_my_history", lang), callback_data="action:history")],
    ])


def _lang_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
            InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang:uz"),
        ],
    ])


class AnalyzeState(StatesGroup):
    waiting_for_channel = State()
    running = State()


# ── Format helpers ─────────────────────────────────────────────────────────

def _top_content_type(metrics: AnalysisMetrics) -> str:
    mix = metrics.content_mix
    types = [
        (mix.pct_photo, "Photo"),
        (mix.pct_video, "Video"),
        (mix.pct_text_only, "Text"),
        (mix.pct_document, "Document"),
        (mix.pct_other, "Other"),
    ]
    best = max(types, key=lambda x: x[0])
    return f"{best[1]} ({best[0]:.0f}%)"


def _build_summary(metrics: AnalysisMetrics, lang: str) -> str:
    """Build a professional, structured analysis summary message."""
    eng = metrics.engagement
    pp = metrics.posting_pattern

    # Channel identity
    ch_type = t("type_supergroup", lang) if metrics.channel_type == "supergroup" else t("type_channel", lang)
    username_str = f"@{metrics.channel_username}" if metrics.channel_username else ""

    # Activity status
    activity_key = f"activity_{metrics.activity_status}"
    activity_label = t(activity_key, lang)

    # Last post info
    if metrics.days_since_last_post == 0:
        last_post_str = t("last_post_today", lang)
    else:
        last_post_str = t("last_post_ago", lang, days=metrics.days_since_last_post)

    # Date range
    date_range = ""
    if metrics.date_from and metrics.date_to:
        date_range = f"{format_date(metrics.date_from, lang)} — {format_date(metrics.date_to, lang)}"

    # Best hour / day
    best_time = ""
    if pp.most_active_hour is not None:
        h = pp.most_active_hour
        best_time = f"{h:02d}:00–{h:02d}:59"
    best_day = ""
    if pp.most_active_weekday is not None:
        best_day = t(_WEEKDAY_KEYS[pp.most_active_weekday], lang)

    lines = [
        t("report_title", lang),
        "",
        f"<b>{metrics.channel_title}</b>",
        f"{ch_type}  •  {username_str}  •  {t('members', lang)}: {metrics.member_count:,}",
        f"{activity_label}  •  {last_post_str}",
    ]
    if date_range:
        lines.append(f"📅 {t('period', lang)}: {date_range} ({metrics.analysis_period_days} {t('days', lang)})")
    lines.append(f"📝 {metrics.total_posts:,} {t('posts_analyzed', lang)}")
    lines.append("")

    # Reach & Engagement
    lines.append(t("section_reach", lang))
    lines.append(
        f"   👀 {t('avg_views', lang)}: <b>{metrics.avg_views:,.0f}</b> "
        f"({t('median', lang)}: {eng.median_views:,.0f})"
    )
    lines.append(f"   📊 {t('engagement_rate', lang)}: <b>{metrics.avg_engagement_rate:.1f}%</b>")
    lines.append(
        f"   🔄 {t('virality', lang)}: {eng.virality_rate:.2f}%  •  "
        f"💬 {t('interaction', lang)}: {eng.interaction_rate:.2f}%"
    )
    lines.append("")

    # Posting Activity
    lines.append(t("section_activity", lang))
    lines.append(f"   📊 {t('posts_per_day', lang)}: <b>{pp.avg_posts_per_day:.1f}</b>")
    if best_time:
        lines.append(f"   🕐 {t('best_time', lang)}: <b>{best_time}</b>")
    if best_day:
        lines.append(f"   📆 {t('best_day', lang)}: <b>{best_day}</b>")
    lines.append("")

    # Content
    lines.append(t("section_content", lang))
    lines.append(f"   📎 {t('top_type', lang)}: <b>{_top_content_type(metrics)}</b>")
    lines.append(f"   🔗 {t('with_links', lang)}: <b>{eng.pct_posts_with_links:.0f}%</b>")
    lines.append("")

    # Warnings for stale/low-activity channels
    if metrics.days_since_last_post > 14:
        lines.append(t("warn_stale_engagement", lang, days=metrics.days_since_last_post))
        lines.append("")
    elif metrics.total_posts < 50 and metrics.analysis_period_days > 90:
        lines.append(t("warn_low_posts", lang, n=metrics.total_posts, days=metrics.analysis_period_days, freq=metrics.posting_pattern.avg_posts_per_day))
        lines.append("")

    # Period clarification for high-volume channels
    if metrics.total_posts >= 500:
        lines.append(t("period_note", lang, n=metrics.total_posts))
        lines.append("")

    lines.append(t("full_report", lang))
    return "\n".join(lines)


# ── Commands ───────────────────────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    lang = _lang(message)
    await message.answer(
        t("welcome", lang),
        parse_mode="HTML",
        reply_markup=_main_menu_kb(lang),
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    lang = _lang(message)
    await message.answer(
        t("help", lang),
        parse_mode="HTML",
        reply_markup=_main_menu_kb(lang),
    )


@router.message(Command("lang"))
async def cmd_lang(message: Message) -> None:
    lang = _lang(message)
    await message.answer(
        t("choose_language", lang),
        parse_mode="HTML",
        reply_markup=_lang_kb(),
    )


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    lang = _lang(message)
    current = await state.get_state()
    if current is None:
        await message.answer(t("nothing_to_cancel", lang))
        return
    await state.clear()
    await message.answer(t("cancelled", lang))


# ── Inline-button callbacks ───────────────────────────────────────────────

@router.callback_query(F.data.startswith("lang:"))
async def cb_set_lang(callback: CallbackQuery) -> None:
    await callback.answer()
    chosen = callback.data.split(":")[1]
    uid = _uid(callback)
    if uid:
        set_lang(uid, chosen)
    lang = chosen
    await callback.message.answer(
        t("language_set", lang),
        parse_mode="HTML",
        reply_markup=_main_menu_kb(lang),
    )


@router.callback_query(F.data == "action:lang")
async def cb_lang(callback: CallbackQuery) -> None:
    await callback.answer()
    lang = _lang(callback)
    await callback.message.answer(
        t("choose_language", lang),
        parse_mode="HTML",
        reply_markup=_lang_kb(),
    )


@router.callback_query(F.data == "action:analyze")
async def cb_analyze(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    lang = _lang(callback)
    current = await state.get_state()
    if current == AnalyzeState.running:
        await callback.message.answer(t("already_running", lang))
        return
    await state.set_state(AnalyzeState.waiting_for_channel)
    await callback.message.answer(t("send_channel", lang), parse_mode="HTML")


@router.callback_query(F.data == "action:history")
async def cb_history(callback: CallbackQuery) -> None:
    await callback.answer()
    lang = _lang(callback)
    uid = _uid(callback)
    if not uid:
        return
    async with async_session() as session:
        repo = AnalysisRepository(session)
        analyses = await repo.get_user_analyses(uid, limit=10)

    if not analyses:
        await callback.message.answer(
            t("no_history", lang),
            reply_markup=_main_menu_kb(lang),
        )
        return

    lines = [t("history_title", lang)]
    for i, a in enumerate(analyses, 1):
        status_icon = {"done": "✅", "failed": "❌", "running": "⏳", "pending": "🕐"}.get(
            a.status, "❓"
        )
        title = a.channel_title or a.channel_identifier
        date_str = a.created_at.strftime("%b %d, %H:%M") if a.created_at else "—"
        lines.append(f"{i}. {status_icon} <b>{title}</b> — {date_str} ({a.status})")

    await callback.message.answer(
        "\n".join(lines),
        parse_mode="HTML",
        reply_markup=_main_menu_kb(lang),
    )


@router.callback_query(F.data == "action:help")
async def cb_help(callback: CallbackQuery) -> None:
    await callback.answer()
    lang = _lang(callback)
    await callback.message.answer(
        t("help", lang),
        parse_mode="HTML",
        reply_markup=_main_menu_kb(lang),
    )


@router.message(Command("history"))
async def cmd_history(message: Message) -> None:
    lang = _lang(message)
    uid = _uid(message)
    if not uid:
        return
    async with async_session() as session:
        repo = AnalysisRepository(session)
        analyses = await repo.get_user_analyses(uid, limit=10)

    if not analyses:
        await message.answer(t("no_history", lang), reply_markup=_main_menu_kb(lang))
        return

    lines = [t("history_title", lang)]
    for i, a in enumerate(analyses, 1):
        status_icon = {"done": "✅", "failed": "❌", "running": "⏳", "pending": "🕐"}.get(
            a.status, "❓"
        )
        title = a.channel_title or a.channel_identifier
        date_str = a.created_at.strftime("%b %d, %H:%M") if a.created_at else "—"
        lines.append(f"{i}. {status_icon} <b>{title}</b> — {date_str} ({a.status})")

    await message.answer("\n".join(lines), parse_mode="HTML", reply_markup=_main_menu_kb(lang))


@router.message(Command("analyze"))
async def cmd_analyze(message: Message, state: FSMContext) -> None:
    lang = _lang(message)
    current = await state.get_state()
    if current == AnalyzeState.running:
        await message.answer(t("already_running", lang))
        return
    await state.set_state(AnalyzeState.waiting_for_channel)
    await message.answer(t("send_channel", lang), parse_mode="HTML")


@router.message(AnalyzeState.waiting_for_channel)
async def handle_channel_input(message: Message, state: FSMContext) -> None:
    lang = _lang(message)
    raw = (message.text or "").strip()
    if not raw:
        await message.answer(t("send_channel_prompt", lang))
        return

    # Validate input
    try:
        username = parse_channel_identifier(raw)
    except ValueError:
        await message.answer(t("invalid_channel", lang), parse_mode="HTML")
        return

    await state.set_state(AnalyzeState.running)

    progress = await message.answer(
        t("analyzing", lang, username=username, stage=t("progress_starting", lang)),
        parse_mode="HTML",
    )

    async def update_progress(stage: str) -> None:
        try:
            await progress.edit_text(
                t("analyzing", lang, username=username, stage=stage),
                parse_mode="HTML",
            )
        except Exception:
            pass

    try:
        async with async_session() as session:
            metrics, pdf_path = await asyncio.wait_for(
                run_analysis(
                    raw,
                    session=session,
                    requested_by=message.from_user.id if message.from_user else None,
                    source="bot",
                    progress_callback=update_progress,
                    lang=lang,
                ),
                timeout=settings.ANALYSIS_TIMEOUT,
            )

        # Send professional summary
        summary = _build_summary(metrics, lang)
        await message.answer(summary, parse_mode="HTML")

        # Send PDF
        if os.path.exists(pdf_path):
            doc = FSInputFile(pdf_path, filename=f"analytics_{username}.pdf")
            await message.answer_document(doc, reply_markup=_after_report_kb(lang))
        else:
            await message.answer(
                t("error_pdf_not_found", lang),
                reply_markup=_main_menu_kb(lang),
            )

    except asyncio.TimeoutError:
        await message.answer(t("error_timeout", lang), reply_markup=_main_menu_kb(lang))
    except ValueError as e:
        error_msg = str(e).lower()
        if "not a channel" in error_msg:
            await message.answer(t("error_not_channel", lang))
        elif "cannot parse" in error_msg:
            await message.answer(t("error_invalid_link", lang))
        else:
            await message.answer(f"❌ {e}")
    except Exception as e:
        logger.error(f"Analysis failed for {raw}: {e}", exc_info=True)
        error_msg = str(e).lower()
        if "no user has" in error_msg or "could not find" in error_msg:
            await message.answer(t("error_not_found", lang))
        elif "flood" in error_msg:
            await message.answer(t("error_flood", lang))
        else:
            await message.answer(
                t("error_generic", lang),
                reply_markup=_main_menu_kb(lang),
            )
    finally:
        await state.clear()
        try:
            await progress.delete()
        except Exception:
            pass
