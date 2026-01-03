from fastapi import Depends, HTTPException, Request
from app.core.redis_client import redis_client


def rate_limit(action: str, limit: int, window: int):
    async def _rate_limit(request: Request, user_email: str = None):
        # identify client (prefer user, fallback to IP)
        identifier = user_email or request.client.host
        key = f"rl:{action}:{identifier}"

        try:
            count = await redis_client.incr(key)

            if count == 1:
                await redis_client.expire(key, window)

            remaining = max(limit - count, 0)

            # attach headers to response
            request.state.rate_limit_headers = {
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": str(remaining),
                "Retry-After": str(window),
            }

            if count > limit:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")

        except HTTPException:
            raise
        except Exception:
            # Fail open if Redis or event loop is unavailable (common in tests)
            return

    return _rate_limit
