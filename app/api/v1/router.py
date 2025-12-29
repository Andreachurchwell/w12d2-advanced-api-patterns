from fastapi import APIRouter
from app.api.v1 import auth, watchlists
from app.api.v1 import external


api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(watchlists.router, prefix="/watchlists", tags=["watchlists"])
api_router.include_router(external.router)