import json
from typing import Any

from app.config import settings


class InMemoryStore:
    """Default store — simple dict. Lost on restart. Good for dev."""

    def __init__(self):
        self._data: dict[str, Any] = {}

    def get(self, key: str) -> Any:
        return self._data.get(key)

    def set(self, key: str, value: Any):
        self._data[key] = value

    def delete(self, key: str):
        self._data.pop(key, None)


class RedisStore:
    """
    Redis-backed store. Persists across restarts.
    Activated when REDIS_URL is set and USE_REDIS=true in .env
    """

    def __init__(self, ttl_seconds: int = 86400):
        import redis
        self.client = redis.from_url(settings.redis_url, decode_responses=True)
        self.ttl = ttl_seconds

    def get(self, key: str) -> Any:
        value = self.client.get(key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    def set(self, key: str, value: Any):
        self.client.set(key, json.dumps(value), ex=self.ttl)

    def delete(self, key: str):
        self.client.delete(key)


def MemoryStore():
    """
    Factory — returns RedisStore if USE_REDIS=true, else InMemoryStore.
    Switch by setting USE_REDIS=true in .env
    """
    use_redis = getattr(settings, "use_redis", False)
    if use_redis:
        try:
            return RedisStore()
        except Exception as exc:
            print(f"[memory] Redis unavailable ({exc}), falling back to in-memory store.")
    return InMemoryStore()
