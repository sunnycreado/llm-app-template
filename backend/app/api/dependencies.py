from fastapi import Header, HTTPException


async def verify_api_key(x_api_key: str | None = Header(default=None)):
    """
    Optional API key guard. Enable by setting APP_API_KEY in .env.
    Leave unset in development — all requests pass through.
    """
    from app.config import settings
    expected = getattr(settings, "app_api_key", None)
    if expected and x_api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid API key.")
