# Prompt Versioning

DB-backed — versions live in PostgreSQL. Promote without redeploying.
File system is used as fallback if the DB is unavailable.

---

## How it works

```
prompt_versions table
┌────┬────────┬─────────┬───────────────┬───────────┬───────────┐
│ id │  name  │ version │    system     │ is_active │ eval_score│
├────┼────────┼─────────┼───────────────┼───────────┼───────────┤
│  1 │  base  │  base   │ You are a ... │   false   │   null    │
│  2 │  base  │   v2    │ You are a ... │   true    │   0.91    │
│  3 │  base  │   v3    │ You are a ... │   false   │   null    │
└────┴────────┴─────────┴───────────────┴───────────┴───────────┘
```

`is_active=true` marks the live version. Only one row per name can be active.

---

## First-time setup

After running migrations, seed existing file-based prompts into the DB:

```bash
make migrate
make seed-prompts
```

This reads every folder under `backend/app/prompts/` and inserts each one as a DB row, marking it active.

---

## Creating a new version

**Via API:**
```bash
curl -X POST http://localhost:4000/api/prompts/base \
  -H "Content-Type: application/json" \
  -d '{
    "version": "v2",
    "system": "You are a helpful assistant...",
    "few_shot": [],
    "model": "meta/llama-3.1-8b-instruct",
    "notes": "Tightened null discipline rule.",
    "activate": false
  }'
```

**Via Swagger:** `http://localhost:4000/docs` → `POST /api/prompts/{name}`

---

## Promoting a version

No redeploy needed — the app picks it up on the next request.

```bash
curl -X POST http://localhost:4000/api/prompts/base/v2/promote
```

Or via Swagger: `POST /api/prompts/{name}/{version}/promote`

---

## Recording an eval score

After running `make eval`:

```bash
curl -X PATCH http://localhost:4000/api/prompts/base/v2/eval-score \
  -H "Content-Type: application/json" \
  -d '{"eval_score": 0.91}'
```

---

## API reference

| Method | Path | What it does |
|---|---|---|
| `GET` | `/api/prompts/{name}` | List all versions |
| `GET` | `/api/prompts/{name}/active` | Get the active version |
| `GET` | `/api/prompts/{name}/{version}` | Get a specific version |
| `POST` | `/api/prompts/{name}` | Create a new version |
| `POST` | `/api/prompts/{name}/{version}/promote` | Promote to active |
| `PATCH` | `/api/prompts/{name}/{version}/eval-score` | Record eval score |

---

## Loading in code

```python
from app.prompts.registry import load, build_messages

# Load active version (default)
prompt = await load(name="base")

# Load specific version
prompt = await load(name="base", version="v2")

# Build full messages array for NIM
messages = await build_messages(name="base", user_text="Hello")
```

---

## File fallback

If the DB is unreachable, `registry.py` falls back to reading from:

```
backend/app/prompts/<name>/system.txt
backend/app/prompts/<name>/few_shot.json
```

This means the app never crashes due to a DB issue — it just uses the file version.

---

## Workflow

```
1. Create new version via API (activate=false)
2. Run make eval against the new version
3. If score is good → promote via API
4. Record eval score via PATCH /eval-score
5. Update CHANGELOG.md with notes
```
