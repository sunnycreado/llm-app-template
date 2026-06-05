# Migrations

Managed with **Alembic**.

## Setup (first time)

```bash
cd backend
alembic init app/database/migrations
```

Update `alembic.ini` to set `sqlalchemy.url` and point `env.py` at `app.database.base.Base`.

## Commands

```bash
# Create a new migration
alembic revision --autogenerate -m "add chat_sessions table"

# Apply all pending migrations
alembic upgrade head

# Roll back one migration
alembic downgrade -1

# Check current state
alembic current
```

## Add to Makefile

```makefile
migrate:
    cd backend && alembic upgrade head

migration:
    cd backend && alembic revision --autogenerate -m "$(name)"
```
