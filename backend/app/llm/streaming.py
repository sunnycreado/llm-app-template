import json
from typing import AsyncGenerator

import httpx
from app.config import settings


async def stream_response(messages: list[dict]) -> AsyncGenerator[str, None]:
    """Yields SSE tokens from NIM streaming endpoint."""

    headers = {
        "Authorization": f"Bearer {settings.nim_api_key}",
        "Content-Type": "application/json",
    }

    body = {
        "model": settings.nim_model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 512,
        "stream": True,
    }

    async with httpx.AsyncClient(timeout=settings.nim_timeout) as client:
        async with client.stream(
            "POST",
            f"{settings.nim_base_url}/chat/completions",
            headers=headers,
            json=body,
        ) as response:
            async for line in response.aiter_lines():
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                try:
                    chunk = json.loads(data)
                    token = chunk["choices"][0]["delta"].get("content", "")
                    if token:
                        yield f"data: {json.dumps({'token': token})}\n\n"
                except (json.JSONDecodeError, KeyError):
                    continue
