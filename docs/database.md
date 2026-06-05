# Database

PostgreSQL via SQLAlchemy async + asyncpg. Migrations managed by Alembic.

---

## Setup (first time)

Alembic is not initialised in the scaffold. Run this once inside the container:

```bash
cd backend
alembic init app/database/migrations
```

Then update two files:

**`alembic.ini`** — set the database URL:
```ini
sqlalchemy.url = postgresql+asyncpg://appuser:apppassword@postgres:5432/appdb
```

**`app/database/migrations/env.py`** — point at your models:
```python
from app.database.base import Base
from app.database import models  # import all models so Alembic sees them
target_metadata = Base.metadata
```

---

## Workflow

```bash
# Apply all pending migrations
make migrate

# Generate a new migration from model changes
make migration name="add users table"

# Roll back one migration
cd backend && alembic downgrade -1

# Check current state
cd backend && alembic current
```

---

## Adding a model

1. Open `backend/app/database/models.py`
2. Add your table:

```python
class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)
```

3. Generate migration:
```bash
make migration name="add users table"
```

4. Apply:
```bash
make migrate
```

---

## Using the DB in a route

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.database.models import User

@router.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

---

## Existing models

| Table | Purpose |
|---|---|
| `chat_sessions` | Stores chat session metadata |
| `chat_messages` | Stores individual messages per session |
| `documents` | Tracks ingested document chunks |

---

## Connection config

| Env var | Default | Description |
|---|---|---|
| `POSTGRES_USER` | `appuser` | DB username |
| `POSTGRES_PASSWORD` | `apppassword` | DB password |
| `POSTGRES_HOST` | `postgres` | Host (docker service name) |
| `POSTGRES_PORT` | `5432` | Port |
| `POSTGRES_DB` | `appdb` | Database name |
