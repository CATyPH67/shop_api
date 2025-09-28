from app.config.rate_limits_config import RATE_LIMITS
from fastapi_limiter.depends import RateLimiter


def rate_limit(name: str):
    times, seconds = RATE_LIMITS[name]
    return RateLimiter(times=times, seconds=seconds)