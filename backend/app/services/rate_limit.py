import logging
import time
from app.services.redis_client import init_redis

LOG = logging.getLogger("app.rate_limit")

def allow(key: str, limit: int, window_seconds: int) -> bool:
    '''
    Sliding-ish window using INCR + EXPIRE in Redis.

    Fail-open: if Redis is unavailable (e.g., local unit tests), allow the request.
    '''
    try:
        r = init_redis.client()
        now_bucket = int(time.time() // window_seconds)
        bucket_key = f"rl:{key}:{now_bucket}"
        v = r.incr(bucket_key)
        if v == 1:
            r.expire(bucket_key, window_seconds + 5)
        return v <= limit
    except Exception:
        LOG.warning("Redis unavailable for rate limiting; allowing request.", exc_info=True)
        return True
