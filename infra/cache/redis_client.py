from __future__ import annotations

import redis.asyncio as redis

# This is a placeholder for the actual client initialization.
# In a real application, this would be configured via settings.
redis_client = redis.from_url("redis://localhost", decode_responses=True)
