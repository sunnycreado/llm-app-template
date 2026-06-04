from app.tools.base import BaseTool


class ToolRegistry:
    """Register tools by name. tool_node looks them up here."""

    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def all(self) -> list[BaseTool]:
        return list(self._tools.values())


# ── Register your tools here ─────────────────────────────────────────
# from app.tools.my_tool import MyTool
# registry = ToolRegistry()
# registry.register(MyTool())
