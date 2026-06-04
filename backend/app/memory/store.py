from typing import Any


class MemoryStore:
    """
    In-memory store (default). Swap for Redis by replacing this class.

    Redis drop-in:
        import redis
        class MemoryStore:
            def __init__(self):
                self.r = redis.from_url(settings.redis_url)
            def get(self, key): ...
            def set(self, key, value): ...
            def delete(self, key): ...
    """

    def __init__(self):
        self._data: dict[str, Any] = {}

    def get(self, key: str) -> Any:
        return self._data.get(key)

    def set(self, key: str, value: Any):
        self._data[key] = value

    def delete(self, key: str):
        self._data.pop(key, None)
