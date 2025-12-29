# from redis.asyncio import Redis
# from app.core.config import settings

# # Default to local Docker Redis
# REDIS_URL = getattr(settings, "REDIS_URL", "redis://localhost:6379/0")

# redis_client: Redis = Redis.from_url(REDIS_URL, decode_responses=True)

from redis.asyncio import Redis
from app.core.config import settings

REDIS_URL = getattr(settings, "REDIS_URL", "redis://localhost:6379/0")

redis_client: Redis = Redis.from_url(REDIS_URL, decode_responses=True)


async def delete_pattern(pattern: str) -> int:
    """
    Delete all Redis keys matching the given pattern.
    Returns the number of keys deleted.
    """
    keys = []
    async for key in redis_client.scan_iter(match=pattern):
        keys.append(key)

    if keys:
        return await redis_client.delete(*keys)

    return 0