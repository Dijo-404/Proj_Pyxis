"""Typed application errors translated to stable API responses."""


class ApplicationError(Exception):
    def __init__(self, *, code: str, message: str, status_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class NotFoundError(ApplicationError):
    def __init__(self, entity: str, identifier: str) -> None:
        super().__init__(
            code=f"{entity.upper()}_NOT_FOUND",
            message=f"{entity} '{identifier}' was not found",
            status_code=404,
        )


class ConflictError(ApplicationError):
    def __init__(self, *, code: str, message: str) -> None:
        super().__init__(code=code, message=message, status_code=409)


class ProcessingError(ApplicationError):
    def __init__(self, *, code: str, message: str) -> None:
        super().__init__(code=code, message=message, status_code=422)


class LocalAIUnavailableError(ApplicationError):
    def __init__(self, message: str) -> None:
        super().__init__(code="LOCAL_AI_UNAVAILABLE", message=message, status_code=503)


class ExternalAIUnavailableError(ApplicationError):
    def __init__(self, message: str) -> None:
        super().__init__(code="EXTERNAL_AI_UNAVAILABLE", message=message, status_code=503)
