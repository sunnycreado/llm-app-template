from app.agents.state import AgentState
from app.llm.client import NIMClient

client = NIMClient()


async def router_node(state: AgentState) -> AgentState:
    """
    Classifies user intent to decide which path the graph takes.
    Returns state with intent set.
    """
    user_input = state["input"]

    response = await client.chat(
        messages=[
            {
                "role": "system",
                "content": (
                    "Classify the user intent into one word: "
                    "'rag' (needs document lookup), "
                    "'tool' (needs a tool), "
                    "'chat' (general conversation). "
                    "Reply with only the intent word."
                ),
            },
            {"role": "user", "content": user_input},
        ],
        max_tokens=10,
        temperature=0.0,
    )

    intent = response["content"].strip().lower()
    return {**state, "intent": intent}
