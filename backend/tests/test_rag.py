import pytest
from unittest.mock import AsyncMock, patch
from app.rag.pipeline import RAGPipeline
from app.rag.ingestion import chunk_text


# ── Unit tests (no external dependencies) ────────────────────────────

def test_chunk_text_basic():
    text = "word " * 200
    chunks = chunk_text(text)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 512


def test_chunk_text_short():
    text = "short text"
    chunks = chunk_text(text)
    assert len(chunks) == 1
    assert chunks[0] == "short text"


def test_chunk_text_empty():
    chunks = chunk_text("")
    assert chunks == []


# ── Integration tests (require Qdrant) ───────────────────────────────

@pytest.mark.asyncio
async def test_pipeline_run_with_mock():
    """Tests pipeline logic without real NIM or Qdrant."""
    mock_vector = [0.1] * 1024

    with (
        patch("app.rag.pipeline.NIMEmbeddings") as mock_embed_cls,
        patch("app.rag.pipeline.Retriever") as mock_retriever_cls,
    ):
        mock_embed = AsyncMock()
        mock_embed.embed_one.return_value = mock_vector
        mock_embed_cls.return_value = mock_embed

        mock_retriever = AsyncMock()
        mock_retriever.search.return_value = [
            {"text": "Relevant document text.", "score": 0.9, "source": "doc.txt", "metadata": {}}
        ]
        mock_retriever_cls.return_value = mock_retriever

        pipeline = RAGPipeline(top_k=3, rerank=False)
        results = await pipeline.run("test query")

        assert len(results) == 1
        assert results[0]["text"] == "Relevant document text."
        mock_embed.embed_one.assert_called_once_with("test query")


@pytest.mark.asyncio
async def test_pipeline_build_context_empty():
    """Returns empty string when no documents are found."""
    with (
        patch("app.rag.pipeline.NIMEmbeddings") as mock_embed_cls,
        patch("app.rag.pipeline.Retriever") as mock_retriever_cls,
    ):
        mock_embed = AsyncMock()
        mock_embed.embed_one.return_value = [0.0] * 1024
        mock_embed_cls.return_value = mock_embed

        mock_retriever = AsyncMock()
        mock_retriever.search.return_value = []
        mock_retriever_cls.return_value = mock_retriever

        pipeline = RAGPipeline(top_k=3)
        context = await pipeline.build_context("empty query")
        assert context == ""
