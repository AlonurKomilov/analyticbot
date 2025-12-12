from __future__ import annotations

import logging
import os
from typing import Any, cast

from aiogram import Bot, F, Router, types
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    MenuButtonDefault,
    MenuButtonWebApp,
    WebAppInfo,
)
from aiogram_i18n import I18nContext

from apps.bot.config import settings
from apps.bot.services.subscription_service import SubscriptionService
from apps.di import get_container
from core.repositories.interfaces import UserRepository

router = Router()
log = logging.getLogger(__name__)


async def get_user_repository() -> UserRepository:
    """Get user repository from DI container"""
    container = get_container()
    return await container.database.user_repo()


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
            log.info(f"TWA URL from settings: {twa}")
            return str(twa)
    except Exception as e:
        log.warning(f"Error getting TWA_HOST_URL from settings: {e}")

    # Try multiple environment variable names
    env_url = os.getenv("TWA_HOST_URL") or os.getenv("WEBAPP_URL")
    if env_url:
        log.info(f"TWA URL from env: {env_url}")
    else:
        log.warning("No TWA_HOST_URL found in settings or environment")
    return env_url


def _is_public_https(url: str) -> bool:
    return (
        url.startswith("https://")
        and (not url.startswith("https://localhost"))
        and (not url.startswith("https://127."))
        and (not url.startswith("https://0.0.0.0"))
    )


def _build_dashboard_kb(i18n: Any) -> tuple[InlineKeyboardMarkup | None, bool]:
    """
    HTTPS bo'lsa WebApp tugmasi (Telegram ichida).
    HTTPS bo'lmasa — hech qanday tugma yubormaymiz (Telegram localhost URL'larni rad etadi).
    return: (markup, is_webapp)
    """
    text = i18n.get("menu-button-dashboard")
    url = _get_webapp_url()
    if not url:
        return (None, False)
    if _is_public_https(url):
        btn = InlineKeyboardButton(text=text, web_app=WebAppInfo(url=url))
        return (InlineKeyboardMarkup(inline_keyboard=[[btn]]), True)
    return (None, False)


