import re

from core.ports.cache_port import AsyncCachePort


class GuardService:
    """Service for managing content moderation and blacklist functionality.

    Uses cache storage (via AsyncCachePort) to maintain per-channel blacklists
    for content filtering and moderation.
    """

    def __init__(self, cache: AsyncCachePort | None = None):
        """Initialize guard service with cache backend.

        Args:
            cache: Async cache implementation for storing blacklists.
                   If None, all operations become no-ops.
        """
        self.cache = cache

    def _key(self, channel_id: int) -> str:
        """Generate cache key for channel blacklist."""
        return f"blacklist:{channel_id}"

    async def add_word(self, channel_id: int, word: str) -> None:
        """Add a word to channel's blacklist.

        Args:
            channel_id: Channel identifier
            word: Word to add to blacklist (case-insensitive)
        """
        if not self.cache:
            return
        await self.cache.sadd(self._key(channel_id), word.lower())

    async def remove_word(self, channel_id: int, word: str) -> None:
        """Remove a word from channel's blacklist.

        Args:
            channel_id: Channel identifier
            word: Word to remove from blacklist
        """
        if not self.cache:
            return
        await self.cache.srem(self._key(channel_id), word.lower())

    async def list_words(self, channel_id: int) -> set[str]:
        """Get all blacklisted words for a channel.

        Args:
            channel_id: Channel identifier

        Returns:
            Set of blacklisted words (lowercase)
        """
        if not self.cache:
            return set()
        return await self.cache.smembers(self._key(channel_id))

    async def is_blocked(self, channel_id: int, text: str) -> bool:
        blocked_words = await self.list_words(channel_id)
        if not blocked_words:
            return False

        # Normalize text: take alphanumeric word tokens
        tokens = re.findall(r"[\w']+", text.lower())
        return any(tok in blocked_words for tok in tokens)

    async def check_bot_is_admin(self, channel_username: str, user_id: int) -> dict:
        """Placeholder admin check returning minimal channel info.

        TODO: Implement real channel admin verification via Telegram API.
        """
        return {"id": 0, "channel_id": 0, "title": "", "username": channel_username}
