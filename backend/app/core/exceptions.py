class DomainError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 422):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def missing() -> DomainError:
    return DomainError("not_found", "Recurso não encontrado.", 404)


def forbidden() -> DomainError:
    return DomainError("forbidden", "Você não tem permissão para esta operação.", 403)


def conflict(message: str) -> DomainError:
    return DomainError("conflict", message, 409)


def unavailable() -> DomainError:
    return DomainError("integration_unavailable", "Integração ainda não configurada.", 503)
