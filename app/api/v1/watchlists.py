from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.rate_limit import rate_limit
from app.api.v1.auth import get_current_user, require_admin
from app.db.deps import get_db
from app.db.models import User, WatchlistItem
from app.core.exceptions import NotFoundError
import json
from app.core.redis_client import redis_client, delete_pattern
from fastapi import BackgroundTasks
from app.core.audit import write_audit_log

router = APIRouter()

class WatchlistItemCreate(BaseModel):
    title: str
    type: str  # "movie" or "show"

class WatchlistItemUpdate(BaseModel):
    title: str | None = None
    type: str | None = None


@router.get("/", dependencies=[Depends(rate_limit("watchlists:list", 60, 60))])
async def list_watchlist(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10,
    type: str | None = None,
    sort: str = "created_at_desc",
):
    cache_key = f"cache:watchlists:{user.email}:skip={skip}:limit={limit}:type={type}:sort={sort}"


    cached = None
    try:
        cached = await redis_client.get(cache_key)
    except Exception:
        cached = None

    if cached:
        return json.loads(cached)

    q = db.query(WatchlistItem).filter(WatchlistItem.user_id == user.id)

    if type:
        q = q.filter(WatchlistItem.media_type == type)

    if sort == "created_at_asc":
        q = q.order_by(WatchlistItem.created_at.asc())
    else:
        q = q.order_by(WatchlistItem.created_at.desc())

    items = q.offset(skip).limit(limit).all()

    response = {
        "user": user.email,
        "skip": skip,
        "limit": limit,
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

    try:
        await redis_client.setex(cache_key, 30, json.dumps(response))
    except Exception:
        pass
    return response



@router.post("/items", status_code=201, dependencies=[Depends(rate_limit("watchlists:write", 30, 60))])
async def add_item(
    payload: WatchlistItemCreate,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = WatchlistItem(
        user_id=user.id,
        title=payload.title,
        media_type=payload.type,
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    background_tasks.add_task(
        write_audit_log,
        f"user={user.email} action=add item_id={item.id} title={item.title} type={item.media_type}"
    )

    await delete_pattern(f"cache:watchlists:{user.email}:*")

    return {
        "status": "ok",
        "item": {
            "id": item.id,
            "title": item.title,
            "type": item.media_type,
            "created_at": item.created_at.isoformat(),
        },
    }


@router.delete("/items/{item_id}", status_code=204, dependencies=[Depends(rate_limit("watchlists:write", 30, 60))])
async def remove_item(
    item_id: int,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = (
        db.query(WatchlistItem)
        .filter(WatchlistItem.id == item_id, WatchlistItem.user_id == user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    deleted_title = item.title
    db.delete(item)
    db.commit()
    background_tasks.add_task(
        write_audit_log,
        f"user={user.email} action=delete item_id={item_id} title={deleted_title}"
    )

    await delete_pattern(f"cache:watchlists:{user.email}:*")

    return


@router.patch("/items/{item_id}", dependencies=[Depends(rate_limit("watchlists:write", 30, 60))])
async def update_item(
    item_id: int,
    payload: WatchlistItemUpdate,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
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
    background_tasks.add_task(
        write_audit_log,
        f"user={user.email} action=update item_id={item.id} title={item.title} type={item.media_type}"
    )

    await delete_pattern(f"cache:watchlists:{user.email}:*")

    return {
        "status": "ok",
        "item": {
            "id": item.id,
            "title": item.title,
            "type": item.media_type,
            "created_at": item.created_at.isoformat(),
        },
    }