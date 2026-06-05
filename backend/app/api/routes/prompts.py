from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.prompts import registry

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────────────

class CreatePromptRequest(BaseModel):
    version: str
    system: str
    few_shot: list = []
    model: str | None = None
    eval_score: float | None = None
    notes: str | None = None
    activate: bool = False


class UpdateEvalScoreRequest(BaseModel):
    eval_score: float


# ── Routes ────────────────────────────────────────────────────────────

@router.get("/prompts/{name}")
async def list_versions(name: str):
    """List all versions for a prompt name."""
    try:
        versions = await registry.list_versions(name)
        return {"name": name, "versions": versions}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/prompts/{name}/active")
async def get_active(name: str):
    """Get the currently active version for a prompt name."""
    try:
        prompt = await registry.load(name=name, version="active")
        return prompt
    except LookupError:
        raise HTTPException(status_code=404, detail=f"No active version found for '{name}'")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/prompts/{name}/{version}")
async def get_version(name: str, version: str):
    """Get a specific prompt version."""
    try:
        prompt = await registry.load(name=name, version=version)
        return prompt
    except LookupError:
        raise HTTPException(status_code=404, detail=f"Prompt '{name}' version '{version}' not found.")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/prompts/{name}", status_code=201)
async def create_version(name: str, body: CreatePromptRequest):
    """
    Create a new prompt version.
    Set activate=true to immediately promote it to active.
    """
    try:
        result = await registry.create_version(
            name=name,
            version=body.version,
            system=body.system,
            few_shot=body.few_shot,
            model=body.model,
            eval_score=body.eval_score,
            notes=body.notes,
            activate=body.activate,
        )
        return result
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/prompts/{name}/{version}/promote")
async def promote(name: str, version: str):
    """
    Promote a version to active — no redeploy needed.
    Instantly switches which prompt the app uses.
    """
    try:
        result = await registry.promote(name=name, version=version)
        return {"message": f"Promoted '{name}' to version '{version}'", **result}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.patch("/prompts/{name}/{version}/eval-score")
async def update_eval_score(name: str, version: str, body: UpdateEvalScoreRequest):
    """Record the eval score after running evals."""
    try:
        await registry.update_eval_score(name, version, body.eval_score)
        return {"message": f"Updated eval_score for '{name}' v'{version}' to {body.eval_score}"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
