# Architecture

## System overview

```
┌─────────────────────────────────────────────────────┐
│  Browser                                            │
│  React + Vite + Zustand                             │
│  components/  hooks/  services/api.ts  store/       │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP / SSE
┌──────────────────────▼──────────────────────────────┐
│  FastAPI  (port 4000)                               │
│  api/routes/  →  agents/graph.py                    │
│                                                     │
│  ┌─────────────────────────────────────────────┐    │
│  │  LangGraph pipeline                         │    │
│  │                                             │    │
│  │  [router_node]                              │    │
│  │       ├── rag  → [retrieval] → [response]   │    │
│  │       ├── tool → [tool]      → [response]   │    │
│  │       └── chat →               [response]   │    │
│  └─────────────────────────────────────────────┘    │
└───────┬──────────────┬──────────────┬───────────────┘
        │              │              │
┌───────▼──────┐ ┌─────▼──────┐ ┌────▼────────┐
│  PostgreSQL  │ │  Qdrant    │ │  Redis      │
│  (sessions, │ │  (vectors, │ │  (memory,   │
│   messages, │ │   RAG)     │ │   cache)    │
│   documents)│ └────────────┘ └─────────────┘
└─────────────┘
        │
┌───────▼──────────────────────────────────────────────┐
│  NVIDIA NIM  (external)                              │
│  chat · embeddings · reranking                       │
└──────────────────────────────────────────────────────┘
```

---

## Request flow — `/api/chat`

```
1. POST /api/chat  { messages, session_id }
2. memory.get(session_id)         — load history
3. run_graph(messages)            — LangGraph pipeline
   a. router_node                 — classify: rag | tool | chat
   b. retrieval_node (if rag)     — embed query → Qdrant → top-k docs
   c. tool_node (if tool)         — select + execute registered tool
   d. response_node               — build prompt → NIM → final answer
4. memory.append(session_id, ...) — persist turn
5. Return ChatResponse
```

---

## Request flow — `/api/chat/stream`

```
1. POST /api/chat/stream  { messages }
2. NIM chat/completions with stream=true
3. Token-by-token SSE: data: {"token": "..."}\n\n
4. Frontend appends each token to UI
```

Note: streaming bypasses the full agent graph for speed.
Use `/api/chat` for full agentic behaviour.

---

## Key modules

| Module | Responsibility |
|---|---|
| `app/config.py` | Single source of truth for all env vars |
| `app/llm/client.py` | All NIM HTTP calls — one place |
| `app/prompts/registry.py` | Load versioned prompts from disk |
| `app/rag/pipeline.py` | Orchestrates embed → retrieve → rerank |
| `app/agents/graph.py` | LangGraph graph definition and entry point |
| `app/agents/state.py` | Shared TypedDict state between all nodes |
| `app/tools/registry.py` | Tool registration and lookup |
| `app/memory/store.py` | Pluggable memory backend |
| `app/database/session.py` | Async SQLAlchemy session factory |

---

## Data stores

| Store | What goes in | Technology |
|---|---|---|
| PostgreSQL | Sessions, messages, document metadata | SQLAlchemy + asyncpg |
| Qdrant | Document vector embeddings for RAG | qdrant-client |
| Redis | Conversation memory (optional) | redis-py |
| In-memory dict | Conversation memory (default, dev) | Python dict |
