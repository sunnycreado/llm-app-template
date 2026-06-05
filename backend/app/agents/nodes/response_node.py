from app.agents.state import AgentState
from app.llm.client import NIMClient
from app.prompts.registry import load
from app.config import settings

client = NIMClient()


async def response_node(state: AgentState) -> AgentState:
    """
    Generates the final response using:
    - The versioned system prompt
    - Retrieved RAG context (if any)
    - Tool results (if any)
    - Conversation history
    """
    system_content = _build_system_prompt(state)

    messages = [{"role": "system", "content": system_content}]

    # Include conversation history (excluding current input)
    for msg in state.get("messages", []):
        if isinstance(msg, dict) and msg.get("role") in ("user", "assistant"):
            messages.append({"role": msg["role"], "content": msg["content"]})

    # Add current user message
    messages.append({"role": "user", "content": state["input"]})

    try:
        result = await client.chat(messages=messages, temperature=0.7, max_tokens=1024)
        output = result["content"]
    except Exception as exc:
        output = f"I encountered an error generating a response: {exc}"

    return {**state, "output": output}


def _build_system_prompt(state: AgentState) -> str:
    """Assembles the system prompt from versioned file + context + tool results."""
    prompt = load(name=settings.prompt_name, version=settings.prompt_version)
    parts = [prompt["system"]]

    if state.get("context"):
        parts.append(
            "Use the following retrieved context to answer the user's question. "
            "Cite the source when relevant.\n\n"
            f"{state['context']}"
        )

    if state.get("tool_calls"):
        tool_lines = "\n".join(
            f"- {t['tool']}({t.get('args', {})}): {t['result']}"
            for t in state["tool_calls"]
        )
        parts.append(f"Tool results available:\n{tool_lines}")

    return "\n\n".join(parts)
