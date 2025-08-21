from __future__ import annotations

import logging
import os
from typing import Any, Optional, cast

from aiogram import Bot, F, Router, types
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    MenuButtonDefault,
    MenuButtonWebApp,
    WebAppInfo,
)
from aiogram_i18n import I18nContext

from bot.config import settings
from bot.database.repositories import UserRepository
from bot.services.subscription_service import SubscriptionService

router = Router()
log = logging.getLogger(__name__)


def _chat_id_of(msg: types.Message) -> int | None:
    if msg.chat:
        return msg.chat.id
    if msg.from_user:
        return msg.from_user.id
    return None


def _get_webapp_url() -> str | None:
    """TWA URL ni settings yoki env dan oladi."""
    try:
        twa = getattr(settings, "TWA_HOST_URL", None)
        if twa:
            return str(twa)
    except Exception:
        pass
    return os.getenv("WEBAPP_URL")


def _is_public_https(url: str) -> bool:
    return (
        url.startswith("https://")
        and not url.startswith("https://localhost")
        and not url.startswith("https://127.")
        and not url.startswith("https://0.0.0.0")
    )


def _build_dashboard_kb(i18n: Any) -> tuple[InlineKeyboardMarkup | None, bool]:
    """
    HTTPS bo'lsa WebApp tugmasi (Telegram ichida).
    HTTPS bo‘lmasa — hech qanday tugma yubormaymiz (Telegram localhost URL'larini rad etadi).
    return: (markup, is_webapp)
    """
    text = i18n.get("menu-button-dashboard")
    url = _get_webapp_url()
    if not url:
        return None, False

    if _is_public_https(url):
        btn = InlineKeyboardButton(text=text, web_app=WebAppInfo(url=url))
        return InlineKeyboardMarkup(inline_keyboard=[[btn]]), True

    # non-HTTPS yoki lokal — tugma yubormaymiz
    return None, False


async def _set_webapp_menu_or_default(message: types.Message, i18n: Any) -> None:
    """
    Persistent menu tugmasi: HTTPS bo‘lsa WebApp, bo‘lmasa default.
    """
    bot = cast(Optional[Bot], message.bot)
    chat_id = _chat_id_of(message)
    if bot is None or chat_id is None:
        return

    text = i18n.get("menu-button-dashboard")
    webapp_url = _get_webapp_url()

    async def _set_default():
        try:
            await bot.set_chat_menu_button(
                chat_id=chat_id, menu_button=MenuButtonDefault()
            )
        except Exception as e:
            log.warning("set_chat_menu_button (default) failed: %s", e)

    if not webapp_url or not _is_public_https(webapp_url):
        if webapp_url:
            log.warning("WEBAPP_URL is not HTTPS (%s); using default menu.", webapp_url)
        await _set_default()
        return

    try:
        await bot.set_chat_menu_button(
            chat_id=chat_id,
            menu_button=MenuButtonWebApp(text=text, web_app=WebAppInfo(url=webapp_url)),
        )
    except Exception as e:
        log.warning("set_chat_menu_button (webapp) failed: %s", e)
        await _set_default()


@router.message(CommandStart())
async def cmd_start(
    message: types.Message,
    user_repo: UserRepository,
    i18n: I18nContext,
):
    # user ro'yxatdan o'tkazish (DB bo'lmasa jim)
    uid = message.from_user.id if message.from_user else None
    uname = message.from_user.username if message.from_user else None
    if uid is not None:
        try:
            await user_repo.create_user(uid, uname)
        except Exception as e:
            log.warning("create_user failed: %s", e)

    # Persistent menu tugmasi
    await _set_webapp_menu_or_default(message, i18n)

    # Xabar ichiga ham tugma qo'yamiz (faqat public HTTPS bo'lsa)
    kb, _ = _build_dashboard_kb(i18n)
    full_name = message.from_user.full_name if message.from_user else "there"
    await message.answer(
        i18n.get("start_message", user_name=full_name), reply_markup=kb
    )


@router.message(F.web_app_data)
async def handle_web_app_data(message: types.Message, i18n: I18nContext):
    await message.answer(i18n.get("twa-data-received-post"))


@router.message(F.text == "/myplan")
async def cmd_myplan(
    message: types.Message,
    subscription_service: SubscriptionService,
    i18n: I18nContext,
):
    uid = message.from_user.id if message.from_user else None
    status: Any = None
    if uid is not None:
        try:
            if hasattr(subscription_service, "get_user_subscription_status"):
                status = await getattr(
                    subscription_service, "get_user_subscription_status"
                )(uid)
            elif hasattr(subscription_service, "get_subscription_status"):
                status = await getattr(subscription_service, "get_subscription_status")(
                    uid
                )
            elif hasattr(subscription_service, "get_user_plan"):
                status = await getattr(subscription_service, "get_user_plan")(uid)
        except Exception as e:
            log.warning("subscription status fetch failed: %s", e)

    if not status:
        await message.answer(i18n.get("myplan-error"))
        return

    plan_name = (getattr(status, "plan_name", None) or "free").capitalize()
    cur_channels = int(getattr(status, "current_channels", 0) or 0)
    max_channels = int(getattr(status, "max_channels", -1) or -1)
    cur_posts = int(getattr(status, "current_posts_this_month", 0) or 0)
    max_posts = int(getattr(status, "max_posts_per_month", -1) or -1)

    channels_line = f"• Channels: {cur_channels}/" + (
        "∞" if max_channels == -1 else str(max_channels)
    )
    posts_line = f"• Posts (this month): {cur_posts}/" + (
        "∞" if max_posts == -1 else str(max_posts)
    )

    lines = [
        i18n.get("myplan-header"),
        i18n.get("myplan-plan-name", name=plan_name),
        channels_line,
        posts_line,
        "",
        i18n.get("myplan-upgrade-prompt"),
    ]
    await message.answer("\n".join(lines))


@router.message(Command("dashboard"))
async def cmd_dashboard(message: types.Message, i18n: I18nContext):
    kb, is_webapp = _build_dashboard_kb(i18n)
    if not kb:
        # HTML parse-mode’da burchak qavs ishlatmaymiz
        msg = (
            "Dashboard URL topilmadi yoki HTTPS emas.\n"
            "Dev uchun Codespaces/Ngrok HTTPS URL qo'ying:\n"
            "WEBAPP_URL=https://YOUR_PUBLIC_HOST/"
        )
        await message.answer(msg)
        return
    await message.answer(i18n.get("menu-button-dashboard"), reply_markup=kb)
