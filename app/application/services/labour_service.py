import logging
from datetime import datetime

from app.application.dtos.labour import LabourDTO
from app.application.dtos.labour_summary import LabourSummaryDTO
from app.application.interfaces.notfication_gateway import NotificationGateway
from app.domain.birthing_person.exceptions import (
    BirthingPersonDoesNotHaveActiveLabour,
    BirthingPersonNotFoundById,
)
from app.domain.birthing_person.repository import BirthingPersonRepository
from app.domain.birthing_person.vo_birthing_person_id import BirthingPersonId
from app.domain.labour.repository import LabourRepository
from app.domain.services.begin_labour import BeginLabourService
from app.domain.services.complete_labour import CompleteLabourService
from app.domain.services.end_contraction import EndContractionService
from app.domain.services.start_contraction import StartContractionService

log = logging.getLogger(__name__)


class LabourService:
    def __init__(
        self,
        birthing_person_repository: BirthingPersonRepository,
        labour_repository: LabourRepository,
        notification_gateway: NotificationGateway,
    ):
        self._birthing_person_repository = birthing_person_repository
        self._labour_repository = labour_repository
        self._notification_gateway = notification_gateway

    async def begin_labour(
        self, birthing_person_id: str, first_labour: bool | None = None
    ) -> LabourDTO:
        domain_id = BirthingPersonId(birthing_person_id)
        birthing_person = await self._birthing_person_repository.get_by_id(domain_id)
        if not birthing_person:
            raise BirthingPersonNotFoundById(birthing_person_id=birthing_person_id)

        BeginLabourService().begin_labour(
            birthing_person=birthing_person, first_labour=first_labour
        )
        await self._birthing_person_repository.save(birthing_person)
        assert birthing_person.active_labour

        # TODO instead of handling domain events here, add them to a Kafka producer and handle them
        # in a dedictead consumer

        for event in birthing_person.active_labour.clear_domain_events():
            self._notification_gateway.send(event.to_dict())

        return LabourDTO.from_domain(birthing_person.active_labour)

    async def complete_labour(
        self, birthing_person_id: str, end_time: datetime | None = None, notes: str | None = None
    ) -> LabourDTO:
        domain_id = BirthingPersonId(birthing_person_id)
        birthing_person = await self._birthing_person_repository.get_by_id(domain_id)
        if not birthing_person:
            raise BirthingPersonNotFoundById(birthing_person_id=birthing_person_id)

        labour = CompleteLabourService().complete_labour(
            birthing_person=birthing_person, end_time=end_time, notes=notes
        )
        await self._labour_repository.save(labour)

        # TODO instead of handling domain events here, add them to a Kafka producer and handle them
        # in a dedictead consumer

        for event in labour.clear_domain_events():
            self._notification_gateway.send(event.to_dict())

        return LabourDTO.from_domain(labour)

    async def start_contraction(
        self,
        birthing_person_id: str,
        intensity: int | None = None,
        start_time: datetime | None = None,
        notes: str | None = None,
    ) -> LabourDTO:
        domain_id = BirthingPersonId(birthing_person_id)
        birthing_person = await self._birthing_person_repository.get_by_id(domain_id)
        if not birthing_person:
            raise BirthingPersonNotFoundById(birthing_person_id=birthing_person_id)

        labour = StartContractionService().start_contraction(
            birthing_person=birthing_person, intensity=intensity, start_time=start_time, notes=notes
        )

        await self._labour_repository.save(labour)

        # TODO instead of handling domain events here, add them to a Kafka producer and handle them
        # in a dedictead consumer

        for event in birthing_person.active_labour.clear_domain_events():
            self._notification_gateway.send(event.to_dict())


        return LabourDTO.from_domain(labour)

    async def end_contraction(
        self,
        birthing_person_id: str,
        intensity: int,
        end_time: datetime | None = None,
        notes: str | None = None,
    ) -> LabourDTO:
        domain_id = BirthingPersonId(birthing_person_id)
        birthing_person = await self._birthing_person_repository.get_by_id(domain_id)
        if not birthing_person:
            raise BirthingPersonNotFoundById(birthing_person_id=birthing_person_id)

        labour = EndContractionService().end_contraction(
            birthing_person=birthing_person, intensity=intensity, end_time=end_time, notes=notes
        )
        await self._labour_repository.save(labour)

        # TODO instead of handling domain events here, add them to a Kafka producer and handle them
        # in a dedictead consumer

        for event in birthing_person.active_labour.clear_domain_events():
            self._notification_gateway.send(event.to_dict())

        return LabourDTO.from_domain(labour)

    async def get_active_labour(self, birthing_person_id: str) -> LabourDTO:
        domain_id = BirthingPersonId(birthing_person_id)
        birthing_person = await self._birthing_person_repository.get_by_id(domain_id)
        if not birthing_person:
            raise BirthingPersonNotFoundById(birthing_person_id=birthing_person_id)

        active_labour = birthing_person.active_labour
        if not active_labour:
            raise BirthingPersonDoesNotHaveActiveLabour(birthing_person_id=birthing_person_id)

        return LabourDTO.from_domain(active_labour)

    async def get_active_labour_summary(self, birthing_person_id: str) -> LabourSummaryDTO:
        domain_id = BirthingPersonId(birthing_person_id)
        birthing_person = await self._birthing_person_repository.get_by_id(domain_id)
        if not birthing_person:
            raise BirthingPersonNotFoundById(birthing_person_id=birthing_person_id)

        active_labour = birthing_person.active_labour
        if not active_labour:
            raise BirthingPersonDoesNotHaveActiveLabour(birthing_person_id=birthing_person_id)

        return LabourSummaryDTO.from_domain(active_labour)
