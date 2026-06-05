# RAG Pipeline

Retrieval-Augmented Generation — the agent searches your documents before answering.

---

## How it works

```
User message
  → embed with NIM (nvidia/nv-embedqa-e5-v5)
  → search Qdrant (cosine similarity, top-k)
  → optional: rerank with NIM (nvidia/llama-3.2-nv-rerankqa-1b-v2)
  → inject context into system prompt
  → NIM generates answer grounded in your documents
```

---

## Ingesting documents

**Step 1** — Put your files in `./docs/` (`.txt` or `.md`)

**Step 2** — Run:
```bash
make ingest
# or with custom path/collection:
python backend/scripts/ingest_docs.py --path ./my-data --collection my-collection
```

**What happens:**
1. Each file is split into 512-character chunks with 64-character overlap
2. Each chunk is embedded via NIM embeddings API
3. Chunks + vectors are upserted into Qdrant with metadata: `source`, `filename`, `chunk_index`

---

## Enabling reranking

Reranking re-scores retrieved chunks for better precision. Costs an extra NIM call.

In `backend/app/agents/nodes/retrieval_node.py`:

```python
pipeline = RAGPipeline(top_k=10, rerank=True)
#                        ↑              ↑
#              fetch more candidates   then rerank to top 3
```

---

## Tuning chunk size

In `backend/app/rag/ingestion.py`:

```python
CHUNK_SIZE = 512     # characters per chunk — increase for longer context
CHUNK_OVERLAP = 64   # overlap between chunks — increase to avoid boundary splits
```

Smaller chunks = more precise retrieval, less context per chunk.
Larger chunks = more context, potentially noisier retrieval.

---

## Supported file types

Currently: `.txt`, `.md`

To add PDF support, extend `ingest_directory()` in `ingestion.py`:

```python
import pypdf

async def ingest_pdf(path: Path, collection: str):
    reader = pypdf.PdfReader(path)
    text = "\n".join(page.extract_text() for page in reader.pages)
    # then call chunk_text(text) and embed as normal
```

---

## Configuration

| Env var | Default | Description |
|---|---|---|
| `QDRANT_URL` | `http://localhost:6333` | Qdrant instance URL |
| `QDRANT_COLLECTION` | `documents` | Collection name |
| `NIM_EMBED_MODEL` | `nvidia/nv-embedqa-e5-v5` | Embedding model |
| `NIM_RERANK_MODEL` | `nvidia/llama-3.2-nv-rerankqa-1b-v2` | Rerank model |

---

## Checking what's in Qdrant

Open the Qdrant dashboard at `http://localhost:6333/dashboard` while the dev container is running. You can browse collections, view vectors, and run test searches.
