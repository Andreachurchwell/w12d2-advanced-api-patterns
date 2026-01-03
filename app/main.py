from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware  

from app.api.v1.router import api_router
from app.core.middleware import RequestIDMiddleware
from app.core.exceptions import AppError, NotFoundError
from app.db.init_db import init_db


def create_app() -> FastAPI:
    app = FastAPI(title="Watchlist API", version="1.0.0")

    # CORS (safe default for local dev + Streamlit)
    origins = [
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

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

    @app.get("/favicon.ico", include_in_schema=False)
    def favicon():
        return Response(status_code=204)

    @app.get("/test-error")
    def test_error():
        raise NotFoundError("Test error works")

    return app


app = create_app()
