"""
Prompt registry — DB-backed with file fallback.

Primary source: PostgreSQL prompt_versions table
Fallback:       File system (backend/app/prompts/<name>/system.txt etc.)

The fallback means the app works even before the DB is seeded,
and local dev works without running migrations first.
"""
import json
import logging
from pathlib import Path

from sqlalchemy import select, update

from app.database.session import AsyncSessionLocal
from app.database.models import PromptVersion

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent


# ── Public API ────────────────────────────────────────────────────────

async def load(name: str = "base", version: str = "active") -> dict:
    """
    Load a prompt by name and version.

    version="active"  → loads the row where is_active=True (default)
    version="latest"  → loads the most recently created row
    version="v2"      → loads that exact version

    Returns:
        { "system": str, "few_shot": list, "meta": dict }
    """
    try:
        return await _load_from_db(name, version)
    except Exception as exc:
        logger.warning(f"DB prompt load failed ({exc}), falling back to files.")
        return _load_from_files(name)


async def build_messages(
    name: str = "base",
    version: str = "active",
    user_text: str = "",
) -> list[dict]:
    """Build the full messages array: system + few-shot + user."""
    prompt = await load(name, version)
    messages = [{"role": "system", "content": prompt["system"]}]
    messages.extend(prompt["few_shot"])
    if user_text:
        messages.append({"role": "user", "content": user_text})
    return messages


async def list_versions(name: str) -> list[dict]:
    """Return all versions for a prompt name, ordered by creation date."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(PromptVersion)
            .where(PromptVersion.name == name)
            .order_by(PromptVersion.created_at.desc())
        )
        rows = result.scalars().all()
        return [_row_to_dict(r) for r in rows]


async def create_version(
    name: str,
    version: str,
    system: str,
    few_shot: list | None = None,
    model: str | None = None,
    eval_score: float | None = None,
    notes: str | None = None,
    activate: bool = False,
) -> dict:
    """
    Insert a new prompt version.
    If activate=True, also promotes it immediately.
    """
    async with AsyncSessionLocal() as session:
        row = PromptVersion(
            name=name,
            version=version,
            system=system,
            few_shot=few_shot or [],
            model=model,
            eval_score=eval_score,
            notes=notes,
            is_active=False,
        )
        session.add(row)
        await session.flush()

        if activate:
            await _deactivate_all(session, name)
            row.is_active = True

        await session.commit()
        await session.refresh(row)
        return _row_to_dict(row)


async def promote(name: str, version: str) -> dict:
    """
    Promote a version to active — no deploy needed.
    Deactivates all other versions for that name.
    """
    async with AsyncSessionLocal() as session:
        await _deactivate_all(session, name)

        result = await session.execute(
            select(PromptVersion).where(
                PromptVersion.name == name,
                PromptVersion.version == version,
            )
        )
        row = result.scalar_one_or_none()
        if not row:
            raise ValueError(f"Prompt '{name}' version '{version}' not found.")

        row.is_active = True
        await session.commit()
        await session.refresh(row)
        logger.info(f"Promoted prompt '{name}' to version '{version}'")
        return _row_to_dict(row)


async def update_eval_score(name: str, version: str, score: float) -> None:
    """Record the eval score after running evals."""
    async with AsyncSessionLocal() as session:
        await session.execute(
            update(PromptVersion)
            .where(PromptVersion.name == name, PromptVersion.version == version)
            .values(eval_score=score)
        )
        await session.commit()


# ── Internal ─────────────────────────────────────────────────────────

async def _load_from_db(name: str, version: str) -> dict:
    async with AsyncSessionLocal() as session:
        if version == "active":
            stmt = select(PromptVersion).where(
                PromptVersion.name == name,
                PromptVersion.is_active == True,
            )
        elif version == "latest":
            stmt = (
                select(PromptVersion)
                .where(PromptVersion.name == name)
                .order_by(PromptVersion.created_at.desc())
                .limit(1)
            )
        else:
            stmt = select(PromptVersion).where(
                PromptVersion.name == name,
                PromptVersion.version == version,
            )

        result = await session.execute(stmt)
        row = result.scalar_one_or_none()

        if not row:
            raise LookupError(f"No prompt found for name='{name}' version='{version}'")

        return {
            "system": row.system,
            "few_shot": row.few_shot or [],
            "meta": _row_to_dict(row),
        }


def _load_from_files(name: str) -> dict:
    """Fallback — reads from the file system."""
    prompt_dir = PROMPTS_DIR / name
    if not prompt_dir.exists():
        raise FileNotFoundError(f"Prompt folder '{name}' not found at {prompt_dir}")

    system = (prompt_dir / "system.txt").read_text(encoding="utf-8").strip()

    few_shot_path = prompt_dir / "few_shot.json"
    few_shot = json.loads(few_shot_path.read_text(encoding="utf-8")) if few_shot_path.exists() else []

    meta_path = prompt_dir / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}

    return {"system": system, "few_shot": few_shot, "meta": meta}


async def _deactivate_all(session, name: str) -> None:
    await session.execute(
        update(PromptVersion)
        .where(PromptVersion.name == name)
        .values(is_active=False)
    )


def _row_to_dict(row: PromptVersion) -> dict:
    return {
        "id": row.id,
        "name": row.name,
        "version": row.version,
        "model": row.model,
        "eval_score": row.eval_score,
        "notes": row.notes,
        "is_active": row.is_active,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }
