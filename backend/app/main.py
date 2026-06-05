import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import chat, completions, health, prompts
from app.config import settings

STATIC_DIR = Path(__file__).parent.parent / "static"

logging.basicConfig(level=settings.log_level.upper())
logger = logging.getLogger(__name__)

_dev = settings.app_env == "development"

app = FastAPI(
    title="LLM App Template",
    version="1.0.0",
    docs_url="/docs" if _dev else None,
    redoc_url="/redoc" if _dev else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(completions.router, prefix="/api", tags=["completions"])
app.include_router(prompts.router, prefix="/api", tags=["prompts"])


if _dev:
    @app.get("/prompt-studio", response_class=HTMLResponse, include_in_schema=False)
    async def prompt_studio():
        """Dev-only Prompt Studio UI — not available in production."""
        return (STATIC_DIR / "prompt_studio.html").read_text(encoding="utf-8")


@app.on_event("startup")
async def startup():
    logger.info(f"Starting in {settings.app_env} mode")
    logger.info(f"Model: {settings.nim_model}")
    if _dev:
        logger.info("Prompt Studio: http://localhost:4000/prompt-studio")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.port, reload=True)
