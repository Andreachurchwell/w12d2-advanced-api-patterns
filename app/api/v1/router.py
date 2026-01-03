from fastapi import APIRouter
from app.api.v1 import auth, watchlists, external
from app.api.v1 import health
from app.api.v1 import admin

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(watchlists.router, prefix="/watchlists", tags=["watchlists"])
api_router.include_router(external.router, prefix="/external", tags=["external"])
api_router.include_router(health.router, tags=["health"])
api_router.include_router(admin.router)