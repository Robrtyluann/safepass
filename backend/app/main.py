from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.modules.auth.router import router as auth_router
from app.modules.plans.router import admin_router as plans_admin_router
from app.modules.plans.router import router as plans_router
from app.modules.platform_reviews.router import admin_router as platform_reviews_admin_router
from app.modules.platform_reviews.router import router as platform_reviews_router
from app.modules.referrals.router import admin_router as referrals_admin_router
from app.modules.referrals.router import router as referrals_router
from app.modules.stats.router import admin_router as stats_admin_router
from app.modules.stats.router import router as stats_router
from app.modules.subscriptions.router import router as subscriptions_router


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="SAFEpass API",
        version="0.1.0",
        description="Backend do Desafio 01: identidade, planos, assinaturas e painel admin.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)

    api_v1 = APIRouter(prefix="/api/v1")
    for router in (
        auth_router,
        plans_router,
        plans_admin_router,
        subscriptions_router,
        platform_reviews_router,
        platform_reviews_admin_router,
        referrals_router,
        referrals_admin_router,
        stats_router,
        stats_admin_router,
    ):
        api_v1.include_router(router)
    app.include_router(api_v1)

    @app.get("/health", tags=["health"], summary="Healthcheck")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
