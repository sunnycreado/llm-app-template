import json
import re

from app.agents.state import AgentState
from app.llm.client import NIMClient
from app.tools.registry import registry

client = NIMClient()

TOOL_SELECTION_SYSTEM = """You are a tool selector. Given the user message and available tools,
decide which tool to call and with what arguments.
Return only valid JSON: {"tool": "<tool_name>", "args": {<key-value pairs>}}
If no tool is appropriate, return: {"tool": null, "args": {}}
Do not include markdown or code fences."""


async def tool_node(state: AgentState) -> AgentState:
    """
    1. Asks the LLM which registered tool to call and with what args
    2. Executes the tool
    3. Returns results in state for response_node
    """
    tools = registry.all()

    if not tools:
        return {**state, "tool_calls": []}

    tool_descriptions = "\n".join(
        f"- {t.name}: {t.description}" for t in tools
    )

    messages = [
        {
            "role": "system",
            "content": f"{TOOL_SELECTION_SYSTEM}\n\nAvailable tools:\n{tool_descriptions}",
        },
        {"role": "user", "content": state["input"]},
    ]

    results = []

    try:
        response = await client.chat(messages=messages, max_tokens=100, temperature=0.0)
        content = response["content"].strip()

        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            parsed = json.loads(match.group())
            tool_name = parsed.get("tool")
            args = parsed.get("args", {})

            if tool_name:
                tool = registry.get(tool_name)
                if tool:
                    result = await tool.run(args)
                    results.append({"tool": tool_name, "args": args, "result": result})
    except Exception as exc:
        print(f"[tool_node] Tool execution failed: {exc}")

    return {**state, "tool_calls": results}
