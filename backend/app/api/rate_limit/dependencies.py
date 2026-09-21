from fastapi import Depends, HTTPException

from app.api.rate_limit.rate_limiter import SlidingWindowRateLimiter
from app.api.rate_limit.client import redis_client
from app.auth.dependecies import get_current_user
from app.database.models import Users_Agent


limiter = SlidingWindowRateLimiter(redis_client, limit=2, window_seconds=60)

def rate_limit(current_user: Users_Agent = Depends(get_current_user)):
    user_id = str(current_user.id)
    allowed = limiter.is_allowed(user_id)

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please slow down.",
        )

    return current_user