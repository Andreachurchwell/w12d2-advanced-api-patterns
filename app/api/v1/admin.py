from fastapi import APIRouter, Depends
from app.api.v1.auth import require_admin
from app.db.models import User

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
def admin_stats(_: User = Depends(require_admin)):
    return {
        "status": "ok",
        "message": "You are an admin and can access this route."
    }