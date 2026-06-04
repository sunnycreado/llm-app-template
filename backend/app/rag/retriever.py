from qdrant_client import AsyncQdrantClient
from qdrant_client.models import SearchRequest
from app.config import settings


class Retriever:
    def __init__(self):
        self.client = AsyncQdrantClient(url=settings.qdrant_url)
        self.collection = settings.qdrant_collection

    async def search(self, vector: list[float], top_k: int = 5) -> list[dict]:
        results = await self.client.search(
            collection_name=self.collection,
            query_vector=vector,
            limit=top_k,
            with_payload=True,
        )
        return [
            {"text": r.payload.get("text", ""), "score": r.score, "metadata": r.payload}
            for r in results
        ]
