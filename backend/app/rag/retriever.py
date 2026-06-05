from qdrant_client import AsyncQdrantClient
from app.config import settings


class Retriever:
    """Searches Qdrant for documents nearest to a query vector."""

    def __init__(self):
        self.client = AsyncQdrantClient(url=settings.qdrant_url)
        self.collection = settings.qdrant_collection

    async def search(self, vector: list[float], top_k: int = 5) -> list[dict]:
        """
        Returns top_k results as:
        [{ "text": str, "score": float, "source": str, "metadata": dict }]
        """
        try:
            results = await self.client.search(
                collection_name=self.collection,
                query_vector=vector,
                limit=top_k,
                with_payload=True,
            )
        except Exception as exc:
            raise RuntimeError(f"Qdrant search failed: {exc}") from exc

        return [
            {
                "text": r.payload.get("text", ""),
                "score": r.score,
                "source": r.payload.get("source", ""),
                "metadata": r.payload,
            }
            for r in results
        ]

    async def close(self):
        await self.client.close()
