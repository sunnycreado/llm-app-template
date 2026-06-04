# Architecture

## Request flow

```
User types
  → Frontend (React)
  → POST /api/chat
  → LangGraph graph
      → router_node   (classify intent)
      → retrieval_node (RAG, if needed)
      → tool_node      (tools, if needed)
      → response_node  (final answer via NIM)
  → Response
```

## LangGraph graph

```
[router] → rag intent  → [retrieval] → [response]
         → tool intent → [tool]      → [response]
         → chat intent →              [response]
```

## Data flow

- **Embeddings:** NIM embed model → Qdrant vectors
- **Retrieval:** query vector → Qdrant search → top-k docs → optional NIM rerank
- **Memory:** per-session message history, pluggable store (dict / Redis)
- **Streaming:** SSE from NIM → streamed to frontend via `/api/chat/stream`