def _build_start_menu_kb(i18n: Any) -> InlineKeyboardMarkup:
    """Build comprehensive start menu with action buttons."""
    buttons = []

    # First row: Add Channel and View Stats
    row1 = [
        InlineKeyboardButton(
            text=i18n.get("button-add-channel"), callback_data="quick_add_channel"
        ),
        InlineKeyboardButton(text=i18n.get("button-view-stats"), callback_data="quick_stats"),
    ]
    buttons.append(row1)

    # Second row: Help and Commands
    row2 = [
        InlineKeyboardButton(text=i18n.get("button-help"), callback_data="quick_help"),
        InlineKeyboardButton(text=i18n.get("button-commands"), callback_data="quick_commands"),
    ]
    buttons.append(row2)

    # Third row: Dashboard (if available)
    dashboard_kb, is_webapp = _build_dashboard_kb(i18n)
    if dashboard_kb and is_webapp:
        # Extract the dashboard button from the dashboard keyboard
        dashboard_btn = dashboard_kb.inline_keyboard[0][0]
        buttons.append([dashboard_btn])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def _set_webapp_menu_or_default(message: types.Message, i18n: Any) -> None:
    """
    Persistent menu tugmasi: HTTPS bo'lsa WebApp, bo'lmasa default.
    """
    bot = cast(Bot | None, message.bot)
    chat_id = _chat_id_of(message)
    if bot is None or chat_id is None:
        return
    text = i18n.get("menu-button-dashboard")
    webapp_url = _get_webapp_url()

    async def _set_default():
        try:
            await bot.set_chat_menu_button(chat_id=chat_id, menu_button=MenuButtonDefault())
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
async def cmd_start(message: types.Message, i18n: I18nContext):
    uid = message.from_user.id if message.from_user else None
    uname = message.from_user.username if message.from_user else None
    full_name = message.from_user.full_name if message.from_user else None

    log.info(
        f"📥 /start command received from telegram_id={uid}, username={uname}, full_name={full_name}"
    )
    log.info(f"📝 Raw message text: {message.text}")

    # Extract referral code from deep link (format: /start ref_CODE)
    referral_code = None
    if message.text:
        parts = message.text.split()
        log.info(f"📋 Message parts: {parts}")
        if len(parts) > 1 and parts[1].startswith("ref_"):
            referral_code = parts[1][4:]  # Remove "ref_" prefix
            log.info(f"🔗 Referral code detected from deep link: {referral_code}")
        else:
            log.info(f"ℹ️ No referral code in message (parts count: {len(parts)})")

    is_new_user = False
    referral_result = None
    new_user_internal_id = None

    if uid is not None:
        try:
            user_repo = await get_user_repository()

            # Check if user already exists (by telegram_id)
            existing_user = await user_repo.get_user_by_telegram_id(uid)
            if existing_user:
                log.info(f"User already exists for telegram_id {uid}")
                # If existing user came with referral code, show message that they already have account
                if referral_code:
                    log.info(f"Existing user tried to use referral code: {referral_code}")
            else:
                is_new_user = True
                # Create new user - DO NOT pass id, let repository generate it from sequence
                user_data = {
                    "username": uname,
                    "full_name": full_name,
                    "plan_id": 1,  # Default to free plan
                    "telegram_id": uid,
                    "auth_provider": "telegram",
                    "status": "active",
                }
                await user_repo.create_user(user_data)
                log.info(f"✅ Created new user for telegram_id {uid}")

                # Get the internal user ID for referral processing
                new_created_user = await user_repo.get_user_by_telegram_id(uid)
                if new_created_user:
                    new_user_internal_id = new_created_user.get("id")
                    log.info(f"New user internal ID: {new_user_internal_id}")

                # Process referral code for new users
                if referral_code and new_user_internal_id:
                    log.info(f"🎁 Processing referral for new user {uid} with code {referral_code}")
                    referral_result = await _process_referral(
                        new_user_telegram_id=uid,
                        new_user_internal_id=new_user_internal_id,
                        referral_code=referral_code,
                        new_user_name=full_name or uname or "New user",
                        bot=message.bot,
                    )
                    if referral_result:
                        log.info(f"✅ Referral processed successfully: {referral_result}")
                    else:
                        log.warning("❌ Referral processing returned None")

        except Exception as e:
            log.error(f"create_user failed: {e}", exc_info=True)

    await _set_webapp_menu_or_default(message, i18n)

    # Build comprehensive menu with action buttons
    start_kb = _build_start_menu_kb(i18n)
    user_display_name = message.from_user.full_name if message.from_user else "there"

    # Build welcome message based on scenario
    if is_new_user and referral_code and referral_result:
        # New user who joined via referral - special welcome!
        referrer_name = referral_result.get("referrer_name", "a friend")
        welcome_msg = f"""🎉 <b>Welcome to AnalyticBot, {user_display_name}!</b>

You joined via <b>{referrer_name}</b>'s referral link!

━━━━━━━━━━━━━━━━━━━━━
🎁 <b>+50 bonus credits</b> added to your account!
━━━━━━━━━━━━━━━━━━━━━

📊 Your ultimate channel analytics companion
✨ Track performance, schedule posts, and grow your audience

<b>Quick Start Guide:</b>
1️⃣ Add your first channel with /addchannel @channelname
2️⃣ View analytics with /stats
3️⃣ Get help anytime with /help

💡 <b>Tip:</b> Invite your friends to earn +100 credits per signup!

👇 <b>Choose an action below to get started!</b>"""

    elif is_new_user:
        # New user without referral
        welcome_msg = f"""🚀 <b>Welcome to AnalyticBot, {user_display_name}!</b>

📊 Your ultimate channel analytics companion
✨ Track performance, schedule posts, and grow your audience

━━━━━━━━━━━━━━━━━━━━━
🎁 <b>+50 starter credits</b> added to your account!
━━━━━━━━━━━━━━━━━━━━━

<b>Quick Start Guide:</b>
1️⃣ Add your first channel with /addchannel @channelname
2️⃣ View analytics with /stats
3️⃣ Get help anytime with /help

💡 <b>Tip:</b> Invite friends with your referral code to earn +100 credits per signup!

👇 <b>Choose an action below to get started!</b>"""

    else:
        # Existing user
        welcome_msg = i18n.get("start_message", user_name=user_display_name)

    await message.answer(welcome_msg, reply_markup=start_kb, parse_mode="HTML")


