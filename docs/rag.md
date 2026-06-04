# RAG Pipeline

## Steps

1. **Ingest** — `make ingest` chunks documents, embeds with NIM, upserts into Qdrant
2. **Retrieve** — query is embedded, top-k nearest vectors fetched from Qdrant
3. **Rerank** (optional) — NIM rerank model scores passages against query
4. **Augment** — context injected into system prompt in `response_node`

## Running ingestion

```bash
make ingest
# or with a custom path:
python backend/scripts/ingest_docs.py --path ./my-docs/
```

Supports `.txt` and `.md` files. Extend `ingestion.py` for PDF, HTML, etc.

## Configuration

| Env var | Default | Description |
|---|---|---|
| `QDRANT_URL` | `http://localhost:6333` | Qdrant instance |
| `QDRANT_COLLECTION` | `documents` | Collection name |
| `NIM_EMBED_MODEL` | `nvidia/nv-embedqa-e5-v5` | Embedding model |
| `NIM_RERANK_MODEL` | `nvidia/llama-3.2-nv-rerankqa-1b-v2` | Rerank model |

## Enabling reranking

In `backend/app/agents/nodes/retrieval_node.py`:

```python
pipeline = RAGPipeline(top_k=10, rerank=True)
```
