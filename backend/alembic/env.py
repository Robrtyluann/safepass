from sqlalchemy import create_engine, pool

from alembic import context
from app.core.config import get_settings
from app.core.database import Base
from app.modules.alerts import models as alerts
from app.modules.coupons import models as coupons
from app.modules.dependents import models as dependents
from app.modules.marketplace import models as marketplace
from app.modules.points import models as points
from app.modules.reviews import models as reviews

# Imports register every module before autogeneration; no create_all at startup.
assert alerts.Alert and coupons.Coupon and dependents.Dependent
assert marketplace.Favorite and points.ManagerAccount and reviews.Review
config = context.config
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=get_settings().database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_engine(get_settings().database_url, poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
