import logging
from datetime import datetime

from app.application.dtos.labour import LabourDTO
from app.application.dtos.labour_summary import LabourSummaryDTO
from app.domain.birthing_person.exceptions import BirthingPersonNotFoundById
from app.domain.birthing_person.repository import BirthingPersonRepository
from app.domain.birthing_person.vo_birthing_person_id import BirthingPersonId
from app.domain.labour.entity import Labour
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
        labour_repository: LabourRepository
    ):
        self._birthing_person_repository = birthing_person_repository
        self._labour_repository = labour_repository


    async def begin_labour(
        self, birthing_person_id: str, first_labour: bool | None = None
    ) -> LabourDTO:
        domain_id = BirthingPersonId(birthing_person_id)
        birthing_person = await self._birthing_person_repository.get_by_id(domain_id)
        if not birthing_person:
            raise BirthingPersonNotFoundById(birthing_person_id=birthing_person_id)

        BeginLabourService().begin_labour(birthing_person=birthing_person, first_labour=first_labour)
        await self._birthing_person_repository.save(birthing_person)
        return LabourDTO.from_domain(birthing_person.active_labour)


    async def complete_labour(
        self,
        birthing_person_id: str,
        end_time: datetime | None = None,
        notes: str | None = None
    ) -> Labour:
        domain_id = BirthingPersonId(birthing_person_id)
        birthing_person = await self._birthing_person_repository.get_by_id(domain_id)
        labour = CompleteLabourService().complete_labour(
            birthing_person=birthing_person,
            end_time=end_time,
            notes=notes
        )
        await self._labour_repository.save(labour)
        return LabourDTO.from_domain(labour)


    async def start_contraction(
        self,
        birthing_person_id: str,
        intensity: int,
        start_time: datetime | None = None,
        notes: str | None = None
    ) -> Labour:
        domain_id = BirthingPersonId(birthing_person_id)
        birthing_person = await self._birthing_person_repository.get_by_id(domain_id)
        labour = StartContractionService().start_contraction(
            birthing_person=birthing_person,
            intensity=intensity,
            start_time=start_time,
            notes=notes
        )
        await self._labour_repository.save(labour)
        return LabourDTO.from_domain(labour)


    async def end_contraction(
        self,
        birthing_person_id: str,
        intensity: int | None = None,
        end_time: datetime | None = None,
        notes: str | None = None
    ) -> Labour:
        domain_id = BirthingPersonId(birthing_person_id)
        birthing_person = await self._birthing_person_repository.get_by_id(domain_id)
        labour = EndContractionService().end_contraction(
            birthing_person=birthing_person,
            intensity=intensity,
            end_time=end_time,
            notes=notes
        )
        await self._labour_repository.save(labour)
        return LabourDTO.from_domain(labour)


    async def get_active_labour_summary(
        self, birthing_person_id: str
    ) -> LabourSummaryDTO | None:
        domain_id = BirthingPersonId(birthing_person_id)
        birthing_person = await self._birthing_person_repository.get_by_id(domain_id)
        active_labour = birthing_person.active_labour
        return LabourSummaryDTO.from_domain(active_labour) if active_labour else None
