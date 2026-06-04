import httpx
from app.config import settings


class NIMClient:
    """Single httpx wrapper for all NIM chat/completion calls."""

    def __init__(self):
        self.base_url = settings.nim_base_url
        self.api_key = settings.nim_api_key
        self.model = settings.nim_model
        self.timeout = settings.nim_timeout

    @property
    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers,
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )
        response.raise_for_status()
        payload = response.json()
        return {
            "content": payload["choices"][0]["message"]["content"],
            "model": payload.get("model", self.model),
            "usage": payload.get("usage"),
        }

    async def complete(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> dict:
        result = await self.chat(
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return {
            "text": result["content"],
            "model": result["model"],
            "usage": result["usage"],
        }
