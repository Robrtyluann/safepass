"""Explicit local-development adapter. Never enabled by app.main or environment flags."""

from uuid import UUID

from app.core.exceptions import DomainError, missing
from app.integrations.identity import Principal

OWNER = UUID("10000000-0000-0000-0000-000000000001")
ADMIN = UUID("10000000-0000-0000-0000-000000000002")
EMPLOYEE = UUID("10000000-0000-0000-0000-000000000003")
OTHER = UUID("10000000-0000-0000-0000-000000000004")


class LocalIdentity:
    identities = {
        "local-owner": Principal(OWNER, frozenset({"provider", "company"})),
        "local-admin": Principal(ADMIN, frozenset({"admin"})),
        "local-employee": Principal(EMPLOYEE, frozenset({"user"})),
        "local-other": Principal(OTHER, frozenset({"provider", "company"})),
    }

    def authenticate(self, credential: str) -> Principal:
        principal = self.identities.get(credential)
        if principal is None:
            raise DomainError("unauthenticated", "Sessão inválida.", 401)
        return principal

    def require_user(self, user_id: UUID) -> None:
        if not any(p.user_id == user_id for p in self.identities.values()):
            raise missing()
