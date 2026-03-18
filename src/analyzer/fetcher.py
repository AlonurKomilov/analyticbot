"""Channel data fetcher — resolves channel info and fetches post history via Telethon"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime

from telethon import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import (
    Channel,
    MessageMediaDocument,
    MessageMediaPhoto,
    MessageMediaWebPage,
)

from src.config import settings

logger = logging.getLogger(__name__)

# Patterns for extracting channel username from various link formats
_LINK_PATTERNS = [
    re.compile(r"(?:https?://)?t\.me/([a-zA-Z_][\w]{3,30})", re.IGNORECASE),
    re.compile(r"@([a-zA-Z_][\w]{3,30})"),
]


@dataclass
class ChannelInfo:
    channel_id: int
    title: str
    username: str | None
    description: str | None
    member_count: int
    channel_type: str  # "channel" or "supergroup"


@dataclass
class FetchedPost:
    message_id: int
    date: datetime
    text: str | None
    views: int
    forwards: int
    replies: int
    reactions_count: int
    media_type: str | None  # "photo", "video", "document", None
    has_link: bool


@dataclass
class FetchResult:
    channel: ChannelInfo
    posts: list[FetchedPost] = field(default_factory=list)
    fetch_time: datetime = field(default_factory=datetime.utcnow)


def parse_channel_identifier(raw: str) -> str:
    """Extract channel username from a link or @-mention. Returns cleaned username."""
    raw = raw.strip()
    for pattern in _LINK_PATTERNS:
        m = pattern.search(raw)
        if m:
            return m.group(1)
    # Already a plain username
    if re.match(r"^[a-zA-Z_][\w]{3,30}$", raw):
        return raw
    raise ValueError(f"Cannot parse channel identifier from: {raw!r}")


def _classify_media(message) -> str | None:
    media = message.media
    if media is None:
        return None
    if isinstance(media, MessageMediaPhoto):
        return "photo"
    if isinstance(media, MessageMediaDocument):
        doc = media.document
        if doc and hasattr(doc, "mime_type"):
            mime = doc.mime_type or ""
            if mime.startswith("video"):
                return "video"
        return "document"
    if isinstance(media, MessageMediaWebPage):
        return None  # web previews are not "media" for content-mix purposes
    return "other"


async def fetch_channel(identifier: str, max_posts: int | None = None) -> FetchResult:
    """
    Connect to Telegram via Telethon, resolve the channel, and fetch recent posts.

    Args:
        identifier: Channel username (without @) or full t.me link.
        max_posts: Maximum posts to fetch (default from settings).

    Returns:
        FetchResult with channel info and post list.
    """
    max_posts = max_posts or settings.MAX_POSTS
    username = parse_channel_identifier(identifier)

    client = TelegramClient("analyticbot_session", settings.API_ID, settings.API_HASH)
    await client.start(phone=settings.PHONE)

    try:
        entity = await client.get_entity(username)
        if not isinstance(entity, Channel):
            raise ValueError(f"@{username} is not a channel or supergroup")

        full = await client(GetFullChannelRequest(entity))
        full_chat = full.full_chat

        channel_info = ChannelInfo(
            channel_id=entity.id,
            title=entity.title,
            username=entity.username,
            description=getattr(full_chat, "about", None),
            member_count=getattr(full_chat, "participants_count", 0) or 0,
            channel_type="supergroup" if entity.megagroup else "channel",
        )

        # Fetch posts in batches
        posts: list[FetchedPost] = []
        offset_id = 0
        batch_size = min(100, max_posts)

        while len(posts) < max_posts:
            limit = min(batch_size, max_posts - len(posts))
            history = await client(
                GetHistoryRequest(
                    peer=entity,
                    offset_id=offset_id,
                    offset_date=None,
                    add_offset=0,
                    limit=limit,
                    max_id=0,
                    min_id=0,
                    hash=0,
                )
            )

            if not history.messages:
                break

            for msg in history.messages:
                if not hasattr(msg, "id"):
                    continue  # skip service messages

                reactions_count = 0
                if hasattr(msg, "reactions") and msg.reactions:
                    for r in msg.reactions.results:
                        reactions_count += r.count

                replies_count = 0
                if hasattr(msg, "replies") and msg.replies:
                    replies_count = msg.replies.replies or 0

                has_link = False
                if msg.entities:
                    has_link = any(
                        hasattr(e, "url") or type(e).__name__ == "MessageEntityUrl"
                        for e in msg.entities
                    )

                posts.append(
                    FetchedPost(
                        message_id=msg.id,
                        date=msg.date,
                        text=msg.message,
                        views=msg.views or 0,
                        forwards=msg.forwards or 0,
                        replies=replies_count,
                        reactions_count=reactions_count,
                        media_type=_classify_media(msg),
                        has_link=has_link,
                    )
                )

            offset_id = history.messages[-1].id
            if len(history.messages) < limit:
                break

        logger.info(f"Fetched {len(posts)} posts from @{username}")
        return FetchResult(channel=channel_info, posts=posts)

    finally:
        await client.disconnect()
