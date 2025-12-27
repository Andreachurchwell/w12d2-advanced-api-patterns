from fastapi import APIRouter, Depends
from app.api.v1.auth import get_current_user

router = APIRouter()

@router.get("/")
def list_watchlist(user: str = Depends(get_current_user)):
    return {"user": user, "watchlist": []}
