import json
from typing import Optional

import redis.asyncio as redis

from app.config import db_settings

# Redis DB 0 for caching
redis_client = redis.from_url(db_settings.REDIS_URL(0), decode_responses=True)

# Default cache TTL (time to live) in seconds — 5 minutes
DEFAULT_TTL = 300


async def cache_get(key: str) -> Optional[dict]:
    """Get a value from cache. Returns None if not found."""
    data = await redis_client.get(key)
    if data:
        return json.loads(data)
    return None


async def cache_set(key: str, value, ttl: int = DEFAULT_TTL):
    """Store a value in cache with a TTL (time to live)."""
    await redis_client.set(key, json.dumps(value, default=str), ex=ttl)


async def cache_delete(key: str):
    """Delete a specific key from cache."""
    await redis_client.delete(key)


async def cache_delete_pattern(pattern: str):
    """Delete all keys matching a pattern (e.g., 'deck:*')."""
    keys = []
    async for key in redis_client.scan_iter(match=pattern):
        keys.append(key)
    if keys:
        await redis_client.delete(*keys)
