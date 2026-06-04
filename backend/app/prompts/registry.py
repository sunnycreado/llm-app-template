import json
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent


def load(name: str = "base", version: str = "latest") -> dict:
    """
    Load a prompt by name and version.
    version='latest' resolves to the highest-numbered folder,
    or falls back to 'base'.

    Returns:
        {
            "system": str,
            "few_shot": list[dict],
            "meta": dict,
        }
    """
    prompt_dir = _resolve_dir(name, version)

    system = (prompt_dir / "system.txt").read_text(encoding="utf-8").strip()

    few_shot_path = prompt_dir / "few_shot.json"
    few_shot = json.loads(few_shot_path.read_text(encoding="utf-8")) if few_shot_path.exists() else []

    meta_path = prompt_dir / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}

    return {"system": system, "few_shot": few_shot, "meta": meta}


def build_messages(name: str = "base", version: str = "latest", user_text: str = "") -> list[dict]:
    """Build the full messages array: system + few-shot + user."""
    prompt = load(name, version)
    messages = [{"role": "system", "content": prompt["system"]}]
    messages.extend(prompt["few_shot"])
    messages.append({"role": "user", "content": user_text})
    return messages


def _resolve_dir(name: str, version: str) -> Path:
    base = PROMPTS_DIR / name
    if not base.exists():
        raise FileNotFoundError(f"Prompt '{name}' not found at {base}")
    if version == "latest":
        return base
    versioned = base / version
    if not versioned.exists():
        raise FileNotFoundError(f"Prompt version '{version}' not found at {versioned}")
    return versioned
