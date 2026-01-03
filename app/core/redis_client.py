import time
import os
from redis.asyncio import Redis
from redis.exceptions import RedisError

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
redis_client: Redis = Redis.from_url(REDIS_URL, decode_responses=True)


async def delete_pattern(pattern: str) -> int:
    """
    Delete all Redis keys matching the given pattern.
    Fail-open: if Redis is down, return 0 and do not crash the API.
    """
    try:
        keys = []
        async for key in redis_client.scan_iter(match=pattern):
            keys.append(key)

        if keys:
            return await redis_client.delete(*keys)
        return 0
    except (RedisError, Exception):
        return 0


async def is_rate_limited(key: str, limit: int, window_seconds: int) -> bool:
    """
    Fail-open: if Redis is down, do NOT rate limit.
    """
    try:
        count = await redis_client.incr(key)
        if count == 1:
            await redis_client.expire(key, window_seconds)
        return count > limit
    except (RedisError, Exception):
        return False


async def rate_limit_info(key: str, limit: int, window_seconds: int) -> dict:
    """
    Fail-open: if Redis is down, return 'not limited' with sane values.
    """
    now = int(time.time())

    try:
        window = now // window_seconds
        redis_key = f"{key}:{window}"

        count = await redis_client.incr(redis_key)
        if count == 1:
            await redis_client.expire(redis_key, window_seconds)

        remaining = max(0, limit - count)
        reset = (window + 1) * window_seconds

        return {
            "limit": limit,
            "remaining": remaining,
            "reset": reset,
            "is_limited": count > limit,
        }

    except (RedisError, Exception):
        # Pretend we're not limited if Redis is unavailable
        return {
            "limit": limit,
            "remaining": limit,
            "reset": now + window_seconds,
            "is_limited": False,
        }


def get_redis():
    return redis_client