# Contributing

Thank you for taking the time to contribute. Please read this before opening an issue or pull request.

---

## Development setup

1. Clone the repo and open in VS Code
2. Click **Reopen in Container** when prompted
3. Copy `cp .env.example backend/.env` and fill in `NIM_API_KEY`
4. Run `make dev` to start the app

---

## Branching

| Branch | Purpose |
|---|---|
| `main` | Stable, production-ready |
| `develop` | Integration branch — all PRs target this |
| `feat/<name>` | New features |
| `fix/<name>` | Bug fixes |
| `chore/<name>` | Tooling, deps, config |
| `docs/<name>` | Documentation only |

**All pull requests must target `develop`, not `main`.**

---

## Before you open a PR

- [ ] `make lint` passes with no errors
- [ ] `make test` passes
- [ ] `make smoke` passes (requires backend running)
- [ ] If you changed a prompt — run `make eval` and record the score in `prompts/CHANGELOG.md`
- [ ] New features have at least one test
- [ ] `docs/` is updated if you changed architecture or added a capability

---

## Commit messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add reranker to RAG pipeline
fix: handle null lob in intent extraction
chore: bump langgraph to 0.2.0
docs: add RAG ingestion guide
refactor: extract NIM client into llm/client.py
test: add smoke test for /api/chat/stream
```

---

## Prompt changes

Prompts are versioned. **Never edit an existing version folder.**

1. Copy `backend/app/prompts/base/` → `backend/app/prompts/v2/`
2. Make your changes
3. Run `make eval` and record the score
4. Add an entry to `backend/app/prompts/CHANGELOG.md`
5. Include the CHANGELOG update in your PR

---

## Adding a tool

See `docs/architecture.md`. In short:

1. Create `backend/app/tools/your_tool.py` extending `BaseTool`
2. Register it in `backend/app/tools/registry.py`
3. Add a test in `backend/tests/`

---

## Code style

**Python** — Black + isort + Ruff. Run `make format` before committing.

**TypeScript** — Prettier + ESLint. Run `make format` before committing.

CI will fail if either linter reports errors.

---

## Reporting a bug

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md).

## Requesting a feature

Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md).
