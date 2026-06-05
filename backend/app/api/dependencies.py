"""
Shared FastAPI dependencies.

Usage in a route:
    from fastapi import Depends
    from app.api.dependencies import get_db

    @router.get("/example")
    async def example(db: AsyncSession = Depends(get_db)):
        ...
"""
from app.database.session import get_db  # re-export for convenience

__all__ = ["get_db"]
