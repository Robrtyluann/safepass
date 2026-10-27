"""Explicit local-development adapter. Never enabled by app.main or environment flags."""

from uuid import UUID

from app.core.exceptions import DomainError, missing
from app.integrations.identity import Principal

MANAGER = UUID("20000000-0000-0000-0000-000000000001")
OTHER_MANAGER = UUID("20000000-0000-0000-0000-000000000002")
DEPENDENT = UUID("20000000-0000-0000-0000-000000000003")
PLAN_PREMIUM = UUID("20000000-0000-0000-0000-00000000000a")


class LocalIdentity:
    identities = {
        "local-manager": Principal(MANAGER, frozenset({"user"}), plan_id=PLAN_PREMIUM),
        "local-other-manager": Principal(OTHER_MANAGER, frozenset({"user"})),
        "local-dependent": Principal(DEPENDENT, frozenset({"dependent"})),
    }

    def authenticate(self, credential: str) -> Principal:
        principal = self.identities.get(credential)
        if principal is None:
            raise DomainError("unauthenticated", "Sessão inválida.", 401)
        return principal

    def require_user(self, user_id: UUID) -> None:
        if not any(p.user_id == user_id for p in self.identities.values()):
            raise missing()
