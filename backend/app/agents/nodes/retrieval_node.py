from app.agents.state import AgentState
from app.rag.pipeline import RAGPipeline

pipeline = RAGPipeline(top_k=5, rerank=False)


async def retrieval_node(state: AgentState) -> AgentState:
    """Runs RAG pipeline and injects context into state."""
    try:
        context = await pipeline.build_context(state["input"])
    except Exception as exc:
        context = ""
        state = {**state, "error": str(exc)}

    return {**state, "context": context}
