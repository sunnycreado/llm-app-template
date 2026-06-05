from app.tools.base import BaseTool


class ToolRegistry:
    """
    Central registry for all tools.
    tool_node looks up tools here by name.

    To add a tool:
        1. Create backend/app/tools/my_tool.py extending BaseTool
        2. Register it below: registry.register(MyTool())
    """

    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def all(self) -> list[BaseTool]:
        return list(self._tools.values())

    def names(self) -> list[str]:
        return list(self._tools.keys())


# ── Global registry ──────────────────────────────────────────────────
registry = ToolRegistry()

# ── Registered tools ─────────────────────────────────────────────────
from app.tools.calculator import CalculatorTool
registry.register(CalculatorTool())
