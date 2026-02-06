import logging
from typing import Optional
import redis

LOG = logging.getLogger("app.redis")

class RedisClient:
    def __init__(self):
        self._url: Optional[str] = None
        self._client: Optional[redis.Redis] = None

    def configure(self, url: str):
        if self._client is not None:
            return
        self._url = url
        self._client = redis.Redis.from_url(url, decode_responses=True)
        LOG.info("Redis configured.")

    def client(self) -> redis.Redis:
        if self._client is None:
            raise RuntimeError("Redis not configured yet.")
        return self._client

    def close(self):
        if self._client is not None:
            try:
                self._client.close()
            except Exception:
                pass
            self._client = None

    def ping(self) -> bool:
        try:
            if self._client is None:
                return False
            return bool(self._client.ping())
        except Exception:
            return False

init_redis = RedisClient()
