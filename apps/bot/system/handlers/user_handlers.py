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

from apps.bot.system.config import settings
from apps.bot.system.services.subscription_service import SubscriptionService
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


def _parse_user_agent(user_agent: str) -> str:
    """Parse user agent string to extract browser and OS info."""
    if not user_agent:
        return "Unknown Browser"

    ua = user_agent.lower()

    # Detect browser
    browser = "Unknown Browser"
    if "edg/" in ua or "edge/" in ua:
        browser = "Edge"
    elif "chrome/" in ua and "safari/" in ua:
        browser = "Chrome"
    elif "firefox/" in ua:
        browser = "Firefox"
    elif "safari/" in ua and "chrome/" not in ua:
        browser = "Safari"
    elif "opera" in ua or "opr/" in ua:
        browser = "Opera"

    # Try to get version
    import re

    version_match = None
    if browser == "Chrome":
        version_match = re.search(r"chrome/(\d+)", ua)
    elif browser == "Firefox":
        version_match = re.search(r"firefox/(\d+)", ua)
    elif browser == "Safari":
        version_match = re.search(r"version/(\d+)", ua)
    elif browser == "Edge":
        version_match = re.search(r"edg/(\d+)", ua)

    if version_match:
        browser = f"{browser} {version_match.group(1)}"

    # Detect OS
    os_name = "Unknown OS"
    if "windows" in ua:
        os_name = "Windows"
    elif "mac os" in ua or "macintosh" in ua:
        os_name = "macOS"
    elif "linux" in ua:
        if "android" in ua:
            os_name = "Android"
        else:
            os_name = "Linux"
    elif "iphone" in ua or "ipad" in ua:
        os_name = "iOS"

    return f"{browser} on {os_name}"


