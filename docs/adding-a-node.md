# Adding an Agent Node

Nodes are the building blocks of the LangGraph pipeline. Each node receives the shared `AgentState`, does one thing, and returns an updated state.

---

## When to add a node

- You need a new step in the pipeline (e.g. summarise, validate, classify)
- You want to branch the graph based on a condition
- An existing node is doing too many things

---

## Step 1 — Create the node file

```python
# backend/app/agents/nodes/my_node.py

from app.agents.state import AgentState
from app.llm.client import NIMClient

client = NIMClient()


async def my_node(state: AgentState) -> AgentState:
    """
    Does one specific thing.
    Always returns the full state with your additions merged in.
    """
    # Read from state
    user_input = state["input"]

    # Do your work
    result = await client.chat(
        messages=[{"role": "user", "content": user_input}],
        max_tokens=100,
    )

    # Return updated state — always spread existing state first
    return {**state, "metadata": {"my_result": result["content"]}}
```

**Rules:**
- Always `return {**state, ...}` — never mutate state in place
- One responsibility per node
- Handle exceptions — let the graph continue if possible

---

## Step 2 — Register it in the graph

Open `backend/app/agents/graph.py`:

```python
from app.agents.nodes.my_node import my_node

# Add the node
graph.add_node("my_node", my_node)

# Wire it into the flow — example: run after retrieval, before response
graph.add_edge("retrieval", "my_node")
graph.add_edge("my_node", "response")
```

Remove or update any existing edge that `my_node` replaces.

---

## Step 3 — Add state fields if needed

If your node produces new data, add it to `AgentState`:

```python
# backend/app/agents/state.py

class AgentState(TypedDict):
    ...
    my_result: str | None   # add your field here
```

---

## Step 4 — Test it

```python
# backend/tests/test_agents.py

@pytest.mark.asyncio
async def test_my_node():
    from app.agents.nodes.my_node import my_node

    state = {
        "messages": [], "input": "test", "intent": None,
        "context": None, "tool_calls": [], "output": None,
        "error": None, "metadata": {}
    }
    result = await my_node(state)
    assert "my_result" in result["metadata"]
```

---

## Current graph

```
[router_node]
     │
     ├── rag  → [retrieval_node] → [response_node] → END
     ├── tool → [tool_node]      → [response_node] → END
     └── chat →                    [response_node] → END
```

Add your node anywhere in this flow by editing `graph.py`.
