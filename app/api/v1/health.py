from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.deps import get_db
from app.core.redis_client import rate_limit_info

router = APIRouter()

@router.get("/health/detailed")
async def health_detailed(db: Session = Depends(get_db)):
    db_ok = False
    redis_ok = False

    # Check DB
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    # Check Redis (by calling your existing redis code)
    try:
        await rate_limit_info(key="healthcheck", limit=1, window_seconds=1)
        redis_ok = True
    except Exception:
        redis_ok = False

    status = "ok" if db_ok and redis_ok else "degraded"

    return {
        "status": status,
        "dependencies": {
            "database": "ok" if db_ok else "down",
            "redis": "ok" if redis_ok else "down",
        },
    }