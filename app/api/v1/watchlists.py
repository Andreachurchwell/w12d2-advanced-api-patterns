from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.db.deps import get_db
from app.db.models import User, WatchlistItem
from app.core.exceptions import NotFoundError

from fastapi import HTTPException

router = APIRouter()

class WatchlistItemCreate(BaseModel):
    title: str
    type: str  # "movie" or "show"

class WatchlistItemUpdate(BaseModel):
    title: str | None = None
    type: str | None = None

@router.get("/")
def list_watchlist(
    user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        return {"user": user_email, "watchlist": []}

    items = (
        db.query(WatchlistItem)
        .filter(WatchlistItem.user_id == user.id)
        .order_by(WatchlistItem.created_at.desc())
        .all()
    )

    return {
        "user": user_email,
        "watchlist": [
            {
                "id": i.id,
                "title": i.title,
                "type": i.media_type,
                "created_at": i.created_at.isoformat(),
            }
            for i in items
        ],
    }


@router.post("/items")
def add_item(
    payload: WatchlistItemCreate,
    user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        return {"status": "error", "message": "User not found (register again)"}

    item = WatchlistItem(
        user_id=user.id,
        title=payload.title,
        media_type=payload.type,
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    return {
        "status": "ok",
        "item": {
            "id": item.id,
            "title": item.title,
            "type": item.media_type,
            "created_at": item.created_at.isoformat(),
        },
    }


@router.delete("/items/{item_id}")
def remove_item(
    item_id: int,
    user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    item = (
        db.query(WatchlistItem)
        .filter(WatchlistItem.id == item_id, WatchlistItem.user_id == user.id)
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()

    return {"status": "ok", "deleted_id": item_id}


@router.patch("/items/{item_id}")
def update_item(
    item_id: int,
    payload: WatchlistItemUpdate,
    user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise NotFoundError("User not found")

    item = (
        db.query(WatchlistItem)
        .filter(WatchlistItem.id == item_id, WatchlistItem.user_id == user.id)
        .first()
    )
    if not item:
        raise NotFoundError("Item not found")

    if payload.title is not None:
        item.title = payload.title
    if payload.type is not None:
        item.media_type = payload.type

    db.commit()
    db.refresh(item)

    return {
        "status": "ok",
        "item": {
            "id": item.id,
            "title": item.title,
            "type": item.media_type,
            "created_at": item.created_at.isoformat(),
        },
    }