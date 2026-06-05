from app.memory.store import InMemoryStore, MemoryStore


class ConversationMemory:
    """Per-session message history backed by pluggable store."""

    def __init__(self, max_turns: int = 20):
        self._store = MemoryStore()
        self.max_turns = max_turns
        self._is_async = not isinstance(self._store, InMemoryStore)

    def get(self, session_id: str) -> list[dict]:
        if self._is_async:
            return []  # async store — caller must use aget()
        return self._store.get(session_id) or []

    def append(self, session_id: str, message: dict):
        if self._is_async:
            return  # async store — caller must use aappend()
        history = self.get(session_id)
        history.append(message)
        if len(history) > self.max_turns * 2:
            history = history[-(self.max_turns * 2):]
        self._store.set(session_id, history)

    async def aget(self, session_id: str) -> list[dict]:
        if self._is_async:
            return await self._store.get(session_id) or []
        return self._store.get(session_id) or []

    async def aappend(self, session_id: str, message: dict):
        history = await self.aget(session_id)
        history.append(message)
        if len(history) > self.max_turns * 2:
            history = history[-(self.max_turns * 2):]
        if self._is_async:
            await self._store.set(session_id, history)
        else:
            self._store.set(session_id, history)

    def clear(self, session_id: str):
        self._store.delete(session_id)
