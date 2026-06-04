from app.agents.state import AgentState
from app.llm.client import NIMClient
from app.prompts.registry import build_messages
from app.config import settings

client = NIMClient()


async def response_node(state: AgentState) -> AgentState:
    """Generates the final response using context + history."""
    system_msg = {
        "role": "system",
        "content": _build_system(state),
    }

    messages = [system_msg] + state.get("messages", [])
    messages.append({"role": "user", "content": state["input"]})

    response = await client.chat(messages=messages)
    return {**state, "output": response["content"]}


def _build_system(state: AgentState) -> str:
    base = build_messages(
        name=settings.prompt_name,
        version=settings.prompt_version,
    )[0]["content"]

    if state.get("context"):
        base += f"\n\nRelevant context:\n{state['context']}"

    if state.get("tool_calls"):
        tool_results = "\n".join(
            f"- {t['tool']}: {t['result']}" for t in state["tool_calls"]
        )
        base += f"\n\nTool results:\n{tool_results}"

    return base
