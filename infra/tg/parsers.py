"""Message and update parsers for MTProto data normalization.

This module provides functions to normalize Telethon message/update objects
into plain dictionaries that can be consumed by repositories without
dependency on Telethon types.
"""

import logging
import re
from datetime import datetime
from typing import Any

from telethon import utils
from telethon.tl.types import MessageMediaWebPage, MessageEntityUrl, MessageEntityTextUrl

logger = logging.getLogger(__name__)

# URL regex pattern for link extraction
URL_PATTERN = re.compile(
    r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
)

# Telegram link patterns
TELEGRAM_LINK_PATTERN = re.compile(r"t\.me/[a-zA-Z0-9_]+(?:/\d+)?")


def normalize_message(message: Any) -> dict[str, Any] | None:
    """Normalize a Telethon message object to a plain dictionary.

    Args:
        message: Telethon message object

    Returns:
        Dictionary with normalized message data containing:
        - channel: channel information
        - post: message/post information
        - metrics: engagement metrics
        Returns None if normalization fails.
    """
    try:
        # Extract basic message info
        message_id = getattr(message, "id", 0)
        text = getattr(message, "message", "") or ""
        date = getattr(message, "date", datetime.utcnow())

        # Extract peer/channel info
        peer = getattr(message, "peer_id", None)
        channel_id = None
        channel_username = None
        channel_title = None
        is_supergroup = False

        if peer:
            # Use Telethon's official utility to convert peer to display ID
            # This handles all peer types correctly:
            # - Channels/Supergroups: adds -100 prefix (e.g., -1002678877654)
            # - Regular chats: returns negative chat_id (e.g., -123456)
            # - Users: returns positive user_id (e.g., 844338517)
            display_id = utils.get_peer_id(peer)
            # Store as positive ID in our database
            channel_id = abs(display_id)

        # Try to get channel info from message
        if hasattr(message, "chat"):
            chat = message.chat
            if chat:
                # If we didn't get channel_id from peer, use chat.id
                if channel_id is None:
                    raw_id = getattr(chat, "id", None)
                    if raw_id:
                        channel_id = abs(raw_id)
                channel_username = getattr(chat, "username", None)
                channel_title = getattr(chat, "title", None)
                is_supergroup = getattr(chat, "megagroup", False)

        # ========== MEDIA TYPE DETECTION (FIXED) ==========
        # Detect media types based on Telegram message structure
        # Uses Telethon's convenience properties which match Telegram's own categorization
        #
        # Telethon provides these properties on message:
        # - message.photo: Photo (not from web preview)
        # - message.video: Video file (MessageMediaDocument with video attributes)
        # - message.audio: Audio file (MessageMediaDocument with audio mime, not voice)
        # - message.voice: Voice message (MessageMediaDocument with voice=True attribute)
        # - message.video_note: Round video message
        # - message.sticker: Sticker (MessageMediaDocument with sticker attribute)
        # - message.gif: GIF animation (MessageMediaDocument with animated attribute)
        # - message.document: Any other document (falls through if not specialized)
        # - message.poll: Poll
        # - message.contact: Contact
        # - message.geo: Location
        # - message.web_preview: Web page preview
        
        has_video = False
        has_photo = False
        has_audio = False
        has_document = False
        has_voice = False
        has_gif = False
        has_sticker = False
        has_poll = False
        has_video_note = False
        has_web_preview = False
        
        # IMPORTANT: Check for web preview FIRST before other media types
        # Web page previews may contain photos/videos but Telegram counts them as "Shared Links"
        # not as Photos or Videos. We need to detect this early.
        media = getattr(message, "media", None)
        if isinstance(media, MessageMediaWebPage):
            has_web_preview = True
        
        # Use Telethon's convenience properties - they match Telegram's categorization exactly
        # BUT: Don't count photos/videos if they're from a web preview
        if getattr(message, "photo", None) and not has_web_preview:
            has_photo = True
        
        if getattr(message, "video", None):
            has_video = True
        
        if getattr(message, "video_note", None):
            # IMPORTANT: Video notes (round videos) count as "Voice" in Telegram stats!
            # Telegram's media statistics groups video notes with voice messages.
            # So we set has_video_note but do NOT set has_video (video_note is separate)
            has_video_note = True
            has_video = False  # Undo video flag - video notes are NOT counted as videos
            has_voice = True  # Telegram counts video notes as voice/audio category
        
        if getattr(message, "gif", None):
            has_gif = True
            has_video = False  # GIFs are technically videos but should be counted separately
        
        if getattr(message, "sticker", None):
            has_sticker = True
        
        if getattr(message, "voice", None):
            has_voice = True
        
        if getattr(message, "audio", None):
            has_audio = True
        
        # Only set has_document for actual files (not videos, audio, etc.)
        # Telethon's message.document returns the document for ANY document type,
        # so we only set has_document if none of the specialized types matched
        if getattr(message, "document", None):
            if not (has_video or has_audio or has_voice or has_gif or has_sticker or has_video_note):
                has_document = True
        
        if getattr(message, "poll", None):
            has_poll = True
        
        # Check for links in text (matches Telegram's "shared links" count)
        # IMPORTANT: Telegram's "Shared links" category counts messages that have:
        # 1. URL entities (MessageEntityUrl, MessageEntityTextUrl) - PRIMARY source
        # 2. MessageMediaWebPage - counted as link too
        # We already detected has_web_preview above
        has_link = False
        entities = getattr(message, "entities", None) or []
        for entity in entities:
            if isinstance(entity, (MessageEntityUrl, MessageEntityTextUrl)):
                has_link = True
                break
        
        # Web preview always counts as link
        if has_web_preview:
            has_link = True
        
        # Aggregate flags for backward compatibility
        # has_media = any visual media (photo, gif, sticker) - NOT video (video is separate)
        has_media = has_photo or has_gif or has_sticker
        
        # Calculate text length for content analysis
        text_length = len(text) if text else 0
        # ========== END MEDIA TYPE DETECTION ==========

        # Extract metrics
        views = getattr(message, "views", 0) or 0
        forwards = getattr(message, "forwards", 0) or 0

        # Extract reply/comment metrics
        # Distinguish between:
        # - Discussion group comments (for channels with linked discussion groups)
        # - Direct threaded replies (for groups/supergroups/channels)
        comments_count = 0  # Discussion group comments
        replies_count = 0  # Direct threaded replies
        total_replies = 0  # Total (for logging/debugging)

        if hasattr(message, "replies") and message.replies:
            total_replies = getattr(message.replies, "replies", 0) or 0
            is_comments_enabled = getattr(message.replies, "comments", False)

            # Determine if this is a channel (not a supergroup)
            is_channel = not is_supergroup and channel_id and channel_id > 0

            if is_channel and is_comments_enabled:
                # Channel with discussion group - these are comments
                comments_count = total_replies
                replies_count = 0
            elif is_channel and not is_comments_enabled:
                # Channel with threaded replies enabled (no discussion group)
                comments_count = 0
                replies_count = total_replies
            else:
                # Group or supergroup - these are threaded replies
                comments_count = 0
                replies_count = total_replies

        # Extract reactions
        reactions = []
        reactions_count = 0
        if hasattr(message, "reactions") and message.reactions:
            if hasattr(message.reactions, "results"):
                for reaction in message.reactions.results:
                    # Convert reaction object to JSON-serializable format
                    reaction_obj = getattr(reaction, "reaction", "")

                    # Handle different reaction types (emoji, custom emoji, etc.)
                    if hasattr(reaction_obj, "emoticon"):  # ReactionEmoji
                        reaction_str = reaction_obj.emoticon
                    elif hasattr(reaction_obj, "document_id"):  # ReactionCustomEmoji
                        reaction_str = f"custom_{reaction_obj.document_id}"
                    elif isinstance(reaction_obj, str):  # Already a string
                        reaction_str = reaction_obj
                    else:  # Unknown type, convert to string
                        reaction_str = str(reaction_obj) if reaction_obj else ""

                    reactions.append(
                        {
                            "reaction": reaction_str,
                            "count": getattr(reaction, "count", 0),
                        }
                    )
                    reactions_count += getattr(reaction, "count", 0)

        # Extract links from text and entities
        links = extract_links(text, getattr(message, "entities", []))

        return {
            "channel": {
                "channel_id": channel_id,
                "username": channel_username,
                "title": channel_title or channel_username or f"Channel_{channel_id}",
                "is_supergroup": is_supergroup,
            },
            "post": {
                "channel_id": channel_id,
                "msg_id": message_id,
                "date": date,
                "text": text,
                "links_json": links,
                # Media type flags for content type analysis
                "has_video": has_video,
                "has_media": has_media,  # Photos, GIFs, stickers
                "has_photo": has_photo,
                "has_audio": has_audio,
                "has_document": has_document,
                "has_voice": has_voice,
                "has_gif": has_gif,
                "has_sticker": has_sticker,
                "has_poll": has_poll,
                "has_link": has_link,
                "has_web_preview": has_web_preview,
                "text_length": text_length,
            },
            "metrics": {
                "channel_id": channel_id,
                "msg_id": message_id,
                "views": views,
                "forwards": forwards,
                "comments_count": comments_count,
                "replies_count": replies_count,
                "reactions_json": reactions,
                "reactions_count": reactions_count,
                "ts": datetime.utcnow(),
            },
        }

    except Exception as e:
        logger.error(
            f"Error normalizing message {getattr(message, 'id', 'unknown')}: {e}", exc_info=True
        )
        # Return None instead of invalid data with channel_id=0
        # Callers should check for None and skip processing
        return None


