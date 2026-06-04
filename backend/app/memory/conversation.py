from app.memory.store import MemoryStore


class ConversationMemory:
    """Per-session message history backed by pluggable store."""

    def __init__(self, max_turns: int = 20):
        self.store = MemoryStore()
        self.max_turns = max_turns

    def get(self, session_id: str) -> list[dict]:
        return self.store.get(session_id) or []

    def append(self, session_id: str, message: dict):
        history = self.get(session_id)
        history.append(message)
        # Keep only last N turns to control token usage
        if len(history) > self.max_turns * 2:
            history = history[-(self.max_turns * 2):]
        self.store.set(session_id, history)

    def clear(self, session_id: str):
        self.store.delete(session_id)
