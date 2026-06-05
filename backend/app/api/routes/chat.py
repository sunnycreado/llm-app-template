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
    Standard chat endpoint.
    Runs the full LangGraph pipeline and returns a single response.
    Persists history if session_id is provided.
    """
    history = memory.get(body.session_id) if body.session_id else []
    all_messages = history + [m.model_dump() for m in body.messages]

    try:
        result = await run_graph(all_messages)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    reply = Message(role="assistant", content=result["output"])

    if body.session_id:
        memory.append(body.session_id, body.messages[-1].model_dump())
        memory.append(body.session_id, reply.model_dump())

    return ChatResponse(message=reply, session_id=body.session_id)


@router.post("/chat/stream")
async def chat_stream(body: ChatRequest):
    """
    Streaming chat endpoint — returns tokens via Server-Sent Events.
    Does NOT run the full agent graph — streams directly from NIM.
    Use /chat for full agentic behaviour, /chat/stream for fast UX.

    Frontend usage:
        const es = new EventSource('/api/chat/stream')
        es.onmessage = (e) => {
            const { token } = JSON.parse(e.data)
            // append token to UI
        }
    """
    history = memory.get(body.session_id) if body.session_id else []
    all_messages = history + [m.model_dump() for m in body.messages]

    return StreamingResponse(
        stream_response(all_messages),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # disable nginx buffering for SSE
        },
    )
