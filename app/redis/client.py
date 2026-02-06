from __future__ import annotations

import os
from typing import Optional

try:
    import redis  # redis-py
except Exception:  # pragma: no cover
    redis = None  # type: ignore

_client: Optional["redis.Redis"] = None


def _enabled() -> bool:
    return os.getenv("REDIS_DISABLED") != "1"


def init_redis(url: str | None = None):
    """
    Initializes global redis client using REDIS_URL.
    Safe to call multiple times.
    """
    global _client
    if not _enabled():
        _client = None
        return None

    if redis is None:
        raise RuntimeError("redis package not installed (pip install redis)")

    if _client is not None:
        return _client

    url = url or os.getenv("REDIS_URL") or ""
    if not url:
        raise RuntimeError("Redis enabled but REDIS_URL is empty")

    _client = redis.from_url(url, decode_responses=True)
    return _client


def ping() -> bool:
    if not _enabled():
        return False
    if _client is None:
        init_redis()
    try:
        return bool(_client.ping())  # type: ignore[union-attr]
    except Exception:
        return False


def close():
    global _client
    try:
        if _client is not None:
            _client.close()
    finally:
        _client = None