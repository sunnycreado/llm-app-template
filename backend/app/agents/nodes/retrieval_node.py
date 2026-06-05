from app.agents.state import AgentState
from app.rag.pipeline import RAGPipeline

pipeline = RAGPipeline(top_k=5, rerank=False)


async def retrieval_node(state: AgentState) -> AgentState:
    """
    Runs the RAG pipeline against the user's input.
    Injects retrieved context into state for response_node to use.
    If retrieval fails or returns nothing, continues with empty context
    so response_node can still answer from conversation history.
    """
    try:
        context = await pipeline.build_context(state["input"])
    except RuntimeError as exc:
        # Qdrant unreachable or collection missing — degrade gracefully
        print(f"[retrieval_node] RAG failed: {exc}")
        context = ""

    return {**state, "context": context or None}
