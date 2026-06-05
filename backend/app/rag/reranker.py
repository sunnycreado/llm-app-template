import httpx
from app.config import settings


class Reranker:
    """
    NIM rerank model — re-scores retrieved docs against the query.
    Docs: https://build.nvidia.com/nvidia/llama-3_2-nv-rerankqa-1b-v2
    """

    async def rerank(self, query: str, docs: list[dict], top_k: int = 3) -> list[dict]:
        if not docs:
            return []

        passages = [{"text": d["text"]} for d in docs]

        try:
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
                        "passages": passages,
                    },
                )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            # Reranker unavailable — return original order
            print(f"Reranker returned {exc.response.status_code}, skipping rerank.")
            return docs[:top_k]
        except Exception as exc:
            print(f"Reranker error: {exc}, skipping rerank.")
            return docs[:top_k]

        rankings = response.json().get("rankings", [])

        reranked = sorted(
            [
                {**docs[r["index"]], "rerank_score": r.get("logit", 0)}
                for r in rankings
                if r["index"] < len(docs)
            ],
            key=lambda x: x["rerank_score"],
            reverse=True,
        )

        return reranked[:top_k]
