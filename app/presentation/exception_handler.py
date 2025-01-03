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
from app.domain.base.exceptions import DomainError
from app.domain.birthing_person.exceptions import (
    BirthingPersonDoesNotHaveActiveLabour,
    BirthingPersonExistsWithID,
    BirthingPersonHasActiveLabour,
    BirthingPersonNotFoundById,
)
from app.domain.labour.exceptions import (
    CannotCompleteLabourWithActiveContraction,
    LabourCompleted,
    LabourHasActiveContraction,
    LabourHasNoActiveContraction,
)
from app.domain.subscriber.exceptions import (
    SubscriberAlreadySubscribedToBirthingPerson,
    SubscriberExistsWithID,
    SubscriberNotFoundById,
    SubscriberNotSubscribedToBirthingPerson,
    SubscriptionTokenIncorrect,
)
from app.infrastructure.auth.interfaces.exceptions import AuthorizationError, InvalidTokenError

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
            DomainError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            ApplicationError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            BirthingPersonNotFoundById: status.HTTP_404_NOT_FOUND,
            BirthingPersonExistsWithID: status.HTTP_409_CONFLICT,
            BirthingPersonHasActiveLabour: status.HTTP_400_BAD_REQUEST,
            BirthingPersonDoesNotHaveActiveLabour: status.HTTP_404_NOT_FOUND,
            LabourHasActiveContraction: status.HTTP_400_BAD_REQUEST,
            LabourHasNoActiveContraction: status.HTTP_400_BAD_REQUEST,
            LabourCompleted: status.HTTP_400_BAD_REQUEST,
            CannotCompleteLabourWithActiveContraction: status.HTTP_400_BAD_REQUEST,
            SubscriberAlreadySubscribedToBirthingPerson: status.HTTP_400_BAD_REQUEST,
            SubscriberExistsWithID: status.HTTP_409_CONFLICT,
            SubscriberNotFoundById: status.HTTP_404_NOT_FOUND,
            SubscriberNotSubscribedToBirthingPerson: status.HTTP_400_BAD_REQUEST,
            SubscriptionTokenIncorrect: status.HTTP_403_FORBIDDEN,
            AuthorizationError: status.HTTP_401_UNAUTHORIZED,
            InvalidTokenError: status.HTTP_401_UNAUTHORIZED,
        }

    def get_status_code(self, exc: Exception) -> int:
        return self.exceptions_status_code_map.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExceptionHeaderMapper:
    def __init__(self) -> None:
        self._exceptions_headers_map: dict[type[Exception], dict[str, Any]] = {
            InvalidTokenError: {"WWW-Authenticate": "Bearer"}
        }

    def get_headers(self, exc: Exception) -> dict[str, Any] | None:
        return self._exceptions_headers_map.get(type(exc))


class ExceptionHandler:
    def __init__(
        self,
        app: FastAPI,
        exception_message_provider: ExceptionMessageProvider,
        exception_mapper: ExceptionMapper,
        exception_header_mapper: ExceptionHeaderMapper,
    ):
        self._app = app
        self._mapper = exception_mapper
        self._header_mapper = exception_header_mapper
        self._exception_message_provider = exception_message_provider

    def setup_handlers(self) -> None:
        for exc_class in self._mapper.exceptions_status_code_map:
            self._app.add_exception_handler(exc_class, self._handle_exception)
        self._app.add_exception_handler(Exception, self._handle_unexpected_exceptions)

    async def _handle_exception(self, _: Request, exc: Exception) -> ORJSONResponse:
        status_code = self._mapper.get_status_code(exc)
        headers = self._header_mapper.get_headers(exc)

        if status_code >= 500:
            log.error(f"Exception {type(exc).__name__} occurred: {exc}", exc_info=True)
        else:
            log.warning(f"Exception {type(exc).__name__} occurred: {exc}")

        exception_message = self._exception_message_provider.get_exception_message(exc, status_code)

        details = exc.errors() if isinstance(exc, pydantic.ValidationError) else None
        return self._create_exception_response(status_code, exception_message, details, headers)

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
        headers: dict[str, Any] | None = None,
    ) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=status_code,
            content=(
                ExceptionSchemaRich(exception_message, jsonable_encoder(details))
                if details
                else ExceptionSchema(exception_message)
            ),
            headers=headers,
        )