async def _process_referral(
    new_user_telegram_id: int,
    new_user_internal_id: int,
    referral_code: str,
    new_user_name: str,
    bot: Bot | None,
) -> dict | None:
    """Process referral code for a new user and notify the referrer"""
    try:
        from apps.di import get_container

        container = get_container()
        pool = await container.database.asyncpg_pool()

        async with pool.acquire() as conn:
            # Get the referrer by code
            referrer = await conn.fetchrow(
                "SELECT id, username, full_name, telegram_id FROM users WHERE referral_code = $1",
                referral_code.upper(),
            )
            if not referrer:
                log.warning(f"❌ Invalid referral code: {referral_code}")
                return None

            referrer_id = referrer["id"]
            referrer_name = referrer["full_name"] or referrer["username"] or "Your friend"
            referrer_telegram_id = referrer["telegram_id"]

            log.info(
                f"Found referrer: {referrer_id} ({referrer_name}), telegram_id: {referrer_telegram_id}"
            )

            # Check if already referred (use correct table: user_referrals)
            existing = await conn.fetchval(
                "SELECT 1 FROM user_referrals WHERE referred_user_id = $1",
                new_user_internal_id,
            )
            if existing:
                log.info(f"User {new_user_internal_id} already has a referrer")
                return None

            # Get referrer's current referral count (use correct table and column)
            referral_count = (
                await conn.fetchval(
                    "SELECT COUNT(*) FROM user_referrals WHERE referrer_user_id = $1 AND status = 'completed'",
                    referrer_id,
                )
                or 0
            )

            # Check if referrer has user_credits record, create if not
            referrer_credits = await conn.fetchval(
                "SELECT 1 FROM user_credits WHERE user_id = $1", referrer_id
            )
            if not referrer_credits:
                await conn.execute(
                    """
                    INSERT INTO user_credits (user_id, balance, lifetime_earned, lifetime_spent, daily_streak)
                    VALUES ($1, 0, 0, 0, 0)
                """,
                    referrer_id,
                )
                log.info(f"Created user_credits record for referrer {referrer_id}")

            # Apply referral in transaction
            async with conn.transaction():
                # Create referral record (use correct table: user_referrals, column: referrer_user_id)
                await conn.execute(
                    """
                    INSERT INTO user_referrals (referrer_user_id, referred_user_id, referral_code, status, completed_at, credits_awarded)
                    VALUES ($1, $2, $3, 'completed', NOW(), 100)
                """,
                    referrer_id,
                    new_user_internal_id,
                    referral_code.upper(),
                )
                log.info("✅ Created referral record in user_referrals")

                # Award credits to referrer (100 credits)
                await conn.execute(
                    """
                    UPDATE user_credits SET
                        balance = balance + 100,
                        lifetime_earned = lifetime_earned + 100
                    WHERE user_id = $1
                """,
                    referrer_id,
                )
                log.info(f"✅ Awarded 100 credits to referrer {referrer_id}")

                # Award credits to new user (50 credits bonus)
                await conn.execute(
                    """
                    INSERT INTO user_credits (user_id, balance, lifetime_earned, lifetime_spent, daily_streak)
                    VALUES ($1, 50, 50, 0, 0)
                    ON CONFLICT (user_id) DO UPDATE SET
                        balance = user_credits.balance + 50,
                        lifetime_earned = user_credits.lifetime_earned + 50
                """,
                    new_user_internal_id,
                )
                log.info(f"✅ Awarded 50 bonus credits to new user {new_user_internal_id}")

                # Log transactions (get current balances for balance_after field)
                referrer_balance = (
                    await conn.fetchval(
                        "SELECT balance FROM user_credits WHERE user_id = $1",
                        referrer_id,
                    )
                    or 0
                )

                new_user_balance = (
                    await conn.fetchval(
                        "SELECT balance FROM user_credits WHERE user_id = $1",
                        new_user_internal_id,
                    )
                    or 50
                )

                await conn.execute(
                    """
                    INSERT INTO credit_transactions (user_id, amount, balance_after, type, description)
                    VALUES ($1, 100, $2, 'referral_reward', $3)
                """,
                    referrer_id,
                    referrer_balance,
                    f"Referral bonus: {new_user_name} joined via your link",
                )

                await conn.execute(
                    """
                    INSERT INTO credit_transactions (user_id, amount, balance_after, type, description)
                    VALUES ($1, 50, $2, 'referral_bonus', $3)
                """,
                    new_user_internal_id,
                    new_user_balance,
                    f"Welcome bonus from {referrer_name}'s referral",
                )

            log.info(
                f"🎉 Referral processed successfully: {referrer_id} referred {new_user_internal_id} via code {referral_code}"
            )

            # 🔔 Notify the referrer about the successful referral!
            if bot and referrer_telegram_id:
                try:
                    new_total = referral_count + 1
                    notification_msg = f"""🎉 <b>Congratulations!</b> 🎉

Someone just joined using your referral link!

━━━━━━━━━━━━━━━━━━━━━
👤 <b>New member:</b> {new_user_name}
💰 <b>You earned:</b> +100 credits!
━━━━━━━━━━━━━━━━━━━━━

📊 <b>Your Referral Stats:</b>
• Total referrals: {new_total}
• Total earned: {new_total * 100} credits

Keep sharing your link to earn more! 🚀"""

                    await bot.send_message(
                        chat_id=referrer_telegram_id,
                        text=notification_msg,
                        parse_mode="HTML",
                    )
                    log.info(f"📬 Notified referrer {referrer_telegram_id} about new referral")
                except Exception as notify_err:
                    log.warning(f"Failed to notify referrer: {notify_err}")
            else:
                log.warning(
                    f"Could not notify referrer: bot={bot is not None}, telegram_id={referrer_telegram_id}"
                )

            return {
                "success": True,
                "referrer_name": referrer_name,
                "referrer_id": referrer_id,
                "credits_received": 50,
            }

    except Exception as e:
        log.error(f"❌ Failed to process referral: {e}", exc_info=True)
        return None


