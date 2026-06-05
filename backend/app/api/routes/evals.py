from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, delete

from app.database.models import EvalCase, EvalRun, EvalCaseResult
from app.database.session import AsyncSessionLocal
from app.evals.runner import run_eval

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────────────

class CreateEvalCaseRequest(BaseModel):
    input: str
    expected_output: str | None = None
    expected_keywords: list[str] = []
    tags: list[str] = []
    notes: str | None = None


# ── Test case CRUD ────────────────────────────────────────────────────

@router.get("/evals/{prompt_name}/cases")
async def list_cases(prompt_name: str):
    """List all test cases for a prompt name."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(EvalCase)
            .where(EvalCase.prompt_name == prompt_name)
            .order_by(EvalCase.created_at.desc())
        )
        cases = result.scalars().all()
        return {
            "prompt_name": prompt_name,
            "cases": [_case_to_dict(c) for c in cases],
        }


@router.post("/evals/{prompt_name}/cases", status_code=201)
async def create_case(prompt_name: str, body: CreateEvalCaseRequest):
    """Add a test case for a prompt name."""
    async with AsyncSessionLocal() as session:
        case = EvalCase(
            prompt_name=prompt_name,
            input=body.input,
            expected_output=body.expected_output,
            expected_keywords=body.expected_keywords,
            tags=body.tags,
            notes=body.notes,
        )
        session.add(case)
        await session.commit()
        await session.refresh(case)
        return _case_to_dict(case)


@router.delete("/evals/{prompt_name}/cases/{case_id}", status_code=204)
async def delete_case(prompt_name: str, case_id: int):
    """Delete a test case."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(EvalCase).where(
                EvalCase.id == case_id,
                EvalCase.prompt_name == prompt_name,
            )
        )
        case = result.scalar_one_or_none()
        if not case:
            raise HTTPException(status_code=404, detail="Test case not found.")
        await session.delete(case)
        await session.commit()


# ── Eval runs ─────────────────────────────────────────────────────────

@router.post("/evals/{prompt_name}/{version}/run")
async def trigger_run(prompt_name: str, version: str):
    """
    Run all test cases for a prompt version.
    Scores each case, stores results, updates eval_score on the prompt version.
    """
    try:
        summary = await run_eval(prompt_name, version)
        return summary
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/evals/{prompt_name}/{version}/runs")
async def list_runs(prompt_name: str, version: str):
    """List all eval runs for a prompt version."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(EvalRun)
            .where(
                EvalRun.prompt_name == prompt_name,
                EvalRun.prompt_version == version,
            )
            .order_by(EvalRun.created_at.desc())
        )
        runs = result.scalars().all()
        return {"runs": [_run_to_dict(r) for r in runs]}


@router.get("/evals/{prompt_name}/{version}/runs/{run_id}")
async def get_run(prompt_name: str, version: str, run_id: int):
    """Get a specific eval run with all case results."""
    async with AsyncSessionLocal() as session:
        run = await session.get(EvalRun, run_id)
        if not run or run.prompt_name != prompt_name:
            raise HTTPException(status_code=404, detail="Run not found.")

        result = await session.execute(
            select(EvalCaseResult).where(EvalCaseResult.run_id == run_id)
        )
        case_results = result.scalars().all()

        return {
            **_run_to_dict(run),
            "results": [_case_result_to_dict(r) for r in case_results],
        }


# ── Helpers ───────────────────────────────────────────────────────────

def _case_to_dict(c: EvalCase) -> dict:
    return {
        "id": c.id,
        "prompt_name": c.prompt_name,
        "input": c.input,
        "expected_output": c.expected_output,
        "expected_keywords": c.expected_keywords,
        "tags": c.tags,
        "notes": c.notes,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }


def _run_to_dict(r: EvalRun) -> dict:
    return {
        "id": r.id,
        "prompt_name": r.prompt_name,
        "prompt_version": r.prompt_version,
        "overall_score": r.overall_score,
        "total_cases": r.total_cases,
        "passed_cases": r.passed_cases,
        "status": r.status,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }


def _case_result_to_dict(r: EvalCaseResult) -> dict:
    return {
        "id": r.id,
        "case_id": r.case_id,
        "input": r.input,
        "actual_output": r.actual_output,
        "expected_keywords": r.expected_keywords,
        "keyword_score": r.keyword_score,
        "relevancy_score": r.relevancy_score,
        "overall_score": r.overall_score,
        "passed": r.passed,
        "error": r.error,
    }
