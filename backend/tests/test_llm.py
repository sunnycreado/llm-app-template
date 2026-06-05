import pytest


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "model" in data


@pytest.mark.asyncio
async def test_completion_returns_text(client):
    response = await client.post(
        "/api/completions",
        json={"prompt": "Reply with only the word: hello", "max_tokens": 20},
    )
    assert response.status_code == 200
    data = response.json()
    assert "text" in data
    assert isinstance(data["text"], str)
    assert len(data["text"]) > 0


@pytest.mark.asyncio
async def test_completion_missing_prompt(client):
    response = await client.post("/api/completions", json={})
    assert response.status_code == 422  # FastAPI validation error


@pytest.mark.asyncio
async def test_chat_returns_message(client):
    response = await client.post(
        "/api/chat",
        json={"messages": [{"role": "user", "content": "Say hello"}]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"]["role"] == "assistant"
    assert len(data["message"]["content"]) > 0


@pytest.mark.asyncio
async def test_chat_with_session_id(client):
    session_id = "test-session-123"
    response = await client.post(
        "/api/chat",
        json={
            "messages": [{"role": "user", "content": "My name is Alice"}],
            "session_id": session_id,
        },
    )
    assert response.status_code == 200
    assert response.json()["session_id"] == session_id
