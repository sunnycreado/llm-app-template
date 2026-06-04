# LLM App Template

> Production-ready scaffolding for LLM applications — FastAPI · LangGraph · RAG · NVIDIA NIM · React

[![CI](https://github.com/your-org/llm-app-template/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/llm-app-template/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

---

## What this is

A professional starting point for LLM-powered applications. It is not a tutorial or demo — it is a working template that enforces clean separation of concerns so you can fork it and build a real product without rewiring the foundation.

**Includes:**
- FastAPI backend with typed config, dependency injection, and streaming
- LangGraph agentic pipeline with router → RAG/tool → response nodes
- RAG pipeline backed by Qdrant with optional NIM reranking
- Versioned prompt system — edit text files, never Python
- Zustand-backed React chat UI with session management
- Dev container — one-click environment for any machine
- `make` commands for every workflow
- CI pipeline on GitHub Actions
- Eval suite with promptfoo

---

## Stack

| Layer | Technology |
|---|---|
| LLM | NVIDIA NIM (`meta/llama-3.1-8b-instruct`) |
| Embeddings | NVIDIA NIM (`nvidia/nv-embedqa-e5-v5`) |
| Reranking | NVIDIA NIM (`nvidia/llama-3.2-nv-rerankqa-1b-v2`) |
| Agent framework | LangGraph |
| Vector store | Qdrant |
| Memory | In-memory (Redis-ready) |
| API | FastAPI + Uvicorn |
| Frontend | React 18 + Vite + Zustand |
| Dev environment | VS Code Dev Container |
| CI | GitHub Actions |
| Eval | promptfoo + deepeval |

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [VS Code](https://code.visualstudio.com/) + [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- NVIDIA NIM API key — get one at [build.nvidia.com](https://build.nvidia.com)

---

## Getting started

### 1. Clone

```bash
git clone https://github.com/your-org/llm-app-template.git
cd llm-app-template
```

### 2. Open in dev container

Open the folder in VS Code. When prompted **"Reopen in Container"**, click it.

The container will:
- Install Python dependencies (`pip install -r backend/requirements.txt`)
- Install Node dependencies (`npm install --prefix frontend`)
- Start Qdrant and Redis as services

### 3. Configure environment

```bash
cp .env.example backend/.env
```

Edit `backend/.env` and set at minimum:

```env
NIM_API_KEY=your_key_here
```

### 4. Start the app

```bash
make dev
```

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:4000 |
| API docs (Swagger) | http://localhost:4000/docs |
| Qdrant dashboard | http://localhost:6333/dashboard |

---

## Commands

```bash
make dev        # Start backend + frontend
make test       # Run pytest
make ingest     # Load documents into Qdrant
make eval       # Run promptfoo eval suite
make smoke      # Hit every endpoint, print pass/fail
make lint       # Ruff (Python) + ESLint (JS)
make format     # Black + isort + Prettier
```

---

## Project structure

```
llm-app-template/
├── .devcontainer/              # Dev container config
├── .github/                    # CI, issue templates, PR template
├── backend/
│   ├── app/
│   │   ├── api/routes/         # FastAPI route handlers
│   │   ├── llm/                # NIM client, streaming, embeddings
│   │   ├── prompts/            # Versioned prompt files + registry
│   │   ├── rag/                # Pipeline, retriever, ingestion, reranker
│   │   ├── agents/             # LangGraph graph + nodes
│   │   ├── tools/              # Tool interface + registry
│   │   └── memory/             # Conversation history + store
│   ├── scripts/                # ingest_docs, run_evals, smoke_test
│   ├── tests/                  # pytest
│   └── evals/                  # promptfoo config + datasets
├── frontend/
│   └── src/
│       ├── components/         # chat/ and ui/ components
│       ├── hooks/              # useChat, useStream
│       ├── services/api.ts     # all fetch calls
│       └── store/              # Zustand global state
└── docs/                       # Architecture, prompts, RAG guides
```

---

## How the agent works

```
User message
  → router_node   classifies intent: rag | tool | chat
  → retrieval_node (if rag) fetches relevant documents from Qdrant
  → tool_node      (if tool) executes registered tools
  → response_node  builds final answer using context + NIM
  → Response
```

---

## Adding a tool

1. Create `backend/app/tools/my_tool.py`:

```python
from app.tools.base import BaseTool

class MyTool(BaseTool):
    name = "my_tool"
    description = "What this tool does"

    async def run(self, args: dict) -> str:
        return "result"
```

2. Register it in `backend/app/tools/registry.py`:

```python
from app.tools.my_tool import MyTool
registry.register(MyTool())
```

Done — `tool_node` picks it up automatically.

---

## Prompt versioning

Prompts live as plain text files — never as Python strings.

```
backend/app/prompts/
└── base/
    ├── system.txt       ← edit this
    ├── few_shot.json    ← add examples here
    └── meta.json        ← version metadata + eval score
```

**To create a new prompt version:**

1. Copy `base/` → `v2/`
2. Edit `system.txt` and `few_shot.json`
3. Update `meta.json` with your notes
4. Set `PROMPT_VERSION=v2` in `.env`
5. Run `make eval` — record the score in `prompts/CHANGELOG.md`

**Never edit an existing version. Always create a new one.**

---

## Ingesting documents

```bash
# Default: loads from ./docs/
make ingest

# Custom path
python backend/scripts/ingest_docs.py --path ./my-docs/
```

Supports `.txt` and `.md`. Extend `backend/app/rag/ingestion.py` for PDF, HTML, etc.

---

## Running evals

```bash
make eval
```

Add test cases to `backend/evals/datasets/`. Each entry defines an input and an assertion:

```json
[
  {
    "vars": { "prompt": "What is 2 + 2?" },
    "assert": [{ "type": "contains", "value": "4" }]
  }
]
```

Reports are saved to `backend/evals/reports/`.

---

## Environment variables

| Variable | Default | Required | Description |
|---|---|---|---|
| `NIM_API_KEY` | — | ✅ | NVIDIA NIM API key |
| `NIM_BASE_URL` | `https://integrate.api.nvidia.com/v1` | | NIM endpoint |
| `NIM_MODEL` | `meta/llama-3.1-8b-instruct` | | Chat model |
| `NIM_EMBED_MODEL` | `nvidia/nv-embedqa-e5-v5` | | Embedding model |
| `NIM_RERANK_MODEL` | `nvidia/llama-3.2-nv-rerankqa-1b-v2` | | Rerank model |
| `NIM_TIMEOUT_MS` | `30000` | | NIM request timeout |
| `QDRANT_URL` | `http://localhost:6333` | | Qdrant instance |
| `QDRANT_COLLECTION` | `documents` | | Collection name |
| `REDIS_URL` | `redis://localhost:6379` | | Redis (for memory) |
| `PROMPT_NAME` | `base` | | Prompt folder name |
| `PROMPT_VERSION` | `latest` | | Prompt version |
| `PORT` | `4000` | | Backend port |

---

## Contributing

See [CONTRIBUTING.md](.github/CONTRIBUTING.md).

---

## License

MIT — see [LICENSE](./LICENSE).
