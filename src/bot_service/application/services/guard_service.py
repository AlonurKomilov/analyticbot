import re
from typing import Optional

try:
    import redis.asyncio as redis  # type: ignore
except Exception:  # pragma: no cover
    redis = None  # type: ignore


class GuardService:
    def __init__(self, redis_conn: Optional["redis.Redis"] = None):  # type: ignore[name-defined]
        # Redis majburiy emas: yo'q bo'lsa in-memory set'lar ishlatilmaydi (faqat False qaytadi)
        self.redis = redis_conn

    def _key(self, channel_id: int) -> str:
        return f"blacklist:{channel_id}"

    async def add_word(self, channel_id: int, word: str):
        if not self.redis:
            return
        await self.redis.sadd(self._key(channel_id), word.lower())

    async def remove_word(self, channel_id: int, word: str):
        if not self.redis:
            return
        await self.redis.srem(self._key(channel_id), word.lower())

    async def list_words(self, channel_id: int) -> set[str]:
        if not self.redis:
            return set()
        words = await self.redis.smembers(self._key(channel_id))
        # Decode bytes from Redis into strings
        return {word.decode("utf-8") for word in words}

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
