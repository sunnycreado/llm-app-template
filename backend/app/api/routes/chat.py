from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.agents.graph import run_graph
from app.llm.streaming import stream_response
from app.memory.conversation import ConversationMemory
from app.schemas import ChatRequest, ChatResponse, Message

router = APIRouter()
memory = ConversationMemory()


@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest):
    """
    Agentic chat endpoint.
    Runs the full LangGraph pipeline (router → RAG/tool → response).
    Persists history per session_id if provided.
    """
    history = await memory.aget(body.session_id) if body.session_id else []
    all_messages = history + [m.model_dump() for m in body.messages]

    try:
        result = await run_graph(all_messages)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    reply = Message(role="assistant", content=result["output"] or "")

    if body.session_id:
        await memory.aappend(body.session_id, body.messages[-1].model_dump())
        await memory.aappend(body.session_id, reply.model_dump())

    return ChatResponse(message=reply, session_id=body.session_id)


@router.post("/chat/stream")
async def chat_stream(body: ChatRequest):
    """
    Streaming chat endpoint — returns tokens via Server-Sent Events.
    Streams directly from NIM without running the full agent graph.
    Use /chat for agentic behaviour, /chat/stream for fast token-by-token UX.

    Frontend usage (fetch-based SSE with POST body):
        const res = await fetch('/api/chat/stream', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ messages })
        })
        const reader = res.body.getReader()
        // read tokens from the stream
    """
    history = await memory.aget(body.session_id) if body.session_id else []
    all_messages = history + [m.model_dump() for m in body.messages]

    return StreamingResponse(
        stream_response(all_messages),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
