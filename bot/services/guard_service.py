from typing import Set
import re
import redis.asyncio as redis


class GuardService:
    def __init__(self, redis_conn: redis.Redis):
        self.redis = redis_conn

    def _key(self, channel_id: int) -> str:
        return f"blacklist:{channel_id}"

    async def add_word(self, channel_id: int, word: str):
        await self.redis.sadd(self._key(channel_id), word.lower())

    async def remove_word(self, channel_id: int, word: str):
        await self.redis.srem(self._key(channel_id), word.lower())

    async def list_words(self, channel_id: int) -> Set[str]:
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
        """Placeholder admin check returning minimal channel info."""
        return {"id": 0, "channel_id": 0, "title": "", "username": channel_username}
