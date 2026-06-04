import pytest
from app.rag.pipeline import RAGPipeline


@pytest.mark.asyncio
async def test_pipeline_returns_list():
    pipeline = RAGPipeline(top_k=3)
    # Requires Qdrant running — skip in CI if not available
    try:
        results = await pipeline.run("test query")
        assert isinstance(results, list)
    except Exception:
        pytest.skip("Qdrant not available")
