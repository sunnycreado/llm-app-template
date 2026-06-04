import httpx
from app.config import settings


class Reranker:
    """NIM rerank model — scores retrieved docs against the query."""

    async def rerank(self, query: str, docs: list[dict], top_k: int = 3) -> list[dict]:
        passages = [d["text"] for d in docs]

        async with httpx.AsyncClient(timeout=settings.nim_timeout) as client:
            response = await client.post(
                f"{settings.nim_base_url}/ranking",
                headers={
                    "Authorization": f"Bearer {settings.nim_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.nim_rerank_model,
                    "query": {"text": query},
                    "passages": [{"text": p} for p in passages],
                },
            )

        response.raise_for_status()
        rankings = response.json().get("rankings", [])

        ranked_docs = sorted(
            [{"score": r["logit"], **docs[r["index"]]} for r in rankings],
            key=lambda x: x["score"],
            reverse=True,
        )

        return ranked_docs[:top_k]
