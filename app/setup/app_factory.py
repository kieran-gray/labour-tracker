# pylint: disable=C0301 (line-too-long)
__all__ = ("initialize_mapping", "create_app_with_container")

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from starlette.middleware.cors import CORSMiddleware

from app.infrastructure.persistence.sqla import initialize_mapping
from app.presentation.http_controllers.exception_handler import (
    ExceptionHandler,
    ExceptionMapper,
    ExceptionMessageProvider,
)
from app.presentation.http_controllers.router_root import root_router
from app.presentation.http_middleware.middleware_auth import AuthMiddleware
from app.setup.config.settings import Settings
from app.setup.ioc.ioc_registry import get_providers


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield None
    await app.state.dishka_container.close()  # noqa; app.state is the place where dishka_container lives


def configure_app(new_app: FastAPI, settings: Settings) -> None:
    new_app.include_router(root_router)
    new_app.add_middleware(AuthMiddleware)  # noqa
    new_app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.security.cors.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    exception_message_provider: ExceptionMessageProvider = (
        ExceptionMessageProvider()
    )
    exception_mapper: ExceptionMapper = ExceptionMapper()
    exception_handler: ExceptionHandler = ExceptionHandler(
        new_app, exception_message_provider, exception_mapper
    )
    exception_handler.setup_handlers()


def create_app(settings: Settings) -> FastAPI:
    new_app: FastAPI = FastAPI(
        lifespan=lifespan, default_response_class=ORJSONResponse
    )
    configure_app(new_app, settings)
    return new_app


def create_app_with_container(settings: Settings) -> FastAPI:
    new_app = create_app(settings)
    async_container: AsyncContainer = make_async_container(
        *get_providers(), context={Settings: settings}
    )
    setup_dishka(async_container, new_app)
    return new_app
