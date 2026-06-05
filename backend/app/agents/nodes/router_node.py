import json
import re

from app.agents.state import AgentState
from app.llm.client import NIMClient

client = NIMClient()

SYSTEM = """You are an intent router for an AI assistant.
Classify the user message into exactly one of these intents:
- rag       : user needs information that requires searching documents or a knowledge base
- tool      : user wants to perform an action (calculate, search web, run code, etc.)
- chat      : general conversation, greeting, simple question answerable from context

Return only valid JSON: {"intent": "<rag|tool|chat>", "reasoning": "<one sentence>"}
Do not include markdown or code fences."""

EXAMPLES = [
    {"role": "user", "content": 'Classify: "What does our refund policy say?"'},
    {"role": "assistant", "content": '{"intent":"rag","reasoning":"Needs document lookup for policy information."}'},
    {"role": "user", "content": 'Classify: "What is 15% of 340?"'},
    {"role": "assistant", "content": '{"intent":"tool","reasoning":"Requires a calculation tool."}'},
    {"role": "user", "content": 'Classify: "Hello, how are you?"'},
    {"role": "assistant", "content": '{"intent":"chat","reasoning":"Simple greeting, no lookup needed."}'},
]


async def router_node(state: AgentState) -> AgentState:
    """
    Classifies user intent to decide the graph path:
    - rag  → retrieval_node → response_node
    - tool → tool_node      → response_node
    - chat →                  response_node
    """
    user_input = state["input"]

    messages = [
        {"role": "system", "content": SYSTEM},
        *EXAMPLES,
        {"role": "user", "content": f'Classify: "{user_input}"'},
    ]

    try:
        result = await client.chat(messages=messages, max_tokens=60, temperature=0.0)
        content = result["content"].strip()

        # Extract JSON safely
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            parsed = json.loads(match.group())
            intent = parsed.get("intent", "chat")
        else:
            intent = "chat"

        # Validate intent value
        if intent not in ("rag", "tool", "chat"):
            intent = "chat"

    except Exception:
        intent = "chat"

    return {**state, "intent": intent}
