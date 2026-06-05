# Getting Started

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) — running
- [VS Code](https://code.visualstudio.com/) + [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- NVIDIA NIM API key — get one free at [build.nvidia.com](https://build.nvidia.com)

---

## Step 1 — Clone and open

```bash
git clone https://github.com/your-org/llm-app-template.git
cd llm-app-template
code .
```

VS Code will prompt **"Reopen in Container"** — click it.

This builds 5 containers: `app`, `backend`, `frontend`, `postgres`, `qdrant`, `redis`.
First build takes ~3 minutes. Subsequent opens are instant.

---

## Step 2 — Configure environment

Inside the container terminal:

```bash
cp .env.example backend/.env
```

Open `backend/.env` and set your key:

```env
NIM_API_KEY=nvapi-xxxxxxxxxxxxxxxx
```

Everything else has sensible defaults for dev. Leave them as-is to start.

---

## Step 3 — Start the app

```bash
make dev
```

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:4000 |
| Swagger docs | http://localhost:4000/docs |
| Qdrant dashboard | http://localhost:6333/dashboard |

---

## Step 4 — Smoke test

In a second terminal:

```bash
make smoke
```

You should see all endpoints returning `PASS`.

---

## Step 5 — Ingest documents (optional, for RAG)

Put `.txt` or `.md` files in `./docs/`, then:

```bash
make ingest
```

This chunks, embeds, and loads them into Qdrant. After ingestion, any message that the router classifies as `rag` intent will search these documents.

---

## What happens when you send a message

```
1. Frontend sends POST /api/chat
2. LangGraph router_node classifies intent (rag / tool / chat)
3a. rag  → retrieval_node fetches relevant docs → response_node answers with context
3b. tool → tool_node executes the right tool   → response_node answers with result
3c. chat →                                        response_node answers directly
4. Response returned and added to session history
```

---

## Next steps

- [Adding a tool](./adding-a-tool.md)
- [Adding an agent node](./adding-a-node.md)
- [Prompt versioning](./prompts.md)
- [RAG pipeline](./rag.md)
- [Database](./database.md)
- [Architecture overview](./architecture.md)
