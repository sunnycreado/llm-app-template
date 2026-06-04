from app.llm.embeddings import NIMEmbeddings
from app.rag.retriever import Retriever
from app.rag.reranker import Reranker


class RAGPipeline:
    """Embed → retrieve → rerank → return context."""

    def __init__(self, top_k: int = 5, rerank: bool = False):
        self.embeddings = NIMEmbeddings()
        self.retriever = Retriever()
        self.reranker = Reranker() if rerank else None
        self.top_k = top_k

    async def run(self, query: str) -> list[dict]:
        query_vector = await self.embeddings.embed_one(query)
        results = await self.retriever.search(query_vector, top_k=self.top_k)

        if self.reranker and results:
            results = await self.reranker.rerank(query, results)

        return results

    async def build_context(self, query: str) -> str:
        docs = await self.run(query)
        return "\n\n".join(d["text"] for d in docs)
