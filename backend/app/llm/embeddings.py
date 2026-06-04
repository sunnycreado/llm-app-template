import httpx
from app.config import settings


class NIMEmbeddings:
    """NIM embedding model wrapper."""

    def __init__(self):
        self.base_url = settings.nim_base_url
        self.api_key = settings.nim_api_key
        self.model = settings.nim_embed_model

    async def embed(self, texts: list[str]) -> list[list[float]]:
        async with httpx.AsyncClient(timeout=settings.nim_timeout) as client:
            response = await client.post(
                f"{self.base_url}/embeddings",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={"model": self.model, "input": texts},
            )
        response.raise_for_status()
        data = response.json()["data"]
        return [item["embedding"] for item in data]

    async def embed_one(self, text: str) -> list[float]:
        results = await self.embed([text])
        return results[0]
