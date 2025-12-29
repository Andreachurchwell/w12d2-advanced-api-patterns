import time
from fastapi import Request, HTTPException, Depends

from app.core.redis_client import redis_client


def rate_limit(limit: int = 60, window_seconds: int = 60):
    """
    Fixed-window rate limit.
    - limit: max requests per window
    - window_seconds: window size in seconds
    Adds required headers and raises 429 when exceeded.
    """
    async def _limit(request: Request):
        # Identify caller (best-effort):
        # If you later have user email in request.state, you can use it here.
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path

        now = int(time.time())
        window = now // window_seconds
        key = f"rl:{client_ip}:{path}:{window}"

        count = await redis_client.incr(key)
        if count == 1:
            # expire key at end of window
            await redis_client.expire(key, window_seconds)

        remaining = max(0, limit - int(count))
        reset = (window + 1) * window_seconds  # epoch seconds when window resets
        retry_after = max(0, reset - now)

        # Attach headers to response via request.state (we'll add a small middleware next)
        request.state.rate_limit_headers = {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset),
        }

        if count > limit:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded",
                headers={"Retry-After": str(retry_after)},
            )

    return Depends(_limit)