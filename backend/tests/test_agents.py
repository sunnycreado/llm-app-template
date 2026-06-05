import pytest
from unittest.mock import AsyncMock, patch
from app.agents.graph import run_graph
from app.tools.calculator import CalculatorTool
from app.tools.registry import ToolRegistry


# ── Calculator tool unit tests ───────────────────────────────────────

@pytest.mark.asyncio
async def test_calculator_basic():
    tool = CalculatorTool()
    result = await tool.run({"expression": "2 + 2"})
    assert "4" in result


@pytest.mark.asyncio
async def test_calculator_complex():
    tool = CalculatorTool()
    result = await tool.run({"expression": "10 * 5 - 3"})
    assert "47" in result


@pytest.mark.asyncio
async def test_calculator_invalid():
    tool = CalculatorTool()
    result = await tool.run({"expression": "import os"})
    assert "Error" in result


@pytest.mark.asyncio
async def test_calculator_empty():
    tool = CalculatorTool()
    result = await tool.run({})
    assert "Error" in result


# ── Tool registry ────────────────────────────────────────────────────

def test_registry_register_and_get():
    reg = ToolRegistry()
    tool = CalculatorTool()
    reg.register(tool)
    assert reg.get("calculator") is tool


def test_registry_get_missing():
    reg = ToolRegistry()
    assert reg.get("nonexistent") is None


def test_registry_all():
    reg = ToolRegistry()
    reg.register(CalculatorTool())
    assert len(reg.all()) == 1


# ── Graph integration (mocked LLM) ───────────────────────────────────

@pytest.mark.asyncio
async def test_graph_chat_intent():
    """Graph returns output for a simple chat message."""
    with patch("app.agents.nodes.router_node.client") as mock_router_client, \
         patch("app.agents.nodes.response_node.client") as mock_response_client:

        mock_router_client.chat = AsyncMock(return_value={
            "content": '{"intent":"chat","reasoning":"Simple greeting."}',
            "model": "test", "usage": None
        })
        mock_response_client.chat = AsyncMock(return_value={
            "content": "Hello! How can I help you?",
            "model": "test", "usage": None
        })

        messages = [{"role": "user", "content": "Hello"}]
        result = await run_graph(messages)

        assert result["output"] == "Hello! How can I help you?"
        assert result["intent"] == "chat"
        assert result["error"] is None