async def _handle_bot_login(
    message: types.Message,
    telegram_id: int | None,
    username: str | None,
    full_name: str | None,
    login_code: str,
    i18n: I18nContext,
) -> None:
    """Handle bot-based login from analyticbot.org website."""
    import aiohttp

    if telegram_id is None:
        await message.answer(
            "❌ Unable to identify your Telegram account. Please try again.",
            parse_mode="HTML",
        )
        return

    log.info(f"🔐 Processing bot login for telegram_id={telegram_id}, code={login_code}")

    # Call the API to confirm the login
    api_base_url = os.getenv("API_BASE_URL", "http://localhost:11400")
    confirm_url = f"{api_base_url}/auth/telegram/bot-login/confirm"

    # Get user's photo URL if available
    photo_url = None
    try:
        if message.from_user:
            photos = await message.bot.get_user_profile_photos(telegram_id, limit=1)
            if photos.total_count > 0:
                # Get the smallest photo (last in the list)
                photo = photos.photos[0][-1]
                file = await message.bot.get_file(photo.file_id)
                if file.file_path:
                    photo_url = (
                        f"https://api.telegram.org/file/bot{message.bot.token}/{file.file_path}"
                    )
    except Exception as e:
        log.warning(f"Failed to get user photo: {e}")

    payload = {
        "login_code": login_code,
        "telegram_id": telegram_id,
        "username": username,
        "first_name": full_name.split()[0] if full_name else (username or "User"),
        "last_name": (
            " ".join(full_name.split()[1:]) if full_name and len(full_name.split()) > 1 else None
        ),
        "photo_url": photo_url,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(confirm_url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    log.info(f"✅ Bot login confirmed for telegram_id={telegram_id}")

                    # Parse client info for display
                    client_info = result.get("client_info", {})
                    client_ip = client_info.get("client_ip", "Unknown")
                    user_agent = client_info.get("user_agent", "")
                    session_token = result.get("session_token", "")

                    # Parse browser and OS from user agent
                    browser_info = _parse_user_agent(user_agent)

                    # Build session info message
                    session_info = f"""<b>🌐 Browser:</b> {browser_info}
<b>📍 IP:</b> {client_ip}"""

                    # Create terminate session keyboard
                    terminate_kb = (
                        InlineKeyboardMarkup(
                            inline_keyboard=[
                                [
                                    InlineKeyboardButton(
                                        text="🚫 Terminate session",
                                        callback_data=f"terminate_session:{session_token[:50]}",
                                    )
                                ]
                            ]
                        )
                        if session_token
                        else None
                    )

                    # Send success message to user with session info
                    await message.answer(
                        f"""✅ <b>Login Successful!</b>

🎉 Welcome, <b>{full_name or username or "User"}</b>!

You have successfully logged in to <b>AnalyticBot</b>.

━━━━━━━━━━━━━━━━━━━━━
{session_info}
━━━━━━━━━━━━━━━━━━━━━

🔄 <b>You can now close the Telegram tab</b> and return to the website - you should be automatically logged in.

💡 Press 'Terminate session' to log out from this device.

📊 <a href="https://analyticbot.org">Go to AnalyticBot.org</a>""",
                        parse_mode="HTML",
                        disable_web_page_preview=True,
                        reply_markup=terminate_kb,
                    )
                elif response.status == 404:
                    log.warning(f"❌ Login code expired or invalid: {login_code}")
                    await message.answer(
                        """❌ <b>Login Failed</b>

The login link has expired or is invalid.

Please go back to <b>analyticbot.org</b> and try again.

━━━━━━━━━━━━━━━━━━━━━
📊 <a href="https://analyticbot.org">Go to AnalyticBot.org</a>
━━━━━━━━━━━━━━━━━━━━━""",
                        parse_mode="HTML",
                        disable_web_page_preview=True,
                    )
                else:
                    error_text = await response.text()
                    log.error(f"❌ Bot login API error: {response.status} - {error_text}")
                    await message.answer(
                        """❌ <b>Login Error</b>

Something went wrong. Please try again later.

If the problem persists, contact support.""",
                        parse_mode="HTML",
                    )
    except Exception as e:
        log.error(f"❌ Bot login request failed: {e}", exc_info=True)
        await message.answer(
            """❌ <b>Connection Error</b>

Unable to connect to the server. Please try again later.""",
            parse_mode="HTML",
        )


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

    # Check for login deep link (format: /start login_CODE)
    if message.text:
        parts = message.text.split()
        if len(parts) > 1 and parts[1].startswith("login_"):
            login_code = parts[1][6:]  # Remove "login_" prefix
            log.info(f"🔐 Login code detected from deep link: {login_code}")
            await _handle_bot_login(message, uid, uname, full_name, login_code, i18n)
            return

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


@router.callback_query(F.data.startswith("terminate_session:"))
async def callback_terminate_session(callback: CallbackQuery):
    """Handle terminate session button click from bot login success message."""
    import aiohttp

    if not callback.data or not callback.from_user:
        await callback.answer("Unable to process request", show_alert=True)
        return

    # Extract session token from callback data
    session_token_partial = callback.data.replace("terminate_session:", "")
    telegram_id = callback.from_user.id

    log.info(f"🔐 User {telegram_id} requested session termination")

    # Call the API to terminate the session
    api_base_url = os.getenv("API_BASE_URL", "http://localhost:11400")
    terminate_url = f"{api_base_url}/auth/telegram/bot-login/terminate-session"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                terminate_url,
                params={
                    "telegram_id": telegram_id,
                    "session_token": session_token_partial,
                },
            ) as response:
                if response.status == 200:
                    log.info(f"✅ Session terminated for user {telegram_id}")

                    # Update the message to show session was terminated
                    if callback.message:
                        try:
                            await callback.message.edit_text(
                                """✅ <b>Session Terminated</b>

Your login session has been successfully ended.

If you want to log in again, visit:
📊 <a href="https://analyticbot.org">AnalyticBot.org</a>""",
                                parse_mode="HTML",
                                disable_web_page_preview=True,
                            )
                        except Exception as edit_err:
                            log.warning(f"Failed to edit message: {edit_err}")

                    await callback.answer("✅ Session terminated", show_alert=True)
                else:
                    error_text = await response.text()
                    log.error(f"❌ Session termination failed: {response.status} - {error_text}")
                    await callback.answer("❌ Failed to terminate session", show_alert=True)
    except Exception as e:
        log.error(f"❌ Session termination request failed: {e}", exc_info=True)
        await callback.answer("❌ Connection error", show_alert=True)


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
