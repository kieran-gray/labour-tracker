from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, status

from app.application.services.birthing_person_service import BirthingPersonService
from app.infrastructure.custom_types import KeycloakUser
from app.presentation.api.auth import get_user_info
from app.presentation.api.schemas.requests.birthing_person import (
    AddContactRequest,
    RegisterBirthingPersonRequest,
)
from app.presentation.api.schemas.responses.birthing_person import BirthingPersonResponse
from app.presentation.exception_handler import ExceptionSchema

birthing_person_router = APIRouter(prefix="/birthing-person", tags=["Birthing Person"])


@birthing_person_router.post(
    "/register",
    responses={
        status.HTTP_200_OK: {"model": BirthingPersonResponse},
        status.HTTP_400_BAD_REQUEST: {"model": ExceptionSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ExceptionSchema},
    },
    status_code=status.HTTP_200_OK,
)
@inject
async def register(
    request_data: RegisterBirthingPersonRequest,
    service: FromDishka[BirthingPersonService],
    user: KeycloakUser = Depends(get_user_info),
) -> BirthingPersonResponse:
    birthing_person = await service.register(
        birthing_person_id=user.id, name=request_data.name, first_labour=request_data.first_labor
    )
    return BirthingPersonResponse(birthing_person=birthing_person)


@birthing_person_router.post(
    "/add-contact",
    responses={
        status.HTTP_200_OK: {"model": BirthingPersonResponse},
        status.HTTP_400_BAD_REQUEST: {"model": ExceptionSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ExceptionSchema},
    },
    status_code=status.HTTP_200_OK,
)
@inject
async def add_contact(
    request_data: AddContactRequest,
    service: FromDishka[BirthingPersonService],
    user: KeycloakUser = Depends(get_user_info),
) -> BirthingPersonResponse:
    birthing_person = await service.add_contact(
        birthing_person_id=user.id,
        name=request_data.name,
        contact_methods=request_data.contact_methods,
        phone_number=request_data.phone_number,
        email=request_data.email,
    )
    return BirthingPersonResponse(birthing_person=birthing_person)


@birthing_person_router.get(
    "/",
    responses={
        status.HTTP_200_OK: {"model": BirthingPersonResponse},
        status.HTTP_400_BAD_REQUEST: {"model": ExceptionSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_404_NOT_FOUND: {"model": ExceptionSchema},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ExceptionSchema},
    },
    status_code=status.HTTP_200_OK,
)
@inject
async def get_birthing_person(
    service: FromDishka[BirthingPersonService],
    user: KeycloakUser = Depends(get_user_info),
) -> BirthingPersonResponse:
    birthing_person = await service.get_birthing_person(birthing_person_id=user.id)
    return BirthingPersonResponse(birthing_person=birthing_person)
