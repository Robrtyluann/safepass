from collections.abc import Awaitable, Callable
from uuid import uuid4

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.exceptions import DomainError
from app.modules.alerts.router import router as alerts
from app.modules.coupons.router import router as coupons
from app.modules.dashboard.router import router as dashboard
from app.modules.dependents.router import router as dependents
from app.modules.marketplace.router import router as marketplace
from app.modules.points.router import router as points
from app.modules.reviews.router import router as reviews


def create_app() -> FastAPI:
    app = FastAPI(title="SAFEpass — Marketplace, Pontos e Cupons", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_settings().cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "PUT"],
        allow_headers=["Authorization", "Content-Type", "Idempotency-Key"],
    )

    @app.middleware("http")
    async def request_id(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Generate internally; do not echo untrusted request headers into logs.
        request.state.request_id = str(uuid4())
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        return response

    @app.exception_handler(DomainError)
    async def domain_error(request: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        # Do not echo inputs, token contents, PII or exception context.
        details = [
            {"field": ".".join(str(i) for i in e["loc"]), "type": e["type"]} for e in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "validation_error",
                    "message": "Dados inválidos.",
                    "details": details,
                }
            },
        )

    @app.exception_handler(SQLAlchemyError)
    async def database_error(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            content={
                "error": {
                    "code": "database_unavailable",
                    "message": "Banco de dados indisponível.",
                }
            },
        )

    @app.get("/health", summary="Verificar conexão com PostgreSQL", tags=["health"])
    def health(db: Session = Depends(get_db)) -> dict[str, str]:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "ok"}

    for router in (dashboard, marketplace, reviews, points, coupons, dependents, alerts):
        app.include_router(router, prefix="/api/v1")
    return app


app = create_app()
