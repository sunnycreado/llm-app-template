.PHONY: dev backend frontend test eval ingest smoke lint format

# ── Dev ─────────────────────────────────────────────────────────────
dev:
	make -j2 backend frontend

backend:
	cd backend && uvicorn app.main:app --reload --port 4000

frontend:
	cd frontend && npm run dev

# ── Quality ─────────────────────────────────────────────────────────
test:
	cd backend && pytest tests/ -v

lint:
	cd backend && ruff check app/
	cd frontend && npm run lint

format:
	cd backend && black app/ && isort app/
	cd frontend && npm run format

# ── Data & Evals ────────────────────────────────────────────────────
ingest:
	python backend/scripts/ingest_docs.py

eval:
	python backend/scripts/run_evals.py

smoke:
	python backend/scripts/smoke_test.py
