from typing import Any
from pydantic import BaseModel


# ── Chat ────────────────────────────────────────────────────────────

class Message(BaseModel):
    role: str  # "user" | "assistant" | "system"
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]
    stream: bool = False
    session_id: str | None = None


class ChatResponse(BaseModel):
    message: Message
    session_id: str | None = None


# ── Completion ───────────────────────────────────────────────────────

class CompletionRequest(BaseModel):
    prompt: str
    max_tokens: int = 512
    temperature: float = 0.7


class CompletionResponse(BaseModel):
    text: str
    model: str
    usage: dict[str, int] | None = None


# ── Agent ────────────────────────────────────────────────────────────

class AgentRequest(BaseModel):
    input: str
    session_id: str | None = None
    context: dict[str, Any] | None = None


class AgentResponse(BaseModel):
    output: str
    steps: list[str] = []
    session_id: str | None = None
