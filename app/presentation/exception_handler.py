import logging
from dataclasses import dataclass
from typing import Any

import pydantic
from fastapi import FastAPI, status
from fastapi.encoders import jsonable_encoder
from fastapi.requests import Request
from fastapi.responses import ORJSONResponse
from pydantic_core import ErrorDetails

from app.application.base.exceptions import ApplicationError
from app.application.exceptions import (
    AuthenticationError,
    AuthorizationError,
)
from app.domain.base.exceptions import DomainError

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ExceptionSchema:
    description: str


@dataclass(frozen=True, slots=True)
class ExceptionSchemaRich:
    description: str
    details: list[dict[str, Any]] | None = None


class ExceptionMessageProvider:
    @staticmethod
    def get_exception_message(exc: Exception, status_code: int) -> str:
        return "Internal server error." if status_code == 500 else str(exc)


class ExceptionMapper:
    def __init__(self) -> None:
        self.exceptions_status_code_map: dict[type[Exception], int] = {
            pydantic.ValidationError: status.HTTP_400_BAD_REQUEST,
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            DomainError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            ApplicationError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        }

    def get_status_code(self, exc: Exception) -> int:
        return self.exceptions_status_code_map.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExceptionHandler:
    def __init__(
        self,
        app: FastAPI,
        exception_message_provider: ExceptionMessageProvider,
        exception_mapper: ExceptionMapper,
    ):
        self._app = app
        self._mapper = exception_mapper
        self._exception_message_provider = exception_message_provider

    def setup_handlers(self) -> None:
        for exc_class in self._mapper.exceptions_status_code_map:
            self._app.add_exception_handler(exc_class, self._handle_exception)
        self._app.add_exception_handler(Exception, self._handle_unexpected_exceptions)

    async def _handle_exception(self, _: Request, exc: Exception) -> ORJSONResponse:
        status_code = self._mapper.get_status_code(exc)

        if status_code >= 500:
            log.error(f"Exception {type(exc).__name__} occurred: {exc}", exc_info=True)
        else:
            log.warning(f"Exception {type(exc).__name__} occurred: {exc}")

        exception_message = self._exception_message_provider.get_exception_message(exc, status_code)

        details = exc.errors() if isinstance(exc, pydantic.ValidationError) else None
        return self._create_exception_response(status_code, exception_message, details)

    async def _handle_unexpected_exceptions(self, _: Request, exc: Exception) -> ORJSONResponse:
        log.error(f"Unexpected exception {type(exc).__name__} occurred: {exc}", exc_info=True)
        exception_message: str = "Internal server error."
        return self._create_exception_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR, exception_message
        )

    @staticmethod
    def _create_exception_response(
        status_code: int,
        exception_message: str,
        details: list[ErrorDetails] | None = None,
    ) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=status_code,
            content=(
                ExceptionSchemaRich(exception_message, jsonable_encoder(details))
                if details
                else ExceptionSchema(exception_message)
            ),
        )
