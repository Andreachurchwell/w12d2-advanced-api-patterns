from redis.asyncio import Redis
from app.core.config import settings

# Default to local Docker Redis
REDIS_URL = getattr(settings, "REDIS_URL", "redis://localhost:6379/0")

redis_client: Redis = Redis.from_url(REDIS_URL, decode_responses=True)