@router.callback_query(F.data == "quick_add_channel")
async def callback_quick_add_channel(callback: CallbackQuery, i18n: I18nContext):
    if callback.message:
        await callback.message.answer(i18n.get("add-channel-usage"))
    await callback.answer()


@router.callback_query(F.data == "quick_stats")
async def callback_quick_stats(callback: CallbackQuery, i18n: I18nContext):
    if callback.message:
        await callback.message.answer(i18n.get("stats-generating"))
    # Here you would normally call the stats handler
    await callback.answer()


@router.callback_query(F.data == "quick_help")
async def callback_quick_help(callback: CallbackQuery, i18n: I18nContext):
    if callback.message:
        await callback.message.answer(i18n.get("help-message"))
    await callback.answer()


@router.callback_query(F.data == "quick_commands")
async def callback_quick_commands(callback: CallbackQuery, i18n: I18nContext):
    if callback.message:
        await callback.message.answer(i18n.get("commands-list"))
    await callback.answer()


@router.message(F.web_app_data)
async def handle_web_app_data(message: types.Message, i18n: I18nContext):
    await message.answer(i18n.get("twa-data-received-post"))


@router.message(F.text == "/myplan")
async def cmd_myplan(
    message: types.Message, subscription_service: SubscriptionService, i18n: I18nContext
):
    uid = message.from_user.id if message.from_user else None
    status: Any = None
    if uid is not None:
        try:
            status = await subscription_service.get_usage_status(uid)
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
        msg = "Dashboard URL topilmadi yoki HTTPS emas.\nDev uchun server IP URL qo'ying:\nTWA_HOST_URL=https://84dp9jc9-3000.euw.devtunnels.ms/"
        await message.answer(msg)
        return
    await message.answer(i18n.get("menu-button-dashboard"), reply_markup=kb)
