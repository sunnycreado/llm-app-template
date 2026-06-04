import pytest


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_completion(client):
    response = await client.post(
        "/api/completions",
        json={"prompt": "Say hello", "max_tokens": 20},
    )
    assert response.status_code == 200
    assert "text" in response.json()
