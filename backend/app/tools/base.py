from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    name: str
    description: str

    @abstractmethod
    async def run(self, args: dict[str, Any]) -> str:
        """Execute the tool and return a string result."""
        ...
