from __future__ import annotations

import shlex
from datetime import datetime, timezone
from typing import Optional, cast

from aiogram import Router, types, Bot
from aiogram.filters import Command, CommandObject
from aiogram_i18n import I18nContext

from bot.database.repositories import ChannelRepository
from bot.services.analytics_service import AnalyticsService
from bot.services.guard_service import GuardService
from bot.services.scheduler_service import SchedulerService
from bot.services.prometheus_service import prometheus_service

router = Router()


# ------- helpers -------


def _bot_of(msg: types.Message) -> Optional[Bot]:
    return cast(Optional[Bot], msg.bot)


def _uid_of(msg: types.Message) -> Optional[int]:
    return msg.from_user.id if msg.from_user else None


# A helper function to verify channel ownership
async def get_and_verify_channel(
    message: types.Message,
    channel_username: str,
    channel_repo: ChannelRepository,
    i18n: I18nContext,
) -> Optional[int]:
    """
    Kanal mavjudligini, DBda ro'yxatdan o'tganini va aynan shu userga tegishliligini tekshiradi.
    Muvaffaqiyatda channel_id qaytaradi, aks holda None va tegishli xabar yuboradi.
    """
    bot = _bot_of(message)
    uid = _uid_of(message)
    if bot is None or uid is None:
        await message.reply(
            i18n.get("guard-channel-not-found", channel_name=channel_username)
        )
        return None

    # Telegramdan kanalni olish
    try:
        channel = await bot.get_chat(chat_id=channel_username)
    except Exception:
        await message.reply(
            i18n.get("guard-channel-not-found", channel_name=channel_username)
        )
        return None

    # DBdan tekshirish
    try:
        db_channel = await channel_repo.get_channel_by_id(channel.id)
    except Exception:
        db_channel = None

    if not db_channel:
        await message.reply(i18n.get("guard-channel-not-registered"))
        return None

    try:
        owner_id = db_channel["user_id"]
    except Exception:
        owner_id = None

    if owner_id != uid:
        await message.reply(i18n.get("guard-channel-not-owner"))
        return None

    return channel.id


# ------- handlers -------


@router.message(Command("add_channel"))
async def add_channel_handler(
    message: types.Message,
    command: CommandObject,
    channel_repo: ChannelRepository,
    i18n: I18nContext,
):
    prometheus_service.record_telegram_update("add_channel")
    channel_username = command.args
    if not channel_username or not channel_username.startswith("@"):
        await message.reply(i18n.get("add-channel-usage"))
        return

    bot = _bot_of(message)
    uid = _uid_of(message)
    if bot is None or uid is None:
        await message.reply(
            i18n.get("add-channel-not-found", channel_name=channel_username)
        )
        return

    try:
        channel = await bot.get_chat(chat_id=channel_username)
    except Exception:
        await message.reply(
            i18n.get("add-channel-not-found", channel_name=channel_username)
        )
        return

    # Store basic channel information in the database
    try:
        await channel_repo.create_channel(
            channel_id=channel.id,
            user_id=uid,
            title=channel.title or "",
            username=getattr(channel, "username", None) or "",
        )
    except Exception:
        # DB bo'lmasa jim/ogohlantirishsiz o'tamiz
        pass

    await message.reply(
        i18n.get(
            "add-channel-success",
            channel_title=channel.title or channel_username,
            channel_id=channel.id,
        )
    )


# --- GUARD MODULE ---


@router.message(Command("add_word"))
async def add_word_handler(
    message: types.Message,
    command: CommandObject,
    channel_repo: ChannelRepository,
    guard_service: GuardService,
    i18n: I18nContext,
):
    args = command.args
    if not args:
        await message.reply(i18n.get("guard-add-usage"))
        return

    parts = args.split()
    if len(parts) != 2:
        await message.reply(i18n.get("guard-add-usage"))
        return

    channel_username, word = parts
    channel_id = await get_and_verify_channel(
        message, channel_username, channel_repo, i18n
    )
    if channel_id is None:
        return

    try:
        await guard_service.add_word(channel_id, word)
    except Exception:
        pass

    await message.reply(
        i18n.get("guard-word-added", word=word, channel_name=channel_username)
    )


@router.message(Command("remove_word"))
async def remove_word_handler(
    message: types.Message,
    command: CommandObject,
    channel_repo: ChannelRepository,
    guard_service: GuardService,
    i18n: I18nContext,
):
    args = command.args
    if not args:
        await message.reply(i18n.get("guard-remove-usage"))
        return

    parts = args.split()
    if len(parts) != 2:
        await message.reply(i18n.get("guard-remove-usage"))
        return

    channel_username, word = parts
    channel_id = await get_and_verify_channel(
        message, channel_username, channel_repo, i18n
    )
    if channel_id is None:
        return

    try:
        await guard_service.remove_word(channel_id, word)
    except Exception:
        pass

    await message.reply(
        i18n.get("guard-word-removed", word=word, channel_name=channel_username)
    )