def normalize_update(update: Any) -> dict[str, Any] | None:
    """Normalize a Telethon update object to a plain dictionary.

    Args:
        update: Telethon update/event object

    Returns:
        Dictionary with normalized update data, or None if not processable
    """
    try:
        # Handle different update types
        if hasattr(update, "message"):
            # New message or message edit
            return normalize_message(update.message)

        # For other update types, we might expand this later
        # For now, return None for unhandled updates
        return None

    except Exception as e:
        logger.error(f"Error normalizing update: {e}")
        return None


def extract_links(text: str, entities: list[Any] | None = None) -> list[str]:
    """Extract links from message text and entities.

    Args:
        text: Message text
        entities: List of message entities (mentions, URLs, etc.)

    Returns:
        List of extracted URLs and Telegram links
    """
    links = []

    try:
        # Extract HTTP/HTTPS URLs from text
        urls = URL_PATTERN.findall(text)
        links.extend(urls)

        # Extract Telegram links
        tg_links = TELEGRAM_LINK_PATTERN.findall(text)
        links.extend([f"https://{link}" for link in tg_links])

        # Extract from entities if available
        if entities:
            for entity in entities:
                try:
                    # Handle URL entities
                    if hasattr(entity, "url"):
                        links.append(entity.url)

                    # Handle text URL entities
                    elif hasattr(entity, "offset") and hasattr(entity, "length"):
                        start = entity.offset
                        end = start + entity.length
                        entity_text = text[start:end]

                        # Check if it's a URL-like entity
                        if entity_text.startswith(("@", "http", "https", "t.me")):
                            if entity_text.startswith("@"):
                                links.append(f"https://t.me/{entity_text[1:]}")
                            else:
                                links.append(entity_text)

                except Exception as e:
                    logger.debug(f"Error processing entity: {e}")
                    continue

        # Remove duplicates and return
        return list(set(links))

    except Exception as e:
        logger.error(f"Error extracting links: {e}")
        return []


def safe_get_attr(obj: Any, attr: str, default: Any = None) -> Any:
    """Safely get attribute from object with fallback.

    Args:
        obj: Object to get attribute from
        attr: Attribute name
        default: Default value if attribute doesn't exist

    Returns:
        Attribute value or default
    """
    try:
        return getattr(obj, attr, default)
    except Exception:
        return default


def format_datetime(dt: Any) -> datetime:
    """Format various datetime representations to standard datetime.

    Args:
        dt: Datetime object or timestamp

    Returns:
        Standard datetime object
    """
    if isinstance(dt, datetime):
        return dt
    elif isinstance(dt, (int, float)):
        return datetime.fromtimestamp(dt)
    else:
        return datetime.utcnow()
