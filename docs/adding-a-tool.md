# Adding a Tool

Tools let the agent perform actions — calculations, API calls, database queries, web searches, etc.

---

## Step 1 — Create the tool file

```python
# backend/app/tools/my_tool.py

from typing import Any
from app.tools.base import BaseTool


class MyTool(BaseTool):
    name = "my_tool"
    description = "What this tool does and when to use it. Args: { param: str }"

    async def run(self, args: dict[str, Any]) -> str:
        param = args.get("param", "")
        # your logic here
        return f"Result for: {param}"
```

**Rules:**
- `name` — unique, lowercase, underscores. The LLM uses this to select the tool.
- `description` — clear, tells the LLM what the tool does and what args it expects.
- `run()` — always async, always returns a string.

---

## Step 2 — Register it

Open `backend/app/tools/registry.py` and add:

```python
from app.tools.my_tool import MyTool
registry.register(MyTool())
```

That's it. `tool_node` picks it up automatically — no other changes needed.

---

## Step 3 — Test it

```python
# backend/tests/test_agents.py

@pytest.mark.asyncio
async def test_my_tool():
    from app.tools.my_tool import MyTool
    tool = MyTool()
    result = await tool.run({"param": "hello"})
    assert "hello" in result
```

Run: `make test`

---

## Built-in tools

| Tool | File | What it does |
|---|---|---|
| `calculator` | `tools/calculator.py` | Evaluates math expressions safely |

To enable the calculator, uncomment in `registry.py`:

```python
from app.tools.calculator import CalculatorTool
registry.register(CalculatorTool())
```

---

## How tool selection works

When the router classifies intent as `tool`, `tool_node`:

1. Lists all registered tools with their descriptions
2. Sends them to the LLM with the user message
3. LLM returns `{ "tool": "my_tool", "args": { "param": "value" } }`
4. `tool_node` calls `registry.get("my_tool").run(args)`
5. Result is passed to `response_node` which uses it to formulate the answer

The quality of tool selection depends heavily on your `description` field — write it clearly.