@router.message(Command("list_words"))
async def list_words_handler(
    message: types.Message,
    command: CommandObject,
    channel_repo: ChannelRepository,
    guard_service: GuardService,
    i18n: I18nContext,
):
    channel_username = command.args
    if not channel_username:
        await message.reply(i18n.get("guard-list-usage"))
        return

    channel_id = await get_and_verify_channel(
        message, channel_username, channel_repo, i18n
    )
    if channel_id is None:
        return

    try:
        words = await guard_service.list_words(channel_id)
    except Exception:
        words = []

    if not words:
        await message.reply(i18n.get("guard-list-empty"))
        return

    response_text = (
        i18n.get("guard-list-header", channel_name=channel_username) + "\n\n"
    )
    response_text += "\n".join([i18n.get("guard-list-item", word=w) for w in words])
    await message.reply(response_text)


# --- SCHEDULER & ANALYTICS ---


@router.message(Command("stats"))
async def get_stats_handler(
    message: types.Message,
    command: CommandObject,
    i18n: I18nContext,
    channel_repo: ChannelRepository,
    analytics_service: AnalyticsService,
):
    """Handles the /stats command, generating a chart for all or a specific channel."""
    await message.reply(i18n.get("stats-generating"))

    channel_id: Optional[int] = None
    channel_name: Optional[str] = command.args

    if channel_name:
        if not channel_name.startswith("@"):
            await message.reply(i18n.get("stats-usage"))
            return

        channel_id = await get_and_verify_channel(
            message, channel_name, channel_repo, i18n
        )
        if not channel_id:
            return

    # None => 0 (all)
    try:
        chart_image = await analytics_service.create_views_chart(channel_id or 0)
    except Exception:
        chart_image = None

    if chart_image:
        photo = types.BufferedInputFile(chart_image, filename="stats.png")
        caption = (
            i18n.get("stats-caption-specific", channel_name=channel_name)
            if channel_name
            else i18n.get("stats-caption-all")
        )
        await message.answer_photo(photo=photo, caption=caption)
    else:
        await message.answer(i18n.get("stats-no-data"))


@router.message(Command("schedule"))
async def handle_schedule(
    message: types.Message,
    command: CommandObject,
    channel_repo: ChannelRepository,
    scheduler_service: SchedulerService,
    i18n: I18nContext,
):
    prometheus_service.record_telegram_update("schedule_post")
    if command.args is None:
        await message.reply(i18n.get("schedule-usage"))
        return

    try:
        args = shlex.split(command.args)
        if len(args) != 3:
            raise ValueError()

        channel_username, dt_str, text = args

        channel_id = await get_and_verify_channel(
            message, channel_username, channel_repo, i18n
        )
        if not channel_id:
            return

        naive_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        aware_dt = naive_dt.replace(tzinfo=timezone.utc)

        if aware_dt < datetime.now(timezone.utc):
            await message.reply(i18n.get("schedule-past-time-error"))
            return

        uid = _uid_of(message)
        if uid is not None:
            try:
                await scheduler_service.schedule_post(
                    user_id=uid,
                    channel_id=channel_id,
                    post_text=text,
                    schedule_time=aware_dt,
                )
            except Exception:
                pass

        await message.reply(
            i18n.get(
                "schedule-success",
                channel_name=channel_username,
                schedule_time=aware_dt.strftime("%Y-%m-%d %H:%M %Z"),
            )
        )

    except ValueError:
        await message.reply(i18n.get("schedule-usage"))


@router.message(Command("views"))
async def get_views_handler(
    message: types.Message,
    command: CommandObject,
    analytics_service: AnalyticsService,
    i18n: I18nContext,
):
    if command.args is None:
        await message.reply(i18n.get("views-usage"))
        return

    try:
        post_id = int(command.args)
    except ValueError:
        await message.reply(i18n.get("views-invalid-id"))
        return

    uid = _uid_of(message)
    try:
        view_count = await analytics_service.get_post_views(post_id, uid or 0)
    except Exception:
        view_count = None

    if view_count is None:
        await message.reply(i18n.get("views-not-found", post_id=post_id))
        return

    await message.reply(
        i18n.get("views-success", post_id=post_id, view_count=view_count)
    )
