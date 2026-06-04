from typing import Any, TypedDict


class AgentState(TypedDict):
    """Shared state passed between all LangGraph nodes."""

    messages: list[dict]       # full conversation history
    input: str                 # latest user message
    intent: str | None         # classified intent
    context: str | None        # RAG retrieved context
    tool_calls: list[dict]     # tools invoked this turn
    output: str | None         # final response
    error: str | None          # error message if any step fails
    metadata: dict[str, Any]   # arbitrary pass-through data
