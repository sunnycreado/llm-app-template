"""
Seeds the prompt_versions table from existing file-based prompts.
Run this once after running migrations to migrate from file-based to DB-backed versioning.

Usage:
    python backend/scripts/seed_prompts.py
    python backend/scripts/seed_prompts.py --activate   # also mark each as active
"""
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

PROMPTS_DIR = Path(__file__).parent.parent / "app" / "prompts"
SKIP_FILES = {"registry.py", "__pycache__", "CHANGELOG.md"}


async def seed(activate: bool = True):
    from app.prompts.registry import create_version
    from app.database.session import AsyncSessionLocal
    from app.database.models import PromptVersion
    from sqlalchemy import select

    prompt_dirs = [
        d for d in PROMPTS_DIR.iterdir()
        if d.is_dir() and d.name not in SKIP_FILES and not d.name.startswith("__")
    ]

    if not prompt_dirs:
        print("No prompt folders found.")
        return

    for prompt_dir in prompt_dirs:
        name = prompt_dir.name
        system_path = prompt_dir / "system.txt"
        few_shot_path = prompt_dir / "few_shot.json"
        meta_path = prompt_dir / "meta.json"

        if not system_path.exists():
            print(f"  Skipping {name} — no system.txt")
            continue

        system = system_path.read_text(encoding="utf-8").strip()
        few_shot = json.loads(few_shot_path.read_text(encoding="utf-8")) if few_shot_path.exists() else []
        meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}

        version = meta.get("version", name)
        model = meta.get("model")
        eval_score = meta.get("eval_score")
        notes = meta.get("notes")

        # Check if already exists
        async with AsyncSessionLocal() as session:
            existing = await session.execute(
                select(PromptVersion).where(
                    PromptVersion.name == name,
                    PromptVersion.version == version,
                )
            )
            if existing.scalar_one_or_none():
                print(f"  Skipping {name}/{version} — already in DB")
                continue

        result = await create_version(
            name=name,
            version=version,
            system=system,
            few_shot=few_shot,
            model=model,
            eval_score=eval_score,
            notes=notes,
            activate=activate,
        )
        status = "active" if result["is_active"] else "inactive"
        print(f"  ✓ Seeded {name}/{version} [{status}]")

    print("\nDone seeding prompts.")


if __name__ == "__main__":
    activate = "--activate" in sys.argv
    asyncio.run(seed(activate=activate))
