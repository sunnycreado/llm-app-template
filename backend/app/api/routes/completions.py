from fastapi import APIRouter, HTTPException
from app.llm.client import NIMClient
from app.schemas import CompletionRequest, CompletionResponse

router = APIRouter()
client = NIMClient()


@router.post("/completions", response_model=CompletionResponse)
async def completions(body: CompletionRequest):
    try:
        result = await client.complete(
            prompt=body.prompt,
            max_tokens=body.max_tokens,
            temperature=body.temperature,
        )
        return CompletionResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
