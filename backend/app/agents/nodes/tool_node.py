from app.agents.state import AgentState
from app.tools.registry import ToolRegistry

registry = ToolRegistry()


async def tool_node(state: AgentState) -> AgentState:
    """
    Executes registered tools based on LLM tool call decisions.
    Extend by registering new tools in app/tools/registry.py.
    """
    tool_calls = state.get("tool_calls", [])
    results = []

    for call in tool_calls:
        tool = registry.get(call["name"])
        if tool:
            result = await tool.run(call.get("args", {}))
            results.append({"tool": call["name"], "result": result})

    return {**state, "tool_calls": results}
