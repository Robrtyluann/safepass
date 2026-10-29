from collections.abc import Callable

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.database import get_db
from app.core.email import EmailSender, SmtpEmailSender
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import InvalidAccessTokenError, decode_access_token
from app.modules.users.repository import UserRepository
from app.shared.identity import CurrentUser
from app.shared.roles import Role

ACCESS_COOKIE = "access_token"
REFRESH_COOKIE = "refresh_token"

_bearer = HTTPBearer(auto_error=False, description="Alternativa ao cookie (testes e Swagger).")

__all__ = [
    "ACCESS_COOKIE",
    "REFRESH_COOKIE",
    "CurrentUser",
    "get_current_user",
    "get_email_sender",
    "get_optional_user",
    "require_role",
]


def _get_token(
    request: Request, credentials: HTTPAuthorizationCredentials | None = Depends(_bearer)
) -> str | None:
    return request.cookies.get(ACCESS_COOKIE) or (credentials.credentials if credentials else None)


def _authenticate(token: str, db: Session, settings: Settings) -> CurrentUser:
    try:
        payload = decode_access_token(
            token, secret=settings.jwt_secret, algorithm=settings.jwt_algorithm
        )
    except InvalidAccessTokenError as exc:
        raise UnauthorizedError("Sessão inválida ou expirada.") from exc
    user = UserRepository(db).get_by_id(payload.user_id)
    if user is None or not user.is_active:
        raise UnauthorizedError("Sessão inválida ou expirada.")
    # O papel vem do banco (não do token): mudança de papel vale imediatamente.
    return CurrentUser(id=user.id, role=Role(user.role), email=user.email, full_name=user.full_name)


def get_current_user(
    token: str | None = Depends(_get_token),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> CurrentUser:
    if token is None:
        raise UnauthorizedError()
    return _authenticate(token, db, settings)


def get_optional_user(
    token: str | None = Depends(_get_token),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> CurrentUser | None:
    if token is None:
        return None
    try:
        return _authenticate(token, db, settings)
    except UnauthorizedError:
        return None


def require_role(*roles: Role) -> Callable[..., CurrentUser]:
    allowed = frozenset(roles)

    def dependency(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role not in allowed:
            raise ForbiddenError()
        return user

    return dependency


def get_email_sender(settings: Settings = Depends(get_settings)) -> EmailSender:
    return SmtpEmailSender(
        host=settings.smtp_host,
        port=settings.smtp_port,
        sender=settings.mail_from,
        username=settings.smtp_username,
        password=settings.smtp_password,
        starttls=settings.smtp_starttls,
    )
