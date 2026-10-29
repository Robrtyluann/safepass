"""Testes de integração: precisam de PostgreSQL (DATABASE_URL). Sem banco, são pulados.

Atenção: criam e TRUNCAM tabelas. Use um banco de teste, nunca o de desenvolvimento com dados.
"""

import pytest
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

TABLES = (
    "referrals, platform_reviews, subscriptions, plans, "
    "password_reset_tokens, refresh_tokens, users"
)


@pytest.fixture(scope="session")
def engine_ready():  # type: ignore[no-untyped-def]
    from app.core import models_registry  # noqa: F401
    from app.core.database import Base, engine

    try:
        with engine.connect() as conn:
            conn.execute(text("select 1"))
    except OperationalError:
        pytest.skip("PostgreSQL indisponível (defina DATABASE_URL para um banco de teste).")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def client(engine_ready):  # type: ignore[no-untyped-def]
    from fastapi.testclient import TestClient

    from app.core.database import SessionLocal
    from app.main import app
    from app.modules.plans.repository import PlanRepository
    from app.modules.plans.seed import DEFAULT_PLANS

    with SessionLocal() as db:
        repo = PlanRepository(db)
        for plan in DEFAULT_PLANS:
            repo.upsert_by_code(plan)
        db.commit()

    yield TestClient(app)

    with engine_ready.begin() as conn:
        conn.execute(text(f"TRUNCATE {TABLES} RESTART IDENTITY CASCADE"))
