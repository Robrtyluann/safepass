"""Importa todos os models para que `Base.metadata` fique completo (Alembic e testes).

Quando um squad adicionar módulo novo, registre o `models` dele aqui.
"""

from app.modules.auth import models as auth_models
from app.modules.platform_reviews import models as platform_reviews_models
from app.modules.plans import models as plans_models
from app.modules.referrals import models as referrals_models
from app.modules.subscriptions import models as subscriptions_models
from app.modules.users import models as users_models

__all__ = [
    "auth_models",
    "plans_models",
    "platform_reviews_models",
    "referrals_models",
    "subscriptions_models",
    "users_models",
]
