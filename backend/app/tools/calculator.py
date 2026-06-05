import ast
import operator
from typing import Any

from app.tools.base import BaseTool

# Safe operators only — no eval() of arbitrary code
_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
}


def _safe_eval(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_safe_eval(node.operand))
    raise ValueError(f"Unsupported expression: {ast.dump(node)}")


class CalculatorTool(BaseTool):
    name = "calculator"
    description = "Evaluates a mathematical expression. Args: { expression: str }"

    async def run(self, args: dict[str, Any]) -> str:
        expression = str(args.get("expression", "")).strip()
        if not expression:
            return "Error: no expression provided."
        try:
            tree = ast.parse(expression, mode="eval")
            result = _safe_eval(tree.body)
            return f"{expression} = {result}"
        except Exception as exc:
            return f"Error evaluating '{expression}': {exc}"
