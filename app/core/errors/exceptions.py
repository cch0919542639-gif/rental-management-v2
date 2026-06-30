class AppError(Exception):
    status_code = 400
    code = "app_error"

    def __init__(self, message: str, *, status_code: int | None = None, code: str | None = None, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details
        if status_code is not None:
            self.status_code = status_code
        if code is not None:
            self.code = code


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"


class ConflictError(AppError):
    status_code = 409
    code = "conflict"


class DomainValidationError(AppError):
    status_code = 422
    code = "validation_error"
