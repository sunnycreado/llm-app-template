from app.llm.embeddings import NIMEmbeddings
from app.rag.retriever import Retriever
from app.rag.reranker import Reranker


class RAGPipeline:
    """
    Full RAG pipeline: embed query → retrieve from Qdrant → optionally rerank.

    Usage:
        pipeline = RAGPipeline(top_k=5, rerank=True)
        context = await pipeline.build_context("What is workers comp?")
    """

    def __init__(self, top_k: int = 5, rerank: bool = False):
        self.embeddings = NIMEmbeddings()
        self.retriever = Retriever()
        self.reranker = Reranker() if rerank else None
        self.top_k = top_k

    async def run(self, query: str) -> list[dict]:
        """Returns ranked list of relevant document chunks."""
        query_vector = await self.embeddings.embed_one(query)
        results = await self.retriever.search(query_vector, top_k=self.top_k)

        if not results:
            return []

        if self.reranker:
            results = await self.reranker.rerank(query, results, top_k=self.top_k)

        return results

    async def build_context(self, query: str, separator: str = "\n\n---\n\n") -> str:
        """
        Runs the pipeline and returns a single context string
        ready to be injected into a prompt.
        """
        docs = await self.run(query)
        if not docs:
            return ""

        parts = []
        for doc in docs:
            source = doc.get("source", "unknown")
            text = doc.get("text", "")
            parts.append(f"[Source: {source}]\n{text}")

        return separator.join(parts)
