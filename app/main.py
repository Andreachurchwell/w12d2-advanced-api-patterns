from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.middleware import RequestIDMiddleware
from app.core.exceptions import AppError, NotFoundError
from app.db.init_db import init_db
from sqlalchemy import text
from app.db.session import SessionLocal
from fastapi import Response

def create_app() -> FastAPI:
    app = FastAPI(title="Watchlist API", version="1.0.0")

    app.add_middleware(RequestIDMiddleware)

    @app.on_event("startup")
    def on_startup():
        init_db()

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

        # ---- DB check ----
        db_status = "ok"
        try:
            db = SessionLocal()
            db.execute(text("SELECT 1"))
        except Exception as e:
            db_status = "error"
        finally:
            try:
                db.close()
            except Exception:
                pass

        # ---- Redis check (placeholder until Redis is wired) ----
        redis_status = "not_configured"

        overall = "ok" if db_status == "ok" and redis_status in ("ok", "not_configured") else "degraded"

        return {
            "status": overall,
            "request_id": request_id,
            "dependencies": {
                "db": {"status": db_status},
                "redis": {"status": redis_status},
            },
        }


    @app.get("/test-error")
    def test_error():
        raise NotFoundError("Test error works")


    @app.middleware("http")
    async def add_rate_limit_headers(request: Request, call_next):
        response: Response = await call_next(request)
        headers = getattr(request.state, "rate_limit_headers", None)
        if headers:
            for k, v in headers.items():
                response.headers[k] = v
        return response


    return app




app = create_app()

