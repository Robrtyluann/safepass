from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class DomainError(Exception):
    """Erro de regra de negócio. Cada módulo herda e define status_code e code."""

    status_code: int = 400
    code: str = "domain_error"
    default_message: str = "Não foi possível concluir a operação."

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.default_message
        super().__init__(self.message)


class NotFoundError(DomainError):
    status_code = 404
    code = "not_found"
    default_message = "Recurso não encontrado."


class ConflictError(DomainError):
    status_code = 409
    code = "conflict"
    default_message = "Conflito com o estado atual do recurso."


class UnauthorizedError(DomainError):
    status_code = 401
    code = "unauthorized"
    default_message = "Faça login para continuar."


class ForbiddenError(DomainError):
    status_code = 403
    code = "forbidden"
    default_message = "Você não tem permissão para esta ação."


class BusinessRuleError(DomainError):
    status_code = 422
    code = "business_rule_violation"
    default_message = "A operação viola uma regra de negócio."


class TooManyRequestsError(DomainError):
    status_code = 429
    code = "too_many_requests"
    default_message = "Muitas tentativas. Aguarde um instante e tente novamente."


def error_body(code: str, message: str, details: list[dict[str, str]] | None = None) -> dict[str, Any]:
    body: dict[str, Any] = {"error": {"code": code, "message": message}}
    if details:
        body["error"]["details"] = details
    return body


def register_exception_handlers(app: FastAPI) -> None:
    """Padroniza todos os erros no formato {"error": {"code", "message"}}."""

    @app.exception_handler(DomainError)
    async def handle_domain_error(_: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content=error_body(exc.code, exc.message))

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        details = [
            {"field": ".".join(str(part) for part in err["loc"][1:]), "message": str(err["msg"])}
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content=error_body("validation_error", "Dados inválidos.", details),
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_error(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=error_body(f"http_{exc.status_code}", str(exc.detail)),
        )
