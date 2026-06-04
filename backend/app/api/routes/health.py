from fastapi import APIRouter
from app.config import settings

router = APIRouter()


@router.get("/health")
def health():
    return {
        "status": "ok",
        "env": settings.app_env,
        "model": settings.nim_model,
    }
