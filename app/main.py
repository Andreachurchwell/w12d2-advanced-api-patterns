from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.middleware import RequestIDMiddleware
from app.core.exceptions import AppError, NotFoundError


from app.db.init_db import init_db


def create_app() -> FastAPI:
    app = FastAPI(title="Watchlist API", version="1.0.0")

    app.add_middleware(RequestIDMiddleware)

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        request_id = getattr(request.state, "request_id", None)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "request_id": request_id,
                }
            },
        )

    app.include_router(api_router, prefix="/v1")

    @app.get("/health")
    def health():
        return {"status": "ok"}
    
    @app.get("/health/detailed")
    def health_detailed(request: Request):
        request_id = getattr(request.state, "request_id", None)
        return {
            "status": "ok",
            "request_id": request_id,
            "dependencies": {
                "redis": {"status": "unknown"},
                "db": {"status": "unknown"},
            },
        }

    @app.get("/test-error")
    def test_error():
        raise NotFoundError("Test error works")

    return app


    @app.on_event("startup")
    def on_startup():
        init_db()

app = create_app()

