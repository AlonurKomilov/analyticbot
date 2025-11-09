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

        # Extract metrics
        views = getattr(message, "views", 0) or 0
        forwards = getattr(message, "forwards", 0) or 0
        replies_count = 0

        if hasattr(message, "replies") and message.replies:
            replies_count = getattr(message.replies, "replies", 0) or 0

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
            },
            "metrics": {
                "channel_id": channel_id,
                "msg_id": message_id,
                "views": views,
                "forwards": forwards,
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
