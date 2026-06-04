from langgraph.graph import END, StateGraph

from app.agents.nodes.response_node import response_node
from app.agents.nodes.retrieval_node import retrieval_node
from app.agents.nodes.router_node import router_node
from app.agents.nodes.tool_node import tool_node
from app.agents.state import AgentState
from app.config import settings


def route(state: AgentState) -> str:
    """Conditional edge — routes based on classified intent."""
    intent = state.get("intent", "chat")
    if intent == "rag":
        return "retrieval"
    if intent == "tool":
        return "tool"
    return "response"


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("router", router_node)
    graph.add_node("retrieval", retrieval_node)
    graph.add_node("tool", tool_node)
    graph.add_node("response", response_node)

    graph.set_entry_point("router")

    graph.add_conditional_edges(
        "router",
        route,
        {
            "retrieval": "retrieval",
            "tool": "tool",
            "response": "response",
        },
    )

    graph.add_edge("retrieval", "response")
    graph.add_edge("tool", "response")
    graph.add_edge("response", END)

    return graph.compile()


_graph = build_graph()


async def run_graph(messages: list[dict]) -> AgentState:
    user_input = next(
        (m["content"] for m in reversed(messages) if m["role"] == "user"), ""
    )

    initial_state: AgentState = {
        "messages": messages[:-1],
        "input": user_input,
        "intent": None,
        "context": None,
        "tool_calls": [],
        "output": None,
        "error": None,
        "metadata": {},
    }

    return await _graph.ainvoke(
        initial_state,
        config={"recursion_limit": settings.langgraph_recursion_limit},
    )
