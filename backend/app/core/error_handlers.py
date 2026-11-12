import logging
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import DocumentNotFoundError, InvalidDocumentFileError, EmailAlreadyRegisteredError, AuthenticationError, ForbiddenError


logger = logging.getLogger(__name__)


def error_payload(
    *,
    code: str,
    message: str,
    details: list[dict] | None = None
) -> dict:
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details,
        }
    }


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DocumentNotFoundError)
    async def document_not_found(request: Request, exc: DocumentNotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content=error_payload(code="DOCUMENT_NOT_FOUND", message=str(exc)))


    @app.exception_handler(InvalidDocumentFileError)
    async def invalid_document(request: Request, exc: InvalidDocumentFileError) -> JSONResponse:
        return JSONResponse(status_code=400, content=error_payload(code="INVALID_DOCUMENT_FILE", message=str(exc)))


    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(status_code=422, content=error_payload(code="VALIDATION_ERROR", message=("La richiesta contiene dati non validi."), details=jsonable_encoder(exc.errors())))


    @app.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content=error_payload(code="HTTP_ERROR", message=str(exc.detail)))


    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled API error", exc_info=exc)
        return JSONResponse(status_code=500, content=error_payload(code="INTERNAL_SERVER_ERROR", message="Si è verificato un errore interno."))


    @app.exception_handler(EmailAlreadyRegisteredError)
    async def email_already_registered(request: Request, exc: EmailAlreadyRegisteredError) -> JSONResponse:
        return JSONResponse(status_code=409, content=error_payload(code="EMAIL_ALREADY_REGISTERED", message=str(exc)))


    @app.exception_handler(AuthenticationError)
    async def authentication_error(request: Request, exc: AuthenticationError) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            headers={"WWW-Authenticate": "Bearer"},
            content=error_payload(code="AUTHENTICATION_ERROR", message=str(exc))
        )


    @app.exception_handler(ForbiddenError)
    async def forbidden_error(request: Request, exc: ForbiddenError) -> JSONResponse:
        return JSONResponse(status_code=403, content=error_payload(code="FORBIDDEN", message=str(exc)))