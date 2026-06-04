import pytest
from app.agents.graph import run_graph


@pytest.mark.asyncio
async def test_graph_returns_output():
    messages = [{"role": "user", "content": "Hello"}]
    result = await run_graph(messages)
    assert result.get("output") is not None
