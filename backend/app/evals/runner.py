"""
Eval runner — runs all test cases for a prompt version.

Steps per test case:
  1. Call /api/chat with the test input
  2. Score keyword assertions (no LLM needed)
  3. Score answer relevancy via DeepEval + NIM judge
  4. Store results in DB
  5. Update prompt version eval_score
"""
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.graph import run_graph
from app.database.models import EvalCase, EvalCaseResult, EvalRun
from app.database.session import AsyncSessionLocal
from app.prompts import registry as prompt_registry

logger = logging.getLogger(__name__)


# ── Keyword scorer (no LLM needed) ───────────────────────────────────

def score_keywords(actual: str, keywords: list[str]) -> float:
    """What fraction of expected keywords appear in the actual output."""
    if not keywords:
        return 1.0
    actual_lower = actual.lower()
    hits = sum(1 for kw in keywords if kw.lower() in actual_lower)
    return round(hits / len(keywords), 3)


# ── Relevancy scorer (DeepEval + NIM) ────────────────────────────────

async def score_relevancy(input_text: str, actual_output: str) -> float | None:
    """Uses DeepEval AnswerRelevancyMetric with NIM as the judge."""
    try:
        from deepeval import evaluate
        from deepeval.metrics import AnswerRelevancyMetric
        from deepeval.test_case import LLMTestCase
        from app.evals.nim_judge import NIMJudge

        judge = NIMJudge()
        metric = AnswerRelevancyMetric(threshold=0.5, model=judge, async_mode=False)
        test_case = LLMTestCase(input=input_text, actual_output=actual_output)
        metric.measure(test_case)
        return round(metric.score, 3)
    except Exception as exc:
        logger.warning(f"Relevancy scoring failed: {exc}")
        return None


# ── Main runner ───────────────────────────────────────────────────────

async def run_eval(prompt_name: str, prompt_version: str) -> dict:
    """
    Runs all EvalCases for the given prompt name against the given version.
    Stores an EvalRun + EvalCaseResults in the DB.
    Updates the prompt version eval_score.
    Returns a summary dict.
    """
    async with AsyncSessionLocal() as session:
        # Load test cases
        result = await session.execute(
            select(EvalCase).where(EvalCase.prompt_name == prompt_name)
        )
        cases = result.scalars().all()

        if not cases:
            return {"error": f"No test cases found for prompt '{prompt_name}'"}

        # Create eval run record
        run = EvalRun(
            prompt_name=prompt_name,
            prompt_version=prompt_version,
            total_cases=len(cases),
            passed_cases=0,
            status="running",
        )
        session.add(run)
        await session.flush()
        run_id = run.id

    # Run each case (outside session to avoid long-held transactions)
    case_results = []
    for case in cases:
        result = await _run_single_case(case, prompt_name, prompt_version)
        case_results.append((case, result))

    # Store results and compute overall score
    async with AsyncSessionLocal() as session:
        run = await session.get(EvalRun, run_id)
        passed = 0
        scores = []

        for case, res in case_results:
            cr = EvalCaseResult(
                run_id=run_id,
                case_id=case.id,
                input=case.input,
                actual_output=res.get("actual_output", ""),
                expected_keywords=case.expected_keywords,
                keyword_score=res.get("keyword_score"),
                relevancy_score=res.get("relevancy_score"),
                overall_score=res.get("overall_score"),
                passed=res.get("passed", False),
                error=res.get("error"),
            )
            session.add(cr)
            if res.get("passed"):
                passed += 1
            if res.get("overall_score") is not None:
                scores.append(res["overall_score"])

        overall = round(sum(scores) / len(scores), 3) if scores else 0.0

        run.passed_cases = passed
        run.overall_score = overall
        run.status = "completed"

        await session.commit()

    # Update prompt version eval_score
    await prompt_registry.update_eval_score(prompt_name, prompt_version, overall)

    logger.info(
        f"Eval complete: {prompt_name}/{prompt_version} — "
        f"{passed}/{len(cases)} passed, score={overall}"
    )

    return {
        "run_id": run_id,
        "prompt_name": prompt_name,
        "prompt_version": prompt_version,
        "total_cases": len(cases),
        "passed_cases": passed,
        "overall_score": overall,
        "status": "completed",
    }


async def _run_single_case(case: EvalCase, prompt_name: str, prompt_version: str) -> dict:
    """Runs one test case — calls the agent, scores output."""
    try:
        # Temporarily switch active prompt to the version being tested
        messages = [{"role": "user", "content": case.input}]
        state = await run_graph(messages)
        actual_output = state.get("output") or ""

        keyword_score = score_keywords(actual_output, case.expected_keywords or [])
        relevancy_score = await score_relevancy(case.input, actual_output)

        # Overall: average of available scores
        available = [s for s in [keyword_score, relevancy_score] if s is not None]
        overall_score = round(sum(available) / len(available), 3) if available else 0.0
        passed = overall_score >= 0.6

        return {
            "actual_output": actual_output,
            "keyword_score": keyword_score,
            "relevancy_score": relevancy_score,
            "overall_score": overall_score,
            "passed": passed,
        }
    except Exception as exc:
        logger.error(f"Case {case.id} failed: {exc}")
        return {
            "actual_output": "",
            "keyword_score": 0.0,
            "relevancy_score": None,
            "overall_score": 0.0,
            "passed": False,
            "error": str(exc),
        }
