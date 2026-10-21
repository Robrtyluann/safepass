from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import DomainError
from app.integrations.identity import IdentityGateway, Principal, UnconfiguredIdentity

bearer = HTTPBearer(auto_error=False)


def get_identity() -> IdentityGateway:
    return UnconfiguredIdentity()


def get_current_user(
    credential: HTTPAuthorizationCredentials | None = Depends(bearer),
    identity: IdentityGateway = Depends(get_identity),
) -> Principal:
    if credential is None:
        raise DomainError("unauthenticated", "Sessão necessária.", 401)
    return identity.authenticate(credential.credentials)
