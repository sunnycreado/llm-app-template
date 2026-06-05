"""
NIM as the DeepEval judge LLM.
DeepEval uses this to score metrics like AnswerRelevancy and Faithfulness.
"""
from typing import Optional
import httpx
from deepeval.models.base_model import DeepEvalBaseLLM
from app.config import settings


class NIMJudge(DeepEvalBaseLLM):
    """Wraps NVIDIA NIM as a DeepEval-compatible judge LLM."""

    def __init__(self, model: str | None = None):
        self.model = model or settings.nim_model

    def load_model(self):
        return self.model

    def generate(self, prompt: str, schema=None) -> str:
        """Synchronous generation — used by DeepEval internally."""
        import asyncio
        return asyncio.run(self.a_generate(prompt, schema))

    async def a_generate(self, prompt: str, schema=None) -> str:
        """Async generation via NIM chat completions."""
        async with httpx.AsyncClient(timeout=settings.nim_timeout) as client:
            response = await client.post(
                f"{settings.nim_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.nim_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.0,
                    "max_tokens": 512,
                },
            )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def get_model_name(self) -> str:
        return self.model
