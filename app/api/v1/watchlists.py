from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.rate_limit import rate_limit
from app.api.v1.auth import get_current_user
from app.db.deps import get_db
from app.db.models import User, WatchlistItem
from app.core.exceptions import NotFoundError
import json
from app.core.redis_client import redis_client
from fastapi import HTTPException
from app.core.app_logger import logger


router = APIRouter()

def write_audit_log(message: str) -> None:
    with open("audit.log", "a", encoding="utf-8") as f:
        f.write(message + "\n")

class WatchlistItemCreate(BaseModel):
    title: str
    type: str  # "movie" or "show"

class WatchlistItemUpdate(BaseModel):
    title: str | None = None
    type: str | None = None

@router.get("/", dependencies=[rate_limit(limit=10, window_seconds=60)])
async def list_watchlist(
    user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 25,
    media_type: str | None = None,
    sort: str = "created_at_desc",
):
    # ---- validate pagination ----
    if skip < 0:
        skip = 0
    if limit < 1:
        limit = 1
    if limit > 100:
        limit = 100

    # ---- validate filters/sort ----
    if media_type is not None and media_type not in ("movie", "show"):
        raise HTTPException(status_code=400, detail="media_type must be 'movie' or 'show'")

    if sort not in ("created_at_desc", "created_at_asc"):
        raise HTTPException(status_code=400, detail="sort must be 'created_at_desc' or 'created_at_asc'")

    # ✅ IMPORTANT: cache key must include params
    cache_key = f"cache:watchlist:{user_email}:skip={skip}:limit={limit}:type={media_type}:sort={sort}"

    # ---- Redis cache check ----
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # ---- DB query ----
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        response = {"user": user_email, "watchlist": []}
        await redis_client.setex(cache_key, 30, json.dumps(response))
        return response

    query = db.query(WatchlistItem).filter(WatchlistItem.user_id == user.id)

    if media_type is not None:
        query = query.filter(WatchlistItem.media_type == media_type)

    if sort == "created_at_asc":
        query = query.order_by(WatchlistItem.created_at.asc())
    else:
        query = query.order_by(WatchlistItem.created_at.desc())

    items = query.offset(skip).limit(limit).all()

    response = {
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

    await redis_client.setex(cache_key, 30, json.dumps(response))
    return response


@router.post("/items")
async def add_item(
    payload: WatchlistItemCreate,
    background_tasks: BackgroundTasks,
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
    await redis_client.delete(f"cache:watchlist:{user_email}")
    db.refresh(item)
    logger.info(
        "watchlist_item_added",
        extra={"user": user_email, "item_id": item.id},
    )
    background_tasks.add_task(
        write_audit_log,
        f"user={user_email} action=add_item id={item.id} title={item.title}",
    )


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
async def remove_item(
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
    await redis_client.delete(f"cache:watchlist:{user_email}")

    return {"status": "ok", "deleted_id": item_id}


@router.patch("/items/{item_id}")
async def update_item(
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
    await redis_client.delete(f"cache:watchlist:{user_email}")

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