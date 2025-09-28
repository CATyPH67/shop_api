from fastapi_limiter.depends import RateLimiter

RATE_LIMITS = {
    "OFTEN": (60, 60),
    "MEDIUM": (30, 60),
    "RARE": (10, 60),
}

def limit(name: str):
    times, seconds = RATE_LIMITS[name]
    return RateLimiter(times=times, seconds=seconds)